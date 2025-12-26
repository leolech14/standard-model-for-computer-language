#!/usr/bin/env python3
"""
Boundary Mapper - Deep analysis of conversation structure.

Maps conversations at multiple granularities:
- REGIONS: Large thematic areas (10+ exchanges)
- SECTIONS: Medium groupings (3-10 exchanges)
- MESSAGES: Individual exchanges with classification
- IDEAS: Key concepts extracted
- INTERACTION TYPE: What kind of exchange
- PURPOSE: Why this message exists
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from enum import Enum


class InteractionType(Enum):
    """Type of user-AI interaction."""
    QUESTION = "question"           # User asking something
    COMMAND = "command"             # User telling AI to do something
    REFLECTION = "reflection"       # User thinking aloud
    FEEDBACK = "feedback"           # User responding to AI output
    CLARIFICATION = "clarification" # User clarifying previous point
    CHALLENGE = "challenge"         # User pushing back
    AGREEMENT = "agreement"         # User confirming
    EXPLORATION = "exploration"     # Open-ended discovery


class MessagePurpose(Enum):
    """Purpose/intent of the message."""
    UNDERSTAND = "understand"       # Seeking understanding
    DECIDE = "decide"               # Making a choice
    VALIDATE = "validate"           # Checking correctness
    CREATE = "create"               # Building something
    DEBUG = "debug"                 # Fixing issues
    DEFINE = "define"               # Establishing concepts
    CONNECT = "connect"             # Linking ideas
    VISUALIZE = "visualize"         # Creating representations
    ORGANIZE = "organize"           # Structuring information
    CHALLENGE = "challenge"         # Questioning assumptions


@dataclass
class Message:
    """Individual message with full classification."""
    index: int
    type: str  # 'user' or 'ai'
    content: str
    line_start: int
    line_end: int

    # Classifications
    interaction_type: Optional[InteractionType] = None
    purpose: Optional[MessagePurpose] = None
    ideas: List[str] = field(default_factory=list)
    intensity: float = 0.0  # CAPS intensity

    # Extracted info
    first_line: str = ""
    word_count: int = 0
    has_code: bool = False
    has_question: bool = False


@dataclass
class Section:
    """Medium grouping of messages."""
    index: int
    messages: List[Message]
    theme: str
    purpose: str
    start_line: int
    end_line: int


@dataclass
class Region:
    """Large thematic area."""
    index: int
    name: str
    sections: List[Section]
    dominant_purpose: str
    key_ideas: List[str]
    start_line: int
    end_line: int


class BoundaryMapper:
    """Maps conversation boundaries at multiple levels."""

    # Interaction type detection
    INTERACTION_PATTERNS = {
        InteractionType.QUESTION: [
            r'\?$', r'^(what|how|why|where|when|which|who|can|does|is|are)\b',
            r'\?{2,}', r'tell me', r'explain'
        ],
        InteractionType.COMMAND: [
            r'^(do|make|create|run|execute|generate|build|add|remove|fix|update)\b',
            r'^(lets|let\'s)\b', r'^proceed', r'^continue', r'^go ahead'
        ],
        InteractionType.REFLECTION: [
            r'^(i think|i feel|i believe|seems like|maybe|perhaps)\b',
            r'^(so|ok so|alright so)\b.*\.\.\.'
        ],
        InteractionType.FEEDBACK: [
            r'^(good|great|perfect|nice|awesome|excellent)\b',
            r'^(no|nope|wrong|incorrect|not quite)\b',
            r'^(yes|yeah|yep|correct|exactly)\b'
        ],
        InteractionType.CLARIFICATION: [
            r'^(i mean|what i meant|to clarify|in other words)\b',
            r'^(no,? i meant|actually)\b'
        ],
        InteractionType.CHALLENGE: [
            r'^(but|however|wait)\b', r'\?\!', r'!!+',
            r'^(are you sure|really\?|why not)\b'
        ],
        InteractionType.AGREEMENT: [
            r'^(agreed|exactly|precisely|yes)\b',
            r'^(that\'s right|correct)\b'
        ],
    }

    # Purpose detection
    PURPOSE_PATTERNS = {
        MessagePurpose.UNDERSTAND: [
            r'what (is|are|does)', r'how (does|do|is)', r'why (is|are|does)',
            r'explain', r'tell me more', r'meaning'
        ],
        MessagePurpose.DECIDE: [
            r'should (we|i)', r'which (one|should)', r'choose', r'pick',
            r'better', r'prefer', r'option'
        ],
        MessagePurpose.VALIDATE: [
            r'(is|are) (this|that|it) (correct|right|valid)',
            r'verify', r'check', r'confirm', r'test', r'reliable'
        ],
        MessagePurpose.CREATE: [
            r'create', r'make', r'build', r'generate', r'implement',
            r'add', r'write'
        ],
        MessagePurpose.DEBUG: [
            r'error', r'bug', r'fix', r'broken', r'wrong', r'issue',
            r'not working', r'failed'
        ],
        MessagePurpose.DEFINE: [
            r'define', r'what (is|are) the', r'meaning of',
            r'(is|are) (the|these)', r'called'
        ],
        MessagePurpose.CONNECT: [
            r'relationship', r'connect', r'link', r'between',
            r'related', r'similar', r'like'
        ],
        MessagePurpose.VISUALIZE: [
            r'visual', r'diagram', r'image', r'show', r'display',
            r'represent', r'keyframe', r'infographic'
        ],
        MessagePurpose.ORGANIZE: [
            r'organize', r'structure', r'categorize', r'group',
            r'list', r'order', r'hierarchy'
        ],
        MessagePurpose.CHALLENGE: [
            r'but why', r'doesn\'t make sense', r'disagree',
            r'not sure', r'question'
        ],
    }

    # Idea extraction patterns
    IDEA_PATTERNS = [
        # Definitions
        (r'(\w+)\s+(?:is|are|means?)\s+(.{10,50})', 'definition'),
        # Comparisons
        (r'(\w+)\s+(?:like|similar to|as)\s+(\w+)', 'analogy'),
        # Key terms (ALL CAPS)
        (r'\b([A-Z]{3,}(?:\s+[A-Z]{3,})*)\b', 'key_term'),
        # Conceptual statements
        (r'(the\s+\w+\s+(?:of|is|are)\s+.{10,60})', 'concept'),
    ]

    def __init__(self, files: List[str]):
        self.files = [Path(f) for f in files]
        self.messages: List[Message] = []
        self.sections: List[Section] = []
        self.regions: List[Region] = []

    def parse_messages(self):
        """Parse all files into individual messages."""
        msg_index = 0

        for file_path in self.files:
            content = file_path.read_text()
            lines = content.split('\n')

            current_type = None
            current_content = []
            current_start = 0

            for i, line in enumerate(lines):
                if line.startswith('### User Input'):
                    if current_type and current_content:
                        msg = self._create_message(
                            msg_index, current_type,
                            '\n'.join(current_content),
                            current_start, i
                        )
                        self.messages.append(msg)
                        msg_index += 1
                    current_type = 'user'
                    current_content = []
                    current_start = i
                elif line.startswith('### Planner Response'):
                    if current_type and current_content:
                        msg = self._create_message(
                            msg_index, current_type,
                            '\n'.join(current_content),
                            current_start, i
                        )
                        self.messages.append(msg)
                        msg_index += 1
                    current_type = 'ai'
                    current_content = []
                    current_start = i
                elif current_type:
                    current_content.append(line)

            # Last message
            if current_type and current_content:
                msg = self._create_message(
                    msg_index, current_type,
                    '\n'.join(current_content),
                    current_start, len(lines)
                )
                self.messages.append(msg)
                msg_index += 1

        # Deduplicate
        seen = set()
        unique = []
        for msg in self.messages:
            key = msg.content[:200].strip()
            if key and key not in seen:
                seen.add(key)
                unique.append(msg)

        self.messages = unique
        print(f"Parsed {len(self.messages)} unique messages")

    def _create_message(self, index: int, msg_type: str, content: str,
                        start: int, end: int) -> Message:
        """Create a fully classified message."""
        # Clean content
        clean_content = content
        if '*User accepted' in clean_content:
            clean_content = clean_content.split('*User accepted')[0].strip()

        # Get first meaningful line
        first_line = ""
        for line in clean_content.split('\n'):
            line = line.strip()
            if line and len(line) > 5 and not line.startswith('```'):
                first_line = line[:100]
                break

        msg = Message(
            index=index,
            type=msg_type,
            content=clean_content,
            line_start=start,
            line_end=end,
            first_line=first_line,
            word_count=len(clean_content.split()),
            has_code='```' in content,
            has_question='?' in clean_content
        )

        # Only classify user messages
        if msg_type == 'user':
            msg.interaction_type = self._detect_interaction_type(clean_content)
            msg.purpose = self._detect_purpose(clean_content)
            msg.ideas = self._extract_ideas(clean_content)
            msg.intensity = self._calculate_intensity(clean_content)

        return msg

    def _detect_interaction_type(self, text: str) -> InteractionType:
        """Detect what type of interaction this is."""
        text_lower = text.lower()
        scores = defaultdict(int)

        for itype, patterns in self.INTERACTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    scores[itype] += 1

        if not scores:
            return InteractionType.EXPLORATION
        return max(scores, key=scores.get)

    def _detect_purpose(self, text: str) -> MessagePurpose:
        """Detect the purpose/intent of the message."""
        text_lower = text.lower()
        scores = defaultdict(int)

        for purpose, patterns in self.PURPOSE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    scores[purpose] += 1

        if not scores:
            return MessagePurpose.UNDERSTAND
        return max(scores, key=scores.get)

    def _extract_ideas(self, text: str) -> List[str]:
        """Extract key ideas/concepts from text."""
        ideas = []

        # Get ALL CAPS terms (high emphasis)
        caps = re.findall(r'\b([A-Z]{3,}(?:\s+[A-Z]{3,})*)\b', text)
        ideas.extend(caps[:5])

        # Get quoted terms
        quoted = re.findall(r'"([^"]+)"', text)
        ideas.extend(quoted[:3])

        return list(set(ideas))[:5]

    def _calculate_intensity(self, text: str) -> float:
        """Calculate emotional/emphasis intensity."""
        words = text.split()
        if not words:
            return 0.0

        caps_words = sum(1 for w in words if w.isupper() and len(w) > 2)
        exclaim = text.count('!')
        question = text.count('?')

        intensity = (caps_words / len(words)) + (exclaim * 0.1) + (question * 0.05)
        return min(1.0, intensity)

    def identify_sections(self, min_size: int = 2, max_size: int = 10):
        """Group messages into sections based on theme/purpose shifts."""
        if not self.messages:
            self.parse_messages()

        sections = []
        current_section = []
        current_purpose = None
        section_idx = 0

        for msg in self.messages:
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

        self.sections = sections
        print(f"Identified {len(self.sections)} sections")
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

    def identify_regions(self, min_sections: int = 2):
        """Group sections into large regions."""
        if not self.sections:
            self.identify_sections()

        regions = []
        current_region = []
        region_idx = 0

        # Simple grouping: every 3-5 sections
        for i, section in enumerate(self.sections):
            current_region.append(section)

            if len(current_region) >= 4 or i == len(self.sections) - 1:
                region = self._create_region(region_idx, current_region)
                regions.append(region)
                region_idx += 1
                current_region = []

        self.regions = regions
        print(f"Identified {len(self.regions)} regions")
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

    def generate_report(self) -> Dict:
        """Generate full boundary analysis report."""
        if not self.regions:
            self.identify_regions()

        # Message stats
        user_msgs = [m for m in self.messages if m.type == 'user']
        ai_msgs = [m for m in self.messages if m.type == 'ai']

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
                'total_messages': len(self.messages),
                'user_messages': len(user_msgs),
                'ai_messages': len(ai_msgs),
                'sections': len(self.sections),
                'regions': len(self.regions),
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
                for r in self.regions
            ],
            'sections': [
                {
                    'index': s.index,
                    'theme': s.theme,
                    'purpose': s.purpose,
                    'messages': len(s.messages),
                    'lines': f"{s.start_line}-{s.end_line}",
                }
                for s in self.sections
            ],
        }

    def generate_ascii_map(self) -> str:
        """Generate ASCII visualization of boundaries."""
        if not self.regions:
            self.identify_regions()

        lines = []
        lines.append("=" * 80)
        lines.append("CONVERSATION BOUNDARY MAP")
        lines.append("=" * 80)
        lines.append("")

        # Legend
        lines.append("INTERACTION TYPES:")
        lines.append("  ❓ question  📋 command  💭 reflection  📝 feedback")
        lines.append("  🔍 clarify   ⚡ challenge  ✅ agree  🌊 explore")
        lines.append("")
        lines.append("PURPOSES:")
        lines.append("  🧠 understand  ⚖️ decide  ✓ validate  🔨 create")
        lines.append("  🐛 debug  📖 define  🔗 connect  🎨 visualize")
        lines.append("")
        lines.append("-" * 80)

        type_symbols = {
            'question': '❓', 'command': '📋', 'reflection': '💭',
            'feedback': '📝', 'clarification': '🔍', 'challenge': '⚡',
            'agreement': '✅', 'exploration': '🌊'
        }

        purpose_symbols = {
            'understand': '🧠', 'decide': '⚖️', 'validate': '✓',
            'create': '🔨', 'debug': '🐛', 'define': '📖',
            'connect': '🔗', 'visualize': '🎨', 'organize': '📁',
            'challenge': '⚡'
        }

        for region in self.regions:
            lines.append("")
            lines.append(f"╔{'═' * 76}╗")
            lines.append(f"║ REGION {region.index + 1}: {region.name[:60]:60} ║")
            lines.append(f"║ Purpose: {region.dominant_purpose:20} Ideas: {', '.join(region.key_ideas[:3])[:40]:40} ║")
            lines.append(f"╠{'═' * 76}╣")

            for section in region.sections:
                purpose_sym = purpose_symbols.get(section.purpose, '•')
                lines.append(f"║  Section {section.index + 1}: {purpose_sym} {section.purpose:12} | Theme: {section.theme[:30]:30} ║")

                # Show first 3 user messages
                user_msgs = [m for m in section.messages if m.type == 'user'][:3]
                for msg in user_msgs:
                    type_sym = type_symbols.get(msg.interaction_type.value if msg.interaction_type else '', '•')
                    intensity_bar = '█' * int(msg.intensity * 5)
                    preview = msg.first_line[:45] if msg.first_line else '...'
                    lines.append(f"║    {type_sym} [{intensity_bar:5}] {preview:50} ║")

            lines.append(f"╚{'═' * 76}╝")

        return '\n'.join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Map conversation boundaries')
    parser.add_argument('files', nargs='+', help='Chat transcript files')
    parser.add_argument('--output', '-o', default='output/chat_summaries', help='Output directory')

    args = parser.parse_args()

    mapper = BoundaryMapper(args.files)
    mapper.parse_messages()
    mapper.identify_sections()
    mapper.identify_regions()

    report = mapper.generate_report()
    ascii_map = mapper.generate_ascii_map()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON report
    json_path = output_dir / 'boundary_analysis.json'
    json_path.write_text(json.dumps(report, indent=2))
    print(f"\nSaved JSON to {json_path}")

    # Save ASCII map
    ascii_path = output_dir / 'boundary_map.txt'
    ascii_path.write_text(ascii_map)
    print(f"Saved ASCII map to {ascii_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("BOUNDARY ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Messages: {report['summary']['total_messages']} ({report['summary']['user_messages']} user, {report['summary']['ai_messages']} AI)")
    print(f"Sections: {report['summary']['sections']}")
    print(f"Regions: {report['summary']['regions']}")
    print()
    print("Top Interaction Types:")
    for itype, count in sorted(report['interaction_types'].items(), key=lambda x: -x[1])[:5]:
        print(f"  {itype}: {count}")
    print()
    print("Top Purposes:")
    for purpose, count in sorted(report['purposes'].items(), key=lambda x: -x[1])[:5]:
        print(f"  {purpose}: {count}")
    print()
    print("Top Ideas/Concepts:")
    for idea, count in report['top_ideas'][:10]:
        print(f"  {idea}: {count}x")

    print("\n" + ascii_map)


if __name__ == '__main__':
    main()
