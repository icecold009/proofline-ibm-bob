"""Public metadata for the fixed code-owned check registry."""

from __future__ import annotations

from api._common import SafeApiHandler, send_json
from proofline.registry import REGISTRY
from proofline.observability import begin_request


class handler(SafeApiHandler):  # noqa: N801
    def do_GET(self) -> None:  # noqa: N802
        begin_request(self, "/api/checks")
        checks = [
            {"id": check_id, "evidence_class": definition.evidence_class}
            for check_id, definition in REGISTRY.items()
        ]
        send_json(self, 200, checks)

    def do_POST(self) -> None:  # noqa: N802
        begin_request(self, "/api/checks")
        send_json(self, 405, {"error": "Use GET to list registered checks."})
