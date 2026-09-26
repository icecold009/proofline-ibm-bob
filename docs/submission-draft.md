# Lablab submission draft

This is a copy-ready content draft, not a submitted entry. The signed-in event
form and event page were checked on 2026-09-26. Do not publish until the
remaining items below have real values and all repository evidence passes a
final redaction review.

## Project information

**Submission title (34/50 characters; required 5–50)**

Proofline: Evidence Before Release

**Short description (151/255 characters; required 50–255)**

Proofline turns software release claims into a traceable evidence report, keeping local checks, simulations, and missing hosted proof clearly distinct.

**Problem & Solution Statement (1,061 characters, 160 words; required 500–4,000 characters and no more than 500 words)**

Teams building with AI can move quickly and still make release claims that the available evidence does not support. A local test is not proof that a hosted integration works, and simulated telemetry is not a live provider result. Proofline makes those limits visible before a team publishes a release claim.

Proofline accepts one bounded evidence manifest, validates its structure, derives a status for each claim, and renders a self-contained report in JSON, Markdown, or HTML. Its statuses distinguish proven, conditional, simulated, unverified, and blocked evidence. An explicit local-check command uses a small code-owned registry; unknown check IDs are blocked, and report generation does not execute checks. The demo uses synthetic fixtures and has no provider or network dependency.

Proofline is a local prototype. A proven status is limited to its declared evidence class; it does not certify hosted behavior or production readiness. The current demo uses three synthetic scenarios to show local proof, simulated evidence, and missing hosted evidence.

**IBM Bob Usage Statement (1,215 characters, 170 words; required 500–4,000 characters and no more than 500 words)**

IBM Bob IDE was used as a repository-aware development partner in the Proofline workspace during the event build. The exported task history records Bob first reading the project instructions, product brief, architecture, and build checklist, then planning and implementing core repository work. Bob helped build a code-owned registry for approved local checks, a bounded runner that blocks unknown check IDs, deterministic evidence reports, and a self-contained HTML report with escaped output and safe copy/download controls. Bob also added regression tests, exercised the local verification workflow, and updated the implementation notes and checklist. The resulting application keeps command selection in reviewed code: report generation does not execute checks, and only an explicitly requested allowlisted local check can run. Claims about hosted or provider behavior remain unverified unless matching evidence is supplied. The project uses synthetic fixtures and makes no claim that watsonx.ai or watsonx Orchestrate was used. The repository includes the redacted Bob task-history Markdown and the task's consumption-summary screenshot in `bob_sessions`; the task summary records 36.50 Bobcoins for this task.

The draft is based on the exported task history and its summary screenshot. Confirm the statement still matches every Bob session included in the final public repository.

**Categories**

Pending: choose from the required Categories selector in the live submission form.

**Technology tags**

Draft: IBM Bob, Python, HTML. Confirm each exact available tag in the required Technologies Used selector.

## Media and links

- Cover image: **Prepared** — `docs/submission/proofline-cover.png` (16:9
  export of the inspected title slide; inspect it once more in the upload form).
- Video demonstration (MP4, no more than 3 minutes; at least 90 seconds must
  show the solution in action): **Pending** — record the demo in
  `docs/demo-narrative.md` and visibly demonstrate IBM Bob's role.
- Slide deck (PDF): **Prepared** — `docs/submission/proofline-pitch.pdf`. The
  editable PowerPoint source is `docs/submission/proofline-pitch.pptx`.
- Public GitHub repository: **Pending** — the repo is private until the
  reviewed release branch is pushed and public visibility is verified.
- Demo platform: **Pending** — deploy a working online prototype and confirm the
  hosting platform.
- Demo URL: **Pending** — verify it from a signed-out browser.
- IBM Bob task evidence: **Prepared locally** —
  `bob_sessions/proofline-session-2026-09-26.md` and
  `bob_sessions/proofline-session-2026-09-26-summary.png`; complete a final
  redaction review before public release.
- Additional information: use the long description above; adapt only to actual
  form requirements.

## Final checks before submission

- Dashboard check: **Approved** account; one-member team; solo participation is
  allowed. The submission draft is in progress and the opened form showed 0%.
- Confirm exact category and technology tag choices, plus later-step upload
  limits and accepted URL formats.
- Verify the public repository from a clean, signed-out browser and the demo URL
  from an external session.
- Verify that all relevant Bob task-history Markdown exports and summary
  screenshots are present in `bob_sessions`; remove credentials, tokens,
  personal data, and private paths before publication.
- Confirm that video, PDF deck, cover image, public repository, and live demo all
  open and correspond to the same final project version.
- License: **MIT** — `LICENSE` and the `pyproject.toml` SPDX declaration are
  present. Bob's role is credited in the submission statement and supported by
  the exported task evidence.
- Submit before September 27, 2026, 20:30 India Standard Time (15:00 UTC),
  as shown by the live event page.

## Sources

- [IBM Bob 2.0 hackathon live page](https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon/live)
- [IBM Bob 2.0 hackathon event page](https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon)
- [Lablab.ai submission requirements overview](https://lablab.ai/guide/ai-hackathons)
- [Lablab.ai submission tutorial](https://lablab.ai/ai-articles/hackathon-guidelines)
- [IBM Bob Hackathon Guide](https://watsonx-hackathons-2026.s3.us.cloud-object-storage.appdomain.cloud/Lablab-IBM-Bob-hackathon-guide-May-2026.pdf)
