"""
Tests for PurposeFieldDetector - hierarchical purpose emergence.
"""
import pytest
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from purpose_field import PurposeFieldDetector, detect_purpose_field, Layer


class TestPurposeFieldDetector:
    """Test suite for PurposeFieldDetector."""
    
    @pytest.fixture
    def detector(self):
        """Create fresh detector instance."""
        return PurposeFieldDetector()
    
    # =========================================================================
    # LAYER ASSIGNMENT
    # =========================================================================
    
    def test_controller_assigned_presentation_layer(self, detector):
        """Controllers should be in presentation layer."""
        nodes = [{"id": "1", "name": "UserController", "kind": "class", "role": "Controller"}]
        
        field = detector.detect_field(nodes)
        
        assert field.nodes["1"].layer == Layer.PRESENTATION
    
    def test_service_assigned_application_layer(self, detector):
        """Services should be in application layer."""
        nodes = [{"id": "1", "name": "UserService", "kind": "class", "role": "ApplicationService"}]
        
        field = detector.detect_field(nodes)
        
        assert field.nodes["1"].layer == Layer.APPLICATION
    
    def test_entity_assigned_domain_layer(self, detector):
        """Entities should be in domain layer."""
        nodes = [{"id": "1", "name": "User", "kind": "class", "role": "Entity"}]
        
        field = detector.detect_field(nodes)
        
        assert field.nodes["1"].layer == Layer.DOMAIN
    
    def test_repository_assigned_infrastructure_layer(self, detector):
        """Repositories should be in infrastructure layer."""
        nodes = [{"id": "1", "name": "UserRepository", "kind": "class", "role": "Repository"}]
        
        field = detector.detect_field(nodes)
        
        assert field.nodes["1"].layer == Layer.INFRASTRUCTURE
    
    # =========================================================================
    # COMPOSITE PURPOSE
    # =========================================================================
    
    @pytest.mark.xfail(
        reason="TODO(SMOC-002): EMERGENCE_RULES lookup fails for frozenset({'Query', 'Command'}). "
               "Returns 'Service' instead of 'Repository'. Bug in purpose_classifier.py.",
        strict=True
    )
    def test_class_with_query_and_command_is_repository(self, detector):
        """Class with Query + Command children should be Repository."""
        nodes = [
            {"id": "1", "name": "UserRepo", "kind": "class", "role": "Unknown"},
            {"id": "2", "name": "UserRepo.get", "kind": "method", "role": "Query"},
            {"id": "3", "name": "UserRepo.save", "kind": "method", "role": "Command"},
        ]

        field = detector.detect_field(nodes)

        assert field.nodes["1"].composite_purpose == "Repository"
    
    def test_class_with_only_tests_is_test_suite(self, detector):
        """Class with only Test children should be TestSuite."""
        nodes = [
            {"id": "1", "name": "TestUser", "kind": "class", "role": "Unknown"},
            {"id": "2", "name": "TestUser.test_one", "kind": "method", "role": "Test"},
            {"id": "3", "name": "TestUser.test_two", "kind": "method", "role": "Test"},
        ]
        
        field = detector.detect_field(nodes)
        
        assert field.nodes["1"].composite_purpose == "TestSuite"
    
    # =========================================================================
    # VIOLATION DETECTION
    # =========================================================================
    
    def test_detects_infrastructure_calling_presentation(self, detector):
        """Should detect violation when infrastructure calls presentation."""
        nodes = [
            {"id": "repo", "name": "UserRepository", "kind": "class", "role": "Repository"},
            {"id": "ctrl", "name": "UserController", "kind": "class", "role": "Controller"},
        ]
        edges = [
            {"source": "repo", "target": "ctrl"}  # Violation!
        ]

        field = detector.detect_field(nodes, edges)

        assert len(field.violations) > 0
        assert any("Repository" in v and "Controller" in v for v in field.violations)
    
    def test_no_violation_for_correct_flow(self, detector):
        """Should not detect violation for correct dependency flow."""
        nodes = [
            {"id": "ctrl", "name": "UserController", "kind": "class", "role": "Controller"},
            {"id": "svc", "name": "UserService", "kind": "class", "role": "ApplicationService"},
            {"id": "repo", "name": "UserRepository", "kind": "class", "role": "Repository"},
        ]
        edges = [
            {"source": "ctrl", "target": "svc"},   # OK: presentation → application
            {"source": "svc", "target": "repo"},  # OK: application → infrastructure
        ]
        
        field = detector.detect_field(nodes, edges)
        
        assert len(field.violations) == 0
    
    # =========================================================================
    # CONVENIENCE FUNCTION
    # =========================================================================
    
    def test_detect_purpose_field_returns_field(self):
        """detect_purpose_field should return PurposeField."""
        nodes = [{"id": "1", "name": "User", "kind": "class", "role": "Entity"}]
        
        field = detect_purpose_field(nodes)
        
        assert field is not None
        assert len(field.nodes) == 1
    
    def test_summary_has_expected_keys(self, detector):
        """summary() should have expected keys."""
        nodes = [
            {"id": "1", "name": "UserController", "kind": "class", "role": "Controller"},
            {"id": "2", "name": "UserService", "kind": "class", "role": "Service"},
        ]
        
        field = detector.detect_field(nodes)
        summary = field.summary()
        
        assert "total_nodes" in summary
        assert "layers" in summary
        assert "purposes" in summary
        assert "violations" in summary
    
    # =========================================================================
    # EDGE CASES
    # =========================================================================
    
    def test_empty_nodes_returns_empty_field(self, detector):
        """Empty node list should return empty field."""
        field = detector.detect_field([])
        
        assert len(field.nodes) == 0
        assert len(field.violations) == 0
    
    def test_handles_tuple_edges(self, detector):
        """Should handle tuple format edges."""
        nodes = [
            {"id": "a", "name": "ServiceA", "kind": "class", "role": "Service"},
            {"id": "b", "name": "ServiceB", "kind": "class", "role": "Service"},
        ]
        edges = [("a", "b")]  # Tuple format
        
        field = detector.detect_field(nodes, edges)
        
        # Should not crash
        assert len(field.purpose_flow) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
