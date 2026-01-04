"""
Purpose Field Detector

Detects the hierarchical emergence of purpose in code:
- Level 1: Atomic Purpose (role of individual functions)
- Level 2: Composite Purpose (emergent from grouped components)
- Level 3: Layer Purpose (shared across architectural layer)
- Level 4: Purpose Field (gradient across entire codebase)
"""

from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from enum import Enum


class Layer(Enum):
    """Architectural layers (purpose zones)"""
    PRESENTATION = "presentation"    # User interface, display
    APPLICATION = "application"      # Use cases, orchestration
    DOMAIN = "domain"               # Business rules, entities
    INFRASTRUCTURE = "infrastructure"  # Technical details, persistence
    TESTING = "testing"             # Test code, fixtures, assertions
    UNKNOWN = "unknown"


@dataclass
class PurposeNode:
    """A node with its purpose at all levels"""
    id: str
    name: str
    kind: str  # function, class, module
    
    # Level 1: Atomic Purpose
    atomic_purpose: str = "Unknown"  # Role
    atomic_confidence: float = 0.0
    
    # Level 2: Composite Purpose (for classes/modules)
    composite_purpose: Optional[str] = None
    child_purposes: List[str] = field(default_factory=list)
    
    # Level 3: Layer
    layer: Layer = Layer.UNKNOWN
    
    # Parent/children for hierarchy
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)


@dataclass
class PurposeField:
    """The complete purpose field of a codebase"""
    nodes: Dict[str, PurposeNode]
    layer_purposes: Dict[Layer, str]
    purpose_flow: List[Tuple[str, str, str]]  # (from_id, to_id, purpose_transfer)
    violations: List[str]
    
    def summary(self) -> dict:
        """Summarize the purpose field"""
        layer_counts = Counter(n.layer for n in self.nodes.values())
        purpose_counts = Counter(n.atomic_purpose for n in self.nodes.values())
        
        return {
            "total_nodes": len(self.nodes),
            "layers": {l.value: c for l, c in layer_counts.items()},
            "purposes": dict(purpose_counts.most_common(10)),
            "violations": len(self.violations),
            "layer_purposes": {l.value: p for l, p in self.layer_purposes.items()}
        }


