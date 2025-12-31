"""
Insight Detectors
=================

Individual detection functions for different types of code issues.
"""

from typing import List, Dict
from collections import Counter

from .models import Insight, InsightType, Priority


# Layer mappings for violation detection
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


class InsightDetector:
    """Detects code issues and generates insights."""

    def __init__(self):
        self.insights: List[Insight] = []

    def detect_all(
        self,
        nodes: List[Dict],
        edges: List = None,
        role_counts: Counter = None
    ) -> List[Insight]:
        """Run all detectors and return insights."""
        self.insights = []
        edges = edges or []

        if role_counts is None:
            role_counts = Counter()
            for node in nodes:
                role = node.get('role', getattr(node, 'role', 'Unknown'))
                role_counts[role] += 1

        # Run all detectors
        self.check_missing_repositories(role_counts)
        self.check_missing_tests(role_counts, len(nodes))
        self.check_service_layer(role_counts)
        self.check_cqrs_opportunity(role_counts)
        self.check_god_class_risk(nodes)
        self.check_pure_function_opportunity(nodes)
        self.check_layer_violations(nodes, edges)

        return self.insights

    def check_missing_repositories(self, role_counts: Counter) -> None:
        """Detect missing repository pattern."""
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

    def check_missing_tests(self, role_counts: Counter, total_nodes: int) -> None:
        """Detect test coverage gaps."""
        tests = role_counts.get('Test', 0)
        logic = (
            role_counts.get('Service', 0) +
            role_counts.get('Command', 0) +
            role_counts.get('ApplicationService', 0) +
            role_counts.get('UseCase', 0)
        )

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

    def check_service_layer(self, role_counts: Counter) -> None:
        """Detect missing service layer."""
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

    def check_cqrs_opportunity(self, role_counts: Counter) -> None:
        """Detect CQRS opportunity."""
        queries = role_counts.get('Query', 0)
        commands = role_counts.get('Command', 0)

        if queries > 20 and commands > 20:
            ratio = queries / commands if commands > 0 else 1
            if 0.3 < ratio < 3:
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

    def check_god_class_risk(self, nodes: List[Dict]) -> None:
        """Detect potential God classes."""
        class_methods = Counter()
        for node in nodes:
            name = node.get('name', getattr(node, 'name', ''))
            if '.' in name:
                class_name = name.rsplit('.', 1)[0]
                class_methods[class_name] += 1

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

    def check_pure_function_opportunity(self, nodes: List[Dict]) -> None:
        """Detect pure function extraction opportunities."""
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

    def check_layer_violations(self, nodes: List[Dict], edges: List) -> None:
        """Detect layer violations from edges."""
        # Build node lookup
        node_lookup = {}
        for node in nodes:
            name = node.get('name', getattr(node, 'name', ''))
            role = node.get('role', getattr(node, 'role', 'Unknown'))
            node_lookup[name] = role

        violations = []
        for edge in edges:
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

            if source_order > target_order and source_layer != 'unknown' and target_layer != 'unknown':
                violations.append(f"{source} ({source_layer}) -> {target} ({target_layer})")

        if len(violations) > 5:
            self.insights.append(Insight(
                type=InsightType.ARCHITECTURE,
                priority=Priority.HIGH,
                title="Layer Boundary Violations",
                description=f"Found {len(violations)} cross-layer violations.",
                affected_components=violations[:5],
                recommendation="Enforce layer boundaries - dependencies should point inward",
                effort_estimate="medium",
                schema="LAYER_ENFORCEMENT"
            ))
