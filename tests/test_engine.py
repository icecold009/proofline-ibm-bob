from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proofline.engine import analyze_manifest
from proofline.model import ValidationError, load_manifest, validate_manifest
from proofline.report import render_markdown


class ProoflineFixtureTests(unittest.TestCase):
    def test_local_fixture_proves_local_claim(self) -> None:
        report = analyze_manifest(load_manifest(ROOT / "fixtures" / "local-pass.json"))
        self.assertEqual(report["summary"]["proven"], 1)
        self.assertEqual(report["claims"][0]["status"], "proven")

    def test_simulated_fixture_does_not_upgrade_to_hosted_proof(self) -> None:
        report = analyze_manifest(load_manifest(ROOT / "fixtures" / "simulated-only.json"))
        self.assertEqual(report["claims"][0]["status"], "simulated")
        self.assertEqual(report["summary"]["proven"], 0)

    def test_missing_provider_evidence_is_unverified(self) -> None:
        report = analyze_manifest(load_manifest(ROOT / "fixtures" / "hosted-unverified.json"))
        self.assertEqual(report["claims"][0]["status"], "unverified")
        self.assertIn("No provider response", report["claims"][0]["limitation"])

    def test_unknown_evidence_reference_is_blocked(self) -> None:
        manifest = validate_manifest(
            {
                "scenario": "missing-reference",
                "claims": [
                    {
                        "id": "claim-1",
                        "title": "A claim",
                        "evidence_class": "local",
                        "evidence_refs": ["missing-check"],
                    }
                ],
                "checks": [],
            }
        )
        report = analyze_manifest(manifest)
        self.assertEqual(report["claims"][0]["status"], "blocked")

    def test_declared_status_is_not_trusted(self) -> None:
        manifest = validate_manifest(
            {
                "scenario": "status-injection",
                "claims": [
                    {
                        "id": "claim-1",
                        "title": "Pretend this passed",
                        "evidence_class": "provider",
                        "evidence_refs": [],
                        "status": "proven",
                    }
                ],
                "checks": [],
            }
        )
        self.assertEqual(analyze_manifest(manifest)["claims"][0]["status"], "unverified")

    def test_unknown_evidence_class_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            validate_manifest(
                {
                    "scenario": "invalid",
                    "claims": [
                        {
                            "id": "claim-1",
                            "title": "Invalid",
                            "evidence_class": "magic",
                            "evidence_refs": [],
                        }
                    ],
                    "checks": [],
                }
            )

    def test_report_id_is_stable_and_markdown_is_safe(self) -> None:
        manifest = load_manifest(ROOT / "fixtures" / "local-pass.json")
        first = analyze_manifest(manifest)
        second = analyze_manifest(manifest)
        self.assertEqual(first["report_id"], second["report_id"])
        markdown = render_markdown(first)
        self.assertIn("# Proofline evidence brief", markdown)
        self.assertNotIn("<script", markdown.lower())


if __name__ == "__main__":
    unittest.main()
