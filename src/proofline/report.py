"""Human-readable report rendering.

Security contract
-----------------
render_html treats every report field as untrusted text.
- _esc() applies html.escape() to all text before inserting into HTML.
- Report JSON embedded in a <script type="application/json"> block has
  </script> sequences escaped to <\\/script> so the block cannot be closed
  early by adversarial claim content.
- The Markdown brief is embedded in a <textarea> whose content is HTML-escaped;
  it is always visible for direct selection/copy.
- All JavaScript DOM writes use textContent or createTextNode, never innerHTML
  on untrusted data.
- No external resources, fonts, or network requests are used.
"""

from __future__ import annotations

import html
import json
from typing import Any


def _cell(value: Any) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ")
    return text.replace("|", "\\|")


def _esc(value: Any) -> str:
    """HTML-escape a value for safe insertion into HTML text or attributes."""
    return html.escape(str(value), quote=True)


def _embed_json(report: dict[str, Any]) -> str:
    """Serialize report to JSON safe for embedding inside a <script> block.

    Escapes </script> sequences so adversarial claim text cannot close the
    block early.  Also escapes U+2028 and U+2029 which are line terminators
    in JavaScript string contexts.
    """
    raw = json.dumps(report, sort_keys=True, ensure_ascii=False)
    # Prevent </script> from closing the enclosing script block.
    raw = raw.replace("</", "<\\/")
    # Escape JS line terminators that are valid JSON but break string literals.
    raw = raw.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return raw


# ---------------------------------------------------------------------------
# Status display helpers
# ---------------------------------------------------------------------------

_STATUS_LABELS: dict[str, str] = {
    "proven":      "PROVEN",
    "conditional": "CONDITIONAL",
    "simulated":   "SIMULATED",
    "unverified":  "UNVERIFIED",
    "blocked":     "BLOCKED",
}

# Inline CSS per status — background + foreground chosen for ≥4.5:1 contrast.
# Labels are also text-only (not color-only) per accessibility requirement.
_STATUS_CSS: dict[str, str] = {
    "proven":      "background:#d1fae5;color:#065f46",
    "conditional": "background:#fef3c7;color:#92400e",
    "simulated":   "background:#dbeafe;color:#1e40af",
    "unverified":  "background:#f3f4f6;color:#374151",
    "blocked":     "background:#fee2e2;color:#991b1b",
}


def _status_badge(status: str) -> str:
    """Return a safe HTML span badge for a status value."""
    label = _STATUS_LABELS.get(status, status.upper())
    css = _STATUS_CSS.get(status, "background:#e5e7eb;color:#111827")
    return (
        f'<span class="status" style="{_esc(css)}" '
        f'aria-label="Status: {_esc(label)}">'
        f'[{_esc(label)}]</span>'
    )


# ---------------------------------------------------------------------------
# HTML renderer
# ---------------------------------------------------------------------------

