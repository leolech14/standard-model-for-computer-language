#!/usr/bin/env python3
"""
🚀 SPECTROMETER V12 - Tree-sitter Universal Engine
Minimal, maximum output, works across 160+ languages
============================================
"""

import os
import ast
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    from type_registry import normalize_type
except ImportError:
    try:
        from core.type_registry import normalize_type
    except ImportError:
        def normalize_type(t): return t

# =============================================================================
# INHERITANCE-BASED DDD TYPE MAPPINGS (99% confidence)
# =============================================================================
DDD_BASE_CLASS_MAPPINGS = {
    # Entities & Aggregates
    "Entity": "Entity",
    "BaseEntity": "Entity",
    "DomainEntity": "Entity",
    "EntityModel": "Entity",
    "AggregateRoot": "AggregateRoot",
    "Aggregate": "AggregateRoot",
    
    # Value Objects
    "ValueObject": "ValueObject",
    "ValueObjectModel": "ValueObject",
    "BaseFrozenModel": "ValueObject",
    
    # Repositories
    "GenericRepository": "Repository",
    "AbstractRepository": "Repository",
    "BaseRepository": "Repository",
    
    # Events
    "DomainEvent": "DomainEvent",
    "Event": "DomainEvent",
    "IntegrationEvent": "DomainEvent",
    
    # Commands/Queries (CQRS)
    "Command": "Command",
    "BaseCommand": "Command",
    "Query": "Query",
    "BaseQuery": "Query",
    
    # Services
    "DomainService": "DomainService",
    "ApplicationService": "Service",
    
    # Configuration
    "BaseSettings": "Configuration",
}


