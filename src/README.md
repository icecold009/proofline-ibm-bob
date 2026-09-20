# Source boundary

The dependency-free deterministic ledger lives in `src/proofline/`. It
validates synthetic manifests and derives evidence statuses without commands,
network access, or provider credentials.

The Bob build should extend this foundation with the safe check registry,
read-only UI, review pass, and exported Bob task evidence. Do not add arbitrary
command execution or live provider claims without updating the specification.
