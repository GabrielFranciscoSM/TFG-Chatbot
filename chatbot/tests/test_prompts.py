"""Tests for adaptive prompts module (HU #17)."""

import pytest

from chatbot.logic.prompts import (
    ADAPTIVE_PROMPTS,
    SYSTEM_PROMPT_ADVANCED,
    SYSTEM_PROMPT_BASIC,
    SYSTEM_PROMPT_INTERMEDIATE,
    SYSTEM_PROMPT_V3,
    DifficultyLevel,
    get_adaptive_prompt,
)


class TestDifficultyLevel:
    """Tests for DifficultyLevel enum."""

    def test_difficulty_levels_exist(self):
        """Test that all expected difficulty levels are defined."""
        assert DifficultyLevel.BASIC.value == "basic"
        assert DifficultyLevel.INTERMEDIATE.value == "intermediate"
        assert DifficultyLevel.ADVANCED.value == "advanced"

    def test_difficulty_level_from_string(self):
        """Test creating DifficultyLevel from string values."""
        assert DifficultyLevel("basic") == DifficultyLevel.BASIC
        assert DifficultyLevel("intermediate") == DifficultyLevel.INTERMEDIATE
        assert DifficultyLevel("advanced") == DifficultyLevel.ADVANCED

    def test_invalid_difficulty_level(self):
        """Test that invalid difficulty levels raise ValueError."""
        with pytest.raises(ValueError):
            DifficultyLevel("expert")


class TestAdaptivePrompts:
    """Tests for adaptive prompt templates."""

    @pytest.mark.parametrize(
        "level,prompt",
        [
            (DifficultyLevel.BASIC, SYSTEM_PROMPT_BASIC),
            (DifficultyLevel.INTERMEDIATE, SYSTEM_PROMPT_INTERMEDIATE),
            (DifficultyLevel.ADVANCED, SYSTEM_PROMPT_ADVANCED),
        ],
    )
    def test_adaptive_prompts_mapping(self, level, prompt):
        """Test that ADAPTIVE_PROMPTS maps correctly."""
        assert ADAPTIVE_PROMPTS[level] == prompt

    def test_all_levels_have_prompts(self):
        """Test that all difficulty levels have corresponding prompts."""
        for level in DifficultyLevel:
            assert level in ADAPTIVE_PROMPTS
            assert ADAPTIVE_PROMPTS[level] is not None
            assert len(ADAPTIVE_PROMPTS[level]) > 0

    def test_prompts_contain_asignatura_placeholder(self):
        """Test that all prompts have the {asignatura} placeholder."""
        for level, prompt in ADAPTIVE_PROMPTS.items():
            assert (
                "{asignatura}" in prompt
            ), f"Missing placeholder in {level.value} prompt"


class TestGetAdaptivePrompt:
    """Tests for get_adaptive_prompt function."""

    def test_get_prompt_with_enum(self):
        """Test getting prompt with DifficultyLevel enum."""
        prompt = get_adaptive_prompt(DifficultyLevel.BASIC, "Docker")
        assert "Docker" in prompt
        assert "BÁSICO" in prompt

    def test_get_prompt_with_string(self):
        """Test getting prompt with string difficulty level."""
        prompt = get_adaptive_prompt("intermediate", "Kubernetes")
        assert "Kubernetes" in prompt
        assert "INTERMEDIO" in prompt

    def test_get_prompt_advanced(self):
        """Test advanced prompt contains expected elements."""
        prompt = get_adaptive_prompt("advanced", "Machine Learning")
        assert "Machine Learning" in prompt
        assert "AVANZADO" in prompt
        assert "trade-offs" in prompt.lower() or "limitaciones" in prompt

    def test_invalid_difficulty_defaults_to_intermediate(self):
        """Test that invalid difficulty falls back to intermediate."""
        prompt = get_adaptive_prompt("invalid_level", "Python")
        assert "Python" in prompt
        # Should default to intermediate prompt
        assert "INTERMEDIO" in prompt

    def test_basic_prompt_has_simpler_language(self):
        """Test that basic prompt emphasizes simpler communication."""
        prompt = get_adaptive_prompt(DifficultyLevel.BASIC, "Test")
        # Basic should mention simple language and examples
        assert any(
            keyword in prompt.lower()
            for keyword in ["simple", "ejemplos", "analogía", "sencill"]
        )

    def test_advanced_prompt_has_technical_depth(self):
        """Test that advanced prompt emphasizes technical depth."""
        prompt = get_adaptive_prompt(DifficultyLevel.ADVANCED, "Test")
        # Advanced should mention technical terminology and analysis
        assert any(
            keyword in prompt.lower()
            for keyword in ["técnic", "análisis", "investigación", "perspectivas"]
        )


class TestPromptDifferentiation:
    """Tests to verify prompts are meaningfully different."""

    def test_prompts_are_different(self):
        """Test that each difficulty level has a distinct prompt."""
        basic = get_adaptive_prompt(DifficultyLevel.BASIC, "Test")
        intermediate = get_adaptive_prompt(DifficultyLevel.INTERMEDIATE, "Test")
        advanced = get_adaptive_prompt(DifficultyLevel.ADVANCED, "Test")

        assert basic != intermediate
        assert intermediate != advanced
        assert basic != advanced

    def test_difficulty_label_in_prompt(self):
        """Test that each prompt contains its difficulty level."""
        basic = get_adaptive_prompt(DifficultyLevel.BASIC, "Test")
        intermediate = get_adaptive_prompt(DifficultyLevel.INTERMEDIATE, "Test")
        advanced = get_adaptive_prompt(DifficultyLevel.ADVANCED, "Test")

        assert "BÁSICO" in basic
        assert "INTERMEDIO" in intermediate
        assert "AVANZADO" in advanced

    def test_all_prompts_have_tools_section(self):
        """Test that all adaptive prompts mention available tools."""
        for level in DifficultyLevel:
            prompt = get_adaptive_prompt(level, "Test")
            assert "rag_search" in prompt
            assert "get_guia" in prompt

    def test_prompt_length_progression(self):
        """Test that prompt structure is appropriate for each level."""
        basic = get_adaptive_prompt(DifficultyLevel.BASIC, "Test")
        advanced = get_adaptive_prompt(DifficultyLevel.ADVANCED, "Test")

        # Both should be substantial prompts
        assert len(basic) > 500
        assert len(advanced) > 500


class TestLegacyPromptCompatibility:
    """Tests to ensure legacy prompts still work."""

    def test_v3_prompt_exists(self):
        """Test that SYSTEM_PROMPT_V3 is still available."""
        assert SYSTEM_PROMPT_V3 is not None
        assert "{asignatura}" in SYSTEM_PROMPT_V3

    def test_v3_prompt_can_be_formatted(self):
        """Test that V3 prompt can be formatted with asignatura."""
        formatted = SYSTEM_PROMPT_V3.format(asignatura="Test Subject")
        assert "Test Subject" in formatted
