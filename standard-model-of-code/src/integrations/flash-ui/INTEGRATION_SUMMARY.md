# Flash UI ↔ PROJECT_elements Integration

**Status:** Complete
**Date:** 2026-01-25
**Research:** Perplexity OKLCH Design Token Architecture + Gemini Analysis
**Secrets:** Doppler (project: `ai-tools`, config: `dev`)

## What Was Done

### 1. Token Bridge (`tokens-bridge.ts`)
- Parses OKLCH values from `appearance.tokens.json`
- Provides `TokenBridge` class with dot-notation lookups
- Exports `toOKLCHString()`, `toHex()`, `parseOKLCH()` utilities
- Includes `SEMANTIC_PRESETS` from design tokens
- Gamut mapping and accessibility utilities

### 2. Enhanced Color Picker (`OKLCHColorPicker.tsx`)
- Integrated with semantic presets (tier, family, ring, semanticRole)
- Added Chroma slider (missing from original)
- State preview (default, hover, active, disabled)
- Hex fallback display
- Accessible text color computation

### 3. Updated App Constants (`constants.ts`)
- Added PROJECT_elements-specific prompts
- Imported `SEMANTIC_PRESETS` from bridge
- Added `DEFAULT_BRAND_COLORS` from tokens
- Added `ANIMATION_DEFAULTS` from tokens
- Added `FLOW_PRESETS` from tokens

### 4. Type Integration (`types.ts`)
- Re-exports `OKLCHColor` from token bridge
- Added `SemanticCategory` type
- Added `DesignSystemConfig` interface

### 5. CSS Extensions (`index.css`)
- Preset tabs and grid styles
- State swatch preview
- Enhanced slider styling

## File Structure

```
src/integrations/flash-ui/
├── index.ts              # Public API exports
├── tokens-bridge.ts      # Token loading and OKLCH utilities
├── OKLCHColorPicker.tsx  # Standalone picker component
├── README.md             # Usage documentation
├── INTEGRATION_SUMMARY.md
└── app/                  # Full Flash UI app with Gemini engine
    ├── index.tsx         # Main app + Copycat Protocol + OKLCH prompts
    ├── types.ts          # Updated with bridge types
    ├── constants.ts      # Updated with presets
    ├── index.css         # Extended styles
    ├── package.json      # Doppler-enabled scripts
    └── components/
        └── OKLCHColorPicker.tsx  # Integrated picker
```

## Usage

### Quick Start
```typescript
import { initFlashUI, OKLCHColorPicker } from './integrations/flash-ui';

// Initialize tokens
await initFlashUI('/schema/viz/tokens/appearance.tokens.json');

// Use in React
<OKLCHColorPicker
    color={{ l: 0.7, c: 0.15, h: 250 }}
    onChange={setColor}
    showPresets={true}
    presetCategory="tier"
/>
```

### Direct Token Access
```typescript
import { getTokenBridge, toHex } from './integrations/flash-ui';

const bridge = getTokenBridge();
const t0Color = bridge.getColor('color.atom.t0-core');
console.log(toHex(t0Color)); // #4a90d9
```

### COLOR Engine Compatibility
```typescript
import { FlashUIColorEngine } from './integrations/flash-ui';

// Same API as color-engine.js COLOR.get()
const hex = FlashUIColorEngine.get('tier', 'T0');
```

## Token Mapping

| Flash UI Prop | TOKEN Path | Description |
|---------------|------------|-------------|
| `brandColor.l` | `color.atom.t0-core` → L | Lightness 0-1 |
| `brandColor.c` | `color.atom.t0-core` → C | Chroma 0-0.4 |
| `brandColor.h` | `color.atom.t0-core` → H | Hue 0-360 |
| `animSpeed` | `animation.hue.speed` | Animation multiplier |
| `animEasing` | Custom | Cubic-bezier string |

## Semantic Presets

From `appearance.tokens.json`:

| Category | Keys |
|----------|------|
| `tier` | T0, T1, T2, T3 |
| `family` | LOG, DAT, ORG, EXE, EXT |
| `ring` | DOMAIN, APPLICATION, PRESENTATION, INTERFACE |
| `semanticRole` | utility, orchestrator, hub, leaf |

## Research Sources

1. **Perplexity Research** (auto-saved):
   - `docs/research/perplexity/docs/20260125_051349_oklch_design_token_system_architecture_2025_2026.md`

2. **Gemini Analysis** (auto-saved):
   - `docs/research/gemini/docs/20260125_051453_what_is_the_complete_oklch_color_system_architectu.md`

## Dependencies

The Flash UI app requires:
```json
{
    "@google/genai": "^0.7.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
}
```

## Next Steps

1. **Setup Doppler**: `doppler setup --project ai-tools --config dev`
2. **Run the app**: `cd app && npm install && npm run dev`
3. **Test Copycat**: Upload an image and click "Copycat" for pixel-perfect replication
4. **Verify gamut**: Check Display P3 colors on wide-gamut displays

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Development with Doppler secrets |
| `npm run dev:local` | Development with .env.local fallback |
| `npm run build` | Production build with Doppler |
