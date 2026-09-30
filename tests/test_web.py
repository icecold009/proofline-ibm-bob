"""Loopback browser interface integration checks."""

from __future__ import annotations

import http.client
import io
import json
import threading
import time
import unittest
from contextlib import redirect_stdout
from http.server import HTTPServer
from unittest.mock import patch

from proofline.registry import REGISTRY
from proofline.web import _handler


class BrowserIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _handler())
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method: str, path: str, body: bytes | None = None):
        status, payload, _ = self.request_with_headers(method, path, body)
        return status, payload

    def request_with_headers(self, method: str, path: str, body: bytes | None = None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        headers = {"Content-Type": "application/json"} if body is not None else {}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        response_headers = dict(response.getheaders())
        status = response.status
        connection.close()
        return status, payload, response_headers

    def test_page_exposes_three_step_guided_and_advanced_intake(self):
        status, body, _ = self.request_with_headers("GET", "/")
        page = body.decode("utf-8")
        self.assertEqual(status, 200)
        self.assertIn("What changed?", page)
        self.assertIn("What supports the claim?", page)
        self.assertIn("Advanced JSON manifest", page)
        self.assertIn("Your report will appear here", page)
        self.assertIn('href="/styles.css"', page)
        self.assertIn('src="/app.js"', page)
        self.assertNotRegex(page, r"<script(?![^>]*\bsrc=)")
        self.assertNotRegex(page, r"\sstyle\s*=")

    def test_static_assets_are_exactly_allowlisted_and_use_strict_csp(self):
        for path, expected_type in (("/styles.css", "text/css"), ("/app.js", "text/javascript")):
            with self.subTest(path=path):
                status, body, headers = self.request_with_headers("GET", path)
                self.assertEqual(status, 200)
                self.assertTrue(body)
                self.assertTrue(headers["Content-Type"].startswith(expected_type))
                policy = headers["Content-Security-Policy"]
                self.assertIn("script-src 'self'", policy)
                self.assertIn("style-src 'self'", policy)
                self.assertNotIn("unsafe-inline", policy)

        for path in ("/secret.txt", "/public/index.html", "/%2e%2e/src/proofline/web.py"):
            with self.subTest(path=path):
                status, _, _ = self.request_with_headers("GET", path)
                self.assertEqual(status, 404)

    def test_html_and_json_responses_receive_strict_csp(self):
        for path in ("/", "/api/checks", "/api/health", "/api/fixtures/local-pass"):
            with self.subTest(path=path):
                status, _, headers = self.request_with_headers("GET", path)
                self.assertEqual(status, 200)
                self.assertIn("default-src 'none'", headers["Content-Security-Policy"])

    def test_health_exposes_only_status_and_version(self):
        status, body, headers = self.request_with_headers("GET", "/api/health")
        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "ok", "version": "0.1.0"})
        self.assertEqual(set(payload), {"status", "version"})
        self.assertTrue(headers["X-Request-ID"])

    def test_local_operational_log_uses_fixed_route_and_no_query_or_client_data(self):
        output = io.StringIO()
        with redirect_stdout(output):
            status, body, headers = self.request_with_headers(
                "GET", "/api/fixtures?name=simulated-only&private_marker=never-log-this"
            )
            expected_request_id = headers["X-Request-ID"]
            deadline = time.monotonic() + 1
            while expected_request_id not in output.getvalue() and time.monotonic() < deadline:
                time.sleep(0.005)
        records = [json.loads(line) for line in output.getvalue().splitlines() if line]
        record = next((item for item in records if item["request_id"] == expected_request_id), None)
        self.assertIsNotNone(record, "the response log for this request was not captured")
        self.assertEqual(status, 200)
        self.assertEqual(record["route"], "/api/fixtures")
        self.assertEqual(record["status"], 200)
        self.assertEqual(record["response_bytes"], len(body))
        self.assertGreaterEqual(record["duration_ms"], 0)
        self.assertEqual(record["request_id"], expected_request_id)
        self.assertEqual(set(record), {"request_id", "route", "status", "response_bytes", "duration_ms"})
        self.assertNotIn("private_marker", output.getvalue())
        self.assertNotIn("127.0.0.1", output.getvalue())

    def test_unsupported_method_uses_safe_json_response_and_log(self):
        output = io.StringIO()
        with redirect_stdout(output):
            status, body, _ = self.request_with_headers("PUT", "/private?marker=do-not-log")
        record = json.loads(output.getvalue())
        self.assertEqual(status, 501)
        self.assertEqual(json.loads(body), {"error": "The request could not be processed."})
        self.assertEqual(record["route"], "other")
        self.assertEqual(record["status"], 501)
        self.assertNotIn("private", output.getvalue())
        self.assertNotIn("do-not-log", output.getvalue())

    def test_check_options_come_from_static_registry(self):
        status, body = self.request("GET", "/api/checks")
        options = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(
            options,
            [
                {"id": check_id, "evidence_class": definition.evidence_class}
                for check_id, definition in REGISTRY.items()
            ],
        )

    def test_browser_report_keeps_declared_pass_conditional_without_running_checks(self):
        manifest = {
            "scenario": "browser-intake-test",
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
        with patch("proofline.runner.run_check", side_effect=AssertionError("browser must not run checks")):
            status, body = self.request("POST", "/api/report", json.dumps(manifest).encode("utf-8"))
        report = json.loads(body)["report"]
        self.assertEqual(status, 200)
        self.assertEqual(report["claims"][0]["status"], "conditional")
        self.assertEqual(report["checks"][0]["provenance"], "manifest-declared")
        self.assertEqual(report["repository_id"], "org/example")
        self.assertIn("Repository: `org/example`", json.loads(body)["markdown"])


if __name__ == "__main__":
    unittest.main()
