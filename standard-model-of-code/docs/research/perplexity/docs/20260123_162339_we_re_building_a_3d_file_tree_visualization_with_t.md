# Research: We're building a 3D file tree visualization with Three.js where node colors encode data (OKLCH: hue=...

> **Date:** 2026-01-23 16:23:39
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:4dd4dfb2506753c038ab14d475b36e236a71f5df467f9a983c2e6599d3256f16`
> **Raw JSON:** `raw/20260123_162339_we_re_building_a_3d_file_tree_visualization_with_t.json`

---

## Query

We're building a 3D file tree visualization with Three.js where node colors encode data (OKLCH: hue=file type, lightness=recency, chroma=importance).

**Problem:** Standard 3D lighting (Phong, Lambert) corrupts the data encoding because:
- Shadows darken nodes (lightness no longer reflects recency)
- Highlights brighten nodes (chroma interpretation changes)
- Ambient occlusion adds unintended darkness

**Proposed solution:** Use unlit/emissive materials so colors are data-pure.

**Questions:**
1. In Three.js, what's the best approach for unlit materials that preserve exact RGB values?
2. Are there any perceptual issues with emissive-only 3D scenes (depth perception, spatial relationships)?
3. Any techniques to maintain depth cues without corrupting color data (e.g., outline shaders, fog, size attenuation)?

---

## Response

For preserving exact RGB values in your data visualization, **use `MeshBasicMaterial`** rather than emissive materials, as it displays colors unaffected by any lighting[1]. If you need emissive properties specifically, `MeshStandardMaterial` with an **`emissiveMap` and high `emissiveIntensity`** can work, though the distinction is that emissive colors always display regardless of lighting conditions while still being technically influenced by the material system[1].

## Best Approach for Unlit Materials

`MeshBasicMaterial` is the most direct solution for data-pure rendering[1]. This material ignores all light sources and displays your encoded OKLCH colors exactly as specified. If you're importing models with embedded materials from tools like Substance Painter, you can traverse the scene and replace lit materials with `MeshBasicMaterial` while preserving the texture maps[4]:

```javascript
loader.load('model.glb', function (gltf) {
  var model = gltf.scene;
  model.traverse(function (o) {
    if (o.isMesh) {
      o.material = new THREE.MeshBasicMaterial({map: o.material.map});
    }
  });
  scene.add(model);
});
```

For the emissive alternative, `MeshStandardMaterial` with an `emissiveMap` provides the same visual effect of always-visible color, controlled by the `emissiveIntensity` property to adjust brightness[1].

## Perceptual Issues with Unlit Scenes

Emissive-only or unlit scenes present genuine depth perception challenges. Without lighting variation, you lose critical spatial cues:

- **Shading gradients** normally help viewers understand surface curvature and orientation
- **Shadows** establish spatial relationships between objects
- **Specular highlights** indicate surface position relative to the viewer

This is particularly problematic for a tree visualization where spatial hierarchy should reinforce data relationships.

## Techniques to Preserve Depth Without Corrupting Color Data

Several approaches can maintain spatial clarity while keeping your OKLCH encoding intact:

**Outline/Edge rendering:** Add subtle wireframe or outline passes that don't affect base colors. This emphasizes 3D structure without altering your data values.

**Fog:** Linear or exponential fog can add atmospheric depth cues without changing individual object colors—distant nodes fade slightly, establishing depth without darkening the OKLCH values themselves[1].

**Size attenuation:** Vary node size based on depth or distance to reinforce spatial relationships independently of color.

**Monochromatic lighting at high intensity:** Use a very bright, uniform directional light with minimal shadow mapping. This provides subtle shading cues for depth perception while keeping color variation minimal. Since the light is uniform and intense, local variations in shade would be negligible.

**Normal-mapped geometry without color influence:** If your nodes have geometry (not just flat planes), subtle normal mapping can create surface detail that signals 3D space without altering perceived color through lighting.

The most effective solution likely combines **`MeshBasicMaterial` for color purity + fog for depth + subtle geometry/outlines for structure**, keeping your OKLCH encoding completely protected while still providing viewers sufficient spatial context to interpret the tree hierarchy.

---

## Citations

1. https://dustinpfister.github.io/2021/06/22/threejs-emissive-map/
2. https://github.com/KhronosGroup/glTF-Blender-Exporter/issues/315
3. https://forum.babylonjs.com/t/receiving-shadows-on-emissive-materials/30600
4. https://discourse.threejs.org/t/glb-modify-material-and-add-emission/4661
5. https://discourse.threejs.org/t/light-emitting-objects/24533
6. https://threejs.org/docs/

---

## Usage Stats

- Prompt tokens: 184
- Completion tokens: 639
- Total tokens: 823
