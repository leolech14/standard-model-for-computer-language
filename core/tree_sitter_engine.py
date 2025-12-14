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
from pathlib import Path
from typing import Dict, List, Any, Optional

class TreeSitterUniversalEngine:
    """Universal Tree-sitter engine for cross-language pattern detection"""

    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.java': 'java',
            '.ts': 'typescript',
            '.js': 'javascript',
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

        # Parse with Tree-sitter (simplified for minimal version)
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
        particles = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Python: restrict to top-level definitions to avoid counting nested helpers (e.g., Pydantic Config)
            if language == 'python':
                if re.match(r'^class\s+\w+', line):
                    particle = self._classify_class_pattern(line, i, file_path)
                    if particle:
                        particles.append(particle)
                elif re.match(r'^(async\s+def|def)\s+\w+', line):
                    particle = self._classify_function_pattern(line, i, file_path)
                    if particle:
                        particles.append(particle)
                continue

            # Other languages: keep permissive matching (indentation is less meaningful)
            if re.match(r'^\s*(class|public class|private class|interface|type)\s+\w+', line):
                particle = self._classify_class_pattern(line, i, file_path)
                if particle:
                    particles.append(particle)
                continue

            if re.match(r'^\s*(def|public|private|protected|func)\s+\w+', line):
                particle = self._classify_function_pattern(line, i, file_path)
                if particle and particle.get('type') != 'Unknown':
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

    def _classify_function_pattern(self, line: str, line_num: int, file_path: str) -> Optional[Dict]:
        """Classify function-like patterns"""
        line_stripped = line.strip()

        # Extract name
        name_match = re.search(r'(?:async\s+def|def|func)\s+(\w+)', line_stripped)
        if not name_match:
            return None

        func_name = name_match.group(1)

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

        if name.startswith('handle_') or name.endswith('_handler'):
            return 'EventHandler'
        elif name.startswith('on_') or name.startswith('when_'):
            return 'Observer'
        elif name.startswith('create_') or name.startswith('make_'):
            return 'Factory'
        elif 'validate' in name_lower or 'check' in name_lower:
            return 'Specification'
        elif name.startswith('execute_') or name.startswith('run_'):
            return 'UseCase'
        elif 'apply' in name_lower:
            return 'Policy'
        elif name.startswith('process_'):
            return 'DomainService'
        elif name.startswith('get_') or name.startswith('fetch_') or name.startswith('find_'):
            return 'Query'
        elif name.startswith('to_') or name.startswith('from_') or name.startswith('as_'):
            return 'Converter'
        elif name.startswith('is_') or name.startswith('has_') or name.startswith('can_'):
            return 'Predicate'
        elif name.startswith('test_'):
            return 'Test'
        elif 'configure' in name_lower or 'setup' in name_lower:
            return 'Configuration'

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
        results = []

        for root, dirs, files in os.walk(directory_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv']]

            for file in files:
                if Path(file).suffix in self.supported_languages:
                    file_path = os.path.join(root, file)
                    result = self.analyze_file(file_path)
                    results.append(result)

        return results
