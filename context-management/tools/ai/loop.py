#!/usr/bin/env python3
"""
THE LOOP: Gemini → Perplexity → Gemini Validation Workflow
============================================================

A convenience wrapper that executes the research validation loop:
1. [Optional] Gemini analyzes context/formulates question
2. Perplexity provides external research
3. [Optional] Gemini synthesizes with local context

Usage:
    # Direct Perplexity query (simplest)
    python loop.py "your research question"

    # With Gemini synthesis (adds local context)
    python loop.py --synthesize "your research question"

    # Full loop: Gemini formulates → Perplexity researches → Gemini integrates
    python loop.py --full "rough question or topic"

Examples:
    python loop.py "What is the academic term for meta-languages that visualize code?"
    python loop.py --synthesize "Is b₂ (Betti number) needed for software dependency graphs?"
    python loop.py --full "validate our topology implementation approach"
"""

import argparse
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
ANALYZE_PY = SCRIPT_DIR / "analyze.py"
PERPLEXITY_PY = SCRIPT_DIR / "perplexity_research.py"


def run_perplexity(query: str, model: str = "sonar-pro") -> str:
    """Run Perplexity research query."""
    result = subprocess.run(
        [sys.executable, str(PERPLEXITY_PY), "--model", model, query],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        print(f"Perplexity error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def run_gemini(prompt: str, context_set: str = "theory") -> str:
    """Run Gemini with local context."""
    result = subprocess.run(
        [sys.executable, str(ANALYZE_PY), "--set", context_set, "--force-oneshot", prompt],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        print(f"Gemini error: {result.stderr}", file=sys.stderr)
        # Don't exit - Gemini might fail due to API key issues
        return ""
    return result.stdout


def main():
    parser = argparse.ArgumentParser(
        description="THE LOOP: Research validation workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("query", help="Research question or topic")
    parser.add_argument("--synthesize", "-s", action="store_true",
                        help="Add Gemini synthesis with local context after Perplexity")
    parser.add_argument("--full", "-f", action="store_true",
                        help="Full loop: Gemini formulate → Perplexity → Gemini integrate")
    parser.add_argument("--model", "-m", default="sonar-pro",
                        choices=["sonar", "sonar-pro", "sonar-reasoning", "sonar-deep-research"],
                        help="Perplexity model (default: sonar-pro)")
    parser.add_argument("--context", "-c", default="theory",
                        help="Context set for Gemini (default: theory)")

    args = parser.parse_args()

    print("=" * 60)
    print("THE LOOP: Research Validation Workflow")
    print("=" * 60)

    # Step 1: Formulate (if full mode)
    research_query = args.query
    if args.full:
        print("\n[STEP 1/3] Gemini formulating research question...")
        formulation_prompt = f"""Given this rough topic/question, formulate a clear, specific
research question suitable for external validation via Perplexity:

TOPIC: {args.query}

Provide ONLY the research question, no explanation."""
        formulated = run_gemini(formulation_prompt, args.context)
        if formulated.strip():
            research_query = formulated.strip()
            print(f"Formulated: {research_query[:100]}...")
        else:
            print("(Using original query)")

    # Step 2: Perplexity Research
    step_num = "2/3" if args.full else ("1/2" if args.synthesize else "1/1")
    print(f"\n[STEP {step_num}] Perplexity researching...")
    print(f"Query: {research_query[:100]}...")
    perplexity_result = run_perplexity(research_query, args.model)

    print("\n" + "=" * 60)
    print("PERPLEXITY RESULT")
    print("=" * 60)
    print(perplexity_result)

    # Step 3: Synthesize (if requested)
    if args.synthesize or args.full:
        step_num = "3/3" if args.full else "2/2"
        print(f"\n[STEP {step_num}] Gemini synthesizing with local context...")
        synthesis_prompt = f"""Synthesize this external research with our local codebase context.

ORIGINAL QUESTION: {args.query}

PERPLEXITY RESEARCH:
{perplexity_result[:4000]}

Provide:
1. Key validated findings
2. How this applies to our Standard Model of Code
3. Recommended actions or updates to documentation"""

        synthesis = run_gemini(synthesis_prompt, args.context)
        if synthesis.strip():
            print("\n" + "=" * 60)
            print("GEMINI SYNTHESIS")
            print("=" * 60)
            print(synthesis)

    print("\n[LOOP COMPLETE]")


if __name__ == "__main__":
    main()
