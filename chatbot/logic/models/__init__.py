"""Models for chatbot logic layer.

This package contains:
- Tool input models (WebSearchInput, RagQueryInput, etc.)
- Test generation models (Question, Answer, MultipleChoiceTest)
- Student profile models (StudentProfile, Interaction, etc.)
"""

# New student profile models
from chatbot.logic.models.student_profile import (
    ConversationTurn,
    Interaction,
    StudentProfile,
    TopicMastery,
)

# Re-export existing models from the original models module
# These were previously in chatbot/logic/models.py
from chatbot.logic.models.tool_models import (
    Answer,
    DocumentMetadata,
    GetSubjectDataInput,
    MultipleChoiceTest,
    Question,
    RagQueryInput,
    SubjectDataKey,
    SubjectLookupInput,
    TestGenerationInput,
    WebSearchInput,
)

__all__ = [
    # Tool input models
    "WebSearchInput",
    "SubjectDataKey",
    "GetSubjectDataInput",
    "SubjectLookupInput",
    "RagQueryInput",
    "DocumentMetadata",
    # Test models
    "Question",
    "Answer",
    "MultipleChoiceTest",
    "TestGenerationInput",
    # Student profile models
    "Interaction",
    "TopicMastery",
    "StudentProfile",
    "ConversationTurn",
]
