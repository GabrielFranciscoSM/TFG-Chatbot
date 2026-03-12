"""Tool for generating review questions and tests."""

import json
import logging

import requests
from langchain.tools import tool

from chatbot.config import settings as chatbot_settings
from chatbot.logic.models import MultipleChoiceTest, TestGenerationInput

logger = logging.getLogger(__name__)


def _get_llm_for_test_generation():
    """Initialize LLM for test generation based on environment configuration."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_mistralai import ChatMistralAI
    from langchain_openai import ChatOpenAI

    from chatbot.config import settings

    if settings.llm_provider == "gemini":
        gemini_key = settings.get_gemini_api_key()
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=gemini_key,
            temperature=0.7,
        )
    elif settings.llm_provider == "mistral":
        mistral_key = settings.get_mistral_api_key()
        if not mistral_key:
            raise ValueError("MISTRAL_API_KEY not found in environment")

        return ChatMistralAI(
            model=settings.mistral_model,
            mistral_api_key=mistral_key,
            temperature=0.7,
        )
    else:  # vllm
        return ChatOpenAI(
            model=settings.model_path,
            openai_api_key="EMPTY",
            openai_api_base=settings.vllm_url,
            temperature=0.7,
        )


def _parse_llm_questions_response(
    response_text: str, num_questions: int, topic: str, difficulty: str
) -> list[dict]:
    """Parse LLM response to extract questions data."""
    import re

    # Try to extract JSON array from response
    json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from LLM response")

    # Fallback: create simple questions
    logger.warning(
        f"Could not parse LLM response for test generation. Response: {response_text[:200]}"
    )
    return [
        {
            "question_text": f"Pregunta {i + 1} sobre {topic}",
            "difficulty": difficulty,
        }
        for i in range(num_questions)
    ]


def _create_test_objects(
    questions_data: list[dict], num_questions: int, difficulty: str
) -> list[MultipleChoiceTest]:
    """Convert question data to MultipleChoiceTest objects."""
    from chatbot.logic.models import Question

    tests = []
    for q_data in questions_data[:num_questions]:
        question = Question(
            question_text=q_data.get("question_text", "Pregunta sin texto"),
            difficulty=q_data.get("difficulty", difficulty),
        )

        # For open-ended review questions, we don't provide multiple choice options
        test = MultipleChoiceTest(
            question=question,
            options=[],  # Empty options for free-form answers
        )
        tests.append(test)

    return tests


def _get_professor_preferences(subject: str) -> dict:
    """Fetch test preferences configured by the professor for a subject."""
    defaults = {
        "default_test_questions": 5,
        "default_test_difficulty": "medium",
    }

    try:
        url = f"{chatbot_settings.backend_service_url}/users/subject/{subject}/preferences"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            prefs = response.json()
            logger.info(f"Got professor preferences for {subject}: {prefs}")
            return prefs
        else:
            logger.warning(
                f"Failed to get professor preferences for {subject}: "
                f"status={response.status_code}"
            )
            return defaults

    except requests.RequestException as e:
        logger.warning(f"Error fetching professor preferences for {subject}: {e}")
        return defaults


@tool(args_schema=TestGenerationInput)
def generate_test(
    topic: str,
    num_questions: int | None = None,
    difficulty: str | None = None,
    context: str | None = None,
    asignatura: str | None = None,
) -> list:
    """Generate review questions on a given topic.

    Args:
        topic: The subject matter for the questions
        num_questions: Number of questions to generate (1-10)
        difficulty: Optional difficulty level (easy, medium, hard)
        context: Relevant context for question generation
        asignatura: The subject to get professor preferences from

    Returns:
        List of MultipleChoiceTest objects with generated questions
    """
    from chatbot.logic.prompts import TEST_GENERATION_PROMPT

    # Fetch professor preferences if we have a subject
    professor_prefs = _get_professor_preferences(asignatura) if asignatura else None

    # Use professor defaults when values not explicitly provided
    if num_questions is None:
        num_questions = (
            professor_prefs.get("default_test_questions", 5) if professor_prefs else 5
        )

    if difficulty is None:
        difficulty = (
            professor_prefs.get("default_test_difficulty", "medium")
            if professor_prefs
            else "medium"
        )

    try:
        # Initialize LLM
        llm = _get_llm_for_test_generation()

        # Build prompt and generate questions
        prompt = TEST_GENERATION_PROMPT.format(
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty,
            context=context or "No additional context provided.",
        )

        response = llm.invoke(prompt)
        response_text = (
            response.content if hasattr(response, "content") else str(response)
        )

        # Parse response and create test objects
        questions_data = _parse_llm_questions_response(
            response_text, num_questions, topic, difficulty
        )
        tests = _create_test_objects(questions_data, num_questions, difficulty)

        logger.info(f"Generated {len(tests)} questions for topic: {topic}")
        return tests

    except Exception as e:
        logger.exception(f"Error generating test: {str(e)}")
        # Return a fallback question
        from chatbot.logic.models import Question

        return [
            MultipleChoiceTest(
                question=Question(
                    question_text=f"¿Qué has aprendido sobre {topic}?",
                    difficulty="medium",
                ),
                options=[],
            )
        ]
