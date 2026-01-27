# Research: Find all uses of Graph.pauseAnimation(), Graph.resumeAnimation(), Graph.onRenderFramePost, Graph.d3F...

> **Date:** 2026-01-27 08:15:19
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:90a65a64f9cd87fe00a412f55d0554c8ffc862738f3198e267a7f0a6146d4149`
> **Raw JSON:** `raw/20260127_081519_find_all_uses_of_graph_pauseanimation____graph_res.json`

---

## Query

Find all uses of Graph.pauseAnimation(), Graph.resumeAnimation(), Graph.onRenderFramePost, Graph.d3Force(), and animation lifecycle management in the current codebase. I need to understand:
1. Do we currently use pauseAnimation/resumeAnimation anywhere?
2. How do we control the force simulation lifecycle?
3. What callbacks are available from 3d-force-graph?
4. How do animation.js and the Graph interact?
5. What's the current pattern for stopping/starting animations?

---

## Response

Based on the provided codebase context, here is the analysis of the animation lifecycle and graph control mechanisms.

### 1. Do we currently use `pauseAnimation` / `resumeAnimation`?

**No.** A search of the provided files (`animation.js`, `panel-handlers.js`, `physics.js`, `layout-helpers.js`, etc.) reveals **zero usages** of `Graph.pauseAnimation()` or `Graph.resumeAnimation()`.

The codebase does not pause the WebGL render loop. Instead, it controls the **physics simulation engine** to stop node movement while keeping the canvas responsive for interaction (cam rotation, hovering).

### 2. How do we control the force simulation lifecycle?

The codebase uses a mix of D3-specific controls and a custom animation loop in `animation.js`.

*   **Freezing (Stopping Physics):**
    *   **Method 1 (`cooldownTicks`):** In `layout-helpers.js` and `panel-handlers.js`, `Graph.cooldownTicks(0)` is used to stop the simulation immediately.
    *   **Method 2 (`d3AlphaTarget`):** `Graph.d3AlphaTarget(0)` is used in `dimension.js` to let the simulation cool down naturally or stop during transitions.
    *   **Method 3 (Nullifying Forces):** `panel-handlers.js` (Freeze button) explicitly removes forces:
        ```javascript
        Graph.d3Force('charge', null);
        Graph.d3Force('link', null);
        ```
    *   **Method 4 (Pinning):** `LAYOUT_HELPERS.freeze()` sets `node.fx`, `node.fy`, `node.fz` to current positions, effectively locking nodes in place.

*   **Heating (Starting Physics):**
    *   **Reheating:** `Graph.d3ReheatSimulation()` is called frequently (e.g., in `physics.js` after slider updates, `layout-forces.js` after applying new forces).
    *   **Alpha Decay:** `Graph.d3AlphaDecay(...)` is adjusted in `panel-handlers.js` to control how fast the simulation settles.

### 3. What callbacks are available from 3d-force-graph?

Based on the code provided, the system does **not** explicitly hook into `3d-force-graph`'s native render callbacks (like `onRenderFramePost`) within the modules provided.

*   **Custom Monitoring:** Instead of relying on Graph callbacks, `perf-monitor.js` sets up its own `requestAnimationFrame` loop to measure FPS and render calls.
*   **Custom Animation Loop:** `animation.js` runs its own `requestAnimationFrame` loop to handle tweening and non-D3 layouts (like Orbital or Grid) and calls `REFRESH.throttled()` to update the graph.

### 4. How do `animation.js` and the `Graph` interact?

`animation.js` acts as an **external controller** that overrides the Graph's internal physics when applying specific layouts.

*   **The "Owner" Pattern:** `animation.js` enforces a single active animation via `_acquireOwnership(owner)`. This prevents `crossfade`, `layout`, and `flock` animations from fighting.
*   **Position Manipulation:**
    *   For layouts like **Grid** or **Orbital**, `animation.js` calculates exact coordinates and writes them to `node.fx`, `node.fy`, `node.fz` (fixed positions).
    *   It then calls `REFRESH.throttled()` (which calls `Graph.refresh()`) to notify the renderer of data changes.
*   **Hiding Edges:** During heavy transitions (like `_animateStaggered`), `animation.js` sets `Graph.linkOpacity(0)` to improve performance, restoring it when the animation completes.
*   **Crossfade:** It manipulates `node._viewOpacity` and traverses the Three.js objects directly (`node.__threeObj.material.opacity`) to handle visual transitions without re-running the physics engine.

### 5. What's the current pattern for stopping/starting animations?

The codebase distinguishes between **Physics Simulation** (D3) and **Visual Transitions** (Tweens).

**A. Physics Simulation (Continuous Force Layout):**
*   **Stop:** `Graph.cooldownTicks(0)` inside `LAYOUT_HELPERS.freeze()`.
*   **Start:** `Graph.d3ReheatSimulation()` inside `PHYSICS.applyState()`.

**B. Visual Transitions (Layout Changes / Camera):**
*   **Start:** `ANIM.applyLayout(preset)` initiates a `requestAnimationFrame` loop stored in `_animationId`.
*   **Stop:** `ANIM.stop()` calls `cancelAnimationFrame(_animationId)` and clears the owner.

**Summary Table of Controls:**

| Action | Mechanism Used | Location |
| :--- | :--- | :--- |
| **Stop Physics** | `Graph.cooldownTicks(0)` | `layout-helpers.js`, `panel-handlers.js` |
| **Disable Forces** | `Graph.d3Force(name, null)` | `panel-handlers.js`, `layout-forces.js` |
| **Restart Physics** | `Graph.d3ReheatSimulation()` | `physics.js`, `control-bar.js` |
| **Stop Transitions**| `cancelAnimationFrame(_animationId)` | `animation.js` |
| **Render Update** | `REFRESH.throttled()` -> `Graph.refresh()` | `refresh-throttle.js` |

---

## Citations

_No citations provided_
