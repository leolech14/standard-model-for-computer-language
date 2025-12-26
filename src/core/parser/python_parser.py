"""
Python AST Parser

Extracts symbols from Python source code using the built-in AST module.
Part of the TreeSitterUniversalEngine decomposition (GOD_CLASS_DECOMPOSITION).
"""
import ast
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class PythonSymbol:
    """A symbol extracted from Python source code."""
    name: str
    kind: str  # class, function, method
    line: int
    end_line: int
    parent: str = ""
    decorators: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    params: List[Dict[str, str]] = field(default_factory=list)
    return_type: str = ""
    docstring: str = ""
    body_source: str = ""
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind,
            "line": self.line,
            "end_line": self.end_line,
            "parent": self.parent,
            "decorators": self.decorators,
            "base_classes": self.base_classes,
            "params": self.params,
            "return_type": self.return_type,
            "docstring": self.docstring,
        }


class PythonASTParser:
    """Parses Python source code using the AST module."""
    
    # Maximum depth before switching to iterative traversal
    MAX_RECURSIVE_DEPTH = 500
    
    def __init__(self):
        self.symbols: List[PythonSymbol] = []
        self.lines: List[str] = []
    
    def parse(self, content: str) -> List[PythonSymbol]:
        """Parse Python content and extract all symbols."""
        self.symbols = []
        self.lines = content.splitlines()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        
        # Measure depth to choose traversal strategy
        depth = self._measure_depth(tree)
        
        if depth < self.MAX_RECURSIVE_DEPTH:
            self._extract_recursive(tree)
        else:
            self._extract_iterative(tree)
        
        return self.symbols
    
    def _measure_depth(self, tree: ast.AST) -> int:
        """Measure AST depth without recursion."""
        max_depth = 0
        stack = [(tree, 0)]
        
        while stack:
            node, depth = stack.pop()
            max_depth = max(max_depth, depth)
            
            for child in ast.iter_child_nodes(node):
                stack.append((child, depth + 1))
        
        return max_depth
    
    def _extract_recursive(self, tree: ast.AST, parent: str = ""):
        """Recursive extraction for normal-depth trees."""
        
        class Visitor(ast.NodeVisitor):
            def __init__(self_v, parser, parent_name):
                self_v.parser = parser
                self_v.parent = parent_name
            
            def visit_ClassDef(self_v, node: ast.ClassDef):
                symbol = self_v.parser._extract_class(node, self_v.parent)
                self_v.parser.symbols.append(symbol)
                
                # Visit methods with class as parent
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_symbol = self_v.parser._extract_function(child, node.name)
                        self_v.parser.symbols.append(method_symbol)
                    elif isinstance(child, ast.ClassDef):
                        Visitor(self_v.parser, node.name).visit(child)
            
            def visit_FunctionDef(self_v, node: ast.FunctionDef):
                if not self_v.parent:  # Only top-level functions
                    symbol = self_v.parser._extract_function(node, "")
                    self_v.parser.symbols.append(symbol)
            
            def visit_AsyncFunctionDef(self_v, node: ast.AsyncFunctionDef):
                if not self_v.parent:
                    symbol = self_v.parser._extract_function(node, "")
                    self_v.parser.symbols.append(symbol)
        
        Visitor(self, parent).visit(tree)
    
    def _extract_iterative(self, tree: ast.AST):
        """Iterative extraction for deep trees (avoids recursion limits)."""
        stack = [(tree, "")]
        
        while stack:
            node, parent = stack.pop()
            
            if isinstance(node, ast.ClassDef):
                symbol = self._extract_class(node, parent)
                self.symbols.append(symbol)
                
                # Add children with class as parent
                for child in reversed(node.body):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_symbol = self._extract_function(child, node.name)
                        self.symbols.append(method_symbol)
                    elif isinstance(child, ast.ClassDef):
                        stack.append((child, node.name))
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not parent:  # Only top-level
                    symbol = self._extract_function(node, "")
                    self.symbols.append(symbol)
            
            elif isinstance(node, ast.Module):
                for child in reversed(node.body):
                    stack.append((child, parent))
    
    def _extract_class(self, node: ast.ClassDef, parent: str) -> PythonSymbol:
        """Extract a class symbol."""
        return PythonSymbol(
            name=node.name,
            kind="class",
            line=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            parent=parent,
            decorators=self._get_decorators(node),
            base_classes=self._get_base_classes(node),
            docstring=self._get_docstring(node),
        )
    
    def _extract_function(self, node, parent: str) -> PythonSymbol:
        """Extract a function/method symbol."""
        return PythonSymbol(
            name=node.name,
            kind="method" if parent else "function",
            line=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            parent=parent,
            decorators=self._get_decorators(node),
            params=self._get_params(node),
            return_type=self._get_return_type(node),
            docstring=self._get_docstring(node),
            body_source=self._get_body_source(node),
        )
    
    def _get_decorators(self, node) -> List[str]:
        """Extract decorator names."""
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(f"{self._get_attribute_name(dec)}")
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    decorators.append(dec.func.id)
                elif isinstance(dec.func, ast.Attribute):
                    decorators.append(self._get_attribute_name(dec.func))
        return decorators
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get full attribute name like pytest.mark.parametrize."""
        parts = [node.attr]
        current = node.value
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return '.'.join(reversed(parts))
    
    def _get_base_classes(self, node: ast.ClassDef) -> List[str]:
        """Extract base class names."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(self._get_attribute_name(base))
        return bases
    
    def _get_params(self, node) -> List[Dict[str, str]]:
        """Extract function parameters with types and defaults."""
        params = []
        args = node.args
        
        # Calculate defaults offset
        defaults_offset = len(args.args) - len(args.defaults)
        
        for i, arg in enumerate(args.args):
            param = {"name": arg.arg}
            
            # Type annotation
            if arg.annotation:
                param["type"] = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else ""
            
            # Default value
            default_idx = i - defaults_offset
            if default_idx >= 0 and default_idx < len(args.defaults):
                try:
                    param["default"] = ast.unparse(args.defaults[default_idx]) if hasattr(ast, 'unparse') else "..."
                except:
                    param["default"] = "..."
            
            params.append(param)
        
        # *args
        if args.vararg:
            params.append({"name": f"*{args.vararg.arg}"})
        
        # **kwargs
        if args.kwarg:
            params.append({"name": f"**{args.kwarg.arg}"})
        
        return params
    
    def _get_return_type(self, node) -> str:
        """Extract return type annotation."""
        if node.returns:
            try:
                return ast.unparse(node.returns) if hasattr(ast, 'unparse') else ""
            except:
                return ""
        return ""
    
    def _get_docstring(self, node) -> str:
        """Extract docstring from function or class."""
        return ast.get_docstring(node) or ""
    
    def _get_body_source(self, node) -> str:
        """Extract body source code."""
        if not self.lines:
            return ""
        
        try:
            start = node.lineno - 1
            end = getattr(node, 'end_lineno', start + 1)
            return '\n'.join(self.lines[start:end])
        except:
            return ""


def parse_python(content: str) -> List[PythonSymbol]:
    """Convenience function to parse Python content."""
    parser = PythonASTParser()
    return parser.parse(content)


if __name__ == "__main__":
    # Test the parser
    test_code = '''
class UserRepository(BaseRepository):
    """Repository for User entities."""
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.session.query(User).get(user_id)
    
    def save(self, user: User) -> User:
        """Save user to database."""
        self.session.add(user)
        return user

def create_user(name: str, email: str) -> User:
    """Factory function for users."""
    return User(name=name, email=email)

@pytest.fixture
def sample_user():
    return User(name="Test", email="test@example.com")
'''
    
    parser = PythonASTParser()
    symbols = parser.parse(test_code)
    
    print("Extracted symbols:")
    for sym in symbols:
        parent_str = f" (in {sym.parent})" if sym.parent else ""
        print(f"  {sym.kind:10} {sym.name:25}{parent_str}")
        if sym.decorators:
            print(f"             decorators: {sym.decorators}")
        if sym.base_classes:
            print(f"             bases: {sym.base_classes}")
