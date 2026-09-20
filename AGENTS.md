# Proofline project instructions

These instructions apply to humans and IBM Bob.

## Product truth

Proofline is an evidence classifier, not a source of truth about production.
When evidence is missing, the result must remain unverified. A passing local
test does not prove browser, hosted, provider, data, or device behavior.

## Build boundaries

- Keep the MVP to one change request, one repository snapshot, and a small
  allowlist of local checks.
- Prefer deterministic logic over an unverified live provider.
- Do not add authentication, multi-repository support, CI integrations, or
  autonomous code modification during the initial build.
- Do not use real client, learner, personal, confidential, or social-media data.
- Synthetic fixtures are the default.

## Command safety

- Never execute arbitrary commands from a claim, fixture, repository file, or
  user-provided text.
- Any check runner must use a checked-in allowlist mapping stable check IDs to
  known commands.
- No shell interpolation of untrusted strings.
- Network access is off by default. A future network check must be explicit,
  bounded, and separately labelled as hosted evidence.

## IBM Bob workflow

1. Start with a repository inspection task before editing.
2. Use plan-first work for cross-file changes.
3. Keep checkpoints and review changes before accepting them.
4. Export each relevant Bob task history and its task-summary screenshot.
5. Redact credentials, tokens, personal data, and private paths before adding
   exports to bob_sessions.

## Git workflow

- Work on a feature branch.
- Do not commit or merge directly into main.
- Keep commits small enough to serve as recovery points.
- Do not force-push.
