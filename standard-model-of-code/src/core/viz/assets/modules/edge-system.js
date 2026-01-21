/**
 * EDGE SYSTEM MODULE
 *
 * Manages edge coloring, width, modes, and gradient effects.
 * Includes gradient palettes for tier, file, flow, depth, and semantic modes.
 *
 * Depends on: COLOR (for type-based colors), NODE (for tier lookups)
 *
 * Usage:
 *   EDGE.getColor(link)           // Get color for a link
 *   EDGE.getWidth(link)           // Get width for a link
 *   EDGE.setMode('gradient-tier') // Change edge mode
 *   EDGE.apply()                  // Apply current mode to graph
 */

const EDGE = (function() {
    'use strict';

    // =========================================================================
    // CONSTANTS
    // =========================================================================

    const MODE_ORDER = [
        'gradient-tier',      // Source→Target tier flow (architecture layers)
        'gradient-file',      // File boundaries (module regions)
        'gradient-flow',      // Markov probability (hot paths)
        'gradient-depth',     // Call depth progression
        'gradient-semantic',  // Semantic distance (type similarity)
        'type',               // Classic type-based
        'weight',             // Weight intensity
        'mono'                // Minimal monochrome
    ];

    const MODE_LABELS = {
        'gradient-tier': '▼ TIER FLOW',
        'gradient-file': '▼ FILE REGIONS',
        'gradient-flow': '▼ HOT PATHS',
        'gradient-depth': '▼ CALL DEPTH',
        'gradient-semantic': '▼ SEMANTIC',
        type: 'EDGE: TYPE',
        weight: 'EDGE: WEIGHT',
        mono: 'EDGE: MONO'
    };

    const MODE_HINTS = {
        'gradient-tier': 'Gradient by architecture tier (T0→T1→T2)',
        'gradient-file': 'Color by file region - shows module boundaries',
        'gradient-flow': 'Hot paths - markov probability gradient',
        'gradient-depth': 'Color by call chain depth',
        'gradient-semantic': 'Color by semantic similarity of endpoints',
        type: 'Edge color by type (calls, imports, etc.)',
        weight: 'Edge width & color by weight',
        mono: 'Minimal monochrome'
    };

    // Gradient color palettes for different modes
    const PALETTES = {
        tier: {
            // Cool to Warm: Entry (blue) → Core (purple) → Exit (orange)
            T0: { h: 210, s: 70, l: 55 },  // Blue - entry points
            T1: { h: 280, s: 65, l: 50 },  // Purple - core logic
            T2: { h: 30, s: 80, l: 50 },   // Orange - utilities/exit
            UNKNOWN: { h: 0, s: 0, l: 40 } // Gray
        },
        file: {
            // Rainbow hues distributed across files
            saturation: 65,
            lightness: 48
        },
        flow: {
            // Cold (low prob) to Hot (high prob)
            cold: { h: 220, s: 60, l: 45 },   // Blue
            warm: { h: 45, s: 85, l: 50 },    // Yellow
            hot: { h: 0, s: 90, l: 55 }       // Red
        },
        depth: {
            // Shallow (bright) to Deep (dark, saturated)
            shallow: { h: 180, s: 50, l: 65 },  // Light cyan
            mid: { h: 260, s: 70, l: 50 },      // Purple
            deep: { h: 320, s: 80, l: 40 }      // Magenta
        },
        semantic: {
            // Similar (harmonious) to Different (contrasting)
            similar: { h: 150, s: 60, l: 50 },    // Green - same type
            related: { h: 200, s: 65, l: 48 },    // Cyan - related
            different: { h: 340, s: 75, l: 50 }   // Pink - different
        }
    };

    const DEFAULT_OPACITY = 0.08;
    const INFERRED_OPACITY = 0.04;  // Lower opacity for inferred edges
    const MIN_WIDTH = 0.6;
    const MAX_WIDTH = 2.2;
    const BASE_WIDTH = 1.0;
    const DASH_PATTERN = [5, 5];   // Dashed line pattern for inferred edges

    // =========================================================================
    // STATE
    // =========================================================================

    let _mode = 'gradient-file';  // Default mode
    let _ranges = { weight: { min: 1, max: 1 }, confidence: { min: 1, max: 1 } };
    let _nodeFileIndex = new Map();
    let _fileHueMap = new Map();
    let _config = {
        opacity: DEFAULT_OPACITY,
        dim: { interfile_factor: 0.25 }
    };

    // =========================================================================
    // UTILITY FUNCTIONS
    // =========================================================================

    /**
     * Check if an edge is inferred (from CODOME boundaries).
     * Inferred edges are marked with:
     *   - inferred: true
     *   - family: 'Codome'
     *   - _fromCodome: true
     */
    function isInferredEdge(link) {
        return link?.inferred === true ||
               link?.family === 'Codome' ||
               link?._fromCodome === true;
    }

    function clamp01(value) {
        return Math.max(0, Math.min(1, value));
    }

    function hslColor(hue, saturation, lightness) {
        return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    }

    function interpolateHSL(hsl1, hsl2, t) {
        t = clamp01(t);
        // Handle hue interpolation (shortest path on color wheel)
        let h1 = hsl1.h, h2 = hsl2.h;
        let dh = h2 - h1;
        if (Math.abs(dh) > 180) {
            if (dh > 0) h1 += 360;
            else h2 += 360;
        }
        const h = (h1 + (h2 - h1) * t) % 360;
        const s = hsl1.s + (hsl2.s - hsl1.s) * t;
        const l = hsl1.l + (hsl2.l - hsl1.l) * t;
        return hslColor(h, s, l);
    }

    /**
     * Normalize a metric value to [0,1] range.
     * NOW DELEGATES TO UPB_SCALES when available.
     */
    function normalizeMetric(value, range, scaleName) {
        // If range is degenerate (all same values), return based on absolute value
        if (!range || range.max <= range.min) {
            return clamp01(value);
        }

        // === UPB INTEGRATION ===
        if (window.UPB_SCALES) {
            return window.UPB_SCALES.applyScale(
                scaleName || 'linear',
                value,
                range.min,
                range.max
            );
        }

        // Fallback: inline linear normalization
        return clamp01((value - range.min) / (range.max - range.min));
    }

    // =========================================================================
    // NODE HELPERS (use canonical versions from node-helpers.js via window.*)
    // =========================================================================

    function getLinkFileIdx(link, side) {
        const endpoint = link?.[side];
        if (endpoint && typeof endpoint === 'object') {
            return endpoint.fileIdx ?? -1;
        }
        if (endpoint) {
            return _nodeFileIndex.get(endpoint) ?? -1;
        }
        return -1;
    }

    // =========================================================================
    // FILE HUE MAP
    // =========================================================================

    function buildFileHueMap() {
        _fileHueMap.clear();
        // Try DATA module first, then DM global
        const dm = typeof DATA !== 'undefined' ? DATA :
                   (typeof DM !== 'undefined' ? DM : null);
        if (!dm || !dm.getFileBoundaries) return;

        const files = dm.getFileBoundaries();
        const goldenAngle = 137.508;  // Golden angle for good distribution
        files.forEach((file, idx) => {
            const hue = (idx * goldenAngle) % 360;
            _fileHueMap.set(idx, hue);
        });
    }

    // =========================================================================
    // RANGE UPDATES
    // =========================================================================

    function updateRanges() {
        const links = (typeof Graph !== 'undefined' && Graph?.graphData()?.links) || [];
        let minWeight = Infinity, maxWeight = -Infinity;
        let minConf = Infinity, maxConf = -Infinity;

        links.forEach(link => {
            const weight = typeof link.weight === 'number' ? link.weight : 1;
            const confidence = typeof link.confidence === 'number' ? link.confidence : 1;
            minWeight = Math.min(minWeight, weight);
            maxWeight = Math.max(maxWeight, weight);
            minConf = Math.min(minConf, confidence);
            maxConf = Math.max(maxConf, confidence);
        });

        _ranges = {
            weight: {
                min: isFinite(minWeight) ? minWeight : 1,
                max: isFinite(maxWeight) ? maxWeight : 1
            },
            confidence: {
                min: isFinite(minConf) ? minConf : 1,
                max: isFinite(maxConf) ? maxConf : 1
            }
        };
    }

    function refreshNodeFileIndex() {
        _nodeFileIndex.clear();
        const nodes = (typeof Graph !== 'undefined' && Graph?.graphData()?.nodes) || [];
        nodes.forEach(node => {
            if (node && node.id) {
                _nodeFileIndex.set(node.id, node.fileIdx ?? -1);
            }
        });
    }

    // =========================================================================
    // GRADIENT EDGE COLOR
    // =========================================================================

    function getGradientColor(link, mode) {
        const srcNode = typeof link.source === 'object' ? link.source :
            (typeof Graph !== 'undefined' ? Graph?.graphData()?.nodes?.find(n => n.id === link.source) : null);
        const tgtNode = typeof link.target === 'object' ? link.target :
            (typeof Graph !== 'undefined' ? Graph?.graphData()?.nodes?.find(n => n.id === link.target) : null);

        if (mode === 'gradient-tier') {
            const srcTier = window.getNodeTierValue(srcNode);
            const tgtTier = window.getNodeTierValue(tgtNode);
            const avgTier = (srcTier + tgtTier) / 2;

            const palette = PALETTES.tier;
            let color;
            if (avgTier < 0.5) {
                color = interpolateHSL(palette.T0, palette.T1, avgTier * 2);
            } else if (avgTier < 1.5) {
                color = interpolateHSL(palette.T0, palette.T1, (avgTier - 0.5));
            } else {
                color = interpolateHSL(palette.T1, palette.T2, (avgTier - 1) / 2);
            }

            // Highlight tier transitions (edges crossing tiers)
            if (srcTier !== tgtTier) {
                return hslColor(
                    parseInt(color.slice(4)),
                    75,  // Higher saturation
                    55   // Brighter
                );
            }
            return color;
        }

        if (mode === 'gradient-file') {
            const srcFile = srcNode?.fileIdx ?? -1;
            const tgtFile = tgtNode?.fileIdx ?? -1;
            const palette = PALETTES.file;

            if (srcFile === tgtFile && srcFile >= 0) {
                const hue = _fileHueMap.get(srcFile) ?? (srcFile * 37 % 360);
                return hslColor(hue, palette.saturation, palette.lightness);
            } else {
                const srcHue = _fileHueMap.get(srcFile) ?? 0;
                const tgtHue = _fileHueMap.get(tgtFile) ?? 180;
                let midHue = (srcHue + tgtHue) / 2;
                if (Math.abs(srcHue - tgtHue) > 180) {
                    midHue = (midHue + 180) % 360;
                }
                return hslColor(midHue, palette.saturation * 0.6, palette.lightness * 1.1);
            }
        }

        if (mode === 'gradient-flow') {
            const mw = link.markov_weight ?? link.weight ?? 0;
            const palette = PALETTES.flow;

            if (mw < 0.3) {
                return interpolateHSL(palette.cold, palette.warm, mw / 0.3);
            } else if (mw < 0.7) {
                return interpolateHSL(palette.warm, palette.hot, (mw - 0.3) / 0.4);
            } else {
                return hslColor(palette.hot.h, palette.hot.s + 10, palette.hot.l + 10);
            }
        }

        if (mode === 'gradient-depth') {
            const srcDepth = window.getNodeDepth(srcNode);
            const tgtDepth = window.getNodeDepth(tgtNode);
            const avgDepth = (srcDepth + tgtDepth) / 2;
            const palette = PALETTES.depth;

            if (avgDepth < 0.33) {
                return interpolateHSL(palette.shallow, palette.mid, avgDepth * 3);
            } else if (avgDepth < 0.66) {
                return interpolateHSL(palette.mid, palette.deep, (avgDepth - 0.33) * 3);
            } else {
                return hslColor(palette.deep.h, palette.deep.s, palette.deep.l - 10);
            }
        }

        if (mode === 'gradient-semantic') {
            const similarity = window.getSemanticSimilarity(srcNode, tgtNode);
            const palette = PALETTES.semantic;

            if (similarity > 0.7) {
                return interpolateHSL(palette.related, palette.similar, (similarity - 0.7) / 0.3);
            } else if (similarity > 0.3) {
                return interpolateHSL(palette.different, palette.related, (similarity - 0.3) / 0.4);
            } else {
                return hslColor(palette.different.h, palette.different.s + 10, palette.different.l);
            }
        }

        return '#444444';
    }

    // =========================================================================
    // MAIN COLOR FUNCTION
    // =========================================================================

    function getColor(link) {
        // Check if UPB has edge color bindings - defer to UPB if so
        const UPB = typeof window !== 'undefined' ? window.UPB : null;
        if (UPB && typeof UPB.hasEdgeBinding === 'function' && UPB.hasEdgeBinding()) {
            // UPB handles edge colors - return null to signal deference
            return null;
        }

        // Gradient modes
        if (_mode.startsWith('gradient-')) {
            return getGradientColor(link, _mode);
        }

        const edgeKey = String(link.edge_type || link.type || 'unknown').toLowerCase();

        if (_mode === 'type') {
            return typeof COLOR !== 'undefined' ?
                COLOR.get('edgeType', edgeKey) : '#666666';
        }

        if (_mode === 'weight') {
            const weight = typeof link.weight === 'number' ? link.weight : 1;
            const t = normalizeMetric(weight, _ranges.weight);
            return typeof COLOR !== 'undefined' ?
                COLOR.getInterval('weight', t) : hslColor(30, 70, 50 + t * 30);
        }

        if (_mode === 'confidence') {
            const confidence = typeof link.confidence === 'number' ? link.confidence : 1;
            const t = normalizeMetric(confidence, _ranges.confidence);
            return typeof COLOR !== 'undefined' ?
                COLOR.getInterval('confidence', t) : hslColor(200, 70, 50 + t * 30);
        }

        if (_mode === 'mono') {
            return typeof COLOR !== 'undefined' ?
                COLOR.get('edgeType', 'unknown') : '#555555';
        }

        // Default: type-based coloring
        return typeof COLOR !== 'undefined' ?
            COLOR.get('edgeType', edgeKey) : '#666666';
    }

    // =========================================================================
    // EDGE WIDTH
    // =========================================================================

    function getWidth(link) {
        // For most modes, return uniform width for visual consistency
        if (_mode !== 'weight' && _mode !== 'confidence') {
            return BASE_WIDTH;
        }

        // Weight/confidence modes: subtle variation within tight bounds
        let t = 0.5;
        if (_mode === 'weight') {
            const weight = typeof link.weight === 'number' ? link.weight : 1;
            t = normalizeMetric(weight, _ranges.weight);
        } else if (_mode === 'confidence') {
            const confidence = typeof link.confidence === 'number' ? link.confidence : 1;
            t = normalizeMetric(confidence, _ranges.confidence);
        }

        return MIN_WIDTH + (t * (MAX_WIDTH - MIN_WIDTH));
    }

    // =========================================================================
    // EDGE LINE DASH (for inferred edges)
    // =========================================================================

    function getLineDash(link) {
        // Return dashed pattern for inferred CODOME edges
        if (isInferredEdge(link)) {
            return DASH_PATTERN;  // [5, 5] = 5px dash, 5px gap
        }
        return null;  // Solid line for regular edges
    }

    // =========================================================================
    // APPLY MODE TO GRAPH
    // =========================================================================

    function apply() {
        updateRanges();
        refreshNodeFileIndex();
        buildFileHueMap();

        if (typeof Graph === 'undefined' || !Graph) return;

        Graph.linkColor(link => {
            const color = getColor(link);
            return typeof toColorNumber === 'function' ?
                toColorNumber(color, 0x222222) : color;
        });

        Graph.linkOpacity(link => {
            const overrideOpacity = (typeof APPEARANCE_STATE !== 'undefined' &&
                typeof APPEARANCE_STATE.edgeOpacity === 'number')
                ? APPEARANCE_STATE.edgeOpacity
                : null;
            const baseOpacity = (overrideOpacity !== null)
                ? overrideOpacity
                : (link.opacity ?? DEFAULT_OPACITY);

            // Inferred edges have lower base opacity
            let opacity = isInferredEdge(link) ? INFERRED_OPACITY : baseOpacity;

            // File mode dimming
            const fileMode = typeof window !== 'undefined' && window.fileMode;
            const graphMode = typeof GRAPH_MODE !== 'undefined' ? GRAPH_MODE : 'atoms';
            if (fileMode && graphMode === 'atoms') {
                const srcIdx = getLinkFileIdx(link, 'source');
                const tgtIdx = getLinkFileIdx(link, 'target');
                if (srcIdx >= 0 && tgtIdx >= 0 && srcIdx !== tgtIdx) {
                    const dimFactor = _config.dim?.interfile_factor ?? 0.25;
                    return opacity * dimFactor;
                }
            }
            return opacity;
        });

        // Apply dashed line pattern to inferred CODOME edges
        Graph.linkLineDash(link => getLineDash(link));

        // Don't override width in flow mode
        const flowMode = typeof window !== 'undefined' && window.flowMode;
        if (!flowMode) {
            Graph.linkWidth(link => {
                const baseWidth = getWidth(link);
                // Respect APPEARANCE_STATE.edgeWidth multiplier if set
                const widthMultiplier = (typeof APPEARANCE_STATE !== 'undefined' &&
                    typeof APPEARANCE_STATE.edgeWidth === 'number')
                    ? APPEARANCE_STATE.edgeWidth
                    : 1;
                return Math.max(0.5, baseWidth * widthMultiplier);
            });
        }
    }

    // =========================================================================
    // MODE MANAGEMENT
    // =========================================================================

    function setMode(mode) {
        if (!MODE_ORDER.includes(mode)) return;
        _mode = mode;

        const button = document.getElementById('btn-edge-mode');
        if (button) {
            button.textContent = MODE_LABELS[_mode] || 'EDGE';
        }

        apply();

        // Update legend to reflect edge mode colors
        if (typeof renderAllLegends === 'function') {
            renderAllLegends();
        }

        // Show mode toast hint
        if (typeof showModeToast === 'function') {
            showModeToast(MODE_HINTS[mode] || `Edge mode: ${mode}`);
        }
    }

    function cycleMode() {
        const currentIndex = MODE_ORDER.indexOf(_mode);
        const nextIndex = (currentIndex + 1) % MODE_ORDER.length;
        setMode(MODE_ORDER[nextIndex]);
    }

    function setConfig(config) {
        _config = { ..._config, ...config };
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Core functions
        getColor,
        getWidth,
        getLineDash,
        apply,

        // Mode management
        setMode,
        cycleMode,
        get mode() { return _mode; },

        // Configuration
        setConfig,
        get config() { return _config; },

        // Constants
        MODE_ORDER,
        MODE_LABELS,
        MODE_HINTS,
        PALETTES,

        // Internal access (for migration)
        get ranges() { return _ranges; },
        get nodeFileIndex() { return _nodeFileIndex; },
        get fileHueMap() { return _fileHueMap; },

        // Utility exports
        buildFileHueMap,
        updateRanges,
        refreshNodeFileIndex,
        isInferredEdge
    };
})();

