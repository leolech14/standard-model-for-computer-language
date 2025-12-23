# Naming Standardization Proposal

**Problem:** Inconsistent terminology across codebase, documentation, and outputs causes confusion and brittleness.

---

## Current State (Problems)

### 1. Node/Element Terminology
**Same concept, 5 different names:**
- `nodes` (in graph theory sense)
- `components` (in graph.json)
- `particles` (physics metaphor)
- `elements` (generic term)
- `symbols` (AST term)

**Impact:** Scripts break when format changes, users don't know which to use.

---

### 2. Output Files
**Multiple overlapping outputs:**
- `graph.json` (87k components)
- `unified_analysis.json` (older format)
- `components.csv` (same data as graph)
- `particles.csv` (same data as graph)
- `semantic_ids.json` (IDs only)
- `learning_report.json` (enriched data)

**Impact:** Which is canonical? Which should external tools read?

---

### 3. Antimatter Terminology
**Two meanings:**
- "Antimatter" = All violations (umbrella term)
- "God Classes" = One type of violation

**Current issue:** Sometimes used interchangeably

**Impact:** Unclear what's being measured

---

## Proposal A: Physics Metaphor (RECOMMENDED)

**Core principle:** Lean into the physics analogy consistently

### Terminology
| Concept | Name | Rationale |
|---------|------|-----------|
| Code element | **Particle** | Fundamental unit (atom is taken) |
| Collection | **Particles** | Plural |
| Graph node | **Particle** (same) | No separate term |
| Output file | **collider_output.json** | Main result |
| Violations | **Antimatter** | Umbrella term |
| God Class | **God Particle** | Specific violation type |

### File Structure
```
output/
├── collider_output.json    # Main canonical output
│   ├── particles: []        # All code elements
│   ├── interactions: []     # Edges/dependencies
│   ├── antimatter: {}       # Violations by type
│   │   ├── god_particles: []
│   │   ├── cross_layer: []
│   │   └── circular_deps: []
│   └── stats: {}
├── particles.csv            # Flat export (legacy compat)
└── report.html              # Visualization
```

### API Example
```python
from collider import analyze

result = analyze("./my_repo")
result.particles         # List of all particles
result.antimatter        # Violations object
result.antimatter.god_particles  # Specific type
```

### Pros
- ✅ Consistent metaphor (Collider = particles)
- ✅ Clear hierarchy (antimatter → types)
- ✅ Memorable terminology
- ✅ Aligns with brand ("Standard Model")

### Cons
- ⚠️ "God Particle" might confuse (not same as Higgs)
- ⚠️ Physics metaphor may not resonate with all devs

---

## Proposal B: Software Engineering Standard

**Core principle:** Use conventional SE terms

### Terminology
| Concept | Name | Rationale |
|---------|------|-----------|
| Code element | **Symbol** | AST term |
| Collection | **Symbols** | Plural |
| Graph node | **Node** | Graph theory |
| Output file | **analysis.json** | Generic |
| Violations | **Violations** | Direct |
| God Class | **God Class** | Established term |

### File Structure
```
output/
├── analysis.json           # Main output
│   ├── symbols: []         # Code elements
│   ├── dependencies: []    # Edges
│   ├── violations: {}      # Issues
│   │   ├── god_classes: []
│   │   ├── layer_violations: []
│   │   └── circular_deps: []
│   └── metrics: {}
├── symbols.csv             # Flat export
└── report.html             # Viz
```

### Pros
- ✅ Familiar to SE community
- ✅ Self-explanatory
- ✅ No metaphor confusion

### Cons
- ⚠️ Generic (less distinctive)
- ⚠️ "Symbol" conflicts with compiler terminology
- ⚠️ Loses brand identity

---

## Proposal C: Minimal Change

**Core principle:** Keep physics terms, just standardize

### Terminology
| Concept | Name | Change |
|---------|------|--------|
| Code element | **Component** | Keep current |
| Collection | **Components** | Keep |
| Graph node | **Component** | Keep |
| Output file | **graph.json** | Keep |
| Violations | **Antimatter** | Keep |
| God Class | **God Class** | Clarify relationship |

