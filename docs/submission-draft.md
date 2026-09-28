# Lablab submission record

This records the copy and artifacts in the submitted Lablab entry. The signed-in
event form and event page were checked on 2026-09-27 (India Standard Time). The
public entry page later confirmed the submission and showed judging in progress.

## Project information

**Submission title (34/50 characters; required 5–50)**

Proofline: Evidence Before Release

**Short description (151/255 characters; required 50–255)**

Proofline turns software release claims into a traceable evidence report, keeping local checks, simulations, and missing hosted proof clearly distinct.

**Problem & Solution Statement (1,162 characters, 176 words; required 500–4,000 characters and no more than 500 words)**

Teams building with AI can move quickly and still make release claims that the available evidence does not support. A local test is not proof that a hosted integration works, and simulated telemetry is not a live provider result. Proofline makes those limits visible before a team publishes a release claim.

Proofline accepts one bounded evidence manifest, validates its structure, derives a status for each claim, and renders a self-contained report in JSON, Markdown, or HTML. Its statuses distinguish proven, conditional, simulated, unverified, and blocked evidence. An explicit local-check command uses a small code-owned registry; unknown check IDs are blocked, and report generation does not execute checks. The demo uses synthetic fixtures and does not depend on an external AI provider or external data service.

Proofline is a local prototype. A proven status is limited to a runner-observed result in its declared evidence class; it does not certify hosted behavior or production readiness. The current demo uses three synthetic scenarios to show a declared local pass (conditional until actually run), simulated evidence, and missing hosted evidence.

**IBM Bob Usage Statement (1,215 characters, 170 words; required 500–4,000 characters and no more than 500 words)**

IBM Bob IDE was used as a repository-aware development partner in the Proofline workspace during the event build. The exported task history records Bob first reading the project instructions, product brief, architecture, and build checklist, then planning and implementing core repository work. Bob helped build a code-owned registry for approved local checks, a bounded runner that blocks unknown check IDs, deterministic evidence reports, and a self-contained HTML report with escaped output and safe copy/download controls. Bob also added regression tests, exercised the local verification workflow, and updated the implementation notes and checklist. The resulting application keeps command selection in reviewed code: report generation does not execute checks, and only an explicitly requested allowlisted local check can run. Claims about hosted or provider behavior remain unverified unless matching evidence is supplied. The project uses synthetic fixtures and makes no claim that watsonx.ai or watsonx Orchestrate was used. The repository includes the redacted Bob task-history Markdown and the task's consumption-summary screenshot in `bob_sessions`; the task summary records 36.50 Bobcoins for this task.

The exported history contains the combined project task; the participant
confirmed that all project prompts were in that task and there are no other
team members. Its paired task-summary screenshot is in `bob_sessions/`.

Current product behavior: manifest-declared pass results remain conditional until the explicit allowlisted runner observes them; report generation and the browser intake do not execute checks.

**Categories — saved in the form**

Developer Tools; Productivity.

**Technology tags — saved in the form**

Ibm (the exact available tag selected in the Technologies Used field).

## Media and links

- Cover image: **Uploaded and saved** — `docs/submission/proofline-cover.png`
  (16:9 export of the inspected title slide).
- Video demonstration (MP4, no more than 3 minutes; at least 90 seconds must
  show the solution in action): **Uploaded in the submitted entry** —
  `docs/submission/proofline-demo.mp4` (178 seconds, 1280×720, captioned).
- Slide deck (PDF): **Uploaded in the submitted entry** —
  `docs/submission/proofline-pitch.pdf`. The editable PowerPoint source and
  slide-copy source are `docs/submission/proofline-pitch.pptx` and
  `docs/submission/proofline-pitch-copy.md`. The revised PDF is the presentation
  linked from the submitted entry.
- Public GitHub repository: **Ready** —
  https://github.com/icecold009/proofline-ibm-bob (GitHub reports Public;
  `main` is the default branch).
- Demo platform: **Vercel**.
- Demo URL: **Verified** —
  https://proofline-ibm-g27i974jq-shaurya-s-projects11.vercel.app (synthetic
  interaction checked; provider and production readiness remain unverified).
- IBM Bob task evidence: **Present in the public repository** —
  `bob_sessions/proofline-session-2026-09-26.md` and
  `bob_sessions/proofline-session-2026-09-26-summary.png`; the task history
  contains the combined project prompts and work, with the matching summary
  screenshot. A targeted redaction review found no common credential patterns,
  personal email, or private home paths.
- Additional information: use the long description above; adapt only to actual
  form requirements.

## Submission verification

- Public entry: **Submitted** —
  https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon/lunar/proofline-evidence-before-release.
- Status: **Judging in progress** on the public entry page when checked.
- Dashboard check: account **Approved**; one-member team; solo participation is
  allowed.
- The public entry includes the revised video and PDF, cover, public repository,
  and verified Vercel demo link.
- GitHub reports the repository as public with `main` as the default branch.
- Keep all relevant Bob task-history Markdown exports and summary screenshots
  in `bob_sessions`; the sole combined project task is present and redacted.
- The video, revised PDF deck, cover image, public repository, and live demo
  were included or linked in the submitted entry.
- License: **MIT** — `LICENSE` and the `pyproject.toml` SPDX declaration are
  present. Bob's role is credited in the submission statement and supported by
  the exported task evidence.
- The published close was September 27, 2026, 20:30 India Standard Time
  (15:00 UTC). The entry is already submitted; the deadline is historical.

## Sources

- [IBM Bob 2.0 hackathon live page](https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon/live)
- [IBM Bob 2.0 hackathon event page](https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon)
- [Lablab.ai submission requirements overview](https://lablab.ai/guide/ai-hackathons)
- [Lablab.ai submission tutorial](https://lablab.ai/ai-articles/hackathon-guidelines)
- [IBM Bob Hackathon Guide](https://watsonx-hackathons-2026.s3.us.cloud-object-storage.appdomain.cloud/Lablab-IBM-Bob-hackathon-guide-May-2026.pdf)
