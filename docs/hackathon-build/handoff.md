# Proofline build handoff

Updated: 2026-09-27 (India Standard Time). This records repository evidence
and remaining submission work; it does not claim that the project has been
submitted.

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
  copy and JSON download were verified. This is local browser evidence, not a
  public deployment check.
- Pitch deck: seven-slide editable PowerPoint, PDF, and 16:9 cover image are in
  `docs/submission/`; slide renders were visually inspected after export.
- Bob's role/evidence: the combined project task contains the prompt history
  and Bob's implementation, tests, and documentation work. Its redacted task
  history and task-consumption-summary screenshot are in `bob_sessions/`. The
  screenshot shows the task ID and 36.50 Bobcoins. A targeted scan of the
  export found no Windows or Unix home paths, email addresses, common
  credential assignments, or recognizable token shapes. The participant
  confirmed all project prompts were in this one task; no other relevant Bob
  task or team member is outstanding.
- Lablab dashboard: account status showed Approved; the one-member team is
  permitted to participate solo. The saved draft has Developer Tools and
  Productivity categories, the `Ibm` technology tag, the cover image, and the
  PDF deck. The media step shows 61% overall progress; the required video is
  still missing, so the form has not advanced to step 3.
- Publication state: GitHub reports the repository as Public, with `main` as
  the default branch. The release branches point to `8620493`. The
  `codex/proofline-product-improvements` feature branch is checked out locally;
  its implementation changes are uncommitted and not pushed. No live demo URL
  or event video exists yet.
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

## Remaining work, in order

1. Deploy the working prototype to the authorized public preview host. Verify
   the preview URL in a signed-out browser and record the actual platform and
   URL; no Proofline deployment exists yet.
2. Complete and save the remaining non-video submission fields when the form
   allows them. The video field is required to leave media step 2; do not enter
   a placeholder or try to bypass that validation.
3. Record the event MP4 last (maximum 3 minutes, with at least 90 seconds
   showing the solution in action), and upload it only after the demo URL,
   project details, and other media have been checked.
4. Review the saved draft and current event deadline. Do not press the final
   Submit control without the participant's explicit instruction.

## Submission copy and limits

The copy draft is in `docs/submission-draft.md` and reflects the event form's
observed text limits and current saved selections. The cover and PDF are saved
in the form; the video and step-3 demo platform/URL remain pending. The public
repository does not establish a demo deployment or a submitted entry.

## Repository state

Current branch and commit are recorded by Git. All reported implementation and
Codex documentation edits remain local until explicitly committed and
published. Continue on a feature branch and do not commit or merge directly to
`main`.
