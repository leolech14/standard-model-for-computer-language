"""
Boundary Models
===============

Data structures for conversation boundary mapping.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


class InteractionType(Enum):
    """Type of user-AI interaction."""
    QUESTION = "question"           # User asking something
    COMMAND = "command"             # User telling AI to do something
    REFLECTION = "reflection"       # User thinking aloud
    FEEDBACK = "feedback"           # User responding to AI output
    CLARIFICATION = "clarification" # User clarifying previous point
    CHALLENGE = "challenge"         # User pushing back
    AGREEMENT = "agreement"         # User confirming
    EXPLORATION = "exploration"     # Open-ended discovery


class MessagePurpose(Enum):
    """Purpose/intent of the message."""
    UNDERSTAND = "understand"       # Seeking understanding
    DECIDE = "decide"               # Making a choice
    VALIDATE = "validate"           # Checking correctness
    CREATE = "create"               # Building something
    DEBUG = "debug"                 # Fixing issues
    DEFINE = "define"               # Establishing concepts
    CONNECT = "connect"             # Linking ideas
    VISUALIZE = "visualize"         # Creating representations
    ORGANIZE = "organize"           # Structuring information
    CHALLENGE = "challenge"         # Questioning assumptions


@dataclass
class Message:
    """Individual message with full classification."""
    index: int
    type: str  # 'user' or 'ai'
    content: str
    line_start: int
    line_end: int

    # Classifications
    interaction_type: Optional[InteractionType] = None
    purpose: Optional[MessagePurpose] = None
    ideas: List[str] = field(default_factory=list)
    intensity: float = 0.0  # CAPS intensity

    # Extracted info
    first_line: str = ""
    word_count: int = 0
    has_code: bool = False
    has_question: bool = False


@dataclass
class Section:
    """Medium grouping of messages."""
    index: int
    messages: List[Message]
    theme: str
    purpose: str
    start_line: int
    end_line: int


@dataclass
class Region:
    """Large thematic area."""
    index: int
    name: str
    sections: List[Section]
    dominant_purpose: str
    key_ideas: List[str]
    start_line: int
    end_line: int
