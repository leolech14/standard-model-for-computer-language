"""
Tests for InsightsEngine - actionable intelligence from classification.
"""
import pytest
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from insights_engine import InsightsEngine, generate_insights, InsightType, Priority


class TestInsightsEngine:
    """Test suite for InsightsEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create fresh engine instance."""
        return InsightsEngine()
    
    # =========================================================================
    # SCHEMA DETECTION
    # =========================================================================
    
    def test_detects_missing_repositories(self, engine):
        """Should detect missing repository pattern when entities > repos."""
        nodes = [
            {"name": "User", "role": "Entity"},
            {"name": "Order", "role": "Entity"},
            {"name": "Product", "role": "Entity"},
            {"name": "Payment", "role": "Entity"},
            {"name": "Invoice", "role": "Entity"},
            {"name": "Customer", "role": "Entity"},
            {"name": "UserRepository", "role": "Repository"},
        ]
        
        insights = engine.analyze(nodes)
        
        # Find repository pattern insight
        repo_insight = next(
            (i for i in insights if "Repository" in i.title),
            None
        )
        
        assert repo_insight is not None
        assert repo_insight.schema == "REPOSITORY_PATTERN"
        assert repo_insight.priority == Priority.MEDIUM
    
    def test_detects_low_test_coverage(self, engine):
        """Should detect low test coverage when tests < logic."""
        nodes = [
            {"name": f"Service{i}.execute", "role": "Command"} 
            for i in range(20)
        ] + [
            {"name": "test_one", "role": "Test"},
            {"name": "test_two", "role": "Test"},
        ]
        
        insights = engine.analyze(nodes)
        
        # Find test coverage insight
        test_insight = next(
            (i for i in insights if "Test" in i.title or "Coverage" in i.title),
            None
        )
        
        assert test_insight is not None
        assert test_insight.schema == "TEST_COVERAGE"
        assert test_insight.priority == Priority.HIGH
    
    def test_detects_god_class(self, engine):
        """Should detect god class when class has 20+ methods."""
        nodes = [
            {"name": f"GodClass.method{i}", "role": "Command"} 
            for i in range(25)
        ]
        
        insights = engine.analyze(nodes)
        
        # Find god class insight
        god_insight = next(
            (i for i in insights if "God" in i.title),
            None
        )
        
        assert god_insight is not None
        assert god_insight.schema == "GOD_CLASS_DECOMPOSITION"
        assert god_insight.priority == Priority.HIGH
    
    def test_detects_pure_function_optimization(self, engine):
        """Should suggest pure function optimization for queries + utilities."""
        nodes = [
            {"name": f"get_{i}", "role": "Query"} for i in range(20)
        ] + [
            {"name": f"util_{i}", "role": "Utility"} for i in range(20)
        ]
        
        insights = engine.analyze(nodes)
        
        # Find pure function insight
        pure_insight = next(
            (i for i in insights if "Pure" in i.title),
            None
        )
        
        assert pure_insight is not None
        assert pure_insight.schema == "PURE_FUNCTION_EXTRACTION"
        assert pure_insight.priority == Priority.LOW
    
    # =========================================================================
    # CONVENIENCE FUNCTION
    # =========================================================================
    
    def test_generate_insights_returns_tuple(self):
        """generate_insights should return (insights, report)."""
        nodes = [{"name": "User", "role": "Entity"}]
        
        result = generate_insights(nodes)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        insights, report = result
        assert isinstance(insights, list)
        assert isinstance(report, str)
    
    # =========================================================================
    # EDGE CASES
    # =========================================================================
    
    def test_empty_nodes_returns_no_insights(self, engine):
        """Empty node list should return no insights."""
        insights = engine.analyze([])
        assert insights == []
    
    def test_healthy_codebase_minimal_insights(self, engine):
        """Well-structured codebase should have minimal insights."""
        nodes = [
            # Balanced entities and repos
            {"name": "User", "role": "Entity"},
            {"name": "UserRepository", "role": "Repository"},
            {"name": "Order", "role": "Entity"},
            {"name": "OrderRepository", "role": "Repository"},
            # Good test coverage
            {"name": "UserService.create", "role": "Command"},
            {"name": "test_user_create", "role": "Test"},
            {"name": "OrderService.process", "role": "Command"},
            {"name": "test_order_process", "role": "Test"},
        ]
        
        insights = engine.analyze(nodes)
        
        # Should have no high-priority insights
        high_priority = [i for i in insights if i.priority in (Priority.CRITICAL, Priority.HIGH)]
        assert len(high_priority) == 0
    
    def test_insight_has_all_fields(self, engine):
        """Each insight should have all required fields."""
        nodes = [
            {"name": f"Service{i}.execute", "role": "Command"} 
            for i in range(20)
        ]
        
        insights = engine.analyze(nodes)
        
        for insight in insights:
            assert insight.type is not None
            assert insight.priority is not None
            assert insight.title
            assert insight.description
            assert insight.recommendation
            assert insight.effort_estimate


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
