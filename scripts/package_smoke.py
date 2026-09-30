"""Verify the offline PEP 517 install and installed CLI in a temporary copy."""

from __future__ import annotations

import importlib.util
import json
import os
import queue
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import urllib.request
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def main() -> int:
    if sys.version_info < (3, 11):
        raise SystemExit("Package smoke requires Python 3.11 or newer.")
    if importlib.util.find_spec("setuptools") is None:
        raise SystemExit("setuptools>=61 must already be available; this smoke never downloads build tools.")
    import setuptools

    version = re.match(r"^(\d+)\.(\d+)", setuptools.__version__)
    if version is None or tuple(map(int, version.groups())) < (61, 0):
        raise SystemExit("setuptools>=61 must already be available; this smoke never downloads build tools.")

    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONUNBUFFERED"] = "1"

    with tempfile.TemporaryDirectory(prefix="proofline-package-smoke-") as temp_name:
        temp = Path(temp_name)
        source = temp / "source"
        source.mkdir()
        for filename in ("pyproject.toml", "README.md", "LICENSE"):
            shutil.copy2(ROOT / filename, source / filename)
        for directory in ("src", "public", "fixtures"):
            shutil.copytree(ROOT / directory, source / directory, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "*.pyo"
            ))

        environment = temp / "venv"
        venv.EnvBuilder(with_pip=True, system_site_packages=True).create(environment)
        scripts = environment / ("Scripts" if os.name == "nt" else "bin")
        python = scripts / ("python.exe" if os.name == "nt" else "python")
        command = scripts / ("proofline.exe" if os.name == "nt" else "proofline")

        _run(
            [
                str(python), "-m", "pip", "install", "--disable-pip-version-check",
                "--no-cache-dir", "--no-index", "--no-deps", "--no-build-isolation",
                str(source),
            ],
            cwd=temp,
            env=env,
        )
        if not command.is_file():
            raise AssertionError("The proofline console entry point was not installed.")

        help_outputs = (
            _run([str(command), "--help"], cwd=temp, env=env),
            _run([str(python), "-m", "proofline", "--help"], cwd=temp, env=env),
        )
        for help_text in help_outputs:
            for subcommand in ("report", "run-check", "run-report", "web"):
                if subcommand not in help_text:
                    raise AssertionError(f"CLI help omitted {subcommand!r}.")

        fixture = source / "fixtures" / "local-pass.json"
        console_report = json.loads(_run(
            [str(command), "report", str(fixture), "--format", "json"], cwd=temp, env=env
        ))
        module_report = json.loads(_run(
            [str(python), "-m", "proofline", str(fixture), "--format", "json"],
            cwd=temp,
            env=env,
        ))
        if console_report["report_id"] != module_report["report_id"]:
            raise AssertionError("Console and module entry points produced different reports.")

        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        process = subprocess.Popen(
            [str(command), "web", "--port", str(port)],
            cwd=temp,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        lines: queue.Queue[str] = queue.Queue()
        threading.Thread(target=lambda: lines.put(process.stdout.readline()), daemon=True).start()
        try:
            startup = lines.get(timeout=15)
            if "Proofline local preview:" not in startup:
                process.wait(timeout=5)
                raise AssertionError(startup + process.stdout.read())
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3) as response:
                page = response.read().decode("utf-8")
                if response.status != 200 or "Proofline" not in page:
                    raise AssertionError("Installed web page did not load correctly.")
                policy = response.headers.get("Content-Security-Policy", "")
                if "script-src 'self'" not in policy or "style-src 'self'" not in policy or "unsafe-inline" in policy:
                    raise AssertionError("Installed web page did not receive the strict same-origin CSP.")
                if "/styles.css" not in page or "/app.js" not in page:
                    raise AssertionError("Installed web page omitted an external static asset.")
            for asset_path, content_type in (
                ("/styles.css", "text/css"),
                ("/app.js", "text/javascript"),
            ):
                with urllib.request.urlopen(f"http://127.0.0.1:{port}{asset_path}", timeout=3) as response:
                    if response.status != 200 or not response.headers.get("Content-Type", "").startswith(content_type):
                        raise AssertionError(f"Installed static asset {asset_path} did not load correctly.")
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=3) as response:
                health = json.loads(response.read())
                if response.status != 200 or health != {"status": "ok", "version": "0.1.0"}:
                    raise AssertionError("Installed health route exposed unexpected or missing metadata.")
                if not response.headers.get("X-Request-ID"):
                    raise AssertionError("Installed health route omitted its request ID.")
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/api/fixtures/local-pass", timeout=3
            ) as response:
                packaged_fixture = json.loads(response.read())
                if response.status != 200 or packaged_fixture["scenario"] != "local-pass":
                    raise AssertionError("Installed synthetic fixture route did not load correctly.")
        finally:
            process.terminate()
            process.wait(timeout=5)

    print(f"Python {sys.version.split()[0]}; setuptools {setuptools.__version__}")
    print("Offline temporary install, console/module help and reports without PYTHONPATH: PASS")
    print("Installed web page, strict CSP, CSS/JS assets, health metadata and synthetic fixture route outside the checkout: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
