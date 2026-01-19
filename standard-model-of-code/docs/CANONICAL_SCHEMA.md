# Canonical Schema: The Standard Code Model

> **"From knowing this schema, we understand the system."**

This document defines the **minimal and complete** data structure for representing any codebase.

---

## 📐 The Core Axiom

Every codebase is a **Graph**:
```
Codebase = (Nodes, Edges, Metadata)
```

Where:
- **Nodes** = Code elements (classes, functions, modules)
- **Edges** = Relationships (calls, imports, inherits)
- **Metadata** = Context (target path, timestamp, statistics)

---

## 🔬 Node Schema (Particle)

### Required Fields (Minimal)
These fields **MUST** exist. Without them, the node is undefined.

```json
{
  "id": "user.py:UserRepository",
  "name": "UserRepository",
  "kind": "class"
}
```

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | `string` | Unique identifier (file:qualifiedName) | `"user.py:UserRepository"` |
| `name` | `string` | Human-readable name | `"UserRepository"` |
| `kind` | `string` | Syntactic type | `"class"`, `"function"`, `"method"`, `"module"` |

---

### Location Fields (Optional but Recommended)
Enable source mapping and navigation.

```json
{
  "file_path": "src/domain/user.py",
  "start_line": 15,
  "end_line": 42
}
```

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `string` | Relative path to source file |
| `start_line` | `int` | Starting line number (1-indexed) |
| `end_line` | `int` | Ending line number (inclusive) |

---

### Classification Fields (Stage 2 Output)
Added by Role Theory analysis.

```json
{
  "role": "Repository",
  "role_confidence": 0.95,
  "discovery_method": "pattern"
}
```

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `role` | `string` | Canonical role | `"Repository"`, `"Entity"`, `"Service"`, `"Controller"`, etc. |
| `role_confidence` | `float` | Confidence score (0-100) | `95.0` = 95% confident |
| `discovery_method` | `string` | How role was detected | `"pattern"`, `"inheritance"`, `"path"`, `"llm"`, `"none"` |

---

### Type Information (Optional)
Preserves language-specific type signatures.

