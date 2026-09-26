"""Public metadata for the fixed code-owned check registry."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from api._common import send_json
from proofline.registry import REGISTRY


class handler(BaseHTTPRequestHandler):  # noqa: N801
    def do_GET(self) -> None:  # noqa: N802
        checks = [
            {"id": check_id, "evidence_class": definition.evidence_class}
            for check_id, definition in REGISTRY.items()
        ]
        send_json(self, 200, checks)

    def do_POST(self) -> None:  # noqa: N802
        send_json(self, 405, {"error": "Use GET to list registered checks."})
