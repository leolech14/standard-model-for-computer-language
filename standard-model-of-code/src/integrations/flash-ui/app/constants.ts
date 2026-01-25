/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * Flash UI Constants - PROJECT_elements Integration
 */

import { SEMANTIC_PRESETS } from '../tokens-bridge';

// Original placeholders + PROJECT_elements specific
export const INITIAL_PLACEHOLDERS = [
    "Design a minimalist weather card",
    "Show me a live stock ticker",
    "Create a futuristic login form",
    "Build a stock portfolio dashboard",
    "Make a brutalist music player",
    "Generate a sleek pricing table",
    // PROJECT_elements specific
    "3D code topology visualization panel",
    "OKLCH color picker with gamut boundary",
    "Atom classification card with tier colors",
    "Collider analysis dashboard",
    "Graph metrics HUD overlay",
    "Ask for anything"
];

// Easing options (from appearance.tokens.json animation section)
export const EASING_OPTIONS = [
    { label: 'Standard', value: 'cubic-bezier(0.16, 1, 0.3, 1)' },
    { label: 'Smooth Ease', value: 'ease-in-out' },
    { label: 'Linear', value: 'linear' },
    { label: 'Sharp Out', value: 'cubic-bezier(0.4, 0, 0.2, 1)' },
    { label: 'Anticipate', value: 'cubic-bezier(0.34, 1.56, 0.64, 1)' },
    // Physics-inspired (from appearance.tokens.json hue.damping)
    { label: 'Orbital', value: 'cubic-bezier(0.1, 0.7, 0.6, 1)' },
    { label: 'Elastic', value: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)' }
];

// Re-export semantic presets for easy access
export { SEMANTIC_PRESETS };

// Default brand colors by category (from appearance.tokens.json)
export const DEFAULT_BRAND_COLORS = {
    tier: { l: 0.70, c: 0.136, h: 236 },      // T0 Blue
    family: { l: 0.88, c: 0.149, h: 201 },    // LOG Cyan
    ring: { l: 0.83, c: 0.171, h: 81 },       // DOMAIN Gold
    highlight: { l: 0.90, c: 0.20, h: 60 }    // Selected Yellow
};

// Animation parameters (from appearance.tokens.json)
export const ANIMATION_DEFAULTS = {
    hue: {
        speed: 0.0008,
        damping: 0.9995,
        rotation: 0.8
    },
    chroma: {
        damping: 0.998,
        gravity: 0.0004,
        center: 0.32,
        amplitude: 0.08
    },
    lightness: {
        speed: 0.02,
        center: 82,
        amplitude: 10
    }
};

// Flow presets (from appearance.tokens.json)
export const FLOW_PRESETS = {
    ember: {
        highlightColor: '#ff8c00',
        particleColor: '#ffaa00',
        dimColor: '#331100',
        edgeColor: '#ff6600'
    },
    ocean: {
        highlightColor: '#00d4ff',
        particleColor: '#4df0ff',
        dimColor: '#001122',
        edgeColor: '#0088cc'
    },
    plasma: {
        highlightColor: '#ff00ff',
        particleColor: '#ff66ff',
        dimColor: '#110011',
        edgeColor: '#cc00cc'
    },
    matrix: {
        highlightColor: '#00ff00',
        particleColor: '#88ff88',
        dimColor: '#001100',
        edgeColor: '#00cc00'
    }
};
