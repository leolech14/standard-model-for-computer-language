/**
 * =============================================================================
 * PROPERTY-QUERY-INIT - Initialize and wire property query into renderer
 * =============================================================================
 *
 * This module:
 * 1. Creates the property query instance (Q)
 * 2. Provides bumpRender() for cache invalidation
 * 3. Exposes debug commands
 *
 * @module PROPERTY_QUERY_INIT
 * @version 1.0.0
 *
 * ## Usage (in app.js after Graph is created)
 * ```javascript
 * import { initPropertyQuery, bumpRender } from './modules/property-query-init.js';
 *
 * const Q = initPropertyQuery();
 *
 * Graph
 *   .nodeColor(n => Q.node(n, 'color'))
 *   .nodeVal(n => Q.node(n, 'size'))
 *   .linkWidth(e => Q.edge(e, 'width'));
 * ```
 */

// Dependencies loaded via script order:
// - createPropertyQuery (from property-query.js)
// - DEFAULT_VIS_SCHEMA (from vis-schema.js)
// - DEFAULT_UPB (from upb-defaults.js)

// =============================================================================
// VIS_STATE EXTENSION
// =============================================================================

/**
 * Ensure VIS_STATE has required structure for property query
 */
function ensureVisStateStructure() {
    if (typeof window === 'undefined') return;

    window.VIS_STATE = window.VIS_STATE || {};
    const state = window.VIS_STATE;

    // Epoch for cache invalidation
    if (state._epoch === undefined) {
        state._epoch = 0;
    }

    // Explicit override bag
    if (!state.overrides) {
        state.overrides = {
            node: {},
            edge: {}
        };
    }

    // Selector state defaults - use LEGACY VIS_STATE keys (colorBy/sizeBy/edgeBy)
    // These match what vis-state.js actually sets
    if (state.colorBy === undefined) state.colorBy = 'tier';
    if (state.sizeBy === undefined) state.sizeBy = 'uniform';
    if (state.edgeBy === undefined) state.edgeBy = 'type';

    // Compatibility aliases (in case any code still uses old names)
    if (state.colorPreset === undefined && state.colorBy !== undefined) state.colorPreset = state.colorBy;
    if (state.sizeMode === undefined && state.sizeBy !== undefined) state.sizeMode = state.sizeBy;
    if (state.edgeColorMode === undefined && state.edgeBy !== undefined) state.edgeColorMode = state.edgeBy;

    // Scale multipliers
    if (state.nodeSizeScale === undefined) state.nodeSizeScale = 1.0;
    if (state.edgeWidthScale === undefined) state.edgeWidthScale = 1.0;

    // Direct slider values (these are overrides)
    // nodeOpacity, edgeOpacity, edgeCurvature, edgeWidth are set by sliders

    return state;
}

// =============================================================================
// UPB INITIALIZATION
// =============================================================================

/**
 * Initialize UPB with defaults, allowing custom overrides
 */
function ensureUPB(customBindings = {}) {
    if (typeof window === 'undefined') return DEFAULT_UPB;

    if (!window.UPB_CONFIG) {
        window.UPB_CONFIG = {
            node: { ...DEFAULT_UPB.node, ...customBindings.node },
            edge: { ...DEFAULT_UPB.edge, ...customBindings.edge }
        };
    }

    return window.UPB_CONFIG;
}

// =============================================================================
// PROPERTY QUERY INSTANCE
// =============================================================================

let _queryInstance = null;

/**
 * Initialize the property query system.
 * Call this once after DOM is ready.
 *
 * @param {Object} options
 * @param {Object} options.customBindings - Custom UPB bindings to merge
 * @param {Object} options.customSchema - Custom schema to merge
 * @returns {Object} Property query interface { node, edge, explainNode, explainEdge }
 */
function initPropertyQuery({ customBindings = {}, customSchema = {} } = {}) {
    ensureVisStateStructure();
    ensureUPB(customBindings);

    const schema = {
        node: { ...DEFAULT_VIS_SCHEMA.node, ...customSchema.node },
        edge: { ...DEFAULT_VIS_SCHEMA.edge, ...customSchema.edge }
    };

    _queryInstance = createPropertyQuery({
        schema,
        getUPB: () => window.UPB_CONFIG || DEFAULT_UPB,
        getVisState: () => window.VIS_STATE || {}
    });

    // Expose globally for debugging
    window.Q = _queryInstance;

    console.log('[PROPERTY_QUERY_INIT] Initialized. Use Q.node(n, "color"), Q.explainNode(n, "color")');

    return _queryInstance;
}

/**
 * Get the property query instance (must call initPropertyQuery first)
 */
function getPropertyQuery() {
    if (!_queryInstance) {
        console.warn('[PROPERTY_QUERY_INIT] Not initialized. Call initPropertyQuery() first.');
        return null;
    }
    return _queryInstance;
}

// =============================================================================
// CACHE INVALIDATION
// =============================================================================

/**
 * Register a custom refresh function to be called on epoch bump.
 * This allows the renderer to control exactly how refresh happens.
 * @param {Function} fn - Refresh function
 */
