"""
Classifier Plugin - Hub-Connected Universal Classifier
=======================================================
SMoC Role: Service | Domain: Classification

Hub-compatible wrapper for UniversalClassifier.
Uses BasePlugin pattern for proper dependency injection.

Usage:
    from src.core.registry.registry_of_registries import get_meta_registry
    from src.core.classification.classifier_plugin import ClassifierPlugin

    hub = get_meta_registry()
    plugin = ClassifierPlugin()
    plugin.initialize(hub)
    plugin.register()
    plugin.start()

    # Use via events
    hub.event_bus.emit('node:classify-request', {'name': 'MyClass', 'type': 'class'})

Part of: MODULE_CONVERSION_INVENTORY.md (Priority 1)
"""

from typing import Dict, Any, Optional
from ..plugin import ServicePlugin
from .universal_classifier import UniversalClassifier


class ClassifierPlugin(ServicePlugin):
    """
    Hub-connected classification service.

    Provides semantic classification via dependency injection instead of globals.
    Emits classification events for reactive downstream processing.
    """

    def __init__(self):
        super().__init__(
            name='universal-classifier',
            version='2.0.0',
            dependencies=['roles', 'patterns', 'atoms']
        )
        self._classifier: Optional[UniversalClassifier] = None

    def initialize(self, hub) -> None:
        """Resolve registries from hub and create classifier."""
        super().initialize(hub)

        # Proper dependency injection from Hub
        self._classifier = UniversalClassifier(
            pattern_repo=hub.get('patterns'),
            role_registry=hub.get('roles'),
            atom_registry=hub.get('atoms')
        )

    def register(self) -> None:
        """Register as service and subscribe to classification events."""
        super().register()  # Registers as 'service:universal-classifier'

        # Listen for classification requests
        self.hub.event_bus.on('node:classify-request', self._handle_classify_request)

        # Listen for pattern updates (future: hot-reload classifier)
        self.hub.event_bus.on('patterns:updated', self._handle_pattern_update)

    def start(self) -> None:
        """Signal ready."""
        self.hub.event_bus.emit('classifier:ready', {
            'name': self.name,
            'version': self.version
        })

    def stop(self) -> None:
        """Cleanup."""
        self.hub.event_bus.emit('classifier:stopped', {'name': self.name})
        self._classifier = None

    # Public API (service methods)

    def classify(self, node_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Classify a code node.

        Args:
            node_data: Node to classify (requires different fields based on method)

        Returns:
            Classification result with role, atom, confidence (or None if no match)
        """
        if not self._classifier:
            raise RuntimeError("Classifier not initialized")

        # Route to appropriate classifier method based on available data
        result = None

        if 'symbol' in node_data:
            # Extracted symbol from tree-sitter
            result = self._classifier.classify_extracted_symbol(**node_data['symbol'])
        elif node_data.get('type') in ('class', 'interface', 'type'):
            # Class-like node
            result = self._classifier.classify_class_pattern(
                line=node_data.get('line', ''),
                line_num=node_data.get('line_num', 0),
                file_path=node_data.get('file_path', '')
            )
        elif node_data.get('type') in ('function', 'method'):
            # Function-like node
            result = self._classifier.classify_function_pattern(
                line=node_data.get('line', ''),
                line_num=node_data.get('line_num', 0),
                file_path=node_data.get('file_path', ''),
                language=node_data.get('language', 'python')
            )

        # Emit event for observers
        if result:
            self.hub.event_bus.emit('node:classified', {
                'node_id': node_data.get('id'),
                'classification': result
            })

        return result

    # Event Handlers

    def _handle_classify_request(self, data: Dict[str, Any]) -> None:
        """Handle classification request via event."""
        try:
            self.classify(data)  # Emits node:classified event
        except Exception as e:
            self.hub.event_bus.emit('classifier:error', {
                'node_id': data.get('id'),
                'error': str(e)
            })

    def _handle_pattern_update(self, data: Dict[str, Any]) -> None:
        """Handle pattern registry updates (hot-reload)."""
        # Future: Recreate classifier with new patterns
        # For now, just log
        self.hub.event_bus.emit('classifier:reloaded', {
            'pattern_count': data.get('count', 0)
        })


# Helper function for backward compatibility
def get_classifier_from_hub(hub) -> UniversalClassifier:
    """
    Get classifier service from hub (backward compatibility helper).

    Args:
        hub: RegistryOfRegistries instance

    Returns:
        UniversalClassifier instance (unwrapped)

    Raises:
        RuntimeError: If classifier not available

    Usage:
        hub = get_meta_registry()
        classifier = get_classifier_from_hub(hub)
        result = classifier.classify_class_pattern(...)
    """
    plugin = hub.get('service:universal-classifier')
    if plugin and hasattr(plugin, '_classifier') and plugin._classifier:
        return plugin._classifier

    # Fallback: Create and register
    plugin = ClassifierPlugin()
    plugin.initialize(hub)
    plugin.register()
    plugin.start()

    assert plugin._classifier is not None, "Failed to initialize classifier"
    return plugin._classifier
