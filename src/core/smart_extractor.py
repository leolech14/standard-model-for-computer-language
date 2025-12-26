#!/usr/bin/env python3
"""
🧠 SMART EXTRACTOR — Rich Context Extraction for LLM Classification

Extracts ComponentCard with full context for Unknown nodes that need LLM classification.
This is the "smart extraction" layer that prepares data for the LLM classifier.
"""

import ast
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple


@dataclass
class ComponentCard:
    """Rich context packet for LLM classification."""
    node_id: str
    file_path: str
    name: str
    kind: str  # class, function, method
    start_line: int
    end_line: int
    
    # Code content
    code_excerpt: str = ""  # Actual code (max ~100 lines)
    signature: str = ""
    docstring: str = ""
    
    # Structural context
    decorators: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    
    # Graph context
    outgoing_calls: List[str] = field(default_factory=list)
    incoming_calls: List[str] = field(default_factory=list)
    
    # Location context
    folder_layer: str = ""  # inferred from path
    
    # Heuristic pre-classification
    heuristic_type: str = "Unknown"
    heuristic_confidence: float = 0.0


class SmartExtractor:
    """
    Extracts rich ComponentCard context for nodes that need LLM classification.
    
    Key features:
    1. Reads actual source code (bounded to ~100 lines)
    2. Extracts AST information (decorators, base classes, docstrings)
    3. Infers folder layer from path
    4. Collects import statements for framework detection
    """
    
    # Layer inference patterns
    LAYER_PATTERNS = {
        "domain": ["/domain/", "/entities/", "/aggregates/", "/value_objects/"],
        "application": ["/application/", "/use_cases/", "/usecases/", "/services/"],
        "infrastructure": ["/infrastructure/", "/adapters/", "/repositories/", "/persistence/"],
        "presentation": ["/presentation/", "/controllers/", "/api/", "/views/", "/endpoints/"],
        "cross_cutting": ["/common/", "/shared/", "/utils/", "/helpers/", "/config/"],
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self._file_cache: Dict[str, List[str]] = {}
        self._import_cache: Dict[str, List[str]] = {}
    
    def extract_card(self, 
                     node: Dict,
                     graph_edges: Optional[List[Dict]] = None) -> ComponentCard:
        """
        Extract a ComponentCard for a single node.
        
        Args:
            node: Node dict from graph.json with name, file_path, line, type, etc.
            graph_edges: Optional list of edges for call graph context
        """
        file_path = node.get("file_path", "")
        name = node.get("name", "")
        line_num = node.get("line", 1)
        kind = node.get("symbol_kind", "function")
        
        # Create basic card
        card = ComponentCard(
            node_id=f"{file_path}:{name}:{line_num}",
            file_path=file_path,
            name=name,
            kind=kind,
            start_line=line_num,
            end_line=line_num + 50,  # Will be refined by AST
            heuristic_type=node.get("type", "Unknown"),
            heuristic_confidence=node.get("confidence", 0.0),
        )
        
        # Enrich with source code
        abs_path = self.repo_path / file_path
        if abs_path.exists():
            self._enrich_from_source(card, abs_path)
        
        # Infer folder layer
        card.folder_layer = self._infer_layer(file_path)
        
        # Add graph context if available
        if graph_edges:
            self._add_graph_context(card, graph_edges)
        
        return card
    
    def _enrich_from_source(self, card: ComponentCard, file_path: Path) -> None:
        """Read source file and extract code context."""
        try:
            # Cache file contents
            if str(file_path) not in self._file_cache:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                self._file_cache[str(file_path)] = content.splitlines()
                
                # Parse imports once per file
                self._import_cache[str(file_path)] = self._extract_imports(content)
            
            lines = self._file_cache[str(file_path)]
            
            # Extract code excerpt (100 lines max around the node)
            start = max(0, card.start_line - 1)
            end = min(len(lines), start + 100)
            card.code_excerpt = "\n".join(lines[start:end])
            card.end_line = end
            
            # Add imports from file
            card.imports = self._import_cache[str(file_path)]
            
            # Parse AST for more details
            self._enrich_from_ast(card, "\n".join(lines))
            
        except Exception as e:
            card.code_excerpt = f"# Error reading source: {e}"
    
    def _enrich_from_ast(self, card: ComponentCard, source: str) -> None:
        """Extract AST information: decorators, base classes, docstring."""
        try:
            tree = ast.parse(source)
            
            # Find the node in AST
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name == card.name.split(".")[-1]:
                        # Extract base classes
                        card.base_classes = [
                            self._get_name(base) for base in node.bases
                        ]
                        
                        # Extract decorators
                        card.decorators = [
                            self._get_decorator_name(d) for d in node.decorator_list
                        ]
                        
                        # Extract docstring
                        card.docstring = ast.get_docstring(node) or ""
                        
                        # Get signature (class definition line)
                        card.signature = f"class {node.name}({', '.join(card.base_classes)})"
                        
                        # Precise line range
                        card.start_line = node.lineno
                        card.end_line = node.end_lineno or card.end_line
                        break
                        
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_name = card.name.split(".")[-1]
                    if node.name == func_name:
                        # Extract decorators
                        card.decorators = [
                            self._get_decorator_name(d) for d in node.decorator_list
                        ]
                        
                        # Extract docstring
                        card.docstring = ast.get_docstring(node) or ""
                        
                        # Get signature
                        args = [a.arg for a in node.args.args]
                        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                        card.signature = f"{prefix} {node.name}({', '.join(args)})"
                        
                        # Precise line range
                        card.start_line = node.lineno
                        card.end_line = node.end_lineno or card.end_line
                        break
                        
        except SyntaxError:
            pass  # Not valid Python, skip AST enrichment
    
    def _get_name(self, node) -> str:
        """Get name from AST node (handles Name, Attribute, Subscript)."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return self._get_name(node.value)
        return str(node)
    
    def _get_decorator_name(self, node) -> str:
        """Get decorator name from AST node."""
        if isinstance(node, ast.Name):
            return f"@{node.id}"
        elif isinstance(node, ast.Call):
            return f"@{self._get_name(node.func)}(...)"
        elif isinstance(node, ast.Attribute):
            return f"@{self._get_name(node)}"
        return "@unknown"
    
    def _extract_imports(self, source: str) -> List[str]:
        """Extract import statements from source."""
        imports = []
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(f"import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"from {module} import {alias.name}")
        except SyntaxError:
            # Fallback: regex-based extraction
            for line in source.splitlines()[:50]:
                if line.strip().startswith(("import ", "from ")):
                    imports.append(line.strip())
        
        return imports[:20]  # Limit to 20 imports
    
    def _infer_layer(self, file_path: str) -> str:
        """Infer architectural layer from file path."""
        normalized = file_path.lower().replace("\\", "/")
        
        for layer, patterns in self.LAYER_PATTERNS.items():
            if any(p in normalized for p in patterns):
                return layer
        
        return "unknown"
    
    def _add_graph_context(self, card: ComponentCard, edges: List[Dict]) -> None:
        """Add call graph context (who calls this, who does this call)."""
        node_id = card.node_id
        name = card.name
        
        for edge in edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            
            if name in source or node_id in source:
                card.outgoing_calls.append(target)
            elif name in target or node_id in target:
                card.incoming_calls.append(source)
        
        # Limit for prompt size
        card.outgoing_calls = card.outgoing_calls[:10]
        card.incoming_calls = card.incoming_calls[:10]
    
    def extract_unknowns(self, 
                         graph_data: Dict,
                         limit: Optional[int] = None) -> List[ComponentCard]:
        """
        Extract ComponentCards for all Unknown nodes in a graph.
        
        Args:
            graph_data: Loaded graph.json
            limit: Optional limit on number of cards to extract
        """
        components = graph_data.get("components", {})
        edges = graph_data.get("edges", [])
        
        unknowns = []
        for name, node in components.items():
            if node.get("type") == "Unknown":
                unknowns.append(node)
                if limit and len(unknowns) >= limit:
                    break
        
        cards = []
        for node in unknowns:
            card = self.extract_card(node, edges)
            cards.append(card)
        
        return cards


def format_card_for_llm(card: ComponentCard) -> str:
    """Format a ComponentCard as a prompt for LLM classification."""
    return f"""Classify this code component:

NODE ID: {card.node_id}
FILE: {card.file_path}
NAME: {card.name}
KIND: {card.kind}
LINES: {card.start_line}-{card.end_line}

SIGNATURE:
```
{card.signature}
```

DOCSTRING:
```
{card.docstring or "(no docstring)"}
```

DECORATORS: {', '.join(card.decorators) or "(none)"}
BASE CLASSES: {', '.join(card.base_classes) or "(none)"}
IMPORTS (sample): {', '.join(card.imports[:5]) or "(none)"}

FOLDER LAYER (heuristic): {card.folder_layer}

CALLS (outgoing): {', '.join(card.outgoing_calls[:5]) or "(none)"}
CALLED BY: {', '.join(card.incoming_calls[:5]) or "(none)"}

CODE EXCERPT:
```python
{card.code_excerpt[:2000]}
```

HEURISTIC PRE-CLASSIFICATION:
- Type guess: {card.heuristic_type}
- Confidence: {card.heuristic_confidence:.2f}

Please classify this component and provide evidence-anchored justification.
"""


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python smart_extractor.py <repo_path> [graph.json]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    graph_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    extractor = SmartExtractor(repo_path)
    
    if graph_path:
        with open(graph_path) as f:
            graph_data = json.load(f)
        
        cards = extractor.extract_unknowns(graph_data, limit=5)
        
        print(f"Extracted {len(cards)} ComponentCards:\n")
        for card in cards:
            print(format_card_for_llm(card))
            print("\n" + "="*60 + "\n")
    else:
        print(f"SmartExtractor initialized for: {repo_path}")
