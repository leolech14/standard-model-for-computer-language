/**
 * LEGEND MANAGER MODULE
 *
 * Manages legend data, counts, and visibility for all visualization dimensions.
 * Delegates all color operations to the COLOR module.
 *
 * Depends on: COLOR, NODE
 *
 * Usage:
 *   LEGEND.init(nodes, links)           // Initialize with graph data
 *   LEGEND.getLegendData('tier')        // Get legend items for a dimension
 *   LEGEND.getColor('tier', 'T0')       // Get color (delegates to COLOR)
 *   LEGEND.subscribe(callback)          // React to legend changes
 */

const LEGEND = (function() {
    'use strict';

    // =========================================================================
    // DIMENSION METADATA
    // =========================================================================

    const dimensions = {
        tier: {
            name: 'TIERS',
            icon: '◐',
            extract: (node) => NODE.getTier(node)
        },
        family: {
            name: 'FAMILIES',
            icon: '⬡',
            extract: (node) => NODE.getFamily(node)
        },
        ring: {
            name: 'RINGS',
            icon: '◎',
            extract: (node) => NODE.getRing(node)
        },
        layer: {
            name: 'LAYERS',
            icon: '☰',
            extract: (node) => NODE.getLayer(node).toUpperCase()
        },
        effect: {
            name: 'EFFECTS',
            icon: '⚡',
            extract: (node) => NODE.getEffect(node)
        },
        edgeType: {
            name: 'EDGE TYPES',
            icon: '→',
            extract: (link) => (link.edge_type || link.type || 'unknown').toLowerCase()
        },
        edgeFamily: {
            name: 'EDGE FAMILIES',
            icon: '⇢',
            extract: (link) => (link.family || 'Dependency')
        }
    };

    // =========================================================================
    // STATE
    // =========================================================================

    let _counts = {};
    let _subscribers = [];

    // =========================================================================
    // CORE FUNCTIONS
    // =========================================================================

    /**
     * Initialize legend with nodes and links data
     */
    function init(nodes, links) {
        _computeCounts(nodes, links);
        return LEGEND;
    }

    /**
     * Compute counts for all dimensions
     */
    function _computeCounts(nodes, links) {
        _counts = {};

        // Node dimensions
        ['tier', 'family', 'ring', 'layer', 'effect'].forEach(dim => {
            const extract = dimensions[dim]?.extract;
            if (!extract) return;

            _counts[dim] = {};
            (nodes || []).forEach(node => {
                const cat = extract(node);
                _counts[dim][cat] = (_counts[dim][cat] || 0) + 1;
            });
        });

        // Edge dimensions
        ['edgeType', 'edgeFamily'].forEach(dim => {
            const extract = dimensions[dim]?.extract;
            if (!extract) return;

            _counts[dim] = {};
            (links || []).forEach(link => {
                const cat = extract(link);
                _counts[dim][cat] = (_counts[dim][cat] || 0) + 1;
            });
        });

        console.log('[LEGEND] Counts computed:', Object.keys(_counts));
        _notifySubscribers('counts-updated', _counts);
    }

    /**
     * Get legend data for a dimension
     * Returns array of { id, label, color, count, dimension }
     */
    function getLegendData(dimension) {
        const counts = _counts[dimension] || {};

        return Object.keys(counts)
            .filter(cat => counts[cat] > 0)
            .sort((a, b) => (counts[b] || 0) - (counts[a] || 0))
            .map(cat => ({
                id: cat,
                label: COLOR.getLabel(dimension, cat),
                color: COLOR.get(dimension, cat),
                count: counts[cat] || 0,
                dimension: dimension
            }));
    }

    /**
     * Get color for a dimension/category (delegates to COLOR)
     */
    function getColor(dimension, category) {
        return COLOR.get(dimension, category);
    }

    /**
     * Get counts for a dimension
     */
    function getCounts(dimension) {
        return _counts[dimension] || {};
    }

    /**
     * Get all available dimensions
     */
    function getDimensions() {
        return Object.keys(dimensions);
    }

    /**
     * Get dimension metadata
     */
    function getDimensionMeta(dimension) {
        return dimensions[dimension] || null;
    }

    // =========================================================================
    // SUBSCRIPTIONS
    // =========================================================================

    function subscribe(callback) {
        _subscribers.push(callback);
        return () => {
            _subscribers = _subscribers.filter(cb => cb !== callback);
        };
    }

    function _notifySubscribers(event, data) {
        _subscribers.forEach(cb => cb(event, data));
    }

    // =========================================================================
    // DOM RENDERING
    // =========================================================================

    /**
     * Render a legend section to the DOM
     * @param {string} containerId - DOM container ID
     * @param {string} dimension - Dimension to render (tier, family, etc.)
     * @param {Set} stateSet - Filter state set (items to show)
     * @param {Function} onUpdate - Callback when filter changes
     */
    function renderSection(containerId, dimension, stateSet, onUpdate) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';

        const legendData = getLegendData(dimension);
        if (!legendData || legendData.length === 0) return;

        // Build legend items
        legendData.forEach(item => {
            const el = document.createElement('div');
            el.className = 'topo-legend-item' + (stateSet && !stateSet.has(item.id) ? ' filtered' : '');
            el.dataset.category = item.id;
            el.dataset.dimension = dimension;

            // Color swatch
            const swatch = document.createElement('span');
            swatch.className = 'topo-legend-swatch';
            swatch.style.backgroundColor = item.color;

            // Label with count
            const label = document.createElement('span');
            label.className = 'topo-legend-label';
            label.textContent = item.id;

            const count = document.createElement('span');
            count.className = 'topo-legend-count';
            count.textContent = `(${item.count})`;

            el.appendChild(swatch);
            el.appendChild(label);
            el.appendChild(count);

            // Click to toggle filter
            if (stateSet) {
                el.addEventListener('click', () => {
                    if (stateSet.has(item.id)) {
                        stateSet.delete(item.id);
                        el.classList.add('filtered');
                    } else {
                        stateSet.add(item.id);
                        el.classList.remove('filtered');
                    }
                    if (onUpdate) onUpdate();
                });
            }

            container.appendChild(el);
        });

        console.log(`[Legend] Rendered ${dimension}: ${legendData.length} items`);
    }

    /**
     * Render all legend sections
     * @param {Object} filters - VIS_FILTERS object with filter Sets
     * @param {Function} onUpdate - Callback when any filter changes (typically refreshGraph)
     */
    function renderAll(filters, onUpdate) {
        // Render node legends
        renderSection('topo-tiers', 'tier', filters?.tiers, onUpdate);
        renderSection('topo-families', 'family', filters?.families, onUpdate);
        renderSection('topo-rings', 'ring', filters?.rings, onUpdate);
        renderSection('topo-layers', 'layer', filters?.layers, onUpdate);
        renderSection('topo-effects', 'effect', filters?.effects, onUpdate);

        // Render edge legends
        renderSection('topo-edges', 'edgeType', filters?.edges, onUpdate);
        renderSection('topo-edge-families', 'edgeFamily', filters?.edgeFamilies, onUpdate);

        console.log('[Legend] All sections rendered');
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        init,
        getLegendData,
        getColor,
        getCounts,
        getDimensions,
        getDimensionMeta,
        subscribe,
        renderSection,
        renderAll,

        // Direct access to dimensions (for migration)
        dimensions,

        // Computed counts
        get counts() { return _counts; }
    };
})();

