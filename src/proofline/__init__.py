"""Proofline's dependency-light evidence ledger."""

__version__ = "0.1.0"

from .engine import analyze_manifest
from .model import Manifest, ValidationError, load_manifest, validate_manifest
from .registry import REGISTRY, CheckDefinition, OperationKind, lookup
from .report import render_html, render_markdown
from .runner import CheckRunResult, run_check

__all__ = [
    "REGISTRY",
    "CheckDefinition",
    "CheckRunResult",
    "Manifest",
    "OperationKind",
    "ValidationError",
    "analyze_manifest",
    "load_manifest",
    "lookup",
    "render_html",
    "render_markdown",
    "run_check",
    "validate_manifest",
    "__version__",
]
