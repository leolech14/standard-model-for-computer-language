/**
 * COLOR ENGINE CONTRACT TESTS
 *
 * Validates that the COLOR engine maintains its OKLCH guarantee:
 * - All outputs are valid hex strings (#RRGGBB)
 * - No HSL, RGB, or other formats leak through
 *
 * Run: COLOR_TEST.runAll() in browser console
 * Or:  Part of Circuit Breaker extended validation
 *
 * @module COLOR_TEST
 * @version 1.0.0
 */

const COLOR_TEST = (function() {
    'use strict';

    // =========================================================================
    // TEST UTILITIES
    // =========================================================================

    const HEX_PATTERN = /^#[0-9a-fA-F]{6}$/;

    function isValidHex(color) {
        return typeof color === 'string' && HEX_PATTERN.test(color);
    }

    function assert(condition, message) {
        if (!condition) {
            throw new Error(`[COLOR_TEST FAIL] ${message}`);
        }
    }

    // =========================================================================
    // CONTRACT TESTS
    // =========================================================================

    const tests = {
        /**
         * Test 1: toHex produces valid hex for standard inputs
         */
        'toHex-standard': () => {
            const COLOR = window.COLOR;
            assert(COLOR && COLOR.toHex, 'COLOR.toHex not available');

            const testCases = [
                { h: 0, c: 0.2, l: 0.5 },      // Red-ish
                { h: 120, c: 0.2, l: 0.5 },    // Green-ish
                { h: 240, c: 0.2, l: 0.5 },    // Blue-ish
                { h: 60, c: 0.15, l: 0.7 },    // Yellow
                { h: 300, c: 0.18, l: 0.55 },  // Magenta
            ];

            testCases.forEach((oklch, i) => {
                const result = COLOR.toHex(oklch);
                assert(isValidHex(result),
                    `toHex case ${i}: expected hex, got ${result}`);
            });

            return { passed: testCases.length, total: testCases.length };
        },

        /**
         * Test 2: toHex handles edge cases
         */
        'toHex-edge-cases': () => {
            const COLOR = window.COLOR;
            const edgeCases = [
                { h: 0, c: 0, l: 0 },          // Pure black
                { h: 0, c: 0, l: 1 },          // Pure white
                { h: 360, c: 0.2, l: 0.5 },    // Hue wraparound (360 = 0)
                { h: 720, c: 0.2, l: 0.5 },    // Hue > 360
                { h: -30, c: 0.2, l: 0.5 },    // Negative hue
                { h: 180, c: 0, l: 0.5 },      // Zero chroma (gray)
                { h: 180, c: 0.4, l: 0.5 },    // Max chroma
                { h: 180, c: 0.2, l: 0.01 },   // Near-black
                { h: 180, c: 0.2, l: 0.99 },   // Near-white
            ];

            let passed = 0;
            edgeCases.forEach((oklch, i) => {
                const result = COLOR.toHex(oklch);
                if (isValidHex(result)) {
                    passed++;
                } else {
                    console.warn(`[COLOR_TEST] Edge case ${i} failed:`, oklch, '→', result);
                }
            });

            return { passed, total: edgeCases.length };
        },

        /**
         * Test 3: get() returns valid hex for all palette dimensions
         */
        'get-palette': () => {
            const COLOR = window.COLOR;
            assert(COLOR && COLOR.get, 'COLOR.get not available');

            const dimensions = ['tier', 'family', 'ring', 'layer', 'atom', 'roleCategory', 'edgeType'];
            let passed = 0;
            let total = 0;

            dimensions.forEach(dim => {
                const categories = COLOR.getCategories(dim);
                categories.forEach(cat => {
                    total++;
                    const result = COLOR.get(dim, cat);
                    if (isValidHex(result)) {
                        passed++;
                    } else {
                        console.warn(`[COLOR_TEST] get('${dim}', '${cat}') = ${result}`);
                    }
                });
            });

            return { passed, total };
        },

        /**
         * Test 4: getInterval() returns valid hex across 0-1 range
         */
        'getInterval-sweep': () => {
            const COLOR = window.COLOR;
            assert(COLOR && COLOR.getInterval, 'COLOR.getInterval not available');

            const intervalNames = ['markov', 'weight', 'confidence', 'complexity', 'trust'];
            const testValues = [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0];

            let passed = 0;
            let total = 0;

            intervalNames.forEach(name => {
                testValues.forEach(v => {
                    total++;
                    const result = COLOR.getInterval(name, v);
                    if (isValidHex(result)) {
                        passed++;
                    } else {
                        console.warn(`[COLOR_TEST] getInterval('${name}', ${v}) = ${result}`);
                    }
                });
            });

            return { passed, total };
        },

        /**
         * Test 5: interpolate() returns valid hex
         */
        'interpolate': () => {
            const COLOR = window.COLOR;
            assert(COLOR && COLOR.interpolate, 'COLOR.interpolate not available');

            const testCases = [
                ['#ff0000', '#0000ff', 0],
                ['#ff0000', '#0000ff', 0.5],
                ['#ff0000', '#0000ff', 1],
                ['#000000', '#ffffff', 0.5],
                [{ h: 0, c: 0.2, l: 0.5 }, { h: 180, c: 0.2, l: 0.5 }, 0.5],
            ];

            let passed = 0;
            testCases.forEach(([c1, c2, t], i) => {
                const result = COLOR.interpolate(c1, c2, t);
                if (isValidHex(result)) {
                    passed++;
                } else {
                    console.warn(`[COLOR_TEST] interpolate case ${i} = ${result}`);
                }
            });

            return { passed, total: testCases.length };
        },

        /**
         * Test 6: getSchemeColor() returns valid hex for all schemes
         */
        'schemes': () => {
            const COLOR = window.COLOR;
            assert(COLOR && COLOR.listSchemes, 'COLOR.listSchemes not available');

            const schemes = COLOR.listSchemes();
            const testValues = [0, 0.25, 0.5, 0.75, 1.0];

            let passed = 0;
            let total = 0;

            schemes.forEach(scheme => {
                testValues.forEach(t => {
                    total++;
                    const result = COLOR.getSchemeColor(scheme, t);
                    if (isValidHex(result)) {
                        passed++;
                    } else {
                        console.warn(`[COLOR_TEST] getSchemeColor('${scheme}', ${t}) = ${result}`);
                    }
                });
            });

            return { passed, total };
        },

        /**
         * Test 7: Telemetry bySource regression test
         * Ensures bySource is populated when perSource:true
         */
        'telemetry-bySource': () => {
            const COLOR = window.COLOR;
            const TELEM = window.COLOR_TELEM;

            if (!TELEM || !TELEM.capture) {
                return { passed: 0, total: 1, skipped: 'COLOR_TELEM not available' };
            }

            const m = TELEM.capture(() => {
                COLOR.getSchemeColor('viridis', 0.5);
                COLOR.get('tier', 'T0');
                COLOR.toHex({ l: 0.5, c: 0.05, h: 60 });
            }, { frameId: 'bySource-test', perSource: true });

            const bs = m.bySource;
            const keys = bs ? Object.keys(bs) : [];

            // Regression test: bySource must exist and have entries
            const hasScheme = keys.some(k => k.startsWith('scheme:'));
            const hasPalette = keys.some(k => k.startsWith('palette:'));
            const hasApi = keys.some(k => k.startsWith('api:'));

            let passed = 0;
            if (bs && keys.length >= 3) passed++;
            if (hasScheme) passed++;
            if (hasPalette) passed++;
            if (hasApi) passed++;

            // Events sum check
            let eventsSum = 0;
            for (const k of keys) {
                eventsSum += bs[k].events;
            }
            if (eventsSum === m.events) passed++;

            return { passed, total: 5 };
        },

        /**
         * Test 8: Categorical palettes must not clip (gamut budget)
         * Categorical colors are semantic labels - clipping is a product defect
         */
        'categorical-gamut-safe': () => {
            const COLOR = window.COLOR;
            const TELEM = window.COLOR_TELEM;

            if (!TELEM || !TELEM.capture) {
                return { passed: 0, total: 1, skipped: 'COLOR_TELEM not available' };
            }

            // Test tier palette (critical categorical)
            const tiers = ['T0', 'T1', 'T2'];
            const tierMetrics = TELEM.capture(() => {
                for (const t of tiers) COLOR.get('tier', t);
            }, { frameId: 'tier-gamut' });

            // Test family palette
            const families = ['LOG', 'DAT', 'ORG', 'EXE', 'EXT'];
            const familyMetrics = TELEM.capture(() => {
                for (const f of families) COLOR.get('family', f);
            }, { frameId: 'family-gamut' });

            let passed = 0;

            // Tier: no collapse, no clip
            if (tierMetrics.collapse_ratio === 1) passed++;
            if (tierMetrics.clip_rate === 0) passed++;

            // Family: no collapse, no clip
            if (familyMetrics.collapse_ratio === 1) passed++;
            if (familyMetrics.clip_rate === 0) passed++;

            return {
                passed,
                total: 4,
                tier_clip_rate: tierMetrics.clip_rate,
                family_clip_rate: familyMetrics.clip_rate
            };
        },

        /**
         * Test 9: No HSL/RGB string outputs anywhere in palette
         */
        'no-hsl-leak': () => {
            const COLOR = window.COLOR;
            const HSL_PATTERN = /^hsl/i;
            const RGB_PATTERN = /^rgb/i;

            let violations = [];

            // Check all palette entries
            const dimensions = Object.keys(COLOR.palette || {});
            dimensions.forEach(dim => {
                const categories = Object.keys(COLOR.palette[dim] || {});
                categories.forEach(cat => {
                    const result = COLOR.get(dim, cat);
                    if (HSL_PATTERN.test(result) || RGB_PATTERN.test(result)) {
                        violations.push(`${dim}.${cat}: ${result}`);
                    }
                });
            });

            if (violations.length > 0) {
                console.error('[COLOR_TEST] HSL/RGB leaks found:', violations);
            }

            return {
                passed: violations.length === 0 ? 1 : 0,
                total: 1,
                violations
            };
        }
    };

    // =========================================================================
    // RUNNER
    // =========================================================================

    function runAll() {
        console.log('%c[COLOR_TEST] Starting contract validation...', 'color: #4dd4ff; font-weight: bold');

        const results = {};
        let totalPassed = 0;
        let totalTests = 0;

        Object.entries(tests).forEach(([name, testFn]) => {
            try {
                const result = testFn();
                results[name] = { status: 'PASS', ...result };
                totalPassed += result.passed;
                totalTests += result.total;
                console.log(`  [+] ${name}: ${result.passed}/${result.total}`);
            } catch (err) {
                results[name] = { status: 'FAIL', error: err.message };
                console.error(`  [-] ${name}: ${err.message}`);
            }
        });

        const allPass = totalPassed === totalTests;
        const summary = `${totalPassed}/${totalTests} assertions passed`;

        if (allPass) {
            console.log(`%c[COLOR_TEST] ALL PASS: ${summary}`, 'color: #4ade80; font-weight: bold');
        } else {
            console.log(`%c[COLOR_TEST] FAIL: ${summary}`, 'color: #f87171; font-weight: bold');
        }

        return {
            passed: allPass,
            summary,
            results
        };
    }

    function runQuick() {
        // Fast smoke test - just verify toHex works
        const COLOR = window.COLOR;
        if (!COLOR || !COLOR.toHex) return false;

        const result = COLOR.toHex({ h: 220, c: 0.2, l: 0.6 });
        return isValidHex(result);
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        runAll,
        runQuick,
        isValidHex,
        tests
    };
})();

// Register globally
if (typeof window !== 'undefined') {
    window.COLOR_TEST = COLOR_TEST;
}

console.log('[Module] COLOR_TEST loaded - COLOR engine contract validation');
