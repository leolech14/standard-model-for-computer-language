#!/usr/bin/env python3
"""
Query Loader for Tree-sitter Queries

Loads and caches .scm query files for tree-sitter parsing.
Follows the ProfileLoader pattern for consistency.

Usage:
    from src.core.queries import get_query_loader, QueryLoader

    loader = get_query_loader()
    symbols_query = loader.load_query('python', 'symbols')
    locals_query = loader.load_query('python', 'locals')

Query Organization:
    queries/
    ├── __init__.py (this file)
    ├── python/
    │   ├── symbols.scm    # Function, class, method detection
    │   └── locals.scm     # Scope analysis (@local.*)
    ├── javascript/
    │   ├── symbols.scm
    │   └── locals.scm
    ├── typescript/
    │   └── symbols.scm    # Inherits from javascript
    ├── go/
    │   └── symbols.scm
    ├── rust/
    │   └── symbols.scm
    └── _fallback/
        └── symbols.scm    # Generic fallback
"""

from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, field


@dataclass
class QueryBundle:
    """A bundle of related queries for a language."""
    language: str
    symbols: Optional[str] = None      # Symbol extraction query
    locals: Optional[str] = None       # Scope/locals query
    highlights: Optional[str] = None   # Syntax highlighting query
    injections: Optional[str] = None   # Language injection query
    patterns: Optional[str] = None     # Pattern detection query
    _raw_files: Dict[str, str] = field(default_factory=dict)

    def has_query(self, query_type: str) -> bool:
        """Check if a query type is available."""
        return getattr(self, query_type, None) is not None

    def get_query(self, query_type: str) -> Optional[str]:
        """Get a query by type name."""
        return getattr(self, query_type, None)


class QueryLoader:
    """Loads and caches tree-sitter query files (.scm)."""

    # Standard query types
    QUERY_TYPES = ['symbols', 'locals', 'highlights', 'injections', 'patterns']

    # Language aliases (multiple extensions map to same queries)
    LANGUAGE_ALIASES = {
        'tsx': 'typescript',
        'jsx': 'javascript',
    }

    # Language inheritance (child inherits from parent if missing)
    LANGUAGE_INHERITANCE = {
        'typescript': 'javascript',
        'tsx': 'javascript',
    }

    def __init__(self, queries_dir: Optional[Path] = None):
        if queries_dir is None:
            # Default to queries/ directory (same as this file)
            self.queries_dir = Path(__file__).parent
        else:
            self.queries_dir = Path(queries_dir)

        self._cache: Dict[str, QueryBundle] = {}
        self._validation_errors: Dict[str, List[str]] = {}

    def _resolve_language(self, language: str) -> str:
        """Resolve language aliases to canonical names."""
        return self.LANGUAGE_ALIASES.get(language, language)

    def _load_query_file(self, language: str, query_type: str) -> Optional[str]:
        """Load a single .scm file, returning None if not found."""
        # Try language-specific file first
        lang_dir = self.queries_dir / language
        query_path = lang_dir / f"{query_type}.scm"

        if query_path.exists():
            try:
                return query_path.read_text(encoding='utf-8')
            except Exception as e:
                self._log_error(language, f"Failed to read {query_path}: {e}")
                return None

        # Try inherited language
        parent = self.LANGUAGE_INHERITANCE.get(language)
        if parent:
            return self._load_query_file(parent, query_type)

        # Try fallback
        if language != '_fallback':
            fallback_path = self.queries_dir / '_fallback' / f"{query_type}.scm"
            if fallback_path.exists():
                try:
                    return fallback_path.read_text(encoding='utf-8')
                except Exception as e:
                    self._log_error(language, f"Failed to read fallback {fallback_path}: {e}")
                    return None

        return None

    def _log_error(self, language: str, error: str):
        """Log a validation error for a language."""
        if language not in self._validation_errors:
            self._validation_errors[language] = []
        self._validation_errors[language].append(error)

    def load_bundle(self, language: str) -> QueryBundle:
        """Load all queries for a language as a bundle."""
        canonical = self._resolve_language(language)

        if canonical in self._cache:
            return self._cache[canonical]

        raw_files = {}
        for query_type in self.QUERY_TYPES:
            content = self._load_query_file(canonical, query_type)
            if content:
                raw_files[query_type] = content

        bundle = QueryBundle(
            language=canonical,
            symbols=raw_files.get('symbols'),
            locals=raw_files.get('locals'),
            highlights=raw_files.get('highlights'),
            injections=raw_files.get('injections'),
            patterns=raw_files.get('patterns'),
            _raw_files=raw_files,
        )

        self._cache[canonical] = bundle
        return bundle

    def load_query(self, language: str, query_type: str) -> Optional[str]:
        """Load a specific query for a language."""
        bundle = self.load_bundle(language)
        return bundle.get_query(query_type)

    def list_languages(self) -> List[str]:
        """List available languages (directories with .scm files)."""
        languages = []
        for item in self.queries_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_') and not item.name.startswith('.'):
                # Check if it has at least one .scm file
                if any(item.glob('*.scm')):
                    languages.append(item.name)
        return sorted(languages)

    def list_queries(self, language: str) -> List[str]:
        """List available query types for a language."""
        canonical = self._resolve_language(language)
        bundle = self.load_bundle(canonical)
        return [qt for qt in self.QUERY_TYPES if bundle.has_query(qt)]

    def get_validation_errors(self) -> Dict[str, List[str]]:
        """Get all validation errors encountered during loading."""
        return self._validation_errors.copy()

    def clear_cache(self):
        """Clear the query cache."""
        self._cache.clear()
        self._validation_errors.clear()

    def validate_query(self, query_text: str, language_obj) -> bool:
        """
        Validate a query against a tree-sitter language.

        Args:
            query_text: The .scm query text
            language_obj: tree-sitter Language object

        Returns:
            True if valid, raises exception otherwise
        """
        try:
            import tree_sitter
            tree_sitter.Query(language_obj, query_text)
            return True
        except Exception as e:
            raise ValueError(f"Invalid query: {e}")


# Singleton loader
_loader: Optional[QueryLoader] = None


def get_query_loader() -> QueryLoader:
    """Get the singleton QueryLoader instance."""
    global _loader
    if _loader is None:
        _loader = QueryLoader()
    return _loader


def get_symbols_query(language: str) -> Optional[str]:
    """Convenience function to get symbols query for a language."""
    return get_query_loader().load_query(language, 'symbols')


def get_locals_query(language: str) -> Optional[str]:
    """Convenience function to get locals query for a language."""
    return get_query_loader().load_query(language, 'locals')


if __name__ == '__main__':
    # Test loading
    loader = QueryLoader()

    print("=" * 60)
    print("QUERY LOADER TEST")
    print("=" * 60)

    print(f"\nQueries directory: {loader.queries_dir}")
    print(f"\nAvailable languages: {loader.list_languages()}")

    for lang in loader.list_languages():
        queries = loader.list_queries(lang)
        print(f"\n{lang}: {queries}")
        for qt in queries:
            content = loader.load_query(lang, qt)
            if content:
                lines = content.strip().split('\n')
                print(f"  {qt}.scm: {len(lines)} lines")

    errors = loader.get_validation_errors()
    if errors:
        print("\nValidation errors:")
        for lang, errs in errors.items():
            for e in errs:
                print(f"  {lang}: {e}")
