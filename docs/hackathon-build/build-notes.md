# Build notes

## 2026-09-20

- Foundation prepared before IBM Bob access.
- The repository is intentionally non-functional at this stage.
- Core implementation is reserved for the event build so Bob can be a visible
  and meaningful part of the work.
- Synthetic fixtures are allowed preparation material; no real data is included.
- The main risk is confusing local or simulated evidence with hosted or provider
  proof.

## Pre-Bob scaffold

- Added a dependency-free Python core under `src/proofline/`.
- Added strict manifest validation with bounded input sizes and allowlisted
  evidence classes/results.
- Added deterministic evidence status calculation and JSON/Markdown rendering.
- Added tests for local proof, simulation, missing provider evidence, blocked
  references, status-field injection, invalid classes, and deterministic output.
- Deliberately left the safe command registry, UI, Bob review, and Bob task
  exports for the official build.

## 2026-09-26 event build status

- The static check registry, bounded `run-check` path, deterministic report
  calculation, and offline HTML report are now present in the repository.
- The user-provided Bob implementation reports attribute the registry, runner,
  CLI, and HTML implementation to Bob. The current working tree was reviewed
  and verified by Codex; this does not substitute for the required Bob task
  history and summary screenshot exports.
- Codex verification: `python scripts/verify.py` ran 100 tests successfully.
- Codex Security diff review: zero findings across the six changed source
  files; no hosted, provider, or production environment was assessed.
- The user reviewed the three generated HTML previews and confirmed the layout,
  statuses, content, and export controls.
- Public demo, public repository publication, and submission video remain
  pending. The deck, cover, and redacted Bob task export are prepared. The
  project declares the MIT License. See `docs/submission-draft.md` and
  `docs/hackathon-build/handoff.md`.
