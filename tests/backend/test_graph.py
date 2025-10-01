import pytest
from langchain_core.messages import HumanMessage, AIMessage
from backend.logic.graph import build_graph, think


def test_build_graph():
    """Test that the graph is built correctly"""
    graph = build_graph()
    assert graph is not None
    # Verify that the graph has the expected structure
    assert hasattr(graph, "invoke")

def test_think_node(mock_chat_openai):
    """Test the think node with a mocked LLM"""
    # Prepare test input
    test_message = HumanMessage(content="Test question")
    state = {"messages": [test_message]}

    # Call the think function
    result = think(state)

    # Verify the response structure
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert result["messages"][0].content == "Test response"

    # Verify that the LLM was called with the correct messages
    mock_chat_openai.return_value.invoke.assert_called_once_with([test_message])

def test_graph_execution(mock_chat_openai):
    """Test the full graph execution"""
    graph = build_graph()
    
    # Prepare test input
    test_message = HumanMessage(content="Test question")
    
    # Execute the graph
    result = graph.invoke({
        "messages": [test_message]
    })
    
    # Verify the result structure
    assert "messages" in result
    assert len(result["messages"]) > 0
    assert isinstance(result["messages"][-1], AIMessage)
    assert result["messages"][-1].content == "Test response"
