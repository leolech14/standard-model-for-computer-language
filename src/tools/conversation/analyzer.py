"""
Conversation Analyzer
=====================

Segments conversations and finds hotspots.
"""

from typing import List, Dict
from collections import defaultdict

from .models import DialogueMode, ConversationSegment
from .detector import ConversationDetector


class ConversationAnalyzer:
    """Analyzes and segments conversations."""

    def __init__(self):
        self.detector = ConversationDetector()

    def segment_conversation(
        self,
        pairs: List[Dict],
        window_size: int = 6
    ) -> List[ConversationSegment]:
        """Group exchanges into coherent segments."""
        segments = []
        current_segment_start = 0
        current_topic = None
        current_mode = None

        for i, pair in enumerate(pairs):
            user_text = pair['user']['content'] if pair['user'] else ''
            ai_text = pair['ai']['content'] if pair['ai'] else ''

            topic = self.detector.detect_topic(user_text + ' ' + ai_text)
            mode = self.detector.detect_mode(user_text, ai_text)

            # Detect segment boundary (topic or mode change)
            topic_changed = current_topic and topic != current_topic
            mode_changed = current_mode and mode != current_mode

            # Create new segment on significant change
            if (topic_changed or mode_changed) and i - current_segment_start >= 2:
                segment = self._create_segment(
                    pairs[current_segment_start:i],
                    current_topic or topic,
                    current_mode or mode
                )
                segments.append(segment)
                current_segment_start = i

            current_topic = topic
            current_mode = mode

        # Final segment
        if current_segment_start < len(pairs):
            segment = self._create_segment(
                pairs[current_segment_start:],
                current_topic or 'general',
                current_mode or DialogueMode.EXPLORING
            )
            segments.append(segment)

        return segments

    def _create_segment(
        self,
        pairs: List[Dict],
        topic: str,
        mode: DialogueMode
    ) -> ConversationSegment:
        """Create a segment from a list of exchange pairs."""
        if not pairs:
            return None

        user_texts = [p['user']['content'] for p in pairs if p['user']]
        ai_texts = [p['ai']['content'] for p in pairs if p['ai']]

        combined_user = '\n'.join(user_texts)
        combined_ai = '\n'.join(ai_texts)
        combined = combined_user + '\n' + combined_ai

        # Extract key content
        key_content = self.detector.extract_key_content(pairs)

        # Calculate metrics
        caps_intensity = self.detector.calculate_caps_intensity(combined_user)
        question_count = combined_user.count('?')
        code_blocks = combined.count('```')

        return ConversationSegment(
            start_line=pairs[0]['user']['start_line'] if pairs[0]['user'] else 0,
            end_line=pairs[-1]['ai']['end_line'] if pairs[-1]['ai'] else pairs[-1]['user']['end_line'],
            source_file=pairs[0]['user']['source'] if pairs[0]['user'] else 'unknown',
            topic=topic,
            mode=mode,
            exchanges=len(pairs),
            key_content=key_content,
            user_caps_intensity=caps_intensity,
            question_density=question_count / max(1, len(pairs)),
            code_density=code_blocks / max(1, len(pairs)),
            importance_score=self.detector.calculate_importance(combined_user, caps_intensity)
        )

    def find_hotspots(
        self,
        segments: List[ConversationSegment],
        threshold: float = 25
    ) -> List[Dict]:
        """Find high-importance segments (hotspots)."""
        hotspots = []

        for seg in segments:
            if seg.importance_score >= threshold:
                hotspots.append({
                    'topic': seg.topic,
                    'mode': seg.mode.value,
                    'importance': seg.importance_score,
                    'exchanges': seg.exchanges,
                    'key_content': seg.key_content[:3],
                    'location': f"{seg.source_file}:{seg.start_line}-{seg.end_line}",
                    'caps_intensity': seg.user_caps_intensity,
                })

        return sorted(hotspots, key=lambda x: -x['importance'])

    def generate_flow_map(self, segments: List[ConversationSegment]) -> Dict:
        """Generate a complete conversation flow map."""
        # Topic flow
        topic_flow = [seg.topic for seg in segments]

        # Mode distribution
        mode_dist = defaultdict(int)
        for seg in segments:
            mode_dist[seg.mode.value] += seg.exchanges

        # Hotspots
        hotspots = self.find_hotspots(segments)

        return {
            'summary': {
                'total_segments': len(segments),
                'total_exchanges': sum(s.exchanges for s in segments),
                'unique_topics': list(set(topic_flow)),
                'dominant_mode': max(mode_dist, key=mode_dist.get) if mode_dist else 'exploring',
            },
            'topic_flow': topic_flow,
            'mode_distribution': dict(mode_dist),
            'hotspots': hotspots[:20],
            'segments': [
                {
                    'topic': s.topic,
                    'mode': s.mode.value,
                    'exchanges': s.exchanges,
                    'importance': s.importance_score,
                    'caps_intensity': s.user_caps_intensity,
                    'key_content': s.key_content[:2],
                    'location': f"{s.source_file}:{s.start_line}",
                }
                for s in segments
            ]
        }
