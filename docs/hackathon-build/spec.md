# Technical specification

## Claim record

- id: stable string;
- title: short human-readable claim;
- evidence_class: local, browser, hosted, provider, data, or security;
- required_check_ids: list of known check IDs;
- status: derived status;
- limitation: explicit explanation;
- evidence_refs: references to check results or supplied artifacts.

## Evidence item

- id: stable string;
- type: test, screenshot, URL, report, fixture, or manifest;
- source: human-readable origin;
- observed_at: timestamp or fixture label;
- redacted: boolean;
- notes: limitation text.

## Check registry

The registry maps a stable check ID to a known local operation. The registry is
code-owned and never constructed from user input. Each check declares:

- timeout;
- working directory;
- allowed environment variables;
- output redaction policy;
- evidence class;
- failure status.

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
