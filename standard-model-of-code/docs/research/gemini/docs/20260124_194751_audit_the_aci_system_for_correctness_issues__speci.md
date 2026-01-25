# Research: Audit the ACI system for correctness issues. Specifically:
1. The HYBRID tier is defined in tier_rou...

> **Date:** 2026-01-24 19:47:51
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:c4d29be1b7172ce2697bb05949e271d87177263284da6c599c5dfcdd460ddb8b`
> **Raw JSON:** `raw/20260124_194751_audit_the_aci_system_for_correctness_issues__speci.json`

---

## Query

Audit the ACI system for correctness issues. Specifically:
1. The HYBRID tier is defined in tier_router.py but analyze.py has no execution path for it - what happens when HYBRID is returned?
2. The semantic_matcher.py can emit sets like 'gateways', 'infrastructure', 'services' that don't exist in analysis_sets.yaml - trace this code path
3. The agent_context trigger_keywords in aci_config.yaml include generic words like 'confidence' and 'run' - show false positive scenarios
4. The Perplexity integration in analyze.py - does it inject internal context into the user prompt (which Perplexity docs say pollutes search)?

For each issue, cite file:line numbers and propose a fix.

---

## Response

Here is the correctness audit for the Adaptive Context Intelligence (ACI) system.

## Executive Summary
The ACI system demonstrates a strong architectural vision (Graph -> Tier -> Context), but suffers from "implementation drift" where specific configurations and mappings have disconnected from the actual execution logic. The most critical issue is the `semantic_matcher.py` referencing non-existent analysis sets, which will cause the "Curriculum Compiler" to return empty contexts for semantically complex queries.

---

### 1. HYBRID Tier: Missing Execution Logic
**Issue**: The `Tier.HYBRID` enum is defined and routed to, but `analyze.py` treats it as a fall-through case, effectively downgrading it to `LONG_CONTEXT` without the external research component that "Hybrid" implies.

**Evidence**:
*   **Definition**: `context-management/tools/ai/aci/tier_router.py:108` defines `HYBRID = "hybrid"`.
*   **Routing**: `tier_router.py:209-216` assigns `Tier.HYBRID` for mixed internal/external scope queries.
*   **Execution Gap**: `context-management/tools/ai/analyze.py:1618` (approximate).
    The execution flow handles `INSTANT` (Line 1391), `PERPLEXITY` (Line 1420), and `FLASH_DEEP` (Line 1500). There is no `if decision.tier == Tier.HYBRID:` block. The code falls through to the catch-all block ("TIER 1 & 2") at Line 1618.

**Impact**: Queries needing external validation (e.g., "Compare our architecture vs 2026 industry standards") will only search the local codebase, failing to retrieve the "industry standard" part.

**Proposed Fix**:
Modify `context-management/tools/ai/analyze.py` to intercept `Tier.HYBRID`. A simple implementation runs Perplexity first, then injects that result into the standard context context.

```python
# In analyze.py, before the generic TIER 1 & 2 block

if decision.tier == Tier.HYBRID:
    print("[HYBRID] Executing external research phase...", file=sys.stderr)
    # 1. Run Perplexity
    try:
        from perplexity_research import research
        # Use Gemini to extract the external part of the query?
        # For now, send full query
        research_res = research(args.prompt, model="sonar-pro")
        external_context = f"\n=== EXTERNAL RESEARCH ===\n{research_res['content']}\n"
    except Exception as e:
        print(f"[HYBRID] Research failed ({e}), proceeding with internal only.", file=sys.stderr)
        external_context = ""
    
    # 2. Proceed to Internal Analysis (fall through but append context)
    # We need a mechanism to inject this into the context builder later
    # This requires refactoring the context build logic to accept string injections
```

---

### 2. Semantic Matcher: "Hallucinated" Analysis Sets
**Issue**: The semantic matcher maps semantic intents to analysis sets that do not exist in the configuration. The `resolve_set` function in `analyze.py` will return empty patterns for these, resulting in zero context loaded.

**Evidence**:
*   **Source**: `context-management/tools/ai/aci/semantic_matcher.py`
    *   Line 354: `"Retrieve": ["pipeline", "data_access"]` -> `data_access` does not exist.
    *   Line 355: `"Persist": ["infrastructure", "data_access"]` -> `infrastructure` does not exist.
    *   Line 359: `"Coordinate": ["services", "orchestration"]` -> `services`, `orchestration` do not exist.
    *   Line 360: `"Transport": ["gateways", "infrastructure"]` -> `gateways` does not exist.
    *   Line 361: `"Present": ["presentation", "viz_core"]` -> `presentation` does not exist.
    *   Lines 368-372: `controllers`, `api`, `domain`, `entities`, `validators` do not exist.
*   **Config**: `context-management/config/analysis_sets.yaml` contains `pipeline`, `viz_core`, `classifiers`, `repo_tool`, etc., but matches very few of the semantic suggestions.

**Impact**: High-semantic queries (e.g., "How do we coordinate services?") will be routed to sets like `['services', 'orchestration']`. Since these sets are undefined, the AI will receive **empty context** or fallback to defaults, rendering the "Curriculum Compiler" useless.

**Proposed Fix**:
Remap `semantic_matcher.py` to use existing sets defined in `analysis_sets.yaml`.

```python
# context-management/tools/ai/aci/semantic_matcher.py

