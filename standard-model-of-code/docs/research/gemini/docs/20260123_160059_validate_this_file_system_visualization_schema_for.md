# Research: Validate this file system visualization schema for a code analysis tool:

CONTEXT: We're building a ...

> **Date:** 2026-01-23 16:00:59
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:408e70c9bb67fdfac08a561821243a33787e59bcd9daba324ae5a00206d05284`
> **Raw JSON:** `raw/20260123_160059_validate_this_file_system_visualization_schema_for.json`

---

## Query

Validate this file system visualization schema for a code analysis tool:

CONTEXT: We're building a 3D file tree visualization for the Collider tool (Standard Model of Code). Currently we have a working 3D graph visualization using Three.js + 3d-force-graph.

PROPOSED SCHEMA:

1. STRUCTURE: Directory tree rendered as 3D tree (natural for hierarchical data)

2. COLOR MAPPING using OKLCH color space:
   - HUE (H) → File format/type with SEMANTIC PROXIMITY
     * .py near .pyx (both Python)
     * .js near .ts near .jsx (JS family)
     * .md near .txt near .rst (docs family)
     * .json near .yaml near .toml (config family)
   
   - LIGHTNESS (L) → TBD (options: age, depth, coverage)
   - CHROMA (C) → TBD (options: activity, importance, health)

3. SIZE MAPPING with per-type NORMALIZERS:
   - Code files: size = f(lines_of_code) or f(tokens)
   - Data files: size = f(file_size_kb)
   - Binary files: different scale (they're huge)
   - Config files: fixed small size
   
   Normalizer pattern: log scale + type-specific min/max clamping

4. THE NORMALIZER CONCEPT:
   Different file types need different scaling functions because:
   - A 1000-line Python file is 'big'
   - A 1000KB image is 'small'
   - Without normalization, binaries would dominate visually

QUESTIONS TO VALIDATE:
1. Is OKLCH the right color space? (vs HSL, LAB, etc.)
2. What should map to Lightness? (age? depth? coverage?)
3. What should map to Chroma? (activity? importance? health?)
4. Is log-scale the right normalizer for file sizes?
5. Should we use 'semantic hue wheels' with predefined positions for file families?
6. Any perceptual issues with this mapping?
7. Academic/UX precedent for this approach?

Rate the overall schema and suggest improvements.

---

## Response

This is a strong, scientifically grounded foundation for visualizing codebase topology. Using **OKLCH** is the correct decision for data visualization because it offers **perceptual uniformity**—a change in numerical value corresponds to a predictable change in perceived color, unlike HSL or RGB.

Here is the senior engineering analysis of your schema, validation of your questions, and specific recommendations to align this with the **Standard Model of Code** context.

---

### Executive Verdict
**Rating: 8.5/10 (High Confidence)**
The schema is conceptually sound but risks collision between **Data Visualization** physics (color sets meaning) and **3D Rendering** physics (lighting affects color).

**Critical Adjustments Needed:**
1.  **Switch Size Mapping:** Use **Cube Root** scaling, not Log scaling, for 3D spheres.
2.  **Define L/C Logic:** Map **Recency** to Lightness and **Topology/Importance** to Chroma.
3.  **Material Strategy:** Use **Unlit/Emissive** materials to prevent 3D lighting from corrupting your data encoding.

---

### Detailed Validation & Answers

#### 1. Is OKLCH the right color space?
**YES.** It is superior to HSL/HSV and LAB for this use case.
*   **Why:** In HSL, pure yellow (`#FFFF00`) appears much brighter than pure blue (`#0000FF`) despite having the same "Lightness" value (50%). In 3D space, this creates false depth cues (brighter objects look closer).
*   **OKLCH Benefit:** L=70% ensures all nodes, regardless of Hue (File Type), have the same perceived brightness. This allows you to use Lightness solely for data encoding without breaking the Hue categorization.

#### 2. What should map to Lightness (L)?
**Recommendation: RECENCY (Time since last edit)**
*   **Mapping:** New/Hot = High Lightness (White/Bright). Old/Stale = Low Lightness (Darker).
*   **Rationale:** "Fading Memory." This aligns with the "Refinery" concept of fresh vs. settled code.
*   **Constraint:** Ensure your 3D background is dark. "Old" code fades into the background; "New" code pops out.

#### 3. What should map to Chroma (C)?
**Recommendation: TOPOLOGICAL IMPORTANCE (PageRank / Centrality)**
*   **Mapping:** High Importance (Hubs) = High Chroma (Vivid). Low Importance (Leaves) = Low Chroma (Greyish).
*   **Rationale:** Attention management. You want the "nervous system" of the code (core utils, main logic) to be vivid, while boilerplate or isolated scripts recede into greyscale.
*   **Alternative:** If "Health" is available (from Socratic audits), Health could drive Chroma (Broken = Vivid, Healthy = Neutral), but Importance is usually more useful for general exploration.

