# Gemini Long Context Blueprint

**Source:** User-provided power-user guidance
**Date:** 2026-01-23
**Relevance:** ACI Tier System, FLASH_DEEP implementation

## Executive Summary

The biggest win is NOT "stuff more code into the prompt." The biggest win is:

1. Make the repo snapshot a **reusable prefix** (cache it)
2. Compile **durable artifacts** (module map / truth registry / dependency graph)
3. Route most interactive questions to **small context** using those artifacts + targeted retrieval
4. Escalate to **long-context only** for the few tasks that truly require global scanning

## Model Context Reality Check

| Model | Input Tokens | Status |
|-------|--------------|--------|
| Gemini 2.0 Flash | 1,048,576 (~1M) | **DEPRECATED** - shuts down March 31, 2026 |
| Gemini 3 Pro Preview | 1,048,576 (~1M) | Active |
| Gemini 3 Flash Preview | 1,048,576 (~1M) | Active |
| Gemini 2.5 Pro/Flash | 1,048,576 (~1M) | Stable |

**Critical:** Don't hardcode `MAX_FLASH_DEEP_TOKENS = 2_000_000`. Use:
```python
model_info = client.models.get(model=...)
limit = model_info.input_token_limit

# Exact sizing before sending
token_count = client.models.count_tokens(model=..., contents=...)
```

## The #1 Unlock: Context Caching

### Implicit Caching (Automatic)
- Enabled by default on many models
- Cache hits depend on repeating a large shared prefix quickly
- **Best practice:** Put large, common content at the beginning; varying question at the end

### Explicit Caching (Manual, Guaranteed Savings)
Create cache once with repo snapshot, then subsequent queries reference it.

```python
from google import genai
from google.genai import types

client = genai.Client()
model = "models/gemini-3-flash-preview"

# 1) Create cache once per repo snapshot (commit SHA)
cache = client.caches.create(
    model=model,
    config=types.CreateCachedContentConfig(
        display_name=f"repo:{commit_sha}",
        system_instruction="You are a senior codebase analyst. Cite file paths as evidence.",
        contents=[repo_snapshot_text],
        ttl="3600s",  # tune TTL (default is 1h)
    )
)

# 2) Reuse cache for many queries
resp = client.models.generate_content(
    model=model,
    contents="Question: explain the pipeline stages and their contracts.",
    config=types.GenerateContentConfig(cached_content=cache.name),
)
```

**Impact:** "2M/1M context mode" stops being "expensive per question." It becomes "expensive per snapshot," cheap thereafter.

## Tier Policy (When to Use What)

### Use RAG / Targeted Context When:
- Question is about a specific function/file/error
- You already know likely file paths (stack trace, symbol)
- You can answer with <50k-200k tokens of context

### Use LONG_CONTEXT (~1M) When:
- Cross-module reasoning in a subsystem cluster
- Reconciling docs + implementation across many files
- "Architecture review" constrained to selected sets

### Use FLASH_DEEP (Compiler Mode) When:
- Generating artifacts (module map, truth registry)
- Repo-wide pattern mining (duplication, layering violations)
- Cross-repo comparison
- Spec drift detection at scale

**Then:** Most human Q&A goes back to RAG/LONG_CONTEXT using the compiled artifacts.

## RepoPack v1 Format (Recommended Order)

Deterministic layout maximizes implicit caching hit rate because prefix stays stable:

1. `REPO_ID` - commit SHA, branch, timestamp
2. `FILE_TREE` - depth-limited
3. `SUBSYSTEMS` - ACI sets + semantic_models domains
4. `PUBLIC_API_INDEX` - exports, CLI entrypoints, HTTP routes
5. `COLLIDER_FACTS` - graphs, invariants, metrics
6. `DOCS/SPECS` - only authoritative ones
7. `RAW_CODE` - only for "hot files" or files referenced by facts
8. `QUESTION` - last

## Artifacts to Compile (High-Leverage)

Produce once per commit (or per release tag):

### 1. Repo Manifest (Registry CSV/SQLite)
- path, language, size, hash, ownership tags, "subsystem", "layer"
- exports, key symbols, dependencies (from Collider)

### 2. Module Map
- subsystem boundaries, public APIs, "entrypoints", lifecycle

### 3. Dependency Graph
- import graph, cycles, layer violations, "hot edges"

### 4. Truth Registry
- validated outputs of Collider + test outcomes + invariants
- versioned by commit, with provenance

### 5. Spec Alignment Map
- which docs/specs correspond to which modules/files

## Evidence Protocol (Reduce Hallucinations)

Make the model produce file-path evidence for every key claim:

```
"For each claim, cite at least one FILE: block path from the context."
"If you cannot find evidence in provided files, say 'NOT FOUND IN CONTEXT'."
```

For machine-checkable output, require JSON (Gemini models support structured outputs).

## 2-Pass Mode Inside Flash Deep

Long context is great, but models can still miss details:

- **Pass A (Map):** Build an index of what's in the snapshot
- **Pass B (Answer):** Answer the user query using that index

If using explicit caching, Pass A becomes especially cheap because you're only sending small prompts after the snapshot is cached.

## FLASH_DEEP Implementation Fixes

### Fix 1: Dynamic Limits
```python
model_info = client.models.get(model=model)
limit = model_info.input_token_limit
token_count = client.models.count_tokens(model=model, contents=prompt)
```

### Fix 2: Caching as Default
```python
# 1. Compute snapshot hash (git SHA + workspace dirty hash)
# 2. Look for existing cache in registry
# 3. If missing/expired -> create cache
# 4. Answer query using cached_content=cache.name
```

### Fix 3: Evidence Protocol
Require citations and support JSON structured output.

### Fix 4: RepoPack Format
Use deterministic ordering to maximize cache hit rate.

## 3 Critical Upgrades (This Week)

1. **Add explicit caching to FLASH_DEEP** (cache repo snapshot keyed by commit SHA)
2. **Stop hardcoding context limits** (use `models.get` + `count_tokens`)
3. **Turn FLASH_DEEP into "compile artifacts"** and have RAG/LONG_CONTEXT consume those artifacts by default

## Truth Registry Requirements

Every cached "truth" must be tied to:
- commit SHA / build ID
- evidence pointers (files + hashes or Collider facts)
- validation status (tests passed, collider checks OK)
- freshness (invalidated when files change)

This prevents "stale AI facts" from quietly poisoning your system.

## Migration Path

Current anchor on `gemini-2.0-flash` needs upgrade path (shuts down March 31, 2026).

Options:
- Gemini 3 Pro Preview (strong reasoning + long context)
- Gemini 3 Flash Preview (speed/scale + long context)
- Gemini 2.5 Pro / 2.5 Flash (stable, 1M context)

Architecturally the caching + compiler approach stays identical across all.
