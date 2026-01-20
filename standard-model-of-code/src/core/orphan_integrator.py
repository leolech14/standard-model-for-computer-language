#!/usr/bin/env python3
"""
ORPHAN INTEGRATOR
=================

Self-healing module that analyzes orphan code and suggests integration points.
Detects code that was written but never wired into the main pipeline.

This module:
1. Analyzes each orphan's purpose (from name, signature, docstring)
2. Finds potential callers in the codebase that could use this orphan
3. Generates integration code snippets

Usage:
    from orphan_integrator import OrphanIntegrator
    
    integrator = OrphanIntegrator()
    analysis = integrator.analyze_orphans(nodes, edges, orphan_ids)
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path


@dataclass
class OrphanAnalysis:
    """Analysis result for a single orphan node."""
    node_id: str
    name: str
    file_path: str
    signature: str
    docstring: str
    purpose: str  # inferred from name/docstring
    category: str  # 'utility', 'detector', 'analyzer', 'config', 'entry_point'
    suggested_callers: List[str] = field(default_factory=list)
    integration_code: Optional[str] = None
    confidence: float = 0.0


class OrphanIntegrator:
    """
    Analyzes orphan code and suggests where it should be integrated.
    
    The integrator uses heuristics based on:
    - Naming conventions (e.g., 'shortest_path' → graph utility)
    - File location (e.g., same module = likely caller)
    - Signature compatibility (e.g., accepts 'nodes' → called by node processors)
    """
    
    # Domain keywords that suggest purpose
    PURPOSE_PATTERNS = {
        'utility': [
            r'util', r'helper', r'common', r'shared', r'_.*',  # leading underscore = private util
        ],
        'detector': [
            r'detect', r'find', r'discover', r'scan', r'check', r'validate',
        ],
        'analyzer': [
            r'analyz', r'extract', r'parse', r'process', r'compute', r'calculate',
        ],
        'generator': [
            r'generat', r'create', r'build', r'construct', r'emit',
        ],
        'config': [
            r'config', r'settings', r'options', r'params',
        ],
        'entry_point': [
            r'main', r'run', r'execute', r'start', r'cli', r'command',
        ],
    }
    
    # Known caller mappings (domain → likely callers)
    CALLER_MAPPINGS = {
        'graph': ['graph_analyzer.py', 'execution_flow.py', 'full_analysis.py'],
        'path': ['graph_analyzer.py', 'execution_flow.py'],
        'detector': ['insights_engine.py', 'full_analysis.py', 'unified_analysis.py'],
        'atom': ['atom_classifier.py', 'atom_extractor.py', 'unified_analysis.py'],
        'edge': ['edge_extractor.py', 'full_analysis.py'],
        'purpose': ['purpose_field.py', 'full_analysis.py'],
        'type': ['graph_type_inference.py', 'heuristic_classifier.py'],
        'stats': ['stats_generator.py', 'full_analysis.py'],
        'flow': ['execution_flow.py', 'full_analysis.py'],
        'output': ['output_generator.py', 'full_analysis.py'],
        'viz': ['visualize_graph_webgl.py', 'output_generator.py'],
    }
    
    def __init__(self):
        self.purpose_regexes = {
            cat: [re.compile(p, re.IGNORECASE) for p in patterns]
            for cat, patterns in self.PURPOSE_PATTERNS.items()
        }
    
    def analyze_orphans(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        orphan_ids: List[str]
    ) -> List[OrphanAnalysis]:
        """
        Analyze each orphan and suggest where it should be integrated.
        
        Args:
            nodes: All nodes in the graph
            edges: All edges in the graph
            orphan_ids: IDs of nodes with no incoming edges
            
        Returns:
            List of OrphanAnalysis with suggestions
        """
        # Build lookup structures
        node_by_id = {n.get('id', ''): n for n in nodes}
        orphan_set = set(orphan_ids)
        non_orphan_nodes = [n for n in nodes if n.get('id', '') not in orphan_set]
        
        results = []
        
        for orphan_id in orphan_ids:
            node = node_by_id.get(orphan_id)
            if not node:
                continue
            
            analysis = self._analyze_single_orphan(node, non_orphan_nodes, edges)
            if analysis:
                results.append(analysis)
        
        # Sort by confidence (highest first)
        results.sort(key=lambda a: a.confidence, reverse=True)
        
        return results
    
    def _analyze_single_orphan(
        self,
        node: Dict,
        non_orphan_nodes: List[Dict],
        edges: List[Dict]
    ) -> Optional[OrphanAnalysis]:
        """Analyze a single orphan node."""
        node_id = node.get('id', '')
        name = node.get('name', '')
        file_path = node.get('file_path', '') or node.get('file', '')
        signature = node.get('signature', '') or f"{name}()"
        docstring = node.get('docstring', '') or ''
        body = node.get('body_source', '') or ''
        
        # Skip module-level file nodes (these are expected orphans)
        if name.endswith('__file__') or node.get('kind') == 'module':
            return None
        
        # Infer purpose
        purpose, category = self._infer_purpose(name, docstring, body)
        
        # Find potential callers
        suggested_callers, confidence = self._find_callers(
            node, non_orphan_nodes, category
        )
        
        # Generate integration code
        integration_code = None
        if suggested_callers:
            integration_code = self._generate_integration(node, suggested_callers[0])
        
        return OrphanAnalysis(
            node_id=node_id,
            name=name,
            file_path=file_path,
            signature=signature,
            docstring=docstring[:200] if docstring else '',
            purpose=purpose,
            category=category,
            suggested_callers=suggested_callers[:3],  # Top 3
            integration_code=integration_code,
            confidence=confidence,
        )
    
    def _infer_purpose(self, name: str, docstring: str, body: str) -> Tuple[str, str]:
        """Infer the purpose and category of an orphan from its metadata."""
        combined = f"{name} {docstring} {body[:500]}".lower()
        
        # Check against purpose patterns
        for category, regexes in self.purpose_regexes.items():
            for regex in regexes:
                if regex.search(combined):
                    purpose = f"{category.title()} function"
                    return purpose, category
        
        # Fallback: infer from name only
        name_lower = name.lower()
        
        if 'get' in name_lower or 'fetch' in name_lower:
            return "Data accessor", "utility"
        if 'is_' in name_lower or 'has_' in name_lower:
            return "Predicate/checker", "utility"
        if 'to_' in name_lower or 'as_' in name_lower:
            return "Converter/transformer", "utility"
        
        return "Unknown purpose", "unknown"
    
    def _find_callers(
        self,
        orphan: Dict,
        candidates: List[Dict],
        category: str
    ) -> Tuple[List[str], float]:
        """Find potential callers for this orphan."""
        orphan_name = orphan.get('name', '').lower()
        orphan_file = Path(orphan.get('file_path', '') or orphan.get('file', '') or '').stem
        
        scored_callers = []
        
        # Strategy 1: Same-file functions (non-orphans)
        for node in candidates:
            node_file = Path(node.get('file_path', '') or node.get('file', '') or '').stem
            node_name = node.get('name', '')
            node_id = node.get('id', '')
            
            score = 0.0
            
            # Same file bonus
            if node_file == orphan_file:
                score += 0.5
            
            # Domain match bonus
            for domain, callers in self.CALLER_MAPPINGS.items():
                if domain in orphan_name:
                    if any(c.replace('.py', '') in node_file for c in callers):
                        score += 0.4
            
            # Category match bonus
            if category in ['analyzer', 'detector']:
                if 'full_analysis' in node_file or 'insights' in node_file:
                    score += 0.3
            
            if score > 0:
                scored_callers.append((node_id, score))
        
        # Strategy 2: Known caller mappings
        for domain, callers in self.CALLER_MAPPINGS.items():
            if domain in orphan_name:
                for caller_file in callers:
                    # Find the main function in that file
                    for node in candidates:
                        node_file = Path(node.get('file_path', '') or node.get('file', '') or '').name
                        if node_file == caller_file:
                            node_id = node.get('id', '')
                            if node_id not in [c[0] for c in scored_callers]:
                                scored_callers.append((node_id, 0.35))
        
        # Sort by score
        scored_callers.sort(key=lambda x: x[1], reverse=True)
        
        if not scored_callers:
            return [], 0.0
        
        callers = [c[0] for c in scored_callers]
        confidence = scored_callers[0][1] if scored_callers else 0.0
        
        return callers, confidence
    
    def _generate_integration(self, orphan: Dict, caller_id: str) -> str:
        """Generate integration code snippet."""
        orphan_name = orphan.get('name', 'orphan_function')
        orphan_file = Path(orphan.get('file_path', '') or orphan.get('file', '') or '').stem
        
        # Extract caller file
        caller_file = caller_id.split(':')[0] if ':' in caller_id else 'caller'
        caller_file = Path(caller_file).stem
        
        # Generate import statement
        import_stmt = f"from {orphan_file} import {orphan_name}"
        
        # Generate usage example based on signature
        signature = orphan.get('signature', '')
        if 'graph' in signature.lower() or 'g:' in signature.lower():
            usage = f"result = {orphan_name}(G, nodes, edges)"
        elif 'nodes' in signature.lower():
            usage = f"result = {orphan_name}(nodes)"
        elif 'path' in signature.lower():
            usage = f"result = {orphan_name}(file_path)"
        else:
            usage = f"result = {orphan_name}()"
        
        return f"""# Integration suggestion for {caller_file}.py
{import_stmt}

