from claude_session_replay.models import ReplayTurn
from claude_session_replay.renderers import render_grouped_plain


def test_compact_grouped_render_humanizes_completion_status() -> None:
    turns = [
        ReplayTurn(
            speaker="assistant",
            timestamp="2026-01-01T00:00:00Z",
            title="Assistant",
            body="Payment audit complete.",
            status_lines=['enqueue: Agent "Audit payment flow" completed | status=completed | task_id=abc'],
        )
    ]

    rendered = render_grouped_plain(turns, compact=True)

    assert 'status: Agent "Audit payment flow" completed' in rendered
    assert "task_id=abc" not in rendered
    assert "enqueue:" not in rendered


def test_detailed_grouped_render_keeps_original_status_line() -> None:
    turns = [
        ReplayTurn(
            speaker="assistant",
            timestamp="2026-01-01T00:00:00Z",
            title="Assistant",
            body="Payment audit complete.",
            status_lines=['enqueue: Agent "Audit payment flow" completed | status=completed | task_id=abc'],
        )
    ]

    rendered = render_grouped_plain(turns, compact=False)

    assert 'status: enqueue: Agent "Audit payment flow" completed | status=completed | task_id=abc' in rendered


def test_compact_grouped_render_uses_event_metadata_for_humanized_lines() -> None:
    from claude_session_replay.models import ReplayEvent

    turn = ReplayTurn(
        speaker="assistant",
        timestamp="2026-01-01T00:00:00Z",
        title="Assistant",
        body="Checking progress.",
    )
    turn.status_events.append(
        ReplayEvent(
            kind="status",
            timestamp=None,
            speaker="system",
            summary='enqueue: {"task_id":"abc","tool_use_id":"tool1","description":"Audit authentication system","task_type":"local_agent"}',
            raw_type="queue-operation",
            metadata={"operation": "enqueue", "task_id": "abc", "task_name": "Audit authentication system"},
            raw={},
        )
    )
    turn.tool_call_events.append(
        ReplayEvent(
            kind="tool_call",
            timestamp=None,
            speaker="assistant",
            summary='TaskOutput: task_id=abc {"block": false, "task_id": "abc", "timeout": 5000}',
            raw_type="assistant/tool_use",
            metadata={"tool_name": "TaskOutput", "task_id": "abc", "task_name": "Audit authentication system"},
            raw={},
        )
    )
    turn.tool_result_events.append(
        ReplayEvent(
            kind="tool_result",
            timestamp=None,
            speaker="tool",
            summary='tool_result[tool1]: <retrieval_status>not_ready</retrieval_status> <task_id>abc</task_id>',
            raw_type="user/tool_result",
            metadata={"retrieval_status": "not_ready", "task_id": "abc"},
            raw={},
        )
    )

    rendered = render_grouped_plain([turn], compact=True)

    assert "status: Launched subagent: Audit authentication system" in rendered
    assert "action: Checked task output: Audit authentication system" in rendered
    assert "result: Task output not ready: Audit authentication system" in rendered


def test_compact_grouped_render_suppresses_duplicate_launch_tool_line() -> None:
    from claude_session_replay.models import ReplayEvent

    turn = ReplayTurn(
        speaker="assistant",
        timestamp="2026-01-01T00:00:00Z",
        title="Assistant",
        body="Launching checks.",
    )
    turn.status_events.append(
        ReplayEvent(
            kind="status",
            timestamp=None,
            speaker="system",
            summary='enqueue: {"task_id":"abc","tool_use_id":"tool1","description":"Audit authentication system","task_type":"local_agent"}',
            raw_type="queue-operation",
            metadata={"operation": "enqueue", "task_id": "abc", "task_name": "Audit authentication system"},
            raw={},
        )
    )
    turn.tool_call_events.append(
        ReplayEvent(
            kind="tool_call",
            timestamp=None,
            speaker="assistant",
            summary="Task: Audit authentication system",
            raw_type="assistant/tool_use",
            metadata={"tool_name": "Task", "task_id": "abc", "task_name": "Audit authentication system"},
            raw={},
        )
    )

    rendered = render_grouped_plain([turn], compact=True)

    assert rendered.count("Audit authentication system") == 1


