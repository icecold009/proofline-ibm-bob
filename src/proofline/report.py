"""Human-readable report rendering."""

from __future__ import annotations

from typing import Any


def _cell(value: Any) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ")
    return text.replace("|", "\\|")


def render_markdown(report: dict[str, Any]) -> str:
    """Render a report without interpreting claim text as HTML."""

    lines = [
        "# Proofline evidence brief",
        "",
        f"- Report: {_cell(report['report_id'])}",
        f"- Scenario: {_cell(report['scenario'])}",
        f"- Generated at: {_cell(report['generated_at'] or 'not supplied')}",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in report["summary"].items():
        lines.append(f"| {_cell(status)} | {count} |")

    lines.extend(
        [
            "",
            "## Claims",
            "",
            "| Claim | Evidence class | Status | Limitation | Next action |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for claim in report["claims"]:
        lines.append(
            "| "
            + " | ".join(
                _cell(claim[field])
                for field in ("title", "evidence_class", "status", "limitation", "next_action")
            )
            + " |"
        )

    lines.extend(["", "## Security notes", ""])
    lines.extend(f"- {_cell(note)}" for note in report["security_notes"])
    return "\n".join(lines) + "\n"
