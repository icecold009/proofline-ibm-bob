# Plan: Code-owned check registry (milestone 7)

## Overview

Add a static, code-owned registry to Proofline that maps each supported check ID
to a named, symbolic local operation plus the required metadata declared in the
spec. When `analyze_manifest` encounters a check whose ID is not in the registry,
it overrides that check's result to `"blocked"` regardless of the value supplied
in the manifest; every claim that references such a check therefore reports
`"blocked"` in the final report. The manifest itself is accepted — no
`ValidationError` is raised for an unregistered ID.

`ValidationError` continues to apply to malformed manifests, unsupported field
values, unknown fields, type violations, duplicate IDs, and size-limit breaches,
exactly as today.

The scope is one new module (`src/proofline/registry.py`), targeted edits to
`engine.py`, and a new injection-focused test file. No UI changes, no provider
integration, no new dependencies, no subprocess execution, no shell strings, no
network access.

---

## Confirmed design decisions

- **Blocking point:** engine time (soft). A well-formed manifest that contains a
  check entry whose ID is absent from the registry is accepted by
  `validate_manifest`. Inside `analyze_manifest`, before `_claim_result` is
  called, each check's result is overridden to `"blocked"` if its ID is not
  found in the registry. The existing `_claim_result` logic already propagates
  `"blocked"` to dependent claims without any further change.

- **`ValidationError` scope (unchanged):** malformed input — missing required
  fields, wrong types, unsupported `evidence_class`, unsupported `result` value,
  unknown root/claim/check fields, duplicate IDs, text length exceeding
  `MAX_TEXT`, and manifest size exceeding `MAX_MANIFEST_BYTES` — continues to
  raise `ValidationError` in `validate_manifest`. Registry membership is not a
  validation-time concern.

- **Operation representation:** each registry entry maps an ID to a symbolic
  `OperationKind` enum value that names the intended local operation as a
  fixed code constant. Operation identifiers are never built from input strings,
  never formatted into shell commands, and never passed to `subprocess` in this
  milestone. Actual execution wiring is a future milestone; see the spec conflict
  note below.

- **MVP allowlist:** two entries —
  - `"check-local-contracts"` → `OperationKind.RUN_LOCAL_CONTRACTS`
  - `"fixture-simulated-telemetry"` → `OperationKind.FIXTURE_EVIDENCE`
  All three existing golden fixtures use only these two IDs and will continue to
  pass without changes to any fixture file.

- **Existing test compatibility:** `test_unknown_evidence_reference_is_blocked`
  in `tests/test_engine.py` uses a manifest that references `"missing-check"`,
  which will not be in the registry. Under the engine-time blocking contract the
  manifest passes validation (it is well-formed). Inside the engine, the missing
  check ID is caught by the existing `_claim_result` logic (the check is not in
  `checks_by_id` at all because it appears only in `evidence_refs`, not in the
  checks list), so the test continues to pass unchanged. No edit is required.

---

## Stated spec conflict

**Unresolved in this milestone:** `docs/hackathon-build/spec.md` lines 24–32
states that each registry entry "declares: timeout; working directory; allowed
environment variables; output redaction policy; evidence class; failure status."
These fields only become meaningful when the registry is used to invoke an
operation. In this milestone no invocation occurs. The `CheckDefinition`
dataclass will carry all six metadata fields (plus `operation`) with concrete
values, but `timeout_s`, `working_dir`, and `allowed_env` will never be read by
any code path in this milestone. The spec's claim that the registry "maps a
stable check ID to a known local operation" is partially satisfied: the mapping
exists and the symbolic operation name is fixed in code, but the link from
`OperationKind` to an actual safe invocation is deferred to the execution
milestone. This gap is recorded here rather than being silently papered over.

---

## Sub-tasks

---

### Sub-task A — Define the registry module

**Intent**
Create `src/proofline/registry.py` as the single source of truth for all
permitted check IDs, their symbolic operations, and their metadata. This module
is code-owned. No part of it is constructed from user input or external data.

**Expected outcomes**
- An `OperationKind` enum (or equivalent) declares the finite set of symbolic
  operations Proofline supports. Each member's value is a short, stable string
  constant. No member value is a shell string, a file path, or a callable.
  Currently two members: `RUN_LOCAL_CONTRACTS` and `FIXTURE_EVIDENCE`.
- A `CheckDefinition` frozen dataclass holds all fields required by the spec:
  `operation: OperationKind`, `evidence_class: str`, `failure_status: str`,
  `timeout_s: int`, `working_dir: str`, `allowed_env: tuple[str, ...]`,
  `redact_output: bool`.
