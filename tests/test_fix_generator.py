"""
Tests for FixGenerator - code template generation.
"""
import pytest
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from fix_generator import FixGenerator, generate_fixes, CodeTemplate


class TestFixGenerator:
    """Test suite for FixGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Create fresh generator instance."""
        return FixGenerator("python")
    
    # =========================================================================
    # TEMPLATE GENERATION
    # =========================================================================
    
    def test_generates_repository_pattern(self, generator):
        """Should generate repository pattern code."""
        fix = generator.generate_fix("REPOSITORY_PATTERN", {
            "entity": "user",
            "Entity": "User"
        })
        
        assert fix is not None
        assert "UserRepository" in fix.code
        assert "IUserRepository" in fix.code
        assert "get_by_id" in fix.code
        assert "save" in fix.code
        assert fix.filename == "user_repository.py"
    
    def test_generates_test_coverage(self, generator):
        """Should generate test template code."""
        fix = generator.generate_fix("TEST_COVERAGE", {
            "component": "service",
            "Component": "Service"
        })
        
        assert fix is not None
        assert "TestService" in fix.code
        assert "pytest" in fix.code
        assert "test_should" in fix.code or "def test_" in fix.code
    
    def test_generates_cqrs_separation(self, generator):
        """Should generate CQRS pattern code."""
        fix = generator.generate_fix("CQRS_SEPARATION", {
            "entity": "order",
            "Entity": "Order"
        })
        
        assert fix is not None
        assert "QueryHandler" in fix.code
        assert "CommandHandler" in fix.code
    
    def test_generates_god_class_decomposition(self, generator):
        """Should generate god class decomposition code."""
        fix = generator.generate_fix("GOD_CLASS_DECOMPOSITION", {
            "class": "manager",
            "Class": "Manager"
        })
        
        assert fix is not None
        assert "ManagerQueryHandler" in fix.code or "QueryHandler" in fix.code
        assert "ManagerCommandHandler" in fix.code or "CommandHandler" in fix.code
    
    # =========================================================================
    # LANGUAGE SUPPORT
    # =========================================================================
    
    def test_typescript_support(self):
        """Should generate TypeScript code when requested."""
        generator = FixGenerator("typescript")
        
        fix = generator.generate_fix("REPOSITORY_PATTERN", {
            "entity": "user",
            "Entity": "User"
        })
        
        assert fix is not None
        assert fix.language == "typescript"
        assert "interface" in fix.code or "class" in fix.code
        assert "async" in fix.code
    
    def test_falls_back_to_available_language(self):
        """Should fallback if requested language not available."""
        generator = FixGenerator("rust")  # Not implemented yet
        
        fix = generator.generate_fix("REPOSITORY_PATTERN", {
            "entity": "user",
            "Entity": "User"
        })
        
        # Should fall back to Python or TypeScript
        assert fix is not None
        assert fix.language in ("python", "typescript")
    
    # =========================================================================
    # PLACEHOLDER SUBSTITUTION
    # =========================================================================
    
    def test_substitutes_entity_placeholder(self, generator):
        """Should substitute {Entity} placeholder."""
        fix = generator.generate_fix("REPOSITORY_PATTERN", {
            "Entity": "Product"
        })
        
        assert fix is not None
        assert "Product" in fix.code
        assert "{Entity}" not in fix.code
    
    def test_substitutes_lowercase_placeholder(self, generator):
        """Should substitute {entity} placeholder."""
        fix = generator.generate_fix("REPOSITORY_PATTERN", {
            "entity": "product",
            "Entity": "Product"
        })
        
        assert fix is not None
        assert "product" in fix.filename
        assert "{entity}" not in fix.filename
    
    # =========================================================================
    # CONVENIENCE FUNCTION
    # =========================================================================
    
    def test_generate_fixes_from_insights(self):
        """generate_fixes should work with insight list."""
        # Mock insights with schema attribute
        class MockInsight:
            def __init__(self, schema):
                self.schema = schema
        
        insights = [
            MockInsight("REPOSITORY_PATTERN"),
            MockInsight("TEST_COVERAGE"),
        ]
        
        fixes = generate_fixes(insights)
        
        assert isinstance(fixes, list)
        assert len(fixes) >= 1
    
    # =========================================================================
    # EDGE CASES
    # =========================================================================
    
    def test_unknown_schema_returns_none(self, generator):
        """Unknown schema should return None."""
        fix = generator.generate_fix("UNKNOWN_SCHEMA", {})
        
        assert fix is None
    
    def test_empty_context_uses_defaults(self, generator):
        """Empty context should still work with defaults."""
        fix = generator.generate_fix("REPOSITORY_PATTERN", {})
        
        # Should have default placeholders or generate something
        assert fix is not None
    
    def test_code_template_has_all_fields(self, generator):
        """CodeTemplate should have all required fields."""
        fix = generator.generate_fix("REPOSITORY_PATTERN", {"Entity": "User"})
        
        assert fix.language is not None
        assert fix.filename is not None
        assert fix.code is not None
        assert fix.description is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
