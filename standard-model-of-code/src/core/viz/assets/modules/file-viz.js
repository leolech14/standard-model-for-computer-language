/**
 * FILE VIZ MODULE
 *
 * Manages file visualization modes: color, hulls, cluster, map, spheres.
 * Handles file coloring, boundaries, mode switching, and FILE GRAPH.
 *
 * FILE GRAPH: Shows repository structure as first-class nodes where each
 * file becomes a hoverable, selectable node. This provides:
 * - Clear view of the repository file system
 * - Hover to see file details (atom count, path, metrics)
 * - Click to expand and see atoms within
 * - Edge weights show inter-file dependencies
 *
 * Depends on: DATA (for file boundaries), COLOR (for transforms)
 *
 * Pattern: IIFE with State Unification (see docs/specs/VISUALIZATION_UI_SPEC.md)
 *
 * Usage:
 *   FILE_VIZ.setMode('map')          // Switch to file-nodes view
 *   FILE_VIZ.toggle()                // Toggle file mode on/off
 *   FILE_VIZ.getColor(idx, total)    // Get color for a file
 *   FILE_VIZ.buildFileGraph()        // Build file-level graph
 *   FILE_VIZ.apply()                 // Apply current mode
 */

const FILE_VIZ = (function() {
    'use strict';

    // =========================================================================
    // CONSTANTS
    // =========================================================================

    const MODES = ['color', 'hulls', 'cluster', 'map', 'spheres'];

    const MODE_HINTS = {
        color: 'Files colored by hue - each file gets unique color',
        hulls: 'Boundary hulls around file clusters',
        cluster: 'Force clustering groups files together',
        map: 'FILE NODES view - see repository structure as nodes! Click to expand.',
        spheres: 'Containment spheres with collision physics'
    };

    // =========================================================================
    // STATE
    // =========================================================================

    let _enabled = false;
    let _mode = 'color';
    let _config = {
        strategy: 'golden-angle',
        angle: 137.5,
        chroma: null,
        saturation: 70,
        lightness: 50
    };
    let _boundaryMeshes = [];
    let _hullRedrawTimer = null;
    let _hullRedrawAttempts = 0;

    // FILE GRAPH STATE - for file-as-nodes visualization
    let _fileGraph = null;          // { nodes: [], links: [] } for file-level view
    let _fileNodeIds = new Map();   // fileIdx -> nodeId mapping
    let _fileNodePositions = new Map(); // Preserve positions across mode switches
    let _expandedFiles = new Set(); // Files expanded to show atoms
    let _graphMode = 'atoms';       // atoms | files | hybrid
    let _expandMode = 'inline';     // inline | detach
    let _activeMapping = 'format';  // Current visual mapping mode

    // =========================================================================
    // VISUAL MAPPING SYSTEM - Map metadata to visual properties
    // =========================================================================

    /**
     * Visual dimension mappings - connect file metadata to visual properties.
     * Each mapping defines: source metadata field → visual property + scale
     */
    const VISUAL_MAPPINGS = {
        // Size-based mappings
        size_bytes: {
            property: 'nodeSize',
            scale: 'sqrt',
            min: 2,
            max: 20,
            label: 'File Size (bytes)'
        },
        token_estimate: {
            property: 'nodeSize',
            scale: 'log',
            min: 2,
            max: 18,
            label: 'Token Count'
        },
        line_count: {
            property: 'nodeSize',
            scale: 'sqrt',
            min: 2,
            max: 15,
            label: 'Line Count'
        },

        // Time-based mappings
        age_days: {
            property: 'opacity',
            scale: 'linear',
            invert: true,  // Older = more faded
            min: 0.3,
            max: 1.0,
            label: 'File Age'
        },

        // Categorical mappings (discrete colors)
        format_category: {
            property: 'hue',
            discrete: true,
            values: {
                code:   210,  // Blue - primary code
                config: 45,   // Orange - configuration
                doc:    120,  // Green - documentation
                data:   280,  // Purple - data files
                test:   340,  // Pink - test files
                style:  180,  // Cyan - stylesheets
                script: 30,   // Yellow-Orange - scripts
                build:  0,    // Red - build files
                other:  0     // Gray (handled by saturation)
            },
            label: 'File Format'
        },
        purpose: {
            property: 'hue',
            discrete: true,
            values: {
                test:       340,  // Pink
                config:     45,   // Orange
                model:      260,  // Purple
                service:    210,  // Blue
                controller: 180,  // Cyan
                utility:    90,   // Yellow-Green
                interface:  300,  // Magenta
                data:       30,   // Orange-Yellow
                general:    200   // Light Blue
            },
            label: 'File Purpose'
        },

        // Complexity mappings
        complexity_density: {
            property: 'saturation',
            scale: 'linear',
            min: 30,
            max: 90,
            label: 'Complexity'
        },
        cohesion: {
            property: 'lightness',
            scale: 'linear',
            min: 35,
            max: 65,
            label: 'Cohesion'
        },

        // Git mappings (if available)
        git_commits: {
            property: 'pulse',  // Animation intensity
            scale: 'log',
            min: 0,
            max: 1,
            label: 'Git Commits'
        }
    };

    /**
     * Apply a visual mapping to file nodes.
     * @param {string} mappingKey - Key from VISUAL_MAPPINGS
     * @param {Array} fileNodes - Array of file node objects
     */
    function applyVisualMapping(mappingKey, fileNodes) {
        const mapping = VISUAL_MAPPINGS[mappingKey];
        if (!mapping) {
            console.warn(`[FILE_VIZ] Unknown mapping: ${mappingKey}`);
            return;
        }

        _activeMapping = mappingKey;

        // Get data range for normalization
        const values = fileNodes.map(n => n[mappingKey]).filter(v => v !== undefined && v !== null);
        if (values.length === 0) {
            console.warn(`[FILE_VIZ] No data for mapping: ${mappingKey}`);
            return;
        }

        const dataMin = Math.min(...values);
        const dataMax = Math.max(...values);

        fileNodes.forEach(node => {
            const rawValue = node[mappingKey];
            if (rawValue === undefined || rawValue === null) return;

            if (mapping.discrete) {
                // Categorical mapping
                const discreteValue = mapping.values[rawValue] ?? mapping.values['other'] ?? 0;
                _applyVisualProperty(node, mapping.property, discreteValue);
            } else {
                // Continuous mapping
                let normalized = _normalizeValue(rawValue, dataMin, dataMax, mapping.scale);
                if (mapping.invert) normalized = 1 - normalized;

                const visualMin = mapping.min ?? 0;
                const visualMax = mapping.max ?? 1;
                const visualValue = visualMin + normalized * (visualMax - visualMin);

                _applyVisualProperty(node, mapping.property, visualValue);
            }
        });

        console.log(`[FILE_VIZ] Applied mapping: ${mappingKey} (${mapping.label})`);
    }

    function _normalizeValue(value, min, max, scale) {
        if (max === min) return 0.5;

        let normalized;
        switch (scale) {
            case 'log':
                const logMin = Math.log10(Math.max(1, min));
                const logMax = Math.log10(Math.max(1, max));
                const logVal = Math.log10(Math.max(1, value));
                normalized = (logVal - logMin) / (logMax - logMin);
                break;
            case 'sqrt':
                const sqrtMin = Math.sqrt(min);
                const sqrtMax = Math.sqrt(max);
                const sqrtVal = Math.sqrt(value);
                normalized = (sqrtVal - sqrtMin) / (sqrtMax - sqrtMin);
                break;
            default: // linear
                normalized = (value - min) / (max - min);
        }
        return Math.max(0, Math.min(1, normalized));
    }

    function _applyVisualProperty(node, property, value) {
        switch (property) {
            case 'nodeSize':
                node.val = value;
                break;
            case 'hue':
                // Rebuild color with new hue
                const sat = _config.saturation ?? 70;
                const light = _config.lightness ?? 50;
                node.color = hslColor(value, sat, light);
                break;
            case 'saturation':
                // Would need to parse existing color - simplified approach
                node._saturation = value;
                break;
            case 'lightness':
                node._lightness = value;
                break;
            case 'opacity':
                node._opacity = value;
                break;
            case 'pulse':
                node._pulseIntensity = value;
                break;
        }
    }

    /**
     * Get color for file based on active mapping or default
     */
    function getColorForMapping(node) {
        const mapping = VISUAL_MAPPINGS[_activeMapping];
        if (!mapping || mapping.property !== 'hue') {
            // Use default golden angle coloring
            return getColor(node.fileIdx, 100, node.file_name);
        }

        const rawValue = node[_activeMapping];
        if (rawValue === undefined || !mapping.discrete) {
            return getColor(node.fileIdx, 100, node.file_name);
        }

        const hue = mapping.values[rawValue] ?? 200;
        const sat = node._saturation ?? (_config.saturation ?? 70);
        const light = node._lightness ?? (_config.lightness ?? 50);
        return hslColor(hue, sat, light);
    }

    // =========================================================================
    // COLOR UTILITIES
    // =========================================================================

    function clampValue(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    function hslColor(hue, saturation, lightness) {
        return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    }

    function hashToUnit(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash = hash & hash;
        }
        return Math.abs(hash % 1000) / 1000;
    }

    function getHue(fileIdx, totalFiles, fileName) {
        const strategy = _config.strategy || 'golden-angle';
        if (strategy === 'sequential') {
            const denom = Math.max(1, totalFiles);
            return (fileIdx / denom) * 360;
        }
        if (strategy === 'hash') {
            const seed = fileName || String(fileIdx);
            return hashToUnit(seed) * 360;
        }
        const angle = _config.angle ?? 137.5;
        return (fileIdx * angle) % 360;
    }

    // =========================================================================
    // MAIN COLOR FUNCTION
    // =========================================================================

    function getColor(fileIdx, totalFiles, fileName, lightnessOverride = null) {
        const saturation = _config.saturation ?? 70;
        const lightness = (lightnessOverride !== null)
            ? lightnessOverride
            : (_config.lightness ?? 50);
        const hue = getHue(fileIdx, totalFiles, fileName);

        // Apply color tweaks if available
        const tweaks = typeof COLOR_TWEAKS !== 'undefined' ? COLOR_TWEAKS : {};

        if (typeof _config.chroma === 'number' && typeof oklchColor === 'function') {
            return oklchColor(lightness, _config.chroma, hue);
        }

        const adjustedHue = hue + (tweaks.hueShift || 0);
        const adjustedLightness = clampValue(lightness + (tweaks.lightnessShift || 0), 0, 100);
        return hslColor(adjustedHue, saturation, adjustedLightness);
    }

    // =========================================================================
    // APPLY COLORS TO NODES
    // =========================================================================

    function applyColors(graphNodes) {
        // Get file boundaries from DATA module or DM global
        const dm = typeof DATA !== 'undefined' ? DATA :
                   (typeof DM !== 'undefined' ? DM : null);
        const boundaries = dm?.getFileBoundaries ? dm.getFileBoundaries() : [];
        const totalFiles = boundaries.length;

        graphNodes.forEach(node => {
            if (node.fileIdx >= 0) {
                const fileInfo = boundaries[node.fileIdx] || {};
                const fileLabel = fileInfo.file || fileInfo.file_name || node.fileIdx;
                node.color = getColor(node.fileIdx, totalFiles, fileLabel);
            }
        });

        if (typeof Graph !== 'undefined' && Graph) {
            Graph.nodeColor(n => {
                return typeof toColorNumber === 'function' ?
                    toColorNumber(n.color, 0x888888) : n.color;
            });
        }
    }

    // =========================================================================
    // FILE GRAPH BUILDING - Repository as Nodes
    // =========================================================================

    /**
     * Build a file-level graph where each file is a node.
     * This creates a clear view of repository structure with:
     * - File nodes sized by atom count
     * - Edges weighted by inter-file dependencies
     * - Colors by file index (golden angle distribution)
     */
    function buildFileGraph() {
        const dm = typeof DATA !== 'undefined' ? DATA :
                   (typeof DM !== 'undefined' ? DM : null);
        const boundaries = dm?.getFileBoundaries ? dm.getFileBoundaries() : [];
        const nodes = dm?.getNodes ? dm.getNodes() : [];
        const links = dm?.getLinks ? dm.getLinks() : [];

        // Get current atom positions from Graph for centroid calculation
        const currentGraphNodes = (typeof Graph !== 'undefined' && Graph)
            ? (Graph.graphData()?.nodes || [])
            : [];
        const atomPositions = new Map();
        currentGraphNodes.forEach(n => {
            if (n && n.id && Number.isFinite(n.x) && Number.isFinite(n.y)) {
                atomPositions.set(n.id, { x: n.x, y: n.y, z: n.z || 0 });
            }
        });

        const totalFiles = boundaries.length;
        const fileNodes = [];
        _fileNodeIds.clear();
        const nodeFileIdx = new Map();

        // Build node -> fileIdx mapping
        nodes.forEach(n => {
            if (n && n.id) {
                nodeFileIdx.set(n.id, n.fileIdx ?? -1);
            }
        });

        // Build file -> atoms mapping for centroid calculation
        const fileAtoms = new Map(); // fileIdx -> [atom positions]
        nodes.forEach(n => {
            if (n && n.id && n.fileIdx !== undefined && n.fileIdx >= 0) {
                const pos = atomPositions.get(n.id);
                if (pos) {
                    if (!fileAtoms.has(n.fileIdx)) fileAtoms.set(n.fileIdx, []);
                    fileAtoms.get(n.fileIdx).push(pos);
                }
            }
        });

        // Create file nodes with centroid positions
        boundaries.forEach((boundary, idx) => {
            const label = boundary.file_name || boundary.file || `file-${idx}`;
            const atomCount = boundary.atom_count || 1;
            const nodeId = `file:${idx}`;
            _fileNodeIds.set(idx, nodeId);

            // Calculate centroid from atom positions (SMOOTH TRANSITION)
            const atoms = fileAtoms.get(idx) || [];
            let cx = 0, cy = 0, cz = 0;
            if (atoms.length > 0) {
                atoms.forEach(p => { cx += p.x; cy += p.y; cz += p.z; });
                cx /= atoms.length;
                cy /= atoms.length;
                cz /= atoms.length;
            } else {
                // Fallback: radial layout for files with no positioned atoms
                const angle = (idx / totalFiles) * Math.PI * 2;
                const radius = 200;
                cx = Math.cos(angle) * radius;
                cy = Math.sin(angle) * radius;
                cz = (Math.random() - 0.5) * 50;
            }

            fileNodes.push({
                id: nodeId,
                name: label,
                fileIdx: idx,
                isFileNode: true,
                // POSITION: Initialize at centroid of atoms for smooth transition
                x: cx, y: cy, z: cz,
                fx: undefined, fy: undefined, fz: undefined, // Allow physics to relax
                val: Math.max(2, Math.sqrt(atomCount) * 1.5), // Size by atom count
                color: getColor(idx, totalFiles, label),
                file_path: boundary.file || '',
                atom_count: atomCount,
                // Enriched file metadata for hover panel and visual mappings
                tier: boundary.tier || 'UNKNOWN',
                ring: boundary.ring || 'UNKNOWN',
                internal_edges: boundary.internal_edges || 0,
                external_edges: boundary.external_edges || 0,
                // Physical metadata
                size_bytes: boundary.size_bytes ?? 0,
                size_kb: boundary.size_kb ?? 0,
                token_estimate: boundary.token_estimate ?? 0,
                line_count: boundary.line_count ?? 0,
                code_lines: boundary.code_lines ?? 0,
                // Temporal metadata
                age_days: boundary.age_days ?? 0,
                modified_date: boundary.modified_date || '',
                is_stale: boundary.is_stale ?? false,
                is_recent: boundary.is_recent ?? false,
                // Categorical metadata
                format_category: boundary.format_category || 'other',
                purpose: boundary.purpose || 'general',
                extension: boundary.extension || '',
                is_test: boundary.is_test ?? false,
                is_config: boundary.is_config ?? false,
                // Complexity metadata
                complexity_density: boundary.complexity_density ?? 0,
                cohesion: boundary.cohesion ?? 0.5,
                code_ratio: boundary.code_ratio ?? 0.5
            });
        });

        // Build inter-file edges with weights
        const edgeMap = new Map();
        links.forEach(link => {
            const srcId = _getLinkEndpointId(link, 'source');
            const tgtId = _getLinkEndpointId(link, 'target');
            const srcIdx = nodeFileIdx.get(srcId) ?? -1;
            const tgtIdx = nodeFileIdx.get(tgtId) ?? -1;

            // Skip internal edges and invalid indices
            if (srcIdx < 0 || tgtIdx < 0 || srcIdx === tgtIdx) return;

            const key = `${srcIdx}->${tgtIdx}`;
            const existing = edgeMap.get(key) || {
                source: _fileNodeIds.get(srcIdx),
                target: _fileNodeIds.get(tgtIdx),
                weight: 0,
                edge_type: 'file-dependency',
                resolution: 'file'
            };
            existing.weight += 1;
            edgeMap.set(key, existing);
        });

        _fileGraph = {
            nodes: fileNodes,
            links: Array.from(edgeMap.values())
        };

        console.log(`[FILE_VIZ] Built file graph: ${fileNodes.length} files, ${edgeMap.size} inter-file edges`);
        return _fileGraph;
    }

    function _getLinkEndpointId(link, side) {
        const endpoint = link?.[side];
        if (!endpoint) return null;
        if (typeof endpoint === 'object') return endpoint.id;
        return endpoint;
    }

    /**
     * Save current file node positions for smooth transitions
     */
    function captureFileNodePositions() {
        _fileNodePositions.clear();
        if (typeof Graph === 'undefined' || !Graph) return;

        const nodes = Graph.graphData()?.nodes || [];
        nodes.forEach(node => {
            if (node && node.isFileNode && Number.isFinite(node.x) && Number.isFinite(node.y)) {
                _fileNodePositions.set(node.fileIdx, {
                    x: node.x,
                    y: node.y,
                    z: Number.isFinite(node.z) ? node.z : 0
                });
            }
        });
    }

    /**
     * Restore saved positions to file nodes
     */
    function restoreFileNodePositions(nodes) {
        nodes.forEach(node => {
            if (node.isFileNode && _fileNodePositions.has(node.fileIdx)) {
                const pos = _fileNodePositions.get(node.fileIdx);
                node.x = pos.x;
                node.y = pos.y;
                node.z = pos.z;
            }
        });
    }

    /**
     * Get file target position for radial layout
     */
    function getFileTarget(fileIdx, totalFiles, radius, zSpread) {
        const angle = (fileIdx / totalFiles) * Math.PI * 2;
        return {
            x: Math.cos(angle) * radius,
            y: Math.sin(angle) * radius,
            z: (Math.random() - 0.5) * zSpread
        };
    }

    /**
     * Expand a file to show its atoms
     */
    function expandFile(fileIdx) {
        _expandedFiles.add(fileIdx);
        _graphMode = 'hybrid';
        if (typeof refreshGraph === 'function') refreshGraph();
    }

    /**
     * Collapse a file to hide its atoms
     */
    function collapseFile(fileIdx) {
        _expandedFiles.delete(fileIdx);
        _graphMode = _expandedFiles.size > 0 ? 'hybrid' : 'files';
        if (typeof refreshGraph === 'function') refreshGraph();
    }

    /**
     * Toggle file expansion
     */
    function toggleFileExpansion(fileIdx) {
        if (_expandedFiles.has(fileIdx)) {
            collapseFile(fileIdx);
        } else {
            expandFile(fileIdx);
        }
    }

    /**
     * Apply the file graph to the visualization
     */
    function applyFileGraphMode() {
        if (!_fileGraph) {
            buildFileGraph();
        }
        if (!_fileGraph || typeof Graph === 'undefined' || !Graph) return;

        restoreFileNodePositions(_fileGraph.nodes);
        Graph.graphData(_fileGraph);
        applyColors(_fileGraph.nodes);

        // Reheat simulation for nice spread
        Graph.d3ReheatSimulation();

        if (typeof showToast === 'function') {
            showToast(`File view: ${_fileGraph.nodes.length} files. Click to expand atoms.`);
        }
    }

    // =========================================================================
    // BOUNDARY MANAGEMENT
    // =========================================================================

    function clearBoundaries() {
        if (typeof Graph === 'undefined' || !Graph) return;
        const scene = Graph.scene();
        if (!scene) return;

        _boundaryMeshes.forEach(mesh => scene.remove(mesh));
        _boundaryMeshes = [];
    }

    function scheduleHullRedraw(delayMs = 1200) {
        if (_hullRedrawTimer) {
            clearTimeout(_hullRedrawTimer);
        }
        _hullRedrawTimer = setTimeout(() => {
            if (!(_enabled && _mode === 'hulls')) {
                _hullRedrawAttempts = 0;
                return;
            }

            // Call external drawFileBoundaries if available
            if (typeof drawFileBoundaries === 'function') {
                const drawn = drawFileBoundaries(null);
                if (drawn === 0 && _hullRedrawAttempts < 3) {
                    _hullRedrawAttempts += 1;
                    scheduleHullRedraw(1000);
                }
            }
        }, delayMs);
    }

    // =========================================================================
    // MODE CLEARING
    // =========================================================================

    function clearAllModes() {
        clearBoundaries();

        // Reset file cohesion force if active
        if (typeof clearFileCohesion === 'function') {
            clearFileCohesion();
        }

        // Reset cluster force if active
        if (typeof clusterForceActive !== 'undefined' && clusterForceActive &&
            typeof Graph !== 'undefined' && Graph) {
            Graph.d3Force('cluster', null);
            if (typeof DEFAULT_LINK_DISTANCE !== 'undefined' && DEFAULT_LINK_DISTANCE !== null) {
                Graph.d3Force('link').distance(DEFAULT_LINK_DISTANCE);
            }
            Graph.d3ReheatSimulation();
        }

        // Stop containment animation if active
        if (typeof stopContainmentAnimation === 'function') {
            stopContainmentAnimation();
        }

        // Clear containment spheres
        if (typeof FILE_CONTAINMENT !== 'undefined' && FILE_CONTAINMENT?.spheres) {
            const scene = typeof Graph !== 'undefined' ? Graph?.scene() : null;
            if (scene) {
                FILE_CONTAINMENT.spheres.forEach(s => {
                    if (s.mesh) scene.remove(s.mesh);
                });
            }
            FILE_CONTAINMENT.spheres = [];
            FILE_CONTAINMENT.boundariesPopped = false;
        }

        // Clear lingering filters
        if (typeof VIS_FILTERS !== 'undefined') {
            const filterSets = ['rings', 'tiers', 'families', 'files', 'roles', 'edges', 'layers', 'effects', 'edgeFamilies'];
            filterSets.forEach(key => {
                if (VIS_FILTERS[key]?.clear) VIS_FILTERS[key].clear();
            });
            document.querySelectorAll('.filter-chip.active').forEach(c => c.classList.remove('active'));
        }

        // Reset POP button state
        const popBtn = document.getElementById('btn-file-pop');
        if (popBtn) {
            popBtn.classList.remove('active');
            popBtn.textContent = 'POP!';
        }
    }

    // =========================================================================
    // SET FILE MODE STATE
    // =========================================================================

    function setEnabled(enabled) {
        _enabled = enabled;

        // Update UI buttons
        const cmdBtn = document.getElementById('cmd-files');
        if (cmdBtn) cmdBtn.classList.toggle('active', _enabled);
        const dockBtn = document.getElementById('btn-files');
        if (dockBtn) dockBtn.classList.toggle('active', _enabled);

        // Update panels
        const filePanel = document.getElementById('file-panel');
        const modeControls = document.getElementById('file-mode-controls');
        const expandControls = document.getElementById('file-expand-controls');

        if (_enabled) {
            if (filePanel) filePanel.classList.add('visible');
            if (modeControls) modeControls.classList.add('visible');
            if (expandControls) expandControls.classList.toggle('visible', _mode === 'map');
            apply();
            if (typeof applyEdgeMode === 'function') applyEdgeMode();
            // Use unified LAYOUT module for reflow
            if (typeof LAYOUT !== 'undefined') LAYOUT.reflow();
        } else {
            if (filePanel) filePanel.classList.remove('visible');
            if (modeControls) modeControls.classList.remove('visible');
            if (expandControls) expandControls.classList.remove('visible');

            // Clear expanded files
            if (typeof EXPANDED_FILES !== 'undefined') EXPANDED_FILES.clear();
            if (typeof GRAPH_MODE !== 'undefined') window.GRAPH_MODE = 'atoms';

            // Use unified LAYOUT module for reflow
            if (typeof LAYOUT !== 'undefined') LAYOUT.reflow();

            clearAllModes();
            if (typeof applyEdgeMode === 'function') applyEdgeMode();
            if (typeof refreshGraph === 'function') refreshGraph();
        }
    }

    function toggle() {
        setEnabled(!_enabled);
    }

    // =========================================================================
    // SET VIZ MODE
    // =========================================================================

    function setMode(mode) {
        if (!MODES.includes(mode)) return;
        _mode = mode;

        // Update button states
        document.querySelectorAll('.file-mode-btn').forEach(btn => btn.classList.remove('active'));
        const modeBtn = document.getElementById('btn-file-' + mode);
        if (modeBtn) modeBtn.classList.add('active');

        // Toggle expand controls visibility
        const expandControls = document.getElementById('file-expand-controls');
        if (expandControls) expandControls.classList.toggle('visible', _mode === 'map');
        if (_mode === 'map' && typeof updateExpandButtons === 'function') {
            updateExpandButtons();
        }

        // Update graph mode
        if (_mode === 'map') {
            const hasExpanded = typeof EXPANDED_FILES !== 'undefined' && EXPANDED_FILES.size > 0;
            if (typeof GRAPH_MODE !== 'undefined') {
                window.GRAPH_MODE = hasExpanded ? 'hybrid' : 'files';
            }
        } else {
            if (typeof EXPANDED_FILES !== 'undefined') EXPANDED_FILES.clear();
            if (typeof GRAPH_MODE !== 'undefined') window.GRAPH_MODE = 'atoms';
        }

        // Apply mode
        if (!_enabled) {
            setEnabled(true);
        } else if (_mode === 'map') {
            apply();
        } else {
            if (typeof refreshGraph === 'function') refreshGraph();
        }
    }

    // =========================================================================
    // APPLY CURRENT MODE
    // =========================================================================

    function apply() {
        if (!_enabled) return;

        // Clear previous state
        clearBoundaries();
        if (_mode !== 'hulls') {
            _hullRedrawAttempts = 0;
        }

        // Get graph nodes
        const dm = typeof DATA !== 'undefined' ? DATA :
                   (typeof DM !== 'undefined' ? DM : null);
        const graphNodes = dm?.getVisibleNodes ?
            dm.getVisibleNodes() :
            (typeof Graph !== 'undefined' ? Graph?.graphData()?.nodes || [] : []);

        // Apply file cohesion for color/hulls/cluster modes
        if (_mode === 'color' || _mode === 'hulls' || _mode === 'cluster') {
            if (typeof applyFileCohesion === 'function' && dm?.raw) {
                const physicsPayload = { physics: dm.raw.physics, config: dm.raw.config };
                applyFileCohesion(physicsPayload);
            }
        }

        if (_mode === 'color') {
            applyColors(graphNodes);
        }
        else if (_mode === 'hulls') {
            applyColors(graphNodes);
            scheduleHullRedraw(1500);
        }
        else if (_mode === 'cluster') {
            applyColors(graphNodes);
            if (typeof applyClusterForce === 'function' && dm?.raw) {
                applyClusterForce(dm.raw);
            }
        }
        else if (_mode === 'map') {
            const hasExpanded = typeof EXPANDED_FILES !== 'undefined' && EXPANDED_FILES.size > 0;
            if (typeof GRAPH_MODE !== 'undefined') {
                window.GRAPH_MODE = hasExpanded ? 'hybrid' : 'files';
            }
            if (typeof refreshGraph === 'function') refreshGraph();
            if (typeof showToast === 'function') {
                showToast('File map active. Click a file node to expand.');
            }
        }
        else if (_mode === 'spheres') {
            applyColors(graphNodes);
            if (typeof buildDirectoryTree === 'function' && dm?.raw) {
                buildDirectoryTree(dm.raw);
            }
            if (typeof computeFileActivity === 'function' && dm?.raw) {
                computeFileActivity(dm.raw, graphNodes);
            }
            if (typeof drawContainmentSpheres === 'function' && dm?.raw) {
                drawContainmentSpheres(dm.raw, graphNodes);
            }
            if (typeof startContainmentAnimation === 'function') {
                startContainmentAnimation();
            }
            if (typeof showToast === 'function') {
                showToast('Containment spheres active. Files as force fields. Click POP! to release.');
            }
        }
    }

    // =========================================================================
    // FILE CLUSTERING FORCES - D3 force manipulation for file grouping
    // =========================================================================

    let _clusterForceActive = false;
    let _fileCohesionActive = false;

    /**
     * Apply cluster force to group nodes by file
     * Creates fixed target positions arranged in a circular pattern
     */
    function applyClusterForce(data) {
        const Graph = window.Graph;
        const DM = window.DM;
        const APPEARANCE_STATE = window.APPEARANCE_STATE;
        const IS_3D = window.IS_3D;

        const clusterConfig = data?.physics?.cluster || {};
        const modeStrength = (typeof clusterConfig.modes?.strong === 'number') ? clusterConfig.modes.strong : null;
        const sliderStrength = (typeof APPEARANCE_STATE?.clusterStrength === 'number') ? APPEARANCE_STATE.clusterStrength : null;
        const clusterStrength = (typeof sliderStrength === 'number')
            ? sliderStrength
            : ((typeof modeStrength === 'number')
                ? modeStrength
                : ((typeof clusterConfig.strength === 'number') ? clusterConfig.strength : 0.3));
        const clusterRadius = (typeof clusterConfig.radius === 'number') ? clusterConfig.radius : 150;
        const clusterZSpacing = (typeof clusterConfig.zSpacing === 'number') ? clusterConfig.zSpacing : 30;
        const linkDistance = (typeof clusterConfig.linkDistance === 'number')
            ? clusterConfig.linkDistance
            : (data?.physics?.forces?.link?.distance || 50);

        const graphNodes = DM ? DM.getVisibleNodes() : (Graph?.graphData()?.nodes || []);
        const boundaries = DM ? DM.getFileBoundaries() : (data?.file_boundaries || []);
        const numFiles = boundaries.length;

        // Fixed target positions: arrange files in circular pattern
        const fileTargets = {};
        for (let i = 0; i < numFiles; i++) {
            fileTargets[i] = getFileTarget(i, numFiles, clusterRadius, clusterZSpacing);
        }

        // Reduce link distance to keep intra-file nodes tighter
        Graph.d3Force('link').distance(linkDistance);

        // Apply strong clustering force toward fixed targets
        Graph.d3Force('cluster', (alpha) => {
            const k = alpha * clusterStrength;
            graphNodes.forEach(node => {
                const target = fileTargets[node.fileIdx];
                if (target) {
                    node.vx = (node.vx || 0) + (target.x - node.x) * k;
                    node.vy = (node.vy || 0) + (target.y - node.y) * k;
                    if (IS_3D) {
                        node.vz = (node.vz || 0) + (target.z - node.z) * k;
                    }
                }
            });
        });

        _clusterForceActive = true;
        Graph.d3ReheatSimulation();
        scheduleHullRedraw(1500);
    }

    /**
     * Apply file cohesion force - nodes in same file attract each other
     * Also stretches inter-file links for better separation
     */
    function applyFileCohesion(data) {
        if (_fileCohesionActive) return;

        const Graph = window.Graph;
        const DM = window.DM;
        const APPEARANCE_STATE = window.APPEARANCE_STATE;
        const IS_3D = window.IS_3D;
        const DEFAULT_LINK_DISTANCE = window.DEFAULT_LINK_DISTANCE || 50;

        const config = data?.physics?.fileCohesion || {};
        const strength = (typeof APPEARANCE_STATE?.fileCohesionStrength === 'number')
            ? APPEARANCE_STATE.fileCohesionStrength
            : (config.strength ?? 0.15);
        const linkMult = config.interFileLinkMultiplier ?? 2.5;
        const minDist = config.minDistance ?? 20;

        const nodes = DM ? DM.getVisibleNodes() : (Graph?.graphData()?.nodes || []);
        if (!nodes.length) return;

        // Pre-compute file groups
        const groups = new Map();
        nodes.forEach(n => {
            const f = n.fileIdx ?? -1;
            if (f >= 0) (groups.get(f) || groups.set(f, []).get(f)).push(n);
        });

        // Intra-file centroid attraction
        Graph.d3Force('fileCohesion', (alpha) => {
            const k = strength * alpha;
            groups.forEach(g => {
                if (g.length < 2) return;
                let cx = 0, cy = 0, cz = 0;
                g.forEach(n => { cx += n.x || 0; cy += n.y || 0; cz += n.z || 0; });
                cx /= g.length; cy /= g.length; cz /= g.length;
                g.forEach(n => {
                    const dx = cx - (n.x || 0), dy = cy - (n.y || 0), dz = cz - (n.z || 0);
                    const d = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;
                    if (d > minDist) {
                        const f = k * Math.min(1, d / 100);
                        n.vx = (n.vx || 0) + dx * f;
                        n.vy = (n.vy || 0) + dy * f;
                        if (IS_3D) n.vz = (n.vz || 0) + dz * f;
                    }
                });
            });
        });

        // Inter-file links stretched
        const base = DEFAULT_LINK_DISTANCE;
        Graph.d3Force('link').distance(link => {
            const s = typeof link.source === 'object' ? link.source : nodes.find(n => n.id === link.source);
            const t = typeof link.target === 'object' ? link.target : nodes.find(n => n.id === link.target);
            if (!s || !t) return base;
            const sf = s.fileIdx ?? -1, tf = t.fileIdx ?? -1;
            return (sf >= 0 && tf >= 0 && sf !== tf) ? base * linkMult : base;
        });

        _fileCohesionActive = true;
        Graph.d3ReheatSimulation();
    }

    /**
     * Clear file cohesion force
     */
    function clearFileCohesion() {
        if (!_fileCohesionActive) return;

        const Graph = window.Graph;
        const DEFAULT_LINK_DISTANCE = window.DEFAULT_LINK_DISTANCE;

        Graph.d3Force('fileCohesion', null);
        if (DEFAULT_LINK_DISTANCE !== null) {
            Graph.d3Force('link').distance(DEFAULT_LINK_DISTANCE);
        }
        _fileCohesionActive = false;
        Graph.d3ReheatSimulation();
    }

    /**
     * Clear cluster force
     */
    function clearClusterForce() {
        if (!_clusterForceActive) return;

        const Graph = window.Graph;
        Graph.d3Force('cluster', null);
        _clusterForceActive = false;
        Graph.d3ReheatSimulation();
    }

    // =========================================================================
    // CONFIGURATION
    // =========================================================================

    function setConfig(config) {
        _config = { ..._config, ...config };
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Core functions
        getColor,
        getHue,
        applyColors,

        // Mode management
        setMode,
        get mode() { return _mode; },
        MODES,
        MODE_HINTS,

        // Enable/disable
        setEnabled,
        toggle,
        get enabled() { return _enabled; },

        // Apply
        apply,

        // FILE GRAPH - Repository as Nodes
        buildFileGraph,
        applyFileGraphMode,
        expandFile,
        collapseFile,
        toggleFileExpansion,
        captureFileNodePositions,
        restoreFileNodePositions,
        getFileTarget,
        get fileGraph() { return _fileGraph; },
        get fileNodeIds() { return _fileNodeIds; },
        get expandedFiles() { return _expandedFiles; },
        get graphMode() { return _graphMode; },
        set graphMode(val) { _graphMode = val; },
        get expandMode() { return _expandMode; },
        set expandMode(val) { _expandMode = val; },

        // VISUAL MAPPING - Metadata to Visual Properties
        applyVisualMapping,
        getColorForMapping,
        VISUAL_MAPPINGS,
        get activeMapping() { return _activeMapping; },
        set activeMapping(val) { _activeMapping = val; },

        // Boundaries
        clearBoundaries,
        clearAllModes,
        scheduleHullRedraw,

        // File Clustering Forces
        applyClusterForce,
        clearClusterForce,
        applyFileCohesion,
        clearFileCohesion,
        get clusterForceActive() { return _clusterForceActive; },
        get fileCohesionActive() { return _fileCohesionActive; },

        // Configuration
        setConfig,
        get config() { return _config; },

        // Internal state access (for migration)
        get boundaryMeshes() { return _boundaryMeshes; },
        set boundaryMeshes(val) { _boundaryMeshes = val; }
    };
})();

