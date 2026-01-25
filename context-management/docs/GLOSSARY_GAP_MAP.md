# GLOSSARY GAP MAP

> Audit of terminology coverage across PROJECT_elements documentation.

**Date:** 2026-01-25
**Sources Analyzed:**
- `context-management/docs/archive/legacy_schema_2025/GLOSSARY.md` (LEGACY)
- `standard-model-of-code/docs/MODEL.md` (CURRENT)
- `context-management/docs/*.md` (NEW -ome docs)

---

## GAP SUMMARY

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                         GLOSSARY COVERAGE STATUS                                ║
╠════════════════════════════════════════════════════════════════════════════════╣
║                                                                                 ║
║   LEGACY GLOSSARY          MODEL.md              NEW -OME DOCS                  ║
║   (archived)               (current)             (2026-01-25)                   ║
║   ─────────────            ─────────             ────────────                   ║
║   3 Planes ✓               3 Planes ✓            (not covered)                  ║
║   13 Levels                16 Levels ✓           (not covered)                  ║
║   8 Lenses ✓               8 Dimensions ✓        (not covered)                  ║
║   Atoms ✓                  Atoms ✓               (not covered)                  ║
║   Roles ✓                  Roles ✓               (not covered)                  ║
║   Edges ✓                  (partial)             (not covered)                  ║
║   Confidence ✓             (partial)             (not covered)                  ║
║                                                                                 ║
║   (missing)                (missing)             PROJECTOME ✓                   ║
║   (missing)                (missing)             CODOME ✓                       ║
║   (missing)                (missing)             CONTEXTOME ✓                   ║
║   (missing)                (missing)             DOMAINS ✓                      ║
║   (missing)                (missing)             REALMS (partial)               ║
║   (missing)                (missing)             SET ALGEBRA ✓                  ║
║   (missing)                (missing)             SYMMETRY STATES ✓              ║
║   (missing)                Wave-Particle ✓       (referenced)                   ║
║   (missing)                (missing)             SUBSYSTEMS (partial)           ║
║                                                                                 ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

---

## DETAILED GAP ANALYSIS

### CATEGORY 1: FOUNDATIONAL STRUCTURES

| Term | Legacy | MODEL.md | -ome Docs | Status |
|------|--------|----------|-----------|--------|
| **3 Planes** (Physical/Virtual/Semantic) | ✓ | ✓ | ✗ | COVERED |
| **16 Levels** (L-3 to L12) | 13 levels | ✓ | ✗ | COVERED (MODEL) |
| **8 Lenses** | ✓ | as "Dimensions" | ✗ | COVERED |
| **4 Phases** (Data/Logic/Org/Exec) | ✗ | ✓ | ✗ | COVERED (MODEL) |
| **RPBL** (Responsibility/Purity/Boundary/Lifecycle) | ✗ | ✓ | ✗ | COVERED (MODEL) |

### CATEGORY 2: CLASSIFICATION

| Term | Legacy | MODEL.md | -ome Docs | Status |
|------|--------|----------|-----------|--------|
| **Atoms** (3,616 total) | ~30 listed | 94 impl | ✗ | PARTIAL |
| **Roles** (33 canonical) | ✓ | ✓ 29 impl | ✗ | COVERED |
| **Tiers** (T0/T1/T2) | ✗ | ✗ | ✗ | **GAP** |
| **Ecosystems** (250+) | ✗ | ✗ | ✗ | **GAP** |

### CATEGORY 3: RELATIONSHIPS

| Term | Legacy | MODEL.md | -ome Docs | Status |
|------|--------|----------|-----------|--------|
| **Edge Types** (calls/imports/inherits/etc) | ✓ 6 types | ✗ | ✗ | LEGACY ONLY |
| **Confidence Sources** | ✓ | ✗ | ✗ | LEGACY ONLY |
| **Confidence Levels** (0-100%) | ✓ | ✗ | ✗ | LEGACY ONLY |

### CATEGORY 4: NAVIGATION TOPOLOGY (NEW)

| Term | Legacy | MODEL.md | -ome Docs | Status |
|------|--------|----------|-----------|--------|
| **PROJECTOME** | ✗ | ✗ | ✓ | **NEW** |
| **CODOME** | ✗ | ✗ | ✓ | **NEW** |
| **CONTEXTOME** | ✗ | ✗ | ✓ | **NEW** |
| **DOMAINS** | ✗ | ✗ | ✓ | **NEW** |
| **TOPOLOGY_MAP** | ✗ | ✗ | ✓ | **NEW** |

### CATEGORY 5: SET ALGEBRA (NEW)

| Term | Legacy | MODEL.md | -ome Docs | Status |
|------|--------|----------|-----------|--------|
| **Partition** (P = C ⊔ X) | ✗ | ✗ | ✓ | **NEW** |
| **Disjoint Union** (⊔) | ✗ | ✗ | ✓ | **NEW** |
| **Set Difference** (P \ C) | ✗ | ✗ | ✓ | **NEW** |
| **Cover** (domains) | ✗ | ✗ | ✓ | **NEW** |
| **MECE** | ✗ | ✗ | ✓ | **NEW** |

