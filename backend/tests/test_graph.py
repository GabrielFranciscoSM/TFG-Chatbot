import pytest
from langchain_core.messages import HumanMessage, AIMessage
from backend.logic.graph import GraphAgent
from unittest.mock import MagicMock, patch

def test_build_graph():
    """Test that the graph builds without errors."""
    agent = GraphAgent()
    graph = agent.build_graph()
    assert graph is not None

@patch('logic.graph.ChatOpenAI')
def test_graph_execution(mock_openai, graph, graph_config, mock_llm_response):
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

@patch('logic.graph.ChatOpenAI')
def test_graph_with_tool_calls(mock_openai, graph, graph_config, mock_llm_with_tools, mock_llm_response):
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

@patch('logic.graph.ChatOpenAI')
def test_call_agent_method(mock_openai, mock_llm_response):
    """Test the call_agent convenience method."""
    # Configure the mock to return our AIMessage
    mock_instance = MagicMock()
    mock_instance.bind_tools.return_value.invoke.return_value = mock_llm_response
    mock_openai.return_value = mock_instance
    
    # Create agent instance
    agent = GraphAgent()
    
    # Call agent with query and id
    result = agent.call_agent(query="Hello, how are you?", id="test-user-123")
    
    # Verify result
    assert "messages" in result
    assert len(result["messages"]) >= 2  # At least input + output
    assert isinstance(result["messages"][-1], AIMessage)


