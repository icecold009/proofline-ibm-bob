# Build checklist

## Build preferences

- Build mode: autonomous execution with bounded checkpoints.
- Comprehension checks: concise handoff summaries after each milestone.
- Git: small feature-branch commits at each verified milestone.
- Verification: mandatory.
- Check-in cadence: after foundation, core ledger, UI, and submission package.

## Pre-Bob foundation

- [x] **1. Confirm the event boundary**
  Spec ref: spec.md > Future runtime boundary
  What to build: Record the current event facts, IBM Bob requirements, and all
  unresolved kickoff questions.
  Acceptance: No unpublished scoring weight, track, or eligibility value is
  presented as confirmed.
  Verify: docs/hackathon-rules.md refreshed 2026-09-26 against the live event
  page and current Lablab.ai guides. Track names and account-only requirements
  remain explicitly unconfirmed.

- [x] **2. Establish Bob-ready repository instructions**
  Spec ref: spec.md > Future runtime boundary
  What to build: Keep AGENTS.md, SECURITY.md, and README.md aligned with the
  evidence boundaries and safe command policy.
  Acceptance: A new builder can understand the product, safety rules, and Bob
  evidence workflow without private context.
  Verify: Read and aligned README.md, AGENTS.md, and SECURITY.md; README now
  documents current commands, status, boundaries, and pending public artifacts.

- [x] **3. Prepare synthetic fixtures**
  Spec ref: spec.md > Claim record
  What to build: Keep local-pass, simulated-only, and hosted-unverified
  scenarios in fixtures/.
  Acceptance: Fixtures contain no secrets, personal information, client data,
  or live provider responses.
  Verify: Inspect fixture contents and run a secret-pattern scan.

- [x] **4. Lock the product contract**
  Spec ref: spec.md > Report contract
  What to build: Confirm the MVP, cut list, status vocabulary, and export
  contract.
  Acceptance: No P1 feature can block the P0 demo.
  Verify: Compare docs/product-brief.md, prd.md, and spec.md.

## Event build

- [x] **5. Export Bob task evidence**
  Spec ref: spec.md > Future runtime boundary
  What to build: Preserve each relevant Bob task as redacted task-history
  Markdown and task-summary screenshots.
  Acceptance: Genuine Bob task evidence is present under bob_sessions with
  credentials, personal data, and private paths removed.
  Verify: The combined Bob task's exported Markdown and consumption-summary
  screenshot are present under bob_sessions. Three private-path lines in the
  export were redacted; the supplied summary screenshot shows task ID, project
  workspace, context usage, and 36.50 Bobcoins. Complete a final whole-repo
  review before changing repository visibility. Codex cannot recreate Bob UI
  evidence.

- [x] **6. Implement schema validation**
  Spec ref: spec.md > Claim record
  What to build: Validate claim and evidence manifests with strict schemas and
  size limits.
  Acceptance: Malformed, oversized, and unknown evidence classes are rejected.
  Verify: Add positive and negative fixture tests.

- [x] **7. Implement the code-owned check registry — declaration**
  Spec ref: spec.md > Check registry > Declaration milestone
  What to build: Add a static, code-owned registry mapping stable check IDs to
  symbolic OperationKind constants and CheckDefinition metadata (evidence class,
  failure status, timeout, working directory, allowed environment, redaction
  policy). In analyze_manifest, override any check whose ID is absent from the
  registry to result="blocked" before claims are evaluated; dependent claims
  report blocked. Do not invoke operations or execute commands.
  Acceptance: Unknown check IDs produce blocked claims and blocked check results
  in the report. Injection-shaped IDs (shell metacharacters, env-var syntax,
  path traversal) also produce blocked. Malformed manifests continue to raise
  ValidationError. No path from manifest input to subprocess, os.system, eval,
  or exec exists. All three golden fixtures remain green.
  Verify: Bob-implemented and Bob-verified. python -m pytest tests/ -v reported
  16 passed (7 existing + 9 new) with PYTHONPATH=src. The pytest command ran;
  the application invoked no check operations or subprocesses.

