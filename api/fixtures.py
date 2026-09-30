"""Serve only the three checked-in synthetic example manifests."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from api._common import _ROOT, SafeApiHandler, send_bytes, send_json
from proofline.observability import begin_request

_FIXTURES = {
    "local-pass": "local-pass.json",
    "simulated-only": "simulated-only.json",
    "hosted-unverified": "hosted-unverified.json",
}


class handler(SafeApiHandler):  # noqa: N801
    def do_GET(self) -> None:  # noqa: N802
        begin_request(self, "/api/fixtures")
        name = parse_qs(urlsplit(self.path).query).get("name", [""])[0]
        filename = _FIXTURES.get(name)
        if filename is None:
            send_json(self, 404, {"error": "Unknown synthetic scenario."})
            return
        body = (_ROOT / "fixtures" / filename).read_bytes()
        send_bytes(self, 200, body, "application/json; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        begin_request(self, "/api/fixtures")
        send_json(self, 405, {"error": "Use GET to load a synthetic scenario."})
