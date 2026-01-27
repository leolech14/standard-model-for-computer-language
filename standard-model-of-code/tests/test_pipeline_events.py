"""
Tests for PipelineManager EventBus Integration
"""

from src.core.pipeline.manager import PipelineManager
from src.core.pipeline.base_stage import BaseStage
from src.core.registry.registry_of_registries import get_meta_registry


class SimpleState:
    """Minimal state object for testing."""
    def __init__(self):
        self.nodes = {}
        self.metadata = {}


class TestStage(BaseStage):
    """Test stage that does minimal work."""

    def __init__(self, name):
        self._name = name
        self.executed = False

    @property
    def name(self):
        return self._name

    @property
    def stage_number(self):
        return 1

    def validate_input(self, state):
        return True

    def execute(self, state):
        self.executed = True
        state.metadata[self.name] = 'done'
        return state

    def validate_output(self, state):
        return True


class TestPipelineEvents:
    """Test PipelineManager event emission."""

    def test_pipeline_emits_started_event(self):
        """Pipeline emits 'pipeline:started' at beginning."""
        hub = get_meta_registry()
        state = SimpleState()
        stage = TestStage('test')

        events = []
        hub.event_bus.on('pipeline:started', lambda d: events.append(d))

        pipeline = PipelineManager(stages=[stage], hub=hub)
        pipeline.run(state)

        assert len(events) == 1
        assert events[0]['stage_count'] == 1
        assert 'test' in events[0]['stages']

    def test_pipeline_emits_stage_events(self):
        """Pipeline emits events for each stage."""
        hub = get_meta_registry()
        state = SimpleState()
        stage = TestStage('analyzer')

        started = []
        completed = []

        hub.event_bus.on('pipeline:stage:started', lambda d: started.append(d))
        hub.event_bus.on('pipeline:stage:complete', lambda d: completed.append(d))

        pipeline = PipelineManager(stages=[stage], hub=hub)
        pipeline.run(state)

        # Started event
        assert len(started) == 1
        assert started[0]['stage'] == 'analyzer'
        assert started[0]['phase'] == 1

        # Complete event
        assert len(completed) == 1
        assert completed[0]['stage'] == 'analyzer'
        assert 'duration_ms' in completed[0]

    def test_pipeline_emits_complete_event(self):
        """Pipeline emits 'pipeline:complete' at end."""
        hub = get_meta_registry()
        state = SimpleState()
        stages = [TestStage(f's{i}') for i in range(3)]

        events = []
        hub.event_bus.on('pipeline:complete', lambda d: events.append(d))

        pipeline = PipelineManager(stages=stages, hub=hub)
        pipeline.run(state)

        assert len(events) == 1
        assert 'total_duration_ms' in events[0]
        assert events[0]['stages_executed'] == 3

    def test_backward_compatibility_without_hub(self):
        """Pipeline still works without Hub (no events emitted)."""
        state = SimpleState()
        stage = TestStage('test')

        # No hub provided - should not crash
        pipeline = PipelineManager(stages=[stage])
        result = pipeline.run(state)

        assert stage.executed
        assert result.metadata['test'] == 'done'

    def test_callbacks_and_events_coexist(self):
        """Legacy callbacks and new events both fire."""
        hub = get_meta_registry()
        state = SimpleState()
        stage = TestStage('test')

        callback_calls = []
        event_calls = []

        hub.event_bus.on('pipeline:stage:complete', lambda d: event_calls.append(d))

        pipeline = PipelineManager(
            stages=[stage],
            hub=hub,
            on_stage_complete=lambda s, ms: callback_calls.append((s.name, ms))
        )

        pipeline.run(state)

        # Both should fire
        assert len(callback_calls) == 1
        assert callback_calls[0][0] == 'test'

        assert len(event_calls) == 1
        assert event_calls[0]['stage'] == 'test'
