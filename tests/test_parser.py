from claude_session_replay.parser import _summarize_tool_input, _trim


def test_trim_compacts_whitespace() -> None:
    assert _trim("a   b\nc") == "a b c"


def test_summarize_command_input_prefers_command() -> None:
    assert _summarize_tool_input({"command": "echo hi"}) == "echo hi"
