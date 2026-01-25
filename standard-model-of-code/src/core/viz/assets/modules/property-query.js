/**
 * =============================================================================
 * PROPERTY-QUERY - Provider-based property resolution for visualization
 * =============================================================================
 *
 * Render-time query system: the renderer asks for "node color", "node size",
 * and doesn't care whether the value came from UPB bindings, UI state,
 * raw node fields, or defaults.
 *
 * RESOLUTION ORDER (priority):
 *   1. EXPLICIT OVERRIDES (100) - VIS_STATE.overrides + slider values
 *   2. UPB BINDINGS (80) - parameterized by selector state
 *   3. RAW DATA (20) - entity's own fields
 *   4. SCHEMA DEFAULT (0) - fallback values
 *
 * @module PROPERTY_QUERY
 * @version 1.0.0
 *
 * ## Usage
 * ```javascript
 * const Q = createPropertyQuery({ schema, upb, getVisState });
 * Graph.nodeColor(n => Q.node(n, 'color'));
 * Graph.nodeVal(n => Q.node(n, 'size'));
 * ```
 *
 * ## Debugging
 * ```javascript
 * Q.explainNode(node, 'color') // → { value, steps: [...] }
 * ```
 */

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

function isDefined(v) {
    return v !== undefined && v !== null;
}

function getPath(obj, path) {
    if (!obj || !path || typeof path !== 'string') return undefined;
    const parts = path.split('.');
    let cur = obj;
    for (const p of parts) {
        if (cur == null) return undefined;
        cur = cur[p];
    }
    return cur;
}

function clampNumber(x, min, max) {
    if (!Number.isFinite(x)) return undefined;
    if (min != null && x < min) x = min;
    if (max != null && x > max) x = max;
    return x;
}

/**
 * Coerce a value to the expected type for a channel.
 * Returns undefined if coercion fails (invalid value).
 */
function coerce(kind, channel, value, schema) {
    const meta = schema?.[kind]?.[channel];
    if (!meta) return value; // No schema, pass through

    switch (meta.type) {
        case 'number': {
            const n = typeof value === 'number' ? value : Number(value);
            return clampNumber(n, meta.min, meta.max);
        }
        case 'boolean':
            return typeof value === 'boolean' ? value : Boolean(value);
        case 'string':
            return value == null ? undefined : String(value);
        case 'color':
            // Accept strings that look like colors
            if (typeof value === 'string' && value.length > 0) return value;
            // Accept numbers (hex color values)
            if (typeof value === 'number') return value;
            return undefined;
        default:
            return value;
    }
}

// =============================================================================
// PROVIDERS
// =============================================================================

/**
 * EXPLICIT OVERRIDE PROVIDER (Priority 100)
 * Reads from VIS_STATE.overrides and direct slider values.
 * These are "I, the user, am forcing this channel" overrides.
 */
function makeExplicitOverrideProvider({ getVisState }) {
    return {
        name: 'OVERRIDE',
        priority: 100,

        get(kind, entity, channel) {
            const state = getVisState?.() ?? {};

            // A) Explicit override bag: VIS_STATE.overrides.node.color
            const overrides = state?.overrides?.[kind];
            if (overrides && Object.prototype.hasOwnProperty.call(overrides, channel)) {
                return overrides[channel];
            }

            // B) Direct slider/toggle values (these ARE overrides)
            if (kind === 'node') {
                if (channel === 'opacity' && isDefined(state.nodeOpacity)) {
                    return state.nodeOpacity;
                }
            }
            if (kind === 'edge') {
                if (channel === 'opacity' && isDefined(state.edgeOpacity)) {
                    return state.edgeOpacity;
                }
                if (channel === 'curvature' && isDefined(state.edgeCurvature)) {
                    return state.edgeCurvature;
                }
                if (channel === 'width' && isDefined(state.edgeWidth)) {
                    return state.edgeWidth;
                }
            }

            return undefined;
        }
    };
}

/**
 * UPB BINDING PROVIDER (Priority 80)
 * Reads binding configuration and resolves based on selector state.
 * Bindings can be: constants, path strings, or selected mappings.
 */
function makeUPBProvider({ getUPB, getVisState }) {
    return {
        name: 'UPB',
        priority: 80,

        get(kind, entity, channel) {
            const upb = getUPB?.() ?? {};
            const binding = upb?.[kind]?.[channel];
            if (!binding) return undefined;

            // 1) Constant value
            if (typeof binding === 'number' || typeof binding === 'boolean') {
                return binding;
            }

            // 2) Path string -> read from entity
            if (typeof binding === 'string') {
                return getPath(entity, binding);
            }

            // 3) Selected mapping: { by, map, default }
            if (typeof binding === 'object' && binding !== null) {
                const state = getVisState?.() ?? {};
                const selectorKey = binding.by ? getPath(state, binding.by) : undefined;
                const picked = (binding.map && selectorKey != null)
                    ? binding.map[selectorKey]
                    : undefined;

                const resolved = isDefined(picked) ? picked : binding.default;

                // Resolved can be a constant or a path
                if (typeof resolved === 'number' || typeof resolved === 'boolean') {
                    return resolved;
                }
                if (typeof resolved === 'string') {
                    return getPath(entity, resolved);
                }
            }

            return undefined;
        }
    };
}

/**
 * RAW DATA PROVIDER (Priority 20)
 * Reads directly from entity's own fields.
 */
