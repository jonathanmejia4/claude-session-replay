from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterator

from .models import ReplayEvent


def iter_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            record["_line_number"] = line_number
            yield record


def inspect_types(path: str | Path, limit: int | None = None) -> tuple[Counter[str], Counter[str]]:
    event_types: Counter[str] = Counter()
    block_types: Counter[str] = Counter()

    for index, record in enumerate(iter_jsonl(path), start=1):
        if limit is not None and index > limit:
            break
        event_type = str(record.get("type", "<missing>"))
        event_types[event_type] += 1

        if event_type == "assistant":
            for block in _content_blocks(record.get("message", {}).get("content")):
                block_types[f"assistant:{block.get('type', '<missing>')}"] += 1

        if event_type == "user":
            content = record.get("message", {}).get("content")
            if isinstance(content, str):
                block_types["user:text"] += 1
            else:
                for block in _content_blocks(content):
                    block_types[f"user:{block.get('type', '<missing>')}"] += 1

    return event_types, block_types


def normalize_events(
    path: str | Path,
    include_tools: bool = True,
    from_line: int | None = None,
    to_line: int | None = None,
) -> Iterator[ReplayEvent]:
    for record in iter_jsonl(path):
        line_number = int(record.get("_line_number", 0))
        if from_line is not None and line_number < from_line:
            continue
        if to_line is not None and line_number > to_line:
            continue
        event = _normalize_record(record, include_tools=include_tools)
        if event is not None:
            yield event


def _normalize_record(record: dict[str, Any], include_tools: bool) -> ReplayEvent | None:
    event_type = record.get("type")
    timestamp = record.get("timestamp")
    line_number = record.get("_line_number")

    if event_type == "user":
        message = record.get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            text = content.strip()
            if text:
                task_note = _summarize_task_notification(text)
                if task_note is not None:
                    return ReplayEvent(
                        kind="task_notification",
                        timestamp=timestamp,
                        speaker="system",
                        summary=task_note,
                        raw_type="user/task_notification",
                        metadata=_extract_task_notification_metadata(text),
                        raw=record,
                    )
                return ReplayEvent(
                    kind="message",
                    timestamp=timestamp,
                    speaker="user",
                    summary=text,
                    raw_type="user",
                    metadata={},
                    raw=record,
                )

        for block in _content_blocks(content):
            if block.get("type") == "tool_result" and include_tools:
                result = _summarize_tool_result_content(block.get("content", ""))
                return ReplayEvent(
                    kind="tool_result",
                    timestamp=timestamp,
                    speaker="tool",
                    summary=f"tool_result[{block.get('tool_use_id', 'unknown')}]: {result}",
                    raw_type="user/tool_result",
                    metadata=_extract_tool_result_metadata(block.get("content", "")),
                    raw=record,
                )
        return None

    if event_type == "assistant":
        text_parts: list[str] = []
        tool_parts: list[str] = []
        for block in _content_blocks(record.get("message", {}).get("content")):
            block_type = block.get("type")
            if block_type == "text":
                text = str(block.get("text", "")).strip()
                if text:
                    text_parts.append(text)
            elif block_type == "tool_use" and include_tools:
                name = str(block.get("name", "tool"))
                tool_input = block.get("input", {})
                tool_parts.append(f"{name}: {_summarize_tool_input(tool_input)}")

        if text_parts:
            return ReplayEvent(
                kind="message",
                timestamp=timestamp,
                speaker="assistant",
                summary="\n\n".join(text_parts),
                raw_type="assistant",
                metadata={},
                raw=record,
            )

        if tool_parts and include_tools:
            return ReplayEvent(
                kind="tool_call",
                timestamp=timestamp,
                speaker="assistant",
                summary="\n".join(tool_parts),
                raw_type="assistant/tool_use",
                metadata=_extract_tool_call_metadata(record.get("message", {}).get("content")),
                raw=record,
            )

        return None

    if event_type == "progress":
        data = record.get("data", {})
        task = data.get("taskDescription") or data.get("message", {}).get("type") or data.get("type")
        if not task:
            task = f"progress line {line_number}"
        return ReplayEvent(
            kind="status",
            timestamp=timestamp,
            speaker="system",
            summary=str(task),
            raw_type="progress",
            metadata={"progress_label": str(task)},
            raw=record,
        )

    if event_type == "queue-operation":
        operation = record.get("operation", "queue")
        content = _trim(str(record.get("content", "")))
        if operation in {"remove", "dequeue"} and not content:
            return None
        task_note = _summarize_task_notification(str(record.get("content", "")))
        if task_note is not None:
            content = task_note
        return ReplayEvent(
            kind="status",
            timestamp=timestamp,
            speaker="system",
            summary=f"{operation}: {content}",
            raw_type="queue-operation",
            metadata=_extract_queue_operation_metadata(operation, str(record.get("content", ""))),
            raw=record,
        )

    return None


