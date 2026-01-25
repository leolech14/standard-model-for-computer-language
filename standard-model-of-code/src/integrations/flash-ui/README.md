# Flash UI Integration

Bridges [Flash UI](https://ai.studio/apps) (Google AI Studio's rapid UI generator) with PROJECT_elements' OKLCH design token system.

## Architecture

```
Flash UI (Google)              PROJECT_elements
─────────────────              ────────────────
OKLCHColorPicker.tsx    ───►   tokens-bridge.ts    ───►   appearance.tokens.json
     │                              │                          │
     │ Component                    │ TokenBridge              │ Design Tokens
     │ renders                      │ parses OKLCH             │ (OKLCH values)
     ▼                              ▼                          ▼
  User picks color          Bridge resolves tokens        COLOR engine
  (L, C, H sliders)         from semantic path            (color-engine.js)
```

## Features

| Feature | Description |
|---------|-------------|
| **Token Bridge** | Loads `appearance.tokens.json` and provides semantic lookups |
| **OKLCH Picker** | Enhanced color picker with gamut visualization |
| **Semantic Presets** | Tier, Family, Ring, SemanticRole palettes |
| **Accessibility** | Hover/active/disabled state generation |
| **Gamut Mapping** | sRGB boundary visualization and warnings |

## Usage

### 1. Initialize Token Bridge

```typescript
import { initFlashUI } from './integrations/flash-ui';

// At app startup
await initFlashUI('/path/to/appearance.tokens.json');
```

### 2. Use Color Picker

```tsx
import { OKLCHColorPicker, OKLCHPickerStyles } from './integrations/flash-ui';

function MyComponent() {
    const [color, setColor] = useState({ l: 0.7, c: 0.15, h: 250 });

    return (
        <>
            <style>{OKLCHPickerStyles}</style>
            <OKLCHColorPicker
                color={color}
                onChange={setColor}
                showPresets={true}
                presetCategory="tier"
                showAccessibility={true}
                showGamut={true}
            />
        </>
    );
}
```

### 3. Query Tokens Directly

```typescript
import { getTokenBridge, toHex } from './integrations/flash-ui';

const bridge = getTokenBridge();

// Get specific color
const t0Color = bridge.getColor('color.atom.t0-core');
console.log(toHex(t0Color)); // #4a90d9

// Get all tier colors
const tierColors = bridge.getCategory('color.atom');
for (const [key, color] of tierColors) {
    console.log(key, toHex(color));
}
```

### 4. COLOR Engine Compatibility

```typescript
import { FlashUIColorEngine } from './integrations/flash-ui';

// Same API as COLOR.get()
const hex = FlashUIColorEngine.get('tier', 'T0');

// Apply transforms
const transformed = FlashUIColorEngine.transform(
    { l: 0.7, c: 0.15, h: 250 },
    { hueShift: 30, chromaScale: 1.2 }
);
```

## Token Schema

The bridge expects tokens in PROJECT_elements format:

```json
{
    "$schema": "design-tokens",
    "color": {
        "atom": {
            "t0-core": {
                "$value": "oklch(70.25% 0.1364 236.02)",
                "$description": "Universal atoms - Blue"
            }
        }
    }
}
```

## Semantic Categories

| Category | Description | Keys |
|----------|-------------|------|
| `tier` | Architecture layers | T0, T1, T2, T3 |
| `family` | Functional groups | LOG, DAT, ORG, EXE, EXT |
| `ring` | Architectural zones | DOMAIN, APPLICATION, PRESENTATION |
| `semanticRole` | Purpose classification | utility, orchestrator, hub, leaf |

## OKLCH Type

```typescript
interface OKLCHColor {
    l: number;  // Lightness 0-1
    c: number;  // Chroma 0-0.4
    h: number;  // Hue 0-360
    alpha?: number;
}
```

## Gamut Handling

The picker visualizes the sRGB gamut boundary. Colors outside sRGB:
- Show a red border on the marker
- Display a "!" warning indicator
- Still work in Display P3 capable browsers

```typescript
import { isInGamut } from './tokens-bridge';

if (!isInGamut(color)) {
    console.warn('Color is outside sRGB gamut');
}
```

## Integration with Gemini Prompts

Flash UI uses Gemini to generate UI. The token bridge enables semantic color references:

```typescript
const prompt = `
Build a UI component using these design tokens:
- Primary: ${toOKLCHString(bridge.getColor('color.atom.t0-core'))}
- Accent: ${toOKLCHString(bridge.getColor('color.highlight.selected'))}
- Background: oklch(16.56% 0.0132 248.65 / 0.85)

Use OKLCH for all colors. Apply ${animSpeed}x animation speed.
`;
```

## Files

| File | Purpose |
|------|---------|
| `tokens-bridge.ts` | Token parsing, OKLCH utilities, bridge class |
| `OKLCHColorPicker.tsx` | React component with presets |
| `index.ts` | Public API exports |

## Related

- `schema/viz/tokens/appearance.tokens.json` - Design token source
- `src/core/viz/assets/modules/color-engine.js` - COLOR engine
- `src/core/viz/assets/modules/color-telemetry.js` - Observability
- `.agent/tools/oklch_color.py` - Python OKLCH mapper
