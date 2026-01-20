"""
Registry Package

Centralized repositories for code analysis data:

- pattern_repository.py: Role detection patterns (prefix, suffix, dunder, etc.)
- schema_repository.py: Optimization schemas (13 patterns with instructions)
- role_registry.py: Canonical roles (33 WHY-dimension roles)
"""

from .pattern_repository import (
    PatternRepository,
    RolePattern,
    get_pattern_repository,
)

from .schema_repository import (
    SchemaRepository,
    OptimizationSchema,
    SchemaCategory,
    Effort,
    get_schema_repository,
)

from .role_registry import (
    RoleRegistry,
    Role,
    get_role_registry,
    ROLE_NORMALIZATION,
)

__all__ = [
    # Pattern repository
    'PatternRepository',
    'RolePattern',
    'get_pattern_repository',

    # Schema repository
    'SchemaRepository',
    'OptimizationSchema',
    'SchemaCategory',
    'Effort',
    'get_schema_repository',

    # Role registry
    'RoleRegistry',
    'Role',
    'get_role_registry',
    'ROLE_NORMALIZATION',
]