function registerRenderRefresh(fn) {
    if (typeof window !== 'undefined') {
        window.__PQ_REFRESH__ = fn;
    }
}

/**
 * Bump the epoch and trigger graph refresh.
 * Call this after ANY UI control changes state.
 */
function bumpRender() {
    if (typeof window === 'undefined') return;

    // Increment epoch
    window.VIS_STATE = window.VIS_STATE || {};
    window.VIS_STATE._epoch = (window.VIS_STATE._epoch ?? 0) + 1;

    // Use registered refresh hook if available
    if (typeof window.__PQ_REFRESH__ === 'function') {
        window.__PQ_REFRESH__();
        return;
    }

    // Fallback: direct Graph refresh
    const Graph = window.Graph;
    if (Graph) {
        if (typeof Graph.refresh === 'function') {
            Graph.refresh();
        } else {
            // Fallback: re-set an accessor to force refresh
            const nc = Graph.nodeColor();
            if (nc) Graph.nodeColor(nc);
        }
    }
}

// =============================================================================
// EXPLICIT OVERRIDE HELPERS
// =============================================================================

/**
 * Set an explicit override for a node channel
 * @param {string} channel - 'color', 'size', 'opacity', etc.
 * @param {*} value - Override value (or undefined to clear)
 */
function setNodeOverride(channel, value) {
    ensureVisStateStructure();
    if (value === undefined) {
        delete window.VIS_STATE.overrides.node[channel];
    } else {
        window.VIS_STATE.overrides.node[channel] = value;
    }
    bumpRender();
}

/**
 * Set an explicit override for an edge channel
 * @param {string} channel - 'color', 'width', 'opacity', etc.
 * @param {*} value - Override value (or undefined to clear)
 */
function setEdgeOverride(channel, value) {
    ensureVisStateStructure();
    if (value === undefined) {
        delete window.VIS_STATE.overrides.edge[channel];
    } else {
        window.VIS_STATE.overrides.edge[channel] = value;
    }
    bumpRender();
}

/**
 * Clear all explicit overrides
 */
function clearOverrides() {
    ensureVisStateStructure();
    window.VIS_STATE.overrides = { node: {}, edge: {} };
    bumpRender();
}

// =============================================================================
// DEBUG COMMANDS
// =============================================================================

/**
 * Debug: Print resolution trace for a node
 */
function debugNode(node, channels = ['color', 'size', 'opacity', 'label']) {
    if (!_queryInstance) {
        console.warn('[DEBUG] Property query not initialized');
        return;
    }

    console.group('[DEBUG] Node Resolution');
    console.log('Node:', node.id || node.label || node);

    for (const channel of channels) {
        const result = _queryInstance.explainNode(node, channel);
        console.log(`  ${channel}:`, result.value);
        console.log(`    Steps:`, result.steps);
    }

    console.groupEnd();
}

/**
 * Debug: Print resolution trace for an edge
 */
function debugEdge(edge, channels = ['color', 'width', 'opacity']) {
    if (!_queryInstance) {
        console.warn('[DEBUG] Property query not initialized');
        return;
    }

    console.group('[DEBUG] Edge Resolution');
    console.log('Edge:', edge.source, '->', edge.target);

    for (const channel of channels) {
        const result = _queryInstance.explainEdge(edge, channel);
        console.log(`  ${channel}:`, result.value);
        console.log(`    Steps:`, result.steps);
    }

    console.groupEnd();
}

// =============================================================================
// WINDOW EXPORTS
// =============================================================================

if (typeof window !== 'undefined') {
    window.initPropertyQuery = initPropertyQuery;
    window.getPropertyQuery = getPropertyQuery;
    window.registerRenderRefresh = registerRenderRefresh;
    window.bumpRender = bumpRender;
    window.setNodeOverride = setNodeOverride;
    window.setEdgeOverride = setEdgeOverride;
    window.clearOverrides = clearOverrides;
    window.debugNode = debugNode;
    window.debugEdge = debugEdge;
}

// =============================================================================
// DEBUG HOTKEY: Ctrl+X or Cmd+X to debug selected node
// =============================================================================

if (typeof document !== 'undefined') {
    document.addEventListener('keydown', (e) => {
        // Ctrl+X or Cmd+X: Debug selected node
        if (e.key.toLowerCase() === 'x' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            const node = window.SELECTED_NODE || window.__selectedNode;
            if (!node) {
                console.warn('[PQ] No selected node. Click a node first.');
                return;
            }
            debugNode(node, ['color', 'size', 'opacity', 'label']);
        }

        // Ctrl+Shift+X: Debug selected edge
        if (e.key.toLowerCase() === 'x' && (e.ctrlKey || e.metaKey) && e.shiftKey) {
            e.preventDefault();
            const edge = window.SELECTED_EDGE || window.__selectedEdge;
            if (!edge) {
                console.warn('[PQ] No selected edge.');
                return;
            }
            debugEdge(edge, ['color', 'width', 'opacity']);
        }
    });
}

console.log('[Module] PROPERTY_QUERY_INIT loaded - call initPropertyQuery() to start');
console.log('[Module] Debug hotkey: Ctrl+X (node), Ctrl+Shift+X (edge)');
