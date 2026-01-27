# Research: I need to fix the performance collapse. The codebase has:
1. Multiple concurrent RAF loops (selectio...

> **Date:** 2026-01-27 08:22:53
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:a87a32aa422f7d0e44d19322ae80470b6e9fc926401469ff4f7518c51457fc91`
> **Raw JSON:** `raw/20260127_082253_i_need_to_fix_the_performance_collapse__the_codeba.json`

---

## Query

I need to fix the performance collapse. The codebase has:
1. Multiple concurrent RAF loops (selection, perf-monitor, possibly others)
2. REFRESH.throttled() being called from inside animation loops every frame
3. controls().enabled = false blocking right-click rotation during marquee select

What's the MINIMAL fix that preserves existing architecture? Should I:
A) Remove REFRESH calls from animation loops? 
B) Consolidate all RAF loops into one master loop?
C) Use Graph.pauseAnimation() pattern instead?
D) Something else?

Also: How can I allow right-click rotation while left-click does marquee select? The issue is controls().enabled = false blocks ALL mouse interactions.

---

## Response

Based on your analysis, **Option A (Remove REFRESH from loops)** combined with a targeted event handling fix is the correct approach. `3d-force-graph` utilizes an internal render loop that automatically picks up position changes (`fx`, `fy`, `fz`) and color updates. Calling `REFRESH.throttled()` (which triggers a full data re-ingest/geometry rebuild) 60 times a second is the root cause of the performance collapse.

Here is the minimal fix.

### 1. Fix Performance Collapse (`animation.js`)

You need to stop the visualization from rebuilding the entire graph topology every single frame.

**In `src/core/viz/assets/modules/animation.js`:**
Locate the `animateFrame` (and similar loop functions) and comment out `REFRESH.throttled()`. Only allow it to run when the animation *completes*.

```javascript
// ... inside animateFrame() ...

    nodes.forEach((n, i) => {
        // ... node interpolation logic ...
    });

    // --- FIX START ---
    // REMOVE THIS: Triggers full geometry rebuild 60fps
    // if (typeof REFRESH !== 'undefined') {
    //     REFRESH.throttled();
    // } 
    // --- FIX END ---

    const totalDuration = baseDuration + staggerSpread;
    if (elapsed < totalDuration) {
        _animationId = requestAnimationFrame(animateFrame);
    } else {
        // ... completion logic ...
        // KEEP THIS: Final sync ensures everything settles correctly
        if (typeof REFRESH !== 'undefined') {
            REFRESH.force();
        }
    }
```

*Repeat this pattern for `_animateSimple`, `_startLayoutMotion`, `flockStep`, `loop` (pulse), and `crossfade` functions within this file.*

### 2. Fix Right-Click Rotation (`selection.js`)

`controls.enabled = false` disables the entire controller (Rotation, Zoom, Pan). To allow Right-Click (Rotate) while blocking Left-Click (Marquee/Pan), we should stop disabling the controls globally and instead stop the Left-Click event from bubbling up to the OrbitControls.

**In `src/core/viz/assets/modules/selection.js`:**
Modify `onPointerDown`.

```javascript
    const onPointerDown = (e) => {
        if (e.button !== 0) return; // Only handle left button
        if (e.target !== canvas) return;

        // SPACE + LEFT = PAN MODE
        if (_spacePressed) {
            _panActive = true;
            _panStart = { x: e.clientX, y: e.clientY };
            canvas.style.cursor = 'grabbing';
            
            // --- FIX START ---
            // DON'T disable controls globally. 
            // This kills Right-Click Rotation and Scroll Zoom.
            /* 
            if (Graph.controls()) {
                Graph.controls().enabled = false; 
            } 
            */
            
            // INSTEAD: Stop immediate propagation.
            // This prevents OrbitControls (which listens on the same element)
            // from receiving this specific Left-Click event.
            e.stopImmediatePropagation();
            // --- FIX END ---
            
            e.preventDefault();
            return;
        }

        // LEFT (no space) = MARQUEE SELECT
        if (typeof HOVERED_NODE !== 'undefined' && HOVERED_NODE) return;
        _marqueeActive = true;
        _marqueeAdditive = !!e.shiftKey;
        _marqueeStart = { x: e.clientX, y: e.clientY };
        
        // ... existing box update logic ...

        // --- FIX START ---
        // Prevent OrbitControls from interpreting this as a "Rotate" drag start
        e.stopImmediatePropagation(); 
        // --- FIX END ---

        e.preventDefault();
        e.stopPropagation();
    };
```

### Summary of Changes

1.  **Performance:** By removing `REFRESH.throttled()` from the loops, you rely on the WebGL renderer's native tick (which is fast) instead of the Data Manager's re-ingest (which is slow).
2.  **Interaction:** By using `e.stopImmediatePropagation()` instead of `controls.enabled = false`, you effectively "steal" the Left Mouse Button for your tools (Marquee/Pan) while leaving the Right Mouse Button available for the OrbitControls to handle Rotation.

---

## Citations

_No citations provided_
