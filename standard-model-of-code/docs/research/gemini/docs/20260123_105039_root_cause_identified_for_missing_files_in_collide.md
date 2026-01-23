# Research: ROOT CAUSE IDENTIFIED for missing files in Collider survey:

The 4 missing JS files (main.js, theory...

> **Date:** 2026-01-23 10:50:39
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:b39d84ada0441ce464445d3a334290aefb6ff467524aadcf0da11a3b2760ead8`
> **Raw JSON:** `raw/20260123_105039_root_cause_identified_for_missing_files_in_collide.json`

---

## Query

ROOT CAUSE IDENTIFIED for missing files in Collider survey:

The 4 missing JS files (main.js, theory.js, index.js) all use IIFE pattern:
```javascript
(function() {
    'use strict';
    
    function myFunction() { ... }  // INDENTED
    const THEORY = { ... };        // INDENTED
})();
```

The tree_sitter_engine.py fallback parser (lines 869-872) skips indented code:
```python
# JS/TS: keep to top-level declarations (no indentation)
if language in {'javascript', 'typescript'}:
    if line \!= line.lstrip():
        continue
```

This means:
1. Tree-sitter primary parser is failing (we see 'Failed to load locals query for javascript' errors)
2. Fallback regex parser skips ALL indented code
3. IIFE modules have NO top-level declarations - everything is inside the wrapper

QUESTION: Is this a survey bug or a pre-existing tree-sitter issue? How should we fix it?

---

## Response

Based on your analysis and the provided context, here is the diagnosis and the fix.

### 1. Is this a survey bug or a pre-existing tree-sitter issue?

**It is a logic bug in the Survey/Fallback system.**

While the root trigger is a **Tree-sitter configuration issue** (missing query files causing `Failed to load locals query`), the **Survey system's fallback logic is flawed**.

*   **The Flaw:** The fallback regex parser enforces Pythonic whitespace rules (ignoring indented code) on JavaScript/TypeScript.
*   **The Reality:** In JavaScript, indentation does not strictly imply "scope privacy" or "local-only" status the way it does in Python. Patterns like IIFE (Immediately Invoked Function Expressions), AMD (Define), and UMD wraps force **all** valid code to be indented.
*   **Consequence:** By skipping indented lines, the fallback parser treats these files as empty/comment-only, resulting in 0 nodes detected and the file being dropped from the survey.

### 2. How to fix it

You need to modify `src/core/tree_sitter_engine.py` to relax the indentation constraint for JavaScript and TypeScript.

Since the fallback parser relies on Regex to find `function Name`, `class Name`, or `const Name`, it is generally safe to scan indented lines. While this might pick up some internal helper functions (increasing noise), it is infinitely better than incorrectly classifying the file as empty (data loss).

#### The Fix

Locate the `_analyze_file_fallback` or `_extract_regex_particles` method (around line 869 as you noted) in `src/core/tree_sitter_engine.py` and modify the loop:

**Current Code (The Bug):**
```python
# ... inside the line iteration loop ...
line_stripped = line.strip()
if not line_stripped or line_stripped.startswith(comment_prefix):
    continue

# JS/TS: keep to top-level declarations (no indentation)
if language in {'javascript', 'typescript'}:
    if line != line.lstrip():
        continue  # <--- THIS IS THE CULPRIT
```

**Recommended Fix:**
Comment out or remove the indentation check for JS/TS.

```python
# ... inside the line iteration loop ...
line_stripped = line.strip()
if not line_stripped or line_stripped.startswith(comment_prefix):
    continue

# FIX: Allow indented code for JS/TS to support IIFE, AMD, and closure patterns.
# Only Python strictly requires top-level declarations for major structural nodes.
if language == 'python':
    if line != line.lstrip():
        continue
```

### Why this is safe

1.  **Regex Robustness:** The regex patterns used for fallback (e.g., `function\s+(\w+)`) usually require a named identifier. Anonymous functions used in callbacks (which cause the most noise) usually won't match standard named definitions.
2.  **Edge Extractor Compatibility:** Your `src/core/edge_extractor.py` (lines 142-154) explicitly contains logic in `JSModuleResolver` to handle IIFE patterns (`const X = (function() {...})()`).
    *   Currently, `tree_sitter_engine.py` filters the code out *before* `edge_extractor.py` ever sees it.
    *   By allowing indented lines, you allow `edge_extractor.py` to successfully detect the `window.X = ...` or `return {...}` exports that happen inside those IIFEs.

### Long Term Fix (Tree-sitter)
To fix the "Failed to load locals query" error preventing the primary parser from working:
1.  Ensure `tree-sitter-javascript` is installed (`pip install tree-sitter-javascript`).
2.  Ensure the `.scm` query files (specifically `locals.scm`) are located where the `tree_sitter` Python binding expects them, or that the `TreeSitterUniversalEngine` class is properly pointing to the vendor directory containing these queries.

---

## Citations

_No citations provided_
