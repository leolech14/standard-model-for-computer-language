"""
Conversation Visualizer
=======================

Generates ASCII visualizations of conversation flow.
"""

from typing import List, Dict

from .models import ConversationSegment
from .patterns import TOPIC_SYMBOLS, MODE_SYMBOLS


class ConversationVisualizer:
    """Generates visualizations of conversation flow."""

    def generate_ascii_timeline(
        self,
        segments: List[ConversationSegment],
        hotspots: List[Dict]
    ) -> str:
        """Generate ASCII visualization of conversation flow."""
        lines = []
        lines.append("=" * 80)
        lines.append("CONVERSATION FLOW TIMELINE")
        lines.append("=" * 80)
        lines.append("")

        # Legend
        lines.append("LEGEND:")
        lines.append(f"  Topics: {' '.join(f'{v}{k}' for k, v in list(TOPIC_SYMBOLS.items())[:7])}")
        lines.append(f"  Modes:  {' '.join(f'{v}{k}' for k, v in list(MODE_SYMBOLS.items())[:5])}")
        lines.append("")
        lines.append("-" * 80)

        # Timeline
        for i, seg in enumerate(segments):
            topic_sym = TOPIC_SYMBOLS.get(seg.topic, '')
            mode_sym = MODE_SYMBOLS.get(seg.mode.value, '')

            # Importance bar
            bar_len = int(seg.importance_score / 5)
            bar = '#' * bar_len + '-' * (20 - bar_len)

            # Key content preview
            preview = seg.key_content[0][:40] if seg.key_content else '...'

            lines.append(f"{i+1:3}. {topic_sym} {seg.topic:12} {mode_sym} {seg.mode.value:12} [{bar}] {seg.exchanges:2}x")
            lines.append(f"     -- {preview}...")
            lines.append("")

        lines.append("-" * 80)

        # Hotspot summary
        if hotspots:
            lines.append("")
            lines.append("HOTSPOTS (High Intensity Moments):")
            for h in hotspots[:5]:
                lines.append(f"   * {h['topic']} ({h['mode']}) - Importance: {h['importance']:.0f}")
                if h['key_content']:
                    lines.append(f"     \"{h['key_content'][0][:60]}...\"")

        return '\n'.join(lines)
