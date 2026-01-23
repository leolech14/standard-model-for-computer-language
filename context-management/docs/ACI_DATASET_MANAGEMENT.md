# ACI Dataset Management Science

> The "Curriculum Compiler" - Preparing optimal study material for AI before answering.

## Executive Summary

ACI (Adaptive Context Intelligence) is a 4-tier context curation system that automatically selects, optimizes, and positions codebase context for AI queries. It treats context as a carefully engineered dataset where token budget, file positioning, and intelligent caching enable optimal reasoning performance.

---

## System Architecture

```
                              USER QUERY
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TIER 0: INSTANT (<100ms)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  load_repo_truths() → answer_from_truths()                          │   │
│  │  Source: .agent/intelligence/truths/repo_truths.yaml                │   │
│  │  Patterns: "how many *", "count of *", "total *"                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ✓ HIT: Return cached answer (0 tokens, 0 API calls)                       │
│  ✗ MISS: Continue to Query Analyzer                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         QUERY ANALYZER                                      │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │
│  │    INTENT     │  │  COMPLEXITY   │  │    SCOPE      │                   │
│  ├───────────────┤  ├───────────────┤  ├───────────────┤                   │
│  │ ARCHITECTURE  │  │ SIMPLE (<3kw) │  │ INTERNAL      │                   │
│  │ DEBUG         │  │ MODERATE      │  │ EXTERNAL      │                   │
│  │ RESEARCH      │  │ COMPLEX (>6kw)│  │ HYBRID        │                   │
│  │ TASK          │  └───────────────┘  └───────────────┘                   │
│  │ COUNT         │                                                          │
│  │ LOCATE        │  Output: QueryProfile(intent, complexity, scope,        │
│  │ EXPLAIN       │          needs_agent_context, suggested_sets)           │
│  │ IMPLEMENT     │                                                          │
│  └───────────────┘                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SEMANTIC MATCHER (Graph-based)                         │
│                                                                             │
│  Uses Standard Model of Code relationship graph for intelligent selection:  │
│                                                                             │
│  PURPOSE FIELD (π₁-π₄)           DIMENSION SPACE (8D)                       │
│  ═══════════════════════         ════════════════════                       │
│  π₁ = Role (atomic)              D1: WHAT (atom type)                       │
│  π₂ = Retrieve/Transform/...     D2: Layer (arch layer)                     │
│  π₃ = DataAccess/BusinessLogic   D3: Role (DDD role)                        │
│  π₄ = System-level purpose       D4-D8: Boundary/State/Effect/...           │
│                                                                             │
│  Query: "how does repository fetch user data"                               │
│      → π₂ match: Retrieve                                                   │
│      → Layer match: Infrastructure                                          │
│      → Role match: Repository                                               │
│      → Flow: LAMINAR (coherent context)                                     │
│                                                                             │
│  EDGE TRAVERSAL (19 types, 5 families)                                      │
│  ═════════════════════════════════════                                      │
│  UPSTREAM:   inherits, implements, receives, decorates                      │
│  DOWNSTREAM: calls, imports, uses, returns, triggers                        │
│                                                                             │
│  Output: SemanticMatch(targets, suggested_files, context_flow, strategy)    │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TIER ROUTER                                        │
│                                                                             │
│  ROUTING_MATRIX[Intent × Complexity × Scope] → Tier                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  (COUNT, SIMPLE, INTERNAL)      → INSTANT   "Use cached truths"     │   │
│  │  (LOCATE, SIMPLE, INTERNAL)     → RAG       "File search + cite"    │   │
│  │  (DEBUG, MODERATE, INTERNAL)    → LONG_CTX  "Multi-file reasoning"  │   │
│  │  (ARCHITECTURE, ANY, INTERNAL)  → LONG_CTX  "Structural reasoning"  │   │
│  │  (TASK, ANY, ANY)               → LONG_CTX  "Agent context needed"  │   │
│  │  (RESEARCH, ANY, EXTERNAL)      → PERPLEXITY "Web search needed"    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Output: RoutingDecision(tier, primary_sets, fallback_tier, inject_agent)  │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              ┌─────────┐   ┌─────────┐   ┌─────────────┐
              │  TIER 1 │   │  TIER 2 │   │   TIER 3    │
              │   RAG   │   │LONG_CTX │   │  PERPLEXITY │
              │  (~5s)  │   │ (~60s)  │   │   (~30s)    │
              │  ~1k tk │   │~50-200k │   │   ~500 tk   │
              └────┬────┘   └────┬────┘   └──────┬──────┘
                   │             │               │
                   └─────────────┼───────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SET RESOLUTION                                        │
│                                                                             │
│  resolve_set("architecture_review")                                         │
│      │                                                                      │
│      ├── Expand includes: [pipeline, classifiers, constraints]              │
│      │       │                                                              │
│      │       ├── pipeline.patterns: ["src/core/full_analysis.py", ...]     │
│      │       ├── classifiers.patterns: ["src/core/classification/*.py"]    │
│      │       └── constraints.patterns: ["schema/constraints/*.yaml"]       │
│      │                                                                      │
│      ├── Merge patterns (deduplicated)                                      │
│      ├── Max aggregation: max_tokens = max(200k, 120k, 80k, 50k) = 200k    │
│      └── Extract: critical_files, positional_strategy                       │
│                                                                             │
│  Multi-Set Merging (_aci_merged):                                           │
│      ACI returns: [agent_tasks, agent_kernel, agent_full]                   │
│      → Creates dynamic set with merged patterns from all                    │
│      → 22 files vs 11 (single set would discard 2 of 3)                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FILE COLLECTION                                       │
│                                                                             │
│  list_local_files(base_dir, patterns, excludes)                             │
│                                                                             │
│  Security Exclusions (hardcoded):                                           │
│  ├── .env, *.key, *.pem, credentials.*                                      │
│  ├── .gcloud/, .aws/, __pycache__/                                          │
│  └── node_modules/, .git/                                                   │
│                                                                             │
│  Pattern Matching:                                                          │
│  ├── fnmatch.fnmatch(rel_path, pattern)                                     │
│  ├── Sorted walks for reproducibility                                       │
│  └── Multi-level: filename, relative path, path components                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT POSITIONING                                      │
│                                                                             │
│  U-SHAPED ATTENTION PATTERN:                                                │
│  LLMs recall beginning and end better than middle ("lost-in-middle")        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  SANDWICH STRATEGY                    FRONT-LOAD STRATEGY           │   │
│  │  ═══════════════════                  ════════════════════          │   │
│  │  ┌─────────────────┐                  ┌─────────────────┐           │   │
│  │  │ CRITICAL FILE 1 │ ← HIGH           │ CRITICAL FILE 1 │ ← HIGH    │   │
│  │  │ CRITICAL FILE 2 │ ← HIGH           │ CRITICAL FILE 2 │ ← HIGH    │   │
│  │  ├─────────────────┤                  ├─────────────────┤           │   │
│  │  │ regular file 3  │                  │ regular file 3  │           │   │
│  │  │ regular file 4  │ ← MEDIUM         │ regular file 4  │ ← MEDIUM  │   │
│  │  │ ...             │   (lost zone)    │ ...             │           │   │
│  │  │ regular file N  │                  │ regular file N  │           │   │
│  │  ├─────────────────┤                  └─────────────────┘           │   │
│  │  │ [ANCHOR BLOCK]  │ ← HIGH                                         │   │
│  │  │ - CRITICAL 1    │                                                │   │
│  │  │ - CRITICAL 2    │                                                │   │
│  │  └─────────────────┘                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TOKEN BUDGET ENFORCEMENT                                 │
│                                                                             │
│  Token Estimation: chars ÷ 4 ≈ tokens                                       │
│                                                                             │
│  Budget Tiers (aci_config.yaml):                                            │
│  ┌────────────────┬─────────┬──────────────────────────────────────────┐   │
│  │     Tier       │ Tokens  │              Risk Level                  │   │
│  ├────────────────┼─────────┼──────────────────────────────────────────┤   │
│  │ guru           │  50,000 │ Safe - focused analysis                  │   │
│  │ architect      │ 150,000 │ Medium - multi-file reasoning            │   │
│  │ archeologist   │ 200,000 │ High - deep exploration                  │   │
│  │ HARD_CAP       │ 200,000 │ DANGER - lost-in-middle effects begin    │   │
│  │ perilous       │ 200,001+│ AVOID - coherence degrades rapidly       │   │
│  └────────────────┴─────────┴──────────────────────────────────────────┘   │
│                                                                             │
│  Enforcement:                                                               │
│  if estimated > 1,000,000: CRITICAL ERROR (exceeds model limit)            │
│  if estimated > 800,000:   WARNING (80% of limit)                          │
│  if estimated > 50,000:    Enable interactive mode (caching)               │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FEEDBACK LOOP                                         │
│                                                                             │
│  Location: .agent/intelligence/aci_feedback.yaml                            │
│                                                                             │
│  Logged per query:                                                          │
│  ├── timestamp, query (truncated 200 chars)                                 │
│  ├── intent, complexity, scope                                              │
│  ├── tier, sets_used                                                        │
│  ├── tokens_input, tokens_output                                            │
│  ├── success, retry_count, fallback_used                                    │
│  ├── duration_ms                                                            │
│  └── error (if failed)                                                      │
│                                                                             │
│  Rolling Statistics:                                                        │
│  ├── total_queries                                                          │
│  ├── by_tier: {instant: N, rag: M, long_context: K, perplexity: J}         │
│  ├── by_intent: {architecture: N, task: M, ...}                            │
│  ├── success_rate (rolling average)                                         │
│  └── avg_tokens (rolling average)                                           │
│                                                                             │
│  Recommendations (after 10+ queries):                                       │
│  └── get_tier_recommendations() → {"tier": "High retry rate, use fallback"}│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Configuration Files

### 1. analysis_sets.yaml (Set Definitions)

```yaml
architecture_review:
  description: "Full architecture review"
  max_tokens: 200000
  auto_interactive: true
  includes:
    - pipeline      # 120k tokens
    - classifiers   # 80k tokens
    - constraints   # 50k tokens
  critical_files:
    - "standard-model-of-code/src/core/full_analysis.py"
    - "standard-model-of-code/docs/COLLIDER.md"
  positional_strategy: "sandwich"
