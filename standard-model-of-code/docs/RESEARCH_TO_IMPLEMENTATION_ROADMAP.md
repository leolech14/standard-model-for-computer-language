# Research → Documentation → Implementation Roadmap

> **Principle:** Research FIRST, document WHILE researching, implement AFTER understanding.
>
> **Goal:** Leverage new theory additions in Collider via Tree-sitter's underutilized 90%.

---

## Phase 0: Current State Assessment

### What We Have (Implemented)

| Component | Location | Status |
|-----------|----------|--------|
| `topology_role` | `full_analysis.py:705-735` | ✅ LIVE |
| `in_degree`, `out_degree` | `full_analysis.py` | ✅ LIVE |
| Basic Tree-sitter parsing | `tree_sitter_engine.py` | ✅ 5-10% utilized |
| Dependency graph | `edge_extractor.py` | ✅ LIVE |
| NetworkX integration | `full_analysis.py` | ✅ LIVE |

### What We Theorized (Not Implemented)

| Concept | Theory Doc | Research Status | Implementation |
|---------|------------|-----------------|----------------|
| Flow Substances | THEORY_EXPANSION §7 | ⚪ OPEN QUESTIONS | ⚪ NOT STARTED |
| Interface Surface | THEORY_EXPANSION §8 | ⚪ OPEN QUESTIONS | ⚪ NOT STARTED |
| Evolvability | THEORY_EXPANSION §9 | ⚪ OPEN QUESTIONS | ⚪ NOT STARTED |
| Network Centrality | RESEARCH_DIRECTIONS §1.3 | ✅ RESEARCHED | ⚪ NOT STARTED |
| Biological Modularity | RESEARCH_DIRECTIONS §1.4 | ✅ RESEARCHED | ⚪ NOT STARTED |

### Tree-sitter Capabilities (Unutilized)

| Capability | Tree-sitter Feature | SMC Theory Connection | Priority |
|------------|--------------------|-----------------------|----------|
| Scope tracking | `@local.scope` | Interface Surface | HIGH |
| Definition tracking | `@local.definition` | What's INSIDE boundary | HIGH |
| Reference tracking | `@local.reference` | What CROSSES boundary | HIGH |
| Unused detection | def without ref | Dead code / Orphan | MEDIUM |
| Data flow | Assignment tracking | Flow Substances | HIGH |
| State detection | Mutation patterns | D5_STATE dimension | MEDIUM |
| Side effects | I/O call patterns | D6_EFFECT dimension | MEDIUM |

---

## Phase 1: RESEARCH (Current Priority)

### 1.1 Network Centrality Deep Dive

**Research Questions:**
- [ ] What betweenness threshold indicates "bridge" nodes?
- [ ] Does high PageRank correlate with change frequency (git)?
- [ ] Can clustering coefficient predict module boundaries?
- [ ] What's the relationship between centrality and bug density?

**Method:**
1. Compute all centrality metrics on existing Collider output
2. Correlate with git history (change frequency, bug fixes)
3. Document findings before implementing

**Output:** `docs/research/CENTRALITY_ANALYSIS.md`

---

### 1.2 Evolvability Measurement Research

**Research Questions:**
- [ ] Can evolvability be measured from structure alone?
- [ ] What's the correlation between topology_role and actual change success?
- [ ] Does Wagner's "neutral network" concept apply to code?
- [ ] How do we measure "weak linkage" quantitatively?

**Method:**
1. Review Wagner, Kirschner, Gerhart papers in depth
2. Identify biological metrics that translate to code
3. Propose candidate formulas (not implement yet)
4. Validate against real codebases

**Output:** `docs/research/EVOLVABILITY_METRICS.md`

---

### 1.3 Interface Surface Research

**Research Questions:**
- [ ] What IS an interface in terms of Tree-sitter nodes?
- [ ] How do we detect "public" vs "private" across languages?
- [ ] What makes an interface "good" (measurable)?
- [ ] Can we detect Liskov violations from structure?

**Method:**
1. Study Tree-sitter's `locals.scm` for Python, JS, TS
2. Map scope boundaries to interface concepts
3. Research existing interface quality metrics
4. Document language-specific patterns

**Output:** `docs/research/INTERFACE_SURFACE_ANALYSIS.md`

---

### 1.4 Flow Substances Research

