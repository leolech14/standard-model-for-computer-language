# PROJECT_elements Evolution Analysis Plan

> Bird's Eye View + Past Evolution + Evolvability Assessment

## Objective

Create a complete temporal-structural understanding of PROJECT_elements:
1. **WHERE** - Current state (topology, structure)
2. **WHENCE** - Past evolution (how it got here)
3. **WHITHER** - Evolvability (where it can go)

---

## Phase 1: WHENCE (Past Evolution)

### 1.1 Git Archaeology
**Tool**: `git log`, custom scripts
**Output**: `GENESIS_TIMELINE.md`

```bash
# Genesis commits - when was each major component born?
git log --diff-filter=A --format="%ai %s" --name-only | head -500

# Commit frequency over time
git log --format="%ad" --date=short | sort | uniq -c

# Major contributors/sessions
git shortlog -sn

# File churn (most modified files)
git log --format=format: --name-only | sort | uniq -c | sort -rn | head -50
```

**Questions to answer**:
- When was standard-model-of-code/ created?
- When was context-management/ created?
- When was .agent/ created?
- What were the "epochs" of development?

### 1.2 Structural Fossils
**Tool**: LOL + REPO_HISTORY.jsonl
**Output**: `STRUCTURAL_FOSSILS.md`

Look for:
- Orphaned files (created but never modified)
- Abandoned directories
- Legacy patterns (old naming conventions)
- Dead ends (code that leads nowhere)

### 1.3 Dependency Archaeology
**Tool**: Collider output
**Output**: `DEPENDENCY_EVOLUTION.md`

Map:
- Core dependencies that everything relies on
- Peripheral code that relies on core
- Islands (disconnected components)
- Bridges (connectors between domains)

---

## Phase 2: WHERE (Current State - Bird's Eye)

### 2.1 Topological Map
**Tool**: Collider `topology` section
**Output**: `TOPOLOGY_MAP.md`

Extract:
- Overall shape (Star? Mesh? Islands?)
- Centralization score
- Component count
- Largest cluster
- Density

### 2.2 Domain Census
**Tool**: LOL_UNIFIED.csv
**Output**: `DOMAIN_CENSUS.md`

For each domain (Particle, Wave, Observer, Meta):
- File count
- Total size
- Primary categories
- Health metrics (freshness, symmetry, purpose clarity)

### 2.3 Role Distribution
**Tool**: Collider `classification.by_role`
**Output**: `ROLE_ATLAS.md`

Map:
- What roles exist?
- Which roles are over/under-represented?
- Role clusters (which roles appear together?)

### 2.4 Health Dashboard
**Tool**: Collider + symmetry_check + purpose_field
**Output**: `HEALTH_DASHBOARD.md`

Metrics:
- Knot score (tangledness)
- Symmetry score (Wave-Particle balance)
- Purpose clarity (coherence)
- Dead code percentage
- Type coverage
- Test coverage proxy

---

## Phase 3: WHITHER (Evolvability)

### 3.1 Constraint Analysis
**Tool**: Collider `constraint_field`
**Output**: `CONSTRAINTS.md`

Identify:
- God classes (high entropy, multiple purposes)
- Tight coupling (hard to change)
- Missing abstractions (repeated patterns)
- Layer violations (architectural debt)

### 3.2 Growth Vectors
**Tool**: Collider `recommendations` + AI analysis
**Output**: `GROWTH_VECTORS.md`

Assess:
- Where can new code be added easily?
- Where would changes cause cascading effects?
- What interfaces are stable vs volatile?

### 3.3 Capability Gaps
**Tool**: Collider `theory_completeness` + manual analysis
**Output**: `CAPABILITY_GAPS.md`

Find:
- Planned but unimplemented features
- TODO/FIXME comments
- Stub functions
- Empty implementations

### 3.4 Evolutionary Fitness
**Tool**: Synthesize all above
**Output**: `EVOLUTIONARY_FITNESS.md`

Score:
- **Modularity**: Can parts evolve independently?
- **Extensibility**: Can new capabilities be added?
- **Maintainability**: Can existing code be understood and changed?
- **Resilience**: Can the system recover from changes?

---

## Execution Order

```
Phase 1 (WHENCE)           Phase 2 (WHERE)           Phase 3 (WHITHER)
─────────────────          ─────────────────         ─────────────────
1.1 Git Archaeology   ──┬──▶ 2.1 Topology Map   ──┬──▶ 3.1 Constraints
1.2 Structural Fossils ─┤   2.2 Domain Census   ─┤   3.2 Growth Vectors
1.3 Dependency Arch.  ──┘   2.3 Role Atlas     ─┤   3.3 Capability Gaps
                            2.4 Health Dashboard─┘   3.4 Fitness Score
                                    │
                                    ▼
                         UNIFIED_EVOLUTION_REPORT.md
```

---

## Tools Required

| Tool | Location | Status |
|------|----------|--------|
| Collider | `./pe collider full` | ✅ Ready |
| LOL Sync | `.agent/tools/lol_sync.py` | ✅ Ready |
| LOL Unify | `.agent/tools/lol_unify.py` | ✅ Ready |
| TDJ | `.agent/intelligence/tdj.jsonl` | ✅ Ready |
| REPO_HISTORY | `.agent/intelligence/REPO_HISTORY.jsonl` | ✅ Ready |
| Symmetry Check | `.agent/tools/symmetry_check.py` | ✅ Ready |
| Git | system | ✅ Ready |
| analyze.py | `context-management/tools/ai/analyze.py` | ✅ Ready |

---

## Estimated Output

After execution:
```
.agent/intelligence/evolution/
├── GENESIS_TIMELINE.md      # When things were born
├── STRUCTURAL_FOSSILS.md    # Dead/orphaned code
├── DEPENDENCY_EVOLUTION.md  # How dependencies grew
├── TOPOLOGY_MAP.md          # Current shape
├── DOMAIN_CENSUS.md         # What's in each domain
├── ROLE_ATLAS.md            # Role distribution
├── HEALTH_DASHBOARD.md      # Current health metrics
├── CONSTRAINTS.md           # What limits evolution
├── GROWTH_VECTORS.md        # Where growth is easy
├── CAPABILITY_GAPS.md       # What's missing
├── EVOLUTIONARY_FITNESS.md  # Overall score
└── UNIFIED_EVOLUTION_REPORT.md  # Executive summary
```

---

## Success Criteria

After this analysis, we should be able to answer:

1. **Origin**: "The repo was born on [date] with [core component]"
2. **Growth**: "It grew through [N] major epochs: [list]"
3. **Current**: "Today it has [N] files across [M] domains with [shape] topology"
4. **Health**: "Health score is [X]/100 due to [factors]"
5. **Future**: "It can most easily evolve in [directions] but is constrained by [factors]"

---

## Next Action

**Execute Phase 1.1: Git Archaeology**

```bash
./pe evolve --phase genesis
```

Or manually:
```bash
python3 .agent/tools/evolution_analyzer.py --phase 1.1
```
