from claude_session_replay import parser as parser_module
from claude_session_replay.parser import _normalize_record, _summarize_tool_input, _trim


def test_trim_compacts_whitespace() -> None:
    assert _trim("a   b\nc") == "a b c"


def test_summarize_command_input_prefers_command() -> None:
    assert _summarize_tool_input({"command": "echo hi"}) == "echo hi"


def test_trim_respects_changed_trim_max() -> None:
    long_text = "x" * 500
    original = parser_module.TRIM_MAX
    try:
        # Default truncates to 220 chars (217 + "...").
        assert len(_trim(long_text)) == 220
        # Raising TRIM_MAX above the text length disables truncation.
        parser_module.TRIM_MAX = 10_000_000
        assert _trim(long_text) == long_text
    finally:
        parser_module.TRIM_MAX = original


def test_assistant_with_two_tool_use_blocks_yields_two_calls_with_ids() -> None:
    record = {
        "type": "assistant",
        "timestamp": "2026-01-01T00:00:00Z",
        "_line_number": 1,
        "message": {
            "content": [
                {"type": "tool_use", "id": "call_a", "name": "Read", "input": {"command": "read a"}},
                {"type": "tool_use", "id": "call_b", "name": "Write", "input": {"command": "write b"}},
            ]
        },
    }

    events = _normalize_record(record, include_tools=True)
    tool_calls = [e for e in events if e.kind == "tool_call"]

    assert len(tool_calls) == 2
    assert tool_calls[0].metadata["tool_use_id"] == "call_a"
    assert tool_calls[0].metadata["tool_name"] == "Read"
    assert tool_calls[1].metadata["tool_use_id"] == "call_b"
    assert tool_calls[1].metadata["tool_name"] == "Write"
    # Each call keeps its own summary, not a joined blob.
    assert tool_calls[0].summary == "Read: read a"
    assert tool_calls[1].summary == "Write: write b"


def test_assistant_emits_text_event_before_tool_use_events() -> None:
    record = {
        "type": "assistant",
        "timestamp": "2026-01-01T00:00:00Z",
        "_line_number": 1,
        "message": {
            "content": [
                {"type": "text", "text": "Let me read it."},
                {"type": "tool_use", "id": "call_a", "name": "Read", "input": {"command": "read a"}},
            ]
        },
    }

    events = _normalize_record(record, include_tools=True)

    assert [e.kind for e in events] == ["message", "tool_call"]
    assert events[0].summary == "Let me read it."
    assert events[1].metadata["tool_use_id"] == "call_a"
