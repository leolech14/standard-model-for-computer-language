"""
Conversation Flow Analyzer
==========================

Main facade that combines parsing, detection, analysis, and visualization.
"""

import json
from pathlib import Path
from typing import List, Dict

from .models import ConversationSegment
from .parser import ConversationParser
from .analyzer import ConversationAnalyzer
from .visualizer import ConversationVisualizer


class ConversationFlowAnalyzer:
    """Analyzes conversation flow and creates semantic maps.

    Facade that coordinates:
    - ConversationParser: Parses transcript files into exchanges
    - ConversationAnalyzer: Segments conversations and finds hotspots
    - ConversationVisualizer: Generates ASCII/visual output
    """

    def __init__(self, files: List[str]):
        self.files = [Path(f) for f in files]
        self._parser = ConversationParser()
        self._analyzer = ConversationAnalyzer()
        self._visualizer = ConversationVisualizer()

        # State
        self.all_exchanges: List[Dict] = []
        self.segments: List[ConversationSegment] = []

    def parse_exchanges(self):
        """Parse all files into ordered exchanges."""
        self.all_exchanges = self._parser.parse_files(self.files)

        print(f"Parsed exchanges from {len(self.files)} files")
        print(f"After deduplication: {len(self.all_exchanges)} unique exchanges")

    def segment_conversation(self, window_size: int = 6):
        """Group exchanges into coherent segments."""
        if not self.all_exchanges:
            self.parse_exchanges()

        # Pair user-AI exchanges
        pairs = self._parser.pair_exchanges(self.all_exchanges)
        print(f"Found {len(pairs)} user-AI exchange pairs")

        # Segment the conversation
        self.segments = self._analyzer.segment_conversation(pairs, window_size)
        print(f"Identified {len(self.segments)} conversation segments")

        return self.segments

    def find_hotspots(self, threshold: float = 25) -> List[Dict]:
        """Find high-importance segments (hotspots)."""
        if not self.segments:
            self.segment_conversation()

        return self._analyzer.find_hotspots(self.segments, threshold)

    def generate_flow_map(self) -> Dict:
        """Generate a complete conversation flow map."""
        if not self.segments:
            self.segment_conversation()

        return self._analyzer.generate_flow_map(self.segments)

    def generate_ascii_timeline(self) -> str:
        """Generate ASCII visualization of conversation flow."""
        if not self.segments:
            self.segment_conversation()

        hotspots = self.find_hotspots()
        return self._visualizer.generate_ascii_timeline(self.segments, hotspots)

    # Backward compatibility - expose detector methods
    def detect_topic(self, text: str) -> str:
        """Detect the primary topic of a text segment."""
        return self._analyzer.detector.detect_topic(text)

    def detect_mode(self, user_text: str, ai_text: str):
        """Detect the dialogue mode of an exchange."""
        return self._analyzer.detector.detect_mode(user_text, ai_text)

    def calculate_caps_intensity(self, text: str) -> float:
        """Calculate how much ALL CAPS is used."""
        return self._analyzer.detector.calculate_caps_intensity(text)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Map conversation flow through chat transcripts'
    )
    parser.add_argument('files', nargs='+', help='Chat transcript files')
    parser.add_argument(
        '--output', '-o',
        default='output/chat_summaries',
        help='Output directory'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'ascii', 'html', 'all'],
        default='all'
    )

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
