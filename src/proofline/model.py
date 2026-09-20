"""Strict, local-only input models for Proofline.

This module validates untrusted JSON before the report engine sees it. It does
not execute commands, access the network, or trust a caller-supplied status.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

EVIDENCE_CLASSES = frozenset({"local", "browser", "hosted", "provider", "data", "security"})
CHECK_RESULTS = frozenset({"pass", "fail", "fixture", "blocked"})
MAX_MANIFEST_BYTES = 256 * 1024
MAX_CLAIMS = 50
MAX_CHECKS = 100
MAX_TEXT = 500


class ValidationError(ValueError):
    """Raised when a manifest is malformed or exceeds its safety limits."""


@dataclass(frozen=True)
class Check:
    id: str
    result: str
    evidence_class: str
    source: str


@dataclass(frozen=True)
class Claim:
    id: str
    title: str
    evidence_class: str
    evidence_refs: tuple[str, ...]
    limitation: str | None = None


@dataclass(frozen=True)
class Manifest:
    scenario: str
    claims: tuple[Claim, ...]
    checks: tuple[Check, ...]


def _text(value: Any, field: str, *, required: bool = True) -> str:
    if not isinstance(value, str) or not value.strip():
        if required:
            raise ValidationError(f"{field} must be a non-empty string")
        return ""
    value = value.strip()
    if len(value) > MAX_TEXT:
        raise ValidationError(f"{field} exceeds {MAX_TEXT} characters")
    return value


def _list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{field} must be an array")
    return value


def _unique_ids(values: list[str], field: str) -> tuple[str, ...]:
    if len(values) != len(set(values)):
        raise ValidationError(f"{field} contains duplicate IDs")
    return tuple(values)


def validate_manifest(raw: Mapping[str, Any]) -> Manifest:
    """Validate an input object and return a typed manifest.

    The optional status field is accepted for fixture readability but is
    intentionally ignored. Status is always derived from evidence below.
    """

    if not isinstance(raw, Mapping):
        raise ValidationError("manifest must be a JSON object")

    allowed_root = {"scenario", "claims", "checks"}
    unknown_root = set(raw) - allowed_root
    if unknown_root:
        raise ValidationError(f"unknown manifest fields: {sorted(unknown_root)}")

    scenario = _text(raw.get("scenario"), "scenario")
    raw_claims = _list(raw.get("claims"), "claims")
    raw_checks = _list(raw.get("checks"), "checks")

    if len(raw_claims) > MAX_CLAIMS:
        raise ValidationError(f"claims exceeds limit of {MAX_CLAIMS}")
    if len(raw_checks) > MAX_CHECKS:
        raise ValidationError(f"checks exceeds limit of {MAX_CHECKS}")

    claims: list[Claim] = []
    claim_ids: list[str] = []
    for index, item in enumerate(raw_claims):
        field = f"claims[{index}]"
        if not isinstance(item, Mapping):
            raise ValidationError(f"{field} must be an object")
        allowed = {"id", "title", "evidence_class", "evidence_refs", "status", "limitation"}
        unknown = set(item) - allowed
        if unknown:
            raise ValidationError(f"{field} has unknown fields: {sorted(unknown)}")

        claim_id = _text(item.get("id"), f"{field}.id")
        evidence_class = _text(item.get("evidence_class"), f"{field}.evidence_class")
        if evidence_class not in EVIDENCE_CLASSES:
            raise ValidationError(f"{field}.evidence_class is not supported")

        raw_refs = _list(item.get("evidence_refs", []), f"{field}.evidence_refs")
        refs = [_text(ref, f"{field}.evidence_refs[{ref_index}]") for ref_index, ref in enumerate(raw_refs)]
        claims.append(
            Claim(
                id=claim_id,
                title=_text(item.get("title"), f"{field}.title"),
                evidence_class=evidence_class,
                evidence_refs=_unique_ids(refs, f"{field}.evidence_refs"),
                limitation=_text(item.get("limitation"), f"{field}.limitation", required=False) or None,
            )
        )
        claim_ids.append(claim_id)

    _unique_ids(claim_ids, "claims")

    checks: list[Check] = []
    check_ids: list[str] = []
    for index, item in enumerate(raw_checks):
        field = f"checks[{index}]"
        if not isinstance(item, Mapping):
            raise ValidationError(f"{field} must be an object")
        allowed = {"id", "result", "evidence_class", "source"}
        unknown = set(item) - allowed
        if unknown:
            raise ValidationError(f"{field} has unknown fields: {sorted(unknown)}")

        check_id = _text(item.get("id"), f"{field}.id")
        result = _text(item.get("result"), f"{field}.result")
        evidence_class = _text(item.get("evidence_class"), f"{field}.evidence_class")
        if result not in CHECK_RESULTS:
            raise ValidationError(f"{field}.result is not supported")
        if evidence_class not in EVIDENCE_CLASSES:
            raise ValidationError(f"{field}.evidence_class is not supported")
        checks.append(
            Check(
                id=check_id,
                result=result,
                evidence_class=evidence_class,
                source=_text(item.get("source"), f"{field}.source"),
            )
        )
        check_ids.append(check_id)

    _unique_ids(check_ids, "checks")
    return Manifest(scenario=scenario, claims=tuple(claims), checks=tuple(checks))


def load_manifest(path: str | Path) -> Manifest:
    """Load one bounded JSON manifest from the local filesystem."""

    manifest_path = Path(path)
    if manifest_path.suffix.lower() != ".json":
        raise ValidationError("manifest must be a .json file")
    try:
        size = manifest_path.stat().st_size
        if size > MAX_MANIFEST_BYTES:
            raise ValidationError(f"manifest exceeds {MAX_MANIFEST_BYTES} bytes")
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError("manifest file was not found") from exc
    except UnicodeDecodeError as exc:
        raise ValidationError("manifest must be UTF-8 JSON") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"manifest is invalid JSON: {exc.msg}") from exc
    return validate_manifest(raw)
