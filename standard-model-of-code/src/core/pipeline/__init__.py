"""
Pipeline Package for Collider.

Provides:
- BaseStage: Abstract base class for all pipeline stages
- PipelineManager: Orchestrates stage execution

The 18-stage Collider pipeline processes codebases through:
1-2. AST/Structure extraction
3-4. Reference/Edge analysis
5-6. Classification (atoms, dimensions)
7-8. Pattern detection
9-10. Purpose/Flow analysis
11-12. Performance prediction
13-14. Health assessment
15-16. Report generation
17-18. Visualization output

Note: Import CodebaseState from data_management directly.
"""

from .base_stage import BaseStage
from .manager import PipelineManager

__all__ = [
    "BaseStage",
    "PipelineManager",
]
