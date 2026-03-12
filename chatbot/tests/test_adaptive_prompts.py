"""Tests for adaptive prompts by difficulty level (HU #17)."""

import pytest

from chatbot.logic.prompts import (
    ADAPTIVE_PROMPTS,
    SYSTEM_PROMPT_ADVANCED,
    SYSTEM_PROMPT_BASIC,
    SYSTEM_PROMPT_INTERMEDIATE,
    DifficultyLevel,
    get_adaptive_prompt,
)


class TestAdaptivePrompts:
    """Test suite for adaptive prompt selection."""

    def test_difficulty_level_enum_values(self):
        """Verify DifficultyLevel enum has correct values."""
        assert DifficultyLevel.BASIC.value == "basic"
        assert DifficultyLevel.INTERMEDIATE.value == "intermediate"
        assert DifficultyLevel.ADVANCED.value == "advanced"

    def test_adaptive_prompts_dict_has_all_levels(self):
        """Verify ADAPTIVE_PROMPTS contains all difficulty levels."""
        assert DifficultyLevel.BASIC in ADAPTIVE_PROMPTS
        assert DifficultyLevel.INTERMEDIATE in ADAPTIVE_PROMPTS
        assert DifficultyLevel.ADVANCED in ADAPTIVE_PROMPTS
        assert len(ADAPTIVE_PROMPTS) == 3

    def test_basic_prompt_characteristics(self):
        """Verify basic prompt has appropriate characteristics."""
        prompt = SYSTEM_PROMPT_BASIC

        # Should mention basic/simple language
        assert "BÁSICO" in prompt or "simple" in prompt.lower()
        # Should mention examples
        assert "ejemplo" in prompt.lower()
        # Should have asignatura placeholder
        assert "{asignatura}" in prompt

    def test_intermediate_prompt_characteristics(self):
        """Verify intermediate prompt has appropriate characteristics."""
        prompt = SYSTEM_PROMPT_INTERMEDIATE

        # Should mention intermediate level
        assert "INTERMEDIO" in prompt
        # Should mention technical terminology
        assert "técnic" in prompt.lower()
        # Should have asignatura placeholder
        assert "{asignatura}" in prompt

    def test_advanced_prompt_characteristics(self):
        """Verify advanced prompt has appropriate characteristics."""
        prompt = SYSTEM_PROMPT_ADVANCED

        # Should mention advanced level
        assert "AVANZADO" in prompt
        # Should mention analysis/synthesis
        assert "análisis" in prompt.lower() or "trade-off" in prompt.lower()
        # Should have asignatura placeholder
        assert "{asignatura}" in prompt


class TestGetAdaptivePrompt:
    """Test suite for get_adaptive_prompt function."""

    @pytest.fixture
    def test_asignatura(self):
        """Test subject name."""
        return "Ingeniería del Software"

    def test_get_prompt_with_string_basic(self, test_asignatura):
        """Get adaptive prompt with string 'basic'."""
        prompt = get_adaptive_prompt("basic", test_asignatura)

        assert test_asignatura in prompt
        assert "BÁSICO" in prompt

    def test_get_prompt_with_string_intermediate(self, test_asignatura):
        """Get adaptive prompt with string 'intermediate'."""
        prompt = get_adaptive_prompt("intermediate", test_asignatura)

        assert test_asignatura in prompt
        assert "INTERMEDIO" in prompt

    def test_get_prompt_with_string_advanced(self, test_asignatura):
        """Get adaptive prompt with string 'advanced'."""
        prompt = get_adaptive_prompt("advanced", test_asignatura)

        assert test_asignatura in prompt
        assert "AVANZADO" in prompt

    def test_get_prompt_with_enum_basic(self, test_asignatura):
        """Get adaptive prompt with DifficultyLevel.BASIC enum."""
        prompt = get_adaptive_prompt(DifficultyLevel.BASIC, test_asignatura)

        assert test_asignatura in prompt
        assert "BÁSICO" in prompt

    def test_get_prompt_with_enum_intermediate(self, test_asignatura):
        """Get adaptive prompt with DifficultyLevel.INTERMEDIATE enum."""
        prompt = get_adaptive_prompt(DifficultyLevel.INTERMEDIATE, test_asignatura)

        assert test_asignatura in prompt
        assert "INTERMEDIO" in prompt

    def test_get_prompt_with_enum_advanced(self, test_asignatura):
        """Get adaptive prompt with DifficultyLevel.ADVANCED enum."""
        prompt = get_adaptive_prompt(DifficultyLevel.ADVANCED, test_asignatura)

        assert test_asignatura in prompt
        assert "AVANZADO" in prompt

    def test_invalid_difficulty_falls_back_to_intermediate(self, test_asignatura):
        """Invalid difficulty string should fall back to intermediate."""
        prompt = get_adaptive_prompt("invalid_level", test_asignatura)

        assert test_asignatura in prompt
        # Should fall back to intermediate
        assert "INTERMEDIO" in prompt

    def test_asignatura_formatting(self):
        """Test that asignatura is correctly formatted into prompt."""
        subjects = [
            "Docker y Contenedores",
            "Bases de Datos",
            "Programación Orientada a Objetos",
        ]

        for subject in subjects:
            for level in DifficultyLevel:
                prompt = get_adaptive_prompt(level, subject)
                assert (
                    subject in prompt
                ), f"Subject '{subject}' not found in {level} prompt"


class TestPromptTools:
    """Test that prompts reference available tools correctly."""

    @pytest.mark.parametrize(
        "prompt",
        [
            SYSTEM_PROMPT_BASIC,
            SYSTEM_PROMPT_INTERMEDIATE,
            SYSTEM_PROMPT_ADVANCED,
        ],
    )
    def test_prompts_mention_rag_search(self, prompt):
        """All adaptive prompts should mention rag_search tool."""
        assert "rag_search" in prompt.lower()

    @pytest.mark.parametrize(
        "prompt",
        [
            SYSTEM_PROMPT_BASIC,
            SYSTEM_PROMPT_INTERMEDIATE,
            SYSTEM_PROMPT_ADVANCED,
        ],
    )
    def test_prompts_mention_get_guia(self, prompt):
        """All adaptive prompts should mention get_guia tool."""
        assert "get_guia" in prompt.lower()

    @pytest.mark.parametrize(
        "prompt",
        [
            SYSTEM_PROMPT_BASIC,
            SYSTEM_PROMPT_INTERMEDIATE,
            SYSTEM_PROMPT_ADVANCED,
        ],
    )
    def test_prompts_have_language_instruction(self, prompt):
        """All prompts should instruct response in user's language."""
        assert "idioma" in prompt.lower() or "language" in prompt.lower()
