# Claude Session Replay

Turn raw Claude Code session `.jsonl` logs into readable conversation history.

`claude-session-replay` is a small CLI tool for people who want to inspect local Claude Code session logs without reading raw JSON. It parses the event stream and renders a cleaner transcript you can open in VS Code.

## What It Does

Claude Code stores local session history as `.jsonl` files containing events such as:

- user messages
- assistant messages
- tool calls
- tool results
- queue events
- progress/status events
- subagent activity

This project converts that machine-oriented event stream into a readable replay.

Current behavior:

- preserves user and assistant messages in full
- preserves long subagent outputs in full
- groups related events into readable turns
- humanizes task launches, task-output checks, and completion notes
- compresses low-value transport noise
- renders slices by raw line number

## Quick Start

If you already know which `.jsonl` file you want, this is the shortest path:

```bash
cd /path/to/claude-session-replay

PYTHONPATH=src python3 -m claude_session_replay.cli render \
  --input "/path/to/session.jsonl" \
  --format grouped \
  --view compact \
  --include-tools \
  --output replay.txt

open -a "Visual Studio Code" replay.txt
```

## Why Use It

Opening a Claude session `.jsonl` directly is possible, but unpleasant:

- each line is a JSON object
- message content is mixed with metadata
- tool activity is interleaved with chat
- long sessions are hard to follow

This tool gives you:

- a readable transcript
- clearer speaker boundaries
- better handling for subagent outputs
- a workflow that fits naturally in VS Code

## Where Claude Session Logs Usually Live

Typical local Claude Code project sessions live under:

```text
~/.claude/projects/
```

Example shape:

```text
~/.claude/projects/
  -Users-you-Desktop-MyRepo/
    session-a.jsonl
    session-b.jsonl
    ...
```

## How Hard Is It To Use

Low effort if you already know which `.jsonl` file you want.

Typical workflow:

1. find the session file
2. run one command to render it
3. open the output in VS Code

If you do not know the right session file yet, the hardest part is usually identifying which `.jsonl` contains the conversation you care about.

## Install / Requirements

The repo runs directly with Python 3.9+.

No packaging step is required for normal use:

```bash
cd /path/to/claude-session-replay
PYTHONPATH=src python3 -m claude_session_replay.cli --help
```

## Basic Usage

### Inspect A Session File

See the rough event mix inside a `.jsonl`:

```bash
cd /path/to/claude-session-replay

PYTHONPATH=src python3 -m claude_session_replay.cli inspect \
  --input "/path/to/session.jsonl"
```

### Render A Readable Replay

```bash
cd /path/to/claude-session-replay

PYTHONPATH=src python3 -m claude_session_replay.cli render \
  --input "/path/to/session.jsonl" \
  --format grouped \
  --view compact \
  --include-tools \
  --output replay.txt
```

Open the result:

```bash
open -a "Visual Studio Code" replay.txt
```

### Render Only Part Of A Session

```bash
cd /path/to/claude-session-replay

PYTHONPATH=src python3 -m claude_session_replay.cli render \
  --input "/path/to/session.jsonl" \
  --format grouped \
  --view compact \
  --include-tools \
  --from-line 5000 \
  --to-line 5600 \
  --output replay-slice.txt
```

If you omit `--to-line`, rendering continues to the end of the file.

## Output Modes

### `--format plain`

Closer to a normalized event dump.

Useful if you want:

- lower-level event visibility
- simpler output
- debugging of parser behavior

### `--format grouped`

The main reading mode.

Useful if you want:

- readable turns
- grouped assistant/tool/task activity
- preserved long-form outputs
- a much more human-readable replay

### `--view compact`

Best for everyday reading.

It:

- compresses transport noise
- humanizes launches, checks, and results
- preserves full authored content
- expands long completed subagent outputs into full labeled blocks

### `--view detailed`

Keeps more literal event detail.

Best when:

- you want more traceability
- compact mode is too opinionated for the task

## What Gets Preserved In Full

This tool is intentionally biased toward preserving real authored content.

Preserved in full:

- user messages
- assistant messages
- long assistant reports
- long prompts/specs/audits
- long completed subagent outputs
- ASCII diagrams, trees, tables, and text layouts written as message content

Compacted:

- queue plumbing
- launch acknowledgements
- repeated completion transport
- polling chatter
- other low-value machine scaffolding

## Example Output

Short example:

```text
[USER | 2026-01-01T12:00:00Z]
Read the prompt file and run the audit.

[ASSISTANT | 2026-01-01T12:00:04Z]
Launching the audit now.
status: Launched subagent: Frontend audit

[ASSISTANT | 2026-01-01T12:02:11Z]
Frontend audit complete. Let me pull the full report.
action: Checked task output: Frontend audit

=======================================================
  SUBAGENT OUTPUT: FRONTEND AUDIT
=======================================================
...full report content...
```

This is the current design goal:

- main conversation stays readable
- long substantive subagent output stays intact
- machine scaffolding stays compact

## Typical Workflow

1. Find the session file you care about.
2. Render a full replay or a line-range slice.
3. Open the result in VS Code.
4. If needed, rerender a smaller range around the part you care about.

## How To Find The Right Session

If you know the session ID already, use that file directly.

If not, search by phrase:

```bash
rg -n -F "exact phrase from the conversation" ~/.claude/projects
```

Or list the newest session files in a project directory:

```bash
ls -lt ~/.claude/projects/<project-folder>/*.jsonl | head
```

## Repo Layout

```text
claude-session-replay/
  docs/development/   # optional implementation notes
  src/claude_session_replay/
    cli.py
    parser.py
    grouping.py
    renderers.py
    models.py
  tests/
  README.md
  pyproject.toml
```

### Key Files

- `parser.py`
  - reads raw `.jsonl`
  - normalizes messages, statuses, tool calls, and tool results

- `grouping.py`
  - groups normalized events into readable turns
  - attaches completion notes to the correct assistant follow-up

- `renderers.py`
  - turns grouped data into readable transcript output
  - preserves long authored outputs
  - renders full subagent output blocks

- `cli.py`
  - command-line entrypoint

## Limitations

This is a replay/readability tool, not a perfect Claude Code clone.

Current limitations:

- it does not recreate the live Claude terminal UI exactly
- it works best on text-based content rather than non-text UI elements
- some operator-note handling is still rough
- some display formatting is still flatter than the original terminal
- cross-session merging is not yet implemented

## Running Tests

```bash
cd /path/to/claude-session-replay
PYTHONPATH=src python3 -m pytest tests -q
```

## Project Status

This repo is already useful for its main purpose:

- extract Claude Code `.jsonl` history
- convert it into readable replay text
- inspect it comfortably in VS Code
- recover hidden prompts, audits, plans, and long-form session history

It is not a perfect replay UI, but it is already practical and usable.

**Note:** This is a one-off utility, not an actively maintained project. It does what it needs to do. Feel free to fork and extend if you want more features.

## License

MIT — see [LICENSE](LICENSE).
