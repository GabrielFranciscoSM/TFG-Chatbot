"""
Entry point for running the backend locally.

Usage from project root:
    cd backend && uv run python -m backend

Or using uvicorn directly (after pip install -e .):
    uvicorn backend.api:app --reload --port 8000
"""

import sys
from pathlib import Path

# Add parent directory to path so 'backend' module can be found
# when running from inside the backend directory
parent = Path(__file__).resolve().parent.parent
if str(parent) not in sys.path:
    sys.path.insert(0, str(parent))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run("backend.api:app", host="127.0.0.1", port=8000, reload=True)
