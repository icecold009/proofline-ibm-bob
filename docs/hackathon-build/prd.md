# Product requirements

## P0 requirements

### Claim intake

- Accept one bounded change request.
- Let a user choose a synthetic scenario or enter one claim in a guided form in
  the local loopback browser interface or hosted Vercel client; retain advanced
  JSON edit/upload for multiple claims.
- Reject oversized or malformed manifests.
- Assign a stable, editable ID to the guided claim; validate IDs in advanced
  manifests.

### Evidence classification

- Support local, browser, hosted, provider, data, and security evidence.
- Default missing evidence to unverified.
- Preserve the original evidence class in every report.
- Show check result, source, provenance, and observation time beside each
  referenced claim.
- Keep a manifest-declared result conditional until an explicit allowlisted
  runner observes it pass.

### Safe verification

- Expose only named check IDs.
- Never execute a command string from the input manifest.
- Show blocked when a required check is unavailable.

### Report

- Display summary counts by status.
- State the plain-language report outcome and explain status meanings.
- Display each claim, its evidence, its limitation, and next action.
- Export deterministic JSON and Markdown.
- Record report generation time.

### Demo reliability

- Run without IBM credentials.
- Use synthetic fixtures.
- Include a failure scenario, not only a happy path.

## P1 requirements

- Friendly empty state.
- Copyable Markdown output.
- Keyboard-accessible status controls.
- Human-readable limitation language.
- Collapse generic method notes so claim evidence stays primary.

## Non-goals

- Production monitoring.
- Security certification.
- Automated deployment approval.
- Provider truth discovery without provider access.

## Submission proof points

- Public repository with setup instructions.
- Public online prototype.
- Short demo video.
- Pitch deck.
- bob_sessions folder with redacted task evidence.
