# Workflow Factory

> A systematic approach to AI-powered codebase exploration using the hybrid Tier 1/Tier 2 system.

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │        WORKFLOW FACTORY             │
                    │   "Right tool for the right job"   │
                    └─────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
        ┌───────────────────┐           ┌───────────────────┐
        │   TIER 1: LONG    │           │  TIER 2: FILE     │
        │     CONTEXT       │           │     SEARCH        │
        │                   │           │                   │
        │ • Holistic view   │           │ • Needle queries  │
        │ • Architecture    │           │ • Citations       │
        │ • Cross-file      │           │ • Repeated Q&A    │
        │ • 1M tokens max   │           │ • Index once      │
        └───────────────────┘           └───────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
                    ┌───────────────────┐
                    │  COMBINED POWER   │
                    │                   │
                    │ File Search finds │
                    │ → Long Context    │
                    │   reasons deeply  │
                    └───────────────────┘
```

## Available File Search Stores

| Store | Files | Best For |
|-------|-------|----------|
| `collider-brain` | 14 | "How does local_analyze.py work?" |
| `collider-docs` | 96 | "What is the theory?" "What debt exists?" |
| `collider-pipeline` | 7 | "How does analysis flow?" "What stages exist?" |
| `collider-schema` | 19 | "What atoms exist?" "What are the roles?" |
| `collider-classifiers` | 10 | "How are nodes classified?" "What heuristics?" |

## Workflow Recipes

### Recipe 1: Understanding a Feature

```bash
# Step 1: Quick discovery with File Search
python local_analyze.py --search "How does role classification work?" \
  --store-name collider-classifiers

# Step 2: Deep dive with Long Context (if needed)
python local_analyze.py --set classifiers --interactive \
  "Explain the role_registry module in detail"
```

### Recipe 2: Debugging an Issue

```bash
# Step 1: Find relevant files
python local_analyze.py --search "Where is RPBL score calculated?" \
  --store-name collider-pipeline

# Citations tell you exactly which files matter

# Step 2: Read those specific files with Long Context
python local_analyze.py --file "src/core/standard_model_enricher.py" \
  "Why might RPBL scores be incorrect for utility functions?"
```

### Recipe 3: Architecture Review

```bash
# Step 1: Query docs for known issues
python local_analyze.py --search "What architecture debt exists?" \
  --store-name collider-docs

# Step 2: Full architecture review with composed set
python local_analyze.py --set architecture_review --interactive
```

### Recipe 4: Theory Exploration

```bash
# Step 1: Quick answer from indexed docs
python local_analyze.py --search "What are the 16 scale levels?" \
  --store-name collider-docs

# Step 2: Full theory deep dive
python local_analyze.py --set theory --interactive
```

### Recipe 5: Adding a New Feature

```bash
# Step 1: Find similar patterns
python local_analyze.py --search "How are new classifiers added?" \
  --store-name collider-classifiers

# Step 2: Understand the pipeline integration
python local_analyze.py --search "How do stages get added to full_analysis?" \
  --store-name collider-pipeline

# Step 3: Full context for implementation
python local_analyze.py --set pipeline "I want to add a new Stage 9 for X"
```

### Recipe 6: Socratic Research Loop (Confidence Boosting)

**Purpose:** Boost confidence on tasks until they meet execution thresholds.

**The Loop:**
```
┌─────────────────────────────────────────────────────────────────────┐
│                    SOCRATIC RESEARCH LOOP                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   1. IDENTIFY GAP                                                   │
│      Task at 85%, needs 95% (A+ threshold)                          │
│      Which dimension is the bottleneck?                             │
│                                                                     │
│   2. GEMINI: Internal Validation                                    │
│      "Does our codebase support this approach?"                     │
│      Boosts: Factual, Current                                       │
│                                                                     │
│   3. PERPLEXITY: External Validation                                │
│      "What do industry best practices say?"                         │
│      Boosts: Factual (external confirmation)                        │
│                                                                     │
│   4. FILE READS: Ground Truth                                       │
│      Read actual files to verify assumptions                        │
│      Boosts: Factual (to 95%+)                                      │
│                                                                     │
│   5. SYNTHESIS: Revised Score                                       │
│      Update 4D matrix with evidence                                 │
│      If min(4D) >= threshold → EXECUTE                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Step 1: Identify the Bottleneck**
```bash
# Check task confidence
cat .agent/registry/active/TASK-XXX.yaml | grep -A5 "confidence:"

# 4D dimensions:
# - Factual: Is my understanding correct?
# - Alignment: Does this serve the mission?
# - Current: Does this fit codebase as-is?
# - Onwards: Does this fit where we're heading?
```

**Step 2: Gemini Internal Validation**
```bash
python context-management/tools/ai/analyze.py \
  "Validate approach for [TASK]: [description].
   Check if codebase supports this. Cite specific files." \
  --set [relevant_set]
```

