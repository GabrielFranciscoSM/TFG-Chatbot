"""
Tools for the LangGraph agent.
Contains various tools that can be used by the agent to perform actions.
"""

from langchain_core.tools import tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


@tool
def web_search(query: str) -> str:
    """
    Search the web for information using DuckDuckGo.
    
    Args:
        query: The search query string
        
    Returns:
        A string containing the search results
    """
    try:
        search = DuckDuckGoSearchAPIWrapper()
        results = search.run(query)
        return results
    except Exception as e:
        return f"Error performing web search: {str(e)}"


@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "5 * 3")
        
    Returns:
        The result of the calculation as a string
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
    
    Returns:
        List of tool objects
    """
    return AVAILABLE_TOOLS
