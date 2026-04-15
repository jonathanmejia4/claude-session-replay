# Forward Completion Attachment Plan

## Goal

Refine task completion grouping so completion notices prefer the next assistant summary when that pattern is obvious, instead of sometimes attaching backward to the prior assistant turn.

## Problem We Are Solving

The current completion buffer already reduces noise, but one awkward case remains:

1. assistant says an agent is still running
2. completion notice arrives
3. assistant follows with a summary like "Payment audit complete"

Right now, the completion may still appear attached to the earlier assistant turn rather than the later assistant summary.

That makes the transcript read slightly backwards.

## What We Want Instead

When the pattern is:

- assistant update
- completion notice
- assistant follow-up summary

the completion should usually attach to the later assistant summary, not the earlier assistant update.

The later assistant message is usually the one that actually interprets the completion for the reader.

## What Success Looks Like

Success means:

- completion notices attach to the assistant summary that reacts to them
- earlier assistant progress updates are not burdened with future completion context
- the transcript reads in a forward direction
- multi-agent sections feel more natural

## Core Idea

We should distinguish between:

- normal status lines that can attach to the current turn
- completion notices that should be held forward for the next assistant turn

That means completion notices should not be treated like ordinary status context.

## Phase 1: Separate Forward Completion State

Instead of letting completions behave like generic statuses, create a dedicated "forward completion" buffer.

This buffer exists specifically to attach to the next assistant summary when possible.

## Phase 2: Delay Completion Attachment

When a completion notice arrives:

- do not immediately attach it to the previous assistant turn
- hold it unless a flush rule says otherwise

This prevents backwards attachment.

## Phase 3: Define Flush Rules

We need clear cases for when the held completion should stop waiting and become visible on its own.

Likely flush rules:

- a user message arrives before an assistant summary
- too many unrelated events pass
- the buffered completions pile up without an assistant follow-up
- end of slice or file

If a flush rule triggers, render them as a standalone system turn.

## Phase 4: Prefer The Next Assistant Message

When the next assistant message arrives after buffered completions:

- attach those completions to that assistant turn
- dedupe them if multiple variants exist
- keep them as supporting status lines, not the main body

This makes the assistant summary feel properly grounded.

## Phase 5: Avoid Bad Forward Attachments

We should not blindly attach every completion to the next assistant message.

Bad cases:

- the next assistant message is clearly about a different topic
- a long unrelated tool sequence intervenes
- a new user request starts a different turn

If the connection is weak, fall back to a standalone system turn.

## Phase 6: Validate On Real Multi-Agent Segments

We should test this on:

- audit-style runs where many subagents complete
- the marketing-agency slice
- sections where assistant says "waiting", then "complete"

We are looking for:

- fewer backwards-looking attachments
- fewer awkward system interruptions
- more natural assistant summary turns

## Deliverables

At the end of this phase, we should have:

- a dedicated forward-completion attachment rule
- cleaner assistant summary turns
- fewer completion notes attached to the wrong assistant message
- updated tests covering forward attachment behavior

## Acceptance Test

We have succeeded if:

- a completion that lands between two assistant messages prefers the later assistant summary
- the earlier assistant progress message remains focused on the state at that moment
- the replay reads more like a human conversation and less like a timeline dump

## Simple Summary

The next refinement is to treat completion notices as forward-looking context that should usually attach to the next assistant summary, rather than backward-looking status that sticks to the previous assistant turn.
