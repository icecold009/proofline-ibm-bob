"""Tests for bounded local check execution (milestone 7A).

Security and behavior requirements covered:
  1. Unknown and injection-shaped IDs return blocked without calling subprocess.
  2. FIXTURE_EVIDENCE returns "fixture" without calling subprocess.
  3. RUN_LOCAL_CONTRACTS calls subprocess with:
       - the exact fixed argv (sys.executable + scripts/verify.py)
       - shell=False
       - the registry timeout (30 s)
       - the derived cwd
       - an explicitly constructed environment (not inherited)
  4. Zero exit code -> result "pass".
  5. Nonzero exit code -> failure_status ("blocked").
  6. subprocess.TimeoutExpired -> failure_status.
  7. FileNotFoundError -> failure_status.
  8. Captured output is NOT present in the returned CheckRunResult.
  9. REGISTRY cannot be mutated at runtime (immutability regression).
 10. analyze_manifest itself never calls run_check or subprocess.
 11. CLI run-check rejects unknown IDs before dispatching (exit 1, no process).
 12. CLI run-check succeeds for fixture marker (exit 1 because result != "pass",
     but no subprocess launched).
 13. REGRESSION: run_check public signature takes only check_id; passing
     repo_root raises TypeError (no caller-controlled root override).
 14. REGRESSION: argv and cwd are rooted at the package-derived _REPO_ROOT,
     not at any caller-supplied path.

All subprocess.run calls are mocked so the test suite never recursively
invokes scripts/verify.py or any other process.

Test seam for argv/cwd shape:
    patch("proofline.runner._REPO_ROOT", Path("/fake/repo"))
This patches the module-level constant that _run_local_contracts reads, so
the tests can verify the exact argv and cwd without a real repository layout.
"""

from __future__ import annotations

import inspect
import io
import subprocess
import sys
import types
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from proofline import (
    CheckRunResult,
    analyze_manifest,
    validate_manifest,
)
from proofline.registry import REGISTRY, OperationKind, lookup
from proofline.runner import run_check

# Stable fake repo root used when patching the internal seam.
_FAKE_ROOT = Path("/fake/repo")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _completed(returncode: int = 0) -> subprocess.CompletedProcess:
    """Return a minimal CompletedProcess with stdout/stderr set."""
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=b"some output that must not leak",
        stderr=b"some stderr that must not leak",
    )


# ---------------------------------------------------------------------------
# 13. REGRESSION: public signature rejects repo_root
# ---------------------------------------------------------------------------

class PublicSignatureRegressionTest(unittest.TestCase):
    """run_check must accept only check_id; any attempt to pass repo_root
    must raise TypeError immediately, before any registry lookup occurs."""

    def test_run_check_rejects_repo_root_kwarg(self) -> None:
        """Passing repo_root= to run_check must raise TypeError."""
        with self.assertRaises(TypeError):
            run_check("check-local-contracts", repo_root=Path("/some/path"))  # type: ignore[call-arg]

    def test_run_check_signature_has_only_check_id(self) -> None:
        """run_check must have exactly one parameter: check_id."""
        sig = inspect.signature(run_check)
        param_names = list(sig.parameters)
        self.assertEqual(param_names, ["check_id"],
                         f"Expected only 'check_id', got {param_names!r}")


# ---------------------------------------------------------------------------
# 14. REGRESSION: argv and cwd rooted at package-derived _REPO_ROOT
# ---------------------------------------------------------------------------

class RootDerivationRegressionTest(unittest.TestCase):
    """argv and cwd must be rooted at proofline.runner._REPO_ROOT, which is
    derived from the module's own location, not from any caller-supplied path."""

    def test_argv_rooted_at_module_derived_root(self) -> None:
        """argv[1] must be _REPO_ROOT/scripts/verify.py."""
        with (
            unittest.mock.patch("proofline.runner._REPO_ROOT", _FAKE_ROOT),
            unittest.mock.patch("proofline.runner.subprocess.run",
                                return_value=_completed(0)) as mock_run,
        ):
            run_check("check-local-contracts")

        argv = mock_run.call_args[0][0]
        expected_script = str(_FAKE_ROOT / "scripts" / "verify.py")
        self.assertEqual(argv[1], expected_script)

    def test_cwd_rooted_at_module_derived_root(self) -> None:
        """cwd must be derived from _REPO_ROOT + registry working_dir."""
        defn = lookup("check-local-contracts")
        assert defn is not None
        expected_cwd = (_FAKE_ROOT / defn.working_dir).resolve()

        with (
            unittest.mock.patch("proofline.runner._REPO_ROOT", _FAKE_ROOT),
            unittest.mock.patch("proofline.runner.subprocess.run",
                                return_value=_completed(0)) as mock_run,
        ):
            run_check("check-local-contracts")

        call_kwargs = mock_run.call_args[1]
        self.assertEqual(call_kwargs.get("cwd"), expected_cwd)


