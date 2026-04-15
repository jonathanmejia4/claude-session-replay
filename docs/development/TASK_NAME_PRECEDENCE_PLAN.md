# Task Name Precedence Plan

## Goal

Fix task-name carry-through so canonical task names come from launch descriptions first, not from later completion summaries.

## Problem We Are Solving

One remaining fidelity issue is that some task checks and retrieval results use completion text as the task name, for example:

- `Checked task output: Agent "Audit dashboard frontend pages" completed`
- `Retrieved completed output: Agent "Audit dashboard frontend pages" completed`

That is wrong. The canonical task name should be:

- `Audit dashboard frontend pages`

The replay is currently learning task names from multiple sources, and completion summaries are sometimes overriding the original launch description.

## What We Want Instead

The task registry should prefer the most stable and human-meaningful name source.

Priority should be:

1. Launch description
2. Explicit task name from tool call metadata
3. Progress label if it matches the task
4. Completion summary only as a last resort

That way later task checks and retrieval results keep the original clean task name.

## What Success Looks Like

Success means:

- task checks use the launch description when available
- completion summaries do not overwrite better names
- results use stable human task names consistently
- the replay reads more like a continuous terminal session

## Core Idea

We need a task-name registry with precedence rules, not just “first or last seen string wins.”

Each task name source should carry a quality level.

When a new candidate arrives for the same task ID:

- replace the stored name only if the new source is better
- keep the old name if the new source is lower quality

## Phase 1: Define Name Source Priorities

Set a clear ranking for task name sources.

Proposed priority:

1. launch description from queue/tool launch
2. explicit task name from tool metadata
3. progress label
4. completion summary

This becomes the rule for the registry.

## Phase 2: Store Name With Source Quality

Instead of storing:

- `task_id -> task_name`

store:

- `task_id -> (task_name, source_priority)`

This allows the registry to decide whether a newly observed name should replace the old one.

## Phase 3: Prevent Completion Summaries From Overwriting Better Names

If a task already has a launch-derived name, and a later completion line arrives like:

- `Agent "Audit dashboard frontend pages" completed`

then the registry should keep:

- `Audit dashboard frontend pages`

and ignore the completion-derived variant for canonical naming.

## Phase 4: Normalize Completion-Derived Names

If completion summaries are ever used as a fallback source, clean them before storing:

- strip `Agent "..." completed`
- keep just the task name text

This ensures fallback names are still usable if no better source exists.

## Phase 5: Validate Against Real Replay Slices

Re-run the early multi-agent slice and look specifically for:

- task checks that used to show completion text as the task name
- retrieval lines that inherited the wrong name

We want those lines to use the original launch description instead.

## Deliverables

At the end of this phase, we should have:

- a precedence-based task-name registry
- normalized fallback names from completion summaries
- cleaner action/result lines in compact replay
- tests covering precedence behavior

## Acceptance Test

We have succeeded if:

- `Checked task output: Audit dashboard frontend pages`
  replaces
  `Checked task output: Agent "Audit dashboard frontend pages" completed`

- completion summaries no longer poison the canonical task-name map

## Simple Summary

The next refinement is to give task names source-based precedence so the replay keeps the original launch description as the canonical task name instead of accidentally learning the noisier completion summary version.
