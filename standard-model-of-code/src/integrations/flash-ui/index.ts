/**
 * FLASH UI INTEGRATION
 *
 * Bridges Flash UI (Google AI Studio app) with PROJECT_elements
 * OKLCH design token system and COLOR engine.
 *
 * @license Apache-2.0
 */

// Token Bridge - loads and manages design tokens
export {
    TokenBridge,
    getTokenBridge,
    initTokenBridge,
    parseOKLCH,
    toOKLCHString,
    toHex,
    SEMANTIC_PRESETS,
    generateStates,
    getAccessibleTextColor,
    estimateContrast
} from './tokens-bridge';

export type {
    OKLCHColor,
    OKLCHColorWithMeta,
    SemanticCategory
} from './tokens-bridge';

// Color Picker Component
export { default as OKLCHColorPicker, OKLCHPickerStyles } from './OKLCHColorPicker';

// =============================================================================
// QUICK START
// =============================================================================

/**
 * Initialize Flash UI with PROJECT_elements tokens
 *
 * @example
 * ```typescript
 * import { initFlashUI, OKLCHColorPicker } from './integrations/flash-ui';
 *
 * // Initialize once at app start
 * await initFlashUI();
 *
 * // Use in components
 * <OKLCHColorPicker
 *   color={{ l: 0.7, c: 0.15, h: 250 }}
 *   onChange={(color) => console.log(color)}
 *   showPresets={true}
 * />
 * ```
 */
export async function initFlashUI(tokensPath?: string): Promise<void> {
    const { initTokenBridge } = await import('./tokens-bridge');

    // Default to the appearance.tokens.json in the schema
    const path = tokensPath || '/schema/viz/tokens/appearance.tokens.json';

    try {
        await initTokenBridge(path);
        console.log('[Flash UI] Token bridge initialized');
    } catch (e) {
        console.warn('[Flash UI] Could not load tokens from', path, e);
    }
}

// =============================================================================
// COLOR ENGINE COMPATIBILITY LAYER
// =============================================================================

/**
 * Provides COLOR engine-compatible API for Flash UI
 *
 * Maps Flash UI color operations to PROJECT_elements COLOR engine patterns.
 */
export const FlashUIColorEngine = {
    /**
     * Get color by semantic category (mirrors COLOR.get)
     */
    get: (category: string, key: string) => {
        const bridge = getTokenBridge();
        const color = bridge.getColor(`color.${category}.${key}`);
        return color ? toHex(color) : '#808080';
    },

    /**
     * Get OKLCH color object
     */
    getOKLCH: (category: string, key: string) => {
        const bridge = getTokenBridge();
        return bridge.getColor(`color.${category}.${key}`);
    },

    /**
     * Get all colors in a category
     */
    getCategory: (category: string) => {
        const bridge = getTokenBridge();
        return bridge.getCategory(`color.${category}`);
    },

    /**
     * Apply global transform (mirrors COLOR.setTransform)
     */
    transform: (
        color: { l: number; c: number; h: number },
        opts: { hueShift?: number; chromaScale?: number; lightnessShift?: number }
    ) => {
        const bridge = getTokenBridge();
        return bridge.applyTransform(color, opts);
    }
};

// Re-export for convenience
import { getTokenBridge, toHex } from './tokens-bridge';