#### 4. Is log-scale the right normalizer for file sizes?
**NO. Use CUBE ROOT ($\sqrt[3]{x}$).**
*   **The Math:** In 3D, if you double the radius, you increase the volume by $8x$ ($r^3$). If you map LOC directly to Radius, a 1000-line file looks massive compared to a 100-line file.
*   **The Fix:** You want the **Volume** (Visual Mass) to represent the Cognitive Mass (LOC/Complexity).
    *   $Radius = c \cdot \sqrt[3]{Metric}$
*   **Exception:** Log scale is acceptable *only if* the variance is extreme (e.g., 1 line vs 1,000,000 lines), but for standard codebases, Cube Root feels more physically accurate.

#### 5. Should we use 'semantic hue wheels'?
**YES.** Divide the 360° Hue wheel into "Sectors of Meaning."
*   **Logic (Py, JS, Go):** Cool Colors (180° - 300°: Cyans, Blues, Purples). *Blue implies structure.*
*   **Data/Config (JSON, YAML):** Warm Neutrals (30° - 90°: Oranges, Browns). *Earth tones imply foundation.*
*   **Documentation (MD, TXT):** Bright Warms (90° - 150°: Yellows, Greens). *Highlighting implies info.*
*   **Assets (PNG, GLB):** Magentas/Pinks (300° - 360°).

#### 6. Any perceptual issues?
**The "Muddy Middle" Problem.**
If a file is Old (Low L) and Unimportant (Low C), it becomes dark grey. Against a dark background, it disappears.
*   **Fix:** Set a minimum floor for Lightness (e.g., L range 0.4 to 0.9, never 0.0).

#### 7. Academic/UX Precedent?
*   **CodeCity (Wettel & Lanza):** Uses "Building" metaphors (Height = Complexity, Base = LOC).
*   **Gource:** Uses tree structures with force-directed layouts.
*   **SonarQube Treemaps:** Uses Size=LOC, Color=Coverage/Complexity.

---

### Refined Schema Specification

To implement this in your `viz/` module (referencing `TASK-010` and `OPP-013` context):

#### A. The "Cognitive Mass" Normalizer
Do not map bytes to size. Map **Complexity** to size.
*   **Metric:** `Cognitive Mass`
*   **Formula:**
    ```javascript
    function getRadius(node) {
      let mass = 0;
      if (node.is_code) mass = node.loc * 1.0; // 1 line = 1 unit
      else if (node.is_config) mass = node.lines * 2.0; // Config is dense
      else if (node.is_doc) mass = node.words / 10.0; // Docs are airy
      else mass = Math.log(node.size_kb) * 10; // Binaries: Log scale fallback

      // Cube root for volumetric consistency
      return Math.cbrt(mass) * GLOBAL_SCALE_FACTOR;
    }
    ```

#### B. The OKLCH Color Function
```javascript
// D3-color or similar library recommended
function getNodeColor(node) {
  // 1. HUE: File Type Family
  const hue = getSemanticHue(node.extension); 
  
  // 2. LIGHTNESS: Recency (Newer = Lighter)
  // Clamp L between 0.45 (visible) and 0.90 (bright)
  const daysOld = (Date.now() - node.last_modified) / (1000 * 60 * 60 * 24);
  const lightness = clamp(0.9 - (daysOld / 365) * 0.4, 0.45, 0.9);

  // 3. CHROMA: Importance/Activity (Important = Vivid)
  // Clamp C between 0.02 (grey) and 0.25 (vivid neon)
  const importance = node.page_rank || 0.1; 
  const chroma = clamp(importance * 0.3, 0.05, 0.25);

  return `oklch(${lightness} ${chroma} ${hue})`;
}
```

#### C. The "Unlit" Material Requirement
In Three.js, standard materials (`MeshStandardMaterial`) react to light. This changes the displayed color based on the angle of the sun/light source, destroying your data encoding (a "White" file looks "Grey" in shadow).

*   **Recommendation:** Use `MeshBasicMaterial` (unlit) or `MeshLambertMaterial` with high Ambient light.
*   **Best:** Use `MeshPhysicalMaterial` with `emissive` set to the OKLCH color and `color` set to black. This makes the data "glow" with its true value.

### Integration with Project Context
This schema supports the **BARE** (Background Auto-Refinement Engine) objectives:
*   **Drift Detection:** "Old" files (Low L) that are "Important" (High C) will appear as **Dark Vivid** nodes. These are risky—critical code that hasn't been touched in a long time. This is an immediate visual cue for the `Socratic Layer`.

---

## Citations

_No citations provided_
