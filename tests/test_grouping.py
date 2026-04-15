from typing import Optional

from claude_session_replay.grouping import group_events_into_turns
from claude_session_replay.models import ReplayEvent


def _event(kind: str, speaker: Optional[str], summary: str, raw_type: str = "test", timestamp: Optional[str] = None) -> ReplayEvent:
    return ReplayEvent(
        kind=kind,
        timestamp=timestamp,
        speaker=speaker,
        summary=summary,
        raw_type=raw_type,
        raw={},
    )


def test_completion_status_attaches_to_next_assistant_turn() -> None:
    events = [
        _event("status", "system", 'Agent "Audit payment/Stripe flow" completed | status=completed | task_id=abc'),
        _event("message", "assistant", "Payment audit complete. Critical findings found."),
    ]

    turns = group_events_into_turns(events, compact=True)

    assert len(turns) == 1
    assert turns[0].speaker == "assistant"
    assert turns[0].status_lines == ['Agent "Audit payment/Stripe flow" completed | status=completed | task_id=abc']


def test_completion_status_flushes_if_user_message_arrives_first() -> None:
    events = [
        _event("status", "system", 'Agent "Audit payment/Stripe flow" completed | status=completed | task_id=abc'),
        _event("message", "user", "what happened?"),
    ]

    turns = group_events_into_turns(events, compact=True)

    assert len(turns) == 2
    assert turns[0].speaker == "system"
    assert turns[1].speaker == "user"


def test_completion_prefers_forward_assistant_summary() -> None:
    events = [
        _event("message", "assistant", "Auth agent is still running."),
        _event("status", "system", 'Agent "Audit auth" completed | status=completed | task_id=auth1'),
        _event("message", "assistant", "Auth audit complete. Password reset is broken."),
    ]

    turns = group_events_into_turns(events, compact=True)

    assert len(turns) == 2
    assert turns[0].speaker == "assistant"
    assert turns[0].status_lines == []
    assert turns[1].speaker == "assistant"
    assert turns[1].status_lines == ['Agent "Audit auth" completed | status=completed | task_id=auth1']


def test_completion_flushes_before_unrelated_assistant_answer() -> None:
    events = [
        _event("status", "system", 'Agent "Audit auth" completed | status=completed | task_id=auth1'),
        _event("message", "assistant", "Good question — let me break down exactly what agencies get from the platform."),
    ]

    turns = group_events_into_turns(events, compact=True)

    assert len(turns) == 2
    assert turns[0].speaker == "system"
    assert turns[1].speaker == "assistant"
    assert turns[1].status_lines == []
