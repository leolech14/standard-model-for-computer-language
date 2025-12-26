#!/usr/bin/env python3
"""
🔗 Graph-Based Type Inference Engine

Deterministically infer node types from their graph connections.
"Purpose emerges from structure" - if we know WHO calls/uses a node,
we can infer WHAT that node is.

Rules:
- Node called by Test → likely a Subject (thing being tested)
- Node that calls Repository → likely a Service
- Node called by Controller → likely a Service or UseCase
- Node that imports only stdlib → likely Utility
- Node with many callers → likely a shared Service/Utility
- Node with high in-degree from domain → likely Core Entity
"""

from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class InferenceRule:
    """A rule for inferring type from graph context."""
    name: str
    inferred_type: str
    confidence: float
    
    # Conditions
    caller_types: Set[str] = None      # Types of nodes that call this
    callee_types: Set[str] = None      # Types of nodes this calls
    min_in_degree: int = 0
    max_in_degree: int = float('inf')
    min_out_degree: int = 0
    max_out_degree: int = float('inf')
    
    def __post_init__(self):
        self.caller_types = self.caller_types or set()
        self.callee_types = self.callee_types or set()


# ===== INFERENCE RULES =====
# These are deterministic logic rules based on graph structure

INFERENCE_RULES = [
    # If only Tests call you → you're the Subject Under Test
    InferenceRule(
        name="called_only_by_tests",
        inferred_type="SubjectUnderTest",
        confidence=85.0,
        caller_types={"Test"},
    ),
    
    # If you call Repository/RepositoryImpl → you're a Service
    InferenceRule(
        name="calls_repository",
        inferred_type="Service",
        confidence=90.0,
        callee_types={"Repository", "RepositoryImpl"},
    ),
    
    # If you call external Client/Gateway → you're an Integration Service
    InferenceRule(
        name="calls_external",
        inferred_type="IntegrationService",
        confidence=85.0,
        callee_types={"Client", "Gateway", "Adapter"},
    ),
    
    # If Controller calls you → you're a UseCase or Service
    InferenceRule(
        name="called_by_controller",
        inferred_type="UseCase",
        confidence=80.0,
        caller_types={"Controller"},
    ),
    
    # If Service calls you and you don't call anything → you're a Query
    InferenceRule(
        name="leaf_called_by_service",
        inferred_type="Query",
        confidence=75.0,
        caller_types={"Service", "DomainService", "ApplicationService"},
        max_out_degree=0,
    ),
    
    # If you have many callers (high in-degree) → you're a shared Utility
    InferenceRule(
        name="high_in_degree_utility",
        inferred_type="Utility",
        confidence=70.0,
        min_in_degree=10,
    ),
    
    # If you call Factory → you're likely a Service doing object creation
    InferenceRule(
        name="calls_factory",
        inferred_type="Service",
        confidence=75.0,
        callee_types={"Factory", "Builder"},
    ),
    
    # If you call Validator/Specification → you're doing validation logic
    InferenceRule(
        name="calls_validator",
        inferred_type="Service",
        confidence=75.0,
        callee_types={"Validator", "Specification"},
    ),
    
    # If EventHandler calls you → you're likely handling an event response
    InferenceRule(
        name="called_by_event_handler",
        inferred_type="EventProcessor",
        confidence=75.0,
        caller_types={"EventHandler", "Observer"},
    ),
    
    # If you call only Mappers → you're likely a data transformer
    InferenceRule(
        name="calls_mappers",
        inferred_type="Mapper",
        confidence=70.0,
        callee_types={"Mapper", "Converter"},
    ),
]


# ===== STRUCTURAL INFERENCE RULES =====
# These rules work based on node properties WITHOUT needing known neighbors

