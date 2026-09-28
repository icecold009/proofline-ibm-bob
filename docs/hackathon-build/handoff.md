# Proofline build handoff

Updated: 2026-09-28 (India Standard Time). This records repository evidence
and the completed public Lablab submission.

## Project and current evidence

- Product: local evidence classifier for release claims.
- Current implementation: validated manifest, deterministic report
  calculation, static check registry, bounded local check runner, JSON/Markdown/
  HTML reports, loopback browser intake, and synthetic demo fixtures. The
  browser intake never runs checks or persists manifests.
- Current local verification: the bundled Python runtime ran
  `scripts/verify.py`; all 106 tests passed. Python source and embedded
  JavaScript syntax checks and `git diff --check` passed.
- Security review: Codex Security diff scan `9a030a58-4d8c-44d6-b8bc-543a6e093e63`
  completed with zero findings across six changed source files. It was a
  sequential source review; it did not cover hosted, provider, or production
  behavior. The readable report is in the Codex Security scan artifact directory
  for this task.
- Browser evidence: the current loopback browser build was reviewed at desktop
  and 390px mobile widths. All three synthetic scenarios showed their expected
  states; the page had no horizontal overflow or console/page errors. Markdown
  copy and JSON download were verified. The public Vercel deployment at
  `https://proofline-ibm-g27i974jq-shaurya-s-projects11.vercel.app/` was also
  opened and its synthetic conditional case reviewed. This does not establish
  provider behavior or production readiness.
- Pitch deck: seven-slide editable PowerPoint, PDF, and 16:9 cover image are in
  `docs/submission/`; slide renders were visually inspected after export. The
  revised pitch deck and seven-slide text source are in the same directory.
- Event video: `docs/submission/proofline-demo.mp4` is a captioned 178-second
  1280×720 H.264 recording, visually checked at representative timestamps. It
  shows the local app's synthetic cases and the redacted Bob summary image;
  it does not claim those recorded interactions ran on the hosted deployment.
- Bob's role/evidence: the combined project task contains the prompt history
  and Bob's implementation, tests, and documentation work. Its redacted task
  history and task-consumption-summary screenshot are in `bob_sessions/`. The
  screenshot shows the task ID and 36.50 Bobcoins. A targeted scan of the
  export found no Windows or Unix home paths, email addresses, common
  credential assignments, or recognizable token shapes. The participant
  confirmed all project prompts were in this one task; no other relevant Bob
  task or team member is outstanding.
- Lablab submission: the public entry is
  https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon/lunar/proofline-evidence-before-release.
  The entry page showed judging in progress when checked. It links the public
  repository, Vercel demo, event video, and revised presentation. The signed-in
  dashboard showed the account as Approved and a one-member team; solo entry is
  allowed.
- Publication state: GitHub reports the repository as Public, with `main` as
  the default branch. The `codex/proofline-product-improvements` feature branch
  contains the submission package and status-document updates in PR #1, which
  targets `main`.
- Licensing: MIT is declared in the root `LICENSE` and `pyproject.toml` to meet
  the event's stated MIT-compliance requirement.
- Event video limit: maximum 3 minutes, with at least 90 seconds demonstrating
  the solution in action. See `docs/demo-narrative.md`.

## Exact local demo commands

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m proofline web
```

Open `http://127.0.0.1:8765`; select each synthetic example or load a bounded
manifest. To explicitly run the referenced allowlisted checks for an observed
report, run:

```powershell
python -m proofline run-report fixtures/local-pass.json --format html --output proofline-verified.html
```

The demo script is
`docs/demo-narrative.md`.

## Submission status

The submission is complete and publicly available at
https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon/lunar/proofline-evidence-before-release.
The page showed judging in progress when checked. No further Lablab submission
fields or media uploads remain.

## Submission copy and limits

The final copy and entry verification are in `docs/submission-draft.md`. The
entry includes the cover, revised PDF, video, public repository, and verified
Vercel demo link. Submission status was confirmed on the public entry page.

## Repository state

Current branch and commit are recorded by Git. Keep repository changes on the
feature branch and merge through its reviewed pull request; do not commit
directly to `main`.
