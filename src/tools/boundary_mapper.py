#!/usr/bin/env python3
"""
Boundary Mapper (Backward Compatibility Module)
===============================================

This module re-exports from the refactored boundary package.
New code should import from src.tools.boundary directly.

Old:
    from boundary_mapper import BoundaryMapper

New:
    from boundary import BoundaryMapper
"""

import json
from pathlib import Path

# Re-export everything from the new package for backward compatibility
from boundary import (
    BoundaryMapper,
    InteractionType,
    MessagePurpose,
    Message,
    Section,
    Region,
    MessageClassifier,
    MessageParser,
    BoundaryAnalyzer,
    BoundaryReporter,
    INTERACTION_PATTERNS,
    PURPOSE_PATTERNS,
    IDEA_PATTERNS,
)

__all__ = [
    'BoundaryMapper',
    'InteractionType',
    'MessagePurpose',
    'Message',
    'Section',
    'Region',
    'MessageClassifier',
    'MessageParser',
    'BoundaryAnalyzer',
    'BoundaryReporter',
    'INTERACTION_PATTERNS',
    'PURPOSE_PATTERNS',
    'IDEA_PATTERNS',
]


# CLI for backward compatibility
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