# Add to appropriate function:
{usage}"""


def analyze_orphans(
    nodes: List[Dict],
    edges: List[Dict],
    orphan_ids: List[str]
) -> List[OrphanAnalysis]:
    """
    Convenience function to analyze orphans.
    
    Usage:
        from orphan_integrator import analyze_orphans
        
        analysis = analyze_orphans(nodes, edges, orphan_ids)
        for a in analysis:
            print(f"{a.name}: {a.purpose} → {a.suggested_callers}")
    """
    integrator = OrphanIntegrator()
    return integrator.analyze_orphans(nodes, edges, orphan_ids)


if __name__ == "__main__":
    # Demo with mock data
    mock_nodes = [
        {"id": "graph_analyzer.py:shortest_path", "name": "shortest_path", 
         "file_path": "graph_analyzer.py", "signature": "shortest_path(G, source, target)"},
        {"id": "full_analysis.py:run_full_analysis", "name": "run_full_analysis",
         "file_path": "full_analysis.py"},
    ]
    mock_edges = []
    mock_orphans = ["graph_analyzer.py:shortest_path"]
    
    results = analyze_orphans(mock_nodes, mock_edges, mock_orphans)
    for r in results:
        print(f"\n{'='*60}")
        print(f"Orphan: {r.name}")
        print(f"Purpose: {r.purpose} ({r.category})")
        print(f"Confidence: {r.confidence:.2f}")
        print(f"Suggested callers: {r.suggested_callers}")
        if r.integration_code:
            print(f"\nIntegration code:\n{r.integration_code}")
