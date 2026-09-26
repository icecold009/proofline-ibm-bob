# Proofline

Proofline is a local, evidence-backed release-readiness tool for AI builders.
It helps a team distinguish what a change actually proved from what is only
simulated, local, or still unverified.

## What it does

- Validates one bounded evidence manifest.
- Derives claim status from evidence: proven, conditional, simulated,
  unverified, or blocked.
- Runs only checks in a static, code-owned allowlist through the explicit
  `run-check` command.
- Produces JSON, Markdown, or self-contained offline HTML reports.
- Uses synthetic fixtures; it does not connect to a provider or deployment.

## Requirements

- Python 3.10 or newer. The project uses only the Python standard library for
  application code and its built-in verifier.
- Run commands from the repository root.

## Verify the project

PowerShell:

```powershell
python scripts/verify.py
```

Or run the test suite directly:

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/ -v
```

The direct pytest command requires `pytest` to be installed; the standard
verification command above does not.

## Generate a report

PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m proofline fixtures/local-pass.json --format html --output proofline-report.html
```

Change the fixture to `simulated-only.json` or `hosted-unverified.json` to see
how Proofline preserves those evidence limits. Supported report formats are
`json` (default), `markdown`, and `html`.

## Run an allowlisted local check

```powershell
$env:PYTHONPATH = "src"
python -m proofline run-check check-local-contracts
```

This explicitly invokes the registered local contract check. Unknown check IDs
are blocked without starting a process. `analyze_manifest` does not execute
checks; report generation only evaluates the supplied manifest.

## Repository map

- `AGENTS.md`, `SECURITY.md` — project workflow and security boundaries.
- `docs/hackathon-rules.md` — published event facts and submission requirements.
- `docs/product-brief.md`, `docs/architecture.md` — product contract and design.
- `docs/hackathon-build/` — spec, checklist, and implementation decisions.
- `docs/submission-draft.md` — copy-ready submission draft and outstanding items.
- `docs/submission/` — editable pitch deck, PDF export, and cover image.
- `fixtures/` — synthetic, non-sensitive examples.
- `src/` and `tests/` — CLI, deterministic engine, registry, runner, renderers,
  and tests.
- `bob_sessions/` — redacted Bob task histories and summary screenshots for
  the public submission; add genuine exports before publishing.

## Evidence limits

A passing local check proves only the local check result. It does not establish
browser, hosted, provider, data, or production behavior. Proofline does not
claim production readiness, and no live provider integration is required for
the current MVP.

## Current build status

The declaration registry, bounded local check runner, deterministic report
calculation, and offline HTML report are implemented. The report was reviewed
in a browser during this project. A seven-slide editable pitch deck and PDF
export are in `docs/submission/`. The Bob task-history Markdown and its
consumption-summary screenshot are in `bob_sessions/`. The repository is
currently private; public repository release, an online demo, and the
event-specific video remain pending. The project uses the MIT License.

Use a feature branch for changes. Never commit credentials, private data, or
Bob exports that have not been redacted.
