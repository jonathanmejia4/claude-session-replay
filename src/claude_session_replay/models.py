from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReplayEvent:
    kind: str
    timestamp: str | None
    speaker: str | None
    summary: str
    raw_type: str
    raw: dict[str, Any] = field(repr=False)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplayTurn:
    speaker: str
    timestamp: str | None
    title: str
    body: str | None = None
    status_events: list[ReplayEvent] = field(default_factory=list, repr=False)
    tool_call_events: list[ReplayEvent] = field(default_factory=list, repr=False)
    tool_result_events: list[ReplayEvent] = field(default_factory=list, repr=False)
    tool_calls: list[str] = field(default_factory=list)
    tool_results: list[str] = field(default_factory=list)
    status_lines: list[str] = field(default_factory=list)
    expanded_blocks: list[tuple[str, str]] = field(default_factory=list)
    raw_types: list[str] = field(default_factory=list)