// Backward compatibility aliases - Using Object.defineProperty to avoid duplicate declarations
Object.defineProperty(window, 'fileMode', {
    get: () => FILE_VIZ.enabled,
    set: (v) => FILE_VIZ.setEnabled(v),
    configurable: true
});
Object.defineProperty(window, 'fileVizMode', {
    get: () => FILE_VIZ.mode,
    set: (v) => FILE_VIZ.setMode(v),
    configurable: true
});
Object.defineProperty(window, 'FILE_COLOR_CONFIG', {
    get: () => FILE_VIZ.config,
    configurable: true
});
Object.defineProperty(window, 'fileBoundaryMeshes', {
    get: () => FILE_VIZ.boundaryMeshes,
    set: (v) => { FILE_VIZ.boundaryMeshes = v; },
    configurable: true
});
// hullRedrawTimer, hullRedrawAttempts - app.js owns these, not duplicated here

function getFileColor(fileIdx, totalFiles, fileName, lightnessOverride) {
    return FILE_VIZ.getColor(fileIdx, totalFiles, fileName, lightnessOverride);
}
function getFileHue(fileIdx, totalFiles, fileName) {
    return FILE_VIZ.getHue(fileIdx, totalFiles, fileName);
}
function setFileModeState(enabled) {
    FILE_VIZ.setEnabled(enabled);
}
function setFileVizMode(mode) {
    FILE_VIZ.setMode(mode);
}
function applyFileVizMode() {
    FILE_VIZ.apply();
}
function applyFileColors(graphNodes) {
    FILE_VIZ.applyColors(graphNodes);
}
function clearFileBoundaries() {
    FILE_VIZ.clearBoundaries();
}
function clearAllFileModes() {
    FILE_VIZ.clearAllModes();
}
function scheduleHullRedraw(delayMs) {
    FILE_VIZ.scheduleHullRedraw(delayMs);
}

