/**
 * UNIVERSAL PROPERTY BINDER - BACKEND TEST SUITE
 * Run with: node test_upb.js
 */

// Mock browser environment for modules that check window
global.window = {};

// Load Modules
const SCALES = require('../scales.js');
const ENDPOINTS = require('../endpoints.js');
const BLENDERS = require('../blenders.js');

// Mock window dependencies for Bindings/Index
window.UPB_SCALES = SCALES;
window.UPB_ENDPOINTS = ENDPOINTS;
window.UPB_BLENDERS = BLENDERS;

const BINDINGS = require('../bindings.js');
window.UPB_BINDINGS = BINDINGS;

const UPB = require('../index.js');
window.UPB = UPB;

// Test Runner Helper
let passed = 0;
let failed = 0;

function test(name, fn) {
    try {
        fn();
        console.log(`✅ PASS: ${name}`);
        passed++;
    } catch (e) {
        console.error(`❌ FAIL: ${name}`);
        console.error(`   ${e.message}`);
        failed++;
    }
}

function assert(condition, message) {
    if (!condition) throw new Error(message || "Assertion failed");
}

function assertNear(actual, expected, tolerance = 0.001) {
    if (Math.abs(actual - expected) > tolerance) {
        throw new Error(`Expected ${expected} +/- ${tolerance}, got ${actual}`);
    }
}

console.log('--- UPB COMPREHENSIVE BACKEND TEST ---\n');

// 1. SCALES Tests
console.log('MODULE: SCALES');
test('Linear Scale', () => {
    assertNear(SCALES.applyScale('linear', 50, 0, 100), 0.5);
    assertNear(SCALES.applyScale('linear', 100, 0, 100), 1.0);
    assertNear(SCALES.applyScale('linear', 0, 0, 100), 0.0);
});

test('Log Scale', () => {
    // log10(1) = 0, log10(100) = 2. log10(10) = 1. Result should be 0.5
    assertNear(SCALES.applyScale('log', 10, 1, 100), 0.5);
});

test('Sqrt Scale', () => {
    // sqrt(0)=0, sqrt(100)=10. sqrt(25)=5. Result should be 0.5
    assertNear(SCALES.applyScale('sqrt', 25, 0, 100), 0.5);
});

test('Inverse Scale', () => {
    assertNear(SCALES.applyScale('inverse', 25, 0, 100), 0.75);
});

test('Discrete Scale', () => {
    const domain = ['a', 'b', 'c'];
    assertNear(SCALES.applyScale('discrete', 'a', 0, 0, domain), 0.0);
    assertNear(SCALES.applyScale('discrete', 'b', 0, 0, domain), 0.5);
    assertNear(SCALES.applyScale('discrete', 'c', 0, 0, domain), 1.0);
});


// 2. ENDPOINTS Tests
console.log('\nMODULE: ENDPOINTS');
test('Source Retrieval', () => {
    const source = ENDPOINTS.getSource('token_estimate');
    assert(source !== null, 'token_estimate should exist');
    assert(source.type === 'continuous', 'token_estimate should be continuous');
});

test('Target Retrieval', () => {
    const target = ENDPOINTS.getTarget('nodeSize');
    assert(target !== null, 'nodeSize should exist');
    assert(target.range[0] === 1, 'nodeSize min range should be 1');
});


// 3. BLENDERS Tests
console.log('\nMODULE: BLENDERS');
test('Blend: Replace (Last Wins)', () => {
    assert(BLENDERS.blend('replace', [0.1, 0.5, 0.9]) === 0.9, 'Should return last value');
});

test('Blend: Average', () => {
    assertNear(BLENDERS.blend('average', [0.0, 1.0]), 0.5);
});

test('Blend: Add (Clamped)', () => {
    assertNear(BLENDERS.blend('add', [0.4, 0.5]), 0.9);
    assertNear(BLENDERS.blend('add', [0.6, 0.6]), 1.0, 0.001); // Should clamp
});

test('Blend: Multiply', () => {
    // 0.5 * 0.5 = 0.25?? No, implementation is: product *= (1 - (w * (1-v))) ??
    // Let's check implementation behavior based on logic:
    // "interpolating between 1 (no effect) and v (full effect)"
    // If weights missing, w=1. effectiveValue = 1 - (1 * (1-v)) = v.
    // So distinct values [0.5, 0.5] -> 0.5 * 0.5 = 0.25
    assertNear(BLENDERS.blend('multiply', [0.5, 0.5]), 0.25);
});


// 4. BINDINGS Tests
console.log('\nMODULE: BINDINGS & GRAPH');
test('Binding Lifecycle', () => {
    const graph = new BINDINGS.BindingGraph();

    // Bind
    graph.bind('token_estimate', 'nodeSize', { scale: 'linear' });
    const bindings = graph.getBindingsFor('nodeSize');
    assert(bindings.length === 1, 'Should have 1 binding');
    assert(bindings[0].source === 'token_estimate', 'Source should match');

    // Unbind
    graph.unbind('token_estimate', 'nodeSize');
    assert(graph.getBindingsFor('nodeSize').length === 0, 'Should be empty after unbind');
});

test('Evaluation Logic', () => {
    const graph = new BINDINGS.BindingGraph();

    // Bind token_estimate (0-100) to nodeSize (0-10)
    // Using linear scale. Input 50 -> Norm 0.5 -> Output 5
    graph.bind('token_estimate', 'nodeSize', {
        scale: 'linear',
        range: [0, 10] // Override target range for test simplicity
    });

    // Set data range for normalization
    graph.setDataRanges({
        'token_estimate': { min: 0, max: 100 }
    });

    const node = { token_estimate: 50 };
    const result = graph.evaluate(node);

    assert(result.nodeSize !== undefined, 'Should produce nodeSize output');
    assertNear(result.nodeSize, 5.0, 0.01);
});

test('Multi-Binding Evaluation (Last Wins)', () => {
    const graph = new BINDINGS.BindingGraph();

    // Bind 1: tokens -> size (Output 5)
    graph.bind('token_estimate', 'nodeSize', { scale: 'linear', range: [0, 10] }); // Input 50 -> 5

    // Bind 2: complexity -> size (Output 8)
    graph.bind('complexity', 'nodeSize', { scale: 'linear', range: [0, 10] }); // Input 80 -> 8

    graph.setDataRanges({
        'token_estimate': { min: 0, max: 100 },
        'complexity': { min: 0, max: 100 }
    });

    const node = { token_estimate: 50, complexity: 80 };
    const result = graph.evaluate(node);

    assertNear(result.nodeSize, 8.0, 0.01); // Last binding wins (default behavior)
});

// 5. PUBLIC API Tests
console.log('\nMODULE: UPB API');
test('UPB.bind & evaluate', () => {
    UPB.init({ 'test_metric': { min: 0, max: 10 } });
    UPB.bind('test_metric', 'opacity', { scale: 'linear', range: [0, 1] });

    const node = { test_metric: 5 };
    const result = UPB.evaluate(node);
    assertNear(result.opacity, 0.5);
});

console.log('\n---------------------------------------');
console.log(`TOTAL: ${passed + failed} | PASSED: ${passed} | FAILED: ${failed}`);

if (failed > 0) process.exit(1);