**Research Questions:**
- [ ] What "substances" actually matter for architecture health?
- [ ] Can we distinguish control flow from data flow in static analysis?
- [ ] How does information theory apply to code flow?
- [ ] What's the relationship between static structure and runtime flow?

**Method:**
1. Literature review on data flow analysis
2. Study Tree-sitter's capabilities for tracking assignments
3. Explore information-theoretic metrics (entropy, mutual information)
4. Document what's measurable vs what needs runtime

**Output:** `docs/research/FLOW_SUBSTANCES_ANALYSIS.md`

---

## Phase 2: DOCUMENTATION (Parallel with Research)

### Living Documents to Maintain

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `THEORY_EXPANSION_2026.md` | Open questions, directions | As discoveries happen |
| `RESEARCH_DIRECTIONS.md` | External theory synthesis | After each research session |
| `MODEL.md` | Canonical theory (only confirmed) | After validation |
| `TREE_SITTER_INTEGRATION_SPEC.md` | Implementation guide | After research confirms approach |

### Documentation Standards

1. **Questions before answers** - Document what we don't know
2. **Evidence required** - No implementation without research backing
3. **Confidence levels** - Mark everything as FACT/HIGH/MEDIUM/LOW
4. **Traceability** - Link theory → research → implementation

---

## Phase 3: IMPLEMENTATION (After Research)

### 3.1 Network Centrality (Ready for Implementation)

**Why Ready:** Well-established algorithms, NetworkX has them.

```python
# Proposed addition to full_analysis.py Stage 7

# Centrality metrics (requires research validation first)
if G is not None:
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)
    # pagerank only for directed graphs
    pagerank = nx.pagerank(G) if G.is_directed() else {}

    for node in nodes:
        node_id = node.get('id', '')
        node['betweenness_centrality'] = betweenness.get(node_id, 0)
        node['closeness_centrality'] = closeness.get(node_id, 0)
        node['pagerank'] = pagerank.get(node_id, 0)
```

**Blocker:** Need research to determine:
- Thresholds for "high" vs "low"
- Which metrics actually predict problems
- How to normalize across different graph sizes

---

### 3.2 Tree-sitter Scope Analysis (Needs Research First)

**Why Not Ready:** Need to understand scope semantics per language.

**Research Required:**
1. How does `@local.scope` work in Python vs JS vs TS?
2. What constitutes a "boundary" in each language?
3. How do we handle dynamic languages (duck typing)?

**Proposed Implementation (after research):**

```python
# src/core/scope_analyzer.py (NEW FILE - AFTER RESEARCH)

class ScopeAnalyzer:
    """
    Analyze scope boundaries using Tree-sitter locals.scm

    Maps to SMC concepts:
    - @local.scope → Interface boundary
    - @local.definition → Internal (private)
    - @local.reference → Cross-boundary usage
    """

    def analyze_interface_surface(self, node, tree, source):
        # Implementation depends on research findings
        pass
```

---

### 3.3 Evolvability Score (Needs Research First)

**Why Not Ready:** No validated formula exists.

**Candidate Factors (from research):**

```python
# HYPOTHETICAL - DO NOT IMPLEMENT UNTIL VALIDATED

def compute_evolvability(node):
    """
    Evolvability = capacity to change without breaking system

    Candidate factors (need validation):
    - coupling_freedom: 1 / (1 + in_degree)  # fewer dependents = freer
    - interface_stability: from git history
    - test_coverage: from coverage reports
    - centrality_risk: 1 - betweenness  # not on critical paths
    """
    # Formula TBD after research
    pass
```

---

## Phase 4: COLLIDER INTEGRATION

### How Theory Additions Enhance Collider Output

| Theory Addition | Collider Enhancement | User Value |
|-----------------|---------------------|------------|
| `topology_role` | Node classification in viz | See leaves vs hubs instantly |
| Network centrality | Highlight critical paths | Know what NOT to break |
| Evolvability | Color by change safety | Know WHERE to evolve safely |
| Interface surface | Show boundaries in graph | Understand module contracts |
| Flow substances | Animate data flow | See what moves through system |

### Proposed Collider Output Enhancements

#### Brain Download (output.md)

