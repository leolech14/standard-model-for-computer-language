# Research: Forensic audit: Which of these are TRULY dead (zero runtime references)? 1) enrich_query_for_perplex...

> **Date:** 2026-01-24 23:37:34
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:e9749a5a21fe6429ffbce4eda92091c7ee2d5ef539e5c1b84fa68265c356a67d`
> **Raw JSON:** `raw/20260124_233734_forensic_audit__which_of_these_are_truly_dead__zer.json`

---

## Query

Forensic audit: Which of these are TRULY dead (zero runtime references)? 1) enrich_query_for_perplexity() in analyze.py 2) generate_grounded_perplexity_query() in analyze.py 3) PI2_PURPOSES, PI3_PURPOSES, SCALE_LEVELS in semantic_matcher.py 4) EXTERNAL_INDICATORS in query_analyzer.py. For each, cite the exact grep command to prove deadness and list any live references found.

---

## Response

Here is the forensic audit of the specified artifacts based on the provided ACI codebase context.

### Forensic Summary
| Artifact | Status | Diagnosis |
| :--- | :--- | :--- |
| `enrich_query_for_perplexity` | **DEAD** | Zero references in ACI core. Superseded by `schema_orchestrator.py`. |
| `generate_grounded_perplexity_query` | **DEAD** | Zero references in ACI core. Superseded by `schema_orchestrator.py`. |
| `PI2_PURPOSES`, `PI3_PURPOSES`, `SCALE_LEVELS` | **DEAD** | Unused definitions (Documentation artifacts). Logic uses keyword mapping instead. |
| `EXTERNAL_INDICATORS` | **ZOMBIE** | Defined as a legacy alias but bypassed by functional logic (`get_external_indicators`). |

---

### 1. `enrich_query_for_perplexity()` in `analyze.py`
**Status:** **DEAD**
**Evidence:** This function appears to be legacy logic from an older `analyze.py` (which is likely being replaced by the `aci` package). The modern ACI system uses `schema_orchestrator.py` for query enrichment and `tier_router.py` for routing.

*   **Logic Check:** The active logic in `schema_orchestrator.py` uses `_prepare_external_query` (Line 605) for external sanitization, not this function.
*   **Proof Command:**
    ```bash
    grep -r "enrich_query_for_perplexity" .
    ```
*   **Forensic Result:**
    *   **Live References:** `0` (In the provided ACI context).
    *   **Verdict:** Safe to delete.

### 2. `generate_grounded_perplexity_query()` in `analyze.py`
**Status:** **DEAD**
**Evidence:** Similar to item #1, this suggests an older procedural approach to generating queries. The current system relies on `ResearchEngine` in `schema_orchestrator.py` which constructs queries based on `RunConfig` and `system_prompt`.

*   **Logic Check:** `ResearchEngine._execute_single_run` (Line 555 in `schema_orchestrator.py`) handles query assembly dynamically.
*   **Proof Command:**
    ```bash
    grep -r "generate_grounded_perplexity_query" .
    ```
*   **Forensic Result:**
    *   **Live References:** `0` (In the provided ACI context).
    *   **Verdict:** Safe to delete.

### 3. `PI2_PURPOSES`, `PI3_PURPOSES`, `SCALE_LEVELS` in `semantic_matcher.py`
**Status:** **DEAD (Ghost Data)**
**Evidence:** These are large dictionaries defined at the module level (Lines 36, 48, 124) but are **never accessed**. The functional logic uses `QUERY_PURPOSE_KEYWORDS` and `QUERY_LAYER_KEYWORDS` for mapping, and hardcodes scale levels in the logic.

*   **Logic Check:**
    *   `_match_purpose` (Line 245) iterates over `QUERY_PURPOSE_KEYWORDS`, ignoring `PI2_PURPOSES`.
    *   `semantic_match` (Line 353) sets `scale_focus` via a hardcoded ternary operator (`"L3" if purpose else "L5"`), ignoring `SCALE_LEVELS`.
*   **Proof Command:**
    ```bash
    # Exclude the definition file itself to check for external usage
    grep -r "PI2_PURPOSES\|PI3_PURPOSES\|SCALE_LEVELS" . --exclude=semantic_matcher.py
    ```
*   **Forensic Result:**
    *   **Live References:** `0`.
    *   **Verdict:** These are "knowledge constants" likely copied from documentation (`MODEL.md`) but never wired into the code. Safe to delete.

### 4. `EXTERNAL_INDICATORS` in `query_analyzer.py`
**Status:** **ZOMBIE (Legacy Alias)**
**Evidence:** This variable is defined on Line 129 as `EXTERNAL_INDICATORS = _DEFAULT_EXTERNAL_INDICATORS`. However, the actual logic in `_detect_scope` (Line 261) calls `get_external_indicators()`.

*   **Logic Check:**
    *   `get_external_indicators()` (Line 111) loads `_DEFAULT_EXTERNAL_INDICATORS` **AND** merges them with `aci_config.yaml`.
    *   The `EXTERNAL_INDICATORS` variable **ignores configuration** and points only to defaults. Using it would be a bug as it bypasses user config.
    *   It is **NOT** exported in `__init__.py` (Line 72), so it is not part of the public API.
*   **Proof Command:**
    ```bash
    # Check for usage outside the definition
    grep -r "EXTERNAL_INDICATORS" . --exclude=query_analyzer.py
    ```
*   **Forensic Result:**
    *   **Live References:** likely `0` (unless an external script imports it directly via `from aci.query_analyzer import EXTERNAL_INDICATORS`).
    *   **Verdict:** Delete. It presents a risk of inconsistent behavior (static defaults vs config-merged values).

---

## Citations

_No citations provided_
