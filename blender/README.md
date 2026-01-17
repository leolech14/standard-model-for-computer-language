# Blender Visualization for Standard Model of Code

Self-contained Blender 3D visualization of the SMC 16-level column.

## Structure

```
blender/
├── tokens/
│   └── appearance.tokens.json   # All visual parameters
├── engine/
│   ├── __init__.py
│   ├── token_resolver.py        # Standalone token loader
│   └── blender_engine.py        # Configuration engine
├── scripts/
│   └── smc_column.py            # Main Blender script
├── output/                      # Generated files (gitignored)
│   ├── *.blend
│   └── *.png
├── _archive/                    # Old script versions
└── README.md
```

## Usage

From the repo root:

```bash
blender --background --python blender/scripts/smc_column.py
```

Output:
- `blender/output/SMC_Column.blend` - Editable Blender file
- `blender/output/SMC_Column_render.png` - 1920x1080 render

## Tuning

Edit `blender/tokens/appearance.tokens.json` to adjust:

| Parameter | Path | Description |
|-----------|------|-------------|
| Funnel height | `smc.geometry.funnel_height` | Height of each level |
| Vase pinch | `smc.curve.pinch_factor` | How much to narrow at middle |
| Colors | `color.fallback_srgb.*` | RGBA palette |
| Emission | `material.emission.*` | Glow intensity by plane |
| Camera distance | `scene.camera.distance` | How far back to view |
| Bloom | `render.bloom.*` | Post-processing glow |

## Architecture

```
appearance.tokens.json → TokenResolver → BlenderEngine → smc_column.py → Blender API
```

Zero hardcoded values in the script. All parameters flow from tokens.

## Requirements

- Blender 4.x (tested with 4.5.3 LTS)
- No Python dependencies outside Blender
