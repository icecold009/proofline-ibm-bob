# Build checklist

## Build preferences

- Build mode: autonomous execution with bounded checkpoints.
- Comprehension checks: concise handoff summaries after each milestone.
- Git: small feature-branch commits at each verified milestone.
- Verification: mandatory.
- Check-in cadence: after foundation, core ledger, UI, and submission package.

## Pre-Bob foundation

- [ ] **1. Confirm the event boundary**
  Spec ref: spec.md > Future runtime boundary
  What to build: Record the current event facts, IBM Bob requirements, and all
  unresolved kickoff questions.
  Acceptance: No unpublished scoring weight, track, or eligibility value is
  presented as confirmed.
  Verify: Review docs/hackathon-rules.md against the current official event page.

- [ ] **2. Establish Bob-ready repository instructions**
  Spec ref: spec.md > Future runtime boundary
  What to build: Keep AGENTS.md, SECURITY.md, and README.md aligned with the
  evidence boundaries and safe command policy.
  Acceptance: A new builder can understand the product, safety rules, and Bob
  evidence workflow without private context.
  Verify: Read the files from a clean checkout.

- [ ] **3. Prepare synthetic fixtures**
  Spec ref: spec.md > Claim record
  What to build: Keep local-pass, simulated-only, and hosted-unverified
  scenarios in fixtures/.
  Acceptance: Fixtures contain no secrets, personal information, client data,
  or live provider responses.
  Verify: Inspect fixture contents and run a secret-pattern scan.

- [ ] **4. Lock the product contract**
  Spec ref: spec.md > Report contract
  What to build: Confirm the MVP, cut list, status vocabulary, and export
  contract.
  Acceptance: No P1 feature can block the P0 demo.
  Verify: Compare docs/product-brief.md, prd.md, and spec.md.

## Event build

- [ ] **5. Use Bob to inspect and plan**
  Spec ref: spec.md > Future runtime boundary
  What to build: Ask Bob to inspect the repository, explain the architecture,
  and produce a bounded implementation plan.
  Acceptance: The task history shows repository context and no blind edits.
  Verify: Export the task history and summary screenshot.

- [ ] **6. Implement schema validation**
  Spec ref: spec.md > Claim record
  What to build: Validate claim and evidence manifests with strict schemas and
  size limits.
  Acceptance: Malformed, oversized, and unknown evidence classes are rejected.
  Verify: Add positive and negative fixture tests.

- [ ] **7. Implement the code-owned check registry**
  Spec ref: spec.md > Check registry
  What to build: Add stable check IDs and safe local execution without shell
  interpolation.
  Acceptance: Unknown check IDs are blocked and input strings cannot become
  commands.
  Verify: Run injection-shaped negative tests.

- [ ] **8. Implement deterministic report calculation**
  Spec ref: spec.md > Report contract
  What to build: Derive statuses, limitations, summaries, and next actions.
  Acceptance: Simulation never becomes hosted or provider proof.
  Verify: Run all three golden fixtures twice and compare outputs.

- [ ] **9. Build the read-only report UI**
  Spec ref: spec.md > Report contract
  What to build: Show claims, status, evidence class, limitations, and export
  actions in one clear view.
  Acceptance: A new viewer understands the result within 30 seconds.
  Verify: Test the three fixtures in a clean browser.

- [ ] **10. Run Bob review and security pass**
  Spec ref: spec.md > Future runtime boundary
  What to build: Have Bob review the implementation, tests, command boundary,
  redaction, and unsupported claims.
  Acceptance: No hardcoded secrets, arbitrary commands, or overclaiming copy.
  Verify: Run tests, static checks, and a manual repository review.

- [ ] **11. Prepare the submission package**
  Spec ref: prd.md > Submission proof points
  What to build: Prepare README setup, demo URL, screenshots, video, deck,
  limitations, and redacted bob_sessions exports.
  Acceptance: A reviewer can run the project and understand Bob's role.
  Verify: Test the public URL and review the repository from a clean clone.

- [ ] **12. Prepare the final handoff**
  Spec ref: prd.md > Submission proof points
  What to build: Gather project story, final screenshots, repository link,
  demo instructions, and the final event-specific submission fields.
  Acceptance: No required submission field is left guessed.
  Verify: Complete the lablab form only after checking kickoff instructions.