```

### 2. aci_config.yaml (Runtime Config)

```yaml
# Token budgets
token_budgets:
  guru: 50000
  architect: 150000
  archeologist: 200000
  hard_cap: 200000

# Agent context triggers
agent_context:
  trigger_keywords:
    - task, sprint, agent, kernel, bare
    - truths, registry, confidence, claim
    - run, handoff, boot, protocol, manifest

# Tier-specific settings
tiers:
  perplexity:
    max_response_time_ms: 30000
    model: sonar-pro
```

### 3. repo_truths.yaml (Cached Facts)

```yaml
version: '2026-01-23T08:24:23'
validated_by: BARE/TruthValidator
confidence: 0.7

counts:
  files:
    python: 186
    javascript: 98
    yaml: 25
  lines_of_code: 130787
  functions: 341
  classes: 183

pipeline:
  stages: 18
```

---

## Key Data Science Principles

### 1. U-Shaped Attention Curve

LLMs exhibit stronger recall at context boundaries (beginning and end) than middle sections.

**Solution:** Sandwich strategy places critical files at both START and END of context.

### 2. Lost-in-Middle Effect

Beyond ~200k tokens, model coherence degrades as important information gets "buried."

**Solution:** Hard cap at 200k tokens; warn at 80% threshold.

### 3. Set Composition Semantics

When composing sets via `includes`, take the MAXIMUM token budget, not the sum.

**Rationale:** Overlapping patterns would double-count; max ensures headroom.

### 4. Instant Query Optimization

COUNT queries ("how many X") bypass AI entirely using cached truths.

**Performance:** <100ms vs ~60s for full reasoning.

### 5. Agent Context Injection

TASK-intent queries automatically inject `.agent/` context (kernel, tasks, intelligence).

**Trigger:** Intent detection or keyword match from `aci_config.yaml`.

### 6. Semantic Graph Matching (NEW)

Queries are matched against the Standard Model of Code relationship graph using:

**PURPOSE Field (π₁-π₄) Hierarchy:**
```
π₁ (Atomic)    = Role (Query, Validator, Repository)
π₂ (Molecular) = Emergent purpose (Retrieve, Persist, Transform, Validate)
π₃ (Organelle) = Container-level (DataAccess, BusinessLogic, Integration)
π₄ (System)    = File-level purpose distribution
```

**Semantic Distance Calculation:**
- 8-dimensional space: WHAT, Layer, Role, Boundary, State, Effect, Lifecycle, Trust
- ~17.9 million possible states (94 atoms × 29 roles × 6,561 RPBL permutations)
- Weighted dimension comparison for proximity scoring

**Context Flow Classification:**
- **Laminar:** Coherent context (single purpose, adjacent layers) → semantic sets first
- **Turbulent:** Mixed context (multiple purposes, scattered layers) → profile sets first

### 7. Graph Traversal for Context Expansion

Edges define causal relationships used for context expansion:

| Direction | Edge Types | Purpose |
|-----------|------------|---------|
| UPSTREAM | inherits, implements, receives, decorates | Find providers, dependencies |
| DOWNSTREAM | calls, imports, uses, returns, triggers | Find consumers, callers |

**Traversal Strategy:**
- **Focused:** Single high-confidence target → direct path
- **Exploratory:** Multiple low-confidence targets → breadth-first
- **Hierarchical:** Multi-layer query → level-by-level traversal

---

## File References

| Component | File | Key Lines |
|-----------|------|-----------|
| Set Definitions | `analysis_sets.yaml` | 1-459 |
| ACI Config | `aci_config.yaml` | 1-100 |
| Query Analyzer | `query_analyzer.py` | 225-387 |
| Tier Router | `tier_router.py` | 46-295 |
| Context Optimizer | `context_optimizer.py` | 69-273 |
| **Semantic Matcher** | `semantic_matcher.py` | 1-420 |
| Feedback Loop | `feedback_loop.py` | 44-267 |
| File Selection | `analyze.py` | 810-886 |
| Context Building | `analyze.py` | 1030-1089 |
| Set Resolution | `analyze.py` | 268-331 |
| Truths Cache | `repo_truths.yaml` | 1-21 |
| PURPOSE Field Schema | `particle.schema.json` | 614-655 |
| Dimensions Schema | `dimensions.json` | 1-83 |

---

## Tier Performance Matrix

| Tier | Latency | Tokens | Cost | Use Case |
|------|---------|--------|------|----------|
| INSTANT | <100ms | 0 | $0 | "how many files" |
| RAG | ~5s | ~1k | ~$0.002 | "find function X" |
| LONG_CONTEXT | ~60s | 50-200k | $0.10-0.40 | "explain architecture" |
| PERPLEXITY | ~30s | ~500 | ~$0.001 | "best practices 2026" |

---

*Document generated: 2026-01-23*
*System: ACI v1.0 (Adaptive Context Intelligence)*
