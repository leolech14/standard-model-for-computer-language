# Research: RESEARCH GAP ANALYSIS: Color Telemetry Engine

## What We're Building
A Color Telemetry Engine for o...

> **Date:** 2026-01-24 19:40:27
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:9489c2c90f4c7be292e9ff44f22e4ae5df5a5aabd06dfb0b40d6b76d7b801026`
> **Raw JSON:** `raw/20260124_194027_research_gap_analysis__color_telemetry_engine.json`

---

## Query

RESEARCH GAP ANALYSIS: Color Telemetry Engine

## What We're Building
A Color Telemetry Engine for our Collider visualization system that:
1. Instruments the OKLCH→hex conversion boundary ('wormhole')
2. Records emission events with source tracking
3. Computes per-frame metrics: unique colors, collapse ratio, gamut clipping
4. Detects display gamut (sRGB vs Display P3 vs Rec2020)
5. Provides HUD overlay with real-time diagnostics

## Architecture Decisions Made
- Single choke point instrumentation with context injection
- Opt-in telemetry with 'Snapshot Mode' (single-frame capture)
- Ring buffer pattern using Float32Arrays for zero-allocation
- Quantization: L±0.001, C±0.001, h±0.1°
- Per-source collapse ratio tracking

## Current Gaps / Uncertainties

### Gap 1: WebGL Color Space Management
We use Three.js (0.149.0) with 3d-force-graph. Questions:
- How to configure gl.drawingBufferColorSpace for Display P3?
- Does Three.js 0.149 support DisplayP3ColorSpace?
- What's the actual pipeline: OKLCH → sRGB → WebGL framebuffer → display?

### Gap 2: Gamut Clipping Detection
We convert OKLCH→sRGB but some OKLCH colors are outside sRGB gamut.
- How do we DETECT that clipping occurred during conversion?
- What's the standard algorithm for gamut mapping (clip vs compress)?
- Is there a way to measure 'how much' a color was clipped?

### Gap 3: Ring Buffer Performance in JavaScript
We plan to use Float32Arrays for zero-allocation telemetry.
- What's the actual performance difference vs object allocation at 60fps?
- Are there gotchas with typed arrays in hot paths?
- Should we use SharedArrayBuffer for worker offloading?

### Gap 4: Browser Gamut Detection Reliability
We plan to use matchMedia('(color-gamut: p3)').
- How reliable is this across browsers (Safari, Chrome, Firefox)?
- Does it update when window moves between monitors?
- Are there edge cases (external monitors, color profiles)?

### Gap 5: Chromaticity Diagram Rendering
For the HUD, we want to show a horseshoe diagram with sRGB/P3 triangles.
- What's the standard way to render CIE xy chromaticity in WebGL/Canvas?
- How do we plot OKLCH colors on a 2D chromaticity diagram?
- Are there existing libraries or should we compute the horseshoe coordinates?

## Your Task
1. Identify which gaps are most critical for our implementation
2. Formulate 2-3 precise Perplexity (sonar-pro) queries that would fill the most important gaps
3. The queries should be specific, technical, and likely to return actionable information
4. Prioritize gaps that could cause bugs or performance issues if we guess wrong

Format your response as:
PRIORITY RANKING: [ordered list of gaps by criticality]
PERPLEXITY QUERIES: [2-3 ready-to-execute queries]
RATIONALE: [why these queries first]

---

## Response

Here is the research gap analysis and the prioritized queries to execute.

### PRIORITY RANKING

1.  **Gap 1: WebGL Color Space Management (Three.js 0.149 Constraints)**
    *   **Criticality:** **SHOWSTOPPER.** Three.js underwent a massive Color Management refactor in r152 (introducing `THREE.ColorManagement`). Version 0.149 relies on the older `renderer.outputEncoding` system. If r149 cannot correctly configure the WebGL context for `display-p3` or write to a P3 buffer, the telemetry engine will record high-fidelity data that is silently crushed by the renderer before it hits the screen.
2.  **Gap 2: Gamut Clipping Detection Algorithms**
    *   **Criticality:** **HIGH.** The "Collapse Ratio" and "Gamut Clipping" metrics define the value of this engine. We need a precise, mathematically inexpensive way to determine *if* a color was clipped and *by how much* (DeltaE or Euclidian distance in linear space) before the `clamp()` operation hides the evidence.
3.  **Gap 4: Browser Gamut Detection Reliability**
    *   **Criticality:** **MEDIUM/HIGH.** The HUD needs to know the "Ground Truth" of the display. If `matchMedia` doesn't fire events when dragging a window from a MacBook (P3) to an external monitor (sRGB), the metrics will be contextualized incorrectly (e.g., warning about clipping that isn't actually happening, or vice versa).

---

### PERPLEXITY QUERIES

**Query 1 (Infrastructure Viability):**
> "Three.js r149 support for Display P3 output using drawingBufferColorSpace. How to enable wide gamut rendering in Three.js versions prior to r152 ColorManagement update?"

**Query 2 (Metric Logic):**
> "Efficient algorithm to detect and quantify gamut clipping magnitude when converting OKLCH to sRGB. How to calculate 'clipping distance' before clamping RGB values?"

**Query 3 (Environment Reliability):**
> "Reliability of `window.matchMedia('(color-gamut: p3)')` event listeners when moving windows between sRGB and P3 monitors in Chrome and Safari. Does the media query update dynamically?"

---

### RATIONALE

**Why these queries first?**

*   **Query 1 is a binary risk.** If Three.js r149 cannot target a P3 framebuffer, we must either upgrade the library (huge regression risk for the rest of the application) or accept that the visualization is strictly sRGB, rendering the P3 telemetry "theoretical" rather than "actual."
*   **Query 2 defines the math.** Simply checking `if (r > 1.0)` determines *presence*, but we need to measure *magnitude* ("how much" was clipped) to calculate the **Collapse Ratio**. We need a standard approach (likely derived from CSS Color 4 specs) to ensure our metrics match standard color science.
*   **Query 3 validates the user context.** If the browser doesn't reliably report the monitor's capability dynamically, our "Gamut Detection" feature will be flaky, leading to user confusion (e.g., "Why does it say sRGB when I'm on a Pro Display XDR?"). We need to know if we have to poll the value or if we can trust the event listener.

---

## Citations

_No citations provided_
