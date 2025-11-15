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


@tool(args_schema=SubjectLookupInput)
def get_guia(
    asignatura: str | None = None,
    key: SubjectDataKey | None = None,
) -> str:
    """Retrieve a stored guia document for the agent's current `asignatura` state.

    The agent should place the subject into its injected state `asignatura`.
    This function reads the injected `asignatura` via `InjectedState("asignatura")`.
    If no asignatura is present the tool returns a helpful error message.
    """
    try:
        # If the agent did not provide an asignatura via injected state,
        # return a clear message so the agent can ask the user to set it.

        if not asignatura:
            return "No guia found for subject"

        asignatura_state = asignatura

        client = MongoDBClient()
        client.connect()
        doc = client.find_by_subject("guias", asignatura_state)
        client.close()
        if not doc:
            return f"No guia found for subject: {asignatura_state}"

        # If a specific key is requested, use the enum value directly (dot notation supported)
        if key:
            path = key.value
            # support nested keys with dot notation
            parts = path.split(".") if isinstance(path, str) else [path]
            value = doc
            for p in parts:
                if not isinstance(value, dict):
                    value = None
                    break
                value = value.get(p)

            if value is None:
                return f"Key '{key.value}' not present in guia for subject {asignatura_state}"

            # Return JSON string for structured content
            return json.dumps(value, ensure_ascii=False)

        # Otherwise, return a short summary
        summary = {
            "subject": doc.get("subject"),
            "asignatura": doc.get("asignatura"),
            "grado": doc.get("grado"),
            "curso": doc.get("curso"),
            "url": doc.get("url"),
            "brief_description": doc.get("breve_descripción_de_contenidos", [])[:3],
        }
        return json.dumps(summary, ensure_ascii=False)
    except Exception as e:
        return f"Error retrieving guia: {str(e)}"


AVAILABLE_TOOLS.append(get_guia)


@tool(args_schema=RagQueryInput)
def rag_search(
    query: str,
    asignatura: str | None = None,
    tipo_documento: str | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    """Perform a semantic search against the external RAG service.

    Returns a structured dict with the following shape on success:
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
        url = f"{backend_settings.rag_service_url.rstrip('/')}/search"
        payload: dict[str, Any] = {"query": query}
        if asignatura:
            payload["asignatura"] = asignatura
        if tipo_documento:
            payload["tipo_documento"] = tipo_documento
        if top_k:
            payload["top_k"] = top_k

        logger.debug("Posting to RAG service url=%s payload=%s", url, payload)

        resp = requests.post(url, json=payload, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        logger.debug("RAG service returned data: %s", data)

        # Normalize the provider response into a compact `results` list of
        # {content, metadata, score} entries. Many RAG services return a
        # 'results' list already; if not, try to map commonly used keys.
        raw_results = data.get("results") if isinstance(data, dict) else None
        logger.debug("raw_results type=%s", type(raw_results))
        normalized = []
        if raw_results and isinstance(raw_results, list):
            for r in raw_results:
                # r might be a dict with content/metadata/score or other shape
                if isinstance(r, dict):
                    logger.debug("Processing raw result keys=%s", list(r.keys()))
                    # Prefer explicit fields used by our RAG service
                    content = (
                        r.get("content")
                        or r.get("text")
                        or r.get("snippet")
                        or r.get("payload")
                    )

                    # metadata may be under different keys depending on vector store
                    metadata = (
                        r.get("metadata")
                        or r.get("meta")
                        or r.get("payload_metadata")
                        or {}
                    )
                    # Normalize metadata to dict
                    if metadata is None:
                        metadata = {}
                    if not isinstance(metadata, dict):
                        try:
                            metadata = dict(metadata)
                        except Exception:
                            metadata = {"raw": metadata}

                    # Score fields: score, similarity, distance (convert where possible)
                    score = None
                    if "score" in r and r.get("score") is not None:
                        score = r.get("score")
                    elif "similarity" in r and r.get("similarity") is not None:
                        score = r.get("similarity")
                    elif "distance" in r and r.get("distance") is not None:
                        # Some stores return distance where smaller is better; keep raw value
                        score = r.get("distance")

                    # Truncate content for logs if it's large
                    try:
                        content_snip = (
                            content[:200] if isinstance(content, str) else str(content)
                        )
                    except Exception:
                        content_snip = str(content)
                    logger.debug(
                        "Normalized result content=%s score=%s metadata_keys=%s",
                        content_snip,
                        score,
                        list(metadata.keys()) if isinstance(metadata, dict) else None,
                    )

                    normalized.append(
                        {"content": content, "metadata": metadata, "score": score}
                    )
                else:
                    normalized.append(
                        {"content": str(r), "metadata": {}, "score": None}
                    )
        else:
            # If the provider returned a flat text or other shape, include it as a single result
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
    except requests.exceptions.RequestException as e:
        # Log a concise error message (avoid printing full traceback during normal test runs)
        logger.error("Error contacting RAG service: %s", str(e))
        return {"ok": False, "error": f"Error contacting RAG service: {str(e)}"}
    except requests.exceptions.Timeout as e:
        return {"ok": False, "error": f"RAG service timeout: {str(e)}"}
    except requests.exceptions.ConnectionError as e:
        return {"ok": False, "error": f"Cannot connect to RAG service: {str(e)}"}
    except Exception as e:
        # Unexpected errors should be logged; keep message concise to avoid noisy test output
        logger.error("Unexpected error in rag_search: %s", str(e))
        return {"ok": False, "error": f"Unexpected error: {str(e)}"}


AVAILABLE_TOOLS.append(rag_search)


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
    import os

    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_openai import ChatOpenAI

    from backend.logic.models import Question
    from backend.logic.prompts import TEST_GENERATION_PROMPT

    try:
        # Get LLM provider from environment
        llm_provider = os.getenv("LLM_PROVIDER", "vllm")

        # Initialize LLM based on provider
        if llm_provider == "gemini":
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            if not gemini_api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")

            llm = ChatGoogleGenerativeAI(
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

            llm = ChatOpenAI(
                model=model_name,
                openai_api_key="EMPTY",
                openai_api_base=vllm_url,
                temperature=0.7,
            )

        # Build prompt
        prompt = TEST_GENERATION_PROMPT.format(
            topic=topic, num_questions=num_questions, difficulty=difficulty or "medium"
        )

        # Generate questions
        response = llm.invoke(prompt)
        response_text = (
            response.content if hasattr(response, "content") else str(response)
        )

        # Parse JSON response
        import re

        # Try to extract JSON array from response
        json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
        if json_match:
            questions_data = json.loads(json_match.group())
        else:
            # Fallback: create simple questions
            logger.warning(
                f"Could not parse LLM response for test generation. Response: {response_text[:200]}"
            )
            questions_data = [
                {
                    "question_text": f"Pregunta {i + 1} sobre {topic}",
                    "difficulty": difficulty or "medium",
                }
                for i in range(num_questions)
            ]

        # Convert to MultipleChoiceTest objects
        tests = []
        for q_data in questions_data[:num_questions]:
            question = Question(
                question_text=q_data.get("question_text", "Pregunta sin texto"),
                difficulty=q_data.get("difficulty", difficulty or "medium"),
            )

            # For open-ended review questions, we don't provide multiple choice options
            # The student provides free-text answers
            test = MultipleChoiceTest(
                question=question,
                options=[],  # Empty options for free-form answers
            )
            tests.append(test)

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