**Step 3: Perplexity External Validation**
```
Use MCP: mcp__perplexity__perplexity_ask
Query: "Best practices for [topic]. Technical validation needed."
```

**Step 4: Ground Truth File Reads**
```bash
# Read the actual files Gemini cited
# Verify claims match reality
```

**Step 5: Update Confidence**
```yaml
# Before:
confidence:
  factual: 85   # "I think this is right"

# After (with evidence):
confidence:
  factual: 95   # "Gemini confirmed, Perplexity validated, files read"
```

**Execution Thresholds:**

| Grade | Threshold | Task Type |
|-------|-----------|-----------|
| A | 85% | Standard tasks (docs, config) |
| A+ | 95% | Multi-file changes, new systems |
| A++ | 99% | High-risk refactors, deletions |

**Example Session:**
```
TASK-117: Enforce state machine (85%, needs 95%)

1. Bottleneck: Factual (85%) - "Is hybrid approach right?"

2. Gemini: "Codebase has claim_task.sh and release_task.sh.
   Adding validation is straightforward."
   → Current: 85% → 95%

3. Perplexity: "Hybrid approach (strict gate + warn mode) is
   best practice for git-based systems."
   → Factual: 85% → 95%

4. File reads: Confirmed tools exist, schema has states

5. Synthesis: min(95, 95, 95, 95) = 95% → MEETS A+ THRESHOLD
```

---

## Decision Matrix

| Question Type | Use | Why |
|---------------|-----|-----|
| "What is X?" | File Search | Quick answer with citations |
| "How does X work?" | File Search → Long Context | Find files, then deep dive |
| "Why does X happen?" | Long Context | Needs cross-file reasoning |
| "Fix bug in X" | File Search → Long Context | Find location, then analyze |
| "Review architecture of X" | Long Context (composed set) | Holistic view needed |
| "What are the patterns for X?" | File Search | Quick discovery |

## Cost Comparison

| Mode | Typical Cost | Best For |
|------|--------------|----------|
| File Search query | ~$0.003 | Repeated questions, discovery |
| Long Context one-shot (50K) | ~$0.02 | Quick analysis |
| Long Context interactive (100K) | ~$0.05/turn | Deep exploration |
| Full architecture review (250K) | ~$0.10/turn | Comprehensive review |

## Store Maintenance

### List stores
```bash
python local_analyze.py --list-stores
```

### Re-index after code changes
```bash
python local_analyze.py --delete-store collider-pipeline
python local_analyze.py --index --set pipeline --store-name collider-pipeline --yes
```

### Add new store for specific area
```bash
python local_analyze.py --index --file "path/to/files/*.py" \
  --store-name my-new-store --yes
```

## Environment Setup

```bash
# Doppler (recommended)
eval $(doppler secrets download --project ai-tools --config dev --no-file --format env-no-quotes)

# Or direct export
export GEMINI_API_KEY='your-key'
```

## Integration with Analysis Sets

The `analysis_sets.yaml` defines file patterns for Long Context analysis.
File Search stores are indexed separately but should mirror these patterns:

| Analysis Set | Corresponding Store |
|--------------|---------------------|
| `brain` | `collider-brain` |
| `pipeline` | `collider-pipeline` |
| `classifiers` | `collider-classifiers` |
| `theory` | `collider-docs` |
| `schema` | `collider-schema` |

Keep them in sync: when you update an analysis set, re-index the corresponding store.

---

## Dataset Optimization Strategy

### RAG vs Long Context: Concrete Thresholds

Based on industry benchmarks (Databricks, PNNL, Perplexity research 2026-01-23):

| Corpus Size | Approach | Rationale |
|-------------|----------|-----------|
| **<16k tokens** | Long Context only | LC performs well, no retrieval overhead |
| **16k-50k tokens** | Long Context OR Hybrid | Sweet spot for LC; hybrid if needle queries |
| **50k-128k tokens** | Hybrid preferred | LC degrades; RAG + focused LC wins |
| **>128k tokens** | RAG required | LC saturation; RAG scales to 2M+ tokens |

**Model-Specific Saturation Points:**

| Model | LC Degrades After |
|-------|-------------------|
| GPT-4-turbo / Claude-3-sonnet | 16k tokens |
| GPT-4-0125-preview | 64k tokens |
| Llama-3.1-405B | 32k tokens |
| Mixtral | 4k tokens |
| Gemini 2.5 Pro | ~200k effective (per ChatGPT research) |

