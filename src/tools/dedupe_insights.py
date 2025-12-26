#!/usr/bin/env python3
"""
Deduplicate insights across multiple chat transcript files.
Merges overlapping sessions and extracts unique content.
"""

import json
import re
import hashlib
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent))
from extract_chat_insights import ChatExtractor


@dataclass
class UniqueInsight:
    """A deduplicated insight with source tracking."""
    content: str
    content_hash: str
    category: str  # 'request', 'decision', 'finding', 'action'
    importance: int
    sources: List[Dict]  # [{file, line}, ...]


def normalize_content(text: str) -> str:
    """Normalize content for comparison."""
    # Remove line numbers, whitespace variations
    text = re.sub(r'\[L\d+\]', '', text)
    text = re.sub(r'Line \d+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip().lower()
    # Remove common prefixes
    text = re.sub(r'^(we must|we need to|lets|ok\.+|go)\s*', '', text)
    return text


def content_hash(text: str) -> str:
    """Create hash of normalized content."""
    normalized = normalize_content(text)
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


def similarity_ratio(text1: str, text2: str) -> float:
    """Calculate similarity between two texts."""
    norm1 = normalize_content(text1)
    norm2 = normalize_content(text2)

    if not norm1 or not norm2:
        return 0.0

    # Simple word overlap
    words1 = set(norm1.split())
    words2 = set(norm2.split())

    if not words1 or not words2:
        return 0.0

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


class InsightDeduplicator:
    """Deduplicate insights across multiple files."""

    SIMILARITY_THRESHOLD = 0.6  # 60% word overlap = duplicate

    def __init__(self, files: List[str]):
        self.files = [Path(f) for f in files]
        self.extractors: Dict[str, ChatExtractor] = {}
        self.unique_insights: List[UniqueInsight] = []
        self.file_stats = {}
        self.overlap_matrix = {}

    def load_files(self):
        """Load and extract from all files."""
        print("Loading files...")
        for f in self.files:
            name = f.stem
            print(f"  - {name}")
            self.extractors[name] = ChatExtractor(str(f))
            self.extractors[name].parse_sections()
            self.file_stats[name] = self.extractors[name].get_statistics()

    def calculate_overlap(self):
        """Calculate content overlap between files."""
        print("\nCalculating file overlaps...")
        names = list(self.extractors.keys())

        for i, name1 in enumerate(names):
            for name2 in names[i+1:]:
                ext1 = self.extractors[name1]
                ext2 = self.extractors[name2]

                # Compare user inputs
                inputs1 = {normalize_content(u['content']) for u in ext1.extract_user_inputs()}
                inputs2 = {normalize_content(u['content']) for u in ext2.extract_user_inputs()}

                if inputs1 and inputs2:
                    overlap = len(inputs1 & inputs2) / min(len(inputs1), len(inputs2))
                    self.overlap_matrix[(name1, name2)] = overlap
                    print(f"  {name1[:20]} <-> {name2[:20]}: {overlap:.0%} overlap")

    def deduplicate(self):
        """Extract unique insights across all files."""
        print("\nDeduplicating insights...")

        all_items = []

        # Collect all insights with source info
        for name, extractor in self.extractors.items():
            # User requests
            for req in extractor.extract_user_inputs():
                all_items.append({
                    'content': req['content'][:500],
                    'category': 'request',
                    'importance': req['importance'],
                    'source': {'file': name, 'line': req['line']}
                })

            # Decisions
            for dec in extractor.extract_decisions():
                all_items.append({
                    'content': dec.content[:300],
                    'category': 'decision',
                    'importance': 5,
                    'source': {'file': name, 'line': dec.line_number}
                })

            # Findings
            for find in extractor.extract_key_findings():
                all_items.append({
                    'content': find.content[:300],
                    'category': 'finding',
                    'importance': 4,
                    'source': {'file': name, 'line': find.line_number}
                })

            # Actions
            for act in extractor.extract_action_items():
                all_items.append({
                    'content': act.content[:200],
                    'category': 'action',
                    'importance': 3,
                    'source': {'file': name, 'line': act.line_number}
                })

        print(f"  Total items before dedup: {len(all_items)}")

        # Group by similarity
        unique_groups: List[List[Dict]] = []
        used_indices = set()

        for i, item in enumerate(all_items):
            if i in used_indices:
                continue

            # Start new group
            group = [item]
            used_indices.add(i)

            # Find similar items
            for j, other in enumerate(all_items):
                if j in used_indices:
                    continue

                if item['category'] == other['category']:
                    sim = similarity_ratio(item['content'], other['content'])
                    if sim >= self.SIMILARITY_THRESHOLD:
                        group.append(other)
                        used_indices.add(j)

            unique_groups.append(group)

        # Create unique insights from groups
        for group in unique_groups:
            # Use the most important/longest as canonical
            best = max(group, key=lambda x: (x['importance'], len(x['content'])))

            self.unique_insights.append(UniqueInsight(
                content=best['content'],
                content_hash=content_hash(best['content']),
                category=best['category'],
                importance=max(g['importance'] for g in group),
                sources=[g['source'] for g in group]
            ))

        print(f"  Unique items after dedup: {len(self.unique_insights)}")

        # Sort by importance
        self.unique_insights.sort(key=lambda x: (-x.importance, -len(x.sources)))

    def get_stats(self) -> Dict:
        """Get deduplication statistics."""
        by_category = defaultdict(list)
        for insight in self.unique_insights:
            by_category[insight.category].append(insight)

        return {
            'files_processed': len(self.files),
            'total_unique': len(self.unique_insights),
            'by_category': {k: len(v) for k, v in by_category.items()},
            'overlap_matrix': {f"{k[0]} <-> {k[1]}": f"{v:.0%}" for k, v in self.overlap_matrix.items()},
            'file_stats': self.file_stats
        }

    def export_json(self, output_path: str):
        """Export deduplicated insights to JSON."""
        data = {
            'stats': self.get_stats(),
            'insights': [
                {
                    'content': i.content,
                    'hash': i.content_hash,
                    'category': i.category,
                    'importance': i.importance,
                    'sources': i.sources,
                    'source_count': len(i.sources)
                }
                for i in self.unique_insights
            ]
        }

        Path(output_path).write_text(json.dumps(data, indent=2))
        print(f"\nExported to {output_path}")

    def export_markdown(self, output_path: str):
        """Export deduplicated insights to Markdown."""
        lines = [
            "# Deduplicated Chat Insights",
            "",
            f"**Files processed:** {len(self.files)}",
            f"**Total unique insights:** {len(self.unique_insights)}",
            "",
            "## File Overlap Analysis",
            "",
        ]

        for (f1, f2), overlap in self.overlap_matrix.items():
            lines.append(f"- **{f1}** <-> **{f2}**: {overlap:.0%} overlap")

        lines.extend(["", "---", ""])

        # Group by category
        by_category = defaultdict(list)
        for insight in self.unique_insights:
            by_category[insight.category].append(insight)

        category_names = {
            'request': 'Key Requests',
            'decision': 'Decisions Made',
            'finding': 'Key Findings',
            'action': 'Action Items'
        }

        for cat, name in category_names.items():
            items = by_category.get(cat, [])
            if not items:
                continue

            lines.extend([f"## {name}", "", f"*{len(items)} unique items*", ""])

            for i, insight in enumerate(items[:30], 1):  # Top 30
                source_str = ", ".join(f"{s['file']}:L{s['line']}" for s in insight.sources[:3])
                if len(insight.sources) > 3:
                    source_str += f" (+{len(insight.sources)-3} more)"

                content = insight.content.replace('\n', ' ')[:200]
                lines.append(f"{i}. **[{insight.importance}]** {content}")
                lines.append(f"   - Sources: {source_str}")
                lines.append("")

        Path(output_path).write_text('\n'.join(lines))
        print(f"Exported to {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Deduplicate insights across chat transcripts')
    parser.add_argument('files', nargs='+', help='Chat transcript files to process')
    parser.add_argument('--output', '-o', default='output/chat_summaries', help='Output directory')
    parser.add_argument('--format', '-f', choices=['json', 'md', 'both'], default='both')

    args = parser.parse_args()

    deduper = InsightDeduplicator(args.files)
    deduper.load_files()
    deduper.calculate_overlap()
    deduper.deduplicate()

    # Print stats
    stats = deduper.get_stats()
    print(f"\n=== DEDUPLICATION RESULTS ===")
    print(f"Files: {stats['files_processed']}")
    print(f"Unique insights: {stats['total_unique']}")
    print(f"By category: {stats['by_category']}")

    # Export
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.format in ('json', 'both'):
        deduper.export_json(str(output_dir / 'deduplicated.json'))
    if args.format in ('md', 'both'):
        deduper.export_markdown(str(output_dir / 'DEDUPLICATED.md'))

    return deduper


if __name__ == '__main__':
    main()
