import pytest
from langchain_core.messages import HumanMessage, AIMessage

@pytest.mark.integration
def test_graph_with_vllm_container(graph,graph_config):
    input_state = {
        "messages": [HumanMessage(content="hello, how are you?")]
    }

    result = graph.invoke(input_state,config=graph_config)
    assert "messages" in result
    assert len(result["messages"]) >= 2
    last_msg = result["messages"][-1]
    assert isinstance(last_msg, AIMessage)


@pytest.mark.integration
def test_graph_with_vllm_container_tools(graph,graph_config):
    input_state = {
        "messages": [HumanMessage(content="How much is is 2 + 2?")]
    }
    result = graph.invoke(input_state,config=graph_config)
    assert "messages" in result
    assert len(result["messages"]) >= 3
    last_msg = result["messages"][-1]
    assert isinstance(last_msg, AIMessage)
    assert "4" in last_msg.content

@pytest.mark.integration
def test_graph_with_memory(graph, graph_config):
    # First interaction
    input_state_1 = {
        "messages": [HumanMessage(content="My name is Alice")]
    }
    result_1 = graph.invoke(input_state_1, config=graph_config)
    assert "messages" in result_1
    assert isinstance(result_1["messages"][-1], AIMessage)
    
    # Second interaction - check if it remembers
    input_state_2 = {
        "messages": [HumanMessage(content="What is my name?")]
    }
    result_2 = graph.invoke(input_state_2, config=graph_config)
    assert "messages" in result_2
    last_msg = result_2["messages"][-1]
    assert isinstance(last_msg, AIMessage)
    assert "Alice" in last_msg.content
@pytest.mark.integration
def test_graph_empty_message(graph, graph_config):
    input_state = {
        "messages": [HumanMessage(content="")]
    }
    result = graph.invoke(input_state, config=graph_config)
    assert "messages" in result
    assert isinstance(result["messages"][-1], AIMessage)

@pytest.mark.integration
def test_graph_with_complex_calculation(graph, graph_config):
    input_state = {
        "messages": [HumanMessage(content="Calcula (15 * 3) + (20 / 4)")]
    }
    result = graph.invoke(input_state, config=graph_config)
    assert "messages" in result
    last_msg = result["messages"][-1]
    assert isinstance(last_msg, AIMessage)
    assert "50" in last_msg.content
