"""
Test session subgraph for interactive question-answer sessions.

This module implements a LangGraph subgraph that manages interactive test/quiz
sessions with human-in-the-loop interrupts. It allows the chatbot to:

- Present questions one at a time
- Wait for user responses at each question
- Evaluate answers and provide immediate feedback
- Track progress through the test session
- Provide final scores and results

Architecture:
    The test session uses a separate subgraph that integrates with the main
    GraphAgent. It implements an interrupt-driven flow:

    Flow:
        generate_test (parent) -> test_session (subgraph)
                                          ↓
                                   present_question
                                          ↓
                                   **INTERRUPT** (wait for user)
                                          ↓
                                   evaluate_answer (on resume)
                                          ↓
                                   should_continue?
                                    /           \
                            next question     provide_summary

    State Management:
        The subgraph shares state with the parent graph, allowing seamless
        communication of test data (questions, scores, user answers).

Key Features:
    - **Human-in-the-loop**: Interrupts for each question
    - **Immediate Feedback**: Evaluates and explains answers
    - **Progress Tracking**: Maintains question index and score
    - **LLM Evaluation**: Uses LLM to assess answer correctness
    - **Final Summary**: Provides complete test results

Example:
    # Test session is invoked automatically by the main agent
    # when user requests a test. The flow:

    1. User: "Quiero un test de Docker"
    2. Agent calls generate_test tool -> creates questions
    3. Agent enters test_session subgraph
    4. Subgraph presents question 1 and interrupts
    5. User provides answer via /resume_chat
    6. Subgraph evaluates, presents question 2, interrupts again
    7. Process repeats until all questions answered
    8. Final summary provided
"""

import os
from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.types import interrupt

from backend.logic.models import MultipleChoiceTest

load_dotenv()


class TestSessionState(MessagesState):
    """
    State schema for the test session subgraph.

    This state is SHARED with the parent SubjectState. All fields defined here
    are accessible and modifiable by both the test subgraph and the parent graph.
    This allows seamless communication of test data between graphs.

    Attributes:
        messages: Conversation messages (inherited from MessagesState)
        topic: Test topic/theme
        num_questions: Total number of questions in the test
        difficulty: Difficulty level (easy/medium/hard)
        questions: List of generated MultipleChoiceTest questions
        current_question_index: Index of the current question being presented
        user_answers: List of answers provided by the user
        feedback_history: Feedback messages for each answer
        scores: Boolean list indicating correct (True) or incorrect (False) answers
    """

    # These fields are shared with parent SubjectState
    topic: str
    num_questions: int
    difficulty: str | None
    questions: list[MultipleChoiceTest]
    current_question_index: int
    user_answers: list[str]
    feedback_history: list[str]
    scores: list[bool]
    # messages is inherited from MessagesState (shared with parent)