function makeRawDataProvider() {
    return {
        name: 'RAW',
        priority: 20,

        get(kind, entity, channel) {
            if (!entity) return undefined;

            // Direct property
            if (Object.prototype.hasOwnProperty.call(entity, channel)) {
                return entity[channel];
            }

            // Common alternative naming: node_color, edge_opacity
            const altKey = `${kind}_${channel}`;
            if (Object.prototype.hasOwnProperty.call(entity, altKey)) {
                return entity[altKey];
            }

            return undefined;
        }
    };
}

// =============================================================================
// RESOLVER
// =============================================================================

/**
 * Create a property query resolver.
 *
 * @param {Object} options
 * @param {Object} options.schema - Channel defaults and constraints
 * @param {Function} options.getUPB - Returns current UPB binding config
 * @param {Function} options.getVisState - Returns current VIS_STATE
 * @returns {Object} Query interface { node, edge, explainNode, explainEdge }
 */
function createPropertyQuery({
    schema = {},
    getUPB = () => ({}),
    getVisState = () => ({})
} = {}) {

    // Build provider chain sorted by priority (descending)
    const providers = [
        makeExplicitOverrideProvider({ getVisState }),
        makeUPBProvider({ getUPB, getVisState }),
        makeRawDataProvider()
    ].sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0));

    // Cache: entity object -> Map("kind:channel", { epoch, value })
    const cache = new WeakMap();

    function getEpoch() {
        const state = getVisState?.() ?? {};
        return state._epoch ?? 0;
    }

    /**
     * Resolve a property value through the provider chain.
     * CRITICAL: Coercion happens per-provider. Invalid values fall through.
     */
    function resolve(kind, entity, channel, { trace = false } = {}) {
        const currentEpoch = getEpoch();
        const cacheKey = `${kind}:${channel}`;

        // Check cache
        let entityCache = cache.get(entity);
        if (!entityCache) {
            entityCache = new Map();
            cache.set(entity, entityCache);
        }

        const cached = entityCache.get(cacheKey);
        if (cached && cached.epoch === currentEpoch && !trace) {
            return cached.value;
        }

        // Resolve through provider chain
        const steps = [];
        let value;

        for (const provider of providers) {
            const raw = provider.get(kind, entity, channel);

            if (trace) {
                steps.push({ provider: provider.name, raw });
            }

            if (!isDefined(raw)) continue;

            // Coerce per provider - invalid values fall through
            const coerced = coerce(kind, channel, raw, schema);

            if (trace) {
                steps.push({ provider: `${provider.name}:coerced`, value: coerced });
            }

            if (isDefined(coerced)) {
                value = coerced;
                break;
            }
            // Invalid coercion -> continue to next provider
        }

        // Fallback to schema default
        if (!isDefined(value)) {
            const defaultVal = schema?.[kind]?.[channel]?.default;
            if (trace) {
                steps.push({ provider: 'DEFAULT', value: defaultVal });
            }
            value = coerce(kind, channel, defaultVal, schema);
        }

        // Apply scale multipliers (post-resolution)
        const state = getVisState?.() ?? {};
        if (kind === 'node' && channel === 'size') {
            const scale = Number(state.nodeSizeScale ?? 1.0);
            if (Number.isFinite(scale) && Number.isFinite(value)) {
                value = value * scale;
                // Re-coerce after scaling
                value = coerce(kind, channel, value, schema);
            }
        }
        if (kind === 'edge' && channel === 'width') {
            const scale = Number(state.edgeWidthScale ?? 1.0);
            if (Number.isFinite(scale) && Number.isFinite(value)) {
                value = value * scale;
                value = coerce(kind, channel, value, schema);
            }
        }

        // Store in cache
        entityCache.set(cacheKey, { epoch: currentEpoch, value });

        if (trace) {
            return { value, steps };
        }
        return value;
    }

    // ==========================================================================
    // PUBLIC API
    // ==========================================================================

    return {
        /**
         * Query a node property
         * @param {Object} node - The node entity
         * @param {string} channel - Property channel (color, size, opacity, etc.)
         * @returns {*} Resolved value
         */
        node(node, channel) {
            return resolve('node', node, channel);
        },

        /**
         * Query an edge property
         * @param {Object} edge - The edge entity
         * @param {string} channel - Property channel (color, width, opacity, etc.)
         * @returns {*} Resolved value
         */
        edge(edge, channel) {
            return resolve('edge', edge, channel);
        },

        /**
         * Debug: explain how a node property was resolved
         * @param {Object} node - The node entity
         * @param {string} channel - Property channel
         * @returns {Object} { value, steps: [...] }
         */
        explainNode(node, channel) {
            return resolve('node', node, channel, { trace: true });
        },

        /**
         * Debug: explain how an edge property was resolved
         * @param {Object} edge - The edge entity
         * @param {string} channel - Property channel
         * @returns {Object} { value, steps: [...] }
         */
        explainEdge(edge, channel) {
            return resolve('edge', edge, channel, { trace: true });
        },

        /**
         * Force cache invalidation (alternative to epoch bump)
         */
        invalidate() {
            // WeakMap doesn't have clear(), so we rely on epoch
            // This is a no-op; use epoch bump instead
            console.log('[PROPERTY_QUERY] Use VIS_STATE._epoch++ to invalidate');
        }
    };
}

// =============================================================================
// WINDOW EXPORT
// =============================================================================

if (typeof window !== 'undefined') {
    window.createPropertyQuery = createPropertyQuery;
}

console.log('[Module] PROPERTY_QUERY loaded - provider-based property resolution');