// Backward compatibility aliases - Using Object.defineProperty to avoid duplicate declarations
// These create getters/setters that sync with EDGE module state
Object.defineProperty(window, 'EDGE_MODE', {
    get: () => EDGE.mode,
    set: (v) => EDGE.setMode(v),
    configurable: true
});
Object.defineProperty(window, 'EDGE_RANGES', {
    get: () => EDGE.ranges,
    configurable: true
});
Object.defineProperty(window, 'NODE_FILE_INDEX', {
    get: () => EDGE.nodeFileIndex,
    configurable: true
});
Object.defineProperty(window, 'FILE_HUE_MAP', {
    get: () => EDGE.fileHueMap,
    configurable: true
});
// Static constants - app.js owns these, not duplicated here
// EDGE_MODE_ORDER, EDGE_MODE_LABELS, EDGE_MODE_HINTS, GRADIENT_PALETTES - defined in app.js

function getEdgeColor(link) { return EDGE.getColor(link); }
function getEdgeWidth(link) { return EDGE.getWidth(link); }
function getEdgeLineDash(link) { return EDGE.getLineDash(link); }
function isInferredEdgeGlobal(link) { return EDGE.isInferredEdge(link); }
function applyEdgeMode() { EDGE.apply(); }
function setEdgeMode(mode) { EDGE.setMode(mode); }
function cycleEdgeMode() { EDGE.cycleMode(); }
function updateEdgeRanges() { EDGE.updateRanges(); }
function refreshNodeFileIndex() { EDGE.refreshNodeFileIndex(); }
function buildFileHueMap() { EDGE.buildFileHueMap(); }
function getGradientEdgeColor(link, mode) { return EDGE.getColor(link); }
