/**
 * DATA MANAGER MODULE
 *
 * Single gate for ALL data access in the visualization.
 * Replaces direct access to FULL_GRAPH and Graph.graphData().
 * Provides O(1) indexed lookups and cached aggregations.
 *
 * Depends on: NODE, COLOR, LEGEND
 *
 * Usage:
 *   DATA.init(graphData)                // Initialize with payload data
 *   DATA.getNodes()                     // Get all raw nodes
 *   DATA.getNode(id)                    // O(1) node lookup
 *   DATA.getNodesByTier('T0')           // O(1) tier lookup
 *   DATA.getEdgesFrom(nodeId)           // O(1) edge lookup
 *   DATA.getTierCounts()                // Cached aggregation
 */

const DATA = (function() {
    'use strict';

    // =========================================================================
    // RAW DATA (immutable after init)
    // =========================================================================

    const raw = {
        nodes: [],
        links: [],
        fileBoundaries: [],
        markov: {},
        kpis: {},
        meta: {},
        physics: {},
        config: {},
        codome_boundaries: null
    };

    // =========================================================================
    // ANALYTICS DATA (all Collider sections)
    // =========================================================================

    const analytics = {
        counts: {},
        stats: {},
        coverage: {},
        performance: {},
        classification: {},
        auto_discovery: {},
        ecosystem_discovery: {},
        dependencies: {},
        architecture: {},
        topology: {},
        execution_flow: {},
        data_flow: {},
        knots: {},
        warnings: [],
        recommendations: [],
        theory_completeness: {},
        distributions: {},
        edge_types: {},
        rpbl_profile: {},
        purpose_field: {},
        top_hubs: [],
        orphans_list: [],
        files: [],
        semantics: {},
        llm_enrichment: {},
        brain_download: {},
        ai_insights: null
    };

    // =========================================================================
    // INDEXES (O(1) lookups - built once)
    // =========================================================================

    const index = {
        nodeById: new Map(),           // id -> node
        nodesByTier: new Map(),        // tier -> [nodes]
        nodesByFamily: new Map(),      // family -> [nodes]
        nodesByRing: new Map(),        // ring -> [nodes]
        nodesByLayer: new Map(),       // layer -> [nodes]
        nodesByEffect: new Map(),      // effect -> [nodes]
        nodesByFile: new Map(),        // fileIdx -> [nodes]
        edgesBySource: new Map(),      // nodeId -> [edges from]
        edgesByTarget: new Map(),      // nodeId -> [edges to]
        edgeByKey: new Map(),          // "src|tgt" -> edge
        fileByIndex: new Map(),        // idx -> fileBoundary
        markovBySource: new Map()      // nodeId -> sorted edges by weight
    };

    // =========================================================================
    // CACHED AGGREGATIONS (computed once, invalidated on filter)
    // =========================================================================

    const cache = {
        tierCounts: null,
        familyCounts: null,
        ringCounts: null,
        layerCounts: null,
        effectCounts: null,
        edgeTypeCounts: null,
        edgeFamilyCounts: null,
        edgeRanges: null
    };

    // =========================================================================
    // CURRENT STATE (filtered view)
    // =========================================================================

    const filtered = {
        nodes: [],
        links: []
    };

    // Legend manager instance
    let _legend = null;

    // =========================================================================
    // INITIALIZATION
    // =========================================================================

    function init(data) {
        // Store raw data
        raw.nodes = Array.isArray(data?.nodes) ? data.nodes : [];
        raw.links = Array.isArray(data?.links) ? data.links : [];
        raw.fileBoundaries = Array.isArray(data?.file_boundaries) ? data.file_boundaries : [];
        raw.markov = data?.markov || {};
        raw.kpis = data?.kpis || {};
        raw.meta = data?.meta || {};
        raw.physics = data?.physics || {};
        raw.config = data?.config || {};
        raw.codome_boundaries = data?.codome_boundaries || null;

        // Store analytics data
        Object.keys(analytics).forEach(key => {
            if (data?.[key] !== undefined) {
                analytics[key] = data[key];
            }
        });

        // Merge CODOME boundaries into main nodes and edges arrays
        _mergeCodomeBooudaries();

        // Build all indexes
        _buildAllIndexes();

        // Initialize legend
        _legend = new LegendManager();
        _legend.init(raw.nodes, raw.links);

        // Set global Legend reference
        if (typeof Legend !== 'undefined') {
            Legend = _legend;
        }

        console.log('%c[DATA] Initialized', 'color: #4ade80; font-weight: bold',
            `${raw.nodes.length} nodes, ${raw.links.length} edges, ${raw.fileBoundaries.length} files`);

        return DATA;
    }

    // =========================================================================
    // CODOME BOUNDARY MERGING
    // =========================================================================

    function _mergeCodomeBooudaries() {
        if (!raw.codome_boundaries) return;

        const boundaryNodes = raw.codome_boundaries.boundary_nodes || [];
        const inferredEdges = raw.codome_boundaries.inferred_edges || [];

        if (boundaryNodes.length === 0 && inferredEdges.length === 0) {
            return;
        }

        // Mark boundary nodes with _fromCodome flag
        boundaryNodes.forEach(node => {
            if (node && typeof node === 'object') {
                node._fromCodome = true;
            }
        });

        // Mark inferred edges with _fromCodome flag
        inferredEdges.forEach(edge => {
            if (edge && typeof edge === 'object') {
                edge._fromCodome = true;
            }
        });

        // Merge boundary nodes into main nodes array
        raw.nodes = raw.nodes.concat(boundaryNodes);

        // Merge inferred edges into main links array
        raw.links = raw.links.concat(inferredEdges);

        console.log('%c[DATA] CODOME boundaries merged', 'color: #60a5fa; font-weight: bold',
            `+${boundaryNodes.length} boundary nodes, +${inferredEdges.length} inferred edges`);
    }

    // =========================================================================
    // INDEX BUILDING
    // =========================================================================

    function _buildAllIndexes() {
        _buildNodeIndex();
        _buildSemanticIndexes();
        _buildEdgeIndexes();
        _buildFileIndex();
        _buildMarkovIndex();
        _invalidateCache();
    }

    function _buildNodeIndex() {
        index.nodeById.clear();
        for (const node of raw.nodes) {
            if (node?.id) {
                index.nodeById.set(node.id, node);
            }
        }
    }

    function _buildSemanticIndexes() {
        index.nodesByTier.clear();
        index.nodesByFamily.clear();
        index.nodesByRing.clear();
        index.nodesByLayer.clear();
        index.nodesByEffect.clear();
        index.nodesByFile.clear();

        for (const node of raw.nodes) {
            if (!node) continue;

            // Tier index
            const tier = NODE.getTier(node);
            if (!index.nodesByTier.has(tier)) {
                index.nodesByTier.set(tier, []);
            }
            index.nodesByTier.get(tier).push(node);

            // Family index
            const family = NODE.getFamily(node);
            if (!index.nodesByFamily.has(family)) {
                index.nodesByFamily.set(family, []);
            }
            index.nodesByFamily.get(family).push(node);

            // Ring index
            const ring = NODE.getRing(node);
            if (!index.nodesByRing.has(ring)) {
                index.nodesByRing.set(ring, []);
            }
            index.nodesByRing.get(ring).push(node);

            // Layer index
            const layer = NODE.getLayer(node);
            if (!index.nodesByLayer.has(layer)) {
                index.nodesByLayer.set(layer, []);
            }
            index.nodesByLayer.get(layer).push(node);

            // Effect index
            const effect = NODE.getEffect(node);
            if (!index.nodesByEffect.has(effect)) {
                index.nodesByEffect.set(effect, []);
            }
            index.nodesByEffect.get(effect).push(node);

            // File index
            const fileIdx = node.fileIdx ?? -1;
            if (fileIdx >= 0) {
                if (!index.nodesByFile.has(fileIdx)) {
                    index.nodesByFile.set(fileIdx, []);
                }
                index.nodesByFile.get(fileIdx).push(node);
            }
        }
    }

    function _buildEdgeIndexes() {
        index.edgesBySource.clear();
        index.edgesByTarget.clear();
        index.edgeByKey.clear();

        for (const link of raw.links) {
            const srcId = _endpointId(link, 'source');
            const tgtId = _endpointId(link, 'target');

            if (srcId) {
                if (!index.edgesBySource.has(srcId)) {
                    index.edgesBySource.set(srcId, []);
                }
                index.edgesBySource.get(srcId).push(link);
            }

            if (tgtId) {
                if (!index.edgesByTarget.has(tgtId)) {
                    index.edgesByTarget.set(tgtId, []);
                }
                index.edgesByTarget.get(tgtId).push(link);
            }

            if (srcId && tgtId) {
                index.edgeByKey.set(`${srcId}|${tgtId}`, link);
            }
        }
    }

    function _buildFileIndex() {
        index.fileByIndex.clear();
        for (let i = 0; i < raw.fileBoundaries.length; i++) {
            index.fileByIndex.set(i, raw.fileBoundaries[i]);
        }
    }

    function _buildMarkovIndex() {
        index.markovBySource.clear();
        for (const link of raw.links) {
            const srcId = _endpointId(link, 'source');
            const mw = link.markov_weight || 0;
            if (srcId && mw > 0) {
                if (!index.markovBySource.has(srcId)) {
                    index.markovBySource.set(srcId, []);
                }
                index.markovBySource.get(srcId).push(link);
            }
        }
        // Sort each list by markov weight descending
        for (const [, edges] of index.markovBySource) {
            edges.sort((a, b) => (b.markov_weight || 0) - (a.markov_weight || 0));
        }
    }

    function _invalidateCache() {
        Object.keys(cache).forEach(key => {
            cache[key] = null;
        });
    }

    // =========================================================================
    // HELPERS
    // =========================================================================

    function _endpointId(link, side) {
        if (!link) return '';
        let value = link[side];
        if (value && typeof value === 'object') value = value.id;
        return (value === undefined || value === null) ? '' : String(value).trim();
    }

    // =========================================================================
    // RAW DATA ACCESSORS
    // =========================================================================

    function getNodes() { return raw.nodes; }
    function getLinks() { return raw.links; }
    function getFileBoundaries() { return raw.fileBoundaries; }
    function getMarkov() { return raw.markov; }
    function getKpis() { return raw.kpis; }
    function getMeta() { return raw.meta; }
    function getPhysics() { return raw.physics; }
    function getConfig() { return raw.config; }
    function getCodomeBooudaries() { return raw.codome_boundaries; }
    function getAnalytics(key) { return analytics[key]; }

    // =========================================================================
    // INDEXED LOOKUPS (O(1))
    // =========================================================================

    function getNode(id) {
        return index.nodeById.get(id) || null;
    }

    function getNodesByTier(tier) {
        return index.nodesByTier.get(tier) || [];
    }

    function getNodesByFamily(family) {
        return index.nodesByFamily.get(family) || [];
    }

    function getNodesByRing(ring) {
        return index.nodesByRing.get(ring) || [];
    }

    function getNodesByLayer(layer) {
        return index.nodesByLayer.get(layer) || [];
    }

    function getNodesByEffect(effect) {
        return index.nodesByEffect.get(effect) || [];
    }

    function getNodesByFile(fileIdx) {
        return index.nodesByFile.get(fileIdx) || [];
    }

    function getEdgesFrom(nodeId) {
        return index.edgesBySource.get(nodeId) || [];
    }

    function getEdgesTo(nodeId) {
        return index.edgesByTarget.get(nodeId) || [];
    }

    function getEdgeBetween(srcId, tgtId) {
        return index.edgeByKey.get(`${srcId}|${tgtId}`) || null;
    }

    function getFile(idx) {
        return index.fileByIndex.get(idx) || null;
    }

    function getTopMarkovEdges(nodeId, k = 5) {
        const edges = index.markovBySource.get(nodeId) || [];
        return edges.slice(0, k);
    }

    function isHighEntropyNode(nodeId) {
        const highEntropy = raw.markov?.high_entropy_nodes || [];
        return highEntropy.some(h => h.node === nodeId);
    }

    // =========================================================================
    // FILTERED DATA
    // =========================================================================

    function setFiltered(nodes, links) {
        filtered.nodes = nodes || [];
        filtered.links = links || [];
    }

    function getVisibleNodes() {
        if (filtered.nodes.length > 0) {
            return filtered.nodes;
        }
        return (typeof Graph !== 'undefined' && Graph?.graphData)
            ? (Graph.graphData().nodes || [])
            : [];
    }

    function getVisibleLinks() {
        if (filtered.links.length > 0) {
            return filtered.links;
        }
        return (typeof Graph !== 'undefined' && Graph?.graphData)
            ? (Graph.graphData().links || [])
            : [];
    }

    // =========================================================================
    // AGGREGATIONS (cached)
    // =========================================================================

    function getTierCounts() {
        if (!cache.tierCounts) {
            cache.tierCounts = new Map();
            for (const [tier, nodes] of index.nodesByTier) {
                cache.tierCounts.set(tier, nodes.length);
            }
        }
        return cache.tierCounts;
    }

    function getFamilyCounts() {
        if (!cache.familyCounts) {
            cache.familyCounts = new Map();
            for (const [family, nodes] of index.nodesByFamily) {
                cache.familyCounts.set(family, nodes.length);
            }
        }
        return cache.familyCounts;
    }

    function getRingCounts() {
        if (!cache.ringCounts) {
            cache.ringCounts = new Map();
            for (const [ring, nodes] of index.nodesByRing) {
                cache.ringCounts.set(ring, nodes.length);
            }
        }
        return cache.ringCounts;
    }

    function getLayerCounts() {
        if (!cache.layerCounts) {
            cache.layerCounts = new Map();
            for (const [layer, nodes] of index.nodesByLayer) {
                cache.layerCounts.set(layer, nodes.length);
            }
        }
        return cache.layerCounts;
    }

    function getEffectCounts() {
        if (!cache.effectCounts) {
            cache.effectCounts = new Map();
            for (const [effect, nodes] of index.nodesByEffect) {
                cache.effectCounts.set(effect, nodes.length);
            }
        }
        return cache.effectCounts;
    }

    function getEdgeTypeCounts() {
        if (!cache.edgeTypeCounts) {
            cache.edgeTypeCounts = new Map();
            for (const link of raw.links) {
                const type = link.edge_type || link.type || 'unknown';
                cache.edgeTypeCounts.set(type, (cache.edgeTypeCounts.get(type) || 0) + 1);
            }
        }
        return cache.edgeTypeCounts;
    }

    function getEdgeFamilyCounts() {
        if (!cache.edgeFamilyCounts) {
            cache.edgeFamilyCounts = new Map();
            for (const link of raw.links) {
                const family = link.family || 'Dependency';
                cache.edgeFamilyCounts.set(family, (cache.edgeFamilyCounts.get(family) || 0) + 1);
            }
        }
        return cache.edgeFamilyCounts;
    }

    function getEdgeRanges() {
        if (!cache.edgeRanges) {
            let minW = Infinity, maxW = -Infinity;
            let minC = Infinity, maxC = -Infinity;
            for (const link of raw.links) {
                const w = link.weight ?? 1;
                const c = link.confidence ?? 1;
                if (w < minW) minW = w;
                if (w > maxW) maxW = w;
                if (c < minC) minC = c;
                if (c > maxC) maxC = c;
            }
            cache.edgeRanges = {
                weight: { min: minW === Infinity ? 0 : minW, max: maxW === -Infinity ? 1 : maxW },
                confidence: { min: minC === Infinity ? 0 : minC, max: maxC === -Infinity ? 1 : maxC }
            };
        }
        return cache.edgeRanges;
    }

    /**
     * Get min/max range for a source property across a specific scope.
     * NOT cached - calculates fresh each call (scopes change dynamically).
     *
     * @param {string} sourceKey - Property name (e.g., 'token_estimate', 'in_degree')
     * @param {string} scope - 'global' | 'visible' | 'selection'
     * @returns {{ min: number, max: number }} Range object
     */
    function getRange(sourceKey, scope = 'global') {
        // Get node set based on scope
        let nodes;
        switch (scope) {
            case 'selection':
                nodes = (typeof SELECTION !== 'undefined' && SELECTION.getSelectedNodes)
                    ? SELECTION.getSelectedNodes()
                    : [];
                break;
            case 'visible':
                nodes = getVisibleNodes();
                break;
            case 'global':
            default:
                nodes = raw.nodes;
                break;
        }

        // Extract numeric values
        const values = [];
        for (const node of nodes) {
            const val = _getNodeValue(node, sourceKey);
            if (typeof val === 'number' && !Number.isNaN(val)) {
                values.push(val);
            }
        }

        // Return safe range
        if (values.length === 0) {
            return { min: 0, max: 1 };
        }

        return {
            min: Math.min(...values),
            max: Math.max(...values)
        };
    }

    /**
     * Extract a value from a node for a given source key.
     * Handles nested properties and computed values.
     */
    function _getNodeValue(node, sourceKey) {
        if (!node || !sourceKey) return undefined;

        // Direct property
        if (node[sourceKey] !== undefined) {
            return node[sourceKey];
        }

        // Nested in metrics
        if (node.metrics && node.metrics[sourceKey] !== undefined) {
            return node.metrics[sourceKey];
        }

        // Computed values
        switch (sourceKey) {
            case 'in_degree':
                return (getEdgesTo(node.id) || []).length;
            case 'out_degree':
                return (getEdgesFrom(node.id) || []).length;
            case 'degree':
                return (getEdgesTo(node.id) || []).length + (getEdgesFrom(node.id) || []).length;
            default:
                return undefined;
        }
    }

    // =========================================================================
    // SELF-TEST
    // =========================================================================

    function selfTest() {
        const errors = [];
        const warnings = [];
        const seenIds = new Set();

        for (const node of raw.nodes) {
            if (!node?.id) {
                errors.push('Node missing id');
                continue;
            }
            if (seenIds.has(node.id)) {
                errors.push(`Duplicate node id: ${node.id}`);
                continue;
            }
            seenIds.add(node.id);
        }

        for (const link of raw.links) {
            const srcId = _endpointId(link, 'source');
            const tgtId = _endpointId(link, 'target');
            if (srcId && !index.nodeById.has(srcId)) {
                warnings.push(`Edge source not in graph: ${srcId}`);
            }
            if (tgtId && !index.nodeById.has(tgtId)) {
                warnings.push(`Edge target not in graph: ${tgtId}`);
            }
        }

        const status = errors.length === 0 ? 'PASS' : 'FAIL';
        const style = errors.length === 0
            ? 'color: #4ade80; font-weight: bold'
            : 'color: #f87171; font-weight: bold';

        console.log(`%c[DATA] Self-Test: ${status}`, style);
        console.log(`  Raw: ${raw.nodes.length} nodes, ${raw.links.length} edges`);
        console.log(`  Indexes: nodeById=${index.nodeById.size}, tiers=${index.nodesByTier.size}`);

        if (errors.length > 0) console.error('[DATA] Errors:', errors);
        if (warnings.length > 0) {
            console.warn('[DATA] Warnings:', warnings.slice(0, 5));
            if (warnings.length > 5) console.warn(`  ... and ${warnings.length - 5} more`);
        }

        return { errors, warnings, pass: errors.length === 0 };
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Init
        init,

        // Raw data
        getNodes,
        getLinks,
        getFileBoundaries,
        getMarkov,
        getKpis,
        getMeta,
        getPhysics,
        getConfig,
        getCodomeBooudaries,
        getAnalytics,

        // Indexed lookups
        getNode,
        getNodesByTier,
        getNodesByFamily,
        getNodesByRing,
        getNodesByLayer,
        getNodesByEffect,
        getNodesByFile,
        getEdgesFrom,
        getEdgesTo,
        getEdgeBetween,
        getFile,
        getTopMarkovEdges,
        isHighEntropyNode,

        // Filtered data
        setFiltered,
        getVisibleNodes,
        getVisibleLinks,

        // Aggregations
        getTierCounts,
        getFamilyCounts,
        getRingCounts,
        getLayerCounts,
        getEffectCounts,
        getEdgeTypeCounts,
        getEdgeFamilyCounts,
        getEdgeRanges,
        getRange,

        // Self-test
        selfTest,

        // Direct access (for migration)
        raw,
        index,
        cache,
        filtered,

        // Legend reference
        get legend() { return _legend; },

        // Color access (convenience)
        get color() { return COLOR; }
    };
})();

