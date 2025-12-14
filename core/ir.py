#!/usr/bin/env python3
"""
📦 INTERMEDIATE REPRESENTATION (IR) — The Unified Language of Spectrometer

Both pipelines (full/tree-sitter and minimal/regex) produce this same IR.
All downstream consumers (diagrams, scoring, LLM context) read only from IR.

This is the contract that makes the system coherent.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
import json


# =============================================================================
# EDGE TYPES
# =============================================================================

class EdgeType(Enum):
    """Types of edges between components."""
    IMPORT = "import"       # File-level import
    CALL = "call"           # Function/method invocation
    INHERIT = "inherit"     # Class inheritance
    IMPLEMENT = "implement" # Interface implementation
    USE = "use"             # General usage (unspecified)
    DATA_FLOW = "data_flow" # Variable flows from A to B
    DECORATE = "decorate"   # Decorator applied to
    INSTANTIATE = "instantiate"  # Creates instance of


# =============================================================================
# EDGE IR
# =============================================================================

@dataclass
class Edge:
    """
    A relationship between two code components.
    
    This is the unified edge format consumed by all downstream tools.
    """
    source: str          # Source component ID (qualified name or file path)
    target: str          # Target component ID
    edge_type: EdgeType  # Type of relationship
    
    # Location (evidence)
    file: str = ""       # File where the edge appears
    line: int = 0        # Line number
    
    # Confidence
    confidence: float = 1.0  # 0.0-1.0 (1.0 = statically proven)
    
    # Metadata
    category: str = ""   # internal, external, stdlib
    weight: int = 1      # Number of occurrences (for import edges)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type.value,
            "file": self.file,
            "line": self.line,
            "confidence": self.confidence,
            "category": self.category,
            "weight": self.weight,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'Edge':
        """Create from dict."""
        return cls(
            source=d["source"],
            target=d["target"],
            edge_type=EdgeType(d["edge_type"]),
            file=d.get("file", ""),
            line=d.get("line", 0),
            confidence=d.get("confidence", 1.0),
            category=d.get("category", ""),
            weight=d.get("weight", 1),
            metadata=d.get("metadata", {}),
        )


# =============================================================================
# COMPONENT IR  
# =============================================================================

@dataclass
class Component:
    """
    A code entity (function, class, module, endpoint, etc.)
    
    This is the unified node format consumed by all downstream tools.
    """
    id: str              # Unique identifier (qualified name)
    name: str            # Simple name
    kind: str            # class, function, module, endpoint, etc.
    
    # Location
    file: str = ""       # File path
    start_line: int = 0
    end_line: int = 0
    
    # Classification (from heuristics or LLM)
    role: Optional[str] = None      # Entity, Repository, UseCase, etc.
    role_confidence: float = 0.0
    role_evidence: List[Dict] = field(default_factory=list)
    
    # Structural metadata
    signature: str = ""
    docstring: str = ""
    decorators: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    
    # Graph position (computed after graph is built)
    layer: Optional[str] = None     # domain, application, infrastructure, presentation
    in_degree: int = 0              # Number of incoming edges
    out_degree: int = 0             # Number of outgoing edges
    
    # Scoring
    rpbl: Dict[str, float] = field(default_factory=dict)  # Responsibility, Purity, Boundary, Lifecycle
    risk_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'Component':
        """Create from dict."""
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# =============================================================================
# GRAPH IR
# =============================================================================

@dataclass
class Graph:
    """
    Complete graph representation of a codebase.
    
    This is the unified output format that both pipelines produce.
    """
    repo_name: str
    repo_path: str
    
    # Nodes and edges
    components: Dict[str, Component] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)
    
    # Indexes (built during construction)
    _edges_by_source: Dict[str, List[Edge]] = field(default_factory=dict, repr=False)
    _edges_by_target: Dict[str, List[Edge]] = field(default_factory=dict, repr=False)
    
    def add_component(self, comp: Component):
        """Add a component to the graph."""
        self.components[comp.id] = comp
    
    def add_edge(self, edge: Edge):
        """Add an edge to the graph."""
        self.edges.append(edge)
        
        # Index by source
        if edge.source not in self._edges_by_source:
            self._edges_by_source[edge.source] = []
        self._edges_by_source[edge.source].append(edge)
        
        # Index by target
        if edge.target not in self._edges_by_target:
            self._edges_by_target[edge.target] = []
        self._edges_by_target[edge.target].append(edge)
        
        # Update degrees
        if edge.source in self.components:
            self.components[edge.source].out_degree += 1
        if edge.target in self.components:
            self.components[edge.target].in_degree += 1
    
    def get_outgoing(self, component_id: str) -> List[Edge]:
        """Get all edges originating from a component."""
        return self._edges_by_source.get(component_id, [])
    
    def get_incoming(self, component_id: str) -> List[Edge]:
        """Get all edges pointing to a component."""
        return self._edges_by_target.get(component_id, [])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        edge_types = {}
        for e in self.edges:
            t = e.edge_type.value
            edge_types[t] = edge_types.get(t, 0) + 1
        
        component_kinds = {}
        for c in self.components.values():
            k = c.kind
            component_kinds[k] = component_kinds.get(k, 0) + 1
        
        roles = {}
        for c in self.components.values():
            r = c.role or "Unknown"
            roles[r] = roles.get(r, 0) + 1
        
        return {
            "total_components": len(self.components),
            "total_edges": len(self.edges),
            "component_kinds": component_kinds,
            "edge_types": edge_types,
            "roles": roles,
            "avg_in_degree": sum(c.in_degree for c in self.components.values()) / max(1, len(self.components)),
            "avg_out_degree": sum(c.out_degree for c in self.components.values()) / max(1, len(self.components)),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "repo_name": self.repo_name,
            "repo_path": self.repo_path,
            "components": {k: v.to_dict() for k, v in self.components.items()},
            "edges": [e.to_dict() for e in self.edges],
            "stats": self.get_stats(),
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_mermaid(self, max_nodes: int = 50, edge_types: Optional[List[EdgeType]] = None) -> str:
        """Generate Mermaid diagram."""
        lines = ["graph LR"]
        
        # Filter edges
        edges = self.edges
        if edge_types:
            edges = [e for e in edges if e.edge_type in edge_types]
        
        # Get most connected components
        component_weights = {}
        for e in edges:
            component_weights[e.source] = component_weights.get(e.source, 0) + 1
            component_weights[e.target] = component_weights.get(e.target, 0) + 1
        
        top_components = sorted(component_weights.keys(), key=lambda x: component_weights[x], reverse=True)[:max_nodes]
        top_set = set(top_components)
        
        # Add nodes
        for cid in top_components:
            comp = self.components.get(cid)
            label = comp.name if comp else cid.split(".")[-1]
            role = comp.role if comp else "Unknown"
            
            # Style by role
            if role in ["Entity", "ValueObject", "AggregateRoot"]:
                lines.append(f'    {self._safe_id(cid)}["{label}"]:::domain')
            elif role in ["UseCase", "Command", "Query"]:
                lines.append(f'    {self._safe_id(cid)}("{label}"):::application')
            elif role in ["Repository", "Gateway", "Client"]:
                lines.append(f'    {self._safe_id(cid)}[("{label}")]:::infrastructure')
            elif role in ["Controller", "Endpoint"]:
                lines.append(f'    {self._safe_id(cid)}[/"{label}"/]:::presentation')
            else:
                lines.append(f'    {self._safe_id(cid)}["{label}"]')
        
        # Add edges
        for e in edges:
            if e.source in top_set and e.target in top_set:
                arrow = "-->" if e.edge_type in [EdgeType.CALL, EdgeType.USE] else "-..->"
                lines.append(f'    {self._safe_id(e.source)} {arrow} {self._safe_id(e.target)}')
        
        # Add styles
        lines.extend([
            "",
            "    classDef domain fill:#A8E6CF,stroke:#4CAF50",
            "    classDef application fill:#FFD93D,stroke:#FFC107",
            "    classDef infrastructure fill:#6C5CE7,stroke:#5E35B1,color:#fff",
            "    classDef presentation fill:#74B9FF,stroke:#2196F3",
        ])
        
        return "\n".join(lines)
    
    def _safe_id(self, s: str) -> str:
        """Convert to Mermaid-safe ID."""
        return s.replace(".", "_").replace("/", "_").replace("-", "_")


# =============================================================================
# CONVERTERS (from existing formats to IR)
# =============================================================================

def edges_from_dependency_analyzer(dep_summary: Dict[str, Any], source_file: str = "") -> List[Edge]:
    """
    Convert DependencyAnalyzer output to Edge IR.
    
    The `dep_summary` is what DependencyAnalyzer.analyze_repository() attaches
    to each file result as `dependencies`.
    """
    edges = []
    
    for category in ["internal", "external", "stdlib"]:
        for dep in dep_summary.get(category, []):
            target = dep.get("target") or dep.get("resolved_file") or ""
            if not target:
                continue
            
            edges.append(Edge(
                source=source_file,
                target=target,
                edge_type=EdgeType.IMPORT,
                file=source_file,
                line=dep.get("line", 0),
                category=category,
                confidence=1.0,  # Imports are proven
                metadata={"kind": dep.get("kind", "import")},
            ))
    
    return edges


def edges_from_internal_edges_list(internal_edges: List[Dict]) -> List[Edge]:
    """
    Convert the `internal_edges` summary from DependencyAnalyzer to Edge IR.
    
    This is the aggregated list: [{"from": "a.py", "to": "b.py", "count": 3}, ...]
    """
    return [
        Edge(
            source=e["from"],
            target=e["to"],
            edge_type=EdgeType.IMPORT,
            weight=e.get("count", 1),
            category="internal",
            confidence=1.0,
        )
        for e in internal_edges
    ]


# =============================================================================
# CLI DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("📦 INTERMEDIATE REPRESENTATION (IR) — Unified Graph Format")
    print("=" * 70)
    print()
    
    # Demo: Create a simple graph
    g = Graph(repo_name="demo", repo_path="/demo")
    
    # Add components
    g.add_component(Component(
        id="demo.user_repo.UserRepository",
        name="UserRepository",
        kind="class",
        file="infrastructure/user_repo.py",
        role="Repository",
        role_confidence=0.85,
    ))
    
    g.add_component(Component(
        id="demo.user_service.UserService",
        name="UserService",
        kind="class",
        file="application/user_service.py",
        role="UseCase",
        role_confidence=0.72,
    ))
    
    # Add edge
    g.add_edge(Edge(
        source="demo.user_service.UserService",
        target="demo.user_repo.UserRepository",
        edge_type=EdgeType.IMPORT,
        file="application/user_service.py",
        line=3,
        category="internal",
    ))
    
    print("📊 Graph Stats:")
    for k, v in g.get_stats().items():
        print(f"   {k}: {v}")
    print()
    
    print("📐 Mermaid Diagram:")
    print("-" * 40)
    print(g.to_mermaid())
    print()
    
    print("✅ IR module ready")