class TreeSitterUniversalEngine:
    """Universal Tree-sitter engine for cross-language pattern detection"""

    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.java': 'java',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.mjs': 'javascript',
            '.cjs': 'javascript',
            '.go': 'go',
            '.rs': 'rust',
            '.kt': 'kotlin',
            '.cs': 'c_sharp',
            '.rb': 'ruby',
            '.php': 'php'
        }

        # Load universal patterns
        patterns_file = Path(__file__).parent.parent / 'patterns' / 'universal_patterns.json'
        with open(patterns_file) as f:
            self.patterns = json.load(f)

        # Load pattern repository for dynamic pattern matching
        try:
            from core.registry.pattern_repository import get_pattern_repository
            self.pattern_repo = get_pattern_repository()
        except ImportError:
            try:
                from registry.pattern_repository import get_pattern_repository
                self.pattern_repo = get_pattern_repository()
            except ImportError:
                self.pattern_repo = None

        self._ts_symbol_extractor = (Path(__file__).parent.parent / "tools" / "ts_symbol_extractor.cjs").resolve()
        self.python_depth_margin = 50
        self.python_recursion_hard_cap = 10000
        self.depth_summary: Dict[str, Any] = {}

    def _tokenize_identifier(self, name: str) -> List[str]:
        """Tokenize identifier into lowercase tokens (snake_case + CamelCase)."""
        if not name:
            return []

        parts = re.split(r'[_\-\s]+', name)
        tokens: List[str] = []
        for part in parts:
            if not part:
                continue
            tokens.extend(
                t.lower()
                for t in re.findall(
                    r'[A-Z]+(?=[A-Z][a-z]|[0-9]|$)|[A-Z]?[a-z]+|[0-9]+',
                    part,
                )
                if t
            )
        return tokens

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for universal patterns"""

        # Determine language
        ext = Path(file_path).suffix
        language = self.supported_languages.get(ext)

        if not language:
            return self._fallback_analysis(file_path)

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return {'particles': [], 'touchpoints': [], 'language': 'unknown'}

        # Parse (simplified for minimal version)
        depth_metrics: Dict[str, Any] = {}
        if language == 'python':
            particles, depth_metrics = self._extract_python_particles_ast(
                content, file_path, include_depth_metrics=True
            )
        else:
            particles = self._extract_particles(content, language, file_path)
        touchpoints = self._extract_touchpoints(content, particles)
        raw_imports = self._extract_raw_imports(content, language)

        result = {
            'file_path': file_path,
            'language': language,
            'particles': particles,
            'touchpoints': touchpoints,
            'raw_imports': raw_imports,
            'lines_analyzed': len(content.split('\n')),
            'chars_analyzed': len(content)
        }
        if depth_metrics:
            result['depth_metrics'] = depth_metrics
        return result

    def _extract_particles(self, content: str, language: str, file_path: str) -> List[Dict]:
        """Extract particles using universal pattern matching"""
        particles = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # JS/TS: keep to top-level declarations (no indentation) to avoid nested helpers and class methods.
            if language in {'javascript', 'typescript'}:
                if line != line.lstrip():
                    continue

                if re.match(r'^\s*(export\s+)?(default\s+)?(abstract\s+)?class\s+\w+', line):
                    particle = self._classify_class_pattern(line, i, file_path)
                    if particle:
                        particles.append(particle)
                    continue

                if re.match(r'^\s*interface\s+\w+', line) or re.match(r'^\s*type\s+\w+\s*=', line):
                    particle = self._classify_class_pattern(line, i, file_path)
                    if particle:
                        particles.append(particle)
                    continue

                if re.match(r'^\s*(export\s+)?(default\s+)?(async\s+)?function\s+\w+', line) or re.match(
                    r'^\s*(export\s+)?(const|let|var)\s+\w+\s*=\s*(async\s*)?\(?[^=]*=>',
                    line,
                ):
                    particle = self._classify_function_pattern(line, i, file_path, language)
                    if particle:
                        particles.append(particle)
                    continue

            # Other languages: keep permissive matching (indentation is less meaningful)
            if re.match(r'^\s*(class|public class|private class|interface|type)\s+\w+', line):
                particle = self._classify_class_pattern(line, i, file_path)
                if particle:
                    particles.append(particle)
                continue

            if re.match(r'^\s*(async\s+def|def|public|private|protected|static|func|fn)\s+\w+', line):
                particle = self._classify_function_pattern(line, i, file_path, language)
                if particle:
                    particles.append(particle)

        return particles

    def _classify_class_pattern(self, line: str, line_num: int, file_path: str) -> Optional[Dict]:
        """Classify class-like patterns"""
        line_stripped = line.strip()

        # Extract name
        name_match = re.search(r'(class|interface|type)\s+(\w+)', line_stripped)
        if not name_match:
            return None

        class_name = name_match.group(2)

        # Determine particle type by location (strong signal in real-world repos)
        normalized_path = file_path.replace('\\', '/').lower()
        particle_type = None

        if '/domain/' in normalized_path and '/entities/' in normalized_path:
            particle_type = 'Entity'
        elif '/domain/' in normalized_path and '/value_objects/' in normalized_path:
            particle_type = 'ValueObject'
        elif '/usecase/' in normalized_path or '/use_case/' in normalized_path:
            particle_type = 'UseCase'
        elif '/domain/' in normalized_path and '/repositories/' in normalized_path:
            particle_type = 'Repository'
        elif '/infrastructure/' in normalized_path and 'repository' in class_name.lower():
            particle_type = 'RepositoryImpl'
        elif 'BaseModel' in line_stripped or '/schemas/' in normalized_path or '/error_messages/' in normalized_path:
            particle_type = 'DTO'
        elif '/presentation/' in normalized_path and ('/handlers/' in normalized_path or '/api/' in normalized_path):
            particle_type = 'Controller'
        elif '/tests/' in normalized_path or '/test/' in normalized_path:
            particle_type = 'Test'
        elif '/config/' in normalized_path or 'settings' in normalized_path:
            particle_type = 'Configuration'
        elif 'exception' in normalized_path or 'error' in normalized_path:
            particle_type = 'Exception'

        # Determine particle type by naming conventions
        if not particle_type:
            particle_type = self._get_particle_type_by_name(class_name)
        if not particle_type:
            # Try to detect by content patterns
            particle_type = self._detect_by_keywords(line_stripped)

        resolved_type = particle_type or 'Unknown'
        confidence = self._calculate_confidence(class_name, line_stripped) if particle_type else 30.0

        return {
            'type': resolved_type,
            'name': class_name,
            'symbol_kind': 'class',
            'file_path': file_path,
            'line': line_num,
            'confidence': confidence,
            'evidence': line_stripped[:100]
        }

    def _classify_function_pattern(self, line: str, line_num: int, file_path: str, language: str) -> Optional[Dict]:
        """Classify function-like patterns"""
        line_stripped = line.strip()

        # Extract name
        func_name = self._extract_function_name(line_stripped, language)
        if not func_name:
            return None

        # Determine particle type
        particle_type = self._get_function_type_by_name(func_name)

        resolved_type = particle_type or 'Unknown'
        confidence = self._calculate_confidence(func_name, line_stripped) if particle_type else 30.0

        return {
            'type': resolved_type,
            'name': func_name,
            'symbol_kind': 'function',
            'file_path': file_path,
            'line': line_num,
            'confidence': confidence,
            'evidence': line_stripped[:100]
        }

    def _classify_extracted_symbol(
        self,
        *,
        name: str,
        symbol_kind: str,
        file_path: str,
        line_num: int,
        evidence: str = "",
        parent: str = "",
        base_classes: List[str] = None,
        decorators: List[str] = None,
        # NEW: Lossless capture fields
        end_line: int = 0,
        body_source: str = "",
        params: List[Dict[str, str]] = None,  # [{"name": "x", "type": "int", "default": "0"}]
        return_type: str = "",
        docstring: str = "",
    ) -> Dict[str, Any]:
        evidence_line = (evidence or "").strip()
        base_classes = base_classes or []
        decorators = decorators or []

        normalized_path = file_path.replace("\\", "/").lower()
        particle_type: Optional[str] = None
        confidence = 30.0  # Default low confidence
        
        # =============================================================================
        # TIER 0: FRAMEWORK-SPECIFIC OVERRIDES (99% confidence)
        # =============================================================================
        # Pytest / Conftest
        if "conftest.py" in normalized_path:
            if any(d for d in decorators if "fixture" in d) or name == "conftest":
                particle_type = "Configuration"
                confidence = 99.0
            else:
                particle_type = "Test" # Default for things in conftest
                confidence = 80.0
                
        if particle_type is None:
            for d in decorators:
                if "fixture" in d: # pytest.fixture
                    particle_type = "Configuration"
                    confidence = 90.0
                    break
                if "validator" in d.lower(): # pydantic validators, marshmallow
                    particle_type = "Validator"
                    confidence = 90.0
                    break
                if "command" in d.lower(): # click/typer commands
                    particle_type = "Command"
                    confidence = 90.0
                    break
                if d.endswith(".task") or d == "task": # celery.task
                    particle_type = "Job"
                    confidence = 90.0
                    break
                if "router" in d: # fastapi router
                    particle_type = "Controller"
                    confidence = 90.0
                    break

        # =============================================================================
        # TIER 1: INHERITANCE-BASED DETECTION (99% confidence)
        # =============================================================================
        if symbol_kind in {"class", "interface", "type", "enum"} and base_classes:
            for base in base_classes:
                if base in DDD_BASE_CLASS_MAPPINGS:
                    particle_type = DDD_BASE_CLASS_MAPPINGS[base]
                    confidence = 99.0  # Inheritance = highest confidence
                    break

        # =============================================================================
        # TIER 2: PATH-BASED DETECTION (90% confidence)
        # =============================================================================
        if particle_type is None and symbol_kind in {"class", "interface", "type", "enum"}:
            # Strong location signals (DDD/Clean folders, or UI layers).
            if "/domain/" in normalized_path and "/entities/" in normalized_path:
                particle_type = "Entity"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/aggregates/" in normalized_path or "/aggregate/" in normalized_path):
                particle_type = "AggregateRoot"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/events/" in normalized_path or "/event/" in normalized_path):
                particle_type = "DomainEvent"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/value_objects/" in normalized_path or "/valueobjects/" in normalized_path):
                particle_type = "ValueObject"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/services/" in normalized_path or "/domain_services/" in normalized_path):
                particle_type = "DomainService"
                confidence = 90.0
            elif "/domain/" in normalized_path and "/repositories/" in normalized_path:
                particle_type = "Repository"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/commands/" in normalized_path or "/command/" in normalized_path):
                particle_type = "Command"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/queries/" in normalized_path or "/query/" in normalized_path):
                particle_type = "Query"
                confidence = 90.0
            elif "/infrastructure/" in normalized_path and "repository" in name.lower():
                particle_type = "RepositoryImpl"
                confidence = 90.0
            elif (
                "/presentation/" in normalized_path
                or "/controllers/" in normalized_path
                or "/api/" in normalized_path
                or "/ro-finance/src/components/" in normalized_path
                or "/ro-finance/src/pages/" in normalized_path
            ):
                particle_type = "Controller"
                confidence = 85.0
            elif "BaseModel" in evidence_line or "/schemas/" in normalized_path or "/error_messages/" in normalized_path:
                particle_type = "DTO"
                confidence = 85.0
            elif "/tests/" in normalized_path or "/test/" in normalized_path:
                particle_type = "Test"
                confidence = 80.0
            elif "/config/" in normalized_path or "settings" in normalized_path:
                particle_type = "Configuration"
                confidence = 80.0
            elif "exception" in normalized_path or "error" in normalized_path:
                particle_type = "Exception"
                confidence = 80.0
            elif "/utils/" in normalized_path or "/helpers/" in normalized_path or "/common/" in normalized_path:
                particle_type = "Utility"
                confidence = 75.0
            elif "/models/" in normalized_path and "/domain/" not in normalized_path:
                particle_type = "DTO"
                confidence = 75.0
            elif "/adapters/" in normalized_path:
                particle_type = "Adapter"
                confidence = 75.0
            elif "/clients/" in normalized_path or "/external/" in normalized_path:
                particle_type = "Client"
                confidence = 75.0
            elif "/gateways/" in normalized_path:
                particle_type = "Gateway"
                confidence = 75.0

        # =============================================================================
        # TIER 2.5: LEARNED PATTERNS FROM patterns.json (80-95% confidence)
        # =============================================================================
        if particle_type is None and self.pattern_repo is not None:
            short_name = name.split(".")[-1] if "." in name else name
            
            # Try prefix patterns first
            prefix_result = self.pattern_repo.classify_by_prefix(short_name)
            if prefix_result and prefix_result[0] != "Unknown":
                particle_type = prefix_result[0]
                confidence = float(prefix_result[1])
            
            # Try suffix patterns (may override or confirm)
            suffix_result = self.pattern_repo.classify_by_suffix(short_name)
            if suffix_result and suffix_result[0] != "Unknown":
                if particle_type is None:
                    particle_type = suffix_result[0]
                    confidence = float(suffix_result[1])
                elif suffix_result[1] > confidence:
                    # Suffix has higher confidence, use it
                    particle_type = suffix_result[0]
                    confidence = float(suffix_result[1])

        # =============================================================================
        # TIER 3: NAMING CONVENTIONS (70-80% confidence)
        # =============================================================================
        if particle_type is None and symbol_kind in {"class", "interface", "type", "enum"}:
            particle_type = self._get_particle_type_by_name(name)
            if particle_type:
                confidence = 75.0

        if symbol_kind in {"function", "method"}:
            # If we get "Class.method", classify primarily by the last segment.
            short_name = name.split(".")[-1] if "." in name else name
            
            if particle_type is None:
                particle_type = self._get_function_type_by_name(short_name)
                if particle_type:
                    confidence = 70.0

            # UI components: exported PascalCase functions/components
            if particle_type is None and (
                "/ro-finance/src/components/" in normalized_path or "/ro-finance/src/pages/" in normalized_path
            ):
                if short_name[:1].isupper():
                    particle_type = "Controller"
                    confidence = 70.0

        resolved_type = normalize_type(particle_type or "Unknown")

        particle: Dict[str, Any] = {
            "type": resolved_type,
            "name": name,
            "symbol_kind": symbol_kind if symbol_kind else "unknown",
            "file_path": file_path,
            "line": line_num,
            "end_line": end_line if end_line else line_num,
            "confidence": confidence,
            "evidence": evidence_line[:200],
            # Lossless fields for code regeneration
            "body_source": body_source,
            "docstring": docstring,
            "return_type": return_type,
        }

        if parent:
            particle["parent"] = parent
        if base_classes:
            particle["base_classes"] = base_classes
        if decorators:
            particle["decorators"] = decorators
        if params:
            particle["params"] = params

        return particle

    def _get_base_class_names(self, node: ast.ClassDef) -> List[str]:
        """Extract base class names from a Python class definition."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)
            elif isinstance(base, ast.Subscript):
                # Generic types like Generic[T]
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
                    # Handle @pytest.fixture where fixture is attribute
                    parts = []
                    while isinstance(decorator, ast.Attribute):
                        parts.append(decorator.attr)
                        decorator = decorator.value
                    if isinstance(decorator, ast.Name):
                        parts.append(decorator.id)
                    decorators.append(".".join(reversed(parts)))
                elif isinstance(decorator, ast.Call):
                    # Handle @decorator(args)
                    if isinstance(decorator.func, ast.Name):
                        decorators.append(decorator.func.id)
                    elif isinstance(decorator.func, ast.Attribute):
                        # Handle @pytest.fixture(scope="module")
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
            
            # Get defaults (aligned from the end)
            defaults = args.defaults or []
            num_defaults = len(defaults)
            num_args = len(args.args)
            
            for i, arg in enumerate(args.args):
                param = {"name": arg.arg}
                
                # Type annotation
                if arg.annotation:
                    param["type"] = ast.unparse(arg.annotation)
                
                # Default value
                default_idx = i - (num_args - num_defaults)
                if default_idx >= 0 and default_idx < len(defaults):
                    param["default"] = ast.unparse(defaults[default_idx])
                
                params.append(param)
            
            # *args
            if args.vararg:
                param = {"name": f"*{args.vararg.arg}"}
                if args.vararg.annotation:
                    param["type"] = ast.unparse(args.vararg.annotation)
                params.append(param)
            
            # **kwargs
            if args.kwarg:
                param = {"name": f"**{args.kwarg.arg}"}
                if args.kwarg.annotation:
                    param["type"] = ast.unparse(args.kwarg.annotation)
                params.append(param)
        except Exception:
            pass
        return params

    def _get_docstring(self, node: Any) -> str:
        """Extract docstring from a function or class."""
        try:
            return ast.get_docstring(node) or ""
        except Exception:
            return ""

    def _get_return_type(self, node: Any) -> str:
        """Extract return type annotation."""
        try:
            if hasattr(node, "returns") and node.returns:
                return ast.unparse(node.returns)
        except Exception:
            pass
        return ""


    def _measure_python_ast_depth(self, tree: ast.AST) -> Dict[str, int]:
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

    def _extract_python_particles_ast_recursive(
        self, tree: ast.AST, file_path: str, lines: List[str]
    ) -> List[Dict]:
        """Recursive AST traversal for Python symbols (fast path)."""
        particles: List[Dict[str, Any]] = []
        class_stack: List[str] = []
        func_stack: List[str] = []

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

                base_classes = self_outer._get_base_class_names(node)
                decorators = self_outer._get_decorators(node)

                particles.append(
                    self_outer._classify_extracted_symbol(
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

                decorators = self_outer._get_decorators(node)
                
                # NEW: Extract lossless fields
                body_source = self_outer._get_function_body(node, lines)
                params = self_outer._get_function_params(node)
                docstring = self_outer._get_docstring(node)
                return_type = self_outer._get_return_type(node)

                particles.append(
                    self_outer._classify_extracted_symbol(
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

        self_outer = self
        Visitor().visit(tree)
        return particles

    def _extract_python_particles_ast_iterative(
        self, tree: ast.AST, file_path: str, lines: List[str]
    ) -> List[Dict]:
        """Iterative AST traversal for deep trees (avoids recursion limits)."""
        particles: List[Dict[str, Any]] = []
        class_stack: List[str] = []
        func_stack: List[str] = []

        def evidence_for_line(line_no: int) -> str:
            idx = max(0, int(line_no or 1) - 1)
            if idx >= len(lines):
                return ""
            return (lines[idx] or "").strip()

        stack: List[Tuple[ast.AST, str]] = [(tree, "enter")]
        while stack:
            node, state = stack.pop()

            if state == "exit":
                if isinstance(node, ast.ClassDef):
                    if class_stack:
                        class_stack.pop()
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if func_stack:
                        func_stack.pop()
                continue

            if isinstance(node, ast.ClassDef):
                class_name = getattr(node, "name", "") or ""
                line_no = getattr(node, "lineno", 0) or 0
                parent = class_stack[-1] if class_stack else (func_stack[-1] if func_stack else "")

                base_classes = self._get_base_class_names(node)
                decorators = self._get_decorators(node)

                particles.append(
                    self._classify_extracted_symbol(
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
                stack.append((node, "exit"))
                children = list(ast.iter_child_nodes(node))
                for child in reversed(children):
                    stack.append((child, "enter"))
                continue

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
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

                decorators = self._get_decorators(node)
                
                # Lossless fields
                body_source = self._get_function_body(node, lines)
                params = self._get_function_params(node)
                docstring = self._get_docstring(node)
                return_type = self._get_return_type(node)

                particles.append(
                    self._classify_extracted_symbol(
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
                stack.append((node, "exit"))
                children = list(ast.iter_child_nodes(node))
                for child in reversed(children):
                    stack.append((child, "enter"))
                continue

            children = list(ast.iter_child_nodes(node))
            for child in reversed(children):
                stack.append((child, "enter"))

        return particles

    def _extract_python_particles_ast(
        self, content: str, file_path: str, *, include_depth_metrics: bool = False
    ):
        """Extract Python particles using AST with depth-aware fallbacks."""
        try:
            tree = ast.parse(content)
        except Exception as exc:
            particles = self._extract_particles(content, "python", file_path)
            if include_depth_metrics:
                return particles, {
                    "file_path": file_path,
                    "language": "python",
                    "strategy": "regex_fallback",
                    "parse_error": str(exc),
                }
            return particles

        lines = content.splitlines()
        depth_metrics = self._measure_python_ast_depth(tree)
        depth_metrics.update(
            {
                "file_path": file_path,
                "language": "python",
                "recursion_limit": sys.getrecursionlimit(),
            }
        )

        required_limit = depth_metrics["max_depth"] + self.python_depth_margin
        depth_metrics["required_recursion_limit"] = required_limit

        original_limit = sys.getrecursionlimit()
        recursion_adjusted = None
        use_iterative = False

        if required_limit > original_limit:
            if required_limit <= self.python_recursion_hard_cap:
                sys.setrecursionlimit(required_limit)
                recursion_adjusted = required_limit
            else:
                use_iterative = True
                depth_metrics["fallback_reason"] = "max_depth_exceeds_cap"

        if recursion_adjusted:
            depth_metrics["recursion_adjusted_to"] = recursion_adjusted

        try:
            if use_iterative:
                depth_metrics["strategy"] = "iterative"
                particles = self._extract_python_particles_ast_iterative(tree, file_path, lines)
            else:
                depth_metrics["strategy"] = "recursive"
                particles = self._extract_python_particles_ast_recursive(tree, file_path, lines)
        except RecursionError:
            depth_metrics["strategy"] = "iterative"
            depth_metrics["fallback_reason"] = "recursion_error"
            particles = self._extract_python_particles_ast_iterative(tree, file_path, lines)
        finally:
            if recursion_adjusted and sys.getrecursionlimit() != original_limit:
                sys.setrecursionlimit(original_limit)

        if include_depth_metrics:
            return particles, depth_metrics
        return particles

    def _extract_function_name(self, line: str, language: str) -> Optional[str]:
        """Extract a function name from a declaration line (best-effort, regex-based)."""
        if language == 'python':
            m = re.search(r'^(?:async\s+def|def)\s+(\w+)', line)
            return m.group(1) if m else None

        if language == 'go':
            # func Name( or func (r Receiver) Name(
            m = re.search(r'^func\s+(?:\([^)]*\)\s*)?(\w+)\s*\(', line)
            return m.group(1) if m else None

        if language == 'rust':
            # fn name( or pub fn name(
            m = re.search(r'^(?:pub\s+)?fn\s+(\w+)\s*\(', line)
            return m.group(1) if m else None

        if language in {'javascript', 'typescript'}:
            # export default async function name(
            m = re.search(r'^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)\s*\(', line)
            if m:
                return m.group(1)

            # export const name = (...) => / const name = async (...) =>
            m = re.search(
                r'^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(?[^=]*=>',
                line,
            )
            if m:
                return m.group(1)

            return None

        # Java/C#/Kotlin/TS methods (best-effort): last identifier before "("
        m = re.search(r'(\w+)\s*\(', line)
        return m.group(1) if m else None

    def _get_particle_type_by_name(self, name: str) -> Optional[str]:
        """Determine particle type by naming conventions"""
        tokens = set(self._tokenize_identifier(name))
        name_lower = name.lower()

        # AggregateRoot has highest priority in naming
        if 'aggregate' in tokens and 'root' in tokens:
            return 'AggregateRoot'
        if name_lower.endswith('aggregate'):
            return 'AggregateRoot'
        
        # Events - check for Event suffix or common event patterns
        if name_lower.endswith('event'):
            return 'Event'
        if tokens & {'event', 'occurred', 'happened', 'created', 'updated', 'deleted', 'changed'}:
            # Only if it looks like an event name (past tense verbs)
            if any(name_lower.endswith(suffix) for suffix in ['created', 'updated', 'deleted', 'changed', 'placed', 'cancelled', 'completed', 'started', 'finished']):
                return 'Event'
        
        if tokens & {'entity', 'model'}:
            return 'Entity'
        elif tokens & {'repository', 'repo'}:
            return 'Repository'
        elif tokens & {'controller', 'view', 'api'}:
            return 'Controller'
        elif tokens & {'service', 'handler', 'engine', 'extractor', 'generator', 'loader'}:
            return 'Service'
        elif tokens & {'value', 'vo'}:
            return 'ValueObject'
        elif 'factory' in tokens:
            return 'Factory'
        elif tokens & {'spec', 'specification'}:
            return 'Specification'
        elif 'command' in tokens:
            return 'Command'
        elif 'query' in tokens:
            return 'Query'
        elif 'usecase' in tokens or ('use' in tokens and 'case' in tokens) or 'use_case' in name_lower:
            return 'UseCase'
        elif tokens & {'dto', 'request', 'response', 'schema'}:
            return 'DTO'
        elif tokens & {'error', 'exception'}:
            return 'Exception'
        elif tokens & {'config', 'settings', 'env'}:
            return 'Configuration'
        elif tokens & {'provider', 'module'}:
            return 'Provider'
        elif tokens & {'test', 'tests', 'spec', 'suite'}:
            return 'Test'
        elif 'utils' in tokens or 'helper' in tokens:
            return 'Utility'
        elif 'builder' in tokens:
            return 'Builder'
        elif 'adapter' in tokens:
            return 'Adapter'
        
        # NEW PATTERNS for improved coverage
        elif tokens & {'parser', 'parse', 'deserialize', 'serialize'}:
            return 'Utility'
        elif tokens & {'mapper', 'mapping', 'converter', 'convert', 'transform', 'translator'}:
            return 'Mapper'
        elif tokens & {'client', 'consumer', 'caller'}:
            return 'Client'
        elif tokens & {'gateway', 'facade', 'proxy'}:
            return 'Gateway'
        elif tokens & {'middleware', 'interceptor', 'filter'}:
            return 'Adapter'
        elif tokens & {'listener', 'watcher', 'monitor'}:
            return 'Observer'
        elif tokens & {'strategy', 'policy', 'rule'}:
            return 'Policy'
        elif tokens & {'state', 'status', 'context'}:
            return 'Entity'
        elif tokens & {'result', 'outcome', 'output'}:
            return 'DTO'

        return None

    def _get_function_type_by_name(self, name: str) -> Optional[str]:
        """Determine function particle type by naming"""
        name_lower = name.lower()
        tokens = set(self._tokenize_identifier(name))

        if tokens & {'handle', 'handler'} or name_lower.endswith('_handler'):
            return 'EventHandler'
        if tokens & {'on', 'when', 'observe', 'observer', 'listener', 'subscribe', 'subscriber'}:
            return 'Observer'

        if tokens & {'create', 'make', 'build'}:
            return 'Factory'

        if tokens & {'validate', 'check', 'verify', 'ensure', 'require'}:
            return 'Specification'

        if tokens & {'get', 'fetch', 'find', 'list', 'read', 'load'}:
            return 'Query'

        if tokens & {'save', 'commit', 'upsert', 'delete', 'write', 'sync', 'import', 'export', 'connect', 'disconnect', 'purge'}:
            return 'Command'

        if tokens & {'execute', 'run', 'start', 'stop', 'restart'}:
            return 'UseCase'

        if 'apply' in tokens:
            return 'Policy'

        if tokens & {'process', 'orchestrate'}:
            return 'DomainService'

        if tokens & {'is', 'has', 'can', 'should'}:
            return 'Specification'

        if tokens & {'setup', 'configure', 'config', 'init', 'bootstrap'}:
            return 'Service'

        # ========================
        # NEW PATTERNS FOR COVERAGE
        # ========================
        
        # Test functions (test_*, *_test)
        if name_lower.startswith('test_') or name_lower.endswith('_test'):
            return 'Test'
        if 'test' in tokens:
            return 'Test'
        
        # Private/internal functions  
        if name_lower.startswith('_') and not name_lower.startswith('__'):
            # Could be internal helper - classify by context
            pass  # Let other rules handle, but mark if nothing else matches
            
        # Validators
        if tokens & {'validate', 'validator', 'assert', 'check'}:
            return 'Validator'
            
        # Parsers and converters
        if tokens & {'parse', 'parser', 'convert', 'converter', 'deserialize', 'serialize', 'format', 'formatter'}:
            return 'Utility'
            
        # Generators and builders
        if tokens & {'generate', 'generator', 'yield'}:
            return 'Factory'
            
        # Error handling
        if tokens & {'error', 'exception', 'raise', 'fail'}:
            return 'Exception'
            
        # Callbacks and hooks
        if tokens & {'callback', 'hook', 'trigger', 'emit'}:
            return 'EventHandler'
            
        # Comparators
        if tokens & {'compare', 'equals', 'equal', 'match', 'matches', 'diff'}:
            return 'Specification'
            
        # Decorators (functions that are decorators)
        if tokens & {'decorator', 'decorate', 'wrap', 'wrapper'}:
            return 'Utility'
        
        # Async patterns
        if tokens & {'async', 'await', 'coroutine'}:
            return 'Service'
            
        # Render/display
        if tokens & {'render', 'display', 'show', 'print', 'format'}:
            return 'Utility'
            
        # Cleanup/teardown
        if tokens & {'cleanup', 'teardown', 'dispose', 'close', 'shutdown'}:
            return 'Service'

        return None

    def _detect_by_keywords(self, line: str) -> Optional[str]:
        """Detect pattern by keywords in line"""
        if any(keyword in line for keyword in ['@dataclass', 'frozen', 'immutable']):
            return 'ValueObject'
        elif any(keyword in line for keyword in ['interface', 'abstract', 'protocol']):
            return 'Service'
        elif '@' in line and any(keyword in line for keyword in ['route', 'get', 'post']):
            return 'Controller'

        return None

    def _calculate_confidence(self, name: str, line: str) -> float:
        """Calculate confidence score for detection"""
        confidence = 50.0  # Base confidence

        name_lower = name.lower()

        # Naming patterns
        if any(pattern in name_lower for pattern in ['entity', 'repository', 'service', 'controller', 'value']):
            confidence += 25.0

        # Keywords
        if any(keyword in line for keyword in ['@dataclass', 'frozen', 'immutable', 'interface', 'abstract']):
            confidence += 20.0

        return min(confidence, 100.0)

    def _extract_touchpoints(self, content: str, particles: List[Dict]) -> List[Dict]:
        """Extract universal touchpoints from content"""
        touchpoints = []

        # Define touchpoint indicators
        touchpoint_patterns = {
            'identity': [r'\b(id|uuid|identifier|key|_id)\b'],
            'state': [r'\b(property|attribute|field|member)\b'],
            'data_access': [r'\b(save|find|delete|query|persist|retrieve)\b'],
            'immutability': [r'\b(frozen|immutable|readonly|final|const)\b'],
            'validation': [r'\b(validate|check|verify|ensure|require)\b'],
            'coordination': [r'\b(coordinate|manage|orchestrate|mediate)\b']
        }

        for touchpoint, patterns in touchpoint_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    touchpoints.append({
                        'type': touchpoint,
                        'evidence': match.group(),
                        'line': line_num,
                        'confidence': 75.0
                    })

        return touchpoints

    def _extract_raw_imports(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract raw import statements for dependency analysis."""
        if language == 'python':
            return self._extract_python_imports(content)
        if language in {'javascript', 'typescript'}:
            return self._extract_js_ts_imports(content)
        if language in {'java', 'kotlin'}:
            return self._extract_java_like_imports(content)
        if language == 'c_sharp':
            return self._extract_csharp_imports(content)
        if language == 'go':
            return self._extract_go_imports(content)
        if language == 'rust':
            return self._extract_rust_imports(content)
        if language == 'ruby':
            return self._extract_ruby_imports(content)
        if language == 'php':
            return self._extract_php_imports(content)
        return []

    def _extract_python_imports(self, content: str) -> List[Dict[str, Any]]:
        imports: List[Dict[str, Any]] = []
        try:
            tree = ast.parse(content)
        except Exception:
            return imports

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name:
                        imports.append(
                            {
                                'kind': 'import',
                                'target': alias.name,
                                'line': getattr(node, 'lineno', 0) or 0,
                                'is_relative': False,
                                'level': 0,
                            }
                        )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                level = getattr(node, 'level', 0) or 0
                imports.append(
                    {
                        'kind': 'from_import',
                        'target': module,
                        'line': getattr(node, 'lineno', 0) or 0,
                        'is_relative': bool(level),
                        'level': level,
                    }
                )

        return imports

    def _extract_js_ts_imports(self, content: str) -> List[Dict[str, Any]]:
        imports: List[Dict[str, Any]] = []
        in_block_comment = False

        for i, raw in enumerate(content.splitlines(), 1):
            line = raw
            stripped = line.strip()

            if in_block_comment:
                if '*/' in stripped:
                    in_block_comment = False
                continue
            if stripped.startswith('/*'):
                in_block_comment = True
                continue
            if stripped.startswith('//'):
                continue

            # import ... from 'x'  | import 'x'
            m = re.match(r'^\s*import\s+(?:type\s+)?(?:.+?\s+from\s+)?[\'"]([^\'"]+)[\'"]', line)
            if m:
                target = m.group(1)
                imports.append(
                    {
                        'kind': 'import',
                        'target': target,
                        'line': i,
                        'is_relative': target.startswith(('.', '/')),
                        'level': 0,
                    }
                )
                continue

            # require('x')
            for m in re.finditer(r'\brequire\(\s*[\'"]([^\'"]+)[\'"]\s*\)', line):
                target = m.group(1)
                imports.append(
                    {
                        'kind': 'require',
                        'target': target,
                        'line': i,
                        'is_relative': target.startswith(('.', '/')),
                        'level': 0,
                    }
                )

            # dynamic import('x')
            for m in re.finditer(r'\bimport\(\s*[\'"]([^\'"]+)[\'"]\s*\)', line):
                target = m.group(1)
                imports.append(
                    {
                        'kind': 'dynamic_import',
                        'target': target,
                        'line': i,
                        'is_relative': target.startswith(('.', '/')),
                        'level': 0,
                    }
                )

        return imports

    def _extract_java_like_imports(self, content: str) -> List[Dict[str, Any]]:
        imports: List[Dict[str, Any]] = []
        for i, line in enumerate(content.splitlines(), 1):
            m = re.match(r'^\s*import\s+([a-zA-Z0-9_.*]+)\s*;', line)
            if not m:
                continue
            target = m.group(1)
            imports.append({'kind': 'import', 'target': target, 'line': i, 'is_relative': False, 'level': 0})
        return imports

    def _extract_csharp_imports(self, content: str) -> List[Dict[str, Any]]:
        imports: List[Dict[str, Any]] = []
        for i, line in enumerate(content.splitlines(), 1):
            if 'using (' in line or line.strip().startswith('using ('):
                continue
            m = re.match(r'^\s*using\s+([a-zA-Z0-9_.]+)\s*;', line)
            if not m:
                continue
            target = m.group(1)
            imports.append({'kind': 'using', 'target': target, 'line': i, 'is_relative': False, 'level': 0})
        return imports

    def _extract_go_imports(self, content: str) -> List[Dict[str, Any]]:
        imports: List[Dict[str, Any]] = []
        in_block = False

        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith('import ('):
                in_block = True
                continue
            if in_block:
                if stripped.startswith(')'):
                    in_block = False
                    continue
                m = re.search(r'\"([^\"]+)\"', stripped)
                if m:
                    target = m.group(1)
                    imports.append({'kind': 'import', 'target': target, 'line': i, 'is_relative': False, 'level': 0})
                continue

            m = re.match(r'^\s*import\s+\"([^\"]+)\"', line)
            if m:
                target = m.group(1)
                imports.append({'kind': 'import', 'target': target, 'line': i, 'is_relative': False, 'level': 0})

        return imports

    def _extract_rust_imports(self, content: str) -> List[Dict[str, Any]]:
        imports: List[Dict[str, Any]] = []
        for i, line in enumerate(content.splitlines(), 1):
            m = re.match(r'^\s*use\s+([^;]+);', line)
            if not m:
                continue
            target = m.group(1).strip()
            imports.append({'kind': 'use', 'target': target, 'line': i, 'is_relative': False, 'level': 0})
        return imports

    def _extract_ruby_imports(self, content: str) -> List[Dict[str, Any]]:
        imports: List[Dict[str, Any]] = []
        for i, line in enumerate(content.splitlines(), 1):
            m = re.match(r'^\s*require(_relative)?\s+[\'"]([^\'"]+)[\'"]', line)
            if not m:
                continue
            target = m.group(2)
            imports.append(
                {
                    'kind': 'require_relative' if m.group(1) else 'require',
                    'target': target,
                    'line': i,
                    'is_relative': bool(m.group(1)) or target.startswith(('.', '/')),
                    'level': 0,
                }
            )
        return imports

    def _extract_php_imports(self, content: str) -> List[Dict[str, Any]]:
        imports: List[Dict[str, Any]] = []
        for i, line in enumerate(content.splitlines(), 1):
            m = re.match(r'^\s*use\s+([^;]+);', line)
            if m:
                target = m.group(1).strip()
                imports.append({'kind': 'use', 'target': target, 'line': i, 'is_relative': False, 'level': 0})
                continue
            m = re.match(r'^\s*(require|include)(_once)?\s*\(?\s*[\'"]([^\'"]+)[\'"]\s*\)?\s*;', line)
            if m:
                target = m.group(3)
                imports.append({'kind': m.group(1), 'target': target, 'line': i, 'is_relative': target.startswith(('.', '/')), 'level': 0})
        return imports

    def _fallback_analysis(self, file_path: str) -> Dict[str, Any]:
        """Fallback analysis for unsupported languages"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return {'particles': [], 'touchpoints': [], 'language': 'unknown'}

        # Basic regex analysis
        particles = []
        touchpoints = []

        # Simple class-like detection
        for i, line in enumerate(content.split('\n'), 1):
            if re.search(r'\b(class|interface|struct|type)\s+\w+', line):
                particles.append({
                    'type': 'Unknown',
                    'name': 'detected_pattern',
                    'line': i,
                    'confidence': 30.0,
                    'evidence': line.strip()
                })

        return {
            'file_path': file_path,
            'language': 'unknown',
            'particles': particles,
            'touchpoints': touchpoints,
            'lines_analyzed': len(content.split('\n')),
            'chars_analyzed': len(content)
        }

    def _summarize_depth_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate depth metrics across files."""
        if not metrics:
            return {}

        depths = [m.get("max_depth", 0) for m in metrics if m.get("max_depth") is not None]
        nodes = [m.get("node_count", 0) for m in metrics if m.get("node_count") is not None]
        required_limits = [
            m.get("required_recursion_limit", 0)
            for m in metrics
            if m.get("required_recursion_limit") is not None
        ]
        adjusted_limits = [
            m.get("recursion_adjusted_to", 0)
            for m in metrics
            if m.get("recursion_adjusted_to") is not None
        ]

        depths_sorted = sorted(depths)
        p95_depth = 0
        if depths_sorted:
            idx = int(0.95 * (len(depths_sorted) - 1))
            p95_depth = depths_sorted[idx]

        strategy_counts = Counter(
            m.get("strategy", "unknown") for m in metrics if m.get("strategy")
        )
        fallback_counts = Counter(
            m.get("fallback_reason", "unknown") for m in metrics if m.get("fallback_reason")
        )

        deepest_files = sorted(
            (
                {
                    "file_path": m.get("file_path", ""),
                    "max_depth": m.get("max_depth", 0),
                    "node_count": m.get("node_count", 0),
                }
                for m in metrics
            ),
            key=lambda x: x["max_depth"],
            reverse=True,
        )[:5]

        return {
            "scope": "python_ast",
            "files_measured": len(depths),
            "max_ast_depth": max(depths) if depths else 0,
            "avg_ast_depth": sum(depths) / len(depths) if depths else 0,
            "p95_ast_depth": p95_depth,
            "max_ast_nodes": max(nodes) if nodes else 0,
            "avg_ast_nodes": sum(nodes) / len(nodes) if nodes else 0,
            "max_required_recursion_limit": max(required_limits) if required_limits else 0,
            "max_recursion_adjusted_to": max(adjusted_limits) if adjusted_limits else 0,
            "strategy_counts": dict(strategy_counts),
            "fallback_reasons": dict(fallback_counts),
            "deepest_files": deepest_files,
        }

    def analyze_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Analyze all supported files in directory"""
        results: List[Dict[str, Any]] = []
        depth_metrics: List[Dict[str, Any]] = []

        # Prefer TypeScript AST extraction for JS/TS when available (richer symbol mapping).
        ts_results = self._extract_js_ts_directory_with_typescript(directory_path)
        ts_files_abs = {Path(r.get("file_path", "")).resolve() for r in ts_results if r.get("file_path")}
        results.extend(ts_results)

        for root, dirs, files in os.walk(directory_path):
            # Skip common ignore directories
            dirs[:] = [
                d
                for d in dirs
                if d
                not in [
                    '.git',
                    '__pycache__',
                    'node_modules',
                    'venv',
                    '.venv',
                    'dist',
                    'build',
                    'coverage',
                    '.next',
                    '.turbo',
                    '.cache',
                ]
            ]

            for file in files:
                if Path(file).suffix in self.supported_languages:
                    file_path = os.path.join(root, file)
                    # Skip JS/TS files already handled by TypeScript extractor.
                    if Path(file_path).resolve() in ts_files_abs:
                        continue
                    result = self.analyze_file(file_path)
                    if result.get("depth_metrics"):
                        depth_metrics.append(result["depth_metrics"])
                    results.append(result)

        self.depth_summary = self._summarize_depth_metrics(depth_metrics)
        return results

    def _extract_js_ts_directory_with_typescript(self, directory_path: str) -> List[Dict[str, Any]]:
        """Extract JS/TS symbols using the TypeScript compiler API (via Node), when available."""
        if not self._ts_symbol_extractor.exists():
            return []

        try:
            proc = subprocess.run(
                ["node", str(self._ts_symbol_extractor), directory_path],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except Exception:
            return []

        if proc.returncode != 0 or not proc.stdout:
            return []

        try:
            payload = json.loads(proc.stdout)
        except Exception:
            return []

        if not payload.get("ok"):
            return []

        out: List[Dict[str, Any]] = []
        for f in payload.get("files", []) or []:
            file_path = str(f.get("file_path") or "")
            language = str(f.get("language") or "unknown")
            if language not in {"javascript", "typescript"} or not file_path:
                continue

            particles: List[Dict[str, Any]] = []
            for sym in f.get("particles", []) or []:
                name = str(sym.get("name") or "")
                symbol_kind = str(sym.get("symbol_kind") or "unknown")
                line_num = int(sym.get("line") or 0)
                evidence = str(sym.get("evidence") or "")
                parent = str(sym.get("parent") or "")
                particles.append(
                    self._classify_extracted_symbol(
                        name=name,
                        symbol_kind=symbol_kind,
                        file_path=file_path,
                        line_num=line_num,
                        evidence=evidence,
                        parent=parent,
                    )
                )

            out.append(
                {
                    "file_path": file_path,
                    "language": language,
                    "particles": particles,
                    "touchpoints": f.get("touchpoints") or [],
                    "raw_imports": f.get("raw_imports") or [],
                    "lines_analyzed": int(f.get("lines_analyzed") or 0),
                    "chars_analyzed": int(f.get("chars_analyzed") or 0),
                }
            )

        return out
