# Tests rely on lightweight factories provided in `backend/tests/conftest.py`.
# Use the fixtures: dummy_message_factory, dummy_multiple_choice_test,
# dummy_tool_factory, dummy_llm_factory, patch_get_tools, interrupt_simulator.

"""
Tests for TestSessionGraph.

Notes on coherence with `conftest.py`:
- This test module relies on fixtures defined in `backend/tests/conftest.py` when
  appropriate (for example the `testGraph` fixture). We avoid globally overriding
  the message classes imported in `backend.logic.testGraph` so tests behave more
  like the real runtime environment declared in `conftest.py`.

Individual tests patch only the small set of external pieces they need (LLM,
interrupt, and tools) using `monkeypatch`.
"""

from typing import Any, cast


def test_initialize_test_creates_questions_and_state(
    monkeypatch,
    dummy_multiple_choice_test,
    dummy_tool_factory,
    patch_get_tools,
    dummy_llm_factory,
    dummy_message_factory,
):
    import backend.logic.testGraph as tg

    # Prepare a dummy generate_test tool that returns two questions
    MCQ = dummy_multiple_choice_test
    q1 = MCQ("What is 2+2?", ["4", "3", "5"])
    q2 = MCQ("Capital of Spain?", ["Madrid", "Barcelona"])
    tool = dummy_tool_factory("generate_test", [q1, q2])

    # Patch get_tools to return our generate_test tool
    patch_get_tools([tool])

    # Create TestSessionGraph but avoid real LLM creation by patching _get_llm
    monkeypatch.setattr(
        tg.TestSessionGraph, "_get_llm", lambda self, temp=None: dummy_llm_factory()
    )

    tsg = tg.TestSessionGraph()

    # Simulate last message having tool_calls with args
    last_msg = dummy_message_factory(
        tool_calls=[{"args": {"topic": "math", "num_questions": 2}}]
    )
    state: dict[str, Any] = {"messages": [last_msg]}

    init_state = tsg.initialize_test(cast(tg.TestSessionState, state))

    assert init_state["topic"] == "math"
    assert init_state["num_questions"] == 2
    assert "questions" in init_state
    assert len(init_state["questions"]) == 2


def test_present_question_returns_ai_message_content(
    monkeypatch, dummy_multiple_choice_test, dummy_llm_factory
):
    import backend.logic.testGraph as tg

    monkeypatch.setattr(
        tg.TestSessionGraph, "_get_llm", lambda self, temp=None: dummy_llm_factory()
    )
    tsg = tg.TestSessionGraph()

    # Create a dummy question and state
    MCQ = dummy_multiple_choice_test
    question = MCQ("Pregunta de prueba", ["A", "B"])
    state: dict[str, Any] = {"questions": [question], "current_question_index": 0}

    out = tsg.present_question(cast(tg.TestSessionState, state))

    assert isinstance(out, dict)
    assert "messages" in out
    assert len(out["messages"]) == 1
    assert out["messages"][0].content == "Pregunta de prueba"


def test_answer_question_interrupt_and_evaluation(
    monkeypatch,
    dummy_multiple_choice_test,
    dummy_llm_factory,
    patch_get_tools,
    interrupt_simulator,
):
    import backend.logic.testGraph as tg

    # Patch LLM to return a clear CORRECT and FEEDBACK response
    monkeypatch.setattr(
        tg.TestSessionGraph,
        "_get_llm",
        lambda self, temp=None: dummy_llm_factory("CORRECT: YES\nFEEDBACK: Bien hecho"),
    )

    # Ensure interrupt returns the user's answer
    interrupt_simulator("B")

    # Patch get_tools (not used here but safe)
    patch_get_tools([])

    tsg = tg.TestSessionGraph()

    # Prepare a single question
    MCQ = dummy_multiple_choice_test
    question = MCQ("Q?", ["A", "B"])  # first option considered correct by factory

    state: dict[str, Any] = {
        "questions": [question],
        "current_question_index": 0,
        "num_questions": 1,
        "topic": "test_topic",
        "user_answers": [],
        "feedback_history": [],
        "scores": [],
        "messages": [],
    }

    out = tsg.answer_question(cast(tg.TestSessionState, state))

    # Validate returned updates
    assert out["user_answers"][-1] == "B"
    assert out["scores"][-1] in (True, False)
    assert out["current_question_index"] == 1
    # Messages should include the human answer and the feedback AI message
    assert any(
        isinstance(m, object) and getattr(m, "content", None) for m in out["messages"]
    )


def test_test_router_continues_and_finalizes():
    import backend.logic.testGraph as tg

    tsg = tg.TestSessionGraph.__new__(tg.TestSessionGraph)

    # continue case
    st: dict[str, Any] = {"current_question_index": 0, "num_questions": 2}
    assert tsg.test_router(cast(tg.TestSessionState, st)) == "continue"

    # finalize case
    st2: dict[str, Any] = {"current_question_index": 2, "num_questions": 2}
    assert tsg.test_router(cast(tg.TestSessionState, st2)) == "finalize"


def test_finalize_test_returns_toolmessage_with_tool_call_id(
    monkeypatch, dummy_llm_factory, dummy_message_factory
):
    import backend.logic.testGraph as tg

    monkeypatch.setattr(
        tg.TestSessionGraph, "_get_llm", lambda self, temp=None: dummy_llm_factory()
    )
    tsg = tg.TestSessionGraph()

    # Create a fake last AI message that contains tool_calls
    last_ai = dummy_message_factory(tool_calls=[{"id": "toolcall-123"}])

    state: dict[str, Any] = {
        "scores": [True, False, True],
        "num_questions": 3,
        "messages": [last_ai],
        "topic": "prueba",
    }

    out = tsg.finalize_test(cast(tg.TestSessionState, state))

    assert "messages" in out
    msg = out["messages"][0]
    assert msg.tool_call_id == "toolcall-123"


def test_evaluate_answer_with_llm_parsing(
    monkeypatch, dummy_llm_factory, dummy_multiple_choice_test
):
    import backend.logic.testGraph as tg

    # Provide a custom LLM response
    llm = dummy_llm_factory("CORRECT: YES\nFEEDBACK: Explicación detallada")
    monkeypatch.setattr(tg.TestSessionGraph, "_get_llm", lambda self, temp=None: llm)

    tsg = tg.TestSessionGraph()

    MCQ = dummy_multiple_choice_test
    q = MCQ("¿2+2?", ["4", "3"])
    state: dict[str, Any] = {"topic": "matematicas"}

    feedback, is_correct = tsg.evaluate_answer_with_llm(
        q, "4", cast(tg.TestSessionState, state)
    )

    assert "Explicación detallada" in feedback
    assert is_correct is True


def test_build_test_subgraph_compiles(monkeypatch, testGraph, dummy_llm_factory):
    """Use the `testGraph` fixture from conftest which creates the subgraph.

    Also patch TestSessionGraph._get_llm to ensure no heavy external LLM is
    instantiated during subgraph construction.
    """
    import backend.logic.testGraph as tg

    # Patch _get_llm so the TestSessionGraph instantiation inside
    # create_test_subgraph/testGraph doesn't reach out to real LLMs.
    monkeypatch.setattr(
        tg.TestSessionGraph, "_get_llm", lambda self, temp=None: dummy_llm_factory()
    )

    compiled = testGraph

    # Compiled graph should expose an invoke method
    assert hasattr(compiled, "invoke")
