"""
Tests for Hub Integration - RegistryOfRegistries + EventBus + Plugins
"""

import pytest
from src.core.registry.registry_of_registries import get_meta_registry, RegistryOfRegistries
from src.core.event_bus import EventBus
from src.core.plugin import BasePlugin


class TestHubBasics:
    """Test basic Hub functionality."""

    def test_hub_singleton(self):
        """get_meta_registry() returns singleton."""
        hub1 = get_meta_registry()
        hub2 = get_meta_registry()
        assert hub1 is hub2

    def test_hub_has_event_bus(self):
        """Hub has event_bus property."""
        hub = get_meta_registry()
        assert hasattr(hub, 'event_bus')
        assert isinstance(hub.event_bus, EventBus)

    def test_hub_has_registries(self):
        """Hub provides access to core registries."""
        hub = get_meta_registry()

        registries = hub.list_registries()

        # Should have at least: roles, patterns, schemas, workflows
        assert 'roles' in registries
        assert 'patterns' in registries
        assert 'schemas' in registries
        assert 'workflows' in registries

    def test_hub_status_report(self):
        """status_report() includes event_bus."""
        hub = get_meta_registry()
        report = hub.status_report()

        assert 'event_bus' in report
        assert 'Active' in report['event_bus']


class TestPluginIntegration:
    """Test BasePlugin integration with Hub."""

    def test_plugin_lifecycle(self):
        """Plugin can go through full lifecycle."""
        hub = get_meta_registry()

        # Create test plugin
        class TestPlugin(BasePlugin):
            def __init__(self):
                super().__init__(name='test', version='1.0.0')
                self.started = False
                self.stopped = False

            def register(self):
                pass

            def start(self):
                self.started = True

            def stop(self):
                self.stopped = True

        plugin = TestPlugin()

        # Lifecycle
        plugin.initialize(hub)
        plugin.register()
        plugin.start()
        plugin.stop()

        assert plugin.started
        assert plugin.stopped

    def test_plugin_can_access_registries(self):
        """Plugin can access registries via hub."""
        hub = get_meta_registry()

        class TestPlugin(BasePlugin):
            def __init__(self):
                super().__init__(
                    name='test',
                    version='1.0.0',
                    dependencies=['roles']
                )
                self.roles_registry = None

            def initialize(self, hub):
                super().initialize(hub)
                self.roles_registry = hub.get('roles')

            def register(self):
                pass

            def start(self):
                pass

            def stop(self):
                pass

        plugin = TestPlugin()
        plugin.initialize(hub)

        assert plugin.roles_registry is not None

    def test_plugin_dependency_validation(self):
        """Plugin initialization fails if dependencies missing."""
        hub = get_meta_registry()

        class TestPlugin(BasePlugin):
            def __init__(self):
                super().__init__(
                    name='test',
                    version='1.0.0',
                    dependencies=['nonexistent-registry']
                )

            def register(self):
                pass

            def start(self):
                pass

            def stop(self):
                pass

        plugin = TestPlugin()

        with pytest.raises(ValueError, match='requires registry'):
            plugin.initialize(hub)


class TestEventDrivenPlugins:
    """Test plugin communication via EventBus."""

    def test_plugins_communicate_via_events(self):
        """Two plugins can communicate via hub event bus."""
        hub = get_meta_registry()
        messages = []

        # Producer plugin
        class Producer(BasePlugin):
            def __init__(self):
                super().__init__(name='producer', version='1.0.0')

            def register(self):
                pass

            def start(self):
                self.hub.event_bus.emit('data:ready', {'value': 42})

            def stop(self):
                pass

        # Consumer plugin
        class Consumer(BasePlugin):
            def __init__(self):
                super().__init__(name='consumer', version='1.0.0')

            def register(self):
                self.hub.event_bus.on('data:ready', lambda d: messages.append(d))

            def start(self):
                pass

            def stop(self):
                pass

        # Lifecycle
        producer = Producer()
        consumer = Consumer()

        producer.initialize(hub)
        consumer.initialize(hub)

        producer.register()
        consumer.register()

        producer.start()  # Emits event
        consumer.start()

        # Consumer should have received message
        assert len(messages) == 1
        assert messages[0] == {'value': 42}

    def test_plugin_error_isolation(self):
        """One plugin's error doesn't crash another."""
        hub = get_meta_registry()
        successful_calls = []

        class FailingPlugin(BasePlugin):
            def __init__(self):
                super().__init__(name='failing', version='1.0.0')

            def register(self):
                def failing_handler(data):
                    raise ValueError("Handler failed")

                self.hub.event_bus.on('test:event', failing_handler)

            def start(self):
                pass

            def stop(self):
                pass

        class WorkingPlugin(BasePlugin):
            def __init__(self):
                super().__init__(name='working', version='1.0.0')

            def register(self):
                self.hub.event_bus.on('test:event', lambda d: successful_calls.append(d))

            def start(self):
                pass

            def stop(self):
                pass

        failing = FailingPlugin()
        working = WorkingPlugin()

        failing.initialize(hub)
        working.initialize(hub)

        failing.register()
        working.register()

        # Emit event
        hub.event_bus.emit('test:event', 'data')

        # Working plugin should succeed despite failing plugin
        assert 'data' in successful_calls


class TestHubAsServiceLocator:
    """Test Hub's service locator pattern."""

    def test_register_and_get_service(self):
        """Hub can register and retrieve services."""
        hub = get_meta_registry()

        class MyService:
            def get_data(self):
                return {'value': 42}

        service = MyService()
        hub.register('my-service', service)

        retrieved = hub.get('my-service')
        assert retrieved is service
        assert retrieved.get_data() == {'value': 42}

    def test_service_plugin_auto_registers(self):
        """ServicePlugin automatically registers as service."""
        from src.core.plugin import ServicePlugin

        hub = get_meta_registry()

        class MyService(ServicePlugin):
            def __init__(self):
                super().__init__(name='auto-service', version='1.0.0')

            def start(self):
                pass

            def stop(self):
                pass

            def get_value(self):
                return 123

        service = MyService()
        service.initialize(hub)
        service.register()  # Auto-registers as 'service:auto-service'

        # Should be retrievable
        retrieved = hub.get('service:auto-service')
        assert retrieved is service
        assert retrieved.get_value() == 123