def _content_blocks(content: Any) -> list[dict[str, Any]]:
    if isinstance(content, list):
        return [block for block in content if isinstance(block, dict)]
    return []


def _summarize_tool_input(tool_input: Any) -> str:
    if isinstance(tool_input, dict):
        if "description" in tool_input:
            description = str(tool_input["description"]).strip()
            if description:
                return description
        if "task_id" in tool_input:
            task_id = str(tool_input.get("task_id", "")).strip()
            return _trim(f"task_id={task_id} {json.dumps(tool_input, sort_keys=True)}")
        if "command" in tool_input:
            return _trim(str(tool_input["command"]))
        return _trim(json.dumps(tool_input, sort_keys=True))
    return _trim(str(tool_input))


def _summarize_tool_result_content(content: Any) -> str:
    if isinstance(content, str):
        task_note = _summarize_task_notification(content)
        if task_note is not None:
            return task_note
        return _trim(content.strip())
    if isinstance(content, list):
        text_chunks: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text" and item.get("text"):
                    text_chunks.append(str(item["text"]))
                else:
                    text_chunks.append(json.dumps(item, sort_keys=True))
            else:
                text_chunks.append(str(item))
        joined = "\n".join(text_chunks).strip()
        task_note = _summarize_task_notification(joined)
        if task_note is not None:
            return task_note
        return _trim(joined)
    return _trim(str(content))


def _summarize_task_notification(text: str) -> str | None:
    if "<task-notification>" not in text:
        return None

    def extract(tag: str) -> str | None:
        match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
        if match:
            value = match.group(1).strip()
            return value or None
        return None

    summary = extract("summary") or "Task notification"
    status = extract("status") or "unknown"
    task_id = extract("task-id")
    usage = extract("usage")

    parts = [summary, f"status={status}"]
    if task_id:
        parts.append(f"task_id={task_id}")
    if usage:
        parts.append(_trim(usage))
    return " | ".join(parts)


def _extract_task_notification_metadata(text: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {"source": "task_notification"}
    if "<task-notification>" not in text:
        return metadata

    for tag, key in (
        ("summary", "task_summary"),
        ("status", "task_status"),
        ("task-id", "task_id"),
        ("tool-use-id", "tool_use_id"),
    ):
        match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
        if match:
            metadata[key] = match.group(1).strip()
    return metadata


def _extract_tool_call_metadata(content: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for block in _content_blocks(content):
        if block.get("type") != "tool_use":
            continue
        name = str(block.get("name", ""))
        tool_input = block.get("input", {})
        metadata["tool_name"] = name
        if isinstance(tool_input, dict):
            if "task_id" in tool_input:
                metadata["task_id"] = str(tool_input["task_id"])
            if "description" in tool_input:
                metadata["task_name"] = str(tool_input["description"])
            if "command" in tool_input:
                metadata["command"] = str(tool_input["command"])
            if "timeout" in tool_input:
                metadata["timeout"] = tool_input["timeout"]
            if "block" in tool_input:
                metadata["block"] = tool_input["block"]
    return metadata


def _extract_tool_result_metadata(content: Any) -> dict[str, Any]:
    text = ""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("text"):
                text_parts.append(str(item["text"]))
            else:
                text_parts.append(str(item))
        text = "\n".join(text_parts)

    metadata: dict[str, Any] = {}
    for tag, key in (
        ("retrieval_status", "retrieval_status"),
        ("task_id", "task_id"),
        ("task_type", "task_type"),
        ("status", "task_status"),
        ("output", "task_output"),
    ):
        match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
        if match:
            metadata[key] = match.group(1).strip()
    return metadata


def _extract_queue_operation_metadata(operation: str, content: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {"operation": operation}

    stripped = content.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            metadata.update({k: payload[k] for k in payload if k in {"task_id", "tool_use_id", "description", "task_type"}})
            if "description" in payload:
                metadata["task_name"] = payload["description"]

    task_meta = _extract_task_notification_metadata(content)
    metadata.update({k: v for k, v in task_meta.items() if v})

    return metadata


def _trim(text: str, max_length: int = 220) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3] + "..."