// Backward compatibility - DataManager class wrapper
class DataManager {
    constructor() {
        this.raw = DATA.raw;
        this.analytics = {};
        this.index = DATA.index;
        this.cache = DATA.cache;
        this.filtered = DATA.filtered;
        this.legend = null;
        this.color = COLOR;
    }

    init(data) {
        DATA.init(data);
        this.raw = DATA.raw;
        this.index = DATA.index;
        this.cache = DATA.cache;
        this.filtered = DATA.filtered;
        this.legend = DATA.legend;
        return this;
    }

    // Delegate all methods to DATA module
    getNodes() { return DATA.getNodes(); }
    getLinks() { return DATA.getLinks(); }
    getFileBoundaries() { return DATA.getFileBoundaries(); }
    getMarkov() { return DATA.getMarkov(); }
    getKpis() { return DATA.getKpis(); }
    getMeta() { return DATA.getMeta(); }
    getCodomeBooudaries() { return DATA.getCodomeBooudaries(); }
    getNode(id) { return DATA.getNode(id); }
    getNodesByTier(tier) { return DATA.getNodesByTier(tier); }
    getNodesByFamily(family) { return DATA.getNodesByFamily(family); }
    getNodesByRing(ring) { return DATA.getNodesByRing(ring); }
    getNodesByFile(fileIdx) { return DATA.getNodesByFile(fileIdx); }
    getEdgesFrom(nodeId) { return DATA.getEdgesFrom(nodeId); }
    getEdgesTo(nodeId) { return DATA.getEdgesTo(nodeId); }
    getEdgeBetween(srcId, tgtId) { return DATA.getEdgeBetween(srcId, tgtId); }
    getFile(idx) { return DATA.getFile(idx); }
    getTopMarkovEdges(nodeId, k) { return DATA.getTopMarkovEdges(nodeId, k); }
    isHighEntropyNode(nodeId) { return DATA.isHighEntropyNode(nodeId); }
    setFiltered(nodes, links) { DATA.setFiltered(nodes, links); }
    getVisibleNodes() { return DATA.getVisibleNodes(); }
    getVisibleLinks() { return DATA.getVisibleLinks(); }
    getTierCounts() { return DATA.getTierCounts(); }
    getFamilyCounts() { return DATA.getFamilyCounts(); }
    getRingCounts() { return DATA.getRingCounts(); }
    getLayerCounts() { return DATA.getLayerCounts(); }
    getEffectCounts() { return DATA.getEffectCounts(); }
    getEdgeTypeCounts() { return DATA.getEdgeTypeCounts(); }
    getEdgeFamilyCounts() { return DATA.getEdgeFamilyCounts(); }
    getEdgeRanges() { return DATA.getEdgeRanges(); }
    getRange(sourceKey, scope) { return DATA.getRange(sourceKey, scope); }
    selfTest() { return DATA.selfTest(); }

