"""
Boundary Reporter
=================

Generates reports and visualizations from boundary analysis.
"""

from typing import Dict, List
from collections import defaultdict

from .models import Message, Section, Region
from .patterns import TYPE_SYMBOLS, PURPOSE_SYMBOLS


class BoundaryReporter:
    """Generates reports from boundary analysis results."""

    def generate_report(
        self,
        messages: List[Message],
        sections: List[Section],
        regions: List[Region]
    ) -> Dict:
        """Generate full boundary analysis report."""
        # Message stats
        user_msgs = [m for m in messages if m.type == 'user']
        ai_msgs = [m for m in messages if m.type == 'ai']

        # Interaction type distribution
        interaction_dist = defaultdict(int)
        for m in user_msgs:
            if m.interaction_type:
                interaction_dist[m.interaction_type.value] += 1

        # Purpose distribution
        purpose_dist = defaultdict(int)
        for m in user_msgs:
            if m.purpose:
                purpose_dist[m.purpose.value] += 1

        # All ideas
        all_ideas = []
        for m in user_msgs:
            all_ideas.extend(m.ideas)
        idea_freq = defaultdict(int)
        for idea in all_ideas:
            idea_freq[idea] += 1
        top_ideas = sorted(idea_freq.items(), key=lambda x: -x[1])[:20]

        # High intensity messages
        high_intensity = sorted(
            [m for m in user_msgs if m.intensity > 0.2],
            key=lambda x: -x.intensity
        )[:10]

        return {
            'summary': {
                'total_messages': len(messages),
                'user_messages': len(user_msgs),
                'ai_messages': len(ai_msgs),
                'sections': len(sections),
                'regions': len(regions),
            },
            'interaction_types': dict(interaction_dist),
            'purposes': dict(purpose_dist),
            'top_ideas': top_ideas,
            'high_intensity_moments': [
                {
                    'content': m.first_line,
                    'intensity': m.intensity,
                    'type': m.interaction_type.value if m.interaction_type else None,
                    'purpose': m.purpose.value if m.purpose else None,
                    'ideas': m.ideas,
                }
                for m in high_intensity
            ],
            'regions': [
                {
                    'index': r.index,
                    'name': r.name,
                    'sections': len(r.sections),
                    'purpose': r.dominant_purpose,
                    'ideas': r.key_ideas,
                    'lines': f"{r.start_line}-{r.end_line}",
                }
                for r in regions
            ],
            'sections': [
                {
                    'index': s.index,
                    'theme': s.theme,
                    'purpose': s.purpose,
                    'messages': len(s.messages),
                    'lines': f"{s.start_line}-{s.end_line}",
                }
                for s in sections
            ],
        }

    def generate_ascii_map(self, regions: List[Region]) -> str:
        """Generate ASCII visualization of boundaries."""
        lines = []
        lines.append("=" * 80)
        lines.append("CONVERSATION BOUNDARY MAP")
        lines.append("=" * 80)
        lines.append("")

        # Legend
        lines.append("INTERACTION TYPES:")
        lines.append("  ? question  [] command   reflection  [] feedback")
        lines.append("   clarify    challenge   agree   explore")
        lines.append("")
        lines.append("PURPOSES:")
        lines.append("   understand   decide   validate   create")
        lines.append("   debug   define   connect   visualize")
        lines.append("")
        lines.append("-" * 80)

        for region in regions:
            lines.append("")
            lines.append(f"{'=' * 76}")
            lines.append(f" REGION {region.index + 1}: {region.name[:60]:60} ")
            lines.append(f" Purpose: {region.dominant_purpose:20} Ideas: {', '.join(region.key_ideas[:3])[:40]:40} ")
            lines.append(f"{'=' * 76}")

            for section in region.sections:
                purpose_sym = PURPOSE_SYMBOLS.get(section.purpose, '')
                lines.append(f"  Section {section.index + 1}: {purpose_sym} {section.purpose:12} | Theme: {section.theme[:30]:30} ")

                # Show first 3 user messages
                user_msgs = [m for m in section.messages if m.type == 'user'][:3]
                for msg in user_msgs:
                    type_sym = TYPE_SYMBOLS.get(msg.interaction_type.value if msg.interaction_type else '', '')
                    intensity_bar = '#' * int(msg.intensity * 5)
                    preview = msg.first_line[:45] if msg.first_line else '...'
                    lines.append(f"    {type_sym} [{intensity_bar:5}] {preview:50} ")

            lines.append(f"{'=' * 76}")

        return '\n'.join(lines)