class PurposeFieldDetector:
    """Detects the Purpose Field of a codebase"""
    
    # Emergence rules: child purposes → composite purpose
    EMERGENCE_RULES = {
        # If all children are Queries → parent is Repository-like
        frozenset(["Query"]): "DataAccess",
        frozenset(["Query", "Command"]): "Repository",
        frozenset(["Query", "Command", "Factory"]): "Repository",
        
        # If children are mixed business logic → Service
        frozenset(["Command", "Query", "Validator"]): "Service",
        frozenset(["UseCase"]): "ApplicationService",
        
        # If all children are Tests → TestSuite
        frozenset(["Test"]): "TestSuite",
        frozenset(["Test", "Fixture"]): "TestSuite",
        
        # If all children are Mappers → Transformer
        frozenset(["Mapper"]): "Transformer",
        frozenset(["Mapper", "Factory"]): "Transformer",
        
        # Controller patterns
        frozenset(["Controller"]): "APILayer",
        frozenset(["Controller", "Validator"]): "APILayer",
    }
    
    # Layer detection based on purpose (role)
    # Covers all 27 roles from the Standard Model
    PURPOSE_TO_LAYER = {
        # PRESENTATION - User interface, display, I/O
        "Controller": Layer.PRESENTATION,
        "APILayer": Layer.PRESENTATION,
        "View": Layer.PRESENTATION,
        "CLI": Layer.PRESENTATION,
        
        # APPLICATION - Use cases, orchestration, coordination
        "ApplicationService": Layer.APPLICATION,
        "UseCase": Layer.APPLICATION,
        "Orchestrator": Layer.APPLICATION,
        "Command": Layer.APPLICATION,  # Commands are application-level actions
        "Query": Layer.APPLICATION,    # Queries are application-level requests
        "EventHandler": Layer.APPLICATION,
        
        # DOMAIN - Business rules, entities, logic
        "Service": Layer.DOMAIN,
        "DomainService": Layer.DOMAIN,
        "Entity": Layer.DOMAIN,
        "ValueObject": Layer.DOMAIN,
        "Policy": Layer.DOMAIN,
        "Specification": Layer.DOMAIN,
        "DTO": Layer.DOMAIN,           # Data transfer objects carry domain data
        "Validator": Layer.DOMAIN,     # Validation is business logic
        "Factory": Layer.DOMAIN,       # Object creation follows domain rules
        "Observer": Layer.DOMAIN,      # Event observation is domain behavior
        "Mapper": Layer.DOMAIN,        # Mapping follows domain transformations
        
        # INFRASTRUCTURE - Technical concerns, persistence, external systems
        "Repository": Layer.INFRASTRUCTURE,
        "DataAccess": Layer.INFRASTRUCTURE,
        "Gateway": Layer.INFRASTRUCTURE,
        "Adapter": Layer.INFRASTRUCTURE,
        "Configuration": Layer.INFRASTRUCTURE,
        "Utility": Layer.INFRASTRUCTURE,   # Utilities are technical helpers
        "Internal": Layer.INFRASTRUCTURE,  # Internal implementation details
        "Exception": Layer.INFRASTRUCTURE, # Exception handling is infrastructure
        "Lifecycle": Layer.INFRASTRUCTURE, # Lifecycle management is technical
        
        # TESTING - Test code layer
        "Test": Layer.TESTING,
        "Fixture": Layer.TESTING,
    }
    
    # Layer purpose descriptions
    LAYER_PURPOSES = {
        Layer.PRESENTATION: "Display data and handle user interaction",
        Layer.APPLICATION: "Orchestrate use cases and coordinate domain",
        Layer.DOMAIN: "Express and enforce business rules",
        Layer.INFRASTRUCTURE: "Handle technical concerns and external systems",
        Layer.TESTING: "Verify behavior and validate expectations",
        Layer.UNKNOWN: "Purpose not yet determined"
    }
    
    def __init__(self):
        self.nodes: Dict[str, PurposeNode] = {}
    
    def detect_field(self, analysis_nodes: list, edges: list = None) -> PurposeField:
        """
        Detect the complete Purpose Field from analysis output.
        
        Args:
            analysis_nodes: List of nodes from unified_analysis
            edges: List of edges (optional, for flow analysis)
        
        Returns:
            PurposeField with all levels computed
        """
        edges = edges or []
        
        # Stage 1: Create PurposeNodes with atomic purpose (from roles)
        self._create_nodes(analysis_nodes)
        
        # Stage 2: Build hierarchy (parent-child relationships)
        self._build_hierarchy(analysis_nodes)
        
        # Stage 3: Compute composite purpose (emergence)
        self._compute_composite_purposes()
        
        # Stage 4: Assign layers
        self._assign_layers()
        
        # Stage 5: Detect purpose flow and violations
        purpose_flow, violations = self._analyze_flow(edges)
        
        return PurposeField(
            nodes=self.nodes,
            layer_purposes=self.LAYER_PURPOSES,
            purpose_flow=purpose_flow,
            violations=violations
        )
    
    def _create_nodes(self, analysis_nodes: list):
        """Create PurposeNodes from analysis output"""
        for i, node in enumerate(analysis_nodes):
            # Handle both dict and object
            if hasattr(node, 'id'):
                node_id = node.id
                name = node.name
                kind = node.kind
                role = node.role
                conf = node.role_confidence
            else:
                node_id = node.get('id', '')
                name = node.get('name', 'unknown')
                kind = node.get('kind', 'function')
                role = node.get('role', 'Unknown')
                conf = node.get('role_confidence', 0.0)
            
            # Use name as ID if ID is empty (common issue)
            if not node_id:
                node_id = name or f"node_{i}"
            
            self.nodes[node_id] = PurposeNode(
                id=node_id,
                name=name,
                kind=kind,
                atomic_purpose=role,
                atomic_confidence=conf
            )
    
    def _build_hierarchy(self, analysis_nodes: list):
        """Build parent-child relationships"""
        # Infer hierarchy from names (Class.method pattern)
        for node_id, node in self.nodes.items():
            if '.' in node.name:
                parent_name = node.name.rsplit('.', 1)[0]
                # Find parent
                for pid, pnode in self.nodes.items():
                    if pnode.name == parent_name:
                        node.parent_id = pid
                        pnode.children_ids.append(node_id)
                        break
    
    def _compute_composite_purposes(self):
        """Compute emergent composite purpose for parent nodes"""
        # Process nodes with children
        for node_id, node in self.nodes.items():
            if node.children_ids:
                # Gather child purposes
                child_purposes = []
                for child_id in node.children_ids:
                    if child_id in self.nodes:
                        child_purposes.append(self.nodes[child_id].atomic_purpose)
                
                node.child_purposes = child_purposes
                
                # Apply emergence rules
                purpose_set = frozenset(set(child_purposes))
                
                if purpose_set in self.EMERGENCE_RULES:
                    node.composite_purpose = self.EMERGENCE_RULES[purpose_set]
                else:
                    # Default: use most common child purpose
                    if child_purposes:
                        most_common = Counter(child_purposes).most_common(1)[0][0]
                        node.composite_purpose = f"{most_common}Container"
    
    def _assign_layers(self):
        """Assign architectural layers based on purpose"""
        for node in self.nodes.values():
            # Use composite purpose if available, else atomic
            purpose = node.composite_purpose or node.atomic_purpose
            
            if purpose in self.PURPOSE_TO_LAYER:
                node.layer = self.PURPOSE_TO_LAYER[purpose]
            else:
                # Try to infer from name patterns
                name_lower = node.name.lower()
                if any(p in name_lower for p in ['controller', 'view', 'route', 'endpoint']):
                    node.layer = Layer.PRESENTATION
                elif any(p in name_lower for p in ['service', 'usecase', 'handler']):
                    node.layer = Layer.APPLICATION
                elif any(p in name_lower for p in ['entity', 'model', 'domain', 'policy']):
                    node.layer = Layer.DOMAIN
                elif any(p in name_lower for p in ['repository', 'gateway', 'adapter', 'config']):
                    node.layer = Layer.INFRASTRUCTURE
    
    def _analyze_flow(self, edges: list) -> Tuple[List, List]:
        """Analyze purpose flow and detect violations"""
        purpose_flow = []
        violations = []
        
        # Layer order (lower index = higher layer)
        layer_order = {
            Layer.PRESENTATION: 0,
            Layer.APPLICATION: 1,
            Layer.DOMAIN: 2,
            Layer.INFRASTRUCTURE: 3,
            Layer.UNKNOWN: 99
        }
        
        for edge in edges:
            # Handle both dict and tuple
            if isinstance(edge, dict):
                source = edge.get('source', edge.get('from', ''))
                target = edge.get('target', edge.get('to', ''))
            elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
                source, target = edge[0], edge[1]
            else:
                continue
            
            source_node = self.nodes.get(source)
            target_node = self.nodes.get(target)
            
            if source_node and target_node:
                source_layer = source_node.layer
                target_layer = target_node.layer
                
                # Record flow
                purpose_flow.append((
                    source,
                    target,
                    f"{source_layer.value} → {target_layer.value}"
                ))
                
                # Detect violations: lower layer calling higher layer
                if layer_order.get(target_layer, 99) < layer_order.get(source_layer, 0):
                    violations.append(
                        f"Purpose flow violation: {source_node.name} ({source_layer.value}) "
                        f"calls {target_node.name} ({target_layer.value})"
                    )
        
        return purpose_flow, violations


