# Proofline demo narrative

## One-line pitch

Proofline turns release claims into a small evidence report, so teams can say
what their AI-assisted change actually proved without mistaking a local test or
simulation for production evidence.

## Recorded event video: 2 minutes 58 seconds

The MP4 is 178 seconds, H.264 at 1280×720, with the original on-screen
captions preserved and an English voiceover. The video stream is unchanged.
More than 130 seconds show the local application analyzing synthetic
examples. A separate closing card shows the verified public Vercel demo URL.

1. **Problem and conditional pass.** Introduce the local synthetic preview,
   analyze the declared local-pass example, and expand its check evidence.
2. **Other evidence states.** Analyze simulated telemetry and missing hosted
   evidence, showing their classifications and next actions.
3. **Reports and limitations.** Show the status guide and method/limitations,
   including that the browser does not execute checks or call an external AI
   provider.
4. **IBM Bob contribution.** Show the redacted Bob task-summary screenshot that
   is also included with the project repository evidence.
5. **Close.** Show the separately verified public Vercel URL and state that
   provider behavior and production readiness remain unverified.

Output: `docs/submission/proofline-demo.mp4`. The full-resolution clip was
visually checked at representative points, including the Bob summary segment.

## Preparation commands

PowerShell, from the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m proofline web
```

Open `http://127.0.0.1:8765` and review all three synthetic scenarios in the
browser before recording. Run the explicit `run-report` command only when
demonstrating an actually observed allowlisted local check. The browser intake
never executes checks.

## Evidence to show

- Three different evidence states from synthetic fixtures.
- The conditional state for a manifest-declared pass.
- Evidence source, provenance, and observation time in the expanded record.
- The limitations and next action beside each claim.
- The browser intake, report guide, method limitations, and export controls.
- The real Bob IDE work and the redacted task-history Markdown plus summary
  screenshot already in `bob_sessions`.

The public Vercel page was checked with synthetic input. This video records the
local preview and displays the public URL separately; it does not claim that
the hosted deployment ran the recorded interactions. The video and revised
presentation are included in the published Lablab entry, whose page showed
judging in progress when checked.
