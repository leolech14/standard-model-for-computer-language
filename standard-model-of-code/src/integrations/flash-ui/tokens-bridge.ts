/**
 * TOKENS BRIDGE - Flash UI ↔ PROJECT_elements Design Token Integration
 *
 * Loads OKLCH design tokens from appearance.tokens.json and provides
 * a unified API compatible with both Flash UI and the COLOR engine.
 *
 * @license Apache-2.0
 * @see standard-model-of-code/schema/viz/tokens/appearance.tokens.json
 */

// =============================================================================
// OKLCH TYPE DEFINITIONS (Compatible with PROJECT_elements)
// =============================================================================

export interface OKLCHColor {
    l: number;  // Lightness 0-1 (stored as 0-100% in tokens)
    c: number;  // Chroma 0-0.4 (typically)
    h: number;  // Hue 0-360
    alpha?: number;
}

export interface OKLCHColorWithMeta extends OKLCHColor {
    label?: string;
    semantic?: string;
    cssString: string;
}

// Design token structure from appearance.tokens.json
interface DesignToken {
    $value: string | number | boolean;
    $description?: string;
    $options?: (string | number | boolean)[];
}

interface TokenCategory {
    [key: string]: DesignToken | TokenCategory;
}

// =============================================================================
// TOKEN CATEGORIES (Mapped from appearance.tokens.json)
// =============================================================================

export type SemanticCategory =
    | 'atom'
    | 'atom-family'
    | 'ring'
    | 'edge'
    | 'highlight'
    | 'tier'
    | 'family'
    | 'layer'
    | 'roleCategory'
    | 'subsystem'
    | 'phase'
    | 'state'
    | 'effect'
    | 'visibility'
    | 'semanticRole'
    | 'fileType'
    | 'edgeType';

// =============================================================================
// OKLCH PARSING & CONVERSION
// =============================================================================

/**
 * Parse CSS oklch() string to OKLCHColor object
 * Supports formats:
 *   - oklch(70.25% 0.1364 236.02)
 *   - oklch(70.25% 0.1364 236.02 / 0.85)
 */
export function parseOKLCH(cssString: string): OKLCHColor | null {
    const match = cssString.match(
        /oklch\(\s*([\d.]+)%?\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\s*\)/i
    );
    if (!match) return null;

    let l = parseFloat(match[1]);
    // Normalize: if value > 1, assume it's a percentage
    if (l > 1) l = l / 100;

    return {
        l,
        c: parseFloat(match[2]),
        h: parseFloat(match[3]),
        alpha: match[4] ? parseFloat(match[4]) : 1
    };
}

/**
 * Convert OKLCHColor to CSS string
 */
export function toOKLCHString(color: OKLCHColor): string {
    const l = Math.round(color.l * 100);
    const c = color.c.toFixed(4);
    const h = Math.round(color.h * 100) / 100;

    if (color.alpha !== undefined && color.alpha < 1) {
        return `oklch(${l}% ${c} ${h} / ${color.alpha})`;
    }
    return `oklch(${l}% ${c} ${h})`;
}

/**
 * Convert OKLCHColor to sRGB hex (with gamut mapping)
 * Uses the oklab-chroma algorithm for out-of-gamut colors
 */
export function toHex(color: OKLCHColor): string {
    // OKLCH -> OKLab -> Linear RGB -> sRGB -> Hex
    const h_rad = color.h * Math.PI / 180;
    const a = color.c * Math.cos(h_rad);
    const b = color.c * Math.sin(h_rad);

    // OKLab to Linear RGB
    const l_ = color.l + 0.3963377774 * a + 0.2158037573 * b;
    const m_ = color.l - 0.1055613458 * a - 0.0638541728 * b;
    const s_ = color.l - 0.0894841775 * a - 1.2914855480 * b;

    const l3 = l_ * l_ * l_;
    const m3 = m_ * m_ * m_;
    const s3 = s_ * s_ * s_;

    let r = +4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3;
    let g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3;
    let bl = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3;

    // Gamut mapping: clamp to sRGB
    r = Math.max(0, Math.min(1, r));
    g = Math.max(0, Math.min(1, g));
    bl = Math.max(0, Math.min(1, bl));

    // Linear RGB to sRGB gamma
    const toSRGB = (c: number) => c <= 0.0031308
        ? 12.92 * c
        : 1.055 * Math.pow(c, 1/2.4) - 0.055;

    const toHexByte = (c: number) => {
        const val = Math.round(toSRGB(c) * 255);
        return Math.max(0, Math.min(255, val)).toString(16).padStart(2, '0');
    };

    return `#${toHexByte(r)}${toHexByte(g)}${toHexByte(bl)}`;
}

