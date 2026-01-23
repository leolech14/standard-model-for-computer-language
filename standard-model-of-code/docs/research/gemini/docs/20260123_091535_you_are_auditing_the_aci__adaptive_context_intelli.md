# Research: You are auditing the ACI (Adaptive Context Intelligence) module - the 'curriculum compiler' that pre...

> **Date:** 2026-01-23 09:15:35
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:c29a307ad3c3b76f44308a56df320cbeb59327196125ef53ed902ce620ff4101`
> **Raw JSON:** `raw/20260123_091535_you_are_auditing_the_aci__adaptive_context_intelli.json`

---

## Query

You are auditing the ACI (Adaptive Context Intelligence) module - the 'curriculum compiler' that prepares context for AI queries.

NOW YOU HAVE THE ACTUAL SOURCE CODE. Review it carefully.

AUDIT QUESTIONS:
1. Is aci_config.yaml actually wired up to the code? Or are values hardcoded?
2. How well does ACI integrate with its siblings (analyze.py, HSL, Perplexity)?
3. What specific code changes are needed to make ACI a true orchestrator?
4. What documentation is missing?

Be SPECIFIC. Cite file:line numbers. Show code snippets that need to change.

---

## Response

This is a forensic audit of the **Adaptive Context Intelligence (ACI)** subsystem based on the provided source code.

### Executive Summary
The ACI module is currently operating in a **"Hardcoded Heuristic"** state rather than a fully configuration-driven state. While `aci_config.yaml` defines a sophisticated control plane, the actual Python logic ignores this file entirely, relying instead on hardcoded dictionaries and constants. Furthermore, the integration with sibling tools (specifically Perplexity) is disconnected, resulting in a "dead end" for the user when external research is required.

---

### 1. Configuration Wiring Audit: The "Ghost Config"
**Verdict: CRITICAL FAILURE.** `aci_config.yaml` is not wired to the codebase.

The configuration file `context-management/config/aci_config.yaml` defines granular controls for thresholds, budgets, and keywords. However, the Python modules ignore this file and use hardcoded constants that duplicate (or drift from) the YAML values.

**Evidence:**
*   **Token Budgets:**
    *   **Config:** `aci_config.yaml` [Lines 37-41] defines `guru: 50000`.
    *   **Code:** `context_optimizer.py` [Lines 24-29] hardcodes `TOKEN_BUDGETS = { "guru": 50_000, ... }`.
    *   **Issue:** Changing the YAML does nothing. The Python file must be edited.
*   **Intent Keywords:**
    *   **Config:** `aci_config.yaml` [Lines 47-66] defines keywords for `architecture`, `debug`, etc.
    *   **Code:** `query_analyzer.py` [Lines 66-99] hardcodes `INTENT_KEYWORDS = { QueryIntent.ARCHITECTURE: [...], ... }`.
    *   **Issue:** The analyzer does not load the YAML.
*   **Missing Loader:**
    *   `analyze.py` loads `analysis_sets.yaml` [Line 132] and `prompts.yaml` [Line 150], but it **never loads** `aci_config.yaml`.

---

### 2. Integration Audit: Sibling Systems
**Verdict: PARTIAL / DISCONNECTED.** ACI identifies the need for sibling tools but fails to invoke them programmatically.

#### A. Perplexity (External Research)
**Status: Dead End.**
When ACI selects the `PERPLEXITY` tier, the system simply prints instructions and exits, rather than calling the available tool.
*   **Evidence:** `analyze.py` [Lines 1178-1183]:
    ```python
    if decision.tier == Tier.PERPLEXITY:
        print("[PERPLEXITY] External research tier selected.", file=sys.stderr)
        print("Use the Perplexity MCP server for this query:", file=sys.stderr)
        # ...
        sys.exit(0) # <--- Execution stops here
    ```
*   **Missed Opportunity:** `perplexity_research.py` exists and is importable, but is unused by the main flow.

#### B. HSL (Holographic-Socratic Layer)
**Status: Unaware.**
*   **Evidence:** `tier_router.py` logic is purely based on `QueryProfile` (Intent/Complexity/Scope). It does not check `hsl_daemon.py` status or the `semantic_models.yaml` state.
*   **Consequence:** ACI routes `VALIDATE` queries [Line 85, `tier_router.py`] to `Tier.LONG_CONTEXT` (Gemini), completely bypassing the specialized Socratic Validator logic built into `analyze.py --verify`.

#### C. `analyze.py` (The Host)
**Status: Superficial.**
*   ACI is treated as a "routing suggester" rather than a controller. `analyze.py` [Lines 1162-1200] contains the logic for handling the decision, rather than ACI returning an executable strategy.

---

### 3. Required Code Changes for True Orchestration

To make ACI a "true orchestrator," we must bridge the gap between configuration and execution.

#### A. Implement Config Loader
**File:** `context-management/tools/ai/aci/config_loader.py` (New File)
**File:** `context-management/tools/ai/aci/__init__.py`

We need a singleton to load the YAML and override the hardcoded defaults.

```python
# PROPOSED CHANGE for __init__.py or config_loader.py
import yaml
from pathlib import Path

