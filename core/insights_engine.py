"""
Insights Engine - Actionable Intelligence from the Standard Model

Derives actionable insights, optimization schemas, and recommendations
from the Collider's classification output.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import Counter
from enum import Enum


class InsightType(Enum):
    """Categories of actionable insights"""
    ARCHITECTURE = "architecture"      # Structural improvements
    TESTING = "testing"                # Test coverage gaps
    REFACTORING = "refactoring"        # Code quality improvements
    PERFORMANCE = "performance"        # Optimization opportunities
    SECURITY = "security"              # Security concerns
    DOCUMENTATION = "documentation"    # Missing docs


class Priority(Enum):
    """Impact priority for insights"""
    CRITICAL = "critical"   # Fix immediately
    HIGH = "high"           # Fix soon
    MEDIUM = "medium"       # Plan for next sprint
    LOW = "low"             # Nice to have


@dataclass
class Insight:
    """A single actionable insight"""
    type: InsightType
    priority: Priority
    title: str
    description: str
    affected_components: List[str]
    recommendation: str
    effort_estimate: str  # "low", "medium", "high"
    schema: Optional[str] = None  # Optimization schema to apply


@dataclass 
class OptimizationSchema:
    """A reusable optimization pattern"""
    name: str
    description: str
    when_to_apply: str
    steps: List[str]
    expected_outcome: str


# =============================================================================
# OPTIMIZATION SCHEMAS
# =============================================================================

SCHEMAS = {
    "REPOSITORY_PATTERN": OptimizationSchema(
        name="Repository Pattern",
        description="Abstract data access behind repository interfaces",
        when_to_apply="Entities without dedicated Repository classes",
        steps=[
            "1. Create IEntityRepository interface",
            "2. Implement EntityRepository with CRUD operations",
            "3. Inject repository into services via dependency injection",
            "4. Replace direct data access with repository calls"
        ],
        expected_outcome="Decoupled data access, easier testing, single source of truth"
    ),
    
    "SERVICE_EXTRACTION": OptimizationSchema(
        name="Service Layer Extraction",
        description="Extract business logic into dedicated service classes",
        when_to_apply="Controllers/handlers with embedded business logic",
        steps=[
            "1. Identify business logic in controllers",
            "2. Create dedicated service class",
            "3. Move logic to service methods",
            "4. Controller calls service, handles only HTTP concerns"
        ],
        expected_outcome="Thin controllers, reusable business logic, better testability"
    ),
    
    "TEST_COVERAGE": OptimizationSchema(
        name="Test Coverage Plan",
        description="Systematic approach to adding tests",
        when_to_apply="Low test-to-logic ratio detected",
        steps=[
            "1. Prioritize by complexity: test high-complexity first",
            "2. Start with unit tests for pure functions (Queries)",
            "3. Add integration tests for Commands with side effects",
            "4. Add E2E tests for critical user flows"
        ],
        expected_outcome="Confidence in refactoring, regression detection, living documentation"
    ),
    
    "CQRS_SEPARATION": OptimizationSchema(
        name="CQRS Separation",
        description="Separate read and write operations",
        when_to_apply="Mixed Query/Command responsibilities in same class",
        steps=[
            "1. Identify Query methods (read, get, find, list)",
            "2. Identify Command methods (create, update, delete, execute)",
            "3. Create separate QueryService and CommandService",
            "4. Route reads through QueryService, writes through CommandService"
        ],
        expected_outcome="Optimized read/write paths, clearer responsibilities, scalability"
    ),
    
    "LAYER_ENFORCEMENT": OptimizationSchema(
        name="Layer Boundary Enforcement",
        description="Enforce architectural layer boundaries",
        when_to_apply="Cross-layer violations detected",
        steps=[
            "1. Define layer interfaces (ports/adapters)",
            "2. Replace direct cross-layer calls with interface calls",
            "3. Add linter rules to prevent layer violations",
            "4. Review PR for layer compliance"
        ],
        expected_outcome="Clean architecture, replaceable implementations, testable boundaries"
    ),
    
    "GOD_CLASS_DECOMPOSITION": OptimizationSchema(
        name="God Class Decomposition",
        description="Break apart large classes with too many responsibilities",
        when_to_apply="Classes with high responsibility score (R < 5)",
        steps=[
            "1. Identify distinct responsibilities within class",
            "2. Group related methods by responsibility",
            "3. Extract each group into dedicated class",
            "4. Compose original class from new components"
        ],
        expected_outcome="Single responsibility, smaller classes, focused testing"
    ),
    
    "PURE_FUNCTION_EXTRACTION": OptimizationSchema(
        name="Pure Function Extraction",
        description="Extract pure logic from impure functions",
        when_to_apply="Functions mixing pure calculation with side effects",
        steps=[
            "1. Identify pure logic segments (no I/O, no state mutation)",
            "2. Extract pure logic into separate functions",
            "3. Compose: pure calculation → then side effect",
            "4. Test pure functions exhaustively (fast, deterministic)"
        ],
        expected_outcome="Easier testing, parallelizable, cacheable results"
    ),
    
    "EVENT_SOURCING": OptimizationSchema(
        name="Event Sourcing",
        description="Store state changes as a sequence of events",
        when_to_apply="Complex domain with audit requirements or temporal queries",
        steps=[
            "1. Identify aggregate roots and their state transitions",
            "2. Define domain events for each state change",
            "3. Replace direct state mutation with event emission",
            "4. Implement event store and projections",
            "5. Add event handlers for read model updates"
        ],
        expected_outcome="Complete audit trail, time travel debugging, flexible projections"
    ),
    
    "SAGA_PATTERN": OptimizationSchema(
        name="Saga Pattern",
        description="Manage distributed transactions with compensating actions",
        when_to_apply="Cross-service operations requiring consistency",
        steps=[
            "1. Identify transaction boundaries across services",
            "2. Define compensating action for each step",
            "3. Implement saga orchestrator or choreography",
            "4. Add idempotency to all operations",
            "5. Implement retry and dead-letter handling"
        ],
        expected_outcome="Reliable distributed operations, graceful failure handling"
    ),
    
    "FACTORY_METHOD": OptimizationSchema(
        name="Factory Method Pattern",
        description="Centralize object creation logic",
        when_to_apply="Scattered 'new' operations with complex initialization",
        steps=[
            "1. Identify objects created in multiple places",
            "2. Create factory class/method for each complex object",
            "3. Move creation logic to factory",
            "4. Replace direct instantiation with factory calls"
        ],
        expected_outcome="Centralized creation, easier testing with mocks, consistent initialization"
    ),
    
    "STRATEGY_PATTERN": OptimizationSchema(
        name="Strategy Pattern",
        description="Encapsulate interchangeable algorithms",
        when_to_apply="Switch/if-else chains selecting between algorithms",
        steps=[
            "1. Identify algorithm selection points",
            "2. Define common interface for all algorithms",
            "3. Implement each algorithm as separate class",
            "4. Replace conditionals with strategy injection"
        ],
        expected_outcome="Open/closed principle, easy algorithm addition, testable strategies"
    ),
    
    "DEPENDENCY_INJECTION": OptimizationSchema(
        name="Dependency Injection",
        description="Invert control of dependency creation",
        when_to_apply="Classes creating their own dependencies directly",
        steps=[
            "1. Identify dependencies created with 'new' inside classes",
            "2. Extract interfaces for dependencies",
            "3. Accept dependencies via constructor/method parameters",
            "4. Configure DI container or manual wiring at composition root"
        ],
        expected_outcome="Loosely coupled code, easy testing, swappable implementations"
    ),
    
    "ERROR_HANDLING": OptimizationSchema(
        name="Error Handling Strategy",
        description="Implement consistent error handling across codebase",
        when_to_apply="Inconsistent exception handling, swallowed errors",
        steps=[
            "1. Define error hierarchy for domain/application/infra",
            "2. Create error handling middleware/decorator",
            "3. Ensure all errors are logged with context",
            "4. Return appropriate responses for each error type",
            "5. Add monitoring/alerting for critical errors"
        ],
        expected_outcome="Consistent error responses, better debugging, improved user experience"
    ),
}


class InsightsEngine:
    """Generates actionable insights from Collider output"""
    
    def __init__(self):
        self.insights: List[Insight] = []
        self.schemas = SCHEMAS
    
    def analyze(self, nodes: list, edges: list = None) -> List[Insight]:
        """
        Analyze Collider output and generate insights.
        
        Args:
            nodes: List of classified nodes from Collider
            edges: List of edges (optional)
        
        Returns:
            List of actionable insights
        """
        edges = edges or []
        self.insights = []
        
        # Count roles
        role_counts = Counter()
        for node in nodes:
            role = node.get('role', node.role if hasattr(node, 'role') else 'Unknown')
            role_counts[role] += 1
        
        # Run all insight detectors
        self._check_missing_repositories(role_counts)
        self._check_missing_tests(role_counts, len(nodes))
        self._check_service_layer(role_counts)
        self._check_cqrs_opportunity(role_counts)
        self._check_god_class_risk(nodes)
        self._check_pure_function_opportunity(nodes)
        self._check_layer_violations(nodes, edges)
        
        # Sort by priority
        priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
        self.insights.sort(key=lambda x: priority_order[x.priority])
        
        return self.insights
    
    def _check_missing_repositories(self, role_counts: Counter):
        """Detect missing repository pattern"""
        # Exclude DTOs - they are data structures, not persisted domain entities
        entities = role_counts.get('Entity', 0) + role_counts.get('AggregateRoot', 0)
        repos = role_counts.get('Repository', 0)
        
        if entities > 5 and repos < entities * 0.3:
            missing = entities - repos
            self.insights.append(Insight(
                type=InsightType.ARCHITECTURE,
                priority=Priority.MEDIUM,
                title="Missing Repository Pattern",
                description=f"Found {entities} data entities but only {repos} repositories.",
                affected_components=[f"{missing} entities without repositories"],
                recommendation="Apply Repository Pattern to abstract data access",
                effort_estimate="medium",
                schema="REPOSITORY_PATTERN"
            ))
    
    def _check_missing_tests(self, role_counts: Counter, total_nodes: int):
        """Detect test coverage gaps"""
        tests = role_counts.get('Test', 0)
        logic = (role_counts.get('Service', 0) + 
                 role_counts.get('Command', 0) + 
                 role_counts.get('ApplicationService', 0) +
                 role_counts.get('UseCase', 0))
        
        test_ratio = tests / logic if logic > 0 else 1.0
        
        if logic > 10 and test_ratio < 0.5:
            self.insights.append(Insight(
                type=InsightType.TESTING,
                priority=Priority.HIGH,
                title="Low Test Coverage",
                description=f"Only {tests} tests for {logic} logic components ({test_ratio:.0%} ratio).",
                affected_components=[f"{logic - tests} untested components"],
                recommendation="Add tests for critical business logic",
                effort_estimate="high",
                schema="TEST_COVERAGE"
            ))
    
    def _check_service_layer(self, role_counts: Counter):
        """Detect missing service layer"""
        controllers = role_counts.get('Controller', 0)
        services = role_counts.get('Service', 0) + role_counts.get('ApplicationService', 0)
        
        if controllers > 5 and services < controllers * 0.5:
            self.insights.append(Insight(
                type=InsightType.REFACTORING,
                priority=Priority.MEDIUM,
                title="Thin Service Layer",
                description=f"Found {controllers} controllers but only {services} services.",
                affected_components=["Controllers may contain business logic"],
                recommendation="Extract business logic into service layer",
                effort_estimate="medium",
                schema="SERVICE_EXTRACTION"
            ))
    
    def _check_cqrs_opportunity(self, role_counts: Counter):
        """Detect CQRS opportunity"""
        queries = role_counts.get('Query', 0)
        commands = role_counts.get('Command', 0)
        
        if queries > 20 and commands > 20:
            ratio = queries / commands if commands > 0 else 1
            if 0.3 < ratio < 3:  # Balanced mix suggests CQRS opportunity
                self.insights.append(Insight(
                    type=InsightType.ARCHITECTURE,
                    priority=Priority.LOW,
                    title="CQRS Opportunity",
                    description=f"Balanced Query/Command mix ({queries} queries, {commands} commands).",
                    affected_components=["Query and Command operations"],
                    recommendation="Consider CQRS pattern for scalability",
                    effort_estimate="high",
                    schema="CQRS_SEPARATION"
                ))
    
    def _check_god_class_risk(self, nodes: list):
        """Detect potential God classes"""
        # Count methods per class
        class_methods = Counter()
        for node in nodes:
            name = node.get('name', node.name if hasattr(node, 'name') else '')
            if '.' in name:
                class_name = name.rsplit('.', 1)[0]
                class_methods[class_name] += 1
        
        # Find classes with many methods
        god_classes = [cls for cls, count in class_methods.items() if count > 20]
        
        if god_classes:
            self.insights.append(Insight(
                type=InsightType.REFACTORING,
                priority=Priority.HIGH,
                title="God Class Detected",
                description=f"Found {len(god_classes)} classes with 20+ methods.",
                affected_components=god_classes[:5],
                recommendation="Decompose into smaller, focused classes",
                effort_estimate="high",
                schema="GOD_CLASS_DECOMPOSITION"
            ))
    
    def _check_pure_function_opportunity(self, nodes: list):
        """Detect pure function extraction opportunities"""
        queries = [n for n in nodes if n.get('role', getattr(n, 'role', '')) == 'Query']
        utilities = [n for n in nodes if n.get('role', getattr(n, 'role', '')) == 'Utility']
        
        pure_candidates = len(queries) + len(utilities)
        if pure_candidates > 30:
            self.insights.append(Insight(
                type=InsightType.PERFORMANCE,
                priority=Priority.LOW,
                title="Pure Function Optimization",
                description=f"Found {pure_candidates} potentially pure functions (Queries + Utilities).",
                affected_components=[f"{len(queries)} queries, {len(utilities)} utilities"],
                recommendation="Verify purity and add caching where beneficial",
                effort_estimate="low",
                schema="PURE_FUNCTION_EXTRACTION"
            ))
    
    def _check_layer_violations(self, nodes: list, edges: list):
        """Detect layer violations from edges"""
        # Layer order (higher = deeper in architecture)
        ROLE_TO_LAYER = {
            'Controller': 'presentation',
            'View': 'presentation',
            
            'ApplicationService': 'application',
            'UseCase': 'application',
            'Service': 'application',
            
            'Entity': 'domain',
            'ValueObject': 'domain',
            'DomainService': 'domain',
            'Policy': 'domain',
            'Specification': 'domain',
            
            'Repository': 'infrastructure',
            'RepositoryImpl': 'infrastructure',
            'Gateway': 'infrastructure',
            'Adapter': 'infrastructure',
            'Configuration': 'infrastructure',
        }
        
        LAYER_ORDER = {
            'presentation': 0,
            'application': 1,
            'domain': 2,
            'infrastructure': 3,
        }
        
        # Build node lookup
        node_lookup = {}
        for node in nodes:
            name = node.get('name', getattr(node, 'name', ''))
            role = node.get('role', getattr(node, 'role', 'Unknown'))
            node_lookup[name] = role
        
        violations = []
        for edge in edges:
            # Handle dict or tuple edges
            if isinstance(edge, dict):
                source = edge.get('source', edge.get('from', ''))
                target = edge.get('target', edge.get('to', ''))
            elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
                source, target = edge[0], edge[1]
            else:
                continue
            
            source_role = node_lookup.get(source, 'Unknown')
            target_role = node_lookup.get(target, 'Unknown')
            
            source_layer = ROLE_TO_LAYER.get(source_role, 'unknown')
            target_layer = ROLE_TO_LAYER.get(target_role, 'unknown')
            
            source_order = LAYER_ORDER.get(source_layer, 99)
            target_order = LAYER_ORDER.get(target_layer, 99)
            
            # Violation: deeper layer calling shallower layer
            if source_order > target_order and source_layer != 'unknown' and target_layer != 'unknown':
                violations.append(f"{source} ({source_layer}) → {target} ({target_layer})")
        
        if len(violations) > 5:
            self.insights.append(Insight(
                type=InsightType.ARCHITECTURE,
                priority=Priority.HIGH,
                title="Layer Boundary Violations",
                description=f"Found {len(violations)} cross-layer violations (infrastructure calling presentation).",
                affected_components=violations[:5],
                recommendation="Enforce layer boundaries - dependencies should point inward",
                effort_estimate="medium",
                schema="LAYER_ENFORCEMENT"
            ))
    
    def get_report(self) -> str:
        """Generate human-readable report"""
        if not self.insights:
            return "✅ No significant issues detected."
        
        lines = ["# Actionable Insights Report\n"]
        
        # Group by type
        by_type = {}
        for insight in self.insights:
            key = insight.type.value
            if key not in by_type:
                by_type[key] = []
            by_type[key].append(insight)
        
        for type_name, insights in by_type.items():
            lines.append(f"\n## {type_name.upper()}\n")
            for i, insight in enumerate(insights, 1):
                lines.append(f"### {i}. {insight.title} [{insight.priority.value.upper()}]")
                lines.append(f"\n{insight.description}\n")
                lines.append(f"**Affected:** {', '.join(insight.affected_components[:3])}")
                lines.append(f"\n**Recommendation:** {insight.recommendation}")
                lines.append(f"\n**Effort:** {insight.effort_estimate}")
                if insight.schema:
                    schema = self.schemas.get(insight.schema)
                    if schema:
                        lines.append(f"\n\n**Optimization Schema: {schema.name}**")
                        lines.append(f"\n{schema.description}")
                        lines.append(f"\n\nSteps:")
                        for step in schema.steps:
                            lines.append(f"\n- {step}")
                lines.append("\n---\n")
        
        return "\n".join(lines)


def generate_insights(nodes: list, edges: list = None) -> Tuple[List[Insight], str]:
    """
    Convenience function to generate insights.
    
    Usage:
        from insights_engine import generate_insights
        
        result = analyze(path)
        insights, report = generate_insights(result.nodes, result.edges)
        print(report)
    """
    engine = InsightsEngine()
    insights = engine.analyze(nodes, edges)
    report = engine.get_report()
    return insights, report


if __name__ == "__main__":
    # Demo
    test_nodes = [
        {"name": "UserService.create", "role": "Command"},
        {"name": "UserService.get", "role": "Query"},
        {"name": "UserService.update", "role": "Command"},
        {"name": "UserRepository.save", "role": "Command"},
        {"name": "User", "role": "Entity"},
        {"name": "Order", "role": "Entity"},
        {"name": "Product", "role": "Entity"},
        {"name": "Payment", "role": "Entity"},
        {"name": "get_config", "role": "Query"},
        {"name": "validate_email", "role": "Utility"},
    ] * 10  # Simulate larger codebase
    
    insights, report = generate_insights(test_nodes)
    print(report)
