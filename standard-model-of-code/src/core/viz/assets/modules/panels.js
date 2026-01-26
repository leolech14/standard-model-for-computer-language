/**
 * PANELS MODULE
 *
 * Manages floating panels and HUD layout for the visualization.
 * Handles panel open/close, command bar, and UI dimming.
 *
 * Usage:
 *   PANELS.open('view')       // Open a panel
 *   PANELS.close('view')      // Close a panel
 *   PANELS.toggle('view')     // Toggle panel visibility
 *   PANELS.initCommandBar()   // Wire up command bar buttons
 */

const PANELS = (function() {
    'use strict';

    // =========================================================================
    // STATE
    // =========================================================================

    let _activePanelId = null;

    // =========================================================================
    // PANEL FUNCTIONS
    // =========================================================================

    /**
     * Open a panel by ID
     */
    function open(panelId) {
        const panel = document.getElementById('panel-' + panelId);
        const btn = document.getElementById('cmd-' + panelId);

        // Close any already-open panel
        if (_activePanelId && _activePanelId !== panelId) {
            close(_activePanelId);
        }

        if (panel) {
            panel.classList.add('visible');
            setTimeout(() => { panel.style.opacity = '1'; }, 10);
        }
        if (btn) btn.classList.add('active');
        _activePanelId = panelId;

        // Dim the universe when panel opens
        document.body.classList.add('ui-active');

        // Dim starfield via JS
        if (typeof STARFIELD !== 'undefined' && STARFIELD?.material) {
            const baseOpacity = typeof STARFIELD_OPACITY !== 'undefined' ? STARFIELD_OPACITY : 0.5;
            STARFIELD.material.opacity = baseOpacity * 0.3;
        }
    }

    /**
     * Close a panel by ID
     */
    function close(panelId) {
        const panel = document.getElementById('panel-' + panelId);
        const btn = document.getElementById('cmd-' + panelId);

        if (panel) {
            panel.classList.remove('visible');
        }
        if (btn) btn.classList.remove('active');
        if (_activePanelId === panelId) _activePanelId = null;

        // Restore universe when all panels closed
        if (!_activePanelId) {
            document.body.classList.remove('ui-active');

            // Restore starfield
            if (typeof STARFIELD !== 'undefined' && STARFIELD?.material) {
                const starsBtn = document.getElementById('btn-stars');
                const starsVisible = starsBtn && starsBtn.classList.contains('active');
                const baseOpacity = typeof STARFIELD_OPACITY !== 'undefined' ? STARFIELD_OPACITY : 0.5;
                STARFIELD.material.opacity = starsVisible ? baseOpacity : 0;
            }
        }
    }

    /**
     * Toggle a panel
     */
    function toggle(panelId) {
        const panel = document.getElementById('panel-' + panelId);
        if (panel && panel.classList.contains('visible')) {
            close(panelId);
        } else {
            open(panelId);
        }
    }

    /**
     * Get active panel ID
     */
    function getActive() {
        return _activePanelId;
    }

    // =========================================================================
    // COMMAND BAR INITIALIZATION
    // =========================================================================

    function initCommandBar() {
        const cmdBtns = {
            'cmd-view': 'view',
            'cmd-filter': 'filter',
            'cmd-style': 'style',
            'cmd-settings': 'settings'
        };

        Object.entries(cmdBtns).forEach(([btnId, panelId]) => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.addEventListener('click', () => toggle(panelId));
            }
        });

        // Settings panel: Oval margin slider
        _initOvalMarginSlider();
        _initOvalDebugToggle();

        // Style panel sliders (consolidated from app.js)
        _initStylePanelSliders();
        _initToggleSwitches();
        _initSegmentedControls();
        _initCommandBarActions();
    }

    // ═══════════════════════════════════════════════════════════════════
    // STYLE PANEL SLIDERS - Connected to appearance system
    // ═══════════════════════════════════════════════════════════════════

    function _initStylePanelSliders() {
        // Node Size Slider
        const nodeSizeSlider = document.getElementById('node-size-slider');
        const nodeSizeValue = document.getElementById('node-size-value');
        if (nodeSizeSlider) {
            nodeSizeSlider.addEventListener('input', (e) => {
                const val = parseFloat(e.target.value);
                if (nodeSizeValue) nodeSizeValue.textContent = val.toFixed(1) + 'x';
                if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.nodeScale = val;
                if (typeof Graph !== 'undefined' && Graph) {
                    Graph.nodeVal(node => (node.val || node.size || 1) * val);
                }
            });
        }

        // Edge Opacity Slider
        const edgeOpacitySlider = document.getElementById('edge-opacity-slider');
        const edgeOpacityValue = document.getElementById('edge-opacity-value');
        if (edgeOpacitySlider) {
            edgeOpacitySlider.addEventListener('input', (e) => {
                const val = parseInt(e.target.value);
                if (edgeOpacityValue) edgeOpacityValue.textContent = val + '%';
                if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.edgeOpacity = val / 100;
                if (typeof applyEdgeMode === 'function') applyEdgeMode();
            });
        }

        // Density Slider (filter panel) - NOTE: #density-slider2 not in current HTML template
        // Code retained for future filter panel implementation
        const densitySlider2 = document.getElementById('density-slider2');
        const densityValue2 = document.getElementById('density-value2');
        if (densitySlider2) {
            densitySlider2.addEventListener('input', (e) => {
                const val = parseInt(e.target.value);
                if (densityValue2) densityValue2.textContent = val + '%';
                if (typeof CURRENT_DENSITY !== 'undefined') window.CURRENT_DENSITY = val;
                if (typeof refreshGraph === 'function') refreshGraph();
            });
        }
    }

    function _initToggleSwitches() {
        document.querySelectorAll('.toggle-switch').forEach(toggle => {
            toggle.addEventListener('click', () => {
                toggle.classList.toggle('active');
            });
        });
    }

    function _initSegmentedControls() {
        document.querySelectorAll('.segmented-control').forEach(control => {
            control.querySelectorAll('.segment').forEach(segment => {
                segment.addEventListener('click', () => {
                    control.querySelectorAll('.segment').forEach(s => s.classList.remove('active'));
                    segment.classList.add('active');

                    // Handle dimension change
                    if (control.id === 'dim-control') {
                        const dim = segment.dataset.dim;
                        const newIs3D = (dim !== '2');
                        // G07 FIX: Use VIS_STATE for centralized state management
                        if (typeof VIS_STATE !== 'undefined' && VIS_STATE.setIs3D) {
                            VIS_STATE.setIs3D(newIs3D, 'panels.dim-control');
                        } else {
                            window.IS_3D = newIs3D;
                        }
                        if (typeof Graph !== 'undefined' && Graph) Graph.numDimensions(newIs3D ? 3 : 2);
                    }

                    // Handle node color mode
                    if (control.id === 'node-color-control') {
                        const mode = segment.dataset.mode;
                        if (mode && typeof setNodeColorMode === 'function') {
                            setNodeColorMode(mode);
                        }
                    }

                    // Handle edge color mode
                    if (control.id === 'edge-color-control') {
                        const mode = segment.dataset.mode;
                        if (mode) {
                            if (typeof EDGE_MODE !== 'undefined') window.EDGE_MODE = mode;
                            if (typeof applyEdgeMode === 'function') applyEdgeMode();
                        }
                    }

                    // Handle panel layout
                    if (control.id === 'layout-control') {
                        const layout = segment.dataset.layout;
                        if (layout) {
                            document.body.setAttribute('data-layout', layout);
                        }
                    }
                });
            });
        });
    }

    function _initCommandBarActions() {
        // Skip if REGISTRY not available (defensive)
        if (typeof REGISTRY === 'undefined' || !REGISTRY.register) return;

        // File mode toggle
        REGISTRY.register('cmd-files2', () => {
            if (typeof setFileModeState === 'function') {
                const newState = typeof fileMode !== 'undefined' ? !fileMode : true;
                setFileModeState(newState);
                const btn = document.getElementById('cmd-files2');
                if (btn) btn.classList.toggle('active', newState);
            }
        }, { desc: 'Toggle File Boundaries Mode' });

        // Flow mode toggle
        REGISTRY.register('cmd-flow2', () => {
            if (typeof toggleFlowMode === 'function') {
                toggleFlowMode();
                const btn = document.getElementById('cmd-flow2');
                if (btn && typeof flowMode !== 'undefined') btn.classList.toggle('active', flowMode);
            }
        }, { desc: 'Toggle Flow Mode' });

        // 3D toggle
        REGISTRY.register('cmd-3d', () => {
            if (typeof toggleDimensions === 'function') {
                toggleDimensions();
            } else {
                // G07 FIX: Use VIS_STATE for centralized state management
                const currentIs3D = typeof VIS_STATE !== 'undefined' ? VIS_STATE.getIs3D() : window.IS_3D;
                const newIs3D = !currentIs3D;
                if (typeof VIS_STATE !== 'undefined' && VIS_STATE.setIs3D) {
                    VIS_STATE.setIs3D(newIs3D, 'panels.cmd-3d');
                } else {
                    window.IS_3D = newIs3D;
                }
                if (typeof Graph !== 'undefined' && Graph) Graph.numDimensions(newIs3D ? 3 : 2);
                const btnDim = document.getElementById('btn-dimensions');
                if (btnDim) btnDim.textContent = newIs3D ? '2D' : '3D';
            }
            const btn = document.getElementById('cmd-3d');
            const is3D = typeof VIS_STATE !== 'undefined' ? VIS_STATE.getIs3D() : window.IS_3D;
            if (btn) btn.classList.toggle('active', is3D);

            // Update dim-control if exists
            const dimControl = document.getElementById('dim-control');
            if (dimControl) {
                const currentIs3D = typeof VIS_STATE !== 'undefined' ? VIS_STATE.getIs3D() : window.IS_3D;
                dimControl.querySelectorAll('.segment').forEach(s => {
                    s.classList.toggle('active', s.dataset.dim === (currentIs3D ? '3' : '2'));
                });
            }
        }, { desc: 'Toggle 2D/3D View' });

        console.log('[PANELS] Command bar actions registered');
    }

    function _initOvalMarginSlider() {
        const ovalSlider = document.getElementById('oval-margin-slider');
        const ovalValue = document.getElementById('oval-margin-value');
        let ovalDebounceTimer = null;

        if (ovalSlider) {
            ovalSlider.addEventListener('input', (e) => {
                if (ovalValue) ovalValue.textContent = e.target.value + '%';
            });

            const applyOvalMargin = () => {
                clearTimeout(ovalDebounceTimer);
                ovalDebounceTimer = setTimeout(() => {
                    const val = ovalSlider.value;
                    document.documentElement.style.setProperty('--oval-margin', val + '%');
                }, 300);
            };

            ovalSlider.addEventListener('mouseup', applyOvalMargin);
            ovalSlider.addEventListener('touchend', applyOvalMargin);
            ovalSlider.addEventListener('change', applyOvalMargin);
        }
    }

    function _initOvalDebugToggle() {
        const toggleOvalDebug = document.getElementById('toggle-oval-debug');
        if (toggleOvalDebug) {
            toggleOvalDebug.addEventListener('click', () => {
                toggleOvalDebug.classList.toggle('active');
                const ovalDebug = document.querySelector('.oval-debug');
                if (ovalDebug) {
                    ovalDebug.style.display = toggleOvalDebug.classList.contains('active') ? 'block' : 'none';
                }
            });
        }
    }

    // =========================================================================
    // HUD LAYOUT MANAGER - REMOVED, USE LAYOUT MODULE
    // =========================================================================
    // The HudLayoutManager has been unified into modules/layout.js
    // Use LAYOUT.reflow() instead of PANELS.HudLayoutManager.reflow()

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        open,
        close,
        toggle,
        getActive,
        initCommandBar,

        // State access
        get activePanelId() { return _activePanelId; }
    };
})();

