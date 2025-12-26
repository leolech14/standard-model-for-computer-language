"""
Python AST Extractor
Extracted from TreeSitterUniversalEngine to handle Python-specific AST parsing.
"""
import ast
from typing import List, Dict, Any, Tuple, Optional

class PythonASTExtractor:
    """Handles parsing and extraction of Python code using the `ast` module."""

    def __init__(self, classifier):
        self.classifier = classifier

    def extract_particles_ast(self, content: str, file_path: str, include_depth_metrics: bool = False) -> Tuple[List[Dict], Dict[str, Any]]:
        """Extract particles using Python's AST module (faster/more accurate for Python)."""
        particles = []
        depth_metrics = {}
        try:
            tree = ast.parse(content)
            
            if include_depth_metrics:
                depth_metrics = self._measure_ast_depth(tree)
            
            lines = content.splitlines()
            
            # Use recursive or iterative based on depth/preference
            # For now, default to recursive as it's cleaner, unless depth is huge
            particles = self._extract_recursive(tree, file_path, lines)
            
        except Exception as e:
            # Fallback or empty if parse fails
            pass
            
        return particles, depth_metrics

    def _measure_ast_depth(self, tree: ast.AST) -> Dict[str, int]:
        """Measure AST depth without recursion to avoid stack limits."""
        max_depth = 0
        node_count = 0
        stack = [(tree, 1)]
        while stack:
            node, depth = stack.pop()
            node_count += 1
            if depth > max_depth:
                max_depth = depth
            for child in ast.iter_child_nodes(node):
                stack.append((child, depth + 1))
        return {"node_count": node_count, "max_depth": max_depth}

    def _extract_recursive(self, tree: ast.AST, file_path: str, lines: List[str]) -> List[Dict]:
        """Recursive AST traversal for Python symbols."""
        particles: List[Dict[str, Any]] = []
        class_stack: List[str] = []
        func_stack: List[str] = []
        
        # Capture self for closure usage in Visitor
        classifier = self.classifier
        extractor = self

        def evidence_for_line(line_no: int) -> str:
            idx = max(0, int(line_no or 1) - 1)
            if idx >= len(lines):
                return ""
            return (lines[idx] or "").strip()

        class Visitor(ast.NodeVisitor):
            def visit_ClassDef(self, node: ast.ClassDef):
                class_name = getattr(node, "name", "") or ""
                line_no = getattr(node, "lineno", 0) or 0
                parent = class_stack[-1] if class_stack else (func_stack[-1] if func_stack else "")

                base_classes = extractor._get_base_class_names(node)
                decorators = extractor._get_decorators(node)

                particles.append(
                    classifier.classify_extracted_symbol(
                        name=class_name,
                        symbol_kind="class",
                        file_path=file_path,
                        line_num=line_no,
                        evidence=evidence_for_line(line_no),
                        parent=parent,
                        base_classes=base_classes,
                        decorators=decorators,
                    )
                )

                class_stack.append(class_name)
                self.generic_visit(node)
                class_stack.pop()

            def visit_FunctionDef(self, node: ast.FunctionDef):
                func_name = getattr(node, "name", "") or ""
                line_no = getattr(node, "lineno", 0) or 0
                end_line_no = getattr(node, "end_lineno", line_no) or line_no
                
                if class_stack:
                    full_name = f"{class_stack[-1]}.{func_name}"
                    parent = class_stack[-1]
                    kind = "method"
                elif func_stack:
                    full_name = f"{func_stack[-1]}.{func_name}"
                    parent = func_stack[-1]
                    kind = "function"
                else:
                    full_name = func_name
                    parent = ""
                    kind = "function"

                decorators = extractor._get_decorators(node)
                
                # Extract lossless fields
                body_source = extractor._get_function_body(node, lines)
                params = extractor._get_function_params(node)
                docstring = extractor._get_docstring(node)
                return_type = extractor._get_return_type(node)

                particles.append(
                    classifier.classify_extracted_symbol(
                        name=full_name,
                        symbol_kind=kind,
                        file_path=file_path,
                        line_num=line_no,
                        end_line=end_line_no,
                        evidence=evidence_for_line(line_no),
                        parent=parent,
                        decorators=decorators,
                        body_source=body_source,
                        params=params,
                        docstring=docstring,
                        return_type=return_type,
                    )
                )

                func_stack.append(func_name)
                self.generic_visit(node)
                func_stack.pop()

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
                self.visit_FunctionDef(node)  # type: ignore[arg-type]

        Visitor().visit(tree)
        return particles

    def _get_base_class_names(self, node: ast.ClassDef) -> List[str]:
        """Extract base class names from a Python class definition."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)
            elif isinstance(base, ast.Subscript):
                if isinstance(base.value, ast.Name):
                    bases.append(base.value.id)
                elif isinstance(base.value, ast.Attribute):
                    bases.append(base.value.attr)
        return bases

    def _get_decorators(self, node: Any) -> List[str]:
        """Extract decorator names from a node."""
        decorators = []
        for decorator in getattr(node, "decorator_list", []):
            try:
                if isinstance(decorator, ast.Name):
                    decorators.append(decorator.id)
                elif isinstance(decorator, ast.Attribute):
                    parts = []
                    while isinstance(decorator, ast.Attribute):
                        parts.append(decorator.attr)
                        decorator = decorator.value
                    if isinstance(decorator, ast.Name):
                        parts.append(decorator.id)
                    decorators.append(".".join(reversed(parts)))
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name):
                        decorators.append(decorator.func.id)
                    elif isinstance(decorator.func, ast.Attribute):
                        parts = []
                        curr = decorator.func
                        while isinstance(curr, ast.Attribute):
                            parts.append(curr.attr)
                            curr = curr.value
                        if isinstance(curr, ast.Name):
                            parts.append(curr.id)
                        decorators.append(".".join(reversed(parts)))
            except Exception:
                pass
        return decorators

    def _get_function_body(self, node: Any, lines: List[str]) -> str:
        """Extract function body source code for lossless regeneration."""
        try:
            start = getattr(node, "lineno", 0) - 1
            end = getattr(node, "end_lineno", start + 1)
            if start >= 0 and end <= len(lines):
                return "\n".join(lines[start:end])
        except Exception:
            pass
        return ""

    def _get_function_params(self, node: Any) -> List[Dict[str, str]]:
        """Extract function parameters with types and defaults."""
        params = []
        try:
            args = getattr(node, "args", None)
            if not args:
                return params
            
            defaults = args.defaults or []
            num_defaults = len(defaults)
            num_args = len(args.args)
            
            for i, arg in enumerate(args.args):
                param = {"name": arg.arg}
                if arg.annotation:
                    param["type"] = ast.unparse(arg.annotation)
                
                default_idx = i - (num_args - num_defaults)
                if default_idx >= 0 and default_idx < len(defaults):
                    param["default"] = ast.unparse(defaults[default_idx])
                
                params.append(param)
            
            if args.vararg:
                param = {"name": f"*{args.vararg.arg}"}
                if args.vararg.annotation:
                    param["type"] = ast.unparse(args.vararg.annotation)
                params.append(param)
            
            if args.kwarg:
                param = {"name": f"**{args.kwarg.arg}"}
                if args.kwarg.annotation:
                    param["type"] = ast.unparse(args.kwarg.annotation)
                params.append(param)
        except Exception:
            pass
        return params

    def _get_docstring(self, node: Any) -> str:
        try:
            return ast.get_docstring(node) or ""
        except Exception:
            return ""

    def _get_return_type(self, node: Any) -> str:
        try:
            if hasattr(node, "returns") and node.returns:
                return ast.unparse(node.returns)
        except Exception:
            pass
        return ""
