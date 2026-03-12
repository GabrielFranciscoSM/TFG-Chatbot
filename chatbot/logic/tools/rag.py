"""Tool for semantic search using the RAG service."""

import logging
from typing import Any

import requests
from langchain.tools import tool

from chatbot.config import settings as chatbot_settings
from chatbot.logic.models import RagQueryInput
from chatbot.logic.tools.utils import normalize_rag_results

logger = logging.getLogger(__name__)


@tool(args_schema=RagQueryInput)
def rag_search(
    query: str,
    asignatura: str | None = None,
    tipo_documento: str | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    """Perform a semantic search against the external RAG service.

    Args:
        query: The search query text
        asignatura: Optional subject filter
        tipo_documento: Optional document type filter
        top_k: Optional limit on number of results

    Returns:
        A structured dict with search results or error info.
    """
    try:
        logger.debug(
            "rag_search called with query=%s, asignatura=%s, tipo_documento=%s, top_k=%s",
            query,
            asignatura,
            tipo_documento,
            top_k,
        )

        # Build request
        url = f"{chatbot_settings.rag_service_url.rstrip('/')}/search"
        payload: dict[str, Any] = {"query": query}
        if asignatura:
            payload["asignatura"] = asignatura
        if tipo_documento:
            payload["tipo_documento"] = tipo_documento
        if top_k:
            payload["top_k"] = top_k

        logger.debug("Posting to RAG service url=%s payload=%s", url, payload)

        # Make request
        resp = requests.post(url, json=payload, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        logger.debug("RAG service returned data: %s", data)

        # Normalize results
        normalized = normalize_rag_results(data)

        logger.debug("Returning %d normalized results", len(normalized))
        return {
            "ok": True,
            "query": data.get("query") if isinstance(data, dict) else query,
            "total_results": (
                data.get("total_results")
                if isinstance(data, dict) and data.get("total_results") is not None
                else len(normalized)
            ),
            "results": normalized,
        }

    except requests.exceptions.Timeout as e:
        logger.error("RAG service timeout: %s", str(e))
        return {"ok": False, "error": f"RAG service timeout: {str(e)}"}
    except requests.exceptions.ConnectionError as e:
        logger.error("Cannot connect to RAG service: %s", str(e))
        return {"ok": False, "error": f"Cannot connect to RAG service: {str(e)}"}
    except requests.exceptions.RequestException as e:
        logger.error("Error contacting RAG service: %s", str(e))
        return {"ok": False, "error": f"Error contacting RAG service: {str(e)}"}
    except Exception as e:
        logger.error("Unexpected error in rag_search: %s", str(e))
        return {"ok": False, "error": f"Unexpected error: {str(e)}"}
