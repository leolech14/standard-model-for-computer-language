"""
Tests for AutoPatternDiscovery - the core role classification engine.
"""
import pytest
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from auto_pattern_discovery import AutoPatternDiscovery


class TestAutoPatternDiscovery:
    """Test suite for AutoPatternDiscovery."""
    
    @pytest.fixture
    def discovery(self):
        """Create fresh discovery instance."""
        return AutoPatternDiscovery()
    
    # =========================================================================
    # PREFIX PATTERNS
    # =========================================================================
    
    def test_get_prefix_returns_query(self, discovery):
        """get_ prefix should be classified as Query."""
        role, conf = discovery.classify_by_pattern("get_user")
        assert role == "Query"
        assert conf >= 80
    
    def test_set_prefix_returns_command(self, discovery):
        """set_ prefix should be classified as Command."""
        role, conf = discovery.classify_by_pattern("set_name")
        assert role == "Command"
        assert conf >= 80
    
    def test_create_prefix_returns_factory(self, discovery):
        """create_ prefix should be classified as Factory."""
        role, conf = discovery.classify_by_pattern("create_user")
        assert role == "Factory"
        assert conf >= 80
    
    def test_validate_prefix_returns_validator(self, discovery):
        """validate_ prefix should be classified as Validator."""
        role, conf = discovery.classify_by_pattern("validate_email")
        assert role == "Validator"
        assert conf >= 80
    
    def test_is_prefix_returns_specification(self, discovery):
        """is_ prefix should be classified as Specification."""
        role, conf = discovery.classify_by_pattern("is_valid")
        assert role == "Specification"
        assert conf >= 80
    
    # =========================================================================
    # SUFFIX PATTERNS
    # =========================================================================
    
    def test_service_suffix_returns_service(self, discovery):
        """*Service suffix should be classified as Service."""
        role, conf = discovery.classify_by_pattern("UserService")
        assert role == "Service"
        assert conf >= 80
    
    def test_repository_suffix_returns_repository(self, discovery):
        """*Repository suffix should be classified as Repository."""
        role, conf = discovery.classify_by_pattern("UserRepository")
        assert role == "Repository"
        assert conf >= 80
    
    def test_controller_suffix_returns_controller(self, discovery):
        """*Controller suffix should be classified as Controller."""
        role, conf = discovery.classify_by_pattern("UserController")
        assert role == "Controller"
        assert conf >= 80
    
    def test_handler_suffix_returns_event_handler(self, discovery):
        """*Handler suffix should be classified as EventHandler."""
        role, conf = discovery.classify_by_pattern("MessageHandler")
        assert role == "EventHandler"
        assert conf >= 80
    
    # =========================================================================
    # DUNDER METHODS
    # =========================================================================
    
    def test_init_returns_lifecycle(self, discovery):
        """__init__ should be classified as Lifecycle."""
        role, conf = discovery.classify_by_pattern("__init__")
        assert role == "Lifecycle"
        assert conf >= 90
    
    def test_str_returns_utility(self, discovery):
        """__str__ should be classified as Utility."""
        role, conf = discovery.classify_by_pattern("__str__")
        assert role == "Utility"
        assert conf >= 90
    
    def test_iter_returns_iterator(self, discovery):
        """__iter__ should be classified as Iterator."""
        role, conf = discovery.classify_by_pattern("__iter__")
        assert role == "Iterator"
        assert conf >= 90
    
    # =========================================================================
    # TEST CONTEXT
    # =========================================================================
    
    def test_test_prefix_returns_test(self, discovery):
        """test_ prefix should be classified as Test."""
        role, conf = discovery.classify_by_pattern("test_user_login")
        assert role == "Test"
        assert conf >= 80
    
    def test_in_test_module_returns_test(self, discovery):
        """Functions in test modules should be classified as Test."""
        role, conf = discovery.classify_by_pattern("tests.test_user.test_login")
        assert role == "Test"
        assert conf >= 80
    
    # =========================================================================
    # JAVA/TYPESCRIPT PATTERNS
    # =========================================================================
    
    def test_java_test_prefix_returns_test(self, discovery):
        """testUserLogin (Java style) should be classified as Test."""
        role, conf = discovery.classify_by_pattern("testUserLogin")
        assert role == "Test"
        assert conf >= 80
    
    def test_should_prefix_returns_test(self, discovery):
        """shouldReturnUser (BDD style) should be classified as Test."""
        role, conf = discovery.classify_by_pattern("shouldReturnUser")
        assert role == "Test"
        assert conf >= 80
    
    def test_describe_returns_test(self, discovery):
        """describe (Jest) should be classified as Test."""
        role, conf = discovery.classify_by_pattern("describe")
        assert role == "Test"
        assert conf >= 80
    
    def test_go_test_prefix_returns_test(self, discovery):
        """TestUserLogin (Go style) should be classified as Test."""
        role, conf = discovery.classify_by_pattern("TestUserLogin")
        assert role == "Test"
        assert conf >= 80
    
    # =========================================================================
    # EDGE CASES
    # =========================================================================
    
    def test_empty_name_returns_unknown(self, discovery):
        """Empty name should return Unknown."""
        role, conf = discovery.classify_by_pattern("")
        assert role == "Unknown"
        assert conf == 0.0
    
    def test_private_method_returns_internal(self, discovery):
        """Private methods (_foo) should be classified as Internal."""
        role, conf = discovery.classify_by_pattern("_private_method")
        assert role == "Internal"
        assert conf >= 70
    
    def test_qualified_name_extracts_short_name(self, discovery):
        """Qualified names should extract short name for classification."""
        role, conf = discovery.classify_by_pattern("module.class.get_user")
        assert role == "Query"
        assert conf >= 80


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
