"""
Registry Package

Centralized repositories for code analysis data:

- pattern_repository.py: Role detection patterns (prefix, suffix, dunder, etc.)
- schema_repository.py: Optimization schemas (13 patterns with instructions)
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
]
