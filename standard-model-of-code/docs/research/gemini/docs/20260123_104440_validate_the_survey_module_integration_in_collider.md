# Research: Validate the survey module integration in Collider. Context:

1. Survey detects vendor/ directory wi...

> **Date:** 2026-01-23 10:44:40
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:744c136aad20c08430ee4e6df658d0bebb996830ad6fdbb6bfacec7b50d8631d`
> **Raw JSON:** `raw/20260123_104440_validate_the_survey_module_integration_in_collider.json`

---

## Query

Validate the survey module integration in Collider. Context:

1. Survey detects vendor/ directory with 3 minified libs (three.min.js, 3d-force-graph.min.js, pako.min.js)
2. Before survey: 4,342 nodes analyzed
3. After survey: 795 nodes analyzed (82% reduction)
4. No suspicious nodes (vendor/minified) found in output
5. BUT: 4 JS files appear missing from analysis: main.js, theory.js, index.js (all in modules/)

QUESTION: How confident should we be that we have ALL the nodes we NEED and ONLY the nodes we NEED?

Evaluate:
- False Positives: Are we excluding real source code?
- False Negatives: Is vendor/minified code still slipping through?
- The 4 missing files - is this a survey bug or tree-sitter parsing issue?

Give a confidence score 0-100% and explain gaps.

---

## Response

Based on the metrics provided and the codebase context, here is the validation assessment of the Survey Module integration.

### Assessment Summary

| Metric | Value | Verdict |
| :--- | :--- | :--- |
| **Noise Reduction** | 82% (4342 → 795) | **EXCELLENT**. Analyzing `three.min.js` and `3d-force-graph` generates thousands of AST nodes that pollute the graph. This reduction is healthy and expected. |
| **False Negatives** | 4 Files (`modules/*.js`) | **CRITICAL FAILURE**. The system is discarding legitimate source code required for the visualization logic. |
| **False Positives** | 0 detected | **PASS**. No vendor blobs appear in the output. |

### Confidence Score: 70%
**Rationale**: The engine successfully solved the "Context Explosion" problem (ignoring massive vendor libs), which was the primary engineering challenge. However, the "Context Myopia" problem (missing source files) makes the current state **unsafe for production** until the exclusion patterns are tuned.

---

### Deep Dive Analysis

#### 1. The 82% Reduction (Validation)
**This is correct behavior.**
*   **Context**: `three.min.js` alone usually generates ~2,000+ AST nodes. `3d-force-graph` generates ~1,500+.
*   **Impact**: Analyzing these nodes distorts the knowledge graph, creating massive "gravity wells" of utility functions that drown out the actual domain logic.
*   **Conclusion**: The drop to 795 nodes represents the *actual* cognitive complexity of your custom logic. This is the desired state.

#### 2. The Missing Files (`modules/`) (Root Cause Analysis)
The files `main.js`, `theory.js`, `index.js` reside in `standard-model-of-code/src/core/viz/assets/modules/`.

**Most Likely Cause: "Broad Pattern Matching"**
The Survey Module likely employs a default exclusion list containing one of the following patterns:
1.  **`**/modules/**`**: Intended to catch `node_modules`, but inadvertently catching your ES6 `modules/` directory.
2.  **`**/assets/**`**: Intended to skip images/css, but your architecture places **logic** (`.js`) inside an `assets` directory.

**Reference**:
In `context-management/config/analysis_sets.yaml`, the `viz_core` set explicitly attempts to include these:
```yaml
viz_core:
  patterns:
    - "standard-model-of-code/src/core/viz/assets/modules/*.js"
```
If the Survey Module applies exclusions *before* inclusion patterns are processed, or if it acts as a hard filter, these files are dropped despite being requested.

#### 3. Is it a Tree-Sitter Issue?
**Unlikely.**
If Tree-sitter failed to parse, it usually returns an empty node list or an error node, but the file would still theoretically be "attempted". Complete absence suggests file-system level exclusion (the file was never handed to the parser).

---

### Remediation Plan

To raise confidence to **100%**, execute the following fixes:

#### 1. Whitelist the Visualization Core
You must explicitly whitelist the `assets/modules` directory to bypass the default "assets" or "modules" ignore rules.

**Action**: Verify `analyze.py` or the Survey Module config handles "Force Include" logic.

#### 2. Refine Exclusion Patterns
Change the exclusion regex from loose matching to strict directory matching.

*   **Bad**: `*modules*` (Matches `viz/assets/modules`)
*   **Good**: `**/node_modules/**`

#### 3. Verification Command
Run the forensic mode on the missing files to verify they are parseable:

```bash
python context-management/tools/ai/analyze.py \
  --mode forensic \
  --file "standard-model-of-code/src/core/viz/assets/modules/main.js"
```

If this returns data, the Survey Module's file walker is the culprit. If this returns nothing, the parser is the culprit.

### Final Verdict
The system is **over-aggressive**. It has successfully stopped eating "junk food" (vendor libs) but is currently starving itself of "nutrition" (source modules). **Tune the ignore patterns.**

---

## Citations

_No citations provided_
