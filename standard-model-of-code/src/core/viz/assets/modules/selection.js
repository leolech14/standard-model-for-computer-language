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

const SELECT = (function() {
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

    function _dimColor(hexColor, factor = 0.33) {
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
                        node.color = _dimColor(orig.color, 0.5);
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
            Graph.refresh();
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
        _originalColorsForDim
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
