# Claude Session Replay Project Plan

## Goal

Build a separate tool that takes a raw Claude Code session file and produces a new readable file you can open in VS Code, so you can recover long hidden conversations without reading raw JSON.

## What We Are Reconstructing From

We have two source materials:

- The raw source of truth for the conversation data:
  `~/.claude/projects/<project-slug>/<session-uuid>.jsonl`
- The visual north star for how the output should feel:
  a saved terminal transcript from a real Claude Code session

So:

- the `.jsonl` file gives us the real content
- the terminal output file gives us the target reading experience

## North Star

The reconstructed output should feel like reading `Terminal Saved Output.txt`, not like reading raw machine logs.

That means the finished output should:

- read top to bottom like a real conversation
- make user and assistant turns obvious
- show tool activity in a way humans can follow
- reduce noise and metadata
- preserve enough structure that you can find where important conversations began and how they evolved

## Where It Will Be Viewed

Primary viewing target:

- a separate reconstructed file opened in VS Code

Why:

- fastest useful outcome
- easy to search
- easy to scroll
- easy to compare against the original files
- no need to build a whole interface first

So the workflow is:

1. raw `.jsonl` session goes in
2. reconstructed readable transcript file comes out
3. you open that new file in VS Code

## Project Location

Separate project folder:

- a standalone project directory

This stays separate from other projects so it is clearly its own tool.

## What The Tool Will Do

Conceptually, the tool will:

1. Read the raw Claude session file
2. Identify which parts are actual human-readable conversation
3. Separate useful content from machine noise
4. Group related events together
5. Write out a reconstructed transcript file in a cleaner structure

The output is not meant to be the original log. It is meant to be a human-readable reconstruction of it.

## Core Problem We Are Solving

The raw Claude session file is preserved, but it is not readable as a conversation because:

- it is machine-oriented
- events are split across many lines
- tool calls/results are mixed in with messages
- metadata overwhelms the actual discussion
- the original UI grouped and hid things that the raw file does not

We are solving that by rebuilding a readable version of the conversation.

## What Success Looks Like

Success means all of the following are true:

- You can point the tool at a Claude `.jsonl` session file.
- It generates a separate readable transcript file.
- You can open that file in VS Code and follow the conversation naturally.
- You can identify where important topic pivots happened.
- You can recover hidden planning discussions without manually decoding JSON.
- The output feels structurally closer to `Terminal Saved Output.txt` than to raw JSONL.

A stronger success condition:

- you can use the tool to recover the lost Public API planning conversation and read it comfortably enough to reconstruct Phase 6 and Phase 7 planning without going back to raw JSON

## What “Good Enough” Looks Like First

First version does not need to perfectly clone Claude Code.

First version is successful if:

- user turns are readable
- assistant turns are readable
- tool events are shown clearly but compactly
- irrelevant noise is reduced
- the order of the conversation is preserved

That is enough to make the session usable.

## What “Better Later” Looks Like

Later versions can get closer to Claude Code by:

- grouping turns more like the original interface
- formatting tool activity more like the original
- hiding internal noise automatically
- making long sections easier to skim
- improving the resemblance to the saved terminal transcript

## How We Are Doing It

The project will be built in phases.

## Phase 1: Define The Output We Want

We look at `Terminal Saved Output.txt` and treat it as the model for readability.

We identify:

- what a readable turn looks like
- how tool actions appear
- what should be hidden
- what should stay visible
- what the reconstructed transcript should emphasize

This phase gives us the target shape.

## Phase 2: Understand The Raw Session Structure

We inspect the Claude `.jsonl` file and identify its main event types.

We determine:

- which entries are user messages
- which are assistant messages
- which are tool calls
- which are tool results
- which are progress/status
- which are noise or internal bookkeeping

This phase gives us the raw ingredients.

## Phase 3: Create A Simpler Internal Conversation Model

Before rendering anything, we define a cleaner conceptual structure.

Instead of raw machine events, we convert everything into simpler categories like:

- user message
- assistant message
- tool call
- tool result
- status update

This phase gives us a stable foundation so the viewer is not tied directly to the raw file mess.

## Phase 4: Group Things The Way Humans Read Them

We determine what belongs together.

For example:

- assistant response plus the tool calls it triggered
- tool results that belong to one task
- repeated progress messages that should not dominate the output
- sequences that should appear as one readable chunk instead of many fragments

This is the step that makes the transcript actually understandable.

## Phase 5: Generate A Separate Reconstructed File

We output a new file specifically for reading.

This file should:

- preserve the order of the conversation
- label speakers clearly
- include tool activity in a compact readable form
- remove or compress noise
- resemble the feel of terminal transcript output

This is the main deliverable.

## Phase 6: Compare Against The North Star

We compare the reconstructed file to `Terminal Saved Output.txt`.

We ask:

- does it feel similarly readable
- are we exposing the same important parts
- are we hiding too much or too little
- are tool sections understandable
- can a human trace a discussion easily

This is how we judge whether the reconstruction is working.

## Phase 7: Improve Fidelity Using Reconstructed Source

We use the `claw-code` reconstruction as a guide for how terminal rendering and display likely worked.

This helps us improve:

- formatting
- grouping
- display conventions
- tool presentation
- markdown rendering

This phase improves similarity, but it comes after readability works.

## Why The Reconstructed Claude Source Helps

The reconstructed source is not our content source. The `.jsonl` is still the content source.

The reconstructed source helps us understand how the UI likely chose to display content.

So:

- `.jsonl` tells us what happened
- `Terminal Saved Output.txt` tells us what “good” looks like
- reconstructed source tells us how to get closer to that look

## Scope Boundaries

What this tool is doing:

- reconstructing a readable transcript from saved Claude session logs

What this tool is not doing:

- modifying the original session file
- restoring the exact live Claude TUI
- rebuilding Claude Code itself
- changing the content of the conversation

It is a replay/reconstruction tool, not a full clone.

## Deliverables

The project should produce:

- a standalone project folder
- a tool that reads raw Claude session JSONL
- a reconstructed readable transcript file
- documentation explaining:
  - what it takes in
  - what it outputs
  - how to use it
  - what success means
- a clear connection between:
  - the source JSONL
  - the reconstructed output
  - the north-star terminal transcript

## Milestones

1. Project folder exists and purpose is documented
2. Raw session structure is understood
3. Readable output format is defined
4. Reconstructed transcript file can be generated
5. Output is usable in VS Code
6. Output is compared against the north star
7. Fidelity improvements are added using reconstructed source behavior

## How We Will Know We Achieved The Original Goal

We achieved the goal if you can do this:

- take a large hidden Claude session
- run it through the tool
- open the reconstructed file in VS Code
- follow the important conversation without raw JSON decoding
- locate discussion pivots like the Public API planning thread
- use that reconstructed transcript as a reliable reading surface

That is the real acceptance test.

## Simple One-Line Summary

We are building a separate replay tool that reads raw Claude session history from `.jsonl`, reconstructs it into a new human-readable transcript file, and uses `Terminal Saved Output.txt` as the model for what the final reading experience should feel like.
