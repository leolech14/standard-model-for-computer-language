# SUBSYSTEM CITIZENSHIP PROTOCOL
# The Official Path to Become Part of Repo Truth

> **Status:** DRAFT (2026-01-26)
> **Purpose:** Define how a component earns a seat on the Systems Scaffold
> **Related:** SOS_MAP_TRUTH.md, LOL.yaml, TOOLS_REGISTRY.yaml

---

## 1. THE SYSTEMS SCAFFOLD

The Systems Scaffold is the **constitutional structure** of PROJECT_elements.

```
SCAFFOLD = { S1, S2, S3, ..., S∞ }

Each seat Sᵢ is OCCUPIED by exactly one SUBSYSTEM.
Each SUBSYSTEM has:
  - Identity (name, ID, realm)
  - Interface (inputs, outputs, invoke)
  - Connections (integrations with other seats)
  - Status (active, degraded, deprecated)
```

### Current Seats (as of 2026-01-26)

| Seat | Subsystem | Realm | Type | Status |
|------|-----------|-------|------|--------|
| S1 | Collider | Particle | Engine | Active (degraded) |
| S2 | HSL | Wave | Framework | Active |
| S3 | analyze.py | Wave | Engine | Active |
| S4 | Perplexity MCP | Wave | Utility | Active |
| S5 | Task Registry | Observer | State | Active |
| S6 | BARE | Observer | Engine | Active |
| S7 | Archive | Wave | Utility | Active |
| S8 | Hygiene | Observer | Guard | Active |
| S9 | Laboratory | Particle | Bridge | Active |
| S9b | Lab Bridge | Wave | Client | Active |
| S10 | AEP | Observer | Engine | Active |
| S11 | ACI Refinery | Wave | Engine | Active |
| S12 | Centripetal | Observer | Utility | Active |
| S13 | Macro Registry | Observer | State | Active |
| **S14** | **VACANT** | - | - | Open |

---

## 2. CITIZENSHIP REQUIREMENTS

To claim a seat on the Scaffold, a component MUST satisfy:

### 2.1 Identity Requirements

```yaml
# REQUIRED: Every subsystem must declare identity
identity:
  id: "S14"                          # Assigned seat number
  name: "Projectome Omniscience"     # Human-readable name
  shortname: "POM"                   # Max 4 chars
  realm: wave                        # particle | wave | observer
  type: engine                       # engine | framework | utility | guard | state | bridge | client
  purpose: "Complete PROJECTOME visibility"  # One-line purpose
  created: "2026-01-25"
  author: "leonardo.lech@gmail.com"
```

### 2.2 Interface Requirements (The Contract)

```yaml
# REQUIRED: Every subsystem must declare its interface
interface:
  # How to invoke this subsystem
  invoke:
    method: cli | python_import | api | hook
    command: "python3 {path}/projectome_omniscience.py --output {output}"
    entrypoint: "context-management/tools/pom/projectome_omniscience.py"

  # What this subsystem CONSUMES
  inputs:
    - name: unified_analysis.json
      type: file
      from: S1  # Explicit dependency on another seat
      required: false

    - name: project_root
      type: path
      default: "."

  # What this subsystem PRODUCES
  outputs:
    - name: pom_manifest.yaml
      type: file
      format: yaml
      schema: "context-management/tools/pom/manifest.schema.yaml"  # REQUIRED

  # What this subsystem REQUIRES to run
  requires:
    - python >= 3.10
    # NO external dependencies = good citizen
```

### 2.3 Integration Requirements

```yaml
# REQUIRED: At least ONE integration with existing scaffold
integrations:
  consumes_from:
    - seat: S1
      artifact: unified_analysis.json
      mechanism: file_read

  produces_for:
    - seat: S_VIZ  # Future visualization seat
      artifact: pom_manifest.yaml
      mechanism: file_write

  # BONUS: Hooks into existing flows
  hooks:
    - trigger: post_collider_analysis
      action: "auto-generate manifest"
```

### 2.4 Documentation Requirements

```yaml
# REQUIRED: Documentation in canonical locations
documentation:
  # User-facing docs
  user_guide: "context-management/docs/specs/POM_USER_GUIDE.md"

  # Developer-facing docs
  api_reference: "context-management/tools/pom/README.md"

  # Integration into LOL.yaml
  lol_entry: true  # Will be added to LOL.yaml on approval
```

### 2.5 Quality Requirements

```yaml
# REQUIRED: Minimum quality bar
quality:
  # Tests exist and pass
  tests:
    path: "context-management/tools/pom/tests/"
    coverage: ">= 50%"  # Minimum

  # No unhandled errors
  error_handling: "graceful"  # Returns clean errors, doesn't crash

  # Self-documenting
  docstrings: true

  # Type hints (for Python)
  typed: true
```

---

## 3. THE CITIZENSHIP PROCESS

### Step 1: APPLY

Create a citizenship application file:

```bash
# Location: .agent/citizenship/applications/
touch .agent/citizenship/applications/POM.citizenship.yaml
```

