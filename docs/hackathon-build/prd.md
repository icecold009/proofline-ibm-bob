# Product requirements

## P0 requirements

### Claim intake

- Accept one bounded change request.
- Reject oversized or malformed manifests.
- Assign stable IDs to claims.

### Evidence classification

- Support local, browser, hosted, provider, data, and security evidence.
- Default missing evidence to unverified.
- Preserve the original evidence class in every report.

### Safe verification

- Expose only named check IDs.
- Never execute a command string from the input manifest.
- Show blocked when a required check is unavailable.

### Report

- Display summary counts by status.
- Display each claim, its evidence, its limitation, and next action.
- Export deterministic JSON and Markdown.

### Demo reliability

- Run without IBM credentials.
- Use synthetic fixtures.
- Include a failure scenario, not only a happy path.

## P1 requirements

- Friendly empty state.
- Copyable Markdown output.
- Keyboard-accessible status controls.
- Human-readable limitation language.

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
