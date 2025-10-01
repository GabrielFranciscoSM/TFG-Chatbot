import pytest
from langchain_core.messages import HumanMessage, AIMessage
from backend.logic.graph import build_graph
from backend.logic.graph import build_graph

@pytest.mark.integration
def test_graph_with_vllm_container():
    graph = build_graph()
    input_state = {
        "messages": [HumanMessage(content="hello, how are you?")]
    }
    result = graph.invoke(input_state)
    assert "messages" in result
    assert len(result["messages"]) >= 2
    last_msg = result["messages"][-1]
    assert isinstance(last_msg, AIMessage)


@pytest.mark.integration
def test_graph_with_vllm_container_tools():
    graph = build_graph()
    input_state = {
        "messages": [HumanMessage(content="How much is is 2 + 2?")]
    }
    result = graph.invoke(input_state)
    assert "messages" in result
    assert len(result["messages"]) >= 3
    last_msg = result["messages"][-1]
    assert isinstance(last_msg, AIMessage)
    assert "4" in last_msg.content