def infer_from_structure(node: Dict) -> Tuple[str, float, str]:
    """
    Infer type from node's own structural properties.
    Works even when no neighbors have known types.
    Returns (type, confidence, rule_name) or None.
    """
    name = node.get('name', '').split('.')[-1].lower()
    return_type = node.get('return_type', '').lower()
    params = node.get('params', [])
    docstring = node.get('docstring', '').lower()
    kind = node.get('kind', node.get('symbol_kind', ''))
    decorators = node.get('decorators', [])
    base_classes = node.get('base_classes', [])
    
    # Skip if already high confidence
    current_conf = node.get('role_confidence', 0)
    if current_conf >= 85:
        return None
    
    # -------------------------------------------------------------------------
    # STRUCTURAL RULE 1: Return type indicates Factory/Builder
    # -------------------------------------------------------------------------
    if return_type:
        # Returns a new object instance → Factory
        if any(x in return_type for x in ['new', 'create', 'make', 'build']):
            return ('Factory', 82.0, 'return_type_factory')
        # Returns a bool → likely Specification/Validator
        if return_type in ('bool', 'boolean'):
            return ('Specification', 78.0, 'return_type_bool')
        # Returns an error → Exception-related
        if 'error' in return_type or 'err' in return_type:
            return ('Exception', 78.0, 'return_type_error')
    
    # -------------------------------------------------------------------------
    # STRUCTURAL RULE 2: Parameter patterns
    # -------------------------------------------------------------------------
    if params:
        param_names = [p.get('name', '').lower() for p in params]
        param_types = [p.get('type', '').lower() for p in params]
        
        # Takes context as first param → often a Command/Query handler
        if param_names and param_names[0] in ('ctx', 'context', 'c'):
            return ('Command', 75.0, 'context_first_param')
        
        # Takes request/response → Controller/Handler
        if any(p in param_names for p in ['request', 'req', 'response', 'resp', 'w', 'r']):
            return ('Controller', 78.0, 'http_params')
        
        # Takes reader/writer → IO utility
        if any('reader' in p or 'writer' in p for p in param_types):
            return ('Utility', 75.0, 'io_params')
    
    # -------------------------------------------------------------------------
    # STRUCTURAL RULE 3: Docstring patterns
    # -------------------------------------------------------------------------
    if docstring:
        if any(x in docstring for x in ['test', 'verify', 'assert']):
            return ('Test', 82.0, 'docstring_test')
        if any(x in docstring for x in ['create', 'build', 'construct', 'generate']):
            return ('Factory', 78.0, 'docstring_factory')
        if any(x in docstring for x in ['validate', 'check', 'ensure']):
            return ('Validator', 78.0, 'docstring_validator')
        if any(x in docstring for x in ['parse', 'decode', 'unmarshal']):
            return ('Query', 78.0, 'docstring_parser')
        if any(x in docstring for x in ['write', 'save', 'store', 'persist']):
            return ('Command', 78.0, 'docstring_persist')
    
    # -------------------------------------------------------------------------
    # STRUCTURAL RULE 4: High complexity → likely Service
    # -------------------------------------------------------------------------
    complexity = node.get('complexity', 0)
    if complexity > 20:
        return ('Service', 72.0, 'high_complexity')
    
    # -------------------------------------------------------------------------
    # STRUCTURAL RULE 5: Zero out-degree leaf → likely DTO/ValueObject
    # -------------------------------------------------------------------------
    if kind == 'class' and node.get('out_degree', 0) == 0:
        return ('DTO', 72.0, 'leaf_class')
    
    return None


