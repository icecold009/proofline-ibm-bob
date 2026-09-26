"""Registry enforcement and injection-resistance tests for Proofline.

Covers milestone 7 acceptance criteria:
  1. Well-formed but unregistered check IDs produce status="blocked" on dependent
     claims (engine-time override, manifest remains reportable).
  2. Injection-shaped check IDs (shell metacharacters, env-var syntax, path
     traversal) also produce status="blocked" — they pass validate_manifest
     because they are well-formed strings, then the engine overrides their
     result to "blocked" before evaluating claims.
  3. An empty check ID raises ValidationError in validate_manifest (malformed
     manifest, not a registry question — caught by the existing _text helper
     before registry membership is relevant).
  4. lookup() returns a CheckDefinition for known IDs and None for unknown IDs.

No subprocess is spawned, no disk is written, no network is accessed, and no
eval/exec is called in any test.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proofline import (
    CheckDefinition,
    ValidationError,
    analyze_manifest,
    lookup,
    validate_manifest,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _raw_manifest_with_check_id(check_id: str) -> dict:
    """Return a structurally valid raw manifest dict with one claim and one check.

    The claim references check_id via evidence_refs.  The check supplies
    result="pass" to confirm that the engine override (not the manifest value)
    is what forces blocked status for unregistered IDs.
    """
    return {
        "scenario": "injection-test",
        "claims": [
            {
                "id": "claim-1",
                "title": "A test claim",
                "evidence_class": "local",
                "evidence_refs": [check_id],
            }
        ],
        "checks": [
            {
                "id": check_id,
                "result": "pass",
                "evidence_class": "local",
                "source": "test",
            }
        ],
    }


# ---------------------------------------------------------------------------
# Tests: unregistered IDs produce blocked claims
# ---------------------------------------------------------------------------

class RegistryBlockingTests(unittest.TestCase):
    """Well-formed manifests with unregistered check IDs remain reportable but
    produce status="blocked" for every dependent claim."""

    def _assert_blocked(self, check_id: str) -> None:
        raw = _raw_manifest_with_check_id(check_id)
        # validate_manifest must succeed — the manifest is structurally valid.
        manifest = validate_manifest(raw)
        report = analyze_manifest(manifest)
        self.assertEqual(
            report["claims"][0]["status"],
            "blocked",
            f"Expected blocked for check_id={check_id!r}; "
            f"got {report['claims'][0]['status']!r}",
        )
        # The report's checks section must also reflect the overridden result.
        self.assertEqual(report["checks"][0]["result"], "blocked")

    def test_unregistered_id_forces_blocked_claim(self) -> None:
        """A well-formed but unregistered check ID produces blocked."""
        self._assert_blocked("unregistered-check")

    def test_semicolon_in_id_forces_blocked_claim(self) -> None:
        """A check ID containing a semicolon (shell command separator) produces blocked."""
        self._assert_blocked("check-local-contracts; rm -rf /")

    def test_pipe_in_id_forces_blocked_claim(self) -> None:
        """A check ID containing a pipe character produces blocked."""
        self._assert_blocked("check-local-contracts | cat /etc/passwd")

    def test_subshell_in_id_forces_blocked_claim(self) -> None:
        """A check ID containing subshell syntax produces blocked."""
        self._assert_blocked("$(whoami)")

    def test_env_var_in_id_forces_blocked_claim(self) -> None:
        """A check ID containing env-var syntax produces blocked."""
        self._assert_blocked("$HOME")

    def test_path_traversal_in_id_forces_blocked_claim(self) -> None:
        """A check ID containing path-traversal sequences produces blocked."""
        self._assert_blocked("../../etc/passwd")


# ---------------------------------------------------------------------------
# Test: empty check ID is a malformed manifest (ValidationError)
# ---------------------------------------------------------------------------

class EmptyCheckIdValidationTest(unittest.TestCase):
    """An empty string for a check ID is a malformed manifest, not a registry
    question.  The existing _text() helper rejects it before registry membership
    is relevant."""

    def test_empty_id_raises_validation_error(self) -> None:
        """validate_manifest must raise ValidationError when a check id is ""."""
        raw = {
            "scenario": "empty-id-test",
            "claims": [
                {
                    "id": "claim-1",
                    "title": "A test claim",
                    "evidence_class": "local",
                    # evidence_refs is deliberately empty so the ValidationError
                    # is caused by the check's empty id, not a ref resolution.
                    "evidence_refs": [],
                }
            ],
            "checks": [
                {
                    "id": "",          # <-- this is the malformed field under test
                    "result": "pass",
                    "evidence_class": "local",
                    "source": "test",
                }
            ],
        }
        with self.assertRaises(ValidationError):
            validate_manifest(raw)


# ---------------------------------------------------------------------------
# Tests: lookup unit tests
# ---------------------------------------------------------------------------

class LookupTests(unittest.TestCase):
    """Direct unit tests for the registry.lookup function."""

    def test_lookup_known_id_returns_definition(self) -> None:
        """lookup returns a CheckDefinition for a registered check ID."""
        result = lookup("check-local-contracts")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CheckDefinition)

    def test_lookup_unknown_id_returns_none(self) -> None:
        """lookup returns None for an ID that is not in the registry."""
        result = lookup("no-such-check")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
