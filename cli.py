#!/usr/bin/env python3
"""
🚀 SPECTROMETER UNIFIED CLI
Refactored entry point for all spectrometer tools.
"""
import sys
import argparse
from pathlib import Path

# Add core to path if needed (though running from root usually works)
sys.path.append(str(Path(__file__).parent))

from learning_engine import run_analysis

def main():
    parser = argparse.ArgumentParser(
        prog="spectrometer",
        description="🔭 Spectrometer v12 - Advanced Code Analysis & Learning System"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # ==========================================
    # ANALYZE Command
    # ==========================================
    analyze_parser = subparsers.add_parser(
        "analyze", 
        help="Analyze a repository or directory of repositories",
        description="Run the Comprehensive Learning Engine on a target codebase."
    )
    
    # Positional path argument
    analyze_parser.add_argument(
        "path",
        nargs="?",
        help="Path to the repository or directory to analyze"
    )
    
    # Flags (copied from learning_engine.py)
    analyze_parser.add_argument(
        "--mode",
        choices=["auto", "full", "minimal"],
        default="auto",
        help="Analysis mode: 'full' (tree-sitter), 'minimal' (regex), 'auto' (default)",
    )
    analyze_parser.add_argument(
        "--output",
        default="output/learning",
        help="Output directory for results",
    )
    analyze_parser.add_argument(
        "--language", 
        default=None, 
        help="Force specific language analysis"
    )
    analyze_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker processes"
    )
    analyze_parser.add_argument(
        "--no-learn",
        action="store_true",
        help="Disable auto-learning of unknown patterns"
    )
    analyze_parser.add_argument(
        "--llm",
        action="store_true",
        help="Enable LLM classification (requires Ollama)"
    )
    analyze_parser.add_argument(
        "--llm-model",
        default="qwen2.5:7b-instruct",
        help="Ollama model to use"
    )

    # ==========================================
    # HEALTH Command
    # ==========================================
    health_parser = subparsers.add_parser(
        "health",
        help="Run comprehensive system health checks (Newman Layer)",
        description="Validates integrity of static analysis, graph generation, and LLM connectivity."
    )
    
    # Parse
    args = parser.parse_args()
    
    if args.command == "health":
        from core.newman_runner import run_health_check
        sys.exit(run_health_check(exit_on_fail=True))
    
    elif args.command == "analyze":
        if not args.path:
            # Fallback to demo mode if no path provided, similar to learning_engine defaults
            # passing empty path to run_analysis which handles logic
            args.single_repo = None
            args.repos_dir = None
        else:
            path_obj = Path(args.path)
            if not path_obj.exists():
                print(f"❌ Error: Path not found: {args.path}")
                sys.exit(1)
            
            # Simple heuristic: treat as single repo by default works best for now
            # The run_analysis logic will handle it.
            args.single_repo = args.path
            args.repos_dir = None
            
        print(f"🚀 Launching Spectrometer Analysis on: {args.path or 'DEMO'}")
        run_analysis(args)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
