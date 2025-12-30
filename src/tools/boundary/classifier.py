"""
Message Classifier
==================

Classifies messages by interaction type, purpose, and ideas.
"""

import re
from typing import List
from collections import defaultdict

from .models import InteractionType, MessagePurpose
from .patterns import INTERACTION_PATTERNS, PURPOSE_PATTERNS


class MessageClassifier:
    """Classifies conversation messages."""

    def detect_interaction_type(self, text: str) -> InteractionType:
        """Detect what type of interaction this is."""
        text_lower = text.lower()
        scores = defaultdict(int)

        for itype, patterns in INTERACTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    scores[itype] += 1

        if not scores:
            return InteractionType.EXPLORATION
        return max(scores, key=scores.get)

    def detect_purpose(self, text: str) -> MessagePurpose:
        """Detect the purpose/intent of the message."""
        text_lower = text.lower()
        scores = defaultdict(int)

        for purpose, patterns in PURPOSE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    scores[purpose] += 1

        if not scores:
            return MessagePurpose.UNDERSTAND
        return max(scores, key=scores.get)

    def extract_ideas(self, text: str) -> List[str]:
        """Extract key ideas/concepts from text."""
        ideas = []

        # Get ALL CAPS terms (high emphasis)
        caps = re.findall(r'\b([A-Z]{3,}(?:\s+[A-Z]{3,})*)\b', text)
        ideas.extend(caps[:5])

        # Get quoted terms
        quoted = re.findall(r'"([^"]+)"', text)
        ideas.extend(quoted[:3])

        return list(set(ideas))[:5]

    def calculate_intensity(self, text: str) -> float:
        """Calculate emotional/emphasis intensity."""
        words = text.split()
        if not words:
            return 0.0

        caps_words = sum(1 for w in words if w.isupper() and len(w) > 2)
        exclaim = text.count('!')
        question = text.count('?')

        intensity = (caps_words / len(words)) + (exclaim * 0.1) + (question * 0.05)
        return min(1.0, intensity)
