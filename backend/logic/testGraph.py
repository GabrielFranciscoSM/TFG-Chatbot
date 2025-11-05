"""Test session subgraph for interactive question-answer sessions.

This module defines a separate subgraph for managing test/quiz sessions
with human-in-the-loop interrupts for each question.
"""

from typing import TypedDict, List, Optional, Tuple
from backend.logic.models import MultipleChoiceTest, Question
from langchain_core.messages import AIMessage
from langgraph.types import interrupt
from langgraph.graph import StateGraph, START, END
import os
from dotenv import load_dotenv

load_dotenv()


class TestSessionState(TypedDict):
    """Private state for the test session subgraph.
    
    This state is NOT shared with the parent graph.
    Only this subgraph can see and modify these fields.
    """
    # Initial params
    topic: str
    num_questions: int
    difficulty: Optional[str]
    
    # Generated content (all questions pre-generated)
    questions: List[MultipleChoiceTest]
    
    # Progress tracking
    current_question_index: int  # 0-indexed
    user_answers: List[str]
    feedback_history: List[str]
    scores: List[bool]  # True = correct, False = incorrect
    
    # Messages for communication (transforms back to parent)
    messages: List  # Shared key with parent!


class TestSessionGraph:
    """Encapsulates the test session subgraph logic."""
    
    def __init__(self, *, vllm_url: str | None = None, model_name: str | None = None,
                 openai_api_key: str = "EMPTY", temperature: float = 0.7):
        """Initialize with LLM configuration for answer evaluation."""
        from langchain_openai import ChatOpenAI
        
        vllm_port = os.getenv("VLLM_MAIN_PORT", "8000")
        vllm_host = os.getenv("VLLM_HOST", "vllm-openai")
        
        self.vllm_url = vllm_url or f"http://{vllm_host}:{vllm_port}/v1"
        self.model_name = model_name or os.getenv(
            "MODEL_PATH", "/models/HuggingFaceTB--SmolLM2-1.7B-Instruct"
        )
        self.openai_api_key = openai_api_key
        self.temperature = temperature
        
        # Initialize LLM for answer evaluation
        self.llm = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.openai_api_key,
            openai_api_base=self.vllm_url,
            temperature=self.temperature,
        )
    
    def start_test_session(self, state: TestSessionState):
        """Generate all questions and initialize test state."""
        from backend.logic.tools.tools import get_tools
        
        tools = get_tools()
        generate_test_tool = next(
            (t for t in tools if t.name == "generate_test"), None
        )
        
        if generate_test_tool is None:
            raise ValueError("generate_test tool not found")
        
        # Generate ALL questions upfront
        args = {
            "topic": state["topic"],
            "num_questions": state["num_questions"],
            "difficulty": state.get("difficulty")
        }
        questions = generate_test_tool.invoke(args)
        
        # Initialize state
        return {
            "questions": questions if isinstance(questions, list) else [questions],
            "current_question_index": 0,
            "user_answers": [],
            "feedback_history": [],
            "scores": [],
            "messages": [AIMessage(content=f"¡Iniciando sesión de repaso sobre {state['topic']}!")]
        }

    def present_question(self, state: TestSessionState):
        """Format and present the current question."""
        idx = state["current_question_index"]
        question = state["questions"][idx]
        
        # Extract question text depending on structure
        if isinstance(question, MultipleChoiceTest):
            question_text = question.question.question_text
        elif isinstance(question, dict):
            question_text = question.get("question", {}).get("question_text", "Question")
        else:
            question_text = str(question)
        
        msg = f"""📝 Pregunta {idx + 1}/{state['num_questions']}

{question_text}

Por favor, proporciona tu respuesta."""
        
        return {"messages": [AIMessage(content=msg)]}

    def answer_question(self, state: TestSessionState):
        """Wait for user answer, then evaluate it.
        
        This is where the INTERRUPT happens!
        """
        idx = state["current_question_index"]
        current_q = state["questions"][idx]
        
        # Extract question text for interrupt payload
        if isinstance(current_q, MultipleChoiceTest):
            question_text = current_q.question.question_text
        elif isinstance(current_q, dict):
            question_text = current_q.get("question", {}).get("question_text", "Question")
        else:
            question_text = str(current_q)
        
        # INTERRUPT: Wait for user's answer
        interrupt_payload = {
            "action": "answer_question",
            "question_num": idx + 1,
            "total_questions": state["num_questions"],
            "question_text": question_text
        }
        
        user_answer = interrupt(interrupt_payload)
        
        # When resumed: evaluate the answer using LLM
        feedback, is_correct = self.evaluate_answer_with_llm(
            current_q, user_answer, state
        )
        
        # Update progress
        updated_answers = state["user_answers"] + [user_answer]
        updated_feedback = state["feedback_history"] + [feedback]
        updated_scores = state["scores"] + [is_correct]
        updated_index = idx + 1
        
        # Format feedback message
        emoji = "✅" if is_correct else "❌"
        feedback_msg = f"""{emoji} {feedback}

Progreso: {updated_index}/{state['num_questions']} completadas"""
        
        return {
            "user_answers": updated_answers,
            "feedback_history": updated_feedback,
            "scores": updated_scores,
            "current_question_index": updated_index,
            "messages": [AIMessage(content=feedback_msg)]
        }

    def test_router(self, state: TestSessionState):
        """Route to next question or finalize."""
        if state["current_question_index"] < state["num_questions"]:
            return "continue"
        else:
            return "finalize"

    def finalize_test(self, state: TestSessionState):
        """Generate final summary and score."""
        score = sum(state["scores"])
        total = state["num_questions"]
        percentage = (score / total) * 100
        
        summary = f"""🎓 ¡Sesión de repaso completada!

Puntuación: {score}/{total} ({percentage:.0f}%)

¡Excelente trabajo repasando {state['topic']}!"""
        
        return {"messages": [AIMessage(content=summary)]}
    
    def evaluate_answer_with_llm(
        self, 
        question: MultipleChoiceTest, 
        user_answer: str,
        state: TestSessionState
    ) -> Tuple[str, bool]:
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
            correct_answers = [
                opt.answer_text for opt in question.options 
                if opt.is_correct
            ] if question.options else []
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
            topic=state['topic'],
            question_text=question_text,
            user_answer=user_answer,
            correct_answer_hint=correct_answer_hint
        )

        try:
            response = self.llm.invoke(evaluation_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response
            is_correct = "CORRECT: YES" in response_text.upper()
            
            # Extract feedback
            if "FEEDBACK:" in response_text:
                feedback = response_text.split("FEEDBACK:")[1].strip()
            else:
                feedback = response_text
            
            return feedback, is_correct
            
        except Exception as e:
            # Fallback evaluation
            return f"Recibí tu respuesta: '{user_answer}'. ¡Continuemos!", True

    def build_test_subgraph(self):
        """Build the test session subgraph with private state.
        
        Returns:
            Compiled subgraph ready to be invoked by parent graph
        """
        subgraph_builder = StateGraph(TestSessionState)
        
        # Add nodes
        subgraph_builder.add_node("start_session", self.start_test_session)
        subgraph_builder.add_node("present_question", self.present_question)
        subgraph_builder.add_node("answer_question", self.answer_question)
        subgraph_builder.add_node("finalize", self.finalize_test)
        
        # Define flow
        subgraph_builder.set_entry_point("start_session")
        subgraph_builder.add_edge("start_session", "present_question")
        subgraph_builder.add_edge("present_question", "answer_question")
        subgraph_builder.add_conditional_edges(
            "answer_question",
            self.test_router,
            {
                "continue": "present_question",
                "finalize": "finalize"
            }
        )
        subgraph_builder.add_edge("finalize", END)
        
        # Compile WITHOUT checkpointer - parent handles it
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