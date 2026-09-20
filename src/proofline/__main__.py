"""Command-line entry point for local fixture reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import analyze_manifest
from .model import ValidationError, load_manifest
from .report import render_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a deterministic Proofline evidence brief.")
    parser.add_argument("manifest", type=Path, help="Path to one bounded JSON manifest")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path, help="Optional output file")
    args = parser.parse_args(argv)

    try:
        report = analyze_manifest(load_manifest(args.manifest))
    except ValidationError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        output = render_markdown(report)
    else:
        output = json.dumps(report, indent=2, sort_keys=True) + "\n"

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
