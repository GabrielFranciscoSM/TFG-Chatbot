""" Tools for the LangGraph agent.
Contains various tools that can be used by the agent to perform actions.
"""

from langchain.tools import tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from backend.logic.models import WebSearchInput, CalculatorInput, GetSubjectDataInput, SubjectDataKey
from backend.logic.models import SubjectLookupInput, RagQueryInput
from backend.config import settings as backend_settings
from backend.db.mongo import MongoDBClient
from typing import Annotated, Optional
import json
import requests
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
@tool(args_schema=WebSearchInput)
def web_search(query: str) -> str:
    """
    Search the web for information using DuckDuckGo.
    """
    try:
        search = DuckDuckGoSearchAPIWrapper()
        results = search.run(query)
        return results
    except Exception as e:
        return f"Error performing web search: {str(e)}"

# List of all available tools
AVAILABLE_TOOLS = [web_search]


@tool(args_schema=SubjectLookupInput)
def get_guia(
    key: SubjectDataKey = None,
    asignatura: str = None,
) -> str:
    """Retrieve a stored guia document for the agent's current `asignatura` state.

    The agent should place the subject into its injected state `asignatura`.
    This function reads the injected `asignatura` via `InjectedState("asignatura")`.
    If no asignatura is present the tool returns a helpful error message.
    """
    try:
        # If the agent did not provide an asignatura via injected state,
        # return a clear message so the agent can ask the user to set it.

        if not asignatura:
            return "No guia found for subject"

        asignatura_state = asignatura

        client = MongoDBClient()
        client.connect()
        doc = client.find_by_subject("guias", asignatura_state)
        client.close()
        if not doc:
            return f"No guia found for subject: {asignatura_state}"

        # If a specific key is requested, use the enum value directly (dot notation supported)
        if key:
            path = key.value
            # support nested keys with dot notation
            parts = path.split('.') if isinstance(path, str) else [path]
            value = doc
            for p in parts:
                if not isinstance(value, dict):
                    value = None
                    break
                value = value.get(p)

            if value is None:
                return f"Key '{key.value}' not present in guia for subject {asignatura_state}"

            # Return JSON string for structured content
            return json.dumps(value, ensure_ascii=False)

        # Otherwise, return a short summary
        summary = {
            "subject": doc.get("subject"),
            "asignatura": doc.get("asignatura"),
            "grado": doc.get("grado"),
            "curso": doc.get("curso"),
            "url": doc.get("url"),
            "brief_description": doc.get("breve_descripción_de_contenidos", [])[:3],
        }
        return json.dumps(summary, ensure_ascii=False)
    except Exception as e:
        return f"Error retrieving guia: {str(e)}"


AVAILABLE_TOOLS.append(get_guia)


@tool(args_schema=RagQueryInput)
def rag_search(
    query: str,
    asignatura: str = None,
    tipo_documento: str = None,
    top_k: int = None,
) -> Dict[str, Any]:
    """Perform a semantic search against the external RAG service.

    Returns a structured dict with the following shape on success:
      {
        "ok": True,
        "query": <original query>,
        "total_results": <int>,
        "results": [
           {"content": str, "metadata": {...}, "score": float},
           ...
        ]
      }

    On error returns:
      {"ok": False, "error": "..."}
    """
    try:
        logger.debug("rag_search called with query=%s, asignatura=%s, tipo_documento=%s, top_k=%s",
                     query, asignatura, tipo_documento, top_k)
        url = f"{backend_settings.rag_service_url.rstrip('/')}/search"
        payload: Dict[str, Any] = {"query": query}
        if asignatura:
            payload["asignatura"] = asignatura
        if tipo_documento:
            payload["tipo_documento"] = tipo_documento
        if top_k:
            payload["top_k"] = top_k

        logger.debug("Posting to RAG service url=%s payload=%s", url, payload)

        resp = requests.post(url, json=payload, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        logger.debug("RAG service returned data: %s", data)

        # Normalize the provider response into a compact `results` list of
        # {content, metadata, score} entries. Many RAG services return a
        # 'results' list already; if not, try to map commonly used keys.
        raw_results = data.get("results") if isinstance(data, dict) else None
        logger.debug("raw_results type=%s", type(raw_results))
        normalized = []
        if raw_results and isinstance(raw_results, list):
            for r in raw_results:
                # r might be a dict with content/metadata/score or other shape
                if isinstance(r, dict):
                    logger.debug("Processing raw result keys=%s", list(r.keys()))
                    # Prefer explicit fields used by our RAG service
                    content = r.get("content") or r.get("text") or r.get("snippet") or r.get("payload")

                    # metadata may be under different keys depending on vector store
                    metadata = r.get("metadata") or r.get("meta") or r.get("payload_metadata") or {}
                    # Normalize metadata to dict
                    if metadata is None:
                        metadata = {}
                    if not isinstance(metadata, dict):
                        try:
                            metadata = dict(metadata)
                        except Exception:
                            metadata = {"raw": metadata}

                    # Score fields: score, similarity, distance (convert where possible)
                    score = None
                    if "score" in r and r.get("score") is not None:
                        score = r.get("score")
                    elif "similarity" in r and r.get("similarity") is not None:
                        score = r.get("similarity")
                    elif "distance" in r and r.get("distance") is not None:
                        # Some stores return distance where smaller is better; keep raw value
                        score = r.get("distance")

                    # Truncate content for logs if it's large
                    try:
                        content_snip = content[:200] if isinstance(content, str) else str(content)
                    except Exception:
                        content_snip = str(content)
                    logger.debug("Normalized result content=%s score=%s metadata_keys=%s",
                                 content_snip, score, list(metadata.keys()) if isinstance(metadata, dict) else None)

                    normalized.append({"content": content, "metadata": metadata, "score": score})
                else:
                    normalized.append({"content": str(r), "metadata": {}, "score": None})
        else:
            # If the provider returned a flat text or other shape, include it as a single result
            if isinstance(data, dict) and "content" in data:
                normalized.append({"content": data.get("content"), "metadata": data.get("metadata", {}), "score": data.get("score")})
            else:
                normalized.append({"content": str(data), "metadata": {}, "score": None})

        logger.debug("Returning %d normalized results", len(normalized))
        return {
            "ok": True,
            "query": data.get("query") if isinstance(data, dict) else query,
            "total_results": data.get("total_results") if isinstance(data, dict) and data.get("total_results") is not None else len(normalized),
            "results": normalized,
        }
    except requests.exceptions.RequestException as e:
        logger.exception("Error contacting RAG service")
        return {"ok": False, "error": f"Error contacting RAG service: {str(e)}"}
    except Exception as e:
        logger.exception("Unexpected error in rag_search tool")
        return {"ok": False, "error": f"Unexpected error in rag_search tool: {str(e)}"}


AVAILABLE_TOOLS.append(rag_search)


def get_tools():
    """
    Returns a list of all available tools for the agent.
    """
    return AVAILABLE_TOOLS
