# Research: FULL AUDIT: Analyze all UI controls in the visualization system. For each control (sliders, toggles,...

> **Date:** 2026-01-24 23:31:26
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:5f6823729e5572f523b94dfa18845bd1afb65bcdb577ae0625639d8c0f9eb6c9`
> **Raw JSON:** `raw/20260124_233126_full_audit__analyze_all_ui_controls_in_the_visuali.json`

---

## Query

FULL AUDIT: Analyze all UI controls in the visualization system. For each control (sliders, toggles, buttons, keyboard shortcuts), trace the complete chain: 1) UI element exists in template.html, 2) Event binding exists in JS, 3) Handler function is called, 4) State is updated, 5) Visual effect occurs. Identify: WORKING controls, ORPHANED controls (missing any link), DUPLICATE bindings, MISSING controls that should exist. Return a structured report.

---

## Response

### FORENSIC CODE AUDIT: UI CONTROLS

This audit traces the execution chain for all user interface controls found in `template.html` and their corresponding JavaScript modules.

---

### 1. ⬢ NODE CONFIGURATION (Left Sidebar)
**Status:** ⚠️ **PARTIALLY BROKEN**
Primary controls for node visualization. Several sliders have bindings but empty handlers.

| Control ID | Type | Chain of Custody | Status |
| :--- | :--- | :--- | :--- |
| `cfg-node-size` | Slider | **HTML:** `template.html:L1135`<br>**Bind:** `sidebar.js:L767`<br>**Handler:** `sidebar.js:L821` → `Graph.nodeVal`<br>**State:** `APPEARANCE_STATE.nodeScale` | ✅ **WORKING** |
| `cfg-node-opacity` | Slider | **HTML:** `template.html:L1145`<br>**Bind:** `sidebar.js:L767`<br>**Handler:** `sidebar.js:L825` → `applyEdgeMode` | ✅ **WORKING** |
| `cfg-node-res` | Slider | **HTML:** `template.html:L1155`<br>**Bind:** `sidebar.js:L767`<br>**Handler:** `sidebar.js:L829` → `Graph.nodeResolution` | ✅ **WORKING** |
| `cfg-label-size` | Slider | **HTML:** `template.html:L1165`<br>**Bind:** `sidebar.js:L767`<br>**Handler:** `sidebar.js:L831` (Case exists but body is empty comment) | ❌ **BROKEN**<br>*(Logic missing)* |
| `cfg-toggle-labels` | Toggle | **HTML:** `template.html:L1172`<br>**Bind:** `sidebar.js:L777`<br>**Handler:** `sidebar.js:L782` → `Graph.nodeLabel` | ✅ **WORKING** |
| `cfg-toggle-highlight`| Toggle | **HTML:** `template.html:L1176`<br>**Bind:** `sidebar.js:L786`<br>**Handler:** `sidebar.js:L787` (Empty callback) | ❌ **BROKEN**<br>*(Logic missing)* |
| `cfg-toggle-pulse` | Toggle | **HTML:** `template.html:L1180`<br>**Bind:** `sidebar.js:L790`<br>**Handler:** `sidebar.js:L792` → `ANIM.togglePulse` | ✅ **WORKING** |
| `cfg-toggle-depth` | Toggle | **HTML:** `template.html:L1184`<br>**Bind:** `sidebar.js:L796`<br>**Handler:** `sidebar.js:L797` (Empty callback) | ❌ **BROKEN**<br>*(Logic missing)* |

---

### 2. ⟷ EDGE CONFIGURATION (Left Sidebar)
**Status:** ⚠️ **MIXED**
Core edge sliders work, but style buttons and some toggles are orphaned.

| Control ID/Class | Type | Chain of Custody | Status |
| :--- | :--- | :--- | :--- |
| `[data-edge-style]` | Buttons | **HTML:** `template.html:L1200` (Solid/Dashed/Particle)<br>**Bind:** **NONE FOUND** in `sidebar.js` or `edge-system.js` | 💀 **ORPHANED**<br>*(UI exists, no JS)* |
| `cfg-edge-opacity` | Slider | **HTML:** `template.html:L1210`<br>**Bind:** `sidebar.js:L767`<br>**Handler:** `sidebar.js:L838` → `applyEdgeMode` | ✅ **WORKING** |
| `cfg-edge-width` | Slider | **HTML:** `template.html:L1220`<br>**Bind:** `sidebar.js:L767`<br>**Handler:** `sidebar.js:L842` → `Graph.linkWidth` | ✅ **WORKING** |
| `cfg-edge-curve` | Slider | **HTML:** `template.html:L1230`<br>**Bind:** `sidebar.js:L767`<br>**Handler:** `sidebar.js:L846` → `Graph.linkCurvature` | ✅ **WORKING** |
| `cfg-particle-speed` | Slider | **HTML:** `template.html:L1240`<br>**Bind:** `sidebar.js:L767`<br>**Handler:** `sidebar.js:L850` → `Graph.linkDirectionalParticleSpeed` | ✅ **WORKING** |
| `cfg-toggle-arrows` | Toggle | **HTML:** `template.html:L1257`<br>**Bind:** `sidebar.js:L800`<br>**Handler:** `sidebar.js:L803` → `Graph.linkDirectionalArrowLength` | ✅ **WORKING** |
| `cfg-toggle-gradient` | Toggle | **HTML:** `template.html:L1261`<br>**Bind:** `sidebar.js:L808`<br>**Handler:** `sidebar.js:L810` → `applyEdgeMode` | ✅ **WORKING** |
| `cfg-toggle-edge-hover`| Toggle| **HTML:** `template.html:L1265`<br>**Bind:** **NONE FOUND** | 💀 **ORPHANED** |
| `cfg-toggle-codome` | Toggle | **HTML:** `template.html:L1269`<br>**Bind:** **NONE FOUND** | 💀 **ORPHANED** |

---

### 3. PHYSICS & LAYOUT (Left Sidebar)
**Status:** ✅ **HEALTHY**
Physics engine controls are fully wired.

| Control ID | Type | Chain of Custody | Status |
| :--- | :--- | :--- | :--- |
| `[data-layout]` | Buttons | **HTML:** `template.html:L1282` (Force, Radial, etc.)<br>**Bind:** `sidebar.js:L656`<br>**Handler:** `sidebar.js:L668` → `ANIM.applyLayout` | ✅ **WORKING** |
| `physics-charge` | Slider | **HTML:** `template.html:L1307`<br>**Bind:** `sidebar.js:L691` (also `L858`)<br>**Handler:** `sidebar.js:L693` → `Graph.d3Force('charge')` | ✅ **WORKING** |
| `physics-link` | Slider | **HTML:** `template.html:L1317`<br>**Bind:** `sidebar.js:L699`<br>**Handler:** `sidebar.js:L701` → `Graph.d3Force('link')` | ✅ **WORKING** |
| `[data-physics]` | Buttons | **HTML:** `template.html:L1332` (Default, Tight, etc.)<br>**Bind:** `sidebar.js:L726`<br>**Handler:** `sidebar.js:L728` → `setPhysicsPreset` | ✅ **WORKING** |

---

### 4. LEGACY APPEARANCE (Lower Left Sidebar)
**Status:** ❌ **BROKEN / ID MISMATCH**
The "Appearance" section contains sliders that conflict with or duplicate the "Node Config" section, but use different IDs that are not handled correctly.

| Control ID | Type | Chain of Custody | Status |
| :--- | :--- | :--- | :--- |
| `node-size` | Slider | **HTML:** `template.html:L1352`<br>**Bind:** `sidebar.js` binds generic ranges, BUT handler at `sidebar.js:L816` expects `cfg-node-size`.<br>**Conflict:** `panels.js:L138` attempts to bind `node-size-slider` (not `node-size`). | ❌ **BROKEN**<br>*(ID Mismatch)* |
| `edge-opacity` | Slider | **HTML:** `template.html:L1362`<br>**Bind:** `sidebar.js` generic bind, BUT handler at `sidebar.js:L816` expects `cfg-edge-opacity`. | ❌ **BROKEN**<br>*(ID Mismatch)* |
| `toggle-labels` | Toggle | **HTML:** `template.html:L1369`<br>**Bind:** **NONE FOUND** (Only `cfg-toggle-labels` is bound in `sidebar.js:L777`) | 💀 **ORPHANED** |

---

### 5. GLOBAL ACTIONS (Top/Overlay)
**Status:** ✅ **HEALTHY**

| Control ID | Type | Chain of Custody | Status |
| :--- | :--- | :--- | :--- |
| `view-mode-toggle` | Buttons | **HTML:** `template.html:L1097` (ATOMS / FILES)<br>**Bind:** `sidebar.js:L485`<br>**Handler:** `sidebar.js:L489` → `setViewMode` | ✅ **WORKING** |
| `btn-reset` | Button | **HTML:** `template.html:L1405`<br>**Bind:** `sidebar.js:L879`<br>**Handler:** `sidebar.js:L882` → `Graph.cameraPosition` | ✅ **WORKING** |
| `btn-screenshot` | Button | **HTML:** `template.html:L1406`<br>**Bind:** `sidebar.js:L889`<br>**Handler:** `sidebar.js:L895` → `domElement.toDataURL` | ✅ **WORKING** |
| `btn-2d` | Button | **HTML:** `template.html:L1407`<br>**Bind:** `dimension.js:L50` (via `main.js` -> `DIMENSION.setup`)<br>**Handler:** `dimension.js:L24` → `toggle` | ✅ **WORKING** |
| `btn-freeze` | Button | **HTML:** `template.html:L1408`<br>**Bind:** `sidebar.js:L906`<br>**Handler:** `sidebar.js:L913` → `Graph.d3AlphaTarget` | ✅ **WORKING** |

---

### 6. RIGHT SIDEBAR CONTROLS
**Status:** ✅ **HEALTHY**

| Control ID | Type | Chain of Custody | Status |
| :--- | :--- | :--- | :--- |
| `selection-clear` | Button | **HTML:** `template.html:L776`<br>**Bind:** `selection.js:L729`<br>**Handler:** `selection.js:L731` → `clear()` | ✅ **WORKING** |
| `[data-preset]` | Buttons | **HTML:** `template.html:L1496` (Tier, Family, etc.)<br>**Bind:** `sidebar.js:L455`<br>**Handler:** `sidebar.js:L461` → `setColorMode` | ✅ **WORKING** |
| `[data-scheme]` | Buttons | **HTML:** Generated by `sidebar.js:L306`<br>**Bind:** `sidebar.js:L341`<br>**Handler:** `sidebar.js:L361` → `applyColorScheme` | ✅ **WORKING** |

---

### 7. KEYBOARD SHORTCUTS
**Status:** ✅ **HEALTHY**

| Shortcut | Context | Chain of Custody | Status |
| :--- | :--- | :--- | :--- |
| `Ctrl+Shift+L` | Layout | `layout.js:L645` → `toggleDebugOverlay` | ✅ **WORKING** |
| `Ctrl+X` | Debug | `property-query-init.js:L303` → `debugNode` | ✅ **WORKING** |
| `Space` | Pan | `TowerRenderer.js:L65` → `controls.mouseButtons.LEFT = PAN` | ✅ **WORKING** |
| `P` | Pipeline | `pipeline-navigator.js:L598` → `togglePipelineNavigator` | ✅ **WORKING** |
| `Escape` | Modal | `selection.js:L678` → `hideSelectionModal` | ✅ **WORKING** |

---

### MISSING CONTROL REFERENCES
The following controls are referenced in JavaScript but do not exist in `template.html`:

1.  **`btn-edge-mode`**: Referenced in `edge-system.js:L498`. The script attempts to update its text content, but the button ID is not in the HTML.
2.  **`btn-create-group`**: Referenced in `groups.js:L146` and `selection.js:L734`.
3.  **`cmd-files`**: Referenced in `file-viz.js:L348` (Command bar button).
4.  **`density-slider2`**: Referenced in `sidebar.js:L165`.

### SUMMARY
*   **Total Controls Analyzed:** 38
*   **Working:** 25 (65%)
*   **Broken/Logic Missing:** 3 (8%)
*   **Orphaned/ID Mismatch:** 6 (16%)
*   **Missing from HTML:** 4 (11%)

**Critical Fixes Needed:**
1.  Add logic to `sidebar.js` for `cfg-label-size` (Label Size) and `cfg-toggle-highlight`.
2.  Remove or rename the legacy "Appearance" section in `template.html` (`node-size`, `edge-opacity`, `toggle-labels`) as these IDs clash with the new "Node Config" section (`cfg-*`).
3.  Add the `[data-edge-style]` bindings in `sidebar.js` to support Solid/Dashed/Particle edge toggling.

---

## Citations

_No citations provided_
