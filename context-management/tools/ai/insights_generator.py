#!/usr/bin/env python3
"""
Collider AI Insights Generator
==============================
Simplified wrapper for generating AI insights from Collider output.

Usage:
  python insights_generator.py /path/to/unified_analysis.json
  python insights_generator.py /path/to/unified_analysis.json --output /path/to/ai_insights.json

The script:
1. Reads Collider's unified_analysis.json
2. Extracts key metrics (topology, RPBL, hubs, etc.)
3. Sends to Vertex AI Gemini for pattern analysis
4. Outputs structured ai_insights.json

Requirements:
- gcloud CLI authenticated
- Vertex AI API enabled
- GCS mirror configured
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def run_insights(collider_json: str, output: str = None, model: str = "gemini-2.0-flash-001"):
    """Run insights analysis on Collider output."""

    analyze_script = SCRIPT_DIR / "analyze.py"

    cmd = [
        sys.executable,
        str(analyze_script),
        "--mode", "insights",
        "--collider-json", collider_json,
        "--model", model,
        "--yes"  # Skip confirmation
    ]

    if output:
        cmd.extend(["--output", output])

    print(f"🔬 Generating AI Insights...")
    print(f"   Input:  {collider_json}")
    print(f"   Model:  {model}")
    if output:
        print(f"   Output: {output}")
    print()

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI insights from Collider analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (outputs to same directory as input)
  python insights_generator.py /tmp/analysis/unified_analysis.json

  # Specify output path
  python insights_generator.py /tmp/analysis/unified_analysis.json -o /tmp/insights.json

  # Use different model
  python insights_generator.py /tmp/analysis/unified_analysis.json --model gemini-1.5-pro-002
"""
    )

    parser.add_argument(
        "collider_json",
        help="Path to Collider's unified_analysis.json"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output path for ai_insights.json (default: same dir as input)"
    )
    parser.add_argument(
        "--model",
        default="gemini-2.0-flash-001",
        help="Gemini model to use (default: gemini-2.0-flash-001)"
    )

    args = parser.parse_args()

    # Validate input
    if not Path(args.collider_json).exists():
        print(f"❌ Error: File not found: {args.collider_json}")
        sys.exit(1)

    # Run analysis
    success = run_insights(
        args.collider_json,
        args.output,
        args.model
    )

    if success:
        print("\n✅ Insights generation complete!")
    else:
        print("\n❌ Insights generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
