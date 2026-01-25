# Research: Explain how the Perplexity tier currently works in analyze.py. Specifically:
1. What happens when AC...

> **Date:** 2026-01-23 14:24:33
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:cddaf2fef52286670abe49df1a0350946f8aad1087e9c5d5f911b35ae1be7598`
> **Raw JSON:** `raw/20260123_142433_explain_how_the_perplexity_tier_currently_works_in.json`

---

## Query

Explain how the Perplexity tier currently works in analyze.py. Specifically:
1. What happens when ACI routes to PERPLEXITY tier?
2. Are the selected context sets used in any way?
3. What is the current flow from query to Perplexity API call?
4. Where would context injection logically fit?

Be concise - bullet points preferred.

---

## Response

Based on the provided ACI (Adaptive Context Intelligence) modules and configuration, here is the analysis of the **PERPLEXITY** tier.

*Note: The actual execution script `analyze.py` is not in the provided context, so the execution steps are inferred from the routing logic and configuration definitions.*

### 1. What happens when ACI routes to PERPLEXITY tier?
*   **Detection:** The `query_analyzer.py` detects **External Scope** via keywords (e.g., "best practice", "latest", "vs", "2026") defined in `aci_config.yaml`.
*   **Routing:** `tier_router.py` returns a `RoutingDecision` object with:
    *   `tier`: **Tier.PERPLEXITY**
    *   `fallback_tier`: **Tier.LONG_CONTEXT** (if the API fails).
    *   `reasoning`: e.g., "External scope - defaulting to Perplexity".
*   **Configuration:** The system prepares to use the `sonar-pro` model with a temperature of `0.1` (defined in `aci_config.yaml`).

### 2. Are the selected context sets used in any way?
*   **In Router:** Yes, `tier_router.py` *still calculates* `primary_sets` (usually defaults to `['theory']` or broad architectural sets if semantic matching occurs).
*   **In Execution:** **No (Likely).** Standard Perplexity API implementations rely on the model's internal knowledge and live web search. The local context sets (files from your repo) are typically **not** sent to Perplexity because:
    1.  The tier is designed for *external* knowledge.
    2.  Perplexity is a search engine, not a RAG over your codebase.
    3.  Sending thousands of lines of local code to a web search API is inefficient and often privacy-violating.

### 3. Current flow from query to Perplexity API call
1.  **Input:** User enters a query (e.g., "What is the latest React state of the art?").
2.  **Analysis:** `analyze_query()` flags it as `QueryScope.EXTERNAL`.
3.  **Routing:** `route_query()` outputs `Tier.PERPLEXITY`.
4.  **Execution (in analyze.py):**
    *   The script sees `decision.tier == Tier.PERPLEXITY`.
    *   It bypasses the local context loading/token counting logic.
    *   It retrieves the API key and config (model `sonar-pro`).
    *   It sends the **raw user query** directly to the Perplexity API.

### 4. Where would context injection logically fit?
If you want Perplexity to understand your codebase context (e.g., "Compare *my architecture* to industry standards"), injection fits here:

*   **Location:** In `analyze.py`, immediately **after** receiving the `RoutingDecision` and **before** the API call.
*   **Strategy:**
    *   Take the `primary_sets` identified by the router.
    *   Generate a **High-Level Summary** of those sets (not the raw code).
    *   **Prefix the Query:** Construct a prompt like:
        > "Context: I am working on a Python project using DDD and ACI. [Insert Summary].
        > Question: [User Query]"
*   **Benefit:** This creates "Grounded Research" where external search results are filtered by relevance to your specific architectural context.

---

## Citations

_No citations provided_
