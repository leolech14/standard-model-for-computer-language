"""
Conversation Detector
=====================

Detects topics, modes, and calculates metrics.
"""

import re
from typing import Dict, List

from .models import DialogueMode, ConversationSegment
from .patterns import TOPIC_PATTERNS, MODE_PATTERNS


class ConversationDetector:
    """Detects topics and modes in conversation exchanges."""

    def detect_topic(self, text: str) -> str:
        """Detect the primary topic of a text segment."""
        scores = {}
        text_lower = text.lower()

        for topic, pattern in TOPIC_PATTERNS.items():
            matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
            if matches > 0:
                scores[topic] = matches

        if not scores:
            return 'general'

        return max(scores, key=scores.get)

    def detect_mode(self, user_text: str, ai_text: str) -> DialogueMode:
        """Detect the dialogue mode of an exchange."""
        combined = user_text + ' ' + ai_text
        scores = {}

        for mode, pattern in MODE_PATTERNS.items():
            matches = len(re.findall(pattern, combined, re.IGNORECASE))
            if matches > 0:
                scores[mode] = matches

        if not scores:
            return DialogueMode.EXPLORING

        return max(scores, key=scores.get)

    def calculate_caps_intensity(self, text: str) -> float:
        """Calculate how much ALL CAPS is used (intensity of emphasis)."""
        words = text.split()
        if not words:
            return 0.0

        caps_words = sum(1 for w in words if w.isupper() and len(w) > 2)
        return min(1.0, caps_words / max(1, len(words)))

    def calculate_importance(self, user_text: str, caps_intensity: float) -> float:
        """Calculate importance score for a segment."""
        score = 0.0

        # Caps intensity is a strong signal
        score += caps_intensity * 30

        # Question marks indicate inquiry
        score += min(10, user_text.count('?') * 2)

        # Exclamation marks indicate emphasis
        score += min(10, user_text.count('!') * 1.5)

        # Key phrases
        key_phrases = ['fundamental', 'important', 'key', 'must', 'essential', 'why', 'how']
        for phrase in key_phrases:
            if phrase in user_text.lower():
                score += 3

        return min(100, score)

    def extract_key_content(self, pairs: List[Dict], limit: int = 5) -> List[str]:
        """Extract key content from exchange pairs."""
        key_content = []

        for p in pairs[:limit]:
            if p['user']:
                lines = p['user']['content'].split('\n')
                for line in lines:
                    line = line.strip()
                    # Skip empty, command noise, or markdown artifacts
                    if not line or line.startswith('*User accepted') or line.startswith('```'):
                        continue
                    # Skip very short lines
                    if len(line) < 5:
                        continue
                    # Found a good line
                    key_content.append(line[:150])
                    break

        return key_content
