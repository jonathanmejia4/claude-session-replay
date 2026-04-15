# Humanized Completion Display Plan

## Goal

Make completion lines in the reconstructed transcript read like human status notes instead of raw queue transport records.

## Problem We Are Solving

Right now completion lines still look like machine-oriented status strings, for example:

- `enqueue: Agent "Audit payment flow" completed | status=completed | task_id=abc`

That is understandable, but it is not pleasant to read and it does not match the goal of a Claude-Code-like replay.

## What We Want Instead

We want default grouped output to show completion lines in a cleaner form, such as:

- `status: Agent "Audit payment flow" completed`

Optionally, more detailed modes can still expose extra metadata when useful, but compact grouped output should prioritize readability.

## What Success Looks Like

Success means:

- completion lines read like plain status notes
- queue-specific prefixes disappear from the default compact view
- redundant metadata is hidden unless needed
- the transcript becomes easier to scan in VS Code

## Core Idea

We should introduce a display-layer transformation for status lines.

The source event remains unchanged, but the displayed line is rewritten into a human-friendly form.

This keeps:

- parsing accuracy
- debugging path availability

while improving:

- readability
- visual flow

## Phase 1: Identify Status Shapes To Rewrite

We need to define the common machine-shaped lines that should be humanized.

Examples:

- `enqueue: Agent "..."`
- `status=completed`
- `task_id=...`
- token and duration metadata blocks

This phase gives us the rewrite targets.

## Phase 2: Define Compact Display Rules

For compact grouped output:

- keep the most meaningful phrase
- drop queue transport prefixes
- drop repetitive task identifiers
- drop token usage unless explicitly useful

The compact display should emphasize what happened, not how the transport layer encoded it.

## Phase 3: Keep Detailed Mode Richer

We should not throw information away globally.

Detailed grouped output can still retain:

- task IDs
- token usage
- duration
- raw-ish status strings when useful

This keeps the tool useful for debugging while making compact mode easier to read.

## Phase 4: Rewrite Completion Lines

Implement a humanization pass that transforms known completion lines into simple readable output.

Examples:

- `enqueue: Agent "Audit payment flow" completed | status=completed | task_id=abc`
  becomes
  `Agent "Audit payment flow" completed`

- task notification variants should normalize to the same display text

This also helps dedupe because equivalent completion variants will end up with the same displayed form.

## Phase 5: Rewrite Other Low-Value Status Noise

After completion lines, we can apply the same idea to other status lines that are still too machine-heavy.

Examples:

- task retrieval statuses
- queue/pop wording
- redundant state markers

This phase should be conservative and avoid hiding meaning.

## Phase 6: Validate Against Real Slices

We should rerun:

- the marketing-agency slice
- multi-agent audit slices

We are checking:

- whether the output is easier to skim
- whether important context is preserved
- whether dedupe still works correctly

## Deliverables

At the end of this phase, we should have:

- a status humanization pass
- cleaner compact grouped output
- detailed mode still available when needed
- updated tests for status rewriting

## Acceptance Test

We have succeeded if:

- completion lines in compact grouped output read like plain-English status notes
- the transcript is easier to scan without losing the meaning of what completed
- the replay feels less like queue logs and more like a readable session transcript

## Simple Summary

The next refinement is to rewrite machine-shaped completion lines into short human-readable status notes so the grouped replay reads more naturally in VS Code.
