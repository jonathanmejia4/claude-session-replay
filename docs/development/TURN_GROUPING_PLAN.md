# Turn Grouping And Tool Display Plan

## Goal

Make the reconstructed transcript feel more like one readable conversation by combining related pieces into a single visible turn and making tool activity easier to follow.

## Problem We Are Solving

Right now the parser is readable, but still too literal.

What is happening now:

- one assistant message may appear
- then a tool call
- then a tool result
- then queue noise
- then a status line
- then another assistant message

That is technically accurate, but it still feels fragmented.

What we want instead:

- one human-readable turn
- with the assistant message and its related actions grouped together
- so the flow reads more like what a person saw in Claude Code

## What Success Looks Like

Success means:

- related assistant message, tool call, and tool result appear as one coherent block
- background queue noise does not interrupt the conversation
- task completions are summarized instead of dumped twice
- subagent activity is readable without overwhelming the main thread
- the replay feels closer to `Terminal Saved Output.txt`

A strong success condition:

- when reading a reconstructed slice, you can follow the conversation without mentally stitching together six separate event types

## North Star

Still the same:

- content source: the raw Claude session `.jsonl`
- visual and reading target: a saved Claude terminal transcript

This phase is specifically about improving the structure of the reconstructed output so it behaves more like that terminal transcript.

## What We Need To Improve

There are two main areas:

1. Turn merging
   - decide which events belong together
   - present them as one visible unit
2. Tool display
   - show tool use clearly
   - avoid flooding the transcript with raw machine detail

## Phase 1: Define What A Turn Is

We need a clear rule for what counts as one visible turn.

A turn should usually be:

- one user message
- or one assistant response
- plus any directly related tool activity and status updates

Examples:

- assistant says “I’m checking that now”
- assistant launches a task
- task launch succeeds

These should likely display as one assistant turn, not three disconnected entries.

This phase creates the rules for grouping.

## Phase 2: Define Event Relationships

We need to figure out how events connect to each other.

Examples of relationships:

- a tool result belongs to the tool call that caused it
- a queue event belongs to a task launch
- a task notification belongs to a specific subagent or task
- a later assistant update may be summarizing earlier tool output

This phase gives us the logic needed to know what should be merged.

## Phase 3: Create Turn Buckets

Instead of rendering events one by one, we first collect them into buckets.

A bucket may contain:

- main speaker text
- tool actions
- tool results
- status lines
- task notifications

The important shift is:

- raw events are no longer the thing we render directly
- grouped turns become the thing we render

This is the structural change that improves readability.

## Phase 4: Merge Common Patterns

We should explicitly handle the common event shapes that repeat in Claude sessions.

Important patterns:

- assistant tool call followed immediately by tool result
- queue enqueue plus task notification for the same task
- assistant says it is checking something, then `TaskOutput`, then completion result
- background progress lines that only exist to support a later assistant update

We do not need perfect intelligence.
We need good handling of the most common patterns first.

## Phase 5: Reduce Duplicate Information

Some information appears multiple times in slightly different forms.

Examples:

- queue enqueue says a task completed
- task notification says the same task completed
- tool result also contains the completion result

We should choose the most human-useful version and suppress or compress the others.

Goal:

- one meaningful display of the event
- not three versions of the same thing

## Phase 6: Design Better Tool Display

Tool activity should be present, but compact.

What good tool display should do:

- show what tool or action was used
- show why it mattered
- show the outcome briefly
- avoid dumping raw payloads unless needed

Good tool display should answer:

- what was done
- what came back
- whether it mattered

Examples of better presentation:

- `Launched subagent: Audit payment/Stripe flow`
- `Subagent completed: Audit payment/Stripe flow`
- `Checked task output: not ready`
- `Checked task output: completed`

This is much easier to read than raw XML-like or JSON-like blobs.

## Phase 7: Handle Background Subagent Activity More Cleanly

Subagent activity is one of the biggest readability problems.

We need a display rule for it.

Good options:

- keep it inline, but very compact
- or show it as a short child section under the parent assistant turn

The key idea:

- subagent details should support the main conversation
- they should not overpower it

This phase focuses on making multi-agent sessions readable.

## Phase 8: Add Display Levels

Not every user wants the same amount of detail.

We should support at least two reading modes:

1. Compact mode
   - mostly main conversation
   - short summaries of tools and tasks
2. Detailed mode
   - main conversation plus tool and task activity
   - still readable, but more forensic

This makes the tool useful both for quick reading and deeper investigation.

## Phase 9: Compare Against Real Transcript Segments

We should use overlapping slices from the raw session and `Terminal Saved Output.txt` and compare them.

Questions to check:

- did we group the same things together a human would expect
- are tool events interrupting too much
- are we hiding too much useful context
- does the transcript now read more naturally

This phase is how we validate improvements instead of guessing.

## Phase 10: Lock In A Stable Rendering Style

Once grouping is working, we should standardize how a visible turn is shown.

Each turn should consistently show:

- speaker
- main message
- optional tool activity
- optional result summary
- optional status or task note

Consistency matters because the main goal is making long sessions easy to scan.

## What We Are Not Doing Yet

This phase is not:

- rebuilding the full Claude UI
- making a browser app
- making a perfect terminal clone
- solving every event type in the whole system

This phase is specifically about:

- better grouping
- better tool display
- better readability

## Deliverables For This Phase

At the end of this phase, we should have:

- a clear definition of turn grouping rules
- improved parser logic for related-event merging
- improved rendering rules for tool activity
- at least two output styles:
  - compact
  - detailed
- transcript slices that are noticeably closer to `Terminal Saved Output.txt`

## Acceptance Test

We have succeeded if:

- you open a reconstructed file in VS Code
- a single assistant action reads like one turn instead of many fragments
- tool activity supports the conversation instead of cluttering it
- you can follow complex sections like the agency-to-public-API pivot with much less mental stitching

## Simple Summary

The next improvement phase is to stop rendering raw events one by one and instead group related events into human-readable turns, while rewriting tool activity into short meaningful summaries so the reconstructed transcript reads more like Claude Code and less like an event log.
