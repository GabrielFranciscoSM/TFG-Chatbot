"""
Entry point for running the Math service locally.

Usage from project root:
    cd math_service && uv run python __main__.py

For Docker:
    uvicorn math_service.api:app --host 0.0.0.0 --port 8083
"""

import sys
from pathlib import Path

# Add parent directory to path so 'math_service' module can be found
# when running from inside the math_service directory
parent = Path(__file__).resolve().parent.parent
if str(parent) not in sys.path:
    sys.path.insert(0, str(parent))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run("math_service.api:app", host="127.0.0.1", port=8083, reload=True)
