"""
Base Plugin Interface - Universal Hub Module Contract
======================================================
SMoC Role: Infrastructure | Domain: Modularity

Defines the standard interface that all Hub-connected modules must implement.
Inspired by BaseStage but generalized for all module types (not just pipeline stages).

Usage:
    from src.core.plugin.base_plugin import BasePlugin
    from src.core.registry.registry_of_registries import RegistryOfRegistries

    class MyModule(BasePlugin):
        def __init__(self):
            super().__init__(name='my-module', version='1.0.0')

        def initialize(self, hub: RegistryOfRegistries) -> None:
            super().initialize(hub)
            self.my_data = hub.get('atoms')

        def register(self) -> None:
            self.hub.event_bus.on('data:ready', self.process)

        def start(self) -> None:
            print(f"{self.name} started")

        def stop(self) -> None:
            print(f"{self.name} stopped")

Part of: MODULAR_ARCHITECTURE_SYNTHESIS.md
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

# Forward reference to avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..registry.registry_of_registries import RegistryOfRegistries


class BasePlugin(ABC):
    """
    Base class for all Hub-connected modules.

    Lifecycle:
        1. __init__() - Construct with metadata
        2. initialize(hub) - Receive hub reference, resolve dependencies
        3. register() - Subscribe to events, register capabilities
        4. start() - Begin normal operation
        5. stop() - Graceful shutdown

    Subclasses must implement:
        - register() - What capabilities/events to wire up
        - start() - Startup logic
        - stop() - Cleanup logic
    """

    def __init__(
        self,
        name: str,
        version: str = '1.0.0',
        dependencies: Optional[List[str]] = None
    ):
        """
        Initialize plugin metadata.

        Args:
            name: Unique module identifier (e.g., 'universal-classifier')
            version: Semantic version (MAJOR.MINOR.PATCH)
            dependencies: Registry keys needed (e.g., ['roles', 'patterns'])
        """
        self._name = name
        self._version = version
        self._dependencies = dependencies or []
        self._hub: Optional['RegistryOfRegistries'] = None
        self._initialized = False

    @property
    def name(self) -> str:
        """Module name."""
        return self._name

    @property
    def version(self) -> str:
        """Module version."""
        return self._version

    @property
    def dependencies(self) -> List[str]:
        """Required registry keys."""
        return self._dependencies

    @property
    def hub(self) -> 'RegistryOfRegistries':
        """Hub reference (available after initialize())."""
        if self._hub is None:
            raise RuntimeError(f"Plugin {self.name} not initialized - call initialize(hub) first")
        return self._hub

    def initialize(self, hub: 'RegistryOfRegistries') -> None:
        """
        Lifecycle Hook: Receive hub reference and resolve dependencies.

        Args:
            hub: The central Hub (RegistryOfRegistries)

        Raises:
            ValueError: If required dependencies are not available

        Example:
            def initialize(self, hub):
                super().initialize(hub)
                self.roles = hub.get('roles')
                self.patterns = hub.get('patterns')
        """
        self._hub = hub
        self._initialized = True

        # Validate dependencies are available
        for dep in self._dependencies:
            if hub.get(dep) is None:
                raise ValueError(
                    f"Plugin {self.name} requires registry '{dep}' but it is not available"
                )

    @abstractmethod
    def register(self) -> None:
        """
        Lifecycle Hook: Register capabilities and event subscriptions.

        This is where the module:
        - Subscribes to events via hub.event_bus.on()
        - Registers interfaces or services with the hub
        - Declares what it provides to other modules

        Example:
            def register(self):
                self.hub.event_bus.on('data:ready', self.process_data)
                self.hub.register_service('my-service', self)
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """
        Lifecycle Hook: Begin normal operation.

        Called after all modules have registered.
        Safe to emit events or call other modules' services.

        Example:
            def start(self):
                self.hub.event_bus.emit('module:started', {'name': self.name})
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Lifecycle Hook: Graceful shutdown.

        Called when the Hub is shutting down.
        Clean up resources, flush pending work.

        Example:
            def stop(self):
                self.hub.event_bus.emit('module:stopped', {'name': self.name})
                self.connection.close()
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get plugin metadata (useful for introspection).

        Returns:
            Dict with name, version, dependencies
        """
        return {
            'name': self.name,
            'version': self.version,
            'dependencies': self.dependencies,
            'initialized': self._initialized
        }


class ServicePlugin(BasePlugin):
    """
    Specialized plugin that provides a service to other modules.

    Automatically registers itself as a service in the hub.
    """

    def register(self) -> None:
        """Register this plugin as a service."""
        self.hub.register(f'service:{self.name}', self)

    @abstractmethod
    def start(self) -> None:
        """Subclasses must implement."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Subclasses must implement."""
        pass


class EventDrivenPlugin(BasePlugin):
    """
    Specialized plugin that primarily reacts to events.

    Provides helper for bulk event registration.
    """

    def register_events(self, event_map: Dict[str, callable]) -> None:
        """
        Register multiple event handlers at once.

        Args:
            event_map: {event_name: handler_function}

        Example:
            self.register_events({
                'data:ready': self.on_data_ready,
                'analysis:complete': self.on_complete
            })
        """
        for event, handler in event_map.items():
            self.hub.event_bus.on(event, handler)

    @abstractmethod
    def register(self) -> None:
        """Subclasses must call register_events()."""
        pass

    @abstractmethod
    def start(self) -> None:
        """Subclasses must implement."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Subclasses must implement."""
        pass
