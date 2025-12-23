"""
ATOM Intermediate Representation (IR)
=====================================
Standard Internal Representation for Code Graphs.
Used to normalize outputs from various extractors before visualization or export.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class EdgeType(Enum):
    IMPORT = "import"
    CALL = "call"
    INHERIT = "inherit"
    DATA_FLOW = "data_flow"
    CONTAINS = "contains"

@dataclass
class Component:
    """A code component (node in the graph)."""
    id: str
    name: str
    kind: str  # class, function, module, etc.
    file: str = ""
    role: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Edge:
    """A relationship between components."""
    source: str
    target: str
    edge_type: EdgeType
    weight: int = 1
    category: str = "structure"
    confidence: float = 1.0
    file: str = ""
    line: int = 0

@dataclass
class Graph:
    """Complete graph representation."""
    repo_name: str
    repo_path: str
    components: Dict[str, Component] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)

    def add_component(self, component: Component):
        self.components[component.id] = component

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

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