- A `REGISTRY: dict[str, CheckDefinition]` constant is defined at module level
  with exactly two entries. Its keys are the two supported check IDs. The dict
  is not mutated after definition.
- A `lookup(check_id: str) -> CheckDefinition | None` function returns
  `REGISTRY.get(check_id)`. It does not format `check_id` into any string, does
  not call `subprocess`, does not access the filesystem, and does not raise.
- The module's only stdlib import is `enum` (and `dataclasses` for the frozen
  dataclass). No third-party dependencies.

**Registry entry shape (MVP)**

| Field | `"check-local-contracts"` | `"fixture-simulated-telemetry"` |
|---|---|---|
| `operation` | `OperationKind.RUN_LOCAL_CONTRACTS` | `OperationKind.FIXTURE_EVIDENCE` |
| `evidence_class` | `"local"` | `"local"` |
| `failure_status` | `"blocked"` | `"blocked"` |
| `timeout_s` | `30` | `0` |
| `working_dir` | `"."` | `"."` |
| `allowed_env` | `()` | `()` |
| `redact_output` | `False` | `False` |

`timeout_s = 0` for `FIXTURE_EVIDENCE` signals that no real timeout applies
because this operation kind is never executed; it is a fixture-evidence marker.

**Steps**
1. Create `src/proofline/registry.py`.
2. Define `OperationKind` as a `str`-based enum with two members.
3. Define `CheckDefinition` as a `@dataclass(frozen=True)`.
4. Define `REGISTRY` as a module-level `dict[str, CheckDefinition]` literal.
5. Define `lookup`.

**Relevant context**
- Spec: `docs/hackathon-build/spec.md` lines 22–32.
- Pattern: `EVIDENCE_CLASSES` frozenset in `src/proofline/model.py` line 14 is
  the closest existing code-owned constant.
- `AGENTS.md` command safety rules: no shell interpolation, no network access.

**Status:** [x] done

---

### Sub-task B — Override unregistered check results in the engine

**Intent**
Make `analyze_manifest` enforce the registry boundary: any check whose ID is
not in the registry has its result silently overridden to `"blocked"` before
`_claim_result` is called. Claims that reference such a check therefore inherit
`"blocked"` through the existing result-propagation logic in `_claim_result`
without any change to that function.

**Expected outcomes**
- `analyze_manifest` in `src/proofline/engine.py` imports `lookup` from
  `.registry`.
- A loop over `manifest.checks` replaces each `Check` whose ID returns `None`
  from `lookup` with an equivalent `Check` where `result = "blocked"`. The
  replacement uses the `Check` dataclass from `model.py`; it does not construct
  a dict or a string command.
- `_claim_result` is not modified.
- All three existing golden fixtures (`local-pass`, `simulated-only`,
  `hosted-unverified`) produce the same reports as before because their check
  IDs are registered.
- A manifest containing an unregistered but well-formed check ID produces a
  report where every claim referencing that check has `status = "blocked"`.
- A manifest whose checks list is empty (like `hosted-unverified.json`)
  is unaffected.
- The `security_notes` list in `analyze_manifest` is updated to replace
  `"No commands were executed."` with a note that names the registry as the
  boundary: `"Check IDs are checked against the static code-owned registry;
  no commands were executed."`.

**Steps**
1. In `src/proofline/engine.py`, add `from .registry import lookup`.
2. After the line `checks_by_id = {check.id: check for check in manifest.checks}`,
   add a comprehension that rebuilds `manifest.checks` — or an equivalent local
   variable — replacing any check whose `lookup(check.id)` returns `None` with
   `Check(id=check.id, result="blocked", evidence_class=check.evidence_class,
   source=check.source)`.
3. Rebuild `checks_by_id` from the (possibly modified) checks list.
4. Update `security_notes`.

**Relevant context**
- `src/proofline/engine.py` — `analyze_manifest` lines 79–111, `_claim_result`
  lines 22–76.
- `src/proofline/model.py` — `Check` dataclass lines 26–31.
- `docs/architecture.md` line 35: "A command is executable only if its check ID
  exists in the static registry."
- Existing golden-fixture tests in `tests/test_engine.py` must all remain green.

**Status:** [x] done

---

### Sub-task C — Add injection-shaped negative tests

