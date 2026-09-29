"""Small, content-free request metadata helpers for local and hosted routes."""

from __future__ import annotations

import json
import time
import uuid
from http.server import BaseHTTPRequestHandler


def begin_request(handler: BaseHTTPRequestHandler, route: str) -> str:
    """Attach a generated request ID and a fixed, non-user-controlled route."""
    request_id = uuid.uuid4().hex
    handler._proofline_request_id = request_id
    handler._proofline_request_started = time.perf_counter()
    handler._proofline_route = route
    return request_id


def request_metadata(
    handler: BaseHTTPRequestHandler,
    status: int,
    response_bytes: int,
) -> dict[str, str | int | float]:
    """Return only the approved operational fields for a completed response."""
    started = getattr(handler, "_proofline_request_started", time.perf_counter())
    return {
        "request_id": getattr(handler, "_proofline_request_id", "unknown"),
        "route": getattr(handler, "_proofline_route", "other"),
        "status": status,
        "response_bytes": response_bytes,
        "duration_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def log_response(handler: BaseHTTPRequestHandler, status: int, response_bytes: int) -> None:
    """Write one structured line without request paths, headers, or contents."""
    print(json.dumps(request_metadata(handler, status, response_bytes), separators=(",", ":")), flush=True)
