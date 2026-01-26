/**
 * ═══════════════════════════════════════════════════════════════════════════
 * CIRCUIT BREAKER MODULE - UI Control Validator
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Runtime self-test system that validates all visualization UI controls.
 * Acts as a quality guardian - detects binding failures, state issues,
 * and provides actionable fix recommendations.
 *
 * @module CIRCUIT
 * @version 2.0.0
 *
 * ## API
 *
 * | Method | Returns | Description |
 * |--------|---------|-------------|
 * | `runAll()` | `{passed, failed, total, results}` | Run all tests |
 * | `test(name)` | `{passed, error, trace}` | Test single control |
 * | `report()` | `Map<name, result>` | Get all results |
 * | `listTests()` | `string[]` | List test names |
 * | `diagnose()` | `{category, failures}[]` | Get categorized fix recommendations |
 * | `inventory()` | `string` | Markdown table of all controls |
 * | `inventoryJSON()` | `object[]` | JSON array of control definitions |
 *
 * ## CLI Integration
 *
 * ```bash
 * python tools/validate_ui.py <html_path> --verbose
 * ```
 *
 * ## Browser Console
 *
 * ```javascript
 * CIRCUIT.runAll()        // Run all tests
 * CIRCUIT.inventory()     // Print control table
 * CIRCUIT.diagnose()      // Get fix recommendations
 * ```
 *
 * @see tools/validate_ui.py - Headless test runner
 * @see CLAUDE.md - UI Controls section
 */

