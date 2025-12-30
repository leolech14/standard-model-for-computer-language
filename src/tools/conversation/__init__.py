"""
Conversation Analysis Package
=============================

Modular conversation flow analysis extracted from ConversationFlowAnalyzer.

Components:
- models: DialogueMode, ConversationSegment, ConversationMap dataclasses
- patterns: Topic/mode detection patterns and visualization symbols
- parser: ConversationParser for parsing transcript files
- detector: ConversationDetector for topic/mode detection
- analyzer: ConversationAnalyzer for segmentation and hotspot detection
- visualizer: ConversationVisualizer for ASCII timeline generation
- mapper: ConversationFlowAnalyzer main facade
"""

from .models import DialogueMode, ConversationSegment, ConversationMap
from .patterns import TOPIC_PATTERNS, MODE_PATTERNS, TOPIC_SYMBOLS, MODE_SYMBOLS
from .parser import ConversationParser
from .detector import ConversationDetector
from .analyzer import ConversationAnalyzer
from .visualizer import ConversationVisualizer
from .mapper import ConversationFlowAnalyzer, main

__all__ = [
    # Models
    'DialogueMode',
    'ConversationSegment',
    'ConversationMap',

    # Patterns
    'TOPIC_PATTERNS',
    'MODE_PATTERNS',
    'TOPIC_SYMBOLS',
    'MODE_SYMBOLS',

    # Classes
    'ConversationParser',
    'ConversationDetector',
    'ConversationAnalyzer',
    'ConversationVisualizer',
    'ConversationFlowAnalyzer',

    # Functions
    'main',
]
