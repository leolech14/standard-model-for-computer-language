/**
 * HOLOGRAPHIC LOGIC SIMULATION
 * Part of the Socratic Layer.
 * 
 * Purpose: Simulates complex state transitions (Atom Mode -> File Mode) to ensure
 * logical consistency of the Universal Property Binder (UPB) across different
 * levels of the Holarchic Scale.
 * 
 * Run with: node holographic_simulation.js
 */

// Mock Environment
global.window = {};
console.log('[HOLOGRAPHIC] Initializing Simulation Environment...');

// Load Modules
const SCALES = require('../scales.js');
const ENDPOINTS = require('../endpoints.js');
const BLENDERS = require('../blenders.js');
window.UPB_SCALES = SCALES;
window.UPB_ENDPOINTS = ENDPOINTS;
window.UPB_BLENDERS = BLENDERS;

const BINDINGS = require('../bindings.js');
window.UPB_BINDINGS = BINDINGS;

const UPB = require('../index.js');
window.UPB = UPB;

// Test Simulation State
let passed = 0;
let failed = 0;
function assert(condition, message) {
    if (!condition) {
        console.error(`❌ FAIL: ${message}`);
        failed++;
        throw new Error(message);
    } else {
        console.log(`✅ PASS: ${message}`);
        passed++;
    }
}

// =============================================================================
// SCENARIO: The "Scale Jump" (Atom -> File)
// =============================================================================
console.log('\n--- SIMULATION: ATOM -> FILE SCALE TRANSITION ---');

// 1. Initial State: Atom Mode
// User binds "Token Count" (which is small for atoms, e.g. 0-100)
console.log('1. User binds "token_estimate" (Atom Scale) -> "nodeSize"');
UPB.init({
    'token_estimate': { min: 0, max: 100 } // Atom range
});
UPB.bind('token_estimate', 'nodeSize', { scale: 'linear' });

// Verify Atom normalization
const atomNode = { id: 'atom1', token_estimate: 50 };
const atomResult = UPB.evaluate(atomNode);
// 50 in [0, 100] -> 0.5 normalized binding -> 0.5 visual output (assuming target 0-1)
// Default target range is often [0,1] unless specified. 
// Let's assume default [0,1] for cleaner math or check endpoints key if needed.
// ENDPOINTS.getTarget('nodeSize').range is [1, 30] usually.
// But BINDINGS default fallback is [0,1] if not found in mock ENDPOINTS?
// Let's define specific mock target range for clarity
window.UPB_ENDPOINTS.TARGETS = {
    nodeSize: { range: [0, 10] }
};
// Re-bind to ensure it picks up the mock (though simulate fresh load)
UPB.bind('token_estimate', 'nodeSize', { scale: 'linear', range: [0, 10] });

const atomResultRefined = UPB.evaluate(atomNode);
assert(Math.abs(atomResultRefined.nodeSize - 5.0) < 0.1, 'Atom (50) correctly maps to 5.0 in range [0,10]');


// 2. Transition: File Mode
// Files have massive token counts (e.g. 5000). 
// If ranges aren't updated, 5000 in [0, 100] gets clamped to MAX (10.0).
console.log('\n2. User switches to File Mode (Large Scale Values)');
const fileNodes = [
    { id: 'file1', token_estimate: 1000 },
    { id: 'file2', token_estimate: 5000 },
    { id: 'file3', token_estimate: 10000 }
];

// SIMULATE THE FIX:
// The fix in file-viz.js calculates new ranges and calls UPB.init() BEFORE apply.
console.log('[SYSTEM] Simulating file-viz.js logic refactor...');

// Logic extracted from file-viz.js fix:
const activeBindings = UPB.BINDINGS.defaultGraph._bindings;
const newRanges = {};
Object.keys(activeBindings).forEach(targetKey => {
    const bindings = activeBindings[targetKey];
    bindings.forEach(b => {
        const sourceKey = b.source;
        const values = fileNodes.map(n => n[sourceKey]);
        newRanges[sourceKey] = {
            min: Math.min(...values),
            max: Math.max(...values)
        };
    });
});
console.log(`[SYSTEM] Calculated New Ranges: ${JSON.stringify(newRanges)}`);
UPB.init(newRanges); // Apply new context

// 3. Execution: Apply to File Nodes
const updates = UPB.apply(fileNodes);

// 4. Validation
const midFileUpdate = updates.find(u => u.id === 'file2'); // 5000 tokens (Mid-range)
// Range is [1000, 10000]. 
// 5000 is roughly 44% of the way: (5000-1000)/(10000-1000) = 4000/9000 = 0.444
// Output in [0, 10] should be ~4.44
console.log(`[Validation] Checking File 2 (5000 tokens)... Visual Result: ${midFileUpdate.visuals.nodeSize}`);

const expected = 4.44;
const actual = midFileUpdate.visuals.nodeSize;
assert(Math.abs(actual - expected) < 0.1, `File 2 localized correctly (${actual.toFixed(2)} approx ${expected}). NOT clamped to max.`);

if (actual > 9.9) {
    console.error('❌ CRITICAL FAILURE: Value was clamped to MAX. Range update failed used Atom ranges.');
    failed++;
}

// 5. Semantic Check
// Verify that the new "Semantic Tags" are actually accessible in the runtime schema
console.log('\n3. Semantic Integrity Check');
const tokenSource = window.UPB_ENDPOINTS.getSource('token_estimate');
const sizeTarget = window.UPB_ENDPOINTS.getTarget('nodeSize');

console.log(`[Schema] Source tags: ${JSON.stringify(tokenSource.tags)}`);
console.log(`[Schema] Target tags: ${JSON.stringify(sizeTarget.tags)}`);

assert(tokenSource.tags.includes('structural'), 'Source has semantic tag "structural"');
assert(sizeTarget.tags.includes('geometric'), 'Target has semantic tag "geometric"');


console.log('\n---------------------------------------');
console.log(`SIMULATION STATUS: ${failed === 0 ? '✅ LOGICALLY CONSISTENT' : '❌ FAILED'}`);

if (failed > 0) process.exit(1);
