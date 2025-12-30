"""
Conversation Models
===================

Data structures for conversation flow analysis.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict


class DialogueMode(Enum):
    """Types of conversational modes."""
    QUESTIONING = "questioning"      # User asking questions
    TESTING = "testing"              # Running code/commands
    EXPLORING = "exploring"          # Open-ended discovery
    EXPLAINING = "explaining"        # AI providing explanations
    DECIDING = "deciding"            # Making choices
    BUILDING = "building"            # Creating/implementing
    DEBUGGING = "debugging"          # Fixing issues
    REFLECTING = "reflecting"        # Meta-discussion
    ONTOLOGY = "ontology"            # Deep conceptual/philosophical
    VISUALIZING = "visualizing"      # Creating diagrams/visuals


@dataclass
class ConversationSegment:
    """A segment of conversation with coherent theme."""
    start_line: int
    end_line: int
    source_file: str
    topic: str
    mode: DialogueMode
    exchanges: int  # Number of user-AI exchanges
    key_content: List[str] = field(default_factory=list)
    user_caps_intensity: float = 0.0  # How much CAPS used (0-1)
    question_density: float = 0.0  # Questions per exchange
    code_density: float = 0.0  # Code blocks per exchange
    importance_score: float = 0.0


@dataclass
class ConversationMap:
    """Full map of a conversation's journey."""
    segments: List[ConversationSegment]
    total_exchanges: int
    duration_estimate: str  # rough estimate
    topic_flow: List[str]  # ordered list of topics
    mode_distribution: Dict[str, int]
    hotspots: List[Dict]  # High-density information areas


@dataclass
class ExchangePair:
    """A paired user-AI exchange."""
    user: Dict
    ai: Dict
    index: int
