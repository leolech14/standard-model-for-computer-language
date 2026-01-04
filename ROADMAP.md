# SMOC Development Roadmap

**North Star:** Self-proving ASAP (proof_score ≥ 80%, phantoms = 0)

**Current State:** Phase 0 complete, PR #1 open with 23 commits

---

## Critical Path to Self-Proving

```
Phase 3 (entrypoints + reachability)
    ↓
Phase 2 (call resolution improvements)
    ↓
Phase 4 (auditability + determinism)
```

---

## Phase 0 — Locked invariants (DONE)

### Deliverables ✅
- Multi-layer graph spec: `GRAPH_LAYERS.md`
- Domain separation spec: `docs/SPEC.md v0.1.3`
- Guardrail tests (6 tests, all passing)
- TS extractor tests with always-run enum derivation guard

### Metrics
- Test suite: **102 passed, 3 skipped**

---

## Phase 1 — Graph substrate completion

**Goal:** Make node identity + node inventory rock-solid across repos.

### Deliverables
1. **Canonical node IDs**
   - Atomic IDs: `rel_path::function`, `rel_path::Class.method`, `rel_path::Class`
   - Container IDs: stable module/file IDs (collision-safe)

2. **Bidirectional containment**
   - `contains` edges: file → component (structural)
   - (Optional) `member_of` edges: component → file (reverse view)

3. **Stable registries**
   - `component_registry.json` for N_atomic
   - `file_registry.json` for N_container

### Acceptance Tests
- Registry accuracy for atomic registry is 100% on `src/core`
- `contains` edges exist for every atomic node
- No atomic ID collisions

### Metrics
- `|N_atomic|`, `|N_container|`
- `contains_coverage = atomic_nodes_with_parent_file / |N_atomic|`

---

## Phase 2 — Resolution correctness

**Goal:** Make resolution strict and reliable without mixing domains.

### Deliverables
1. **Call resolver (atomic target domain only)**
   - `calls`: resolve against N_atomic only
   - Never "upgrade" a file/container match into resolved_internal

2. **Import resolver (container target domain only)**
   - `imports`: resolve against N_container only
   - Strict stdlib/builtin classification

3. **Resolution evidence**
   - Every resolved_internal edge includes evidence fields

### Acceptance Tests
- Guardrails stay green
- Negative fixtures for: alias shadowing, relative vs absolute imports, builtin shadowing

### Metrics
- `calls_resolved_internal / calls_total`
- `imports_resolved_internal / imports_total`
- `unresolved_call_reasons` histogram

---

## Phase 3 — Entrypoints + reachability (PRIORITY)

**Goal:** Raise reachability while preserving rule-based entrypoints.

### Deliverables
1. **Entrypoint detection expansion (atomic-only)**
   - main patterns (`if __name__ == "__main__": main()`)
   - CLI frameworks (click/typer/fire/argparse)
   - Web frameworks (FastAPI/Flask routing decorators)
   - Test entrypoints behind flag (`--include-tests`)

2. **Reachability engine**
   - BFS/DFS over proof graph (calls + resolved_internal)
   - Persist witness paths for debuggable proof

3. **Reachability reporting**
   - Report why nodes are unreachable:
     - no incoming edges
     - edges unresolved
     - entrypoints missing

### Acceptance Tests
- Reachability increases on `src/core` from baseline (~29.3%)
- Guardrails stay green
- "Entrypoints are atomic-only" test exists and passes

### Metrics
- `reachability = reachable_atomic / |N_atomic|`
- `unreachable_buckets` (by reason)
- Target: `proof_score ≥ 80` AND `phantoms = 0`

---

## Phase 4 — Proof system hardening

**Goal:** Make proof outputs auditable and hard to fake.

### Deliverables
1. **Proof traceability**
   - Store witness paths for reachability
   - Store edge verification stats with evidence

2. **Proof invariants enforced in code**
   - Proof substrate definition centralized and tested
   - Denominators explicitly `|N_atomic|`

3. **"Self-proving" mode**
   - Single command returns pass/fail + diagnostics

### Acceptance Tests
- Proof graph matches recomputation from source
- Proof score stable across runs (deterministic)

### Metrics
- `proof_score`, `phantoms`, `edge_accuracy`, `connection_coverage`, `reachability`
- Determinism hash for artifacts

---

## Phase 5 — Dimensions + lenses enrichment

**Goal:** Turn the graph into an analysis machine.

### Deliverables
1. **Dimensions D1–D8 for N_atomic**
2. **Lenses R1–R8**
3. **Evidence model** (confidence + evidence per field)

### Metrics
- Enrichment coverage: `% atomic nodes with D-fields`
- Avg confidence and distribution

---

## Phase 6 — Pillars engine + derived graphs

**Goal:** Compute P1–P4 on the right graphs.

### Deliverables
1. **Atomic call graph metrics** (Markov, Knot, Game, Constructal)
2. **Derived graphs** (file dependency, aggregated call graph, interface graph)
3. **Issue detectors** (cycles, hotspots, unstable equilibria)

---

## Phase 7 — Productization

**Goal:** Make SMOC easy to run and integrate.

### Deliverables
- CLI contracts: `analyze`, `validate-all`, `prove`, `bundle`, `issues`, `viz`
- Output schema versioning
- Dashboard / report

---

## Phase 8 — Multi-language (TS/JS first)

**Goal:** Extend SMOC beyond Python.

### Deliverables
- TS/JS parity layer
- Cross-language normalization

---

## Phase 9 — Governance

**Goal:** Keep the theory coherent and implementation evolvable.

### Deliverables
- Versioned SPEC + changelog
- Theory-to-code map
- PR checklist for domain changes

---

## Suggested PR Sequence (Post PR #1)

| PR | Focus | Key Deliverable |
|----|-------|-----------------|
| PR2 | Entry rules expansion | Entrypoint detection for click/typer/FastAPI |
| PR3 | Reachability diagnostics | BFS engine + unreachable buckets report |
| PR4 | Call resolver upgrades | self/cls/import aliasing + fixtures |
| PR5 | Proof traceability | Witness paths + determinism hash |
| PR6 | Derived graphs | File-level aggregation (non-proof) |
| PR7 | Dimensions/Lenses | Enrichment passes + evidence model |
| PR8 | Pillars stabilization | Issue detectors |

---

## Current Bottleneck

```
Reachability: 29.3% ← This is the forcing function
```

**Root causes to investigate:**
1. Missing entrypoint rules (click/typer/FastAPI decorators)
2. Unresolved calls (self/cls patterns, import aliasing)
3. Isolated subgraphs (no path from any entrypoint)

---

*Last updated: 2026-01-04*
