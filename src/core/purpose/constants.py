"""
Purpose Field Constants
=======================

Single source of truth for all purpose-related enums, mappings, and rules.
"""

from enum import Enum
from typing import Dict, FrozenSet


class Layer(Enum):
    """Architectural layers (purpose zones)"""
    PRESENTATION = "presentation"      # User interface, display
    APPLICATION = "application"        # Use cases, orchestration
    DOMAIN = "domain"                  # Business rules, entities
    INFRASTRUCTURE = "infrastructure"  # Technical details, persistence
    TESTING = "testing"                # Test code, fixtures, assertions
    UNKNOWN = "unknown"


# Layer order for dependency validation (lower = higher in architecture)
LAYER_ORDER: Dict[Layer, int] = {
    Layer.PRESENTATION: 0,
    Layer.APPLICATION: 1,
    Layer.DOMAIN: 2,
    Layer.INFRASTRUCTURE: 3,
    Layer.TESTING: 4,
    Layer.UNKNOWN: 99,
}


# Layer purpose descriptions
LAYER_PURPOSES: Dict[Layer, str] = {
    Layer.PRESENTATION: "Display data and handle user interaction",
    Layer.APPLICATION: "Orchestrate use cases and coordinate domain",
    Layer.DOMAIN: "Express and enforce business rules",
    Layer.INFRASTRUCTURE: "Handle technical concerns and external systems",
    Layer.TESTING: "Verify behavior and validate expectations",
    Layer.UNKNOWN: "Purpose not yet determined",
}


# Role to Layer mapping (covers all 27 roles from Standard Model)
ROLE_TO_LAYER: Dict[str, Layer] = {
    # PRESENTATION - User interface, display, I/O
    "Controller": Layer.PRESENTATION,
    "APILayer": Layer.PRESENTATION,
    "View": Layer.PRESENTATION,
    "CLI": Layer.PRESENTATION,

    # APPLICATION - Use cases, orchestration, coordination
    "ApplicationService": Layer.APPLICATION,
    "UseCase": Layer.APPLICATION,
    "Orchestrator": Layer.APPLICATION,
    "Command": Layer.APPLICATION,
    "Query": Layer.APPLICATION,
    "EventHandler": Layer.APPLICATION,

    # DOMAIN - Business rules, entities, logic
    "Service": Layer.DOMAIN,
    "DomainService": Layer.DOMAIN,
    "Entity": Layer.DOMAIN,
    "ValueObject": Layer.DOMAIN,
    "Policy": Layer.DOMAIN,
    "Specification": Layer.DOMAIN,
    "DTO": Layer.DOMAIN,
    "Validator": Layer.DOMAIN,
    "Factory": Layer.DOMAIN,
    "Observer": Layer.DOMAIN,
    "Mapper": Layer.DOMAIN,

    # INFRASTRUCTURE - Technical concerns, persistence, external systems
    "Repository": Layer.INFRASTRUCTURE,
    "DataAccess": Layer.INFRASTRUCTURE,
    "Gateway": Layer.INFRASTRUCTURE,
    "Adapter": Layer.INFRASTRUCTURE,
    "Configuration": Layer.INFRASTRUCTURE,
    "Utility": Layer.INFRASTRUCTURE,
    "Internal": Layer.INFRASTRUCTURE,
    "Exception": Layer.INFRASTRUCTURE,
    "Lifecycle": Layer.INFRASTRUCTURE,

    # TESTING - Test code layer
    "Test": Layer.TESTING,
    "Fixture": Layer.TESTING,
}


# Emergence rules: child purposes → composite purpose
# Note: frozenset order doesn't matter, so avoid duplicates
EMERGENCE_RULES: Dict[FrozenSet[str], str] = {
    # Repository patterns (data access layer)
    frozenset(["Query"]): "DataAccess",
    frozenset(["Query", "Command"]): "Repository",  # Primary CRUD pattern
    frozenset(["Query", "Command", "Factory"]): "Repository",

    # Service patterns (requires Validator to distinguish from Repository)
    frozenset(["Command", "Query", "Validator"]): "Service",
    frozenset(["UseCase"]): "ApplicationService",

    # Test patterns
    frozenset(["Test"]): "TestSuite",
    frozenset(["Test", "Fixture"]): "TestSuite",

    # Transformer patterns
    frozenset(["Mapper"]): "Transformer",
    frozenset(["Mapper", "Factory"]): "Transformer",

    # Controller patterns
    frozenset(["Controller"]): "APILayer",
    frozenset(["Controller", "Validator"]): "APILayer",
}


# Name patterns for layer inference (fallback)
LAYER_NAME_PATTERNS: Dict[Layer, tuple] = {
    Layer.PRESENTATION: ('controller', 'view', 'route', 'endpoint', 'api'),
    Layer.APPLICATION: ('service', 'usecase', 'handler', 'orchestrator'),
    Layer.DOMAIN: ('entity', 'model', 'domain', 'policy', 'specification'),
    Layer.INFRASTRUCTURE: ('repository', 'gateway', 'adapter', 'config', 'db'),
    Layer.TESTING: ('test', 'spec', 'fixture', 'mock'),
}
