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
safe invocation via `run_check(check_id)` in `runner.py`.
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
- nullable repository identifier (`repository_id`), null when not supplied;
- claims;
- checks;
- summary counts;
- limitations;
- security notes.

`repository_id` is optional descriptive metadata. When supplied it must be a
non-empty string after trimming, contain no Unicode control characters, and
fit the existing 500-character text limit. It is not a repository URL, path,
source selector, or permission to inspect another checkout. It is included in
JSON, Markdown, and HTML output using format-safe escaping. With the field
omitted or null, the canonical report-ID input stays exactly as it was for
legacy manifests; a supplied normalized value is added to that input.
`generated_at` is excluded from report-ID calculation. The value cannot alter
claim status, provenance, evidence, check selection, or execution.

## Runtime interface

Proofline supports Python 3.11 or newer. The CLI exposes `report`, `run-check`,
`run-report`, and `web`, and continues to accept the legacy positional
manifest report form. `runner.run_check(check_id)` accepts only a static
registry ID; its repository root, argv, working directory, environment, and
timeout are resolved by code.

The `src/` package uses setuptools as its PEP 517 build backend and installs a
`proofline` console entry point. Application runtime dependencies remain empty.
The distribution includes only the named local browser page and synthetic
fixtures needed by the existing `web` command.

## Determinism

Given the same fixture and check outputs, the report must be byte-for-byte
stable apart from an explicitly injected generated-at value.

## Future runtime boundary

If a provider is added later, provider output must be labelled provider-backed
and must not silently upgrade local, simulated, or hosted claims.
