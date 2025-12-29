"""
🚀 COLLIDER UNIFIED CLI
Refactored entry point for all standard model tools.
"""
import sys
import argparse
from pathlib import Path

# Add root to path to ensure modules are found
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src"))

# Import the robust prove engine
from src.tools.prove import run_proof

def main():
    parser = argparse.ArgumentParser(
        prog="collider",
        description="🔬 Collider - Standard Model of Code - Analyze any codebase structure"
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
    
    # Flags
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

    # ==========================================
    # VIZ Command
    # ==========================================
    viz_parser = subparsers.add_parser(
        "viz",
        help="Generate interactive HTML visualization",
        description="Creates a robust, interactive HTML visualization from a graph.json file."
    )
    viz_parser.add_argument(
        "graph_path",
        help="Path to graph.json file"
    )
    viz_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output path for the HTML file"
    )

    # ==========================================
    # DASHBOARD Command
    # ==========================================
    dash_parser = subparsers.add_parser(
        "dashboard",
        help="Generate interactive HTML dashboard from analysis",
        description="Creates a visual dashboard with 8D coverage, atom distribution, and Math Engine metrics."
    )
    dash_parser.add_argument(
        "analysis_path",
        help="Path to unified_analysis.json file"
    )
    dash_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output path for the HTML dashboard"
    )
    dash_parser.add_argument(
        "--title", "-t",
        default="Collider Analysis Dashboard",
        help="Dashboard title"
    )

    # ==========================================
    # ISSUES Command
    # ==========================================
    issues_parser = subparsers.add_parser(
        "issues",
        help="Generate GitHub Issues from analysis insights",
        description="Creates actionable tickets for code quality improvements, violations, and tech debt."
    )
    issues_parser.add_argument(
        "analysis_path",
        help="Path to unified_analysis.json file"
    )
    issues_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output path for issues file"
    )
    issues_parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    # ==========================================
    # FIX Command (Consolidated from FixGenerator)
    # ==========================================
    fix_parser = subparsers.add_parser(
        "fix",
        help="Generate fix code for optimization schemas",
        description="Generates scaffolding code for architectural patterns (Repositories, Services, etc.)."
    )
    fix_parser.add_argument(
        "--schema", "-s",
        required=True,
        choices=["REPOSITORY_PATTERN", "TEST_COVERAGE", "SERVICE_EXTRACTION", "CQRS_SEPARATION", "GOD_CLASS_DECOMPOSITION"],
        help="Optimization schema to generate code for"
    )
    fix_parser.add_argument(
        "--entity", "-e",
        default="Entity",
        help="Name of the entity/component (e.g. 'User')"
    )
    fix_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (prints to stdout if not specified)"
    )

    # ==========================================
    # ENRICH Command (LLM Classification)
    # ==========================================
    enrich_parser = subparsers.add_parser(
        "enrich",
        help="Enrich unknown atoms using LLM classification",
        description="Uses LLM (Claude or Ollama) to classify unknown code entities."
    )
    enrich_parser.add_argument(
        "analysis_path",
        help="Path to unified_analysis.json file"
    )
    enrich_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output path for enriched results"
    )
    enrich_parser.add_argument(
        "--limit", "-n",
        type=int,
        default=100,
        help="Maximum entities to classify (default: 100)"
    )
    enrich_parser.add_argument(
        "--backend", "-b",
        choices=["auto", "ollama", "claude", "heuristic"],
        default="auto",
        help="LLM backend to use (default: auto)"
    )
    enrich_parser.add_argument(
        "--model", "-m",
        default="qwen2.5:7b-instruct",
        help="Model name (default: qwen2.5:7b-instruct for Ollama)"
    )

    # Parse
    args = parser.parse_args()
    
    if args.command == "health":
        from core.newman_runner import run_health_check
        sys.exit(run_health_check(exit_on_fail=True))
    

    elif args.command == "audit":
        from core.audit_runner import run_full_audit
        sys.exit(run_full_audit(target_path=args.path, output_dir=args.output))

    elif args.command == "analyze":
        if not args.path:
            print("❌ Error: path argument is required for analyze command")
            print("Usage: collider analyze <path_to_code>")
            sys.exit(1)

        print(f"🚀 Launching Collider Analysis on: {args.path}")
        try:
            run_proof(
                args.path, 
                llm=args.llm, 
                llm_model=args.llm_model,
                language=args.language,
                no_learn=args.no_learn,
                output_dir=args.output
            )
            # The run_proof function generates the spectrometer_report.html
            print("\n✅ Analysis complete. Visualization report generated.")
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            sys.exit(1)
    
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
    
            print(f"\n✅ Report saved to: {output_path}")

    elif args.command == "viz":
        from core.viz_generator import VisualizationGenerator
        
        graph_path = Path(args.graph_path)
        output_path = Path(args.output) if args.output else graph_path.parent / "collider_viz.html"
        
        generator = VisualizationGenerator()
        try:
            saved_path = generator.generate(graph_path, output_path)
            print(f"✅ Visualization generated: {saved_path}")
        except Exception as e:
            print(f"❌ Error generating visualization: {e}")
            sys.exit(1)

    elif args.command == "dashboard":
        from core.dashboard_generator import generate_dashboard

        analysis_path = Path(args.analysis_path)
        if not analysis_path.exists():
            print(f"❌ Error: Analysis file not found: {args.analysis_path}")
            sys.exit(1)

        try:
            output_path = generate_dashboard(
                str(analysis_path),
                args.output,
                args.title
            )
            print(f"✅ Dashboard generated: {output_path}")
        except Exception as e:
            print(f"❌ Error generating dashboard: {e}")
            sys.exit(1)

    elif args.command == "issues":
        from core.github_issues_generator import generate_issues

        analysis_path = Path(args.analysis_path)
        if not analysis_path.exists():
            print(f"❌ Error: Analysis file not found: {args.analysis_path}")
            sys.exit(1)

        try:
            output_path = generate_issues(
                str(analysis_path),
                args.output,
                args.format
            )
            print(f"✅ GitHub Issues generated: {output_path}")
        except Exception as e:
            print(f"❌ Error generating issues: {e}")
            sys.exit(1)

    elif args.command == "fix":
        from core.fix_generator import FixGenerator

        generator = FixGenerator("python") # Default to python for now
        
        # Context building
        context = {
            "entity": args.entity.lower(),
            "Entity": args.entity.capitalize(),
            "component": args.entity,
            "Component": args.entity.capitalize(),
            "class": args.entity,
            "Class": args.entity.capitalize()
        }
        
        template = generator.generate_fix(args.schema, context)
        
        if template:
            if args.output:
                out_path = Path(args.output)
                with open(out_path, 'w') as f:
                    f.write(template.code)
                print(f"✅ Generated {args.schema} implementation at {out_path}")
            else:
                print(f"# {template.filename}")
                print(template.code)
        else:
            print(f"❌ Could not generate fix for schema: {args.schema}")
            sys.exit(1)

    elif args.command == "enrich":
        from core.llm_classifier import LLMClassifier
        import json

        analysis_path = Path(args.analysis_path)
        if not analysis_path.exists():
            print(f"Error: Analysis file not found: {args.analysis_path}")
            sys.exit(1)

        print(f"Loading analysis from {args.analysis_path}...")

        with open(analysis_path) as f:
            data = json.load(f)

        # Extract unknowns
        unknowns = [
            node for node in data.get('nodes', [])
            if node.get('role') == 'Unknown' or node.get('dimensions', {}).get('D3_ROLE') == 'Unknown'
        ]

        print(f"Found {len(unknowns)} unknown entities")
        print(f"Using backend: {args.backend}, model: {args.model}")

        classifier = LLMClassifier(model_name=args.model, backend=args.backend)

        # Classify unknowns
        results = []
        for i, node in enumerate(unknowns[:args.limit]):
            context = f"Name: {node.get('name')}\nKind: {node.get('kind')}\nFile: {node.get('file_path')}"
            if node.get('body_source'):
                context += f"\nBody: {node['body_source'][:300]}"

            role, confidence = classifier.classify_with_llm(context)
            results.append({
                "name": node.get('name'),
                "role": role,
                "confidence": confidence,
                "file": node.get('file_path')
            })

            if (i + 1) % 10 == 0:
                print(f"  Classified {i + 1}/{min(len(unknowns), args.limit)}...")

        # Summary
        role_counts = {}
        for r in results:
            role = r['role']
            role_counts[role] = role_counts.get(role, 0) + 1

        print(f"\nResults by role:")
        for role, count in sorted(role_counts.items(), key=lambda x: -x[1]):
            print(f"  {role}: {count}")

        # Save results
        output_path = args.output or str(analysis_path.parent / "llm_enriched.json")
        with open(output_path, 'w') as f:
            json.dump({
                "total_classified": len(results),
                "by_role": role_counts,
                "backend": classifier.get_stats()['backend'],
                "results": results
            }, f, indent=2)

        print(f"\nSaved to {output_path}")
        print(f"Stats: {classifier.get_stats()}")

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