// =============================================================================
// TOKEN BRIDGE CLASS
// =============================================================================

export class TokenBridge {
    private tokens: TokenCategory = {};
    private colorCache = new Map<string, OKLCHColorWithMeta>();

    constructor(tokensData?: TokenCategory) {
        if (tokensData) {
            this.tokens = tokensData;
            this.buildCache();
        }
    }

    /**
     * Load tokens from JSON (fetch or import)
     */
    async loadFromURL(url: string): Promise<void> {
        const response = await fetch(url);
        this.tokens = await response.json();
        this.buildCache();
    }

    /**
     * Load tokens from inline JSON
     */
    loadFromJSON(json: TokenCategory): void {
        this.tokens = json;
        this.buildCache();
    }

    /**
     * Build the color cache for fast lookups
     */
    private buildCache(): void {
        this.colorCache.clear();
        this.walkTokens(this.tokens.color as TokenCategory, 'color');
    }

    private walkTokens(obj: TokenCategory | DesignToken, path: string): void {
        if (!obj) return;

        if ('$value' in obj && typeof obj.$value === 'string') {
            const value = obj.$value as string;
            if (value.startsWith('oklch(')) {
                const parsed = parseOKLCH(value);
                if (parsed) {
                    const desc = (obj as DesignToken).$description || '';
                    this.colorCache.set(path, {
                        ...parsed,
                        label: desc.split(' - ')[0] || path.split('.').pop(),
                        semantic: desc.split(' - ')[1],
                        cssString: value
                    });
                }
            }
        } else if (typeof obj === 'object') {
            for (const [key, val] of Object.entries(obj)) {
                if (key.startsWith('$')) continue;
                this.walkTokens(val as TokenCategory, `${path}.${key}`);
            }
        }
    }

    /**
     * Get a color by semantic path (e.g., "color.atom.t0-core")
     */
    getColor(path: string): OKLCHColorWithMeta | null {
        return this.colorCache.get(path) || null;
    }

    /**
     * Get all colors in a category (e.g., "color.atom")
     */
    getCategory(category: string): Map<string, OKLCHColorWithMeta> {
        const result = new Map<string, OKLCHColorWithMeta>();
        for (const [path, color] of this.colorCache) {
            if (path.startsWith(category + '.')) {
                const key = path.slice(category.length + 1);
                result.set(key, color);
            }
        }
        return result;
    }

    /**
     * Get all semantic categories
     */
    getCategories(): SemanticCategory[] {
        const categories = new Set<string>();
        for (const path of this.colorCache.keys()) {
            const parts = path.split('.');
            if (parts.length >= 2) {
                categories.add(parts[1]);
            }
        }
        return Array.from(categories) as SemanticCategory[];
    }

    /**
     * Create a color scale for a given lightness range
     * Useful for generating accessible variants
     */
    createLightnessScale(
        baseColor: OKLCHColor,
        steps: number = 9,
        minL: number = 0.15,
        maxL: number = 0.95
    ): OKLCHColor[] {
        const scale: OKLCHColor[] = [];
        for (let i = 0; i < steps; i++) {
            const t = i / (steps - 1);
            scale.push({
                l: minL + (maxL - minL) * t,
                c: baseColor.c * (1 - Math.abs(t - 0.5) * 0.5), // Reduce chroma at extremes
                h: baseColor.h
            });
        }
        return scale;
    }

    /**
     * Get animation parameters from tokens
     */
    getAnimationParams(): {
        hue: { speed: number; damping: number; rotation: number };
        chroma: { damping: number; gravity: number; center: number; amplitude: number };
        lightness: { speed: number; center: number; amplitude: number };
    } | null {
        const anim = this.tokens.animation as TokenCategory;
        if (!anim) return null;

        const get = (path: string): number => {
            const parts = path.split('.');
            let obj: any = anim;
            for (const p of parts) {
                obj = obj?.[p];
            }
            return (obj as DesignToken)?.$value as number || 0;
        };

        return {
            hue: {
                speed: get('hue.speed'),
                damping: get('hue.damping'),
                rotation: get('hue.rotation')
            },
            chroma: {
                damping: get('chroma.damping'),
                gravity: get('chroma.gravity'),
                center: get('chroma.center'),
                amplitude: get('chroma.amplitude')
            },
            lightness: {
                speed: get('lightness.speed'),
                center: get('lightness.center'),
                amplitude: get('lightness.amplitude')
            }
        };
    }

