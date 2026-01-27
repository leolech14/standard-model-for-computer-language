"""
manager.py

Pipeline Manager for orchestrating stage execution.
Coordinates the 18-stage Collider analysis pipeline.

Hub Integration:
- Accepts Hub reference for service access
- Emits events via EventBus (replaces callbacks)
- Stages can request services from Hub
"""

import time
from typing import List, Optional, Callable, TYPE_CHECKING

from .base_stage import BaseStage

if TYPE_CHECKING:
    from ..data_management import CodebaseState
    from ..observability import PerformanceManager
    from ..registry.registry_of_registries import RegistryOfRegistries


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
        hub: Optional["RegistryOfRegistries"] = None,
    ):
        """
        Initialize the pipeline manager.

        Args:
            stages: List of stages to execute in order.
            perf_manager: Optional PerformanceManager for detailed metrics.
            on_stage_start: Optional callback when a stage begins (DEPRECATED - use hub events).
            on_stage_complete: Optional callback when a stage ends (DEPRECATED - use hub events).
            hub: Optional Hub reference for service access and EventBus.

        Hub Integration:
            If hub provided, emits events via hub.event_bus:
            - 'pipeline:stage:started' - {stage: str, phase: int}
            - 'pipeline:stage:complete' - {stage: str, duration_ms: float}
            - 'pipeline:started' - {stage_count: int}
            - 'pipeline:complete' - {total_duration_ms: float}
        """
        self.stages = stages
        self._perf_manager = perf_manager
        self._on_stage_start = on_stage_start
        self._on_stage_complete = on_stage_complete
        self.hub = hub  # Hub reference for service access and events

    def run(self, state: "CodebaseState") -> "CodebaseState":
        """
        Execute all stages in sequence.

        Args:
            state: Initial CodebaseState to process.

        Returns:
            Final CodebaseState after all stages complete.
        """
        pipeline_start = time.perf_counter()

        # Emit pipeline started event
        if self.hub and self.hub.event_bus:
            self.hub.event_bus.emit('pipeline:started', {
                'stage_count': len(self.stages),
                'stages': [s.name for s in self.stages]
            })

        for stage in self.stages:
            # Notify start (callbacks for backward compatibility)
            if self._on_stage_start:
                self._on_stage_start(stage)

            # Emit event (new pattern)
            if self.hub and self.hub.event_bus:
                self.hub.event_bus.emit('pipeline:stage:started', {
                    'stage': stage.name,
                    'phase': getattr(stage, 'stage_number', None)
                })

            # Validate input
            if not stage.validate_input(state):
                print(f"  [Pipeline] WARN: {stage.name} input validation failed, skipping")
                if self.hub and self.hub.event_bus:
                    self.hub.event_bus.emit('pipeline:stage:skipped', {
                        'stage': stage.name,
                        'reason': 'input_validation_failed'
                    })
                continue

            # Execute with timing
            start_time = time.perf_counter()
            state = stage.execute(state)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            # Validate output
            if not stage.validate_output(state):
                print(f"  [Pipeline] WARN: {stage.name} output validation failed")

            # Notify complete (callbacks for backward compatibility)
            if self._on_stage_complete:
                self._on_stage_complete(stage, elapsed_ms)

            # Emit event (new pattern)
            if self.hub and self.hub.event_bus:
                self.hub.event_bus.emit('pipeline:stage:complete', {
                    'stage': stage.name,
                    'duration_ms': elapsed_ms,
                    'node_count': len(state.nodes) if hasattr(state, 'nodes') else 0
                })

        # Emit pipeline complete
        pipeline_elapsed = (time.perf_counter() - pipeline_start) * 1000
        if self.hub and self.hub.event_bus:
            self.hub.event_bus.emit('pipeline:complete', {
                'total_duration_ms': pipeline_elapsed,
                'final_node_count': len(state.nodes) if hasattr(state, 'nodes') else 0,
                'stages_executed': len(self.stages)
            })

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
