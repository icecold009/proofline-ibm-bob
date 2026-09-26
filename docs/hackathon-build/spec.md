# Technical specification

## Claim record

- id: stable string;
- title: short human-readable claim;
- evidence_class: local, browser, hosted, provider, data, or security;
- required_check_ids: list of known check IDs;
- status: derived status;
- limitation: explicit explanation;
- evidence_refs: references to check results or supplied artifacts.
- change_request: optional bounded text describing the proposed change.

## Evidence item

- id: stable string;
- type: test, screenshot, URL, report, fixture, or manifest;
- source: human-readable origin;
- observed_at: timestamp or fixture label;
- redacted: boolean;
- notes: limitation text.

## Check provenance

Manifest input may declare a result, evidence class, and source. The parser never
accepts caller-supplied provenance or observation timestamps. Such results are
reported as `manifest-declared`; a passing declaration is conditional. Only
the explicit `run-report` CLI path can attach `runner-observed` provenance and
an observation timestamp. Fixture markers remain simulated. The loopback web UI
never executes checks and never persists uploaded manifests.

## Check registry

The registry maps a stable check ID to a known local operation. The registry is
code-owned and never constructed from user input. Each check declares:

- timeout;
- working directory;
- allowed environment variables;
- output redaction policy;
- evidence class;
- failure status.

### Registry milestones

**Declaration milestone (complete):** defines the static, code-owned registry
with `CheckDefinition` metadata and `OperationKind` symbolic constants. Unknown
check IDs are blocked at engine time — any check whose ID is absent from the
registry has its result overridden to `"blocked"` before claims are evaluated.
No operations are invoked, no commands are executed, and no shell strings are
constructed.

**Execution milestone (complete):** wires each `OperationKind` to a bounded
safe invocation via `run_check(check_id, repo_root=...)` in `runner.py`.
`RUN_LOCAL_CONTRACTS` uses a fixed argv (`[sys.executable, scripts/verify.py]`),
`shell=False`, `capture_output=True`, registry timeout, registry working
directory, and only explicitly allowed environment variables (no full env
inheritance). `FIXTURE_EVIDENCE` returns `"fixture"` deterministically without
starting any process. Unknown IDs are blocked before any dispatch. Output is
discarded and never surfaced in reports. See checklist item 7A.

## Report contract

Every report contains:

- report ID;
- generated-at value;
- repository identifier;
- claims;
- checks;
- summary counts;
- limitations;
- security notes.

## Determinism

Given the same fixture and check outputs, the report must be byte-for-byte
stable apart from an explicitly injected generated-at value.

## Future runtime boundary

If a provider is added later, provider output must be labelled provider-backed
and must not silently upgrade local, simulated, or hosted claims.
