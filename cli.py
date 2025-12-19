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
        description="🔬 Standard Code Spectrometer - Analyze any codebase structure"
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
    
    # ==========================================
    # AUDIT Command
    # ==========================================
    audit_parser = subparsers.add_parser(
        "audit",
        help="Run a combined health check and minimal analysis to validate the toolchain",
        description="Performs a full audit: Newman suite + minimal repo scan to prove the pipeline works."
    )
    audit_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repository (defaults to current directory)"
    )
    audit_parser.add_argument(
        "--mode",
        choices=["minimal", "auto"],
        default="minimal",
        help="Analysis mode for the audit scan"
    )
    audit_parser.add_argument(
        "--output",
        default="output/audit",
        help="Output directory for audit artifacts"
    )

    # ==========================================
    # GRAPH Command
    # ==========================================
    graph_parser = subparsers.add_parser(
        "graph",
        help="Analyze a code graph for patterns, bottlenecks, and optimization opportunities",
        description="Run network analysis on a graph.json file produced by the analyze command."
    )
    graph_parser.add_argument(
        "graph_path",
        nargs="?",
        help="Path to graph.json file"
    )
    graph_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output path for the markdown report"
    )
    graph_parser.add_argument(
        "--top", "-n",
        type=int,
        default=20,
        help="Number of top results to show (default: 20)"
    )
    graph_parser.add_argument(
        "--shortest-path",
        default=None,
        help="Find shortest path between two functions (format: 'source:target')"
    )
    graph_parser.add_argument(
        "--bottlenecks",
        action="store_true",
        help="Show only bottleneck analysis"
    )

    # Parse
    args = parser.parse_args()
    
    if args.command == "health":
        from core.newman_runner import run_health_check
        sys.exit(run_health_check(exit_on_fail=True))
    

    elif args.command == "audit":
        from core.audit_runner import run_full_audit
        sys.exit(run_full_audit(target_path=args.path, mode=args.mode, output_dir=args.output))

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
    
    elif args.command == "graph":
        from core.graph_analyzer import analyze_full, generate_report, load_graph, shortest_path
        
        if not args.graph_path:
            print("❌ Error: graph.json path required")
            sys.exit(1)
        
        graph_path = Path(args.graph_path)
        if not graph_path.exists():
            print(f"❌ Error: Graph file not found: {args.graph_path}")
            sys.exit(1)
        
        print(f"🔬 Analyzing graph: {args.graph_path}")
        
        if args.shortest_path:
            # Handle shortest path query
            parts = args.shortest_path.split(":")
            if len(parts) != 2:
                print("❌ Error: shortest-path format should be 'source:target'")
                sys.exit(1)
            G = load_graph(graph_path)
            path = shortest_path(G, parts[0], parts[1])
            if path:
                print(f"📍 Shortest path ({len(path)} hops):")
                for i, node in enumerate(path):
                    name = node.split("|")[-2] if "|" in node else node[:50]
                    print(f"   {i+1}. {name}")
            else:
                print("❌ No path found between those nodes")
        else:
            # Full analysis
            result = analyze_full(graph_path, top_n=args.top)
            output_path = args.output or str(graph_path.parent / "GRAPH_ANALYSIS.md")
            generate_report(result, output_path)
            print(f"\n✅ Report saved to: {output_path}")
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
