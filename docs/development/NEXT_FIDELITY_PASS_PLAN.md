# Next Fidelity Pass Plan

## Goal

Address the next four issues identified by comparing the replay against the saved Claude terminal transcript:

- launch actions are duplicated as both `status` and `tool`
- some task checks still show task IDs instead of task names
- leaked operator or instruction text still shows up as generic `status:` lines
- the replay is still flatter than the saved transcript

## Why This Plan Exists

The replay is now clearly readable, but comparison against the north star still shows a few recurring mismatches that keep it from feeling like a terminal replay:

- duplicated action lines make the output noisy
- fallback-to-ID task checks make the output harder to scan
- operator text is being misclassified
- the visual hierarchy between narrative and actions is still too weak

This phase focuses on fixing those gaps.

## North Star

Still the same:

- source content: Claude session `.jsonl`
- target reading feel: a saved Claude terminal transcript

## What Success Looks Like

Success means:

- launch actions appear once, not twice
- task checks and results usually refer to task names, not task IDs
- injected operator instructions are shown as notes or separate guidance, not generic system status
- action lines look more like terminal actions and less like flat prefixed rows

## Phase 1: Remove Duplicate Launch Display

Right now a launch can appear as:

- `status: Launched subagent: ...`
- `tool: Launched subagent: ...`

We need one canonical display path for launches in compact grouped output.

Preferred outcome:

- keep launch as one readable line
- do not repeat the same launch under both status and tool

This likely means either:

- suppressing the tool launch line when the status launch is already present
- or treating launch actions as tool lines only and hiding the status variant

## Phase 2: Strengthen Task Name Memory

Some task output checks still fall back to opaque task IDs because the task name was not carried far enough through grouping.

We should maintain a stronger task map:

- task ID -> task description

This map should be available when rendering:

- task checks
- retrieval results
- completion notices

Success here means task names appear whenever they have already been seen earlier in the replay.

## Phase 3: Reclassify Operator Text

Some queue-originated text is not system status at all. It is operator guidance or human instruction, for example:

- `hey check the production website not the local one ...`

These should not render as:

- `status: ...`

We should classify them separately, likely as:

- `note: ...`

or another distinct display type that makes clear this is human guidance, not task state.

## Phase 4: Add Better Action Hierarchy

The replay still feels flatter than the saved transcript because every supporting line uses the same basic format.

We should introduce a stronger visual distinction between:

- assistant narrative
- status lines
- actions
- results
- notes

Without changing the underlying content, we can improve the shape by:

- using clearer prefixes
- adding indentation or stronger visual separation
- making action lines feel secondary to assistant text

This is a formatting pass after the semantic cleanup.

## Phase 5: Keep Detailed Mode Conservative

Compact mode can become more opinionated.

Detailed mode should remain closer to normalized events so the replay is still useful for debugging and inspection.

That means:

- compact mode gets the new dedupe, task-name substitution, operator-note handling, and stronger formatting
- detailed mode stays more literal

## Phase 6: Validate Against Real Slices

Re-run:

- early multi-agent audit slice
- marketing agency slice

Check specifically:

- are launches still duplicated
- do task checks still show IDs
- are operator notes still misclassified
- does the visual hierarchy feel better

## Deliverables

At the end of this phase, we should have:

- deduplicated launch rendering
- better task-name propagation
- operator-note classification
- improved action-line formatting
- updated tests covering these changes

## Acceptance Test

We have succeeded if:

- a launch only shows once in compact replay
- task checks mostly read with task names
- operator text no longer looks like machine status
- the replay feels more like a terminal action log with narrative on top

## Simple Summary

The next fidelity pass removes duplicated launches, improves task-name carry-through, separates operator guidance from status, and adds stronger action-line formatting so the replay feels closer to the saved terminal transcript.
