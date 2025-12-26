#!/usr/bin/env python3
"""
Conversation Flow Mapper - Analyzes the journey through chat transcripts.

Maps conversation segments by:
- Topics/themes
- Dialogue modes (questioning, testing, exploring, deciding)
- Information density hotspots
- Flow patterns

Creates a semantic map of the conversation evolution.
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from enum import Enum


class DialogueMode(Enum):
    """Types of conversational modes."""
    QUESTIONING = "questioning"      # User asking questions
    TESTING = "testing"              # Running code/commands
    EXPLORING = "exploring"          # Open-ended discovery
    EXPLAINING = "explaining"        # AI providing explanations
    DECIDING = "deciding"            # Making choices
    BUILDING = "building"            # Creating/implementing
    DEBUGGING = "debugging"          # Fixing issues
    REFLECTING = "reflecting"        # Meta-discussion
    ONTOLOGY = "ontology"            # Deep conceptual/philosophical
    VISUALIZING = "visualizing"      # Creating diagrams/visuals


@dataclass
class ConversationSegment:
    """A segment of conversation with coherent theme."""
    start_line: int
    end_line: int
    source_file: str
    topic: str
    mode: DialogueMode
    exchanges: int  # Number of user-AI exchanges
    key_content: List[str] = field(default_factory=list)
    user_caps_intensity: float = 0.0  # How much CAPS used (0-1)
    question_density: float = 0.0  # Questions per exchange
    code_density: float = 0.0  # Code blocks per exchange
    importance_score: float = 0.0


@dataclass
class ConversationMap:
    """Full map of a conversation's journey."""
    segments: List[ConversationSegment]
    total_exchanges: int
    duration_estimate: str  # rough estimate
    topic_flow: List[str]  # ordered list of topics
    mode_distribution: Dict[str, int]
    hotspots: List[Dict]  # High-density information areas