class TestSessionGraph:
    """
    Test session subgraph manager.

    This class encapsulates the logic for interactive test sessions, including:
    - Presenting questions sequentially
    - Interrupting for user input
    - Evaluating answers using LLM
    - Tracking progress and scores
    - Providing final results

    The subgraph is designed to be invoked by the main GraphAgent when a test
    session is initiated. It maintains its own flow but shares state with the
    parent graph for seamless integration.

    Design Decisions:
        - Separate subgraph for clean separation of concerns
        - Shared state with parent for easy data access
        - LLM-based evaluation for flexible answer assessment
        - Interrupt-based flow for true interactive experience
    """

    def __init__(
        self,
        *,
        llm_provider: Literal["vllm", "gemini"] = "vllm",
        vllm_url: str | None = None,
        model_name: str | None = None,
        openai_api_key: str = "EMPTY",
        gemini_api_key: str | None = None,
        gemini_model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
    ):
        """Initialize with LLM configuration for answer evaluation.

        Args:
            llm_provider: Either "vllm" (local vLLM) or "gemini" (Google Gemini)
            vllm_url: URL for vLLM service (only for vllm provider)
            model_name: Model name (only for vllm provider)
            openai_api_key: API key for vLLM OpenAI-compatible endpoint
            gemini_api_key: Google Gemini API key (only for gemini provider)
            gemini_model: Gemini model name (default: gemini-1.5-flash)
            temperature: LLM temperature
        """
        self.llm_provider = llm_provider
        self.temperature = temperature

        # vLLM configuration
        vllm_port = os.getenv("VLLM_MAIN_PORT", "8000")
        vllm_host = os.getenv("VLLM_HOST", "vllm-openai")
        self.vllm_url = vllm_url or f"http://{vllm_host}:{vllm_port}/v1"
        self.model_name = model_name or os.getenv(
            "MODEL_PATH", "/models/HuggingFaceTB--SmolLM2-1.7B-Instruct"
        )
        self.openai_api_key = openai_api_key

        # Gemini configuration
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.gemini_model = gemini_model
        if self.gemini_api_key:
            os.environ["GOOGLE_API_KEY"] = self.gemini_api_key

        # Initialize LLM for answer evaluation
        self.llm = self._get_llm()

    def _get_llm(self, temperature: float | None = None):
        """Get configured LLM instance based on provider.

        Args:
            temperature: Override temperature (uses instance default if None)

        Returns:
            Configured LLM instance (ChatOpenAI or ChatGoogleGenerativeAI)
        """
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_openai import ChatOpenAI

        temp = temperature if temperature is not None else self.temperature

        if self.llm_provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError(
                    "GEMINI_API_KEY not found. Set it in .env or pass gemini_api_key parameter."
                )
            return ChatGoogleGenerativeAI(
                model=self.gemini_model,
                google_api_key=self.gemini_api_key,
                temperature=temp,
            )
        else:  # vllm
            return ChatOpenAI(
                model=self.model_name,
                openai_api_key=self.openai_api_key,
                openai_api_base=self.vllm_url,
                temperature=temp,
            )

    def initialize_test(self, state: TestSessionState):
        """Entry point: Extract tool call args and generate questions.

        This node:
        1. Reads last message's tool_calls from parent state
        2. Generates all questions using generate_test tool
        3. Initializes test tracking fields
        """
        from backend.logic.tools.tools import get_tools

        tools = get_tools()
        generate_test_tool = next((t for t in tools if t.name == "generate_test"), None)

        if generate_test_tool is None:
            raise ValueError("generate_test tool not found")

        messages = state["messages"]
        last_message = messages[-1]
        tool_calls = getattr(last_message, "tool_calls", [])

        if not tool_calls:
            return {}

        args = tool_calls[0]["args"]

        # Generate ALL questions upfront
        questions = generate_test_tool.invoke(args)

        # Initialize test session state
        return {
            "topic": args["topic"],
            "num_questions": args.get("num_questions", 5),
            "difficulty": args.get("difficulty"),
            "questions": questions if isinstance(questions, list) else [questions],
            "current_question_index": 0,
            "user_answers": [],
            "feedback_history": [],
            "scores": [],
        }

    def present_question(self, state: TestSessionState):
        """Format and present the current question.

        Note: We don't add messages here - the question will be shown
        in the interrupt payload, not saved to conversation history.
        """
        idx = state.get("current_question_index", 0)
        questions = state.get("questions", [])

        # Safety check: ensure we have questions and valid index
        if not questions:
            print(f"ERROR: No questions in state! State keys: {state.keys()}")
            # Force finalization by returning empty - router will handle
            return {}

        if idx >= len(questions):
            print(f"ERROR: Index {idx} out of range for {len(questions)} questions")
            # This might happen if state is inconsistent - let router decide
            return {}

        question = questions[idx]

        # Extract question text depending on structure
        if isinstance(question, MultipleChoiceTest):
            question_text = question.question.question_text
        elif isinstance(question, dict):
            question_text = question.get("question", {}).get(
                "question_text", "Question"
            )
        else:
            question_text = str(question)

        return {"messages": [AIMessage(content=question_text)]}

    def answer_question(self, state: TestSessionState):
        """Wait for user answer, then evaluate it.

        This is where the INTERRUPT happens!
        The question is shown in the interrupt payload, not saved to messages.
        Only feedback is saved to conversation history.
        """
        idx = state.get("current_question_index", 0)
        questions = state.get("questions", [])

        # Safety check - if error, force finalization
        if not questions or idx >= len(questions):
            print(
                f"ERROR in answer_question: idx={idx}, len(questions)={len(questions)}"
            )
            # Force the session to end by setting index to num_questions
            num_questions = state.get("num_questions", len(questions))
            return {
                "current_question_index": num_questions,
                "messages": [
                    AIMessage(
                        content="⚠️ Error en la sesión de preguntas. Finalizando..."
                    )
                ],
            }

        current_q = questions[idx]

        # Extract question text for interrupt payload
        if isinstance(current_q, MultipleChoiceTest):
            question_text = current_q.question.question_text
        elif isinstance(current_q, dict):
            question_text = current_q.get("question", {}).get(
                "question_text", "Question"
            )
        else:
            question_text = str(current_q)

        # INTERRUPT: Wait for user's answer
        # The question appears here in the payload, NOT in messages
        interrupt_payload = {
            "action": "answer_question",
            "question_num": idx + 1,
            "total_questions": state.get("num_questions", len(questions)),
            "question_text": question_text,
        }

        user_answer = interrupt(interrupt_payload)

        # When resumed: evaluate the answer using LLM
        feedback, is_correct = self.evaluate_answer_with_llm(
            current_q, user_answer, state
        )

        # Update progress
        updated_answers = state.get("user_answers", []) + [user_answer]
        updated_feedback = state.get("feedback_history", []) + [feedback]
        updated_scores = state.get("scores", []) + [is_correct]
        updated_index = idx + 1

        # Format feedback message - THIS is saved to messages
        emoji = "✅" if is_correct else "❌"
        feedback_msg = f"""{emoji} {feedback}

Progreso: {updated_index}/{state.get("num_questions", len(questions))} completadas"""

        return {
            "user_answers": updated_answers,
            "feedback_history": updated_feedback,
            "scores": updated_scores,
            "current_question_index": updated_index,
            "messages": [
                HumanMessage(content=user_answer),
                AIMessage(content=feedback_msg),
            ],
        }

    def test_router(self, state: TestSessionState):
        """Route to next question or finalize."""
        current_idx = state.get("current_question_index", 0)
        num_questions = state.get("num_questions", 0)

        if current_idx < num_questions:
            return "continue"
        else:
            return "finalize"

    def finalize_test(self, state: TestSessionState):
        """Generate final summary and score, return as ToolMessage."""
        scores = state.get("scores", [])
        score = sum(scores)
        total = state.get("num_questions", len(scores))
        percentage = (score / total) * 100 if total > 0 else 0

        # Get tool_call_id from the original tool call
        messages = state.get("messages", [])
        last_ai_message = next(
            (
                m
                for m in reversed(messages)
                if hasattr(m, "tool_calls") and m.tool_calls
            ),
            None,
        )
        tool_call_id = (
            last_ai_message.tool_calls[0]["id"] if last_ai_message else "unknown"
        )

        topic = state.get("topic", "este tema")
        summary = f"""🎓 ¡Sesión de repaso completada!

Puntuación: {score}/{total} ({percentage:.0f}%)

¡Excelente trabajo repasando {topic}!"""

        return {"messages": [ToolMessage(content=summary, tool_call_id=tool_call_id)]}

    def evaluate_answer_with_llm(
        self, question: MultipleChoiceTest, user_answer: str, state: TestSessionState
    ) -> tuple[str, bool]:
        """Evaluate user's answer using the LLM.

        Args:
            question: The question being answered
            user_answer: User's free-text answer
            state: Current test session state

        Returns:
            Tuple of (feedback_text, is_correct)
        """
        from backend.logic.prompts import TEST_EVALUATION_PROMPT

        # Extract question details
        if isinstance(question, MultipleChoiceTest):
            question_text = question.question.question_text
            # Get correct answer(s) from options
            correct_answers = (
                [opt.answer_text for opt in question.options if opt.is_correct]
                if question.options
                else []
            )
        elif isinstance(question, dict):
            question_text = question.get("question", {}).get("question_text", "")
            correct_answers = []
        else:
            question_text = str(question)
            correct_answers = []

        # Build evaluation prompt using template
        correct_answer_hint = (
            f"Correct Answer(s): {', '.join(correct_answers)}"
            if correct_answers
            else ""
        )

        evaluation_prompt = TEST_EVALUATION_PROMPT.format(
            topic=state["topic"],
            question_text=question_text,
            user_answer=user_answer,
            correct_answer_hint=correct_answer_hint,
        )

        try:
            response = self.llm.invoke(evaluation_prompt)
            response_text = (
                response.content if hasattr(response, "content") else str(response)
            )

            # Parse response
            is_correct = "CORRECT: YES" in response_text.upper()

            # Extract feedback
            if "FEEDBACK:" in response_text:
                feedback = response_text.split("FEEDBACK:")[1].strip()
            else:
                feedback = response_text

            return feedback, is_correct

        except Exception:
            # Fallback evaluation
            return f"Recibí tu respuesta: '{user_answer}'. ¡Continuemos!", True

    def build_test_subgraph(self):
        """Build the test session subgraph.

        This subgraph is added directly as a node in the parent graph.
        It shares state keys with parent via TestSessionState (extends MessagesState).

        Returns:
            Compiled subgraph ready to be added as a node to parent graph
        """
        subgraph_builder = StateGraph(TestSessionState)

        # Add nodes - NOW includes initialization as entry point
        subgraph_builder.add_node("initialize_test", self.initialize_test)
        subgraph_builder.add_node("present_question", self.present_question)
        subgraph_builder.add_node("answer_question", self.answer_question)
        subgraph_builder.add_node("finalize", self.finalize_test)

        # Define flow - START with initialization
        subgraph_builder.set_entry_point("initialize_test")
        subgraph_builder.add_edge("initialize_test", "present_question")
        subgraph_builder.add_edge("present_question", "answer_question")
        subgraph_builder.add_conditional_edges(
            "answer_question",
            self.test_router,
            {"continue": "present_question", "finalize": "finalize"},
        )
        subgraph_builder.add_edge("finalize", END)

        # NO checkpointer - parent propagates it automatically when added as node
        return subgraph_builder.compile()


# Factory function for easy instantiation
def create_test_subgraph(**kwargs):
    """Create and return a compiled test session subgraph.

    Args:
        **kwargs: Optional LLM configuration parameters

    Returns:
        Compiled StateGraph for test sessions
    """
    graph_instance = TestSessionGraph(**kwargs)
    return graph_instance.build_test_subgraph()
