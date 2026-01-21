"""
Tests for QueryLoader - tree-sitter query file management.
"""
import pytest
from pathlib import Path
from src.core.queries import QueryLoader, QueryBundle, get_query_loader, get_symbols_query, get_locals_query


class TestQueryBundle:
    """Tests for QueryBundle dataclass."""

    def test_has_query_with_content(self):
        """Test has_query returns True when query exists."""
        bundle = QueryBundle(language='test', symbols='(function_declaration) @func')
        assert bundle.has_query('symbols') is True

    def test_has_query_without_content(self):
        """Test has_query returns False when query is None."""
        bundle = QueryBundle(language='test', symbols=None)
        assert bundle.has_query('symbols') is False

    def test_get_query_returns_content(self):
        """Test get_query returns the query string."""
        query = '(function_declaration) @func'
        bundle = QueryBundle(language='test', symbols=query)
        assert bundle.get_query('symbols') == query

    def test_get_query_returns_none_for_missing(self):
        """Test get_query returns None for missing query type."""
        bundle = QueryBundle(language='test')
        assert bundle.get_query('nonexistent') is None


class TestQueryLoader:
    """Tests for QueryLoader class."""

    @pytest.fixture
    def loader(self):
        """Create a QueryLoader instance."""
        return QueryLoader()

    def test_list_languages(self, loader):
        """Test that list_languages finds language directories."""
        languages = loader.list_languages()
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'typescript' in languages
        assert 'go' in languages
        assert 'rust' in languages
        # Fallback directory should not be listed
        assert '_fallback' not in languages

    def test_load_python_symbols(self, loader):
        """Test loading Python symbols query."""
        query = loader.load_query('python', 'symbols')
        assert query is not None
        assert '@func' in query
        assert 'function_definition' in query

    def test_load_python_locals(self, loader):
        """Test loading Python locals query."""
        query = loader.load_query('python', 'locals')
        assert query is not None
        assert '@local.scope' in query
        assert '@local.definition' in query
        assert '@local.reference' in query

    def test_load_javascript_symbols(self, loader):
        """Test loading JavaScript symbols query."""
        query = loader.load_query('javascript', 'symbols')
        assert query is not None
        assert '@func' in query
        assert 'arrow_function' in query

    def test_typescript_inherits_javascript_locals(self, loader):
        """Test that TypeScript inherits JavaScript locals query."""
        ts_locals = loader.load_query('typescript', 'locals')
        js_locals = loader.load_query('javascript', 'locals')
        assert ts_locals is not None
        assert ts_locals == js_locals

    def test_typescript_has_own_symbols(self, loader):
        """Test that TypeScript has its own symbols query."""
        ts_symbols = loader.load_query('typescript', 'symbols')
        assert ts_symbols is not None
        assert 'interface_declaration' in ts_symbols or 'type_alias' in ts_symbols

    def test_language_alias_jsx(self, loader):
        """Test that jsx resolves to javascript."""
        jsx_bundle = loader.load_bundle('jsx')
        js_bundle = loader.load_bundle('javascript')
        assert jsx_bundle.symbols == js_bundle.symbols

    def test_language_alias_tsx(self, loader):
        """Test that tsx resolves to typescript."""
        tsx_bundle = loader.load_bundle('tsx')
        ts_bundle = loader.load_bundle('typescript')
        assert tsx_bundle.language == ts_bundle.language

    def test_fallback_for_unknown_language(self, loader):
        """Test that unknown language falls back to _fallback."""
        query = loader.load_query('unknown_language_xyz', 'symbols')
        assert query is not None
        # Fallback should be minimal but functional
        assert '@func' in query or '@class' in query

    def test_cache_works(self, loader):
        """Test that queries are cached."""
        bundle1 = loader.load_bundle('python')
        bundle2 = loader.load_bundle('python')
        assert bundle1 is bundle2

    def test_clear_cache(self, loader):
        """Test cache clearing."""
        bundle1 = loader.load_bundle('python')
        loader.clear_cache()
        bundle2 = loader.load_bundle('python')
        # After cache clear, should be different objects
        assert bundle1 is not bundle2
        # But same content
        assert bundle1.symbols == bundle2.symbols


class TestSingletonLoader:
    """Tests for singleton loader pattern."""

    def test_get_query_loader_returns_same_instance(self):
        """Test that get_query_loader returns singleton."""
        loader1 = get_query_loader()
        loader2 = get_query_loader()
        assert loader1 is loader2

    def test_convenience_functions(self):
        """Test convenience functions."""
        symbols = get_symbols_query('python')
        assert symbols is not None
        assert '@func' in symbols

        locals_q = get_locals_query('python')
        assert locals_q is not None
        assert '@local.scope' in locals_q


class TestQuerySyntax:
    """Tests for query file syntax correctness."""

    @pytest.fixture
    def loader(self):
        return QueryLoader()

    def test_python_symbols_syntax(self, loader):
        """Test Python symbols query has valid structure."""
        query = loader.load_query('python', 'symbols')
        # Should have capture patterns
        assert query.count('@') >= 5
        # Should not have obvious syntax errors (balanced parens)
        assert query.count('(') == query.count(')')

    def test_python_locals_syntax(self, loader):
        """Test Python locals query has valid structure."""
        query = loader.load_query('python', 'locals')
        # Must have all 4 local capture types
        assert '@local.scope' in query
        assert '@local.definition' in query
        assert '@local.reference' in query
        # PEP 227 comment should be present
        assert 'PEP 227' in query or 'class' in query.lower()

    def test_javascript_locals_has_tdz_awareness(self, loader):
        """Test JavaScript locals query is TDZ-aware."""
        query = loader.load_query('javascript', 'locals')
        # Should distinguish var from let/const
        assert 'var' in query
        assert 'let' in query or 'lexical_declaration' in query