# ---------------------------------------------------------------------------
# 1-2. Unknown and injection-shaped IDs: blocked, no subprocess
# ---------------------------------------------------------------------------

class UnknownIdBlockingTests(unittest.TestCase):
    """run_check must return blocked for any ID not in the registry, without
    calling subprocess.run."""

    def _assert_blocked_no_subprocess(self, check_id: str) -> None:
        with unittest.mock.patch("proofline.runner.subprocess.run") as mock_run:
            result = run_check(check_id)
        mock_run.assert_not_called()
        self.assertEqual(result.result, "blocked")
        self.assertIsInstance(result, CheckRunResult)

    def test_unregistered_id_blocked_no_subprocess(self) -> None:
        self._assert_blocked_no_subprocess("unregistered-check")

    def test_semicolon_injection_blocked_no_subprocess(self) -> None:
        self._assert_blocked_no_subprocess("check-local-contracts; rm -rf /")

    def test_pipe_injection_blocked_no_subprocess(self) -> None:
        self._assert_blocked_no_subprocess("check-local-contracts | cat /etc/passwd")

    def test_subshell_injection_blocked_no_subprocess(self) -> None:
        self._assert_blocked_no_subprocess("$(whoami)")

    def test_env_var_injection_blocked_no_subprocess(self) -> None:
        self._assert_blocked_no_subprocess("$HOME")

    def test_path_traversal_blocked_no_subprocess(self) -> None:
        self._assert_blocked_no_subprocess("../../etc/passwd")


# ---------------------------------------------------------------------------
# 2. FIXTURE_EVIDENCE: returns "fixture", never calls subprocess
# ---------------------------------------------------------------------------

class FixtureEvidenceTests(unittest.TestCase):
    """FIXTURE_EVIDENCE must return "fixture" deterministically without
    starting a process, and must never treat timeout_s=0 as a timeout."""

    def test_fixture_evidence_returns_fixture_no_subprocess(self) -> None:
        with unittest.mock.patch("proofline.runner.subprocess.run") as mock_run:
            result = run_check("fixture-simulated-telemetry")
        mock_run.assert_not_called()
        self.assertEqual(result.result, "fixture")
        self.assertEqual(result.check_id, "fixture-simulated-telemetry")
        self.assertEqual(result.evidence_class, "local")

    def test_fixture_evidence_does_not_read_timeout_as_process_timeout(self) -> None:
        """Confirm the definition has timeout_s=0 and that the handler
        never passes it to subprocess."""
        defn = lookup("fixture-simulated-telemetry")
        self.assertIsNotNone(defn)
        self.assertEqual(defn.timeout_s, 0)  # type: ignore[union-attr]
        # The handler never calls subprocess regardless of timeout_s value.
        with unittest.mock.patch("proofline.runner.subprocess.run") as mock_run:
            run_check("fixture-simulated-telemetry")
        mock_run.assert_not_called()


# ---------------------------------------------------------------------------
# 3-8. RUN_LOCAL_CONTRACTS: subprocess call shape and result mapping
# ---------------------------------------------------------------------------