def render_html(report: dict[str, Any]) -> str:
    """Render a fully self-contained, offline HTML evidence brief.

    Security guarantees:
    - All report text is HTML-escaped before insertion.
    - Embedded JSON uses _embed_json() to prevent script-block escape.
    - The Markdown textarea content is HTML-escaped.
    - JavaScript DOM writes use textContent; no innerHTML on untrusted data.
    - No external resources (fonts, scripts, images, or network calls).

    The output is deterministic: identical report dict → identical HTML.
    """
    markdown_text = render_markdown(report)
    json_blob = _embed_json(report)

    # ---- Summary table rows ----
    summary_rows = ""
    for status, count in report["summary"].items():
        badge = _status_badge(status)
        summary_rows += (
            f"<tr><td>{badge}</td>"
            f"<td class='num'>{_esc(count)}</td></tr>\n"
        )

    # ---- Claim articles ----
    claims_html = ""
    for claim in report["claims"]:
        status = claim.get("status", "unverified")
        refs = claim.get("evidence_refs") or []
        refs_html = (
            "<ul>" + "".join(f"<li>{_esc(r)}</li>" for r in refs) + "</ul>"
            if refs else "<em>none</em>"
        )
        claims_html += f"""
<article class="claim">
  <h3>{_esc(claim.get("title", ""))}</h3>
  <dl>
    <dt>Evidence class</dt><dd>{_esc(claim.get("evidence_class", ""))}</dd>
    <dt>Status</dt><dd>{_status_badge(status)}</dd>
    <dt>Evidence references</dt><dd>{refs_html}</dd>
    <dt>Limitation</dt><dd>{_esc(claim.get("limitation") or "—")}</dd>
    <dt>Next action</dt><dd>{_esc(claim.get("next_action") or "—")}</dd>
  </dl>
</article>
"""

    # ---- Security notes ----
    notes_html = "\n".join(
        f"<li>{_esc(n)}</li>" for n in report.get("security_notes", [])
    )

    # ---- Inline JS (all DOM writes use textContent) ----
    # The JSON payload is embedded in a <script type="application/json"> block
    # so it is not executed.  The copy/download handlers read it from the DOM.
    js = r"""
(function () {
  'use strict';

  function getJSON() {
    var el = document.getElementById('report-json-data');
    return el ? el.textContent : '{}';
  }

  function getMarkdown() {
    var el = document.getElementById('markdown-textarea');
    return el ? el.value : '';
  }

  function showFeedback(btnId, msg) {
    var btn = document.getElementById(btnId);
    if (!btn) return;
    var orig = btn.textContent;
    btn.textContent = msg;
    btn.disabled = true;
    setTimeout(function () {
      btn.textContent = orig;
      btn.disabled = false;
    }, 1500);
  }

  function downloadBlob(content, filename, mime) {
    var blob = new Blob([content], { type: mime });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }

  document.getElementById('btn-copy-md').addEventListener('click', function () {
    var text = getMarkdown();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        showFeedback('btn-copy-md', 'Copied!');
      }, function () {
        /* clipboard blocked (local file) — select textarea as fallback */
        var ta = document.getElementById('markdown-textarea');
        if (ta) { ta.select(); }
        showFeedback('btn-copy-md', 'Select & copy above');
      });
    } else {
      var ta = document.getElementById('markdown-textarea');
      if (ta) { ta.select(); }
      showFeedback('btn-copy-md', 'Select & copy above');
    }
  });

  document.getElementById('btn-dl-json').addEventListener('click', function () {
    downloadBlob(getJSON(), 'proofline-report.json', 'application/json');
    showFeedback('btn-dl-json', 'Downloaded!');
  });

  document.getElementById('btn-dl-md').addEventListener('click', function () {
    downloadBlob(getMarkdown(), 'proofline-report.md', 'text/markdown');
    showFeedback('btn-dl-md', 'Downloaded!');
  });
}());
"""

    generated_at = _esc(report.get("generated_at") or "not supplied")
    report_id = _esc(report.get("report_id", ""))
    scenario = _esc(report.get("scenario", ""))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Proofline evidence brief — {scenario}</title>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
  font-size: 15px; line-height: 1.6; color: #1f2328; background: #ffffff;
  padding: 1.5rem;
}}
.container {{ max-width: 800px; margin: 0 auto; }}
h1 {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem; }}
h2 {{ font-size: 1.15rem; font-weight: 600; margin: 2rem 0 0.75rem;
      border-bottom: 1px solid #e5e7eb; padding-bottom: 0.3rem; }}
h3 {{ font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem; }}
.meta {{ color: #57606a; font-size: 0.875rem; margin-bottom: 1.5rem; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 1rem; }}
th, td {{ text-align: left; padding: 0.4rem 0.75rem;
          border: 1px solid #e5e7eb; }}
th {{ background: #f7f8fa; font-weight: 600; }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.claim {{ border: 1px solid #e5e7eb; border-radius: 6px;
          padding: 1rem; margin-bottom: 1rem; background: #f7f8fa; }}
dl {{ display: grid; grid-template-columns: 10rem 1fr; gap: 0.25rem 1rem; }}
dt {{ font-weight: 600; color: #57606a; font-size: 0.875rem; padding-top: 0.1rem; }}
dd ul {{ margin: 0; padding-left: 1.2rem; }}
.status {{
  display: inline-block; padding: 0.1em 0.4em;
  border-radius: 4px; font-size: 0.8rem; font-weight: 700;
  font-family: monospace; white-space: nowrap;
}}
.controls {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin: 1rem 0; }}
button {{
  padding: 0.4rem 1rem; border: 1px solid #d1d5db;
  border-radius: 6px; background: #ffffff; color: #1f2328;
  font-size: 0.875rem; cursor: pointer;
}}
button:hover {{ background: #f3f4f6; }}
button:focus {{ outline: 2px solid #3b82d4; outline-offset: 2px; }}
textarea {{
  width: 100%; height: 12rem; font-family: monospace; font-size: 0.8rem;
  border: 1px solid #e5e7eb; border-radius: 4px; padding: 0.5rem;
  background: #f7f8fa; color: #1f2328; resize: vertical;
}}
ul.notes {{ padding-left: 1.4rem; }}
footer {{ margin-top: 2.5rem; padding-top: 1rem;
          border-top: 1px solid #e5e7eb; color: #57606a;
          font-size: 0.75rem; text-align: center; }}
@media (max-width: 600px) {{
  dl {{ grid-template-columns: 1fr; }}
  dt {{ padding-top: 0.5rem; }}
}}
</style>
</head>
<body>
<div class="container">

<h1>Proofline evidence brief</h1>
<p class="meta">
  Report: <code>{report_id}</code> &nbsp;|&nbsp;
  Scenario: <strong>{scenario}</strong> &nbsp;|&nbsp;
  Generated: {generated_at}
</p>

<h2>Summary</h2>
<table>
  <thead><tr><th>Status</th><th class="num">Count</th></tr></thead>
  <tbody>
{summary_rows}  </tbody>
</table>

<h2>Claims</h2>
{claims_html}

<h2>Security notes</h2>
<ul class="notes">
{notes_html}
</ul>

<h2>Export</h2>
<div class="controls">
  <button id="btn-copy-md" type="button">Copy Markdown</button>
  <button id="btn-dl-json" type="button">Download JSON</button>
  <button id="btn-dl-md" type="button">Download Markdown</button>
</div>
<p style="font-size:0.8rem;color:#57606a;margin-bottom:0.5rem">
  Markdown brief (select all to copy if clipboard is unavailable):
</p>
<textarea id="markdown-textarea" readonly
  aria-label="Markdown evidence brief">{_esc(markdown_text)}</textarea>

</div>

<script type="application/json" id="report-json-data">{json_blob}</script>
<script>{js}</script>
<footer>Made with IBM Bob</footer>
</body>
</html>
"""


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
