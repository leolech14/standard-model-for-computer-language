const UPB_BINDINGS = (function () {
    'use strict';

    /**
     * UNIVERSAL PROPERTY BINDER - BINDINGS GRAPH MODULE
     * Core engine for Many-to-Many property binding.
     * 
     * Dependencies: UPB_SCALES, UPB_ENDPOINTS
     */

    // =========================================================================
    // CLASS: BINDING
    // A single connection between a Data Source and a Visual Target
    // =========================================================================
    function Binding(source, target, options) {
        options = options || {};

        this.id = options.id || Math.random().toString(36).substr(2, 9);
        this.source = source;      // e.g., 'token_estimate'
        this.target = target;      // e.g., 'nodeSize'
        this.scale = options.scale || 'linear';
        this.weight = options.weight !== undefined ? options.weight : 1.0;
        this.range = options.range || null; // Override target default range

        // Metadata
        this.active = true;
    }

    Binding.prototype.apply = function (node, sourceValue, dataMin, dataMax) {
        if (!this.active) return null;

        // 1. Normalize
        const SCALES = window.UPB_SCALES;
        if (!SCALES) {
            console.error('[UPB] UPB_SCALES not found');
            return 0;
        }

        // Get domain for discrete scales if needed
        const ENDPOINTS = window.UPB_ENDPOINTS;
        const sourceDef = ENDPOINTS ? ENDPOINTS.getSource(this.source) : null;
        const domain = sourceDef ? sourceDef.values : null;

        const normalized = SCALES.applyScale(this.scale, sourceValue, dataMin, dataMax, domain);

        // 2. Map to Target Range
        const targetDef = ENDPOINTS ? ENDPOINTS.getTarget(this.target) : null;

        // Use binding override range, or target default, or fallback [0,1]
        const range = this.range || (targetDef ? targetDef.range : [0, 1]);

        // Interpolate
        return range[0] + normalized * (range[1] - range[0]);
    };


    // =========================================================================
    // CLASS: BINDING GRAPH
    // Manages all active bindings and evaluates them against nodes
    // =========================================================================
    function BindingGraph() {
        this._bindings = {}; // target_key -> [Binding, Binding, ...]
        this._dataRanges = {}; // source_key -> {min, max} cache
    }

    BindingGraph.prototype.bind = function (source, target, options) {
        if (!this._bindings[target]) {
            this._bindings[target] = [];
        }

        // Check for exclusivity (replace existing if 1:1 implied, or add if N:1 supported)
        // For now, simple append. Blending logic handles the rest.
        const binding = new Binding(source, target, options);
        this._bindings[target].push(binding);

        console.log(`[UPB] Bound ${source} -> ${target} (${options?.scale || 'linear'})`);
        return binding;
    };

    BindingGraph.prototype.unbind = function (source, target) {
        if (!this._bindings[target]) return;

        if (source === '*') {
            // Unbind all for this target
            delete this._bindings[target];
        } else {
            // Remove specific binding
            this._bindings[target] = this._bindings[target].filter(b => b.source !== source);
            if (this._bindings[target].length === 0) {
                delete this._bindings[target];
            }
        }
    };

    BindingGraph.prototype.clear = function () {
        this._bindings = {};
        this._dataRanges = {};
    };

    BindingGraph.prototype.getBindingsFor = function (target) {
        return this._bindings[target] || [];
    };

    /**
     * Set data ranges explicitly (usually calculated by data-manager)
     */
    BindingGraph.prototype.setDataRanges = function (ranges) {
        this._dataRanges = ranges || {};
    };

    /**
     * Evaluate all bindings for a single node
     * Returns: { nodeSize: 12.5, hue: 200, ... }
     */
    BindingGraph.prototype.evaluate = function (node) {
        const result = {};
        const targets = Object.keys(this._bindings);

        for (let i = 0; i < targets.length; i++) {
            const targetKey = targets[i];
            const bindings = this._bindings[targetKey];

            if (!bindings || bindings.length === 0) continue;

            const values = [];
            const weights = [];

            // Calculate contribution from each binding
            for (let j = 0; j < bindings.length; j++) {
                const binding = bindings[j];
                const sourceKey = binding.source;

                // Get safe value
                const val = this._getNodeValue(node, sourceKey);
                if (val === null || val === undefined) continue;

                // Get range
                const range = this._dataRanges[sourceKey] || { min: 0, max: 100 };

                const calculated = binding.apply(node, val, range.min, range.max);
                values.push(calculated);
                weights.push(binding.weight);
            }

            // BLEND using UPB_BLENDERS (Phase 6: Robustness)
            if (values.length > 0) {
                // Get target definition for blend mode and minOutput
                const ENDPOINTS = window.UPB_ENDPOINTS;
                const targetDef = ENDPOINTS ? ENDPOINTS.getTarget(targetKey) : null;
                const blendMode = targetDef?.blendMode || 'replace';
                const minOutput = targetDef?.minOutput;

                // Apply blending
                const BLENDERS = window.UPB_BLENDERS;
                let finalValue;
                if (BLENDERS && typeof BLENDERS.blend === 'function') {
                    finalValue = BLENDERS.blend(blendMode, values, weights);
                } else {
                    // Fallback: last wins
                    finalValue = values[values.length - 1];
                }

                // Apply minOutput clamping
                if (minOutput !== undefined && finalValue < minOutput) {
                    finalValue = minOutput;
                }

                result[targetKey] = finalValue;
            }
        }
        return result;
    };

    BindingGraph.prototype.evaluateAll = function (nodes) {
        return nodes.map(n => ({
            id: n.id,
            visuals: this.evaluate(n)
        }));
    };

    // Helper to traverse node properties safely
    BindingGraph.prototype._getNodeValue = function (node, key) {
        if (node[key] !== undefined) return node[key];
        if (node.dimensions && node.dimensions[key] !== undefined) return node.dimensions[key];

        // Dimension alias map
        const aliases = {
            'tier': 'D1_TIER',
            'ring': 'D2_RING',
            'layer': 'D2_LAYER',
            'effect': 'D6_EFFECT'
        };
        if (aliases[key] && node.dimensions) return node.dimensions[aliases[key]];

        return null;
    };

    // Default singleton instance
    const defaultGraph = new BindingGraph();

    // =========================================================================
    // PRESET BINDINGS (T8-T9)
    // Recommended mappings for tree-sitter analysis data
    // =========================================================================
    const PRESETS = {
        // T8: Purity → Lightness (pure code appears brighter)
        'purity-lightness': {
            source: 'D6_pure_score',
            target: 'lightness',
            scale: 'linear',
            range: [30, 90],  // 30% dark (impure) to 90% bright (pure)
            description: 'Pure code appears brighter'
        },

        // T9: PageRank → Node Size (influential nodes are larger)
        'pagerank-size': {
            source: 'pagerank',
            target: 'nodeSize',
            scale: 'sqrt',    // Compress outliers
            range: [3, 25],
            description: 'Influential nodes appear larger'
        },

        // Bonus: Betweenness → Saturation (bridge nodes are more vivid)
        'betweenness-saturation': {
            source: 'betweenness_centrality',
            target: 'saturation',
            scale: 'sqrt',
            range: [20, 100],
            description: 'Bridge nodes appear more vivid'
        },

        // Bonus: Topology Role → Hue (different roles, different colors)
        'topology-hue': {
            source: 'topology_role',
            target: 'hue',
            scale: 'discrete',
            // orphan=red, root=green, leaf=blue, hub=purple, internal=gray
            range: [0, 360],
            description: 'Topology roles have distinct colors'
        },

        // =====================================================================
        // CONTROL FLOW PRESETS (P3-09)
        // =====================================================================

        // Cyclomatic Complexity → Node Size (complex functions are larger)
        'complexity-size': {
            source: 'cyclomatic_complexity',
            target: 'nodeSize',
            scale: 'sqrt',    // Compress outliers
            range: [3, 30],
            description: 'Complex functions appear larger'
        },

        // Nesting Depth → Saturation (deeply nested = more vivid warning)
        'nesting-saturation': {
            source: 'max_nesting_depth',
            target: 'saturation',
            scale: 'linear',
            range: [20, 100],
            description: 'Deeply nested code appears more vivid'
        },

        // Complexity → Hue (simple=green, complex=red gradient)
        'complexity-hue': {
            source: 'cyclomatic_complexity',
            target: 'hue',
            scale: 'linear',
            range: [120, 0],  // Green (120) → Red (0)
            description: 'Simple=green, Complex=red'
        },

        // =====================================================================
        // RPBL PRESETS (P4-05/07/08) - Theory Character Visualization
        // =====================================================================

        // Responsibility → Size (high responsibility = larger)
        'responsibility-size': {
            source: 'rpbl_responsibility',
            target: 'nodeSize',
            scale: 'linear',
            range: [3, 25],
            description: 'High responsibility nodes appear larger'
        },

        // Purity → Lightness (pure = bright, impure = dark)
        'rpbl-purity-lightness': {
            source: 'rpbl_purity',
            target: 'lightness',
            scale: 'linear',
            range: [30, 90],
            description: 'Pure code appears brighter'
        },

        // Boundary → Saturation (exposed = vivid, internal = muted)
        'boundary-saturation': {
            source: 'rpbl_boundary',
            target: 'saturation',
            scale: 'linear',
            range: [20, 100],
            description: 'Exposed boundaries appear more vivid'
        },

        // Lifecycle → Opacity (stable = solid, transient = faded)
        'lifecycle-opacity': {
            source: 'rpbl_lifecycle',
            target: 'opacity',
            scale: 'linear',
            range: [0.3, 1.0],
            description: 'Long-lived code appears more solid'
        }
    };

    /**
     * Apply a named preset to the default graph
     * @param {string} presetName - Key from PRESETS
     * @returns {Binding|null}
     */
    function applyPreset(presetName) {
        const preset = PRESETS[presetName];
        if (!preset) {
            console.warn(`[UPB] Unknown preset: ${presetName}`);
            return null;
        }
        return defaultGraph.bind(preset.source, preset.target, {
            id: `preset-${presetName}`,
            scale: preset.scale,
            range: preset.range
        });
    }

    /**
     * Apply all presets
     */
    function applyAllPresets() {
        Object.keys(PRESETS).forEach(name => applyPreset(name));
        console.log(`[UPB] Applied ${Object.keys(PRESETS).length} preset bindings`);
    }

    /**
     * List available presets
     */
    function listPresets() {
        return Object.keys(PRESETS).map(name => ({
            name,
            ...PRESETS[name]
        }));
    }

    return {
        Binding,
        BindingGraph,
        defaultGraph,
        PRESETS,
        applyPreset,
        applyAllPresets,
        listPresets
    };

})();

// Export 
if (typeof window !== 'undefined') window.UPB_BINDINGS = UPB_BINDINGS;
if (typeof module !== 'undefined') module.exports = UPB_BINDINGS;