    // Internal methods
    _buildAllIndexes() {}
    _buildNodeIndex() {}
    _buildSemanticIndexes() {}
    _buildEdgeIndexes() {}
    _buildFileIndex() {}
    _buildMarkovIndex() {}
    _invalidateCache() {}
    _endpointId(link, side) {
        if (!link) return '';
        let value = link[side];
        if (value && typeof value === 'object') value = value.id;
        return (value === undefined || value === null) ? '' : String(value).trim();
    }
    _getNodeTier(node) { return NODE.getTier(node); }
    _getNodeFamily(node) { return NODE.getFamily(node); }
    _getNodeRing(node) { return NODE.getRing(node); }
    _getNodeLayer(node) { return NODE.getLayer(node); }
    _getNodeEffect(node) { return NODE.getEffect(node); }
}

// Global DM instance - defined by app.js (not duplicated here to avoid redeclaration)
// DM is accessed as a global variable provided by app.js

// Parity check function
function runDmParity(dm, data) {
    if (!dm) return;
    const checks = [];
    const rawNodes = Array.isArray(data?.nodes) ? data.nodes.length : 0;
    const rawEdges = Array.isArray(data?.links) ? data.links.length : 0;
    const dmNodes = dm.raw.nodes.length;
    const dmEdges = dm.raw.links.length;

    checks.push({ name: 'Node count', dm: dmNodes, old: rawNodes, pass: dmNodes === rawNodes });
    checks.push({ name: 'Edge count', dm: dmEdges, old: rawEdges, pass: dmEdges === rawEdges });
    checks.push({ name: 'Node index size', dm: dm.index.nodeById.size, old: rawNodes, pass: dm.index.nodeById.size === rawNodes });

    const allPass = checks.every(c => c.pass);
    const style = allPass ? 'color: #4ade80; font-weight: bold' : 'color: #f87171; font-weight: bold';
    console.log(`%c[DM Parity] ${allPass ? 'ALL PASS' : 'MISMATCH'}`, style);
    checks.forEach(c => {
        const icon = c.pass ? '✓' : '✗';
        console.log(`  ${icon} ${c.name}: DM=${c.dm}, Raw=${c.old}`);
    });
}
