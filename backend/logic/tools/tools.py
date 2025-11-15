"""Tools for the LangGraph agent.
Contains various tools that can be used by the agent to perform actions.
"""

import json
import logging
from typing import Any

import requests
from langchain.tools import tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from backend.config import settings as backend_settings
from backend.db.mongo import MongoDBClient
from backend.logic.models import (
    MultipleChoiceTest,
    RagQueryInput,
    SubjectDataKey,
    SubjectLookupInput,
    TestGenerationInput,
    WebSearchInput,
)

logger = logging.getLogger(__name__)


@tool(args_schema=WebSearchInput)
def web_search(query: str) -> str:
    """
    Search the web for information using DuckDuckGo.
    """
    try:
        search = DuckDuckGoSearchAPIWrapper()
        results = search.run(query)
        return results
    except Exception as e:
        return f"Error performing web search: {str(e)}"


# List of all available tools
AVAILABLE_TOOLS = [web_search]


def _navigate_nested_dict(data: dict, path: str) -> Any | None:
    """Navigate a nested dictionary using dot notation path.

    Args:
        data: The dictionary to navigate
        path: Dot-separated path (e.g., "parent.child.key")

    Returns:
        The value at the path, or None if not found
    """
    parts = path.split(".")
    value: dict[Any, Any] | Any = data
    for part in parts:
        if not isinstance(value, dict):
            return None
        value = value.get(part)
        if value is None:
            return None
    return value


def _build_guia_summary(doc: dict) -> dict:
    """Build a short summary of a guia document.

    Args:
        doc: The complete guia document

    Returns:
        Dictionary with key summary fields
    """
    return {
        "subject": doc.get("subject"),
        "asignatura": doc.get("asignatura"),
        "grado": doc.get("grado"),
        "curso": doc.get("curso"),
        "url": doc.get("url"),
        "brief_description": doc.get("breve_descripción_de_contenidos", [])[:3],
    }


@tool(args_schema=SubjectLookupInput)
def get_guia(
    asignatura: str | None = None,
    key: SubjectDataKey | None = None,
) -> str:
    """Retrieve a stored guia document for the agent's current `asignatura` state.

    The agent should place the subject into its injected state `asignatura`.
    This function reads the injected `asignatura` via `InjectedState("asignatura")`.
    If no asignatura is present the tool returns a helpful error message.

    Args:
        asignatura: The subject identifier to look up
        key: Optional specific key to retrieve from the document

    Returns:
        JSON string with guia data or error message
    """
    try:
        if not asignatura:
            return "No guia found for subject"

        client = MongoDBClient()
        client.connect()
        doc = client.find_by_subject("guias", asignatura)
        client.close()

        if not doc:
            return f"No guia found for subject: {asignatura}"

        # If a specific key is requested, navigate to it
        if key:
            value = _navigate_nested_dict(doc, key.value)
            if value is None:
                return f"Key '{key.value}' not present in guia for subject {asignatura}"
            return json.dumps(value, ensure_ascii=False)

        # Otherwise, return a short summary
        summary = _build_guia_summary(doc)
        return json.dumps(summary, ensure_ascii=False)

    except Exception as e:
        return f"Error retrieving guia: {str(e)}"


AVAILABLE_TOOLS.append(get_guia)


def _extract_content_from_result(result: dict) -> str | None:
    """Extract content from a RAG result using common field names.

    Args:
        result: A single result dictionary from RAG service

    Returns:
        Content string or None
    """
    return (
        result.get("content")
        or result.get("text")
        or result.get("snippet")
        or result.get("payload")
    )


def _extract_metadata_from_result(result: dict) -> dict:
    """Extract and normalize metadata from a RAG result.

    Args:
        result: A single result dictionary from RAG service

    Returns:
        Normalized metadata dictionary
    """
    metadata = (
        result.get("metadata")
        or result.get("meta")
        or result.get("payload_metadata")
        or {}
    )

    if metadata is None:
        return {}

    if not isinstance(metadata, dict):
        try:
            return dict(metadata)
        except Exception:
            return {"raw": metadata}

    return metadata


