from __future__ import annotations

import argparse
from pathlib import Path

from .grouping import group_events_into_turns
from .parser import inspect_types, normalize_events
from .renderers import render_grouped_plain, render_markdown, render_plain


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="claude-session-replay")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect event and block type counts.")
    inspect_parser.add_argument("--input", required=True, help="Path to Claude session JSONL file.")
    inspect_parser.add_argument("--limit", type=int, default=None, help="Only inspect the first N records.")

    render_parser = subparsers.add_parser("render", help="Render a readable transcript.")
    render_parser.add_argument("--input", required=True, help="Path to Claude session JSONL file.")
    render_parser.add_argument("--output", help="Write transcript to this path instead of stdout.")
    render_parser.add_argument(
        "--format",
        choices=("markdown", "plain", "grouped"),
        default="plain",
        help="Transcript output format.",
    )
    render_parser.add_argument(
        "--view",
        choices=("detailed", "compact"),
        default="detailed",
        help="Detailed keeps more tool/status output; compact groups and suppresses more noise.",
    )
    render_parser.add_argument(
        "--include-tools",
        action="store_true",
        help="Include compact tool call and tool result events.",
    )
    render_parser.add_argument("--from-line", type=int, default=None, help="Only consider raw records from this line onward.")
    render_parser.add_argument("--to-line", type=int, default=None, help="Only consider raw records through this line.")
    render_parser.add_argument(
        "--max-events",
        type=int,
        default=None,
        help="Only render the first N normalized events.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "inspect":
        event_types, block_types = inspect_types(args.input, limit=args.limit)
        print("Event types")
        for name, count in event_types.most_common():
            print(f"  {name}: {count}")
        print("\nBlock types")
        for name, count in block_types.most_common():
            print(f"  {name}: {count}")
        return 0

    events = list(
        normalize_events(
            args.input,
            include_tools=args.include_tools,
            from_line=args.from_line,
            to_line=args.to_line,
        )
    )
    if args.max_events is not None:
        events = events[: args.max_events]

    if args.format == "markdown":
        rendered = render_markdown(events)
    elif args.format == "plain":
        rendered = render_plain(events)
    else:
        turns = group_events_into_turns(events, compact=args.view == "compact")
        rendered = render_grouped_plain(turns, compact=args.view == "compact")
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
