/**
 * @module ControlRegistry
 * @description Manages mapping of 3D navigation actions to input devices (Mouse/Keyboard).
 * Persists user preferences to localStorage.
 */

const ControlRegistry = (function () {
    'use strict';

    // Storage Key
    const STORAGE_KEY = 'collider_control_settings_v1';

    // THREE.MOUSE Constants (mapped manually to avoid dependency loop if THREE isn't loaded yet)
    // 0: LEFT, 1: MIDDLE, 2: RIGHT
    const MOUSE_BUTTONS = {
        LEFT: 0,
        MIDDLE: 1,
        RIGHT: 2
    };

    // THREE.MOUSE Actions (what the buttons DO)
    // 0: ROTATE, 1: DOLLY (ZOOM), 2: PAN
    const ACTIONS = {
        ROTATE: 0,
        DOLLY: 1,
        PAN: 2
    };

    // Default Configuration:
    // LEFT: PAN (but selection.js intercepts for marquee)
    // RIGHT: ROTATE around origin
    // MIDDLE: DOLLY (zoom)
    // PAN: via SPACE + LEFT drag (handled in selection.js)
    const DEFAULTS = {
        mouse: {
            LEFT: ACTIONS.PAN,      // 2 - OrbitControls pan, but selection.js intercepts
            MIDDLE: ACTIONS.DOLLY,  // 1
            RIGHT: ACTIONS.ROTATE   // 0
        },
        damping: {
            enabled: true,
            factor: 0.1
        },
        speed: {
            rotate: 1.0,
            zoom: 1.2,
            pan: 1.0
        }
    };

    // Current State
    let currentConfig = loadSettings();

    /**
     * Load settings from localStorage or use defaults
     */
    function loadSettings() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                const parsed = JSON.parse(saved);
                // Merge with defaults to ensure structure
                return {
                    mouse: { ...DEFAULTS.mouse, ...(parsed.mouse || {}) },
                    damping: { ...DEFAULTS.damping, ...(parsed.damping || {}) },
                    speed: { ...DEFAULTS.speed, ...(parsed.speed || {}) }
                };
            }
        } catch (e) {
            console.warn('[ControlRegistry] Failed to load settings:', e);
        }
        return JSON.parse(JSON.stringify(DEFAULTS));
    }

    /**
     * Save current settings to localStorage
     */
    function saveSettings() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(currentConfig));
            // Dispatch event for listeners
            window.dispatchEvent(new CustomEvent('controls-updated', { detail: currentConfig }));
        } catch (e) {
            console.error('[ControlRegistry] Failed to save settings:', e);
        }
    }

    // Public API
    return {
        /**
         * Get the current control mapping for THREE.OrbitControls
         * Returns object compatible with controls.mouseButtons
         */
        getMapping: function () {
            return {
                LEFT: currentConfig.mouse.LEFT,
                MIDDLE: currentConfig.mouse.MIDDLE,
                RIGHT: currentConfig.mouse.RIGHT
            };
        },

        /**
         * Get full configuration object
         */
        getConfig: function () {
            return JSON.parse(JSON.stringify(currentConfig)); // Deep copy
        },

        /**
         * Update a specific button mapping
         * @param {string} button 'LEFT', 'MIDDLE', or 'RIGHT'
         * @param {number} actionId 0 (ROTATE), 1 (DOLLY), or 2 (PAN)
         */
        updateMapping: function (button, actionId) {
            if (currentConfig.mouse[button] !== undefined) {
                currentConfig.mouse[button] = parseInt(actionId);
                saveSettings();
                console.log(`[ControlRegistry] Updated ${button} to Action ${actionId}`);
            }
        },

        /**
         * Reset to factory defaults
         */
        resetDefaults: function () {
            currentConfig = JSON.parse(JSON.stringify(DEFAULTS));
            saveSettings();
            console.log('[ControlRegistry] Reset to defaults');
        },

        /**
         * Constants for UI builders
         */
        CONSTANTS: {
            MOUSE_BUTTONS,
            ACTIONS,
            ACTION_LABELS: {
                0: 'Rotate',
                1: 'Zoom (Dolly)',
                2: 'Pan'
            }
        }
    };
})();

// Export
if (typeof window !== 'undefined') window.ControlRegistry = ControlRegistry;
if (typeof module !== 'undefined') module.exports = ControlRegistry;
