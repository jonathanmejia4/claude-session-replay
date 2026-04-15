from __future__ import annotations

from typing import Iterable

from .models import ReplayEvent, ReplayTurn


def group_events_into_turns(events: Iterable[ReplayEvent], compact: bool = False) -> list[ReplayTurn]:
    turns: list[ReplayTurn] = []
    pending_completion_statuses: list[ReplayEvent] = []
    seen_completion_keys: set[str] = set()

    for event in events:
        if event.kind == "message":
            if event.speaker == "assistant":
                carried_statuses = pending_completion_statuses
                pending_completion_statuses = []
                attach_carried_to_assistant = _assistant_likely_summarizes_completion(event.summary)
                if carried_statuses and not attach_carried_to_assistant:
                    _flush_pending_completion_statuses(turns, carried_statuses)
                    seen_completion_keys.update(_canonical_status_key(status.summary) for status in carried_statuses)
                    carried_statuses = []
                previous = turns[-1] if turns else None
                if previous and previous.speaker == "assistant" and not previous.body and _can_merge_assistant_followup(previous, event):
                    previous.body = event.summary
                    for status in carried_statuses:
                        if _canonical_status_key(status.summary) not in {_canonical_status_key(line) for line in previous.status_lines}:
                            previous.status_lines.append(status.summary)
                            previous.status_events.append(status)
                    seen_completion_keys.update(_canonical_status_key(status.summary) for status in carried_statuses)
                    previous.raw_types.append(event.raw_type)
                    continue
                turn = ReplayTurn(
                    speaker="assistant",
                    timestamp=event.timestamp,
                    title="Assistant",
                    body=event.summary,
                    raw_types=[event.raw_type],
                )
                for status in carried_statuses:
                    if _canonical_status_key(status.summary) not in {_canonical_status_key(line) for line in turn.status_lines}:
                        turn.status_lines.append(status.summary)
                        turn.status_events.append(status)
                seen_completion_keys.update(_canonical_status_key(status.summary) for status in carried_statuses)
                turns.append(turn)
                continue

            if pending_completion_statuses:
                _flush_pending_completion_statuses(turns, pending_completion_statuses)
                seen_completion_keys.update(_canonical_status_key(status.summary) for status in pending_completion_statuses)
                pending_completion_statuses = []
            turns.append(
                ReplayTurn(
                    speaker=event.speaker or "unknown",
                    timestamp=event.timestamp,
                    title=(event.speaker or "unknown").title(),
                    body=event.summary,
                    raw_types=[event.raw_type],
                )
            )
            continue

        if event.kind in {"tool_call", "tool_result", "status", "task_notification"}:
            if event.kind in {"status", "task_notification"} and _is_completion_status(event.summary):
                status_key = _canonical_status_key(event.summary)
                if status_key in seen_completion_keys:
                    continue
                if status_key not in {_canonical_status_key(line.summary) for line in pending_completion_statuses}:
                    pending_completion_statuses.append(event)
                continue

            target = _find_target_turn(turns)
            if target is None:
                target = ReplayTurn(
                    speaker="system",
                    timestamp=event.timestamp,
                    title="System",
                    raw_types=[],
                )
                turns.append(target)

            if event.timestamp and not target.timestamp:
                target.timestamp = event.timestamp
            target.raw_types.append(event.raw_type)

            if event.kind == "tool_call":
                target.tool_calls.append(event.summary)
                target.tool_call_events.append(event)
            elif event.kind == "tool_result":
                if compact and _is_launch_noise(event.summary):
                    continue
                target.tool_results.append(event.summary)
                target.tool_result_events.append(event)
            else:
                if compact and _is_low_signal_status(event.summary):
                    continue
                status_key = _canonical_status_key(event.summary)
                if status_key not in {_canonical_status_key(line) for line in target.status_lines}:
                    target.status_lines.append(event.summary)
                    target.status_events.append(event)

    if pending_completion_statuses:
        _flush_pending_completion_statuses(turns, pending_completion_statuses)
        seen_completion_keys.update(_canonical_status_key(status.summary) for status in pending_completion_statuses)

    return [turn for turn in turns if _turn_has_visible_content(turn)]


def _find_target_turn(turns: list[ReplayTurn]) -> ReplayTurn | None:
    if not turns:
        return None
    last = turns[-1]
    if last.speaker in {"assistant", "system"}:
        return last
    return None


def _can_merge_assistant_followup(previous: ReplayTurn, event: ReplayEvent) -> bool:
    if previous.tool_calls or previous.tool_results or previous.status_lines:
        return True
    return False


def _is_launch_noise(summary: str) -> bool:
    lowered = summary.lower()
    return "async agent launched successfully" in lowered


def _is_low_signal_status(summary: str) -> bool:
    lowered = summary.lower()
    return lowered.startswith("dequeue:") or lowered.startswith("remove:")


def _is_completion_status(summary: str) -> bool:
    lowered = summary.lower()
    return "status=completed" in lowered or " completed | " in lowered or lowered.startswith('agent "') and " completed" in lowered


def _assistant_likely_summarizes_completion(summary: str) -> bool:
    lowered = summary.lower()
    summary_markers = (
        "complete",
        "completed",
        "done",
        "remaining",
        "waiting for",
        "waiting on",
        "agents done",
        "agent ",
        "subagent",
        "wrapping up",
        "still running",
    )
    return any(marker in lowered for marker in summary_markers)


def _canonical_status_key(summary: str) -> str:
    compact = summary.strip()
    for prefix in ("enqueue: ", "popAll: ", "dequeue: "):
        if compact.startswith(prefix):
            return compact[len(prefix) :]
    return compact


def _turn_has_visible_content(turn: ReplayTurn) -> bool:
    return bool(turn.body or turn.tool_calls or turn.tool_results or turn.status_lines)


def _flush_pending_completion_statuses(turns: list[ReplayTurn], pending_completion_statuses: list[ReplayEvent]) -> None:
    if not pending_completion_statuses:
        return
    turn = ReplayTurn(
        speaker="system",
        timestamp=None,
        title="System",
        raw_types=[],
    )
    for status in pending_completion_statuses:
        if _canonical_status_key(status.summary) not in {_canonical_status_key(line) for line in turn.status_lines}:
            turn.status_lines.append(status.summary)
            turn.status_events.append(status)
    turns.append(turn)
