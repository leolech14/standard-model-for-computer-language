/**
 * CIRCUIT BREAKER MODULE - Enhanced Diagnostics
 *
 * Runtime self-test system that validates all UI controls work.
 * Provides detailed diagnostics for fixing broken controls.
 *
 * Usage:
 *   CIRCUIT.runAll()           // Run all tests with full diagnostics
 *   CIRCUIT.test('edge-opacity') // Test specific control
 *   CIRCUIT.report()           // Get test results
 *   CIRCUIT.diagnose()         // Get fix recommendations
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
    // =========================================================================

    const TESTS = [
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
                return {
                    passed: isActiveNow !== window._arrowsActiveBefore,
                    expected: !window._arrowsActiveBefore,
                    actual: isActiveNow,
                    stateExists: true
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
                // Use window.Graph explicitly (Graph is exposed at app.js:1111)
                const G = window.Graph;
                if (!G) {
                    return { passed: false, error: 'Graph not defined', stateExists: false };
                }
                if (!G.d3Force) {
                    return { passed: false, error: 'Graph.d3Force not available', stateExists: false };
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
                    return {
                        passed: strength === -200,
                        expected: -200,
                        actual: strength,
                        stateExists: true
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
                    passed: transitionStarted || window.DIMENSION_TRANSITION === true,
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
    // PUBLIC API
    // =========================================================================

    return {
        runAll,
        test,
        report,
        listTests,
        diagnose,
        get isRunning() { return _running; },
        TESTS
    };
})();

// Global shortcut
window.CIRCUIT = CIRCUIT;

console.log('[Module] CIRCUIT loaded - UI control validator with diagnostics');
