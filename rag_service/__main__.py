"""
Entry point for running the RAG service locally.

Usage from project root:
    cd rag_service && uv run python __main__.py

For Docker:
    uvicorn rag_service.api:app --host 0.0.0.0 --port 8081
"""

import sys
from pathlib import Path

# Add parent directory to path so 'rag_service' module can be found
# when running from inside the rag_service directory
parent = Path(__file__).resolve().parent.parent
if str(parent) not in sys.path:
    sys.path.insert(0, str(parent))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run("rag_service.api:app", host="127.0.0.1", port=8081, reload=True)
