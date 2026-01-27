/**
 * FILE VIZ CONTROLLER
 *
 * Thin orchestrator for file visualization modes.
 * Delegates to specialized modules:
 *   - FileColorModel: Color generation
 *   - LayoutForces: D3 physics manipulation
 *   - HullVisualizer: SDF-based boundary rendering
 *
 * DESIGN PRINCIPLE: This module coordinates, it does NOT implement.
 * All implementation details live in the delegated modules.
 *
 * @usage
 *   FILE_VIZ.setEnabled(true);
 *   FILE_VIZ.setMode('hulls');
 *   FILE_VIZ.apply();
 */

const FILE_VIZ = (function () {
    'use strict';

    // =========================================================================
    // CONSTANTS & MODES
    // =========================================================================

    const MODES = {
        OFF: 'off',
        COLOR: 'color',
        HULLS: 'hulls',
        MAP: 'map'
    };

    // =========================================================================
    // STATE (minimal - delegates to child modules)
    // =========================================================================

    let _enabled = false;
    let _mode = MODES.COLOR;
    let _colorModel = null;
    let _hullVisualizer = null;
    let _fileGraph = null;
    let _expandedFiles = new Set();
    let _graphMode = 'atoms'; // atoms | files

    // =========================================================================
    // INITIALIZATION
    // =========================================================================

    function _ensureColorModel() {
        if (!_colorModel && typeof FileColorModel !== 'undefined') {
            _colorModel = new FileColorModel({ strategy: 'golden-angle' });
        }
        return _colorModel;
    }

    function _ensureHullVisualizer() {
        if (!_hullVisualizer && typeof HullVisualizer !== 'undefined') {
            const scene = typeof Graph !== 'undefined' ? Graph.scene() : null;
            const renderer = typeof Graph !== 'undefined' ? Graph.renderer() : null;
            if (scene && renderer) {
                _hullVisualizer = new HullVisualizer(scene, renderer, {
                    blendFactor: 2.0,
                    opacity: 0.2
                });
            }
        }
        return _hullVisualizer;
    }

    // =========================================================================
    // COLOR FUNCTIONS (delegated to FileColorModel)
    // =========================================================================

    function getColor(fileIdx, totalFiles, fileName, lightnessOverride = null) {
        const model = _ensureColorModel();
        if (!model) {
            // Strict fallback: use COLOR engine if available, else neutral gray
            if (typeof COLOR !== 'undefined' && COLOR.toHex) {
                const hue = (fileIdx * 137.5) % 360;
                return COLOR.toHex({ h: hue, c: 0.18, l: 0.55 });
            }
            return '#888888';
        }

        const overrides = lightnessOverride ? { lightness: lightnessOverride } : {};
        return model.getColor(fileIdx, totalFiles, fileName, overrides);
    }

    function applyColors(graphNodes) {
        if (!_enabled || !graphNodes) return;

        // Check if UPB has active color bindings - defer to UPB if so
        const UPB = typeof window !== 'undefined' ? window.UPB : null;
        if (UPB && typeof UPB.hasColorBinding === 'function' && UPB.hasColorBinding()) {
            // UPB is handling colors - don't override
            console.log('[FILE_VIZ] Deferring to UPB for node colors');
            return;
        }

        const dm = typeof DM !== 'undefined' ? DM : null;
        const boundaries = dm ? dm.getFileBoundaries() : [];
        const totalFiles = boundaries.length;

        graphNodes.forEach(node => {
            if (node.fileIdx !== undefined && node.fileIdx >= 0) {
                const fileName = boundaries[node.fileIdx]?.file_name || '';
                node.color = getColor(node.fileIdx, totalFiles, fileName);
            }
        });
    }

    // =========================================================================
    // HULL FUNCTIONS (delegated to HullVisualizer)
    // =========================================================================

    function drawFileBoundaries(data) {
        const viz = _ensureHullVisualizer();
        if (!viz) {
            console.warn('[FILE_VIZ] HullVisualizer not available');
            return 0;
        }

        const dm = typeof DM !== 'undefined' ? DM : null;
        if (!dm) return 0;

        const nodes = dm.getNodes();
        const boundaries = dm.getFileBoundaries();

        // Group nodes by file
        const nodesByFile = new Map();
        nodes.forEach(node => {
            if (node.fileIdx === undefined || node.fileIdx < 0) return;
            if (!nodesByFile.has(node.fileIdx)) {
                nodesByFile.set(node.fileIdx, []);
            }
            nodesByFile.get(node.fileIdx).push(node);
        });

        // Color provider
        const colorProvider = (fileIdx, total) => {
            const fileName = boundaries[fileIdx]?.file_name || '';
            return getColor(fileIdx, total, fileName);
        };

        viz.update(nodesByFile, colorProvider);
        return nodesByFile.size;
    }

    function clearBoundaries() {
        if (_hullVisualizer) {
            _hullVisualizer.clear();
        }
    }

    // =========================================================================
    // PHYSICS FUNCTIONS (delegated to LayoutForces)
    // =========================================================================

    function applyClusterForce(data) {
        if (typeof LayoutForces === 'undefined' || typeof Graph === 'undefined') {
            return false;
        }

        const dm = typeof DM !== 'undefined' ? DM : null;
        if (!dm) return false;

        const nodes = dm.getNodes();
        const boundaries = dm.getFileBoundaries();

        // Compute file centroid targets
        const targets = new Map();
        const fileNodes = new Map();

        nodes.forEach(node => {
            if (node.fileIdx === undefined || node.fileIdx < 0) return;
            if (!fileNodes.has(node.fileIdx)) {
                fileNodes.set(node.fileIdx, []);
            }
            fileNodes.get(node.fileIdx).push(node);
        });

        // Create spiral layout for file groups
        const totalFiles = fileNodes.size;
        let fileIndex = 0;
        fileNodes.forEach((group, fileIdx) => {
            const angle = fileIndex * 2.4; // Golden angle
            const radius = 50 + fileIndex * 10;
            const target = {
                x: Math.cos(angle) * radius,
                y: Math.sin(angle) * radius,
                z: (fileIndex - totalFiles / 2) * 5
            };

            group.forEach(node => {
                targets.set(node.id, target);
            });
            fileIndex++;
        });

        return LayoutForces.applyClusterForce(Graph, nodes, targets);
    }

    function applyCohesion(data) {
        if (typeof LayoutForces === 'undefined' || typeof Graph === 'undefined') {
            return false;
        }

        const dm = typeof DM !== 'undefined' ? DM : null;
        if (!dm) return false;

        const nodes = dm.getNodes();
        const physicsConfig = dm.raw?.physics || {};

        return LayoutForces.applyCohesionForce(Graph, nodes, {
            strength: physicsConfig.fileCohesion || 0.3
        });
    }

    function clearCohesion() {
        if (typeof LayoutForces !== 'undefined' && typeof Graph !== 'undefined') {
            LayoutForces.clearForces(Graph);
        }
    }

    // =========================================================================
    // FILE GRAPH (map mode)
    // =========================================================================

    function buildFileGraph() {
        const dm = typeof DM !== 'undefined' ? DM : null;
        if (!dm) return null;

        const boundaries = dm.getFileBoundaries();
        const links = dm.getLinks();

        // Create file nodes
        const fileNodes = boundaries.map((boundary, idx) => ({
            id: `file:${idx}`,
            name: boundary.file_name || `File ${idx}`,
            fileIdx: idx,
            isFileNode: true,
            atomCount: boundary.atom_count || boundary.atom_indices?.length || 0,
            val: Math.max(1, Math.sqrt(boundary.atom_count || 1)),
            color: getColor(idx, boundaries.length, boundary.file_name),
            x: 0, y: 0, z: 0
        }));

        // Build file-to-file links from atom links
        const atomToFile = new Map();
        dm.getNodes().forEach(node => {
            if (node.fileIdx !== undefined && node.fileIdx >= 0) {
                atomToFile.set(node.id, node.fileIdx);
            }
        });

        const fileLinkCounts = new Map();
        links.forEach(link => {
            const srcFile = atomToFile.get(link.source?.id || link.source);
            const tgtFile = atomToFile.get(link.target?.id || link.target);

            if (srcFile !== undefined && tgtFile !== undefined && srcFile !== tgtFile) {
                const key = `${srcFile}-${tgtFile}`;
                fileLinkCounts.set(key, (fileLinkCounts.get(key) || 0) + 1);
            }
        });

        const fileLinks = [];
        fileLinkCounts.forEach((count, key) => {
            const [src, tgt] = key.split('-').map(Number);
            fileLinks.push({
                source: `file:${src}`,
                target: `file:${tgt}`,
                weight: count,
                opacity: Math.min(0.8, 0.1 + count * 0.05)
            });
        });

        _fileGraph = { nodes: fileNodes, links: fileLinks };
        return _fileGraph;
    }

    function applyFileGraphMode() {
        if (!_fileGraph) buildFileGraph();
        if (!_fileGraph || !Graph) return;  // Guard against null AND undefined

        Graph.graphData(_fileGraph);
        _graphMode = 'files';

        if (typeof showToast !== 'undefined') {
            showToast(`File Map: ${_fileGraph.nodes.length} files, ${_fileGraph.links.length} connections`);
        }

        // Enforce strict centering on Origin (0,0,0)
        if (Graph.d3Force) {
            Graph.d3Force('center', d3.forceCenter(0, 0, 0));
        }
    }

    // =========================================================================
    // MODE APPLICATION
    // =========================================================================

    function apply() {
        if (!_enabled) {
            clearBoundaries();
            clearCohesion();
            return;
        }

        const dm = typeof DM !== 'undefined' ? DM : null;
        if (!dm) return;

        switch (_mode) {
            case MODES.COLOR:
                clearBoundaries();
                applyColors(dm.getNodes());
                if (typeof refreshGraph !== 'undefined') refreshGraph();
                break;

            case MODES.HULLS:
                applyColors(dm.getNodes());
                applyCohesion();
                drawFileBoundaries();
                break;

            case MODES.MAP:
                clearBoundaries();
                applyFileGraphMode();
                break;

            case MODES.OFF:
            default:
                clearBoundaries();
                clearCohesion();
                break;
        }
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    function setEnabled(enabled) {
        _enabled = !!enabled;
        apply();

        // Update UI if available
        const btn = document.getElementById('cmd-files');
        if (btn) {
            btn.classList.toggle('active', _enabled);
        }
    }

    function toggle() {
        setEnabled(!_enabled);
        return _enabled;
    }

    function setMode(mode) {
        if (!MODES[mode.toUpperCase()] && !Object.values(MODES).includes(mode)) {
            console.warn(`[FILE_VIZ] Unknown mode: ${mode}`);
            return;
        }
        _mode = mode.toLowerCase();
        if (_enabled) apply();
    }

    function isEnabled() { return _enabled; }
    function getMode() { return _mode; }
    function getFileGraph() { return _fileGraph; }
    function getExpandedFiles() { return _expandedFiles; }

    // =========================================================================
    // CLEANUP
    // =========================================================================

    function dispose() {
        clearBoundaries();
        clearCohesion();
        if (_hullVisualizer) {
            _hullVisualizer.dispose();
            _hullVisualizer = null;
        }
        _colorModel = null;
        _fileGraph = null;
        _expandedFiles.clear();
    }

    // =========================================================================
    // RETURN PUBLIC API
    // =========================================================================

    return {
        // Mode control
        setEnabled,
        toggle,
        setMode,
        apply,

        // Color functions
        getColor,
        applyColors,

        // Hull functions
        drawFileBoundaries,
        clearBoundaries,

        // Physics
        applyClusterForce,
        applyCohesion,
        clearCohesion,

        // File graph
        buildFileGraph,
        buildUnifiedGraph: function() {
            const dm = typeof DM !== 'undefined' ? DM : (typeof DATA !== 'undefined' ? DATA : null);
            if (!dm || !dm.getUnifiedGraph) return null;
            return dm.getUnifiedGraph();
        },

        // Getters
        isEnabled,
        getMode,
        getFileGraph,
        getExpandedFiles,

        // Cleanup
        dispose,

        // Constants
        MODES
    };
})();

// Register globally
if (typeof window !== 'undefined') {
    window.FILE_VIZ = FILE_VIZ;
    // Backward compat aliases
    window.drawFileBoundaries = FILE_VIZ.drawFileBoundaries;
    window.getColorForMapping = FILE_VIZ.getColor;
    // Global getter for EXPANDED_FILES (read-only, like SELECTED_NODE_IDS)
    Object.defineProperty(window, 'EXPANDED_FILES', {
        get: () => FILE_VIZ.getExpandedFiles(),
        configurable: true
    });
}
