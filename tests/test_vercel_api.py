"""Integration checks for the hosted serverless API adapters."""

from __future__ import annotations

import http.client
import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from api.checks import handler as ChecksHandler
from api.fixtures import handler as FixturesHandler
from api.report import handler as ReportHandler
from proofline.registry import REGISTRY


class _Routes(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        path = urlsplit(self.path).path
        if path == "/api/checks":
            ChecksHandler.do_GET(self)
        elif path == "/api/fixtures":
            FixturesHandler.do_GET(self)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if urlsplit(self.path).path == "/api/report":
            ReportHandler.do_POST(self)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass


class VercelApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _Routes)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method: str, path: str, payload: object | None = None):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"} if body is not None else {}
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        content = response.read()
        connection.close()
        return response.status, content

    def test_registry_endpoint_returns_only_code_owned_checks(self):
        status, body = self.request("GET", "/api/checks")
        self.assertEqual(status, 200)
        self.assertEqual(
            json.loads(body),
            [
                {"id": check_id, "evidence_class": definition.evidence_class}
                for check_id, definition in REGISTRY.items()
            ],
        )

    def test_vercel_config_uses_self_only_script_and_style_sources(self):
        config = json.loads((_ROOT / "vercel.json").read_text(encoding="utf-8"))
        headers = config["headers"][0]["headers"]
        csp = next(header["value"] for header in headers if header["key"] == "Content-Security-Policy")
        self.assertIn("script-src 'self'", csp)
        self.assertIn("style-src 'self'", csp)
        self.assertNotIn("unsafe-inline", csp)

    def test_fixture_endpoint_is_whitelisted(self):
        status, body = self.request("GET", "/api/fixtures?name=simulated-only")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["scenario"], "simulated-only")
        status, body = self.request("GET", "/api/fixtures?name=../../README")
        self.assertEqual(status, 404)
        self.assertNotIn(b"README", body)

    def test_hosted_report_is_declaration_only_and_does_not_run_checks(self):
        manifest = {
            "scenario": "hosted-api-test",
            "repository_id": " org/example ",
            "claims": [{
                "id": "claim-1",
                "title": "A declared local check passes",
                "evidence_class": "local",
                "evidence_refs": ["check-local-contracts"],
            }],
            "checks": [{
                "id": "check-local-contracts",
                "result": "pass",
                "evidence_class": "local",
                "source": "test declaration",
            }],
        }
        with patch("proofline.runner.run_check", side_effect=AssertionError("API must not run checks")):
            status, body = self.request("POST", "/api/report", manifest)
        report = json.loads(body)["report"]
        self.assertEqual(status, 200)
        self.assertEqual(report["claims"][0]["status"], "conditional")
        self.assertEqual(report["checks"][0]["provenance"], "manifest-declared")
        self.assertEqual(report["repository_id"], "org/example")
        self.assertIn("Repository: `org/example`", json.loads(body)["markdown"])
