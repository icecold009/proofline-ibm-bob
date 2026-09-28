"""Hosted report endpoint; it validates and analyzes but never runs checks."""

from __future__ import annotations

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler

from api._common import RequestError, read_manifest, send_json
from proofline.engine import analyze_manifest
from proofline.report import render_markdown


class handler(BaseHTTPRequestHandler):  # noqa: N801
    def do_POST(self) -> None:  # noqa: N802
        try:
            manifest = read_manifest(self)
        except RequestError as exc:
            send_json(self, exc.status, {"error": str(exc)})
            return

        generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        report = analyze_manifest(manifest, generated_at=generated_at)
        send_json(self, 200, {"report": report, "markdown": render_markdown(report)})

    def do_GET(self) -> None:  # noqa: N802
        send_json(self, 405, {"error": "Use POST to analyze a manifest."})
