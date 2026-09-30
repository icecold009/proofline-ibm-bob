"""Loopback-only browser interface for synthetic and supplied manifests.

The web interface never runs checks, persists manifests, or makes outbound
network requests. Execution remains available only through the explicit CLI
run-report command and the code-owned local check registry.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from sysconfig import get_path
from urllib.parse import parse_qs, urlsplit

from .engine import analyze_manifest
from .model import MAX_MANIFEST_BYTES, ValidationError, validate_manifest
from . import __version__
from .observability import begin_request, log_response
from .registry import REGISTRY
from .report import render_markdown

def _application_root() -> Path:
    """Locate the source checkout or packaged static data without caller paths."""
    source_root = Path(__file__).resolve().parents[2]
    install_root = Path(get_path("data"))
    required_files = (
        Path("public") / "index.html",
        Path("public") / "styles.css",
        Path("public") / "app.js",
        Path("fixtures") / "local-pass.json",
        Path("fixtures") / "simulated-only.json",
        Path("fixtures") / "hosted-unverified.json",
    )
    for candidate in (source_root, install_root):
        if all((candidate / relative).is_file() for relative in required_files):
            return candidate
    raise RuntimeError("Proofline's packaged browser page or synthetic fixtures are missing.")


_ROOT = _application_root()
_FIXTURES = {
    "local-pass": "local-pass.json",
    "simulated-only": "simulated-only.json",
    "hosted-unverified": "hosted-unverified.json",
}

_PAGE_FILE = _ROOT / "public" / "index.html"
_STATIC_ASSETS = {
    "/styles.css": (_ROOT / "public" / "styles.css", "text/css; charset=utf-8"),
    "/app.js": (_ROOT / "public" / "app.js", "text/javascript; charset=utf-8"),
}
_CONTENT_SECURITY_POLICY = (
    "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
    "img-src 'none'; object-src 'none'; base-uri 'none'; form-action 'self'; "
    "frame-ancestors 'none'"
)

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _handler() -> type[BaseHTTPRequestHandler]:
    class ProoflineHandler(BaseHTTPRequestHandler):
        server_version = "ProoflineLocal/1"

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            if not hasattr(self, "_proofline_request_id"):
                begin_request(self, "other")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Request-ID", self._proofline_request_id)
            self.send_header(
                "Content-Security-Policy",
                _CONTENT_SECURITY_POLICY,
            )
            self.end_headers()
            self.wfile.write(body)
            log_response(self, status, len(body))

        def _json(self, status: int, payload: object) -> None:
            self._send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def _host_is_local(self) -> bool:
            host = self.headers.get("Host", "").lower()
            return host in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

        def do_GET(self) -> None:  # noqa: N802
            path = urlsplit(self.path).path
            if path in {"/", "/styles.css", "/app.js", "/api/checks", "/api/health"}:
                route = path
            elif path == "/api/fixtures" or path.startswith("/api/fixtures/"):
                route = "/api/fixtures"
            else:
                route = "other"
            begin_request(self, route)
            if not self._host_is_local():
                self._json(403, {"error": "Only loopback requests are allowed."})
                return
            if path == "/":
                self._send(200, _PAGE_FILE.read_bytes(), "text/html; charset=utf-8")
                return
            asset = _STATIC_ASSETS.get(path)
            if asset is not None:
                asset_path, content_type = asset
                self._send(200, asset_path.read_bytes(), content_type)
                return
            if path == "/api/checks":
                checks = [
                    {"id": check_id, "evidence_class": definition.evidence_class}
                    for check_id, definition in REGISTRY.items()
                ]
                self._json(200, checks)
                return
            if path == "/api/health":
                self._json(200, {"status": "ok", "version": __version__})
                return
            prefix = "/api/fixtures/"
            if path == "/api/fixtures" or path.startswith(prefix):
                slug = (
                    parse_qs(urlsplit(self.path).query).get("name", [""])[0]
                    if path == "/api/fixtures"
                    else path[len(prefix):]
                )
                filename = _FIXTURES.get(slug)
                if filename is None:
                    self._json(404, {"error": "Unknown synthetic scenario."})
                    return
                body = (_ROOT / "fixtures" / filename).read_bytes()
                self._send(200, body, "application/json; charset=utf-8")
                return
            self._json(404, {"error": "Not found."})

        def do_POST(self) -> None:  # noqa: N802
            path = urlsplit(self.path).path
            begin_request(self, "/api/report" if path == "/api/report" else "other")
            if not self._host_is_local():
                self._json(403, {"error": "Only loopback requests are allowed."})
                return
            if path != "/api/report":
                self._json(404, {"error": "Not found."})
                return
            if self.headers.get_content_type() != "application/json":
                self._json(415, {"error": "Send a JSON manifest."})
                return
            raw_length = self.headers.get("Content-Length", "")
            if not raw_length.isdigit() or len(raw_length) > 6:
                self._json(411, {"error": "A valid Content-Length is required."})
                return
            length = int(raw_length)
            if length > MAX_MANIFEST_BYTES:
                self._json(413, {"error": "Manifest exceeds the 256 KB size limit."})
                return
            try:
                raw = json.loads(self.rfile.read(length).decode("utf-8"))
                manifest = validate_manifest(raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._json(400, {"error": "Manifest must be valid UTF-8 JSON."})
                return
            except ValidationError as exc:
                self._json(400, {"error": str(exc)})
                return

            report = analyze_manifest(manifest, generated_at=_utc_now())
            self._json(200, {"report": report, "markdown": render_markdown(report)})

        def log_message(self, format: str, *args: object) -> None:
            # Avoid BaseHTTPRequestHandler's raw path, query, and client address log.
            return

        def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
            # _send emits one normalized record after writing the response body.
            return

        def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
            # Do not echo parser details or fall back to the default HTML error page.
            self._json(code, {"error": "The request could not be processed."})

    return ProoflineHandler


def serve(*, host: str = "127.0.0.1", port: int = 8765) -> int:
    """Start the bounded loopback-only browser interface."""
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError("The local web preview may bind only to loopback.")
    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535.")
    server = HTTPServer((host, port), _handler())
    print(f"Proofline local preview: http://127.0.0.1:{server.server_port}/ (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
