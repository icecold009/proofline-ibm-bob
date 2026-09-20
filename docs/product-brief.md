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

- Input one change request or Git diff.
- Load one small evidence manifest.
- Classify claims into six evidence classes.
- Show explicit statuses: proven, conditional, simulated, unverified, or
  blocked.
- Run only allowlisted local checks.
- Export JSON and Markdown.
- Work fully with synthetic fixtures and no live provider dependency.

## Explicit cuts

- No authentication.
- No multi-user workspace.
- No multi-repository analysis.
- No autonomous code changes.
- No arbitrary terminal execution.
- No claims of production readiness.
- No provider integration required for the first demo.
