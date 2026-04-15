from __future__ import annotations

import re
from typing import Iterable

from .models import ReplayEvent, ReplayTurn


def render_markdown(events: Iterable[ReplayEvent]) -> str:
    parts: list[str] = []
    for event in events:
        header = _header(event)
        parts.append(header)
        parts.append("")
        parts.append(event.summary)
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def render_plain(events: Iterable[ReplayEvent]) -> str:
    parts: list[str] = []
    for event in events:
        parts.append(_header(event))
        parts.append(event.summary)
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def render_grouped_plain(turns: Iterable[ReplayTurn], compact: bool = False) -> str:
    parts: list[str] = []
    task_names: dict[str, tuple[str, int]] = {}
    for turn in turns:
        header = _turn_header(turn)
        parts.append(header)
        if turn.body:
            parts.append(turn.body)
        if turn.status_events:
            task_names.update(_collect_task_names(turn.status_events))
            for event in turn.status_events:
                rendered = _humanize_status_event(event) if compact else event.summary
                prefix = _status_prefix(event, compact=compact)
                parts.append(f"{prefix}: {rendered}")
        elif turn.status_lines:
            for line in turn.status_lines:
                rendered = _humanize_status_line(line) if compact else line
                parts.append(f"status: {rendered}")
        if turn.tool_call_events:
            task_names.update(_collect_task_names(turn.tool_call_events))
            for event in turn.tool_call_events:
                if compact and _is_duplicate_launch_tool_event(event, turn.status_events):
                    continue
                rendered = _humanize_tool_call_event(event, task_names=task_names) if compact else event.summary
                parts.append(f"action: {rendered}" if compact else f"tool: {rendered}")
        elif turn.tool_calls:
            for line in turn.tool_calls:
                parts.append(f"tool: {line}")
        if turn.tool_result_events:
            task_names.update(_collect_task_names(turn.tool_result_events))
            for event in turn.tool_result_events:
                expanded = _expanded_tool_result_block(event, task_names=task_names) if compact else None
                if expanded is not None:
                    label, content = expanded
                    parts.append("")
                    parts.extend(_render_expanded_block(label, content))
                    parts.append("")
                    continue
                rendered = _humanize_tool_result_event(event, task_names=task_names) if compact else event.summary
                parts.append(f"result: {rendered}")
        elif turn.tool_results:
            for line in turn.tool_results:
                parts.append(f"result: {line}")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def _header(event: ReplayEvent) -> str:
    speaker = (event.speaker or event.kind).upper()
    if event.timestamp:
        return f"[{speaker} | {event.timestamp} | {event.raw_type}]"
    return f"[{speaker} | {event.raw_type}]"


def _turn_header(turn: ReplayTurn) -> str:
    speaker = turn.speaker.upper()
    if turn.timestamp:
        return f"[{speaker} | {turn.timestamp}]"
    return f"[{speaker}]"


def _humanize_status_line(line: str) -> str:
    compact = line.strip()
    for prefix in ("enqueue: ", "popAll: ", "dequeue: "):
        if compact.startswith(prefix):
            compact = compact[len(prefix) :]
            break

    match = re.match(r'^(Agent ".+?" completed)(?: \| .*)?$', compact)
    if match:
        return match.group(1)

    return compact


def _collect_task_names(events: Iterable[ReplayEvent]) -> dict[str, str]:
    task_names: dict[str, tuple[str, int]] = {}
    for event in events:
        metadata = event.metadata or {}
        task_id = metadata.get("task_id")
        task_name, priority = _task_name_candidate(event)
        if task_id and task_name:
            existing = task_names.get(str(task_id))
            if existing is None or priority > existing[1]:
                task_names[str(task_id)] = (task_name, priority)
    return task_names


def _status_prefix(event: ReplayEvent, compact: bool) -> str:
    if compact and _looks_like_operator_note(event):
        return "note"
    return "status"


def _humanize_status_event(event: ReplayEvent) -> str:
    metadata = event.metadata or {}

    task_name = metadata.get("task_name") or metadata.get("description")
    if task_name and metadata.get("operation") == "enqueue" and metadata.get("task_id"):
        return f"Launched subagent: {task_name}"

    task_summary = metadata.get("task_summary")
    if task_summary and metadata.get("task_status") == "completed":
        return task_summary

    if event.raw_type == "progress":
        label = metadata.get("progress_label")
        if label:
            return f"Waiting on: {label}"

    if _looks_like_operator_note(event):
        return _clean_operator_note(event.summary)

    return _humanize_status_line(event.summary)


