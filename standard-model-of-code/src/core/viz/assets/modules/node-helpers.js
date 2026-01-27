/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NODE-HELPERS MODULE - Node classification and color functions
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Node color mode selection, data enrichment helpers, and tier grouping.
 * Depends on: COLOR (ColorOrchestrator), NODE (node-accessors), DM, Graph
 *
 * @module NODE_HELPERS
 * @version 1.0.0
 */

window.NODE_HELPERS = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // NODE COLOR BY MODE
    // ═══════════════════════════════════════════════════════════════════════

    // =========================================================================
    // MODE_ACCESSORS: Declarative map replacing the mega-switch
    // Each mode maps to a function: (node, Color) => colorString
    // =========================================================================

    const MODE_ACCESSORS = {
        // 1. ARCHITECTURE
        tier:           (n, C) => C.get('tier', window.getNodeTier(n)),
        layer:          (n, C) => C.get('layer', (n.layer || n.dimensions?.D2_LAYER || 'UNKNOWN').toUpperCase()),
        subsystem:      (n, C) => C.get('subsystem', getSubsystem(n)),
        boundary_score: (n, C) => C.getInterval('boundary_score', window.normalize(n.rpbl?.boundary ?? 1, 9)),
        phase:          (n, C) => C.get('phase', getPhase(n)),

        // 2. TAXONOMY
        atom:           (n, C) => C.get('atom', (n.kind || n.type || 'unknown').toLowerCase()),
        family:         (n, C) => C.get('family', window.getNodeAtomFamily(n)),
        role:           (n, C) => C.get('roleCategory', n.role_cat || 'Unknown'),
        roleCategory:   (n, C) => C.get('roleCategory', n.role_cat || getRoleCategory(n)),
        fileType:       (n, C) => C.get('fileType', getFileType(n)),

        // 3. METRICS
        complexity:     (n, C) => C.getInterval('complexity', window.normalize(n.complexity || 0, 20)),
        loc:            (n, C) => C.getInterval('loc', window.normalize(n.lines_of_code || 0, 500)),
        fan_in:         (n, C) => C.getInterval('fan_in', window.normalize(n.in_degree || 0, 20)),
        fan_out:        (n, C) => C.getInterval('fan_out', window.normalize(n.out_degree || 0, 20)),
        trust:          (n, C) => C.getInterval('trust', n.trust || n.confidence || 0),

        // 4. RPBL DNA
        responsibility: (n, C) => C.getInterval('responsibility', window.normalize(n.rpbl?.responsibility ?? 1, 9)),
        purity:         (n, C) => C.getInterval('purity', window.normalize(n.rpbl?.purity ?? 1, 9)),
        lifecycle_score:(n, C) => C.getInterval('lifecycle_score', window.normalize(n.rpbl?.lifecycle ?? 1, 9)),
        state:          (n, C) => C.get('state', (n.dimensions?.D5_STATE === 'Stateful') ? 'Stateful' : 'Stateless'),
        visibility:     (n, C) => C.get('visibility', n.dimensions?.D4_BOUNDARY === 'External' ? 'Public' : 'Private'),

        // 5. TOPOLOGY
        centrality:     (n, C) => C.getInterval('centrality', n.centrality || 0),
        rank:           (n, C) => C.getInterval('centrality', n.pagerank || 0),
        ring:           (n, C) => C.get('ring', window.getNodeRing(n)),

        // 6. SEMANTIC PURPOSE (Stage 6.7 - PURPOSE = f(edges))
        semanticRole:   (n, C) => C.get('semanticRole', n.semantic_role || 'unknown'),

        // 7. HOLARCHY SCALE (Stage 2.6 - 16-level classification)
        scale:          (n, C) => C.get('scale', n.level || 'L3'),
        levelZone:      (n, C) => C.get('levelZone', n.level_zone || 'SEMANTIC'),

        // 8. EVOLUTION (Placeholders)
        churn:          (n, C) => C.getInterval('churn', Math.random() * 0.5),
        age:            (n, C) => C.getInterval('churn', 0.2)
    };

    function getNodeColorByMode(node) {
        const Color = window.Color;
        const NODE_COLOR_MODE = window.NODE_COLOR_MODE;
        const DM = window.DM;

        // Special case: CODOME boundary nodes (external callers)
        // Always use their explicit color_hint, regardless of color mode
        if (node.is_codome_boundary || node.kind === 'boundary') {
            if (node.color_hint) {
                return node.color_hint;
            }
            // Fallback color mapping by codome_source
            const CODOME_COLORS = {
                'test_entry': '#4CAF50',      // Green
                'entry_point': '#2196F3',     // Blue
                'framework_managed': '#9C27B0', // Purple
                'cross_language': '#FF9800',  // Orange
                'external_boundary': '#00BCD4', // Cyan
                'dynamic_target': '#E91E63'   // Pink
            };
            return CODOME_COLORS[node.codome_source] || '#FF9800';
        }

        // Special case: file coloring needs extra context
        if (NODE_COLOR_MODE === 'file') {
            const fileIdx = node.fileIdx ?? -1;
            if (fileIdx < 0) return Color.get('tier', 'UNKNOWN');
            const fileBoundaries = DM ? DM.getFileBoundaries() : [];
            const totalFiles = fileBoundaries.length;
            const fileInfo = fileBoundaries[fileIdx] || {};
            const fileLabel = fileInfo.file || fileInfo.file_name || fileIdx;
            return window.getFileColor(fileIdx, totalFiles, fileLabel);
        }

        // Use MODE_ACCESSORS map - O(1) lookup instead of if-chain
        const accessor = MODE_ACCESSORS[NODE_COLOR_MODE];
        if (accessor) return accessor(node, Color);

        // Default fallback
        return Color.get('tier', window.getNodeTier(node));
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DATA ENRICHMENT HELPERS
    // ═══════════════════════════════════════════════════════════════════════

    function getSubsystem(node) {
        if (!node.file_path) return 'Unknown';
        if (node.file_path.includes('/api/')) return 'Ingress';
        if (node.file_path.includes('/db/') || node.file_path.includes('repository')) return 'Persistence';
        if (node.file_path.includes('/core/') || node.file_path.includes('domain')) return 'Domain';
        if (node.file_path.includes('/ui/') || node.file_path.includes('frontend')) return 'Presentation';
        if (node.file_path.includes('config')) return 'Config';
        return 'Domain';
    }

    function getPhase(node) {
        const kind = (node.kind || '').toLowerCase();
        if (kind.includes('data') || kind.includes('entity') || kind.includes('schema')) return 'DATA';
        if (kind.includes('function') || kind.includes('logic')) return 'LOGIC';
        if (kind.includes('module') || kind.includes('package')) return 'ORGANIZATION';
        if (kind.includes('script') || kind.includes('main')) return 'EXECUTION';
        return 'LOGIC';
    }

    function getFileType(node) {
        const p = node.file_path || node.id || '';
        const ext = p.split('.').pop().toLowerCase();
        return ext || 'unknown';
    }

    function getRoleCategory(node) {
        const r = (node.role || '').toLowerCase();
        if (r.includes('service') || r.includes('manager')) return 'Orchestration';
        if (r.includes('repo') || r.includes('store')) return 'Storage';
        if (r.includes('controller') || r.includes('handler')) return 'Ingress';
        if (r.includes('util') || r.includes('helper')) return 'Utility';
        return 'Unknown';
    }

    // ═══════════════════════════════════════════════════════════════════════
    // NODE COLOR APPLICATION
    // ═══════════════════════════════════════════════════════════════════════

    function applyNodeColors(nodes) {
        const DM = window.DM;
        const fileBoundaries = DM ? DM.getFileBoundaries() : [];
        const totalFiles = fileBoundaries.length;

        nodes.forEach(node => {
            // PRE-COMPUTE file_color for UPB/Property Query resolution
            // This ensures Q.node(n, 'color') works when colorBy='file'
            if (node.fileIdx !== undefined && node.fileIdx >= 0 && totalFiles > 0) {
                const fileInfo = fileBoundaries[node.fileIdx] || {};
                const fileLabel = fileInfo.file || fileInfo.file_name || node.fileIdx;
                node.file_color = window.getFileColor(node.fileIdx, totalFiles, fileLabel);
            }

            if (node && node.isFileNode) {
                if (!node.color) {
                    node.color = node.file_color || window.getFileColor(node.fileIdx, totalFiles, '');
                }
                return;
            }
            if (window.fileMode) {
                return;
            }
            // For boundary nodes, always apply their specific color
            if (node.is_codome_boundary || node.kind === 'boundary') {
                node.color = getNodeColorByMode(node);
                return;
            }
            node.color = getNodeColorByMode(node);
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // NODE SIZE MODE
    // ═══════════════════════════════════════════════════════════════════════

    function applyNodeSizeMode(mode) {
        const Graph = window.Graph;
        if (!Graph) return;
        const scale = window.APPEARANCE_STATE?.nodeScale || 1;
        const BOUNDARY_NODE_SIZE_MULTIPLIER = 1.5; // Boundary nodes 1.5x larger

        const isBoundaryNode = (n) => n.is_codome_boundary || n.kind === 'boundary';
        const sizeWithBoundaryCheck = (baseSize) =>
            isBoundaryNode({ is_codome_boundary: arguments[0]?.is_codome_boundary, kind: arguments[0]?.kind })
                ? baseSize * BOUNDARY_NODE_SIZE_MULTIPLIER
                : baseSize;

        switch (mode) {
            case 'uniform':
                Graph.nodeVal(n => (isBoundaryNode(n) ? 1.5 : 1) * scale);
                break;
            case 'degree':
                Graph.nodeVal(n => {
                    const baseSize = Math.max(1, ((n.in_degree || 0) + (n.out_degree || 0)) * 0.5);
                    return (isBoundaryNode(n) ? baseSize * BOUNDARY_NODE_SIZE_MULTIPLIER : baseSize) * scale;
                });
                break;
            case 'fanout':
                Graph.nodeVal(n => {
                    const baseSize = n.val || n.fanout || 1;
                    return (isBoundaryNode(n) ? baseSize * BOUNDARY_NODE_SIZE_MULTIPLIER : baseSize) * scale;
                });
                break;
            case 'complexity':
                Graph.nodeVal(n => {
                    const baseSize = Math.max(1, (n.complexity || n.loc || 10) * 0.05);
                    return (isBoundaryNode(n) ? baseSize * BOUNDARY_NODE_SIZE_MULTIPLIER : baseSize) * scale;
                });
                break;
            default:
                Graph.nodeVal(n => {
                    const baseSize = n.val || 1;
                    return (isBoundaryNode(n) ? baseSize * BOUNDARY_NODE_SIZE_MULTIPLIER : baseSize) * scale;
                });
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // TIER/DEPTH/SIMILARITY HELPERS
    // ═══════════════════════════════════════════════════════════════════════

    function getNodeTierValue(node) {
        if (!node) return 1;
        const tier = window.getNodeTier(node);
        if (tier === 'T0') return 0;
        if (tier === 'T1') return 1;
        if (tier === 'T2') return 2;
        return 1;
    }

    function getNodeDepth(node) {
        if (node && typeof node.y === 'number') {
            return Math.abs(node.y) / 500;
        }
        return 0.5;
    }

    function getSemanticSimilarity(srcNode, tgtNode) {
        if (!srcNode || !tgtNode) return 0.5;
        let score = 0;
        if (srcNode.type === tgtNode.type) score += 0.4;
        if (srcNode.fileIdx === tgtNode.fileIdx) score += 0.3;
        if (window.getNodeTier(srcNode) === window.getNodeTier(tgtNode)) score += 0.2;
        if (srcNode.ring === tgtNode.ring) score += 0.1;
        return score;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // TIER GROUPING
    // ═══════════════════════════════════════════════════════════════════════

    function groupNodesByTier(nodes) {
        const groups = { T0: [], T1: [], T2: [], UNKNOWN: [] };
        nodes.forEach(n => {
            const tier = window.getNodeTier(n);
            (groups[tier] || groups.UNKNOWN).push(n);
        });
        return groups;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        getColorByMode: getNodeColorByMode,
        getSubsystem: getSubsystem,
        getPhase: getPhase,
        getFileType: getFileType,
        getRoleCategory: getRoleCategory,
        applyColors: applyNodeColors,
        applySizeMode: applyNodeSizeMode,
        getTierValue: getNodeTierValue,
        getDepth: getNodeDepth,
        getSemanticSimilarity: getSemanticSimilarity,
        groupByTier: groupNodesByTier
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.getNodeColorByMode = NODE_HELPERS.getColorByMode;
window.getSubsystem = NODE_HELPERS.getSubsystem;
window.getPhase = NODE_HELPERS.getPhase;
window.getFileType = NODE_HELPERS.getFileType;
window.getRoleCategory = NODE_HELPERS.getRoleCategory;
window.applyNodeColors = NODE_HELPERS.applyColors;
window.applyNodeSizeMode = NODE_HELPERS.applySizeMode;
window.getNodeTierValue = NODE_HELPERS.getTierValue;
window.getNodeDepth = NODE_HELPERS.getDepth;
window.getSemanticSimilarity = NODE_HELPERS.getSemanticSimilarity;
window.groupNodesByTier = NODE_HELPERS.groupByTier;

console.log('[Module] NODE_HELPERS loaded - 11 functions');
