"""
base_stage.py

Abstract Base Class for all Pipeline Stages.
Provides a uniform interface for the 18-stage Collider pipeline.

Following the pattern from EdgeExtractionStrategy(ABC) at edge_extractor.py:415.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..data_management import CodebaseState


class BaseStage(ABC):
    """
    Abstract base class for pipeline stages.

    All pipeline stages must implement:
    - name: Stage identifier for logging/metrics
    - execute(): The core processing logic

    Optional:
    - validate_input(): Pre-condition checks
    - validate_output(): Post-condition checks
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stage identifier (e.g., 'ast_extraction', 'edge_analysis')."""
        pass

    @property
    def stage_number(self) -> Optional[int]:
        """Optional stage number for ordering (e.g., 1, 2, 3)."""
        return None

    @abstractmethod
    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Execute the stage's core logic.

        Args:
            state: The current CodebaseState to process/enrich.

        Returns:
            The modified CodebaseState (may be same object, mutated).
        """
        pass

    def validate_input(self, state: "CodebaseState") -> bool:
        """
        Validate preconditions before execution.
        Override in subclasses for stage-specific validation.

        Returns:
            True if state is valid for this stage, False otherwise.
        """
        return True

    def validate_output(self, state: "CodebaseState") -> bool:
        """
        Validate postconditions after execution.
        Override in subclasses for stage-specific validation.

        Returns:
            True if stage produced valid output, False otherwise.
        """
        return True

    def __repr__(self) -> str:
        if self.stage_number is not None:
            return f"<{self.__class__.__name__} stage={self.stage_number} name='{self.name}'>"
        return f"<{self.__class__.__name__} name='{self.name}'>"