**Intent**
Prove through automated tests that:
(a) adversarially shaped check IDs (shell metacharacters, env-var references,
    path traversal, empty string) do not execute commands and produce
    `"blocked"` in the report for the referencing claim;
(b) the `lookup` function behaves correctly for known and unknown IDs;
(c) the existing `test_unknown_evidence_reference_is_blocked` test in
    `tests/test_engine.py` remains unaffected (no edit needed there).

**Expected outcomes**
- New file `tests/test_registry.py`.
- Each injection test constructs an in-memory raw manifest dict, calls
  `validate_manifest` (which must succeed — the manifest is well-formed), calls
  `analyze_manifest`, and asserts `status == "blocked"` on the referencing claim.
- No `subprocess`, no disk writes, no network calls, no `eval` in any test.
- Two positive `lookup` unit tests: known ID returns a `CheckDefinition`;
  unknown ID returns `None`.

**Injection vectors to cover (minimum)**

| Test name | Attack vector | Expected outcome |
|---|---|---|
| `test_unregistered_id_forces_blocked_claim` | Well-formed but unregistered ID `"unregistered-check"` | `status == "blocked"` |
| `test_semicolon_in_id_forces_blocked_claim` | `"check-local-contracts; rm -rf /"` | `status == "blocked"` |
| `test_pipe_in_id_forces_blocked_claim` | `"check-local-contracts \| cat /etc/passwd"` | `status == "blocked"` |
| `test_subshell_in_id_forces_blocked_claim` | `"$(whoami)"` | `status == "blocked"` |
| `test_env_var_in_id_forces_blocked_claim` | `"$HOME"` | `status == "blocked"` |
| `test_path_traversal_in_id_forces_blocked_claim` | `"../../etc/passwd"` | `status == "blocked"` |
| `test_empty_id_forces_blocked_claim` | `""` | `ValidationError` (empty string fails `_text` in model.py — the manifest is malformed, not a registry question) |

**Note on the empty-ID case:** `""` is rejected by `validate_manifest` via the
existing `_text` helper, which raises `ValidationError` for empty strings. This
is a malformed-manifest case, not a registry case. The test asserts
`ValidationError`, not a blocked claim. This is the correct distinction.

**Steps**
1. Create `tests/test_registry.py`.
2. Write `_raw_manifest_with_check_id(check_id)` — a helper that returns a raw
   dict with one claim referencing `check_id` and one check entry with that
   `id`, `result = "pass"`, `evidence_class = "local"`, `source = "test"`.
3. For each injection test row where the outcome is `status == "blocked"`:
   call `validate_manifest(raw)` (expect no exception), then call
   `analyze_manifest(manifest)`, and assert
   `report["claims"][0]["status"] == "blocked"`.
4. For the empty-ID test: wrap `validate_manifest(raw)` in
   `self.assertRaises(ValidationError)`.
5. Add `test_lookup_known_id_returns_definition`: assert
   `lookup("check-local-contracts")` is not None and is a `CheckDefinition`.
6. Add `test_lookup_unknown_id_returns_none`: assert
   `lookup("no-such-check")` is None.

**Relevant context**
- Existing injection precedent: `test_declared_status_is_not_trusted` in
  `tests/test_engine.py` lines 49–65 (validates that a manifest with a
  user-supplied `status` field is accepted by `validate_manifest` but the field
  is ignored by the engine).
- `validate_manifest` and `analyze_manifest` are importable from `proofline`.
- `lookup` and `CheckDefinition` will be importable from `proofline` after
  Sub-task A adds them to `__init__.py`.

**Status:** [x] done

---

### Sub-task D — Export registry symbols and update security note

**Intent**
Make `CheckDefinition`, `OperationKind`, `REGISTRY`, and `lookup` part of the
public API via `src/proofline/__init__.py`. Confirm the security note update
from Sub-task B is in place. Do not mark the checklist milestone complete here —
that follows only after implementation and verification are confirmed.

**Expected outcomes**
- `src/proofline/__init__.py` imports and re-exports `CheckDefinition`,
  `OperationKind`, `REGISTRY`, and `lookup` from `.registry`.
- `__all__` in `__init__.py` is extended accordingly.
- `analyze_manifest` in `engine.py` carries the updated security note.

**Steps**
1. In `src/proofline/__init__.py`, add
   `from .registry import CheckDefinition, OperationKind, REGISTRY, lookup`.
2. Add the four names to `__all__`.
3. Confirm the security note change from Sub-task B step 4 is present.