def _extract_score_from_result(result: dict) -> float | None:
    """Extract score/similarity from a RAG result.

    Args:
        result: A single result dictionary from RAG service

    Returns:
        Score as float or None
    """
    if "score" in result and result.get("score") is not None:
        return result.get("score")
    elif "similarity" in result and result.get("similarity") is not None:
        return result.get("similarity")
    elif "distance" in result and result.get("distance") is not None:
        return result.get("distance")
    return None


def _normalize_single_result(result: Any) -> dict[str, Any]:
    """Normalize a single RAG result to standard format.

    Args:
        result: A single result (dict or other) from RAG service

    Returns:
        Normalized result dict with content, metadata, and score
    """
    if isinstance(result, dict):
        logger.debug("Processing raw result keys=%s", list(result.keys()))

        content = _extract_content_from_result(result)
        metadata = _extract_metadata_from_result(result)
        score = _extract_score_from_result(result)

        # Log truncated content for debugging
        try:
            content_snip = content[:200] if isinstance(content, str) else str(content)
        except Exception:
            content_snip = str(content)

        logger.debug(
            "Normalized result content=%s score=%s metadata_keys=%s",
            content_snip,
            score,
            list(metadata.keys()) if isinstance(metadata, dict) else None,
        )

        return {"content": content, "metadata": metadata, "score": score}
    else:
        return {"content": str(result), "metadata": {}, "score": None}


def _normalize_rag_results(data: Any) -> list[dict[str, Any]]:
    """Normalize RAG service response into standard format.

    Args:
        data: Raw response from RAG service

    Returns:
        List of normalized results with content, metadata, and score
    """
    raw_results = data.get("results") if isinstance(data, dict) else None
    logger.debug("raw_results type=%s", type(raw_results))

    normalized = []

    if raw_results and isinstance(raw_results, list):
        for result in raw_results:
            normalized.append(_normalize_single_result(result))
    else:
        # If the provider returned a flat text or other shape
        if isinstance(data, dict) and "content" in data:
            normalized.append(
                {
                    "content": data.get("content"),
                    "metadata": data.get("metadata", {}),
                    "score": data.get("score"),
                }
            )
        else:
            normalized.append({"content": str(data), "metadata": {}, "score": None})

    return normalized


