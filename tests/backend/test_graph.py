import pytest
from langchain_core.messages import HumanMessage, AIMessage
from backend.logic.graph import build_graph, think
from unittest.mock import MagicMock, patch
from backend.logic.graph import build_graph

def test_build_graph():
    """Test that the graph builds without errors."""
    graph = build_graph()
    assert graph is not None

@patch('backend.logic.graph.ChatOpenAI')
def test_think_node(mock_openai, mock_llm_response):
    """Test the think node returns a proper response."""
    # Configure the mock to return our AIMessage
    mock_instance = MagicMock()
    mock_instance.bind_tools.return_value.invoke.return_value = mock_llm_response
    mock_openai.return_value = mock_instance
    
    # Create initial state
    state = {
        "messages": [HumanMessage(content="Hello")]
    }
    
    # Call think node
    result = think(state)
    
    # Verify the result
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert result["messages"][0].content == "Test response"

@patch('backend.logic.graph.ChatOpenAI')
def test_graph_execution(mock_openai,graph,graph_config, mock_llm_response):
    """Test that the graph executes successfully."""
    # Configure the mock to return our AIMessage
    mock_instance = MagicMock()
    mock_instance.bind_tools.return_value.invoke.return_value = mock_llm_response
    mock_openai.return_value = mock_instance
        
    # Execute graph
    result = graph.invoke(
        {"messages": [HumanMessage(content="Hello")]},
        config=graph_config
        )
    
    # Verify result
    assert "messages" in result
    assert len(result["messages"]) >= 2  # At least input + output
    # The last message should be from the agent
    assert isinstance(result["messages"][-1], AIMessage)

@patch('backend.logic.graph.ChatOpenAI')
def test_graph_with_tool_calls(mock_openai,graph,graph_config, mock_llm_with_tools, mock_llm_response):
    """Test graph execution when tools are called."""
    # Configure mock to first return tool call, then final response
    mock_instance = MagicMock()
    mock_bound = MagicMock()
    mock_bound.invoke.side_effect = [mock_llm_with_tools, mock_llm_response]
    mock_instance.bind_tools.return_value = mock_bound
    mock_openai.return_value = mock_instance
            
    # Execute graph with a query that should trigger tools
    result = graph.invoke(
        {"messages": [HumanMessage(content="Search for Python tutorials")]},
        config=graph_config
    )
    
    # Verify result
    assert "messages" in result
    assert len(result["messages"]) >= 2