// Backward compatibility - LegendManager class wrapper
class LegendManager {
    constructor() {
        this.dimensions = LEGEND.dimensions;
        this.counts = {};
        this._subscribers = [];
    }

    init(nodes, links) {
        LEGEND.init(nodes, links);
        this.counts = LEGEND.counts;
        return this;
    }

    _computeCounts(nodes, links) {
        LEGEND.init(nodes, links);
        this.counts = LEGEND.counts;
    }

    getLegendData(dimension) {
        return LEGEND.getLegendData(dimension);
    }

    getColor(dimension, category) {
        return LEGEND.getColor(dimension, category);
    }

    subscribe(callback) {
        this._subscribers.push(callback);
        return () => {
            this._subscribers = this._subscribers.filter(cb => cb !== callback);
        };
    }

    _notifySubscribers(event, data) {
        this._subscribers.forEach(cb => cb(event, data));
    }
}

// Global Legend instance - defined by app.js (not duplicated here to avoid redeclaration)
// Legend is accessed as a global variable provided by app.js

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

// renderLegendSection calls LEGEND.renderSection with Legend (global) as source
window.renderLegendSection = function(containerId, dimension, stateSet, onUpdate) {
    LEGEND.renderSection(containerId, dimension, stateSet, onUpdate);
};

// renderAllLegends uses VIS_FILTERS and refreshGraph from app.js globals
// Includes 100ms debounce to prevent DOM thrashing during rapid updates
let _legendDebounceTimer = null;
window.renderAllLegends = function() {
    if (_legendDebounceTimer) clearTimeout(_legendDebounceTimer);
    _legendDebounceTimer = setTimeout(() => {
        _legendDebounceTimer = null;
        const VIS_FILTERS = window.VIS_FILTERS;
        const refreshGraph = window.refreshGraph;
        if (VIS_FILTERS && refreshGraph) {
            LEGEND.renderAll(VIS_FILTERS, refreshGraph);
        } else {
            console.warn('[Legend] VIS_FILTERS or refreshGraph not available');
        }
    }, 100);
};

console.log('[Module] LEGEND loaded - 10 functions');