### Changes
1. Deprecate: particles.csv, semantic_ids.json
2. Keep: graph.json as canonical
3. Document: "Antimatter includes God Classes, layer violations, etc."

### Pros
- ✅ Minimal disruption
- ✅ Existing tools still work
- ✅ Fast to implement

### Cons
- ⚠️ "Component" overloaded (React components?)
- ⚠️ Doesn't fully solve confusion
- ⚠️ Misses chance to improve

---

## Proposal D: Hybrid (Physics + Clarity)

**Core principle:** Physics metaphor but with clear aliases

### Terminology
| Concept | Primary | Alias | In Code |
|---------|---------|-------|---------|
| Code element | **Particle** | node, element | `particle` |
| Collection | **Particles** | nodes | `particles` |
| Output file | **collider_analysis.json** | - | - |
| Violations | **Defects** | antimatter | `defects` |
| God Class | **God Class** | bloated_class | `god_class` |

### File Structure
```
output/
├── collider_analysis.json  # Canonical
│   ├── particles: []
│   ├── edges: []
│   ├── defects: {          # Clear, not "antimatter"
│   │   god_classes: [],
│   │   layer_violations: [],
│   │   coupling_issues: []
│   │ }
│   └── metadata: {}
└── report.html
```

### Pros
- ✅ Physics branding preserved
- ✅ "Defects" clearer than "Antimatter"
- ✅ Familiar SE term (God Class)

### Cons
- ⚠️ More to learn (primary + alias)
- ⚠️ "Defects" loses metaphor elegance

---

## Comparison Matrix

| Criteria | A: Physics | B: SE Standard | C: Minimal | D: Hybrid |
|----------|------------|----------------|------------|-----------|
| **Brand consistency** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Clarity** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Ease of adoption** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Memorability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **SE familiarity** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Breaking changes** | High | High | Low | Medium |

---

## Recommendation: Proposal D (Hybrid)

**Why:**
1. **Preserves brand** ("Collider" + particles)
2. **Improves clarity** (defects > antimatter)
3. **Balances metaphor with SE terms**
4. **Medium breaking changes** (manageable migration)

**Implementation Plan:**

### Phase 1: Update Core (1 week)
- Rename `graph.json` → `collider_analysis.json`
- Unify schema: `particles`, `edges`, `defects`
- Add `@deprecated` warnings to old fields

### Phase 2: Update Scripts (1 week)
- Fix all internal scripts to use new names
- Add backwards compat layer (read old format)

### Phase 3: Update Docs (3 days)
- Global find/replace in docs
- Update README, CANONICAL_SCHEMA
- Add migration guide

### Phase 4: Deprecate (1 month notice)
- Mark old files/fields as deprecated
- Print warnings when used
- Remove in next major version

---

## Alternative Recommendations

**If brand is less important:** Proposal B (SE Standard)
- Most familiar to traditional devs
- Least explanation needed

**If stability is critical:** Proposal C (Minimal)
- Ships fastest
- Least disruption

**If physics is core:** Proposal A (Pure Physics)
- Most distinctive
- Best for differentiation

---

## Decision Criteria

**Choose Proposal A if:**
- Physics branding is essential
- Target audience: academic/research
- Willing to educate users on metaphor

**Choose Proposal B if:**
- Targeting enterprise/conservative teams
- Familiarity > brand identity
- Want fastest adoption

**Choose Proposal C if:**
- Time-constrained
- Many existing integrations
- Can't afford breaking changes

**Choose Proposal D if:**
- Want best of both worlds
- Can manage medium migration
- Value clarity + brand

---

## Next Steps (After Decision)

1. **Vote/decide** on proposal
2. **Create migration plan** (version, timeline)
3. **Implement Phase 1** (core schema)
4. **Update mini-validation** to use new names
5. **Document** in CHANGELOG

---

**My vote: Proposal D (Hybrid)**

Balances all concerns while pushing toward clarity.
