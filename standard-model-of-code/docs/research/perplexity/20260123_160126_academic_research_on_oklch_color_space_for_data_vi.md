# Perplexity Research: Academic research on OKLCH color space for data visualization:

1. Why is OKLCH preferred over HSL/H...

> **Date:** 2026-01-23 16:01:26
> **Model:** sonar-pro
> **Query Length:** 666 chars

---

## Query

Academic research on OKLCH color space for data visualization:

1. Why is OKLCH preferred over HSL/HSV for encoding data in visualizations?
2. What is 'perceptual uniformity' and why does it matter for color-coded data?
3. For 3D node-based visualizations, should size scaling use logarithmic or cube root?
4. What is the 'CodeCity' visualization approach and how does it map code metrics to visuals?
5. Best practices for mapping file types to hue positions on a color wheel (semantic color assignment)
6. How to prevent 3D lighting from corrupting data-encoded colors (emissive materials)?

Looking for academic papers, UX research, and D3/Three.js best practices.

---

## Response

I can provide comprehensive answers to questions 1-2 based on the search results, but questions 3-6 require information beyond what's available in these sources.

## OKLCH vs. HSL/HSV for Data Visualization

**OKLCH is preferred over HSL because it maintains perceptual uniformity across color changes**, while HSL introduces unwanted variations in brightness and saturation. When using HSL with consistent lightness values, colors appear inconsistently bright—some look vivid while others appear muted or grayish.[1] OKLCH solves this by using the **OKLab color space**, which ensures that changing only the hue produces colors with uniform perceived brightness and saturation.[1]

For practical data encoding, this matters significantly. With HSL, if you define a color palette by varying hue while keeping lightness constant, the resulting colors won't look uniformly prominent, making it difficult to create fair visual comparisons in data.[1] OKLCH allows you to "use the same value for all colors and just change the hue," creating visually consistent data encodings.[1]

Additionally, when adjusting lightness values, HSL shifts hue unpredictably—a blue might become purple in lighter shades and grayish-brown in darker shades.[1] OKLCH maintains consistent hue across all lightness levels, preserving data integrity when representing sequential or diverging scales.[1]

## Perceptual Uniformity and Its Importance

**Perceptual uniformity means that equal mathematical changes in color values correspond to equal perceived visual differences** to the human eye. OKLCH achieves this through the OKLab color space, which was specifically designed to be perceptually uniform.[1]

For data visualization, perceptual uniformity is critical because it ensures that color differences accurately represent data differences. If a visualization's color encoding isn't perceptually uniform, viewers may misinterpret relative magnitudes—a 20% increase in hue might appear visually larger or smaller than the same increase elsewhere on the scale, introducing cognitive bias.[1] OKLCH also supports the wider Display-P3 color gamut available on modern displays, offering "upwards of 50% more color than the sRGB gamut"[2], which provides additional flexibility for distinguishing data categories without color repetition.

## Regarding Your Other Questions

I cannot find academic research in the provided search results addressing questions 3-6 about logarithmic scaling in 3D visualizations, CodeCity approaches, semantic hue mapping, or emissive material techniques for color preservation. These specialized topics would require domain-specific papers from visualization research, computer graphics literature, or D3/Three.js documentation that aren't included in these sources.

---

## Citations

1. https://gigazine.net/gsc_news/en/20250826-what-are-oklch-colors/
2. https://www.smashingmagazine.com/2023/08/oklch-color-spaces-gamuts-css/
3. https://observablehq.com/@clhenrick/color-palette-analysis-using-oklch
4. https://uxdesign.cc/oklch-with-chatgpt-5-2848ba090e14
5. https://blog.jim-nielsen.com/2023/ok-lch-im-convinced/
6. https://www.cs.ubc.ca/~tmm/courses/547-25/slides/week7-4x4.pdf
7. https://dl.acm.org/doi/full/10.1145/3696593.3696598

---

## Usage Stats

- Input tokens: 154
- Output tokens: 534
