from __future__ import annotations

import uuid


def generate_request_id() -> str:
    """Generate a unique request/correlation ID."""
    return str(uuid.uuid4())
