# Research: Three.js r149 support for Display P3 output using drawingBufferColorSpace. How to enable wide gamut ...

> **Date:** 2026-01-24 19:40:49
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:38c83dbd561301a4f293896362189d584f4f3a160c7ce754981d4abab5a1df43`
> **Raw JSON:** `raw/20260124_194049_three_js_r149_support_for_display_p3_output_using.json`

---

## Query

Three.js r149 support for Display P3 output using drawingBufferColorSpace. How to enable wide gamut rendering in Three.js versions prior to r152 ColorManagement update? What are the limitations and workarounds?

---

## Response

Based on the search results, Three.js r149 does not have built-in support for Display P3 output through ColorManagement. However, you can access the underlying WebGL `drawingBufferColorSpace` property directly to enable wide-gamut rendering.

## Direct WebGL Access Approach

Since Three.js r149 predates the ColorManagement updates in r152, you can manually set the drawing buffer color space by accessing the WebGL context:[1][2]

```javascript
const canvas = document.getElementById("canvas");
const renderer = new THREE.WebGLRenderer({ canvas });
const gl = renderer.getContext();

// Enable Display P3 color space
gl.drawingBufferColorSpace = "display-p3";
```

This sets the **drawing buffer to Display P3**, allowing the renderer to output in the wider color gamut.[1][2]

## Browser and Version Requirements

Display P3 support via `drawingBufferColorSpace` is **available by default in Chrome 104 and later**.[1] To detect support before attempting to use it, check for the property's presence:[1]

```javascript
if ('drawingBufferColorSpace' in gl) {
  gl.drawingBufferColorSpace = 'display-p3';
}
```

## Key Limitations

- **No automatic color space management:** Unlike r152 and later, r149 lacks integrated ColorManagement for handling color conversions across textures, shaders, and output. You must manually manage color space conversions.
- **Texture unpacking:** The `unpackColorSpace` property must be set separately for texture imports to be properly converted to Display P3.[2]
- **Shader conversions:** Color conversion in shaders is not automated and must be implemented manually.[1]

## Recommended Workaround

For optimal performance, **upload texture data without conversion** (using `Uint8ClampedArray`) and perform color conversion to the `drawingBufferColorSpace` via shaders on the GPU, rather than on the CPU.[1] This avoids conversion overhead during texture loading.

The most practical solution is to **upgrade to Three.js r152 or later**, where Display P3 support is integrated into ColorManagement with proper handling of color spaces across the entire rendering pipeline.[4][5]

---

## Citations

1. https://ccameron-chromium.github.io/webgl-examples/p3.html
2. https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/drawingBufferColorSpace
3. https://forum.babylonjs.com/t/display-p3-colorspace/40456
4. https://github.com/mrdoob/three.js/issues/26479
5. https://threejs.org/docs/pages/module-ColorSpaces.html
6. https://discourse.threejs.org/t/how-to-work-with-display-p3-wide-gamut-color-profile-in-webgl-three-js/6471
7. https://threejs.org/docs/
8. https://discourse.threejs.org/t/issue-with-srgbcolorspace-output-after-upgrade-r164/66217
9. https://caniuse.com/mdn-api_webglrenderingcontext_drawingbuffercolorspace

---

## Usage Stats

- Prompt tokens: 44
- Completion tokens: 443
- Total tokens: 487
