# Proofline demo narrative

## One-line pitch

Proofline turns release claims into a small evidence report, so teams can say
what their AI-assisted change actually proved without mistaking a local test or
simulation for production evidence.

## Event video plan: 2 minutes 55 seconds target

The event-specific limit is **3 minutes maximum**, with **at least 90 seconds
showing the solution in action**. This plan allocates 105 seconds to live
application interaction and leaves five seconds under the hard limit.

1. **Problem (15 seconds).** A passing local test does not prove a hosted
   integration works. State that Proofline uses three synthetic scenarios.
2. **Local-pass report (55 seconds; application in action).** Open the
   local-pass HTML report. Show the summary, claim, evidence reference,
   limitation, next action, and explain that “proven” is limited to the declared
   local evidence class.
3. **Simulated and unverified reports (50 seconds; application in action).**
   Open the other two reports. Show that simulation stays simulated and absent
   hosted evidence stays unverified.
4. **Safety boundary and exports (25 seconds).** Show that report generation
   does not execute checks; the separate runner accepts only an allowlisted
   local check and blocks unknown IDs. Show the HTML copy/download controls.
5. **IBM Bob contribution (25 seconds).** Show the genuine Bob IDE work and
   the redacted session history/summary screenshot in `bob_sessions`. Point to
   a concrete Bob-assisted source change; do not imply the local report proves
   hosted behavior.
6. **Close (5 seconds).** Proofline makes evidence limits visible; it does not
   certify production readiness.

Target total: **175 seconds**. Keep the final export at or below 180 seconds
and preserve at least 90 seconds of on-screen application demonstration.

## Preparation commands

PowerShell, from the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m proofline fixtures/local-pass.json --format html --output proofline-local-pass.html
python -m proofline fixtures/simulated-only.json --format html --output proofline-simulated-only.html
python -m proofline fixtures/hosted-unverified.json --format html --output proofline-hosted-unverified.html
```

Open the generated files in a browser before recording. The user has already
reviewed all three previews and confirmed the report layout, status distinctions,
claim content, and copy/download controls. Recheck the exact build being recorded.

## Evidence to show

- Three different evidence states from synthetic fixtures.
- The limitations and next action beside each claim.
- The offline report and export controls.
- The real Bob IDE work and the redacted task-history Markdown plus summary
  screenshot already in `bob_sessions`.

Do not say a URL is live, Bob task evidence is exported, or the project was
submitted unless that has been verified.