**Relevant context**
- `src/proofline/__init__.py` current contents: lines 1–19 (updated).
- Checklist: `docs/hackathon-build/checklist.md` item 7 is marked `[x]` based
  on Bob-reported verification of 16 passing tests. Operation invocation remains
  deferred to item 7A.

**Status:** [x] done

---

## Files changed (milestones 7 and 7A)

| File | Change type | Reason |
|---|---|---|
| `src/proofline/registry.py` | New + Edit | Code-owned registry (milestone 7); frozen with `MappingProxyType`, `allowed_env` updated (milestone 7A) |
| `src/proofline/engine.py` | Edit | Override unregistered check results to `"blocked"` before `_claim_result`; update security note |
| `src/proofline/__init__.py` | Edit | Export `CheckDefinition`, `OperationKind`, `REGISTRY`, `lookup`, `CheckRunResult`, `run_check` |
| `src/proofline/runner.py` | **New** | Bounded check execution — `run_check`, `CheckRunResult`, dispatch table, `FIXTURE_EVIDENCE` exception |
| `src/proofline/__main__.py` | Edit | Add `run-check` subcommand; preserve legacy manifest-report usage |
| `tests/test_registry.py` | **New** | Injection-shaped blocked-claim tests + `lookup` unit tests (milestone 7) |
| `tests/test_runner.py` | **New** | Runner unit tests, immutability regression, CLI tests (milestone 7A) |

`src/proofline/model.py` and fixture files were not changed.
`docs/hackathon-build/checklist.md` updated: item 7 `[x]`, item 7A `[x]`.

---

## Acceptance criteria (milestone 7)

1. **Unknown IDs produce blocked claims.** A well-formed manifest containing a
   check entry whose ID is absent from `REGISTRY` is accepted by
   `validate_manifest` and produces a report where every claim referencing that
   check ID has `status = "blocked"`.

2. **Injection-shaped IDs also produce blocked claims.** Check IDs containing
   shell metacharacters, env-var syntax, or path traversal sequences are
   well-formed strings that pass `validate_manifest` but are not in `REGISTRY`;
   the engine overrides their result to `"blocked"` and no command is executed.

3. **Malformed manifests continue to raise `ValidationError`.** Empty check ID,
   unsupported `evidence_class`, unknown fields, duplicate IDs, and size-limit
   violations all raise `ValidationError` in `validate_manifest`, as today.

4. **All three golden fixtures remain green.** `check-local-contracts` and
   `fixture-simulated-telemetry` are in `REGISTRY`; their registered results
   drive the report status unchanged.

5. **No command is constructed or executed.** There is no path from any manifest
   field to `subprocess`, `os.system`, `eval`, or `exec` in this milestone.
   `OperationKind` values are symbolic string constants fixed in code.

---

## Spec conflict resolution (milestone 7A)

The conflict recorded during milestone 7 — that `spec.md` required invocable
operations but no invocation occurred — is resolved by milestone 7A.

`runner.py` wires each `OperationKind` to a bounded handler. All six metadata
fields in `CheckDefinition` are now used at runtime: `timeout_s` is passed to
`subprocess.run`, `working_dir` resolves the `cwd`, `allowed_env` constructs
the explicit environment dict, `failure_status` is returned on any failure,
`evidence_class` is returned in `CheckRunResult`, and `redact_output` is present
for future use (output is currently always discarded).

**Remaining documented exception:** `OperationKind.FIXTURE_EVIDENCE` has
`timeout_s=0`. The `_fixture_evidence` handler explicitly does not call
`subprocess.run` and does not read `timeout_s`. This is an intentional,
documented exception — not a gap. The `timeout_s=0` sentinel means
"not applicable for a fixture marker".

---

## Verification (milestones 7 and 7A)

```powershell
python scripts/verify.py        # dependency-free suite
$env:PYTHONPATH = "src"
python -m pytest tests/ -v      # full suite with pytest
```

**Milestone 7 result (Bob-reported):** 16 passed — 7 existing + 9 new. The
pytest command ran; the application invoked no check operations or subprocesses.

**Milestone 7A result (Bob-reported):** 43 passed in 0.22s — 16 existing +
27 new tests in `tests/test_runner.py`. `python scripts/verify.py` exit 0.
CLI smoke tests: `run-check check-local-contracts` → `pass` (exit 0);
`run-check fixture-simulated-telemetry` → `fixture` (exit 1, no subprocess);
`run-check no-such-check` → blocked (exit 1, no subprocess launched).
`git diff --check` exit 0.
