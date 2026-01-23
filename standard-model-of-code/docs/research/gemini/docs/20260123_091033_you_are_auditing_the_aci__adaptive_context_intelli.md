# Research: You are auditing the ACI (Adaptive Context Intelligence) module - the 'curriculum compiler' that pre...

> **Date:** 2026-01-23 09:10:33
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:d2f4bb9ca875d8ae33a5a70a0c5b24f8d9e30c9ce0b14fea54422f732e9af71b`
> **Raw JSON:** `raw/20260123_091033_you_are_auditing_the_aci__adaptive_context_intelli.json`

---

## Query

You are auditing the ACI (Adaptive Context Intelligence) module - the 'curriculum compiler' that prepares context for AI queries.

CURRENT STATE:
- ACI has 4 files: query_analyzer.py, tier_router.py, context_optimizer.py, feedback_loop.py
- Only analyze.py imports ACI
- aci_config.yaml exists but values are HARDCODED in code (not read from config)
- No dedicated documentation (only docstrings)
- Not connected to: HSL (validation), Perplexity (research), BARE (truths system)

QUESTION:
1. What documentation should ACI have? (filename, sections, purpose)
2. How should aci_config.yaml be wired up?
3. How should ACI connect to sibling subsystems (HSL, Perplexity, BARE)?
4. What's the minimal viable integration to make ACI a true orchestrator?

Be specific. Give file paths and code patterns.

---

## Response

This is a critical architectural audit. The ACI module is currently operating as a "stub" rather than the intelligence engine described in `aci_config.yaml`. To elevate it from a hardcoded heuristic script to a true **Adaptive Context Intelligence**, we need to externalize configuration and formalize the interfaces.

Here is the remediation plan.

### 1. Documentation Architecture

**Filename:** `context-management/docs/specs/ACI_ARCHITECTURE.md`

This document defines the "Brain's Routing Protocol." It must be distinct from `TOOL.md` (which describes the CLI) and `THEORY.md` (which describes the data).

**Required Sections:**
1.  **Routing Logic:** How `query_analyzer.py` calculates `complexity_score` and maps it to Tiers defined in `aci_config.yaml`.
2.  **Context Injection Strategy:** How `context_optimizer.py` selects between `minimal`, `standard`, and `full` agent contexts based on the keywords in `aci_config.yaml`.
3.  **The Feedback Loop:** How `feedback_loop.py` writes to `.agent/intelligence/aci_feedback.yaml` to tune thresholds over time.
4.  **Interface Contract:** The input/output signature expected by `analyze.py`.

### 2. Wiring `aci_config.yaml` (The Fix)

Currently, `tier_router.py` likely has `if complexity > 5: return 'long_context'`. This must change to read from the YAML.

**Step A: Create a Config Loader**
Add a utility method in `context-management/tools/ai/aci/utils.py` (or inside `query_analyzer.py` if keeping file count low):

```python
import yaml
from pathlib import Path

# Path to the config provided in context
CONFIG_PATH = Path("context-management/config/aci_config.yaml")

def load_aci_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"ACI Config missing at {CONFIG_PATH}")
    
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

# Global singleton to prevent re-reading every query
ACI_CONFIG = load_aci_config()
```

**Step B: Refactor `tier_router.py`**
Stop using magic numbers. Use the loaded config.

```python
from .utils import ACI_CONFIG

def route_tier(query_metrics):
    # 1. Check Overrides (Fastest)
    query_text = query_metrics['text'].lower()
    for tier, patterns in ACI_CONFIG['routing_overrides'].items():
        if any(p.replace('*', '') in query_text for p in patterns):
            return tier

    # 2. Check Complexity Thresholds (Logic derived from config)
    # Note: You'll need to map config descriptions to logic, or add explicit 
    # score thresholds to the yaml in a future update. 
    # For now, map intent to tiers defined in config:
    
    if query_metrics['is_external_scope']:
        return "perplexity" # As defined in config
        
    if query_metrics['requires_reasoning']:
        return "long_context"
        
    return "rag" # Default fallthrough
