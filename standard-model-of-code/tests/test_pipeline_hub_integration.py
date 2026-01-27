"""
Tests for PipelineManager Hub Integration
"""

import pytest
from src.core.pipeline.manager import PipelineManager
from src.core.pipeline.base_stage import BaseStage
from src.core.data_management import CodebaseState
from src.core.registry.registry_of_registries import get_meta_registry


class MockStage(BaseStage):
    """Mock stage for testing."""

    def __init__(self, name):
        self._name = name
        self.executed = False

    @property
    def name(self):
        return self._name

    def validate_input(self, state):
        return True

    def execute(self, state):
        self.executed = True
        state.metadata[self.name] = 'executed'
        return state

    def validate_output(self, state):
        return True


class TestPipelineBackwardCompatibility:
    """Test PipelineManager works WITHOUT Hub (backward compatibility)."""

    def test_pipeline_runs_without_hub(self):
        """Pipeline executes stages without Hub reference."""
        state = CodebaseState(target_path='.')
        stage1 = MockStage('stage1')
        stage2 = MockStage('stage2')

        pipeline = PipelineManager(stages=[stage1, stage2])
        result = pipeline.run(state)

        assert stage1.executed
        assert stage2.executed
        assert result.metadata['stage1'] == 'executed'
        assert result.metadata['stage2'] == 'executed'

    def test_pipeline_callbacks_still_work(self):
        """Old callback pattern still functional."""
        state = CodebaseState(target_path='.')
        stage = MockStage('test')
        started = []
        completed = []

        pipeline = PipelineManager(
            stages=[stage],
            on_stage_start=lambda s: started.append(s.name),
            on_stage_complete=lambda s, ms: completed.append((s.name, ms))
        )

        pipeline.run(state)

        assert 'test' in started
        assert completed[0][0] == 'test'
        assert completed[0][1] > 0  # Duration in ms


class TestPipelineHubIntegration:
    """Test PipelineManager WITH Hub (new pattern)."""

    def test_pipeline_emits_events_when_hub_provided(self):
        """Pipeline emits events via Hub's EventBus."""
        hub = get_meta_registry()
        state = CodebaseState(target_path='.')
        stage = MockStage('test-stage')

        events = []

        # Subscribe to pipeline events
        hub.event_bus.on('pipeline:started', lambda d: events.append(('started', d)))
        hub.event_bus.on('pipeline:stage:started', lambda d: events.append(('stage_start', d)))
        hub.event_bus.on('pipeline:stage:complete', lambda d: events.append(('stage_done', d)))
        hub.event_bus.on('pipeline:complete', lambda d: events.append(('done', d)))

        # Run pipeline with Hub
        pipeline = PipelineManager(stages=[stage], hub=hub)
        pipeline.run(state)

        # Verify events emitted
        event_types = [e[0] for e in events]
        assert 'started' in event_types
        assert 'stage_start' in event_types
        assert 'stage_done' in event_types
        assert 'done' in event_types

    def test_stage_events_include_metadata(self):
        """Stage events include useful metadata."""
        hub = get_meta_registry()
        state = CodebaseState(target_path='.')
        stage = MockStage('analyzer')

        stage_events = []
        hub.event_bus.on('pipeline:stage:complete', lambda d: stage_events.append(d))

        pipeline = PipelineManager(stages=[stage], hub=hub)
        pipeline.run(state)

        assert len(stage_events) == 1
        event_data = stage_events[0]

        assert event_data['stage'] == 'analyzer'
        assert 'duration_ms' in event_data
        assert event_data['duration_ms'] > 0

    def test_pipeline_complete_event_has_summary(self):
        """Pipeline complete event includes summary stats."""
        hub = get_meta_registry()
        state = CodebaseState(target_path='.')
        stages = [MockStage(f'stage{i}') for i in range(3)]

        complete_events = []
        hub.event_bus.on('pipeline:complete', lambda d: complete_events.append(d))

        pipeline = PipelineManager(stages=stages, hub=hub)
        pipeline.run(state)

        assert len(complete_events) == 1
        summary = complete_events[0]

        assert 'total_duration_ms' in summary
        assert summary['stages_executed'] == 3

    def test_hub_and_callbacks_both_work(self):
        """Hub events and legacy callbacks both fire."""
        hub = get_meta_registry()
        state = CodebaseState(target_path='.')
        stage = MockStage('test')

        callback_fired = []
        event_fired = []

        hub.event_bus.on('pipeline:stage:started', lambda d: event_fired.append(d))

        pipeline = PipelineManager(
            stages=[stage],
            hub=hub,
            on_stage_start=lambda s: callback_fired.append(s.name)
        )

        pipeline.run(state)

        # Both patterns should work
        assert 'test' in callback_fired
        assert len(event_fired) == 1
        assert event_fired[0]['stage'] == 'test'


class TestPipelineSkippedStages:
    """Test event emission for skipped stages."""

    def test_skipped_stage_emits_event(self):
        """Skipped stages emit pipeline:stage:skipped event."""
        hub = get_meta_registry()
        state = CodebaseState(target_path='.')

        class FailingStage(BaseStage):
            @property
            def name(self):
                return 'failing-stage'

            def validate_input(self, state):
                return False  # Always fails validation

            def execute(self, state):
                raise RuntimeError("Should not execute")

            def validate_output(self, state):
                return True

        skipped_events = []
        hub.event_bus.on('pipeline:stage:skipped', lambda d: skipped_events.append(d))

        pipeline = PipelineManager(stages=[FailingStage()], hub=hub)
        pipeline.run(state)

        assert len(skipped_events) == 1
        assert skipped_events[0]['stage'] == 'failing-stage'
        assert skipped_events[0]['reason'] == 'input_validation_failed'
