"""Command-line entry point for local fixture reports and check execution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import analyze_manifest
from .model import ValidationError, load_manifest
from .registry import lookup
from .report import render_html, render_markdown
from .runner import run_check


def _cmd_report(args: argparse.Namespace) -> int:
    """Existing manifest-report subcommand (formerly the only command)."""
    try:
        report = analyze_manifest(load_manifest(args.manifest))
    except ValidationError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        output = render_markdown(report)
    elif args.format == "html":
        output = render_html(report)
    else:
        output = json.dumps(report, indent=2, sort_keys=True) + "\n"

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


def _cmd_run_check(args: argparse.Namespace) -> int:
    """Explicit run-check subcommand.

    Resolves check_id through the static registry and dispatches to the
    appropriate bounded handler.  The check_id is the ONLY untrusted input;
    unknown or injection-shaped IDs return blocked without launching anything.

    No arbitrary command passthrough is possible: the registry and dispatch
    table are code-owned and immutable at runtime.
    """
    check_id: str = args.check_id

    # Guard: reject IDs not in the registry before any dispatch.
    # run_check also enforces this, but an explicit gate here makes the
    # CLI's own security boundary visible and testable.
    if lookup(check_id) is None:
        print(
            f"blocked: check ID {check_id!r} is not in the static registry; "
            "no process was launched.",
            file=sys.stderr,
        )
        return 1

    result = run_check(check_id)
    print(json.dumps({"check_id": result.check_id, "result": result.result,
                      "evidence_class": result.evidence_class},
                     indent=2))
    return 0 if result.result == "pass" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Proofline: evidence-backed release readiness.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- report subcommand (original behavior, now explicit) ---
    report_parser = subparsers.add_parser(
        "report",
        help="Create a deterministic evidence brief from a manifest.",
    )
    report_parser.add_argument("manifest", type=Path, help="Path to one bounded JSON manifest")
    report_parser.add_argument("--format", choices=("json", "markdown", "html"), default="json")
    report_parser.add_argument("--output", type=Path, help="Optional output file")

    # --- run-check subcommand ---
    run_check_parser = subparsers.add_parser(
        "run-check",
        help="Invoke one registered local check by its stable check ID.",
    )
    run_check_parser.add_argument(
        "check_id",
        help="Stable check ID from the static registry (e.g. check-local-contracts).",
    )

    # Detect legacy invocation (python -m proofline <manifest> [--format ...])
    # before argparse errors out.  When argv is None we use sys.argv[1:].
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    if raw_args and raw_args[0] not in ("report", "run-check") and not raw_args[0].startswith("-"):
        # First token is not a known subcommand and not a flag — treat as the
        # legacy positional manifest path and re-parse with "report" injected.
        return main(["report"] + raw_args)

    args = parser.parse_args(argv)

    if args.command == "report":
        return _cmd_report(args)
    if args.command == "run-check":
        return _cmd_run_check(args)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
