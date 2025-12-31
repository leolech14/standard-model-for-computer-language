"""
Insights Models
===============

Enums and dataclasses for the insights engine.
"""

from typing import List, Optional
from dataclasses import dataclass
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
