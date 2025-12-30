#!/usr/bin/env python3
"""
Conversation Flow Mapper - Analyzes the journey through chat transcripts.

REFACTORED: This module now re-exports from the conversation/ package.
The monolithic implementation has been split into:
- conversation/models.py: DialogueMode, ConversationSegment, ConversationMap
- conversation/patterns.py: Topic/mode detection patterns
- conversation/parser.py: ConversationParser
- conversation/detector.py: ConversationDetector
- conversation/analyzer.py: ConversationAnalyzer
- conversation/visualizer.py: ConversationVisualizer
- conversation/mapper.py: ConversationFlowAnalyzer facade

All original imports continue to work for backward compatibility.
"""

# Re-export everything from the conversation package
# Use try/except to support both relative and absolute imports
try:
    from .conversation import (
        DialogueMode,
        ConversationSegment,
        ConversationMap,
        TOPIC_PATTERNS,
        MODE_PATTERNS,
        TOPIC_SYMBOLS,
        MODE_SYMBOLS,
        ConversationParser,
        ConversationDetector,
        ConversationAnalyzer,
        ConversationVisualizer,
        ConversationFlowAnalyzer,
        main,
    )
except ImportError:
    from conversation import (
        DialogueMode,
        ConversationSegment,
        ConversationMap,
        TOPIC_PATTERNS,
        MODE_PATTERNS,
        TOPIC_SYMBOLS,
        MODE_SYMBOLS,
        ConversationParser,
        ConversationDetector,
        ConversationAnalyzer,
        ConversationVisualizer,
        ConversationFlowAnalyzer,
        main,
    )

__all__ = [
    'DialogueMode',
    'ConversationSegment',
    'ConversationMap',
    'TOPIC_PATTERNS',
    'MODE_PATTERNS',
    'TOPIC_SYMBOLS',
    'MODE_SYMBOLS',
    'ConversationParser',
    'ConversationDetector',
    'ConversationAnalyzer',
    'ConversationVisualizer',
    'ConversationFlowAnalyzer',
    'main',
]

if __name__ == '__main__':
    main()
