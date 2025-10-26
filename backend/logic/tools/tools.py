""" Tools for the LangGraph agent.
Contains various tools that can be used by the agent to perform actions.
"""

from langchain_core.tools import tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from backend.logic.models import WebSearchInput, CalculatorInput, GetSubjectDataInput, SubjectDataKey
from backend.logic.models import SubjectLookupInput
from backend.db.mongo import MongoDBClient
from langgraph.prebuilt import InjectedState
from typing import Annotated, Optional
import json

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


@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    """
    try:
        # Using eval with restricted globals for safety
        allowed_names = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow, "len": len
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

# List of all available tools
AVAILABLE_TOOLS = [web_search, calculator]


@tool(args_schema=SubjectLookupInput)
def get_guia(
    key: SubjectDataKey = None,
    asignatura_state: Annotated[Optional[str], InjectedState("asignatura")] = None,
) -> str:
    """Retrieve a stored guia document for the agent's current `asignatura` state.

    The agent should place the subject into its injected state `asignatura`.
    This function reads the injected `asignatura` via `InjectedState("asignatura")`.
    If no asignatura is present the tool returns a helpful error message.
    """
    try:

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


def get_tools():
    """
    Returns a list of all available tools for the agent.
    """
    return AVAILABLE_TOOLS
