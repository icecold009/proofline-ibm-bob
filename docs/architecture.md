# Architecture

## Flow

1. Enter a bounded change request and load or edit one evidence manifest in the
   local loopback UI or the hosted static client.
2. Normalize claims and evidence references.
3. Validate the manifest against a strict schema.
4. Resolve only known local check IDs.
5. Keep manifest-declared results distinct from runner-observed results.
6. Produce an evidence ledger with source, provenance, and observation time.
7. Render the ledger in the local browser UI, hosted client, and report.
8. Export a Markdown and JSON evidence brief.

## Components

- Input boundary: schema validation and size limits.
- Claim ledger: immutable claim IDs and evidence-class ownership.
- Check registry: static mapping from check IDs to safe local commands.
- Report engine: deterministic status calculation.
- Local UI: loopback-only manifest intake, read-only report details, status
  guide, and export controls. It never runs a check.
- Hosted adapter: static client in `public/` uses the Vercel API functions in
  `api/` for bounded analysis and report rendering. The API does not run checks
  or persist application data; it has no application-layer authentication or
  per-caller rate limit. Effective platform protection and request retention
  remain unverified. Hosted requests reach Vercel, so use synthetic or
  public-safe data only.
- Fixtures: synthetic scenarios for repeatable demo verification.

## Interface and report identity

The supported Python minimum is 3.11. The CLI provides `report`, `run-check`,
`run-report`, and `web`; the legacy positional-manifest report form remains
supported. The only runner entry point is `run_check(check_id)`, and all
execution parameters and repository-root resolution remain code-owned.
The src-layout package is built with setuptools through PEP 517 and exposes a
`proofline` console script. Runtime dependencies remain empty. The installed
distribution includes the local page and three synthetic fixtures; the web
command resolves only these code-owned assets from the checkout or install
data directory.

The manifest may include a nullable top-level `repository_id`. A supplied
value is trimmed, non-empty text of at most 500 characters with no control
characters. It is descriptive metadata and cannot select a checkout, path,
check, evidence source, or status. Reports emit null when the field is absent.
The canonical report-ID seed remains byte-for-byte equivalent for old
manifests without the field; when supplied, the normalized value participates
in the seed. `generated_at` remains outside that seed.

## Status semantics

- proven — a referenced allowlisted check ran and passed in its declared class;
- conditional — a manifest-declared pass was not runner-verified, or evidence
  came from a different class;
- simulated — a fixture or simulation was used;
- unverified — evidence is missing;
- blocked — the check could not safely run or requires unavailable access.

A passing result supplied in a manifest is a declaration, not a runner
observation, and therefore remains conditional. `run-report` is the explicit
CLI workflow that executes only referenced allowlisted checks.

## Trust boundaries

- A claim is untrusted text.
- A fixture is untrusted data.
- A repository file is untrusted data.
- A command is executable only if its check ID exists in the static registry.
- Local application paths make no outbound network calls. The hosted adapter
  receives same-origin browser requests and does not call external providers.
- A local result cannot upgrade a hosted or provider claim.

## Future Bob contribution

Bob should be used to inspect the repository, build the cross-file plan,
implement bounded components, review security constraints, and improve tests.
The final repository must include redacted Bob task histories and screenshots.