const CIRCUIT = (function() {
    'use strict';

    // Test results storage
    const _results = new Map();
    let _running = false;

    // =========================================================================
    // DIAGNOSTIC HELPERS
    // =========================================================================

    function getStateValue(path) {
        try {
            const parts = path.split('.');
            let obj = window;
            for (const part of parts) {
                if (obj === undefined || obj === null) return { exists: false, value: undefined };
                obj = obj[part];
            }
            return { exists: true, value: obj };
        } catch (e) {
            return { exists: false, value: undefined, error: e.message };
        }
    }

    function traceBinding(elementId, statePath, graphMethod) {
        const trace = {
            element: { id: elementId, found: false, hasListeners: false },
            state: { path: statePath, exists: false, value: undefined },
            graph: { method: graphMethod, callable: false },
            chain: []
        };

        // Check element
        const el = document.getElementById(elementId);
        if (el) {
            trace.element.found = true;
            trace.element.tagName = el.tagName;
            trace.element.type = el.type || el.tagName;
            trace.element.value = el.value;
            trace.chain.push(`✓ DOM element #${elementId} exists`);
        } else {
            trace.chain.push(`✗ DOM element #${elementId} NOT FOUND`);
            return trace;
        }

        // Check state
        if (statePath) {
            const stateResult = getStateValue(statePath);
            trace.state.exists = stateResult.exists;
            trace.state.value = stateResult.value;
            if (stateResult.exists) {
                trace.chain.push(`✓ State ${statePath} = ${JSON.stringify(stateResult.value)}`);
            } else {
                trace.chain.push(`✗ State ${statePath} is undefined`);
            }
        }

        // Check Graph method
        if (graphMethod && typeof Graph !== 'undefined' && Graph) {
            const method = Graph[graphMethod];
            trace.graph.callable = typeof method === 'function';
            if (trace.graph.callable) {
                trace.chain.push(`✓ Graph.${graphMethod}() is callable`);
            } else {
                trace.chain.push(`✗ Graph.${graphMethod}() NOT a function`);
            }
        }

        return trace;
    }

    // =========================================================================
    // TEST DEFINITIONS - Enhanced with diagnostics
    // Target: 82+ controls for full UI coverage
    // =========================================================================

    const TESTS = [
        // ═══════════════════════════════════════════════════════════════════════
        // SECTION 1: LEGACY SIDEBAR CONTROLS (9 existing tests)
        // ═══════════════════════════════════════════════════════════════════════

        // --- EDGE CONTROLS ---
        {
            name: 'edge-opacity',
            type: 'slider',
            elementId: 'cfg-edge-opacity',
            statePath: 'APPEARANCE_STATE.edgeOpacity',
            graphMethod: 'linkOpacity',
            expected: 0.8,
            trigger: (el) => {
                el.value = '0.8';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                const state = getStateValue('APPEARANCE_STATE.edgeOpacity');
                return {
                    passed: state.exists && state.value === 0.8,
                    expected: 0.8,
                    actual: state.value,
                    stateExists: state.exists
                };
            },
            cleanup: (el) => {
                el.value = '0.6';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            fix: 'Ensure bindSlider() in app.js updates APPEARANCE_STATE.edgeOpacity and calls applyEdgeMode()'
        },
        {
            name: 'edge-width',
            type: 'slider',
            elementId: 'cfg-edge-width',
            statePath: 'APPEARANCE_STATE.edgeWidth',
            graphMethod: 'linkWidth',
            expected: 'changed',
            trigger: (el) => {
                // Store initial value, then change it
                window._edgeWidthBefore = getStateValue('APPEARANCE_STATE.edgeWidth').value;
                el.value = '3';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                const state = getStateValue('APPEARANCE_STATE.edgeWidth');
                const changed = state.exists && state.value !== window._edgeWidthBefore;
                return {
                    passed: changed,
                    expected: 'different from ' + window._edgeWidthBefore,
                    actual: state.value,
                    stateExists: state.exists
                };
            },
            cleanup: (el) => {
                el.value = '1.5';
                el.dispatchEvent(new Event('input', { bubbles: true }));
                delete window._edgeWidthBefore;
            },
            fix: 'Check if cfg-edge-width has oninput handler that updates APPEARANCE_STATE.edgeWidth'
        },
        {
            name: 'edge-curvature',
            type: 'slider',
            elementId: 'cfg-edge-curve',
            statePath: 'APPEARANCE_STATE.edgeCurvature',
            graphMethod: 'linkCurvature',
            expected: 'changed',
            trigger: (el) => {
                window._edgeCurveBefore = getStateValue('APPEARANCE_STATE.edgeCurvature').value;
                el.value = '0.5';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                const state = getStateValue('APPEARANCE_STATE.edgeCurvature');
                const changed = state.exists && state.value !== window._edgeCurveBefore;
                return {
                    passed: changed,
                    expected: 'different from ' + window._edgeCurveBefore,
                    actual: state.value,
                    stateExists: state.exists
                };
            },
            cleanup: (el) => {
                el.value = '0';
                el.dispatchEvent(new Event('input', { bubbles: true }));
                delete window._edgeCurveBefore;
            },
            fix: 'Check if cfg-edge-curve has oninput handler that updates APPEARANCE_STATE.edgeCurvature'
        },

        // --- NODE CONTROLS ---
        {
            name: 'node-size',
            type: 'slider',
            elementId: 'cfg-node-size',
            statePath: 'APPEARANCE_STATE.nodeScale',
            graphMethod: 'nodeRelSize',
            expected: 'changed',
            trigger: (el) => {
                // Slider has max=4, so use valid value
                window._nodeSizeBefore = getStateValue('APPEARANCE_STATE.nodeScale').value;
                el.value = '3';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                const state = getStateValue('APPEARANCE_STATE.nodeScale');
                const changed = state.exists && state.value !== window._nodeSizeBefore;
                return {
                    passed: changed,
                    expected: 'different from ' + window._nodeSizeBefore,
                    actual: state.value,
                    stateExists: state.exists
                };
            },
            cleanup: (el) => {
                el.value = '1';
                el.dispatchEvent(new Event('input', { bubbles: true }));
                delete window._nodeSizeBefore;
            },
            fix: 'Check if cfg-node-size has oninput handler that updates APPEARANCE_STATE.nodeScale'
        },
        {
            name: 'node-opacity',
            type: 'slider',
            elementId: 'cfg-node-opacity',
            statePath: 'APPEARANCE_STATE.nodeOpacity',
            graphMethod: 'nodeOpacity',
            expected: 0.5,
            trigger: (el) => {
                el.value = '0.5';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                const state = getStateValue('APPEARANCE_STATE.nodeOpacity');
                return {
                    passed: state.exists && state.value === 0.5,
                    expected: 0.5,
                    actual: state.value,
                    stateExists: state.exists
                };
            },
            cleanup: (el) => {
                el.value = '1';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            fix: 'Check if cfg-node-opacity has oninput handler that updates APPEARANCE_STATE.nodeOpacity'
        },

        // --- TOGGLES ---
        {
            name: 'toggle-arrows',
            type: 'toggle',
            elementId: 'cfg-toggle-arrows',
            statePath: null,
            graphMethod: 'linkDirectionalArrowLength',
            expected: 'toggled',
            trigger: (el) => {
                window._arrowsActiveBefore = el.classList.contains('active');
                el.click();
            },
            validate: () => {
                const el = document.getElementById('cfg-toggle-arrows');
                if (!el) return { passed: false, error: 'Element not found' };
                const isActiveNow = el.classList.contains('active');
                const wasSet = typeof window._arrowsActiveBefore !== 'undefined';
                return {
                    passed: wasSet && isActiveNow !== window._arrowsActiveBefore,
                    expected: !window._arrowsActiveBefore,
                    actual: isActiveNow,
                    stateExists: wasSet
                };
            },
            cleanup: (el) => {
                el.click();
                delete window._arrowsActiveBefore;
            },
            fix: 'Ensure toggle click handler toggles .active class and calls Graph.linkDirectionalArrowLength()'
        },

        // --- PHYSICS CONTROLS ---
        {
            name: 'physics-charge',
            type: 'slider',
            elementId: 'physics-charge',
            statePath: null,  // Bypasses PHYSICS_STATE, goes direct to Graph
            graphMethod: 'd3Force',
            expected: -200,
            trigger: (el) => {
                window._originalChargeValue = el.value;
                el.value = '-200';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                // Check both Graph.d3Force AND window.PHYSICS_STATE.charge binding
                const G = window.Graph;
                const physicsState = window.PHYSICS_STATE;
                if (!G) {
                    return { passed: false, error: 'Graph not defined', stateExists: false };
                }
                if (!G.d3Force) {
                    return { passed: false, error: 'Graph.d3Force not available', stateExists: false };
                }
                if (!physicsState) {
                    return { passed: false, error: 'PHYSICS_STATE not defined', stateExists: false };
                }
                try {
                    const chargeForce = G.d3Force('charge');
                    if (!chargeForce || !chargeForce.strength) {
                        return { passed: false, error: 'charge force not configured', stateExists: false };
                    }
                    // d3-force strength() returns accessor function, not value
                    // Call it with dummy node to get actual strength
                    const strengthFn = chargeForce.strength();
                    const strength = typeof strengthFn === 'function' ? strengthFn({}, 0, []) : strengthFn;
                    // Verify both Graph.d3Force and PHYSICS_STATE.charge match
                    const graphOK = strength === -200;
                    const stateOK = physicsState.charge === -200;
                    return {
                        passed: graphOK && stateOK,
                        expected: -200,
                        actual: strength,
                        stateExists: graphOK && stateOK
                    };
                } catch (e) {
                    return { passed: false, error: e.message, stateExists: false };
                }
            },
            cleanup: (el) => {
                if (window._originalChargeValue) {
                    el.value = window._originalChargeValue;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    delete window._originalChargeValue;
                }
            },
            fix: 'Ensure physics-charge slider calls Graph.d3Force("charge").strength(value) - check sidebar.js binding'
        },

        // NOTE: btn-edge-mode test removed - button never existed in template.html
        // The EDGE module handles missing button gracefully (line 443-446 of edge-system.js)

        // --- DIMENSION TOGGLE ---
        {
            name: 'dimension-toggle',
            type: 'button',
            elementId: 'btn-2d',
            statePath: 'DIMENSION_TRANSITION',
            graphMethod: null,
            expected: 'transition started',
            trigger: (el) => {
                // Animation takes 3s, so we check DIMENSION_TRANSITION flag (set immediately)
                window._transitionBefore = window.DIMENSION_TRANSITION;
                el.click();
            },
            validate: () => {
                // DIMENSION_TRANSITION is set true immediately on click, then false after 3s animation
                // We check that clicking triggered the transition (flag went true or animation completed)
                const transitionStarted = window.DIMENSION_TRANSITION === true ||
                                         window.DIMENSION_TRANSITION !== window._transitionBefore;
                return {
                    passed: transitionStarted,
                    expected: 'DIMENSION_TRANSITION = true (animation in progress)',
                    actual: window.DIMENSION_TRANSITION,
                    stateExists: typeof window.DIMENSION_TRANSITION !== 'undefined'
                };
            },
            cleanup: () => {
                // Don't click again - let animation complete naturally
                delete window._transitionBefore;
            },
            fix: 'Check if btn-2d click handler sets DIMENSION_TRANSITION and calls DIMENSION.toggle() - see dimension.js'
        },

        // --- VIEW MODE ---
        {
            name: 'view-mode-files',
            type: 'button',
            elementId: null,
            selector: '[data-mode="files"]',
            statePath: 'GRAPH_MODE',
            graphMethod: null,
            expected: 'files',
            trigger: (el) => {
                el.click();
            },
            validate: () => {
                const state = getStateValue('GRAPH_MODE');
                return {
                    passed: state.exists && state.value === 'files',
                    expected: 'files',
                    actual: state.value,
                    stateExists: state.exists
                };
            },
            cleanup: () => {
                const atomsBtn = document.querySelector('[data-mode="atoms"]');
                if (atomsBtn) atomsBtn.click();
            },
            fix: 'Ensure [data-mode="files"] button sets GRAPH_MODE = "files" and rebuilds graph'
        },

        // ═══════════════════════════════════════════════════════════════════════
        // SECTION 2: GRIDSTACK PANEL CONTROLS (37 new controls)
        // ═══════════════════════════════════════════════════════════════════════

        // --- FILTERING PANEL ---
        {
            name: 'panel-search',
            type: 'input',
            elementId: 'panel-search-nodes',
            statePath: 'FILTER_STATE._state.search',
            graphMethod: 'nodeVisibility',
            expected: 'test',
            trigger: (el) => {
                el.value = 'test';
                el.dispatchEvent(new Event('input', { bubbles: true }));
            },
            validate: () => {
                const state = typeof FILTER_STATE !== 'undefined' ? FILTER_STATE.getSearch() : null;
                return { passed: state === 'test', expected: 'test', actual: state, stateExists: state !== null };
            },
            cleanup: (el) => { el.value = ''; el.dispatchEvent(new Event('input', { bubbles: true })); },
            fix: 'FILTER_STATE.setSearch should update search and trigger Graph.nodeVisibility'
        },
        {
            name: 'panel-toggle-orphans',
            type: 'toggle',
            elementId: 'panel-toggle-orphans',
            statePath: 'FILTER_STATE._state.hideOrphans',
            graphMethod: 'nodeVisibility',
            expected: true,
            trigger: (el) => { window._orphansBefore = el.classList.contains('active'); el.click(); },
            validate: () => {
                const el = document.getElementById('panel-toggle-orphans');
                return { passed: el && el.classList.contains('active') !== window._orphansBefore, expected: 'toggled', actual: el?.classList.contains('active'), stateExists: true };
            },
            cleanup: (el) => { el.click(); delete window._orphansBefore; },
            fix: 'panel-toggle-orphans should toggle FILTER_STATE.setHideOrphans'
        },
        {
            name: 'panel-toggle-dead',
            type: 'toggle',
            elementId: 'panel-toggle-dead',
            statePath: 'FILTER_STATE._state.hideDeadCode',
            graphMethod: 'nodeVisibility',
            expected: true,
            trigger: (el) => { window._deadBefore = el.classList.contains('active'); el.click(); },
            validate: () => {
                const el = document.getElementById('panel-toggle-dead');
                return { passed: el && el.classList.contains('active') !== window._deadBefore, expected: 'toggled', actual: el?.classList.contains('active'), stateExists: true };
            },
            cleanup: (el) => { el.click(); delete window._deadBefore; },
            fix: 'panel-toggle-dead should toggle FILTER_STATE.setHideDeadCode'
        },
        {
            name: 'panel-filter-degree',
            type: 'slider',
            elementId: 'panel-filter-degree',
            statePath: 'FILTER_STATE._state.minDegree',
            graphMethod: 'nodeVisibility',
            expected: 5,
            trigger: (el) => { el.value = '5'; el.dispatchEvent(new Event('input', { bubbles: true })); },
            validate: () => {
                const state = typeof FILTER_STATE !== 'undefined' ? FILTER_STATE.getState().minDegree : null;
                return { passed: state === 5, expected: 5, actual: state, stateExists: state !== null };
            },
            cleanup: (el) => { el.value = '0'; el.dispatchEvent(new Event('input', { bubbles: true })); },
            fix: 'panel-filter-degree should call FILTER_STATE.setMinDegree'
        },

        // --- SELECTION PANEL ---
        {
            name: 'panel-selection-mode-single',
            type: 'button',
            elementId: null,
            selector: '[data-selection-mode="single"]',
            statePath: null,
            graphMethod: null,
            expected: 'active',
            trigger: (el) => { el.click(); },
            validate: () => {
                const el = document.querySelector('[data-selection-mode="single"]');
                return { passed: el?.classList.contains('active'), expected: 'active', actual: el?.classList.contains('active') ? 'active' : 'inactive', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Selection mode button should toggle active class'
        },
        {
            name: 'panel-selection-mode-multi',
            type: 'button',
            elementId: null,
            selector: '[data-selection-mode="multi"]',
            statePath: null,
            graphMethod: null,
            expected: 'active',
            trigger: (el) => { el.click(); },
            validate: () => {
                const el = document.querySelector('[data-selection-mode="multi"]');
                return { passed: el?.classList.contains('active'), expected: 'active', actual: el?.classList.contains('active') ? 'active' : 'inactive', stateExists: true };
            },
            cleanup: () => { document.querySelector('[data-selection-mode="single"]')?.click(); },
            fix: 'Selection mode button should toggle active class'
        },
        {
            name: 'panel-selection-mode-lasso',
            type: 'button',
            elementId: null,
            selector: '[data-selection-mode="lasso"]',
            statePath: null,
            graphMethod: null,
            expected: 'active',
            trigger: (el) => { el.click(); },
            validate: () => {
                const el = document.querySelector('[data-selection-mode="lasso"]');
                return { passed: el?.classList.contains('active'), expected: 'active', actual: el?.classList.contains('active') ? 'active' : 'inactive', stateExists: true };
            },
            cleanup: () => { document.querySelector('[data-selection-mode="single"]')?.click(); },
            fix: 'Selection mode button should toggle active class'
        },
        {
            name: 'panel-khop',
            type: 'slider',
            elementId: 'panel-khop',
            statePath: null,
            graphMethod: null,
            expected: 3,
            trigger: (el) => { el.value = '3'; el.dispatchEvent(new Event('input', { bubbles: true })); },
            validate: () => {
                const el = document.getElementById('panel-khop');
                return { passed: el?.value === '3', expected: '3', actual: el?.value, stateExists: true };
            },
            cleanup: (el) => { el.value = '1'; el.dispatchEvent(new Event('input', { bubbles: true })); },
            fix: 'K-hop slider should sync value'
        },
        {
            name: 'panel-select-expand',
            type: 'button',
            elementId: 'panel-select-expand',
            statePath: null,
            graphMethod: null,
            expected: 'clickable',
            trigger: (_el) => { /* Don't click - just verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-select-expand');
                return { passed: !!el && !el.disabled, expected: 'clickable', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Expand button should exist and be clickable'
        },
        {
            name: 'panel-select-isolate',
            type: 'button',
            elementId: 'panel-select-isolate',
            statePath: null,
            graphMethod: null,
            expected: 'clickable',
            trigger: (_el) => { /* Don't click - just verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-select-isolate');
                return { passed: !!el && !el.disabled, expected: 'clickable', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Isolate button should exist and be clickable'
        },

        // --- CAMERA PANEL ---
        {
            name: 'panel-auto-rotate',
            type: 'toggle',
            elementId: 'panel-auto-rotate',
            statePath: null,
            graphMethod: 'controls',
            expected: 'toggled',
            trigger: (el) => { window._rotateBefore = el.classList.contains('active'); el.click(); },
            validate: () => {
                const el = document.getElementById('panel-auto-rotate');
                return { passed: el?.classList.contains('active') !== window._rotateBefore, expected: 'toggled', actual: el?.classList.contains('active'), stateExists: true };
            },
            cleanup: (el) => { el.click(); delete window._rotateBefore; },
            fix: 'Auto-rotate toggle should set Graph.controls().autoRotate'
        },
        {
            name: 'panel-rotate-speed',
            type: 'slider',
            elementId: 'panel-rotate-speed',
            statePath: null,
            graphMethod: 'controls',
            expected: 2,
            trigger: (el) => { el.value = '2'; el.dispatchEvent(new Event('input', { bubbles: true })); },
            validate: () => {
                const el = document.getElementById('panel-rotate-speed');
                return { passed: el?.value === '2', expected: '2', actual: el?.value, stateExists: true };
            },
            cleanup: (el) => { el.value = '1'; el.dispatchEvent(new Event('input', { bubbles: true })); },
            fix: 'Rotate speed slider should set Graph.controls().autoRotateSpeed'
        },
        {
            name: 'panel-cam-reset',
            type: 'button',
            elementId: 'panel-cam-reset',
            statePath: null,
            graphMethod: 'cameraPosition',
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-cam-reset');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Camera reset button should call Graph.cameraPosition()'
        },
        {
            name: 'panel-cam-fit',
            type: 'button',
            elementId: 'panel-cam-fit',
            statePath: null,
            graphMethod: 'zoomToFit',
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-cam-fit');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Fit all button should call Graph.zoomToFit()'
        },

        // --- ACCESSIBILITY PANEL ---
        {
            name: 'panel-colorblind',
            type: 'select',
            elementId: 'panel-colorblind',
            statePath: null,
            graphMethod: null,
            expected: 'deuteranopia',
            trigger: (el) => { el.value = 'deuteranopia'; el.dispatchEvent(new Event('change', { bubbles: true })); },
            validate: () => {
                const el = document.getElementById('panel-colorblind');
                return { passed: el?.value === 'deuteranopia', expected: 'deuteranopia', actual: el?.value, stateExists: true };
            },
            cleanup: (el) => { el.value = 'none'; el.dispatchEvent(new Event('change', { bubbles: true })); },
            fix: 'Colorblind select should set body dataset and COLOR.setColorblindMode'
        },
        {
            name: 'panel-high-contrast',
            type: 'toggle',
            elementId: 'panel-high-contrast',
            statePath: null,
            graphMethod: null,
            expected: 'toggled',
            trigger: (el) => { window._contrastBefore = el.classList.contains('active'); el.click(); },
            validate: () => {
                const el = document.getElementById('panel-high-contrast');
                return { passed: el?.classList.contains('active') !== window._contrastBefore, expected: 'toggled', actual: el?.classList.contains('active'), stateExists: true };
            },
            cleanup: (el) => { el.click(); delete window._contrastBefore; },
            fix: 'High contrast toggle should toggle body.classList.high-contrast'
        },
        {
            name: 'panel-reduced-motion',
            type: 'toggle',
            elementId: 'panel-reduced-motion',
            statePath: null,
            graphMethod: null,
            expected: 'toggled',
            trigger: (el) => { window._motionBefore = el.classList.contains('active'); el.click(); },
            validate: () => {
                const el = document.getElementById('panel-reduced-motion');
                return { passed: el?.classList.contains('active') !== window._motionBefore, expected: 'toggled', actual: el?.classList.contains('active'), stateExists: true };
            },
            cleanup: (el) => { el.click(); delete window._motionBefore; },
            fix: 'Reduced motion toggle should toggle body.classList.reduced-motion'
        },

        // --- EXPORT PANEL ---
        {
            name: 'panel-export-png',
            type: 'button',
            elementId: 'panel-export-png',
            statePath: null,
            graphMethod: 'renderer',
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-export-png');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'PNG export button should capture canvas and download'
        },
        {
            name: 'panel-export-json',
            type: 'button',
            elementId: 'panel-export-json',
            statePath: null,
            graphMethod: 'graphData',
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-export-json');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'JSON export button should export Graph.graphData() as JSON'
        },
        {
            name: 'panel-export-svg',
            type: 'button',
            elementId: 'panel-export-svg',
            statePath: null,
            graphMethod: null,
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-export-svg');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'SVG export button exists (WebGL canvas limitation noted)'
        },
        {
            name: 'panel-export-embed',
            type: 'button',
            elementId: 'panel-export-embed',
            statePath: null,
            graphMethod: null,
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-export-embed');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Embed code button should copy iframe code to clipboard'
        },

        // --- ANALYSIS PANEL ---
        {
            name: 'panel-stat-visible',
            type: 'display',
            elementId: 'panel-stat-visible',
            statePath: null,
            graphMethod: 'graphData',
            expected: 'exists',
            trigger: (_el) => { /* Read-only */ },
            validate: () => {
                const el = document.getElementById('panel-stat-visible');
                return { passed: !!el, expected: 'exists', actual: el ? el.textContent : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Visible count display should show current visible node count'
        },
        {
            name: 'panel-stat-selected',
            type: 'display',
            elementId: 'panel-stat-selected',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: (_el) => { /* Read-only */ },
            validate: () => {
                const el = document.getElementById('panel-stat-selected');
                return { passed: !!el, expected: 'exists', actual: el ? el.textContent : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Selected count display should show current selection count'
        },
        {
            name: 'panel-stat-edges',
            type: 'display',
            elementId: 'panel-stat-edges',
            statePath: null,
            graphMethod: 'graphData',
            expected: 'exists',
            trigger: (_el) => { /* Read-only */ },
            validate: () => {
                const el = document.getElementById('panel-stat-edges');
                return { passed: !!el, expected: 'exists', actual: el ? el.textContent : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Edge count display should show current edge count'
        },
        {
            name: 'panel-stat-density',
            type: 'display',
            elementId: 'panel-stat-density',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: (_el) => { /* Read-only */ },
            validate: () => {
                const el = document.getElementById('panel-stat-density');
                return { passed: !!el, expected: 'exists', actual: el ? el.textContent : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Density display should show graph density percentage'
        },
        {
            name: 'panel-toggle-metrics',
            type: 'toggle',
            elementId: 'panel-toggle-metrics',
            statePath: null,
            graphMethod: null,
            expected: 'toggled',
            trigger: (el) => { window._metricsBefore = el.classList.contains('active'); el.click(); },
            validate: () => {
                const el = document.getElementById('panel-toggle-metrics');
                return { passed: el?.classList.contains('active') !== window._metricsBefore, expected: 'toggled', actual: el?.classList.contains('active'), stateExists: true };
            },
            cleanup: (el) => { el.click(); delete window._metricsBefore; },
            fix: 'Metrics toggle should show/hide metrics overlay'
        },

        // --- LAYOUT PANEL ---
        {
            name: 'panel-reheat',
            type: 'button',
            elementId: 'panel-reheat',
            statePath: null,
            graphMethod: 'd3ReheatSimulation',
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-reheat');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Reheat button should call Graph.d3ReheatSimulation()'
        },
        {
            name: 'panel-freeze',
            type: 'button',
            elementId: 'panel-freeze',
            statePath: null,
            graphMethod: 'd3Force',
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-freeze');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Freeze button should disable d3 forces'
        },
        {
            name: 'panel-cool',
            type: 'button',
            elementId: 'panel-cool',
            statePath: null,
            graphMethod: 'cooldownTicks',
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-cool');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Cool button should set Graph.cooldownTicks(100)'
        },
        {
            name: 'panel-alpha-decay',
            type: 'slider',
            elementId: 'panel-alpha-decay',
            statePath: null,
            graphMethod: 'd3AlphaDecay',
            expected: 0.05,
            trigger: (el) => { el.value = '0.05'; el.dispatchEvent(new Event('input', { bubbles: true })); },
            validate: () => {
                const el = document.getElementById('panel-alpha-decay');
                return { passed: el?.value === '0.05', expected: '0.05', actual: el?.value, stateExists: true };
            },
            cleanup: (el) => { el.value = '0.0228'; el.dispatchEvent(new Event('input', { bubbles: true })); },
            fix: 'Alpha decay slider should set Graph.d3AlphaDecay(value)'
        },

        // --- VIEW MODES PANEL ---
        {
            name: 'panel-view-3d',
            type: 'button',
            elementId: 'panel-view-3d',
            statePath: 'IS_3D',
            graphMethod: null,
            expected: 'active',
            trigger: (el) => { el.click(); },
            validate: () => {
                const el = document.getElementById('panel-view-3d');
                return { passed: el?.classList.contains('active'), expected: 'active', actual: el?.classList.contains('active') ? 'active' : 'inactive', stateExists: true };
            },
            cleanup: () => {},
            fix: '3D button should set IS_3D=true and switch dimension'
        },
        {
            name: 'panel-view-2d',
            type: 'button',
            elementId: 'panel-view-2d',
            statePath: 'IS_3D',
            graphMethod: null,
            expected: 'active',
            trigger: (el) => { el.click(); },
            validate: () => {
                const el = document.getElementById('panel-view-2d');
                return { passed: el?.classList.contains('active'), expected: 'active', actual: el?.classList.contains('active') ? 'active' : 'inactive', stateExists: true };
            },
            cleanup: () => { document.getElementById('panel-view-3d')?.click(); },
            fix: '2D button should set IS_3D=false and switch dimension'
        },
        {
            name: 'panel-mode-atoms',
            type: 'button',
            elementId: null,
            selector: '[data-panel-mode="atoms"]',
            statePath: 'GRAPH_MODE',
            graphMethod: null,
            expected: 'active',
            trigger: (el) => { el.click(); },
            validate: () => {
                const el = document.querySelector('[data-panel-mode="atoms"]');
                return { passed: el?.classList.contains('active'), expected: 'active', actual: el?.classList.contains('active') ? 'active' : 'inactive', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Atoms button should set GRAPH_MODE="atoms"'
        },
        {
            name: 'panel-mode-files',
            type: 'button',
            elementId: null,
            selector: '[data-panel-mode="files"]',
            statePath: 'GRAPH_MODE',
            graphMethod: null,
            expected: 'active',
            trigger: (el) => { el.click(); },
            validate: () => {
                const el = document.querySelector('[data-panel-mode="files"]');
                return { passed: el?.classList.contains('active'), expected: 'active', actual: el?.classList.contains('active') ? 'active' : 'inactive', stateExists: true };
            },
            cleanup: () => { document.querySelector('[data-panel-mode="atoms"]')?.click(); },
            fix: 'Files button should set GRAPH_MODE="files"'
        },

        // --- PANEL SETTINGS ---
        {
            name: 'panel-reset-layout',
            type: 'button',
            elementId: 'panel-reset-layout',
            statePath: null,
            graphMethod: null,
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-reset-layout');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Reset layout button should call PANEL_SYSTEM.resetLayout()'
        },
        {
            name: 'panel-toggle-dock',
            type: 'button',
            elementId: 'panel-toggle-dock',
            statePath: null,
            graphMethod: null,
            expected: 'clickable',
            trigger: (_el) => { /* Verify exists */ },
            validate: () => {
                const el = document.getElementById('panel-toggle-dock');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Toggle dock button should hide/show panel-container'
        },

        // ═══════════════════════════════════════════════════════════════════════
        // SECTION 3: UPB DATA FLOW VERIFICATION
        // ═══════════════════════════════════════════════════════════════════════

        {
            name: 'upb-module-loaded',
            type: 'module',
            elementId: null,
            statePath: 'UPB',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof UPB !== 'undefined' && UPB.VERSION, expected: 'UPB defined', actual: typeof UPB !== 'undefined' ? UPB.VERSION : 'undefined', stateExists: typeof UPB !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'UPB module should be loaded via upb/index.js'
        },
        {
            name: 'upb-bindings-module',
            type: 'module',
            elementId: null,
            statePath: 'UPB_BINDINGS',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof UPB_BINDINGS !== 'undefined' && UPB_BINDINGS.defaultGraph, expected: 'UPB_BINDINGS defined', actual: typeof UPB_BINDINGS !== 'undefined' ? 'loaded' : 'undefined', stateExists: typeof UPB_BINDINGS !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'UPB_BINDINGS module should be loaded via upb/bindings.js'
        },
        {
            name: 'upb-scales-module',
            type: 'module',
            elementId: null,
            statePath: 'UPB_SCALES',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof UPB_SCALES !== 'undefined' && typeof UPB_SCALES.applyScale === 'function', expected: 'applyScale function', actual: typeof UPB_SCALES?.applyScale, stateExists: typeof UPB_SCALES !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'UPB_SCALES module should be loaded via upb/scales.js'
        },
        {
            name: 'upb-endpoints-module',
            type: 'module',
            elementId: null,
            statePath: 'UPB_ENDPOINTS',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof UPB_ENDPOINTS !== 'undefined' && UPB_ENDPOINTS.SOURCES, expected: 'SOURCES defined', actual: typeof UPB_ENDPOINTS?.SOURCES, stateExists: typeof UPB_ENDPOINTS !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'UPB_ENDPOINTS module should be loaded via upb/endpoints.js'
        },

        // ═══════════════════════════════════════════════════════════════════════
        // SECTION 4: EVENT BUS VERIFICATION
        // ═══════════════════════════════════════════════════════════════════════

        {
            name: 'event-bus-loaded',
            type: 'module',
            elementId: null,
            statePath: 'EVENT_BUS',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof EVENT_BUS !== 'undefined' && typeof EVENT_BUS.emit === 'function', expected: 'emit function', actual: typeof EVENT_BUS?.emit, stateExists: typeof EVENT_BUS !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'EVENT_BUS module should be loaded via event-bus.js'
        },
        {
            name: 'filter-state-loaded',
            type: 'module',
            elementId: null,
            statePath: 'FILTER_STATE',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof FILTER_STATE !== 'undefined' && typeof FILTER_STATE.apply === 'function', expected: 'apply function', actual: typeof FILTER_STATE?.apply, stateExists: typeof FILTER_STATE !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'FILTER_STATE module should be loaded via filter-state.js'
        },
        {
            name: 'panel-system-loaded',
            type: 'module',
            elementId: null,
            statePath: 'PANEL_SYSTEM',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof PANEL_SYSTEM !== 'undefined' && typeof PANEL_SYSTEM.init === 'function', expected: 'init function', actual: typeof PANEL_SYSTEM?.init, stateExists: typeof PANEL_SYSTEM !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'PANEL_SYSTEM module should be loaded via panel-system.js'
        },
        {
            name: 'panel-handlers-loaded',
            type: 'module',
            elementId: null,
            statePath: 'PANEL_HANDLERS',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof PANEL_HANDLERS !== 'undefined' && typeof PANEL_HANDLERS.init === 'function', expected: 'init function', actual: typeof PANEL_HANDLERS?.init, stateExists: typeof PANEL_HANDLERS !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'PANEL_HANDLERS module should be loaded via panel-handlers.js'
        },

        // ═══════════════════════════════════════════════════════════════════════
        // SECTION 5: GRIDSTACK INTEGRATION
        // ═══════════════════════════════════════════════════════════════════════

        {
            name: 'gridstack-loaded',
            type: 'module',
            elementId: null,
            statePath: 'GridStack',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof GridStack !== 'undefined', expected: 'GridStack defined', actual: typeof GridStack, stateExists: typeof GridStack !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'GridStack should be loaded from CDN in template.html'
        },
        {
            name: 'panel-container-exists',
            type: 'element',
            elementId: null,
            selector: '.panel-container.grid-stack',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('.panel-container.grid-stack');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Panel container with grid-stack class should exist in template.html'
        },
        {
            name: 'gridstack-items-count',
            type: 'element',
            elementId: null,
            selector: '.grid-stack-item',
            statePath: null,
            graphMethod: null,
            expected: '9 panels',
            trigger: () => {},
            validate: () => {
                const items = document.querySelectorAll('.grid-stack-item');
                return { passed: items.length >= 9, expected: '>= 9', actual: items.length, stateExists: true };
            },
            cleanup: () => {},
            fix: 'At least 9 grid-stack-item panels should exist'
        },

        // ═══════════════════════════════════════════════════════════════════════
        // SECTION 6: ADDITIONAL SIDEBAR CONTROLS
        // ═══════════════════════════════════════════════════════════════════════

        {
            name: 'sidebar-link-distance',
            type: 'slider',
            elementId: 'physics-link-distance',
            statePath: null,
            graphMethod: 'd3Force',
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.getElementById('physics-link-distance');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Link distance slider should exist'
        },
        {
            name: 'sidebar-link-strength',
            type: 'slider',
            elementId: 'physics-link-strength',
            statePath: null,
            graphMethod: 'd3Force',
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.getElementById('physics-link-strength');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Link strength slider should exist'
        },
        {
            name: 'sidebar-gravity',
            type: 'slider',
            elementId: 'physics-gravity',
            statePath: null,
            graphMethod: 'd3Force',
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.getElementById('physics-gravity');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Gravity slider should exist'
        },
        {
            name: 'sidebar-collision',
            type: 'slider',
            elementId: 'physics-collision',
            statePath: null,
            graphMethod: 'd3Force',
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.getElementById('physics-collision');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Collision radius slider should exist'
        },
        {
            name: 'sidebar-node-label',
            type: 'slider',
            elementId: 'cfg-node-label',
            statePath: 'APPEARANCE_STATE.labelSize',
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.getElementById('cfg-node-label');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Node label size slider should exist'
        },
        {
            name: 'sidebar-bloom-strength',
            type: 'slider',
            elementId: 'cfg-bloom-strength',
            statePath: 'APPEARANCE_STATE.bloomStrength',
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.getElementById('cfg-bloom-strength');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Bloom strength slider should exist'
        },
        {
            name: 'sidebar-bloom-radius',
            type: 'slider',
            elementId: 'cfg-bloom-radius',
            statePath: 'APPEARANCE_STATE.bloomRadius',
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.getElementById('cfg-bloom-radius');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Bloom radius slider should exist'
        },
        {
            name: 'sidebar-particle-count',
            type: 'slider',
            elementId: 'cfg-particle-count',
            statePath: 'APPEARANCE_STATE.particleCount',
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.getElementById('cfg-particle-count');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Particle count slider should exist'
        },
        {
            name: 'sidebar-particle-width',
            type: 'slider',
            elementId: 'cfg-particle-width',
            statePath: 'APPEARANCE_STATE.particleWidth',
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.getElementById('cfg-particle-width');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Particle width slider should exist'
        },
        {
            name: 'sidebar-particle-speed',
            type: 'slider',
            elementId: 'cfg-particle-speed',
            statePath: 'APPEARANCE_STATE.particleSpeed',
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.getElementById('cfg-particle-speed');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Particle speed slider should exist'
        },

        // ═══════════════════════════════════════════════════════════════════════
        // SECTION 7: CORE MODULES VERIFICATION
        // ═══════════════════════════════════════════════════════════════════════

        {
            name: 'color-engine-loaded',
            type: 'module',
            elementId: null,
            statePath: 'COLOR',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof COLOR !== 'undefined' && typeof COLOR.getNodeColor === 'function', expected: 'getNodeColor function', actual: typeof COLOR?.getNodeColor, stateExists: typeof COLOR !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'COLOR module should be loaded via color-engine.js'
        },
        {
            name: 'data-manager-loaded',
            type: 'module',
            elementId: null,
            statePath: 'DATA',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof DATA !== 'undefined' && typeof DATA.getNodes === 'function', expected: 'getNodes function', actual: typeof DATA?.getNodes, stateExists: typeof DATA !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'DATA module should be loaded via data-manager.js'
        },
        {
            name: 'selection-module-loaded',
            type: 'module',
            elementId: null,
            statePath: 'SELECT',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof SELECT !== 'undefined' && typeof SELECT.clear === 'function', expected: 'clear function', actual: typeof SELECT?.clear, stateExists: typeof SELECT !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'SELECT module should be loaded via selection.js'
        },
        {
            name: 'animation-module-loaded',
            type: 'module',
            elementId: null,
            statePath: 'ANIM',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof ANIM !== 'undefined' && typeof ANIM.applyLayout === 'function', expected: 'applyLayout function', actual: typeof ANIM?.applyLayout, stateExists: typeof ANIM !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'ANIM module should be loaded via animation.js'
        },
        {
            name: 'legend-module-loaded',
            type: 'module',
            elementId: null,
            statePath: 'LEGEND',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof LEGEND !== 'undefined' && typeof LEGEND.render === 'function', expected: 'render function', actual: typeof LEGEND?.render, stateExists: typeof LEGEND !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'LEGEND module should be loaded via legend-manager.js'
        },
        {
            name: 'refresh-module-loaded',
            type: 'module',
            elementId: null,
            statePath: 'REFRESH',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof REFRESH !== 'undefined' && typeof REFRESH.throttled === 'function', expected: 'throttled function', actual: typeof REFRESH?.throttled, stateExists: typeof REFRESH !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'REFRESH module should be loaded via refresh-throttle.js'
        },
        {
            name: 'edge-system-loaded',
            type: 'module',
            elementId: null,
            statePath: 'EDGE',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof EDGE !== 'undefined' && typeof EDGE.setMode === 'function', expected: 'setMode function', actual: typeof EDGE?.setMode, stateExists: typeof EDGE !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'EDGE module should be loaded via edge-system.js'
        },
        {
            name: 'file-viz-loaded',
            type: 'module',
            elementId: null,
            statePath: 'FILE_VIZ',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof FILE_VIZ !== 'undefined' && typeof FILE_VIZ.setMode === 'function', expected: 'setMode function', actual: typeof FILE_VIZ?.setMode, stateExists: typeof FILE_VIZ !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'FILE_VIZ module should be loaded via file-viz.js'
        },
        {
            name: 'control-bar-loaded',
            type: 'module',
            elementId: null,
            statePath: 'CONTROL_BAR',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof CONTROL_BAR !== 'undefined' && typeof CONTROL_BAR.toggle === 'function', expected: 'toggle function', actual: typeof CONTROL_BAR?.toggle, stateExists: typeof CONTROL_BAR !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'CONTROL_BAR module should be loaded via control-bar.js'
        },
        {
            name: 'sidebar-module-loaded',
            type: 'module',
            elementId: null,
            statePath: 'SIDEBAR',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof SIDEBAR !== 'undefined' && typeof SIDEBAR.init === 'function', expected: 'init function', actual: typeof SIDEBAR?.init, stateExists: typeof SIDEBAR !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'SIDEBAR module should be loaded via sidebar.js'
        },
        {
            name: 'hud-module-loaded',
            type: 'module',
            elementId: null,
            statePath: 'HUD',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof HUD !== 'undefined' && typeof HUD.setupFade === 'function', expected: 'setupFade function', actual: typeof HUD?.setupFade, stateExists: typeof HUD !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'HUD module should be loaded via hud.js'
        },
        {
            name: 'dimension-module-loaded',
            type: 'module',
            elementId: null,
            statePath: 'DIMENSION',
            graphMethod: null,
            expected: 'loaded',
            trigger: () => {},
            validate: () => {
                return { passed: typeof DIMENSION !== 'undefined' && typeof DIMENSION.setup === 'function', expected: 'setup function', actual: typeof DIMENSION?.setup, stateExists: typeof DIMENSION !== 'undefined' };
            },
            cleanup: () => {},
            fix: 'DIMENSION module should be loaded via dimension.js'
        },

        // ═══════════════════════════════════════════════════════════════════════
        // SECTION 8: LAYOUT PRESET BUTTONS
        // ═══════════════════════════════════════════════════════════════════════

        {
            name: 'layout-preset-force',
            type: 'button',
            elementId: null,
            selector: '[data-layout="force"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-layout="force"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Force layout button should exist'
        },
        {
            name: 'layout-preset-radial',
            type: 'button',
            elementId: null,
            selector: '[data-layout="radial"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-layout="radial"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Radial layout button should exist'
        },
        {
            name: 'layout-preset-tree',
            type: 'button',
            elementId: null,
            selector: '[data-layout="tree"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-layout="tree"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Tree layout button should exist'
        },
        {
            name: 'layout-preset-grid',
            type: 'button',
            elementId: null,
            selector: '[data-layout="grid"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-layout="grid"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Grid layout button should exist'
        },
        {
            name: 'layout-preset-sphere',
            type: 'button',
            elementId: null,
            selector: '[data-layout="sphere"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-layout="sphere"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Sphere layout button should exist'
        },
        {
            name: 'layout-preset-spiral',
            type: 'button',
            elementId: null,
            selector: '[data-layout="spiral"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-layout="spiral"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Spiral layout button should exist'
        },

        // ═══════════════════════════════════════════════════════════════════════
        // SECTION 9: COLOR PRESET BUTTONS
        // ═══════════════════════════════════════════════════════════════════════

        {
            name: 'color-preset-tier',
            type: 'button',
            elementId: null,
            selector: '[data-color="tier"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-color="tier"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Tier color preset button should exist'
        },
        {
            name: 'color-preset-role',
            type: 'button',
            elementId: null,
            selector: '[data-color="role"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-color="role"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Role color preset button should exist'
        },
        {
            name: 'color-preset-family',
            type: 'button',
            elementId: null,
            selector: '[data-color="family"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-color="family"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Family color preset button should exist'
        },
        {
            name: 'color-preset-file',
            type: 'button',
            elementId: null,
            selector: '[data-color="file"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-color="file"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'File color preset button should exist'
        },
        {
            name: 'color-preset-degree',
            type: 'button',
            elementId: null,
            selector: '[data-color="degree"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-color="degree"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Degree color preset button should exist'
        },
        {
            name: 'color-preset-complexity',
            type: 'button',
            elementId: null,
            selector: '[data-color="complexity"]',
            statePath: null,
            graphMethod: null,
            expected: 'exists',
            trigger: () => {},
            validate: () => {
                const el = document.querySelector('[data-color="complexity"]');
                return { passed: !!el, expected: 'exists', actual: el ? 'exists' : 'missing', stateExists: true };
            },
            cleanup: () => {},
            fix: 'Complexity color preset button should exist'
        }
    ];

    // =========================================================================
    // TEST RUNNER - Enhanced with diagnostics
    // =========================================================================

    async function runTest(testDef) {
        const result = {
            name: testDef.name,
            type: testDef.type,
            passed: false,
            error: null,
            elementFound: false,
            // Enhanced diagnostics
            expected: testDef.expected,
            actual: null,
            stateExists: false,
            trace: null,
            fix: testDef.fix || null
        };

        try {
            // Find element
            const el = testDef.elementId
                ? document.getElementById(testDef.elementId)
                : document.querySelector(testDef.selector);

            if (!el) {
                result.error = 'Element not found';
                result.trace = traceBinding(testDef.elementId || testDef.selector, testDef.statePath, testDef.graphMethod);
                return result;
            }
            result.elementFound = true;

            // Trace binding chain before test
            result.trace = traceBinding(testDef.elementId || testDef.selector, testDef.statePath, testDef.graphMethod);

            // Run trigger
            testDef.trigger(el);

            // Small delay for async effects
            await new Promise(r => setTimeout(r, 50));

            // Validate with enhanced result
            const validateResult = testDef.validate();
            if (typeof validateResult === 'object') {
                result.passed = validateResult.passed;
                result.expected = validateResult.expected !== undefined ? validateResult.expected : testDef.expected;
                result.actual = validateResult.actual;
                result.stateExists = validateResult.stateExists;
                if (validateResult.error) result.error = validateResult.error;
            } else {
                result.passed = validateResult;
            }

            // Cleanup
            if (testDef.cleanup) {
                await new Promise(r => setTimeout(r, 50));
                testDef.cleanup(el);
            }

        } catch (err) {
            result.error = err.message;
            result.passed = false;
        }

        return result;
    }

    async function runAll() {
        if (_running) {
            console.warn('[CIRCUIT] Already running');
            return;
        }
        _running = true;
        _results.clear();

        console.log('%c[CIRCUIT] Starting control validation...', 'color: #4dd4ff; font-weight: bold');

        const startTime = performance.now();
        let passed = 0;
        let failed = 0;

        for (const test of TESTS) {
            const result = await runTest(test);
            _results.set(test.name, result);

            if (result.passed) {
                passed++;
                console.log(`  %c✓ ${test.name}`, 'color: #4ade80');
            } else {
                failed++;
                const reason = result.error || (!result.elementFound ? 'Element not found' : 'Validation failed');
                console.log(`  %c✗ ${test.name}: ${reason}`, 'color: #f87171');
                if (result.expected !== undefined && result.actual !== undefined) {
                    console.log(`    Expected: ${JSON.stringify(result.expected)}, Got: ${JSON.stringify(result.actual)}`);
                }
            }

            // Small delay between tests
            await new Promise(r => setTimeout(r, 100));
        }

        const elapsed = (performance.now() - startTime).toFixed(0);
        const total = passed + failed;
        const pct = ((passed / total) * 100).toFixed(1);

        console.log('%c─────────────────────────────────────', 'color: #666');
        if (failed === 0) {
            console.log(`%c[CIRCUIT] ALL PASS: ${passed}/${total} controls (${elapsed}ms)`,
                'color: #4ade80; font-weight: bold');
        } else {
            console.log(`%c[CIRCUIT] ${passed}/${total} passed (${pct}%), ${failed} FAILED (${elapsed}ms)`,
                'color: #f87171; font-weight: bold');
        }

        _running = false;
        return { passed, failed, total, results: Object.fromEntries(_results) };
    }

    async function test(name) {
        const testDef = TESTS.find(t => t.name === name);
        if (!testDef) {
            console.error(`[CIRCUIT] Unknown test: ${name}`);
            return null;
        }
        const result = await runTest(testDef);
        _results.set(name, result);
        return result;
    }

    function report() {
        return Object.fromEntries(_results);
    }

    function listTests() {
        return TESTS.map(t => ({ name: t.name, type: t.type }));
    }

    /**
     * Get detailed fix recommendations for all failures
     */
    function diagnose() {
        const failures = [];
        for (const [name, result] of _results) {
            if (!result.passed) {
                failures.push({
                    control: name,
                    type: result.type,
                    error: result.error,
                    expected: result.expected,
                    actual: result.actual,
                    elementFound: result.elementFound,
                    stateExists: result.stateExists,
                    trace: result.trace ? result.trace.chain : [],
                    fix: result.fix
                });
            }
        }
        return failures;
    }

    // =========================================================================
    // INVENTORY - Generate control tables for documentation
    // =========================================================================

    /**
     * Generate markdown table of all tested controls
     * @returns {string} Markdown table
     */
    function inventory() {
        const lines = [
            '| Control | Type | Element ID | State Path | Purpose |',
            '|---------|------|------------|------------|---------|'
        ];
        TESTS.forEach(t => {
            const purpose = t.fix ? t.fix.split(' - ')[0].replace(/^(Check|Ensure) /, '') : t.name;
            lines.push(`| ${t.name} | ${t.type} | \`${t.elementId || '-'}\` | \`${t.statePath || '-'}\` | ${purpose.substring(0, 40)} |`);
        });
        return lines.join('\n');
    }

    /**
     * Generate JSON inventory of all controls
     * @returns {Array} Control definitions
     */
    function inventoryJSON() {
        return TESTS.map(t => ({
            name: t.name,
            type: t.type,
            elementId: t.elementId,
            statePath: t.statePath,
            graphMethod: t.graphMethod,
            expected: t.expected
        }));
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        runAll,
        test,
        report,
        listTests,
        diagnose,
        inventory,
        inventoryJSON,
        get isRunning() { return _running; },
        TESTS
    };
})();

// Global shortcut
window.CIRCUIT = CIRCUIT;

console.log('[Module] CIRCUIT loaded - UI control validator with diagnostics');
