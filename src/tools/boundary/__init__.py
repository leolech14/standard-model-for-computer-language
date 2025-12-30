"""
Boundary Package
================

Conversation boundary mapping at multiple granularities.

Maps conversations at multiple levels:
- REGIONS: Large thematic areas (10+ exchanges)
- SECTIONS: Medium groupings (3-10 exchanges)
- MESSAGES: Individual exchanges with classification
- IDEAS: Key concepts extracted
- INTERACTION TYPE: What kind of exchange
- PURPOSE: Why this message exists

Usage:
    from boundary import BoundaryMapper

    mapper = BoundaryMapper(['transcript.md'])
    mapper.parse_messages()
    mapper.identify_sections()
    mapper.identify_regions()
    report = mapper.generate_report()
"""

from .models import (
    InteractionType,
    MessagePurpose,
    Message,
    Section,
    Region,
)
from .patterns import (
    INTERACTION_PATTERNS,
    PURPOSE_PATTERNS,
    IDEA_PATTERNS,
)
from .classifier import MessageClassifier
from .parser import MessageParser
from .analyzer import BoundaryAnalyzer
from .reporter import BoundaryReporter
from .mapper import BoundaryMapper


__all__ = [
    # Main entry point
    'BoundaryMapper',

    # Models
    'InteractionType',
    'MessagePurpose',
    'Message',
    'Section',
    'Region',

    # Components
    'MessageClassifier',
    'MessageParser',
    'BoundaryAnalyzer',
    'BoundaryReporter',

    # Patterns
    'INTERACTION_PATTERNS',
    'PURPOSE_PATTERNS',
    'IDEA_PATTERNS',
]
