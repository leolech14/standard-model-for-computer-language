# Research: Reliability of window.matchMedia('(color-gamut: p3)') event listeners when moving windows between sR...

> **Date:** 2026-01-24 19:43:45
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:de91ac7b8ea595d5e4c2786a55f4a905f675bf9273bc3534f7de42746c8fd1b0`
> **Raw JSON:** `raw/20260124_194345_reliability_of_window_matchmedia___color_gamut__p3.json`

---

## Query

Reliability of window.matchMedia('(color-gamut: p3)') event listeners when moving windows between sRGB and P3 monitors in Chrome and Safari. Does the media query update dynamically when a window is dragged to a different display? Are there known browser bugs or limitations?

---

## Response

**In Chrome and Safari, `window.matchMedia('(color-gamut: p3)')` event listeners reliably update dynamically when a window is dragged between sRGB and P3 monitors, as both browsers correctly evaluate the media query based on the current display's capabilities.** [1][2][4]

This dynamic behavior stems from standard media query implementation, where `window.matchMedia()` reflects the active display's gamut (sRGB vs. DCI-P3 or equivalent), and adding listeners like `mql.addEventListener('change', handler)` triggers on changes such as window movement between monitors. [2][4]

- Chrome accurately reports `true` for P3 on wide-gamut displays and `false` on sRGB, with JavaScript examples confirming real-time checks via `.matches`. [1][2]
- Safari similarly supports this, matching P3-capable hardware (e.g., modern Macs) and enabling conditional styles or scripts for vivid content. [1][4]

No known bugs or limitations are documented in search results for this specific cross-monitor scenario in Chrome or Safari; both outperform Firefox, which always returns `false` regardless of display support. [1] Unrelated Safari issues exist, such as WebGL color management regressions in macOS Sonoma, but these do not impact `color-gamut` media queries. [3] For implementation, test with code like:

```javascript
const mql = window.matchMedia('(color-gamut: p3)');
console.log(mql.matches); // true/false based on current display
mql.addEventListener('change', (e) => {
  console.log('Gamut changed:', e.matches);
});
```

Drag the window between monitors to observe updates. [2][4]

---

## Citations

1. https://github.com/mdn/browser-compat-data/issues/21422
2. https://developer.chrome.com/docs/css-ui/migrate-hd-color
3. https://discourse.threejs.org/t/over-saturated-colors-in-safari/56540
4. https://webkit.org/blog/6682/improving-color-on-the-web/
5. https://css-tricks.com/the-expanding-gamut-of-color-on-the-web/
6. https://polypane.app/blog/the-complete-guide-to-css-media-queries/
7. https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/color-gamut
8. https://furbo.org/color/ResponsiveColor/

---

## Usage Stats

- Prompt tokens: 57
- Completion tokens: 356
- Total tokens: 413
