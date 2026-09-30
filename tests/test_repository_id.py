from __future__ import annotations

import unittest

from proofline.engine import analyze_manifest
from proofline.model import ValidationError, load_manifest, validate_manifest
from proofline.report import render_html, render_markdown


def _manifest(repository_id: object = ...):
    raw = {
        "scenario": "repository-id-test",
        "claims": [
            {
                "id": "claim-1",
                "title": "A claim supported by a declaration",
                "evidence_class": "local",
                "evidence_refs": ["check-local-contracts"],
            }
        ],
        "checks": [
            {
                "id": "check-local-contracts",
                "result": "pass",
                "evidence_class": "local",
                "source": "synthetic test declaration",
            }
        ],
    }
    if repository_id is not ...:
        raw["repository_id"] = repository_id
    return raw


class RepositoryIdValidationTests(unittest.TestCase):
    def test_omitted_and_null_are_both_absent(self):
        omitted = validate_manifest(_manifest())
        explicit_null = validate_manifest(_manifest(None))
        self.assertIsNone(omitted.repository_id)
        self.assertIsNone(explicit_null.repository_id)
        self.assertEqual(analyze_manifest(omitted)["report_id"], analyze_manifest(explicit_null)["report_id"])

    def test_normalizes_supplied_value(self):
        manifest = validate_manifest(_manifest("  org/example  "))
        self.assertEqual(manifest.repository_id, "org/example")

    def test_rejects_non_string_values(self):
        for value in (False, 17, [], {}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_manifest(_manifest(value))

    def test_rejects_empty_values(self):
        for value in ("", "   "):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_manifest(_manifest(value))

    def test_rejects_control_characters_before_trimming(self):
        for value in ("org\n/example", "\torg/example", "org/example\x7f"):
            with self.subTest(value=repr(value)), self.assertRaises(ValidationError):
                validate_manifest(_manifest(value))

    def test_rejects_more_than_500_characters(self):
        with self.assertRaisesRegex(ValidationError, "500 characters"):
            validate_manifest(_manifest("r" * 501))


class RepositoryIdReportTests(unittest.TestCase):
    def test_legacy_fixture_report_id_is_unchanged(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        report = analyze_manifest(load_manifest(root / "fixtures" / "local-pass.json"))
        self.assertEqual(report["report_id"], "report-dbd6402ceb0c")
        self.assertIsNone(report["repository_id"])

    def test_normalized_values_have_equal_ids_and_distinct_repositories_do_not(self):
        first = analyze_manifest(validate_manifest(_manifest("  org/example ")))
        equivalent = analyze_manifest(validate_manifest(_manifest("org/example")))
        other = analyze_manifest(validate_manifest(_manifest("org/another")))
        self.assertEqual(first["repository_id"], "org/example")
        self.assertEqual(first["report_id"], equivalent["report_id"])
        self.assertNotEqual(first["report_id"], other["report_id"])

    def test_repository_metadata_does_not_change_evidence_or_status(self):
        legacy = analyze_manifest(validate_manifest(_manifest()))
        identified = analyze_manifest(validate_manifest(_manifest("C:\\private\\repo")))
        self.assertEqual(legacy["claims"], identified["claims"])
        self.assertEqual(legacy["checks"], identified["checks"])
        self.assertEqual(legacy["summary"], identified["summary"])
        self.assertNotEqual(legacy["report_id"], identified["report_id"])

    def test_repository_metadata_is_present_in_json_markdown_and_html(self):
        value = "org/example"
        report = analyze_manifest(validate_manifest(_manifest(value)))
        markdown = render_markdown(report)
        html = render_html(report)
        self.assertEqual(report["repository_id"], value)
        self.assertIn(f"- Repository: `{value}`", markdown)
        self.assertIn(f"<p><strong>Repository:</strong> {value}</p>", html)

    def test_repository_metadata_is_safely_escaped_for_markdown_and_html(self):
        value = "org/`<script>alert(1)</script>|repo"
        report = analyze_manifest(validate_manifest(_manifest(value)))
        markdown = render_markdown(report)
        html = render_html(report)
        self.assertIn(f"- Repository: ``{value}``", markdown)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)


if __name__ == "__main__":
    unittest.main()