class GraphTypeInference:
    """
    Infer unknown node types from graph structure.
    Deterministic, no LLM required.
    """
    
    def __init__(self):
        self.rules = INFERENCE_RULES
        self.inference_log: List[Dict] = []
    
    def build_graph_index(self, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """Build index structures for efficient graph traversal."""
        
        # Node lookup by ID
        node_by_id = {n.get('id', n.get('name', '')): n for n in nodes}
        
        # Caller/callee relationships
        callers = defaultdict(set)  # node_id -> set of caller node_ids
        callees = defaultdict(set)  # node_id -> set of callee node_ids
        
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            edge_type = edge.get('edge_type', '')
            
            if edge_type in ('calls', 'uses', 'imports'):
                callees[source].add(target)
                callers[target].add(source)
        
        # In/out degree
        in_degree = {n_id: len(callers[n_id]) for n_id in node_by_id}
        out_degree = {n_id: len(callees[n_id]) for n_id in node_by_id}
        
        return {
            'node_by_id': node_by_id,
            'callers': dict(callers),
            'callees': dict(callees),
            'in_degree': in_degree,
            'out_degree': out_degree,
        }
    
    def get_neighbor_types(self, node_id: str, neighbors: Set[str], 
                           node_by_id: Dict) -> Set[str]:
        """Get the types/roles of neighboring nodes."""
        types = set()
        for neighbor_id in neighbors:
            neighbor = node_by_id.get(neighbor_id)
            if neighbor:
                role = neighbor.get('role', neighbor.get('type', 'Unknown'))
                if role and role != 'Unknown':
                    types.add(role)
        return types
    
    def infer_type(self, node: Dict, graph_index: Dict) -> Tuple[str, float, str]:
        """
        Infer type for a single node based on graph context.
        Returns (inferred_type, confidence, rule_name).
        """
        node_id = node.get('id', node.get('name', ''))
        
        # Get graph context
        callers = graph_index['callers'].get(node_id, set())
        callees = graph_index['callees'].get(node_id, set())
        in_deg = graph_index['in_degree'].get(node_id, 0)
        out_deg = graph_index['out_degree'].get(node_id, 0)
        
        caller_types = self.get_neighbor_types(
            node_id, callers, graph_index['node_by_id'])
        callee_types = self.get_neighbor_types(
            node_id, callees, graph_index['node_by_id'])
        
        # Try each rule
        best_match = None
        best_confidence = 0.0
        
        for rule in self.rules:
            matches = True
            
            # Check caller type conditions
            if rule.caller_types:
                if not caller_types.intersection(rule.caller_types):
                    matches = False
            
            # Check callee type conditions
            if rule.callee_types:
                if not callee_types.intersection(rule.callee_types):
                    matches = False
            
            # Check degree conditions
            if in_deg < rule.min_in_degree or in_deg > rule.max_in_degree:
                matches = False
            if out_deg < rule.min_out_degree or out_deg > rule.max_out_degree:
                matches = False
            
            if matches and rule.confidence > best_confidence:
                best_match = rule
                best_confidence = rule.confidence
        
        if best_match:
            return (best_match.inferred_type, best_match.confidence, best_match.name)
        
        return ('Unknown', 0.0, 'no_rule_matched')
    
    def infer_all(self, nodes: List[Dict], edges: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Infer types for all unknown nodes.
        Returns updated nodes and inference report.
        """
        # Build graph index
        graph_index = self.build_graph_index(nodes, edges)
        
        inferred_count = 0
        inference_details = []
        
        for node in nodes:
            current_role = node.get('role', node.get('type', 'Unknown'))
            
            # Only infer for unknown nodes
            if current_role == 'Unknown':
                inferred_type, confidence, rule = self.infer_type(node, graph_index)
                
                if inferred_type != 'Unknown':
                    node['role'] = inferred_type
                    node['type'] = inferred_type
                    node['role_confidence'] = confidence
                    node['discovery_method'] = f'graph_inference:{rule}'
                    inferred_count += 1
                    
                    inference_details.append({
                        'node': node.get('name', ''),
                        'inferred': inferred_type,
                        'confidence': confidence,
                        'rule': rule,
                    })
        
        report = {
            'total_inferred': inferred_count,
            'rules_applied': len(set(d['rule'] for d in inference_details)),
            'details': inference_details[:20],  # Top 20 examples
        }
        
        return nodes, report


def apply_graph_inference(nodes: List[Dict], edges: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Apply graph-based type inference to reduce unknowns.
    Includes parent-role inheritance for nested functions.
    Deterministic - no LLM required.
    """
    engine = GraphTypeInference()
    nodes, report = engine.infer_all(nodes, edges)
    
    # =========================================================================
    # STRUCTURAL INFERENCE - runs on ALL nodes, can boost low-confidence
    # =========================================================================
    structural_boosted = 0
    for node in nodes:
        result = infer_from_structure(node)
        if result:
            inferred_type, confidence, rule = result
            current_conf = node.get('role_confidence', 0)
            
            # Apply if: Unknown role OR structural confidence is higher
            if node.get('role') == 'Unknown' or confidence > current_conf:
                node['role'] = inferred_type
                node['type'] = inferred_type
                node['role_confidence'] = confidence
                node['discovery_method'] = f'structural:{rule}'
                structural_boosted += 1
    
    report['structural_boosted'] = structural_boosted
    report['total_inferred'] = report.get('total_inferred', 0) + structural_boosted
    
    # =========================================================================
    # PARENT-ROLE INHERITANCE
    # Nested functions (like test_options_work.index) inherit parent's role
    # =========================================================================
    parent_inherited = 0
    node_by_name = {n.get('name', ''): n for n in nodes}
    
    for node in nodes:
        if node.get('role') == 'Unknown' or node.get('type') == 'Unknown':
            name = node.get('name', '')
            parent_name = node.get('parent', '')
            
            # If no explicit parent, try to extract from dotted name
            if not parent_name and '.' in name:
                parent_name = name.rsplit('.', 1)[0]
            
            if parent_name:
                parent = node_by_name.get(parent_name)
                if parent:
                    parent_role = parent.get('role', parent.get('type', 'Unknown'))
                    if parent_role and parent_role != 'Unknown':
                        node['role'] = parent_role
                        node['type'] = parent_role
                        node['role_confidence'] = parent.get('role_confidence', 70.0) * 0.9  # Slightly lower confidence
                        node['discovery_method'] = f'parent_inheritance:{parent_name}'
                        parent_inherited += 1
    
    report['parent_inherited'] = parent_inherited
    report['total_inferred'] = report.get('total_inferred', 0) + parent_inherited
    
    return nodes, report


if __name__ == '__main__':
    # Test with sample data
    test_nodes = [
        {'id': 'A', 'name': 'UserService', 'role': 'Unknown'},
        {'id': 'B', 'name': 'UserRepository', 'role': 'Repository'},
        {'id': 'C', 'name': 'test_user', 'role': 'Test'},
        {'id': 'D', 'name': 'helper_func', 'role': 'Unknown'},
    ]
    
    test_edges = [
        {'source': 'A', 'target': 'B', 'edge_type': 'calls'},
        {'source': 'C', 'target': 'D', 'edge_type': 'calls'},
    ]
    
    nodes, report = apply_graph_inference(test_nodes, test_edges)
    
    print("=== GRAPH INFERENCE TEST ===")
    for node in nodes:
        print(f"{node['name']}: {node['role']} (method: {node.get('discovery_method', 'original')})")
    
    print(f"\nInferred: {report['total_inferred']}")
    print(f"Rules applied: {report['rules_applied']}")
