# Task Completion Grouping Plan

## Goal

Improve how background task completions appear in the reconstructed transcript so they attach cleanly to the assistant update that follows, instead of appearing as separate standalone system blocks.

## Problem We Are Solving

Right now the grouped output is cleaner than the raw event stream, but task completions still often show up like this:

1. system block says an agent completed
2. assistant message follows a few seconds later summarizing that completion

That is accurate, but it still reads as slightly fragmented.

What we want instead:

- the assistant update should be the main visible turn
- the related completion note should appear as supporting context inside that assistant turn
- system-only task completion blocks should appear only when there is no meaningful assistant follow-up nearby

## What Success Looks Like

Success means:

- task completion events no longer interrupt the conversation when the assistant immediately follows with a summary
- assistant turns feel more self-contained
- background completions still remain visible, but as context rather than noise
- the transcript reads more like a single flowing conversation

## North Star

The north star is still:

- source of truth content: the Claude session `.jsonl`
- reading and display target: a saved Claude terminal transcript

This phase improves how completion-related events are grouped so the replay better matches the way terminal output feels when read by a person.

## Core Idea

We should treat task completion notices as "pending context" for a short window.

If an assistant message follows soon after and clearly summarizes or reacts to that completion, the completion should attach to that assistant turn.

If no assistant follow-up appears, the completion can remain as its own visible system turn.

## Phase 1: Identify Completion Event Types

We need to define exactly which events count as task completion signals.

Likely candidates:

- queue-operation entries that say an agent completed
- task notification entries with completed status
- tool results that confirm a task is done

This phase gives us the set of events that should enter the "pending completion" buffer.

## Phase 2: Define A Holding Window

We need a simple rule for when to hold a completion instead of rendering it immediately.

Conceptually:

- if the next assistant message comes soon after, attach completion to it
- if enough time or unrelated events pass, render completion as its own system turn

This does not need to be perfect. It just needs to capture the common pattern well.

## Phase 3: Build A Pending Completion Buffer

Instead of emitting completion notices immediately, we place them in a temporary holding area.

Then:

- if the next assistant turn is the obvious consumer, move completion notes into that turn
- if not, flush them as a standalone system block

This is the main structural change.

## Phase 4: Attach Completion Notes To Assistant Turns

When an assistant message arrives after a completion, we attach the completion notes to that assistant turn as supporting status lines.

The assistant turn remains the main visible block.

The completion note becomes secondary context such as:

- `status: Agent "Audit payment flow" completed`

This makes the assistant summary feel grounded without breaking the flow.

## Phase 5: Avoid Bad Attachments

We should not attach completions blindly.

Cases to avoid:

- long unrelated gaps
- a new user message arriving first
- completions piling up across topic shifts

If the connection is weak, we should fall back to a standalone system turn.

## Phase 6: Handle Multiple Completions Gracefully

Sometimes several subagents complete near each other before the assistant responds.

We should support:

- multiple completion notes attaching to one assistant update
- deduping repeated notices for the same task
- keeping the list compact and readable

This matters for audit-style and multi-agent sessions.

## Phase 7: Preserve Debuggability

Even though we are grouping more aggressively, we should keep the raw normalized event path available.

That means:

- grouped output becomes more human-friendly
- detailed output remains available for debugging and edge cases

This prevents the grouped mode from becoming a black box.

## Phase 8: Validate Against Real Slices

We should test this on:

- the marketing-agency to API pivot section
- earlier multi-agent audit sections
- places where several subagents finish close together

Questions to check:

- does the assistant turn read more naturally
- did we attach the right completion notes
- did we accidentally hide useful information

## Deliverables

At the end of this phase, we should have:

- explicit completion detection rules
- a pending completion buffer in the grouping pass
- assistant turns that absorb nearby completion notes
- fallback behavior for completions with no assistant follow-up
- cleaner compact grouped output

## Acceptance Test

We have succeeded if:

- a completion followed quickly by an assistant summary appears as one coherent assistant turn
- fewer standalone system completion blocks interrupt the transcript
- multi-agent sections feel more like a readable conversation and less like a task queue dump

## Simple Summary

The next grouping improvement is to hold task completion notices briefly and attach them to the assistant message that follows, so the transcript reads as one flowing conversation instead of alternating between system completion blocks and assistant summaries.
