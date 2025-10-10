""" Tools for the LangGraph agent.
Contains various tools that can be used by the agent to perform actions.
"""

from langchain_core.tools import tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from backend.logic.models import WebSearchInput, CalculatorInput

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


def get_tools():
    """
    Returns a list of all available tools for the agent.
    """
    return AVAILABLE_TOOLS