- [x] **7A. Implement bounded local check execution**
  Spec ref: spec.md > Check registry > Execution milestone
  What to build: Wire each OperationKind to a bounded safe local invocation.
  Each operation must use a fixed, code-owned allowlisted command. Enforce
  timeout, working directory, and allowed environment variables from
  CheckDefinition. Apply output redaction policy. Return failure_status on
  non-zero exit. No shell interpolation. No command string constructed from
  input.
  Acceptance: Each registered OperationKind maps to an explicit, fixed local
  command in code. Commands are invoked only through the checked-in allowlist.
  Unknown or injection-shaped IDs cannot reach subprocess. Timeout, working
  directory, allowed environment, and redaction are all enforced at runtime.
  Verify: Bob-implemented and Bob-verified. python scripts/verify.py and
  python -m pytest tests/ -v both passed (43 tests). CLI smoke tests:
  run-check check-local-contracts -> pass (exit 0); run-check
  fixture-simulated-telemetry -> fixture (exit 1, no subprocess);
  run-check no-such-check -> blocked (exit 1, no subprocess). The pytest
  command ran; the application invoked no check operations or subprocesses
  except the single allowlisted check-local-contracts invocation in the
  real CLI smoke test.

- [x] **8. Implement deterministic report calculation**
  Spec ref: spec.md > Report contract
  What to build: Derive statuses, limitations, summaries, and next actions.
  Acceptance: Simulation never becomes hosted or provider proof.
  Verify: Run all three golden fixtures twice and compare outputs.

- [x] **9. Build the read-only report UI and browser intake**
  Spec ref: spec.md > Report contract
  What to build: Show a plain-language outcome, claim statuses, expandable
  evidence provenance, limitations, next actions, and exports. Provide a
  loopback-only guided single-claim intake and advanced bounded JSON manifest
  intake.
  Acceptance: A new viewer understands the result within 30 seconds; browser
  intake never executes checks, saves manifests, or calls external services.
  Verify: the bundled Python runtime ran `scripts/verify.py`; all 106 tests
  passed, including loopback intake, registry options, and the no-check-execution
  contract. Browser review covered all three scenarios, expected status changes,
  evidence details, a 390px mobile layout, Markdown copy, and JSON download. No
  horizontal overflow or console/page errors appeared.
  Implementation status: Guided intake and advanced JSON mode are implemented
  on codex/proofline-product-improvements and visually reviewed in a browser.

- [x] **10. Run code review and security pass**
  Spec ref: spec.md > Future runtime boundary
  What to build: Review the implementation, tests, command boundary,
  redaction, and unsupported claims.
  Acceptance: Review reports no security findings; command execution is
  allowlisted and bounded; report text preserves evidence limits.
  Verify: Codex Security diff scan completed with zero findings across six
  changed source files. The current local suite passes 106 tests. The scan did
  not assess hosted or production behavior.

- [ ] **11. Prepare the submission package**
  Spec ref: prd.md > Submission proof points
  What to build: Prepare README setup, demo URL, screenshots, video, deck,
  limitations, and redacted bob_sessions exports. Copy draft, editable deck,
  PDF, and cover image are prepared in docs/submission-draft.md and
  docs/submission/; Bob evidence is present. Public repository access is
  verified; demo URL and video remain pending; MIT licensing is declared.
  Acceptance: A reviewer can run the project and understand Bob's role; the
  required public URL, video, form fields, and evidence are complete.
  Verify: Event form requires title (5–50 characters), short description
  (50–255), problem/solution and Bob usage statements (500–4,000 characters
  each, no more than 500 words), categories, technologies, public repository,
  Bob summary screenshots, demo platform and URL, cover image, MP4 video
  (3-minute maximum with at least 90 seconds of solution action), and PDF deck.
  Copy draft is updated. Bob evidence is present. GitHub reports the repository
  as public with `main` as default. The Lablab draft has the cover, PDF,
  Developer Tools and Productivity categories, and the `Ibm` technology tag
  saved. The required video, live demo URL, and final form fields remain
  pending. MIT is declared in the root license and package metadata.

- [ ] **12. Prepare the final handoff**
  Spec ref: prd.md > Submission proof points
  What to build: Gather project story, final screenshots, repository link,
  demo instructions, and the final event-specific submission fields. A local
  handoff with known facts and explicit pending items is in
  docs/hackathon-build/handoff.md.
  Acceptance: No required submission field is left guessed.
  Verify: Complete the lablab form only after checking kickoff instructions.
