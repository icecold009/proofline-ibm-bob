"""Command-line entry point for local fixture reports and check execution."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .engine import analyze_manifest
from .model import ValidationError, load_manifest
from .registry import lookup
from .report import render_html, render_markdown
from .runner import CheckRunResult, run_check


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _format_report(report: dict, output_format: str) -> str:
    if output_format == "markdown":
        return render_markdown(report)
    if output_format == "html":
        return render_html(report)
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def _cmd_report(args: argparse.Namespace) -> int:
    """Existing manifest-report subcommand (formerly the only command)."""
    try:
        report = analyze_manifest(load_manifest(args.manifest), generated_at=_utc_now())
    except ValidationError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 2

    output = _format_report(report, args.format)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


def _cmd_run_report(args: argparse.Namespace) -> int:
    """Explicitly run only registered checks referenced by this manifest."""
    try:
        manifest = load_manifest(args.manifest)
    except ValidationError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 2

    referenced = {ref for claim in manifest.claims for ref in claim.evidence_refs}
    results: dict[str, CheckRunResult] = {}
    for check in manifest.checks:
        if check.id in referenced and lookup(check.id) is not None:
            results[check.id] = run_check(check.id)

    report = analyze_manifest(
        manifest,
        generated_at=_utc_now(),
        runner_results=results,
    )
    output = _format_report(report, args.format)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


def _cmd_web(args: argparse.Namespace) -> int:
    from .web import serve

    return serve(host=args.host, port=args.port)


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
                      "evidence_class": result.evidence_class,
                      "source": result.source, "provenance": result.provenance,
                      "observed_at": result.observed_at},
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

    run_report_parser = subparsers.add_parser(
        "run-report",
        help="Explicitly run only referenced allowlisted checks, then create a report.",
    )
    run_report_parser.add_argument("manifest", type=Path, help="Path to one bounded JSON manifest")
    run_report_parser.add_argument("--format", choices=("json", "markdown", "html"), default="json")
    run_report_parser.add_argument("--output", type=Path, help="Optional output file")

    web_parser = subparsers.add_parser(
        "web",
        help="Start the local browser interface (does not execute checks).",
    )
    web_parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: loopback only)")
    web_parser.add_argument("--port", type=int, default=8765, help="HTTP port (default: 8765)")

    # Detect legacy invocation (python -m proofline <manifest> [--format ...])
    # before argparse errors out.  When argv is None we use sys.argv[1:].
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    if raw_args and raw_args[0] not in ("report", "run-check", "run-report", "web") and not raw_args[0].startswith("-"):
        # First token is not a known subcommand and not a flag — treat as the
        # legacy positional manifest path and re-parse with "report" injected.
        return main(["report"] + raw_args)

    args = parser.parse_args(argv)

    if args.command == "report":
        return _cmd_report(args)
    if args.command == "run-check":
        return _cmd_run_check(args)
    if args.command == "run-report":
        return _cmd_run_report(args)
    if args.command == "web":
        return _cmd_web(args)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
