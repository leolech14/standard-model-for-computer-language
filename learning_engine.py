#!/usr/bin/env python3
"""
🧠 COMPREHENSIVE LEARNING ENGINE

Single command to:
1. Scan repos (local or clone from list)
2. Extract complete structure (atoms + graphs + bodies)
3. Generate semantic IDs
4. Auto-learn unknown patterns
5. Measure coverage gradient
6. Export LLM-ready representation

Usage:
    python3 learning_engine.py --repos-dir ./repos --output ./output
    python3 learning_engine.py --single-repo ./path/to/repo
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add core to path
sys.path.insert(0, str(Path(__file__).parent / "core"))

from atom_registry import AtomRegistry
from discovery_engine import DiscoveryEngine
from graph_extractor import GraphExtractor
from complete_extractor import CompleteExtractor
from semantic_ids import SemanticIDGenerator, SemanticMatrix, SemanticID


@dataclass
class RepoAnalysis:
    """Complete analysis of a single repository."""
    name: str
    path: str
    language: str
    
    # Metrics
    files: int = 0
    lines: int = 0
    bytes: int = 0
    
    # Atoms
    total_nodes: int = 0
    known_atoms: int = 0
    unknown_atoms: int = 0
    coverage_pct: float = 0.0
    
    # Graph
    classes: int = 0
    functions: int = 0
    call_edges: int = 0
    import_edges: int = 0
    inherit_edges: int = 0
    
    # Semantic IDs
    semantic_ids: int = 0
    semantic_id_list: List[SemanticID] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list) # (Caller, Callee) names
    
    # Discoveries
    new_patterns: List[Dict] = field(default_factory=list)
    
    # Timing
    analysis_time_ms: int = 0


@dataclass
class LearningReport:
    """Complete learning report across all repos."""
    
    # Meta
    run_id: str = ""
    timestamp: str = ""
    repos_analyzed: int = 0
    
    # Aggregates
    total_files: int = 0
    total_lines: int = 0
    total_nodes: int = 0
    total_known: int = 0
    total_unknown: int = 0
    avg_coverage: float = 0.0
    
    # Registry state
    registry_size_before: int = 0
    registry_size_after: int = 0
    atoms_learned: int = 0
    
    # Semantic matrix
    total_semantic_ids: int = 0
    
    # Per-repo details
    repos: List[RepoAnalysis] = field(default_factory=list)
    
    # All discoveries
    all_discoveries: List[Dict] = field(default_factory=list)


class LearningEngine:
    """
    Comprehensive code learning engine.
    
    Combines all analysis modules into a single pipeline:
    - AtomRegistry (canonical vocabulary)
    - DiscoveryEngine (find unknowns)
    - GraphExtractor (relationships)
    - CompleteExtractor (full bodies)
    - SemanticIDGenerator (LLM-ready IDs)
    """
    
    def __init__(self, auto_learn: bool = True, mode: str = "auto", llm_model: str = None):
        self.mode = mode
        self.auto_learn = auto_learn
        self.output_dir = "output/learning"
        self.semantic_matrix = SemanticMatrix()
        self.llm_classifier = None

        # Initialize engines based on mode
        self.registry = AtomRegistry()
        self.semantic_generator = SemanticIDGenerator()
        
        # HOW/WHERE detectors (v14+)
        try:
            from core.boundary_detector import BoundaryDetector
            from core.purity_detector import PurityDetector
            self.boundary_detector = BoundaryDetector()
            self.purity_detector = PurityDetector()
            self.enable_how_where = True
        except ImportError:
            print("⚠️  HOW/WHERE detectors not available (missing tools)")
            self.boundary_detector = None
            self.purity_detector = None
            self.enable_how_where = False
        
        # Track all discoveries across repos
        self.all_discoveries: Dict[str, Dict] = {}
        
        if self.mode != "minimal":
            self.discovery = DiscoveryEngine()
            self.graph_extractor = GraphExtractor()
            self.complete_extractor = CompleteExtractor()
            self._load_learned_atoms()
        else:
            # Minimal primitives
            from core.universal_detector import UniversalPatternDetector
            self.universal_detector = UniversalPatternDetector()
            self.discovery = None
            self.graph_extractor = None
            self.complete_extractor = None
        
        # Initialize LLM classifier if model specified
        if llm_model:
            try:
                from core.llm_classifier import create_ollama_classifier
                self.llm_classifier = create_ollama_classifier(model=llm_model)
                if self.llm_classifier.llm_client.is_available():
                    print(f"🦙 LLM classifier enabled with {llm_model}")
                else:
                    print(f"⚠️  Ollama not available, LLM classification disabled")
                    self.llm_classifier = None
            except Exception as e:
                print(f"⚠️  LLM classifier init failed: {e}")
                self.llm_classifier = None
    
    def _load_learned_atoms(self):
        """Load atoms from the enhanced registry (including discovered atoms)."""
        # First try: enhanced registry with discovered atoms
        registry_path = Path(__file__).parent / "output" / "atom_registry_canon.json"
        if registry_path.exists():
            try:
                data = json.loads(registry_path.read_text())
                discovered_count = 0
                for atom_id, atom in data.get("atoms", {}).items():
                    if atom.get("source") == "discovered":
                        # Add discovered atom to known atoms
                        for ast_type in atom.get("ast_types", []):
                            self.discovery.known_atoms[ast_type] = {
                                "name": atom["name"],
                                "continent": atom.get("continent", "Discovered"),
                                "fundamental": atom.get("fundamental", "Auto-Learned"),
                            }
                        discovered_count += 1
                if discovered_count > 0:
                    print(f"📚 Loaded {discovered_count} discovered atoms from registry")
                    print(f"   Total atoms now: {len(data.get('atoms', {}))}")
                return
            except Exception as e:
                print(f"⚠️  Could not load registry: {e}")
        
        # Fallback: auto_learning_results.json
        learned_path = Path(__file__).parent / "output" / "auto_learning_results.json"
        if learned_path.exists():
            try:
                data = json.loads(learned_path.read_text())
                for atom in data.get("learned_atoms", []):
                    self.discovery.known_atoms[atom["ast_type"]] = {
                        "name": atom["name"],
                        "continent": atom["continent"],
                        "fundamental": atom["fundamental"],
                    }
                print(f"📚 Loaded {len(data.get('learned_atoms', []))} previously learned atoms")
            except Exception as e:
                print(f"⚠️  Could not load learned atoms: {e}")
    
    

    def analyze_repo(self, repo_path: str, language: Optional[str] = None) -> RepoAnalysis:
        """
        Analyze a repository (Auto-detect or specific language).
        """
        path = Path(repo_path)
        print(f"📁 Analyzing: {path} (Mode: {self.mode})")
        
        if self.mode == "minimal":
            return self._analyze_repo_minimal(str(path))
        
        from core.language_loader import LanguageLoader
        if language:
            languages = [language]
        else:
            languages = LanguageLoader.get_supported_languages()
            # Dedupe
            languages = list(set(languages))
        
        print(f"🔍 Scan targets: {', '.join(languages)}")
        
        # Aggregate results
        # Aggregate results
        total_files = 0
        all_semantic_ids = []
        all_edges = []
        
        for lang in languages:
            try:
                # 1. Discovery (Structure)
                report = self.discovery.analyze_repo(str(path), language=lang)
                if report.files_analyzed == 0 and report.total_nodes == 0:
                    continue
                    
                print(f"  ✓ {lang}: {report.total_nodes} nodes")
                
                # 2. Complete Extraction
                codebase = self.complete_extractor.extract(str(path), language=lang)
                stats = codebase.get_stats()
                
                # 3. Semantic Identification
                semantic_ids = self.semantic_generator.generate_ids(codebase)
                all_semantic_ids.extend(semantic_ids)
                
                # 4. Edge Extraction
                for f in codebase.functions.values():
                    for callee in f.calls:
                        all_edges.append((f.name, callee))
                
                total_files += stats["files"]

            except Exception as e:
                print(f"    ⚠️  Extraction error ({lang}): {e}")
                pass
        
        print(f"\n📊 Results:")
        print(f"   Files: {total_files}")
        print(f"   Semantic IDs: {len(all_semantic_ids)}")

        analysis = RepoAnalysis(
            name=path.name,
            path=str(path),
            language=language or "mixed",
            files=total_files,
            semantic_ids=len(all_semantic_ids),
            semantic_id_list=all_semantic_ids,
            edges=all_edges
        )
        return analysis

    def _analyze_repo_minimal(self, repo_path: str) -> RepoAnalysis:
        """Minimal analysis using regex-based Universal Detector."""
        print(f"  ⚡ Running Minimal Pipeline (Universal Detector)...")
        results = self.universal_detector.analyze_repository(repo_path, output_dir=self.output_dir)
        
        comp_results = results.get("comprehensive_results", {})
        particles = comp_results.get("particles", [])
        dependencies = comp_results.get("dependencies", {})
        
        # Convert to Semantic IDs
        semantic_ids = []
        for p in particles:
            sid = self.semantic_generator.from_particle(p)
            semantic_ids.append(sid)
        
        # Extract edges from DependencyAnalyzer output (unified IR format)
        from core.ir import edges_from_internal_edges_list
        internal_edges_list = dependencies.get("internal_edges", [])
        ir_edges = edges_from_internal_edges_list(internal_edges_list)
        
        # Convert to tuple format for backward compat with RepoAnalysis
        edges = [(e.source, e.target) for e in ir_edges]
        
        print(f"  ✓ Found {len(particles)} particles, converted to {len(semantic_ids)} Semantic IDs")
        print(f"  ✓ Found {len(edges)} internal dependency edges")
        
        # LLM Reclassification for low-confidence particles
        if self.llm_classifier is not None:
            semantic_ids, llm_stats = self._llm_reclassify_particles(
                particles, semantic_ids, repo_path
            )
            print(f"  🦙 LLM reclassification: {llm_stats['llm_escalated']} escalated, "
                  f"{llm_stats['llm_succeeded']} improved")
        
        # NEW: HOW/WHERE Enrichment
        if self.enable_how_where:
            print(f"  🔬 Enriching with HOW/WHERE dimensions...")
            
            # Run detectors
            purity_data = self.purity_detector.analyze(repo_path)
            boundary_data = self.boundary_detector.analyze(repo_path)
            
            # Import enrichment helpers
            from core.enrichment_helpers import _enrich_with_how, _enrich_with_where
            
            # Enrich semantic IDs
            _enrich_with_how(self, semantic_ids, purity_data)
            _enrich_with_where(self, semantic_ids, boundary_data)
            
            print(f"  ✓ Enriched {len(semantic_ids)} IDs with behavior and context data")
        
        # NEW: WHY Enrichment (Intent/Patterns)
        try:
            from core.intent_detector import IntentDetector
            intent_detector = IntentDetector(llm_classifier=self.llm_classifier)
            intent_data = intent_detector.analyze(semantic_ids)
            
            from core.enrichment_helpers import _enrich_with_why
            _enrich_with_why(self, semantic_ids, intent_data)
            
            patterns = intent_data.get("patterns_detected", {})
            smells = intent_data.get("smells_detected", {})
            print(f"  🎯 Intent analysis: {sum(patterns.values())} patterns, {sum(smells.values())} smells detected")
        except Exception as e:
            print(f"  ⚠️  Intent detection failed: {e}")
        
        # NEW: Export to 4D Particle Registry
        try:
            from core.particle_registry_4d import ParticleRegistry4D
            registry_4d = ParticleRegistry4D()
            count = registry_4d.add_from_semantic_ids(semantic_ids)
            
            # Save to output directory
            output_path = Path(repo_path) / "output" / "particle_registry_4d.json"
            if not output_path.parent.exists():
                output_path = Path("output") / "particle_registry_4d.json"
            
            registry_4d.save(str(output_path))
            
            stats = registry_4d.get_stats()
            print(f"  📦 4D Registry: {count} particles exported")
            print(f"     Patterns: {stats['by_pattern']}")
            print(f"     Smells: {stats['by_smell']}")
        except Exception as e:
            print(f"  ⚠️  4D Registry export failed: {e}")
        
        return RepoAnalysis(
            name=Path(repo_path).name,
            path=repo_path,
            language="mixed",
            files=results.get("summary", {}).get("files_processed", 0),
            semantic_ids=len(semantic_ids),
            semantic_id_list=semantic_ids,
            edges=edges,
            total_nodes=len(semantic_ids),
            known_atoms=len(semantic_ids),
            unknown_atoms=0,
            coverage_pct=comp_results.get("stats", {}).get("recognition_rate", 0.0)
        )
    
    def _llm_reclassify_particles(
        self, 
        particles: List[Dict], 
        semantic_ids: List, 
        repo_path: str
    ) -> Tuple[List, Dict]:
        """
        Reclassify low-confidence particles using section-based LLM classification.
        
        For large repos:
        1. First maps the full structure
        2. Groups particles by directory/section
        3. Sends batched context per section (more efficient, better context)
        
        Returns:
            Updated semantic_ids list and LLM stats dict
        """
        from core.llm_classifier import ComponentCard
        from collections import defaultdict
        
        escalation_threshold = 0.55
        file_cache = {}
        
        # Phase 1: Group particles by directory section
        sections = defaultdict(list)
        for i, (particle, sid) in enumerate(zip(particles, semantic_ids)):
            file_path = particle.get("file_path", "")
            # Group by parent directory (section)
            section = str(Path(file_path).parent) if file_path else "unknown"
            sections[section].append((i, particle, sid))
        
        # Phase 2: Build structure summary for LLM context
        structure_summary = self._build_structure_summary(particles, semantic_ids)
        
        # Phase 3: Process each section
        updated_ids = list(semantic_ids)  # Copy to avoid mutation issues
        
        for section_path, section_items in sections.items():
            # Filter to low-confidence items in this section
            low_conf_items = [
                (i, p, sid) for i, p, sid in section_items
                if sid.properties.get("confidence", 50) / 100.0 < escalation_threshold
                or sid.properties.get("type", "Unknown") == "Unknown"
            ]
            
            if not low_conf_items:
                continue
            
            # Limit batch size for LLM context window
            batch_size = 5
            for batch_start in range(0, len(low_conf_items), batch_size):
                batch = low_conf_items[batch_start:batch_start + batch_size]
                
                # Build section context
                section_context = self._build_section_context(
                    batch, section_path, structure_summary, file_cache
                )
                
                # Classify batch
                for idx, particle, sid in batch:
                    try:
                        file_path = particle.get("file_path", "")
                        start_line = particle.get("line", 1)
                        name = particle.get("name", "")
                        
                        # Get code excerpt
                        code_excerpt = self._get_code_excerpt(file_path, start_line, file_cache)
                        
                        card = ComponentCard(
                            node_id=sid.to_string() if hasattr(sid, 'to_string') else str(idx),
                            file_path=file_path,
                            name=name,
                            kind=particle.get("category", "class"),
                            start_line=start_line,
                            end_line=start_line + code_excerpt.count("\n"),
                            code_excerpt=code_excerpt[:2000],
                            signature=name,
                            docstring=section_context,  # Pass structure as context
                            decorators=[],
                            base_classes=[],
                            imports=[],
                            heuristic_role=sid.properties.get("type", "Unknown"),
                            heuristic_confidence=sid.properties.get("confidence", 50) / 100.0,
                            heuristic_evidence=[],
                            folder_layer=self._infer_layer_from_path(file_path),
                        )
                        
                        result = self.llm_classifier.classify(card)
                        
                        if result.role != "Unknown" and result.confidence > card.heuristic_confidence:
                            sid.properties["type"] = result.role
                            sid.properties["confidence"] = int(result.confidence * 100)
                            sid.properties["llm_classified"] = True
                            sid.properties["llm_reasoning"] = result.reasoning[:200]
                        
                        updated_ids[idx] = sid
                        
                    except Exception as e:
                        pass
        
        return updated_ids, self.llm_classifier.get_stats()
    
    def _build_structure_summary(self, particles: List[Dict], semantic_ids: List) -> str:
        """Build a high-level structure summary for LLM context."""
        from collections import defaultdict
        
        by_layer = defaultdict(list)
        for p, sid in zip(particles, semantic_ids):
            file_path = p.get("file_path", "")
            layer = self._infer_layer_from_path(file_path)
            role = sid.properties.get("type", "Unknown")
            name = p.get("name", "?")
            by_layer[layer].append(f"{name} ({role})")
        
        lines = ["REPOSITORY STRUCTURE:"]
        for layer in ["domain", "application", "infrastructure", "presentation", "unknown"]:
            if by_layer[layer]:
                lines.append(f"\n{layer.upper()} LAYER ({len(by_layer[layer])} components):")
                for item in by_layer[layer][:10]:  # Limit per layer
                    lines.append(f"  - {item}")
                if len(by_layer[layer]) > 10:
                    lines.append(f"  ... and {len(by_layer[layer]) - 10} more")
        
        return "\n".join(lines)
    
    def _build_section_context(
        self, 
        batch: List[Tuple], 
        section_path: str,
        structure_summary: str,
        file_cache: Dict
    ) -> str:
        """Build context for a section batch."""
        lines = [structure_summary, "", f"CURRENT SECTION: {section_path}", ""]
        lines.append("Components in this section:")
        for idx, particle, sid in batch:
            name = particle.get("name", "?")
            role = sid.properties.get("type", "Unknown")
            conf = sid.properties.get("confidence", 50)
            lines.append(f"  - {name}: {role} ({conf}% confidence)")
        return "\n".join(lines)
    
    def _get_code_excerpt(self, file_path: str, start_line: int, file_cache: Dict) -> str:
        """Extract code excerpt from file."""
        if file_path not in file_cache:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_cache[file_path] = f.read()
            except:
                file_cache[file_path] = ""
        
        full_content = file_cache[file_path]
        lines = full_content.split('\n')
        
        if start_line > 0 and start_line <= len(lines):
            end_line = min(start_line + 50, len(lines))
            for j in range(start_line, min(start_line + 100, len(lines))):
                if j < len(lines):
                    line = lines[j]
                    if j > start_line and (line.startswith('class ') or line.startswith('def ')):
                        end_line = j
                        break
            return '\n'.join(lines[start_line-1:end_line])
        return full_content[:2000]
    
    def _infer_layer_from_path(self, file_path: str) -> str:
        """Infer architectural layer from file path."""
        path_lower = file_path.lower()
        if "/domain/" in path_lower or "/entities/" in path_lower or "/model/" in path_lower:
            return "domain"
        if "/usecase/" in path_lower or "/application/" in path_lower or "/service/" in path_lower:
            return "application"
        if "/infra" in path_lower or "/repository/" in path_lower or "/gateway/" in path_lower:
            return "infrastructure"
        if "/api/" in path_lower or "/controller/" in path_lower or "/presentation/" in path_lower:
            return "presentation"
        return "unknown"

    def _export_results(self, semantic_ids, output_dir, edges=None):
        """Export merged results including unified graph."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        
        # Semantic IDs
        try:
            # Convert objects to dicts and serialize enums
            data = []
            for s in semantic_ids:
                d = s.__dict__.copy()
                # Convert enums to values
                if hasattr(d['continent'], 'value'): d['continent'] = d['continent'].value
                if hasattr(d['fundamental'], 'value'): d['fundamental'] = d['fundamental'].value
                if hasattr(d['level'], 'value'): d['level'] = d['level'].value
                data.append(d)
                
            with open(out / "semantic_ids.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"  ⚠️  Failed to export semantic_ids: {e}")
        
        # Unified Graph (with edges)
        if edges:
            try:
                from core.ir import Graph, Component, Edge, EdgeType
                
                graph = Graph(repo_name="analysis", repo_path=str(out))
                
                # Add components from semantic IDs
                for sid in semantic_ids:
                    graph.add_component(Component(
                        id=sid.to_string() if hasattr(sid, 'to_string') else str(sid),
                        name=sid.name if hasattr(sid, 'name') else "",
                        kind="class",  # Default; could be refined
                        file=sid.module_path if hasattr(sid, 'module_path') else "",
                        role=sid.properties.get("type") if hasattr(sid, 'properties') else None,
                    ))
                
                # Add edges
                for src, tgt in edges:
                    graph.add_edge(Edge(
                        source=src,
                        target=tgt,
                        edge_type=EdgeType.IMPORT,
                        category="internal",
                    ))
                
                # Export graph JSON
                with open(out / "graph.json", "w") as f:
                    f.write(graph.to_json())
                
                # Export Mermaid diagram
                mermaid = graph.to_mermaid(max_nodes=60)
                with open(out / "graph.mermaid", "w") as f:
                    f.write(mermaid)
                
                print(f"   - graph.json ({len(graph.components)} nodes, {len(graph.edges)} edges)")
                print(f"   - graph.mermaid")
            except Exception as e:
                print(f"  ⚠️  Failed to export graph: {e}")
            
        # Summary
        with open(out / "LEARNING_SUMMARY.md", "w") as f:
            f.write(f"# Analysis Summary\n\nTotal Semantic IDs: {len(semantic_ids)}\n")
            if edges:
                f.write(f"Total Edges: {len(edges)}\n")
            
        print(f"\n💾 Exported to: {out}")
        print(f"   - semantic_ids.json ({len(semantic_ids)} IDs)")
    def analyze_repos(self, repos_dir: str, language: str = "python", 
                      max_workers: int = 4) -> LearningReport:
        """
        Analyze all repositories in a directory.
        """
        path = Path(repos_dir)
        report = LearningReport(
            run_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            timestamp=datetime.now().isoformat(),
            registry_size_before=len(self.registry.atoms) + len([
                k for k in self.discovery.known_atoms 
                if k not in [a.ast_types[0] for a in self.registry.atoms.values() if a.ast_types]
            ]),
        )
        
        # Find all repos (directories with .py files)
        repos: List[Path] = []
        for child in path.iterdir():
            if child.is_dir():
                if any(child.rglob("*.py")):
                    repos.append(child)
        
        print(f"\n🔬 Analyzing {len(repos)} repositories...")
        print("=" * 70)
        
        # Analyze in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.analyze_repo, str(repo), language): repo
                for repo in repos
            }
            
            for future in as_completed(futures):
                repo = futures[future]
                try:
                    analysis = future.result()
                    report.repos.append(analysis)
                    
                    # Merge Semantic IDs
                    for sid in analysis.semantic_id_list:
                        self.semantic_matrix.add(sid)
                    
                    print(f"  ✅ {analysis.name}: {analysis.coverage_pct:.1f}% coverage, "
                          f"{analysis.semantic_ids} IDs, {analysis.analysis_time_ms}ms")
                except Exception as e:
                    print(f"  ❌ {repo.name}: {e}")
        
        # Aggregate stats
        report.repos_analyzed = len(report.repos)
        report.total_files = sum(r.files for r in report.repos)
        report.total_lines = sum(r.lines for r in report.repos)
        report.total_nodes = sum(r.total_nodes for r in report.repos)
        report.total_known = sum(r.known_atoms for r in report.repos)
        report.total_unknown = sum(r.unknown_atoms for r in report.repos)
        report.avg_coverage = sum(r.coverage_pct for r in report.repos) / len(report.repos) if report.repos else 0
        report.total_semantic_ids = sum(r.semantic_ids for r in report.repos)
        
        # Auto-learn if enabled
        if self.auto_learn and self.all_discoveries:
            learned = self._auto_learn()
            report.atoms_learned = len(learned)
        
        report.registry_size_after = report.registry_size_before + report.atoms_learned
        
        # Convert discoveries for JSON
        report.all_discoveries = [
            {
                "ast_type": d["ast_type"],
                "name": d["name"],
                "count": d["count"],
                "repos": list(d["repos"]),
                "continent": d["continent"],
                "fundamental": d["fundamental"],
            }
            for d in sorted(self.all_discoveries.values(), key=lambda x: -x["count"])
        ]
        
        return report
    
    def _auto_learn(self) -> List[Dict]:
        """Auto-learn all unknown patterns and persist to registry."""
        learned = []
        
        # Load current registry to get next_id
        registry_path = Path(__file__).parent / "output" / "atom_registry_canon.json"
        if registry_path.exists():
            registry = json.loads(registry_path.read_text())
            next_id = registry['stats'].get('next_id', 121)
        else:
            next_id = 121  # Start after current known atoms
        
        for ast_type, data in sorted(self.all_discoveries.items(), key=lambda x: -x[1]["count"]):
            if ast_type in self.discovery.known_atoms:
                continue
            if ast_type in self.discovery.syntax_tokens:
                continue
            
            # Generate name
            name = "".join(word.capitalize() for word in ast_type.replace("_", " ").split())
            
            # Add to discovery engine (memory)
            self.discovery.known_atoms[ast_type] = {
                "name": name,
                "continent": data["continent"] or "Logic & Flow",
                "fundamental": data["fundamental"] or "Expressions",
            }
            
            learned.append({
                "id": next_id,
                "ast_type": ast_type,
                "name": name,
                "count": data["count"],
                "repos": list(data["repos"]),
                "continent": data["continent"] or "Logic & Flow",
                "fundamental": data["fundamental"] or "Expressions",
            })
            
            next_id += 1
        
        # PERSIST to registry file
        if learned:
            self._persist_learned_atoms(learned)
        
        return learned
    
    def _persist_learned_atoms(self, learned: List[Dict]):
        """Persist newly learned atoms to the registry file."""
        registry_path = Path(__file__).parent / "output" / "atom_registry_canon.json"
        
        if not registry_path.exists():
            print("⚠️  Registry file not found, cannot persist")
            return
        
        try:
            registry = json.loads(registry_path.read_text())
            
            added = 0
            for atom in learned:
                atom_id = str(atom['id'])
                
                # Check if already exists
                if atom_id not in registry['atoms']:
                    registry['atoms'][atom_id] = {
                        'id': atom['id'],
                        'name': atom['name'],
                        'ast_types': [atom['ast_type']],
                        'continent': atom.get('continent', 'Discovered'),
                        'fundamental': atom.get('fundamental', 'Auto-Learned'),
                        'level': 'atom',
                        'description': f"Auto-discovered: {atom['ast_type']} ({atom['count']} occurrences)",
                        'detection_rule': f"AST type: {atom['ast_type']}",
                        'source': 'discovered',
                        'discovered_at': datetime.now().isoformat(),
                    }
                    added += 1
            
            if added > 0:
                # Update stats
                registry['stats']['total_atoms'] = len(registry['atoms'])
                registry['stats']['next_id'] = max(int(k) for k in registry['atoms'].keys()) + 1
                registry['stats']['by_source']['discovered'] = sum(
                    1 for a in registry['atoms'].values() if a.get('source') == 'discovered'
                )
                registry['timestamp'] = datetime.now().isoformat()
                
                # Save
                registry_path.write_text(json.dumps(registry, indent=2))
                print(f"💾 Auto-persisted {added} new atoms to registry")
                print(f"   Registry now: {registry['stats']['total_atoms']} atoms")
        
        except Exception as e:
            print(f"⚠️  Could not persist atoms: {e}")
    
    def export(self, report: LearningReport, output_dir: str):
        """Export all learning results."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        
        # 1. Full report JSON
        report_data = asdict(report)
        (out / "learning_report.json").write_text(json.dumps(report_data, indent=2, default=str))
        
        # 2. Semantic IDs
        semantic_data = {
            "stats": self.semantic_matrix.get_stats(),
            "ids": [sid.to_string() for sid in self.semantic_matrix.ids],
        }
        (out / "semantic_ids.json").write_text(json.dumps(semantic_data, indent=2))
        
        # 3. LLM context
        llm_context = self.semantic_matrix.to_llm_context()
        (out / "llm_context.md").write_text(llm_context)
        
        # 4. Discoveries for review
        discoveries_md = self._generate_discoveries_md(report)
        (out / "discoveries.md").write_text(discoveries_md)
        
        # 5. Summary markdown
        summary_md = self._generate_summary_md(report)
        (out / "LEARNING_SUMMARY.md").write_text(summary_md)
        
        # 6. Generate Full Network Diagram
        network_path = out / "NETWORK_DIAGRAM.mermaid"
        with open(network_path, "w") as f:
            f.write("graph TD\n")
            f.write("    %% Nodes (Functions/Classes)\n")
            
            # Map names to IDs for easier linking
            node_map = {}
            for sid in self.semantic_matrix.ids:
                node_map[sid.name] = sid
                safe_id = sid.content_hash
                display_name = sid.name.replace('"', '').replace('(', '').replace(')', '')
                
                # Fallback for empty names (usually file aggregations)
                if not display_name.strip():
                     display_name = Path(sid.module_path).name
                
                f.write(f'    {safe_id}["{display_name}"]\n')
                
                if "LOGIC" in str(sid.continent):
                    f.write(f'    style {safe_id} fill:#e1f5fe,stroke:#01579b\n')
                elif "EXEC" in str(sid.continent):
                    f.write(f'    style {safe_id} fill:#fff3e0,stroke:#e65100\n')
            
            f.write("\n    %% Edges (Calls)\n")
            all_edges = []
            for repo in report.repos:
                all_edges.extend(repo.edges)
            
            filtered_edges = 0
            for caller, callee in all_edges:
                caller_node = node_map.get(caller)
                callee_node_match = None
                
                if callee in node_map:
                    callee_node_match = node_map[callee]
                else:
                    if "." in callee:
                        short_name = callee.split(".")[-1]
                        for name, sid in node_map.items():
                             if name.endswith("." + short_name) or name == short_name:
                                 callee_node_match = sid
                                 break
                
                if caller_node and callee_node_match:
                    f.write(f"    {caller_node.content_hash} --> {callee_node_match.content_hash}\n")
                    filtered_edges += 1
        
        print(f"\n💾 Exported to: {out}")
        print(f"   - learning_report.json")
        print(f"   - semantic_ids.json ({len(self.semantic_matrix.ids)} IDs)")
        print(f"   - llm_context.md")
        print(f"   - discoveries.md")
        print(f"   - LEARNING_SUMMARY.md")
        
        # 7. Export unified graph.json with IR format
        try:
            from core.ir import Graph, Component, Edge, EdgeType
            
            repo_name = report.repos[0].name if report.repos else "analysis"
            repo_root = Path(report.repos[0].path).resolve() if report.repos and report.repos[0].path else Path(".").resolve()
            graph = Graph(repo_name=repo_name, repo_path=str(repo_root))

            contains_seen: set[tuple[str, str]] = set()
            import_seen: set[tuple[str, str]] = set()

            repo_node_id = f"{repo_name}/"
            graph.add_component(
                Component(
                    id=repo_node_id,
                    name=repo_name,
                    kind="repo",
                    file="",
                    role="Repo",
                    role_confidence=1.0,
                )
            )

            def _posix(p: Path) -> str:
                return p.as_posix()

            def _rel_file(file_path: str) -> str:
                if not file_path:
                    return ""
                p = Path(file_path)
                if p.is_absolute():
                    candidate = p
                else:
                    rooted = (repo_root / p)
                    candidate = rooted if rooted.exists() else p
                try:
                    resolved = candidate.resolve()
                except Exception:
                    resolved = candidate
                try:
                    rel = resolved.relative_to(repo_root)
                    return _posix(rel)
                except Exception:
                    return str(file_path).replace("\\", "/").lstrip("./")

            def _dir_id(dir_path: str) -> str:
                d = dir_path.strip().strip("/")
                return f"{d}/" if d else ""

            def _add_contains(source: str, target: str) -> None:
                if not source or not target:
                    return
                key = (source, target)
                if key in contains_seen:
                    return
                contains_seen.add(key)
                graph.add_edge(
                    Edge(
                        source=source,
                        target=target,
                        edge_type=EdgeType.CONTAINS,
                        category="structural",
                        confidence=1.0,
                    )
                )

            def _add_import(source: str, target: str) -> None:
                if not source or not target:
                    return
                key = (source, target)
                if key in import_seen:
                    return
                import_seen.add(key)
                graph.add_edge(
                    Edge(
                        source=source,
                        target=target,
                        edge_type=EdgeType.IMPORT,
                        category="internal",
                        confidence=1.0,
                    )
                )

            def _ensure_directory(dir_path: str) -> str:
                did = _dir_id(dir_path)
                if not did:
                    return repo_node_id
                if did in graph.components:
                    return did

                name = Path(dir_path).name if dir_path else repo_name
                graph.add_component(
                    Component(
                        id=did,
                        name=name,
                        kind="directory",
                        file=did,
                        role="Directory",
                        role_confidence=1.0,
                    )
                )

                parent = str(Path(dir_path).parent).replace("\\", "/")
                if parent in (".", "/"):
                    parent_id = repo_node_id
                else:
                    parent_id = _ensure_directory(parent)

                _add_contains(parent_id, did)
                return did

            def _ensure_file(file_rel: str) -> str:
                rel = str(file_rel).replace("\\", "/").lstrip("./")
                if not rel:
                    return ""
                if rel in graph.components:
                    return rel

                suffix = Path(rel).suffix.lower()
                kind = "file"
                if suffix in {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}:
                    kind = "asset"

                graph.add_component(
                    Component(
                        id=rel,
                        name=Path(rel).name,
                        kind=kind,
                        file=rel,
                        role="File",
                        role_confidence=1.0,
                    )
                )

                parent_dir = Path(rel).parent.as_posix()
                parent_id = repo_node_id if parent_dir in (".", "") else _ensure_directory(parent_dir)
                _add_contains(parent_id, rel)
                return rel
            
            symbol_index: dict[tuple[str, str], str] = {}
            pending_symbol_contains: list[tuple[str, str, str]] = []  # (file_rel, parent_name, child_id)

            # Add components from semantic IDs
            for sid in self.semantic_matrix.ids:
                role = sid.properties.get("type") if hasattr(sid, 'properties') else None
                sid_id = sid.to_string() if hasattr(sid, "to_string") else str(sid)
                file_path = ""
                if hasattr(sid, "properties") and isinstance(getattr(sid, "properties", None), dict):
                    file_path = str(sid.properties.get("file_path") or "")
                file_rel = _rel_file(file_path)

                graph.add_component(
                    Component(
                        id=sid_id,
                        name=sid.name if hasattr(sid, "name") else "",
                        kind=str(sid.fundamental.value) if hasattr(sid, "fundamental") else "unknown",
                        file=file_rel or (sid.module_path if hasattr(sid, "module_path") else ""),
                        role=role,
                        role_confidence=(
                            sid.properties.get("confidence", 0) / 100.0
                            if hasattr(sid, "properties") and sid.properties.get("confidence")
                            else 0.0
                        ),
                    )
                )

                if file_rel:
                    file_node = _ensure_file(file_rel)
                    _add_contains(file_node, sid_id)
                    symbol_index[(file_rel, sid.name)] = sid_id

                    parent_name = str(sid.properties.get("parent") or "") if hasattr(sid, "properties") else ""
                    if parent_name:
                        pending_symbol_contains.append((file_rel, parent_name, sid_id))

            for file_rel, parent_name, child_id in pending_symbol_contains:
                parent_id = symbol_index.get((file_rel, parent_name))
                if parent_id:
                    _add_contains(parent_id, child_id)
            
            # Add edges from all repos
            for repo in report.repos:
                for src, tgt in repo.edges:
                    src_rel = str(src).replace("\\", "/").lstrip("./")
                    tgt_rel = str(tgt).replace("\\", "/").lstrip("./")
                    _ensure_file(src_rel)
                    _ensure_file(tgt_rel)
                    _add_import(src_rel, tgt_rel)
            
            # Export
            (out / "graph.json").write_text(graph.to_json())
            print(f"   - graph.json ({len(graph.components)} nodes, {len(graph.edges)} edges)")
            
        except Exception as e:
            print(f"   ⚠️  graph.json export failed: {e}")
    
    def _generate_discoveries_md(self, report: LearningReport) -> str:
        """Generate markdown report of discoveries."""
        lines = [
            "# 🔬 Atom Discoveries",
            "",
            f"**Run:** {report.run_id}",
            f"**Repos:** {report.repos_analyzed}",
            f"**New Atoms Learned:** {report.atoms_learned}",
            "",
            "## Discovered Patterns",
            "",
            "| # | AST Type | Name | Count | Repos |",
            "|---|----------|------|------:|-------|",
        ]
        
        for i, d in enumerate(report.all_discoveries[:50], 1):
            repos = ", ".join(d["repos"][:3])
            if len(d["repos"]) > 3:
                repos += f" +{len(d['repos'])-3}"
            lines.append(f"| {i} | `{d['ast_type']}` | {d['name']} | {d['count']:,} | {repos} |")
        
        return "\n".join(lines)
    
    def _generate_summary_md(self, report: LearningReport) -> str:
        """Generate summary markdown."""
        lines = [
            "# 🧠 Learning Engine Summary",
            "",
            f"**Run ID:** `{report.run_id}`",
            f"**Timestamp:** {report.timestamp}",
            "",
            "## Metrics",
            "",
            "| Metric | Value |",
            "|--------|------:|",
            f"| Repos Analyzed | {report.repos_analyzed} |",
            f"| Total Files | {report.total_files:,} |",
            f"| Total Lines | {report.total_lines:,} |",
            f"| Total AST Nodes | {report.total_nodes:,} |",
            f"| Known Atoms | {report.total_known:,} |",
            f"| Unknown Atoms | {report.total_unknown:,} |",
            f"| Average Coverage | {report.avg_coverage:.1f}% |",
            f"| Semantic IDs | {report.total_semantic_ids:,} |",
            "",
            "## Registry Growth",
            "",
            f"- Before: **{report.registry_size_before}** atoms",
            f"- After:  **{report.registry_size_after}** atoms",
            f"- Learned: **{report.atoms_learned}** new atoms",
            "",
            "## Per-Repo Breakdown",
            "",
            "| Repo | Files | Coverage | IDs | Time |",
            "|------|------:|--------:|----:|-----:|",
        ]
        
        for r in sorted(report.repos, key=lambda x: -x.coverage_pct):
            lines.append(f"| {r.name} | {r.files} | {r.coverage_pct:.1f}% | {r.semantic_ids} | {r.analysis_time_ms}ms |")
        
        return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

def run_analysis(args):
    """Run analysis with parsed arguments."""
    from core.system_health import SystemHealth
    
    # Pre-Flight Checklist
    # Only hard fail if user explicitly requested full mode
    exit_on_fail = (args.mode == "full")
    SystemHealth.print_checklist(mode=args.mode, exit_on_fail=exit_on_fail)
    
    print("=" * 70)
    print("🧠 COMPREHENSIVE LEARNING ENGINE")
    print("=" * 70)
    
    llm_model = args.llm_model if hasattr(args, 'llm') and args.llm else None
    
    # Handle both argparse Namespace and dict
    no_learn = args.no_learn if hasattr(args, 'no_learn') else False
    mode = args.mode if hasattr(args, 'mode') else "auto"
    
    engine = LearningEngine(auto_learn=not no_learn, mode=mode, llm_model=llm_model)
    
    # Determine input source
    single_repo = args.single_repo if hasattr(args, 'single_repo') else None
    repos_dir = args.repos_dir if hasattr(args, 'repos_dir') else None
    language = args.language if hasattr(args, 'language') else None
    output_dir = args.output if hasattr(args, 'output') else "output/learning"
    engine.output_dir = output_dir
    workers = args.workers if hasattr(args, 'workers') else 4
    
    if single_repo:
        # Single repo mode
        print(f"\n📁 Analyzing: {single_repo}")
        analysis = engine.analyze_repo(single_repo, language)
        
        # Add to matrix
        for sid in analysis.semantic_id_list:
            engine.semantic_matrix.add(sid)
        
        print(f"\n📊 Results:")
        print(f"   Files: {analysis.files}")
        print(f"   Coverage: {analysis.coverage_pct:.1f}%")
        print(f"   Semantic IDs: {analysis.semantic_ids}")
        print(f"   Classes: {analysis.classes}")
        print(f"   Functions: {analysis.functions}")
        print(f"   Call edges: {analysis.call_edges}")
        
        if analysis.new_patterns:
            print(f"\n🔬 New patterns discovered:")
            for p in analysis.new_patterns[:5]:
                print(f"   - {p['type']}: {p['count']}x")
        
        # Create minimal report
        report = LearningReport(
            run_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            timestamp=datetime.now().isoformat(),
            repos_analyzed=1,
            repos=[analysis],
        )
        
    elif repos_dir:
        # Multi-repo mode
        report = engine.analyze_repos(repos_dir, language, workers)
        
        print("\n" + "=" * 70)
        print("📊 AGGREGATE RESULTS")
        print("=" * 70)
        print(f"   Repos: {report.repos_analyzed}")
        print(f"   Files: {report.total_files:,}")
        print(f"   Lines: {report.total_lines:,}")
        print(f"   Nodes: {report.total_nodes:,}")
        print(f"   Coverage: {report.avg_coverage:.1f}%")
        print(f"   Semantic IDs: {report.total_semantic_ids:,}")
        print(f"   Atoms learned: {report.atoms_learned}")
        
    else:
        # Demo mode - use dddpy
        demo_path = Path(__file__).parent / "validation" / "dddpy_real"
        if demo_path.exists():
            print(f"\n📁 Demo mode: {demo_path}")
            analysis = engine.analyze_repo(str(demo_path), language)
            
            print(f"\n📊 Results:")
            print(f"   Files: {analysis.files}")
            report = LearningReport(
                run_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                timestamp=datetime.now().isoformat(),
                repos_analyzed=1,
                repos=[analysis],
            )
        else:
            print("❌ No input specified and demo repo not found")
            return

    # Export results
    engine.export(report, output_dir)

def main():
    # CLI Argument Parsing
    parser = argparse.ArgumentParser(
        description="🧠 Comprehensive Learning Engine - Analyze and learn from real codebases"
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "full", "minimal"],
        default="auto",
        help="Analysis mode: 'full' (requires tree-sitter), 'minimal' (regex-only), or 'auto' (degrade gracefully)",
    )
    parser.add_argument(
        "--repos-dir",
        help="Directory containing repos to analyze",
    )
    parser.add_argument(
        "--single-repo",
        help="Path to a single repo to analyze",
    )
    parser.add_argument(
        "--output",
        default="output/learning",
        help="Output directory for results",
    )
    parser.add_argument("--language", default=None, help="Language to analyze (default: auto-detect)")
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--no-learn",
        action="store_true",
        help="Disable auto-learning of unknown patterns",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Enable LLM classification for low-confidence components (requires Ollama)",
    )
    parser.add_argument(
        "--llm-model",
        default="qwen2.5:7b-instruct",
        help="Ollama model to use for LLM classification",
    )
    
    args = parser.parse_args()
    run_analysis(args)



if __name__ == "__main__":
    sys.exit(main())