def detect_purpose_field(nodes: list, edges: list = None) -> PurposeField:
    """
    Convenience function to detect purpose field.
    
    Usage:
        from purpose_field import detect_purpose_field
        
        result = analyze(path)
        field = detect_purpose_field(result.nodes, result.edges)
        print(field.summary())
    """
    detector = PurposeFieldDetector()
    return detector.detect_field(nodes, edges)


if __name__ == "__main__":
    # Demo with simple test data
    test_nodes = [
        {"id": "1", "name": "UserRepository", "kind": "class", "role": "Repository"},
        {"id": "2", "name": "UserRepository.get", "kind": "method", "role": "Query"},
        {"id": "3", "name": "UserRepository.save", "kind": "method", "role": "Command"},
        {"id": "4", "name": "UserService", "kind": "class", "role": "Service"},
        {"id": "5", "name": "UserService.create_user", "kind": "method", "role": "Command"},
        {"id": "6", "name": "UserController", "kind": "class", "role": "Controller"},
    ]
    
    test_edges = [
        ("6", "4"),  # Controller → Service (OK)
        ("4", "1"),  # Service → Repository (OK)
        ("1", "6"),  # Repository → Controller (VIOLATION!)
    ]
    
    field = detect_purpose_field(test_nodes, test_edges)
    
    print("Purpose Field Summary:")
    print(json.dumps(field.summary(), indent=2))
    
    if field.violations:
        print("\nViolations detected:")
        for v in field.violations:
            print(f"  ⚠ {v}")
