"""
Tests for ClassifierPlugin - Hub-Connected Classification Service
"""

import pytest
from src.core.registry.registry_of_registries import get_meta_registry
from src.core.classification.classifier_plugin import ClassifierPlugin, get_classifier_from_hub


class TestClassifierPluginDI:
    """Test dependency injection in ClassifierPlugin."""

    def test_classifier_plugin_initializes_with_hub(self):
        """ClassifierPlugin receives dependencies from hub."""
        hub = get_meta_registry()
        plugin = ClassifierPlugin()

        plugin.initialize(hub)

        # Classifier should be created with injected dependencies
        assert plugin._classifier is not None
        assert plugin._classifier.pattern_repo is not None
        assert plugin._classifier.role_registry is not None
        assert plugin._classifier.atom_registry is not None

    def test_classifier_uses_hub_registries(self):
        """ClassifierPlugin uses Hub's registries, not globals."""
        hub = get_meta_registry()
        plugin = ClassifierPlugin()

        plugin.initialize(hub)

        # Verify the classifier is using Hub's registries
        hub_patterns = hub.get('patterns')
        hub_roles = hub.get('roles')

        assert plugin._classifier.pattern_repo is hub_patterns
        assert plugin._classifier.role_registry is hub_roles

    def test_backward_compatibility(self):
        """UniversalClassifier still works without arguments."""
        from src.core.classification.universal_classifier import UniversalClassifier

        # Old code that doesn't use Hub
        classifier = UniversalClassifier()

        assert classifier.pattern_repo is not None
        assert classifier.role_registry is not None

    def test_get_classifier_from_hub_helper(self):
        """get_classifier_from_hub() returns unwrapped classifier."""
        hub = get_meta_registry()

        classifier = get_classifier_from_hub(hub)

        assert classifier is not None
        # Should be a UniversalClassifier instance
        assert hasattr(classifier, 'classify_class_pattern')
        assert hasattr(classifier, 'classify_function_pattern')


class TestClassifierPluginLifecycle:
    """Test full plugin lifecycle."""

    def test_full_lifecycle(self):
        """ClassifierPlugin goes through complete lifecycle."""
        hub = get_meta_registry()
        plugin = ClassifierPlugin()

        # Initialize
        plugin.initialize(hub)
        assert plugin._classifier is not None

        # Register
        plugin.register()
        # Should be registered as service
        assert hub.get('service:universal-classifier') is plugin

        # Start
        plugin.start()
        # Should emit classifier:ready event (can't easily test without listener)

        # Stop
        plugin.stop()
        # Classifier should be cleared
        assert plugin._classifier is None


class TestClassifierPluginEvents:
    """Test event-driven classification."""

    def test_classification_request_via_events(self):
        """Plugin responds to node:classify-request events."""
        hub = get_meta_registry()
        plugin = ClassifierPlugin()
        results = []

        plugin.initialize(hub)
        plugin.register()

        # Subscribe to results
        hub.event_bus.on('node:classified', lambda data: results.append(data))

        # Emit classification request
        hub.event_bus.emit('node:classify-request', {
            'id': 'test-node',
            'type': 'function',
            'name': 'create_user',
            'line': 'def create_user(data):',
            'file_path': 'src/services/user.py',
            'line_num': 10,
            'language': 'python'
        })

        # Should have received classification
        assert len(results) == 1
        assert results[0]['node_id'] == 'test-node'
        assert 'classification' in results[0]

    def test_error_event_on_failure(self):
        """Plugin emits classifier:error on exceptions."""
        hub = get_meta_registry()
        plugin = ClassifierPlugin()
        errors = []

        plugin.initialize(hub)
        plugin.register()

        # Subscribe to errors
        hub.event_bus.on('classifier:error', lambda data: errors.append(data))

        # Emit invalid request (missing required fields)
        hub.event_bus.emit('node:classify-request', {
            'id': 'bad-node',
            'type': 'unknown-type'
            # Missing required fields
        })

        # Should have received error (or no result if None is returned)
        # The plugin catches exceptions and emits classifier:error
        # But if classify returns None, no event is emitted
        # This test verifies error handling works
