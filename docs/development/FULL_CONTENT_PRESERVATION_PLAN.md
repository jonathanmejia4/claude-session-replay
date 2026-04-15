# Full Content Preservation Plan

## Goal

Preserve all substantive user, assistant, and subagent-written content in full, while compressing only machine scaffolding such as queue plumbing, polling chatter, and transport metadata.

## Why This Plan Exists

The replay has been moving toward readability, but there is an important constraint for this tool:

- if a message is long because it was intentionally written, it should not be truncated
- if a subagent produced a real report, that output should be visible in full

The tool should be useful for forensic recovery of entire conversations, not just for short summaries.

That means the replay should prefer:

- full authored content
- structured grouping
- minimal loss of substance

while still compressing:

- machine scaffolding
- duplicate queue noise
- transport wrappers

## North Star

Still the same:

- source content: Claude session `.jsonl`
- target reading feel: a saved Claude terminal transcript

But this phase adds a stronger content-preservation rule:

- real written content stays full
- only machine scaffolding gets collapsed

## What Success Looks Like

Success means:

- user messages are preserved in full
- assistant messages are preserved in full
- subagent final outputs are preserved in full
- subagent outputs are clearly labeled and grouped
- queue/polling/transport chatter is still compressed
- long substantive content is no longer treated as something to trim just because it is long

## Core Principle

The replay should distinguish between two classes of data:

1. Authored content
   - user prompts
   - assistant replies
   - subagent final reports
   - plans, audits, specs, writeups

2. Machine scaffolding
   - queue operations
   - launch acknowledgements
   - polling checks
   - repeated completion transport
   - low-value metadata

The first class should be preserved in full.
The second class may be compacted.

## Phase 1: Define What Counts As Authored Content

We need explicit rules for what should never be truncated in compact replay.

Preserve in full:

- user messages
- assistant messages
- subagent final report outputs
- any tool/result content that is clearly a real written report rather than a transport status

Compress:

- transport wrappers around those outputs
- polling and task retrieval noise
- queue metadata

## Phase 2: Detect Subagent Final Outputs

We need to identify when a tool result or task retrieval contains a real final report rather than a short status.

Examples:

- `retrieval_status=success` with a long written report in output
- task completion notification with a linked or embedded final report

These should be upgraded from “result line” into a full output block.

## Phase 3: Introduce Explicit Subagent Output Blocks

Instead of showing long subagent content as a single `result:` line, render it as a labeled block such as:

- `Subagent output: Audit payment flow`

followed by the full content.

This makes it obvious:

- where the content came from
- what task produced it
- that it is substantive output, not transport noise

## Phase 4: Preserve Full Main-Thread Messages

Ensure the renderer never truncates:

- assistant report bodies
- long user instructions

The replay should preserve these exactly as written in the session, subject only to formatting improvements, not summarization.

## Phase 5: Keep Transport Noise Compact

Even with full content preservation, we still need the replay to stay readable.

So compact:

- launch acknowledgements
- repeated “not ready” checks
- raw tool transport wrappers
- duplicate queue notifications

The key is:

- preserve substance
- compress scaffolding

## Phase 6: Distinguish Final Output From Polling Output

Task output checks can return:

- not ready
- partial/in-progress state
- completed final report

Only the last one should expand into a full output block.

The first two should stay short.

## Phase 7: Improve Visual Structure For Long Outputs

Long outputs should not just be dumped inline as if they were ordinary status lines.

They need clear structure:

- label
- spacing
- maybe a fenced block or clearly separated section

This makes long forensic replay readable instead of overwhelming.

## Phase 8: Preserve Traceability

Even while preserving full content, each expanded subagent output should still make clear:

- task name
- relation to the surrounding assistant turn
- whether it came from a subagent completion or retrieval

This keeps the replay understandable.

## Phase 9: Validate On Real Long-Output Sections

Re-run slices where:

- subagents returned full audit reports
- assistant pasted long plans
- hidden conversation sections include large blocks of real content

Check:

- was full authored content preserved
- was machine noise still compressed
- can a human clearly tell main-thread and subagent content apart

## Deliverables

At the end of this phase, we should have:

- explicit authored-content preservation rules
- subagent final output detection
- full subagent output blocks
- no truncation of substantive user/assistant/subagent content
- compact treatment of machine scaffolding only

## Acceptance Test

We have succeeded if:

- a long assistant answer appears in full
- a long subagent audit report appears in full
- the replay clearly shows where a subagent was launched, completed, and what full content it produced
- transport noise remains compact enough that the replay is still readable

## Simple Summary

The next phase is to preserve all real written content in full, especially subagent final outputs, while compressing only queue and transport scaffolding so the replay becomes a true forensic transcript instead of a summarized event log.