class LocalContractsSubprocessTests(unittest.TestCase):
    """Tests that RUN_LOCAL_CONTRACTS calls subprocess with the exact
    required parameters and maps exit codes correctly.

    The internal seam proofline.runner._REPO_ROOT is patched to _FAKE_ROOT
    so tests verify the exact argv/cwd shape without requiring a real layout.
    """

    def _run_with_mock(
        self,
        returncode: int = 0,
        side_effect: BaseException | None = None,
    ) -> tuple[CheckRunResult, unittest.mock.MagicMock]:
        with (
            unittest.mock.patch("proofline.runner._REPO_ROOT", _FAKE_ROOT),
            unittest.mock.patch("proofline.runner.subprocess.run") as mock_run,
        ):
            if side_effect is not None:
                mock_run.side_effect = side_effect
            else:
                mock_run.return_value = _completed(returncode)
            result = run_check("check-local-contracts")
        return result, mock_run

    def test_uses_fixed_argv_with_sys_executable(self) -> None:
        """argv must be [sys.executable, <_REPO_ROOT>/scripts/verify.py]."""
        _result, mock_run = self._run_with_mock(returncode=0)
        call_args = mock_run.call_args
        argv = call_args[0][0]  # first positional arg
        self.assertEqual(argv[0], sys.executable)
        expected_script = str(_FAKE_ROOT / "scripts" / "verify.py")
        self.assertEqual(argv[1], expected_script,
                         f"Expected {expected_script!r}, got {argv[1]!r}")

    def test_shell_is_false(self) -> None:
        """shell=False must be set — never interpret argv as a shell string."""
        _result, mock_run = self._run_with_mock(returncode=0)
        call_kwargs = mock_run.call_args[1]
        self.assertIs(call_kwargs.get("shell"), False)

    def test_uses_registry_timeout(self) -> None:
        """timeout must come from the registry definition (30 s)."""
        defn = lookup("check-local-contracts")
        self.assertIsNotNone(defn)
        _result, mock_run = self._run_with_mock(returncode=0)
        call_kwargs = mock_run.call_args[1]
        self.assertEqual(call_kwargs.get("timeout"), defn.timeout_s)  # type: ignore[union-attr]

    def test_uses_derived_cwd(self) -> None:
        """cwd must be derived from _REPO_ROOT + registry working_dir."""
        defn = lookup("check-local-contracts")
        self.assertIsNotNone(defn)
        expected_cwd = (_FAKE_ROOT / defn.working_dir).resolve()  # type: ignore[union-attr]
        _result, mock_run = self._run_with_mock(returncode=0)
        call_kwargs = mock_run.call_args[1]
        self.assertEqual(call_kwargs.get("cwd"), expected_cwd)

    def test_env_is_explicit_dict_not_inherited(self) -> None:
        """env must be an explicitly constructed dict, not None (full inherit).

        The dict contains only keys from allowed_env that exist in os.environ
        (currently SYSTEMROOT/SystemRoot on Windows for asyncio DLL loading).
        It must never be None, which would inherit the full parent environment.
        """
        _result, mock_run = self._run_with_mock(returncode=0)
        call_kwargs = mock_run.call_args[1]
        env = call_kwargs.get("env")
        # env must be a dict, not None (None would inherit the full environment).
        self.assertIsInstance(env, dict)
        # The dict must contain only allowed keys — never arbitrary env vars.
        defn = lookup("check-local-contracts")
        assert defn is not None
        for key in env:
            self.assertIn(key, defn.allowed_env,
                          f"env key {key!r} is not in allowed_env allowlist")

    def test_capture_output_is_true(self) -> None:
        """capture_output=True must be set so output is never printed."""
        _result, mock_run = self._run_with_mock(returncode=0)
        call_kwargs = mock_run.call_args[1]
        self.assertIs(call_kwargs.get("capture_output"), True)

    def test_zero_exit_returns_pass(self) -> None:
        result, _ = self._run_with_mock(returncode=0)
        self.assertEqual(result.result, "pass")

    def test_nonzero_exit_returns_failure_status(self) -> None:
        defn = lookup("check-local-contracts")
        self.assertIsNotNone(defn)
        result, _ = self._run_with_mock(returncode=1)
        self.assertEqual(result.result, defn.failure_status)  # type: ignore[union-attr]

    def test_timeout_returns_failure_status(self) -> None:
        defn = lookup("check-local-contracts")
        self.assertIsNotNone(defn)
        result, _ = self._run_with_mock(
            side_effect=subprocess.TimeoutExpired(cmd=[], timeout=30)
        )
        self.assertEqual(result.result, defn.failure_status)  # type: ignore[union-attr]

    def test_file_not_found_returns_failure_status(self) -> None:
        defn = lookup("check-local-contracts")
        self.assertIsNotNone(defn)
        result, _ = self._run_with_mock(side_effect=FileNotFoundError())
        self.assertEqual(result.result, defn.failure_status)  # type: ignore[union-attr]

    def test_output_not_in_result(self) -> None:
        """Subprocess stdout/stderr must not appear anywhere in CheckRunResult."""
        result, _ = self._run_with_mock(returncode=0)
        # CheckRunResult has only check_id, result, evidence_class.
        self.assertFalse(hasattr(result, "stdout"))
        self.assertFalse(hasattr(result, "stderr"))
        self.assertFalse(hasattr(result, "output"))


# ---------------------------------------------------------------------------
# 9. REGISTRY immutability
# ---------------------------------------------------------------------------

