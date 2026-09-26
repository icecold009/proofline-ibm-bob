"""Deterministic evidence-to-status calculation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any

from .model import Check, Claim, Manifest
from .registry import lookup


def _canonical_manifest(manifest: Manifest) -> str:
    payload = {
        "scenario": manifest.scenario,
        "claims": [asdict(claim) for claim in manifest.claims],
        "checks": [asdict(check) for check in manifest.checks],
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


def analyze_manifest(manifest: Manifest, *, generated_at: str | None = None) -> dict[str, Any]:
    """Calculate a stable report without commands, network access, or providers."""

    # Build a normalized check list without mutating the frozen manifest.
    # Any check whose ID is absent from the static registry has its result
    # overridden to "blocked" regardless of the value supplied in the manifest.
    # The manifest itself is accepted (registry membership is not a validation
    # concern); this override happens here, before claims are evaluated.
    normalized_checks: list[Check] = [
        check
        if lookup(check.id) is not None
        else Check(
            id=check.id,
            result="blocked",
            evidence_class=check.evidence_class,
            source=check.source,
        )
        for check in manifest.checks
    ]

    checks_by_id = {check.id: check for check in normalized_checks}
    claims = [_claim_result(claim, checks_by_id) for claim in manifest.claims]
    statuses = {status: 0 for status in ("proven", "conditional", "simulated", "unverified", "blocked")}
    for claim in claims:
        statuses[claim["status"]] += 1

    report_seed = _canonical_manifest(manifest).encode("utf-8")
    report_id = f"report-{hashlib.sha256(report_seed).hexdigest()[:12]}"
    return {
        "report_id": report_id,
        "generated_at": generated_at,
        "scenario": manifest.scenario,
        "claims": claims,
        "checks": [
            {
                "id": check.id,
                "result": check.result,
                "evidence_class": check.evidence_class,
                "source": check.source,
            }
            for check in normalized_checks
        ],
        "summary": statuses,
        "limitations": sorted({claim["limitation"] for claim in claims}),
        "security_notes": [
            "Check IDs are resolved against the static code-owned registry; "
            "no commands were executed.",
            "No network or provider access was used.",
            "Claim-supplied status values are not trusted; statuses are derived from evidence.",
        ],
    }
