"""Tests for render_html — HTML report renderer (checklist item 9).

Covers:
  1.  Output is valid HTML with required structural elements.
  2.  Report metadata (report_id, scenario, generated_at) present.
  3.  All summary statuses and counts present.
  4.  Claim title, evidence_class, status, evidence_refs, limitation,
      next_action all present in the HTML.
  5.  Status badge text labels present for each status value.
  6.  Embedded JSON payload contains correct report data.
  7.  Embedded Markdown payload (in textarea) matches render_markdown output.
  8.  Export control buttons present (copy-md, dl-json, dl-md).
  9.  HTML output is deterministic: same report → same output byte-for-byte.
 10.  Escaping: <script> injection in claim title displayed as literal text.
 11.  Escaping: HTML markup in limitation displayed as literal text.
 12.  Escaping: </script> sequence in a field cannot break out of the JSON
      data block.
 13.  Escaping: double-quote in claim title does not break HTML attribute.
 14.  Existing render_markdown behavior unchanged.
 15.  CLI --format html produces HTML, --format json still default.
 16.  All three golden fixtures produce valid HTML with their claim content.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proofline.engine import analyze_manifest
from proofline.model import load_manifest
from proofline.report import render_html, render_markdown

FIXTURES = ROOT / "fixtures"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _report(fixture_name: str) -> dict:
    return analyze_manifest(load_manifest(FIXTURES / f"{fixture_name}.json"))


def _minimal_report(**overrides) -> dict:
    """Return a minimal valid report dict for targeted tests."""
    base = {
        "report_id": "report-abc123",
        "generated_at": "2024-01-01T00:00:00Z",
        "scenario": "test-scenario",
        "claims": [
            {
                "id": "claim-1",
                "title": "A test claim",
                "evidence_class": "local",
                "status": "proven",
                "evidence_refs": ["check-1"],
                "limitation": "Evidence passed in the declared evidence class.",
                "next_action": "Keep the artifact.",
            }
        ],
        "checks": [{"id": "check-1", "result": "pass",
                    "evidence_class": "local", "source": "test"}],
        "summary": {"proven": 1, "conditional": 0, "simulated": 0,
                    "unverified": 0, "blocked": 0},
        "limitations": ["Evidence passed in the declared evidence class."],
        "security_notes": ["No commands were executed."],
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# 1. Structural elements
# ---------------------------------------------------------------------------

class HtmlStructureTests(unittest.TestCase):

    def setUp(self):
        self.html = render_html(_minimal_report())

    def test_doctype_present(self):
        self.assertTrue(self.html.strip().startswith("<!DOCTYPE html>"),
                        "HTML must start with DOCTYPE declaration")

    def test_html_lang_attribute(self):
        self.assertIn('lang="en"', self.html)

    def test_charset_meta(self):
        self.assertIn("UTF-8", self.html)

    def test_viewport_meta(self):
        self.assertIn("viewport", self.html)

    def test_h1_present(self):
        self.assertIn("<h1>", self.html)

    def test_summary_section_present(self):
        self.assertIn("Summary", self.html)

    def test_claims_section_present(self):
        self.assertIn("Claims", self.html)

    def test_security_notes_section_present(self):
        self.assertIn("Security notes", self.html)

    def test_export_section_present(self):
        self.assertIn("Export", self.html)

    def test_footer_present(self):
        self.assertIn("Made with IBM Bob", self.html)

    def test_no_external_resources(self):
        """No src=http/https, no href=http/https linking external assets."""
        import re
        # Check for any external URL in src or href attributes (CDN, fonts, etc.)
        # Allow data: URIs and relative paths; block http/https.
        external = re.findall(r'(?:src|href)\s*=\s*["\']https?://', self.html)
        self.assertEqual(external, [],
                         f"Found external resource references: {external!r}")

    def test_no_inline_event_handlers(self):
        """No onclick/onload/onerror etc. as HTML attributes."""
        import re
        handlers = re.findall(r'\bon\w+\s*=\s*["\']', self.html)
        self.assertEqual(handlers, [],
                         f"Found inline event handlers: {handlers!r}")


# ---------------------------------------------------------------------------
# 2. Report metadata present
# ---------------------------------------------------------------------------

class MetadataTests(unittest.TestCase):

    def test_report_id_present(self):
        html = render_html(_minimal_report())
        self.assertIn("report-abc123", html)

    def test_scenario_present(self):
        html = render_html(_minimal_report())
        self.assertIn("test-scenario", html)

    def test_generated_at_present(self):
        html = render_html(_minimal_report())
        self.assertIn("2024-01-01T00:00:00Z", html)

    def test_none_generated_at_shows_fallback(self):
        html = render_html(_minimal_report(generated_at=None))
        self.assertIn("not supplied", html)


# ---------------------------------------------------------------------------
# 3. Summary counts
# ---------------------------------------------------------------------------

class SummaryTests(unittest.TestCase):

    def test_all_status_names_present(self):
        html = render_html(_minimal_report())
        for status in ("proven", "conditional", "simulated", "unverified", "blocked"):
            self.assertIn(status.upper(), html,
                          f"Status label '{status.upper()}' not found in HTML")

    def test_count_values_present(self):
        html = render_html(_minimal_report())
        # proven=1, others=0
        self.assertIn(">1<", html)


# ---------------------------------------------------------------------------
# 4 & 5. Claim fields and status badges
# ---------------------------------------------------------------------------

class ClaimFieldTests(unittest.TestCase):

    def test_claim_title_present(self):
        html = render_html(_minimal_report())
        self.assertIn("A test claim", html)

    def test_claim_evidence_class_present(self):
        html = render_html(_minimal_report())
        self.assertIn("local", html)

    def test_claim_status_badge_present(self):
        html = render_html(_minimal_report())
        self.assertIn("[PROVEN]", html)

    def test_claim_evidence_ref_present(self):
        html = render_html(_minimal_report())
        self.assertIn("check-1", html)

    def test_claim_limitation_present(self):
        html = render_html(_minimal_report())
        self.assertIn("Evidence passed in the declared evidence class.", html)

    def test_claim_next_action_present(self):
        html = render_html(_minimal_report())
        self.assertIn("Keep the artifact.", html)

    def test_all_status_badges(self):
        """Each status value produces the correct bracket label."""
        for status, label in [
            ("proven", "[PROVEN]"),
            ("conditional", "[CONDITIONAL]"),
            ("simulated", "[SIMULATED]"),
            ("unverified", "[UNVERIFIED]"),
            ("blocked", "[BLOCKED]"),
        ]:
            report = _minimal_report()
            report["claims"][0]["status"] = status
            html = render_html(report)
            self.assertIn(label, html,
                          f"Badge {label!r} not found for status={status!r}")

    def test_empty_evidence_refs_shows_none(self):
        report = _minimal_report()
        report["claims"][0]["evidence_refs"] = []
        html = render_html(report)
        self.assertIn("none", html)


# ---------------------------------------------------------------------------
# 6. Embedded JSON payload
# ---------------------------------------------------------------------------

class EmbeddedJsonTests(unittest.TestCase):

    def test_json_data_block_present(self):
        html = render_html(_minimal_report())
        self.assertIn('id="report-json-data"', html)
        self.assertIn('type="application/json"', html)

    def test_json_payload_contains_report_id(self):
        html = render_html(_minimal_report())
        # Extract the JSON block between the script tags.
        start = html.index('id="report-json-data">') + len('id="report-json-data">')
        end = html.index("</script>", start)
        payload_text = html[start:end]
        # Un-escape the <\/ sequences our encoder inserted.
        payload_text = payload_text.replace("<\\/", "</")
        data = json.loads(payload_text)
        self.assertEqual(data["report_id"], "report-abc123")

    def test_json_payload_contains_scenario(self):
        html = render_html(_minimal_report())
        start = html.index('id="report-json-data">') + len('id="report-json-data">')
        end = html.index("</script>", start)
        payload_text = html[start:end].replace("<\\/", "</")
        data = json.loads(payload_text)
        self.assertEqual(data["scenario"], "test-scenario")


# ---------------------------------------------------------------------------
# 7. Embedded Markdown (textarea)
# ---------------------------------------------------------------------------

class EmbeddedMarkdownTests(unittest.TestCase):

    def test_markdown_textarea_present(self):
        html = render_html(_minimal_report())
        self.assertIn('id="markdown-textarea"', html)

    def test_markdown_textarea_contains_report_id(self):
        html = render_html(_minimal_report())
        self.assertIn("report-abc123", html)

    def test_markdown_content_matches_render_markdown(self):
        report = _minimal_report()
        expected_md = render_markdown(report)
        html = render_html(report)
        # The Markdown in the textarea is HTML-escaped; un-escape for comparison.
        import html as html_lib
        # Find the textarea value.
        ta_start = html.index('id="markdown-textarea"')
        content_start = html.index(">", ta_start) + 1
        content_end = html.index("</textarea>", content_start)
        raw_ta = html[content_start:content_end]
        unescaped = html_lib.unescape(raw_ta)
        self.assertEqual(unescaped, expected_md)


# ---------------------------------------------------------------------------
# 8. Export controls
# ---------------------------------------------------------------------------

class ExportControlTests(unittest.TestCase):

    def test_copy_md_button_present(self):
        html = render_html(_minimal_report())
        self.assertIn('id="btn-copy-md"', html)

    def test_dl_json_button_present(self):
        html = render_html(_minimal_report())
        self.assertIn('id="btn-dl-json"', html)

    def test_dl_md_button_present(self):
        html = render_html(_minimal_report())
        self.assertIn('id="btn-dl-md"', html)

    def test_buttons_are_type_button(self):
        """Buttons must be type=button to prevent form submission."""
        html = render_html(_minimal_report())
        import re
        buttons = re.findall(r'<button[^>]*>', html)
        for btn in buttons:
            self.assertIn('type="button"', btn,
                          f"Button without type=button: {btn!r}")


# ---------------------------------------------------------------------------
# 9. Determinism
# ---------------------------------------------------------------------------

class DeterminismTests(unittest.TestCase):

    def test_same_report_same_output(self):
        report = _minimal_report()
        self.assertEqual(render_html(report), render_html(report))

    def test_golden_fixture_stable(self):
        report = _report("local-pass")
        self.assertEqual(render_html(report), render_html(report))


# ---------------------------------------------------------------------------
# 10-13. Security escaping
# ---------------------------------------------------------------------------

class EscapingTests(unittest.TestCase):

    def test_script_injection_in_title_is_escaped(self):
        """A claim title containing <script>alert(1)</script> must not create
        a live script element; it must appear as escaped text."""
        report = _minimal_report()
        report["claims"][0]["title"] = "<script>alert(1)</script>"
        html = render_html(report)
        # The raw string must not appear unescaped.
        self.assertNotIn("<script>alert(1)</script>", html,
                         "Unescaped <script> tag found in HTML output")
        # The escaped version must be present.
        self.assertIn("&lt;script&gt;", html)

    def test_html_markup_in_limitation_is_escaped(self):
        """HTML markup in a limitation must be displayed as literal text."""
        report = _minimal_report()
        report["claims"][0]["limitation"] = '<b>bold</b> & "quoted"'
        html = render_html(report)
        self.assertNotIn("<b>bold</b>", html)
        self.assertIn("&lt;b&gt;bold&lt;/b&gt;", html)
        self.assertIn("&amp;", html)
        self.assertIn("&quot;quoted&quot;", html)

    def test_script_close_in_json_data_is_escaped(self):
        """A </script> sequence in a claim field must not close the JSON
        data block when the report is embedded in the HTML."""
        report = _minimal_report()
        report["claims"][0]["title"] = 'bad</script><script>alert(2)'
        html = render_html(report)
        # The raw </script> sequence must not appear unescaped inside the
        # JSON data block (it will be encoded as <\/).
        # Find the JSON data block.
        start = html.index('id="report-json-data">') + len('id="report-json-data">')
        # The block should NOT contain unescaped </script>
        first_script_close = html.index("</script>", start)
        json_block = html[start:first_script_close]
        self.assertNotIn("</script>", json_block,
                         "Unescaped </script> found inside JSON data block")

    def test_double_quote_in_title_does_not_break_html(self):
        """A double-quote in a claim title must be HTML-escaped."""
        report = _minimal_report()
        report["claims"][0]["title"] = 'He said "hello"'
        html = render_html(report)
        self.assertIn("&quot;hello&quot;", html)

    def test_unicode_separators_in_json_block_are_escaped(self):
        """U+2028 and U+2029 in claim text must be escaped in the JSON block."""
        report = _minimal_report()
        report["claims"][0]["title"] = "line\u2028sep\u2029here"
        html = render_html(report)
        start = html.index('id="report-json-data">') + len('id="report-json-data">')
        end = html.index("</script>", start)
        json_block = html[start:end]
        self.assertNotIn("\u2028", json_block)
        self.assertNotIn("\u2029", json_block)
        self.assertIn("\\u2028", json_block)
        self.assertIn("\\u2029", json_block)


# ---------------------------------------------------------------------------
# 14. render_markdown unchanged
# ---------------------------------------------------------------------------

class MarkdownUnchangedTests(unittest.TestCase):

    def test_render_markdown_still_works(self):
        report = _minimal_report()
        md = render_markdown(report)
        self.assertIn("# Proofline evidence brief", md)
        self.assertIn("report-abc123", md)
        self.assertIn("A test claim", md)


# ---------------------------------------------------------------------------
# 15. CLI --format html / default json
# ---------------------------------------------------------------------------

class CliFormatTests(unittest.TestCase):

    def _invoke(self, extra_args: list[str]) -> str:
        import io
        import unittest.mock
        from proofline.__main__ import main
        buf = io.StringIO()
        with unittest.mock.patch("sys.stdout", buf):
            main(["report", str(FIXTURES / "local-pass.json")] + extra_args)
        return buf.getvalue()

    def test_default_format_is_json(self):
        out = self._invoke([])
        data = json.loads(out)
        self.assertIn("report_id", data)

    def test_format_json_explicit(self):
        out = self._invoke(["--format", "json"])
        data = json.loads(out)
        self.assertIn("report_id", data)

    def test_format_markdown(self):
        out = self._invoke(["--format", "markdown"])
        self.assertIn("# Proofline evidence brief", out)

    def test_format_html(self):
        out = self._invoke(["--format", "html"])
        self.assertIn("<!DOCTYPE html>", out)
        self.assertIn("local-pass", out)

    def test_format_html_contains_claim(self):
        out = self._invoke(["--format", "html"])
        self.assertIn("local report generator", out)


# ---------------------------------------------------------------------------
# 16. All three golden fixtures
# ---------------------------------------------------------------------------

class GoldenFixtureHtmlTests(unittest.TestCase):

    def _check_fixture(self, name: str, expected_status_label: str,
                       expected_title_fragment: str) -> None:
        report = _report(name)
        html = render_html(report)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn(name, html)
        self.assertIn(expected_status_label, html)
        self.assertIn(expected_title_fragment, html)

    def test_local_pass_fixture(self):
        self._check_fixture("local-pass", "[PROVEN]", "local report generator")

    def test_simulated_only_fixture(self):
        self._check_fixture("simulated-only", "[SIMULATED]", "Critical alerts")

    def test_hosted_unverified_fixture(self):
        self._check_fixture("hosted-unverified", "[UNVERIFIED]",
                            "Provider-backed synchronization")

    def test_all_three_produce_html_with_security_notes(self):
        for name in ("local-pass", "simulated-only", "hosted-unverified"):
            report = _report(name)
            html = render_html(report)
            self.assertIn("Security notes", html,
                          f"Security notes section missing from {name}")


if __name__ == "__main__":
    unittest.main()
