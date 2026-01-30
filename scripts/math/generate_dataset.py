#!/usr/bin/env python3
"""
Script to generate a synthetic dataset of document fragments for clustering validation.
"""

import argparse
import json
import logging
import random
import time
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_mistralai import ChatMistralAI
except ImportError:
    ChatMistralAI = None

from langchain_openai import ChatOpenAI

# Import settings from chatbot config
try:
    from chatbot.config import settings
except ImportError:
    # Fallback or manual config if not in python path
    import sys

    sys.path.append(str(Path(__file__).parent.parent.parent))
    from chatbot.config import settings

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

Template for Normal Fragments:
{{
    "text": "Academic content here...",
    "label": "Theme Name",
    "metadata": {{
        "theme": "Theme Name",
        "subtopic": "Subtopic Name"
    }}
}}

Template for Trap Fragments (Mixed Vocabulary):
{{
    "text": "Mixed content covering both Theme A and Theme B...",
    "label": "Mixed",
    "is_trap": true,
    "metadata": {{
        "themes": ["Theme A", "Theme B"],
        "subtopic": "Mixed context"
    }}
}}
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
        else:  # vllm
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
    ) -> dict[str, Any] | None:
        if is_trap:
            prompt = f"Generate a 'trap' document fragment that mixes vocabulary and concepts from '{theme}' and '{other_theme}'. Make it sound like a coherent document that spans both domains."
        else:
            prompt = f"Generate a document fragment about '{theme}', specifically focusing on the subtopic '{subtopic}'."

        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]

        for attempt in range(3):
            try:
                response = self.llm.invoke(messages)
                content = response.content
                # Strip potential markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                return json.loads(content)
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed for {theme}/{subtopic}: {e}"
                )
                time.sleep(2)

        return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic dataset for clustering validation."
    )
    parser.add_argument("--count", type=int, default=100, help="Fragments per theme")
    parser.add_argument(
        "--traps", type=int, default=20, help="Number of trap fragments"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/synthetic_dataset.json",
        help="Path to save the dataset",
    )
    parser.add_argument(
        "--provider", type=str, help="LLM provider (gemini, mistral, vllm)"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Generate only a few fragments for testing",
    )

    args = parser.parse_args()

    if args.test_mode:
        args.count = 2
        args.traps = 1
        logger.info("Running in TEST MODE. Generating 2 fragments per theme + 1 trap.")

    generator = DatasetGenerator(provider=args.provider)
    dataset = []

    # Generate normal fragments
    for theme, subtopics in THEMES.items():
        logger.info(f"Generating fragments for theme: {theme}")
        for _ in range(args.count):
            subtopic = random.choice(subtopics)
            fragment = generator.generate_fragment(theme, subtopic)
            if fragment:
                dataset.append(fragment)
                logger.info(f"  [{len(dataset)}] Generated {theme}: {subtopic}")

            if not args.test_mode:
                time.sleep(0.5)  # Avoid rate limits

    # Generate trap fragments
    logger.info("Generating trap fragments")
    theme_names = list(THEMES.keys())
    for _ in range(args.traps):
        t1, t2 = random.sample(theme_names, 2)
        fragment = generator.generate_fragment(t1, None, is_trap=True, other_theme=t2)
        if fragment:
            dataset.append(fragment)
            logger.info(f"  [{len(dataset)}] Generated Trap: {t1} + {t2}")

        if not args.test_mode:
            time.sleep(0.5)

    # Save dataset
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    logger.info(f"Dataset saved to {args.output}. Total fragments: {len(dataset)}")


if __name__ == "__main__":
    main()