```

### 3. Sibling Subsystem Connection Strategy

ACI must act as the **Dispatcher**, identifying the intent and delegating to the specialized subsystem via `analyze.py`.

**A. HSL (Holographic-Socratic Layer)**
*   **Trigger:** `query_analyzer.py` detects keywords from `aci_config.yaml` -> `intent_keywords.architecture` or explicit `--verify` flags.
*   **Action:** ACI returns a `routing_instruction` object.
*   **Implementation:**
    ```python
    # In query_analyzer.py
    if any(k in query for k in ACI_CONFIG['intent_keywords']['architecture']):
        return {
            "tier": "socratic",
            "context_set": "architecture_review",
            "validation_mode": True 
        }
    ```

**B. Perplexity (External Research)**
*   **Trigger:** `query_analyzer.py` checks `ACI_CONFIG['external_indicators']` (e.g., "latest", "2026", "best practice").
*   **Action:** ACI routes to `perplexity` tier.
*   **Implementation:**
    ```python
    # In tier_router.py
    external_triggers = ACI_CONFIG['external_indicators']
    if any(t in query for t in external_triggers):
        return "perplexity" 
    ```

**C. BARE (Background Auto-Refinement Engine)**
*   **Trigger:** Keywords like "truth", "drift", "confidence" (from `ACI_CONFIG['agent_context']['trigger_keywords']`).
*   **Action:** `context_optimizer.py` injects the `agent_intelligence` Analysis Set.
*   **Implementation:**
    ```python
    # In context_optimizer.py
    def get_context_mix(query):
        triggers = ACI_CONFIG['agent_context']['trigger_keywords']
        if any(t in query for t in triggers):
            # Dynamic injection of BARE truths
            return ["agent_intelligence", "agent_kernel"] 
        return ["agent_kernel"] # Default
    ```

### 4. Minimal Viable Integration (The Orchestrator Pattern)

To make ACI the true orchestrator without rewriting `analyze.py` entirely, implement this **Facade Pattern** in `analyze.py`:

**Current (Likely State):**
```python
# analyze.py
import tier_router
tier = tier_router.get_tier(query)
if tier == 'rag': ...
```

**Proposed MVI (The Orchestrator):**

Modify `context-management/tools/ai/analyze.py` to use a unified entry point.

1.  **Create `ACIResult` DTO:**
    ```python
    @dataclass
    class ACIResult:
        tier: str              # 'rag', 'long_context', 'perplexity', 'socratic'
        analysis_sets: List[str] # ['pipeline', 'agent_intelligence']
        token_budget: int      # From aci_config.yaml token_budgets
        system_prompt_modifier: str # e.g., "You are a FORENSIC ANALYST..."
    ```

2.  **Update `analyze.py` Main Loop:**
    ```python
    from context_management.tools.ai.aci import orchestrator

    def analyze(query, ...):
        # 1. ACI decides the strategy
        plan: ACIResult = orchestrator.compile_plan(query)

        print(f"🧠 ACI Plan: Tier={plan.tier}, Budget={plan.token_budget}")

        # 2. Execute based on plan
        if plan.tier == 'perplexity':
            return run_perplexity(query)
        elif plan.tier == 'socratic':
            return run_socratic_validation(plan.analysis_sets)
        else:
            # Standard Gemini/RAG path
            context = build_context(plan.analysis_sets, plan.token_budget)
            return run_llm(context, query)
    ```

**Specific Action Items for You:**
1.  Create `context-management/docs/specs/ACI_ARCHITECTURE.md`.
2.  Add config loading logic to `context-management/tools/ai/aci/__init__.py` or a util file to expose `ACI_CONFIG`.
3.  Update `query_analyzer.py` to read `intent_keywords` from that config object.
4.  Modify `analyze.py` to accept an `ACIResult` object rather than raw strings.

---

## Citations

_No citations provided_
