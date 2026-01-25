# Research: How do I use this tool (analyze.py) effectively? Specifically:

1. How do I select specific files fo...

> **Date:** 2026-01-24 18:06:32
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:6e15eee9e499a9216a46b5e151c37f143f050d02a336d16222863b5b9303a872`
> **Raw JSON:** `raw/20260124_180632_how_do_i_use_this_tool__analyze_py__effectively__s.json`

---

## Query

How do I use this tool (analyze.py) effectively? Specifically:

1. How do I select specific files for context using --file?
2. What model options are available and how do I use Gemini 2.5 Pro with 1M context?
3. What does the --tier option do? What's the difference between long_context and deep?
4. How should I size context for a query about comparing two directories for duplication?
5. What's the optimal context size for a 'duplication audit' query?

Give me practical examples.

---

## Response

Based on the ACI (Adaptive Context Intelligence) codebase provided, here is the practical guide to using `analyze.py` effectively.

### 1. Selecting specific files for context (`--file`)

The `analyze.py` tool uses the **Context Optimizer** (`context_optimizer.py`) to manage what gets sent to the LLM. While the tool often selects files automatically using **Refinery** (`refinery.py`), you can manually force files into the context.

**How it works:**
The system typically "sandwiches" or "front-loads" critical files based on the `positioning` logic in `context_optimizer.py`.

**Usage Examples:**

*   **Single File:**
    ```bash
    python analyze.py "Why is the pipeline failing?" --file src/core/pipeline.py
    ```
*   **Multiple Files:**
    ```bash
    python analyze.py "Check for circular imports" --file src/core/pipeline.py src/utils/helpers.py
    ```
*   **Wildcards (Shell Expansion):**
    ```bash
    python analyze.py "Explain the authentication flow" --file src/auth/*.py
    ```

**Tip:** When you provide `--file`, the **Tier Router** likely treats this as a focused intent. If you provide many files, ensure you are using at least the `long_context` tier so the `refinery.py` logic doesn't aggressively truncate them to fit a small budget.

---

### 2. Model Options & Using Gemini (1M Context)

According to `tier_router.py` and `aci_config.yaml`, models are generally mapped to **Tiers** rather than selected manually, though overrides exist.

**Available Models (Internal mappings):**
*   **Gemini 2.0 Flash (`gemini-2.0-flash-thinking-exp`):** Used by `flash_deep` tier. Supports up to **2M tokens**.
*   **Gemini 3 Pro (`gemini-3-pro`):** Used by `long_context` tier. Supports **1M tokens**.
*   **Gemini 2.0 Flash 001:** Used by `rag` tier (fast, lower latency).

**How to use 1M+ Context:**
You do not need to specify the model version explicitly. Instead, you trigger the tier that utilizes that model.

*   **For ~1M Context (Reasoning Focus):** Use `long_context`.
    ```bash
    python analyze.py "Refactor the entire auth module" --tier long_context
    ```
*   **For ~2M Context (Massive Analysis):** Use `flash_deep`.
    ```bash
    python analyze.py "Analyze the entire codebase for architectural drift" --tier flash_deep
    ```

---

### 3. Understanding `--tier`: `long_context` vs `deep`

The **Tier Router** (`tier_router.py`) logic defines distinct use cases for these tiers.

#### **`long_context` (Tier 2)**
*   **Backend:** Defaults to `gemini-3-pro` or `gemini-2.0-flash-001`.
*   **Budget:** ~200,000 to 1,000,000 tokens.
*   **Use Case:** Multi-file reasoning, complex debugging, architecture review of specific modules.
*   **Behavior:** It uses `refinery.py` to select relevant *sets* of files (e.g., "pipeline" set, "theory" set).
*   **Command:**
    ```bash
    python analyze.py "How do the semantic matcher and tier router interact?" --tier long_context
    ```

#### **`deep` / `flash_deep` (Tier 4)**
*   **Backend:** Defaults to `gemini-2.0-flash-thinking-exp`.
*   **Budget:** Up to **2,000,000 tokens**.
*   **Use Case:** "Holistic" questions, cross-repo comparisons, or queries containing words like "comprehensive," "everything," or "all files."
*   **Behavior:** It bypasses standard selection and loads the **RepoPack** (`repopack.py`)—a massive, deterministic snapshot of your entire file tree and critical code. It caches this snapshot using `cache_registry.py`.
*   **Command:**
    ```bash
    python analyze.py "Do we have duplication between the legacy tools and the new aci module?" --tier deep
    ```

---

### 4. Sizing context for comparing two directories

Comparing directories requires the LLM to "see" all files simultaneously to detect patterns. RAG (searching) will fail here because it only retrieves snippets.

**Strategy:**
1.  **Do not use RAG:** It will miss the duplication.
2.  **Force `flash_deep`:** This ensures the context window is large enough (2M tokens) to hold both directories fully.
3.  **Targeting:** If `analyze.py` supports directory flags, use them. Otherwise, rely on `flash_deep`'s behavior of loading the full `RepoPack`.

**Example:**
```bash
python analyze.py "Compare src/v1/utils and src/v2/common for duplicated logic" --tier deep
```

**Why this works:**
The `tier_router.py` logic checks for keywords. If you don't use `--tier deep`, you can trigger it naturally by using "trigger words" defined in `FLASH_DEEP_TRIGGERS`:
> *"comprehensive", "holistic", "all files", "entire codebase"*

```bash
# Implicitly triggers deep tier due to "comprehensive" keyword
python analyze.py "Perform a comprehensive duplication check between v1 and v2 utils"
```

---

### 5. Optimal Context Size for 'Duplication Audit'

For a duplication audit, you are fighting against "Lost-in-the-Middle" effects.

*   **Recommended Config:** `tier: flash_deep`
*   **Token Estimate:**
    *   **Small Repos (<50 files):** ~50k - 100k tokens.
    *   **Medium Repos:** ~200k - 500k tokens.
    *   **Context Strategy:** The `repopack.py` tool formats the context into a single block. This is optimal for duplication audits because the model can attend to the entire tree structure in one pass.

**Config Warning:**
Your `aci_config.yaml` has a default hard cap:
```yaml
token_budgets:
  hard_cap: 200000     # Absolute maximum
```
**However**, `tier_router.py` contains logic that overrides this for `FLASH_DEEP`:
```python
elif tier == Tier.FLASH_DEEP:
    # FLASH_DEEP: Load EVERYTHING - 2M context capacity
```
So, for a duplication audit, **always use `flash_deep`**. If you use `long_context`, you might hit the 200k safety cap defined in `context_optimizer.py`, which would truncate files and make the duplication audit impossible.

**Summary Checklist for Duplication Audit:**
1.  **Tier:** `deep` (or `flash_deep`)
2.  **Keywords:** Use "comprehensive" or "all files" in your query.
3.  **Expectation:** It will take longer (uses context caching), but it ensures the model sees 100% of the code.

---

## Citations

_No citations provided_