class RegistryImmutabilityTest(unittest.TestCase):
    """REGISTRY must be a MappingProxyType; mutation must raise TypeError."""

    def test_registry_is_mapping_proxy(self) -> None:
        self.assertIsInstance(REGISTRY, types.MappingProxyType)

    def test_registry_cannot_be_mutated(self) -> None:
        with self.assertRaises(TypeError):
            REGISTRY["injected-key"] = None  # type: ignore[index]

    def test_registry_existing_entries_intact(self) -> None:
        self.assertIn("check-local-contracts", REGISTRY)
        self.assertIn("fixture-simulated-telemetry", REGISTRY)


# ---------------------------------------------------------------------------
# 10. analyze_manifest never calls subprocess
# ---------------------------------------------------------------------------

class AnalyzeManifestNoSubprocessTest(unittest.TestCase):
    """analyze_manifest must remain deterministic and command-free; it must
    never call run_check or subprocess.run, even for registered check IDs."""

    def test_analyze_manifest_never_calls_subprocess(self) -> None:
        raw = {
            "scenario": "no-exec-test",
            "claims": [
                {
                    "id": "claim-1",
                    "title": "Local contracts",
                    "evidence_class": "local",
                    "evidence_refs": ["check-local-contracts"],
                }
            ],
            "checks": [
                {
                    "id": "check-local-contracts",
                    "result": "pass",
                    "evidence_class": "local",
                    "source": "test",
                }
            ],
        }
        manifest = validate_manifest(raw)
        with unittest.mock.patch("subprocess.run") as mock_run:
            with unittest.mock.patch("proofline.runner.subprocess.run") as mock_runner_run:
                analyze_manifest(manifest)
        mock_run.assert_not_called()
        mock_runner_run.assert_not_called()


# ---------------------------------------------------------------------------
# 11-12. CLI run-check: unknown ID blocked (no process); fixture marker works
# ---------------------------------------------------------------------------

class CliRunCheckTests(unittest.TestCase):
    """CLI run-check must gate on the registry before dispatching."""

    def _invoke_cli(self, argv: list[str]) -> tuple[int, str, str]:
        """Run main() with captured stdout/stderr; return (exit_code, out, err)."""
        from proofline.__main__ import main
        buf_out = io.StringIO()
        buf_err = io.StringIO()
        with (
            unittest.mock.patch("sys.stdout", buf_out),
            unittest.mock.patch("sys.stderr", buf_err),
        ):
            exit_code = main(argv)
        return exit_code, buf_out.getvalue(), buf_err.getvalue()

    def test_unknown_id_exits_1_no_subprocess(self) -> None:
        with unittest.mock.patch("proofline.runner.subprocess.run") as mock_run:
            exit_code, _out, err = self._invoke_cli(["run-check", "no-such-check"])
        mock_run.assert_not_called()
        self.assertEqual(exit_code, 1)
        self.assertIn("blocked", err)

    def test_injection_id_exits_1_no_subprocess(self) -> None:
        with unittest.mock.patch("proofline.runner.subprocess.run") as mock_run:
            exit_code, _out, err = self._invoke_cli(["run-check", "$(whoami)"])
        mock_run.assert_not_called()
        self.assertEqual(exit_code, 1)
        self.assertIn("blocked", err)

    def test_fixture_marker_exits_1_no_subprocess(self) -> None:
        """fixture-simulated-telemetry returns result="fixture"; exit code is 1
        (not "pass"), but no subprocess is launched."""
        with unittest.mock.patch("proofline.runner.subprocess.run") as mock_run:
            exit_code, out, _err = self._invoke_cli(
                ["run-check", "fixture-simulated-telemetry"]
            )
        mock_run.assert_not_called()
        self.assertEqual(exit_code, 1)  # "fixture" != "pass"
        import json as _json
        data = _json.loads(out)
        self.assertEqual(data["result"], "fixture")

    def test_known_check_calls_subprocess(self) -> None:
        """check-local-contracts reaches subprocess (mocked to pass)."""
        with unittest.mock.patch(
            "proofline.runner.subprocess.run",
            return_value=_completed(0),
        ) as mock_run:
            exit_code, out, _err = self._invoke_cli(
                ["run-check", "check-local-contracts"]
            )
        mock_run.assert_called_once()
        self.assertEqual(exit_code, 0)
        import json as _json
        data = _json.loads(out)
        self.assertEqual(data["result"], "pass")


if __name__ == "__main__":
    unittest.main()
