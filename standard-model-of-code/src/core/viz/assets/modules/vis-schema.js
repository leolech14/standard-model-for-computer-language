/**
 * =============================================================================
 * VIS-SCHEMA - Default values and type coercion for visual channels
 * =============================================================================
 *
 * Provides schema definitions for all visual channels with:
 * - Type information (color, number, boolean, string)
 * - Default values
 * - Validation constraints (min, max)
 *
 * @module VIS_SCHEMA
 * @version 1.0.0
 */

const DEFAULT_VIS_SCHEMA = {
    node: {
        color:      { type: 'color',   default: '#9aa0a6' },
        size:       { type: 'number',  default: 4,    min: 0.5, max: 50 },
        opacity:    { type: 'number',  default: 1.0,  min: 0,   max: 1 },
        label:      { type: 'string',  default: '' },
        visible:    { type: 'boolean', default: true },
        // Extended channels
        hue:        { type: 'number',  default: 220,  min: 0,   max: 360 },
        saturation: { type: 'number',  default: 0.6,  min: 0,   max: 1 },
        lightness:  { type: 'number',  default: 0.65, min: 0,   max: 1 }
    },
    edge: {
        color:      { type: 'color',   default: '#9aa0a6' },
        width:      { type: 'number',  default: 1,    min: 0,   max: 10 },
        opacity:    { type: 'number',  default: 0.6,  min: 0,   max: 1 },
        curvature:  { type: 'number',  default: 0.2,  min: 0,   max: 2 },
        visible:    { type: 'boolean', default: true }
    }
};

// Export for both ES modules and window
if (typeof window !== 'undefined') {
    window.DEFAULT_VIS_SCHEMA = DEFAULT_VIS_SCHEMA;
}

console.log('[Module] VIS_SCHEMA loaded - visual channel defaults');
