# Script boundary

`verify.py` runs the dependency-free unit suite. Runtime checks must remain
code-owned and explicitly allowlisted; do not add a generic run-anything
endpoint or accept shell command strings from fixtures.