```json
{
  "params": [
    {"name": "user_id", "type": "str"},
    {"name": "username", "type": "str"}
  ],
  "return_type": "User",
  "base_classes": ["BaseRepository"],
  "decorators": ["cached"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `params` | `List[{name, type}]` | Function/method parameters |
| `return_type` | `string` | Return type annotation |
| `base_classes` | `List[string]` | Parent classes (for inheritance) |
| `decorators` | `List[string]` | Decorators/annotations |

---

### Documentation (Optional)
Captures human-written context.

```json
{
  "docstring": "Repository for user persistence and retrieval.",
  "signature": "class UserRepository(BaseRepository<User>)"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `docstring` | `string` | Extracted docstring/comment |
| `signature` | `string` | Full signature (formatted) |

---

### Code Capture (Optional)
Lossless source preservation for later LLM analysis.

```json
{
  "body_source": "def find(self, user_id: str):\n    return self.db.query(...)"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `body_source` | `string` | Full implementation code |

---

### Metrics (Optional)
Complexity and size measurements.

```json
{
  "complexity": 8,
  "lines_of_code": 27
}
```

| Field | Type | Description |
|-------|------|-------------|
| `complexity` | `int` | Cyclomatic complexity |
| `lines_of_code` | `int` | Total lines (excluding comments) |

---

### Graph Properties (Optional)
Computed from edge analysis.

```json
{
  "in_degree": 5,
  "out_degree": 3
}
```

| Field | Type | Description |
|-------|------|-------------|
| `in_degree` | `int` | Number of incoming edges (callers) |
| `out_degree` | `int` | Number of outgoing edges (callees) |

---

### Enrichment Fields (Added by Analysis Stages)
Populated by Purpose Field (Stage 6), Flow (Stage 7), Performance (Stage 8).

```json
{
  "layer": "Infrastructure",
  "composite_purpose": "User data persistence",
  "is_orphan": false,
  "is_hotspot": true,
  "hotspot_score": 87.5
}
```

| Field | Type | Stage | Description |
|-------|------|-------|-------------|
| `layer` | `string` | 6 | Architectural layer: `"Domain"`, `"Infrastructure"`, `"Application"`, `"Presentation"` |
| `composite_purpose` | `string` | 6 | Derived semantic purpose |
| `is_orphan` | `boolean` | 7 | True if unreachable (dead code) |
| `is_hotspot` | `boolean` | 8 | True if performance-critical |
| `hotspot_score` | `float` | 8 | Performance criticality (0-100) |

---

### Metadata (Extensible)
Catch-all for custom/experimental data.

```json
{
  "metadata": {
    "intelligence": "LLM-generated summary",
    "custom_tag": "experimental"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `metadata` | `Dict[string, any]` | Arbitrary key-value pairs |

---

## 🔗 Edge Schema (Connection)

### Required Fields (Minimal)

```json
{
  "source": "user.py:UserService",
  "target": "user.py:UserRepository",
  "edge_type": "CALLS"
}
```

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `source` | `string` | Source node ID | `"user.py:UserService"` |
| `target` | `string` | Target node ID | `"user.py:UserRepository"` |
| `edge_type` | `string` | Relationship type | `"CALLS"`, `"IMPORTS"`, `"INHERITS"`, `"IMPLEMENTS"` |

---

### Optional Fields

```json
{
  "weight": 1.0,
  "confidence": 0.98,
  "file_path": "src/domain/user.py",
  "line": 23
}
```

| Field | Type | Description |
|-------|------|-------------|
| `weight` | `float` | Edge strength (e.g., call frequency) |
| `confidence` | `float` | Detection confidence (0-100) |
| `file_path` | `string` | Where the relationship was declared |
| `line` | `int` | Line number of the reference |

---

### Edge Types (Canonical)

| Type | Meaning | Example |
|------|---------|---------|
| `CONTAINS` | Parent-child (file → class) | `user.py` CONTAINS `UserRepository` |
| `CALLS` | Function invocation | `UserService` CALLS `UserRepository.find()` |
| `IMPORTS` | Module dependency | `service.py` IMPORTS `repository.py` |
| `INHERITS` | Class inheritance | `UserRepository` INHERITS `BaseRepository` |
| `IMPLEMENTS` | Interface realization | `UserService` IMPLEMENTS `IUserService` |
| `USES` | General dependency | `Controller` USES `UserService` |

---

## 📊 Complete Graph Schema

### The Unified Output

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-12-22T23:50:00",
  "target_path": "/path/to/codebase",
  
  "nodes": [
    {
      "id": "user.py:UserRepository",
      "name": "UserRepository",
      "kind": "class",
      "role": "Repository",
      "layer": "Infrastructure",
      "file_path": "src/domain/user.py",
      "complexity": 8,
      "is_hotspot": true
    }
  ],
  
  "edges": [
    {
      "source": "user.py:UserService",
      "target": "user.py:UserRepository",
      "edge_type": "CALLS",
      "confidence": 0.98
    }
  ],
  
  "metadata": {
    "layers_activated": ["classification", "purpose", "flow", "performance"],
    "stats": {
      "node_count": 245,
      "edge_count": 512,
      "avg_complexity": 5.3
    }
  }
}
```

---

## 🎯 The Minimal Complete Set

**To understand ANY codebase, you ONLY need:**

1. **Nodes** with `id`, `name`, `kind`, `role`, `layer`
2. **Edges** with `source`, `target`, `edge_type`
3. **Metadata** with `target_path`, `generated_at`

**Everything else is optional enrichment.**

---

## 🔬 Field Lifecycle (When Fields Appear)

| Stage | Fields Added |
|-------|-------------|
| **Stage 1 (Classification)** | `id`, `name`, `kind`, `file_path`, `lines`, `complexity` |
| **Stage 2 (Roles)** | `role`, `role_confidence`, `discovery_method` |
| **Stage 6 (Purpose)** | `layer`, `composite_purpose` |
| **Stage 7 (Flow)** | `is_orphan`, `in_degree`, `out_degree` |
| **Stage 8 (Performance)** | `is_hotspot`, `hotspot_score` |

**The schema is additive.** Each stage adds fields without modifying existing ones.

---

## ✅ Schema Validation Rules

1. **Node ID Uniqueness**: No two nodes can have the same `id`.
2. **Edge Referential Integrity**: `source` and `target` must exist in `nodes`.
3. **Layer Constraint**: `layer` must be one of: `Domain`, `Infrastructure`, `Application`, `Presentation`, `Unknown`.
4. **Role Constraint**: `role` should be a canonical role from the 33-role taxonomy (or `Unknown`).
5. **Confidence Range**: `role_confidence` and `confidence` must be in `[0, 100]`.

---

**This is the source of truth.** All tools (Collider, Visualization, LLM agents) consume and produce this schema.