class ConversationFlowAnalyzer:
    """Analyzes conversation flow and creates semantic maps."""

    # Topic detection patterns
    TOPIC_PATTERNS = {
        'architecture': r'\b(component|architecture|system|design|structure|layer)\b',
        'atoms': r'\b(atom|particle|node|element|symbol)\b',
        'ast': r'\b(AST|syntax|tree|parse|token)\b',
        'patterns': r'\b(pattern|prefix|suffix|naming|convention)\b',
        'dimensions': r'\b(dimension|WHAT|WHERE|HOW|WHY|WHO|WHEN)\b',
        'graph': r'\b(graph|edge|connection|relationship|link)\b',
        'physics': r'\b(physics|force|mass|charge|spin|particle)\b',
        'astronomy': r'\b(star|constellation|galaxy|universe|cosmos)\b',
        'fractals': r'\b(fractal|scale|self-similar|recursive|mandel)\b',
        'roles': r'\b(Factory|Repository|Analyzer|Validator|Controller|Service)\b',
        'confidence': r'\b(confidence|accuracy|precision|coverage)\b',
        'testing': r'\b(test|benchmark|validate|verify)\b',
        'visualization': r'\b(visual|diagram|chart|image|keyframe)\b',
    }

    # Mode detection patterns
    MODE_PATTERNS = {
        DialogueMode.QUESTIONING: r'\?{1,}|\bwhat\b|\bhow\b|\bwhy\b|\bwhere\b|\bwhen\b',
        DialogueMode.TESTING: r'\*User accepted|```python|run_benchmark|pytest',
        DialogueMode.EXPLORING: r'\blet\'s\b|\bexplore\b|\bshow me\b|\bwhat if\b',
        DialogueMode.EXPLAINING: r'\bbecause\b|\bthis means\b|\bfor example\b|\bin other words\b',
        DialogueMode.DECIDING: r'\bdecided\b|\bchoose\b|\bwill use\b|\bshould\b',
        DialogueMode.BUILDING: r'\bcreate\b|\bimplement\b|\badd\b|\bbuild\b',
        DialogueMode.DEBUGGING: r'\berror\b|\bfix\b|\bissue\b|\bproblem\b',
        DialogueMode.REFLECTING: r'\blearned\b|\brealized\b|\binteresting\b|\binsight\b',
        DialogueMode.ONTOLOGY: r'[A-Z]{4,}|AS ABOVE|SO BELOW|fundamental|essence|nature of',
        DialogueMode.VISUALIZING: r'\bdiagram\b|\bvisualize\b|\bkeyframe\b|\bimage\b',
    }

    def __init__(self, files: List[str]):
        self.files = [Path(f) for f in files]
        self.all_exchanges: List[Dict] = []
        self.segments: List[ConversationSegment] = []

    def parse_exchanges(self):
        """Parse all files into ordered exchanges."""
        for file_path in self.files:
            content = file_path.read_text()
            lines = content.split('\n')

            current_type = None
            current_content = []
            current_start = 0

            for i, line in enumerate(lines):
                if line.startswith('### User Input'):
                    if current_type and current_content:
                        self.all_exchanges.append({
                            'type': current_type,
                            'content': '\n'.join(current_content),
                            'start_line': current_start,
                            'end_line': i,
                            'source': file_path.stem,
                        })
                    current_type = 'user'
                    current_content = []
                    current_start = i
                elif line.startswith('### Planner Response'):
                    if current_type and current_content:
                        self.all_exchanges.append({
                            'type': current_type,
                            'content': '\n'.join(current_content),
                            'start_line': current_start,
                            'end_line': i,
                            'source': file_path.stem,
                        })
                    current_type = 'ai'
                    current_content = []
                    current_start = i
                elif current_type:
                    current_content.append(line)

            # Don't forget last segment
            if current_type and current_content:
                self.all_exchanges.append({
                    'type': current_type,
                    'content': '\n'.join(current_content),
                    'start_line': current_start,
                    'end_line': len(lines),
                    'source': file_path.stem,
                })

        # Deduplicate exchanges (files may overlap)
        seen_content = set()
        unique_exchanges = []
        for ex in self.all_exchanges:
            # Use first 200 chars as content key
            content_key = ex['content'][:200].strip()
            if content_key and content_key not in seen_content:
                seen_content.add(content_key)
                unique_exchanges.append(ex)

        dedup_count = len(self.all_exchanges) - len(unique_exchanges)
        self.all_exchanges = unique_exchanges

        print(f"Parsed {len(self.all_exchanges) + dedup_count} exchanges from {len(self.files)} files")
        print(f"After deduplication: {len(self.all_exchanges)} unique exchanges ({dedup_count} duplicates removed)")

    def detect_topic(self, text: str) -> str:
        """Detect the primary topic of a text segment."""
        scores = {}
        text_lower = text.lower()

        for topic, pattern in self.TOPIC_PATTERNS.items():
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

        for mode, pattern in self.MODE_PATTERNS.items():
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

    def segment_conversation(self, window_size: int = 6):
        """Group exchanges into coherent segments."""
        if not self.all_exchanges:
            self.parse_exchanges()

        # Pair user-AI exchanges
        pairs = []
        i = 0
        while i < len(self.all_exchanges):
            user_ex = self.all_exchanges[i] if self.all_exchanges[i]['type'] == 'user' else None
            ai_ex = self.all_exchanges[i + 1] if i + 1 < len(self.all_exchanges) and self.all_exchanges[i + 1]['type'] == 'ai' else None

            if user_ex:
                pairs.append({
                    'user': user_ex,
                    'ai': ai_ex,
                    'index': len(pairs)
                })
                i += 2 if ai_ex else 1
            else:
                i += 1

        print(f"Found {len(pairs)} user-AI exchange pairs")

        # Sliding window to detect segment boundaries
        segments = []
        current_segment_start = 0
        current_topic = None
        current_mode = None

        for i, pair in enumerate(pairs):
            user_text = pair['user']['content'] if pair['user'] else ''
            ai_text = pair['ai']['content'] if pair['ai'] else ''

            topic = self.detect_topic(user_text + ' ' + ai_text)
            mode = self.detect_mode(user_text, ai_text)

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

        self.segments = segments
        print(f"Identified {len(segments)} conversation segments")
        return segments

    def _create_segment(self, pairs: List[Dict], topic: str, mode: DialogueMode) -> ConversationSegment:
        """Create a segment from a list of exchange pairs."""
        if not pairs:
            return None

        user_texts = [p['user']['content'] for p in pairs if p['user']]
        ai_texts = [p['ai']['content'] for p in pairs if p['ai']]

        combined_user = '\n'.join(user_texts)
        combined_ai = '\n'.join(ai_texts)
        combined = combined_user + '\n' + combined_ai

        # Extract key content (first meaningful line from each exchange)
        key_content = []
        for p in pairs[:5]:  # Top 5
            if p['user']:
                # Get all lines and find first meaningful one
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

        # Calculate metrics
        caps_intensity = self.calculate_caps_intensity(combined_user)
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
            importance_score=self._calculate_importance(combined_user, caps_intensity)
        )

    def _calculate_importance(self, user_text: str, caps_intensity: float) -> float:
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

    def find_hotspots(self, threshold: float = 25) -> List[Dict]:
        """Find high-importance segments (hotspots)."""
        if not self.segments:
            self.segment_conversation()

        hotspots = []
        for seg in self.segments:
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

    def generate_flow_map(self) -> Dict:
        """Generate a complete conversation flow map."""
        if not self.segments:
            self.segment_conversation()

        # Topic flow
        topic_flow = [seg.topic for seg in self.segments]

        # Mode distribution
        mode_dist = defaultdict(int)
        for seg in self.segments:
            mode_dist[seg.mode.value] += seg.exchanges

        # Hotspots
        hotspots = self.find_hotspots()

        return {
            'summary': {
                'total_segments': len(self.segments),
                'total_exchanges': sum(s.exchanges for s in self.segments),
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
                for s in self.segments
            ]
        }

    def generate_ascii_timeline(self) -> str:
        """Generate ASCII visualization of conversation flow."""
        if not self.segments:
            self.segment_conversation()

        lines = []
        lines.append("=" * 80)
        lines.append("CONVERSATION FLOW TIMELINE")
        lines.append("=" * 80)
        lines.append("")

        # Topic legend
        topic_symbols = {
            'architecture': '🏗',
            'atoms': '⚛',
            'ast': '🌳',
            'patterns': '🔍',
            'dimensions': '📐',
            'graph': '🕸',
            'physics': '🔬',
            'astronomy': '🌌',
            'fractals': '🌀',
            'roles': '🎭',
            'confidence': '📊',
            'testing': '🧪',
            'visualization': '🎨',
            'general': '💬',
        }

        mode_symbols = {
            'questioning': '❓',
            'testing': '🔧',
            'exploring': '🔎',
            'explaining': '💡',
            'deciding': '⚖️',
            'building': '🔨',
            'debugging': '🐛',
            'reflecting': '🤔',
            'ontology': '🔮',
            'visualizing': '🖼',
        }

        lines.append("LEGEND:")
        lines.append(f"  Topics: {' '.join(f'{v}{k}' for k, v in list(topic_symbols.items())[:7])}")
        lines.append(f"  Modes:  {' '.join(f'{v}{k}' for k, v in list(mode_symbols.items())[:5])}")
        lines.append("")
        lines.append("-" * 80)

        # Timeline
        for i, seg in enumerate(self.segments):
            topic_sym = topic_symbols.get(seg.topic, '•')
            mode_sym = mode_symbols.get(seg.mode.value, '•')

            # Importance bar
            bar_len = int(seg.importance_score / 5)
            bar = '█' * bar_len + '░' * (20 - bar_len)

            # Key content preview
            preview = seg.key_content[0][:40] if seg.key_content else '...'

            lines.append(f"{i+1:3}. {topic_sym} {seg.topic:12} {mode_sym} {seg.mode.value:12} [{bar}] {seg.exchanges:2}x")
            lines.append(f"     └─ {preview}...")
            lines.append("")

        lines.append("-" * 80)

        # Hotspot summary
        hotspots = self.find_hotspots()
        if hotspots:
            lines.append("")
            lines.append("🔥 HOTSPOTS (High Intensity Moments):")
            for h in hotspots[:5]:
                lines.append(f"   • {h['topic']} ({h['mode']}) - Importance: {h['importance']:.0f}")
                if h['key_content']:
                    lines.append(f"     \"{h['key_content'][0][:60]}...\"")

        return '\n'.join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Map conversation flow through chat transcripts')
    parser.add_argument('files', nargs='+', help='Chat transcript files')
    parser.add_argument('--output', '-o', default='output/chat_summaries', help='Output directory')
    parser.add_argument('--format', '-f', choices=['json', 'ascii', 'html', 'all'], default='all')

    args = parser.parse_args()

    analyzer = ConversationFlowAnalyzer(args.files)
    analyzer.parse_exchanges()
    analyzer.segment_conversation()

    flow_map = analyzer.generate_flow_map()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.format in ('json', 'all'):
        json_path = output_dir / 'conversation_flow.json'
        json_path.write_text(json.dumps(flow_map, indent=2))
        print(f"Saved JSON to {json_path}")

    if args.format in ('ascii', 'all'):
        timeline = analyzer.generate_ascii_timeline()
        print("\n" + timeline)

        ascii_path = output_dir / 'conversation_timeline.txt'
        ascii_path.write_text(timeline)
        print(f"\nSaved timeline to {ascii_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("CONVERSATION FLOW SUMMARY")
    print("=" * 60)
    print(f"Total segments: {flow_map['summary']['total_segments']}")
    print(f"Total exchanges: {flow_map['summary']['total_exchanges']}")
    print(f"Topics covered: {', '.join(flow_map['summary']['unique_topics'])}")
    print(f"Dominant mode: {flow_map['summary']['dominant_mode']}")
    print(f"Hotspots found: {len(flow_map['hotspots'])}")


if __name__ == '__main__':
    main()
