#!/usr/bin/env python
"""Export OpenAPI specifications from all FastAPI services.

This script generates OpenAPI JSON specs for each microservice,
which can be used for:
- API documentation
- Contract testing
- Client generation
- API gateway configuration

Usage:
    python scripts/export_openapi.py

Output files are created in docs/api/:
    - backend_openapi.json
    - chatbot_openapi.json
    - rag_service_openapi.json
"""

import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def export_backend_spec():
    """Export backend/gateway OpenAPI spec."""
    from backend.api import app

    spec = app.openapi()
    spec["info"]["title"] = "TFG Chatbot Backend/Gateway API"
    spec["info"]["description"] = (
        "API Gateway for the TFG Chatbot. Handles authentication, "
        "session management, and routes requests to internal services."
    )
    return spec


def export_chatbot_spec():
    """Export chatbot OpenAPI spec."""
    from chatbot.api import app

    spec = app.openapi()
    spec["info"]["title"] = "TFG Chatbot AI Agent API"
    spec["info"]["description"] = (
        "AI Agent service powered by LangGraph. Handles conversation flow, "
        "tool execution, and test session management."
    )
    return spec


def export_rag_service_spec():
    """Export RAG service OpenAPI spec."""
    from rag_service.api import app

    spec = app.openapi()
    spec["info"]["title"] = "TFG Chatbot RAG Service API"
    spec["info"]["description"] = (
        "Retrieval-Augmented Generation service. Handles document indexing, "
        "semantic search, and file management."
    )
    return spec


def main():
    """Export all OpenAPI specs."""
    output_dir = project_root / "docs" / "api"
    output_dir.mkdir(parents=True, exist_ok=True)

    services = [
        ("backend", export_backend_spec),
        ("chatbot", export_chatbot_spec),
        ("rag_service", export_rag_service_spec),
    ]

    for name, export_func in services:
        try:
            print(f"Exporting {name} OpenAPI spec...")
            spec = export_func()
            output_file = output_dir / f"{name}_openapi.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(spec, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Saved to {output_file}")
        except Exception as e:
            print(f"  ✗ Failed to export {name}: {e}")

    print("\nDone! OpenAPI specs exported to docs/api/")


if __name__ == "__main__":
    main()
