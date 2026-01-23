/**
 * SELECTION MODULE
 *
 * Manages node selection, multi-select, marquee selection, and selection visuals.
 * Includes animated selection colors using OKLCH pendulum system.
 *
 * Depends on: CORE (PENDULUM, SELECTION_SIZE_MULT), NODE, COLOR
 *
 * Usage:
 *   SELECT.set([id1, id2])              // Set selection
 *   SELECT.toggle(node)                 // Toggle node selection
 *   SELECT.clear()                      // Clear selection
 *   SELECT.getSelectedNodes()           // Get selected node objects
 *   SELECT.ids                          // Get Set of selected IDs
 */

const SELECT = (function () {
    'use strict';

    // =========================================================================
    // STATE
    // =========================================================================

    const _ids = new Set();
    let _marqueeActive = false;
    let _marqueeStart = null;
    let _marqueeAdditive = false;
    let _lastMarqueeEndTs = 0;

    // Selection visuals state
    const _selectionOriginals = new Map();
    const _originalColorsForDim = new Map();

    // THREE.js geometries (created lazily)
    let _selectionHaloGeometry = null;
    let _groupHaloGeometry = null;

    // =========================================================================
    // CORE SELECTION FUNCTIONS
    // =========================================================================

    /**
     * Get currently selected nodes
     */
    function getSelectedNodes() {
        if (typeof Graph === 'undefined' || !Graph?.graphData) return [];
        const nodes = Graph.graphData().nodes || [];
        return nodes.filter(node => node && node.id && _ids.has(node.id));
    }

    /**
     * Set selection (optionally additive)
     */
    function set(ids, additive = false) {
        if (!additive) {
            _ids.clear();
        }
        (ids || []).forEach(id => {
            if (id) _ids.add(id);
        });
        _updatePanel();
        // Use app.js's updateSelectionVisuals if available (has group halo logic)
        // Otherwise fall back to internal _updateVisuals
        if (typeof window.updateSelectionVisuals === 'function') {
            window.updateSelectionVisuals();
        } else {
            _updateVisuals();
        }
        _updateGroupButtonState();
    }

    /**
     * Toggle a node's selection state
     */
    function toggle(node) {
        if (!node || !node.id) return;
        if (_ids.has(node.id)) {
            _ids.delete(node.id);
        } else {
            _ids.add(node.id);
        }
        _updatePanel();
        if (typeof window.updateSelectionVisuals === 'function') {
            window.updateSelectionVisuals();
        } else {
            _updateVisuals();
        }
        _updateGroupButtonState();
    }

    /**
     * Clear all selection
     */
    function clear() {
        _ids.clear();
        _updatePanel();
        if (typeof window.updateSelectionVisuals === 'function') {
            window.updateSelectionVisuals();
        } else {
            _updateVisuals();
        }
        _updateGroupButtonState();
    }

    /**
     * Maybe clear selection (with marquee debounce)
     */
    function maybeClear() {
        const now = Date.now();
        if (_marqueeActive) return;
        if (now - _lastMarqueeEndTs < 250) return;
        clear();
    }

    /**
     * Add nodes to selection
     */
    function add(ids) {
        (ids || []).forEach(id => {
            if (id) _ids.add(id);
        });
        _updatePanel();
        if (typeof window.updateSelectionVisuals === 'function') {
            window.updateSelectionVisuals();
        } else {
            _updateVisuals();
        }
        _updateGroupButtonState();
    }

    /**
     * Remove nodes from selection
     */
    function remove(ids) {
        (ids || []).forEach(id => {
            _ids.delete(id);
        });
        _updatePanel();
        if (typeof window.updateSelectionVisuals === 'function') {
            window.updateSelectionVisuals();
        } else {
            _updateVisuals();
        }
        _updateGroupButtonState();
    }

    // =========================================================================
    // OKLCH COLOR UTILITIES
    // =========================================================================

    function _oklchToHex(L, C, H) {
        const hRad = H * Math.PI / 180;
        const a = C * Math.cos(hRad);
        const b = C * Math.sin(hRad);

        const l_ = L / 100 + 0.3963377774 * a + 0.2158037573 * b;
        const m_ = L / 100 - 0.1055613458 * a - 0.0638541728 * b;
        const s_ = L / 100 - 0.0894841775 * a - 1.2914855480 * b;

        const l = l_ * l_ * l_;
        const m = m_ * m_ * m_;
        const s = s_ * s_ * s_;

        let rLin = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s;
        let gLin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
        let bLin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s;

        const gamma = x => x <= 0 ? 0 : x >= 1 ? 1 : x < 0.0031308 ? 12.92 * x : 1.055 * Math.pow(x, 1 / 2.4) - 0.055;

        let rOut = Math.round(gamma(rLin) * 255);
        let gOut = Math.round(gamma(gLin) * 255);
        let bOut = Math.round(gamma(bLin) * 255);

        rOut = Math.max(0, Math.min(255, rOut));
        gOut = Math.max(0, Math.min(255, gOut));
        bOut = Math.max(0, Math.min(255, bOut));

        return '#' + [rOut, gOut, bOut].map(x => x.toString(16).padStart(2, '0')).join('');
    }

    function _dimColor(hexColor, factor = 0.2) {
        const hex = hexColor.replace('#', '');
        const r = Math.round(parseInt(hex.substr(0, 2), 16) * (1 - factor));
        const g = Math.round(parseInt(hex.substr(2, 2), 16) * (1 - factor));
        const b = Math.round(parseInt(hex.substr(4, 2), 16) * (1 - factor));
        return '#' + [r, g, b].map(x => Math.max(0, Math.min(255, x)).toString(16).padStart(2, '0')).join('');
    }

    // =========================================================================
    // PENDULUM ANIMATION
    // =========================================================================

    function _updatePendulums(dt) {
        const PENDULUM = CORE.PENDULUM;
        const p1 = PENDULUM.hue;
        const p2 = PENDULUM.chroma;

        // Pendulum 1: Modulates hue rotation speed
        const accel1 = -(p1.gravity / p1.length) * Math.sin(p1.angle);
        p1.velocity += accel1 * dt;
        p1.velocity *= p1.damping;
        p1.angle += p1.velocity * dt;

        // Continuous hue rotation
        const speedMod = 1 + Math.sin(p1.angle) * 0.5;
        PENDULUM.currentHue = (PENDULUM.currentHue + p1.rotationSpeed * speedMod * (dt / 16)) % 360;

        // Pendulum 2: Chroma with coupling
        const coupling = 0.00015 * Math.sin(p1.angle);
        const accel2 = -(p2.gravity / p2.length) * Math.sin(p2.angle) + coupling;
        p2.velocity += accel2 * dt;
        p2.velocity *= p2.damping;
        p2.angle += p2.velocity * dt;

        // Lightness phase
        PENDULUM.lightness.phase += PENDULUM.lightness.speed * dt;
    }

    function _getSelectionColor(phaseOffset = 0) {
        const PENDULUM = CORE.PENDULUM;
        const p2 = PENDULUM.chroma;
        const p3 = PENDULUM.lightness;

        const H = (PENDULUM.currentHue + phaseOffset * 45) % 360;
        const C = Math.max(0.18, p2.center + Math.sin(p2.angle + phaseOffset * Math.PI * 2) * p2.amplitude);
        const L = p3.center + Math.sin(p3.phase + phaseOffset * Math.PI * 4) * p3.amplitude;

        return _oklchToHex(L, C, H);
    }

    function _getNodeSpatialPhase(node) {
        const x = node.x || 0;
        const y = node.y || 0;
        const z = node.z || 0;

        const distance = Math.sqrt(x * x + y * y + z * z);
        const PENDULUM = CORE.PENDULUM;
        const scale = PENDULUM.ripple ? (PENDULUM.ripple.scale || 200) : 200;
        const ripplePhase = (distance / scale) % 1;

        const angle = Math.atan2(y, x);
        const angularOffset = Math.sin(angle * 3) * 0.1;

        return (ripplePhase + angularOffset + 1) % 1;
    }

    function _animateSelectionColors(timestamp) {
        const PENDULUM = CORE.PENDULUM;
        if (!PENDULUM.running) return;

        const dt = PENDULUM.lastTime ? Math.min(timestamp - PENDULUM.lastTime, 50) : 16;
        PENDULUM.lastTime = timestamp;

        _updatePendulums(dt);

        if (_ids.size > 0 && typeof Graph !== 'undefined' && Graph?.graphData) {
            const nodes = Graph.graphData().nodes || [];

            nodes.forEach(node => {
                if (_ids.has(node.id)) {
                    const spatialPhase = _getNodeSpatialPhase(node);
                    node.color = _getSelectionColor(spatialPhase);
                }
            });

            if (typeof toColorNumber === 'function') {
                Graph.nodeColor(n => toColorNumber(n.color, 0x888888));
            }
        }

        requestAnimationFrame(_animateSelectionColors);
    }

    function startAnimation() {
        const PENDULUM = CORE.PENDULUM;
        if (!PENDULUM.running) {
            PENDULUM.running = true;
            PENDULUM.hue.velocity = 0.02 + Math.random() * 0.01;
            PENDULUM.chroma.velocity = 0.015 + Math.random() * 0.01;
            PENDULUM.lastTime = 0;
            requestAnimationFrame(_animateSelectionColors);
        }
    }

    function stopAnimation() {
        CORE.PENDULUM.running = false;
    }

    // =========================================================================
    // VISUAL UPDATES
    // =========================================================================

    function _updateVisuals() {
        if (typeof Graph === 'undefined' || !Graph?.graphData) return;

        const nodes = Graph.graphData().nodes || [];
        const hasSelection = _ids.size > 0;
        const SELECTION_SIZE_MULT = CORE.SELECTION_SIZE_MULT;

        nodes.forEach(node => {
            const isSelected = _ids.has(node.id);

            // Save original for restoration
            if (hasSelection && !_originalColorsForDim.has(node.id)) {
                _originalColorsForDim.set(node.id, {
                    color: node.color,
                    val: node.val || 1
                });
            }

            if (isSelected && !_selectionOriginals.has(node.id)) {
                _selectionOriginals.set(node.id, {
                    color: node.color,
                    val: node.val || 1
                });
            }

            // Apply styling
            if (hasSelection) {
                if (isSelected) {
                    const orig = _selectionOriginals.get(node.id);
                    node.val = (orig?.val || 1) * SELECTION_SIZE_MULT;
                } else {
                    const orig = _originalColorsForDim.get(node.id);
                    if (orig) {
                        node.color = _dimColor(orig.color, 0.4); // Less aggressive dimming (was 0.5)
                        node.val = orig.val * 0.7;
                    }
                }
            } else {
                // Restore originals
                const orig = _originalColorsForDim.get(node.id);
                if (orig) {
                    node.color = orig.color;
                    node.val = orig.val;
                }
            }

            // Update halo visibility
            if (node.__selectionHalo) {
                node.__selectionHalo.visible = isSelected;
            }
        });

        // Handle animation state
        if (hasSelection) {
            startAnimation();
        } else {
            stopAnimation();
            _selectionOriginals.clear();
            _originalColorsForDim.clear();
        }

        if (typeof REFRESH !== 'undefined') {
            REFRESH.throttled();
        } else if (Graph) {
            REFRESH.throttled();
        }
    }

    function _updatePanel() {
        if (typeof updateSelectionPanel === 'function') {
            updateSelectionPanel();
        }
    }

    function _updateGroupButtonState() {
        if (typeof updateGroupButtonState === 'function') {
            updateGroupButtonState();
        }
    }

    // =========================================================================
    // NODE OVERLAYS (3D halos)
    // =========================================================================

    function ensureOverlays(node) {
        if (!node) return null;
        if (node.__overlayGroup) return node.__overlayGroup;

        // Lazy init geometry
        if (!_selectionHaloGeometry) {
            _selectionHaloGeometry = new THREE.SphereGeometry(1, 12, 12);
            _groupHaloGeometry = new THREE.SphereGeometry(1, 12, 12);
        }

        const group = new THREE.Group();

        const selectionMaterial = new THREE.MeshBasicMaterial({
            color: 0x00ffff,
            transparent: true,
            opacity: 0.85,
            depthWrite: false
        });
        const selectionHalo = new THREE.Mesh(_selectionHaloGeometry, selectionMaterial);
        selectionHalo.visible = false;
        selectionHalo.renderOrder = 3;

        const groupMaterial = new THREE.MeshBasicMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.45,
            depthWrite: false
        });
        const groupHalo = new THREE.Mesh(_groupHaloGeometry, groupMaterial);
        groupHalo.visible = false;
        groupHalo.renderOrder = 2;

        group.add(selectionHalo);
        group.add(groupHalo);

        node.__selectionHalo = selectionHalo;
        node.__groupHalo = groupHalo;
        node.__overlayGroup = group;

        return group;
    }

    function updateOverlayScale(node) {
        const APPEARANCE_STATE = typeof window !== 'undefined' ? window.APPEARANCE_STATE : { nodeScale: 1 };
        const base = Math.max(0.6, (node.val || 1) * (APPEARANCE_STATE?.nodeScale || 1));
        const selectionScale = base * 2.5;
        const groupScale = base * 1.8;

        if (node.__selectionHalo) {
            node.__selectionHalo.scale.set(selectionScale, selectionScale, selectionScale);
        }
        if (node.__groupHalo) {
            node.__groupHalo.scale.set(groupScale, groupScale, groupScale);
        }
    }

    // =========================================================================
    // MARQUEE STATE
    // =========================================================================

    function setMarqueeActive(active) {
        _marqueeActive = active;
        if (!active) {
            _lastMarqueeEndTs = Date.now();
        }
    }

    function setMarqueeStart(pos) {
        _marqueeStart = pos;
    }

    function setMarqueeAdditive(additive) {
        _marqueeAdditive = additive;
    }

    // =========================================================================
    // UI HELPERS
    // =========================================================================

    function formatCountList(items, limit = 4) {
        return items.slice(0, limit).map(([key, count]) => `${key} ${count}`).join(' · ') || '--';
    }

    function appendSelectionRow(container, label, value) {
        const row = document.createElement('div');
        row.className = 'selection-row';
        const labelEl = document.createElement('span');
        labelEl.className = 'label';
        labelEl.textContent = label;
        const valueEl = document.createElement('span');
        valueEl.textContent = value || '--';
        row.appendChild(labelEl);
        row.appendChild(valueEl);
        container.appendChild(row);
    }

    // =========================================================================
    // SELECTION PANEL
    // =========================================================================

    function updateSelectionPanel() {
        const panel = document.getElementById('selection-panel');
        const body = document.getElementById('selection-body');
        const title = document.getElementById('selection-title');
        if (!panel || !body) return;

        const nodes = getSelectedNodes();
        if (!nodes.length) {
            panel.classList.remove('visible');
            body.innerHTML = '';
            return;
        }

        panel.classList.add('visible');
        if (title) title.textContent = `SELECTION (${nodes.length})`;
        body.innerHTML = '';

        if (nodes.length <= 3) {
            nodes.forEach(node => {
                const item = document.createElement('div');
                item.className = 'selection-item';
                const name = document.createElement('div');
                name.className = 'selection-name';
                name.textContent = node.name || node.id || 'Unknown';
                item.appendChild(name);
                appendSelectionRow(item, 'Family', typeof getNodeAtomFamily === 'function' ? getNodeAtomFamily(node) : '--');
                appendSelectionRow(item, 'Ring', typeof getNodeRing === 'function' ? getNodeRing(node) : '--');
                appendSelectionRow(item, 'Tier', typeof getNodeTier === 'function' ? getNodeTier(node) : '--');
                appendSelectionRow(item, 'Role', node.role || '--');
                const filePath = node.file_path || node.file || '';
                if (filePath) {
                    const shortPath = filePath.length > 48 ? '...' + filePath.slice(-45) : filePath;
                    appendSelectionRow(item, 'File', shortPath);
                }
                body.appendChild(item);
            });
        } else {
            const summary = document.createElement('div');
            summary.className = 'selection-summary';

            const families = typeof collectCounts === 'function' ? collectCounts(nodes, n => typeof getNodeAtomFamily === 'function' ? getNodeAtomFamily(n) : '--') : [];
            const rings = typeof collectCounts === 'function' ? collectCounts(nodes, n => typeof getNodeRing === 'function' ? getNodeRing(n) : '--') : [];
            const tiers = typeof collectCounts === 'function' ? collectCounts(nodes, n => typeof getNodeTier === 'function' ? getNodeTier(n) : '--') : [];

            const total = document.createElement('div');
            total.textContent = `Total: ${nodes.length} nodes`;
            summary.appendChild(total);

            const familyRow = document.createElement('div');
            familyRow.textContent = `Family: ${formatCountList(families)}`;
            summary.appendChild(familyRow);

            const ringRow = document.createElement('div');
            ringRow.textContent = `Ring: ${formatCountList(rings)}`;
            summary.appendChild(ringRow);

            const tierRow = document.createElement('div');
            tierRow.textContent = `Tier: ${formatCountList(tiers)}`;
            summary.appendChild(tierRow);

            const numericKeys = [
                ['tokens', 'TOKENS'],
                ['bytes', 'BYTES'],
                ['loc', 'LOC'],
                ['lines', 'LINES'],
                ['lines_of_code', 'LOC'],
                ['size', 'SIZE']
            ];
            const totals = {};
            nodes.forEach(node => {
                numericKeys.forEach(([key]) => {
                    const value = Number(node[key]);
                    if (Number.isFinite(value)) {
                        totals[key] = (totals[key] || 0) + value;
                    }
                });
            });
            numericKeys.forEach(([key, label]) => {
                if (totals[key]) {
                    const row = document.createElement('div');
                    row.textContent = `${label}: ${Math.round(totals[key])}`;
                    summary.appendChild(row);
                }
            });

            body.appendChild(summary);
        }

        if (typeof HudLayoutManager !== 'undefined' && HudLayoutManager.reflow) {
            HudLayoutManager.reflow();
        }
    }

    // =========================================================================
    // SELECTION MODAL
    // =========================================================================

    function showSelectionModal() {
        const nodes = getSelectedNodes();
        if (!nodes.length) {
            if (typeof showToast === 'function') showToast('No nodes selected');
            return;
        }

        const overlay = document.getElementById('selection-modal-overlay');
        const title = document.getElementById('selection-modal-title');
        const statsContainer = document.getElementById('selection-modal-stats');
        const body = document.getElementById('selection-modal-body');

        if (!overlay || !body) return;

        // Calculate aggregates
        let totalTokens = 0, totalBytes = 0, totalLoc = 0;
        const tierCounts = {};
        const ringCounts = {};
        const familyCounts = {};

        nodes.forEach(node => {
            totalTokens += Number(node.tokens) || 0;
            totalBytes += Number(node.bytes) || 0;
            totalLoc += Number(node.loc || node.lines || node.lines_of_code) || 0;

            const tier = typeof getNodeTier === 'function' ? getNodeTier(node) : '--';
            const ring = typeof getNodeRing === 'function' ? getNodeRing(node) : '--';
            const family = typeof getNodeAtomFamily === 'function' ? getNodeAtomFamily(node) : '--';

            tierCounts[tier] = (tierCounts[tier] || 0) + 1;
            ringCounts[ring] = (ringCounts[ring] || 0) + 1;
            familyCounts[family] = (familyCounts[family] || 0) + 1;
        });

        const maxVal = Math.max(...nodes.map(n => n.val || n.size || 1));

        title.textContent = `SELECTED NODES (${nodes.length})`;

        // Build stats bar
        statsContainer.innerHTML = '';
        const stats = [
            ['NODES', nodes.length.toLocaleString()],
            ['TOKENS', totalTokens.toLocaleString()],
            ['BYTES', totalBytes.toLocaleString()],
            ['LOC', totalLoc.toLocaleString()],
            ['TIERS', Object.keys(tierCounts).join(', ')],
            ['FAMILIES', Object.keys(familyCounts).length]
        ];
        stats.forEach(([label, value]) => {
            if (value && value !== '0') {
                const stat = document.createElement('div');
                stat.className = 'selection-modal-stat';
                stat.innerHTML = `
                    <span class="selection-modal-stat-label">${label}</span>
                    <span class="selection-modal-stat-value">${value}</span>
                `;
                statsContainer.appendChild(stat);
            }
        });

        // Build table
        const sortedNodes = [...nodes].sort((a, b) => (b.val || b.size || 1) - (a.val || a.size || 1));

        body.innerHTML = `
            <table class="selection-modal-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Tier</th>
                        <th>Ring</th>
                        <th>Family</th>
                        <th>Level</th>
                        <th>Tokens</th>
                        <th>LOC</th>
                        <th>Relevance</th>
                    </tr>
                </thead>
                <tbody id="selection-modal-tbody"></tbody>
            </table>
        `;

        const tbody = document.getElementById('selection-modal-tbody');
        sortedNodes.forEach(node => {
            const tier = typeof getNodeTier === 'function' ? getNodeTier(node) : '--';
            const ring = typeof getNodeRing === 'function' ? getNodeRing(node) : '--';
            const family = typeof getNodeAtomFamily === 'function' ? getNodeAtomFamily(node) : '--';
            const level = node.level || node.scale_level || 'L3';
            const tokens = Number(node.tokens) || '--';
            const loc = Number(node.loc || node.lines || node.lines_of_code) || '--';
            const relevance = ((node.val || node.size || 1) / maxVal * 100).toFixed(0);

            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="node-name" title="${node.name || node.id}">${node.name || node.id}</td>
                <td><span class="level-badge tier-badge">${tier}</span></td>
                <td><span class="level-badge ring-badge">${ring}</span></td>
                <td><span class="level-badge family-badge">${family}</span></td>
                <td>${level}</td>
                <td class="numeric">${typeof tokens === 'number' ? tokens.toLocaleString() : tokens}</td>
                <td class="numeric">${typeof loc === 'number' ? loc.toLocaleString() : loc}</td>
                <td>
                    <div class="relevance-bar">
                        <div class="relevance-fill" style="width: ${relevance}%"></div>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });

        overlay.classList.add('visible');
    }

    function hideSelectionModal() {
        const overlay = document.getElementById('selection-modal-overlay');
        if (overlay) overlay.classList.remove('visible');
    }

    function initSelectionModal() {
        const overlay = document.getElementById('selection-modal-overlay');
        const closeBtn = document.getElementById('selection-modal-close');
        const selectionTitle = document.getElementById('selection-title');

        if (closeBtn) {
            closeBtn.addEventListener('click', hideSelectionModal);
        }

        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) hideSelectionModal();
            });
        }

        if (selectionTitle) {
            selectionTitle.style.cursor = 'pointer';
            selectionTitle.addEventListener('click', showSelectionModal);
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'i' && !e.ctrlKey && !e.metaKey && !e.altKey) {
                const activeEl = document.activeElement;
                if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA')) return;
                if (getSelectedNodes().length > 0) {
                    e.preventDefault();
                    showSelectionModal();
                }
            }
            if (e.key === 'Escape') {
                hideSelectionModal();
            }
        });
    }

    // =========================================================================
    // SELECTION BOX / MARQUEE
    // =========================================================================

    let _selectionBox = null;

    function updateSelectionBox(rect) {
        if (!_selectionBox) _selectionBox = document.getElementById('selection-box');
        if (!_selectionBox) return;
        _selectionBox.style.display = 'block';
        _selectionBox.style.left = `${rect.left}px`;
        _selectionBox.style.top = `${rect.top}px`;
        _selectionBox.style.width = `${rect.width}px`;
        _selectionBox.style.height = `${rect.height}px`;
    }

    function getNodeScreenPosition(node) {
        if (typeof Graph === 'undefined' || !Graph?.camera || !node) return null;
        if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return null;
        const camera = Graph.camera();
        const vector = new THREE.Vector3(node.x, node.y, node.z || 0);
        vector.project(camera);
        const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
        const y = (-vector.y * 0.5 + 0.5) * window.innerHeight;
        return { x, y };
    }

    function selectNodesInBox(rect, additive = true) {
        if (typeof Graph === 'undefined' || !Graph?.graphData) return;
        const nodes = Graph.graphData().nodes || [];
        const selected = [];
        nodes.forEach(node => {
            const pos = getNodeScreenPosition(node);
            if (!pos) return;
            if (pos.x >= rect.left && pos.x <= rect.right &&
                pos.y >= rect.top && pos.y <= rect.bottom) {
                if (node.id) selected.push(node.id);
            }
        });
        if (selected.length) {
            set(selected, additive);
        }
    }

    function setupSelectionInteractions() {
        const clearBtn = document.getElementById('selection-clear');
        if (clearBtn) {
            clearBtn.onclick = () => clear();
        }

        const groupBtn = document.getElementById('btn-create-group');
        if (groupBtn && typeof createGroupFromSelection === 'function') {
            groupBtn.onclick = () => createGroupFromSelection();
        }

        _selectionBox = document.getElementById('selection-box');
        if (typeof Graph === 'undefined' || !Graph?.renderer || !_selectionBox) return;

        const canvas = Graph.renderer().domElement;
        if (!canvas) return;

        const onPointerDown = (e) => {
            if (e.button !== 0) return;
            if (typeof SPACE_PRESSED !== 'undefined' && SPACE_PRESSED) return;
            if (e.target !== canvas) return;
            if (typeof HOVERED_NODE !== 'undefined' && HOVERED_NODE) return;
            _marqueeActive = true;
            _marqueeAdditive = !!e.shiftKey;
            _marqueeStart = { x: e.clientX, y: e.clientY };
            updateSelectionBox(typeof getBoxRect === 'function' ? getBoxRect(_marqueeStart, _marqueeStart) : { left: e.clientX, top: e.clientY, width: 0, height: 0 });
            if (Graph.controls()) {
                Graph.controls().enabled = false;
            }
            e.preventDefault();
        };

        const onPointerMove = (e) => {
            if (!_marqueeActive || !_marqueeStart) return;
            updateSelectionBox(typeof getBoxRect === 'function' ? getBoxRect(_marqueeStart, { x: e.clientX, y: e.clientY }) : { left: Math.min(_marqueeStart.x, e.clientX), top: Math.min(_marqueeStart.y, e.clientY), width: Math.abs(e.clientX - _marqueeStart.x), height: Math.abs(e.clientY - _marqueeStart.y), right: Math.max(_marqueeStart.x, e.clientX), bottom: Math.max(_marqueeStart.y, e.clientY) });
        };

        const finishSelection = (e) => {
            if (!_marqueeActive || !_marqueeStart) return;
            const rect = typeof getBoxRect === 'function' ? getBoxRect(_marqueeStart, { x: e.clientX, y: e.clientY }) : { left: Math.min(_marqueeStart.x, e.clientX), top: Math.min(_marqueeStart.y, e.clientY), width: Math.abs(e.clientX - _marqueeStart.x), height: Math.abs(e.clientY - _marqueeStart.y), right: Math.max(_marqueeStart.x, e.clientX), bottom: Math.max(_marqueeStart.y, e.clientY) };
            _selectionBox.style.display = 'none';
            const additive = _marqueeAdditive;
            _marqueeActive = false;
            _marqueeStart = null;
            _marqueeAdditive = false;
            _lastMarqueeEndTs = Date.now();
            if (Graph.controls()) {
                Graph.controls().enabled = true;
            }
            const didDrag = rect.width > 4 && rect.height > 4;
            if (didDrag) {
                // Only update timestamp if we actually dragged, to prevent blocking valid background clicks
                _lastMarqueeEndTs = Date.now();
                selectNodesInBox(rect, additive);
            } else {
                // If it was just a click, do NOT update timestamp so maybeClear() can work
                _lastMarqueeEndTs = 0;
            }
        };

        canvas.addEventListener('pointerdown', onPointerDown, { passive: false });
        canvas.addEventListener('pointermove', onPointerMove, { passive: true });
        canvas.addEventListener('pointerup', finishSelection, { passive: true });
        canvas.addEventListener('pointerleave', finishSelection, { passive: true });
    }

    // =========================================================================
    // SYNC AND INIT
    // =========================================================================

    function syncSelectionAfterGraphUpdate() {
        if (typeof Graph === 'undefined' || !Graph?.graphData) return;
        const visibleIds = new Set((Graph.graphData().nodes || []).map(n => n.id));
        const idsToRemove = [];
        Array.from(_ids).forEach(id => {
            if (!visibleIds.has(id)) {
                idsToRemove.push(id);
            }
        });
        if (idsToRemove.length > 0) {
            remove(idsToRemove);
        } else {
            _updateVisuals();
        }
        _updateGroupButtonState();
    }

    function initSelectionState(data) {
        if (typeof buildDatasetKey === 'function') {
            window.DATASET_KEY = buildDatasetKey(data);
            window.GROUPS_STORAGE_KEY = `collider_groups_${window.DATASET_KEY}`;
        }
        if (typeof loadGroups === 'function') loadGroups();
        if (typeof renderGroupList === 'function') renderGroupList();
        updateSelectionPanel();
        _updateGroupButtonState();
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Core selection
        set,
        toggle,
        clear,
        maybeClear,
        add,
        remove,
        getSelectedNodes,

        // State access
        get ids() { return _ids; },
        get size() { return _ids.size; },
        has(id) { return _ids.has(id); },

        // Animation
        startAnimation,
        stopAnimation,

        // Overlays
        ensureOverlays,
        updateOverlayScale,

        // Marquee
        setMarqueeActive,
        setMarqueeStart,
        setMarqueeAdditive,
        get marqueeActive() { return _marqueeActive; },
        get marqueeStart() { return _marqueeStart; },
        get marqueeAdditive() { return _marqueeAdditive; },
        get lastMarqueeEndTs() { return _lastMarqueeEndTs; },

        // Internal access (for migration)
        _selectionOriginals,
        _originalColorsForDim,

        // UI (moved from app.js)
        updateSelectionPanel,
        showSelectionModal,
        hideSelectionModal,
        initSelectionModal,
        updateSelectionBox,
        getNodeScreenPosition,
        selectNodesInBox,
        setupSelectionInteractions,
        syncSelectionAfterGraphUpdate,
        initSelectionState
    };
})();

