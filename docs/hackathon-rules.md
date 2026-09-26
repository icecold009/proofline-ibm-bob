# IBM Bob 2.0 Hackathon guidance

Last checked: 2026-09-27 (India Standard Time) against the live event page and
signed-in submission form. Recheck the dashboard before submitting.

## Current event facts

- Event: IBM Bob 2.0 hackathon.
- Format: online; 48-hour build window, September 25–27, 2026.
- Published submission close: September 27, 2026 at 15:00 UTC (20:30 India
  Standard Time).
- Published prize pool: $12,000.
- The event page says participants may build solo or as a team and must register
  before the kickoff stream to start building with Bob.
- The event page currently shows submissions open and a close at September 27,
  2026, 20:30 India Standard Time (15:00 UTC).
- The signed-in dashboard shows the account as Approved and a one-member team;
  solo participation is allowed. The saved form shows Developer Tools and
  Productivity categories, the `Ibm` technology tag, cover and PDF uploads, and
  61% overall progress. The required video remains missing.
- Solo participation is allowed; the one-member team is not itself a blocker.

Sources:

- [IBM Bob 2.0 hackathon event page](https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon)
- [IBM Bob 2.0 hackathon live page](https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon/live)
- [Lablab.ai participation and submission FAQ](https://lablab.ai/guide)

Lablab's general participation FAQ says all team members must register and
participants must belong to a Lablab team, including solo participants. Check
the event dashboard to confirm the account is enrolled and associated with a
team before relying on eligibility.

## Event-specific submission requirements

The live event page and logged-in form require the following:

- Basic information: title (5–50 characters), short description
  (50–255 characters), problem-and-solution statement (500–4,000 characters,
  no more than 500 words), IBM Bob usage statement (500–4,000 characters,
  no more than 500 words), categories, and technology tags.
- Application and code: publicly accessible code repository, IBM Bob task
  session summary screenshots, demo application platform, and application URL.
- Media: cover image, video demonstration, and slide presentation.
- The video must be MP4, no more than 3 minutes, with at least 90 seconds
  showing the solution in action. It must explain the problem, narrate the
  demonstration, and clearly show IBM Bob's role.
- The repository must contain the code/files where IBM Bob assisted and
  task-summary screenshots from each team member.
- The event page states that submissions must be original and MIT-compliant.
  The project now declares the MIT License in `LICENSE` and `pyproject.toml`.
- The current form's first step showed required Categories and Technologies
  Used selectors; no track selector was visible on that step. Use only choices
  actually offered by the form.

The general Lablab guide says up to five minutes, but that broader limit is
superseded here by the event-specific three-minute maximum.

Sources:

- [Lablab.ai AI hackathon guide](https://lablab.ai/guide/ai-hackathons)
- [Lablab.ai submission tutorial](https://lablab.ai/ai-articles/hackathon-guidelines)

## IBM Bob evidence and project-data boundaries

The current event page requires active IBM Bob use, the relevant code/files in
the repository, and task-summary screenshots from each team member. The May
2026 sponsor guide additionally explains how to export Bob IDE task histories
and summaries. Preserve genuine Bob exports and redact credentials and private
data before any public upload.

- Sponsor guide (May 2026):
  https://watsonx-hackathons-2026.s3.us.cloud-object-storage.appdomain.cloud/Lablab-IBM-Bob-hackathon-guide-May-2026.pdf

Project policy: use synthetic fixtures; do not include real client, learner,
personal, confidential, or social-media data. Redact credentials, tokens, and
private paths from Bob history and screenshots before placing them in the repo.

## Remaining account or submission checks

- The account's Approved status and one-member team were observed in the
  dashboard; recheck eligibility if the dashboard changes.
- Any further fields shown on the final submission step; the required video
  currently blocks navigation from media step 2.
- Upload size limits for the remaining video and accepted URL formats for the
  final step are not yet verified; inspect those fields before completing them.
- The redacted combined-task Bob history and its summary screenshot are present
  under `bob_sessions/` in the public repository; the user confirmed all
  project prompts were within that one task.
- GitHub reports the repository as public, with `main` as the default branch.
  The public demo and video are not yet available.

Do not claim a public demo or completed submission until its corresponding
artifact exists and has been checked.
