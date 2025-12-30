"""
Boundary Analyzer
=================

Identifies sections and regions in conversation messages.
"""

from typing import List

from .models import Message, Section, Region, MessagePurpose


class BoundaryAnalyzer:
    """Analyzes message boundaries to identify sections and regions."""

    def identify_sections(
        self,
        messages: List[Message],
        min_size: int = 2,
        max_size: int = 10
    ) -> List[Section]:
        """Group messages into sections based on theme/purpose shifts."""
        sections = []
        current_section = []
        current_purpose = None
        section_idx = 0

        for msg in messages:
            if msg.type != 'user':
                current_section.append(msg)
                continue

            # Check for section boundary
            new_purpose = msg.purpose
            purpose_changed = current_purpose and new_purpose != current_purpose
            section_too_big = len(current_section) >= max_size * 2

            if (purpose_changed or section_too_big) and len(current_section) >= min_size * 2:
                section = self._create_section(section_idx, current_section)
                sections.append(section)
                section_idx += 1
                current_section = []

            current_section.append(msg)
            current_purpose = new_purpose

        # Final section
        if current_section:
            section = self._create_section(section_idx, current_section)
            sections.append(section)

        return sections

    def _create_section(self, idx: int, messages: List[Message]) -> Section:
        """Create a section from messages."""
        user_msgs = [m for m in messages if m.type == 'user']

        # Determine dominant purpose
        purposes = [m.purpose for m in user_msgs if m.purpose]
        purpose = max(set(purposes), key=purposes.count) if purposes else MessagePurpose.UNDERSTAND

        # Determine theme from ideas
        all_ideas = []
        for m in user_msgs:
            all_ideas.extend(m.ideas)
        theme = all_ideas[0] if all_ideas else "general"

        return Section(
            index=idx,
            messages=messages,
            theme=theme,
            purpose=purpose.value,
            start_line=messages[0].line_start,
            end_line=messages[-1].line_end
        )

    def identify_regions(
        self,
        sections: List[Section],
        min_sections: int = 2
    ) -> List[Region]:
        """Group sections into large regions."""
        regions = []
        current_region = []
        region_idx = 0

        # Simple grouping: every 3-5 sections
        for i, section in enumerate(sections):
            current_region.append(section)

            if len(current_region) >= 4 or i == len(sections) - 1:
                region = self._create_region(region_idx, current_region)
                regions.append(region)
                region_idx += 1
                current_region = []

        return regions

    def _create_region(self, idx: int, sections: List[Section]) -> Region:
        """Create a region from sections."""
        # Collect all ideas
        all_ideas = []
        for section in sections:
            for msg in section.messages:
                if msg.type == 'user':
                    all_ideas.extend(msg.ideas)

        # Determine dominant purpose
        purposes = [s.purpose for s in sections]
        dominant = max(set(purposes), key=purposes.count) if purposes else "understand"

        # Name from top ideas
        top_ideas = list(set(all_ideas))[:3]
        name = " + ".join(top_ideas) if top_ideas else f"Region {idx+1}"

        return Region(
            index=idx,
            name=name,
            sections=sections,
            dominant_purpose=dominant,
            key_ideas=top_ideas,
            start_line=sections[0].start_line,
            end_line=sections[-1].end_line
        )
