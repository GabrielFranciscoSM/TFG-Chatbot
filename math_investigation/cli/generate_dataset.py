#!/usr/bin/env python3
"""CLI for generating synthetic document datasets for clustering and topic modeling validation.

Migrated from scripts/math/generate_dataset.py
"""

import argparse
import json
import logging
import random
import time
import typing

# Try to use existing chatbot config, fallback to environment if not available
try:
    from chatbot.config import settings
except ImportError:

    class MockSettings:
        llm_provider = "vllm"
        gemini_model = "gemini-pro"
        mistral_model = "mistral-large-latest"
        vllm_url = "http://localhost:8000/v1"
        model_path = "google/gemma-7b"

        def get_gemini_api_key(self):
            return "MOCK"

        def get_mistral_api_key(self):
            return "MOCK"

    settings: typing.Any = MockSettings()  # type: ignore

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_mistralai import ChatMistralAI
except ImportError:
    ChatMistralAI = None

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

THEMES = {
    "Cloud Computing": [
        "Infrastructure as Service (IaaS)",
        "Serverless computing",
        "Hybrid cloud strategy",
        "Kubernetes orchestration",
        "Cloud storage scalability",
        "Virtualization technologies",
    ],
    "Artificial Intelligence": [
        "Deep Learning architectures",
        "Natural Language Processing",
        "Reinforcement Learning",
        "Neural network optimization",
        "Computer Vision",
        "Transformer models",
    ],
    "Cybersecurity": [
        "Zero Trust architecture",
        "Encryption algorithms",
        "Network intrusion detection",
        "Malware analysis",
        "Identity and Access Management",
        "Phishing prevention",
    ],
}

SYSTEM_PROMPT = """You are a specialized generator of synthetic academic content.
Your goal is to generate short, highly technical document fragments about specific topics.

Requirements:
1. Content must be technical and academic in tone.
2. Each fragment should be between 100 and 200 words.
3. Use specialized terminology related to the theme.
4. Output MUST be a valid JSON object.

Template:
{
    "text": "Academic content here...",
    "theme": "Theme Name",
    "subtopic": "Subtopic Name"
}
"""


class DatasetGenerator:
    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.llm_provider
        self.llm = self._init_llm()

    def _init_llm(self):
        if self.provider == "gemini":
            if ChatGoogleGenerativeAI is None:
                raise ImportError("langchain-google-genai is not installed")
            return ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.get_gemini_api_key(),
                temperature=0.7,
            )
        elif self.provider == "mistral":
            if ChatMistralAI is None:
                raise ImportError("langchain-mistralai is not installed")
            return ChatMistralAI(
                model=settings.mistral_model,
                mistral_api_key=settings.get_mistral_api_key(),
                temperature=0.7,
            )
        else:
            return ChatOpenAI(
                model=settings.model_path,
                openai_api_base=settings.vllm_url,
                openai_api_key="EMPTY",
                temperature=0.7,
            )

    def generate_fragment(
        self,
        theme: str,
        subtopic: str | None,
        is_trap: bool = False,
        other_theme: str | None = None,
    ) -> dict | None:
        if is_trap:
            prompt = f"Generate a 'trap' document fragment that mixes concepts from '{theme}' and '{other_theme}'."
        else:
            prompt = f"Generate a document fragment about '{theme}', specifically '{subtopic}'."

        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]

        for attempt in range(3):
            try:
                response = self.llm.invoke(messages)
                content = response.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                return json.loads(content)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2)
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic document dataset")
    parser.add_argument("--count", type=int, default=5, help="Fragments per theme")
    parser.add_argument("--traps", type=int, default=2, help="Number of trap fragments")
    parser.add_argument(
        "--output", type=str, default="math_investigation/data/synthetic_dataset.json"
    )
    parser.add_argument("--provider", type=str, help="LLM provider")
    parser.add_argument("--test-mode", action="store_true")

    args = parser.parse_args()
    if args.test_mode:
        args.count, args.traps = 1, 1

    generator = DatasetGenerator(provider=args.provider)
    dataset = []

    for theme, subtopics in THEMES.items():
        logger.info(f"Generating for theme: {theme}")
        for _ in range(args.count):
            subtopic = random.choice(subtopics)
            frag = generator.generate_fragment(theme, subtopic)
            if frag:
                dataset.append(frag)

    # Traps
    themes = list(THEMES.keys())
    for _ in range(args.traps):
        t1, t2 = random.sample(themes, 2)
        frag = generator.generate_fragment(t1, None, is_trap=True, other_theme=t2)
        if frag:
            dataset.append(frag)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved to {args.output}. Total fragments: {len(dataset)}")


if __name__ == "__main__":
    main()