@tool(args_schema=RagQueryInput)
def rag_search(
    query: str,
    asignatura: str | None = None,
    tipo_documento: str | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    """Perform a semantic search against the external RAG service.

    Args:
        query: The search query text
        asignatura: Optional subject filter
        tipo_documento: Optional document type filter
        top_k: Optional limit on number of results

    Returns:
        A structured dict with the following shape on success:
          {
            "ok": True,
            "query": <original query>,
            "total_results": <int>,
            "results": [
               {"content": str, "metadata": {...}, "score": float},
               ...
            ]
          }

        On error returns:
          {"ok": False, "error": "..."}
    """
    try:
        logger.debug(
            "rag_search called with query=%s, asignatura=%s, tipo_documento=%s, top_k=%s",
            query,
            asignatura,
            tipo_documento,
            top_k,
        )

        # Build request
        url = f"{backend_settings.rag_service_url.rstrip('/')}/search"
        payload: dict[str, Any] = {"query": query}
        if asignatura:
            payload["asignatura"] = asignatura
        if tipo_documento:
            payload["tipo_documento"] = tipo_documento
        if top_k:
            payload["top_k"] = top_k

        logger.debug("Posting to RAG service url=%s payload=%s", url, payload)

        # Make request
        resp = requests.post(url, json=payload, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        logger.debug("RAG service returned data: %s", data)

        # Normalize results
        normalized = _normalize_rag_results(data)

        logger.debug("Returning %d normalized results", len(normalized))
        return {
            "ok": True,
            "query": data.get("query") if isinstance(data, dict) else query,
            "total_results": (
                data.get("total_results")
                if isinstance(data, dict) and data.get("total_results") is not None
                else len(normalized)
            ),
            "results": normalized,
        }

    except requests.exceptions.Timeout as e:
        logger.error("RAG service timeout: %s", str(e))
        return {"ok": False, "error": f"RAG service timeout: {str(e)}"}
    except requests.exceptions.ConnectionError as e:
        logger.error("Cannot connect to RAG service: %s", str(e))
        return {"ok": False, "error": f"Cannot connect to RAG service: {str(e)}"}
    except requests.exceptions.RequestException as e:
        logger.error("Error contacting RAG service: %s", str(e))
        return {"ok": False, "error": f"Error contacting RAG service: {str(e)}"}
    except Exception as e:
        logger.error("Unexpected error in rag_search: %s", str(e))
        return {"ok": False, "error": f"Unexpected error: {str(e)}"}


AVAILABLE_TOOLS.append(rag_search)


def _get_llm_for_test_generation():
    """Initialize LLM for test generation based on environment configuration.

    Returns:
        Configured LLM instance (ChatOpenAI or ChatGoogleGenerativeAI)

    Raises:
        ValueError: If required API keys are missing
    """
    import os

    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_openai import ChatOpenAI

    llm_provider = os.getenv("LLM_PROVIDER", "vllm")

    if llm_provider == "gemini":
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        return ChatGoogleGenerativeAI(
            model=gemini_model,
            google_api_key=gemini_api_key,
            temperature=0.7,
        )
    else:  # vllm
        vllm_port = os.getenv("VLLM_MAIN_PORT", "8000")
        vllm_host = os.getenv("VLLM_HOST", "vllm-openai")
        vllm_url = f"http://{vllm_host}:{vllm_port}/v1"
        model_name = os.getenv(
            "MODEL_PATH", "/models/HuggingFaceTB--SmolLM2-1.7B-Instruct"
        )

        return ChatOpenAI(
            model=model_name,
            openai_api_key="EMPTY",
            openai_api_base=vllm_url,
            temperature=0.7,
        )


def _parse_llm_questions_response(
    response_text: str, num_questions: int, topic: str, difficulty: str
) -> list[dict]:
    """Parse LLM response to extract questions data.

    Args:
        response_text: Raw text response from LLM
        num_questions: Expected number of questions
        topic: Topic for fallback questions
        difficulty: Difficulty level for fallback questions

    Returns:
        List of question data dictionaries
    """
    import re

    # Try to extract JSON array from response
    json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    else:
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
    """Convert question data to MultipleChoiceTest objects.

    Args:
        questions_data: List of question data dictionaries
        num_questions: Number of questions to create
        difficulty: Default difficulty level

    Returns:
        List of MultipleChoiceTest objects
    """
    from backend.logic.models import Question

    tests = []
    for q_data in questions_data[:num_questions]:
        question = Question(
            question_text=q_data.get("question_text", "Pregunta sin texto"),
            difficulty=q_data.get("difficulty", difficulty),
        )

        # For open-ended review questions, we don't provide multiple choice options
        # The student provides free-text answers
        test = MultipleChoiceTest(
            question=question,
            options=[],  # Empty options for free-form answers
        )
        tests.append(test)

    return tests


@tool(args_schema=TestGenerationInput)
def generate_test(
    topic: str, num_questions: int, difficulty: str | None = None
) -> list:
    """Generate review questions on a given topic.

    Creates thought-provoking questions for an informal review session.
    Questions are designed to encourage reflection and understanding.

    Args:
        topic: The subject matter for the questions
        num_questions: Number of questions to generate (1-10)
        difficulty: Optional difficulty level (easy, medium, hard)

    Returns:
        List of MultipleChoiceTest objects with generated questions
    """
    from backend.logic.models import Question
    from backend.logic.prompts import TEST_GENERATION_PROMPT

    difficulty = difficulty or "medium"

    try:
        # Initialize LLM
        llm = _get_llm_for_test_generation()

        # Build prompt and generate questions
        prompt = TEST_GENERATION_PROMPT.format(
            topic=topic, num_questions=num_questions, difficulty=difficulty
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
        return [
            MultipleChoiceTest(
                question=Question(
                    question_text=f"¿Qué has aprendido sobre {topic}?",
                    difficulty="medium",
                ),
                options=[],
            )
        ]


AVAILABLE_TOOLS.append(generate_test)


def get_tools():
    """
    Returns a list of all available tools for the agent.
    """
    return AVAILABLE_TOOLS