    /**
     * Apply transform state (like COLOR engine's transform)
     */
    applyTransform(
        color: OKLCHColor,
        transform: {
            hueShift?: number;
            chromaScale?: number;
            lightnessShift?: number;
        }
    ): OKLCHColor {
        return {
            l: Math.max(0, Math.min(1, color.l + (transform.lightnessShift || 0) / 100)),
            c: Math.max(0, color.c * (transform.chromaScale || 1)),
            h: ((color.h + (transform.hueShift || 0)) % 360 + 360) % 360,
            alpha: color.alpha
        };
    }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

let _bridge: TokenBridge | null = null;

export function getTokenBridge(): TokenBridge {
    if (!_bridge) {
        _bridge = new TokenBridge();
    }
    return _bridge;
}

export async function initTokenBridge(tokensUrl: string): Promise<TokenBridge> {
    const bridge = getTokenBridge();
    await bridge.loadFromURL(tokensUrl);
    return bridge;
}

// =============================================================================
// PRESET SEMANTIC PALETTES (From appearance.tokens.json)
// =============================================================================

export const SEMANTIC_PRESETS = {
    // Tier colors (architecture layers)
    tier: {
        'T0': { l: 0.70, c: 0.136, h: 236, label: 'Universal Core', semantic: 'Blue' },
        'T1': { l: 0.78, c: 0.152, h: 88, label: 'Architectural', semantic: 'Yellow' },
        'T2': { l: 0.55, c: 0.250, h: 310, label: 'Ecosystem', semantic: 'Purple' },
        'T3': { l: 0.56, c: 0.143, h: 39, label: 'Discovered', semantic: 'Orange' }
    },

    // Atom family colors (functional categories)
    family: {
        'LOG': { l: 0.88, c: 0.149, h: 201, label: 'Logic', semantic: 'Cyan' },
        'DAT': { l: 0.88, c: 0.210, h: 157, label: 'Data', semantic: 'Green' },
        'ORG': { l: 0.83, c: 0.171, h: 81, label: 'Organization', semantic: 'Gold' },
        'EXE': { l: 0.64, c: 0.254, h: 15, label: 'Execution', semantic: 'Red' },
        'EXT': { l: 0.53, c: 0.250, h: 301, label: 'External', semantic: 'Purple' }
    },

    // Ring colors (architectural zones)
    ring: {
        'DOMAIN': { l: 0.83, c: 0.171, h: 81, label: 'Domain', semantic: 'Gold' },
        'APPLICATION': { l: 0.88, c: 0.149, h: 201, label: 'Application', semantic: 'Cyan' },
        'PRESENTATION': { l: 0.88, c: 0.210, h: 157, label: 'Presentation', semantic: 'Green' },
        'INTERFACE': { l: 0.70, c: 0.136, h: 236, label: 'Interface', semantic: 'Blue' },
        'INFRASTRUCTURE': { l: 0.64, c: 0.254, h: 15, label: 'Infrastructure', semantic: 'Red' }
    },

    // Semantic role colors (purpose classification)
    semanticRole: {
        'utility': { l: 0.65, c: 0.18, h: 190, label: 'Utility', semantic: 'Cyan - serves many' },
        'orchestrator': { l: 0.60, c: 0.22, h: 280, label: 'Orchestrator', semantic: 'Purple - calls many' },
        'hub': { l: 0.65, c: 0.26, h: 30, label: 'Hub', semantic: 'Orange - critical junction' },
        'leaf': { l: 0.55, c: 0.10, h: 220, label: 'Leaf', semantic: 'Blue-gray - edge node' }
    }
} as const;

// =============================================================================
// ACCESSIBILITY UTILITIES
// =============================================================================

/**
 * Calculate approximate WCAG contrast ratio
 * Based on OKLCH lightness difference (simplified APCA approach)
 */
export function estimateContrast(fg: OKLCHColor, bg: OKLCHColor): number {
    const deltaL = Math.abs(fg.l - bg.l);
    // Simplified: 0.3 lightness diff ≈ 4.5:1 contrast (WCAG AA)
    return deltaL * 15;
}

/**
 * Suggest accessible text color for a background
 */
export function getAccessibleTextColor(bg: OKLCHColor): OKLCHColor {
    // If background is light (L > 0.55), use dark text
    if (bg.l > 0.55) {
        return { l: 0.15, c: 0.02, h: bg.h };
    }
    return { l: 0.95, c: 0.02, h: bg.h };
}

/**
 * Generate hover/active states with OKLCH
 */
export function generateStates(base: OKLCHColor): {
    default: OKLCHColor;
    hover: OKLCHColor;
    active: OKLCHColor;
    disabled: OKLCHColor;
} {
    return {
        default: base,
        hover: { ...base, l: Math.max(0, base.l - 0.10) },
        active: { ...base, l: Math.max(0, base.l - 0.15) },
        disabled: { ...base, c: base.c * 0.3, l: base.l * 0.8 + 0.2 }
    };
}
