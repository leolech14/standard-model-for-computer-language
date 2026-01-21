#!/usr/bin/env python3
"""
PATTERN MATCHER - Tree-sitter based atom detection.

Uses patterns.scm queries to detect code atoms structurally.
This replaces regex-based heuristics with precise AST pattern matching.

Usage:
    from src.core.pattern_matcher import PatternMatcher

    matcher = PatternMatcher()
    atoms = matcher.detect_atoms(tree, source, 'python')

    for atom in atoms:
        print(f"{atom['type']}: {atom['name']} (confidence: {atom['confidence']})")
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Lazy imports for tree-sitter
_tree_sitter = None
_languages = {}


def _get_tree_sitter():
    """Lazy load tree-sitter module."""
    global _tree_sitter
    if _tree_sitter is None:
        import tree_sitter
        _tree_sitter = tree_sitter
    return _tree_sitter


def _get_language(lang: str):
    """Lazy load language module."""
    global _languages
    if lang not in _languages:
        if lang == 'python':
            import tree_sitter_python
            _languages[lang] = tree_sitter_python.language()
        elif lang in ('javascript', 'typescript'):
            import tree_sitter_javascript
            _languages[lang] = tree_sitter_javascript.language()
        else:
            return None
    return _languages[lang]


@dataclass
class AtomMatch:
    """Represents a detected atom from pattern matching."""
    type: str                    # e.g., 'entity', 'service', 'repository'
    name: str                    # The captured name
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    confidence: float           # 0.0 to 1.0
    evidence: str               # Matching pattern or source snippet
    capture_name: str           # The full capture name from query


# Confidence scores by atom type (based on pattern reliability)
ATOM_CONFIDENCE = {
    'entity': 0.90,
    'repository': 0.92,
    'service': 0.85,
    'controller': 0.88,
    'handler': 0.82,
    'factory': 0.90,
    'dto': 0.88,
    'valueobject': 0.92,
    'validator': 0.85,
    'mapper': 0.80,
    'query': 0.75,
    'command': 0.75,
    'test': 0.95,
    'fixture': 0.90,
    'exception': 0.95,
    'configuration': 0.88,
    'middleware': 0.85,
    'utility': 0.70,
    'internal': 0.65,
    'component': 0.92,
    'hook': 0.95,
    'store': 0.88,
    'context': 0.90,
    'provider': 0.85,
    'reducer': 0.90,
}


class PatternMatcher:
    """
    Tree-sitter pattern matcher for atom detection.

    Loads patterns.scm files and runs queries against parsed trees
    to detect code atoms structurally.
    """

    def __init__(self, queries_dir: Optional[str] = None):
        """
        Initialize pattern matcher.

        Args:
            queries_dir: Path to queries directory. Defaults to src/core/queries/
        """
        if queries_dir is None:
            queries_dir = Path(__file__).parent / 'queries'
        self.queries_dir = Path(queries_dir)
        self._pattern_cache: Dict[str, Any] = {}
        self._parser_cache: Dict[str, Any] = {}

    def _get_parser(self, language: str):
        """Get or create parser for language."""
        if language not in self._parser_cache:
            ts = _get_tree_sitter()
            lang = _get_language(language)
            if lang is None:
                return None
            parser = ts.Parser()
            parser.language = ts.Language(lang)
            self._parser_cache[language] = parser
        return self._parser_cache[language]

    def _load_patterns(self, language: str) -> Optional[Any]:
        """Load patterns.scm for a language."""
        if language in self._pattern_cache:
            return self._pattern_cache[language]

        # Map language to directory
        lang_dir = 'javascript' if language == 'typescript' else language
        pattern_path = self.queries_dir / lang_dir / 'patterns.scm'

        if not pattern_path.exists():
            self._pattern_cache[language] = None
            return None

        try:
            ts = _get_tree_sitter()
            lang = _get_language(language)
            if lang is None:
                return None

            query_text = pattern_path.read_text()
            # Use the Query constructor with Language object
            query = ts.Query(ts.Language(lang), query_text)
            self._pattern_cache[language] = query
            return query
        except Exception as e:
            print(f"Warning: Failed to load patterns for {language}: {e}")
            self._pattern_cache[language] = None
            return None

    def detect_atoms(self, tree, source: bytes, language: str) -> List[AtomMatch]:
        """
        Detect atoms in a parsed tree.

        Args:
            tree: tree-sitter Tree object
            source: Source code as bytes
            language: Language name (python, javascript, typescript)

        Returns:
            List of AtomMatch objects
        """
        query = self._load_patterns(language)
        if query is None:
            return []

        atoms = []
        seen = set()  # Track seen (type, name, line) to avoid duplicates

        try:
            ts = _get_tree_sitter()
            cursor = ts.QueryCursor(query)
            captures = cursor.captures(tree.root_node)

            # captures is a dict: { capture_name: [nodes] }
            for capture_name, nodes in captures.items():
                # Parse capture name: @atom.<type>.name or @atom.<type>
                if not capture_name.startswith('atom.'):
                    continue

                parts = capture_name.split('.')
                if len(parts) < 2:
                    continue

                atom_type = parts[1]  # e.g., 'entity', 'service'

                # Skip if this is a pattern match helper (starts with _)
                if atom_type.startswith('_'):
                    continue

                for node in nodes:
                    # Get the name from the node
                    name = source[node.start_byte:node.end_byte].decode('utf8', errors='replace')

                    # Clean up string literals (remove quotes)
                    if name.startswith('"') or name.startswith("'"):
                        name = name[1:-1] if len(name) > 2 else name

                    # Create unique key
                    key = (atom_type, name, node.start_point[0])
                    if key in seen:
                        continue
                    seen.add(key)

                    # Get confidence
                    confidence = ATOM_CONFIDENCE.get(atom_type, 0.70)

                    # Create match
                    atom = AtomMatch(
                        type=atom_type,
                        name=name,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        start_byte=node.start_byte,
                        end_byte=node.end_byte,
                        confidence=confidence,
                        evidence=f"Pattern: @{capture_name}",
                        capture_name=capture_name,
                    )
                    atoms.append(atom)

        except Exception as e:
            print(f"Warning: Pattern matching failed: {e}")

        return atoms

    def detect_atoms_in_code(self, code: str, language: str) -> List[AtomMatch]:
        """
        Convenience method to detect atoms in source code string.

        Args:
            code: Source code as string
            language: Language name

        Returns:
            List of AtomMatch objects
        """
        parser = self._get_parser(language)
        if parser is None:
            return []

        source = bytes(code, 'utf8')
        tree = parser.parse(source)
        return self.detect_atoms(tree, source, language)

    def get_atom_summary(self, atoms: List[AtomMatch]) -> Dict[str, int]:
        """Get count of each atom type."""
        summary = {}
        for atom in atoms:
            summary[atom.type] = summary.get(atom.type, 0) + 1
        return summary


def detect_atoms(tree, source: bytes, language: str) -> List[AtomMatch]:
    """
    Module-level function to detect atoms.

    Args:
        tree: tree-sitter Tree object
        source: Source code as bytes
        language: Language name

    Returns:
        List of AtomMatch objects
    """
    matcher = PatternMatcher()
    return matcher.detect_atoms(tree, source, language)


def detect_atoms_in_file(file_path: str) -> List[AtomMatch]:
    """
    Detect atoms in a file.

    Args:
        file_path: Path to source file

    Returns:
        List of AtomMatch objects
    """
    path = Path(file_path)
    if not path.exists():
        return []

    # Determine language from extension
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
    }
    language = ext_map.get(path.suffix.lower())
    if language is None:
        return []

    code = path.read_text()
    matcher = PatternMatcher()
    return matcher.detect_atoms_in_code(code, language)


if __name__ == '__main__':
    # Test with sample code
    python_code = '''
class UserRepository:
    def get(self, id):
        return self.db.find(id)

    def save(self, user):
        self.db.insert(user)

class UserService:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, user_id):
        return self.repo.get(user_id)

def validate_email(email):
    if '@' not in email:
        raise ValueError("Invalid email")
    return True

def create_user(name, email):
    return {"name": name, "email": email}

class EmailError(Exception):
    pass

def test_user_creation():
    user = create_user("test", "test@example.com")
    assert user["name"] == "test"
'''

    print("=" * 60)
    print("PATTERN MATCHER TEST")
    print("=" * 60)

    matcher = PatternMatcher()
    atoms = matcher.detect_atoms_in_code(python_code, 'python')

    print(f"\nDetected {len(atoms)} atoms:\n")
    for atom in atoms:
        print(f"  [{atom.type:15}] {atom.name:25} (line {atom.start_line}, conf: {atom.confidence:.0%})")

    print(f"\nSummary: {matcher.get_atom_summary(atoms)}")