### Step 2: FILL APPLICATION

```yaml
# .agent/citizenship/applications/POM.citizenship.yaml

application:
  version: "1.0"
  submitted: "2026-01-26"
  applicant: "leonardo.lech@gmail.com"

# All sections from 2.1 - 2.5
identity: { ... }
interface: { ... }
integrations: { ... }
documentation: { ... }
quality: { ... }

# Self-assessment
self_assessment:
  why_needed: |
    POM provides complete PROJECTOME visibility that no other
    subsystem offers. It bridges CODOME (S1) with CONTEXTOME
    analysis and enables symmetry detection.

  alternatives_considered:
    - name: "Extend S1 Collider"
      rejected_because: "Collider is Particle realm, POM is Wave realm"

  integration_plan:
    - "Read unified_analysis.json from S1"
    - "Produce pom_manifest.yaml for future S_VIZ"
    - "Hook into post-analysis flow"
```

### Step 3: VALIDATION

The application is validated against requirements:

```bash
# Validation script (to be created)
./pe citizenship validate .agent/citizenship/applications/POM.citizenship.yaml
```

Validation checks:
1. ✅ All required fields present
2. ✅ Entrypoint exists and runs
3. ✅ Inputs/outputs match declared types
4. ✅ At least one integration with existing seat
5. ✅ Tests exist and pass
6. ✅ Documentation exists

### Step 4: APPROVAL

If validation passes:

```bash
./pe citizenship approve POM
```

This:
1. Assigns next available seat (S14)
2. Adds entry to LOL.yaml
3. Adds entry to SOS_MAP_TRUTH.md
4. Adds entry to TOOLS_REGISTRY.yaml
5. Creates integration hooks
6. Moves application to `.agent/citizenship/approved/`

### Step 5: SEAT ASSIGNMENT

```
POM is now S14.

SCAFFOLD:
  S1  Collider     [Particle]
  S2  HSL          [Wave]
  ...
  S13 Macro Registry [Observer]
  S14 POM          [Wave]      ← NEW CITIZEN
```

---

## 4. CITIZENSHIP SCHEMA

```yaml
# .agent/schema/citizenship.schema.yaml

$schema: "http://json-schema.org/draft-07/schema#"
title: "Subsystem Citizenship Application"
type: object

required:
  - application
  - identity
  - interface
  - integrations
  - documentation
  - quality

properties:
  application:
    type: object
    required: [version, submitted, applicant]

  identity:
    type: object
    required: [name, shortname, realm, type, purpose]
    properties:
      realm:
        enum: [particle, wave, observer]
      type:
        enum: [engine, framework, utility, guard, state, bridge, client]

  interface:
    type: object
    required: [invoke, inputs, outputs]
    properties:
      invoke:
        type: object
        required: [method, entrypoint]
      inputs:
        type: array
        minItems: 0
      outputs:
        type: array
        minItems: 1  # Must produce SOMETHING

  integrations:
    type: object
    anyOf:
      - required: [consumes_from]
      - required: [produces_for]
    # Must have at least one integration

  documentation:
    type: object
    required: [user_guide]

  quality:
    type: object
    required: [tests, error_handling]
```

---

## 5. VACANT SEATS (Candidates)

| Candidate | Proposed Seat | Realm | Blocker |
|-----------|---------------|-------|---------|
| **POM** | S14 | Wave | Needs citizenship application |
| **Charts/Viz** | S15 | Observer | Not implemented yet |
| **Purpose Flow** | S16 | Particle | Needs Phase 2-4 complete |
| **Tree-sitter** | S17 | Particle | External dependency |

---

## 6. DEPRECATION PROTOCOL

Seats can be DEPRECATED but not REMOVED (history preservation):

```yaml
# A deprecated seat
S99:
  name: "Legacy Tool"
  status: deprecated
  deprecated_date: "2026-01-01"
  replaced_by: S14
  migration_guide: "docs/migrations/S99_to_S14.md"
```

---

## 7. THE SCAFFOLD INVARIANTS

```
INVARIANT 1: Totality
  ∀ component C under PROJECT_elements/:
    is_subsystem(C) → ∃ seat S. C occupies S

INVARIANT 2: Uniqueness
  ∀ seats S1, S2:
    S1 ≠ S2 → occupant(S1) ≠ occupant(S2)

INVARIANT 3: Connectivity
  ∀ seat S (except S1):
    ∃ seat S'. S integrates with S'

INVARIANT 4: Traceability
  ∀ seat S:
    ∃ application A. A approved S

INVARIANT 5: Documentation
  ∀ seat S:
    ∃ entry in LOL.yaml ∧
    ∃ entry in SOS_MAP_TRUTH.md ∧
    ∃ entry in TOOLS_REGISTRY.yaml
```

---

## CHANGELOG

| Date | Change |
|------|--------|
| 2026-01-26 | Initial protocol definition |

---

*"A component without a seat is a ghost. A seat without a component is a phantom."*
