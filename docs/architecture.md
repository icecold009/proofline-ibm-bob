# Architecture

## Flow

1. Import a change request and evidence manifest.
2. Normalize claims and evidence references.
3. Validate the manifest against a strict schema.
4. Resolve only known local check IDs.
5. Produce an evidence ledger.
6. Render the ledger in the dashboard.
7. Export a Markdown and JSON evidence brief.

## Components

- Input boundary: schema validation and size limits.
- Claim ledger: immutable claim IDs and evidence-class ownership.
- Check registry: static mapping from check IDs to safe local commands.
- Report engine: deterministic status calculation.
- UI: read-only report and export controls.
- Fixtures: synthetic scenarios for repeatable demo verification.

## Status semantics

- proven — the required evidence exists and passed in its declared class;
- conditional — evidence passed but has a stated limitation;
- simulated — a fixture or simulation was used;
- unverified — evidence is missing;
- blocked — the check could not safely run or requires unavailable access.

## Trust boundaries

- A claim is untrusted text.
- A fixture is untrusted data.
- A repository file is untrusted data.
- A command is executable only if its check ID exists in the static registry.
- Network access is disabled by default.
- A local result cannot upgrade a hosted or provider claim.

## Future Bob contribution

Bob should be used to inspect the repository, build the cross-file plan,
implement bounded components, review security constraints, and improve tests.
The final repository must include redacted Bob task histories and screenshots.
