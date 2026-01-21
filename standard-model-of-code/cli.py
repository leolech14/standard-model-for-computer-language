"""
🚀 COLLIDER UNIFIED CLI
Refactored entry point for all standard model tools.
"""
import sys
import os
import argparse
import re
import tempfile
from datetime import datetime
from pathlib import Path

# Add root to path to ensure modules are found
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))


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
        help="Analyze a repository and emit the canonical output bundle",
        description="Runs the canonical full analysis and produces both LLM-oriented JSON and human-readable HTML."
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
        default=None,
        help="Output directory for results (defaults to <repo>/.collider)",
    )
    analyze_open = analyze_parser.add_mutually_exclusive_group()
    analyze_open.add_argument(
        "--open",
        dest="open_latest",
        action="store_true",
        help="Open newest HTML output after analysis",
    )
    analyze_open.add_argument(
        "--no-open",
        dest="open_latest",
        action="store_false",
        help="Do not open HTML output after analysis",
    )
    analyze_parser.set_defaults(open_latest=None)
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
    # DOCTOR Command - Contract Validation
    # ==========================================
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Run pipeline + output contract validation",
        description="Runs analysis, normalizes outputs, and validates canonical output contract."
    )
    doctor_parser.add_argument(
        "path",
        help="Path to the repository or directory to analyze"
    )
    doctor_parser.add_argument(
        "--output",
        default=None,
        help="Optional output directory for doctor artifacts"
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
    # FULL Command - Complete Analysis
    # ==========================================
    full_parser = subparsers.add_parser(
        "full",
        help="Run complete deterministic analysis with all theoretical frameworks",
        description="Single command for Markov chains, knot detection, data flow, and complete Standard Model."
    )
    full_parser.add_argument(
        "path",
        help="Path to the repository to analyze"
    )
    full_parser.add_argument(
        "--output",
        default=None,
        help="Output directory for results (defaults to <repo>/.collider)"
    )
    full_open = full_parser.add_mutually_exclusive_group()
    full_open.add_argument(
        "--open",
        dest="open_latest",
        action="store_true",
        help="Open newest HTML output after analysis",
    )
    full_open.add_argument(
        "--no-open",
        dest="open_latest",
        action="store_false",
        help="Do not open HTML output after analysis",
    )
    full_parser.set_defaults(open_latest=None)
    full_parser.add_argument(
        "--roadmap",
        default=None,
        help="Architectural roadmap to evaluate against (e.g. 'internal_tool')"
    )
    full_parser.add_argument(
        "--ai-insights",
        action="store_true",
        help="Generate AI insights using Vertex AI Gemini (requires gcloud auth)"
    )
    full_parser.add_argument(
        "--ai-insights-model",
        default="gemini-2.0-flash-001",
        help="Gemini model for insights generation (default: gemini-2.0-flash-001)"
    )
    full_parser.add_argument(
        "--timing",
        action="store_true",
        help="Enable pipeline timing metrics (summary at end)"
    )
    full_parser.add_argument(
        "--verbose-timing",
        action="store_true",
        help="Print per-stage timing during execution (implies --timing)"
    )
    full_parser.add_argument(
        "--validate-ui",
        action="store_true",
        help="Run circuit breaker UI tests on generated HTML (requires playwright)"
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
    viz_parser.add_argument(
        "--3d",
        dest="use_3d",
        action="store_true",
        help="Use new 3D visualization (MermaidFlow)"
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
    # DISCOVER Command - Self-Learning Taxonomy
    # ==========================================
    discover_parser = subparsers.add_parser(
        "discover",
        help="Run discovery engine to find unknown patterns (T3)",
        description="Analyze a codebase using T0/T1/T2 cascade, document unknown patterns as T3 discoveries."
    )
    discover_parser.add_argument(
        "path",
        help="Path to the repository to analyze"
    )
    discover_parser.add_argument(
        "--language",
        default=None,
        help="Analyze only specific language (python, go, typescript, etc.)"
    )
    discover_parser.add_argument(
        "--output", "-o",
        default="output/discoveries.json",
        help="Output path for discovered patterns JSON"
    )
    discover_parser.add_argument(
        "--load",
        default=None,
        help="Load previous discoveries to merge with new ones"
    )

    # ==========================================
    # EVAL Command - Comprehensive Evaluation
    # ==========================================
    eval_parser = subparsers.add_parser(
        "eval",
        help="Run comprehensive evaluation of the analysis pipeline",
        description="Test Python, Go, JS extraction and classification with clear PASS/FAIL metrics."
    )
    eval_parser.add_argument(
        "--full",
        action="store_true",
        help="Run full benchmark (200 files per language)"
    )
    eval_parser.add_argument(
        "--save",
        metavar="NAME",
        help="Save results with given name (e.g., 'baseline')"
    )
    eval_parser.add_argument(
        "--compare",
        metavar="NAME",
        help="Compare current results to saved baseline"
    )

    # Parse
    args = parser.parse_args()
    
    if args.command == "discover":
        from src.core.discovery_engine import DiscoveryEngine
        # Path already imported globally at top of file

        print(f"🔬 Discovery Engine — Hybrid T0/T1/T2 + T3 Discovery")
        print("=" * 60)

        engine = DiscoveryEngine()

        # Load previous discoveries if specified
        if args.load and Path(args.load).exists():
            print(f"   Loading previous discoveries from: {args.load}")
            engine.load_discoveries(args.load)
            print(f"   Loaded {len(engine.discovered_registry)} existing patterns")

        print(f"\n   Analyzing: {args.path}")
        if args.language:
            print(f"   Language: {args.language}")

        report = engine.analyze_repo(args.path, language=args.language)
        print(engine.generate_report())

        # Export discoveries
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        engine.export_discoveries(str(output_path))
        print(f"\n   Discoveries exported to: {output_path}")

        # Show taxonomy candidates
        candidates = engine.get_taxonomy_candidates(min_occurrences=10, min_confidence=0.5)
        if candidates:
            print(f"\n   {len(candidates)} patterns ready for taxonomy promotion")

        sys.exit(0)

    elif args.command == "eval":
        from scripts.evaluate import run_evaluation, save_result, compare_results
        result = run_evaluation(full=args.full)
        if args.save:
            save_result(result, args.save)
        if args.compare:
            compare_results(result, args.compare)
        sys.exit(0 if result.overall_status == "PASS" else 1)

    elif args.command == "health":
        from src.core.newman_runner import run_health_check
        sys.exit(run_health_check(exit_on_fail=True))
    

    elif args.command == "audit":
        from src.core.audit_runner import run_full_audit
        sys.exit(run_full_audit(target_path=args.path, output_dir=args.output))

    elif args.command == "full":
        from src.core.full_analysis import run_full_analysis
        try:
            options = {"roadmap": args.roadmap} if args.roadmap else {}
            if args.open_latest is not None:
                options["open_latest"] = args.open_latest
            if getattr(args, 'ai_insights', False):
                options["ai_insights"] = True
                options["ai_insights_model"] = getattr(args, 'ai_insights_model', 'gemini-2.0-flash-001')
            # Timing options
            if getattr(args, 'verbose_timing', False):
                options["verbose_timing"] = True
                options["timing"] = True  # verbose implies timing
            elif getattr(args, 'timing', False):
                options["timing"] = True
            run_full_analysis(args.path, args.output, options=options)

            # UI Validation (optional)
            if getattr(args, 'validate_ui', False):
                import glob
                output_dir = args.output or os.path.join(args.path, '.collider')
                html_files = glob.glob(os.path.join(output_dir, 'output_human-readable_*.html'))
                if html_files:
                    newest_html = max(html_files, key=os.path.getmtime)
                    print(f"\n🧪 Running UI validation on: {os.path.basename(newest_html)}")
                    try:
                        # Dynamic import of validate_ui from tools directory
                        import importlib.util
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        validate_ui_path = os.path.join(script_dir, 'tools', 'validate_ui.py')
                        spec = importlib.util.spec_from_file_location("validate_ui", validate_ui_path)
                        validate_ui_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(validate_ui_module)

                        result = validate_ui_module.validate_ui(newest_html, verbose=True)
                        validate_ui_module.print_report(result, verbose=True)
                        if result['failed'] > 0:
                            print("\n⚠️  UI validation found failures. See above for details.")
                    except ImportError as e:
                        if 'playwright' in str(e).lower():
                            print("⚠️  UI validation requires playwright. Install with: pip install playwright && playwright install chromium")
                        else:
                            print(f"⚠️  UI validation import error: {e}")
                else:
                    print("⚠️  No HTML output found for UI validation")
        except Exception as e:
            print(f"❌ Full analysis failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    elif args.command == "analyze":
        if not args.path:
            print("❌ Error: path argument is required for analyze command")
            print("Usage: collider analyze <path_to_code>")
            sys.exit(1)

        print(f"🚀 Launching Collider Analysis on: {args.path}")
        try:
            from src.core.full_analysis import run_full_analysis

            options = {}
            if args.open_latest is not None:
                options["open_latest"] = args.open_latest
            if args.llm:
                options["llm"] = True
                options["llm_model"] = args.llm_model
            if args.language:
                options["language"] = args.language
            if args.no_learn:
                options["no_learn"] = True
            if args.workers:
                options["workers"] = args.workers

            if args.no_learn or args.workers:
                print("⚠️  Note: --no-learn/--workers are accepted but not used by the full pipeline yet.")

            run_full_analysis(args.path, args.output, options=options)
            print("\n✅ Analysis complete. Consolidated outputs generated.")
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            sys.exit(1)

    elif args.command == "doctor":
        from src.core.full_analysis import run_full_analysis
        from src.core.normalize_output import normalize_output, validate_contract
        from collections import Counter

        output_dir = args.output or tempfile.mkdtemp(prefix="collider_doctor_")
        print(f"🩺 Doctor running on: {args.path}")
        print(f"   Output: {output_dir}")

        try:
            result = run_full_analysis(args.path, output_dir, options={})
        except Exception as e:
            print(f"❌ Doctor failed during analysis: {e}")
            sys.exit(1)

        normalized = normalize_output(result)
        errors, warnings = validate_contract(normalized)

        if warnings:
            print("⚠️  Warnings:")
            for msg in warnings:
                print(f"   - {msg}")

        if errors:
            print("❌ Contract validation failed:")
            for msg in errors:
                print(f"   - {msg}")
            sys.exit(1)

        print("✅ Doctor PASS: output contract verified.")
        nodes = normalized.get("nodes", []) if isinstance(normalized, dict) else []
        atom_family_counts = Counter()
        tier_counts = Counter()
        for node in nodes:
            if not isinstance(node, dict):
                continue
            atom_family = node.get("atom_family") or "unknown"
            tier = node.get("tier") or "unknown"
            atom_family_counts[str(atom_family)] += 1
            tier_counts[str(tier)] += 1
        if nodes:
            print("   atom_family counts:", dict(atom_family_counts))
            print("   tier counts:", dict(tier_counts))
    
    elif args.command == "graph":
        from src.core.graph_analyzer import analyze_full, generate_report, load_graph, shortest_path
        
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

    elif args.command == "viz":
        graph_path = Path(args.graph_path)
        if args.output:
            output_path = Path(args.output)
        else:
            stem = re.sub(r"[^A-Za-z0-9]+", "-", graph_path.stem.lower()).strip("-") or "graph"
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = graph_path.parent / f"output_human-readable_{stem}_{ts}.html"

        try:
            if args.use_3d:
                from src.core.viz_generator import VisualizationGenerator
                generator = VisualizationGenerator()
                saved_path = generator.generate(graph_path, output_path, mode="3d")
            else:
                from src.core.output_generator import write_html_report
                saved_path = write_html_report(graph_path, output_path.parent, filename=output_path.name)
            print(f"✅ Visualization generated: {saved_path}")
        except Exception as e:
            print(f"❌ Error generating visualization: {e}")
            sys.exit(1)

    elif args.command == "fix":
        from src.core.fix_generator import FixGenerator
        
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
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
