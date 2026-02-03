"""Tool for retrieving teaching guides (guías docentes)."""

import json
import logging

from langchain.tools import tool

from chatbot.db.mongo import MongoDBClient
from chatbot.logic.models import SubjectDataKey, SubjectLookupInput
from chatbot.logic.tools.utils import navigate_nested_dict

logger = logging.getLogger(__name__)


def _build_guia_summary(doc: dict) -> dict:
    """Build a short summary of a guia document.

    Args:
        doc: The complete guia document

    Returns:
        Dictionary with key summary fields
    """
    return {
        "subject": doc.get("subject"),
        "asignatura": doc.get("asignatura"),
        "grado": doc.get("grado"),
        "curso": doc.get("curso"),
        "url": doc.get("url"),
        "brief_description": doc.get("breve_descripción_de_contenidos", [])[:3],
    }


@tool(args_schema=SubjectLookupInput)
def get_guia(
    asignatura: str | None = None,
    key: SubjectDataKey | None = None,
) -> str:
    """Retrieve a stored guia document for the agent's current `asignatura` state.

    Args:
        asignatura: The subject identifier to look up
        key: Optional specific key to retrieve from the document

    Returns:
        JSON string with guia data or error message
    """
    try:
        if not asignatura:
            return "No guia found for subject"

        client = MongoDBClient()
        client.connect()
        doc = client.find_by_subject("guias", asignatura)
        client.close()

        if not doc:
            return f"No guia found for subject: {asignatura}"

        # If a specific key is requested, navigate to it
        if key:
            value = navigate_nested_dict(doc, key.value)
            if value is None:
                return f"Key '{key.value}' not present in guia for subject {asignatura}"
            return json.dumps(value, ensure_ascii=False)

        # Otherwise, return a short summary
        summary = _build_guia_summary(doc)
        return json.dumps(summary, ensure_ascii=False)

    except Exception as e:
        logger.error("Error retrieving guia: %s", str(e))
        return f"Error retrieving guia: {str(e)}"
