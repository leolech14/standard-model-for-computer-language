# Research: TERMINOLOGY AUDIT: We just replaced 'Domain' with 'Concordance' across the project glossary and key ...

> **Date:** 2026-01-27 02:11:32
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:1cfc6a9a881dfecb47a2b5e083140fc579e6ab4776e999e0b774c8d7764ce8e4`
> **Raw JSON:** `raw/20260127_021132_terminology_audit__we_just_replaced__domain__with.json`

---

## Query

TERMINOLOGY AUDIT: We just replaced 'Domain' with 'Concordance' across the project glossary and key docs.

Please verify:
1. Is GLOSSARY.md now consistent? Does it define CONCORDANCE properly and remove DOMAIN as a core term?
2. Is CONCORDANCES.md the canonical definition file?
3. Are CODOME.md, CONTEXTOME.md, PROJECTOME.md, TOPOLOGY_MAP.md all updated to reference CONCORDANCES instead of DOMAINS?
4. Is the algebra in CODESPACE_ALGEBRA.md updated to use C for Concordances instead of D for Domains?
5. Are there any INCONSISTENCIES where 'Domain' is still used to mean our semantic grouping concept (not the DDD architectural layer)?

Focus on the key terminology files in context-management/docs/. Report any remaining inconsistencies.

---

## Response

Based on the provided codebase context, here is the audit of the **Domain $\to$ Concordance** terminology refactor.

### Executive Summary
The refactor is **~85% complete**. The core theoretical documents (`GLOSSARY`, `CODESPACE_ALGEBRA`) and the canonical definition (`CONCORDANCES`) are correct. However, significant "ghosts" of the old terminology remain in `CONTEXTOME.md` and the system configuration files, creating a dissonance between the theory and the definitions.

---

### 1. GLOSSARY.md Consistency
**Status: ✅ CONSISTENT**

*   **Definition:** Correctly defines **CONCORDANCE** as "A semantic grouping with measured purpose alignment... Score ∈ [0,1]."
*   **Algebra:** Uses the correct notation: `CONCORDANCES (Cover)`, `⋃ Cᵢ = P`.
*   **"Domain" Usage:** Effectively removed as a core term for the "vertical slice" concept. It now appears primarily in the **16-Level Scale** (L11 Domain), which is the correct usage (referring to DDD/Architectural domains, not the Concordance measurement unit).
*   **Navigation:** The ASCII map references `CONCORDANCES`.

### 2. Canonical Definition
**Status: ✅ CONSISTENT**

*   **File:** `context-management/docs/CONCORDANCES.md` is present and correctly structured.
*   **Content:** It explicitly defines the etymology (replacing Domain) and the mathematical definition (`C = {C₁, C₂, ..., Cₘ}`).
*   **Deprecation:** `DOMAINS_DEPRECATED.md` exists and correctly redirects to `CONCORDANCES.md`.

### 3. Cross-References (CODOME, CONTEXTOME, PROJECTOME)
**Status: ⚠️ MIXED / INCOMPLETE**

*   **`PROJECTOME.md`**: ✅ **Updated.** Uses "Concordance" in headers, tables, and algebra sections.
*   **`CODOME.md`**: ✅ **Updated.** The "See Also" section references `CONCORDANCES.md`.
*   **`CONTEXTOME.md`**: ❌ **INCONSISTENT.** While the headers were updated, the body text reverts to "Domain" in several critical explanatory sections (see Section 5 below).
*   **`TOPOLOGY_MAP.md`**: ❓ **UNKNOWN.** This file was not provided in the context context, so it cannot be verified.

### 4. Algebra (CODESPACE_ALGEBRA.md)
**Status: ✅ CONSISTENT**

*   **Section 7 (Concordance Algebra):** Correctly uses $C$ for Concordances.
*   **Notation:** Updates $\mu: P \to \mathcal{P}(C)$ (Membership function maps to Power set of Concordances).
*   **Metric:** Explicitly defines `concordance(C)` score.

---

### 5. Detected Inconsistencies (Action Items)

The following areas require immediate remediation to complete the refactor:

#### A. The Textual Reversion in `CONTEXTOME.md`
In `context-management/docs/CONTEXTOME.md`, the header was changed, but the explanatory paragraphs were skipped.

*   **Line ~36:** "A **Domain** is defined by the relationship between its code and its context."
    *   *Fix:* Change "Domain" to "Concordance".
*   **Line ~38 (Section Header):** "### **Domain** Symmetry"
    *   *Fix:* Change to "Concordance Symmetry".
*   **Line ~40:** "For any **domain** D:"
    *   *Fix:* Change to "For any concordance C:", and update variables `D.code` $\to$ `C.code`.
*   **Line ~45:** "**Domain** Health = ..."
    *   *Fix:* Change to "Concordance Health".

#### B. The Configuration Lag (`semantic_models.yaml`)
While not a doc file, `context-management/config/semantic_models.yaml` drives the HSL validation reports. It still uses `DOMAIN` as a primary key.

*   **Lines 8, 48, 64:** `# DOMAIN: PIPELINE`, `# DOMAIN: THEORY`, `# DOMAIN: ARCHITECTURE`.
*   **Impact:** If the `analyze.py` tool reads these keys to generate reports, the output reports (`socratic_audit_*.md`) will likely still use the term "Domain", confusing the user.
*   *Recommendation:* Update the comment headers to `# CONCORDANCE: ...` or `# SECTOR: ...` to align with the new glossary.

#### C. The Documentation Map (`documentation_map.yaml`)
*   **Line 7:** `# DOCUMENTATION → CONCEPTS`
*   **Line 55:** The comments here generally look okay, but check if any logic parses "domains" from this file.

### Recommendation
1.  **Edit `CONTEXTOME.md`** immediately to replace the ~5 remaining instances of "Domain".
2.  **Verify `TOPOLOGY_MAP.md`** manually as it was not in the audit context.
3.  **Refactor `semantic_models.yaml`** comments to ensure generated reports align with `GLOSSARY.md`.

---

## Citations

_No citations provided_
