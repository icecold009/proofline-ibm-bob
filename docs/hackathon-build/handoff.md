# Proofline build handoff

Updated: 2026-09-26. This records repository evidence and the remaining
submission work; it does not claim that the project has been published or
submitted.

## Project and current evidence

- Product: local evidence classifier for release claims.
- Current implementation: validated manifest, deterministic report
  calculation, static check registry, bounded local check runner, JSON/Markdown/
  HTML reports, and synthetic demo fixtures.
- Local verification: `python scripts/verify.py` — 100 tests passed.
- Security review: Codex Security diff scan `9a030a58-4d8c-44d6-b8bc-543a6e093e63`
  completed with zero findings across six changed source files. It was a
  sequential source review; it did not cover hosted, provider, or production
  behavior. The readable report is in the Codex Security scan artifact directory
  for this task.
- Browser evidence: the user reviewed all three HTML previews and confirmed the
  content, layout, status distinctions, and copy/download controls.
- Pitch deck: seven-slide editable PowerPoint, PDF, and 16:9 cover image are in
  `docs/submission/`; slide renders were visually inspected after export.
- Bob's role/evidence: the redacted task-history Markdown and consumption-summary
  screenshot for the combined Bob task are in `bob_sessions/`. The screenshot
  records 36.50 Bobcoins. Complete a final whole-repository evidence review
  before making the repository public.
- Lablab dashboard: account status showed Approved; the team has one member,
  and the event allows solo participation. The submission draft is in progress;
  the opened form showed 0% completion.
- Publication state: the connected GitHub repository currently displays as
  Private. The local working changes have not been published. No live demo URL
  or event video exists in the repository.
- Licensing: MIT is declared in the root `LICENSE` and `pyproject.toml` to meet
  the event's stated MIT-compliance requirement.
- Event video limit: maximum 3 minutes, with at least 90 seconds demonstrating
  the solution in action. See `docs/demo-narrative.md`.

## Exact local demo commands

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python scripts/verify.py
python -m proofline fixtures/local-pass.json --format html --output proofline-local-pass.html
python -m proofline fixtures/simulated-only.json --format html --output proofline-simulated-only.html
python -m proofline fixtures/hosted-unverified.json --format html --output proofline-hosted-unverified.html
```

Open the three generated HTML files in a browser. The demo script is
`docs/demo-narrative.md`.

## Remaining work, in order

1. Complete a final redaction review of the genuine Bob task-history Markdown
   and summary screenshot already in `bob_sessions/`.
2. Confirm required category and technology tag selections and later-step
   upload limits in the Lablab form; do not guess values.
3. Record the MP4 presentation (maximum 3 minutes; at least 90 seconds showing
   the solution in action). Review the cover image and PDF deck against the
   final demo before upload.
4. Resolve the private-repository blocker and choose a hosting platform. Publish
   the reviewed feature branch, then verify the repository and online prototype
   from signed-out browser sessions. Record their real URLs.
5. Complete and submit the dashboard form before September 27, 2026, 20:30
   India Standard Time (15:00 UTC), after confirming the live dashboard still
   shows that deadline.

## Submission copy and limits

The copy draft is in `docs/submission-draft.md` and now reflects the event form's
observed text limits and video requirement. It leaves categories, technology
tags, video, public repository access, demo platform, and demo URL pending.
Proofline is a local prototype today; the current repository does not establish
deployment, public access, or submission.

## Repository state

Current branch and commit are recorded by Git. All reported implementation and
Codex documentation edits remain local until explicitly committed and
published. Continue on a feature branch and do not commit or merge directly to
`main`.