### Hybrid Workflow: RAG → Long Context

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID WORKFLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. RETRIEVAL PHASE (RAG)                                   │
│     ┌─────────────┐      ┌─────────────┐                    │
│     │ Large Corpus│ ───► │ Vector/BM25 │ ───► Top-K chunks  │
│     │  (2M+ tokens)│      │  Retrieval  │      (5-20 docs)  │
│     └─────────────┘      └─────────────┘                    │
│                                                             │
│  2. CONTEXT ASSEMBLY (16k-48k tokens optimal)               │
│     ┌───────────────────────────────────────────┐           │
│     │ [Critical files at START]                 │ ← Sandwich│
│     │ [Retrieved chunks in MIDDLE]              │           │
│     │ [Instructions + critical recap at END]    │           │
│     └───────────────────────────────────────────┘           │
│                                                             │
│  3. REASONING PHASE (Long Context)                          │
│     ┌─────────────┐      ┌─────────────┐                    │
│     │  Assembled  │ ───► │   Gemini    │ ───► Answer +      │
│     │   Context   │      │  Reasoning  │      citations     │
│     └─────────────┘      └─────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Performance (OP-RAG benchmarks):**
- 16k tokens: 44.43 F1
- 48k tokens: 47.25 F1 (peak)
- 117k tokens: 34.26 F1 (degraded)

### When to Use Each Approach

| Approach | Best For | Why |
|----------|----------|-----|
| **RAG (File Search)** | Needle queries, citations, repeated Q&A | Fast, cheap, scales to any corpus |
| **Long Context** | Cross-file reasoning, architecture review | Holistic view, sees relationships |
| **Hybrid** | Debug workflows, feature implementation | RAG finds files, Long Context reasons |

### Dataset Purity Principles

**Purity = Signal / (Signal + Noise)**

A pure dataset has high information density. An impure dataset dilutes relevant information with noise.

```
High Purity (Good):              Low Purity (Bad):
┌────────────────────┐           ┌────────────────────┐
│ ████████████████   │           │ ██                 │
│ ████████████████   │           │    █     █         │
│ ████████████████   │           │      █      █      │
│ Signal             │           │ Signal scattered   │
└────────────────────┘           │ in noise           │
                                 └────────────────────┘
```

### Designing High-Purity Sets

1. **Start focused** - Begin with exact files needed, expand only if insufficient
2. **Exclude archive/** - Historical files pollute context with outdated patterns
3. **Prefer explicit patterns** - `src/core/full_analysis.py` over `src/**/*.py`
4. **Use critical_files** - Mark essential files for positional strategy
5. **Cap at 200k** - Beyond this, lost-in-middle dominates

### Token Budget Decision Tree

```
Is this a needle query? (find specific thing)
  YES → Use RAG (File Search)
  NO  ↓

Do you need cross-file reasoning?
  NO  → Use focused set (<50k tokens)
  YES ↓

How many files need simultaneous view?
  2-5 files   → Compose micro-set (50k-100k)
  5-10 files  → Use composed set (100k-150k)
  10+ files   → Split into phases or use RAG + focused follow-up
```

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| `**/*.py` glob | Includes everything | Use explicit file lists |
| No token limit | Silent degradation | Always set `max_tokens` |
| Archive in context | Outdated patterns confuse | Exclude `archive/**` |
| Duplicate content | Wastes tokens, confuses | Dedupe before analysis |
| Huge composed sets | >200k = lost-in-middle | Break into focused phases |

### Reference

See `.agent/KERNEL.md` → Context Engineering for attention patterns and quality rules.

---

## GraphRAG Integration Status

### What's Implemented

| Component | Status | Location |
|-----------|--------|----------|
| **Gemini File Search (Vector RAG)** | ✓ IMPLEMENTED | `analyze.py:412-625` |
| **GraphRAG Export** | ✓ IMPLEMENTED | `export_graphrag.py` |
| **Collider Graph Component** | ✓ 9/10 aligned | Entity/edge/community |
| **Positional Strategy** | ✓ IMPLEMENTED | `analyze.py:875-934` |

### What's Missing (GraphRAG Gap)

| Component | Status | Action Needed |
|-----------|--------|---------------|
| Query-time Graph Retrieval | ✗ NOT IMPLEMENTED | Build subgraph retrieval API |
| Community Summarization | ⚠️ PARTIAL | Auto-summary per community |
| Hybrid Orchestration | ⚠️ MANUAL | Automate RAG → LC pipeline |

### Collider → GraphRAG Alignment

From `docs/research/GRAPHRAG_LANDSCAPE.md`:

| Pillar | Score | Implementation |
|--------|-------|----------------|
| Entity Extraction | 10/10 | `TreeSitterUniversalEngine` |
| Edge Building | 10/10 | `edge_extractor.py` |
| Community Detection | 10/10 | `graph_analyzer.py` |
| Summarization | 8/10 | `ComponentCard` + AI insights |
| Multi-hop Reasoning | 9/10 | Knots, Markov, execution flow |

**Bottom Line:** Collider is a near-perfect "Graph" component. Missing the "RAG runtime" layer that combines retrieval with reasoning.
