# Security policy

## Scope

Proofline will inspect repository metadata, evidence manifests, test output,
and user-entered claims. It must treat all of those inputs as untrusted.

## Non-negotiable controls

- No secrets in source, fixtures, logs, screenshots, or Bob exports.
- No personal, client, confidential, or social-media data in demo inputs.
- No arbitrary command execution.
- No network calls unless a future check explicitly declares its purpose,
  destination, timeout, and evidence class.
- No HTML rendering from untrusted input without sanitization.
- No detailed stack traces or sensitive paths in user-facing reports.
- Unknown and failed checks must not be silently converted to success.

## Evidence semantics

Evidence is scoped to the environment that produced it:

- local — files, parsers, and local tests;
- browser — an observed browser flow;
- hosted — a deployed URL or remote check;
- provider — a real provider response;
- data — data provenance and permission;
- security — secret and policy checks.

One class must never be presented as another class.

## Reporting a vulnerability

Do not publish secrets or exploit details in a public issue. Contact the
maintainer privately with the affected path, impact, reproduction, and a safe
remediation suggestion.
