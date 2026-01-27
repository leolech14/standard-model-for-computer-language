# Universal Module API - Hub Connection Contract

> **Purpose:** Standard interface for all Hub-connected modules
> **Validated:** Gemini 3.0 Pro forensic analysis (2026-01-27)
> **Status:** Canonical specification

---

## The Interface Contract

Every module connecting to the Hub MUST implement:

```python
from src.core.plugin import BasePlugin

class MyModule(BasePlugin):
    def __init__(self):
        super().__init__(
            name='my-module',           # Unique ID
            version='1.0.0',            # Semantic version
            dependencies=['roles']      # Required registries
        )

    def initialize(self, hub):
        """PHASE 1: Receive hub, resolve dependencies"""
        super().initialize(hub)
        self.roles = hub.get('roles')

    def register(self):
        """PHASE 2: Subscribe to events, register services"""
        self.hub.event_bus.on('data:ready', self.process)

    def start(self):
        """PHASE 3: Begin normal operation"""
        print(f"{self.name} started")

    def stop(self):
        """PHASE 4: Graceful shutdown"""
        print(f"{self.name} stopping")
```

---

## Lifecycle Phases

```
┌──────────────┐
│ __init__()   │  Metadata only (name, version, deps)
└──────┬───────┘
       ↓
┌──────────────┐
│ initialize() │  Hub reference, resolve dependencies
└──────┬───────┘
       ↓
┌──────────────┐
│ register()   │  Event subscriptions, service registration
└──────┬───────┘
       ↓
┌──────────────┐
│ start()      │  Normal operation begins
└──────┬───────┘
       │
    [Running]
       │
       ↓
┌──────────────┐
│ stop()       │  Cleanup and shutdown
└──────────────┘
```

---

## Event Contracts

### Naming Convention

```
domain:entity:action
```

**Examples:**
- `analysis:node:classified`
- `pipeline:stage:complete`
- `graph:edge:added`
- `validation:rule:violated`

### Payload Schema

ALL event payloads must be JSON-serializable:

```python
{
    'timestamp': '2026-01-27T08:00:00Z',
    'source': 'module-name',
    'data': {
        # Module-specific payload
    }
}
```

### Standard Events (System-Wide)

| Event | When | Payload |
|-------|------|---------|
| `hub:initialized` | Hub startup complete | `{'registries': [...]}` |
| `hub:shutdown` | Hub shutting down | `{}` |
| `module:registered` | Module registered | `{'name': str, 'version': str}` |
| `module:started` | Module started | `{'name': str}` |
| `module:error` | Module error | `{'name': str, 'error': str}` |

---

## Service Registration

Modules can register as services for other modules to use:

```python
class MyServicePlugin(BasePlugin):
    def register(self):
        # Register self as service
        self.hub.register(f'service:{self.name}', self)

    def provide_data(self):
        return {'data': 'from service'}

# Other modules use it:
service = hub.get('service:my-module')
data = service.provide_data()
```

---

## Data Contracts

### Registry Interface

All registries SHOULD provide:
- `get(key)` - Retrieve item by ID
- `list_all()` or `all()` - List all items
- `count()` - Item count

### State Object

Modules that process `CodebaseState` must:
- Accept state as input
- Return modified state as output
- Not modify state in-place (functional style)

---

## Specialized Plugin Types

### ServicePlugin

Automatically registers as a service:

```python
from src.core.plugin import ServicePlugin

class MyService(ServicePlugin):
    def start(self):
        # Available as hub.get('service:my-service')
        pass
```

### EventDrivenPlugin

Helper for bulk event registration:

```python
from src.core.plugin import EventDrivenPlugin

class MyListener(EventDrivenPlugin):
    def register(self):
        self.register_events({
            'data:ready': self.on_data,
            'analysis:complete': self.on_complete
        })
```

---

## Module Compatibility Checklist

- [ ] Inherits from `BasePlugin` (or subclass)
- [ ] Has unique `name` property
- [ ] Declares `dependencies` list
- [ ] Implements `initialize(hub)` - no global imports
- [ ] Implements `register()` - event subscriptions
- [ ] Implements `start()` - ready for operation
- [ ] Implements `stop()` - cleanup
- [ ] Uses `hub.get()` instead of global singletons
- [ ] Emits events for state changes
- [ ] All public methods have type hints
- [ ] Has tests using Hub
- [ ] Documented in HUB_INTEGRATION_INDEX.md

---

## Examples

### Example 1: Classifier Module

```python
class ClassifierPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name='universal-classifier',
            version='2.0.0',
            dependencies=['roles', 'patterns']
        )
        self.classifier = None

    def initialize(self, hub):
        super().initialize(hub)
        roles = hub.get('roles')
        patterns = hub.get('patterns')
        self.classifier = UniversalClassifier(roles, patterns)

    def register(self):
        # Listen for classification requests
        self.hub.event_bus.on('node:classify-request', self.classify_node)

    def start(self):
        self.hub.event_bus.emit('classifier:ready', {'name': self.name})

    def stop(self):
        self.hub.event_bus.emit('classifier:stopped', {'name': self.name})

    def classify_node(self, node_data):
        result = self.classifier.classify(node_data)
        self.hub.event_bus.emit('node:classified', result)
```

### Example 2: Validator Module

```python
class ValidatorPlugin(EventDrivenPlugin):
    def __init__(self):
        super().__init__(
            name='constraint-validator',
            version='1.0.0',
            dependencies=['schemas']
        )

    def initialize(self, hub):
        super().initialize(hub)
        self.schemas = hub.get('schemas')

    def register(self):
        self.register_events({
            'graph:node-added': self.validate_node,
            'graph:edge-added': self.validate_edge
        })

    def start(self):
        pass  # Event-driven, no startup needed

    def stop(self):
        pass  # No resources to clean up

    def validate_node(self, node):
        violations = self.check_violations(node)
        if violations:
            self.hub.event_bus.emit('violation:detected', {
                'node': node['id'],
                'violations': violations
            })
```

---

## Anti-Patterns (DO NOT)

| Anti-Pattern | Why Bad | Fix |
|--------------|---------|-----|
| Global imports in `__init__` | Can't hot-reload | Use `initialize(hub)` |
| Direct module imports | Tight coupling | Request via `hub.get()` |
| Shared mutable state | Race conditions | Use event bus or immutable state |
| Blocking I/O in handlers | Deadlocks | Use async or background threads |
| Circular event loops | Infinite recursion | Use `event_bus.once()` or flags |

---

## Implementation: base_plugin.py

**Location:** `src/core/plugin/base_plugin.py`

**Provides:**
- `BasePlugin` - Base class for all modules
- `ServicePlugin` - Modules that provide services
- `EventDrivenPlugin` - Event-reactive modules

---

## Next Steps

1. ✅ Universal API defined (BasePlugin)
2. ⏭️ Convert high-value modules (UniversalClassifier, ConstraintEngine)
3. ⏭️ Build MCP server wrapper to expose Hub
4. ⏭️ Create plugin.json manifests