// Backward compatibility aliases - Using getters to ensure live updates
// Note: All variables use Object.defineProperty to avoid duplicate declarations with app.js
// SELECTED_NODE_IDS - selection.js is now the SINGLE SOURCE OF TRUTH (unified in modularization)
Object.defineProperty(window, 'SELECTED_NODE_IDS', { get: () => SELECT.ids, configurable: true });
Object.defineProperty(window, 'MARQUEE_ACTIVE', { get: () => SELECT.marqueeActive, configurable: true });
Object.defineProperty(window, 'MARQUEE_START', { get: () => SELECT.marqueeStart, configurable: true });
Object.defineProperty(window, 'MARQUEE_ADDITIVE', { get: () => SELECT.marqueeAdditive, configurable: true });
Object.defineProperty(window, 'LAST_MARQUEE_END_TS', { get: () => SELECT.lastMarqueeEndTs, configurable: true });
// selectionOriginals, originalColorsForDim - app.js owns these, not duplicated here

function getSelectedNodes() { return SELECT.getSelectedNodes(); }
function setSelection(ids, additive) { SELECT.set(ids, additive); }
function toggleSelection(node) { SELECT.toggle(node); }
function clearSelection() { SELECT.clear(); }
function maybeClearSelection() { SELECT.maybeClear(); }
function startSelectionAnimation() { SELECT.startAnimation(); }
function stopSelectionAnimation() { SELECT.stopAnimation(); }
function ensureNodeOverlays(node) { return SELECT.ensureOverlays(node); }
function updateOverlayScale(node) { SELECT.updateOverlayScale(node); }

// UI functions (moved from app.js)
function updateSelectionPanel() { SELECT.updateSelectionPanel(); }
function showSelectionModal() { SELECT.showSelectionModal(); }
function hideSelectionModal() { SELECT.hideSelectionModal(); }
function initSelectionModal() { SELECT.initSelectionModal(); }
function updateSelectionBox(rect) { SELECT.updateSelectionBox(rect); }
function getNodeScreenPosition(node) { return SELECT.getNodeScreenPosition(node); }
function selectNodesInBox(rect, additive) { SELECT.selectNodesInBox(rect, additive); }
function setupSelectionInteractions() { SELECT.setupSelectionInteractions(); }
function syncSelectionAfterGraphUpdate() { SELECT.syncSelectionAfterGraphUpdate(); }
function initSelectionState(data) { SELECT.initSelectionState(data); }

console.log('[Module] SELECT loaded - selection UI, modal, marquee, animation');