### CATEGORY 6: SYMMETRY STATES (NEW)

| Term | Legacy | MODEL.md | -ome Docs | Status |
|------|--------|----------|-----------|--------|
| **SYMMETRIC** (code ↔ docs match) | ✗ | ✗ | ✓ | **NEW** |
| **ORPHAN** (code, no docs) | ✗ | ✗ | ✓ | **NEW** |
| **PHANTOM** (docs, no code) | ✗ | ✗ | ✓ | **NEW** |
| **DRIFT** (both exist, mismatch) | ✗ | ✗ | ✓ | **NEW** |

### CATEGORY 7: REALMS & PHYSICS METAPHOR

| Term | Legacy | MODEL.md | -ome Docs | Status |
|------|--------|----------|-----------|--------|
| **Particle Realm** (standard-model-of-code/) | ✗ | ✗ | partial | **GAP** |
| **Wave Realm** (context-management/) | ✗ | ✗ | partial | **GAP** |
| **Observer Realm** (.agent/) | ✗ | ✗ | partial | **GAP** |
| **Wave-Particle Duality** | ✗ | referenced | ✗ | **GAP** |
| **Collapse** (measurement) | ✗ | ✗ | ✗ | **GAP** |

### CATEGORY 8: SUBSYSTEMS

| Term | Legacy | MODEL.md | -ome Docs | Status |
|------|--------|----------|-----------|--------|
| **Collider** | ✗ | ✗ | ✗ | In CLAUDE.md only |
| **HSL** (Holographic-Socratic Layer) | ✗ | ✗ | ✗ | In specs only |
| **ACI** (Adaptive Context Intelligence) | ✗ | ✗ | ✗ | In specs only |
| **BARE** (Background Auto-Refinement) | ✗ | ✗ | ✗ | In specs only |
| **Registry of Registries** | ✗ | ✗ | ✗ | In specs only |

### CATEGORY 9: ETYMOLOGY

| Term | Legacy | MODEL.md | -ome Docs | Status |
|------|--------|----------|-----------|--------|
| **-ome suffix** (Greek -ωμα) | ✗ | ✗ | ✓ | **NEW** |
| **Holons** (Koestler) | ✗ | ✓ | ✗ | MODEL only |
| **Three Worlds** (Popper) | ✗ | ✓ | ✗ | MODEL only |

---

## ASCII RELATIONSHIP DIAGRAMS NEEDED

### 1. The Universe Partition (EXISTS in TOPOLOGY_MAP.md)
```
PROJECTOME = CODOME ⊔ CONTEXTOME
```

### 2. The Realm Partition (MISSING)
```
PROJECTOME = Particle ⊔ Wave ⊔ Observer
           = standard-model-of-code/ ⊔ context-management/ ⊔ .agent/
```

### 3. Domain Cover (PARTIAL in DOMAINS.md)
```
⋃ Domains = PROJECTOME
Domains may overlap (Cover, not Partition)
```

### 4. Classification Function (MISSING)
```
σ: Nodes → Atoms
Every node maps to exactly one atom type
```

### 5. Symmetry Relation (MISSING)
```
R ⊆ CODOME × CONTEXTOME × {SYMMETRIC, ORPHAN, PHANTOM, DRIFT}
```

### 6. Level Hierarchy (EXISTS in MODEL.md, needs diagram)
```
L12 (Universe) ⊃ L11 ⊃ ... ⊃ L3 (Node) ⊃ ... ⊃ L-3 (Bit)
```

### 7. Subsystem Data Flow (EXISTS in SUBSYSTEM_INTEGRATION.md)
```
Collider → unified_analysis.json → ACI → Tasks → BARE → Code
```

---

## GAP PRIORITY MATRIX

| Gap | Impact | Effort | Priority |
|-----|--------|--------|----------|
| **Unified GLOSSARY.md** | HIGH | MEDIUM | P0 |
| Realm definitions | MEDIUM | LOW | P1 |
| Subsystem glossary entries | MEDIUM | MEDIUM | P1 |
| Classification function diagram | LOW | LOW | P2 |
| Symmetry relation diagram | LOW | LOW | P2 |
| Tier/Ecosystem documentation | LOW | HIGH | P3 |

---

## RECOMMENDED ACTION

Create a **unified GLOSSARY.md** at `context-management/docs/GLOSSARY.md` containing:

1. **Navigation Topology** (PROJECTOME, CODOME, CONTEXTOME, DOMAINS)
2. **Set Algebra** (partitions, covers, functions)
3. **Foundational Structures** (Planes, Levels, Dimensions)
4. **Classification** (Atoms, Roles, Tiers)
5. **Relationships** (Edge types, Symmetry states)
6. **Subsystems** (Collider, HSL, ACI, BARE)
7. **Realms** (Particle, Wave, Observer)
8. **ASCII Diagrams** for all relationships

**Estimated size:** ~400 lines
**Consolidates:** Legacy glossary + MODEL.md + -ome docs

---

*Generated: 2026-01-25*