# Load config once
CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config/aci_config.yaml"
_ACI_CONFIG = {}
if CONFIG_PATH.exists():
    with open(CONFIG_PATH) as f:
        _ACI_CONFIG = yaml.safe_load(f)

def get_config():
    return _ACI_CONFIG
```

#### B. Refactor `query_analyzer.py` to use Config
**Target:** `context-management/tools/ai/aci/query_analyzer.py`

```python
# CURRENT (Hardcoded) [Lines 66-68]
INTENT_KEYWORDS = {
    QueryIntent.ARCHITECTURE: [ ... ]
}

# REQUIRED CHANGE
from .config_loader import get_config
config = get_config()

# Merge hardcoded defaults with YAML overrides
INTENT_KEYWORDS = {
    QueryIntent.ARCHITECTURE: config.get('intent_keywords', {}).get('architecture', []) + [
        "how does", "architecture", ... # fallback defaults
    ],
    # ...
}
```

#### C. Activate Perplexity Integration
**Target:** `context-management/tools/ai/analyze.py`

The script needs to import the research tool and execute it when recommended.

```python
# REQUIRED CHANGE around Line 1178 in analyze.py
if decision.tier == Tier.PERPLEXITY:
    try:
        from perplexity_research import research
        print("[ACI] Auto-executing Perplexity Research...", file=sys.stderr)
        result = research(args.prompt, model="sonar-reasoning")
        print(result['content'])
        sys.exit(0)
    except ImportError:
        print("Perplexity tool not found in path.")
```

#### D. Wire Feedback Loop
**Target:** `context-management/tools/ai/analyze.py`

Although `log_aci_query` is imported [Line 113], it is never called.

```python
# REQUIRED CHANGE at end of main execution in analyze.py
if args.aci:
    # Calculate stats
    duration = int((time.time() - start_time) * 1000)
    log_aci_query(
        profile=profile, # Need to expose this from analyze_and_route
        decision=decision,
        tokens_input=token_usage.prompt,   # hypothetical
        tokens_output=token_usage.response, # hypothetical
        success=True,
        duration_ms=duration
    )
```

---

### 4. Missing Documentation

1.  **ACI Tuning Guide:** `AI_USER_GUIDE.md` mentions the tool but does not explain how to modify `aci_config.yaml` to change behavior (e.g., "How to add a new 'Intent' keyword").
2.  **Architecture Diagram:** There is no visual representation of how `analyze.py` hands off control to `aci` and receives a `OptimizedContext`.
3.  **Feedback Loop Analysis:** There is no documentation on how to read or act upon `.agent/intelligence/aci_feedback.yaml`. A script `aci_stats.py` is likely needed to visualize this data.

### Summary of Recommendations

1.  **Immediate Fix:** Delete the hardcoded dictionaries in `query_analyzer.py` and `context_optimizer.py` and replace them with a YAML loader referencing `aci_config.yaml`.
2.  **Integration:** Modify `analyze.py` to actually call `perplexity_research.py` instead of printing a suggestion.
3.  **Refinement:** Route `VALIDATE` intent queries to the HSL/Socratic validator (`--verify`) logic instead of the generic Long Context LLM.

---

## Citations

_No citations provided_
