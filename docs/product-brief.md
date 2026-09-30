# Product brief

## Product

Proofline — release claims you can prove.

## User

A solo developer or small AI team preparing to release, demonstrate, or submit
an application.

## Problem

AI-assisted development makes implementation faster, but teams still confuse
local tests, simulated telemetry, hosted behavior, and provider-backed behavior.
That produces overconfident release notes and fragile demos.

## Promise

Proofline turns a change request into a small, traceable evidence report:
what passed, where it passed, what it does not prove, and the smallest next
check required.

## MVP acceptance boundary

- Enter one bounded change request or short diff summary.
- Load or edit one small evidence manifest through the local loopback UI, the
  hosted Vercel client, or the CLI.
- Classify claims into six evidence classes.
- Show explicit statuses: proven, conditional, simulated, unverified, or
  blocked.
- Treat manifest-declared results as conditional; mark a local result proven
  only when the explicit allowlisted runner observed it pass in the claim's
  declared evidence class.
- Run only allowlisted local checks through an explicit CLI action.
- Export JSON and Markdown.
- Work fully with synthetic fixtures and no live provider dependency.

The local loopback UI and hosted Vercel client accept bounded manifests and
render evidence details without executing checks or persisting submissions.
The hosted client sends requests to Vercel; platform request retention is
unverified, so use synthetic or public-safe data only. Neither browser surface
calls an external evidence provider.

## Explicit cuts

- No authentication.
- No multi-user workspace.
- No multi-repository analysis.
- No autonomous code changes.
- No arbitrary terminal execution.
- No claims of production readiness.
- No provider integration required for the first demo.
