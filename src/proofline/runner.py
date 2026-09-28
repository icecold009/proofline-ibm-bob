"""Bounded local check execution for Proofline.

This module is the ONLY place in Proofline that may call subprocess.
Every execution path is gated by the static, code-owned registry.

Security contract
-----------------
- check_id is the ONLY input to run_check.  No caller may supply a working
  directory, executable path, argv fragment, environment variable name,
  timeout value, or repository root.  All of these are code-owned and derived
  from this module's own location on the filesystem.
- The repository root is derived from the location of this module file:
      Path(__file__).resolve().parents[2]
  This places it two levels above src/proofline/, which is the repository root.
  No external caller can override this derivation.
- check_id is resolved through registry.lookup before any dispatch occurs.
  Unknown or unregistered IDs return a blocked result without reaching subprocess.
- The argv vector for each operation is a fixed, code-owned list.  It is never
  constructed from user input.
- shell=False is enforced for every subprocess call.
- The process environment is explicitly constructed from the registry's
  allowed_env tuple.  The full parent environment is never inherited.
- Captured output is discarded and never placed in any returned structure
  or in reports.

FIXTURE_EVIDENCE exception
--------------------------
OperationKind.FIXTURE_EVIDENCE is a deterministic fixture marker.  Its
handler returns a fixed result without starting any process.  The timeout_s=0
sentinel in its CheckDefinition is never read as an executable timeout.
This is an explicitly documented exception to the general execution flow.

analyze_manifest contract
-------------------------
analyze_manifest in engine.py never calls run_check.  It reads manifest-
supplied check results (after registry-based blocking) and derives statuses
deterministically.  The security note in every report accurately reflects
this: "Check IDs are checked against the static code-owned registry; no
commands were executed."  Calling run_check is an explicit, separate action
available only through the run-check CLI subcommand.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .registry import CheckDefinition, OperationKind, lookup

# ---------------------------------------------------------------------------
# Code-owned repository root.
#
# Derived from this module's own location — never from a caller argument.
# runner.py lives at <repo>/src/proofline/runner.py:
#   parents[0] = <repo>/src/proofline/
#   parents[1] = <repo>/src/
#   parents[2] = <repo>/          <-- repository root
#
# Tests that need to probe argv/cwd shape should patch this name via
# unittest.mock.patch("proofline.runner._REPO_ROOT", <fake_path>).
# ---------------------------------------------------------------------------

_REPO_ROOT: Path = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class CheckRunResult:
    """The result of invoking one registered local check.

    Fields
    ------
    check_id        The stable registry ID that was run.
    result          "pass", "fail", "blocked", or "fixture".
    evidence_class  Evidence class from the registry definition.
    """

    check_id: str
    result: str
    evidence_class: str
    source: str = "Proofline allowlisted local runner"
    provenance: str = "runner-observed"
    observed_at: str | None = None


# ---------------------------------------------------------------------------
# Internal per-operation handlers.
#
# Each handler receives:
#   defn      CheckDefinition from the static registry
#
# Handlers read only defn and the module-level _REPO_ROOT constant.
# They must not accept or use any data from manifests, fixtures, or
# CLI arguments.
# ---------------------------------------------------------------------------

def _run_local_contracts(defn: CheckDefinition) -> str:
    """Invoke scripts/verify.py with a fixed, code-owned argv.

    The script path is constructed from _REPO_ROOT, which is derived from
    this module's own location — never from a caller-supplied argument.

    Returns "pass" on exit code 0, defn.failure_status on any other outcome.
    Captured stdout/stderr is discarded and never surfaced.
    """
    # Fixed argv — code-owned, derived from _REPO_ROOT.
    argv = [sys.executable, str(_REPO_ROOT / "scripts" / "verify.py")]

    # Environment: construct explicitly from the allowed_env allowlist.
    # SYSTEMROOT/SystemRoot are included for Windows asyncio DLL initialisation.
    # No other environment variables are passed; the full parent env is not
    # inherited.
    env: dict[str, str] = {
        key: os.environ[key]
        for key in defn.allowed_env
        if key in os.environ
    }

    # Working directory: derived from _REPO_ROOT + registry working_dir.
    # defn.working_dir is "." so this resolves to _REPO_ROOT itself.
    cwd = (_REPO_ROOT / defn.working_dir).resolve()

    try:
        proc = subprocess.run(
            argv,
            shell=False,           # never interpret as a shell command
            check=False,           # we handle the return code ourselves
            capture_output=True,   # discard stdout/stderr — never surfaced
            timeout=defn.timeout_s,
            env=env,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired:
        return defn.failure_status
    except (FileNotFoundError, OSError):
        return defn.failure_status

    return "pass" if proc.returncode == 0 else defn.failure_status


def _fixture_evidence(defn: CheckDefinition) -> str:  # noqa: ARG001
    """Return fixture evidence deterministically without starting any process.

    timeout_s=0 in the registry entry for FIXTURE_EVIDENCE is a sentinel that
    means 'not applicable'.  This handler explicitly does NOT use it as a
    process timeout.  No subprocess is launched.
    """
    return "fixture"


# ---------------------------------------------------------------------------
# Dispatch table — maps each OperationKind to its handler.
#
# This table is defined once at module load.  It is a module-private dict
# and is never exposed to callers or accepted from external input.
# ---------------------------------------------------------------------------

_DISPATCH: dict[OperationKind, Callable[[CheckDefinition], str]] = {
    OperationKind.RUN_LOCAL_CONTRACTS: _run_local_contracts,
    OperationKind.FIXTURE_EVIDENCE: _fixture_evidence,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_check(check_id: str) -> CheckRunResult:
    """Run one registered local check and return its result.

    Parameters
    ----------
    check_id   The stable registry ID to run.  This is the ONLY input.
               It is resolved through the static registry; unknown or
               injection-shaped IDs return a blocked result without reaching
               subprocess.

               No other parameter is accepted.  The repository root,
               working directory, executable path, argv, environment, and
               timeout are all code-owned and derived from this module's
               own location.

    Returns
    -------
    CheckRunResult with result "pass", "fail", "blocked", or "fixture".
    Output from any subprocess is discarded and never included.
    """
    defn: CheckDefinition | None = lookup(check_id)
    if defn is None:
        # Unknown or injection-shaped ID — blocked without any process launch.
        return CheckRunResult(
            check_id=check_id,
            result="blocked",
            evidence_class="local",
            source="Unknown check ID; no process was launched",
            provenance="registry-blocked",
        )

    handler = _DISPATCH.get(defn.operation)
    if handler is None:
        # Registered ID with an unmapped OperationKind — should not happen,
        # but fail closed rather than silently succeed.
        return CheckRunResult(
            check_id=check_id,
            result=defn.failure_status,
            evidence_class=defn.evidence_class,
            source="Registered operation has no runner",
            provenance="runner-error",
        )

    result = handler(defn)
    is_fixture = defn.operation is OperationKind.FIXTURE_EVIDENCE
    return CheckRunResult(
        check_id=check_id,
        result=result,
        evidence_class=defn.evidence_class,
        source="Synthetic fixture marker" if is_fixture else "Proofline allowlisted local runner",
        provenance="synthetic-fixture" if is_fixture else "runner-observed",
        observed_at=(
            None
            if is_fixture
            else datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        ),
    )