def _purpose_to_sets(purpose: str) -> List[str]:
    mapping = {
        "Retrieve": ["pipeline", "repo_tool"],       # 'repo_tool' contains engine logic
        "Persist": ["repo_tool", "schemas"],         # 'schemas' defines data structures
        "Transform": ["pipeline", "classifiers"],    # Existing sets
        "Compute": ["pipeline", "repo_theory"],
        "Validate": ["classifiers", "constraints"],  # 'constraints' exists
        "Coordinate": ["pipeline", "agent_tasks"],   # 'agent_tasks' for coordination
        "Transport": ["pipeline"],                   # Fallback
        "Present": ["viz_core"],                     # Exists
    }
    return mapping.get(purpose, ["pipeline"])

# Similarly update _layer_to_sets to use 'repo_theory', 'repo_tool', 'classifiers'
```

---

### 3. Agent Context: High False-Positive Rate
**Issue**: The trigger keywords for injecting the Agent/Kernel context are too generic. Common English words trigger a context injection of ~30k-50k tokens (`agent_kernel` + `agent_tasks`), wasting budget and distracting the model.

**Evidence**:
*   **Config**: `context-management/config/aci_config.yaml:80`
    *   `- "confidence"` (Used in "I have low confidence in this code")
    *   `- "run"` (Used in "Run the script", "Runtime error")
    *   `- "task"` (Used in "The task failed")
*   **Logic**: `context-management/tools/ai/aci/query_analyzer.py:344`
    ```python
    for indicator in agent_indicators:
        if indicator in query_lower:
            return True
    ```
    This is a simple substring check. "runtime error" contains "run". "verify task execution" contains "task".

**Impact**:
1.  **Cost**: Unnecessary loading of `agent_tasks` (50k tokens) for simple debugging queries.
2.  **Confusion**: The model sees Sprint planning docs when asked to debug a Python script.

**Proposed Fix**:
Refine `aci_config.yaml` to use more specific compound terms, or switch `query_analyzer.py` to use token-based matching rather than substring matching.

**Immediate Config Fix (`aci_config.yaml`):**
```yaml
  trigger_keywords:
    - "agent task"
    - "current sprint"
    - "kernel boot"
    - "bare protocol"
    - "update registry"
    - "confidence score" # Specific to the meta-metric
    - "claim task"
    # Remove "run", "confidence", "task" (too generic)
```

---

### 4. Perplexity Integration: Context Pollution
**Issue**: The logic in `analyze.py` injects raw local code excerpts into the prompt sent to Perplexity. Search engine LLMs (Sonar) are optimized for web search queries; injecting 2000 chars of local Python code often confuses the retrieval mechanism, causing it to search for the *specific code strings* on the web rather than the *concept*.

**Evidence**:
*   **File**: `context-management/tools/ai/analyze.py`
*   **Function**: `enrich_query_for_perplexity` (Line 538)
*   **Logic**:
    ```python
    # Line 587
    file_excerpts.append(f"[{fname}]: {excerpt}...")
    # Line 600
    enriched = f"""CONTEXT FROM LOCAL CODEBASE... \n{...}\n RESEARCH QUESTION: {query}"""
    ```
*   **Usage**: In `tier_router.py`, fallback from specific grounding often hits `enrich_query_for_perplexity`.

**Impact**: A query like "best practice for Python imports" becomes "best practice for Python imports... [file: pipeline.py] import os...". Perplexity might try to find that specific file online or halluncinate that the provided code is the "best practice" it should reference.

**Proposed Fix**:
In `analyze.py`, restrict `enrich_query_for_perplexity` to only inject **Definitions** (from Glossary/Theory), not **Implementation** (Code excerpts).

```python
# context-management/tools/ai/analyze.py

def enrich_query_for_perplexity(query: str, decision, analysis_sets: dict) -> str:
    # ... (Keep glossary loading) ...

    # REMOVE lines 570-594 (Critical file excerpt loading)
    
    # Replace with strict conceptual framing
    return f"""
    Context: I am working on a project called "Standard Model of Code" 
    (a meta-language for software architecture).
    
    Local Definitions relevant to query:
    {chr(10).join(relevant_terms[:5])}
    
    Research Question:
    {query}
    """
```

---

## Citations

_No citations provided_
