# Proofline

Proofline is an evidence-backed release-readiness tool for AI builders.

Its job is deliberately narrow: help a builder distinguish what a change has
actually proved from what is only simulated, local, or still unverified.

## Hackathon direction

Proofline is being prepared for the IBM Bob 2.0 Hackathon. The repository is
structured so IBM Bob can become a visible, repository-aware part of the build
once the hackathon-provisioned Bob access is available.

The pre-Bob foundation contains planning documents, synthetic fixtures,
acceptance criteria, security boundaries, and Bob project instructions. It does
not claim that the hackathon's core implementation was completed before the
event window.

## MVP

- Analyze one change request or Git diff at a time.
- Track claims across local, browser, hosted, provider, data, and security
  evidence.
- Use deterministic statuses: proven, conditional, simulated, unverified, or
  blocked.
- Run only explicitly allowlisted local checks.
- Export a Markdown and JSON evidence brief.

## Repository map

- AGENTS.md — project rules for humans and IBM Bob.
- docs/hackathon-rules.md — confirmed guidance and items still requiring kickoff
  confirmation.
- docs/product-brief.md — product scope and cuts.
- docs/architecture.md — data flow and security boundaries.
- docs/demo-narrative.md — submission and demo story.
- docs/hackathon-build/ — scope, PRD, spec, checklist, and decision journal.
- fixtures/ — synthetic, non-sensitive demo inputs.
- src/ — implementation boundary; intentionally empty before Bob access.
- tests/ — verification boundary.
- bob_sessions/ — exported Bob task histories and redacted screenshots.

## Current status

This is a foundation branch. IBM Bob-specific task evidence must be added under
bob_sessions during the official build.

## Safety rules

- Never commit credentials, personal information, client data, or confidential
  material.
- Never describe simulation as hosted or provider-backed proof.
- Never run arbitrary commands supplied by a repository or user input.
- Never commit directly to main; use a feature branch.
