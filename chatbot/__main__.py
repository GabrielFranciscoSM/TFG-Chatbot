"""
Entry point for running the chatbot service locally.

Usage from project root:
    cd chatbot && uv run python __main__.py

For Docker:
    uvicorn chatbot.api:app --host 0.0.0.0 --port 8080
"""

import sys
from pathlib import Path

# Add parent directory to path so 'chatbot' module can be found
# when running from inside the chatbot directory
parent = Path(__file__).resolve().parent.parent
if str(parent) not in sys.path:
    sys.path.insert(0, str(parent))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run("chatbot.api:app", host="127.0.0.1", port=8080, reload=True)