```markdown
## TOPOLOGY ANALYSIS (NEW SECTION)

### Flow Structure
| Role | Count | % | Health |
|------|-------|---|--------|
| Root (entry points) | 12 | 3% | ✓ |
| Leaf (terminals) | 89 | 22% | ✓ |
| Hub (coordinators) | 8 | 2% | ⚠ High coupling |
| Internal (flow) | 290 | 72% | ✓ |
| Orphan (dead) | 5 | 1% | ✗ Remove |

### Critical Paths (Betweenness > 0.1)
- `src/core/full_analysis.py::run_full_analysis` - 43% of paths
- `src/core/edge_extractor.py::extract_edges` - 28% of paths

### Evolvability Zones
- **Safe to change (periphery):** 89 leaf nodes
- **Careful (boundary):** 290 internal nodes
- **Dangerous (core):** 8 hub nodes

### Recommendations
1. **Refactor hub:** `full_analysis.py` has betweenness 0.43 - split responsibilities
2. **Remove orphans:** 5 unreachable nodes detected
3. **Test coverage gap:** Hub nodes have 34% coverage (should be >80%)
```

#### Visualization (HTML)

```javascript
// Color nodes by evolvability zone
function getNodeColor(node) {
    if (node.topology_role === 'leaf') return '#4CAF50';  // Green - safe
    if (node.topology_role === 'hub') return '#F44336';   // Red - dangerous
    if (node.topology_role === 'orphan') return '#9E9E9E'; // Gray - dead
    if (node.betweenness > 0.1) return '#FF9800';         // Orange - critical path
    return '#2196F3';  // Blue - normal
}
```

---

## Phase 5: VALIDATION

### Before Any Implementation

1. **Hypothesis:** State what we expect to find
2. **Experiment:** Analyze real codebases
3. **Measure:** Correlate metrics with known outcomes (bugs, changes)
4. **Document:** Write up findings with evidence
5. **Implement:** Only if research supports it

### Validation Codebases

| Codebase | Size | Why |
|----------|------|-----|
| Collider itself | ~50 files | We know it intimately |
| express.js | Medium | Well-documented architecture |
| lodash | Large | Many small functions (leaf-heavy?) |
| A monolith | Large | Hub-heavy, coupling problems |

---

## Current Action Items

### Completed (Jan 21, 2026)
- [x] Document theory framework (THEORY_EXPANSION_2026.md)
- [x] Research external theories (RESEARCH_DIRECTIONS.md)
- [x] Create roadmap (this document)
- [x] **Centrality research** on Collider itself via Perplexity API
- [x] Run centrality analysis on Collider's own graph - **VALIDATED**
- [x] Document findings in `docs/research/CENTRALITY_ANALYSIS.md`
- [x] Fetch tree-sitter locals.scm for Python/JS/TS/Go - **DOCUMENTED**

### Validation Results (Jan 21, 2026)
- `topology_role` computed on 1768 nodes
- Distribution: 52% internal, 21% leaf, 17% root, 7% orphan, 4% hub
- Top hub: `layout.js::get` (310 in-degree) - potential risk point
- See `docs/research/CENTRALITY_ANALYSIS.md` for details

### T2 Ecosystem Detection (Jan 21, 2026)

**Problem:** Framework detection (Django/Flask/FastAPI) was at 0% due to `all()` bug in `detect_t2_atom()`.

**Quick Fix Applied:**
- Changed `all()` to `any()` for keyword matching
- Patterns now detect correctly (verified Django, Flask, FastAPI)

**Long-term Recommendation (from Oracle/Perplexity):**
- String matching is fundamentally limited
- Production tools (Semgrep, Bandit) use AST-based detection
- Tree-sitter queries can match structural patterns, not just text
- Example: Detect `@app.route` as a decorator node, not a substring

**Next Steps for T2 Detection:**
- [ ] Write tree-sitter queries for Django/Flask/FastAPI patterns
- [ ] Replace string matching with structural AST queries
- [ ] Test against real framework repositories

### Next Session
- [ ] Correlate topology_role with git history (change frequency, bug fixes)
- [ ] Implement betweenness centrality in full_analysis.py
- [ ] Implement PageRank in full_analysis.py
- [ ] Investigate 116 orphan nodes (dead code analysis)

### Future
- [ ] Evolvability formula validation (empirical)
- [ ] Interface surface detection via Tree-sitter scopes
- [ ] Flow substance tracking
- [ ] NST element mapping to SMC atoms

---

## Guiding Principles

1. **Research proves implementation** - No code without evidence
2. **Questions are valuable** - Document unknowns explicitly
3. **Theory guides practice** - SMC theory informs what to build
4. **Tree-sitter is the key** - 90% untapped capability
5. **Collider is the product** - All theory serves tool usefulness
