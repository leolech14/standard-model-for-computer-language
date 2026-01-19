[Home](../README.md) > [Docs](./README.md) > **Purpose Field**

---

# Purpose Field Theory

## Hierarchical Organization of Purpose

### Overview

Code has **PURPOSE** - the reason it exists. Purpose is organized at multiple levels:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  LEVEL 4: PURPOSE FIELD (Application)                                   │
│  ─────────────────────────────────────────────────────                  │
│  The global purpose gradient across the entire codebase                 │
├─────────────────────────────────────────────────────────────────────────┤
│  LEVEL 3: LAYER PURPOSE (Architecture)                                  │
│  ─────────────────────────────────────────────────────                  │
│  Shared purpose of components in the same architectural layer          │
├─────────────────────────────────────────────────────────────────────────┤
│  LEVEL 2: COMPOSITE PURPOSE (Components)                                │
│  ─────────────────────────────────────────────────────                  │
│  Aggregated purpose from grouped components                             │
├─────────────────────────────────────────────────────────────────────────┤
│  LEVEL 1: ATOMIC PURPOSE (Role)                                         │
│  ─────────────────────────────────────────────────────                  │
│  Intrinsic purpose of individual functions/classes                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Level 1: Atomic Purpose

Every code element has an **intrinsic purpose** - the reason it was written.

| Element | Atomic Purpose | Role |
|---------|---------------|------|
| `get_user()` | Retrieve user data | Query |
| `save_user()` | Persist user data | Command |
| `validate_email()` | Verify email format | Validator |
| `user_to_dict()` | Transform user representation | Mapper |

**Detection**: Pattern matching on names → ROLE assignment

**Equation**: 
```
π₁(node) = role(node)
```

---

## Level 2: Composite Purpose

When components are **grouped together** (by class, module, or relationship), a new purpose arises from the combination of their individual purposes.

### Example: UserRepository

```python
class UserRepository:
    def get(id): ...      # Query
    def save(user): ...   # Command  
    def delete(id): ...   # Command
    def list_all(): ...   # Query
```

**Atomic purposes**: Query, Command, Command, Query

**Composite purpose**: "User data persistence" → **Repository**

The composite purpose:
- Is NOT just "Query + Command + Command + Query"
- Reflects the unified role of the containing class
- Has distinct semantic meaning from its parts

**Detection**: Aggregate roles within containing class → infer composite role

**Equation**:
```
π₂(class) = emergence(∑ π₁(method) for method in class)
```

---

## Level 3: Layer Purpose

Components with related composite purposes form **layers** with shared architectural purpose.

### Example: Persistence Layer

```
Persistence Layer
├── UserRepository      (π₂ = data persistence for users)
├── OrderRepository     (π₂ = data persistence for orders)  
├── ProductRepository   (π₂ = data persistence for products)
└── PaymentRepository   (π₂ = data persistence for payments)
```

**Layer purpose**: "All data persistence for the application"

This layer has:
- Shared characteristics (all interact with database)
- Shared constraints (no business logic, no presentation)
- Shared relationships (all called by services, all call infrastructure)

**Detection**: Graph analysis → cluster by relationship patterns → infer layer

**Equation**:
```
π₃(layer) = common_purpose({π₂(c) for c in layer.components})
```

---

## Level 4: Purpose Field

The **entire codebase** has a purpose field - a gradient of meaning that flows through the architecture.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   ┌─────────────┐                                                       │
│   │ PRESENTATION│  Purpose: Display → User sees data                   │
│   └──────┬──────┘                                                       │
│          │                                                              │
│          ▼                                                              │
│   ┌─────────────┐                                                       │
│   │ APPLICATION │  Purpose: Orchestrate → Use cases happen              │
│   └──────┬──────┘                                                       │
│          │                                                              │
│          ▼                                                              │
│   ┌─────────────┐                                                       │
│   │   DOMAIN    │  Purpose: Express → Business rules enforced          │
│   └──────┬──────┘                                                       │
│          │                                                              │
│          ▼                                                              │
│   ┌─────────────┐                                                       │
│   │INFRASTRUCTURE│ Purpose: Implement → Technical details handled      │
│   └─────────────┘                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Purpose flows downward**: Higher layers depend on lower layers
**Abstraction increases upward**: Lower layers know nothing of higher purpose

**The Purpose Field describes**:
- Where purpose originates (user intent at presentation)
- How purpose transforms (through each layer)
- Where purpose terminates (side effects at infrastructure)

**Equation**:
```
Π(codebase) = ∫ π₃(layer) d(layer)
```

---

## Mathematical Formalization

### Purpose Function

For any code element `e`, the purpose function `π` is defined recursively:

```
π(e) = {
    π₁(e)                           if e is atomic (function/method)
    emergence(∑ π(child))           if e is composite (class/module)
    common_purpose({π(member)})     if e is layer
    integrate({π(layer)})           if e is codebase
}
```

### Emergence Function

The emergence function captures how composite purpose arises:

```
emergence(purposes) = {
    p : p ∈ ROLES ∧ 
        p encompasses all purposes ∧
        p is minimal such encompassment
}
```

### Purpose Conservation

Purpose is **conserved** through the call graph:

```
∀ caller, callee:
    purpose(callee) must be compatible with purpose(caller)
```

**Violations** (antimatter):
- Repository calling Controller → purpose flows wrong direction
- Command returning data → purpose mismatch
- Query causing side effects → purpose leakage

---

## Implementation Strategy

### Stage 1: Detect Atomic Purpose (DONE ✅)
- Pattern matching on names → roles
- 33 roles detected with >90% accuracy

### Stage 2: Infer Composite Purpose
```python
def composite_purpose(class_node):
    method_roles = [π₁(m) for m in class_node.methods]
    return emergence(method_roles)
```

### Stage 3: Cluster into Layers
```python
def detect_layers(graph):
    # Cluster nodes by:
    # - Similar composite purpose
    # - Similar graph position (depth from entry)
    # - Similar dependencies
    return layers
```

### Stage 4: Compute Purpose Field
```python
def purpose_field(codebase):
    layers = detect_layers(codebase.graph)
    return {
        layer: layer_purpose(layer)
        for layer in layers
    }
```

---

## Why This Matters

### For LLMs

With the Purpose Field, an LLM understands:

1. **Where to add code**: "Add user validation" → Domain layer
2. **What patterns to follow**: Domain layer components look like X
3. **What to avoid**: Don't call Presentation from Domain
4. **What's missing**: Purpose gap between layers = missing component

### For Architecture

The Purpose Field makes architecture **explicit**:

- Not just "folders" but "purpose zones"
- Not just "imports" but "purpose flow"
- Not just "layers" but "purpose gradient"

### For Verification

Violations are **purpose flow errors**:

- Purpose flowing upward (infrastructure calling domain)
- Purpose leaking (query with side effects)
- Purpose gaps (entity without repository)