def test_compact_grouped_render_classifies_operator_note() -> None:
    from claude_session_replay.models import ReplayEvent

    turn = ReplayTurn(
        speaker="assistant",
        timestamp="2026-01-01T00:00:00Z",
        title="Assistant",
        body="Frontend audit complete.",
    )
    turn.status_events.append(
        ReplayEvent(
            kind="status",
            timestamp=None,
            speaker="system",
            summary="enqueue: hey check the production website not the local one production one is at example.com",
            raw_type="queue-operation",
            metadata={"operation": "enqueue"},
            raw={},
        )
    )

    rendered = render_grouped_plain([turn], compact=True)

    assert "note: hey check the production website not the local one production one is at example.com" in rendered


def test_task_name_precedence_prefers_launch_description_over_completion_summary() -> None:
    from claude_session_replay.models import ReplayEvent

    turn = ReplayTurn(
        speaker="assistant",
        timestamp="2026-01-01T00:00:00Z",
        title="Assistant",
        body="Checking frontend progress.",
    )
    turn.status_events.append(
        ReplayEvent(
            kind="status",
            timestamp=None,
            speaker="system",
            summary='enqueue: {"task_id":"abc","tool_use_id":"tool1","description":"Audit dashboard frontend pages","task_type":"local_agent"}',
            raw_type="queue-operation",
            metadata={"operation": "enqueue", "task_id": "abc", "task_name": "Audit dashboard frontend pages"},
            raw={},
        )
    )
    turn.status_events.append(
        ReplayEvent(
            kind="status",
            timestamp=None,
            speaker="system",
            summary='Agent "Audit dashboard frontend pages" completed | status=completed | task_id=abc',
            raw_type="user/task_notification",
            metadata={"task_id": "abc", "task_summary": 'Agent "Audit dashboard frontend pages" completed', "task_status": "completed"},
            raw={},
        )
    )
    turn.tool_call_events.append(
        ReplayEvent(
            kind="tool_call",
            timestamp=None,
            speaker="assistant",
            summary='TaskOutput: task_id=abc {"block": false, "task_id": "abc", "timeout": 5000}',
            raw_type="assistant/tool_use",
            metadata={"tool_name": "TaskOutput", "task_id": "abc"},
            raw={},
        )
    )
    turn.tool_result_events.append(
        ReplayEvent(
            kind="tool_result",
            timestamp=None,
            speaker="tool",
            summary='tool_result[tool1]: <retrieval_status>success</retrieval_status> <task_id>abc</task_id> <status>completed</status>',
            raw_type="user/tool_result",
            metadata={"retrieval_status": "success", "task_id": "abc", "task_status": "completed"},
            raw={},
        )
    )

    rendered = render_grouped_plain([turn], compact=True)

    assert 'action: Checked task output: Audit dashboard frontend pages' in rendered
    assert 'result: Retrieved completed output: Audit dashboard frontend pages' in rendered
    assert 'Agent "Audit dashboard frontend pages" completed' not in rendered.split("action:")[1]


def test_completion_summary_normalizes_when_only_name_source() -> None:
    from claude_session_replay.models import ReplayEvent

    turn = ReplayTurn(
        speaker="assistant",
        timestamp="2026-01-01T00:00:00Z",
        title="Assistant",
        body="Checking progress.",
    )
    turn.status_events.append(
        ReplayEvent(
            kind="status",
            timestamp=None,
            speaker="system",
            summary='Agent "Audit dashboard frontend pages" completed | status=completed | task_id=abc',
            raw_type="user/task_notification",
            metadata={"task_id": "abc", "task_summary": 'Agent "Audit dashboard frontend pages" completed', "task_status": "completed"},
            raw={},
        )
    )
    turn.tool_call_events.append(
        ReplayEvent(
            kind="tool_call",
            timestamp=None,
            speaker="assistant",
            summary='TaskOutput: task_id=abc {"block": false, "task_id": "abc", "timeout": 5000}',
            raw_type="assistant/tool_use",
            metadata={"tool_name": "TaskOutput", "task_id": "abc"},
            raw={},
        )
    )

    rendered = render_grouped_plain([turn], compact=True)

    assert 'action: Checked task output: Audit dashboard frontend pages' in rendered