def _humanize_tool_call_event(event: ReplayEvent, task_names: dict[str, tuple[str, int]]) -> str:
    metadata = event.metadata or {}
    tool_name = metadata.get("tool_name")
    task_name = metadata.get("task_name")
    task_id = metadata.get("task_id")

    if tool_name == "TaskOutput":
        if not task_name and task_id:
            task_entry = task_names.get(str(task_id))
            task_name = task_entry[0] if task_entry else None
        if task_name:
            return f"Checked task output: {task_name}"
        if task_id:
            return f"Checked task output: {task_id}"

    if tool_name == "Task" and task_name:
        return f"Launched subagent: {task_name}"

    return event.summary


def _humanize_tool_result_event(event: ReplayEvent, task_names: dict[str, tuple[str, int]]) -> str:
    metadata = event.metadata or {}
    retrieval_status = metadata.get("retrieval_status")
    task_status = metadata.get("task_status")
    task_id = metadata.get("task_id")
    task_entry = task_names.get(str(task_id)) if task_id else None
    task_name = task_entry[0] if task_entry else None

    if retrieval_status == "not_ready":
        if task_name:
            return f"Task output not ready: {task_name}"
        return "Task output not ready"
    if retrieval_status == "success" and task_status == "completed":
        if _should_expand_tool_result(event):
            if task_name:
                return f"Retrieved completed output: {task_name}"
            return "Retrieved completed output"
        if task_name:
            return f"Retrieved completed output: {task_name}"
        return "Retrieved completed output"
    if retrieval_status == "success":
        if task_name:
            return f"Retrieved task output: {task_name}"
        return "Retrieved task output"

    return event.summary


def _is_duplicate_launch_tool_event(event: ReplayEvent, status_events: Iterable[ReplayEvent]) -> bool:
    metadata = event.metadata or {}
    if metadata.get("tool_name") != "Task":
        return False
    task_name = metadata.get("task_name")
    if not task_name:
        return False
    for status_event in status_events:
        status_meta = status_event.metadata or {}
        if status_meta.get("operation") == "enqueue" and (status_meta.get("task_name") or status_meta.get("description")) == task_name:
            return True
    return False


def _looks_like_operator_note(event: ReplayEvent) -> bool:
    metadata = event.metadata or {}
    if metadata.get("operation") not in {"enqueue", "popAll"}:
        return False
    summary = event.summary.lower()
    return "hey " in summary or "check the production website" in summary or "project:" in summary


def _clean_operator_note(text: str) -> str:
    compact = text.strip()
    for prefix in ("enqueue: ", "popAll: "):
        if compact.startswith(prefix):
            compact = compact[len(prefix) :]
            break
    return compact


def _task_name_candidate(event: ReplayEvent) -> tuple[str | None, int]:
    metadata = event.metadata or {}

    if metadata.get("operation") == "enqueue":
        task_name = metadata.get("task_name") or metadata.get("description")
        if task_name:
            return str(task_name), 4

    task_name = metadata.get("task_name")
    if task_name:
        return str(task_name), 3

    progress_label = metadata.get("progress_label")
    if progress_label:
        return str(progress_label), 2

    task_summary = metadata.get("task_summary")
    if task_summary:
        return _normalize_completion_summary(str(task_summary)), 1

    return None, 0


def _normalize_completion_summary(text: str) -> str:
    match = re.match(r'^Agent "(.*?)" completed$', text.strip())
    if match:
        return match.group(1)
    return text.strip()


def _expanded_tool_result_block(event: ReplayEvent, task_names: dict[str, tuple[str, int]]) -> tuple[str, str] | None:
    if not _should_expand_tool_result(event):
        return None

    metadata = event.metadata or {}
    task_id = metadata.get("task_id")
    task_entry = task_names.get(str(task_id)) if task_id else None
    task_name = task_entry[0] if task_entry else None
    output = metadata.get("task_output")
    if not output:
        return None

    label = "subagent output"
    if task_name:
        label = f"subagent output: {task_name}"
    return label, str(output).strip()


def _should_expand_tool_result(event: ReplayEvent) -> bool:
    metadata = event.metadata or {}
    if metadata.get("retrieval_status") != "success":
        return False
    if metadata.get("task_status") != "completed":
        return False
    output = metadata.get("task_output")
    if not output:
        return False
    text = str(output).strip()
    if len(text) < 280:
        return False
    return True


def _render_expanded_block(label: str, content: str) -> list[str]:
    title = label.upper()
    border = "=" * min(max(len(title) + 8, 28), 88)
    return [
        border,
        f"  {title}",
        border,
        content,
    ]
