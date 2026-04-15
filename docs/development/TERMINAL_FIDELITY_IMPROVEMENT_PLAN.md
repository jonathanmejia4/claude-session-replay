# Terminal Fidelity Improvement Plan

## Goal

Improve the replay so it feels materially closer to the saved Claude terminal transcript, not just a cleaned-up event log.

## Why This Plan Exists

A side-by-side comparison with a saved Claude terminal transcript showed that the replay is now readable, but it still differs from the north star in several important ways:

- task launch statuses are still too raw
- tool lines are still too literal
- tool result lines are too verbose and transport-heavy
- some user-injected queue text leaks through as generic status lines
- the overall formatting still feels like a normalized transcript instead of terminal actions

This plan addresses those gaps.

## North Star

We are still reconstructing from:

- source content: Claude session `.jsonl`
- target reading feel: `Terminal Saved Output.txt`

The goal is not a perfect clone, but a replay that feels much closer to the terminal transcript when read in VS Code.

## What Success Looks Like

Success means:

- task launches read like human actions, not JSON blobs
- task output checks read like deliberate terminal actions
- task results read like short outcomes, not raw transport payloads
- leaked queue/user text is classified and rendered more appropriately
- the transcript is easier to scan top-to-bottom
- the output feels more like a terminal replay and less like a log dump

## Problem Areas To Fix

### 1. Task Launch Statuses Are Too Raw

Current shape:

- `status: {"task_id":"...","description":"Audit authentication system",...}`

Desired shape:

- `status: Launched subagent: Audit authentication system`

### 2. Tool Calls Are Too Literal

Current shape:

- `tool: TaskOutput: task_id=... {"block": false, ...}`

Desired shape:

- `tool: Checked task output for Audit authentication system`

### 3. Tool Results Are Too Transport-Heavy

Current shape:

- raw `tool_result[...] <retrieval_status>not_ready</retrieval_status> ...`

Desired shape:

- `result: Task output not ready`
- `result: Retrieved completed output for Frontend audit`

### 4. User-Injected Queue Text Leaks Through

Current shape:

- arbitrary instruction text inside queue status blocks

Desired shape:

- either classify it separately as an instruction note
- or suppress it if it is just queue plumbing noise

### 5. Visual Structure Still Feels Too Flat

Current shape:

- transcript headings plus prefixed lines

Desired shape:

- stronger distinction between:
  - assistant narrative
  - status/action lines
  - tool checks
  - tool outcomes

The output should feel more like a sequence of terminal actions.

## Phase 1: Humanize Task Launch Statuses

Detect queue status lines that represent new subagent launches and rewrite them into clear readable actions.

Examples:

- `Launched subagent: Audit authentication system`
- `Launched subagent: Playwright test example.com landing`

This immediately removes the worst raw-JSON statuses.

## Phase 2: Humanize TaskOutput Tool Calls

Detect tool calls that mean “check current output for task X” and render them as readable action lines.

Examples:

- `Checked task output: Audit authentication system`
- `Checked task output: Landing page and known issues`

If the task name is not known, use the task ID only as a fallback.

## Phase 3: Humanize Retrieval Results

Detect tool results that represent task retrieval states and rewrite them into short readable outcomes.

Examples:

- `Task output not ready`
- `Retrieved completed output`
- `Retrieved completed output for Frontend audit`

Detailed mode can still keep more raw information if needed.

## Phase 4: Track Task Names By Task ID

To humanize TaskOutput and result lines properly, we should maintain a small in-memory mapping:

- task ID -> task description

This allows later task checks and results to render with names instead of opaque IDs.

This should happen during grouping or rendering, depending on where the information is easiest to carry.

## Phase 5: Reclassify User-Injected Queue Text

Identify queue lines that are not machine status but actual human instructions or prompts.

Examples:

- `hey check the production website not the local one ...`

These should not appear as normal system statuses.

Options:

- render as `note: ...`
- attach to the nearest assistant turn as operator input
- suppress obvious queue plumbing wrappers

This phase prevents misleading status output.

## Phase 6: Improve Visual Formatting

Once the content is more humanized, improve the visible shape of grouped replay output.

Ideas:

- use clearer prefixes:
  - `status:`
  - `action:`
  - `result:`
  - `note:`
- keep assistant body visually primary
- keep tool/status lines visually secondary

This is a formatting pass, not a parser rewrite.

## Phase 7: Keep Detailed Mode Intact

Compact mode should become much friendlier, but detailed mode should remain closer to the raw normalized event stream.

That means:

- compact mode prioritizes readability
- detailed mode prioritizes traceability

This preserves debuggability.

## Phase 8: Validate Against Real Transcript Slices

Re-run:

- early multi-agent audit slice
- marketing agency slice
- any slice with repeated task completions and TaskOutput checks

Compare against the north star and ask:

- are the launches readable
- are the checks readable
- are the results readable
- is the overall replay easier to follow

## Deliverables

At the end of this phase, we should have:

- humanized task launch statuses
- humanized task output checks
- humanized retrieval results
- better handling for injected instruction text
- more terminal-like grouped output
- updated tests for these transformations

## Acceptance Test

We have succeeded if:

- a long replay section reads like a sequence of assistant updates plus terminal actions
- raw JSON launch payloads are gone from compact mode
- raw retrieval payloads are replaced with short readable outcomes
- the replay is noticeably closer to `Terminal Saved Output.txt`

## Simple Summary

The next phase is to humanize task launches, task-output checks, task retrieval results, and leaked queue instruction text so the replay looks and reads more like a Claude terminal transcript instead of a normalized event log.
