# Script boundary

`verify.py` runs the dependency-free unit suite. Runtime checks must remain
code-owned and explicitly allowlisted; do not add a generic run-anything
endpoint or accept shell command strings from fixtures.

`package_smoke.py` is a separate offline packaging check. It uses the current
Python interpreter and already available setuptools to install a temporary
copy of the package with `--no-index --no-deps --no-build-isolation`. It then
checks the installed `proofline` command, `python -m proofline`, and packaged
web assets from outside the checkout. It never downloads build tools.

Run it from the repository root with Python 3.11 or newer:

```powershell
python scripts/package_smoke.py
```
