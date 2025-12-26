"""
Execution Flow Detector

Analyzes code execution flow as a parallel semantic layer to Purpose Field:
- Level 1: Node Mapping (structural identity - atoms)
- Level 2: Purpose Field (semantic purpose - roles/layers)
- Level 3: Execution Flow (causality sequence)

Capabilities:
- Causality chain detection (entry → calls → exit)
- Orphan detection (dead code, unused functions)
- Integration error detection (broken references)
- Cross-layer correlation with Purpose Field
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum


class FlowType(Enum):
    """Types of execution flow"""
    CALL = "call"           # Function/method call
    IMPORT = "import"       # Module import
    INHERIT = "inherit"     # Class inheritance
    INSTANTIATE = "new"     # Object instantiation


@dataclass
class FlowNode:
    """A node in the execution flow graph"""
    id: str
    name: str
    kind: str                   # function, class, module
    
    # Purpose Field correlation
    role: str = "Unknown"       # From Purpose Field
    layer: str = "unknown"      # From Purpose Field
    
    # Flow properties
    in_degree: int = 0          # How many call this
    out_degree: int = 0         # How many this calls
    
    # Node status
    is_entry_point: bool = False    # Root node (explicitly callable)
    is_orphan: bool = False         # Never called & not entry point
    is_public: bool = True          # Public API (no underscore prefix)
    
    # Connections
    callers: List[str] = field(default_factory=list)
    callees: List[str] = field(default_factory=list)


@dataclass
class CausalityChain:
    """A sequence of execution from entry to exits"""
    entry_point: str
    path: List[str]             # Node IDs in order
    length: int
    layers_crossed: List[str]   # Purpose layers traversed
    has_violation: bool         # Does flow violate layer rules?


@dataclass
class IntegrationError:
    """A detected integration problem"""
    type: str                   # missing_call, circular_dep, layer_violation
    source: str                 # Source node
    target: str                 # Target node (if applicable)
    message: str


@dataclass
class ExecutionFlow:
    """Complete execution flow analysis of a codebase"""
    nodes: Dict[str, FlowNode]
    chains: List[CausalityChain]
    orphans: List[str]
    entry_points: List[str]
    integration_errors: List[IntegrationError]
    
    # Statistics
    total_nodes: int = 0
    reachable_nodes: int = 0
    dead_code_percent: float = 0.0
    
    def summary(self) -> dict:
        """Summarize execution flow"""
        layer_distribution = defaultdict(int)
        orphan_by_layer = defaultdict(list)
        
        for node in self.nodes.values():
            layer_distribution[node.layer] += 1
            if node.is_orphan:
                orphan_by_layer[node.layer].append(node.name)
        
        return {
            "total_nodes": self.total_nodes,
            "entry_points": len(self.entry_points),
            "reachable_nodes": self.reachable_nodes,
            "orphan_count": len(self.orphans),
            "dead_code_percent": self.dead_code_percent,
            "chains_count": len(self.chains),
            "integration_errors": len(self.integration_errors),
            "layer_distribution": dict(layer_distribution),
            "orphans_by_layer": {k: len(v) for k, v in orphan_by_layer.items()}
        }
    
    def correlate_with_purpose(self, purpose_field) -> dict:
        """Correlate execution flow with purpose field"""
        # Count flow violations by layer pair
        layer_violations = defaultdict(int)
        
        for chain in self.chains:
            if chain.has_violation:
                for i in range(len(chain.layers_crossed) - 1):
                    pair = f"{chain.layers_crossed[i]} → {chain.layers_crossed[i+1]}"
                    layer_violations[pair] += 1
        
        return {
            "flow_layer_violations": dict(layer_violations),
            "orphans_with_purpose": {
                node_id: self.nodes[node_id].role 
                for node_id in self.orphans 
                if node_id in self.nodes
            }
        }


class ExecutionFlowDetector:
    """Detects execution flow patterns in code"""
    
    # Entry point detection patterns
    ENTRY_PATTERNS = {
        "decorators": ["@app.route", "@router", "@pytest.fixture", "@click.command", 
                       "@main", "@entrypoint", "@api", "@task"],
        "names": ["main", "run", "start", "execute", "cli", "app"],
        "prefixes": ["test_", "setup_", "teardown_"],
        "suffixes": ["_main", "_cli", "_app"],
    }
    
    # Layer order for violation detection (lower = higher in architecture)
    LAYER_ORDER = {
        "presentation": 0,
        "application": 1,
        "domain": 2,
        "infrastructure": 3,
        "testing": 4,
        "unknown": 99
    }
    
    def __init__(self):
        self.nodes: Dict[str, FlowNode] = {}
        self.edges: Dict[str, Set[str]] = defaultdict(set)  # source -> targets
        self.reverse_edges: Dict[str, Set[str]] = defaultdict(set)  # target -> sources
    
    def detect_flow(self, analysis_nodes: list, edges: list, 
                    purpose_nodes: dict = None) -> ExecutionFlow:
        """
        Detect execution flow from analysis output.
        
        Args:
            analysis_nodes: Nodes from unified_analysis
            edges: Edges from unified_analysis
            purpose_nodes: Optional Purpose Field nodes for correlation
        """
        # Stage 1: Build flow nodes
        self._build_nodes(analysis_nodes, purpose_nodes)
        
        # Stage 2: Build edge graph
        self._build_edges(edges)
        
        # Stage 3: Detect entry points
        entry_points = self._detect_entry_points()
        
        # Stage 4: Find reachable nodes (from entry points)
        reachable = self._find_reachable(entry_points)
        
        # Stage 5: Detect orphans
        orphans = self._detect_orphans(reachable)
        
        # Stage 6: Build causality chains
        chains = self._build_chains(entry_points)
        
        # Stage 7: Detect integration errors
        errors = self._detect_integration_errors()
        
        # Calculate statistics
        total = len(self.nodes)
        dead_code_pct = len(orphans) / total * 100 if total else 0
        
        return ExecutionFlow(
            nodes=self.nodes,
            chains=chains,
            orphans=orphans,
            entry_points=entry_points,
            integration_errors=errors,
            total_nodes=total,
            reachable_nodes=len(reachable),
            dead_code_percent=round(dead_code_pct, 2)
        )
    
    def _build_nodes(self, analysis_nodes: list, purpose_nodes: dict = None):
        """Build FlowNodes from analysis output"""
        purpose_nodes = purpose_nodes or {}
        
        for i, node in enumerate(analysis_nodes):
            # Handle both dict and object
            if hasattr(node, 'name'):
                node_id = node.id if node.id else node.name
                name = node.name
                kind = node.kind
                role = getattr(node, 'role', 'Unknown')
                decorators = getattr(node, 'decorators', [])
            else:
                node_id = node.get('id') or node.get('name') or f"node_{i}"
                name = node.get('name', '')
                kind = node.get('kind', 'function')
                role = node.get('role', 'Unknown')
                decorators = node.get('decorators', [])
            
            # Get layer from purpose field if available
            layer = "unknown"
            if node_id in purpose_nodes:
                pn = purpose_nodes[node_id]
                layer = pn.layer.value if hasattr(pn.layer, 'value') else str(pn.layer)
            
            # Determine if public (no underscore prefix)
            # Handle fully qualified names (Class.method)
            short_name = name.split('.')[-1]
            # Public if doesn't start with _, BUT dunder methods (e.g. __init__)
            # are considered "internal/implicit" so we don't flag them as public orphans.
            is_public = not short_name.startswith('_')
            # Note: We treat __init__ etc as NOT public for orphan checks because 
            # they are invoked implicitly usually. OR we could check startswith('__') -> False.
            
            # Check if entry point
            # TRUST THE ROLE if it was already classified as EntryPoint
            is_entry = self._is_entry_point(name, decorators) or role == 'EntryPoint'
            
            self.nodes[node_id] = FlowNode(
                id=node_id,
                name=name,
                kind=kind,
                role=role,
                layer=layer,
                is_entry_point=is_entry,
                is_public=is_public
            )
    
    def _build_edges(self, edges: list):
        """Build edge graph"""
        for edge in edges:
            if isinstance(edge, dict):
                source = edge.get('source', edge.get('from', ''))
                target = edge.get('target', edge.get('to', ''))
            elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
                source, target = edge[0], edge[1]
            else:
                continue
            
            if source and target:
                self.edges[source].add(target)
                self.reverse_edges[target].add(source)
                
                # Update degrees
                if source in self.nodes:
                    self.nodes[source].out_degree += 1
                    self.nodes[source].callees.append(target)
                if target in self.nodes:
                    self.nodes[target].in_degree += 1
                    self.nodes[target].callers.append(source)
    
    def _is_entry_point(self, name: str, decorators: list) -> bool:
        """Determine if a node is an entry point"""
        name_lower = name.lower()
        
        # Check decorators
        for dec in decorators:
            dec_str = str(dec).lower()
            for pattern in self.ENTRY_PATTERNS["decorators"]:
                if pattern.lower() in dec_str:
                    return True
        
        # Check name patterns
        for entry_name in self.ENTRY_PATTERNS["names"]:
            if name_lower == entry_name:
                return True
        
        for prefix in self.ENTRY_PATTERNS["prefixes"]:
            if name_lower.startswith(prefix):
                return True
        
        for suffix in self.ENTRY_PATTERNS["suffixes"]:
            if name_lower.endswith(suffix):
                return True
        
        # Special: if __name__ == "__main__" patterns
        if name_lower in ["__main__", "if_main"]:
            return True
        
        return False
    
    def _detect_entry_points(self) -> List[str]:
        """Find all entry points"""
        entries = []
        
        for node_id, node in self.nodes.items():
            # Explicit entry points
            if node.is_entry_point:
                entries.append(node_id)
            # Implicit: public functions with no callers
            elif node.in_degree == 0 and node.is_public and node.kind in ['function', 'class']:
                entries.append(node_id)
        
        return entries
    
    def _find_reachable(self, entry_points: List[str]) -> Set[str]:
        """Find all nodes reachable from entry points (BFS)"""
        reachable = set()
        queue = list(entry_points)
        
        while queue:
            current = queue.pop(0)
            if current in reachable:
                continue
            reachable.add(current)
            
            for target in self.edges.get(current, []):
                if target not in reachable:
                    queue.append(target)
        
        return reachable
    
    def _detect_orphans(self, reachable: Set[str]) -> List[str]:
        """Find orphan nodes (not reachable and not entry points)"""
        orphans = []
        
        for node_id, node in self.nodes.items():
            # Only flag public non-entry-point nodes
            if node_id not in reachable and node.is_public and not node.is_entry_point:
                node.is_orphan = True
                orphans.append(node_id)
        
        return orphans
    
    def _build_chains(self, entry_points: List[str], max_depth: int = 20) -> List[CausalityChain]:
        """Build causality chains from entry points"""
        chains = []
        
        for entry in entry_points[:50]:  # Limit for performance
            visited = set()
            path = []
            layers = []
            
            self._trace_chain(entry, path, layers, visited, max_depth)
            
            if path:
                has_violation = self._check_layer_violation(layers)
                chains.append(CausalityChain(
                    entry_point=entry,
                    path=path[:max_depth],
                    length=len(path),
                    layers_crossed=layers[:max_depth],
                    has_violation=has_violation
                ))
        
        return chains
    
    def _trace_chain(self, node_id: str, path: list, layers: list, 
                     visited: set, depth: int):
        """Recursively trace a causality chain"""
        if depth <= 0 or node_id in visited:
            return
        
        visited.add(node_id)
        path.append(node_id)
        
        if node_id in self.nodes:
            layers.append(self.nodes[node_id].layer)
        
        for target in list(self.edges.get(node_id, []))[:5]:  # Limit branching
            self._trace_chain(target, path, layers, visited, depth - 1)
    
    def _check_layer_violation(self, layers: List[str]) -> bool:
        """Check if layer sequence has violations"""
        for i in range(len(layers) - 1):
            current_order = self.LAYER_ORDER.get(layers[i], 99)
            next_order = self.LAYER_ORDER.get(layers[i + 1], 99)
            
            # Violation: lower layer (infra) calling higher layer (presentation)
            if current_order > next_order and current_order != 99 and next_order != 99:
                return True
        
        return False
    
    def _detect_integration_errors(self) -> List[IntegrationError]:
        """Detect integration errors"""
        errors = []
        
        # Find calls to non-existent nodes
        for source, targets in self.edges.items():
            for target in targets:
                if target not in self.nodes:
                    errors.append(IntegrationError(
                        type="missing_reference",
                        source=source,
                        target=target,
                        message=f"{source} references missing {target}"
                    ))
        
        # Find circular dependencies (simplified)
        for node_id in list(self.nodes.keys())[:100]:  # Limit for performance
            if node_id in self.edges.get(node_id, set()):
                errors.append(IntegrationError(
                    type="self_reference",
                    source=node_id,
                    target=node_id,
                    message=f"{node_id} references itself"
                ))
        
        return errors


def detect_execution_flow(nodes: list, edges: list, purpose_field=None) -> ExecutionFlow:
    """
    Convenience function to detect execution flow.
    
    Usage:
        from execution_flow import detect_execution_flow
        
        result = analyze(path)
        flow = detect_execution_flow(result.nodes, result.edges)
        print(flow.summary())
    """
    purpose_nodes = {}
    if purpose_field and hasattr(purpose_field, 'nodes'):
        purpose_nodes = purpose_field.nodes
    
    detector = ExecutionFlowDetector()
    return detector.detect_flow(nodes, edges, purpose_nodes)


if __name__ == "__main__":
    import json
    
    # Demo with simple test data
    test_nodes = [
        {"id": "main", "name": "main", "kind": "function", "role": "Entry"},
        {"id": "process", "name": "process", "kind": "function", "role": "Service"},
        {"id": "save", "name": "save", "kind": "function", "role": "Repository"},
        {"id": "orphan", "name": "orphan_func", "kind": "function", "role": "Utility"},
    ]
    
    test_edges = [
        ("main", "process"),
        ("process", "save"),
    ]
    
    flow = detect_execution_flow(test_nodes, test_edges)
    
    print("Execution Flow Summary:")
    print(json.dumps(flow.summary(), indent=2))
    
    if flow.orphans:
        print(f"\nOrphans detected: {flow.orphans}")
