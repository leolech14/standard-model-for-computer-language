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
from pathlib import Path
from typing import Dict, List, Any, Optional

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

        self._ts_symbol_extractor = (Path(__file__).parent.parent / "tools" / "ts_symbol_extractor.cjs").resolve()

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
        particles = self._extract_particles(content, language, file_path)
        touchpoints = self._extract_touchpoints(content, particles)
        raw_imports = self._extract_raw_imports(content, language)

        return {
            'file_path': file_path,
            'language': language,
            'particles': particles,
            'touchpoints': touchpoints,
            'raw_imports': raw_imports,
            'lines_analyzed': len(content.split('\n')),
            'chars_analyzed': len(content)
        }

    def _extract_particles(self, content: str, language: str, file_path: str) -> List[Dict]:
        """Extract particles using universal pattern matching"""
        if language == 'python':
            return self._extract_python_particles_ast(content, file_path)

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
    ) -> Dict[str, Any]:
        evidence_line = (evidence or "").strip()

        normalized_path = file_path.replace("\\", "/").lower()
        particle_type: Optional[str] = None

        if symbol_kind in {"class", "interface", "type", "enum"}:
            # Strong location signals (DDD/Clean folders, or UI layers).
            if "/domain/" in normalized_path and "/entities/" in normalized_path:
                particle_type = "Entity"
            elif "/domain/" in normalized_path and ("/value_objects/" in normalized_path or "/valueobjects/" in normalized_path):
                particle_type = "ValueObject"
            elif "/domain/" in normalized_path and ("/services/" in normalized_path or "/domain_services/" in normalized_path):
                particle_type = "DomainService"
            elif "/domain/" in normalized_path and "/repositories/" in normalized_path:
                particle_type = "Repository"
            elif "/infrastructure/" in normalized_path and "repository" in name.lower():
                particle_type = "RepositoryImpl"
            elif (
                "/presentation/" in normalized_path
                or "/controllers/" in normalized_path
                or "/api/" in normalized_path
                or "/ro-finance/src/components/" in normalized_path
                or "/ro-finance/src/pages/" in normalized_path
            ):
                particle_type = "Controller"
            elif "BaseModel" in evidence_line or "/schemas/" in normalized_path or "/error_messages/" in normalized_path:
                particle_type = "DTO"
            elif "/tests/" in normalized_path or "/test/" in normalized_path:
                particle_type = "Test"
            elif "/config/" in normalized_path or "settings" in normalized_path:
                particle_type = "Configuration"
            elif "exception" in normalized_path or "error" in normalized_path:
                particle_type = "Exception"

            # Naming conventions fallback.
            if particle_type is None:
                particle_type = self._get_particle_type_by_name(name)

        elif symbol_kind in {"function", "method"}:
            # If we get "Class.method", classify primarily by the last segment.
            short_name = name.split(".")[-1] if "." in name else name
            particle_type = self._get_function_type_by_name(short_name)

            # UI components: exported PascalCase functions/components
            if particle_type is None and (
                "/ro-finance/src/components/" in normalized_path or "/ro-finance/src/pages/" in normalized_path
            ):
                if short_name[:1].isupper():
                    particle_type = "Controller"

        resolved_type = particle_type or "Unknown"
        confidence = self._calculate_confidence(name, evidence_line) if particle_type else 30.0

        particle: Dict[str, Any] = {
            "type": resolved_type,
            "name": name,
            "symbol_kind": symbol_kind if symbol_kind else "unknown",
            "file_path": file_path,
            "line": line_num,
            "confidence": confidence,
            "evidence": evidence_line[:200],
        }

        if parent:
            particle["parent"] = parent

        return particle

    def _extract_python_particles_ast(self, content: str, file_path: str) -> List[Dict]:
        """Extract Python particles using `ast` for accurate nested/class method detection."""
        try:
            tree = ast.parse(content)
        except Exception:
            return []

        lines = content.splitlines()
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
                particles.append(
                    self_outer._classify_extracted_symbol(
                        name=class_name,
                        symbol_kind="class",
                        file_path=file_path,
                        line_num=line_no,
                        evidence=evidence_for_line(line_no),
                        parent=parent,
                    )
                )

                class_stack.append(class_name)
                self.generic_visit(node)
                class_stack.pop()

            def visit_FunctionDef(self, node: ast.FunctionDef):
                func_name = getattr(node, "name", "") or ""
                line_no = getattr(node, "lineno", 0) or 0
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

                particles.append(
                    self_outer._classify_extracted_symbol(
                        name=full_name,
                        symbol_kind=kind,
                        file_path=file_path,
                        line_num=line_no,
                        evidence=evidence_for_line(line_no),
                        parent=parent,
                    )
                )

                func_stack.append(func_name)
                self.generic_visit(node)
                func_stack.pop()

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
                # Reuse FunctionDef logic
                self.visit_FunctionDef(node)  # type: ignore[arg-type]

        self_outer = self
        Visitor().visit(tree)

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

        if tokens & {'entity', 'model', 'aggregate'}:
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
        elif 'query' in tokens or 'get' in tokens:
            return 'Query'
        elif 'usecase' in tokens or ('use' in tokens and 'case' in tokens) or 'use_case' in name.lower():
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

    def analyze_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Analyze all supported files in directory"""
        results: List[Dict[str, Any]] = []

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
                    results.append(result)

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
