"""Safe liveness metadata for the hosted API."""

from __future__ import annotations

from api._common import SafeApiHandler, send_json
from proofline import __version__
from proofline.observability import begin_request


class handler(SafeApiHandler):  # noqa: N801
    def do_GET(self) -> None:  # noqa: N802
        begin_request(self, "/api/health")
        send_json(self, 200, {"status": "ok", "version": __version__})

    def do_POST(self) -> None:  # noqa: N802
        begin_request(self, "/api/health")
        send_json(self, 405, {"error": "Use GET to check service health."})
