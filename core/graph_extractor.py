#!/usr/bin/env python3
"""
Graph Extractor — Captures relationships between code components.

This module extracts the EDGES that connect our atoms:
1. Call Graph:       function → function (who calls whom)
2. Dependency Graph: module → module (import chains)
3. Inheritance:      class → class (parent-child)
4. Data Flow:        variable → variable (assignments/usage)

Together with atoms, this provides ~90% of information needed to
reconstruct a complete system diagram.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import json


@dataclass
class Edge:
    """A relationship between two code entities."""
    source: str          # Source node (e.g., "UserRepository.save")
    target: str          # Target node (e.g., "Database.insert")
    edge_type: str       # call, import, inherit, data_flow
    file: str = ""       # Source file
    line: int = 0        # Line number
    metadata: Dict = field(default_factory=dict)


@dataclass
class Node:
    """A code entity (file, class, function, variable)."""
    id: str              # Unique identifier
    name: str            # Human-readable name
    node_type: str       # file, class, function, variable
    raw_type: str = ""   # Original Tree-sitter type (e.g. class_declaration)
    file: str = ""       # Source file
    start_line: int = 0
    end_line: int = 0
    parent: str = ""     # Parent node ID (e.g., class for method)
    metadata: Dict = field(default_factory=dict)


@dataclass
class CodeGraph:
    """Complete graph representation of a codebase."""
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)
    
    # Indexed views for fast lookup
    call_graph: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    reverse_call_graph: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    import_graph: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    inheritance_graph: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    data_flow: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    
    def add_node(self, node: Node):
        self.nodes[node.id] = node
    
    def add_edge(self, edge: Edge):
        self.edges.append(edge)
        
        # Index by type
        if edge.edge_type == "call":
            self.call_graph[edge.source].append(edge.target)
            self.reverse_call_graph[edge.target].append(edge.source)
        elif edge.edge_type == "import":
            self.import_graph[edge.source].append(edge.target)
        elif edge.edge_type == "inherit":
            self.inheritance_graph[edge.source].append(edge.target)
        elif edge.edge_type == "data_flow":
            self.data_flow[edge.source].append(edge.target)
    
    def get_stats(self) -> Dict:
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "call_edges": sum(len(v) for v in self.call_graph.values()),
            "import_edges": sum(len(v) for v in self.import_graph.values()),
            "inherit_edges": sum(len(v) for v in self.inheritance_graph.values()),
            "data_flow_edges": sum(len(v) for v in self.data_flow.values()),
        }


class GraphExtractor:
    """
    Extracts comprehensive relationship graphs from source code.
    
    Uses tree-sitter for accurate AST-based extraction.
    """
    
    def __init__(self):
        self.parsers = {}
        self._init_parsers()
    
    def _init_parsers(self):
        from core.language_loader import LanguageLoader
        self.parsers, self.languages, self.extensions = LanguageLoader.load_all()
    
    def extract(self, repo_path: str, language: str = "python") -> CodeGraph:
        """
        Extract complete code graph from a repository.
        """
        path = Path(repo_path)
        graph = CodeGraph()
        
        if language not in self.parsers:
            # Try to auto-detect or fallback? For now raise.
            # But wait, 'typescript' vs 'tsx'. User passes 'typescript'.
            # We should probably check if language is valid.
            if language not in self.parsers:
                # Fallback for 'typescript' which might mean 'tsx' too?
                # The loader returns 'typescript' and 'tsx' as separate keys.
                raise ValueError(f"Unsupported language: {language}")
        
        parser = self.parsers[language]
        
        # First pass: collect all files and their structure
        file_contents = {}
        
        # Use extensions from loader
        patterns = self.extensions.get(language, ["*.py"])
        found_files = []
        for pattern in patterns:
            # Ensure pattern is a glob (e.g. ".ts" -> "*.ts")
            glob_pat = pattern if pattern.startswith("*") else f"*{pattern}"
            found_files.extend(list(path.rglob(glob_pat)))
            # Also check for src/ for TS if needed commonly?
            # Loader puts simple exts. Let's add recursive search for them.
            # actually rglob('*.ts') is recursive. 'src/**/*.ts' is redundant if we do pattern='*.ts'.
            
        for py_file in found_files:
            if any(x in str(py_file) for x in ["__pycache__", "node_modules", ".git", ".venv", "dddlint_env", "output/"]):
                continue
            
            try:
                rel_path = str(py_file.relative_to(path))
                code = py_file.read_bytes()
                tree = parser.parse(code)
                file_contents[rel_path] = (code, tree)
                
                # Add file node
                graph.add_node(Node(
                    id=f"file:{rel_path}",
                    name=rel_path,
                    node_type="file",
                    raw_type="file",
                    file=rel_path,
                ))
            except Exception as e:
                pass
        
        # Second pass: extract structure and relationships
        for rel_path, (code, tree) in file_contents.items():
            self._extract_from_file(graph, rel_path, code, tree)
        
        return graph
    
    def _extract_from_file(self, graph: CodeGraph, file_path: str, code: bytes, tree):
        """Extract all nodes and edges from a single file."""
        
        # Track current scope for qualified names
        scope_stack = [file_path]
        
        def get_qualified_name(name: str) -> str:
            if len(scope_stack) > 1:
                return f"{scope_stack[-1]}.{name}"
            return f"{file_path}:{name}"
        
        def extract_name(node) -> str:
            """Extract identifier name from a node."""
            for child in node.children:
                if child.type == "identifier":
                    return child.text.decode()
            return ""
        
        def visit(node, parent_class=None, parent_func=None):
            node_type = node.type
            
            # ═══ IMPORTS ═══
            if node_type == "import_statement":
                # import x, y, z
                for child in node.children:
                    if child.type == "dotted_name":
                        module_name = child.text.decode()
                        graph.add_edge(Edge(
                            source=f"file:{file_path}",
                            target=f"module:{module_name}",
                            edge_type="import",
                            file=file_path,
                            line=node.start_point[0] + 1,
                        ))
            
            elif node_type == "import_from_statement":
                # from x import y
                module_name = ""
                for child in node.children:
                    if child.type == "dotted_name":
                        module_name = child.text.decode()
                        break
                    elif child.type == "relative_import":
                        module_name = child.text.decode()
                        break
                
                if module_name:
                    graph.add_edge(Edge(
                        source=f"file:{file_path}",
                        target=f"module:{module_name}",
                        edge_type="import",
                        file=file_path,
                        line=node.start_point[0] + 1,
                    ))
            
            # ═══ CLASSES ═══
            elif node_type == "class_definition":
                class_name = extract_name(node)
                class_id = get_qualified_name(class_name)
                
                graph.add_node(Node(
                    id=class_id,
                    name=class_name,
                    node_type="class",
                    raw_type=node.type,
                    file=file_path,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=f"file:{file_path}",
                ))
                
                # Extract inheritance (argument_list contains base classes)
                for child in node.children:
                    if child.type == "argument_list":
                        for base in child.children:
                            if base.type == "identifier":
                                base_name = base.text.decode()
                                graph.add_edge(Edge(
                                    source=class_id,
                                    target=f"class:{base_name}",
                                    edge_type="inherit",
                                    file=file_path,
                                    line=node.start_point[0] + 1,
                                ))
                            elif base.type == "attribute":
                                base_name = base.text.decode()
                                graph.add_edge(Edge(
                                    source=class_id,
                                    target=f"class:{base_name}",
                                    edge_type="inherit",
                                    file=file_path,
                                    line=node.start_point[0] + 1,
                                ))
                
                # Process class body
                scope_stack.append(class_id)
                for child in node.children:
                    if child.type == "block":
                        for stmt in child.children:
                            visit(stmt, parent_class=class_id)
                scope_stack.pop()
                return  # Don't recurse further
            
            # ═══ FUNCTIONS ═══
            elif node_type in ("function_definition", "async_function_definition"):
                func_name = extract_name(node)
                func_id = get_qualified_name(func_name)
                
                graph.add_node(Node(
                    id=func_id,
                    name=func_name,
                    node_type="function",
                    raw_type=node.type,
                    file=file_path,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=parent_class or f"file:{file_path}",
                ))
                
                # Process function body for calls
                scope_stack.append(func_id)
                for child in node.children:
                    if child.type == "block":
                        self._extract_calls(graph, child, func_id, file_path)
                        self._extract_data_flow(graph, child, func_id, file_path)
                scope_stack.pop()
                return  # Don't recurse further
            
            # Recurse into children
            for child in node.children:
                visit(child, parent_class, parent_func)
        
        visit(tree.root_node)
    
    def _extract_calls(self, graph: CodeGraph, block_node, caller_id: str, file_path: str):
        """Extract function calls from a code block."""
        
        def visit(node):
            if node.type == "call":
                # Extract the function being called
                callee = self._extract_callee(node)
                if callee:
                    graph.add_edge(Edge(
                        source=caller_id,
                        target=f"func:{callee}",
                        edge_type="call",
                        file=file_path,
                        line=node.start_point[0] + 1,
                    ))
            
            for child in node.children:
                visit(child)
        
        visit(block_node)
    
    def _extract_callee(self, call_node) -> Optional[str]:
        """Extract the name of the function being called."""
        for child in call_node.children:
            if child.type == "identifier":
                return child.text.decode()
            elif child.type == "attribute":
                return child.text.decode()
        return None
    
    def _extract_data_flow(self, graph: CodeGraph, block_node, scope_id: str, file_path: str):
        """Extract data flow (variable assignments and usage)."""
        
        assignments = {}  # var_name -> line where assigned
        
        def visit(node):
            if node.type == "assignment":
                # Track what's being assigned
                for child in node.children:
                    if child.type == "identifier":
                        var_name = child.text.decode()
                        var_id = f"{scope_id}::{var_name}"
                        
                        graph.add_node(Node(
                            id=var_id,
                            name=var_name,
                            node_type="variable",
                            file=file_path,
                            start_line=node.start_point[0] + 1,
                            parent=scope_id,
                        ))
                        
                        assignments[var_name] = var_id
                        break
                
                # Track what's being used (right side)
                for child in node.children[1:]:
                    self._track_variable_usage(graph, child, scope_id, assignments, file_path)
            
            for child in node.children:
                visit(child)
        
        visit(block_node)
    
    def _track_variable_usage(self, graph: CodeGraph, node, scope_id: str, 
                               assignments: Dict, file_path: str):
        """Track variable usage to build data flow edges."""
        if node.type == "identifier":
            var_name = node.text.decode()
            if var_name in assignments:
                # Variable used from earlier assignment
                graph.add_edge(Edge(
                    source=assignments[var_name],
                    target=f"{scope_id}::usage:{var_name}",
                    edge_type="data_flow",
                    file=file_path,
                    line=node.start_point[0] + 1,
                ))
        
        for child in node.children:
            self._track_variable_usage(graph, child, scope_id, assignments, file_path)
    
    def to_mermaid(self, graph: CodeGraph, max_nodes: int = 50) -> str:
        """Generate Mermaid diagram from graph."""
        lines = ["graph TD"]
        
        # Add nodes (limited for readability)
        node_ids = set()
        for i, (node_id, node) in enumerate(graph.nodes.items()):
            if i >= max_nodes:
                break
            
            safe_id = node_id.replace(":", "_").replace(".", "_").replace("/", "_")
            node_ids.add(node_id)
            
            if node.node_type == "file":
                lines.append(f'    {safe_id}["{node.name}"]')
            elif node.node_type == "class":
                lines.append(f'    {safe_id}[["🏛️ {node.name}"]]')
            elif node.node_type == "function":
                lines.append(f'    {safe_id}(("📦 {node.name}"))')
        
        # Add edges
        for edge in graph.edges[:100]:  # Limit edges
            if edge.source in node_ids or edge.target in node_ids:
                src = edge.source.replace(":", "_").replace(".", "_").replace("/", "_")
                tgt = edge.target.replace(":", "_").replace(".", "_").replace("/", "_")
                
                if edge.edge_type == "call":
                    lines.append(f'    {src} --> {tgt}')
                elif edge.edge_type == "import":
                    lines.append(f'    {src} -.-> {tgt}')
                elif edge.edge_type == "inherit":
                    lines.append(f'    {src} ==> {tgt}')
        
        return "\n".join(lines)
    
    def export_json(self, graph: CodeGraph, path: str):
        """Export graph to JSON for visualization."""
        data = {
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.node_type,
                    "file": n.file,
                    "start_line": n.start_line,
                    "end_line": n.end_line,
                    "parent": n.parent,
                } for n in graph.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "type": e.edge_type,
                    "file": e.file,
                    "line": e.line,
                } for e in graph.edges
            ],
            "stats": graph.get_stats(),
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    from pathlib import Path
    
    print("=" * 70)
    print("🔗 GRAPH EXTRACTOR — Relationships Between Components")
    print("=" * 70)
    print()
    
    extractor = GraphExtractor()
    
    # Test on dddpy
    dddpy_path = Path(__file__).parent.parent / "validation" / "dddpy_real"
    
    if dddpy_path.exists():
        print(f"Analyzing: {dddpy_path}")
        print()
        
        graph = extractor.extract(str(dddpy_path))
        stats = graph.get_stats()
        
        print("📊 GRAPH STATISTICS:")
        print(f"   Nodes:          {stats['nodes']:>6}")
        print(f"   Total Edges:    {stats['edges']:>6}")
        print(f"   ├─ Call edges:  {stats['call_edges']:>6}")
        print(f"   ├─ Import edges:{stats['import_edges']:>6}")
        print(f"   ├─ Inherit:     {stats['inherit_edges']:>6}")
        print(f"   └─ Data flow:   {stats['data_flow_edges']:>6}")
        print()
        
        # Show sample relationships
        print("📞 SAMPLE CALL GRAPH (first 10):")
        shown = 0
        for caller, callees in graph.call_graph.items():
            if shown >= 10:
                break
            for callee in callees[:2]:
                caller_short = caller.split(":")[-1] if ":" in caller else caller
                print(f"   {caller_short} → {callee}")
                shown += 1
        print()
        
        print("📥 SAMPLE IMPORTS (first 10):")
        for i, (src, targets) in enumerate(graph.import_graph.items()):
            if i >= 10:
                break
            for target in targets[:2]:
                src_short = src.replace("file:", "")
                tgt_short = target.replace("module:", "")
                print(f"   {src_short} imports {tgt_short}")
        print()
        
        print("🏛️ INHERITANCE:")
        for child, parents in graph.inheritance_graph.items():
            for parent in parents:
                child_short = child.split(":")[-1] if ":" in child else child
                parent_short = parent.replace("class:", "")
                print(f"   {child_short} extends {parent_short}")
        print()
        
        # Export
        output_path = Path(__file__).parent.parent / "output" / "code_graph.json"
        output_path.parent.mkdir(exist_ok=True)
        extractor.export_json(graph, str(output_path))
        print(f"💾 Exported to: {output_path}")
        
        # Generate Mermaid
        mermaid = extractor.to_mermaid(graph)
        mermaid_path = Path(__file__).parent.parent / "output" / "code_graph.mmd"
        mermaid_path.write_text(mermaid)
        print(f"📊 Mermaid diagram: {mermaid_path}")
    else:
        print(f"ERROR: dddpy not found at {dddpy_path}")
