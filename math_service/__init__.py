"""Math service package.

This module intentionally avoids importing the FastAPI `app` at package
import time (to prevent pulling FastAPI and other heavy deps when tools
or tests only need type information). Import `math_service.api.app` when an
ASGI server needs it.
"""

__all__: list[str] = []
