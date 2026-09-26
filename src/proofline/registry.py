"""Code-owned check registry for Proofline.

This module is the single source of truth for all permitted check IDs.
It is never constructed from user input, manifest data, or external configuration.

Each supported check ID maps to a CheckDefinition that names the intended
local operation as a symbolic OperationKind constant and records the metadata
required by the spec (timeout, working directory, allowed environment variables,
output redaction policy, evidence class, and failure status).

FIXTURE_EVIDENCE exception — OperationKind.FIXTURE_EVIDENCE is a deterministic
fixture marker.  Its timeout_s=0 is a sentinel meaning "not applicable"; the
runner explicitly does NOT use it as a process timeout and does NOT start a
subprocess for this operation kind.  This exception is documented in runner.py.
"""

from __future__ import annotations

import types
from dataclasses import dataclass
from enum import Enum


class OperationKind(str, Enum):
    """Symbolic identifiers for the local operations Proofline supports.

    Values are stable string constants fixed in code.  They are never
    interpolated into shell strings, passed to subprocess, or constructed
    from user input.
    """

    RUN_LOCAL_CONTRACTS = "run-local-contracts"
    FIXTURE_EVIDENCE = "fixture-evidence"


@dataclass(frozen=True)
class CheckDefinition:
    """All metadata the spec requires for a registry entry.

    Fields
    ------
    operation       Symbolic operation kind (never a shell string).
    evidence_class  Evidence class this check contributes to.
    failure_status  Status assigned to a dependent claim when this check fails.
    timeout_s       Execution timeout in seconds.  0 means not applicable
                    (used for FIXTURE_EVIDENCE, which is never executed).
    working_dir     Working directory for future execution.  Stored but not
                    used in this milestone.
    allowed_env     Environment variable names permitted during execution.
                    Empty tuple means no extra variables allowed.
    redact_output   Whether check output must be redacted from reports.
    """

    operation: OperationKind
    evidence_class: str
    failure_status: str
    timeout_s: int
    working_dir: str
    allowed_env: tuple[str, ...]
    redact_output: bool


# ---------------------------------------------------------------------------
# Static, code-owned registry.  Keys are stable check IDs.  The registry is
# wrapped in MappingProxyType so it cannot be mutated at runtime.
# ---------------------------------------------------------------------------

REGISTRY: types.MappingProxyType[str, CheckDefinition] = types.MappingProxyType(
    {
        "check-local-contracts": CheckDefinition(
            operation=OperationKind.RUN_LOCAL_CONTRACTS,
            evidence_class="local",
            failure_status="blocked",
            timeout_s=30,
            working_dir=".",
            # SYSTEMROOT / SystemRoot are required on Windows for the asyncio
            # and socket DLLs to load inside the subprocess.  They are
            # read-only system paths with no security implication.
            # No other environment variables are inherited.
            allowed_env=("SYSTEMROOT", "SystemRoot"),
            redact_output=False,
        ),
        "fixture-simulated-telemetry": CheckDefinition(
            # FIXTURE_EVIDENCE is a fixture-evidence marker, not an executable
            # operation.  timeout_s=0 signals "not applicable"; the runner
            # explicitly does NOT interpret this as a process timeout and does
            # NOT start a subprocess for this operation kind.
            operation=OperationKind.FIXTURE_EVIDENCE,
            evidence_class="local",
            failure_status="blocked",
            timeout_s=0,
            working_dir=".",
            allowed_env=(),
            redact_output=False,
        ),
    }
)


def lookup(check_id: str) -> CheckDefinition | None:
    """Return the CheckDefinition for check_id, or None if not registered.

    This function never formats check_id into a shell string, never calls
    subprocess, and never raises.  Unknown IDs silently return None so that
    callers can enforce the blocked-result contract without catching exceptions.
    """
    return REGISTRY.get(check_id)