def test_compact_grouped_render_expands_long_completed_subagent_output() -> None:
    from claude_session_replay.models import ReplayEvent

    long_output = "Audit report start\n" + ("detail line\n" * 80)

    turn = ReplayTurn(
        speaker="assistant",
        timestamp="2026-01-01T00:00:00Z",
        title="Assistant",
        body="Waiting for final audit.",
    )
    turn.status_events.append(
        ReplayEvent(
            kind="status",
            timestamp=None,
            speaker="system",
            summary='enqueue: {"task_id":"abc","tool_use_id":"tool1","description":"Audit dashboard frontend pages","task_type":"local_agent"}',
            raw_type="queue-operation",
            metadata={"operation": "enqueue", "task_id": "abc", "task_name": "Audit dashboard frontend pages"},
            raw={},
        )
    )
    turn.tool_result_events.append(
        ReplayEvent(
            kind="tool_result",
            timestamp=None,
            speaker="tool",
            summary="tool_result[tool1]: success",
            raw_type="user/tool_result",
            metadata={
                "retrieval_status": "success",
                "task_id": "abc",
                "task_status": "completed",
                "task_output": long_output,
            },
            raw={},
        )
    )

    rendered = render_grouped_plain([turn], compact=True)

    assert "SUBAGENT OUTPUT: AUDIT DASHBOARD FRONTEND PAGES" in rendered
    assert long_output.strip() in rendered


def test_grouped_render_interleaves_results_under_matching_calls() -> None:
    from claude_session_replay.models import ReplayEvent

    turn = ReplayTurn(
        speaker="assistant",
        timestamp="2026-01-01T00:00:00Z",
        title="Assistant",
        body="Doing two things.",
    )
    turn.tool_call_events.append(
        ReplayEvent(
            kind="tool_call",
            timestamp=None,
            speaker="assistant",
            summary="Read: file_a",
            raw_type="assistant/tool_use",
            metadata={"tool_name": "Read", "tool_use_id": "call_a"},
            raw={},
        )
    )
    turn.tool_call_events.append(
        ReplayEvent(
            kind="tool_call",
            timestamp=None,
            speaker="assistant",
            summary="Write: file_b",
            raw_type="assistant/tool_use",
            metadata={"tool_name": "Write", "tool_use_id": "call_b"},
            raw={},
        )
    )
    # Result for call_b appears BEFORE call_a's result — pairing is by id, not order.
    turn.tool_result_events.append(
        ReplayEvent(
            kind="tool_result",
            timestamp=None,
            speaker="tool",
            summary="tool_result[call_b]: wrote b",
            raw_type="user/tool_result",
            metadata={"tool_use_id": "call_b"},
            raw={},
        )
    )
    turn.tool_result_events.append(
        ReplayEvent(
            kind="tool_result",
            timestamp=None,
            speaker="tool",
            summary="tool_result[call_a]: read a",
            raw_type="user/tool_result",
            metadata={"tool_use_id": "call_a"},
            raw={},
        )
    )
    # An orphan result whose call lived in a prior turn → trailing un-indented.
    turn.tool_result_events.append(
        ReplayEvent(
            kind="tool_result",
            timestamp=None,
            speaker="tool",
            summary="tool_result[call_x]: orphan",
            raw_type="user/tool_result",
            metadata={"tool_use_id": "call_x"},
            raw={},
        )
    )

    rendered = render_grouped_plain([turn], compact=False)
    lines = [line for line in rendered.splitlines() if line]

    # Each result is indented two spaces immediately under its matching call.
    assert lines.index("tool: Read: file_a") + 1 == lines.index("  result: tool_result[call_a]: read a")
    assert lines.index("tool: Write: file_b") + 1 == lines.index("  result: tool_result[call_b]: wrote b")
    # The orphan falls to a trailing un-indented result block.
    assert "result: tool_result[call_x]: orphan" in lines
    assert "  result: tool_result[call_x]: orphan" not in lines


def test_compact_grouped_render_keeps_short_completed_result_compact() -> None:
    from claude_session_replay.models import ReplayEvent

    turn = ReplayTurn(
        speaker="assistant",
        timestamp="2026-01-01T00:00:00Z",
        title="Assistant",
        body="Waiting for final audit.",
    )
    turn.tool_result_events.append(
        ReplayEvent(
            kind="tool_result",
            timestamp=None,
            speaker="tool",
            summary="tool_result[tool1]: success",
            raw_type="user/tool_result",
            metadata={
                "retrieval_status": "success",
                "task_id": "abc",
                "task_status": "completed",
                "task_output": "short output",
            },
            raw={},
        )
    )

    rendered = render_grouped_plain([turn], compact=True)

    assert "subagent output:" not in rendered
    assert "result: Retrieved completed output" in rendered
