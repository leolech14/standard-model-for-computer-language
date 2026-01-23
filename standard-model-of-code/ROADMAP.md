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

### Deliverables ✓
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

## Phase 5 — Dimensions + attributes enrichment

**Goal:** Turn the graph into an analysis machine.

### Deliverables
1. **Dimensions D1–D8 for N_atomic**
2. **Attributes A1–A8** (formerly "Lenses")
3. **Evidence model** (confidence + evidence per field)
4. **Terminology standardization**
   - **Attributes** = inherent properties of each atom (schema/data model)
   - **Lenses** = analytical perspectives for examining code (process/methodology)
   - Update THEORY.md, schema files, and code to use consistent terminology:
     > "Every atom has 8 **attributes**. We examine them through 8 **lenses**."

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

## Phase 10 — Adaptive Intelligence Layer (SURVEY)

**Goal:** Make Collider smart about WHAT to analyze before HOW to analyze.

### Problem Statement
Collider currently parses everything blindly. Analyzing `viz/assets/` produced 4,342 nodes where 80% (3,500+) came from vendor libraries (`three.min.js`, `3d-force-graph.min.js`). The signal-to-noise ratio is destroyed.

### Solution: Pre-Analysis Survey Phase

```
┌────────────────────────────────────────────────────────────┐
│  NEW: Stage 0 — SURVEY (AI-Powered)                        │
├────────────────────────────────────────────────────────────┤
│  1. Directory scan (fast, no parsing)                      │
│  2. Pattern detection:                                     │
│     - vendor/, node_modules/, lib/, dist/                  │
│     - *.min.js, *.bundle.js (minified)                     │
│     - *.generated.ts, *.pb.go (generated)                  │
│     - __fixtures__/, testdata/ (test data)                 │
│  3. Heuristics:                                            │
│     - Single-line files > 10KB = minified                  │
│     - Avg line length > 500 chars = minified               │
│     - No whitespace variance = obfuscated                  │
│  4. AI classification (analyze.py):                        │
│     - "Is this vendor code?" → exclude                     │
│     - "What's the project structure?" → configure          │
│     - "Estimated complexity?" → warn/adapt                 │
│  5. Output: analysis_config.yaml                           │
│     - exclude_patterns: [...]                              │
│     - focus_paths: [...]                                   │
│     - estimated_nodes: N                                   │
│     - recommended_flags: [...]                             │
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│  Stage 1 — AST Parsing (with config applied)               │
│  Now only parses YOUR code, not vendor libraries           │
└────────────────────────────────────────────────────────────┘
```

### Deliverables

1. **Survey Module** (`src/core/survey.py`)
   - Fast directory scanner (no AST, just file stats)
   - Pattern-based exclusion detector
   - Minification heuristics
   - Token/complexity estimator

2. **AI Integration** (optional, via analyze.py)
   - Gemini-powered project understanding
   - Smart exclusion recommendations
   - "What kind of codebase is this?"

3. **CLI Integration**
   - `./collider survey <path>` — Run survey only, output config
   - `./collider full <path> --survey` — Auto-survey before analysis
   - `./collider full <path> --exclude vendor/` — Manual exclusion

4. **Interactive Mode**
   ```
   $ ./collider full ./my-app

   [SURVEY] Detected potential exclusions:
     - node_modules/     (1,247 files, ~50MB)
     - vendor/three.js   (minified, 30K lines)
     - dist/             (build output)

   Exclude these? [Y/n/customize]:
   ```

### Acceptance Tests
- Survey completes in <5s for repos up to 10K files
- Minified file detection accuracy >95%
- Vendor directory detection accuracy 100%
- Analysis of `viz/assets/` with survey → <500 nodes (vs 4,342)

### Metrics
- `survey_time_ms`
- `exclusion_accuracy`
- `signal_to_noise_ratio = your_code_nodes / total_nodes`
- `analysis_speedup = time_without_survey / time_with_survey`

### Implementation Phases

| Sub-phase | Deliverable | Complexity |
|-----------|-------------|------------|
| 10.1 | Pattern-based exclusions (no AI) | LOW |
| 10.2 | Minification heuristics | LOW |
| 10.3 | CLI --exclude flag | LOW |
| 10.4 | Interactive survey mode | MEDIUM |
| 10.5 | AI-powered classification | MEDIUM |
| 10.6 | Auto-survey by default | LOW |

### Why This Matters
- **Focus**: Analyze YOUR code, not npm's code
- **Speed**: 10x faster on typical JS/TS projects
- **Signal**: Clean graphs that show YOUR architecture
- **UX**: Users don't need to know what to exclude

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
| PR7 | Dimensions/Attributes | Enrichment passes + evidence model + terminology |
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

*Last updated: 2026-01-16*
