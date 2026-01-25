/**
 * =============================================================================
 * UPB-DEFAULTS - Default binding configuration for Collider visualization
 * =============================================================================
 *
 * Maps VIS_STATE selector values to entity fields via UPB binding system.
 * Uses LEGACY VIS_STATE keys: colorBy, sizeBy, edgeBy (not colorPreset/sizeMode)
 *
 * BINDING TYPES:
 *   - Constant: 4, 0.8, true, '#ff00aa'
 *   - Path string: 'tier_color', 'metrics.fanout'
 *   - Selected mapping: { by: 'colorBy', map: {...}, default: '...' }
 *
 * @module UPB_DEFAULTS
 * @version 1.0.0
 */

const DEFAULT_UPB = {
    node: {
        // COLOR: Maps colorBy (legacy VIS_STATE key) to entity field
        color: {
            by: 'colorBy',
            map: {
                tier:     'tier_color',      // node.tier_color (pre-computed by Color module)
                family:   'family_color',
                layer:    'layer_color',
                ring:     'ring_color',
                file:     'file_color',
                flow:     'flow_color',
                role:     'role_color',
                atom:     'atom_color',
                // Interval modes (continuous gradients)
                complexity: 'complexity_color',
                fan_in:     'fanin_color',
                fan_out:    'fanout_color',
                centrality: 'centrality_color',
                trust:      'trust_color'
            },
            default: 'tier_color'
        },

        // SIZE: Maps sizeBy (legacy VIS_STATE key) to entity field
        size: {
            by: 'sizeBy',
            map: {
                uniform:    4,              // Constant size
                degree:     'degree',       // node.degree (in + out)
                fanout:     'fanout',       // node.fanout (out_degree)
                fanin:      'fanin',        // node.fanin (in_degree)
                complexity: 'elevation',    // node.elevation (complexity metric)
                loc:        'loc_scaled',   // Lines of code, scaled
                pagerank:   'pagerank_scaled'
            },
            default: 4
        },

        // LABEL: Maps viewMode to label field
        label: {
            by: 'viewMode',
            map: {
                atoms: 'label',
                files: 'file_path'
            },
            default: 'label'
        },

        // VISIBLE: Always true by default (can be overridden)
        visible: true
    },

    edge: {
        // WIDTH: Maps edgeStyle to width values
        width: {
            by: 'edgeStyle',
            map: {
                solid:    1.0,
                dashed:   1.0,
                particle: 0.5
            },
            default: 1.0
        },

        // COLOR: Maps edgeBy (legacy VIS_STATE key) to edge field
        color: {
            by: 'edgeBy',
            map: {
                type:       'edge_color',
                resolution: 'resolution_color',
                weight:     'weight_color',
                gradient:   'gradient_color'
            },
            default: 'edge_color'
        },

        // VISIBLE: Always true by default
        visible: true
    }
};

// =============================================================================
// HELPERS
// =============================================================================

/**
 * Merge custom bindings with defaults
 * @param {Object} customBindings - User-provided bindings
 * @returns {Object} Merged UPB configuration
 */
function mergeUPB(customBindings = {}) {
    return {
        node: { ...DEFAULT_UPB.node, ...customBindings.node },
        edge: { ...DEFAULT_UPB.edge, ...customBindings.edge }
    };
}

/**
 * Add a binding dynamically
 * @param {Object} upb - UPB configuration object
 * @param {string} kind - 'node' or 'edge'
 * @param {string} channel - Property channel
 * @param {*} binding - Binding definition
 */
function addBinding(upb, kind, channel, binding) {
    if (!upb[kind]) upb[kind] = {};
    upb[kind][channel] = binding;
    return upb;
}

// =============================================================================
// WINDOW EXPORT
// =============================================================================

if (typeof window !== 'undefined') {
    window.DEFAULT_UPB = DEFAULT_UPB;
    window.mergeUPB = mergeUPB;
    window.addBinding = addBinding;
}

console.log('[Module] UPB_DEFAULTS loaded - default binding configuration');
