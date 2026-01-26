#!/usr/bin/env python3
"""
🔬 COLLIDER - Unified Analysis Entry Point

Single activation entry point for complete codebase analysis.
Produces consistent output schema for ALL repos, even with partial data.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from edge_extractor import file_node_id, resolve_edges, extract_call_edges, extract_exposure_edges, get_import_resolution_diagnostics

try:
    from core.registry.role_registry import get_role_registry
    _role_registry = get_role_registry()
except ImportError:
    try:
        from registry.role_registry import get_role_registry
        _role_registry = get_role_registry()
    except ImportError:
        _role_registry = None


@dataclass
class UnifiedNode:
    """Universal node schema for any code element."""
    id: str
    name: str
    kind: str  # class, function, method, module, repo

    # Location
    file_path: str = ""
    start_line: int = 0
    end_line: int = 0

    # Classification
    role: str = "Unknown"
    role_confidence: float = 0.0
    discovery_method: str = "none"  # pattern, inheritance, path, llm, none

    # Type Information
    params: List[Dict[str, str]] = field(default_factory=list)
    return_type: str = ""
    base_classes: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)

    # Documentation
    docstring: str = ""
    signature: str = ""

    # Lossless Code Capture
    body_source: str = ""

    # Metrics
    complexity: int = 0
    lines_of_code: int = 0

    # Graph Properties
    in_degree: int = 0
    out_degree: int = 0
    layer: Optional[str] = None

    # V2: 8 Dimensions
    dimensions: Dict[str, str] = field(default_factory=dict)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedEdge:
    """Universal edge schema for any relationship."""
    source: str
    target: str
    edge_type: str  # contains, calls, imports, inherits, implements, uses

    weight: float = 1.0
    confidence: float = 1.0

    # Context
    file_path: str = ""
    line: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedAnalysisOutput:
    """
    Complete unified output schema for ANY codebase analysis.
    Consistent structure regardless of repo type/size.
    """

    # === METADATA ===
    schema_version: str = "2.0.0"
    collider_version: str = "2.3.0"
    generated_at: str = ""
    analysis_time_ms: int = 0

    # === TARGET ===
    target_path: str = ""
    target_name: str = ""
    target_type: str = "directory"  # directory, file, repository

    # === GRAPH (CORE) ===
    nodes: List[Dict] = field(default_factory=list)
    edges: List[Dict] = field(default_factory=list)

    # === STATISTICS ===
    stats: Dict[str, Any] = field(default_factory=lambda: {
        "total_files": 0,
        "total_lines": 0,
        "total_nodes": 0,
        "total_edges": 0,
        "languages": [],
        "coverage_percentage": 0.0,
        "unknown_percentage": 0.0,
    })

    # === CLASSIFICATION BREAKDOWN ===
    classification: Dict[str, Any] = field(default_factory=lambda: {
        "by_role": {},      # {"Service": 45, "Query": 23, ...}
        "by_kind": {},      # {"class": 12, "function": 89, ...}
        "by_layer": {},     # {"domain": 20, "infrastructure": 15, ...}
        "by_confidence": {  # Confidence distribution
            "high": 0,      # >= 80%
            "medium": 0,    # 50-80%
            "low": 0,       # < 50%
        }
    })

    # === AUTO-DISCOVERY ===
    auto_discovery: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "patterns_applied": 0,
        "particles_reclassified": 0,
        "top_patterns": [],
        "suggested_new_patterns": [],
    })

    # === DEPENDENCIES ===
    dependencies: Dict[str, Any] = field(default_factory=lambda: {
        "internal": [],     # Internal module imports
        "external": [],     # External package imports
        "stdlib": [],       # Standard library imports
        "analysis_status": "not_applied"
    })

    # === CODE SMELLS / ANTIMATTER ===
    antimatter: Dict[str, Any] = field(default_factory=lambda: {
        "god_classes": [],
        "long_methods": [],
        "high_coupling": [],
        "analysis_status": "not_applied"
    })

    # === ARCHITECTURAL PATTERNS ===
    architecture: Dict[str, Any] = field(default_factory=lambda: {
        "detected_patterns": [],  # ["DDD", "Clean Architecture", "MVC"]
        "layer_violations": [],
        "analysis_status": "not_applied"
    })

    # === LLM ENRICHMENT ===
    llm_enrichment: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "model": "none",
        "particles_enhanced": 0,
        "analysis_status": "not_applied"
    })

    # === WARNINGS / RECOMMENDATIONS ===
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dict for JSON serialization."""
        return asdict(self)

    def save(self, output_path: str):
        """Save to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str, sort_keys=True)


def create_unified_output(
    target_path: str,
    nodes: List[Dict],
    edges: List[Dict],
    stats: Dict,
    auto_discovery_report: Optional[Dict] = None,
    analysis_time_ms: int = 0,
) -> UnifiedAnalysisOutput:
    """
    Create a unified output from analysis results.
    Ensures consistent schema regardless of what analysis was performed.
    """

    output = UnifiedAnalysisOutput(
        generated_at=datetime.now().isoformat(),
        analysis_time_ms=analysis_time_ms,
        target_path=str(target_path),
        target_name=Path(target_path).name,
    )

    # Populate nodes (normalize to schema)
    for node in nodes:
        # Resolve ID: Use existing or generate formatted ID
        node_id = node.get("id")
        if not node_id:
            file = node.get("file_path", node.get("file", "unknown"))
            name = node.get("name", "unknown")
            node_id = f"{file}:{name}"

        # Normalize role/type - these are used interchangeably
        role_value = node.get("type") or node.get("role") or "Unknown"
        # Enforce canonical roles via RoleRegistry
        if _role_registry and role_value:
            role_value = _role_registry.normalize(role_value)
        kind_value = node.get("symbol_kind") or node.get("kind") or "unknown"
        layer_value = node.get("layer") or node.get("purpose_layer") or node.get("dimensions", {}).get("D2_LAYER")
        effect_value = node.get("dimensions", {}).get("D6_EFFECT", "Unknown")

        unified_node = {
            "id": node_id,
            "name": node.get("name", ""),
            "kind": kind_value,
            "symbol_kind": kind_value,  # Alias for consistent access
            "file_path": node.get("file_path", node.get("file", "")),
            "start_line": node.get("line", node.get("start_line", 0)),
            "end_line": node.get("end_line", node.get("line", 0)),
            "type": role_value,  # Synced with role for consistency
            "role": role_value,
            "role_confidence": node.get("confidence", node.get("role_confidence", 0.0)),
            "confidence": node.get("confidence", node.get("role_confidence", 0.0)),  # Alias
            "discovery_method": node.get("discovery_method", "pattern"),
            "params": node.get("params", []),
            "return_type": node.get("return_type", ""),
            "base_classes": node.get("base_classes", []),
            "decorators": node.get("decorators", []),
            "docstring": node.get("docstring", ""),
            "signature": node.get("evidence", node.get("signature", "")),
            "body_source": node.get("body_source", ""),
            "complexity": node.get("complexity", 0),
            "lines_of_code": (node.get("end_line", 0) - node.get("line", 0)) or 0,
            "in_degree": node.get("in_degree", 0),
            "out_degree": node.get("out_degree", 0),
            "layer": layer_value,
            "effect": effect_value,
            # Standard Model Theory fields
            "rpbl": node.get("rpbl", {}),
            "atom": node.get("atom", ""),
            "dimensions": node.get("dimensions", {}),
            "metadata": node.get("metadata", {}),
            # Structural containment (parent class for methods)
            "parent": node.get("parent", ""),
        }
        output.nodes.append(unified_node)

    # Populate edges
    for edge in edges:
        unified_edge = {
            "source": edge.get("source", ""),
            "target": edge.get("target", ""),
            "edge_type": edge.get("edge_type", "unknown"),
            "family": edge.get("family", "Dependency"),
            "resolution": edge.get("resolution"),
            "weight": edge.get("weight", 1.0),
            "confidence": edge.get("confidence", 1.0),
            "file_path": edge.get("file", ""),
            "line": edge.get("line", 0),
            "metadata": edge.get("metadata", {}),
        }
        output.edges.append(unified_edge)

    # Populate stats
    output.stats = {
        "total_files": stats.get("files_analyzed", stats.get("total_files", 0)),
        "total_lines": stats.get("total_lines_analyzed", stats.get("total_lines", 0)),
        "total_nodes": len(output.nodes),
        "total_edges": len(output.edges),
        "languages": list(stats.get("languages_detected", stats.get("languages", []))),
        "coverage_percentage": stats.get("recognized_percentage", stats.get("coverage_percentage", 0.0)),
        "unknown_percentage": 100.0 - stats.get("recognized_percentage", stats.get("coverage_percentage", 0.0)),
    }

    # Classification breakdown
    role_counts = {}
    kind_counts = {}
    confidence_dist = {"high": 0, "medium": 0, "low": 0}

    for node in output.nodes:
        role = node.get("role", "Unknown")
        kind = node.get("kind", "unknown")
        conf = node.get("role_confidence", 0)

        role_counts[role] = role_counts.get(role, 0) + 1
        kind_counts[kind] = kind_counts.get(kind, 0) + 1

        if conf >= 80:
            confidence_dist["high"] += 1
        elif conf >= 50:
            confidence_dist["medium"] += 1
        else:
            confidence_dist["low"] += 1

    output.classification = {
        "by_role": role_counts,
        "by_kind": kind_counts,
        "by_layer": {},  # TODO: populate from layer analysis
        "by_confidence": confidence_dist,
    }

    # Import resolution stats
    import_edges = [e for e in output.edges if e.get("edge_type") == "imports"]
    if import_edges:
        counts, _ = get_import_resolution_diagnostics(output.edges)
        output.stats["import_resolution"] = counts

    # Auto-discovery report
    if auto_discovery_report:
        output.auto_discovery = {
            "enabled": True,
            "patterns_applied": auto_discovery_report.get("total_classified", 0),
            "particles_reclassified": auto_discovery_report.get("particles_updated", 0),
            "top_patterns": auto_discovery_report.get("top_patterns", []),
            "suggested_new_patterns": auto_discovery_report.get("suggested_new_patterns", []),
        }

    return output


# === SINGLE ENTRY POINT ===

def analyze(target_path: str, output_dir: Optional[str] = None, **options) -> UnifiedAnalysisOutput:
    """
    🎯 SINGLE ENTRY POINT for all Collider analysis.

    PIPELINE ORDER:
    1. AST Parse → Raw particles
    2. RPBL Classification → Classified particles
    3. Auto Pattern Discovery → Reduced unknowns
    4. Edge Extraction → Call graph
    5. Graph Inference → Infer remaining unknowns from structure
    6. Output → Unified schema

    Args:
        target_path: Path to file, directory, or repository to analyze
        output_dir: Optional output directory
        **options: llm, llm_model, language

    Returns:
        UnifiedAnalysisOutput with consistent schema
    """
    from tree_sitter_engine import TreeSitterUniversalEngine
    from stats_generator import StatsGenerator

    start_time = time.time()
    target = Path(target_path).resolve()

    print(f"🔬 COLLIDER UNIFIED ANALYSIS")
    print(f"   Target: {target}")
    print(f"=" * 60)

    # =========================================================================
    # STAGE 1: AST PARSE → Raw Particles
    # =========================================================================
    print("\n📂 Stage 1: AST Parsing...")
    ts_engine = TreeSitterUniversalEngine()

    # Get exclusions from options (passed by survey in full_analysis.py)
    exclude_paths = options.get('exclude_paths', [])
    if exclude_paths:
        print(f"   → Excluding {len(exclude_paths)} paths from survey")

    if target.is_file():
        results = [ts_engine.analyze_file(str(target))]
    else:
        results = ts_engine.analyze_directory(str(target), exclude_paths=exclude_paths)

    raw_particle_count = sum(len(r.get('particles', [])) for r in results)
    print(f"   → {raw_particle_count} particles extracted")

    # =========================================================================
    # STAGE 2: RPBL CLASSIFICATION
    # =========================================================================
    # classifier = ParticleClassifier()

    # for result in results:
    #     classified = []
    #     for particle in result.get('particles', []):
    #         classified.append(classifier.classify_particle(particle))
    #     result['particles'] = classified

    # =========================================================================
    # STAGE 3: AUTO PATTERN DISCOVERY
    # =========================================================================
    print("\n🔍 Stage 3: Auto Pattern Discovery...")
    stats_gen = StatsGenerator()
    comprehensive = stats_gen.generate_comprehensive_stats(results)

    particles = comprehensive.get('particles', [])
    auto_discovery = comprehensive.get('auto_discovery', {})

    # =========================================================================
    # STAGE 3.5: LLM ENRICHMENT (Optional)
    # =========================================================================
    if options.get('llm'):
        print("\n🤖 Stage 3.5: LLM Enrichment...")
        try:
            from llm_classifier import LLMClassifier  # type: ignore[import-not-found]
            model_name = options.get('llm_model', 'qwen2.5:7b-instruct')
            print(f"   → Using model: {model_name}")

            enricher = LLMClassifier(model_name=model_name)

            # Identify candidates for enrichment (Unknowns or Low Confidence)
            candidates = [p for p in particles if p.get('type') == 'Unknown' or p.get('confidence', 0) < 0.5]
            print(f"   → Refining {len(candidates)} low-confidence particles...")

            refined_count = 0
            for p in candidates:
                # Basic context construction
                context = f"Name: {p.get('name')}\nFile: {p.get('file_path')}\nBody: {p.get('body_source', '')[:200]}"

                new_role, confidence = enricher.classify_with_llm(context)

                if new_role and new_role != "Unknown":
                    p['type'] = new_role
                    p['confidence'] = confidence
                    p['discovery_method'] = 'llm'
                    refined_count += 1

            print(f"   → {refined_count} particles refined by LLM")

        except ImportError:
            print("   ⚠️  LLM Classifier not found or dependencies missing")
        except Exception as e:
            print(f"   ⚠️  LLM Enrichment failed: {e}")

    # =========================================================================
    # FILE NODES: Emit module/file nodes for all scanned files
    particles, file_node_count = _emit_file_nodes(particles, results)
    if file_node_count:
        print(f"   -> {file_node_count} file nodes emitted")

    # STAGE 4: EDGE EXTRACTION → Call Graph
    # =========================================================================
    print("\n🔗 Stage 4: Edge Extraction...")
    edges = extract_call_edges(particles, results, target_path=str(target))

    # Extract exposure edges (module.exports, export statements)
    exposure_edges = extract_exposure_edges(particles, results=results)
    edges.extend(exposure_edges)

    print(f"   → {len(edges)} edges extracted ({len(exposure_edges)} exposure)")

    # Resolve edges against known nodes
    if edges:
        node_ids = {p.get('id', '') for p in particles if p.get('id')}
        file_node_ids = {
            p.get('file_path', ''): p.get('id', '')
            for p in particles
            if p.get('kind') == 'module' and p.get('file_path')
        }
        edges = resolve_edges(
            edges,
            node_ids=node_ids,
            target_root=str(target),
            file_node_ids=file_node_ids,
        )
        resolved_count = sum(1 for e in edges if e.get('resolution') == 'resolved_internal')
        print(f"   → {resolved_count}/{len(edges)} edges resolved internally")

    # =========================================================================
    # STAGE 5: GRAPH INFERENCE → Infer unknowns from structure
    # =========================================================================
    print("\n🧠 Stage 5: Graph-Based Type Inference...")
    graph_inference_report = {"total_inferred": 0, "analysis_status": "not_applied"}

    if edges:
        try:
            from graph_type_inference import apply_graph_inference
            particles, graph_inference_report = apply_graph_inference(particles, edges)
            print(f"   → {graph_inference_report.get('total_inferred', 0)} types inferred from graph")
        except ImportError as e:
            print(f"   ⚠️  Graph inference not available: {e}")
    else:
        print("   ⚠️  No edges - skipping graph inference")

    # =========================================================================
    # STAGE 5.5: PURPOSE FIELD → Assign layers to particles
    # =========================================================================
    try:
        from purpose_field import detect_purpose_field
        purpose_field = detect_purpose_field(particles, edges)

        # Build multiple lookup indices for matching
        # Build with direct key access since we filter for existence
        particle_by_id = {p['id']: p for p in particles if 'id' in p and p['id']}
        particle_by_name = {p['name']: p for p in particles if 'name' in p and p['name']}

        # Assign layers using multiple matching strategies
        for pf_node in purpose_field.nodes.values():
            layer_val = pf_node.layer.value if hasattr(pf_node.layer, 'value') else str(pf_node.layer)

            # Skip unknown layers to avoid overwriting with garbage
            if layer_val == 'unknown':
                continue

            # Strategy 1: Match by exact ID
            if pf_node.id in particle_by_id:
                particle_by_id[pf_node.id]['layer'] = layer_val
            # Strategy 2: Match by name
            elif pf_node.name in particle_by_name:
                particle_by_name[pf_node.name]['layer'] = layer_val
            # Strategy 3: Match by name in ID (file_path:name format)
            else:
                for p_id, particle in particle_by_id.items():
                    if p_id.endswith(f":{pf_node.name}") or pf_node.name == particle.get('name'):
                        particle['layer'] = layer_val
                        break

        layer_count = sum(1 for p in particles if p.get('layer') and p.get('layer') != 'unknown')
        print(f"   → {layer_count} particles assigned layers")
    except Exception as e:
        print(f"   ⚠️  Purpose field detection skipped: {e}")

    # =========================================================================
    # STAGE 5.6: STANDARD MODEL ENRICHMENT → Apply full theory
    # =========================================================================
    print("\n🧬 Stage 5.6: Standard Model Enrichment...")
    try:
        from standard_model_enricher import enrich_with_standard_model
        particles = enrich_with_standard_model(particles)

        # Count enriched particles
        with_rpbl = sum(1 for p in particles if p.get('rpbl'))
        with_atom = sum(1 for p in particles if p.get('atom'))
        print(f"   → {with_rpbl} particles with RPBL scores")
        print(f"   → {with_atom} particles with Atom IDs")
    except ImportError as e:
        print(f"   ⚠️  Standard Model enrichment not available: {e}")
    except Exception as e:
        print(f"   ⚠️  Standard Model enrichment failed: {e}")

    # =========================================================================
    # STAGE 6: OUTPUT → Unified Schema
    # =========================================================================
    print("\n📊 Stage 6: Building Unified Output...")

    summary = comprehensive.get('summary', {})
    detailed = comprehensive.get('detailed_stats', {})

    stats = {
        **summary,
        **detailed.get('file_analysis', {}),
        'languages_detected': detailed.get('language_analysis', {}).get('languages_detected', []),
    }

    # Recalculate coverage after inference
    unknown_count = sum(1 for p in particles if p.get('type') == 'Unknown')
    total_count = len(particles)
    final_coverage = ((total_count - unknown_count) / total_count * 100) if total_count else 0
    stats['recognized_percentage'] = final_coverage

    analysis_time_ms = int((time.time() - start_time) * 1000)

    output = create_unified_output(
        target_path=str(target),
        nodes=particles,
        edges=edges,
        stats=stats,
        auto_discovery_report=auto_discovery,
        analysis_time_ms=analysis_time_ms,
    )

    # Add graph inference to output
    output.architecture['graph_inference'] = graph_inference_report
    if graph_inference_report.get('total_inferred', 0) > 0:
        output.architecture['analysis_status'] = "applied"

    # Save output (unless write_output=False, used when called from full_analysis.py)
    write_output = options.get('write_output', True)
    output_file = None

    if write_output:
        if output_dir:
            out_path = Path(output_dir)
        else:
            out_path = target / "collider_output" if target.is_dir() else target.parent / "collider_output"

        out_path.mkdir(parents=True, exist_ok=True)
        output_file = out_path / "unified_analysis.json"
        output.save(str(output_file))

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print(f"\n{'=' * 60}")
    print(f"✅ ANALYSIS COMPLETE")
    print(f"   Nodes: {output.stats['total_nodes']}")
    print(f"   Edges: {output.stats['total_edges']}")
    print(f"   Coverage: {output.stats['coverage_percentage']:.1f}%")
    print(f"   Time: {analysis_time_ms}ms")
    if output_file:
        print(f"   Output: {output_file}")

    return output




def _emit_file_nodes(particles: List[Dict], results: List[Dict]) -> tuple:
    """Ensure file-level nodes exist for all scanned Python files."""
    existing_ids = set()
    for p in particles:
        node_id = p.get("id")
        if not node_id:
            file_path = p.get("file_path", "")
            name = p.get("name", "")
            if file_path and name:
                try:
                    file_path = str(Path(file_path).resolve())
                except Exception:
                    pass
                node_id = f"{file_path}:{name}"
        if node_id:
            existing_ids.add(node_id)

    file_nodes = []
    seen_files = set()

    for result in results:
        file_path = result.get("file_path", "")
        if not file_path:
            continue
        if Path(file_path).suffix != ".py":
            continue

        try:
            normalized_path = str(Path(file_path).resolve())
        except Exception:
            normalized_path = file_path

        if normalized_path in seen_files:
            continue
        seen_files.add(normalized_path)

        node_id = file_node_id(normalized_path, existing_ids)
        if node_id in existing_ids:
            continue

        node_name = node_id.rsplit(":", 1)[-1]
        # Normalize 'Module' via RoleRegistry (Module -> Utility)
        file_type = _role_registry.normalize("Module") if _role_registry else "Module"
        file_nodes.append({
            "id": node_id,
            "name": node_name,
            "kind": "module",
            "file_path": normalized_path,
            "start_line": 1,
            "end_line": result.get("lines_analyzed", 0),
            "type": file_type,
            "confidence": 100.0,
            "discovery_method": "filesystem",
            "metadata": {"file_node": True},
        })
        existing_ids.add(node_id)

    if file_nodes:
        particles = particles + file_nodes

    return particles, len(file_nodes)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        result = analyze(sys.argv[1])
        print(json.dumps(result.to_dict(), indent=2, default=str)[:2000] + "...")
    else:
        print("Usage: python unified_analysis.py <path>")
