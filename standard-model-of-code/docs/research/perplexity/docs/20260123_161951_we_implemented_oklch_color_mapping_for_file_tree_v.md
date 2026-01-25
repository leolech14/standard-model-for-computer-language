# Research: We implemented OKLCH color mapping for file tree visualization with these design choices:

1. **Hue ...

> **Date:** 2026-01-23 16:19:51
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:ab9472a89bde07cb4f024ea4ac059c73ae7f7d0da91138075619bf7179966e71`
> **Raw JSON:** `raw/20260123_161951_we_implemented_oklch_color_mapping_for_file_tree_v.json`

---

## Query

We implemented OKLCH color mapping for file tree visualization with these design choices:

1. **Hue (0-360°)**: Semantic file type mapping
   - Logic/Code: 180-300° (cyan to purple)
   - Config: 30-90° (orange to yellow-green)
   - Docs: 90-150° (yellow-green to green)
   - Assets: 300-360° (magenta to red)
   - Unknown: 0° (red fallback)

2. **Lightness (0.3-0.9)**: Recency mapping
   - 0 days (today): L=0.9 (brightest)
   - 7 days: L=0.7
   - 30 days: L=0.5
   - 90+ days: L=0.3 (darkest)
   - Piecewise linear interpolation between breakpoints

3. **Chroma (0.1-0.4)**: Importance mapping
   - Linear scale: importance 0.0→chroma 0.1, importance 1.0→chroma 0.4
   - Kept low to avoid "muddy middle" problem in OKLCH

Validate:
- Is the chroma range 0.1-0.4 appropriate for OKLCH perceptual uniformity?
- Is piecewise linear interpolation for lightness the right approach vs logarithmic decay?
- Any known issues with OKLCH→sRGB conversion at these lightness/chroma ranges (gamut clipping)?

---

## Response

Your OKLCH implementation is well-founded, though there are some refinements to consider based on how the color space behaves:

## Chroma Range (0.1-0.4)

Your range is **appropriate and conservative**. According to CSS specifications, chroma in OKLCH treats +0.4 as 100% and practically doesn't exceed +0.5[3]. By keeping chroma between 0.1-0.4, you're operating safely within the perceptually uniform range where equal numerical changes produce equal perceptual changes[5]. This avoids the "muddy middle" problem you mentioned—staying below the upper limits where chroma becomes unpredictable across different hues and lightness values[1]. The lower boundary (0.1) also works well for importance zero, maintaining visibility while reducing saturation.

## Lightness Interpolation: Piecewise Linear vs. Logarithmic

**Piecewise linear is the right choice for your use case.** OKLCH's key strength is that it's **perceptually uniform**, meaning equal numerical changes in lightness produce equal perceptual changes across different hues[1][2]. This means L=0.9 to L=0.7 (0.2 difference) will feel like the same brightness change as L=0.7 to L=0.5 (another 0.2 difference).

For a recency-based visualization, piecewise linear interpolation directly leverages this uniformity—a file from today (L=0.9) will appear noticeably "fresher" than one from 7 days ago (L=0.7) with the same visual consistency as the 7-to-30 day transition. Logarithmic decay would complicate this, making older files fade more gradually than recent files, which could obscure the visual hierarchy you're building[7].

## Gamut Clipping at Your Ranges

At your ranges (L: 0.3-0.9, C: 0.1-0.4), **gamut clipping is unlikely to be a significant issue**. OKLCH was specifically designed to address unexpected hue and lightness changes that plagued earlier color spaces like CIELAB[3]. Your lightness range is well within the safe 0-1 spectrum, and your chroma values remain conservative. The main risk occurs at extreme combinations (very high chroma with very high or very low lightness), which you're avoiding[4].

However, two practical notes:

- **Wide-gamut support**: If your visualization targets Display P3 displays, OKLCH can leverage 50% more colors than sRGB[4], making your importance and recency gradations even more distinct.
- **sRGB fallback**: Modern browsers handle OKLCH→sRGB conversion, but some older devices may clip out-of-gamut colors. Test your specific hue ranges (especially the 300-360° asset colors) on target devices, as reds and high-saturation magenta can push gamut boundaries more easily than other hues.

Your design choices align well with OKLCH's perceptual strengths for hierarchical visualization.

---

## Citations

1. https://calebduren.com/posts/oklch
2. https://uxdesign.cc/oklch-explained-for-designers-dc6af4433611
3. https://en.wikipedia.org/wiki/Oklab_color_space
4. https://uploadcare.com/blog/oklch-in-css/
5. https://oklch.net/hex-to-oklch
6. https://css-tricks.com/almanac/functions/o/oklch/
7. https://observablehq.com/@mjbo/perceptually-uniform-color-models
8. https://nikhgupta.com/posts/uniform-colors-oklch

---

## Usage Stats

- Prompt tokens: 324
- Completion tokens: 640
- Total tokens: 964
