"""
Schema Repository

Centralized storage for optimization schemas.
Single source of truth for all recommended patterns and fixes.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class SchemaCategory(Enum):
    """Category of optimization schema."""
    ARCHITECTURE = "architecture"
    REFACTORING = "refactoring"
    TESTING = "testing"
    PERFORMANCE = "performance"
    SECURITY = "security"


class Effort(Enum):
    """Effort level for applying a schema."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class OptimizationSchema:
    """An optimization schema with instructions and templates."""
    id: str
    name: str
    category: SchemaCategory
    description: str
    when_to_apply: str
    effort: Effort
    steps: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    examples: Dict[str, str] = field(default_factory=dict)  # language -> code
    related_schemas: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "when_to_apply": self.when_to_apply,
            "effort": self.effort.value,
            "steps": self.steps,
            "benefits": self.benefits,
            "risks": self.risks,
            "related_schemas": self.related_schemas,
        }


class SchemaRepository:
    """
    Repository for optimization schemas.
    
    Each schema provides:
    - When to apply it (detection criteria)
    - Step-by-step instructions
    - Code templates per language
    - Benefits and risks
    """
    
    def __init__(self):
        self._schemas: Dict[str, OptimizationSchema] = {}
        self._load_default_schemas()
    
    def _load_default_schemas(self):
        """Load all default optimization schemas."""
        
        # REPOSITORY_PATTERN
        self._schemas["REPOSITORY_PATTERN"] = OptimizationSchema(
            id="REPOSITORY_PATTERN",
            name="Repository Pattern",
            category=SchemaCategory.ARCHITECTURE,
            description="Abstract data access behind repository interfaces",
            when_to_apply="Entities without corresponding repositories",
            effort=Effort.MEDIUM,
            steps=[
                "Create repository interface (IEntityRepository)",
                "Define CRUD methods: get, save, delete, find_all",
                "Implement concrete repository class",
                "Inject repository into services",
                "Replace direct data access with repository calls",
            ],
            benefits=[
                "Decouples business logic from data access",
                "Enables easy testing with mocks",
                "Supports swapping storage implementations",
            ],
            risks=[
                "Over-abstraction for simple cases",
                "Performance overhead if misused",
            ],
            related_schemas=["CQRS_SEPARATION", "DEPENDENCY_INJECTION"],
        )
        
        # TEST_COVERAGE
        self._schemas["TEST_COVERAGE"] = OptimizationSchema(
            id="TEST_COVERAGE",
            name="Test Coverage",
            category=SchemaCategory.TESTING,
            description="Add unit tests for untested components",
            when_to_apply="Test-to-logic ratio below 1:3",
            effort=Effort.MEDIUM,
            steps=[
                "Identify critical paths (commands, services)",
                "Create test file following naming convention",
                "Write tests for happy path first",
                "Add edge cases and error scenarios",
                "Aim for 80% coverage on critical paths",
            ],
            benefits=[
                "Catches regressions early",
                "Documents expected behavior",
                "Enables confident refactoring",
            ],
            risks=[
                "Brittle tests if too coupled to implementation",
                "Maintenance overhead for trivial tests",
            ],
            related_schemas=["GOD_CLASS_DECOMPOSITION"],
        )
        
        # CQRS_SEPARATION
        self._schemas["CQRS_SEPARATION"] = OptimizationSchema(
            id="CQRS_SEPARATION",
            name="CQRS Separation",
            category=SchemaCategory.ARCHITECTURE,
            description="Separate read (query) and write (command) operations",
            when_to_apply="Mixed read/write operations in same class",
            effort=Effort.HIGH,
            steps=[
                "Identify query methods (no side effects, return data)",
                "Identify command methods (mutate state, may return void)",
                "Create QueryHandler interface",
                "Create CommandHandler interface",
                "Move methods to appropriate handlers",
                "Update callers to use correct handler",
            ],
            benefits=[
                "Enables read/write scaling independently",
                "Clearer intent in code",
                "Better separation of concerns",
            ],
            risks=[
                "Increases complexity for simple cases",
                "Eventual consistency challenges",
            ],
            related_schemas=["EVENT_SOURCING", "REPOSITORY_PATTERN"],
        )
        
        # GOD_CLASS_DECOMPOSITION
        self._schemas["GOD_CLASS_DECOMPOSITION"] = OptimizationSchema(
            id="GOD_CLASS_DECOMPOSITION",
            name="God Class Decomposition",
            category=SchemaCategory.REFACTORING,
            description="Split large classes into smaller, focused components",
            when_to_apply="Classes with 20+ methods or 500+ lines",
            effort=Effort.HIGH,
            steps=[
                "Identify cohesive method groups (by functionality)",
                "Create new class for each group",
                "Move methods to new classes",
                "Use composition in original class",
                "Update callers to use new classes",
            ],
            benefits=[
                "Single Responsibility Principle",
                "Easier to test individual components",
                "Reduced cognitive load",
            ],
            risks=[
                "May break existing interfaces",
                "Increased file count",
            ],
            related_schemas=["SERVICE_EXTRACTION", "STRATEGY_PATTERN"],
        )
        
        # SERVICE_EXTRACTION
        self._schemas["SERVICE_EXTRACTION"] = OptimizationSchema(
            id="SERVICE_EXTRACTION",
            name="Service Extraction",
            category=SchemaCategory.REFACTORING,
            description="Extract business logic into dedicated service classes",
            when_to_apply="Controllers with embedded business logic",
            effort=Effort.MEDIUM,
            steps=[
                "Identify business logic in controller",
                "Create service class with domain methods",
                "Move logic to service",
                "Inject service into controller",
                "Controller becomes thin orchestrator",
            ],
            benefits=[
                "Reusable business logic",
                "Testable without HTTP concerns",
                "Clear separation of concerns",
            ],
            risks=["Over-engineering simple endpoints"],
            related_schemas=["DEPENDENCY_INJECTION"],
        )
        
        # LAYER_ENFORCEMENT
        self._schemas["LAYER_ENFORCEMENT"] = OptimizationSchema(
            id="LAYER_ENFORCEMENT",
            name="Layer Enforcement",
            category=SchemaCategory.ARCHITECTURE,
            description="Enforce clean layer boundaries in architecture",
            when_to_apply="Cross-layer violations detected",
            effort=Effort.MEDIUM,
            steps=[
                "Define layer boundaries (presentation, application, domain, infrastructure)",
                "Add lint rules or tests for layer violations",
                "Refactor violating imports",
                "Use interfaces for cross-layer communication",
            ],
            benefits=[
                "Clean Architecture compliance",
                "Independent layer evolution",
                "Testability at each layer",
            ],
            risks=["Too rigid for small projects"],
            related_schemas=["DEPENDENCY_INJECTION"],
        )
        
        # PURE_FUNCTION_EXTRACTION
        self._schemas["PURE_FUNCTION_EXTRACTION"] = OptimizationSchema(
            id="PURE_FUNCTION_EXTRACTION",
            name="Pure Function Extraction",
            category=SchemaCategory.PERFORMANCE,
            description="Extract pure functions for caching and parallelization",
            when_to_apply="Functions mixing pure computation with side effects",
            effort=Effort.LOW,
            steps=[
                "Identify pure computations (no I/O, no state mutation)",
                "Extract to standalone pure functions",
                "Add @lru_cache or similar memoization",
                "Parallelize where beneficial",
            ],
            benefits=[
                "Easy to cache results",
                "Safe for parallelization",
                "Easier to test",
            ],
            risks=["Cache invalidation complexity"],
            related_schemas=[],
        )
        
        # EVENT_SOURCING
        self._schemas["EVENT_SOURCING"] = OptimizationSchema(
            id="EVENT_SOURCING",
            name="Event Sourcing",
            category=SchemaCategory.ARCHITECTURE,
            description="Store state as sequence of events",
            when_to_apply="Audit requirements or complex state history needs",
            effort=Effort.HIGH,
            steps=[
                "Define domain events for state changes",
                "Create event store",
                "Implement aggregate reconstruction from events",
                "Add projections for read models",
            ],
            benefits=[
                "Complete audit trail",
                "Temporal queries",
                "Replay for debugging",
            ],
            risks=[
                "Significant paradigm shift",
                "Eventual consistency",
            ],
            related_schemas=["CQRS_SEPARATION", "SAGA_PATTERN"],
        )
        
        # SAGA_PATTERN
        self._schemas["SAGA_PATTERN"] = OptimizationSchema(
            id="SAGA_PATTERN",
            name="Saga Pattern",
            category=SchemaCategory.ARCHITECTURE,
            description="Manage distributed transactions with compensating actions",
            when_to_apply="Distributed transactions across services",
            effort=Effort.HIGH,
            steps=[
                "Identify transaction boundaries",
                "Define compensating actions for each step",
                "Implement saga orchestrator or choreography",
                "Handle partial failures gracefully",
            ],
            benefits=[
                "Maintains consistency across services",
                "No distributed locks needed",
            ],
            risks=[
                "Complex error handling",
                "Eventually consistent",
            ],
            related_schemas=["EVENT_SOURCING"],
        )
        
        # FACTORY_METHOD
        self._schemas["FACTORY_METHOD"] = OptimizationSchema(
            id="FACTORY_METHOD",
            name="Factory Method",
            category=SchemaCategory.REFACTORING,
            description="Centralize object creation logic",
            when_to_apply="Scattered object creation with complex setup",
            effort=Effort.LOW,
            steps=[
                "Identify repeated object creation patterns",
                "Create factory class or method",
                "Move creation logic to factory",
                "Replace direct instantiation with factory calls",
            ],
            benefits=[
                "Single place for creation logic",
                "Easy to change implementations",
                "Testable with mock factories",
            ],
            risks=["Over-abstraction"],
            related_schemas=["BUILDER_PATTERN", "DEPENDENCY_INJECTION"],
        )
        
        # STRATEGY_PATTERN
        self._schemas["STRATEGY_PATTERN"] = OptimizationSchema(
            id="STRATEGY_PATTERN",
            name="Strategy Pattern",
            category=SchemaCategory.REFACTORING,
            description="Replace conditionals with polymorphism",
            when_to_apply="Switch/if-else chains based on type or strategy",
            effort=Effort.MEDIUM,
            steps=[
                "Define strategy interface",
                "Create concrete strategies for each case",
                "Replace conditionals with strategy dispatch",
                "Use dependency injection for strategy selection",
            ],
            benefits=[
                "Open/Closed Principle",
                "Easy to add new strategies",
                "Testable strategies in isolation",
            ],
            risks=["More classes to maintain"],
            related_schemas=["FACTORY_METHOD"],
        )
        
        # DEPENDENCY_INJECTION
        self._schemas["DEPENDENCY_INJECTION"] = OptimizationSchema(
            id="DEPENDENCY_INJECTION",
            name="Dependency Injection",
            category=SchemaCategory.ARCHITECTURE,
            description="Inject dependencies instead of hard-coding them",
            when_to_apply="Hard-coded dependencies in constructors",
            effort=Effort.MEDIUM,
            steps=[
                "Define interface for dependency",
                "Accept dependency through constructor",
                "Configure DI container or manual wiring",
                "Create mock implementations for testing",
            ],
            benefits=[
                "Testable with mocks",
                "Swappable implementations",
                "Loose coupling",
            ],
            risks=["DI container complexity"],
            related_schemas=["REPOSITORY_PATTERN", "SERVICE_EXTRACTION"],
        )
        
        # ERROR_HANDLING
        self._schemas["ERROR_HANDLING"] = OptimizationSchema(
            id="ERROR_HANDLING",
            name="Error Handling",
            category=SchemaCategory.REFACTORING,
            description="Standardize exception handling patterns",
            when_to_apply="Inconsistent exception handling across codebase",
            effort=Effort.LOW,
            steps=[
                "Define domain-specific exception hierarchy",
                "Create error codes or types",
                "Implement global exception handler",
                "Log errors with context",
                "Return consistent error responses",
            ],
            benefits=[
                "Consistent error messages",
                "Easier debugging",
                "Better user experience",
            ],
            risks=["Over-catching exceptions"],
            related_schemas=[],
        )
    
    # =========================================================================
    # Query Methods
    # =========================================================================
    
    def get(self, schema_id: str) -> Optional[OptimizationSchema]:
        """Get a schema by ID."""
        return self._schemas.get(schema_id)
    
    def get_all(self) -> List[OptimizationSchema]:
        """Get all schemas."""
        return list(self._schemas.values())
    
    def get_by_category(self, category: SchemaCategory) -> List[OptimizationSchema]:
        """Get schemas by category."""
        return [s for s in self._schemas.values() if s.category == category]
    
    def get_by_effort(self, effort: Effort) -> List[OptimizationSchema]:
        """Get schemas by effort level."""
        return [s for s in self._schemas.values() if s.effort == effort]
    
    def list_ids(self) -> List[str]:
        """List all schema IDs."""
        return list(self._schemas.keys())
    
    def count(self) -> int:
        """Get total number of schemas."""
        return len(self._schemas)


# Singleton instance
_schema_repository = None

def get_schema_repository() -> SchemaRepository:
    """Get the singleton schema repository."""
    global _schema_repository
    if _schema_repository is None:
        _schema_repository = SchemaRepository()
    return _schema_repository


if __name__ == "__main__":
    repo = get_schema_repository()
    
    print("Schema Repository Summary")
    print("=" * 50)
    print(f"Total schemas: {repo.count()}")
    print(f"\nSchemas by category:")
    for cat in SchemaCategory:
        schemas = repo.get_by_category(cat)
        if schemas:
            print(f"  {cat.value}: {len(schemas)}")
            for s in schemas:
                print(f"    - {s.name} [{s.effort.value}]")
    
    print(f"\nAll schema IDs:")
    for sid in sorted(repo.list_ids()):
        print(f"  {sid}")
