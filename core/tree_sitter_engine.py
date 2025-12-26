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

# NEW: Import Delegated Components
try:
    from core.classification.universal_classifier import UniversalClassifier
    from core.parser.python_extractor import PythonASTExtractor
except ImportError:
    # Try local import (if running from core)
    try:
        from classification.universal_classifier import UniversalClassifier
        from parser.python_extractor import PythonASTExtractor
    except ImportError:
        # Fallback for direct script execution without package structure
        sys.path.append(str(Path(__file__).parent))
        from classification.universal_classifier import UniversalClassifier
        from parser.python_extractor import PythonASTExtractor


class TreeSitterUniversalEngine:
    """
    Universal Tree-sitter engine for cross-language pattern detection.
    
    REFACTORED (2025-12-24): Now acts as a Facade to:
    - UniversalClassifier (classification logic)
    - PythonASTExtractor (parsing logic)
    """

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
        try:
            with open(patterns_file) as f:
                self.patterns = json.load(f)
        except Exception:
            self.patterns = {}

        # INITIALIZE DELEGATES
        self.classifier = UniversalClassifier()
        self.python_extractor = PythonASTExtractor(self.classifier)

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
            # DELEGATE to PythonASTExtractor
            particles, depth_metrics = self.python_extractor.extract_particles_ast(
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
        
    def analyze_directory(self, dir_path: str, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """Analyze all supported files in a directory."""
        results = []
        path = Path(dir_path)
        
        if not path.exists():
            return []
            
        for root, _, files in os.walk(path):
            if any(p in str(Path(root)) for p in ['.git', '__pycache__', 'node_modules', 'venv']):
                continue
                
            for file in files:
                file_path = str(Path(root) / file)
                ext = Path(file).suffix
                
                if extensions and ext not in extensions:
                    continue
                    
                if ext in self.supported_languages:
                    results.append(self.analyze_file(file_path))
                    
        return results

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
                    # DELEGATE to Classifier
                    particle = self.classifier.classify_class_pattern(line, i, file_path)
                    if particle:
                        particles.append(particle)
                    continue

                if re.match(r'^\s*interface\s+\w+', line) or re.match(r'^\s*type\s+\w+\s*=', line):
                    # DELEGATE to Classifier
                    particle = self.classifier.classify_class_pattern(line, i, file_path)
                    if particle:
                        particles.append(particle)
                    continue

                if re.match(r'^\s*(export\s+)?(default\s+)?(async\s+)?function\s+\w+', line) or re.match(
                    r'^\s*(export\s+)?(const|let|var)\s+\w+\s*=\s*(async\s*)?\(?[^=]*=>',
                    line,
                ):
                    # DELEGATE to Classifier
                    particle = self.classifier.classify_function_pattern(line, i, file_path, language)
                    if particle:
                        particles.append(particle)
                    continue

            # Other languages: keep permissive matching (indentation is less meaningful)
            if re.match(r'^\s*(class|public class|private class|interface|type)\s+\w+', line):
                # DELEGATE to Classifier
                particle = self.classifier.classify_class_pattern(line, i, file_path)
                if particle:
                    particles.append(particle)
                continue

            if re.match(r'^\s*(async\s+def|def|public|private|protected|static|func|fn)\s+\w+', line):
                # DELEGATE to Classifier
                particle = self.classifier.classify_function_pattern(line, i, file_path, language)
                if particle:
                    particles.append(particle)

        return particles

    # === DELEGATED METHODS (Required for compatibility with tests/external code) ===

    def _classify_class_pattern(self, line: str, line_num: int, file_path: str) -> Optional[Dict]:
        """Delegate to classifier (compat wrapper)."""
        return self.classifier.classify_class_pattern(line, line_num, file_path)

    def _classify_function_pattern(self, line: str, line_num: int, file_path: str, language: str) -> Optional[Dict]:
        """Delegate to classifier (compat wrapper)."""
        return self.classifier.classify_function_pattern(line, line_num, file_path, language)

    def _classify_extracted_symbol(self, **kwargs) -> Dict[str, Any]:
        """Delegate to classifier (compat wrapper)."""
        return self.classifier.classify_extracted_symbol(**kwargs)

    # === Original Methods (Kept for now if self-contained) ===

    def _extract_touchpoints(self, content: str, particles: List[Dict]) -> List[Dict[str, str]]:
        """Extract touchpoints (API endpoints, CLI commands, etc)."""
        touchpoints = []
        # Simplified logic
        for p in particles:
            if p.get('type') == 'Controller' or p.get('type') == 'Command':
                touchpoints.append({
                    "type": p['type'],
                    "name": p['name'],
                    "file_path": p.get('file_path', ''),
                    "line": p.get('line', 0)
                })
        return touchpoints

    def _extract_raw_imports(self, content: str, language: str) -> List[str]:
        """Extract raw import statements."""
        imports = []
        if language == 'python':
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            imports.append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for n in node.names:
                            imports.append(f"{module}.{n.name}")
            except:
                pass
        return imports

    def _fallback_analysis(self, file_path: str) -> Dict[str, Any]:
        """Minimal fallback for unsupported files."""
        return {
            'file_path': file_path,
            'language': 'unknown',
            'particles': [],
            'touchpoints': [],
            'raw_imports': [],
            'lines_analyzed': 0,
            'chars_analyzed': 0
        }

    # === DEPRECATED / REMOVED METHODS (Moved to Delegates) ===
    # _get_particle_type_by_name -> classifier
    # _detect_by_keywords -> classifier
    # _calculate_confidence -> classifier
    # _extract_function_name -> classifier
    # _get_base_class_names -> extractor
    # _get_decorators -> extractor
    # _get_function_body -> extractor
    # _get_function_params -> extractor
    # _get_docstring -> extractor
    # _get_return_type -> extractor
    # _measure_python_ast_depth -> extractor
    # _extract_python_particles_ast_recursive -> extractor
    # _extract_python_particles_ast_iterative -> extractor
    
    # Minimal stubs if absolutely needed by obscure tests, otherwise removed.
    def _extract_python_particles_ast(self, content, file_path, include_depth_metrics=False):
        return self.python_extractor.extract_particles_ast(content, file_path, include_depth_metrics)