// Backward compatibility - _activePanelId is managed by app.js
function openPanel(panelId) { PANELS.open(panelId); }
function closePanel(panelId) { PANELS.close(panelId); }
function togglePanel(panelId) { PANELS.toggle(panelId); }
function initCommandBar() { PANELS.initCommandBar(); }
// HudLayoutManager - app.js owns this, not duplicated here

// ════════════════════════════════════════════════════════════════════════
// PANEL DRAG & RESIZE - Make panels movable and resizable
// ════════════════════════════════════════════════════════════════════════

const PANEL_DRAG = (function() {
    'use strict';

    const _panels = new Map();
    let _dragState = null;
    let _resizeState = null;
    const STORAGE_KEY = 'collider-panel-positions';

    function init() {
        // Initialize draggable/resizable panels (use actual element IDs)
        initPanel('side-dock', { draggable: true, resizable: true, minWidth: 150, maxWidth: 400 });
        initPanel('header-panel', { draggable: true, resizable: false });
        initPanel('stats-panel', { draggable: true, resizable: false });
        initPanel('metrics-panel', { draggable: true, resizable: true, minWidth: 180, maxWidth: 350 });

        // Restore saved positions
        restorePositions();

        // Global mouse handlers
        document.addEventListener('mousemove', (e) => _onMouseMove(e));
        document.addEventListener('mouseup', (e) => _onMouseUp(e));
    }

    function initPanel(id, options = {}) {
        const panel = document.getElementById(id) || document.querySelector('.' + id);
        if (!panel) return;

        const config = {
            el: panel,
            id: id,
            draggable: options.draggable !== false,
            resizable: options.resizable === true,
            minWidth: options.minWidth || 100,
            maxWidth: options.maxWidth || 600,
            minHeight: options.minHeight || 50,
            maxHeight: options.maxHeight || window.innerHeight - 100
        };

        _panels.set(id, config);

        // Make panel positioned if not already
        const style = window.getComputedStyle(panel);
        if (style.position === 'static') {
            panel.style.position = 'absolute';
        }

        // Add drag handle (the panel header or title)
        if (config.draggable) {
            const header = panel.querySelector('.side-title, .hud-title, .panel-header') || panel;
            header.style.cursor = 'move';
            header.addEventListener('mousedown', (e) => _startDrag(e, id));
        }

        // Add resize handle
        if (config.resizable) {
            const handle = document.createElement('div');
            handle.className = 'panel-resize-handle';
            handle.addEventListener('mousedown', (e) => _startResize(e, id));
            panel.appendChild(handle);
            panel.style.position = 'absolute';
        }
    }

    function _startDrag(e, panelId) {
        // Don't drag if clicking on interactive elements
        if (e.target.closest('input, button, select, .collapsible-content, .preset-btn, .layout-btn, .scheme-btn')) {
            return;
        }

        const config = _panels.get(panelId);
        if (!config) return;

        e.preventDefault();
        const rect = config.el.getBoundingClientRect();

        _dragState = {
            panelId,
            startX: e.clientX,
            startY: e.clientY,
            startLeft: rect.left,
            startTop: rect.top
        };

        config.el.classList.add('panel-dragging');
    }

    function _startResize(e, panelId) {
        const config = _panels.get(panelId);
        if (!config) return;

        e.preventDefault();
        e.stopPropagation();

        const rect = config.el.getBoundingClientRect();

        _resizeState = {
            panelId,
            startX: e.clientX,
            startY: e.clientY,
            startWidth: rect.width,
            startHeight: rect.height
        };

        config.el.classList.add('panel-resizing');
    }

    function _onMouseMove(e) {
        if (_dragState) {
            const config = _panels.get(_dragState.panelId);
            if (!config) return;

            const dx = e.clientX - _dragState.startX;
            const dy = e.clientY - _dragState.startY;

            let newLeft = _dragState.startLeft + dx;
            let newTop = _dragState.startTop + dy;

            // Keep within viewport
            newLeft = Math.max(0, Math.min(window.innerWidth - 50, newLeft));
            newTop = Math.max(0, Math.min(window.innerHeight - 50, newTop));

            config.el.style.left = newLeft + 'px';
            config.el.style.top = newTop + 'px';
            config.el.style.right = 'auto';
            config.el.style.bottom = 'auto';
        }

        if (_resizeState) {
            const config = _panels.get(_resizeState.panelId);
            if (!config) return;

            const dx = e.clientX - _resizeState.startX;
            const dy = e.clientY - _resizeState.startY;

            let newWidth = _resizeState.startWidth + dx;
            let newHeight = _resizeState.startHeight + dy;

            // Apply constraints
            newWidth = Math.max(config.minWidth, Math.min(config.maxWidth, newWidth));
            newHeight = Math.max(config.minHeight, Math.min(config.maxHeight, newHeight));

            config.el.style.width = newWidth + 'px';
            // Only resize height for certain panels
            if (config.el.classList.contains('side-dock') || config.el.classList.contains('side-content')) {
                // Don't change height for sidebar - it's auto
            } else {
                config.el.style.height = newHeight + 'px';
            }
        }
    }

    function _onMouseUp(_e) {
        if (_dragState) {
            const config = _panels.get(_dragState.panelId);
            if (config) {
                config.el.classList.remove('panel-dragging');
                savePositions();
            }
            _dragState = null;
        }

        if (_resizeState) {
            const config = _panels.get(_resizeState.panelId);
            if (config) {
                config.el.classList.remove('panel-resizing');
                savePositions();
            }
            _resizeState = null;
        }
    }

    function savePositions() {
        const positions = {};
        _panels.forEach((config, id) => {
            const rect = config.el.getBoundingClientRect();
            const style = config.el.style;
            positions[id] = {
                left: style.left || rect.left + 'px',
                top: style.top || rect.top + 'px',
                width: style.width || null,
                height: style.height || null
            };
        });
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(positions));
        } catch (e) {
            console.warn('[PANEL_DRAG] Could not save positions:', e);
        }
    }

    function restorePositions() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (!saved) return;

            const positions = JSON.parse(saved);
            Object.entries(positions).forEach(([id, pos]) => {
                const config = _panels.get(id);
                if (!config) return;

                if (pos.left) config.el.style.left = pos.left;
                if (pos.top) config.el.style.top = pos.top;
                if (pos.width) config.el.style.width = pos.width;
                if (pos.height) config.el.style.height = pos.height;

                // Clear right/bottom if we're setting left/top
                if (pos.left) config.el.style.right = 'auto';
                if (pos.top) config.el.style.bottom = 'auto';
            });
        } catch (e) {
            console.warn('[PANEL_DRAG] Could not restore positions:', e);
        }
    }

    function resetPositions() {
        try {
            localStorage.removeItem(STORAGE_KEY);
            location.reload();
        } catch (e) {
            console.warn('[PANEL_DRAG] Could not reset positions:', e);
        }
    }

    return {
        init,
        initPanel,
        savePositions,
        restorePositions,
        resetPositions,
        get panels() { return _panels; }
    };
})();

// Backward compatibility wrapper
const PanelManager = {
    panels: PANEL_DRAG.panels,
    init() { PANEL_DRAG.init(); },
    initPanel(id, opts) { PANEL_DRAG.initPanel(id, opts); },
    savePositions() { PANEL_DRAG.savePositions(); },
    restorePositions() { PANEL_DRAG.restorePositions(); },
    resetPositions() { PANEL_DRAG.resetPositions(); }
};

// Initialize after DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => PANEL_DRAG.init());
} else {
    setTimeout(() => PANEL_DRAG.init(), 100);
}

// Expose globally
window.PANEL_DRAG = PANEL_DRAG;
window.PanelManager = PanelManager;
