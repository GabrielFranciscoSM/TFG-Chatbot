"""Tools for the LangGraph agent.
Contains various tools that can be used by the agent to perform actions.
"""

import logging

from chatbot.logic.tools.guia import get_guia
from chatbot.logic.tools.rag import rag_search
from chatbot.logic.tools.test_gen import generate_test

logger = logging.getLogger(__name__)

# List of all available tools
AVAILABLE_TOOLS: list = [
    get_guia,
    rag_search,
    generate_test,
]


def get_tools():
    """
    Returns a list of all available tools for the agent.
    """
    return AVAILABLE_TOOLS
