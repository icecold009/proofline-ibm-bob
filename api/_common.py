"""Shared bounded request and response helpers for hosted API functions."""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_SOURCE = _ROOT / "src"
if str(_SOURCE) not in sys.path:
    sys.path.insert(0, str(_SOURCE))

from proofline.model import MAX_MANIFEST_BYTES, Manifest, ValidationError, validate_manifest


class RequestError(ValueError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def send_bytes(
    handler: BaseHTTPRequestHandler,
    status: int,
    body: bytes,
    content_type: str,
) -> None:
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Referrer-Policy", "no-referrer")
    handler.end_headers()
    handler.wfile.write(body)


def send_json(handler: BaseHTTPRequestHandler, status: int, payload: Any) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    send_bytes(handler, status, body, "application/json; charset=utf-8")


def read_manifest(handler: BaseHTTPRequestHandler) -> Manifest:
    if handler.headers.get_content_type() != "application/json":
        raise RequestError(415, "Send a JSON manifest.")

    raw_length = handler.headers.get("Content-Length", "")
    if not raw_length.isdigit() or len(raw_length) > 6:
        raise RequestError(411, "A valid Content-Length is required.")
    length = int(raw_length)
    if length > MAX_MANIFEST_BYTES:
        raise RequestError(413, "Manifest exceeds the 256 KB size limit.")

    try:
        raw = json.loads(handler.rfile.read(length).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RequestError(400, "Manifest must be valid UTF-8 JSON.") from exc
    try:
        return validate_manifest(raw)
    except ValidationError as exc:
        raise RequestError(400, str(exc)) from exc
