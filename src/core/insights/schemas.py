"""
Optimization Schemas
====================

Reusable optimization patterns for code improvements.
"""

from .models import OptimizationSchema


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
            "3. Compose: pure calculation -> then side effect",
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
