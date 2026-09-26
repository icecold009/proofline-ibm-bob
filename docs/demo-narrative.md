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
2. **Manifest intake (25 seconds; application in action).** Open the
   loopback browser interface. Select the declared local-pass example, show the
   bounded manifest and enter a short change request, then analyze it.
3. **Evidence and status (45 seconds; application in action).** Show why the
   manifest-declared pass is conditional, expand its evidence record, and point
   out the source and missing runner observation. Explain that “proven” now
   requires an explicit allowlisted run in the declared evidence class.
4. **Scenario changes and exports (45 seconds; application in action).** Select
   the simulated and unverified examples. Show the status guide, next actions,
   and JSON/Markdown downloads. Simulation stays simulated; absent hosted
   evidence stays unverified.
5. **Explicit local verification (20 seconds).** In a terminal, show:

   ```powershell
   python -m proofline run-report fixtures/local-pass.json --format html --output proofline-verified.html
   ```

   Explain that only this explicit CLI path runs referenced allowlisted checks;
   the browser intake never executes them.
6. **IBM Bob contribution (20 seconds).** Show the genuine Bob IDE work and
   the redacted session history/summary screenshot in `bob_sessions`. Point to
   a concrete Bob-assisted source change; do not imply the local report proves
   hosted behavior.
7. **Close (5 seconds).** Proofline makes evidence limits visible; it does not
   certify production readiness.

Target total: **175 seconds**. Keep the final export at or below 180 seconds
and preserve at least 90 seconds of on-screen application demonstration.

## Preparation commands

PowerShell, from the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m proofline web
```

Open `http://127.0.0.1:8765` and review all three scenarios in the browser
before recording. Run the explicit `run-report` command only when demonstrating
an actually observed allowlisted local check. Recheck the exact build being
recorded.

## Evidence to show

- Three different evidence states from synthetic fixtures.
- The conditional state for a manifest-declared pass.
- Evidence source, provenance, and observation time in the expanded record.
- The limitations and next action beside each claim.
- The browser intake, offline report, and export controls.
- The real Bob IDE work and the redacted task-history Markdown plus summary
  screenshot already in `bob_sessions`.

Do not say a URL is live, Bob task evidence is exported, or the project was
submitted unless that has been verified.
