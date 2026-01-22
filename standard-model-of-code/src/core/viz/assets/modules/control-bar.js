/**
 * CONTROL BAR MODULE - Visual Mapping Command Center
 *
 * A persistent control bar (like ChatGPT/Claude input) that allows dynamic
 * mapping of any data characteristic to any visual/physics property.
 *
 * Features:
 * - Always visible at bottom of screen
 * - Works with selected nodes or node groups
 * - Dropdown to choose data source (any field)
 * - Dropdown to choose visual target (size, color, position, physics...)
 * - Group comparison with numbered badges
 * - Real-time preview as you adjust
 *
 * Depends on: DATA, COLOR, ANIM, SELECT
 */

const CONTROL_BAR = (function () {
    'use strict';

    // =========================================================================
    // AVAILABLE DATA SOURCES (what we can map FROM)
    // =========================================================================

    // =========================================================================
    // AVAILABLE DATA SOURCES (Delegated to UPB)
    // =========================================================================
    const DATA_SOURCES = (window.UPB && window.UPB.ENDPOINTS && window.UPB.ENDPOINTS.SOURCES) || {
        // Fallback for safety if UPB fails to load
        token_estimate: { label: 'Token Count', type: 'continuous', domain: 'file' }
    };

    // =========================================================================
    // AVAILABLE TARGETS (Delegated to UPB)
    // =========================================================================
    const VISUAL_TARGETS = (window.UPB && window.UPB.ENDPOINTS && window.UPB.ENDPOINTS.TARGETS) || {
        // Fallback
        nodeSize: { label: 'Node Size', category: 'appearance', range: [1, 30] }
    };

    // =========================================================================
    // SCALE FUNCTIONS (Delegated to UPB)
    // =========================================================================
    const SCALES = (window.UPB && window.UPB.SCALES && window.UPB.SCALES.SCALES) || {
        linear: (v, min, max) => (v - min) / (max - min || 1)
    };

    // =========================================================================
    // STATE
    // =========================================================================

    let _visible = false;
    let _container = null;
    let _activeMapping = null;
    let _groups = [];         // [{id, name, nodeIds, color}]
    let _groupCounter = 0;

    // Current mapping configuration
    let _config = {
        source: 'token_estimate',
        target: 'nodeSize',
        scale: 'sqrt',
        scope: 'selection',   // 'selection' | 'all' | 'group:X'
        invert: false
    };

    // =========================================================================
    // UI BUILDING
    // =========================================================================

    let _isDocked = false;

    function createUI() {
        if (_container) return _container;

        const dockContainer = document.getElementById('control-bar-container');
        _isDocked = !!dockContainer;

        _container = document.createElement('div');
        _container.id = 'control-bar';
        _container.className = _isDocked ? 'control-bar docked' : 'control-bar';

        // Scope Section
        const scopeHTML = `
            <div class="control-section scope-section">
                <label>SCOPE</label>
                <div class="row-group">
                    <select id="cb-scope" class="cb-select">
                        <option value="selection">Selected Nodes</option>
                        <option value="all">All Nodes</option>
                        <optgroup label="Groups" id="cb-groups-optgroup"></optgroup>
                    </select>
                    <button id="cb-add-group" class="cb-btn cb-btn-small" title="Create group from selection">+G</button>
                    <span id="cb-node-count" class="cb-badge">0</span>
                </div>
            </div>
        `;

        // Map FROM
        const sourceHTML = `
            <div class="control-section">
                <label>MAP DATA SOURCE</label>
                <select id="cb-source" class="cb-select full-width">
                    <optgroup label="Structural">
                        <option value="token_estimate">Token Count</option>
                        <option value="line_count">Line Count</option>
                        <option value="size_bytes">File Size</option>
                        <option value="code_lines">Code Lines</option>
                        <option value="complexity_density">Complexity</option>
                        <option value="cohesion">Cohesion</option>
                    </optgroup>
                    <optgroup label="Temporal">
                        <option value="age_days">Age (days)</option>
                    </optgroup>
                    <optgroup label="Graph">
                        <option value="in_degree">In-Degree</option>
                        <option value="out_degree">Out-Degree</option>
                    </optgroup>
                    <optgroup label="Categorical">
                        <option value="tier">Tier</option>
                        <option value="ring">Ring</option>
                        <option value="layer">Layer</option>
                        <option value="role">Role</option>
                        <option value="format_category">Format</option>
                        <option value="effect">Effect</option>
                    </optgroup>
                    <optgroup label="Boolean">
                        <option value="is_test">Is Test?</option>
                        <option value="is_config">Is Config?</option>
                        <option value="is_stale">Is Stale?</option>
                    </optgroup>
                    <optgroup label="Tree-sitter Analysis">
                        <option value="D6_pure_score">Purity Score (0-1)</option>
                        <option value="D6_EFFECT">Purity Rating</option>
                        <option value="pagerank">PageRank Influence</option>
                        <option value="betweenness_centrality">Betweenness (Bridge)</option>
                        <option value="topology_role">Topology Role</option>
                    </optgroup>
                    <optgroup label="Control Flow (P3-09)">
                        <option value="cyclomatic_complexity">Cyclomatic Complexity</option>
                        <option value="complexity_rating">Complexity Rating</option>
                        <option value="max_nesting_depth">Nesting Depth</option>
                        <option value="nesting_rating">Nesting Rating</option>
                    </optgroup>
                </select>
            </div>
        `;

        // Arrow (only for float mode, skip or style differently in dock)
        const arrowHTML = _isDocked ? '' : `
            <div class="control-section arrow-section">
                <span class="arrow">&#8594;</span>
            </div>
        `;

        // Map TO
        const targetHTML = `
            <div class="control-section">
                <label>TO VISUAL PROPERTY</label>
                <select id="cb-target" class="cb-select full-width">
                    <optgroup label="Appearance">
                        <option value="nodeSize">Node Size</option>
                        <option value="hue">Color Hue</option>
                        <option value="saturation">Saturation</option>
                        <option value="lightness">Lightness</option>
                        <option value="opacity">Opacity</option>
                    </optgroup>
                    <optgroup label="Position">
                        <option value="xPosition">X Position</option>
                        <option value="yPosition">Y Position</option>
                        <option value="zPosition">Z Depth</option>
                        <option value="radius">Radial Distance</option>
                    </optgroup>
                    <optgroup label="Physics">
                        <option value="charge">Charge (repel)</option>
                        <option value="mass">Mass</option>
                    </optgroup>
                    <optgroup label="Animation">
                        <option value="pulseSpeed">Pulse Speed</option>
                    </optgroup>
                </select>
            </div>
        `;

        // Scale
        const scaleHTML = `
            <div class="control-section">
                <label>SCALING</label>
                <select id="cb-scale" class="cb-select full-width">
                    <option value="linear">Linear (even spread)</option>
                    <option value="sqrt" selected>Sqrt (compress giants)</option>
                    <option value="log">Log (heavy compress)</option>
                    <option value="exp">Exp (emphasize extremes)</option>
                    <option value="inverse">Inverse (flip)</option>
                </select>
            </div>
        `;

        // Actions
        const actionsHTML = `
            <div class="control-section actions-section">
                <button id="cb-apply" class="cb-btn cb-btn-primary full-width">APPLY MAPPING</button>
                <button id="cb-reset" class="cb-btn full-width" style="margin-top:4px">Reset</button>
            </div>
        `;

        // Groups Display
        const groupsHTML = `
            <div class="control-section groups-section" id="cb-groups-display"></div>
        `;

        // Toggle (only for float mode)
        const toggleHTML = _isDocked ? '' : `
            <button id="cb-toggle" class="cb-toggle" title="Toggle Control Bar">
                <span class="chevron">&#9660;</span>
            </button>
        `;

        _container.innerHTML = `
            <div class="control-bar-inner">
                ${scopeHTML}
                ${sourceHTML}
                ${arrowHTML}
                ${targetHTML}
                ${scaleHTML}
                ${actionsHTML}
                ${groupsHTML}
                ${toggleHTML}
            </div>
        `;

        // Add styles
        addStyles();

        // Attach event listeners
        attachListeners();

        if (_isDocked) {
            dockContainer.appendChild(_container);
        } else {
            document.body.appendChild(_container);
        }

        _visible = true;

        return _container;
    }

    function addStyles() {
        if (document.getElementById('control-bar-styles')) return;

        const style = document.createElement('style');
        style.id = 'control-bar-styles';
        style.textContent = `
            /* BASE STYLES */
            .control-bar {
                font-family: 'SF Mono', 'Consolas', monospace;
            }

            /* FLOATING MODE */
            .control-bar:not(.docked) {
                position: fixed;
                bottom: 16px;
                left: 50%;
                transform: translateX(-50%);
                max-width: 900px;
                width: calc(100% - 48px);
                z-index: 9999;
                background: linear-gradient(180deg, rgba(28, 30, 35, 0.95) 0%, rgba(22, 24, 28, 0.98) 100%);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(100, 105, 115, 0.15);
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
                transition: transform 0.3s ease, opacity 0.3s ease;
            }

            .control-bar:not(.docked) .control-bar-inner {
                display: flex;
                align-items: center;
                gap: 16px;
                padding: 12px 20px;
                overflow-x: auto;
            }

            /* DOCKED MODE */
            .control-bar.docked {
                position: static;
                width: 100%;
                background: transparent;
                border: none;
                box-shadow: none;
                padding: 0;
            }

            .control-bar.docked .control-bar-inner {
                display: flex;
                flex-direction: column;
                gap: 12px;
                padding: 0;
            }

            /* SHARED COMPONENTS */
            .control-section {
                display: flex;
                flex-direction: column;
                gap: 4px;
                width: 100%; /* Full width when docked */
            }

            .control-section label {
                font-size: 9px;
                font-weight: 600;
                color: rgba(140, 145, 155, 0.6);
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .row-group {
                display: flex;
                gap: 6px;
                align-items: center;
            }

            .cb-select {
                background: rgba(35, 38, 45, 0.85);
                border: 1px solid rgba(100, 105, 115, 0.2);
                border-radius: 6px;
                color: #c8ccd5;
                padding: 6px 10px;
                font-size: 11px;
                font-family: inherit;
                cursor: pointer;
                transition: all 0.2s;
                flex: 1;
            }

            .cb-select:hover {
                background: rgba(45, 48, 55, 0.9);
                border-color: rgba(120, 125, 135, 0.35);
            }
            
            .cb-select:focus {
                outline: none;
                border-color: var(--accent, #4a9eff);
            }

            .full-width {
                width: 100%;
            }

            .cb-btn {
                background: rgba(50, 55, 65, 0.6);
                border: 1px solid rgba(100, 105, 115, 0.2);
                border-radius: 6px;
                color: #b0b5c0;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                text-transform: uppercase;
            }
            .actions-section {
                width: 100%;
            }
            .cb-btn:hover {
                background: rgba(65, 70, 80, 0.75);
                color: #fff;
            }

            .cb-btn-primary {
                background: var(--accent-dim, rgba(74, 158, 255, 0.15));
                color: var(--accent, #4a9eff);
                border-color: var(--accent, #4a9eff);
            }

            .cb-btn-primary:hover {
                background: var(--accent, #4a9eff);
                color: #000;
            }

            .cb-btn-small {
                padding: 4px 8px;
                min-width: 30px;
            }

            .cb-badge {
                font-size: 10px;
                color: #666;
                min-width: 15px;
                text-align: center;
            }

            /* GROUP CHIPS */
            .groups-section {
                flex-direction: row;
                flex-wrap: wrap;
                gap: 4px;
            }

            .group-chip {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 10px;
                cursor: default;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }

            .group-color {
                width: 6px;
                height: 6px;
                border-radius: 50%;
            }

            .group-remove {
                margin-left: 4px;
                cursor: pointer;
                opacity: 0.5;
            }
            .group-remove:hover { opacity: 1; }
        `;

        document.head.appendChild(style);
    }

    function attachListeners() {
        // Toggle collapse
        const toggleBtn = document.getElementById('cb-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggle);
        }

        // Scope change
        const scopeSelect = document.getElementById('cb-scope');
        if (scopeSelect) {
            scopeSelect.addEventListener('change', (e) => {
                _config.scope = e.target.value;
                updateNodeCount();
            });
        }

        // Source change
        const sourceSelect = document.getElementById('cb-source');
        if (sourceSelect) {
            sourceSelect.addEventListener('change', (e) => {
                _config.source = e.target.value;
            });
        }

        // Target change
        const targetSelect = document.getElementById('cb-target');
        if (targetSelect) {
            targetSelect.addEventListener('change', (e) => {
                _config.target = e.target.value;
            });
        }

        // Scale change
        const scaleSelect = document.getElementById('cb-scale');
        if (scaleSelect) {
            scaleSelect.addEventListener('change', (e) => {
                _config.scale = e.target.value;
            });
        }

        // Apply button
        const applyBtn = document.getElementById('cb-apply');
        if (applyBtn) {
            applyBtn.addEventListener('click', applyMapping);
        }

        // Reset button
        const resetBtn = document.getElementById('cb-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', resetMapping);
        }

        // Add group button
        const addGroupBtn = document.getElementById('cb-add-group');
        if (addGroupBtn) {
            addGroupBtn.addEventListener('click', createGroupFromSelection);
        }

        // Update node count periodically
        setInterval(updateNodeCount, 1000);
    }

    // =========================================================================
    // GROUP MANAGEMENT
    // =========================================================================

    const GROUP_COLORS = [
        '#4a9eff', '#ff6b6b', '#51cf66', '#ffd43b',
        '#cc5de8', '#20c997', '#ff922b', '#748ffc'
    ];

    function createGroupFromSelection() {
        const selectedIds = getSelectedNodeIds();
        if (selectedIds.length === 0) {
            showToast('Select nodes first to create a group');
            return;
        }

        _groupCounter++;
        const groupId = `group-${_groupCounter}`;
        const color = GROUP_COLORS[(_groupCounter - 1) % GROUP_COLORS.length];

        const group = {
            id: groupId,
            name: `Group ${_groupCounter}`,
            nodeIds: [...selectedIds],
            color: color
        };

        _groups.push(group);
        updateGroupsUI();
        showToast(`Created ${group.name} with ${selectedIds.length} nodes`);
    }

    function removeGroup(groupId) {
        _groups = _groups.filter(g => g.id !== groupId);
        updateGroupsUI();
    }

    function updateGroupsUI() {
        // Update dropdown
        const optgroup = document.getElementById('cb-groups-optgroup');
        if (optgroup) {
            optgroup.innerHTML = _groups.map(g =>
                `<option value="group:${g.id}">${g.name} (${g.nodeIds.length})</option>`
            ).join('');
        }

        // Update chips display
        const display = document.getElementById('cb-groups-display');
        if (display) {
            display.innerHTML = _groups.map(g => `
                <div class="group-chip" data-group="${g.id}">
                    <span class="group-color" style="background: ${g.color}"></span>
                    <span class="group-name">${g.name}</span>
                    <span class="group-count">${g.nodeIds.length}</span>
                    <span class="group-remove" onclick="CONTROL_BAR.removeGroup('${g.id}')">&times;</span>
                </div>
            `).join('');
        }
    }

    // =========================================================================
    // MAPPING APPLICATION
    // =========================================================================

    function getTargetNodes() {
        const dm = typeof DATA !== 'undefined' ? DATA : null;
        const allNodes = dm?.getNodes ? dm.getNodes() : (typeof graphNodes !== 'undefined' ? graphNodes : []);

        if (_config.scope === 'all') {
            return allNodes;
        }

        if (_config.scope === 'selection') {
            const selectedIds = getSelectedNodeIds();
            return allNodes.filter(n => selectedIds.includes(n.id));
        }

        if (_config.scope.startsWith('group:')) {
            const groupId = _config.scope.replace('group:', '');
            const group = _groups.find(g => g.id === groupId);
            if (group) {
                return allNodes.filter(n => group.nodeIds.includes(n.id));
            }
        }

        return [];
    }

    function applyMapping() {
        if (!window.UPB) {
            console.error('UPB not loaded');
            return;
        }

        const nodes = getTargetNodes();
        if (nodes.length === 0) {
            showToast('No nodes to map. Select nodes or change scope.');
            return;
        }

        const sourceKey = _config.source;
        const targetKey = _config.target;

        // 1. Create/Update Binding in UPB Graph
        window.UPB.bind(sourceKey, targetKey, {
            id: `cb-binding-${Date.now()}`,
            scale: _config.scale,
            range: VISUAL_TARGETS[targetKey]?.range
        });

        // 2. Set Data Ranges for normalization (Phase 6: use DATA.getRange)
        // Map control-bar scope to DATA.getRange scope
        const dm = typeof DATA !== 'undefined' ? DATA : null;
        if (dm && typeof dm.getRange === 'function') {
            const dataScope = _config.scope === 'selection' ? 'selection' :
                              _config.scope === 'all' ? 'global' : 'visible';
            const range = dm.getRange(sourceKey, dataScope);
            if (window.UPB.BINDINGS.defaultGraph) {
                window.UPB.BINDINGS.defaultGraph._dataRanges[sourceKey] = range;
            }
        } else {
            // Fallback: calculate ad-hoc if DATA.getRange not available
            const values = nodes.map(n => getNodeValue(n, sourceKey)).filter(v => typeof v === 'number');
            if (values.length > 0 && window.UPB.BINDINGS.defaultGraph) {
                window.UPB.BINDINGS.defaultGraph._dataRanges[sourceKey] = {
                    min: Math.min(...values),
                    max: Math.max(...values)
                };
            }
        }

        // 3. Apply to Nodes
        const updates = window.UPB.apply(nodes);

        // 4. Render Updates
        updates.forEach(update => {
            const node = nodes.find(n => n.id === update.id);
            if (node) {
                Object.keys(update.visuals).forEach(key => {
                    applyToNode(node, key, update.visuals[key]);
                });
            }
        });

        // Refresh graph
        if (typeof REFRESH !== 'undefined') {
            REFRESH.throttled();
        } else if (typeof Graph !== 'undefined' && Graph) {
            REFRESH.throttled();
        }

        showToast(`Bound ${sourceKey} -> ${targetKey} via UPB`);
        console.log(`[CONTROL_BAR] UPB Binding Active: ${sourceKey} -> ${targetKey}`);
    }

    function getNodeValue(node, key) {
        // Direct property
        if (node[key] !== undefined) return node[key];

        // Nested in dimensions
        if (node.dimensions && node.dimensions[key] !== undefined) {
            return node.dimensions[key];
        }

        // Check common dimension mappings
        const dimMap = {
            'tier': 'D1_TIER',
            'ring': 'D2_RING',
            'layer': 'D2_LAYER',
            'effect': 'D6_EFFECT'
        };

        if (dimMap[key] && node.dimensions) {
            return node.dimensions[dimMap[key]];
        }

        return null;
    }

    function applyToNode(node, targetKey, value) {
        switch (targetKey) {
            case 'nodeSize':
                node.val = value;
                break;

            case 'hue':
                // Use OKLCH color space via COLOR module
                const hueOklch = window.COLOR.hexToOklch(node.color || '#808080');
                hueOklch.h = value;
                node.color = window.COLOR.toHex(hueOklch);
                break;

            case 'saturation':
                // Map saturation (0-100) to OKLCH chroma (0-0.3)
                const satOklch = window.COLOR.hexToOklch(node.color || '#808080');
                satOklch.c = (value / 100) * 0.3;
                node.color = window.COLOR.toHex(satOklch);
                break;

            case 'lightness':
                // Map lightness (0-100) to OKLCH lightness (0-1)
                const litOklch = window.COLOR.hexToOklch(node.color || '#808080');
                litOklch.l = value / 100;
                node.color = window.COLOR.toHex(litOklch);
                break;

            case 'opacity':
                node.opacity = value;
                // Update color alpha if using rgba
                if (node.color && !node.color.startsWith('hsl')) {
                    node.color = setAlpha(node.color, value);
                }
                break;

            case 'xPosition':
                node.fx = value;
                break;

            case 'yPosition':
                node.fy = value;
                break;

            case 'zPosition':
                node.fz = value;
                break;

            case 'radius':
                // Position on a circle at given radius
                const angle = (node.fileIdx || Math.random() * 100) * 0.618 * Math.PI * 2;
                node.fx = Math.cos(angle) * value;
                node.fy = Math.sin(angle) * value;
                break;

            case 'charge':
                node.__charge = value;
                break;

            case 'mass':
                node.__mass = value;
                break;

            case 'pulseSpeed':
                node.__pulseSpeed = value;
                break;

            default:
                node[targetKey] = value;
        }
    }

    function setAlpha(colorStr, alpha) {
        // Simple alpha injection
        if (colorStr.startsWith('rgba')) {
            return colorStr.replace(/[\d.]+\)$/, `${alpha})`);
        }
        if (colorStr.startsWith('rgb')) {
            return colorStr.replace('rgb', 'rgba').replace(')', `, ${alpha})`);
        }
        return colorStr;
    }

    function resetMapping() {
        // Clear fixed positions
        const nodes = getTargetNodes();
        nodes.forEach(n => {
            delete n.fx;
            delete n.fy;
            delete n.fz;
            delete n.__charge;
            delete n.__mass;
            delete n.__pulseSpeed;
        });

        // Reheat simulation
        if (typeof Graph !== 'undefined' && Graph) {
            Graph.d3ReheatSimulation();
        }

        showToast('Reset node positions and custom properties');
    }

    // =========================================================================
    // HELPERS
    // =========================================================================

    function getSelectedNodeIds() {
        if (typeof SELECT !== 'undefined' && SELECT.getSelectedNodes) {
            return SELECT.getSelectedNodes().map(n => n.id);
        }
        if (typeof SELECTED_NODE_IDS !== 'undefined') {
            return Array.from(SELECTED_NODE_IDS);
        }
        return [];
    }

    function updateNodeCount() {
        const badge = document.getElementById('cb-node-count');
        if (!badge) return;

        const nodes = getTargetNodes();
        badge.textContent = nodes.length;
    }

    function showToast(msg) {
        if (typeof window.showToast === 'function') {
            window.showToast(msg);
        } else {
            console.log(`[CONTROL_BAR] ${msg}`);
        }
    }

    function toggle() {
        if (_container) {
            _container.classList.toggle('collapsed');
            _visible = !_container.classList.contains('collapsed');
        }
    }

    function show() {
        if (_container) {
            _container.classList.remove('collapsed');
            _visible = true;
        }
    }

    function hide() {
        if (_container) {
            _container.classList.add('collapsed');
            _visible = false;
        }
    }

    // =========================================================================
    // INIT
    // =========================================================================

    function init() {
        createUI();
        updateNodeCount();
        console.log('[CONTROL_BAR] Initialized');
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        init,
        toggle,
        show,
        hide,
        applyMapping,
        resetMapping,
        createGroupFromSelection,
        removeGroup,
        get visible() { return _visible; },
        get config() { return _config; },
        get groups() { return _groups; },
        DATA_SOURCES,
        VISUAL_TARGETS,
        SCALES
    };

})();

// Auto-init when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => CONTROL_BAR.init());
} else {
    // Small delay to ensure other modules are loaded
    setTimeout(() => CONTROL_BAR.init(), 100);
}