// File graph backward compatibility - Using getters for live updates
Object.defineProperty(window, 'FILE_GRAPH', {
    get: () => FILE_VIZ.fileGraph,
    set: (val) => { /* Ignore - module manages state */ },
    configurable: true
});
Object.defineProperty(window, 'FILE_NODE_IDS', {
    get: () => FILE_VIZ.fileNodeIds,
    configurable: true
});
// FILE_NODE_POSITIONS is managed by app.js (not in this module's scope)
Object.defineProperty(window, 'EXPANDED_FILES', {
    get: () => FILE_VIZ.expandedFiles,
    configurable: true
});
Object.defineProperty(window, 'FILE_EXPAND_MODE', {
    get: () => FILE_VIZ.expandMode,
    set: (val) => { FILE_VIZ.expandMode = val; },
    configurable: true
});

function buildFileGraph(data) {
    // Calls module's buildFileGraph - FILE_GRAPH getter will return the result
    FILE_VIZ.buildFileGraph();
    FILE_NODE_IDS = FILE_VIZ.fileNodeIds;
    return FILE_VIZ.fileGraph;  // Return directly from module
}
function captureFileNodePositions() {
    FILE_VIZ.captureFileNodePositions();
}
function restoreNodePositions(nodes) {
    FILE_VIZ.restoreFileNodePositions(nodes);
}
function getFileTarget(fileIdx, totalFiles, radius, zSpread) {
    return FILE_VIZ.getFileTarget(fileIdx, totalFiles, radius, zSpread);
}

// File clustering force shims
function applyClusterForce(data) {
    FILE_VIZ.applyClusterForce(data);
}
function clearClusterForce() {
    FILE_VIZ.clearClusterForce();
}
function applyFileCohesion(data) {
    FILE_VIZ.applyFileCohesion(data);
}
function clearFileCohesion() {
    FILE_VIZ.clearFileCohesion();
}
Object.defineProperty(window, 'clusterForceActive', {
    get: () => FILE_VIZ.clusterForceActive,
    configurable: true
});
Object.defineProperty(window, 'fileCohesionActive', {
    get: () => FILE_VIZ.fileCohesionActive,
    configurable: true
});
