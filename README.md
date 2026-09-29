# Proofline

Proofline is a local, evidence-backed release-readiness tool for AI builders.
It helps a team distinguish what a change actually proved from what is only
simulated, local, or still unverified.

## What it does

- Validates one bounded evidence manifest.
- Derives claim status from evidence: proven, conditional, simulated,
  unverified, or blocked.
- Runs only checks in a static, code-owned allowlist through the explicit
  `run-check` or `run-report` command.
- Produces JSON, Markdown, or self-contained offline HTML reports.
- Includes a local loopback browser interface and a separate Vercel static/API
  adapter for hosted analysis. Both browser paths validate bounded manifests
  and render reports without executing checks or persisting application data.
- Uses synthetic fixtures and has no provider integration. The hosted adapter
  sends browser requests to Vercel; use synthetic or public-safe data only.

## Requirements

- Python 3.11 or newer. The project uses only the Python standard library for
  application code and its built-in verifier.
- Run commands from the repository root.

## Install the CLI

From a source checkout, install Proofline into the active Python environment:

```powershell
python -m pip install .
```

The `proofline` command and `python -m proofline` expose the same CLI. The
package has no runtime dependencies; its setuptools build backend is used only
to build the distribution. Installation includes the local browser page and
synthetic fixtures so the `web` command remains available outside a checkout.

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

## Manifest and report contract

The bounded manifest has `scenario`, `claims`, and `checks`, with optional
`change_request` and optional nullable `repository_id`. A supplied repository
identifier is trimmed text of at most 500 characters and may not contain
control characters. It is descriptive metadata only: it does not select a
checkout, path, check, or evidence source. JSON reports contain
`"repository_id": null` when it was not supplied; Markdown and HTML display
“Not supplied.”

Report IDs are deterministic. Omitting or setting `repository_id` to null
preserves the existing report-ID seed for legacy manifests. A supplied,
normalized identifier becomes part of the seed and produces a distinct report
identity. `generated_at` is not part of the seed.

The CLI surface is `python -m proofline report <manifest>`,
`python -m proofline run-check <check-id>`,
`python -m proofline run-report <manifest>`, and `python -m proofline web`.
The legacy `python -m proofline <manifest>` report form remains supported.
`run_check(check_id)` accepts only a registered check ID; repository root,
command arguments, working directory, environment, and timeout are
code-owned.

## Generate a report

PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m proofline fixtures/local-pass.json --format html --output proofline-report.html
```

This command analyzes only the supplied manifest. A declared passing result is
shown as **conditional** until Proofline observes the allowlisted check run.
Change the fixture to `simulated-only.json` or `hosted-unverified.json` to see
how Proofline preserves those evidence limits. Supported report formats are
`json` (default), `markdown`, and `html`.

To explicitly run only the registered checks referenced by a manifest, then
write a report containing those observed results:

```powershell
$env:PYTHONPATH = "src"
python -m proofline run-report fixtures/local-pass.json --format html --output proofline-verified.html
```

The separate command runs only code-owned allowlisted checks. It does not
interpret command text from the manifest.

## Open the browser interface

```powershell
$env:PYTHONPATH = "src"
python -m proofline web
```

Open `http://127.0.0.1:8765`. The local preview binds to loopback, processes
manifests in memory, and does not run checks or persist submissions. The
repository also includes a Vercel static/API adapter under `public/` and `api/`.
An earlier public Vercel demo check used synthetic input. That historical
check does not verify the current deployment or establish provider behavior
or production readiness.
Hosted requests leave the browser and reach Vercel. The application does not
persist manifests, but platform request retention has not been verified; use
synthetic or public-safe data only.

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
- `docs/submission-draft.md` — submitted copy and current public-entry record.
- `docs/submission/` — editable pitch deck, PDF export, cover, and event video.
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
calculation, offline HTML report, loopback browser intake, and Vercel adapter
code are implemented. The hosted API has no application-layer authentication
or per-caller rate limit; effective platform protection and request retention
are unverified, so use synthetic or public-safe data only. A public Vercel demo
was checked with synthetic input in an earlier review; that is historical
evidence and does not establish the current deployment state.
Manifest-declared results remain conditional; `run-report` is the explicit path
that can produce runner-observed local evidence. Reports expose evidence source,
provenance, and observation time. A seven-slide editable pitch deck and PDF
export are in `docs/submission/`. The Bob task-history Markdown and its
consumption-summary screenshot are in `bob_sessions/`. The GitHub repository is
public, with `main` as the default branch. The event-specific video and revised
PDF deck are included in `docs/submission/`; the public Lablab entry is live and
its judging status was shown as in progress when checked. The project uses the
MIT License.

Use a feature branch for changes. Never commit credentials, private data, or
Bob exports that have not been redacted.
