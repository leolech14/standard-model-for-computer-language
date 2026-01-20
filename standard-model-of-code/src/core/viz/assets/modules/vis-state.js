/**
 * ═══════════════════════════════════════════════════════════════════════════
 * VIS-STATE MODULE - Unified visualization state management
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Single source of truth for visualization state. All controls funnel through
 * applyState() to ensure consistency.
 *
 * KEY DESIGN DECISIONS:
 * 1. Palette selection NEVER auto-switches colorBy mode
 * 2. Palette is "armed" - it applies when colorBy changes to interval mode
 * 3. Presets are macros that call applyState() with multiple properties
 * 4. syncUIFromState() updates all UI elements to match state
 *
 * @module VIS_STATE
 * @version 1.0.0
 */

window.VIS_STATE = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // CATEGORICAL vs INTERVAL MODE CLASSIFICATION
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Categorical modes use discrete color palettes (tier, family, atom...)
     * Interval modes use continuous gradients (complexity, fan_in, loc...)
     */
    const CATEGORICAL_MODES = new Set([
        'tier', 'family', 'atom', 'ring', 'layer', 'role', 'roleCategory',
        'subsystem', 'phase', 'fileType', 'file', 'state', 'visibility'
    ]);

    const INTERVAL_MODES = new Set([
        'complexity', 'loc', 'fan_in', 'fan_out', 'trust',
        'responsibility', 'purity', 'lifecycle_score', 'boundary_score',
        'centrality', 'rank', 'churn', 'age', 'depth'
    ]);

    function isIntervalMode(mode) {
        return INTERVAL_MODES.has(mode);
    }

    function isCategoricalMode(mode) {
        return CATEGORICAL_MODES.has(mode);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // STATE OBJECT - Single source of truth
    // ═══════════════════════════════════════════════════════════════════════

    const state = {
        colorBy: 'fan_in',         // Default to interval mode to show OKLCH schemes
        sizeBy: 'fanout',          // 'uniform', 'degree', 'fanout', 'complexity'
        edgeBy: 'type',            // 'type', 'resolution', 'weight', 'gradient-tier', etc.
        palette: 'helix',          // OKLCH helix path - visually striking default
        paletteType: 'interval'    // Derived: 'categorical' or 'interval'
    };

    // ═══════════════════════════════════════════════════════════════════════
    // VIEW PRESETS - Macros that set multiple properties at once
    // ═══════════════════════════════════════════════════════════════════════

    const VIEW_PRESETS = {
        tier: {
            label: 'Tier',
            description: 'T0/T1/T2 architectural height',
            colorBy: 'tier',
            sizeBy: 'fanout',
            edgeBy: 'type'
        },
        family: {
            label: 'Family',
            description: 'LOG, DAT, ORG, EXE, EXT',
            colorBy: 'family',
            sizeBy: 'fanout',
            edgeBy: 'type'
        },
        layer: {
            label: 'Layer',
            description: 'Physical/Virtual/Semantic',
            colorBy: 'layer',
            sizeBy: 'uniform',
            edgeBy: 'resolution'
        },
        ring: {
            label: 'Ring',
            description: 'Domain architecture rings',
            colorBy: 'ring',
            sizeBy: 'fanout',
            edgeBy: 'type'
        },
        file: {
            label: 'File',
            description: 'Each file gets unique hue',
            colorBy: 'file',
            sizeBy: 'uniform',
            edgeBy: 'resolution'
        },
        flow: {
            label: 'Flow',
            description: 'Markov transition probability',
            colorBy: 'fan_in',  // Use interval mode for flow
            sizeBy: 'degree',
            edgeBy: 'weight',
            special: 'flow'    // Triggers flow visualization
        }
    };

    // ═══════════════════════════════════════════════════════════════════════
    // APPLY STATE - Central function all controls use
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Apply state changes. This is THE function all UI controls call.
     *
     * @param {Object} nextState - Partial state to merge
     * @param {string} reason - Debug label for console (e.g., 'preset:tier', 'control:colorBy')
     */
    function applyState(nextState, reason = 'unknown') {
        const prevColorBy = state.colorBy;
        const prevPalette = state.palette;

        // Merge new state
        if (nextState.colorBy !== undefined) state.colorBy = nextState.colorBy;
        if (nextState.sizeBy !== undefined) state.sizeBy = nextState.sizeBy;
        if (nextState.edgeBy !== undefined) state.edgeBy = nextState.edgeBy;
        if (nextState.palette !== undefined) state.palette = nextState.palette;

        // Derive paletteType from colorBy
        state.paletteType = isIntervalMode(state.colorBy) ? 'interval' : 'categorical';

        console.log(`[VIS_STATE] applyState(${reason}):`, {
            colorBy: state.colorBy,
            sizeBy: state.sizeBy,
            edgeBy: state.edgeBy,
            palette: state.palette,
            paletteType: state.paletteType
        });

        // ─── Apply color mode ───
        if (nextState.colorBy !== undefined && nextState.colorBy !== prevColorBy) {
            _applyColorMode(state.colorBy);
        }

        // ─── Apply size mode ───
        if (nextState.sizeBy !== undefined) {
            _applySizeMode(state.sizeBy);
        }

        // ─── Apply edge mode ───
        if (nextState.edgeBy !== undefined) {
            _applyEdgeMode(state.edgeBy);
        }

        // ─── Apply palette (only if in interval mode) ───
        if (nextState.palette !== undefined || nextState.colorBy !== undefined) {
            _applyPalette();
        }

        // ─── Handle special modes (flow) ───
        if (nextState.special === 'flow') {
            _enableFlowMode();
        } else if (prevColorBy === 'flow' && nextState.colorBy !== 'flow') {
            _disableFlowMode();
        }

        // ─── Sync UI to match state ───
        syncUIFromState();

        // ─── Refresh visualization ───
        _refreshGraph();
    }

    // ═══════════════════════════════════════════════════════════════════════
    // INTERNAL APPLY FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    function _applyColorMode(mode) {
        // Update globals for backward compatibility
        window.NODE_COLOR_MODE = mode;

        if (typeof window.APPEARANCE_STATE !== 'undefined') {
            window.APPEARANCE_STATE.colorMode = mode;
            window.APPEARANCE_STATE.currentPreset = mode;
        }

        // Disable flow mode if switching away from flow
        if (mode !== 'flow' && typeof window.flowMode !== 'undefined' && window.flowMode) {
            if (typeof window.disableFlowMode === 'function') {
                window.disableFlowMode();
            }
        }
    }

    function _applySizeMode(mode) {
        if (typeof window.APPEARANCE_STATE !== 'undefined') {
            window.APPEARANCE_STATE.sizeMode = mode;
        }

        if (typeof window.applyNodeSizeMode === 'function') {
            window.applyNodeSizeMode(mode);
        } else if (typeof window.NODE_HELPERS !== 'undefined') {
            window.NODE_HELPERS.applySizeMode(mode);
        }
    }

    function _applyEdgeMode(mode) {
        if (typeof window.EDGE_GRADIENT_MODE !== 'undefined') {
            // Edge gradient modes
            if (mode.startsWith('gradient-')) {
                window.EDGE_GRADIENT_MODE = mode.replace('gradient-', '');
            }
        }

        if (typeof window.applyEdgeMode === 'function') {
            window.applyEdgeMode();
        }
    }

    function _applyPalette() {
        // Only apply scheme coloring if in interval mode
        if (state.paletteType === 'interval' && state.palette) {
            if (typeof window.COLOR !== 'undefined' && window.COLOR.applyScheme) {
                window.COLOR.applyScheme(state.palette);
            }
        } else {
            // In categorical mode, clear active scheme
            if (typeof window.COLOR !== 'undefined' && window.COLOR.applyScheme) {
                window.COLOR.applyScheme(null);
            }
        }
    }

    function _enableFlowMode() {
        if (typeof window.flowMode !== 'undefined' && !window.flowMode) {
            if (typeof window.toggleFlowMode === 'function') {
                window.toggleFlowMode();
            }
        }
    }

    function _disableFlowMode() {
        if (typeof window.flowMode !== 'undefined' && window.flowMode) {
            if (typeof window.disableFlowMode === 'function') {
                window.disableFlowMode();
            }
        }
    }

    function _refreshGraph() {
        // Recompute node colors
        const DM = window.DM;
        const Graph = window.Graph;
        const nodes = DM ? DM.getNodes() : (Graph?.graphData ? Graph.graphData().nodes : []);

        if (typeof window.applyNodeColors === 'function' && nodes.length > 0) {
            window.applyNodeColors(nodes);
        }

        // Trigger WebGL re-render with new function reference to force update
        if (Graph) {
            Graph.nodeColor(n => n.color);
        }

        // Refresh edge gradients
        if (typeof window.refreshGradientEdgeColors === 'function') {
            window.refreshGradientEdgeColors();
        }

        // Re-render legends
        if (typeof window.renderAllLegends === 'function') {
            window.renderAllLegends();
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // SYNC UI FROM STATE
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Update all UI elements to reflect current state.
     * Called after every applyState() and on initialization.
     */
    function syncUIFromState() {
        // ─── View Preset buttons ───
        document.querySelectorAll('.preset-btn[data-preset]').forEach(btn => {
            const presetKey = btn.dataset.preset;
            const preset = VIEW_PRESETS[presetKey];
            const isActive = preset && preset.colorBy === state.colorBy;
            btn.classList.toggle('active', isActive);
        });

        // ─── Color Mode buttons (PRESET_CONFIG grid) ───
        document.querySelectorAll('.color-btn[data-preset]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.preset === state.colorBy);
        });

        // ─── Size Mode buttons ───
        document.querySelectorAll('[data-size-mode]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.sizeMode === state.sizeBy);
        });

        // ─── Edge Mode buttons ───
        document.querySelectorAll('[data-edge-mode]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.edgeMode === state.edgeBy);
        });

        // ─── Palette buttons ───
        document.querySelectorAll('.scheme-btn[data-scheme]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.scheme === state.palette);
        });

        // ─── Palette panel enabled/disabled state ───
        const schemesPanel = document.getElementById('section-schemes');
        if (schemesPanel) {
            const isDisabled = state.paletteType === 'categorical';
            schemesPanel.classList.toggle('disabled', isDisabled);

            // Update scheme buttons opacity/interactivity
            schemesPanel.querySelectorAll('.scheme-btn').forEach(btn => {
                btn.disabled = isDisabled;
                btn.style.opacity = isDisabled ? '0.4' : '1';
                btn.style.pointerEvents = isDisabled ? 'none' : 'auto';
            });

            // Show hint when disabled
            let hint = schemesPanel.querySelector('.scheme-hint');
            if (isDisabled) {
                if (!hint) {
                    hint = document.createElement('div');
                    hint.className = 'scheme-hint';
                    hint.style.cssText = 'padding: 8px; font-size: 10px; opacity: 0.6; text-align: center; font-style: italic;';
                    hint.textContent = 'Switch to a metric mode (Fan-In, Complexity, etc.) to enable color schemes';
                    schemesPanel.insertBefore(hint, schemesPanel.firstChild);
                }
            } else if (hint) {
                hint.remove();
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CONVENIENCE METHODS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Apply a view preset by name
     */
    function applyPreset(presetKey) {
        const preset = VIEW_PRESETS[presetKey];
        if (!preset) {
            console.warn('[VIS_STATE] Unknown preset:', presetKey);
            return;
        }

        applyState({
            colorBy: preset.colorBy,
            sizeBy: preset.sizeBy,
            edgeBy: preset.edgeBy,
            special: preset.special
        }, `preset:${presetKey}`);
    }

    /**
     * Set color mode only
     */
    function setColorBy(mode) {
        applyState({ colorBy: mode }, `colorBy:${mode}`);
    }

    /**
     * Set size mode only
     */
    function setSizeBy(mode) {
        applyState({ sizeBy: mode }, `sizeBy:${mode}`);
    }

    /**
     * Set edge mode only
     */
    function setEdgeBy(mode) {
        applyState({ edgeBy: mode }, `edgeBy:${mode}`);
    }

    /**
     * Set palette (arms the palette, applies if in interval mode)
     */
    function setPalette(schemeName) {
        applyState({ palette: schemeName }, `palette:${schemeName}`);
    }

    /**
     * Get current state (read-only copy)
     */
    function getState() {
        return { ...state };
    }

    /**
     * Initialize from saved preferences or defaults
     */
    function init() {
        try {
            const savedScheme = localStorage.getItem('collider_scheme');
            const savedColorMode = localStorage.getItem('collider_color_mode');

            if (savedScheme) state.palette = savedScheme;
            if (savedColorMode) state.colorBy = savedColorMode;

            state.paletteType = isIntervalMode(state.colorBy) ? 'interval' : 'categorical';
        } catch (e) { /* ignore localStorage errors */ }

        // Apply initial state to globals (critical for NODE_COLOR_MODE)
        _applyColorMode(state.colorBy);
        _applyPalette();

        console.log('[VIS_STATE] Initialized:', state);
    }

    /**
     * Save current preferences
     */
    function savePreferences() {
        try {
            localStorage.setItem('collider_scheme', state.palette);
            localStorage.setItem('collider_color_mode', state.colorBy);
        } catch (e) { /* ignore */ }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        // State access
        getState,
        isIntervalMode,
        isCategoricalMode,

        // Main API
        applyState,
        applyPreset,
        syncUIFromState,

        // Convenience setters
        setColorBy,
        setSizeBy,
        setEdgeBy,
        setPalette,

        // Lifecycle
        init,
        savePreferences,

        // Constants
        VIEW_PRESETS,
        CATEGORICAL_MODES,
        INTERVAL_MODES
    };
})();

console.log('[Module] VIS_STATE loaded - unified visualization state');
