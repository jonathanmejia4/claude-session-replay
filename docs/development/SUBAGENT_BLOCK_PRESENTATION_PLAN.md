# Subagent Block Presentation Plan

## Goal

Make long subagent output blocks visually distinct enough that you can immediately tell they are separate subagent reports and not part of the surrounding main-thread assistant message.

## Problem

The content is now preserved correctly, but visually it can still blur together:

- assistant says something
- then a long subagent block appears
- then another assistant update follows

Even if the labels are correct, long blocks can still feel like part of the assistant’s own body unless the structure is stronger.

## What Success Looks Like

Success means:

- long subagent outputs are instantly recognizable as separate blocks
- you can tell which task produced the block
- main-thread assistant narrative remains visually primary
- multiple subagent outputs near each other do not run together
- the replay becomes easier to scan in VS Code

## Core Idea

Do not change the content. Change the containment and layout.

The fix is presentation, not parsing:

- clearer labels
- clearer spacing
- consistent block boundaries
- optional visual wrappers

## Phase 1: Define A Distinct Subagent Block Style

Choose one consistent visual style for full subagent outputs.

Good candidates:

- fenced block with a labeled header
- divider lines before and after
- indented block under a `Subagent Output` heading

Example concept:

- `Subagent Output: Audit dashboard frontend pages`
- clear separator
- full report body
- closing separator or blank spacing

The important part is consistency.

## Phase 2: Separate Main Thread From Subagent Thread

Make the assistant’s own message visually different from embedded subagent output.

Conceptually:

- assistant body remains plain narrative text
- subagent output becomes a contained child block

That makes it obvious what the assistant is saying versus what the retrieved subagent report says.

## Phase 3: Improve Spacing Around Long Blocks

Long blocks need more breathing room.

Rules:

- blank line before a subagent block
- blank line after a subagent block
- stronger separation if another subagent block follows nearby

This alone will improve readability a lot.

## Phase 4: Add Stronger Labels

Make labels harder to miss.

Instead of a light prefix only, use a heading-like label such as:

- `Subagent Output: Audit payment flow`
- `Subagent Output: Frontend audit`

That label should sit above the block, not inline with the first line of content.

## Phase 5: Handle Multiple Adjacent Subagent Blocks

If two or more long subagent outputs appear close together:

- each needs its own clearly separated container
- do not let them run one after another with only minimal spacing

This is especially important for audit-style sessions.

## Phase 6: Keep Compact And Detailed Behavior Sensible

Compact mode:

- still preserve full long subagent output
- but use the clearer containment style

Detailed mode:

- may preserve even more surrounding metadata
- but should still use the same containment pattern for long subagent content

So the containment pattern should become the standard way long subagent content is shown.

## Phase 7: Validate Against Real Multi-Block Sections

Test on a real slice where:

- assistant messages
- subagent reports
- follow-up summaries

appear close together

Check:

- can you instantly spot where subagent output begins and ends
- does the assistant thread remain easy to follow
- do multiple long blocks remain distinct

## Deliverables

At the end of this phase, we should have:

- one consistent visual container style for long subagent outputs
- clearer separation between assistant narrative and subagent content
- better spacing around long blocks
- improved readability in VS Code without changing the underlying content

## Acceptance Test

We have succeeded if:

- you can scan a replay and instantly identify subagent report sections
- long retrieved reports no longer visually blend into the assistant’s own narrative
- multiple nearby subagent outputs remain clearly separated

## Simple Summary

The next step is to keep all long subagent content intact but render it inside a stronger visual container so it reads as a distinct subagent report, not as part of the main assistant message.
