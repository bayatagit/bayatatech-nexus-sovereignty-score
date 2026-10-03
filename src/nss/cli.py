"""Command line interface for the Nexus Sovereignty Score."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nss import __version__
from nss.scoring import NSSInputError, score


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nss", description="Nexus Sovereignty Score")
    subparsers = parser.add_subparsers(dest="command", required=True)

    score_parser = subparsers.add_parser("score", help="Score an assessment input file")
    score_parser.add_argument("input_json", type=Path, help="Path to assessment JSON")
    score_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    score_parser.add_argument(
        "--output",
        type=Path,
        help="Write result to FILE instead of stdout",
    )

    subparsers.add_parser("version", help="Print package version")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        print(__version__)
        return 0

    if args.command == "score":
        try:
            with args.input_json.open(encoding="utf-8") as handle:
                assessment = json.load(handle)
            result = score(assessment)
        except NSSInputError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        except (OSError, json.JSONDecodeError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

        indent = 2 if args.pretty else None
        payload = json.dumps(result, indent=indent, ensure_ascii=True)
        if args.output is not None:
            args.output.write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
