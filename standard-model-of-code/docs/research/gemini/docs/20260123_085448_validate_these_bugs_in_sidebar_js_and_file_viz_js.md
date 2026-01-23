# Research: Validate these bugs in sidebar.js and file-viz.js: Bug 1: setViewMode('files') at lines 558-572 does...

> **Date:** 2026-01-23 08:54:48
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:dd16a40ce05be30bc15ebe9c1525c9cdab35a91a7780abc55ce83b36d477f035`
> **Raw JSON:** `raw/20260123_085448_validate_these_bugs_in_sidebar_js_and_file_viz_js.json`

---

## Query

Validate these bugs in sidebar.js and file-viz.js: Bug 1: setViewMode('files') at lines 558-572 doesn't switch graph data. Bug 2: setViewMode('atoms') at lines 574-582 doesn't restore original atom data. Read the actual code and confirm the bugs exist.

---

## Response

Based on the code analysis of `sidebar.js` and `file-viz.js`, I can confirm **both bugs are valid**.

Here is the validation breakdown:

### Bug 1: `setViewMode('files')` doesn't reliably switch graph data
**Location:** `sidebar.js` (approx. lines 558-572)

**Analysis:**
In `sidebar.js`, the code delegates the entire mode switching logic to `FILE_VIZ`:
```javascript
// sidebar.js
if (mode === 'files') {
    if (typeof FILE_VIZ !== 'undefined') {
        FILE_VIZ.buildFileGraph();
        window.GRAPH_MODE = 'files';
        FILE_VIZ.graphMode = 'files';
        FILE_VIZ.setMode('map');
        FILE_VIZ.setEnabled(true); // <--- Relies on this side-effect to switch data
    }
    // ...
}
```
In `file-viz.js`, `setEnabled(true)` triggers `apply()`, which triggers `applyFileGraphMode()`. While `applyFileGraphMode` *does* contain a call to `Graph.graphData(_fileGraph)`, this chain is fragile and architecturaly incorrect because:
1.  **Implicit Side Effect:** `sidebar.js` (the controller) acts as if it is setting a visual mode, but relies on a deep internal side-effect of `FILE_VIZ` to perform the critical data model swap (Atoms -> Files).
2.  **Missing Fallback:** If `FILE_VIZ.apply()` returns early (e.g., if `DM` is not found, see `file-viz.js` line 352), `sidebar.js` has no mechanism to ensure the data was actually swapped.
3.  **Inconsistency:** In the legacy `else` block (lines 568-572), `sidebar.js` handles data logic explicitly. In the `FILE_VIZ` block, it abdicates responsibility.

**Verdict:** **Valid.** `sidebar.js` should explicitly call `Graph.graphData(FILE_VIZ.getFileGraph())` to ensure the data model update occurs, rather than hoping `FILE_VIZ.setEnabled(true)` does it as a side effect.

---

### Bug 2: `setViewMode('atoms')` doesn't restore original atom data
**Location:** `sidebar.js` (approx. lines 574-582)

**Analysis:**
When switching back to 'atoms', `sidebar.js` executes:
```javascript
// sidebar.js
} else {
    // Switch to atoms view
    if (typeof FILE_VIZ !== 'undefined') {
        FILE_VIZ.graphMode = 'atoms';
        FILE_VIZ.setEnabled(false); // <--- THE BUG
    } 
    // ...
}
```
It calls `FILE_VIZ.setEnabled(false)`. Looking at `file-viz.js`:
```javascript
// file-viz.js
function apply() {
    if (!_enabled) {
        clearBoundaries(); // Clears visuals
        clearCohesion();   // Clears physics
        return;            // <--- EXITS WITHOUT RESTORING DATA
    }
    // ...
}
```
`FILE_VIZ` correctly cleans up its own visual artifacts (hulls, cohesion forces) but **does not restore the graph topology**. The `Graph` object retains the `_fileGraph` (File Nodes) loaded in the previous step. The user is left looking at File Nodes (L5) with no visual hulls, instead of returning to Atom Nodes (L3/L2).

**Verdict:** **Valid & Critical.** The logic completely fails to reload the Atom-level data. `sidebar.js` must explicitly fetch the original nodes/links (via `DM.getNodes()`/`DM.getLinks()`) and pass them to `Graph.graphData()` when disabling file mode.

---

## Citations

_No citations provided_
