"""
manager.py

Pipeline Manager for orchestrating stage execution.
Coordinates the 18-stage Collider analysis pipeline.
"""

import time
from typing import List, Optional, Callable, TYPE_CHECKING

from .base_stage import BaseStage

if TYPE_CHECKING:
    from ..data_management import CodebaseState
    from ..observability import PerformanceManager


class PipelineManager:
    """
    Orchestrates pipeline stage execution.

    Responsibilities:
    - Execute stages in order
    - Track timing per stage
    - Handle errors gracefully
    - Provide hooks for monitoring
    """

    def __init__(
        self,
        stages: List[BaseStage],
        perf_manager: Optional["PerformanceManager"] = None,
        on_stage_start: Optional[Callable[[BaseStage], None]] = None,
        on_stage_complete: Optional[Callable[[BaseStage, float], None]] = None,
    ):
        """
        Initialize the pipeline manager.

        Args:
            stages: List of stages to execute in order.
            perf_manager: Optional PerformanceManager for detailed metrics.
            on_stage_start: Optional callback when a stage begins.
            on_stage_complete: Optional callback when a stage ends (with duration_ms).
        """
        self.stages = stages
        self._perf_manager = perf_manager
        self._on_stage_start = on_stage_start
        self._on_stage_complete = on_stage_complete

    def run(self, state: "CodebaseState") -> "CodebaseState":
        """
        Execute all stages in sequence.

        Args:
            state: Initial CodebaseState to process.

        Returns:
            Final CodebaseState after all stages complete.
        """
        for stage in self.stages:
            # Notify start
            if self._on_stage_start:
                self._on_stage_start(stage)

            # Validate input
            if not stage.validate_input(state):
                print(f"  [Pipeline] WARN: {stage.name} input validation failed, skipping")
                continue

            # Execute with timing
            start_time = time.perf_counter()
            state = stage.execute(state)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Validate output
            if not stage.validate_output(state):
                print(f"  [Pipeline] WARN: {stage.name} output validation failed")

            # Notify complete
            if self._on_stage_complete:
                self._on_stage_complete(stage, elapsed_ms)

        return state

    def run_stage(self, stage_name: str, state: "CodebaseState") -> "CodebaseState":
        """
        Execute a single stage by name.

        Args:
            stage_name: Name of the stage to run.
            state: Current CodebaseState.

        Returns:
            Modified CodebaseState.

        Raises:
            ValueError: If stage_name not found.
        """
        for stage in self.stages:
            if stage.name == stage_name:
                return stage.execute(state)
        raise ValueError(f"Stage not found: {stage_name}")

    def list_stages(self) -> List[str]:
        """Return list of stage names in execution order."""
        return [s.name for s in self.stages]

    def __repr__(self) -> str:
        return f"<PipelineManager stages={len(self.stages)}>"
