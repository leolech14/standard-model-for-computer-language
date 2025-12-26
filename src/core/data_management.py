"""
data_management.py

The Unified Data Layer for the Collider system.
Provides a single source of truth for Codebase State, enforcing schema integrity
and enabling cross-layer data enrichment.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path

from unified_analysis import UnifiedNode, UnifiedEdge, UnifiedAnalysisOutput

class CodebaseState:
    """
    Singleton-like container for the entire state of a codebase analysis.
    
    Acts as the central bus for all 'Islands of Analysis' (Purpose, Flow, Perf, etc.)
    to write their results back into a shared, validated graph.
    """
    
    def __init__(self, target_path: str):
        self.target_path = target_path
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "target": target_path,
            "layers_activated": []
        }
        
        # Indices for fast lookup
        self._node_lookup: Dict[str, Dict[str, Any]] = {}

    def load_initial_graph(self, nodes: List[Any], edges: List[Any]):
        """
        Load the initial AST/Ref graph from Stage 1-2.
        Accepts dicts or objects (Dataclasses).
        """
        # clear existing
        self.nodes = {}
        self.edges = []
        
        # Ingest nodes
        for n in nodes:
            # Normalize to dict
            if hasattr(n, 'to_dict'):
                n_dict = n.to_dict()
            elif hasattr(n, '__dict__'):
                n_dict = vars(n)
            else:
                n_dict = dict(n)
                
            # Ensure ID
            nid = n_dict.get('id')
            if not nid:
                continue # Skip invalid nodes
                
            self.nodes[nid] = n_dict
            self._node_lookup[nid] = n_dict
            
        # Ingest edges
        for e in edges:
            if hasattr(e, 'to_dict'):
                e_dict = e.to_dict()
            elif hasattr(e, '__dict__'):
                e_dict = vars(e)
            else:
                e_dict = dict(e)
            
            self.edges.append(e_dict)
            
        print(f"  [State] Loaded {len(self.nodes)} nodes and {len(self.edges)} edges.")

    def enrich_node(self, node_id: str, layer_name: str, **attributes):
        """
        Enrich a specific node with semantic data from a layer.
        
        Args:
            node_id: The ID of the node to enrich.
            layer_name: The source of this data (e.g., "purpose", "flow").
            **attributes: Key-value pairs to merge into the node.
        """
        if node_id not in self.nodes:
            # We silently skip enrichment for non-existent nodes to avoid crashing 
            # on transient or virtual nodes created by some sub-systems
            return
            
        node = self.nodes[node_id]
        
        # Merge attributes
        for k, v in attributes.items():
            node[k] = v
            
        # Track layer activation
        if layer_name not in self.metadata["layers_activated"]:
            self.metadata["layers_activated"].append(layer_name)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(node_id)

    def validate(self) -> List[str]:
        """
        Check for referential integrity violations.
        Returns a list of error messages.
        """
        errors = []
        
        # 1. Edge integrity
        for i, edge in enumerate(self.edges):
            src = edge.get('source')
            tgt = edge.get('target')
            
            if src not in self.nodes:
                errors.append(f"Edge {i} source not found: {src}")
            if tgt not in self.nodes:
                errors.append(f"Edge {i} target not found: {tgt}")
                
        return errors

    def export(self) -> Dict[str, Any]:
        """
        Export the fully reconciled state as a unified dictionary
        ready for visualization or JSON dump.
        """
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "metadata": self.metadata
        }
