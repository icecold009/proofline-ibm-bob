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
