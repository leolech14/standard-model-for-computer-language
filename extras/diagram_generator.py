#!/usr/bin/env python3
"""
📊 SYSTEM DIAGRAM GENERATOR — Full Application Knowledge Visualization

Generates comprehensive architectural diagrams from analyzed codebases:
1. Layer Architecture Diagram (DDD/Clean/Hexagonal)
2. Component Dependency Graph
3. Class Hierarchy Tree
4. Call Flow Diagrams
5. Module Dependency Map
6. Entity-Relationship Diagram (for DDD)

These diagrams become TOOLS for developing large systems.
"""

import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "core"))


@dataclass
class SystemDiagram:
    """Complete system diagram package."""
    repo_name: str
    
    # Diagrams (Mermaid format)
    layer_diagram: str = ""
    component_diagram: str = ""
    class_hierarchy: str = ""
    call_flow: str = ""
    module_deps: str = ""
    package_map: str = ""  # New: High-level package interaction map
    entity_relations: str = ""
    
    # Summary
    summary: str = ""
    
    # Stats
    layers: List[str] = field(default_factory=list)
    components: int = 0
    relationships: int = 0


class SystemDiagramGenerator:
    """
    Generates comprehensive system diagrams from analysis.
    """
    
    LAYER_COLORS = {
        "domain": "#4CAF50",      # Green
        "application": "#2196F3", # Blue
        "infrastructure": "#FF9800", # Orange
        "presentation": "#9C27B0",   # Purple
        "interfaces": "#00BCD4",     # Cyan
    }
    
    COMPONENT_ICONS = {
        "Entity": "🔷",
        "ValueObject": "💎",
        "AggregateRoot": "👑",
        "Repository": "🗄️",
        "UseCase": "⚡",
        "Service": "🔧",
        "DTO": "📦",
        "Error": "❌",
        "Abstract": "📐",
        "Enum": "🔢",
    }
    
    def __init__(self):
        self.engine = None
    
    def _init_engine(self):
        """Initialize learning engine."""
        if self.engine is None:
            from learning_engine import LearningEngine
            self.engine = LearningEngine(auto_learn=False)
    
    def generate(self, repo_path: str) -> SystemDiagram:
        """Generate all diagrams for a repository."""
        self._init_engine()
        
        path = Path(repo_path)
        diagram = SystemDiagram(repo_name=path.name)
        
        # Analyze
        analysis = self.engine.analyze_repo(repo_path)
        codebase = self.engine.complete_extractor.extract(repo_path)
        graph = self.engine.graph_extractor.extract(repo_path)
        
        # Extract truth for layer info
        from truth_extractor import TruthExtractor
        extractor = TruthExtractor()
        truth = extractor.extract(repo_path)
        spec = extractor.to_golden_spec(truth)
        
        diagram.layers = truth.layers
        diagram.components = len(codebase.classes)
        diagram.relationships = len(graph.edges)
        
        # Generate diagrams
        diagram.layer_diagram = self._generate_layer_diagram(
            truth, spec, codebase
        )
        diagram.component_diagram = self._generate_component_diagram(
            spec, codebase
        )
        diagram.class_hierarchy = self._generate_class_hierarchy(
            codebase, graph
        )
        diagram.call_flow = self._generate_call_flow(
            codebase, graph
        )
        diagram.module_deps = self._generate_module_deps(
            graph
        )
        diagram.package_map = self._generate_package_map(
            graph
        )
        diagram.entity_relations = self._generate_entity_relations(
            spec, codebase
        )
        diagram.summary = self._generate_summary(
            diagram, analysis, truth
        )
        
        return diagram
    
    def _generate_layer_diagram(self, truth, spec, codebase) -> str:
        """Generate DDD layer architecture diagram."""
        layers = truth.layers or ["domain", "application", "infrastructure", "presentation"]
        
        lines = [
            "```mermaid",
            "graph TB",
            "    subgraph PRESENTATION[\"🖥️ Presentation Layer\"]",
        ]
        
        # Find presentation components
        pres_comps = [c for c in spec["expected_components"] 
                      if "DTO" in c.get("type", "") or "Schema" in c.get("name", "")]
        for comp in pres_comps[:5]:
            lines.append(f"        {comp['name'].replace(' ', '_')}[\"{comp['name']}\"]")
        if not pres_comps:
            lines.append("        API[\"API/Handlers\"]")
        
        lines.extend([
            "    end",
            "",
            "    subgraph APPLICATION[\"⚡ Application Layer\"]",
        ])
        
        # Find use cases
        usecases = [c for c in spec["expected_components"]
                    if "UseCase" in c.get("type", "") or "UseCase" in c.get("name", "")]
        for uc in usecases[:8]:
            lines.append(f"        {uc['name'].replace(' ', '_')}[\"{uc['name']}\"]")
        if not usecases:
            lines.append("        UseCases[\"Use Cases\"]")
        
        lines.extend([
            "    end",
            "",
            "    subgraph DOMAIN[\"🔷 Domain Layer\"]",
        ])
        
        # Find entities
        entities = [c for c in spec["expected_components"]
                    if c.get("type", "") in ("Entity", "AggregateRoot", "ValueObject")]
        for ent in entities[:8]:
            icon = self.COMPONENT_ICONS.get(ent.get("type", ""), "")
            lines.append(f"        {ent['name'].replace(' ', '_')}[\"{icon} {ent['name']}\"]")
        if not entities:
            lines.append("        Entities[\"Entities\"]")
        
        lines.extend([
            "    end",
            "",
            "    subgraph INFRASTRUCTURE[\"🗄️ Infrastructure Layer\"]",
        ])
        
        # Find repositories
        repos = [c for c in spec["expected_components"]
                 if "Repository" in c.get("type", "") or "Impl" in c.get("name", "")]
        for repo in repos[:5]:
            lines.append(f"        {repo['name'].replace(' ', '_')}[\"{repo['name']}\"]")
        if not repos:
            lines.append("        Repositories[\"Repositories\"]")
        
        lines.extend([
            "    end",
            "",
            "    PRESENTATION --> APPLICATION",
            "    APPLICATION --> DOMAIN",
            "    APPLICATION --> INFRASTRUCTURE",
            "    INFRASTRUCTURE --> DOMAIN",
            "```",
        ])
        
        return "\n".join(lines)
    
    def _generate_component_diagram(self, spec, codebase) -> str:
        """Generate component dependency diagram."""
        lines = [
            "```mermaid",
            "graph LR",
        ]
        
        # Group by type
        by_type = defaultdict(list)
        for comp in spec["expected_components"]:
            by_type[comp.get("type", "Unknown")].append(comp["name"])
        
        for comp_type, names in by_type.items():
            icon = self.COMPONENT_ICONS.get(comp_type, "📦")
            lines.append(f"    subgraph {comp_type}[\"{icon} {comp_type}\"]")
            for name in names[:6]:
                safe_name = name.replace(" ", "_").replace("-", "_")
                lines.append(f"        {safe_name}[\"{name}\"]")
            if len(names) > 6:
                lines.append(f"        more_{comp_type}[\"...+{len(names)-6} more\"]")
            lines.append("    end")
        
        lines.append("```")
        return "\n".join(lines)
    
    def _generate_class_hierarchy(self, codebase, graph) -> str:
        """Generate class inheritance hierarchy."""
        lines = [
            "```mermaid",
            "graph TB",
        ]
        
        # Find inheritance relationships (edge_type is 'inherit' not 'inherits')
        inheritance_edges = [e for e in graph.edges if e.edge_type == "inherit"]
        
        seen = set()
        for edge in inheritance_edges[:50]:  # Increased limit
            # Extract clean names from source/target
            child = edge.source.split(":")[-1].split(".")[-1].replace(" ", "_").replace("-", "_")
            parent = edge.target.split(":")[-1].split(".")[-1].replace(" ", "_").replace("-", "_")
            if child and parent and (child, parent) not in seen:
                lines.append(f"    {parent} --> {child}")
                seen.add((child, parent))
        
        if not inheritance_edges:
            lines.append("    NoInheritance[\"No inheritance detected\"]")
        else:
            lines.insert(1, f"    %% {len(inheritance_edges)} inheritance relationships")
        
        lines.append("```")
        return "\n".join(lines)
    
    def _generate_call_flow(self, codebase, graph) -> str:
        """Generate function call flow diagram."""
        lines = [
            "```mermaid",
            "flowchart LR",  # Changed from sequenceDiagram for better call graph
        ]
        
        # Find call relationships (edge_type is 'call' not 'calls')
        call_edges = [e for e in graph.edges if e.edge_type == "call"][:40]  # Increased limit
        
        seen = set()
        subgraphs = {}  # Group by file
        
        for edge in call_edges:
            # Extract clean names
            src = edge.source.split(":")[-1] if ":" in edge.source else edge.source
            src = src.split(".")[-1].replace(" ", "_").replace("-", "_")[:20]
            tgt = edge.target.split(":")[-1] if ":" in edge.target else edge.target  
            tgt = tgt.split(".")[-1].replace(" ", "_").replace("-", "_")[:20]
            
            if src and tgt and src != tgt and (src, tgt) not in seen:
                lines.append(f"    {src} --> {tgt}")
                seen.add((src, tgt))
        
        if not call_edges:
            lines.append("    NoCallFlow[\"No call flow detected\"]")
        else:
            lines.insert(1, f"    %% {len(call_edges)} call relationships")
        
        lines.append("```")
        return "\n".join(lines)
    
    def _generate_module_deps(self, graph) -> str:
        """Generate module dependency diagram."""
        lines = [
            "```mermaid",
            "graph LR",
        ]
        
        # Find import relationships (edge_type is 'import' not 'imports')
        import_edges = [e for e in graph.edges if e.edge_type == "import"][:40]
        
        seen = set()
        for edge in import_edges:
            # Extract meaningful module names
            src = edge.source.split(":")[-1].split("/")[-1].replace(".py", "")
            tgt = edge.target.split(":")[-1].split(".")[-1]
            src = src.replace("-", "_")[:20]
            tgt = tgt.replace("-", "_")[:20]
            if src and tgt and (src, tgt) not in seen and src != tgt:
                lines.append(f"    {src} --> {tgt}")
                seen.add((src, tgt))
        
        if not import_edges:
            lines.append("    NoImports[\"No imports detected\"]")
        else:
            lines.insert(1, f"    %% {len(import_edges)} import relationships")
        
        lines.append("```")
        return "\n".join(lines)

    def _generate_package_map(self, graph) -> str:
        """Generate high-level package interaction map (Heterogeneity View)."""
        lines = [
            "```mermaid",
            "graph TB",
        ]
        
        # Group checks by top-level directory
        import_edges = [e for e in graph.edges if e.edge_type == "import"]
        
        package_deps = defaultdict(int)
        
        for edge in import_edges:
            # Source path format: file:path/to/file.py
            # Target path format: module:pkg.subpkg.mod
            
            # Extract source top-level dir
            src_path = edge.source.split(":")[-1]
            src_parts = src_path.split("/")
            src_pkg = src_parts[0] if len(src_parts) > 1 else "root"
            if src_pkg in [".", ".."]: src_pkg = "root"
            
            # Extract target top-level package
            tgt_path = edge.target.split(":")[-1]
            tgt_parts = tgt_path.split(".")
            tgt_pkg = tgt_parts[0]
            
            # Filter standard library/external common
            if tgt_pkg in ["typing", "datetime", "pathlib", "collections", "json", "sys", "os", "logging"]:
                continue
                
            if src_pkg != tgt_pkg:
                package_deps[(src_pkg, tgt_pkg)] += 1
        
        # Sort by frequency
        sorted_deps = sorted(package_deps.items(), key=lambda x: x[1], reverse=True)[:30]
        
        for (src, tgt), count in sorted_deps:
            s_clean = src.replace("-", "_").replace(".", "_")
            t_clean = tgt.replace("-", "_").replace(".", "_")
            weight = "thick" if count > 10 else "thin"
            lines.append(f"    {s_clean} -{'-' if weight == 'thick' else '-'}-> {t_clean}")
            
        if not sorted_deps:
            lines.append("    NoInterPackageDeps[\"No cross-package dependencies detected\"]")
            
        lines.append("```")
        return "\n".join(lines)
    
    def _generate_entity_relations(self, spec, codebase) -> str:
        """Generate entity-relationship diagram."""
        lines = [
            "```mermaid",
            "erDiagram",
        ]
        
        # Find entities and their relationships
        entities = [c for c in spec["expected_components"]
                    if c.get("type", "") in ("Entity", "AggregateRoot")]
        
        for ent in entities[:10]:
            safe_name = ent["name"].replace(" ", "_").replace("-", "_")
            lines.append(f"    {safe_name} {{")
            lines.append(f"        string id PK")
            lines.append(f"    }}")
        
        # Add some relationships
        for i, ent in enumerate(entities[:-1]):
            if i < 5:
                src = ent["name"].replace(" ", "_").replace("-", "_")
                tgt = entities[i+1]["name"].replace(" ", "_").replace("-", "_")
                lines.append(f"    {src} ||--o{{ {tgt} : \"contains\"")
        
        if not entities:
            lines.append("    NoEntities[\"No entities detected\"]")
        
        lines.append("```")
        return "\n".join(lines)
    
    def _generate_summary(self, diagram, analysis, truth) -> str:
        """Generate summary markdown."""
        return f"""# 📊 System Diagram: {diagram.repo_name}

## Overview
| Metric | Value |
|--------|------:|
| Layers | {', '.join(diagram.layers) if diagram.layers else 'Unknown'} |
| Components | {diagram.components} |
| Relationships | {diagram.relationships} |
| Coverage | {analysis.coverage_pct:.1f}% |
| Semantic IDs | {analysis.semantic_ids} |

## Architecture
{diagram.layer_diagram}

## Components by Type
{diagram.component_diagram}

## Class Hierarchy
{diagram.class_hierarchy}

## Call Flow
{diagram.call_flow}

## Package Heterogeneity Map
{diagram.package_map}

## Module Dependencies
{diagram.module_deps}

## Entity Relationships
{diagram.entity_relations}
"""
    
    def export(self, diagram: SystemDiagram, output_path: str):
        """Export diagram to file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(diagram.summary)
        return path


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="📊 System Diagram Generator — Full application knowledge"
    )
    parser.add_argument("repo_path", help="Path to repository")
    parser.add_argument("--output", help="Output path for diagram")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("📊 SYSTEM DIAGRAM GENERATOR")
    print("=" * 70)
    
    gen = SystemDiagramGenerator()
    diagram = gen.generate(args.repo_path)
    
    print(f"\n📁 Repo: {diagram.repo_name}")
    print(f"🏛️ Layers: {diagram.layers}")
    print(f"📦 Components: {diagram.components}")
    print(f"🔗 Relationships: {diagram.relationships}")
    
    if args.output:
        out = gen.export(diagram, args.output)
        print(f"\n💾 Exported: {out}")
    else:
        print("\n" + diagram.summary)
