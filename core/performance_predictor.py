"""
Performance Predictor

Layer 4 of the Standard Model semantic layers:
- Layer 1: Node Mapping (structural identity)
- Layer 2: Purpose Field (semantic purpose)
- Layer 3: Execution Flow (causality sequence)
- Layer 4: Performance (time estimation)

Capabilities:
- Time type classification (5 types)
- Cost estimation per node
- Critical path detection
- Hotspot identification
- Time distribution by layer
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import re


class TimeType(Enum):
    """Time complexity types for nodes"""
    INSTANT = "τ_instant"       # O(1) trivial ops (getters, DTOs)
    COMPUTE = "τ_compute"       # CPU-bound logic
    IO_LOCAL = "τ_io_local"     # Local I/O (disk, cache)
    IO_NETWORK = "τ_io_network" # Network I/O (API, DB)
    BLOCKING = "τ_blocking"     # Synchronous waits


# Time type assignment rules by role
ROLE_TO_TIME_TYPE = {
    # Instant operations
    "Controller": TimeType.INSTANT,
    "DTO": TimeType.INSTANT,
    "ValueObject": TimeType.INSTANT,
    "Factory": TimeType.INSTANT,
    "Configuration": TimeType.INSTANT,
    "Entity": TimeType.INSTANT,
    
    # Compute operations
    "Query": TimeType.COMPUTE,
    "Command": TimeType.COMPUTE,
    "Validator": TimeType.COMPUTE,
    "Service": TimeType.COMPUTE,
    "DomainService": TimeType.COMPUTE,
    "ApplicationService": TimeType.COMPUTE,
    "UseCase": TimeType.COMPUTE,
    "Specification": TimeType.COMPUTE,
    "Mapper": TimeType.COMPUTE,
    "Observer": TimeType.COMPUTE,
    "Test": TimeType.COMPUTE,
    "Utility": TimeType.COMPUTE,
    "Internal": TimeType.COMPUTE,
    
    # Local I/O operations
    "Repository": TimeType.IO_LOCAL,
    "DataAccess": TimeType.IO_LOCAL,
    "Logger": TimeType.IO_LOCAL,
    "Cache": TimeType.IO_LOCAL,
    
    # Network I/O operations
    "Gateway": TimeType.IO_NETWORK,
    "Adapter": TimeType.IO_NETWORK,
    "Client": TimeType.IO_NETWORK,
    "API": TimeType.IO_NETWORK,
}

# Pattern detection for overrides
IO_NETWORK_PATTERNS = [
    r"http", r"request", r"socket", r"api", r"client", 
    r"fetch", r"post", r"get_url", r"send", r"receive"
]
IO_LOCAL_PATTERNS = [
    r"file", r"open", r"read", r"write", r"path", 
    r"disk", r"cache", r"storage", r"save", r"load"
]
BLOCKING_PATTERNS = [
    r"sleep", r"wait", r"lock", r"acquire", r"join",
    r"semaphore", r"mutex", r"synchron"
]
DATABASE_PATTERNS = [
    r"database", r"sql", r"query", r"cursor", r"session",
    r"commit", r"rollback", r"transaction"
]

# Cost multipliers by time type
COST_MULTIPLIERS = {
    TimeType.INSTANT: 1,
    TimeType.COMPUTE: 1,    # Modified by complexity
    TimeType.IO_LOCAL: 50,
    TimeType.IO_NETWORK: 500,
    TimeType.BLOCKING: 100,
}


@dataclass
class PerformanceNode:
    """A node with performance characteristics"""
    id: str
    name: str
    role: str
    layer: str
    
    # Time characteristics
    time_type: TimeType = TimeType.COMPUTE
    lines_of_code: int = 1
    complexity: int = 1
    
    # Cost estimation
    base_cost: float = 1.0
    estimated_cost: float = 1.0
    
    # Hotspot metrics
    in_degree: int = 0
    hotspot_score: float = 0.0


@dataclass
class PerformanceProfile:
    """Complete performance profile of a codebase"""
    nodes: Dict[str, PerformanceNode]
    
    # Critical path
    critical_path: List[str]
    critical_path_cost: float
    
    # Hotspots (high traffic + high cost)
    hotspots: List[str]
    
    # Distributions
    time_by_layer: Dict[str, float]
    time_by_type: Dict[str, float]
    node_count_by_type: Dict[str, int]
    
    # Statistics
    total_estimated_cost: float
    average_node_cost: float
    
    def summary(self) -> dict:
        """Summarize performance profile"""
        return {
            "total_nodes": len(self.nodes),
            "total_estimated_cost": round(self.total_estimated_cost, 2),
            "average_node_cost": round(self.average_node_cost, 2),
            "critical_path_length": len(self.critical_path),
            "critical_path_cost": round(self.critical_path_cost, 2),
            "hotspot_count": len(self.hotspots),
            "time_by_type": {k: round(v, 1) for k, v in self.time_by_type.items()},
            "time_by_layer": {k: round(v, 1) for k, v in self.time_by_layer.items()},
            "node_count_by_type": self.node_count_by_type
        }


class PerformancePredictor:
    """Predicts performance characteristics of code"""
    
    def __init__(self):
        self.nodes: Dict[str, PerformanceNode] = {}
    
    def predict(self, analysis_nodes: list, exec_flow=None) -> PerformanceProfile:
        """
        Predict performance profile from analysis output.
        
        Args:
            analysis_nodes: Nodes from unified_analysis
            exec_flow: Optional ExecutionFlow for chain analysis
        """
        # Stage 1: Build performance nodes
        self._build_nodes(analysis_nodes, exec_flow)
        
        # Stage 2: Classify time types
        self._classify_time_types()
        
        # Stage 3: Estimate costs
        self._estimate_costs()
        
        # Stage 4: Calculate hotspot scores
        self._calculate_hotspots()
        
        # Stage 5: Find critical path
        critical_path, critical_cost = self._find_critical_path(exec_flow)
        
        # Stage 6: Calculate distributions
        time_by_layer, time_by_type, count_by_type = self._calculate_distributions()
        
        # Calculate totals
        total_cost = sum(n.estimated_cost for n in self.nodes.values())
        avg_cost = total_cost / len(self.nodes) if self.nodes else 0
        
        # Get top hotspots
        hotspots = sorted(
            self.nodes.keys(),
            key=lambda k: self.nodes[k].hotspot_score,
            reverse=True
        )[:10]
        
        return PerformanceProfile(
            nodes=self.nodes,
            critical_path=critical_path,
            critical_path_cost=critical_cost,
            hotspots=hotspots,
            time_by_layer=time_by_layer,
            time_by_type=time_by_type,
            node_count_by_type=count_by_type,
            total_estimated_cost=total_cost,
            average_node_cost=avg_cost
        )
    
    def _build_nodes(self, analysis_nodes: list, exec_flow=None):
        """Build PerformanceNodes from analysis output"""
        exec_nodes = exec_flow.nodes if exec_flow else {}
        
        for i, node in enumerate(analysis_nodes):
            # Handle both dict and object
            if hasattr(node, 'name'):
                node_id = node.id if node.id else node.name
                name = node.name
                role = getattr(node, 'role', 'Unknown')
                loc = getattr(node, 'lines_of_code', 1) or 1
                complexity = getattr(node, 'complexity', 1) or 1
            else:
                node_id = node.get('id') or node.get('name') or f"node_{i}"
                name = node.get('name', '')
                role = node.get('role', 'Unknown')
                loc = node.get('lines_of_code', 1) or 1
                complexity = node.get('complexity', 1) or 1
            
            # Get layer and in_degree from exec_flow if available
            layer = "unknown"
            in_degree = 0
            if node_id in exec_nodes:
                en = exec_nodes[node_id]
                layer = en.layer
                in_degree = en.in_degree
            
            self.nodes[node_id] = PerformanceNode(
                id=node_id,
                name=name,
                role=role,
                layer=layer,
                lines_of_code=loc,
                complexity=complexity,
                in_degree=in_degree
            )
    
    def _classify_time_types(self):
        """Classify time type for each node"""
        for node in self.nodes.values():
            # First try role-based classification
            if node.role in ROLE_TO_TIME_TYPE:
                node.time_type = ROLE_TO_TIME_TYPE[node.role]
            else:
                node.time_type = TimeType.COMPUTE  # Default
            
            # Override based on name patterns
            name_lower = node.name.lower()
            
            # Check for network I/O patterns
            for pattern in IO_NETWORK_PATTERNS:
                if re.search(pattern, name_lower):
                    node.time_type = TimeType.IO_NETWORK
                    break
            
            # Check for database patterns (network I/O)
            for pattern in DATABASE_PATTERNS:
                if re.search(pattern, name_lower):
                    node.time_type = TimeType.IO_NETWORK
                    break
            
            # Check for local I/O patterns
            for pattern in IO_LOCAL_PATTERNS:
                if re.search(pattern, name_lower):
                    if node.time_type != TimeType.IO_NETWORK:  # Don't override network
                        node.time_type = TimeType.IO_LOCAL
                    break
            
            # Check for blocking patterns
            for pattern in BLOCKING_PATTERNS:
                if re.search(pattern, name_lower):
                    node.time_type = TimeType.BLOCKING
                    break
    
    def _estimate_costs(self):
        """Estimate cost for each node"""
        for node in self.nodes.values():
            base_cost = node.lines_of_code
            multiplier = COST_MULTIPLIERS[node.time_type]
            
            # For compute nodes, factor in complexity
            if node.time_type == TimeType.COMPUTE:
                multiplier = max(1, node.complexity)
            
            node.base_cost = base_cost
            node.estimated_cost = base_cost * multiplier
    
    def _calculate_hotspots(self):
        """Calculate hotspot score for each node"""
        for node in self.nodes.values():
            # Hotspot = high traffic × high cost
            node.hotspot_score = node.in_degree * node.estimated_cost
    
    def _find_critical_path(self, exec_flow) -> Tuple[List[str], float]:
        """Find the critical path (longest by cost)"""
        if not exec_flow or not exec_flow.chains:
            return [], 0.0
        
        best_path = []
        best_cost = 0.0
        
        for chain in exec_flow.chains:
            chain_cost = sum(
                self.nodes[nid].estimated_cost 
                for nid in chain.path 
                if nid in self.nodes
            )
            if chain_cost > best_cost:
                best_cost = chain_cost
                best_path = chain.path
        
        return best_path, best_cost
    
    def _calculate_distributions(self) -> Tuple[Dict, Dict, Dict]:
        """Calculate time distribution by layer and type"""
        time_by_layer = defaultdict(float)
        time_by_type = defaultdict(float)
        count_by_type = defaultdict(int)
        
        for node in self.nodes.values():
            time_by_layer[node.layer] += node.estimated_cost
            time_by_type[node.time_type.value] += node.estimated_cost
            count_by_type[node.time_type.value] += 1
        
        return dict(time_by_layer), dict(time_by_type), dict(count_by_type)


def predict_performance(nodes: list, exec_flow=None) -> PerformanceProfile:
    """
    Convenience function to predict performance.
    
    Usage:
        from performance_predictor import predict_performance
        
        result = analyze(path)
        flow = detect_execution_flow(result.nodes, result.edges)
        perf = predict_performance(result.nodes, flow)
        print(perf.summary())
    """
    predictor = PerformancePredictor()
    return predictor.predict(nodes, exec_flow)


if __name__ == "__main__":
    import json
    
    # Demo with simple test data
    test_nodes = [
        {"id": "main", "name": "main", "role": "Controller", "lines_of_code": 10},
        {"id": "process", "name": "process_data", "role": "Service", "lines_of_code": 50, "complexity": 5},
        {"id": "save", "name": "save_to_db", "role": "Repository", "lines_of_code": 20},
        {"id": "api", "name": "fetch_api", "role": "Gateway", "lines_of_code": 15},
    ]
    
    perf = predict_performance(test_nodes)
    
    print("Performance Profile Summary:")
    print(json.dumps(perf.summary(), indent=2))
    
    print("\nNode costs:")
    for nid, node in perf.nodes.items():
        print(f"  {node.name}: {node.time_type.value} → cost={node.estimated_cost}")
