"""Deterministic evidence-to-status calculation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .model import Check, Claim, Manifest
from .registry import lookup
from .runner import CheckRunResult


def _canonical_manifest(manifest: Manifest, checks: list[Check]) -> str:
    payload = {
        "scenario": manifest.scenario,
        "change_request": manifest.change_request,
        "claims": [asdict(claim) for claim in manifest.claims],
        "checks": [
            {
                "id": check.id,
                "result": check.result,
                "evidence_class": check.evidence_class,
                "source": check.source,
                "provenance": check.provenance,
            }
            for check in checks
        ],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _claim_result(claim: Claim, checks_by_id: dict[str, Any]) -> dict[str, Any]:
    if not claim.evidence_refs:
        return {
            "id": claim.id,
            "title": claim.title,
            "evidence_class": claim.evidence_class,
            "status": "unverified",
            "evidence_refs": [],
            "limitation": claim.limitation or "No supporting evidence was supplied.",
            "next_action": "Supply a check or artifact from the declared evidence class.",
        }

    missing = [ref for ref in claim.evidence_refs if ref not in checks_by_id]
    if missing:
        return {
            "id": claim.id,
            "title": claim.title,
            "evidence_class": claim.evidence_class,
            "status": "blocked",
            "evidence_refs": list(claim.evidence_refs),
            "limitation": f"Referenced checks are missing: {', '.join(missing)}.",
            "next_action": "Add the referenced evidence or remove the stale reference.",
        }

    checks = [checks_by_id[ref] for ref in claim.evidence_refs]
    if any(check.result == "blocked" for check in checks):
        status = "blocked"
        limitation = "At least one required check was blocked."
        next_action = "Resolve the blocked check before making the claim."
    elif any(check.result == "fail" for check in checks):
        status = "unverified"
        limitation = "At least one required check failed."
        next_action = "Fix the failing check and rerun the report."
    elif any(check.result == "fixture" for check in checks):
        status = "simulated"
        limitation = claim.limitation or "Fixture evidence is not live behavior."
        next_action = "Replace the fixture with evidence from the declared environment."
    elif any(check.evidence_class != claim.evidence_class for check in checks):
        status = "conditional"
        limitation = claim.limitation or "Supporting evidence came from a different evidence class."
        next_action = "Repeat the check in the declared evidence class."
    elif any(
        check.provenance != "runner-observed" or not check.observed_at
        for check in checks
    ):
        status = "conditional"
        limitation = claim.limitation or (
            "The manifest declares a passing result; Proofline did not run or independently verify it."
        )
        next_action = "Run the registered check with Proofline's explicit run-report command."
    else:
        status = "proven"
        limitation = claim.limitation or "Evidence passed in the declared evidence class."
        next_action = "Keep the evidence artifact with the release record."

    return {
        "id": claim.id,
        "title": claim.title,
        "evidence_class": claim.evidence_class,
        "status": status,
        "evidence_refs": list(claim.evidence_refs),
        "limitation": limitation,
        "next_action": next_action,
    }


def analyze_manifest(
    manifest: Manifest,
    *,
    generated_at: str | None = None,
    runner_results: Mapping[str, CheckRunResult] | None = None,
) -> dict[str, Any]:
    """Calculate a stable report without commands, network access, or providers."""

    observed = runner_results or {}
    # Build a normalized check list without mutating the frozen manifest.
    # Any check whose ID is absent from the static registry has its result
    # overridden to "blocked" regardless of the value supplied in the manifest.
    # The manifest itself is accepted (registry membership is not a validation
    # concern); this override happens here, before claims are evaluated.
    normalized_checks: list[Check] = []
    for check in manifest.checks:
        if lookup(check.id) is None:
            normalized_checks.append(Check(
            id=check.id,
            result="blocked",
            evidence_class=check.evidence_class,
            source=check.source,
            provenance="registry-blocked",
        ))
            continue
        result = observed.get(check.id)
        if result is not None and result.check_id == check.id:
            normalized_checks.append(Check(
                id=check.id,
                result=result.result,
                evidence_class=result.evidence_class,
                source=result.source,
                provenance=result.provenance,
                observed_at=result.observed_at,
            ))
        else:
            normalized_checks.append(check)

    checks_by_id = {check.id: check for check in normalized_checks}
    claims = [_claim_result(claim, checks_by_id) for claim in manifest.claims]
    statuses = {status: 0 for status in ("proven", "conditional", "simulated", "unverified", "blocked")}
    for claim in claims:
        statuses[claim["status"]] += 1

    report_seed = _canonical_manifest(manifest, normalized_checks).encode("utf-8")
    report_id = f"report-{hashlib.sha256(report_seed).hexdigest()[:12]}"
    return {
        "report_id": report_id,
        "generated_at": generated_at,
        "scenario": manifest.scenario,
        "change_request": manifest.change_request,
        "claims": claims,
        "checks": [
            {
                "id": check.id,
                "result": check.result,
                "evidence_class": check.evidence_class,
                "source": check.source,
                "provenance": check.provenance,
                "observed_at": check.observed_at,
            }
            for check in normalized_checks
        ],
        "summary": statuses,
        "limitations": sorted({claim["limitation"] for claim in claims}),
        "security_notes": [
            (
                "This report resolved referenced entries through the explicit run-report workflow. "
                "Only code-owned allowlisted operations were considered; no manifest command was executed."
                if observed
                else "This report did not execute checks; manifest-declared results are not independently verified."
            ),
            "Check IDs are resolved against the static code-owned registry.",
            "No network or provider access was used.",
            "Claim-supplied status values are ignored; statuses are derived from evidence and provenance.",
        ],
    }
