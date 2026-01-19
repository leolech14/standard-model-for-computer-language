window.process = window.process || { env: { NODE_ENV: "production" } };
window.global = window.global || window;
// UMD globals: THREE, ForceGraph3D, pako already loaded
// Three.js addons attach to THREE global: THREE.ConvexGeometry
const ConvexGeometry = THREE.ConvexGeometry;
// Note: Post-processing (bloom) removed for simplicity - addons not available in r149+ UMD builds

// COMPRESSED_PAYLOAD: Base64-encoded gzipped JSON data
const COMPRESSED_PAYLOAD = "{PAYLOAD}";

// --------------------------------------------------------------------
// WEB WORKER: JSON Parsing Only (Decompression in main thread)
// OPTIMIZED: Main thread uses already-loaded pako, no duplicate CDN fetch
// --------------------------------------------------------------------
const workerScript = `
        self.onmessage = function(e) {
            const jsonStr = e.data;
            try {
                self.postMessage({status: 'PARSING...'});
                const data = JSON.parse(jsonStr);
                self.postMessage({status: 'ANALYZING COSMOS...', result: data});
            } catch (err) {
                self.postMessage({error: err.message});
            }
        };
        `;

// Initialize Worker (minimal - no pako needed)
const blob = new Blob([workerScript], { type: 'application/javascript' });
const worker = new Worker(URL.createObjectURL(blob));

// OPTIMIZED: Decompress in main thread using already-loaded pako
function decompressPayload(payload) {
    // Update status
    const statusEl = document.getElementById('loader-status');
    if (statusEl) statusEl.innerText = 'DECOMPRESSING...';

    // 1. Decode Base64
    const charData = atob(payload);
    const binData = new Uint8Array(charData.length);
    for (let i = 0; i < charData.length; i++) {
        binData[i] = charData.charCodeAt(i);
    }

    // 2. Inflate using main thread's pako (already loaded from CDN)
    if (statusEl) statusEl.innerText = 'INFLATING...';
    const jsonStr = pako.inflate(binData, { to: 'string' });

    return jsonStr;
}

let FULL_GRAPH = null;
let Graph = null;
let CURRENT_DENSITY = 1; // Default: show all nodes
let ACTIVE_DATAMAPS = new Set();
let DATAMAP_CONFIGS = [];
let DATAMAP_INDEX = {};
let DATAMAP_UI = new Map();
let HOVERED_NODE = null;
let SELECTED_NODE_IDS = new Set();
let DATASET_KEY = 'default';
let GROUPS_STORAGE_KEY = 'collider_groups_default';
let GROUPS = [];
let ACTIVE_GROUP_ID = null;
let MARQUEE_ACTIVE = false;
let MARQUEE_START = null;
let MARQUEE_ADDITIVE = false;
let SELECTION_BOX = null;
let LAST_MARQUEE_END_TS = 0;
const SELECTION_HALO_GEOMETRY = new THREE.SphereGeometry(1, 12, 12);
const GROUP_HALO_GEOMETRY = new THREE.SphereGeometry(1, 12, 12);
let SPACE_PRESSED = false;
let IS_3D = true;
let DIMENSION_TRANSITION = false;
let STARFIELD = null;
let STARFIELD_OPACITY = 0;
let BLOOM_PASS = null;
let BLOOM_STRENGTH = 0;
let EDGE_MODE = 'gradient-file';  // DEFAULT: Show file regions with gradients!
let EDGE_DEFAULT_OPACITY = 0.2;
let DEFAULT_LINK_DISTANCE = null;
let EDGE_MODE_CONFIG = {
    resolution: {
        internal: '#4dd4ff',
        external: '#ff6b6b',
        unresolved: '#9aa0a6',
        unknown: '#666666'
    },
    weight: { hue_min: 210, hue_max: 50, chroma: null, saturation: 45, lightness: 42 },
    confidence: { hue_min: 20, hue_max: 120, chroma: null, saturation: 45, lightness: 44 },
    width: { base: 1.2, weight_scale: 2.5, confidence_scale: 1.5 },
    dim: { interfile_factor: 0.25 },
    opacity: 0.12
};
let EDGE_COLOR_CONFIG = {
    default: '#333333',
    calls: '#4dd4ff',
    contains: '#00ff9d',
    uses: '#ffb800',
    imports: '#9aa0a6',
    inherits: '#ff6b6b'
};
let FILE_COLOR_CONFIG = {
    strategy: 'golden-angle',
    angle: 137.5,
    chroma: null,
    saturation: 70,
    lightness: 50
};
let EDGE_RANGES = { weight: { min: 1, max: 1 }, confidence: { min: 1, max: 1 } };
let NODE_FILE_INDEX = new Map();
let NODE_COLOR_CONFIG = { tier: {}, ring: {}, unknown: '#666666' };
let FLOW_CONFIG = {};  // Flow mode settings from THE REMOTE CONTROL
let GRAPH_MODE = 'atoms'; // atoms | files | hybrid

// Layout stability: cache node positions to prevent re-randomization on toggles
let NODE_POSITION_CACHE = new Map();
let LAYOUT_FROZEN = false;  // When true, don't reheat simulation
let HINTS_ENABLED = true;   // Show mode toasts

let FILE_GRAPH = null;
let LAST_FILTER_SUMMARY = null;
let FILE_NODE_IDS = new Map();
let FILE_NODE_POSITIONS = new Map();
let EXPANDED_FILES = new Set();
let FILE_EXPAND_MODE = 'inline'; // inline | detach
let NODE_COLOR_MODE = 'tier';
let COLOR_TWEAKS = {
    hueShift: 0,
    chromaScale: 1,
    lightnessShift: 0
};
let VIS_FILTERS = {
    tiers: new Set(),
    rings: new Set(),
    roles: new Set(),
    edges: new Set(),
    families: new Set(),  // Atom families: LOG, DAT, ORG, EXE, EXT
    files: new Set(),     // File-based filtering
    layers: new Set(),    // D2_LAYER: Interface, Application, Core, Infrastructure, Test
    effects: new Set(),   // D6_EFFECT: Pure, Read, Write, ReadWrite
    edgeFamilies: new Set(), // Edge families: Structural, Dependency, Inheritance, Semantic, Temporal
    metadata: {
        showLabels: true,
        showFilePanel: true,
        showReportPanel: true,
        showEdges: true
    }
};
let SIDEBAR_STATE = {
    open: false,
    locked: false
};
let APPEARANCE_STATE = {
    nodeScale: 1,
    edgeOpacity: null,
    boundaryFill: null,
    boundaryWire: null,
    backgroundBase: null,
    backgroundBrightness: 1,
    fileLightness: null,
    clusterStrength: null,
    currentPreset: 'tier',
    colorMode: 'tier',
    sizeMode: 'fanout',
    edgeMode: 'type',
    // Amplifier: Power law exponent for visual contrast
    // γ=1 linear, γ>1 amplifies differences, γ<1 compresses
    amplifier: 1.0,
    amplifierTarget: 'all'  // 'all', 'edges', 'nodes', 'opacity'
};

// =====================================================================
// FILE BOUNDARY & SELECTION STATE (declared early to avoid TDZ errors)
// =====================================================================
let fileBoundaryMeshes = [];
let fileMode = false;
let fileVizMode = 'color'; // 'color' | 'hulls' | 'cluster'
let originalNodeColors = new Map();
let clusterForceActive = false;
let hullRedrawTimer = null;
let hullRedrawAttempts = 0;
const originalColorsForDim = new Map();
let flowMode = false; // Hoisted from line 7333

// ===================================
// RUNTIME REGISTRY: Centralized UI Management
// ===================================
class RuntimeRegistry {
    constructor() {
        this.items = new Map();
        this.commands = new Map();
    }

    register(id, item, options = {}) {
        // CASE 1: Registering a Command Identifier + Handler Function
        // e.g. REGISTRY.register('cmd-files', () => toggleFiles(), { desc: '...' })
        if (typeof item === 'function') {
            this.commands.set(id, { handler: item, options });

            // Auto-wire if DOM element exists with this ID
            // (Wait a tick in case DOM isn't ready, though usually called after DOM load)
            const btn = document.getElementById(id);
            if (btn) {
                // Using onclick ensures we don't stack listeners if re-registered.
                btn.onclick = (e) => {
                    item(e);
                };
                btn.setAttribute('data-command-id', id);
            }
            return;
        }

        // CASE 2: Registering a DOM Element directly
        // e.g. REGISTRY.register(btn) OR REGISTRY.register('my-btn', btnElement)

        let element = item;
        let elementId = id;

        // Overload: register(element) -> id comes from element.id
        if ((item instanceof Element) && arguments.length === 1) {
            element = item;
            elementId = element.id;
        }
        // Overload: register(id, element)
        else if (item instanceof Element) {
            element = item;
        }
        // Fallback: mismatched args
        else if (!element && (typeof id === 'object' && id instanceof Element)) {
            element = id;
            elementId = element.id;
        }

        if (!element || !element.setAttribute) {
            // console.warn('[Registry] Invalid element registration', id, item);
            return;
        }

        if (!elementId) {
            // console.warn('[Registry] Element has no ID', element);
            return;
        }

        this.items.set(elementId, element);
        element.setAttribute('data-registry-id', elementId);
    }

    get(id) {
        return this.items.get(id) || document.getElementById(id);
    }
}
const REGISTRY = new RuntimeRegistry();
window.REGISTRY = REGISTRY;

// =================================================================
// GLOBAL CONSTANTS (Hoisted for safety)
// =================================================================
const SELECTION_SIZE_MULT = 2.2;    // Make selected nodes BIGGER

// OKLCH PENDULUM COLOR OSCILLATOR - FULL RAINBOW EDITION
const PENDULUM = {
    // Pendulum 1: Controls HUE (FULL RAINBOW - dramatic cycling!)
    hue: {
        angle: Math.random() * Math.PI * 2,  // Random start
        velocity: 0,
        damping: 0.9995,      // Very low damping for perpetual motion
        gravity: 0.0008,     // Stronger gravity = faster oscillations
        length: 1.0,
        rotationSpeed: 0.8   // Base rotation speed
    },
    // Pendulum 2: Controls CHROMA (DRAMATIC VIBRANCE!)
    chroma: {
        angle: Math.random() * Math.PI * 2,
        velocity: 0,
        damping: 0.998,
        gravity: 0.0004,
        length: 1.0,
        center: 0.32,        // High saturation center
        amplitude: 0.08      // Vibrance variation
    },
    // Lightness for SELECTED nodes (SUBTLE RIPPLE)
    lightness: {
        phase: 0,
        speed: 0.02,
        center: 82,          // Bright center
        amplitude: 10        // Pulse amplitude
    },
    // Ripple effect
    ripple: {
        speed: 0.035,
        scale: 200
    },
    // Current hue (continuous rotation)
    currentHue: Math.random() * 360,
    lastTime: 0,
    running: false
};

// =====================================================================
// HOVER & SELECTION STATE (declared early to avoid TDZ errors)
// =====================================================================
let _lastHoveredNodeId = null;
const selectionOriginals = new Map();

// Amplification function using power law: f(x) = x^(1/γ) for γ values
// Maps normalized [0,1] input to amplified [0,1] output
function amplify(value, gamma = APPEARANCE_STATE.amplifier) {
    if (gamma === 1) return value;
    // Clamp to valid range
    const v = Math.max(0, Math.min(1, value));
    // Power law: v^(1/γ) - when γ>1, small diffs become larger
    // Using 1/γ so that higher slider = more amplification
    return Math.pow(v, 1 / gamma);
}

// Contrast amplification: expands values away from midpoint
function amplifyContrast(value, strength = APPEARANCE_STATE.amplifier) {
    if (strength === 1) return value;
    const v = Math.max(0, Math.min(1, value));
    // S-curve using tanh for smooth contrast expansion
    const centered = (v - 0.5) * 2;  // [-1, 1]
    const amplified = Math.tanh(centered * strength) / Math.tanh(strength);
    return (amplified + 1) / 2;  // Back to [0, 1]
}

// =====================================================================
// DATA MANAGER: Minimal runtime checks for deterministic self-test/parity
// =====================================================================

// =====================================================================
// COLOR ORCHESTRATOR: Centralized Color Intelligence System
// =====================================================================
// SINGLE SOURCE OF TRUTH for ALL colors in the visualization.
// Everything reads from here. OKLCH transforms apply here.
// =====================================================================
const ColorOrchestrator = {
    // =================================================================
    // BASE PALETTE: Semantic color definitions (before OKLCH transforms)
    // =================================================================
    palette: {
        // NODE DIMENSIONS - VIVID BASE COLORS (high chroma for bold schemes)
        tier: {
            'T0': { h: 142, c: 0.22, l: 0.68, label: 'Foundation', semantic: 'stable' },      // Green
            'T1': { h: 220, c: 0.22, l: 0.68, label: 'Domain', semantic: 'structure' },       // Blue
            'T2': { h: 330, c: 0.22, l: 0.68, label: 'Application', semantic: 'active' },     // Pink
            'UNKNOWN': { h: 0, c: 0.04, l: 0.50, label: 'Unknown', semantic: 'neutral' }      // Gray
        },
        family: {
            'LOG': { h: 220, c: 0.24, l: 0.65, label: 'Logic', semantic: 'computation' },     // Blue
            'DAT': { h: 142, c: 0.22, l: 0.68, label: 'Data', semantic: 'storage' },          // Green
            'ORG': { h: 280, c: 0.24, l: 0.62, label: 'Organization', semantic: 'structure' },// Purple
            'EXE': { h: 15, c: 0.26, l: 0.62, label: 'Execution', semantic: 'action' },       // Red
            'EXT': { h: 35, c: 0.22, l: 0.65, label: 'External', semantic: 'boundary' },      // Orange
            'UNKNOWN': { h: 0, c: 0.04, l: 0.50, label: 'Unknown', semantic: 'neutral' }
        },
        ring: {
            'DOMAIN': { h: 45, c: 0.22, l: 0.70, label: 'Domain', semantic: 'core' },         // Amber
            'APPLICATION': { h: 220, c: 0.20, l: 0.65, label: 'Application', semantic: 'logic' },
            'INFRASTRUCTURE': { h: 0, c: 0.04, l: 0.50, label: 'Infrastructure', semantic: 'foundation' },
            'PRESENTATION': { h: 280, c: 0.20, l: 0.65, label: 'Presentation', semantic: 'interface' },
            'TESTING': { h: 165, c: 0.14, l: 0.60, label: 'Testing', semantic: 'validation' },
            'UNKNOWN': { h: 0, c: 0.02, l: 0.40, label: 'Unknown', semantic: 'neutral' }
        },
        layer: {
            'PHYSICAL': { h: 220, c: 0.14, l: 0.62, label: 'Physical', semantic: 'concrete' },
            'VIRTUAL': { h: 142, c: 0.14, l: 0.65, label: 'Virtual', semantic: 'runtime' },
            'SEMANTIC': { h: 330, c: 0.14, l: 0.65, label: 'Semantic', semantic: 'meaning' }
        },
        // EDGE DIMENSIONS
        edgeType: {
            'calls': { h: 220, c: 0.12, l: 0.55, label: 'Calls', semantic: 'flow' },
            'contains': { h: 142, c: 0.12, l: 0.55, label: 'Contains', semantic: 'structure' },
            'uses': { h: 45, c: 0.12, l: 0.55, label: 'Uses', semantic: 'dependency' },
            'imports': { h: 280, c: 0.12, l: 0.50, label: 'Imports', semantic: 'external' },
            'inherits': { h: 330, c: 0.12, l: 0.55, label: 'Inherits', semantic: 'hierarchy' },
            'implements': { h: 165, c: 0.12, l: 0.55, label: 'Implements', semantic: 'contract' },
            'unknown': { h: 0, c: 0.02, l: 0.35, label: 'Unknown', semantic: 'neutral' }
        }
    },

    // =================================================================
    // OKLCH TRANSFORM STATE: Applied to all colors
    // =================================================================
    transform: {
        hueShift: 0,        // -180 to 180
        chromaScale: 1.0,   // 0 to 2
        lightnessShift: 0,  // -20 to 20 (percentage points)
        amplifier: 1.0      // Gamma for contrast
    },

    // =================================================================
    // INTERVAL MAPPINGS: For numeric data → color gradients
    // =================================================================
    intervals: {
        markov: {
            stops: [
                { value: 0.0, h: 220, c: 0.05, l: 0.35 },  // Low probability - dim blue
                { value: 0.3, h: 45, c: 0.12, l: 0.55 },   // Medium - amber
                { value: 0.7, h: 15, c: 0.18, l: 0.60 },   // High - orange
                { value: 1.0, h: 0, c: 0.22, l: 0.65 }     // Max - red hot
            ]
        },
        weight: {
            stops: [
                { value: 0.0, h: 220, c: 0.08, l: 0.40 },
                { value: 0.5, h: 180, c: 0.12, l: 0.50 },
                { value: 1.0, h: 142, c: 0.16, l: 0.60 }
            ]
        },
        confidence: {
            stops: [
                { value: 0.0, h: 0, c: 0.02, l: 0.30 },    // Low confidence - gray
                { value: 0.5, h: 45, c: 0.10, l: 0.50 },   // Medium - amber
                { value: 1.0, h: 142, c: 0.16, l: 0.65 }   // High - green
            ]
        }
    },

    // =================================================================
    // CORE API: Get color with transforms applied
    // =================================================================
    get(dimension, category) {
        const base = this.palette[dimension]?.[category];
        if (!base) return this._toHex({ h: 0, c: 0.02, l: 0.40 }); // Fallback gray

        return this._applyTransform(base);
    },

    // Get color for a numeric value using interval mapping
    getInterval(intervalName, value) {
        const interval = this.intervals[intervalName];
        if (!interval) return this._toHex({ h: 0, c: 0.02, l: 0.40 });

        const stops = interval.stops;
        const v = Math.max(0, Math.min(1, value));

        // Find surrounding stops
        let lower = stops[0];
        let upper = stops[stops.length - 1];

        for (let i = 0; i < stops.length - 1; i++) {
            if (v >= stops[i].value && v <= stops[i + 1].value) {
                lower = stops[i];
                upper = stops[i + 1];
                break;
            }
        }

        // Interpolate between stops
        const range = upper.value - lower.value;
        const t = range > 0 ? (v - lower.value) / range : 0;

        const interpolated = {
            h: lower.h + (upper.h - lower.h) * t,
            c: lower.c + (upper.c - lower.c) * t,
            l: lower.l + (upper.l - lower.l) * t
        };

        return this._applyTransform(interpolated);
    },

    // Get raw OKLCH values (for advanced use)
    getRaw(dimension, category) {
        return this.palette[dimension]?.[category] || { h: 0, c: 0.02, l: 0.40 };
    },

    // Get all categories for a dimension
    getCategories(dimension) {
        return Object.keys(this.palette[dimension] || {});
    },

    // Get label for a category
    getLabel(dimension, category) {
        return this.palette[dimension]?.[category]?.label || category;
    },

    // =================================================================
    // TRANSFORM CONTROLS: Update OKLCH state
    // =================================================================
    setTransform(key, value) {
        if (key in this.transform) {
            this.transform[key] = value;
            this._notifySubscribers('transform-change', { key, value });
        }
    },

    setAllTransforms(transforms) {
        Object.assign(this.transform, transforms);
        this._notifySubscribers('transform-change', transforms);
    },

    resetTransforms() {
        this.transform = {
            hueShift: 0,
            chromaScale: 1.0,
            lightnessShift: 0,
            amplifier: 1.0
        };
        this._notifySubscribers('transform-change', this.transform);
    },

    // =================================================================
    // INTERNAL: Apply OKLCH transforms and convert to hex
    // =================================================================
    _applyTransform(oklch) {
        const t = this.transform;

        // Apply transforms
        let h = (oklch.h + t.hueShift + 360) % 360;
        let c = Math.max(0, Math.min(0.4, oklch.c * t.chromaScale));
        let l = Math.max(0, Math.min(1, oklch.l + t.lightnessShift / 100));

        // Apply amplifier to chroma for contrast
        if (t.amplifier !== 1) {
            c = Math.pow(c / 0.4, 1 / t.amplifier) * 0.4;
        }

        return this._toHex({ h, c, l });
    },

    _toHex(oklch) {
        // OKLCH to sRGB conversion (simplified)
        // Using CSS color conversion would be ideal, but this approximation works
        const { h, c, l } = oklch;

        // Convert OKLCH to approximate RGB
        const hRad = h * Math.PI / 180;
        const a = c * Math.cos(hRad);
        const b = c * Math.sin(hRad);

        // Simplified OKLab to linear RGB (approximate)
        const L = l;
        const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
        const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
        const s_ = L - 0.0894841775 * a - 1.2914855480 * b;

        const l3 = l_ * l_ * l_;
        const m3 = m_ * m_ * m_;
        const s3 = s_ * s_ * s_;

        let r = +4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3;
        let g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3;
        let bl = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3;

        // Clamp and convert to sRGB
        const toSRGB = (x) => {
            x = Math.max(0, Math.min(1, x));
            return x <= 0.0031308 ? 12.92 * x : 1.055 * Math.pow(x, 1 / 2.4) - 0.055;
        };

        r = Math.round(toSRGB(r) * 255);
        g = Math.round(toSRGB(g) * 255);
        bl = Math.round(toSRGB(bl) * 255);

        r = Math.max(0, Math.min(255, r));
        g = Math.max(0, Math.min(255, g));
        bl = Math.max(0, Math.min(255, bl));

        return '#' + [r, g, bl].map(x => x.toString(16).padStart(2, '0')).join('');
    },

    // =================================================================
    // REACTIVE SUBSCRIPTIONS
    // =================================================================
    _subscribers: [],

    subscribe(callback) {
        this._subscribers.push(callback);
        return () => {
            this._subscribers = this._subscribers.filter(cb => cb !== callback);
        };
    },

    _notifySubscribers(event, data) {
        this._subscribers.forEach(cb => cb(event, data));
    },

    // =================================================================
    // DEBUG: Log current state
    // =================================================================
    debug() {
        console.log('[ColorOrchestrator] Transform state:', this.transform);
        console.log('[ColorOrchestrator] Palette dimensions:', Object.keys(this.palette));
        console.log('[ColorOrchestrator] Interval mappings:', Object.keys(this.intervals));
    }
};

// Global alias for convenience
const Color = ColorOrchestrator;

// =====================================================================
// LEGEND MANAGER: Counts + Visibility + Extraction
// ALL COLORS come from ColorOrchestrator - no duplicates
// =====================================================================
class LegendManager {
    constructor() {
        // Dimension metadata (NO COLORS - those live in ColorOrchestrator)
        this.dimensions = {
            tier: {
                name: 'TIERS',
                icon: '◐',
                extract: (node) => typeof getNodeTier === 'function' ? getNodeTier(node) : 'UNKNOWN'
            },
            family: {
                name: 'FAMILIES',
                icon: '⬡',
                extract: (node) => typeof getNodeAtomFamily === 'function' ? getNodeAtomFamily(node) : 'UNKNOWN'
            },
            ring: {
                name: 'RINGS',
                icon: '◎',
                extract: (node) => typeof getNodeRing === 'function' ? getNodeRing(node) : 'UNKNOWN'
            },
            layer: {
                name: 'LAYERS',
                icon: '☰',
                extract: (node) => (node.layer || node.dimensions?.D2_LAYER || 'Unknown').toUpperCase()
            },
            effect: {
                name: 'EFFECTS',
                icon: '⚡',
                extract: (node) => (node.effect || node.dimensions?.D6_EFFECT || 'Unknown')
            },
            edgeType: {
                name: 'EDGE TYPES',
                icon: '→',
                extract: (link) => (link.edge_type || link.type || 'unknown').toLowerCase()
            },
            edgeFamily: {
                name: 'EDGE FAMILIES',
                icon: '⇢',
                extract: (link) => (link.family || 'Dependency')
            }
        };

        this.counts = {};      // Computed counts per dimension
        this._subscribers = [];
    }

    init(nodes, links) {
        this._computeCounts(nodes, links);
        return this;
    }

    _computeCounts(nodes, links) {
        this.counts = {};

        // Node dimensions
        ['tier', 'family', 'ring', 'layer'].forEach(dim => {
            const extract = this.dimensions[dim]?.extract;
            if (!extract) return;
            this.counts[dim] = {};
            (nodes || []).forEach(node => {
                const cat = extract(node);
                this.counts[dim][cat] = (this.counts[dim][cat] || 0) + 1;
            });
        });

        // Edge dimension
        const edgeExtract = this.dimensions.edgeType?.extract;
        if (edgeExtract) {
            this.counts.edgeType = {};
            (links || []).forEach(link => {
                const cat = edgeExtract(link);
                this.counts.edgeType[cat] = (this.counts.edgeType[cat] || 0) + 1;
            });
        }

        console.log('[Legend] Counts:', this.counts);
    }

    // Get legend data - COLORS FROM ColorOrchestrator
    getLegendData(dimension) {
        const counts = this.counts[dimension] || {};

        return Object.keys(counts)
            .filter(cat => counts[cat] > 0)
            .sort((a, b) => (counts[b] || 0) - (counts[a] || 0))
            .map(cat => ({
                id: cat,
                label: Color.getLabel(dimension, cat),  // FROM ColorOrchestrator
                color: Color.get(dimension, cat),       // FROM ColorOrchestrator (with transforms!)
                count: counts[cat] || 0,
                dimension: dimension
            }));
    }

    // Get color - DELEGATES to ColorOrchestrator
    getColor(dimension, category) {
        return Color.get(dimension, category);
    }

    subscribe(callback) {
        this._subscribers.push(callback);
        return () => { this._subscribers = this._subscribers.filter(cb => cb !== callback); };
    }

    _notifySubscribers(event, data) {
        this._subscribers.forEach(cb => cb(event, data));
    }
}

// Global legend manager instance
let Legend = null;

// ═══════════════════════════════════════════════════════════════════════════
// DATAMANAGER: Single Gate for ALL Data Access
// ═══════════════════════════════════════════════════════════════════════════
// This is THE source of truth. All data flows through here.
// NO direct access to FULL_GRAPH or Graph.graphData() - use DM instead.
// ═══════════════════════════════════════════════════════════════════════════
class DataManager {
    constructor() {
        // ═══════════════════════════════════════════════════════════════
        // RAW DATA (immutable after init)
        // ═══════════════════════════════════════════════════════════════
        this.raw = {
            nodes: [],
            links: [],
            fileBoundaries: [],
            markov: {},
            kpis: {},
            meta: {}
        };

        // ═══════════════════════════════════════════════════════════════
        // ANALYTICS DATA (all 30+ Collider sections)
        // ═══════════════════════════════════════════════════════════════
        this.analytics = {
            // Structural metrics
            counts: {},
            stats: {},
            coverage: {},
            performance: {},

            // Classification & discovery
            classification: {},
            auto_discovery: {},
            ecosystem_discovery: {},

            // Architecture & dependencies
            dependencies: {},
            architecture: {},
            topology: {},

            // Flow analysis
            execution_flow: {},
            data_flow: {},
            knots: {},

            // Health & recommendations
            warnings: [],
            recommendations: [],
            theory_completeness: {},

            // Distributions
            distributions: {},
            edge_types: {},

            // RPBL profile (Responsibility, Purity, Boundary, Lifecycle)
            rpbl_profile: {},
            purpose_field: {},

            // Special nodes
            top_hubs: [],
            orphans_list: [],

            // Files
            files: [],

            // Semantic analysis
            semantics: {},
            llm_enrichment: {},

            // Brain download (the full report)
            brain_download: {},

            // Raw Config & Physics (for token-driven features)
            physics: {},
            config: {}
        };

        // ═══════════════════════════════════════════════════════════════
        // INDEXES (O(1) lookups - built once)
        // ═══════════════════════════════════════════════════════════════
        this.index = {
            nodeById: new Map(),           // id → node
            nodesByTier: new Map(),        // tier → [nodes]
            nodesByFamily: new Map(),      // family → [nodes]
            nodesByRing: new Map(),        // ring → [nodes]
            nodesByLayer: new Map(),       // layer (D2_LAYER) → [nodes]
            nodesByEffect: new Map(),      // effect (D6_EFFECT) → [nodes]
            nodesByFile: new Map(),        // fileIdx → [nodes]
            edgesBySource: new Map(),      // nodeId → [edges from]
            edgesByTarget: new Map(),      // nodeId → [edges to]
            edgeByKey: new Map(),          // "src|tgt" → edge
            fileByIndex: new Map(),        // idx → fileBoundary
            markovBySource: new Map()      // nodeId → sorted edges by weight
        };

        // ═══════════════════════════════════════════════════════════════
        // CACHED AGGREGATIONS (computed once, invalidated on filter)
        // ═══════════════════════════════════════════════════════════════
        this.cache = {
            tierCounts: null,
            familyCounts: null,
            ringCounts: null,
            edgeTypeCounts: null,
            edgeRanges: null
        };

        // ═══════════════════════════════════════════════════════════════
        // CURRENT STATE (filtered view)
        // ═══════════════════════════════════════════════════════════════
        this.filtered = {
            nodes: [],
            links: []
        };

        // Legend manager
        this.legend = new LegendManager();

        // ═══════════════════════════════════════════════════════════════
        // COLOR SYSTEM: Single gate for all color access
        // ═══════════════════════════════════════════════════════════════
        this.color = ColorOrchestrator;  // Reference to ColorOrchestrator
    }

    // ═══════════════════════════════════════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════════════════════════════════════
    init(data) {
        // Store raw data
        this.raw.nodes = Array.isArray(data?.nodes) ? data.nodes : [];
        this.raw.links = Array.isArray(data?.links) ? data.links : [];
        this.raw.fileBoundaries = Array.isArray(data?.file_boundaries) ? data.file_boundaries : [];
        this.raw.markov = data?.markov || {};
        this.raw.kpis = data?.kpis || {};
        this.raw.meta = data?.meta || {};
        this.raw.physics = data?.physics || {};
        this.raw.config = data?.config || {};

        // Build all indexes
        this._buildAllIndexes();

        // Initialize legend
        this.legend.init(this.raw.nodes, this.raw.links);
        Legend = this.legend;

        console.log('%c[DM] Initialized', 'color: #4ade80; font-weight: bold',
            `${this.raw.nodes.length} nodes, ${this.raw.links.length} edges, ${this.raw.fileBoundaries.length} files`);

        return this;
    }

    _buildAllIndexes() {
        this._buildNodeIndex();
        this._buildSemanticIndexes();
        this._buildEdgeIndexes();
        this._buildFileIndex();
        this._buildMarkovIndex();
        this._invalidateCache();
    }

    _buildNodeIndex() {
        this.index.nodeById.clear();
        for (const node of this.raw.nodes) {
            if (node?.id) {
                this.index.nodeById.set(node.id, node);
            }
        }
    }

    _buildSemanticIndexes() {
        this.index.nodesByTier.clear();
        this.index.nodesByFamily.clear();
        this.index.nodesByRing.clear();
        this.index.nodesByLayer.clear();
        this.index.nodesByEffect.clear();
        this.index.nodesByFile.clear();

        for (const node of this.raw.nodes) {
            if (!node) continue;

            // Tier index
            const tier = this._getNodeTier(node);
            if (!this.index.nodesByTier.has(tier)) {
                this.index.nodesByTier.set(tier, []);
            }
            this.index.nodesByTier.get(tier).push(node);

            // Family index
            const family = this._getNodeFamily(node);
            if (!this.index.nodesByFamily.has(family)) {
                this.index.nodesByFamily.set(family, []);
            }
            this.index.nodesByFamily.get(family).push(node);

            // Ring index
            const ring = this._getNodeRing(node);
            if (!this.index.nodesByRing.has(ring)) {
                this.index.nodesByRing.set(ring, []);
            }
            this.index.nodesByRing.get(ring).push(node);

            // Layer index (D2_LAYER)
            const layer = this._getNodeLayer(node);
            if (!this.index.nodesByLayer.has(layer)) {
                this.index.nodesByLayer.set(layer, []);
            }
            this.index.nodesByLayer.get(layer).push(node);

            // Effect index (D6_EFFECT)
            const effect = this._getNodeEffect(node);
            if (!this.index.nodesByEffect.has(effect)) {
                this.index.nodesByEffect.set(effect, []);
            }
            this.index.nodesByEffect.get(effect).push(node);

            // File index
            const fileIdx = node.fileIdx ?? -1;
            if (fileIdx >= 0) {
                if (!this.index.nodesByFile.has(fileIdx)) {
                    this.index.nodesByFile.set(fileIdx, []);
                }
                this.index.nodesByFile.get(fileIdx).push(node);
            }
        }
    }

    _buildEdgeIndexes() {
        this.index.edgesBySource.clear();
        this.index.edgesByTarget.clear();
        this.index.edgeByKey.clear();

        for (const link of this.raw.links) {
            const srcId = this._endpointId(link, 'source');
            const tgtId = this._endpointId(link, 'target');

            if (srcId) {
                if (!this.index.edgesBySource.has(srcId)) {
                    this.index.edgesBySource.set(srcId, []);
                }
                this.index.edgesBySource.get(srcId).push(link);
            }

            if (tgtId) {
                if (!this.index.edgesByTarget.has(tgtId)) {
                    this.index.edgesByTarget.set(tgtId, []);
                }
                this.index.edgesByTarget.get(tgtId).push(link);
            }

            if (srcId && tgtId) {
                this.index.edgeByKey.set(`${srcId}|${tgtId}`, link);
            }
        }
    }

    _buildFileIndex() {
        this.index.fileByIndex.clear();
        for (let i = 0; i < this.raw.fileBoundaries.length; i++) {
            this.index.fileByIndex.set(i, this.raw.fileBoundaries[i]);
        }
    }

    _buildMarkovIndex() {
        this.index.markovBySource.clear();
        // Group edges by source and sort by markov weight
        for (const link of this.raw.links) {
            const srcId = this._endpointId(link, 'source');
            const mw = link.markov_weight || 0;
            if (srcId && mw > 0) {
                if (!this.index.markovBySource.has(srcId)) {
                    this.index.markovBySource.set(srcId, []);
                }
                this.index.markovBySource.get(srcId).push(link);
            }
        }
        // Sort each list by markov weight descending
        for (const [srcId, edges] of this.index.markovBySource) {
            edges.sort((a, b) => (b.markov_weight || 0) - (a.markov_weight || 0));
        }
    }

    _invalidateCache() {
        this.cache.tierCounts = null;
        this.cache.familyCounts = null;
        this.cache.ringCounts = null;
        this.cache.edgeTypeCounts = null;
        this.cache.edgeRanges = null;
    }

    // ═══════════════════════════════════════════════════════════════════
    // HELPER FUNCTIONS (internal)
    // ═══════════════════════════════════════════════════════════════════
    _endpointId(link, side) {
        if (!link) return '';
        let value = link[side];
        if (value && typeof value === 'object') value = value.id;
        return (value === undefined || value === null) ? '' : String(value).trim();
    }

    _getNodeTier(node) {
        if (!node) return 'UNKNOWN';
        if (node.tier) return node.tier;
        if (node.layer === 'foundation') return 'T0';
        if (node.layer === 'domain') return 'T1';
        if (node.layer === 'application') return 'T2';
        return 'UNKNOWN';
    }

    _getNodeFamily(node) {
        if (!node) return 'EXT';
        const family = (node.atom_family || node.family || 'EXT').toUpperCase();
        return ['LOG', 'DAT', 'ORG', 'EXE', 'EXT'].includes(family) ? family : 'EXT';
    }

    _getNodeRing(node) {
        if (!node) return 'UNKNOWN';
        const ring = (node.ring || node.layer || 'UNKNOWN').toUpperCase();
        return ring;
    }

    _getNodeLayer(node) {
        if (!node) return 'Unknown';
        return node.layer || node.dimensions?.D2_LAYER || 'Unknown';
    }

    _getNodeEffect(node) {
        if (!node) return 'Unknown';
        return node.effect || node.dimensions?.D6_EFFECT || 'Unknown';
    }

    // ═══════════════════════════════════════════════════════════════════
    // RAW DATA ACCESSORS (replaces FULL_GRAPH.*)
    // ═══════════════════════════════════════════════════════════════════
    getNodes() {
        return this.raw.nodes;
    }

    getLinks() {
        return this.raw.links;
    }

    getFileBoundaries() {
        return this.raw.fileBoundaries;
    }

    getMarkov() {
        return this.raw.markov;
    }

    getKpis() {
        return this.raw.kpis;
    }

    getMeta() {
        return this.raw.meta;
    }

    // ═══════════════════════════════════════════════════════════════════
    // INDEXED LOOKUPS (O(1))
    // ═══════════════════════════════════════════════════════════════════
    getNode(id) {
        return this.index.nodeById.get(id) || null;
    }

    getNodesByTier(tier) {
        return this.index.nodesByTier.get(tier) || [];
    }

    getNodesByFamily(family) {
        return this.index.nodesByFamily.get(family) || [];
    }

    getNodesByRing(ring) {
        return this.index.nodesByRing.get(ring) || [];
    }

    getNodesByFile(fileIdx) {
        return this.index.nodesByFile.get(fileIdx) || [];
    }

    getEdgesFrom(nodeId) {
        return this.index.edgesBySource.get(nodeId) || [];
    }

    getEdgesTo(nodeId) {
        return this.index.edgesByTarget.get(nodeId) || [];
    }

    getEdgeBetween(srcId, tgtId) {
        return this.index.edgeByKey.get(`${srcId}|${tgtId}`) || null;
    }

    getFile(idx) {
        return this.index.fileByIndex.get(idx) || null;
    }

    getTopMarkovEdges(nodeId, k = 5) {
        const edges = this.index.markovBySource.get(nodeId) || [];
        return edges.slice(0, k);
    }

    isHighEntropyNode(nodeId) {
        const highEntropy = this.raw.markov?.high_entropy_nodes || [];
        return highEntropy.some(h => h.node === nodeId);
    }

    // ═══════════════════════════════════════════════════════════════════
    // FILTERED DATA (replaces Graph.graphData())
    // ═══════════════════════════════════════════════════════════════════
    setFiltered(nodes, links) {
        this.filtered.nodes = nodes || [];
        this.filtered.links = links || [];
    }

    getVisibleNodes() {
        // Return filtered if set, otherwise return from Graph
        if (this.filtered.nodes.length > 0) {
            return this.filtered.nodes;
        }
        // Fallback to Graph.graphData() during transition
        return (Graph && Graph.graphData) ? (Graph.graphData().nodes || []) : [];
    }

    getVisibleLinks() {
        if (this.filtered.links.length > 0) {
            return this.filtered.links;
        }
        return (Graph && Graph.graphData) ? (Graph.graphData().links || []) : [];
    }

    // ═══════════════════════════════════════════════════════════════════
    // AGGREGATIONS (cached)
    // ═══════════════════════════════════════════════════════════════════
    getTierCounts() {
        if (!this.cache.tierCounts) {
            this.cache.tierCounts = new Map();
            for (const [tier, nodes] of this.index.nodesByTier) {
                this.cache.tierCounts.set(tier, nodes.length);
            }
        }
        return this.cache.tierCounts;
    }

    getFamilyCounts() {
        if (!this.cache.familyCounts) {
            this.cache.familyCounts = new Map();
            for (const [family, nodes] of this.index.nodesByFamily) {
                this.cache.familyCounts.set(family, nodes.length);
            }
        }
        return this.cache.familyCounts;
    }

    getRingCounts() {
        if (!this.cache.ringCounts) {
            this.cache.ringCounts = new Map();
            for (const [ring, nodes] of this.index.nodesByRing) {
                this.cache.ringCounts.set(ring, nodes.length);
            }
        }
        return this.cache.ringCounts;
    }

    getEdgeTypeCounts() {
        if (!this.cache.edgeTypeCounts) {
            this.cache.edgeTypeCounts = new Map();
            for (const link of this.raw.links) {
                const type = link.edge_type || link.type || 'unknown';
                this.cache.edgeTypeCounts.set(type, (this.cache.edgeTypeCounts.get(type) || 0) + 1);
            }
        }
        return this.cache.edgeTypeCounts;
    }

    getLayerCounts() {
        if (!this.cache.layerCounts) {
            this.cache.layerCounts = new Map();
            for (const [layer, nodes] of this.index.nodesByLayer) {
                this.cache.layerCounts.set(layer, nodes.length);
            }
        }
        return this.cache.layerCounts;
    }

    getEffectCounts() {
        if (!this.cache.effectCounts) {
            this.cache.effectCounts = new Map();
            for (const [effect, nodes] of this.index.nodesByEffect) {
                this.cache.effectCounts.set(effect, nodes.length);
            }
        }
        return this.cache.effectCounts;
    }

    getEdgeFamilyCounts() {
        if (!this.cache.edgeFamilyCounts) {
            this.cache.edgeFamilyCounts = new Map();
            for (const link of this.raw.links) {
                const family = link.family || 'Dependency';
                this.cache.edgeFamilyCounts.set(family, (this.cache.edgeFamilyCounts.get(family) || 0) + 1);
            }
        }
        return this.cache.edgeFamilyCounts;
    }

    getEdgeRanges() {
        if (!this.cache.edgeRanges) {
            let minW = Infinity, maxW = -Infinity;
            let minC = Infinity, maxC = -Infinity;
            for (const link of this.raw.links) {
                const w = link.weight ?? 1;
                const c = link.confidence ?? 1;
                if (w < minW) minW = w;
                if (w > maxW) maxW = w;
                if (c < minC) minC = c;
                if (c > maxC) maxC = c;
            }
            this.cache.edgeRanges = {
                weight: { min: minW === Infinity ? 0 : minW, max: maxW === -Infinity ? 1 : maxW },
                confidence: { min: minC === Infinity ? 0 : minC, max: maxC === -Infinity ? 1 : maxC }
            };
        }
        return this.cache.edgeRanges;
    }

    // ═══════════════════════════════════════════════════════════════════
    // SELF-TEST
    // ═══════════════════════════════════════════════════════════════════
    selfTest() {
        const errors = [];
        const warnings = [];
        const seenIds = new Set();

        for (const node of this.raw.nodes) {
            if (!node?.id) {
                errors.push('Node missing id');
                continue;
            }
            if (seenIds.has(node.id)) {
                errors.push(`Duplicate node id: ${node.id}`);
                continue;
            }
            seenIds.add(node.id);
        }

        for (const link of this.raw.links) {
            const srcId = this._endpointId(link, 'source');
            const tgtId = this._endpointId(link, 'target');
            if (srcId && !this.index.nodeById.has(srcId)) {
                warnings.push(`Edge source not in graph: ${srcId}`);
            }
            if (tgtId && !this.index.nodeById.has(tgtId)) {
                warnings.push(`Edge target not in graph: ${tgtId}`);
            }
        }

        // Index integrity checks
        const indexChecks = [
            ['nodeById', this.index.nodeById.size, this.raw.nodes.length],
            ['nodesByTier total', [...this.index.nodesByTier.values()].flat().length, this.raw.nodes.length],
            ['edgesBySource total', [...this.index.edgesBySource.values()].flat().length, this.raw.links.length],
        ];

        for (const [name, actual, expected] of indexChecks) {
            if (actual !== expected) {
                warnings.push(`Index ${name}: ${actual} vs expected ${expected}`);
            }
        }

        const status = errors.length === 0 ? '✅ PASS' : '❌ FAIL';
        console.log(`%c[DM] Self-Test: ${status}`, errors.length === 0 ? 'color: #4ade80; font-weight: bold' : 'color: #f87171; font-weight: bold');
        console.log(`  Raw: ${this.raw.nodes.length} nodes, ${this.raw.links.length} edges, ${this.raw.fileBoundaries.length} files`);
        console.log(`  Indexes: nodeById=${this.index.nodeById.size}, tiers=${this.index.nodesByTier.size}, families=${this.index.nodesByFamily.size}`);
        console.log(`  Edges: bySource=${this.index.edgesBySource.size}, byTarget=${this.index.edgesByTarget.size}, markov=${this.index.markovBySource.size}`);

        if (errors.length > 0) console.error('[DM] Errors:', errors);
        if (warnings.length > 0) {
            console.warn('[DM] Warnings:', warnings.slice(0, 5));
            if (warnings.length > 5) console.warn(`  ... and ${warnings.length - 5} more`);
        }

        return { errors, warnings, pass: errors.length === 0 };
    }
}

function runDmParity(dm, data) {
    if (!dm) return;
    const checks = [];
    const rawNodes = Array.isArray(data?.nodes) ? data.nodes.length : 0;
    const rawEdges = Array.isArray(data?.links) ? data.links.length : 0;
    const dmNodes = dm.raw.nodes.length;
    const dmEdges = dm.raw.links.length;

    checks.push({ name: 'Node count', dm: dmNodes, old: rawNodes, pass: dmNodes === rawNodes });
    checks.push({ name: 'Edge count', dm: dmEdges, old: rawEdges, pass: dmEdges === rawEdges });
    checks.push({ name: 'Node index size', dm: dm.index.nodeById.size, old: rawNodes, pass: dm.index.nodeById.size === rawNodes });

    const rawMarkovEdges = (Array.isArray(data?.links) ? data.links : [])
        .filter(l => (l?.markov_weight || 0) > 0).length;
    const dmMarkovEdges = (Array.isArray(dm.raw.links) ? dm.raw.links : [])
        .filter(l => (l?.markov_weight || 0) > 0).length;
    checks.push({ name: 'Markov edges', dm: dmMarkovEdges, old: rawMarkovEdges, pass: dmMarkovEdges === rawMarkovEdges });

    const allPass = checks.every(c => c.pass);
    const style = allPass ? 'color: #4ade80; font-weight: bold' : 'color: #f87171; font-weight: bold';
    console.log(`%c[DM Parity] ${allPass ? '✅ ALL PASS' : '❌ MISMATCH'}`, style);
    checks.forEach(c => {
        const icon = c.pass ? '✓' : '✗';
        console.log(`  ${icon} ${c.name}: DM=${c.dm}, Raw=${c.old}`);
    });
}

let DM = null;

// =====================================================================
// FLOATING PANEL CONTROL SYSTEM
// =====================================================================
let _activePanelId = null;

function openPanel(panelId) {
    const panel = document.getElementById('panel-' + panelId);
    const btn = document.getElementById('cmd-' + panelId);

    // Close any already-open panel
    if (_activePanelId && _activePanelId !== panelId) {
        closePanel(_activePanelId);
    }

    if (panel) {
        panel.classList.add('visible');
        // Short delay for transform animation
        setTimeout(() => { panel.style.opacity = '1'; }, 10);
    }
    if (btn) btn.classList.add('active');
    _activePanelId = panelId;

    // UI_ACTIVE: "Quiet the universe" - dim graph when panel opens
    document.body.classList.add('ui-active');

    // Also dim starfield via JS (CSS filter doesn't reach WebGL)
    if (typeof STARFIELD !== 'undefined' && STARFIELD && STARFIELD.material) {
        STARFIELD.material.opacity = STARFIELD_OPACITY * 0.3;
    }
}

function closePanel(panelId) {
    const panel = document.getElementById('panel-' + panelId);
    const btn = document.getElementById('cmd-' + panelId);
    if (panel) {
        panel.classList.remove('visible');
    }
    if (btn) btn.classList.remove('active');
    if (_activePanelId === panelId) _activePanelId = null;

    // UI_ACTIVE: Restore universe when all panels closed
    if (!_activePanelId) {
        document.body.classList.remove('ui-active');

        // Restore starfield opacity
        if (typeof STARFIELD !== 'undefined' && STARFIELD && STARFIELD.material) {
            const starsBtn = document.getElementById('btn-stars');
            const starsVisible = starsBtn && starsBtn.classList.contains('active');
            STARFIELD.material.opacity = starsVisible ? STARFIELD_OPACITY : 0;
        }
    }
}

function togglePanel(panelId) {
    const panel = document.getElementById('panel-' + panelId);
    if (panel && panel.classList.contains('visible')) {
        closePanel(panelId);
    } else {
        openPanel(panelId);
    }
}

// Wire up command bar and panel controls
function initCommandBar() {
    // Command bar buttons
    const cmdBtns = {
        'cmd-view': 'view',
        'cmd-filter': 'filter',
        'cmd-style': 'style',
        'cmd-settings': 'settings'
    };

    Object.entries(cmdBtns).forEach(([btnId, panelId]) => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.addEventListener('click', () => togglePanel(panelId));
        }
    });

    // Settings panel: Oval margin slider (debounced - apply 300ms after release)
    const ovalSlider = document.getElementById('oval-margin-slider');
    const ovalValue = document.getElementById('oval-margin-value');
    let ovalDebounceTimer = null;
    if (ovalSlider) {
        // Update display value immediately
        ovalSlider.addEventListener('input', (e) => {
            if (ovalValue) ovalValue.textContent = e.target.value + '%';
        });
        // Apply actual change only after 300ms pause (on mouseup/touchend)
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

    // Oval debug toggle
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

    // ═══════════════════════════════════════════════════════════════════
    // STYLE PANEL SLIDERS - Connected to appearance system
    // ═══════════════════════════════════════════════════════════════════

    // Node Size Slider
    const nodeSizeSlider = document.getElementById('node-size-slider');
    const nodeSizeValue = document.getElementById('node-size-value');
    if (nodeSizeSlider) {
        nodeSizeSlider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            if (nodeSizeValue) nodeSizeValue.textContent = val.toFixed(1) + 'x';
            APPEARANCE_STATE.nodeScale = val;
            if (Graph) {
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
            APPEARANCE_STATE.edgeOpacity = val / 100;
            if (typeof applyEdgeMode === 'function') applyEdgeMode();
        });
    }

    // Density Slider (filter panel duplicate)
    const densitySlider2 = document.getElementById('density-slider2');
    const densityValue2 = document.getElementById('density-value2');
    if (densitySlider2) {
        densitySlider2.addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            if (densityValue2) densityValue2.textContent = val + '%';
            CURRENT_DENSITY = val;
            refreshGraph();
        });
    }

    // Toggle switches
    document.querySelectorAll('.toggle-switch').forEach(toggle => {
        toggle.addEventListener('click', () => {
            toggle.classList.toggle('active');
        });
    });

    // Segmented controls
    document.querySelectorAll('.segmented-control').forEach(control => {
        control.querySelectorAll('.segment').forEach(segment => {
            segment.addEventListener('click', () => {
                control.querySelectorAll('.segment').forEach(s => s.classList.remove('active'));
                segment.classList.add('active');

                // Handle dimension change
                if (control.id === 'dim-control') {
                    const dim = segment.dataset.dim;
                    if (dim === '2') {
                        IS_3D = false;
                        if (Graph) Graph.numDimensions(2);
                    } else {
                        IS_3D = true;
                        if (Graph) Graph.numDimensions(3);
                    }
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
                        EDGE_MODE = mode;
                        if (typeof applyEdgeMode === 'function') applyEdgeMode();
                    }
                }

                // Handle panel layout
                if (control.id === 'layout-control') {
                    const layout = segment.dataset.layout;
                    if (layout) {
                        document.body.setAttribute('data-layout', layout);
                        console.log('[Layout] Switched to:', layout);
                    }
                }
            });
        });
    });

    // ═══════════════════════════════════════════════════════════════════
    // COMMAND BAR DIRECT ACTIONS (no proxy clicks - call functions directly)
    // ═══════════════════════════════════════════════════════════════════

    // File mode toggle
    REGISTRY.register('cmd-files2', () => {
        if (typeof setFileModeState === 'function') {
            const newState = !fileMode;
            setFileModeState(newState);
            // Visual feedback is handled by setFileModeState, but we toggle active here for instant response
            const btn = document.getElementById('cmd-files2');
            if (btn) btn.classList.toggle('active', newState);
        } else {
            console.warn('setFileModeState function missing');
        }
    }, { desc: 'Toggle File Boundaries Mode' });

    // Flow mode toggle
    REGISTRY.register('cmd-flow2', () => {
        if (typeof toggleFlowMode === 'function') {
            toggleFlowMode();
            // Visual feedback usually managed by toggle function
            const btn = document.getElementById('cmd-flow2');
            if (btn) btn.classList.toggle('active', flowMode);
        }
    }, { desc: 'Toggle Flow Mode' });

    // 3D toggle
    REGISTRY.register('cmd-3d', () => {
        if (typeof toggleDimensions === 'function') {
            toggleDimensions();
        } else {
            // Direct implementation fallback
            IS_3D = !IS_3D;
            if (Graph) Graph.numDimensions(IS_3D ? 3 : 2);
            const btnDim = document.getElementById('btn-dimensions');
            if (btnDim) btnDim.textContent = IS_3D ? '2D' : '3D';
        }
        const btn = document.getElementById('cmd-3d');
        if (btn) btn.classList.toggle('active', IS_3D);

        // Update dim-control if exists
        const dimControl = document.getElementById('dim-control');
        if (dimControl) {
            dimControl.querySelectorAll('.segment').forEach(s => {
                s.classList.toggle('active', s.dataset.dim === (IS_3D ? '3' : '2'));
            });
        }
    }, { desc: 'Toggle 2D/3D View' });

    console.log('[CommandBar] Initialized with direct function calls');
}

// Build chip buttons for filter groups
function buildChipGroup(containerId, items, stateSet, onUpdate) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    // "ALL" chip
    const allChip = document.createElement('button');
    allChip.className = 'chip active';
    allChip.textContent = 'ALL';
    allChip.addEventListener('click', () => {
        // Toggle all on/off
        const allActive = Array.from(items.keys()).every(k => stateSet.has(k));
        if (allActive) {
            stateSet.clear();
            container.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        } else {
            items.forEach((count, key) => stateSet.add(key));
            container.querySelectorAll('.chip').forEach(c => c.classList.add('active'));
        }
        if (onUpdate) onUpdate();
    });
    container.appendChild(allChip);

    // Individual chips
    items.forEach((count, key) => {
        const chip = document.createElement('button');
        chip.className = 'chip' + (stateSet.has(key) ? ' active' : '');
        chip.innerHTML = `${key}<span class="chip-count">${count}</span>`;
        chip.addEventListener('click', () => {
            if (stateSet.has(key)) {
                stateSet.delete(key);
                chip.classList.remove('active');
            } else {
                stateSet.add(key);
                chip.classList.add('active');
            }
            // Update "ALL" chip state
            const allActive = Array.from(items.keys()).every(k => stateSet.has(k));
            allChip.classList.toggle('active', allActive);
            if (onUpdate) onUpdate();
        });
        container.appendChild(chip);
    });
}

// Populate filter chips in floating panels
function populateFilterChips() {
    if (!DM) return;  // ALL DATA FROM DM

    // Use DM cached aggregations (O(1) lookups)
    const tierCounts = DM.getTierCounts();
    const ringCounts = DM.getRingCounts();
    const edgeCounts = DM.getEdgeTypeCounts();

    buildChipGroup('chips-tiers', tierCounts, VIS_FILTERS.tiers, refreshGraph);
    buildChipGroup('chips-rings', ringCounts, VIS_FILTERS.rings, refreshGraph);
    buildChipGroup('chips-edges', edgeCounts, VIS_FILTERS.edges, refreshGraph);
}

// =====================================================================
// LEGEND RENDERER: Color-coded hierarchical legend using LegendManager
// =====================================================================
function renderLegendSection(containerId, dimension, stateSet, onUpdate) {
    const container = document.getElementById(containerId);
    if (!container || !Legend) return;

    container.innerHTML = '';

    const legendData = Legend.getLegendData(dimension);
    if (!legendData || legendData.length === 0) return;

    // Build legend items
    legendData.forEach(item => {
        const el = document.createElement('div');
        el.className = 'topo-legend-item' + (stateSet && !stateSet.has(item.id) ? ' filtered' : '');
        el.dataset.category = item.id;
        el.dataset.dimension = dimension;

        // Color swatch
        const swatch = document.createElement('span');
        swatch.className = 'topo-legend-swatch';
        swatch.style.backgroundColor = item.color;

        // Label with count
        const label = document.createElement('span');
        label.className = 'topo-legend-label';
        label.textContent = item.id;

        const count = document.createElement('span');
        count.className = 'topo-legend-count';
        count.textContent = `(${item.count})`;

        el.appendChild(swatch);
        el.appendChild(label);
        el.appendChild(count);

        // Click to toggle filter
        if (stateSet) {
            el.addEventListener('click', () => {
                if (stateSet.has(item.id)) {
                    stateSet.delete(item.id);
                    el.classList.add('filtered');
                } else {
                    stateSet.add(item.id);
                    el.classList.remove('filtered');
                }
                if (onUpdate) onUpdate();
            });
        }

        container.appendChild(el);
    });

    console.log(`[Legend] Rendered ${dimension}: ${legendData.length} items`);
}

// Render all legend sections
function renderAllLegends() {
    if (!Legend) {
        console.warn('[Legend] LegendManager not initialized');
        return;
    }

    // Render node legends
    renderLegendSection('topo-tiers', 'tier', VIS_FILTERS.tiers, refreshGraph);
    renderLegendSection('topo-families', 'family', VIS_FILTERS.families, refreshGraph);
    renderLegendSection('topo-rings', 'ring', VIS_FILTERS.rings, refreshGraph);
    renderLegendSection('topo-layers', 'layer', VIS_FILTERS.layers, refreshGraph);
    renderLegendSection('topo-effects', 'effect', VIS_FILTERS.effects, refreshGraph);

    // Render edge legends
    renderLegendSection('topo-edges', 'edgeType', VIS_FILTERS.edges, refreshGraph);
    renderLegendSection('topo-edge-families', 'edgeFamily', VIS_FILTERS.edgeFamilies, refreshGraph);

    console.log('[Legend] All sections rendered');
}

// =====================================================================
// HUD LAYOUT MANAGER: Smart Text Placement with Collision Avoidance
// =====================================================================
const HudLayoutManager = {
    // Margin from viewport edges
    MARGIN: 16,
    // Panels by priority (higher = more important, won't be moved)
    fixed: ['top-left-header', 'stats-panel', 'metrics-panel', 'bottom-dock', 'report-panel', 'side-dock'],
    // Dynamic panels in priority order (hover-panel > file-panel)
    dynamic: ['hover-panel', 'file-panel'],

    // Throttle state
    _rafPending: false,
    _lastReflow: 0,
    REFLOW_THROTTLE_MS: 50,

    // Mouse position for hover-panel placement
    _mouseX: 0,
    _mouseY: 0,

    // Get viewport rectangle
    getViewport() {
        return {
            left: this.MARGIN,
            top: this.MARGIN,
            right: window.innerWidth - this.MARGIN,
            bottom: window.innerHeight - this.MARGIN,
            width: window.innerWidth - 2 * this.MARGIN,
            height: window.innerHeight - 2 * this.MARGIN
        };
    },

    // Check if sidebar is effectively "open" (occupying space)
    isSidebarOpen() {
        const sideDock = document.getElementById('side-dock');
        if (!sideDock) return false;
        return SIDEBAR_STATE.locked ||
            SIDEBAR_STATE.open ||
            sideDock.classList.contains('locked') ||
            sideDock.classList.contains('expanded') ||
            sideDock.matches(':hover');
    },

    // Get rectangle for an element (returns null if hidden/missing)
    getRect(el) {
        if (!el) return null;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') return null;
        const r = el.getBoundingClientRect();
        if (r.width === 0 && r.height === 0) return null;
        return { left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height };
    },

    // Get sidebar occupied region (full expanded width when open)
    getSidebarRect() {
        const sideDock = document.getElementById('side-dock');
        if (!sideDock || !this.isSidebarOpen()) return null;
        const sideWidth = parseInt(getComputedStyle(sideDock).getPropertyValue('--side-width')) || 260;
        // Sidebar is on the left, vertically centered
        return {
            left: 0,
            top: 0,
            right: 16 + sideWidth + 20, // left margin + width + padding
            bottom: window.innerHeight,
            width: 16 + sideWidth + 20,
            height: window.innerHeight
        };
    },

    // Get all occupied rectangles (fixed panels + sidebar when open)
    getOccupiedRects() {
        const rects = [];

        // Sidebar takes priority when open
        const sidebarRect = this.getSidebarRect();
        if (sidebarRect) rects.push(sidebarRect);

        // Fixed panels
        this.fixed.forEach(id => {
            if (id === 'side-dock') return; // Handled separately above
            const el = document.getElementById(id) || document.querySelector('.' + id);
            const rect = this.getRect(el);
            if (rect) rects.push(rect);
        });

        // Top-left header (special case - class-based)
        const topLeft = document.querySelector('.top-left');
        const topLeftRect = this.getRect(topLeft);
        if (topLeftRect) rects.push(topLeftRect);

        return rects;
    },

    // Calculate overlap area between two rectangles
    overlapArea(r1, r2) {
        if (!r1 || !r2) return 0;
        const xOverlap = Math.max(0, Math.min(r1.right, r2.right) - Math.max(r1.left, r2.left));
        const yOverlap = Math.max(0, Math.min(r1.bottom, r2.bottom) - Math.max(r1.top, r2.top));
        return xOverlap * yOverlap;
    },

    // Check if rect is fully inside viewport
    isInsideViewport(rect, viewport) {
        return rect.left >= viewport.left &&
            rect.top >= viewport.top &&
            rect.right <= viewport.right &&
            rect.bottom <= viewport.bottom;
    },

    // Clamp position to keep panel inside viewport
    clampToViewport(pos, panelWidth, panelHeight, viewport) {
        return {
            left: Math.max(viewport.left, Math.min(pos.left, viewport.right - panelWidth)),
            top: Math.max(viewport.top, Math.min(pos.top, viewport.bottom - panelHeight))
        };
    },

    // Generate candidate positions for file panel (4 corners, biased away from sidebar)
    getFilePanelCandidates(panelWidth, panelHeight) {
        const vp = this.getViewport();
        const margin = 20;
        const sidebarOpen = this.isSidebarOpen();
        const sidebarWidth = sidebarOpen ? 300 : 0;

        // Candidates: TR, BR, BL, TL (prefer right side when sidebar open)
        const candidates = sidebarOpen ? [
            { left: vp.right - panelWidth - margin, top: vp.top + margin },           // Top-right
            { left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin }, // Bottom-right
            { left: sidebarWidth + margin, top: vp.bottom - panelHeight - margin },  // Bottom-left (clear of sidebar)
            { left: sidebarWidth + margin, top: vp.top + margin }                     // Top-left (clear of sidebar)
        ] : [
            { left: vp.left + margin, top: vp.bottom - panelHeight - margin },       // Bottom-left (default)
            { left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin }, // Bottom-right
            { left: vp.right - panelWidth - margin, top: vp.top + margin },          // Top-right
            { left: vp.left + margin, top: vp.top + margin }                          // Top-left
        ];

        return candidates;
    },

    // Generate candidate positions for selection panel (prefer right side)
    getSelectionPanelCandidates(panelWidth, panelHeight) {
        const vp = this.getViewport();
        const margin = 20;
        const sidebarOpen = this.isSidebarOpen();
        const sidebarWidth = sidebarOpen ? 300 : 0;

        return sidebarOpen ? [
            { left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin }, // Bottom-right
            { left: vp.right - panelWidth - margin, top: vp.top + margin },                  // Top-right
            { left: sidebarWidth + margin, top: vp.bottom - panelHeight - margin },         // Bottom-left
            { left: sidebarWidth + margin, top: vp.top + margin }                           // Top-left
        ] : [
            { left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin },
            { left: vp.right - panelWidth - margin, top: vp.top + margin },
            { left: vp.left + margin, top: vp.bottom - panelHeight - margin },
            { left: vp.left + margin, top: vp.top + margin }
        ];
    },

    // Get screen centroid of selected nodes (for smart tooltip positioning)
    getSelectionCentroid() {
        if (!Graph || !Graph.graphData || SELECTED_NODE_IDS.size === 0) return null;
        const nodes = Graph.graphData().nodes || [];
        const selectedNodes = nodes.filter(n => SELECTED_NODE_IDS.has(n.id));
        if (selectedNodes.length === 0) return null;

        // Calculate centroid in 3D space
        let sumX = 0, sumY = 0, sumZ = 0;
        selectedNodes.forEach(n => {
            sumX += n.x || 0;
            sumY += n.y || 0;
            sumZ += n.z || 0;
        });
        const centroid3D = {
            x: sumX / selectedNodes.length,
            y: sumY / selectedNodes.length,
            z: sumZ / selectedNodes.length
        };

        // Project to screen coordinates
        const camera = Graph.camera();
        if (!camera) return null;
        const vector = new THREE.Vector3(centroid3D.x, centroid3D.y, centroid3D.z);
        vector.project(camera);
        return {
            x: (vector.x * 0.5 + 0.5) * window.innerWidth,
            y: (-vector.y * 0.5 + 0.5) * window.innerHeight
        };
    },

    // Generate candidate positions for hover panel (4 quadrants around anchor point)
    getHoverPanelCandidates(mouseX, mouseY, panelWidth, panelHeight) {
        const vp = this.getViewport();
        const offset = 16;  // Offset from anchor

        // Smart positioning: If hovering a selected node, position near selection centroid
        let anchorX = mouseX;
        let anchorY = mouseY;

        if (HOVERED_NODE && SELECTED_NODE_IDS.has(HOVERED_NODE.id)) {
            const centroid = this.getSelectionCentroid();
            if (centroid) {
                // Position panel near the selection cluster edge, not centroid center
                // Blend between mouse position and centroid for natural feel
                anchorX = mouseX * 0.3 + centroid.x * 0.7;
                anchorY = mouseY * 0.3 + centroid.y * 0.7;
            }
        }

        // Account for sidebar when it's open
        const sidebarOpen = this.isSidebarOpen();
        const sidebarRect = sidebarOpen ? this.getSidebarRect() : null;
        const minLeft = sidebarRect ? sidebarRect.right + offset : vp.left;

        // Candidates: TR, BR, BL, TL around anchor position
        let candidates = [
            { left: anchorX + offset, top: anchorY - panelHeight - offset },        // Top-right
            { left: anchorX + offset, top: anchorY + offset },                       // Bottom-right
            { left: anchorX - panelWidth - offset, top: anchorY + offset },         // Bottom-left
            { left: anchorX - panelWidth - offset, top: anchorY - panelHeight - offset }  // Top-left
        ];

        // Ensure candidates clear the sidebar
        if (sidebarRect) {
            candidates = candidates.map(c => ({
                left: Math.max(c.left, minLeft),
                top: c.top
            }));
        }

        return candidates;
    },

    // Update mouse position (called on mousemove)
    updateMousePosition(x, y) {
        this._mouseX = x;
        this._mouseY = y;
    },

    // Place a panel at the best position (least overlap)
    placePanel(panelEl, candidates, occupiedRects) {
        if (!panelEl) return null;

        const rect = panelEl.getBoundingClientRect();
        const panelWidth = rect.width || 400;
        const panelHeight = rect.height || 350;
        const viewport = this.getViewport();

        let bestPos = candidates[0];
        let bestOverlap = Infinity;

        for (const pos of candidates) {
            const clampedPos = this.clampToViewport(pos, panelWidth, panelHeight, viewport);
            const panelRect = {
                left: clampedPos.left,
                top: clampedPos.top,
                right: clampedPos.left + panelWidth,
                bottom: clampedPos.top + panelHeight
            };

            // Calculate total overlap with all occupied rects
            let totalOverlap = 0;
            for (const occRect of occupiedRects) {
                totalOverlap += this.overlapArea(panelRect, occRect);
            }

            // Check viewport containment penalty
            if (!this.isInsideViewport(panelRect, viewport)) {
                totalOverlap += 10000; // Heavy penalty for going outside viewport
            }

            if (totalOverlap < bestOverlap) {
                bestOverlap = totalOverlap;
                bestPos = clampedPos;
                if (totalOverlap === 0) break; // Perfect position found
            }
        }

        return bestPos;
    },

    // Reflow all dynamic panels
    reflow() {
        const now = Date.now();
        if (now - this._lastReflow < this.REFLOW_THROTTLE_MS) {
            // Throttle: schedule for later via RAF
            if (!this._rafPending) {
                this._rafPending = true;
                requestAnimationFrame(() => {
                    this._rafPending = false;
                    this.reflow();
                });
            }
            return;
        }
        this._lastReflow = now;

        const occupiedRects = this.getOccupiedRects();

        // Place hover panel first (higher priority)
        const hoverPanel = document.getElementById('hover-panel');
        let hoverPanelRect = null;
        if (hoverPanel && hoverPanel.classList.contains('visible')) {
            const hoverWidth = hoverPanel.offsetWidth || 280;
            const hoverHeight = hoverPanel.offsetHeight || 200;
            const candidates = this.getHoverPanelCandidates(
                this._mouseX, this._mouseY, hoverWidth, hoverHeight
            );
            const pos = this.placePanel(hoverPanel, candidates, occupiedRects);
            if (pos) {
                hoverPanel.style.left = pos.left + 'px';
                hoverPanel.style.top = pos.top + 'px';
                hoverPanel.style.right = 'auto';
                // Track hover panel rect for file panel to avoid
                hoverPanelRect = {
                    left: pos.left,
                    top: pos.top,
                    right: pos.left + hoverWidth,
                    bottom: pos.top + hoverHeight
                };
            }
        }

        // Build occupied rects for file panel (includes hover panel if visible)
        const filePanelOccupied = [...occupiedRects];
        if (hoverPanelRect) {
            filePanelOccupied.push(hoverPanelRect);
        }

        // Place selection panel (secondary priority)
        const selectionPanel = document.getElementById('selection-panel');
        let selectionPanelRect = null;
        if (selectionPanel && selectionPanel.classList.contains('visible')) {
            const candidates = this.getSelectionPanelCandidates(
                selectionPanel.offsetWidth || 320,
                selectionPanel.offsetHeight || 280
            );
            const pos = this.placePanel(selectionPanel, candidates, filePanelOccupied);
            if (pos) {
                selectionPanel.style.left = pos.left + 'px';
                selectionPanel.style.top = pos.top + 'px';
                selectionPanel.style.right = 'auto';
                selectionPanelRect = {
                    left: pos.left,
                    top: pos.top,
                    right: pos.left + (selectionPanel.offsetWidth || 320),
                    bottom: pos.top + (selectionPanel.offsetHeight || 280)
                };
                filePanelOccupied.push(selectionPanelRect);
            }
        }

        // Place file panel (lower priority, avoids hover panel too)
        const filePanel = document.getElementById('file-panel');
        if (filePanel && filePanel.classList.contains('visible')) {
            const candidates = this.getFilePanelCandidates(
                filePanel.offsetWidth || 400,
                filePanel.offsetHeight || 350
            );
            const pos = this.placePanel(filePanel, candidates, filePanelOccupied);
            if (pos) {
                filePanel.style.left = pos.left + 'px';
                filePanel.style.top = pos.top + 'px';
                filePanel.style.bottom = 'auto'; // Override default bottom positioning
            }
        }
    },

    // Initialize event listeners for reflow triggers
    init() {
        // Window resize
        window.addEventListener('resize', () => this.reflow());

        // Track mouse position for hover-panel placement
        window.addEventListener('mousemove', (e) => {
            this.updateMousePosition(e.clientX, e.clientY);
        }, { passive: true });

        // Sidebar state changes (lock toggle is handled separately)
        const sideDock = document.getElementById('side-dock');
        if (sideDock) {
            sideDock.addEventListener('mouseenter', () => this.reflow());
            sideDock.addEventListener('mouseleave', () => {
                // Delay reflow slightly to let CSS transition complete
                setTimeout(() => this.reflow(), 200);
            });
        }

        console.log('[HudLayoutManager] Initialized');
    }
};

worker.onmessage = function (e) {
    if (e.data.status && !e.data.result) {
        document.getElementById('loader-status').innerText = e.data.status;
    } else if (e.data.error) {
        document.getElementById('loader-status').innerText = "ERROR: " + e.data.error;
        document.getElementById('loader-status').style.color = "red";
    } else if (e.data.result) {
        FULL_GRAPH = e.data.result;
        FILE_GRAPH = null;
        FILE_NODE_POSITIONS = new Map();
        EXPANDED_FILES.clear();
        GRAPH_MODE = 'atoms';
        document.getElementById('loader-status').innerText = "INITIALIZING VISUALIZATION...";
        initGraph(FULL_GRAPH);
    }
};

// Start Work: Decompress in main thread, then send JSON string to worker for parsing
try {
    const jsonStr = decompressPayload(COMPRESSED_PAYLOAD);
    worker.postMessage(jsonStr);
} catch (err) {
    document.getElementById('loader-status').innerText = "ERROR: " + err.message;
    document.getElementById('loader-status').style.color = "red";
    console.error('[Decompression] Failed:', err);
}

// =====================================================================
// 2D CANVAS FALLBACK: Used when WebGL is unavailable
// =====================================================================
function initFallback2D(container, graphData, fullData) {
    console.log('[2D Fallback] Initializing canvas renderer');
    showToast('WebGL unavailable - using 2D fallback');

    const loader = document.getElementById('loader');
    if (loader) loader.style.display = 'none';

    // Update HUD stats even in 2D fallback mode
    updateHudStats(fullData);

    container.innerHTML = '';
    container.style.position = 'relative';
    container.style.overflow = 'hidden';

    const canvas = document.createElement('canvas');
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.display = 'block';
    canvas.style.background = '#03040a';
    container.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    let width = container.clientWidth || window.innerWidth;
    let height = container.clientHeight || window.innerHeight;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    // Layout: simple force-directed positions
    const nodes = graphData.nodes || [];
    const links = graphData.links || [];
    const nodeMap = new Map();

    nodes.forEach((n, i) => {
        const angle = (i / nodes.length) * Math.PI * 2;
        const radius = Math.min(width, height) * 0.35;
        n._x = width / 2 + Math.cos(angle) * radius * (0.5 + Math.random() * 0.5);
        n._y = height / 2 + Math.sin(angle) * radius * (0.5 + Math.random() * 0.5);
        n._vx = 0;
        n._vy = 0;
        nodeMap.set(n.id, n);
    });

    // Camera state
    let camX = 0, camY = 0, zoom = 1;
    let dragging = false, lastX = 0, lastY = 0;

    canvas.addEventListener('mousedown', e => {
        dragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
    });
    canvas.addEventListener('mousemove', e => {
        if (!dragging) return;
        camX += (e.clientX - lastX) / zoom;
        camY += (e.clientY - lastY) / zoom;
        lastX = e.clientX;
        lastY = e.clientY;
    });
    canvas.addEventListener('mouseup', () => dragging = false);
    canvas.addEventListener('mouseleave', () => dragging = false);
    canvas.addEventListener('wheel', e => {
        e.preventDefault();
        const factor = e.deltaY > 0 ? 0.9 : 1.1;
        zoom = Math.max(0.1, Math.min(5, zoom * factor));
    }, { passive: false });

    function toScreen(x, y) {
        return {
            x: (x + camX - width / 2) * zoom + width / 2,
            y: (y + camY - height / 2) * zoom + height / 2
        };
    }

    function parseColor(c) {
        if (typeof c === 'number') {
            return '#' + c.toString(16).padStart(6, '0');
        }
        return c || '#888888';
    }

    function render() {
        ctx.fillStyle = '#03040a';
        ctx.fillRect(0, 0, width, height);

        // Draw edges
        ctx.strokeStyle = 'rgba(100,100,100,0.3)';
        ctx.lineWidth = 0.5;
        for (const link of links) {
            const src = typeof link.source === 'object' ? link.source : nodeMap.get(link.source);
            const tgt = typeof link.target === 'object' ? link.target : nodeMap.get(link.target);
            if (!src || !tgt) continue;
            const p1 = toScreen(src._x, src._y);
            const p2 = toScreen(tgt._x, tgt._y);
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
        }

        // Draw nodes
        for (const node of nodes) {
            const p = toScreen(node._x, node._y);
            const r = Math.max(2, (node.val || 1) * zoom * 0.5);
            ctx.fillStyle = parseColor(node.color);
            ctx.beginPath();
            ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
            ctx.fill();
        }

        // Info overlay
        ctx.fillStyle = 'rgba(255,255,255,0.5)';
        ctx.font = '11px monospace';
        ctx.fillText('2D Fallback Mode (WebGL unavailable)', 10, 20);
        ctx.fillText('Drag to pan, scroll to zoom', 10, 35);
        ctx.fillText(`Nodes: ${nodes.length} | Edges: ${links.length}`, 10, 50);

        requestAnimationFrame(render);
    }

    function resize() {
        width = container.clientWidth || window.innerWidth;
        height = container.clientHeight || window.innerHeight;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.scale(dpr, dpr);
    }

    window.addEventListener('resize', resize);
    render();

    // Initialize DataManager (required for UI controls)
    DM = new DataManager();
    DM.init(fullData);
    window.DM = DM;

    // Setup UI controls (they work independently of 3D graph)
    setupControls(fullData);
    setupReport(fullData);
    setupAIInsights(fullData);
    setupMetrics(fullData);
    setupHudFade();
    setupDimensionToggle();

    // Update stats with actual node/edge counts
    updateHudStats(graphData);
}

function initGraph(data) {
    // =================================================================
    // DATA MANAGER: Self-test + parity checks
    // =================================================================
    DM = new DataManager();
    DM.init(data);
    window.DM = DM;
    DM.selfTest();
    runDmParity(DM, data);

    // =================================================================
    // HUD STATS: Populate header and stats panel with graph data
    // =================================================================
    updateHudStats(data);

    // =================================================================
    // TOKEN-DRIVEN CONFIG: Extract from payload
    // =================================================================
    const physicsConfig = data.physics || {};
    const appearanceConfig = data.appearance || {};
    const simulation = physicsConfig.simulation || {};
    const background = appearanceConfig.background || {};
    const stars = background.stars || {};
    const bloom = background.bloom || {};
    // NEW: Render, highlight, flow_mode from THE REMOTE CONTROL
    const renderConfig = appearanceConfig.render || {};
    const highlightConfig = appearanceConfig.highlight || {};
    FLOW_CONFIG = appearanceConfig.flow_mode || {};
    const edgeModes = appearanceConfig.edge_modes || {};
    EDGE_MODE_CONFIG = {
        resolution: edgeModes.resolution || EDGE_MODE_CONFIG.resolution,
        weight: edgeModes.weight || EDGE_MODE_CONFIG.weight,
        confidence: edgeModes.confidence || EDGE_MODE_CONFIG.confidence,
        width: edgeModes.width || EDGE_MODE_CONFIG.width,
        dim: edgeModes.dim || EDGE_MODE_CONFIG.dim,
        opacity: (typeof edgeModes.opacity === 'number') ? edgeModes.opacity : EDGE_MODE_CONFIG.opacity
    };
    FILE_COLOR_CONFIG = Object.assign({}, FILE_COLOR_CONFIG, appearanceConfig.file_color || {});
    EDGE_DEFAULT_OPACITY =
        (typeof EDGE_MODE_CONFIG.opacity === 'number') ? EDGE_MODE_CONFIG.opacity : EDGE_DEFAULT_OPACITY;
    const boundaryConfig = appearanceConfig.boundary || {};
    APPEARANCE_STATE.edgeOpacity = EDGE_DEFAULT_OPACITY;
    APPEARANCE_STATE.boundaryFill = boundaryConfig.fill_opacity ?? APPEARANCE_STATE.boundaryFill;
    APPEARANCE_STATE.boundaryWire = boundaryConfig.wire_opacity ?? APPEARANCE_STATE.boundaryWire;
    APPEARANCE_STATE.backgroundBase = background.color || '#000000';
    APPEARANCE_STATE.fileLightness = FILE_COLOR_CONFIG.lightness ?? APPEARANCE_STATE.fileLightness;
    const nodeColor = appearanceConfig.node_color || {};
    NODE_COLOR_CONFIG = {
        tier: nodeColor.tier || {},
        ring: nodeColor.ring || {},
        unknown: nodeColor.unknown || '#666666'
    };
    const edgeColor = appearanceConfig.edge_color || {};
    EDGE_COLOR_CONFIG = Object.assign({}, EDGE_COLOR_CONFIG, edgeColor);

    // Initial Filter: show full graph
    const filtered = filterGraph(data, CURRENT_DENSITY, ACTIVE_DATAMAPS, VIS_FILTERS);

    const div = document.getElementById('3d-graph');

    // ═══════════════════════════════════════════════════════════════════
    // GRADIENT EDGES: Custom THREE.js lines with vertex colors
    // Creates beautiful gradients from source to target node colors
    // ═══════════════════════════════════════════════════════════════════
    let GRADIENT_EDGES_ENABLED = true;  // Toggle for gradient edges

    function hexToRgb(hex) {
        // Convert hex color to RGB array [0-1, 0-1, 0-1]
        if (typeof hex === 'number') {
            return [
                ((hex >> 16) & 255) / 255,
                ((hex >> 8) & 255) / 255,
                (hex & 255) / 255
            ];
        }
        if (typeof hex === 'string') {
            hex = hex.replace('#', '');
            if (hex.length === 3) {
                hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
            }
            const num = parseInt(hex, 16);
            return [
                ((num >> 16) & 255) / 255,
                ((num >> 8) & 255) / 255,
                (num & 255) / 255
            ];
        }
        return [0.5, 0.5, 0.5];  // Default gray
    }

    function createGradientEdge(link) {
        // Get source and target nodes
        const srcNode = typeof link.source === 'object' ? link.source :
            (Graph?.graphData()?.nodes?.find(n => n.id === link.source));
        const tgtNode = typeof link.target === 'object' ? link.target :
            (Graph?.graphData()?.nodes?.find(n => n.id === link.target));

        // Get colors from nodes (using current color mode)
        const srcColorHex = srcNode ? toColorNumber(getNodeColorByMode(srcNode), 0x888888) : 0x888888;
        const tgtColorHex = tgtNode ? toColorNumber(getNodeColorByMode(tgtNode), 0x888888) : 0x888888;
        const srcRgb = hexToRgb(srcColorHex);
        const tgtRgb = hexToRgb(tgtColorHex);

        // Create geometry with 2 vertices
        const geometry = new THREE.BufferGeometry();

        // Positions will be updated by linkPositionUpdate
        const positions = new Float32Array([0, 0, 0, 0, 0, 0]);
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        // Vertex colors: source color at start, target color at end
        const colors = new Float32Array([
            srcRgb[0], srcRgb[1], srcRgb[2],  // Source vertex color
            tgtRgb[0], tgtRgb[1], tgtRgb[2]   // Target vertex color
        ]);
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        // Material with vertex colors
        const material = new THREE.LineBasicMaterial({
            vertexColors: true,
            transparent: true,
            opacity: link.opacity ?? EDGE_DEFAULT_OPACITY,
            linewidth: 1  // Note: linewidth > 1 only works on some platforms
        });

        return new THREE.Line(geometry, material);
    }

    function updateGradientEdge(line, link, coords) {
        // Update line positions
        const posArr = line.geometry.attributes.position.array;
        posArr[0] = coords.start.x || 0;
        posArr[1] = coords.start.y || 0;
        posArr[2] = coords.start.z || 0;
        posArr[3] = coords.end.x || 0;
        posArr[4] = coords.end.y || 0;
        posArr[5] = coords.end.z || 0;
        line.geometry.attributes.position.needsUpdate = true;

        // Update colors based on current node colors
        const srcNode = typeof link.source === 'object' ? link.source :
            (Graph?.graphData()?.nodes?.find(n => n.id === link.source));
        const tgtNode = typeof link.target === 'object' ? link.target :
            (Graph?.graphData()?.nodes?.find(n => n.id === link.target));

        const srcColorHex = srcNode ? toColorNumber(getNodeColorByMode(srcNode), 0x888888) : 0x888888;
        const tgtColorHex = tgtNode ? toColorNumber(getNodeColorByMode(tgtNode), 0x888888) : 0x888888;
        const srcRgb = hexToRgb(srcColorHex);
        const tgtRgb = hexToRgb(tgtColorHex);

        const colArr = line.geometry.attributes.color.array;
        colArr[0] = srcRgb[0]; colArr[1] = srcRgb[1]; colArr[2] = srcRgb[2];
        colArr[3] = tgtRgb[0]; colArr[4] = tgtRgb[1]; colArr[5] = tgtRgb[2];
        line.geometry.attributes.color.needsUpdate = true;
    }

    // Refresh all gradient edge colors (call when node color mode changes)
    function refreshGradientEdgeColors() {
        if (!GRADIENT_EDGES_ENABLED || !Graph) return;
        // Force rebuild of all link objects to update colors
        Graph.linkThreeObject(link => createGradientEdge(link));
    }

    // Make it globally accessible for color mode changes
    window.refreshGradientEdgeColors = refreshGradientEdgeColors;

    // TOKEN-DRIVEN: Read render config from THE REMOTE CONTROL
    const dimensions = renderConfig.dimensions || 3;
    const nodeRes = renderConfig.nodeResolution || 8;

    try {
        Graph = ForceGraph3D({
            rendererConfig: {
                antialias: true,
                alpha: true,
                powerPreference: 'high-performance'
            }
        })
            (div)
            .graphData(filtered)
            .numDimensions(dimensions)
            .backgroundColor(toColorNumber(background.color, 0x000000))
            .nodeLabel('name')
            .nodeColor(node => toColorNumber(node.color, 0x888888))
            .nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale)
            // ═══════════════════════════════════════════════════════════════════
            // GRADIENT EDGES: Custom THREE.Line with vertex colors
            // Each edge smoothly transitions from source node color to target node color
            // ═══════════════════════════════════════════════════════════════════
            .linkThreeObject(link => GRADIENT_EDGES_ENABLED ? createGradientEdge(link) : null)
            .linkPositionUpdate((line, coords, link) => {
                if (GRADIENT_EDGES_ENABLED && line) {
                    updateGradientEdge(line, link, coords);
                }
                return true;  // Keep default behavior for non-gradient
            })
            .linkColor(link => GRADIENT_EDGES_ENABLED ? null : toColorNumber(getEdgeColor(link), 0x222222))
            .linkOpacity(link => GRADIENT_EDGES_ENABLED ? 0 : (link.opacity ?? EDGE_DEFAULT_OPACITY))
            .nodeThreeObjectExtend(true)
            .nodeThreeObject(node => ensureNodeOverlays(node))
            .nodeResolution(Math.max(nodeRes, 16))
            .linkResolution(6)
            .showNavInfo(false)
            .warmupTicks(simulation.warmupTicks || 30)
            .cooldownTicks(simulation.cooldownTicks || 0)
            .onNodeHover(node => handleNodeHover(node, data))
            .onNodeClick((node, event) => handleNodeClick(node, event))
            .onBackgroundClick(() => maybeClearSelection())
            .onEngineStop(() => {
                // Physics-dependent operations (run after simulation stabilizes)
                drawFileBoundaries(data);
                // LAYOUT STABILITY: Freeze layout after initial simulation completes
                if (!LAYOUT_FROZEN) {
                    saveNodePositions();
                    freezeLayout();
                }
            });
    } catch (err) {
        console.error('[WebGL] Failed to initialize 3D graph:', err);
        initFallback2D(div, filtered, data);
        return;
    }

    window.Graph = Graph;

    // FIX: Drift on resize
    // Updates Graph renderer size when window creates
    window.addEventListener('resize', () => {
        if (Graph) {
            Graph.width(window.innerWidth);
            Graph.height(window.innerHeight);
        }
    });

    // OPTIMIZATION: Hide loader immediately after Graph creation (don't wait for physics)
    // This makes the visualization appear 200-500ms faster
    document.getElementById('loader').style.display = 'none';

    // =================================================================
    // RENDERER QUALITY: Enable anti-aliasing and high DPI
    // =================================================================
    const renderer = Graph.renderer();
    if (renderer) {
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        // Enable high quality rendering
        renderer.antialias = true;
        renderer.alpha = true;
        renderer.powerPreference = 'high-performance';
    }

    initSelectionState(data);
    setupSelectionInteractions();
    updateSelectionVisuals();

    // =================================================================
    // CONTROLS: keep default camera behavior, enable damping
    // =================================================================
    const controls = Graph.controls();
    if (controls) {
        // TOKEN-DRIVEN: Read from payload (if available), else use defaults
        // Allow remote configuration of mouse buttons and damping
        const navConfig = data.config?.controls || data.controls || {};

        controls.enableDamping = navConfig.enableDamping !== undefined ? navConfig.enableDamping : true;
        controls.dampingFactor = navConfig.dampingFactor || 0.1;
        controls.enableRotate = navConfig.enableRotate !== undefined ? navConfig.enableRotate : true;
        controls.enablePan = navConfig.enablePan !== undefined ? navConfig.enablePan : true;

        // Mouse Buttons: Map generic names to integer constants
        // 0: ROTATE, 1: DOLLY (Zoom), 2: PAN
        const defaultButtons = {
            LEFT: 2, // PAN
            MIDDLE: 1, // DOLLY
            RIGHT: 0 // ROTATE
        };

        if (navConfig.mouseButtons) {
            controls.mouseButtons = {
                LEFT: navConfig.mouseButtons.LEFT ?? defaultButtons.LEFT,
                MIDDLE: navConfig.mouseButtons.MIDDLE ?? defaultButtons.MIDDLE,
                RIGHT: navConfig.mouseButtons.RIGHT ?? defaultButtons.RIGHT
            };
        } else {
            controls.mouseButtons = defaultButtons;
        }

        // Spacebar toggling disabled to ensure stability
    }

    // =================================================================
    // TOKEN-DRIVEN: Force Configuration
    // =================================================================
    const forces = physicsConfig.forces || {};
    if (forces.charge?.enabled) {
        Graph.d3Force('charge').strength(forces.charge.strength || -120);
        Graph.d3Force('charge').distanceMax(forces.charge.distanceMax || 500);
    }
    if (forces.link?.enabled) {
        const linkDistance = forces.link.distance || 50;
        Graph.d3Force('link').distance(linkDistance);
        DEFAULT_LINK_DISTANCE = linkDistance;
    }
    if (forces.center?.enabled) {
        Graph.d3Force('center').strength(forces.center.strength || 0.05);
    }

    // =================================================================
    // TOKEN-DRIVEN: Starfield (Cosmic Background)
    // =================================================================
    const scene = Graph.scene();
    const starsGeometry = new THREE.BufferGeometry();
    const starsCount = stars.count || 2000;
    const starsSpread = stars.spread || 5000;
    const posArray = new Float32Array(starsCount * 3);

    for (let i = 0; i < starsCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * starsSpread;
    }

    starsGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const starsMaterial = new THREE.PointsMaterial({
        size: stars.size || 2,
        color: 0xffffff,
        transparent: true,
        opacity: stars.opacity || 0.8,
    });
    const starMesh = new THREE.Points(starsGeometry, starsMaterial);
    scene.add(starMesh);
    STARFIELD = starMesh;
    STARFIELD_OPACITY = starsMaterial.opacity;

    // =================================================================
    // TOKEN-DRIVEN: Bloom Post-Processing (DISABLED - UMD build compatibility)
    // Post-processing addons require ES modules; using UMD for file:// support
    // =================================================================
    // Bloom disabled for compatibility - visualization works without it

    // Setup Hud Controls (TOKEN-DRIVEN)
    // OPTIMIZATION: Defer UI setup to next frame so graph renders first
    // This makes the visualization appear 150-200ms faster
    Promise.resolve().then(() => {
        setupControls(data);
        setupReport(data);
        setupAIInsights(data);
        setupMetrics(data);
        setupHudFade();
        setupDimensionToggle();
        applyEdgeMode();

        // SELF-TEST: Deterministic validation of UI controls (deferred)
        runSelfTest(data);
    });
}

function runSelfTest(data) {
    const results = {
        timestamp: new Date().toISOString(),
        passed: [],
        failed: []
    };

    const test = (name, condition) => {
        if (condition) {
            results.passed.push(name);
        } else {
            results.failed.push(name);
        }
    };

    // Test 1: Core UI elements exist (canonical UI: command bar + floating panels + side dock)

    // Command bar and buttons
    test('command-bar-exists', !!document.getElementById('command-bar'));
    test('cmd-view-exists', !!document.getElementById('cmd-view'));
    test('cmd-filter-exists', !!document.getElementById('cmd-filter'));
    test('cmd-style-exists', !!document.getElementById('cmd-style'));
    test('cmd-settings-exists', !!document.getElementById('cmd-settings'));

    // Floating panels
    test('panel-view-exists', !!document.getElementById('panel-view'));
    test('panel-filter-exists', !!document.getElementById('panel-filter'));
    test('panel-style-exists', !!document.getElementById('panel-style'));
    test('panel-settings-exists', !!document.getElementById('panel-settings'));

    // Side dock
    const sideDock = document.getElementById('side-dock');
    test('side-dock-exists', !!sideDock);
    test('topo-minimap-exists', !!document.getElementById('dock-minimap'));
    test('preset-grid-exists', !!document.getElementById('dock-presets'));
    test('color-scheme-grid-exists', !!document.getElementById('dock-schemes'));

    // OKLCH picker
    test('oklch-picker-exists', !!document.getElementById('oklch-picker'));

    // Topo tooltip
    test('topo-tooltip-exists', !!document.getElementById('topo-tooltip'));

    // Bottom dock controls
    const datamapContainer = document.getElementById('datamap-controls');
    test('datamap-controls-exist', !!datamapContainer);
    test('btn-files-exists', !!document.getElementById('btn-files'));
    test('btn-flow-exists', !!document.getElementById('btn-flow'));
    test('btn-edge-mode-exists', !!document.getElementById('btn-edge-mode'));
    test('btn-report-exists', !!document.getElementById('btn-report'));
    test('btn-stars-exists', !!document.getElementById('btn-stars'));
    test('btn-dimensions-exists', !!document.getElementById('btn-dimensions'));

    // Graph state
    test('starfield-initialized', !!STARFIELD);

    // Test 1b: Side dock content visibility
    const sideContent = document.getElementById('side-content');
    if (sideDock && sideContent) {
        const contentVisible = window.getComputedStyle(sideContent).display !== 'none';
        test('side-dock-content-visible', contentVisible);
    }

    // Test 1c: HUD Layout Manager tests
    test('hud-layout-manager-exists', typeof HudLayoutManager === 'object' && HudLayoutManager !== null);
    test('hud-layout-manager-has-reflow', typeof HudLayoutManager.reflow === 'function');
    test('hud-layout-manager-has-placePanel', typeof HudLayoutManager.placePanel === 'function');

    // Test 1d: HUD placement with synthetic rects (collision avoidance)
    if (typeof HudLayoutManager.placePanel === 'function') {
        // Create a test scenario: occupied rect on top-left, panel should avoid it
        const fakeOccupied = [{ left: 0, top: 0, right: 300, bottom: 200 }];
        const fakeCandidates = [
            { left: 20, top: 100 },   // Would overlap with occupied
            { left: 400, top: 100 }   // Should be clear
        ];
        // Create a mock panel element
        const mockPanel = document.createElement('div');
        mockPanel.style.width = '200px';
        mockPanel.style.height = '150px';
        mockPanel.style.position = 'fixed';
        document.body.appendChild(mockPanel);

        const result = HudLayoutManager.placePanel(mockPanel, fakeCandidates, fakeOccupied);
        // Should choose the second candidate (no overlap)
        const pickedNonOverlapping = result && result.left >= 300;
        test('hud-placement-avoids-overlap', pickedNonOverlapping);

        document.body.removeChild(mockPanel);
    }

    // Test 1e: Canonical taxonomy field tests
    // Test that node.tier is preferred over atom prefix inference
    const mockNodeWithTier = { tier: 'T2', atom: 'CORE.001', ring: 'DOMAIN' };
    const tierResult = getNodeTier(mockNodeWithTier);
    test('node-tier-prefers-field', tierResult === 'T2');  // Should use tier field, not infer T0 from CORE.

    // Test that node.ring is used when present
    const mockNodeWithRing = { ring: 'PRESENTATION', layer: 'APPLICATION' };
    const ringResult = getNodeRing(mockNodeWithRing);
    test('node-ring-prefers-field', ringResult === 'PRESENTATION');  // Should use ring, not layer

    // Test tier aliases work (CORE → T0, EXT → T2)
    test('tier-alias-core-to-t0', normalizeTier('CORE') === 'T0');
    test('tier-alias-ext-to-t2', normalizeTier('EXT') === 'T2');

    // Test atom_family extraction
    const mockNodeWithFamily = { atom_family: 'LOG', atom: 'ORG.AGG.M' };
    const familyResult = getNodeAtomFamily(mockNodeWithFamily);
    test('node-atom-family-prefers-field', familyResult === 'LOG');  // Should use atom_family, not infer ORG

    // Test 1f: Hover panel tests
    test('hover-panel-exists', document.getElementById('hover-panel') !== null);

    // Test hover panel uses canonical fields
    const mockCanonicalNode = {
        name: 'TestNode',
        atom_family: 'LOG',
        ring: 'PRESENTATION',
        tier: 'T2',
        atom: 'ORG.AGG.M',
        kind: 'function',
        role: 'Utility'
    };
    // Simulate updateHoverPanel with mock node
    if (typeof updateHoverPanel === 'function') {
        updateHoverPanel(mockCanonicalNode);
        const hoverFamily = document.getElementById('hover-family')?.textContent;
        const hoverRing = document.getElementById('hover-ring')?.textContent;
        const hoverTier = document.getElementById('hover-tier')?.textContent;
        // Verify canonical fields are used (LOG not ORG, PRESENTATION, T2)
        test('hover-panel-uses-canonical-fields',
            hoverFamily === 'LOG' && hoverRing === 'PRESENTATION' && hoverTier === 'T2');
        // Clean up: hide panel
        updateHoverPanel(null);
    }

    // Test 2: Metrics panel populated
    test('metric-edge-resolution', document.getElementById('metric-edge-resolution')?.textContent !== '--');
    test('metric-call-ratio', document.getElementById('metric-call-ratio')?.textContent !== '--');
    test('metric-reachability', document.getElementById('metric-reachability')?.textContent !== '--');
    test('metric-dead-code', document.getElementById('metric-dead-code')?.textContent !== '--');
    test('metric-topology', document.getElementById('metric-topology')?.textContent !== '--');

    // Test 3: Data integrity
    test('nodes-count-positive', data.nodes && data.nodes.length > 0);
    test('links-count-positive', data.links && data.links.length > 0);
    test('graph-initialized', !!window.Graph);

    // Test 4: Controls config loaded
    test('controls-config-exists', !!data.controls);
    test('appearance-config-exists', !!data.appearance);
    test('physics-config-exists', !!data.physics);

    // Test 5: Initial state correct
    const densitySlider = document.getElementById('density-slider2');
    test('density-slider2-has-value', densitySlider && densitySlider.value !== undefined);
    test('3d-mode-default', IS_3D === true);

    // Expose results to window for external testing
    window.SELF_TEST_RESULTS = results;

    // Log summary
    const total = results.passed.length + results.failed.length;
    const passRate = ((results.passed.length / total) * 100).toFixed(1);

    if (results.failed.length === 0) {
        console.log(`%c✅ SELF-TEST PASSED: ${results.passed.length}/${total} tests (${passRate}%)`, 'color: #00ff00; font-weight: bold');
    } else {
        console.warn(`%c⚠️ SELF-TEST: ${results.passed.length}/${total} passed (${passRate}%)`, 'color: #ffaa00; font-weight: bold');
        console.warn('Failed tests:', results.failed);
    }

    return results;
}

// Tier aliases: legacy names → canonical T0/T1/T2
const TIER_ALIASES = {
    'CORE': 'T0', 'T0': 'T0',
    'ARCH': 'T1', 'T1': 'T1',
    'EXT': 'T2', 'T2': 'T2',
    'DISCOVERED': 'T2',  // EXT.DISCOVERED → T2
    'UNKNOWN': 'UNKNOWN'
};

function normalizeTier(tier) {
    if (!tier) return 'UNKNOWN';
    const upper = String(tier).toUpperCase();
    return TIER_ALIASES[upper] || upper;
}

// Prefer canonical node.tier field; fallback to atom prefix inference
function getNodeTier(node) {
    // If node is a string (backward compat: called with atomId), infer from prefix
    if (typeof node === 'string') {
        const atomId = node;
        if (!atomId) return 'UNKNOWN';
        if (atomId.startsWith('CORE.')) return 'T0';
        if (atomId.startsWith('ARCH.')) return 'T1';
        if (atomId.startsWith('EXT.')) return 'T2';
        return 'UNKNOWN';
    }
    // Prefer canonical field
    if (node.tier) {
        return normalizeTier(node.tier);
    }
    // Fallback: infer from atom prefix
    const atomId = String(node.atom || '');
    if (atomId.startsWith('CORE.')) return 'T0';
    if (atomId.startsWith('ARCH.')) return 'T1';
    if (atomId.startsWith('EXT.')) return 'T2';
    return 'UNKNOWN';
}

// Get atom family from canonical field or infer from atom prefix
function getNodeAtomFamily(node) {
    // Prefer canonical field
    if (node.atom_family) {
        return String(node.atom_family).toUpperCase();
    }
    // Fallback: infer from atom (e.g., "LOG.FNC.M" → "LOG")
    const atomId = String(node.atom || '');
    const dotIdx = atomId.indexOf('.');
    if (dotIdx > 0) {
        return atomId.substring(0, dotIdx).toUpperCase();
    }
    return 'UNKNOWN';
}

function normalizeRingValue(value) {
    if (value === null || value === undefined) return null;
    const ring = String(value).trim().toUpperCase();
    if (!ring) return null;
    const aliases = {
        TEST: 'TESTING'
    };
    return aliases[ring] || ring;
}

function getNodeRing(node) {
    const ring = node.ring || node.layer || 'UNKNOWN';
    return normalizeRingValue(ring) || 'UNKNOWN';
}

function getNodeLayer(node) {
    if (!node) return 'Unknown';
    return node.layer || node.dimensions?.D2_LAYER || 'Unknown';
}

function getNodeEffect(node) {
    if (!node) return 'Unknown';
    return node.effect || node.dimensions?.D6_EFFECT || 'Unknown';
}

function getNodeColorByMode(node) {
    // ═══════════════════════════════════════════════════════════════════
    // ALL COLORS NOW COME FROM ColorOrchestrator (aliased as Color)
    // This ensures legend colors match visualization colors exactly
    // OKLCH transforms are applied automatically
    // ═══════════════════════════════════════════════════════════════════

    if (NODE_COLOR_MODE === 'file') {
        const fileIdx = node.fileIdx ?? -1;
        if (fileIdx < 0) {
            return Color.get('tier', 'UNKNOWN');  // Use ColorOrchestrator
        }
        // ALL DATA FROM DM
        const fileBoundaries = DM ? DM.getFileBoundaries() : [];
        const totalFiles = fileBoundaries.length;
        const fileInfo = fileBoundaries[fileIdx] || {};
        const fileLabel = fileInfo.file || fileInfo.file_name || fileIdx;
        return getFileColor(fileIdx, totalFiles, fileLabel);
    }

    if (NODE_COLOR_MODE === 'family') {
        const atomFamily = getNodeAtomFamily(node);
        return Color.get('family', atomFamily);  // FROM ColorOrchestrator
    }

    if (NODE_COLOR_MODE === 'ring') {
        const ring = getNodeRing(node);
        return Color.get('ring', ring);  // FROM ColorOrchestrator
    }

    if (NODE_COLOR_MODE === 'layer') {
        const layer = (node.layer || 'VIRTUAL').toUpperCase();
        return Color.get('layer', layer);  // FROM ColorOrchestrator
    }

    // Tier color mode (default)
    const tier = getNodeTier(node);
    return Color.get('tier', tier);  // FROM ColorOrchestrator
}

function applyNodeColors(nodes) {
    const fileBoundaries = DM ? DM.getFileBoundaries() : [];  // ALL DATA FROM DM
    nodes.forEach(node => {
        if (node && node.isFileNode) {
            if (!node.color) {
                const totalFiles = fileBoundaries.length;
                const fileInfo = fileBoundaries[node.fileIdx] || {};
                const fileLabel = fileInfo.file || fileInfo.file_name || node.fileIdx;
                node.color = getFileColor(node.fileIdx, totalFiles, fileLabel);
            }
            return;
        }
        if (fileMode) {
            return;
        }
        node.color = getNodeColorByMode(node);
    });
}

function filterGraph(data, minVal, datamapSet, filters) {
    // ALL DATA FROM DM - the processing pipeline
    const allNodes = DM ? DM.getNodes() : (data?.nodes || []);
    const allLinks = DM ? DM.getLinks() : (data?.links || []);

    const tierFilter = filters?.tiers || new Set();
    const ringFilter = filters?.rings || new Set();
    const roleFilter = filters?.roles || new Set();
    const edgeFilter = filters?.edges || new Set();
    const familyFilter = filters?.families || new Set();
    const layerFilter = filters?.layers || new Set();
    const effectFilter = filters?.effects || new Set();
    const edgeFamilyFilter = filters?.edgeFamilies || new Set();
    const showEdges = filters?.metadata?.showEdges !== false;

    const availableRings = Array.from(new Set(allNodes.map(n => getNodeRing(n)))).sort();
    let ringFilterValues = Array.from(ringFilter);
    let ringIntersection = ringFilterValues.filter(r => availableRings.includes(r));
    if (ringFilterValues.length > 0 && ringIntersection.length === 0) {
        console.warn('[Filters] Ring filter values not present in dataset; clearing.', {
            ringValues: ringFilterValues,
            availableRings
        });
        ringFilter.clear();
        ringFilterValues = [];
        ringIntersection = [];
    }

    // Filter nodes by size/importance
    const sampleNode = allNodes.length > 0 ? allNodes[0] : null;
    let visibleNodes = allNodes.filter(n => (n.val ?? 1) >= minVal);
    const countAfterMinVal = visibleNodes.length;

    if (datamapSet && datamapSet.size > 0) {
        visibleNodes = visibleNodes.filter(n => {
            for (const id of datamapSet) {
                const config = DATAMAP_INDEX[id];
                if (config && datamapMatches(n, config)) return true;
            }
            return false;
        });
    }
    const countAfterDatamap = visibleNodes.length;

    const tierFilterActive = tierFilter.size > 0;
    const ringFilterActive = ringFilter.size > 0;
    const roleFilterActive = roleFilter.size > 0;
    const familyFilterActive = familyFilter.size > 0;
    const layerFilterActive = layerFilter.size > 0;
    const effectFilterActive = effectFilter.size > 0;

    const filterSummary = {
        active: {
            tier: tierFilter.size,
            ring: ringFilter.size,
            role: roleFilter.size,
            family: familyFilter.size,
            layer: layerFilter.size,
            effect: effectFilter.size
        },
        ringValues: ringFilterValues.slice().sort(),
        availableRings,
        ringIntersectionSize: ringIntersection.length
    };
    const filterSummaryKey = JSON.stringify(filterSummary);
    if (filterSummaryKey !== LAST_FILTER_SUMMARY) {
        console.log('[Filters] summary', filterSummary);
        LAST_FILTER_SUMMARY = filterSummaryKey;
    }

    visibleNodes = visibleNodes.filter(n => {
        if (tierFilterActive && !tierFilter.has(getNodeTier(n))) return false;
        if (ringFilterActive && !ringFilter.has(getNodeRing(n))) return false;
        if (roleFilterActive && !roleFilter.has(String(n.role || 'Unknown'))) return false;
        if (familyFilterActive && !familyFilter.has(getNodeAtomFamily(n))) return false;
        if (layerFilterActive && !layerFilter.has(getNodeLayer(n))) return false;
        if (effectFilterActive && !effectFilter.has(getNodeEffect(n))) return false;
        return true;
    });



    // Zero-node protection: warn when dimension filters result in empty graph
    if (visibleNodes.length === 0 && (tierFilterActive || ringFilterActive || roleFilterActive || familyFilterActive || layerFilterActive || effectFilterActive)) {
        const activeFilters = [];
        if (tierFilterActive) activeFilters.push(`tiers: [${Array.from(tierFilter).join(', ')}]`);
        if (ringFilterActive) activeFilters.push(`rings: [${Array.from(ringFilter).join(', ')}]`);
        if (roleFilterActive) activeFilters.push(`roles: [${Array.from(roleFilter).join(', ')}]`);
        if (familyFilterActive) activeFilters.push(`families: [${Array.from(familyFilter).join(', ')}]`);
        if (layerFilterActive) activeFilters.push(`layers: [${Array.from(layerFilter).join(', ')}]`);
        if (effectFilterActive) activeFilters.push(`effects: [${Array.from(effectFilter).join(', ')}]`);
        console.warn('[filterGraph] Zero nodes match filters:', activeFilters.join(', '));
    }

    const visibleIds = new Set(visibleNodes.map(n => n.id));

    // Keep edges only between visible nodes
    let visibleLinks = allLinks.filter(l =>
        visibleIds.has(l.source.id || l.source) &&
        visibleIds.has(l.target.id || l.target)
    );

    if (edgeFilter.size > 0) {
        visibleLinks = visibleLinks.filter(l => edgeFilter.has(String(l.edge_type || l.type || 'default')));
    }

    if (edgeFamilyFilter.size > 0) {
        visibleLinks = visibleLinks.filter(l => edgeFamilyFilter.has(l.family || 'Dependency'));
    }

    if (!showEdges) {
        visibleLinks = [];
    }

    return { nodes: visibleNodes, links: visibleLinks };
}

// ====================================================================
// LAYOUT STABILITY: Preserve node positions across graph updates
// ====================================================================
function saveNodePositions() {
    if (!Graph) return;
    const nodes = Graph.graphData().nodes || [];
    nodes.forEach(node => {
        if (node.x !== undefined && node.y !== undefined) {
            NODE_POSITION_CACHE.set(node.id, {
                x: node.x, y: node.y, z: node.z || 0,
                vx: node.vx || 0, vy: node.vy || 0, vz: node.vz || 0,
                fx: node.fx, fy: node.fy, fz: node.fz
            });
        }
    });
}

function restoreNodePositions(nodes) {
    nodes.forEach(node => {
        const cached = NODE_POSITION_CACHE.get(node.id);
        if (cached) {
            node.x = cached.x;
            node.y = cached.y;
            node.z = cached.z;
            node.vx = cached.vx;
            node.vy = cached.vy;
            node.vz = cached.vz;
            // Pin nodes in place when layout is frozen
            if (LAYOUT_FROZEN) {
                node.fx = cached.x;
                node.fy = cached.y;
                node.fz = cached.z;
            }
        }
    });
}

function freezeLayout() {
    LAYOUT_FROZEN = true;
    if (!Graph) return;
    const nodes = Graph.graphData().nodes || [];
    nodes.forEach(node => {
        if (node.x !== undefined) {
            node.fx = node.x;
            node.fy = node.y;
            node.fz = node.z;
        }
    });
    Graph.cooldownTicks(0);  // Stop simulation immediately
}

function unfreezeLayout() {
    LAYOUT_FROZEN = false;
    if (!Graph) return;
    const nodes = Graph.graphData().nodes || [];
    nodes.forEach(node => {
        node.fx = undefined;
        node.fy = undefined;
        node.fz = undefined;
    });
}

function resetLayout() {
    // Clear position cache and reheat simulation
    NODE_POSITION_CACHE.clear();
    unfreezeLayout();
    if (Graph) {
        Graph.cooldownTicks(200);  // Allow simulation to run
        Graph.d3ReheatSimulation();
    }
    showModeToast('Layout reset - physics running');
}

// ====================================================================
// MODE TOASTS: Brief hints when changing modes
// ====================================================================
let _toastTimeout = null;

function showModeToast(message) {
    if (!HINTS_ENABLED) return;

    let toast = document.getElementById('mode-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'mode-toast';
        toast.className = 'mode-toast';
        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.classList.add('visible');

    if (_toastTimeout) clearTimeout(_toastTimeout);
    _toastTimeout = setTimeout(() => {
        toast.classList.remove('visible');
    }, 1200);
}

function getLinkEndpointId(link, side) {
    const endpoint = link?.[side];
    if (endpoint && typeof endpoint === 'object') {
        return endpoint.id || endpoint;
    }
    return endpoint;
}

function getFileTarget(fileIdx, totalFiles, radius, zSpacing) {
    if (totalFiles <= 0) {
        return { x: 0, y: 0, z: 0 };
    }
    const angle = (fileIdx / totalFiles) * Math.PI * 2;
    return {
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius,
        z: IS_3D ? (fileIdx - totalFiles / 2) * zSpacing : 0
    };
}

function stableOffset(node, salt, radius) {
    const angle = stableSeed(node, `${salt}:angle`) * Math.PI * 2;
    const spread = 0.3 + stableSeed(node, `${salt}:radius`) * 0.7;
    const zJitter = (stableSeed(node, `${salt}:z`) - 0.5) * radius * 0.6;
    const dist = radius * spread;
    return {
        x: Math.cos(angle) * dist,
        y: Math.sin(angle) * dist,
        z: zJitter
    };
}

function buildFileGraph(data) {
    // ALL DATA FROM DM (data param kept for backward compatibility)
    const boundaries = DM ? DM.getFileBoundaries() : (data?.file_boundaries || []);
    const nodes = DM ? DM.getNodes() : (data?.nodes || []);
    const links = DM ? DM.getLinks() : (data?.links || []);

    const totalFiles = boundaries.length;
    const fileNodes = [];
    const fileNodeIds = new Map();
    const nodeFileIdx = new Map();

    nodes.forEach(n => {
        if (n && n.id) {
            nodeFileIdx.set(n.id, n.fileIdx ?? -1);
        }
    });

    boundaries.forEach((boundary, idx) => {
        const label = boundary.file_name || boundary.file || `file-${idx}`;
        const atomCount = boundary.atom_count || 1;
        const nodeId = `file:${idx}`;
        fileNodeIds.set(idx, nodeId);
        fileNodes.push({
            id: nodeId,
            name: label,
            fileIdx: idx,
            isFileNode: true,
            val: Math.max(2, Math.sqrt(atomCount)),
            color: getFileColor(idx, totalFiles, label),
            file_path: boundary.file || '',
            atom_count: atomCount
        });
    });

    const edgeMap = new Map();
    links.forEach(link => {
        const srcId = getLinkEndpointId(link, 'source');
        const tgtId = getLinkEndpointId(link, 'target');
        const srcIdx = nodeFileIdx.get(srcId) ?? -1;
        const tgtIdx = nodeFileIdx.get(tgtId) ?? -1;
        if (srcIdx < 0 || tgtIdx < 0 || srcIdx === tgtIdx) return;
        const key = `${srcIdx}->${tgtIdx}`;
        const existing = edgeMap.get(key) || {
            source: fileNodeIds.get(srcIdx),
            target: fileNodeIds.get(tgtIdx),
            weight: 0,
            edge_type: 'file',
            resolution: 'file'
        };
        existing.weight += 1;
        edgeMap.set(key, existing);
    });

    FILE_NODE_IDS = fileNodeIds;
    return {
        nodes: fileNodes,
        links: Array.from(edgeMap.values())
    };
}

function captureFileNodePositions() {
    FILE_NODE_POSITIONS = new Map();
    const nodes = (Graph && Graph.graphData().nodes) ? Graph.graphData().nodes : [];
    nodes.forEach(node => {
        if (node && node.isFileNode && Number.isFinite(node.x) && Number.isFinite(node.y)) {
            FILE_NODE_POSITIONS.set(node.fileIdx, {
                x: node.x,
                y: node.y,
                z: Number.isFinite(node.z) ? node.z : 0
            });
        }
    });
}

function buildHybridGraph(data) {
    // ALL DATA FROM DM - the reaction chamber for data chemistry
    if (!FILE_GRAPH) {
        FILE_GRAPH = buildFileGraph(data);
    }
    const boundaries = DM ? DM.getFileBoundaries() : (data?.file_boundaries || []);
    const nodes = DM ? DM.getNodes() : (data?.nodes || []);
    const links = DM ? DM.getLinks() : (data?.links || []);

    const totalFiles = boundaries.length;
    const clusterConfig = data?.physics?.cluster || {};
    const detachRadius = (typeof clusterConfig.radius === 'number') ? clusterConfig.radius * 1.3 : 200;
    const detachZ = (typeof clusterConfig.zSpacing === 'number') ? clusterConfig.zSpacing * 2 : 80;
    const expandRadius = 30;
    const expandedSet = new Set(EXPANDED_FILES);

    const fileNodes = FILE_GRAPH.nodes.map(node => {
        const copy = Object.assign({}, node);
        const anchor = FILE_NODE_POSITIONS.get(node.fileIdx) || getFileTarget(node.fileIdx, totalFiles, 140, 30);
        const detachOffset = (FILE_EXPAND_MODE === 'detach' && expandedSet.has(node.fileIdx))
            ? getFileTarget(node.fileIdx, totalFiles, detachRadius, detachZ)
            : { x: 0, y: 0, z: 0 };
        copy.x = anchor.x + detachOffset.x;
        copy.y = anchor.y + detachOffset.y;
        copy.z = (anchor.z || 0) + detachOffset.z;
        return copy;
    });

    const nodeFileIdx = new Map();
    nodes.forEach(n => {
        if (n && n.id) {
            nodeFileIdx.set(n.id, n.fileIdx ?? -1);
        }
    });

    const childNodes = [];
    nodes.forEach(node => {
        if (!expandedSet.has(node.fileIdx)) return;
        const anchor = FILE_NODE_POSITIONS.get(node.fileIdx) || getFileTarget(node.fileIdx, totalFiles, 140, 30);
        const detachOffset = (FILE_EXPAND_MODE === 'detach')
            ? getFileTarget(node.fileIdx, totalFiles, detachRadius, detachZ)
            : { x: 0, y: 0, z: 0 };
        const local = stableOffset(node, `file-${node.fileIdx}`, expandRadius);
        const copy = Object.assign({}, node);
        copy.x = anchor.x + detachOffset.x + local.x;
        copy.y = anchor.y + detachOffset.y + local.y;
        copy.z = (anchor.z || 0) + detachOffset.z + (IS_3D ? local.z : 0);
        childNodes.push(copy);
    });

    const childLinks = [];
    links.forEach(link => {
        const srcId = getLinkEndpointId(link, 'source');
        const tgtId = getLinkEndpointId(link, 'target');
        const srcIdx = nodeFileIdx.get(srcId) ?? -1;
        const tgtIdx = nodeFileIdx.get(tgtId) ?? -1;
        if (srcIdx < 0 || tgtIdx < 0 || srcIdx !== tgtIdx) return;
        if (!expandedSet.has(srcIdx)) return;
        childLinks.push({
            source: srcId,
            target: tgtId,
            color: link.color,
            opacity: link.opacity,
            edge_type: link.edge_type,
            weight: link.weight,
            confidence: link.confidence,
            resolution: link.resolution
        });
    });

    return {
        nodes: fileNodes.concat(childNodes),
        links: FILE_GRAPH.links.concat(childLinks)
    };
}

function setupControls(data) {
    // Initialize the Unified UI Manager
    UIManager.init(data);

    // Initialize Smart Text Placement
    HudLayoutManager.init();

    // Initialize Command Bar and Floating Panels
    initCommandBar();

    // Initialize Selection Detail Modal
    initSelectionModal();

    // Render color-coded legends with counts
    renderAllLegends();

    // Flow mode button (attached here for proper DOM timing)
    const btnFlow = document.getElementById('btn-flow');
    if (btnFlow) btnFlow.onclick = () => toggleFlowMode();
}

/**
 * =================================================================
 * UIManager: Orchestrates the "One Dock" unified interface
 * =================================================================
 */
const UIManager = {
    data: null,

    init(data) {
        this.data = data;
        this.setupSidebar();
        this.setupDock();
        this.setupModes();
        this.populateFilters();
        this.updateStatus();
    },

    setupSidebar() {
        const sidebar = document.getElementById('sidebar');
        const btnFilters = document.getElementById('btn-filters');
        const btnClose = document.getElementById('sidebar-close');

        // Toggle Sidebar
        const toggle = () => {
            sidebar.classList.toggle('open');
            this.updateFilterBadge();
        };

        if (btnFilters) btnFilters.onclick = (e) => {
            e.stopPropagation();
            toggle();
        };
        if (btnClose) btnClose.onclick = () => sidebar.classList.remove('open');

        // Accordion Logic
        document.querySelectorAll('.accordion-header').forEach(header => {
            header.onclick = () => {
                const accordion = header.parentElement;
                // Optional: Close others for "exclusive" behavior
                // document.querySelectorAll('.accordion').forEach(a => {
                //    if(a !== accordion) a.classList.remove('open');
                // });
                accordion.classList.toggle('open');
            };
        });
    },

    setupDock() {
        // Note: Density slider now in floating panel (density-slider2), set up in setupFloatingPanels()

        // Reset Layout
        const btnReset = document.getElementById('btn-reset-layout');
        if (btnReset) btnReset.onclick = () => {
            Graph.zoomToFit(1000);
        };

        // Stars Toggle
        const btnStars = document.getElementById('btn-stars');
        if (btnStars) btnStars.onclick = () => {
            if (typeof toggleStarfield === 'function') {
                toggleStarfield();
                btnStars.classList.toggle('active');
            }
        };

        // Dimensions Toggle (2D/3D - stub for now)
        const btnDim = document.getElementById('btn-dimensions');
        if (btnDim) btnDim.onclick = () => {
            console.log("Dimension toggle requested");
            // Future: Switch visualization engine
        };

        // Report Button
        const btnReport = document.getElementById('btn-report');
        if (btnReport) btnReport.onclick = () => {
            const reportPanel = document.getElementById('report-panel');
            if (reportPanel) {
                const isHidden = reportPanel.style.display === 'none';
                reportPanel.style.display = isHidden ? 'block' : 'none';
                btnReport.classList.toggle('active', isHidden);
            }
        };
    },

    setupModes() {
        const modes = ['explore', 'files', 'flow'];

        const setMode = (mode) => {
            // Update buttons
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById(`mode-${mode}`);
            if (activeBtn) activeBtn.classList.add('active');

            // Show specific controls
            document.querySelectorAll('.mode-control-group').forEach(g => g.style.display = 'none');
            const group = document.getElementById(`${mode}-controls`);
            if (group) group.style.display = 'flex';

            // Set global mode flags if needed
            if (mode === 'files') {
                // Enable file hulls or specific rendering
            }
        };

        modes.forEach(mode => {
            const btn = document.getElementById(`mode-${mode}`);
            if (btn) btn.onclick = () => setMode(mode);
        });

        // Files Sub-controls wiring
        const bindToggle = (id, onClick) => {
            const el = document.getElementById(id);
            if (el) el.onclick = (e) => {
                e.target.classList.toggle('active');
                if (onClick) onClick(e.target.classList.contains('active'));
            };
        };

        bindToggle('btn-file-hulls', (active) => {
            // Toggle hull visibility
            // if(active) showHulls(); else hideHulls();
        });
    },

    populateFilters() {
        const data = this.data;
        if (!data) return;

        // --- Helper: Create Filter Chips ---
        const createChips = (containerId, counts, activeSet) => {
            const container = document.getElementById(containerId);
            if (!container) return;
            container.innerHTML = ''; // Clear previous

            counts.forEach(([key, count]) => {
                const chip = document.createElement('div');
                const isActive = activeSet.has(key);
                chip.className = `filter-chip ${isActive ? 'active' : ''}`;
                chip.innerHTML = `${key} <span class=\"chip-count\">${count}</span>`;
                chip.onclick = () => {
                    if (activeSet.has(key)) activeSet.delete(key);
                    else activeSet.add(key);

                    chip.classList.toggle('active');
                    this.updateFilterBadge();
                    // DEBOUNCE REFRESH if needed, otherwise immediate
                    refreshGraph();
                };
                container.appendChild(chip);
            });

            // Update the accordion header count
            const type = containerId.replace('filter-', '');
            const countEl = document.getElementById(`count-${type}`);
            if (countEl) countEl.innerText = activeSet.size;
        };

        // 1. LAYERS (Rings)
        const ringCounts = collectCounts(data.nodes, n => getNodeRing(n));
        const rawRingDefaults = data.controls?.filters?.rings || [];
        const ringDefaults = rawRingDefaults
            .map(v => normalizeRingValue(v))
            .filter(v => v !== null);
        // Ensure defaults are populated if set is empty
        if (VIS_FILTERS.rings.size === 0 && ringDefaults.length > 0) {
            const availableRings = new Set(ringCounts.map(([ring]) => ring));
            const matchedRings = ringDefaults.filter(r => availableRings.has(r));
            if (matchedRings.length > 0) {
                matchedRings.forEach(r => VIS_FILTERS.rings.add(r));
            } else {
                const familyCounts = collectCounts(data.nodes, n => getNodeAtomFamily(n));
                const availableFamilies = new Set(familyCounts.map(([family]) => family));
                const matchedFamilies = ringDefaults.filter(f => availableFamilies.has(f));
                if (matchedFamilies.length > 0 && VIS_FILTERS.families.size === 0) {
                    matchedFamilies.forEach(f => VIS_FILTERS.families.add(f));
                    console.warn('[Filters] Ring defaults matched families; applying as family filters.', {
                        defaults: ringDefaults
                    });
                } else {
                    console.warn('[Filters] Ring defaults did not match dataset rings; leaving rings unfiltered.', {
                        defaults: ringDefaults,
                        available: Array.from(availableRings)
                    });
                }
            }
        }
        createChips('filter-rings', ringCounts, VIS_FILTERS.rings);

        // 2. TIERS
        const tierCounts = collectCounts(data.nodes, n => getNodeTier(n));
        createChips('filter-tiers', tierCounts, VIS_FILTERS.tiers);

        // 3. ROLES
        const roleCounts = collectCounts(data.nodes, n => String(n.role || 'Unknown'));
        createChips('filter-roles', roleCounts, VIS_FILTERS.roles);

        // 4. EDGES
        const edgeCounts = collectCounts(data.links, l => String(l.edge_type || l.type || 'default'));
        createChips('filter-edges', edgeCounts, VIS_FILTERS.edges);

        // 5. DATAMAPS
        this.populateDatamaps();

        // Initial Badge Update
        this.updateFilterBadge();
    },

    populateDatamaps() {
        const container = document.getElementById('filter-datamaps');
        if (!container) return;
        container.innerHTML = '';

        const controls = this.data.controls || {};
        const configs = resolveDatamapConfigs(controls); // Assuming this helper exists globally

        // Add "Global" toggles (e.g. ALL / NONE) if needed
        // For now, just the list

        configs.forEach(cfg => {
            const chip = document.createElement('div');
            const isActive = ACTIVE_DATAMAPS.has(cfg.id);
            chip.className = `filter-chip ${isActive ? 'active' : ''}`;
            chip.style.width = '100%'; // Full width for datamaps
            chip.style.marginBottom = '4px';
            chip.innerHTML = `${cfg.label}`;

            chip.onclick = () => {
                // Exclusive toggle? Or additive? 
                // Using additive for consistency, or setDatamap implementation
                setDatamap(cfg.id); // This function usually clears others

                // Update UI state manually since visualization state changed
                // (In a reactive framework this would be automatic)
                Array.from(container.children).forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
            };
            container.appendChild(chip);
        });

        if (document.getElementById('count-datamaps')) {
            document.getElementById('count-datamaps').innerText = configs.length;
        }
    },

    updateFilterBadge() {
        // Count active chips in visual filters
        let total = 0;
        // Just summing strict filter sets size might be misleading if "all selected" means 0 filtering
        // But for UI feedback:
        total += VIS_FILTERS.rings.size;
        total += VIS_FILTERS.tiers.size;
        total += VIS_FILTERS.roles.size;

        const badge = document.getElementById('filter-badge');
        const miniBadge = document.getElementById('filter-badge-mini');

        if (badge) badge.innerText = total;
        if (miniBadge) {
            miniBadge.innerText = total;
            miniBadge.classList.toggle('visible', total > 0);
        }

        const summary = document.getElementById('filter-summary');
        if (summary) {
            summary.innerText = total > 0 ? `${total} filters active` : "No filters active";
        }
    },

    updateStatus() {
        if (this.data && this.data.nodes) {
            const n = this.data.nodes.length;
            const e = this.data.links.length;
            const statusNodes = document.getElementById('status-nodes');
            const statusEdges = document.getElementById('status-edges');

            if (statusNodes) statusNodes.innerText = n;
            if (statusEdges) statusEdges.innerText = e;
        }
    }
};

function refreshGraph() {
    if (!DM || !Graph) return;  // ALL DATA FROM DM

    // LAYOUT STABILITY: Save current positions before any graph update
    saveNodePositions();

    if (GRAPH_MODE === 'files') {
        if (!FILE_GRAPH) {
            FILE_GRAPH = buildFileGraph(null);  // Uses DM internally
        }
        restoreNodePositions(FILE_GRAPH.nodes);
        Graph.graphData(FILE_GRAPH);
        applyFileColors(FILE_GRAPH.nodes);
        Graph.nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale);
        Graph.nodeLabel('name');
        applyEdgeMode();
        updateDatamapControls();
        syncSelectionAfterGraphUpdate();
        if (LAYOUT_FROZEN) freezeLayout();
        return;
    }

    if (GRAPH_MODE === 'hybrid') {
        const hybrid = buildHybridGraph(null);  // Uses DM internally
        restoreNodePositions(hybrid.nodes);
        Graph.graphData(hybrid);
        applyFileColors(hybrid.nodes);
        Graph.nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale);
        Graph.nodeLabel(VIS_FILTERS.metadata.showLabels ? 'name' : '');
        applyEdgeMode();
        updateDatamapControls();
        syncSelectionAfterGraphUpdate();
        if (LAYOUT_FROZEN) freezeLayout();
        return;
    }

    const subset = filterGraph(null, CURRENT_DENSITY, ACTIVE_DATAMAPS, VIS_FILTERS);  // Uses DM internally
    if (ACTIVE_DATAMAPS.size > 0 && subset.nodes.length === 0) {
        showToast('No nodes for that datamap selection.');
        ACTIVE_DATAMAPS.clear();
        const fallback = filterGraph(null, CURRENT_DENSITY, new Set(), VIS_FILTERS);  // Uses DM internally
        restoreNodePositions(fallback.nodes);
        Graph.graphData(fallback);
        applyNodeColors(fallback.nodes);
        // Force re-evaluation of accessors
        Graph.nodeColor(Graph.nodeColor());
        Graph.nodeRelSize(Graph.nodeRelSize());
        Graph.nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale);
        Graph.nodeLabel(VIS_FILTERS.metadata.showLabels ? 'name' : '');
        applyEdgeMode();
        if (fileMode && GRAPH_MODE === 'atoms') {
            applyFileVizMode();
        }
        updateDatamapControls();
        syncSelectionAfterGraphUpdate();
        if (LAYOUT_FROZEN) freezeLayout();
        return;
    }

    // Zero-node protection for VIS_FILTERS (tier/ring/family/role)
    const hasActiveFilters = VIS_FILTERS.tiers.size > 0 || VIS_FILTERS.rings.size > 0 ||
                             VIS_FILTERS.families.size > 0 || VIS_FILTERS.roles.size > 0;
    if (subset.nodes.length === 0 && hasActiveFilters) {
        showToast('No nodes match current filters. Clearing filters.');
        clearAllFilters();
        const fallback = filterGraph(null, CURRENT_DENSITY, ACTIVE_DATAMAPS, VIS_FILTERS);
        restoreNodePositions(fallback.nodes);
        Graph.graphData(fallback);
        applyNodeColors(fallback.nodes);
        Graph.nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale);
        Graph.nodeLabel(VIS_FILTERS.metadata.showLabels ? 'name' : '');
        applyEdgeMode();
        updateDatamapControls();
        syncSelectionAfterGraphUpdate();
        if (LAYOUT_FROZEN) freezeLayout();
        return;
    }

    applyNodeColors(subset.nodes);
    restoreNodePositions(subset.nodes);
    Graph.graphData(subset);
    Graph.nodeVal(node => (node.val || 1) * APPEARANCE_STATE.nodeScale);
    Graph.nodeLabel(VIS_FILTERS.metadata.showLabels ? 'name' : '');
    applyEdgeMode();
    if (fileMode && GRAPH_MODE === 'atoms') {
        applyFileVizMode();
    }
    updateDatamapControls();
    syncSelectionAfterGraphUpdate();
    if (LAYOUT_FROZEN) freezeLayout();
}

// ═══════════════════════════════════════════════════════════════════════
// 3D TOPOLOGICAL MINIMAP - Interactive filter visualization
// THE STANDARD MODEL TOPOLOGY: 16 Levels × 3 Layers × Families
// ═══════════════════════════════════════════════════════════════════════

// THE 16 ABSTRACTION LEVELS (vertical axis: L-3 to L12)
const SCALE_16_LEVELS = {
    // COSMOLOGICAL (L8-L12) - Beyond scope, shown as outer haze
    'L12': { name: 'UNIVERSE', symbol: '🌐', zone: 'COSMOLOGICAL', y: 1.4, color: { h: 260, s: 30, l: 25 } },
    'L11': { name: 'DOMAIN', symbol: '🏛️', zone: 'COSMOLOGICAL', y: 1.3, color: { h: 250, s: 35, l: 30 } },
    'L10': { name: 'ORGANIZATION', symbol: '🏢', zone: 'COSMOLOGICAL', y: 1.2, color: { h: 240, s: 40, l: 35 } },
    'L9': { name: 'PLATFORM', symbol: '☁️', zone: 'COSMOLOGICAL', y: 1.1, color: { h: 230, s: 45, l: 40 } },
    'L8': { name: 'ECOSYSTEM', symbol: '🔗', zone: 'COSMOLOGICAL', y: 1.0, color: { h: 220, s: 50, l: 45 } },
    // ARCHITECTURAL (L4-L7) - Primary visible zone (teal - virtual depths)
    'L7': { name: 'SYSTEM', symbol: '⬡', zone: 'ARCHITECTURAL', y: 0.7, color: { h: 175, s: 60, l: 52 } },
    'L6': { name: 'PACKAGE', symbol: '📦', zone: 'ARCHITECTURAL', y: 0.5, color: { h: 178, s: 62, l: 48 } },
    'L5': { name: 'FILE', symbol: '📄', zone: 'ARCHITECTURAL', y: 0.3, color: { h: 180, s: 65, l: 44 } },
    'L4': { name: 'CONTAINER', symbol: '⬢', zone: 'ARCHITECTURAL', y: 0.1, color: { h: 182, s: 68, l: 40 } },
    // SEMANTIC (L1-L3) - The operational core (silver/white - surface light)
    'L3': { name: 'NODE', symbol: '★', zone: 'SEMANTIC', y: -0.1, color: { h: 210, s: 25, l: 92 } },  // Brightest - fundamental unit
    'L2': { name: 'BLOCK', symbol: '▣', zone: 'SEMANTIC', y: -0.3, color: { h: 210, s: 30, l: 85 } },
    'L1': { name: 'STATEMENT', symbol: '─', zone: 'SEMANTIC', y: -0.5, color: { h: 210, s: 35, l: 78 } },
    // SYNTACTIC (L0) - The event horizon between meaning and data
    'L0': { name: 'TOKEN', symbol: '·', zone: 'SYNTACTIC', y: -0.7, color: { h: 60, s: 90, l: 55 } },  // Bright yellow - event horizon
    // PHYSICAL (L-1 to L-3) - The substrate (deep blue - ocean floor)
    'L-1': { name: 'CHARACTER', symbol: 'a', zone: 'PHYSICAL', y: -0.9, color: { h: 220, s: 70, l: 42 } },
    'L-2': { name: 'BYTE', symbol: '01', zone: 'PHYSICAL', y: -1.1, color: { h: 220, s: 75, l: 35 } },
    'L-3': { name: 'BIT/QUBIT', symbol: '⚡', zone: 'PHYSICAL', y: -1.3, color: { h: 220, s: 80, l: 28 } }  // Deepest
};

// THE THREE PARALLEL LAYERS (shells around the structure) - Depth/Elevation palette
const THREE_LAYERS = {
    'PHYSICAL': { order: 0, radius: 1.8, opacity: 0.15, color: { h: 220, s: 75, l: 35 }, description: 'Hardware, bits, memory, I/O' },
    'VIRTUAL': { order: 1, radius: 1.4, opacity: 0.25, color: { h: 175, s: 65, l: 45 }, description: 'Code, structures, algorithms' },
    'SEMANTIC': { order: 2, radius: 1.0, opacity: 0.35, color: { h: 210, s: 30, l: 88 }, description: 'Meaning, business logic, intent' }
};

// ═══════════════════════════════════════════════════════════════════════
// STANDARD MODEL THEORY CONTENT - Semantic descriptions for tooltips
// The codespace is a high-dimensional space where all software artifacts exist
// ═══════════════════════════════════════════════════════════════════════

const SMC_THEORY = {
    // THE THREE FUNDAMENTAL LAYERS
    layers: {
        'PHYSICAL': {
            icon: '⚡',
            title: 'Physical Layer',
            subtitle: 'The Substrate',
            body: 'The hardware reality: electrons, circuits, memory cells. Everything that exists in physical space-time.',
            theory: '"Matter is the canvas upon which computation paints its patterns."',
            examples: ['CPU registers', 'RAM cells', 'disk sectors', 'network signals']
        },
        'VIRTUAL': {
            icon: '💠',
            title: 'Virtual Layer',
            subtitle: 'The Structure',
            body: 'Pure information structures: code, data, algorithms. The mathematical forms that live in computational space.',
            theory: '"Between the physical and the meaningful lies the virtual — pure form without matter or purpose."',
            examples: ['variables', 'functions', 'classes', 'data structures']
        },
        'SEMANTIC': {
            icon: '🎯',
            title: 'Semantic Layer',
            subtitle: 'The Meaning',
            body: 'Intent and purpose: business logic, user goals, system behavior. The "why" behind the code.',
            theory: '"Semantics is where computation meets human intention — the bridge between bits and understanding."',
            examples: ['user stories', 'business rules', 'API contracts', 'domain models']
        }
    },

    // ATOM FAMILIES
    families: {
        'LOG': {
            icon: '📊',
            title: 'Logic Family',
            subtitle: 'The Reasoners',
            body: 'Elements that transform data through computation: conditionals, loops, calculations.',
            theory: '"Logic atoms are the decision-makers — they take inputs and produce outputs through transformation."',
            examples: ['if/else', 'for loops', 'calculations', 'validators']
        },
        'DAT': {
            icon: '📦',
            title: 'Data Family',
            subtitle: 'The Containers',
            body: 'Elements that hold and organize information: variables, structures, databases.',
            theory: '"Data atoms store state — they are the nouns in the grammar of code."',
            examples: ['variables', 'arrays', 'objects', 'databases']
        },
        'ORG': {
            icon: '🏗️',
            title: 'Organization Family',
            subtitle: 'The Architects',
            body: 'Elements that structure code: modules, classes, packages. They create boundaries.',
            theory: '"Organization atoms create order from chaos — the folders in the file system of abstraction."',
            examples: ['modules', 'classes', 'packages', 'namespaces']
        },
        'EXE': {
            icon: '⚙️',
            title: 'Execution Family',
            subtitle: 'The Doers',
            body: 'Elements that perform actions: function calls, I/O, system operations.',
            theory: '"Execution atoms are the verbs — where potential becomes actual."',
            examples: ['function calls', 'API requests', 'file writes', 'renders']
        },
        'EXT': {
            icon: '🔌',
            title: 'External Family',
            subtitle: 'The Connectors',
            body: 'Elements that interface with the outside: APIs, imports, system calls.',
            theory: '"External atoms are portals — they connect isolated systems into larger ecosystems."',
            examples: ['imports', 'API calls', 'env vars', 'dependencies']
        }
    },

    // TIERS
    tiers: {
        'T0': {
            icon: '🔬',
            title: 'Tier 0 — Foundation',
            subtitle: 'Low-level primitives',
            body: 'The atomic building blocks: individual statements, expressions, basic operations.',
            theory: '"T0 is where code meets silicon — the ground floor of abstraction."',
            examples: ['assignments', 'operators', 'literals', 'basic types']
        },
        'T1': {
            icon: '🔧',
            title: 'Tier 1 — Components',
            subtitle: 'Functional units',
            body: 'Grouped functionality: functions, methods, small modules.',
            theory: '"T1 is the sweet spot — complex enough to be useful, simple enough to understand."',
            examples: ['functions', 'methods', 'handlers', 'utilities']
        },
        'T2': {
            icon: '🏛️',
            title: 'Tier 2 — Architecture',
            subtitle: 'System structure',
            body: 'High-level organization: classes, modules, services. The skeleton of the codebase.',
            theory: '"T2 defines the shape of software — patterns emerge that echo through every line."',
            examples: ['classes', 'modules', 'services', 'controllers']
        }
    },

    // SPECIAL ELEMENTS
    special: {
        'core': {
            icon: '✨',
            title: 'The Nexus',
            subtitle: 'Singularity Point',
            body: 'The center of the topology: where all paths converge.',
            theory: '"Every codebase has a heart — the central modules that everything depends upon."',
            examples: ['main.js', 'app.py', 'index.ts', 'core.rs']
        },
        'elevator': {
            icon: '🚀',
            title: 'Data Elevator',
            subtitle: 'Cross-tier Highway',
            body: 'Vertical connections that move data between abstraction levels.',
            theory: '"Elevators are the call stacks of architecture."',
            examples: ['API layers', 'ORMs', 'serializers', 'adapters']
        },
        'hub-star': {
            icon: '⭐',
            title: 'Hub Node',
            subtitle: 'High-connectivity Center',
            body: 'A node with many incoming connections. Often a critical dependency.',
            theory: '"Hubs are the load-bearing walls — remove them and everything collapses."',
            examples: ['utils', 'config', 'logger', 'database']
        }
    }
};

// Tooltip state
const TOOLTIP_STATE = { visible: false, currentKey: null, element: null, hideTimeout: null };

function initTooltips() {
    TOOLTIP_STATE.element = document.getElementById('topo-tooltip');
}

function showTopoTooltip(category, key, x, y) {
    if (!TOOLTIP_STATE.element) initTooltips();
    if (!TOOLTIP_STATE.element) return;
    const content = SMC_THEORY[category]?.[key];
    if (!content) return;
    clearTimeout(TOOLTIP_STATE.hideTimeout);
    document.getElementById('tooltip-icon').textContent = content.icon || '';
    document.getElementById('tooltip-title').textContent = content.title || key;
    document.getElementById('tooltip-subtitle').textContent = content.subtitle || '';
    document.getElementById('tooltip-body').textContent = content.body || '';
    document.getElementById('tooltip-theory').textContent = content.theory || '';
    const examplesEl = document.getElementById('tooltip-examples');
    examplesEl.innerHTML = (content.examples || []).map(ex => `<span class="topo-tooltip-example">${ex}</span>`).join('');
    const tooltip = TOOLTIP_STATE.element;
    let left = x + 15, top = y + 15;
    if (left + 280 > window.innerWidth) left = x - 295;
    if (top + 200 > window.innerHeight) top = y - 215;
    if (left < 0) left = 15;
    if (top < 0) top = 15;
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
    tooltip.classList.add('visible');
    TOOLTIP_STATE.visible = true;
    TOOLTIP_STATE.currentKey = `${category}:${key}`;
}

function hideTopoTooltip(immediate = false) {
    if (!TOOLTIP_STATE.element) return;
    if (immediate) {
        TOOLTIP_STATE.element.classList.remove('visible');
        TOOLTIP_STATE.visible = false;
    } else {
        TOOLTIP_STATE.hideTimeout = setTimeout(() => {
            TOOLTIP_STATE.element.classList.remove('visible');
            TOOLTIP_STATE.visible = false;
        }, 150);
    }
}

// ZONES define which levels belong to which visual band
const LEVEL_ZONES = {
    'COSMOLOGICAL': { levels: ['L12', 'L11', 'L10', 'L9', 'L8'], opacity: 0.2, blur: true },
    'ARCHITECTURAL': { levels: ['L7', 'L6', 'L5', 'L4'], opacity: 0.6, blur: false },
    'SEMANTIC': { levels: ['L3', 'L2', 'L1'], opacity: 1.0, blur: false },        // Primary focus
    'SYNTACTIC': { levels: ['L0'], opacity: 0.8, blur: false },                   // Event horizon
    'PHYSICAL': { levels: ['L-1', 'L-2', 'L-3'], opacity: 0.4, blur: true }
};

const TOPO_COLORS = {
    // Tiers: Map to operational zones (T0=Semantic, T1=Architectural, T2=External)
    tiers: {
        'T0': { h: 200, s: 80, l: 55 },  // Cyan-blue (core/semantic)
        'T1': { h: 280, s: 70, l: 50 },  // Purple (architecture)
        'T2': { h: 35, s: 85, l: 50 },   // Orange (external/ecosystem)
        'UNKNOWN': { h: 0, s: 0, l: 40 } // Gray
    },
    // Atom families: Semantic domains - each has a distinct angular position
    families: {
        'LOG': { h: 180, s: 70, l: 45, angle: 0 },      // Teal (logic/control) - 0°
        'DAT': { h: 45, s: 80, l: 50, angle: 72 },      // Gold (data) - 72°
        'ORG': { h: 270, s: 60, l: 50, angle: 144 },    // Violet (organization) - 144°
        'EXE': { h: 120, s: 60, l: 45, angle: 216 },    // Green (execution) - 216°
        'EXT': { h: 15, s: 75, l: 50, angle: 288 },     // Orange-red (external) - 288°
        'UNKNOWN': { h: 0, s: 0, l: 35, angle: 0 }      // Gray
    },
    // Rings: Concentric semantic layers
    rings: {
        'KERNEL': { h: 200, s: 90, l: 60 },
        'CORE': { h: 220, s: 75, l: 55 },
        'SERVICE': { h: 260, s: 65, l: 50 },
        'ADAPTER': { h: 300, s: 60, l: 50 },
        'INTERFACE': { h: 340, s: 55, l: 50 },
        'EXTERNAL': { h: 20, s: 70, l: 50 },
        'UNKNOWN': { h: 0, s: 0, l: 40 }
    }
};

// ═══════════════════════════════════════════════════════════════════════
// VISUALIZATION PRESETS - Different ways to see the topology
// ═══════════════════════════════════════════════════════════════════════
const VIS_PRESETS = {
    'tier': {
        name: 'By Tier (T0/T1/T2)',
        description: 'Core → Architecture → External',
        colorBy: 'tier',
        sizeBy: 'fanout',
        edgeBy: 'type'
    },
    'family': {
        name: 'By Atom Family',
        description: 'LOG, DAT, ORG, EXE, EXT',
        colorBy: 'family',
        sizeBy: 'fanout',
        edgeBy: 'type'
    },
    'layer': {
        name: 'By Layer',
        description: 'Physical → Virtual → Semantic',
        colorBy: 'layer',
        sizeBy: 'uniform',
        edgeBy: 'resolution'
    },
    'ring': {
        name: 'By Ring (Domain)',
        description: 'Domain architecture layers',
        colorBy: 'ring',
        sizeBy: 'fanout',
        edgeBy: 'type'
    },
    'file': {
        name: 'By File',
        description: 'Each file gets unique hue',
        colorBy: 'file',
        sizeBy: 'uniform',
        edgeBy: 'resolution'
    },
    'flow': {
        name: 'Markov Flow',
        description: 'Edge width = transition probability',
        colorBy: 'tier',
        sizeBy: 'entropy',
        edgeBy: 'weight'
    },
    'depth': {
        name: 'By Depth (Call Distance)',
        description: 'Distance from entry points',
        colorBy: 'depth',
        sizeBy: 'fanout',
        edgeBy: 'type'
    },

    // ═══════════════════════════════════════════════════════════════
    // OKLCH COLOR SCHEMES - BOLD & DRAMATIC
    // Each scheme creates a distinct, unmistakable visual transformation
    // ═══════════════════════════════════════════════════════════════

    'thermal': {
        name: 'THERMAL',
        description: 'Heat signature - activity glows hot',
        colorBy: 'family',
        sizeBy: 'entropy',
        edgeBy: 'weight',
        isColorScheme: true,
        oklch: {
            L: { base: 0.70, range: 0.3 },
            C: { base: 0.25, boost: 2.2 },    // HIGH saturation
            H: { shift: -60, compress: 0.6 }, // STRONG red shift
            edgeL: 0.55, edgeC: 0.20, bgL: 0.02
        },
        amplifier: 4.0,
        lightness: 8
    },

    'spectrum': {
        name: 'SPECTRUM',
        description: 'Full rainbow - structure as color',
        colorBy: 'file',
        sizeBy: 'fanout',
        edgeBy: 'gradient-file',
        isColorScheme: true,
        oklch: {
            L: { base: 0.75, range: 0.15 },
            C: { base: 0.30, boost: 2.5 },    // MAXIMUM chroma
            H: { shift: 0, compress: 1.0 },
            edgeL: 0.65, edgeC: 0.25, bgL: 0.01
        },
        amplifier: 3.0,
        lightness: 12
    },

    'neon': {
        name: 'NEON',
        description: 'Cyberpunk - electric on void',
        colorBy: 'family',
        sizeBy: 'fanout',
        edgeBy: 'gradient-tier',
        isColorScheme: true,
        oklch: {
            L: { base: 0.82, range: 0.2 },    // VERY bright
            C: { base: 0.35, boost: 2.8 },    // EXTREME chroma
            H: { shift: 180, compress: 0.8 }, // Cyan/magenta
            edgeL: 0.75, edgeC: 0.30, bgL: 0.0
        },
        amplifier: 5.0,
        lightness: 18
    },

    'ocean': {
        name: 'OCEAN',
        description: 'Deep sea - cool depths',
        colorBy: 'ring',
        sizeBy: 'uniform',
        edgeBy: 'gradient-file',
        isColorScheme: true,
        oklch: {
            L: { base: 0.55, range: 0.25 },
            C: { base: 0.22, boost: 1.8 },
            H: { shift: 200, compress: 0.4 }, // STRONG blue shift
            edgeL: 0.50, edgeC: 0.18, bgL: 0.02
        },
        amplifier: 2.5,
        lightness: -5
    },

    'plasma': {
        name: 'PLASMA',
        description: 'Energy field - purple/pink plasma',
        colorBy: 'tier',
        sizeBy: 'entropy',
        edgeBy: 'gradient-flow',
        isColorScheme: true,
        oklch: {
            L: { base: 0.72, range: 0.22 },
            C: { base: 0.28, boost: 2.4 },    // HIGH saturation
            H: { shift: 280, compress: 0.5 }, // STRONG purple shift
            edgeL: 0.62, edgeC: 0.24, bgL: 0.01
        },
        amplifier: 4.5,
        lightness: 10
    },

    'matrix': {
        name: 'MATRIX',
        description: 'Hacker - phosphor green glow',
        colorBy: 'tier',
        sizeBy: 'fanout',
        edgeBy: 'type',
        isColorScheme: true,
        oklch: {
            L: { base: 0.68, range: 0.3 },
            C: { base: 0.26, boost: 2.2 },
            H: { shift: 130, compress: 0.3 }, // STRONG green shift
            edgeL: 0.55, edgeC: 0.22, bgL: 0.0
        },
        amplifier: 4.0,
        lightness: 5
    },

    'infrared': {
        name: 'INFRARED',
        description: 'Night vision - heat on black',
        colorBy: 'file',
        sizeBy: 'entropy',
        edgeBy: 'weight',
        isColorScheme: true,
        oklch: {
            L: { base: 0.60, range: 0.35 },
            C: { base: 0.24, boost: 2.0 },
            H: { shift: -90, compress: 0.4 }, // Red/orange/yellow
            edgeL: 0.50, edgeC: 0.20, bgL: 0.0
        },
        amplifier: 5.0,
        lightness: -2
    },

    'aurora': {
        name: 'AURORA',
        description: 'Northern lights - ethereal shimmer',
        colorBy: 'ring',
        sizeBy: 'fanout',
        edgeBy: 'gradient-tier',
        isColorScheme: true,
        oklch: {
            L: { base: 0.75, range: 0.18 },
            C: { base: 0.28, boost: 2.3 },
            H: { shift: 150, compress: 0.7 }, // Green → cyan → purple
            edgeL: 0.65, edgeC: 0.24, bgL: 0.01
        },
        amplifier: 3.5,
        lightness: 12
    }
};

// ═══════════════════════════════════════════════════════════════════════
// LAYOUT PRESETS - Geometric arrangements of nodes in 3D space
// ═══════════════════════════════════════════════════════════════════════

let CURRENT_LAYOUT = 'force';
let LAYOUT_ANIMATION_ID = null;
let LAYOUT_TIME = 0;

const LAYOUT_PRESETS = {
    'force': { name: 'FORCE', icon: '🌀', description: 'Physics-based clustering', motion: 'settle', cooldown: 300, warmupTicks: 40, getPosition: null },
    'orbital': {
        name: 'ORBITAL', icon: '🪐', description: 'Planetary orbit bands', motion: 'orbit', cooldown: Infinity, orbitSpeed: 0.002,
        getPosition: (node, idx, total, time) => {
            const tier = getNodeTier(node), family = getNodeAtomFamily(node);
            const r = { T0: 80, T1: 160, T2: 280, UNKNOWN: 200 }[tier] || 200;
            const fOff = { LOG: 0, DAT: 1, ORG: 2, EXE: 3, EXT: 4, UNKNOWN: 2.5 }[family] || 0;
            const angle = (fOff / 5) * Math.PI * 2 + (idx / Math.max(1, total)) * Math.PI * 0.3 + (time || 0) * (0.5 + r * 0.001);
            const wobble = Math.sin(idx * 0.7 + (time || 0) * 2) * 15;
            return { x: Math.cos(angle) * (r + wobble), y: Math.sin(idx * 0.3) * 40 + (tier === 'T0' ? -50 : tier === 'T2' ? 50 : 0), z: Math.sin(angle) * (r + wobble) };
        }
    },
    'radial': {
        name: 'RADIAL', icon: '🎯', description: 'Concentric tier rings', motion: 'static', cooldown: 0,
        getPosition: (node, idx, total, time, tierGroups) => {
            const tier = getNodeTier(node), r = { T0: 60, T1: 150, T2: 280, UNKNOWN: 220 }[tier] || 180;
            const tierNodes = tierGroups?.[tier] || [], tierIdx = tierNodes.indexOf(node), tierTotal = tierNodes.length || 1;
            const angle = (tierIdx / tierTotal) * Math.PI * 2;
            return { x: Math.cos(angle) * r, y: 0, z: Math.sin(angle) * r };
        }
    },
    'spiral': {
        name: 'SPIRAL', icon: '🧬', description: 'DNA-like helix', motion: 'rotate', cooldown: Infinity, rotateSpeed: 0.003,
        getPosition: (node, idx, total, time) => {
            const t = idx / Math.max(1, total), angle = t * Math.PI * 2 * 4 + (time || 0), r = 100 + t * 150;
            return { x: Math.cos(angle) * r, y: (t - 0.5) * 400, z: Math.sin(angle) * r };
        }
    },
    'sphere': {
        name: 'SPHERE', icon: '🌍', description: 'Globe surface', motion: 'rotate', cooldown: Infinity, rotateSpeed: 0.001,
        getPosition: (node, idx, total, time) => {
            const tier = getNodeTier(node), family = getNodeAtomFamily(node);
            const latBase = { T0: 0.8, T1: 0.5, T2: 0.2, UNKNOWN: 0.5 }[tier] || 0.5;
            const lat = (latBase + (idx % 10) * 0.02) * Math.PI;
            const lonBase = { LOG: 0, DAT: 72, ORG: 144, EXE: 216, EXT: 288, UNKNOWN: 180 }[family] || 0;
            const lon = ((lonBase + idx * 3) % 360) * Math.PI / 180 + (time || 0), r = 200;
            return { x: Math.sin(lat) * Math.cos(lon) * r, y: Math.cos(lat) * r, z: Math.sin(lat) * Math.sin(lon) * r };
        }
    },
    'torus': {
        name: 'TORUS', icon: '🍩', description: 'Donut surface', motion: 'rotate', cooldown: Infinity, rotateSpeed: 0.002,
        getPosition: (node, idx, total, time) => {
            const tier = getNodeTier(node), family = getNodeAtomFamily(node), majorR = 180, minorR = 70;
            const famAngle = { LOG: 0, DAT: 72, ORG: 144, EXE: 216, EXT: 288, UNKNOWN: 0 }[family] || 0;
            const u = (famAngle * Math.PI / 180) + (idx * 0.05) + (time || 0);
            const tierV = { T0: 0.25, T1: 0.5, T2: 0.75, UNKNOWN: 0.5 }[tier] || 0.5;
            const v = tierV * Math.PI * 2 + Math.sin(idx * 0.2) * 0.3;
            return { x: (majorR + minorR * Math.cos(v)) * Math.cos(u), y: minorR * Math.sin(v), z: (majorR + minorR * Math.cos(v)) * Math.sin(u) };
        }
    },
    'grid': {
        name: 'GRID', icon: '📊', description: '3D lattice', motion: 'static', cooldown: 0,
        getPosition: (node, idx, total) => {
            const tier = getNodeTier(node), family = getNodeAtomFamily(node);
            const tierX = { T0: -150, T1: 0, T2: 150, UNKNOWN: 0 }[tier] || 0;
            const famZ = { LOG: -120, DAT: -60, ORG: 0, EXE: 60, EXT: 120, UNKNOWN: 0 }[family] || 0;
            const row = Math.floor(idx / 15), col = idx % 15;
            return { x: tierX + (col - 7) * 20, y: row * 25 - 100, z: famZ + Math.sin(idx * 0.5) * 20 };
        }
    },
    'cylinder': {
        name: 'CYLINDER', icon: '🗼', description: 'Vertical tube', motion: 'rotate', cooldown: Infinity, rotateSpeed: 0.0015,
        getPosition: (node, idx, total, time) => {
            const tier = getNodeTier(node), family = getNodeAtomFamily(node);
            const famAngle = { LOG: 0, DAT: 72, ORG: 144, EXE: 216, EXT: 288, UNKNOWN: 0 }[family] || 0;
            const angle = (famAngle * Math.PI / 180) + (idx * 0.1) + (time || 0);
            const tierY = { T0: -120, T1: 0, T2: 120, UNKNOWN: 0 }[tier] || 0;
            return { x: Math.cos(angle) * 150, y: tierY + Math.sin(idx * 0.3) * 30, z: Math.sin(angle) * 150 };
        }
    },
    'tree': {
        name: 'TREE', icon: '🌲', description: 'Hierarchical tree', motion: 'static', cooldown: 0,
        getPosition: (node, idx, total, time, tierGroups) => {
            const tier = getNodeTier(node), tierY = { T0: 150, T1: 0, T2: -150, UNKNOWN: 0 }[tier] || 0;
            const tierNodes = tierGroups?.[tier] || [], tierIdx = tierNodes.indexOf(node), tierTotal = tierNodes.length || 1;
            const spread = 300 * (1 + (tier === 'T2' ? 0.5 : tier === 'T1' ? 0.2 : 0));
            return { x: ((tierIdx / tierTotal) - 0.5) * spread, y: tierY, z: Math.sin(tierIdx * 0.7) * 50 };
        }
    },
    'flock': {
        name: 'FLOCK', icon: '🐦', description: 'Swarming birds', motion: 'flock', cooldown: Infinity,
        flockParams: { separation: 25, alignment: 0.05, cohesion: 0.01, maxSpeed: 2 }, getPosition: null
    },
    'galaxy': {
        name: 'GALAXY', icon: '🌌', description: 'Spiral arms', motion: 'rotate', cooldown: Infinity, rotateSpeed: 0.001,
        getPosition: (node, idx, total, time) => {
            const family = getNodeAtomFamily(node), tier = getNodeTier(node);
            const armOff = { LOG: 0, DAT: 1, ORG: 2, EXE: 3, EXT: 4, UNKNOWN: 2.5 }[family] || 0;
            const baseAngle = (armOff / 5) * Math.PI * 2, dist = 50 + (idx / total) * 250;
            const spiralAngle = baseAngle + dist * 0.015 + (time || 0);
            const tierY = { T0: -30, T1: 0, T2: 30, UNKNOWN: 0 }[tier] || 0;
            return { x: Math.cos(spiralAngle) * dist, y: tierY + Math.sin(idx * 0.5) * 20, z: Math.sin(spiralAngle) * dist };
        }
    }
};

function groupNodesByTier(nodes) {
    const groups = { T0: [], T1: [], T2: [], UNKNOWN: [] };
    nodes.forEach(n => { const tier = getNodeTier(n); (groups[tier] || groups.UNKNOWN).push(n); });
    return groups;
}

function applyLayoutPreset(presetKey, animate = true) {
    const preset = LAYOUT_PRESETS[presetKey]; if (!preset) return;
    CURRENT_LAYOUT = presetKey;
    const nodes = Graph?.graphData()?.nodes || [], total = nodes.length, tierGroups = groupNodesByTier(nodes);
    if (LAYOUT_ANIMATION_ID) { cancelAnimationFrame(LAYOUT_ANIMATION_ID); LAYOUT_ANIMATION_ID = null; }
    if (presetKey === 'force') {
        nodes.forEach(n => { n.fx = undefined; n.fy = undefined; n.fz = undefined; });
        Graph.cooldownTicks(preset.cooldown); Graph.d3ReheatSimulation();
        showModeToast('🌀 FORCE layout'); return;
    }
    if (preset.getPosition) {
        const startPos = nodes.map(n => ({ x: n.x || 0, y: n.y || 0, z: n.z || 0 }));
        const targetPos = nodes.map((n, i) => preset.getPosition(n, i, total, 0, tierGroups));
        if (animate) {
            const duration = 1500, startTime = Date.now();
            function animateTransition() {
                const progress = Math.min(1, (Date.now() - startTime) / duration);
                const eased = progress * progress * (3 - 2 * progress);
                nodes.forEach((n, i) => {
                    n.fx = startPos[i].x + (targetPos[i].x - startPos[i].x) * eased;
                    n.fy = startPos[i].y + (targetPos[i].y - startPos[i].y) * eased;
                    n.fz = startPos[i].z + (targetPos[i].z - startPos[i].z) * eased;
                });
                Graph.refresh();
                if (progress < 1) requestAnimationFrame(animateTransition);
                else if (preset.motion === 'rotate' || preset.motion === 'orbit') startLayoutMotion(presetKey);
            }
            animateTransition();
        } else {
            nodes.forEach((n, i) => { const p = targetPos[i]; n.fx = p.x; n.fy = p.y; n.fz = p.z; });
            Graph.refresh();
            if (preset.motion === 'rotate' || preset.motion === 'orbit') startLayoutMotion(presetKey);
        }
    }
    if (preset.motion === 'flock') startFlockSimulation(preset.flockParams);
    Graph.cooldownTicks(preset.cooldown); showModeToast(`${preset.icon} ${preset.name} layout`);
}

function startLayoutMotion(presetKey) {
    const preset = LAYOUT_PRESETS[presetKey]; if (!preset || !preset.getPosition) return;
    const nodes = Graph?.graphData()?.nodes || [], total = nodes.length;
    const tierGroups = groupNodesByTier(nodes), speed = preset.rotateSpeed || preset.orbitSpeed || 0.002;
    function animate() {
        LAYOUT_TIME += speed;
        nodes.forEach((n, i) => { const pos = preset.getPosition(n, i, total, LAYOUT_TIME, tierGroups); n.fx = pos.x; n.fy = pos.y; n.fz = pos.z; });
        Graph.refresh(); LAYOUT_ANIMATION_ID = requestAnimationFrame(animate);
    }
    LAYOUT_ANIMATION_ID = requestAnimationFrame(animate);
}

function startFlockSimulation(params) {
    const nodes = Graph?.graphData()?.nodes || [];
    const { separation, alignment, cohesion, maxSpeed } = params;
    nodes.forEach(n => { n._vx = (Math.random() - 0.5) * 2; n._vy = (Math.random() - 0.5) * 2; n._vz = (Math.random() - 0.5) * 2; });
    function flockStep() {
        nodes.forEach(n => {
            let sepX = 0, sepY = 0, sepZ = 0, sepCount = 0, alignX = 0, alignY = 0, alignZ = 0, alignCount = 0;
            let cohX = 0, cohY = 0, cohZ = 0, cohCount = 0; const myFamily = getNodeAtomFamily(n);
            nodes.forEach(other => {
                if (other === n) return;
                const dx = (other.x || 0) - (n.x || 0), dy = (other.y || 0) - (n.y || 0), dz = (other.z || 0) - (n.z || 0);
                const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) || 0.001;
                if (dist < separation * 2) { sepX -= dx / dist; sepY -= dy / dist; sepZ -= dz / dist; sepCount++; }
                if (getNodeAtomFamily(other) === myFamily && dist < 150) {
                    alignX += other._vx || 0; alignY += other._vy || 0; alignZ += other._vz || 0; alignCount++;
                    cohX += other.x || 0; cohY += other.y || 0; cohZ += other.z || 0; cohCount++;
                }
            });
            if (sepCount > 0) { n._vx += (sepX / sepCount) * separation * 0.05; n._vy += (sepY / sepCount) * separation * 0.05; n._vz += (sepZ / sepCount) * separation * 0.05; }
            if (alignCount > 0) { n._vx += ((alignX / alignCount) - n._vx) * alignment; n._vy += ((alignY / alignCount) - n._vy) * alignment; n._vz += ((alignZ / alignCount) - n._vz) * alignment; }
            if (cohCount > 0) { n._vx += (cohX / cohCount - (n.x || 0)) * cohesion; n._vy += (cohY / cohCount - (n.y || 0)) * cohesion; n._vz += (cohZ / cohCount - (n.z || 0)) * cohesion; }
            n._vx -= (n.x || 0) * 0.0005; n._vy -= (n.y || 0) * 0.0005; n._vz -= (n.z || 0) * 0.0005;
            const speed = Math.sqrt(n._vx * n._vx + n._vy * n._vy + n._vz * n._vz);
            if (speed > maxSpeed) { n._vx = (n._vx / speed) * maxSpeed; n._vy = (n._vy / speed) * maxSpeed; n._vz = (n._vz / speed) * maxSpeed; }
            n.fx = (n.x || 0) + n._vx; n.fy = (n.y || 0) + n._vy; n.fz = (n.z || 0) + n._vz;
        });
        Graph.refresh(); LAYOUT_ANIMATION_ID = requestAnimationFrame(flockStep);
    }
    LAYOUT_ANIMATION_ID = requestAnimationFrame(flockStep);
}

const TOPO_MINIMAP = {
    scene: null,
    camera: null,
    renderer: null,
    meshes: [],
    tierRings: {},
    familySegments: {},
    animationId: null,
    container: null,
    canvas: null,
    data: null,
    rotation: 0,
    hoveredMesh: null
};

function hslToHex(h, s, l) {
    s /= 100;
    l /= 100;
    const a = s * Math.min(l, 1 - l);
    const f = n => {
        const k = (n + h / 30) % 12;
        const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        return Math.round(255 * color).toString(16).padStart(2, '0');
    };
    return parseInt(f(0) + f(8) + f(4), 16);
}

function initTopoMinimap(data) {
    const container = document.getElementById('topo-minimap');
    const canvas = document.getElementById('topo-canvas');
    if (!container || !canvas) return;

    TOPO_MINIMAP.container = container;
    TOPO_MINIMAP.canvas = canvas;
    TOPO_MINIMAP.data = data;

    // Create Three.js scene
    const width = container.clientWidth || 200;
    const height = container.clientHeight || 180;

    TOPO_MINIMAP.scene = new THREE.Scene();
    TOPO_MINIMAP.camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
    TOPO_MINIMAP.camera.position.set(0, 3.5, 4);
    TOPO_MINIMAP.camera.lookAt(0, 0, 0);

    TOPO_MINIMAP.renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true,
        alpha: true
    });
    TOPO_MINIMAP.renderer.setSize(width, height);
    TOPO_MINIMAP.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    TOPO_MINIMAP.renderer.setClearColor(0x000000, 0);

    // Add subtle ambient light
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    TOPO_MINIMAP.scene.add(ambient);

    // Add directional light for depth
    const directional = new THREE.DirectionalLight(0xffffff, 0.6);
    directional.position.set(2, 4, 3);
    TOPO_MINIMAP.scene.add(directional);

    // Build the topology visualization
    buildTopoGeometry(data);

    // Build the interactive legends
    buildTopoLegends(data);

    // Start animation
    animateTopoMinimap();

    // Add mouse interaction
    canvas.addEventListener('mousemove', onTopoMouseMove);
    canvas.addEventListener('click', onTopoClick);
    canvas.addEventListener('mouseout', onTopoMouseOut);
}

function buildTopoGeometry(data) {
    if (!data || !data.nodes) return;

    // ═══════════════════════════════════════════════════════════════
    // ANALYTICAL GEOMETRY - Calculus-based smooth parametric surface
    // Using partial derivatives for exact normals, Hermite interpolation
    // for seamless color gradients, and integral-based curvature
    // ═══════════════════════════════════════════════════════════════

    const tiers = ['T0', 'T1', 'T2'];
    const families = ['LOG', 'DAT', 'ORG', 'EXE', 'EXT'];

    // Layer definitions with smooth transition zones
    const LAYERS = [
        { name: 'PHYSICAL', color: { h: 220, s: 75, l: 35 } },
        { name: 'VIRTUAL', color: { h: 175, s: 65, l: 45 } },
        { name: 'SEMANTIC', color: { h: 210, s: 30, l: 88 } }
    ];

    // Count nodes by tier and family
    const tierFamilyCounts = new Map();
    tiers.forEach(t => {
        tierFamilyCounts.set(t, new Map());
        families.forEach(f => tierFamilyCounts.get(t).set(f, 0));
    });

    data.nodes.forEach(node => {
        const tier = getNodeTier(node);
        const family = getNodeAtomFamily(node);
        if (tierFamilyCounts.has(tier)) {
            const familyMap = tierFamilyCounts.get(tier);
            if (familyMap.has(family)) {
                familyMap.set(family, familyMap.get(family) + 1);
            }
        }
    });

    let maxCount = 1;
    tierFamilyCounts.forEach(fm => fm.forEach(c => { if (c > maxCount) maxCount = c; }));

    TOPO_MINIMAP.meshes = [];

    // ═══════════════════════════════════════════════════════════════
    // PARAMETRIC SURFACE S(u,v) - Hyperboloid of revolution
    // S(u,v) = (r(v)·cos(u), h(v), r(v)·sin(u))
    // where u ∈ [0, 2π], v ∈ [0, 1]
    // ═══════════════════════════════════════════════════════════════

    // Profile function r(v) - Hyperboloid with smooth organic variation
    // r(v) = a·cosh(k·(v - 0.5)) + density_modulation
    const a = 0.42;   // Minimum radius at waist
    const k = 1.8;    // Curvature parameter

    // Height function h(v) - Maps v to vertical position
    // h(v) = H·(v - 0.5) where H = total height
    const H = 3.0;

    // Density field D(u,v) - Smooth 2D scalar field from node counts
    // Uses bicubic interpolation for C² continuity
    function getDensity(u, v) {
        const famIdx = (u / (Math.PI * 2)) * families.length;
        const tierIdx = v * 3;

        // Bicubic kernel for smooth interpolation
        function cubic(t) {
            const at = Math.abs(t);
            if (at < 1) return (1.5 * at - 2.5) * at * at + 1;
            if (at < 2) return ((-0.5 * at + 2.5) * at - 4) * at + 2;
            return 0;
        }

        let sum = 0, weight = 0;
        for (let ti = 0; ti < 3; ti++) {
            for (let fi = 0; fi < families.length; fi++) {
                const count = tierFamilyCounts.get(tiers[ti])?.get(families[fi]) || 0;
                const wv = cubic(tierIdx - ti - 0.5);
                const wu = cubic(famIdx - fi - 0.5);
                const w = wv * wu;
                sum += count * w;
                weight += w;
            }
        }
        return weight > 0 ? sum / weight / maxCount : 0;
    }

    // Parametric surface with analytical derivatives
    function surface(u, v) {
        const density = getDensity(u, v);
        const densityMod = 1 + density * 0.18;

        // r(v) = a·cosh(k·(v - 0.5)) with density modulation
        const vCentered = v - 0.5;
        const coshVal = Math.cosh(k * vCentered);
        const r = (a * coshVal + 0.35) * densityMod;

        // h(v) = H·(v - 0.5)
        const h = H * vCentered;

        // S(u,v) = (r·cos(u), h, r·sin(u))
        return {
            x: r * Math.cos(u),
            y: h,
            z: r * Math.sin(u)
        };
    }

    // Partial derivatives for exact normals (∂S/∂u × ∂S/∂v)
    function surfaceNormal(u, v) {
        const eps = 0.001;

        // Central differences for partial derivatives
        const Su0 = surface(u - eps, v);
        const Su1 = surface(u + eps, v);
        const Sv0 = surface(u, v - eps);
        const Sv1 = surface(u, v + eps);

        // ∂S/∂u
        const dSdu = {
            x: (Su1.x - Su0.x) / (2 * eps),
            y: (Su1.y - Su0.y) / (2 * eps),
            z: (Su1.z - Su0.z) / (2 * eps)
        };

        // ∂S/∂v
        const dSdv = {
            x: (Sv1.x - Sv0.x) / (2 * eps),
            y: (Sv1.y - Sv0.y) / (2 * eps),
            z: (Sv1.z - Sv0.z) / (2 * eps)
        };

        // Cross product: ∂S/∂u × ∂S/∂v
        const nx = dSdu.y * dSdv.z - dSdu.z * dSdv.y;
        const ny = dSdu.z * dSdv.x - dSdu.x * dSdv.z;
        const nz = dSdu.x * dSdv.y - dSdu.y * dSdv.x;

        // Normalize
        const len = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
        return { x: nx / len, y: ny / len, z: nz / len };
    }

    // Hermite basis functions for C¹ continuous color interpolation
    function hermite(t) {
        const t2 = t * t;
        const t3 = t2 * t;
        return {
            h00: 2 * t3 - 3 * t2 + 1,      // Position at p0
            h10: t3 - 2 * t2 + t,        // Tangent at p0
            h01: -2 * t3 + 3 * t2,         // Position at p1
            h11: t3 - t2               // Tangent at p1
        };
    }

    // HSL to RGB (analytical)
    function hslToRgb(h, s, l) {
        s /= 100; l /= 100;
        const c = (1 - Math.abs(2 * l - 1)) * s;
        const x = c * (1 - Math.abs((h / 60) % 2 - 1));
        const m = l - c / 2;
        let r, g, b;
        if (h < 60) { r = c; g = x; b = 0; }
        else if (h < 120) { r = x; g = c; b = 0; }
        else if (h < 180) { r = 0; g = c; b = x; }
        else if (h < 240) { r = 0; g = x; b = c; }
        else if (h < 300) { r = x; g = 0; b = c; }
        else { r = c; g = 0; b = x; }
        return [r + m, g + m, b + m];
    }

    // ═══════════════════════════════════════════════════════════════
    // BUILD CONTINUOUS MESH with vertex colors
    // ═══════════════════════════════════════════════════════════════

    const uSegments = 96;   // Radial resolution (seamless wrap)
    const vSegments = 64;   // Vertical resolution

    const positions = [];
    const normals = [];
    const colors = [];
    const indices = [];

    for (let vi = 0; vi <= vSegments; vi++) {
        const v = vi / vSegments;

        // Tier blending (smooth transitions at 0.33 and 0.66)
        let tierIdx, tierBlend;
        if (v < 0.33) {
            tierIdx = 0;
            tierBlend = hermite(v / 0.33).h01;  // Fade into tier 1
        } else if (v < 0.66) {
            tierIdx = 1;
            tierBlend = hermite((v - 0.33) / 0.33).h01;  // Fade into tier 2
        } else {
            tierIdx = 2;
            tierBlend = 0;
        }

        const layerCurr = LAYERS[tierIdx];
        const layerNext = LAYERS[Math.min(tierIdx + 1, 2)];

        for (let ui = 0; ui <= uSegments; ui++) {
            const u = (ui / uSegments) * Math.PI * 2;

            // Family blending (smooth around the circle)
            const famFloat = (ui / uSegments) * families.length;
            const famIdx = Math.floor(famFloat) % families.length;
            const famNext = (famIdx + 1) % families.length;
            const famT = famFloat - Math.floor(famFloat);
            const famH = hermite(famT);
            const famBlend = famH.h01;  // Smooth transition

            // Surface position
            const pos = surface(u, v);
            positions.push(pos.x, pos.y, pos.z);

            // Analytical normal
            const norm = surfaceNormal(u, v);
            normals.push(norm.x, norm.y, norm.z);

            // === SMOOTH COLOR FIELD ===
            const famColor0 = TOPO_COLORS.families[families[famIdx]] || { h: 180, s: 50, l: 50 };
            const famColor1 = TOPO_COLORS.families[families[famNext]] || famColor0;

            // Hermite interpolation for family colors
            const famH_h = famColor0.h * (1 - famBlend) + famColor1.h * famBlend;
            const famH_s = famColor0.s * (1 - famBlend) + famColor1.s * famBlend;
            const famH_l = famColor0.l * (1 - famBlend) + famColor1.l * famBlend;

            // Hermite interpolation for layer colors
            const layH_h = layerCurr.color.h * (1 - tierBlend) + layerNext.color.h * tierBlend;
            const layH_s = layerCurr.color.s * (1 - tierBlend) + layerNext.color.s * tierBlend;
            const layH_l = layerCurr.color.l * (1 - tierBlend) + layerNext.color.l * tierBlend;

            // Blend: 55% family, 45% layer
            const density = getDensity(u, v);
            const finalH = famH_h * 0.55 + layH_h * 0.45;
            const finalS = (famH_s * 0.55 + layH_s * 0.45) * (0.75 + density * 0.25);
            const finalL = Math.min(78, (famH_l * 0.5 + layH_l * 0.5) + density * 12);

            // Subtle iridescence (view-angle dependent hue shift)
            const iridescence = 6 * Math.sin(u * 2 + v * Math.PI);

            const [r, g, b] = hslToRgb(finalH + iridescence, finalS, finalL);
            colors.push(r, g, b);
        }
    }

    // Build triangle indices (seamless wrap)
    for (let vi = 0; vi < vSegments; vi++) {
        for (let ui = 0; ui < uSegments; ui++) {
            const a = vi * (uSegments + 1) + ui;
            const b = a + 1;
            const c = a + (uSegments + 1);
            const d = c + 1;

            indices.push(a, c, b);
            indices.push(b, c, d);
        }
    }

    const shellGeom = new THREE.BufferGeometry();
    shellGeom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    shellGeom.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    shellGeom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    shellGeom.setIndex(indices);

    // ═══════════════════════════════════════════════════════════════
    // CHAOS → COSMOLOGY GRADIENT SHADER
    // Bottom (chaos) = deep blue OKLCH(0.2, 0.1, 200)
    // Top (cosmology) = warm orange OKLCH(0.6, 0.15, 30)
    // ═══════════════════════════════════════════════════════════════

    const chaosCosmosVertexShader = `
                varying vec3 vNormal;
                varying vec3 vPosition;
                varying vec3 vColor;
                varying vec2 vUv;

                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vPosition = position;
                    vColor = color;
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `;

    const chaosCosmosFragmentShader = `
                uniform float uTime;
                uniform vec3 uChaosColor;      // Deep blue (bottom)
                uniform vec3 uCosmosColor;     // Warm orange (top)
                uniform float uGradientMix;    // How much gradient vs vertex color

                varying vec3 vNormal;
                varying vec3 vPosition;
                varying vec3 vColor;
                varying vec2 vUv;

                // Simple noise for organic feel
                float hash(vec2 p) {
                    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
                }

                float noise(vec2 p) {
                    vec2 i = floor(p);
                    vec2 f = fract(p);
                    f = f * f * (3.0 - 2.0 * f);
                    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
                               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
                }

                void main() {
                    // Normalize Y position to 0-1 range (cone goes from -1.5 to 1.5)
                    float gradientT = (vPosition.y + 1.5) / 3.0;
                    gradientT = clamp(gradientT, 0.0, 1.0);

                    // Smooth step for better gradient transition
                    float smoothT = gradientT * gradientT * (3.0 - 2.0 * gradientT);

                    // Add subtle animated noise to the gradient
                    float n = noise(vPosition.xz * 3.0 + uTime * 0.15) * 0.08;
                    smoothT = clamp(smoothT + n, 0.0, 1.0);

                    // Chaos → Cosmos gradient
                    vec3 gradientColor = mix(uChaosColor, uCosmosColor, smoothT);

                    // Blend gradient with vertex colors
                    vec3 finalColor = mix(gradientColor, vColor, uGradientMix);

                    // Add subtle rim lighting
                    vec3 viewDir = normalize(cameraPosition - vPosition);
                    float rim = 1.0 - max(0.0, dot(viewDir, vNormal));
                    rim = pow(rim, 3.0) * 0.35;
                    finalColor += vec3(rim * 0.4, rim * 0.6, rim * 1.0);

                    // Pulsing glow at tier boundaries
                    float tierGlow = 0.0;
                    float y = vPosition.y;
                    tierGlow += exp(-pow((y - (-0.5)) * 8.0, 2.0)) * 0.15;  // T0/T1 boundary
                    tierGlow += exp(-pow((y - 0.5) * 8.0, 2.0)) * 0.15;     // T1/T2 boundary
                    tierGlow *= 0.5 + 0.5 * sin(uTime * 2.0);
                    finalColor += vec3(0.3, 0.6, 1.0) * tierGlow;

                    // Basic lighting
                    vec3 lightDir = normalize(vec3(2.0, 4.0, 3.0));
                    float diff = max(0.0, dot(vNormal, lightDir)) * 0.6 + 0.4;
                    finalColor *= diff;

                    gl_FragColor = vec4(finalColor, 0.92);
                }
            `;

    // OKLCH-inspired colors (converted to linear RGB for Three.js)
    // Chaos (bottom): OKLCH(0.25, 0.12, 240) ≈ deep cosmic blue
    // Cosmos (top): OKLCH(0.65, 0.16, 45) ≈ warm stellar orange
    const chaosColor = new THREE.Color(0.05, 0.08, 0.25);   // Deep blue
    const cosmosColor = new THREE.Color(0.85, 0.55, 0.25);  // Warm orange

    const shellMat = new THREE.ShaderMaterial({
        uniforms: {
            uTime: { value: 0 },
            uChaosColor: { value: chaosColor },
            uCosmosColor: { value: cosmosColor },
            uGradientMix: { value: 0.45 },  // 45% vertex colors, 55% gradient
            cameraPosition: { value: TOPO_MINIMAP.camera.position }
        },
        vertexShader: chaosCosmosVertexShader,
        fragmentShader: chaosCosmosFragmentShader,
        vertexColors: true,
        transparent: true,
        side: THREE.DoubleSide
    });

    // Store reference for animation updates
    TOPO_MINIMAP.shellMaterial = shellMat;

    const shellMesh = new THREE.Mesh(shellGeom, shellMat);
    shellMesh.userData = { type: 'shell', interactive: true };
    TOPO_MINIMAP.scene.add(shellMesh);
    TOPO_MINIMAP.meshes.push(shellMesh);

    // ═══════════════════════════════════════════════════════════════
    // TIER BOUNDARY RINGS - Smooth torus rings at tier transitions
    // ═══════════════════════════════════════════════════════════════

    [0.33, 0.66].forEach((v, i) => {
        const pos = surface(0, v);
        const r = Math.sqrt(pos.x * pos.x + pos.z * pos.z) + 0.015;

        const ringGeom = new THREE.TorusGeometry(r, 0.012, 12, 72);
        const ringMat = new THREE.MeshBasicMaterial({
            color: i === 0 ? 0x44aaff : 0x88ddff,
            transparent: true,
            opacity: 0.5
        });
        const ring = new THREE.Mesh(ringGeom, ringMat);
        ring.rotation.x = Math.PI / 2;
        ring.position.y = pos.y;
        ring.userData = { type: 'tier-boundary', tier: i };
        TOPO_MINIMAP.scene.add(ring);
    });

    // ═══════════════════════════════════════════════════════════════
    // FAMILY MERIDIANS - Geodesic curves along the surface
    // ═══════════════════════════════════════════════════════════════

    families.forEach((family, famIdx) => {
        const u = (famIdx / families.length) * Math.PI * 2;
        const points = [];

        for (let j = 0; j <= 60; j++) {
            const v = j / 60;
            const pos = surface(u, v);
            points.push(new THREE.Vector3(pos.x * 1.005, pos.y, pos.z * 1.005));
        }

        const curve = new THREE.CatmullRomCurve3(points);
        const tubeGeom = new THREE.TubeGeometry(curve, 50, 0.006, 6, false);
        const famColor = TOPO_COLORS.families[family] || { h: 180, s: 50, l: 60 };
        const tubeMat = new THREE.MeshBasicMaterial({
            color: hslToHex(famColor.h, famColor.s * 0.6, Math.min(75, famColor.l + 20)),
            transparent: true,
            opacity: 0.4
        });
        const tube = new THREE.Mesh(tubeGeom, tubeMat);
        tube.userData = { type: 'meridian', family: family };
        TOPO_MINIMAP.scene.add(tube);
    });

    // ═══════════════════════════════════════════════════════════════
    // CENTRAL AXIS - Vertical data highway through the core
    // ═══════════════════════════════════════════════════════════════

    // Single central vertical axis line
    const axisPoints = [];
    for (let j = 0; j <= 40; j++) {
        const t = j / 40;
        const y = (t - 0.5) * 3.2;  // Slightly longer than the shape
        axisPoints.push(new THREE.Vector3(0, y, 0));
    }
    const axisCurve = new THREE.CatmullRomCurve3(axisPoints);
    const axisGeom = new THREE.TubeGeometry(axisCurve, 20, 0.025, 8, false);
    const axisMat = new THREE.MeshBasicMaterial({
        color: 0x00ffff,
        transparent: true,
        opacity: 0.6
    });
    const axisTube = new THREE.Mesh(axisGeom, axisMat);
    axisTube.userData = { type: 'elevator', subtype: 'central-axis' };
    TOPO_MINIMAP.scene.add(axisTube);

    // ═══════════════════════════════════════════════════════════════
    // HORIZONTAL TIER RINGS - 3 parallel rings orthogonal to axis
    // These cut the toroidal shape at T0, T1, T2 boundaries
    // ═══════════════════════════════════════════════════════════════

    const tierYPositions = [-1.0, 0, 1.0];  // Bottom (T0), Middle (T1), Top (T2)
    const tierColors = [0x4488cc, 0x33ccbb, 0xe8f0ff];  // Physical, Virtual, Semantic colors

    tierYPositions.forEach((yPos, tierIdx) => {
        // Calculate radius at this Y position on the hyperboloid
        const vCentered = (yPos / 3.0) + 0.5;  // Map to 0-1 range
        const coshVal = Math.cosh(1.8 * (vCentered - 0.5));
        const baseR = (0.42 * coshVal + 0.35) * 1.02;  // Slightly outside surface

        // Create ring with multiple segments for smooth appearance
        const ringGeom = new THREE.TorusGeometry(baseR, 0.018, 8, 64);
        const ringMat = new THREE.MeshBasicMaterial({
            color: tierColors[tierIdx],
            transparent: true,
            opacity: 0.55
        });
        const ring = new THREE.Mesh(ringGeom, ringMat);
        ring.rotation.x = Math.PI / 2;  // Lay flat (orthogonal to Y axis)
        ring.position.y = yPos;
        ring.userData = { type: 'tier-ring', tier: tierIdx };
        TOPO_MINIMAP.scene.add(ring);
    });

    // ═══════════════════════════════════════════════════════════════
    // SINGULARITY CORE - The nexus point
    // ═══════════════════════════════════════════════════════════════

    const coreGeom = new THREE.SphereGeometry(0.15, 32, 32);
    const coreMat = new THREE.MeshPhongMaterial({
        color: 0x00ffff,
        emissive: 0x00aaff,
        emissiveIntensity: 0.8,
        transparent: true,
        opacity: 0.9
    });
    const coreMesh = new THREE.Mesh(coreGeom, coreMat);
    coreMesh.userData = { type: 'core' };
    TOPO_MINIMAP.scene.add(coreMesh);

    // Add glow ring around core
    const ringGeom = new THREE.TorusGeometry(0.25, 0.03, 8, 32);
    const ringMat = new THREE.MeshBasicMaterial({
        color: 0x00ffff,
        transparent: true,
        opacity: 0.5
    });
    const ringMesh = new THREE.Mesh(ringGeom, ringMat);
    ringMesh.rotation.x = Math.PI / 2;
    ringMesh.userData = { type: 'glow' };
    TOPO_MINIMAP.scene.add(ringMesh);

    // ═══════════════════════════════════════════════════════════════
    // ORBITAL PARTICLE SYSTEM - Micro Solar Systems
    // Nodes orbit at different levels like planets around stars
    // ═══════════════════════════════════════════════════════════════

    TOPO_MINIMAP.particles = [];
    TOPO_MINIMAP.solarSystems = [];

    // Create orbital particles based on actual node distribution
    const maxParticles = Math.min(data.nodes.length, 80);  // Limit for performance
    const sampleRate = Math.max(1, Math.floor(data.nodes.length / maxParticles));

    // Identify hub nodes (high in-degree) for micro solar systems
    const inDegree = new Map();
    (data.links || []).forEach(link => {
        const targetId = link.target?.id || link.target;
        inDegree.set(targetId, (inDegree.get(targetId) || 0) + 1);
    });

    // Sort nodes by in-degree to find hubs
    const sortedByDegree = [...data.nodes].sort((a, b) =>
        (inDegree.get(b.id) || 0) - (inDegree.get(a.id) || 0)
    );
    const hubNodes = sortedByDegree.slice(0, 5);  // Top 5 hubs become "stars"
    const hubIds = new Set(hubNodes.map(n => n.id));

    // Create micro solar systems for each hub
    hubNodes.forEach((hub, hubIdx) => {
        const tier = getNodeTier(hub);
        const family = getNodeAtomFamily(hub);
        const tierIdx = tiers.indexOf(tier);
        const famIdx = families.indexOf(family);

        // Hub position in the hyperboloid
        const hubY = (tierIdx - 1) * 1.0;  // -1, 0, 1 for T0, T1, T2
        const hubAngle = (famIdx / families.length) * Math.PI * 2 + hubIdx * 0.3;
        const hubRadius = 0.7 + tierIdx * 0.35;

        const hubColor = TOPO_COLORS.families[family] || TOPO_COLORS.families['UNKNOWN'];

        // Create the hub "star"
        const starGeom = new THREE.SphereGeometry(0.08, 16, 16);
        const starMat = new THREE.MeshPhongMaterial({
            color: hslToHex(hubColor.h, hubColor.s, hubColor.l + 15),
            emissive: hslToHex(hubColor.h, hubColor.s * 0.6, hubColor.l * 0.4),
            emissiveIntensity: 0.6,
            transparent: true,
            opacity: 0.9
        });
        const starMesh = new THREE.Mesh(starGeom, starMat);
        starMesh.userData = {
            type: 'hub-star',
            nodeId: hub.id,
            tier: tier,
            family: family,
            baseAngle: hubAngle,
            baseRadius: hubRadius,
            baseY: hubY,
            orbitSpeed: 0.3 + Math.random() * 0.2
        };
        TOPO_MINIMAP.scene.add(starMesh);
        TOPO_MINIMAP.solarSystems.push(starMesh);

        // Find satellite nodes (nodes that call this hub)
        const satellites = data.nodes.filter(n => {
            if (n.id === hub.id) return false;
            return (data.links || []).some(l => {
                const src = l.source?.id || l.source;
                const tgt = l.target?.id || l.target;
                return src === n.id && tgt === hub.id;
            });
        }).slice(0, 6);  // Max 6 satellites per hub

        // Create satellite particles orbiting the hub
        satellites.forEach((sat, satIdx) => {
            const satTier = getNodeTier(sat);
            const satFamily = getNodeAtomFamily(sat);
            const satColor = TOPO_COLORS.families[satFamily] || TOPO_COLORS.families['UNKNOWN'];

            const particleGeom = new THREE.SphereGeometry(0.03, 8, 8);
            const particleMat = new THREE.MeshBasicMaterial({
                color: hslToHex(satColor.h, satColor.s, satColor.l),
                transparent: true,
                opacity: 0.8
            });
            const particle = new THREE.Mesh(particleGeom, particleMat);

            // Orbital parameters
            const orbitRadius = 0.12 + satIdx * 0.04;
            const orbitSpeed = 1.5 - satIdx * 0.15;  // Inner orbits faster
            const orbitTilt = (satIdx % 3) * 0.3;    // Different orbital planes
            const startAngle = (satIdx / satellites.length) * Math.PI * 2;

            particle.userData = {
                type: 'satellite',
                parentHub: starMesh,
                orbitRadius: orbitRadius,
                orbitSpeed: orbitSpeed,
                orbitTilt: orbitTilt,
                orbitAngle: startAngle,
                nodeId: sat.id
            };

            TOPO_MINIMAP.scene.add(particle);
            TOPO_MINIMAP.particles.push(particle);
        });
    });

    // Create free-floating particles for non-hub nodes
    let particleCount = 0;
    data.nodes.forEach((node, idx) => {
        if (hubIds.has(node.id)) return;
        if (idx % sampleRate !== 0) return;
        if (particleCount >= maxParticles - hubNodes.length * 6) return;

        const tier = getNodeTier(node);
        const family = getNodeAtomFamily(node);
        const tierIdx = tiers.indexOf(tier);
        const famIdx = families.indexOf(family);
        const color = TOPO_COLORS.families[family] || TOPO_COLORS.families['UNKNOWN'];

        const particleGeom = new THREE.SphereGeometry(0.025, 6, 6);
        const particleMat = new THREE.MeshBasicMaterial({
            color: hslToHex(color.h, color.s, color.l),
            transparent: true,
            opacity: 0.6
        });
        const particle = new THREE.Mesh(particleGeom, particleMat);

        // Orbital parameters based on tier and family
        const baseRadius = 0.5 + tierIdx * 0.5 + Math.random() * 0.2;
        const baseY = (tierIdx - 1) * 0.8 + (Math.random() - 0.5) * 0.4;
        const baseAngle = (famIdx / families.length) * Math.PI * 2 + Math.random() * 0.5;
        const orbitSpeed = 0.2 + Math.random() * 0.3;
        const orbitTilt = (famIdx % 3) * 0.2 + Math.random() * 0.1;

        particle.userData = {
            type: 'free-particle',
            baseRadius: baseRadius,
            baseY: baseY,
            baseAngle: baseAngle,
            orbitSpeed: orbitSpeed,
            orbitTilt: orbitTilt,
            orbitAngle: Math.random() * Math.PI * 2,
            tier: tier,
            family: family,
            nodeId: node.id
        };

        TOPO_MINIMAP.scene.add(particle);
        TOPO_MINIMAP.particles.push(particle);
        particleCount++;
    });

    // Store layers for animation
    TOPO_MINIMAP.layers = LAYERS;
}

function buildTopoLegends(data) {
    if (!data || !data.nodes) return;

    // Count by category
    const tierCounts = collectCounts(data.nodes, n => getNodeTier(n));
    const familyCounts = collectCounts(data.nodes, n => getNodeAtomFamily(n));
    const ringCounts = collectCounts(data.nodes, n => getNodeRing(n));
    const edgeCounts = collectCounts(data.links || [], l => String(l.edge_type || l.type || 'default'));

    // Build tier legend
    const tierContainer = document.getElementById('topo-tiers');
    if (tierContainer) {
        tierContainer.innerHTML = '';
        tierCounts.forEach(([tier, count]) => {
            const color = TOPO_COLORS.tiers[tier] || TOPO_COLORS.tiers['UNKNOWN'];
            const item = createTopoLegendItem(tier, count, color, 'tier');
            tierContainer.appendChild(item);
        });
    }

    // Build family legend
    const famContainer = document.getElementById('topo-families');
    if (famContainer) {
        famContainer.innerHTML = '';
        familyCounts.forEach(([family, count]) => {
            const color = TOPO_COLORS.families[family] || TOPO_COLORS.families['UNKNOWN'];
            const item = createTopoLegendItem(family, count, color, 'family');
            famContainer.appendChild(item);
        });
    }

    // Build ring legend
    const ringContainer = document.getElementById('topo-rings');
    if (ringContainer) {
        ringContainer.innerHTML = '';
        ringCounts.forEach(([ring, count]) => {
            const color = TOPO_COLORS.rings[ring] || TOPO_COLORS.rings['UNKNOWN'];
            const item = createTopoLegendItem(ring, count, color, 'ring');
            ringContainer.appendChild(item);
        });
    }

    // Build edge filter chips
    const edgeContainer = document.getElementById('topo-edges');
    if (edgeContainer) {
        edgeContainer.innerHTML = '';
        edgeCounts.forEach(([edgeType, count]) => {
            const chip = document.createElement('div');
            chip.className = 'topo-edge-chip active';
            chip.dataset.value = edgeType;
            chip.textContent = `${edgeType} (${count})`;
            chip.onclick = () => toggleEdgeFilter(edgeType, chip);
            edgeContainer.appendChild(chip);
        });
    }
}

function createTopoLegendItem(label, count, color, filterType) {
    const item = document.createElement('div');
    item.className = 'topo-legend-item';
    item.dataset.value = label;
    item.dataset.filterType = filterType;

    const swatch = document.createElement('div');
    swatch.className = 'topo-legend-swatch';
    swatch.style.backgroundColor = `hsl(${color.h}, ${color.s}%, ${color.l}%)`;

    const text = document.createElement('span');
    text.textContent = `${label} (${count})`;

    item.appendChild(swatch);
    item.appendChild(text);

    item.onclick = () => toggleTopoFilter(filterType, label, item);

    // Add semantic tooltip on hover
    const category = filterType === 'tier' ? 'tiers' : filterType === 'family' ? 'families' : null;
    if (category && SMC_THEORY[category]?.[label]) {
        item.addEventListener('mouseenter', (e) => {
            showTopoTooltip(category, label, e.clientX, e.clientY);
        });
        item.addEventListener('mouseleave', () => hideTopoTooltip());
        item.addEventListener('mousemove', (e) => {
            if (TOOLTIP_STATE.visible) {
                const tooltip = TOOLTIP_STATE.element;
                let left = e.clientX + 15, top = e.clientY + 15;
                if (left + 280 > window.innerWidth) left = e.clientX - 295;
                if (top + 200 > window.innerHeight) top = e.clientY - 215;
                tooltip.style.left = left + 'px';
                tooltip.style.top = top + 'px';
            }
        });
    }

    return item;
}

function toggleTopoFilter(filterType, value, element) {
    let filterSet;
    switch (filterType) {
        case 'tier': filterSet = VIS_FILTERS.tiers; break;
        case 'family': filterSet = VIS_FILTERS.families || new Set(); break;
        case 'ring': filterSet = VIS_FILTERS.rings; break;
        default: return;
    }

    // Initialize families filter if needed
    if (filterType === 'family' && !VIS_FILTERS.families) {
        VIS_FILTERS.families = new Set(['LOG', 'DAT', 'ORG', 'EXE', 'EXT', 'UNKNOWN']);
    }

    if (filterSet.has(value)) {
        filterSet.delete(value);
        element.classList.add('filtered');
    } else {
        filterSet.add(value);
        element.classList.remove('filtered');
    }

    // Update minimap visuals
    updateTopoMinimapFilters();

    // Refresh main graph
    refreshGraph();
}

function toggleEdgeFilter(edgeType, element) {
    if (VIS_FILTERS.edges.has(edgeType)) {
        VIS_FILTERS.edges.delete(edgeType);
        element.classList.remove('active');
    } else {
        VIS_FILTERS.edges.add(edgeType);
        element.classList.add('active');
    }
    refreshGraph();
}

/**
 * Clear all dimension filters (tier, ring, family, role, file, edge)
 * Used for zero-node recovery and manual reset
 */
function clearAllFilters() {
    VIS_FILTERS.tiers.clear();
    VIS_FILTERS.rings.clear();
    VIS_FILTERS.families.clear();
    VIS_FILTERS.roles.clear();
    VIS_FILTERS.files.clear();
    VIS_FILTERS.edges.clear();
    VIS_FILTERS.layers.clear();
    VIS_FILTERS.effects.clear();
    VIS_FILTERS.edgeFamilies.clear();

    // Update legend UI
    document.querySelectorAll('.topo-legend-item.filtered').forEach(el => el.classList.remove('filtered'));

    // Update chip UI
    document.querySelectorAll('.filter-chip.active').forEach(el => el.classList.remove('active'));

    // Update minimap if present
    if (typeof updateTopoMinimapFilters === 'function') {
        updateTopoMinimapFilters();
    }

    console.log('[Filters] All filters cleared');
}

// Expose for UI buttons
window.clearAllFilters = clearAllFilters;

// ═══════════════════════════════════════════════════════════════════════
// DISSOLUTION PARTICLE SYSTEM - Particles disperse when layers toggle
// ═══════════════════════════════════════════════════════════════════════

const DISSOLUTION_PARTICLES = {
    pool: [],
    active: [],
    maxParticles: 50,
    geometry: null,
    material: null
};

function initDissolutionParticles() {
    if (!TOPO_MINIMAP.scene) return;

    // Create particle geometry once
    DISSOLUTION_PARTICLES.geometry = new THREE.SphereGeometry(0.015, 6, 6);
    DISSOLUTION_PARTICLES.material = new THREE.MeshBasicMaterial({
        color: 0x88ccff,
        transparent: true,
        opacity: 0.8
    });

    // Pre-create particle pool
    for (let i = 0; i < DISSOLUTION_PARTICLES.maxParticles; i++) {
        const particle = new THREE.Mesh(
            DISSOLUTION_PARTICLES.geometry,
            DISSOLUTION_PARTICLES.material.clone()
        );
        particle.visible = false;
        particle.userData = { type: 'dissolution', velocity: new THREE.Vector3(), life: 0, maxLife: 1 };
        TOPO_MINIMAP.scene.add(particle);
        DISSOLUTION_PARTICLES.pool.push(particle);
    }
}

function spawnDissolutionParticles(position, color, count = 8, disperse = true) {
    if (DISSOLUTION_PARTICLES.pool.length === 0) initDissolutionParticles();

    for (let i = 0; i < count && DISSOLUTION_PARTICLES.pool.length > 0; i++) {
        const particle = DISSOLUTION_PARTICLES.pool.pop();
        if (!particle) continue;

        particle.visible = true;
        particle.position.copy(position);

        // Random velocity for dispersion
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        const speed = disperse ? (0.02 + Math.random() * 0.03) : 0;

        particle.userData.velocity.set(
            Math.sin(phi) * Math.cos(theta) * speed,
            Math.cos(phi) * speed + (disperse ? 0.01 : -0.01),
            Math.sin(phi) * Math.sin(theta) * speed
        );
        particle.userData.life = disperse ? 1.0 : 0;
        particle.userData.maxLife = 0.8 + Math.random() * 0.4;
        particle.userData.targetPos = disperse ? null : position.clone();
        particle.userData.startPos = particle.position.clone();
        particle.userData.disperse = disperse;

        // Set particle color based on source
        if (particle.material && color) {
            particle.material.color.setHSL(color.h / 360, color.s / 100, color.l / 100);
        }

        DISSOLUTION_PARTICLES.active.push(particle);
    }
}

function updateDissolutionParticles(deltaTime = 0.016) {
    const toRemove = [];

    DISSOLUTION_PARTICLES.active.forEach((particle, idx) => {
        const ud = particle.userData;

        if (ud.disperse) {
            // Dispersing: fade out and move away
            ud.life -= deltaTime / ud.maxLife;

            particle.position.add(ud.velocity);
            ud.velocity.y -= 0.0003; // Gravity
            ud.velocity.multiplyScalar(0.98); // Drag

            if (particle.material) {
                particle.material.opacity = Math.max(0, ud.life * 0.8);
            }
            particle.scale.setScalar(ud.life * 0.8 + 0.2);

            if (ud.life <= 0) toRemove.push(idx);
        } else {
            // Converging: fade in and move toward target
            ud.life += deltaTime / ud.maxLife;

            if (ud.targetPos) {
                const t = Math.min(1, ud.life);
                const eased = t * t * (3 - 2 * t); // Smooth step
                particle.position.lerpVectors(ud.startPos, ud.targetPos, eased);
            }

            if (particle.material) {
                particle.material.opacity = Math.min(0.8, ud.life * 0.8);
            }
            particle.scale.setScalar(0.2 + ud.life * 0.8);

            if (ud.life >= 1) toRemove.push(idx);
        }
    });

    // Return particles to pool
    toRemove.reverse().forEach(idx => {
        const particle = DISSOLUTION_PARTICLES.active.splice(idx, 1)[0];
        particle.visible = false;
        DISSOLUTION_PARTICLES.pool.push(particle);
    });
}

function updateTopoMinimapFilters() {
    if (!TOPO_MINIMAP.meshes) return;

    TOPO_MINIMAP.meshes.forEach(mesh => {
        if (mesh.userData.type !== 'cell') return;

        const tier = mesh.userData.tier;
        const family = mesh.userData.family;

        const tierActive = VIS_FILTERS.tiers.has(tier);
        const familyActive = !VIS_FILTERS.families || VIS_FILTERS.families.has(family);

        const isActive = tierActive && familyActive;
        const wasActive = mesh.userData.wasActive !== undefined ? mesh.userData.wasActive : true;

        // Spawn dissolution particles on state change
        if (wasActive !== isActive) {
            const color = TOPO_COLORS.families[family] || { h: 200, s: 70, l: 55 };
            spawnDissolutionParticles(mesh.position, color, 6, wasActive); // disperse if was active
        }

        mesh.userData.wasActive = isActive;

        // Update material opacity
        if (mesh.material) {
            mesh.material.opacity = isActive ? 0.9 : 0.15;
            mesh.material.emissiveIntensity = isActive ? 0.4 : 0.1;
        }
    });
}

// ═══════════════════════════════════════════════════════════════════════
// MUSICAL HARMONIC RATIOS - Orbital periods encode relationships
// Like clockwork: related nodes have harmonically related periods
// ═══════════════════════════════════════════════════════════════════════
const HARMONIC_RATIOS = {
    // Musical intervals as orbit period multipliers
    unison: 1,        // Same frequency
    octave: 2,        // 2:1 ratio
    fifth: 1.5,       // 3:2 ratio (perfect fifth)
    fourth: 1.333,    // 4:3 ratio (perfect fourth)
    majorThird: 1.25, // 5:4 ratio
    minorThird: 1.2,  // 6:5 ratio
    // Tier-based base periods (T0 fastest, T2 slowest)
    tierPeriods: { T0: 1.0, T1: 1.5, T2: 2.0 },
    // Family-based phase offsets (creates visual "chords")
    familyPhases: { LOG: 0, DAT: Math.PI / 3, ORG: 2 * Math.PI / 3, EXE: Math.PI, EXT: 4 * Math.PI / 3 }
};

function animateTopoMinimap() {
    if (!TOPO_MINIMAP.renderer || !TOPO_MINIMAP.scene || !TOPO_MINIMAP.camera) return;

    TOPO_MINIMAP.rotation += 0.004;
    const time = Date.now() * 0.001;

    // Update chaos→cosmology shader time uniform
    if (TOPO_MINIMAP.shellMaterial && TOPO_MINIMAP.shellMaterial.uniforms) {
        TOPO_MINIMAP.shellMaterial.uniforms.uTime.value = time;
    }

    // Rotate the entire scene (cells follow hyperboloid)
    TOPO_MINIMAP.meshes.forEach(mesh => {
        mesh.rotation.y = TOPO_MINIMAP.rotation;
    });

    // ═══════════════════════════════════════════════════════════════
    // CLOCKWORK ORBITAL PHYSICS - Particles orbit with harmonic periods
    // ═══════════════════════════════════════════════════════════════

    // Animate hub stars (they orbit the core slowly)
    if (TOPO_MINIMAP.solarSystems) {
        TOPO_MINIMAP.solarSystems.forEach(star => {
            const ud = star.userData;
            if (ud.type !== 'hub-star') return;

            // Hub stars orbit the hyperboloid structure
            const tierPeriod = HARMONIC_RATIOS.tierPeriods[ud.tier] || 1.5;
            const familyPhase = HARMONIC_RATIOS.familyPhases[ud.family] || 0;
            const orbitAngle = ud.baseAngle + time * ud.orbitSpeed / tierPeriod + familyPhase;

            // ═══ TIER-BASED IMPORTANCE PULSING ═══
            // T2 (architecture) pulses stronger than T0 (foundation)
            const tierImportance = { T0: 0.4, T1: 0.6, T2: 0.9 }[ud.tier] || 0.5;
            const importancePulse = Math.sin(time * (2 + tierImportance * 2)) * tierImportance * 0.3;

            // Position with importance-based breathing
            const y = ud.baseY;
            const r = ud.baseRadius + Math.sin(time * 0.5) * 0.05 + importancePulse * 0.02;

            star.position.set(
                Math.cos(orbitAngle) * r,
                y + Math.sin(time * tierPeriod) * 0.08,
                Math.sin(orbitAngle) * r
            );

            // ═══ IMPORTANCE GLOW + SCALE PULSE ═══
            const beat = Math.abs(Math.sin(orbitAngle * 2));
            const scalePulse = 1 + Math.sin(time * 3 + familyPhase) * 0.15 * tierImportance;
            star.scale.set(scalePulse, scalePulse, scalePulse);

            if (star.material) {
                const baseGlow = 0.3 + tierImportance * 0.4;
                star.material.emissiveIntensity = baseGlow + beat * 0.3 + importancePulse * 0.2;
            }
        });
    }

    // Animate satellite particles (orbit their parent hubs)
    if (TOPO_MINIMAP.particles) {
        TOPO_MINIMAP.particles.forEach(particle => {
            const ud = particle.userData;

            if (ud.type === 'satellite' && ud.parentHub) {
                // Satellite orbits around its parent hub star
                const hubPos = ud.parentHub.position;
                ud.orbitAngle += ud.orbitSpeed * 0.02;  // Kepler: inner = faster

                // Tilted orbital plane
                const x = Math.cos(ud.orbitAngle) * ud.orbitRadius;
                const z = Math.sin(ud.orbitAngle) * ud.orbitRadius;
                const tiltedY = Math.sin(ud.orbitAngle) * Math.sin(ud.orbitTilt) * ud.orbitRadius * 0.5;

                particle.position.set(
                    hubPos.x + x,
                    hubPos.y + tiltedY,
                    hubPos.z + z
                );

                // Brightness pulses when aligned (conjunction)
                const conjunction = Math.abs(Math.cos(ud.orbitAngle));
                if (particle.material) {
                    particle.material.opacity = 0.5 + conjunction * 0.4;
                }
            }

            if (ud.type === 'free-particle') {
                // Free particles orbit the core with harmonic periods
                const tierPeriod = HARMONIC_RATIOS.tierPeriods[ud.tier] || 1.5;
                const familyPhase = HARMONIC_RATIOS.familyPhases[ud.family] || 0;

                ud.orbitAngle += ud.orbitSpeed * 0.015 / tierPeriod;

                // Orbital position with tilt
                const angle = ud.baseAngle + ud.orbitAngle + familyPhase;
                const r = ud.baseRadius + Math.sin(time * 0.3 + familyPhase) * 0.08;
                const y = ud.baseY + Math.sin(angle * 2) * Math.sin(ud.orbitTilt) * 0.15;

                particle.position.set(
                    Math.cos(angle) * r,
                    y,
                    Math.sin(angle) * r
                );

                // Harmonic resonance glow (brighten when multiple orbits align)
                const resonance = Math.abs(Math.sin(time * tierPeriod + familyPhase));
                if (particle.material) {
                    particle.material.opacity = 0.4 + resonance * 0.3;
                }
            }
        });
    }

    // Animate scene elements (core, glow, elevators)
    TOPO_MINIMAP.scene.children.forEach(child => {
        if (!child.userData) return;

        if (child.userData.type === 'core') {
            // Pulsing core - "heartbeat" of the system
            const pulse = 1 + Math.sin(time * 3) * 0.15;
            child.scale.set(pulse, pulse, pulse);
            if (child.material) {
                // Core pulses brighter when orbital "chords" align
                const chordResonance = Math.abs(Math.sin(time) * Math.sin(time * 1.5) * Math.sin(time * 2));
                child.material.emissiveIntensity = 0.5 + chordResonance * 0.5;
            }
        }

        if (child.userData.type === 'glow') {
            // Rotating glow ring
            child.rotation.z = time * 0.5;
            const ringPulse = 1 + Math.sin(time * 2.5) * 0.1;
            child.scale.set(ringPulse, ringPulse, 1);
        }

        if (child.userData.type === 'elevator') {
            // Central axis - pulsing data flow
            if (child.userData.subtype === 'central-axis' && child.material) {
                const pulse = 0.4 + Math.abs(Math.sin(time * 2)) * 0.35;
                child.material.opacity = pulse;
            }
        }

        // ═══ HORIZONTAL TIER RINGS ═══
        if (child.userData.type === 'tier-ring') {
            const tierIdx = child.userData.tier;
            const tierPhase = tierIdx * Math.PI * 0.667;
            const ringPulse = 1 + Math.sin(time * 2 + tierPhase) * 0.08;
            child.scale.set(ringPulse, ringPulse, 1);
            if (child.material) {
                child.material.opacity = 0.4 + tierIdx * 0.1 + Math.abs(Math.sin(time * 1.5 + tierPhase)) * 0.2;
            }
        }

        // ═══ TIER BOUNDARY RING PULSING ═══
        if (child.userData.type === 'tier-boundary') {
            const tierIdx = child.userData.tier;
            // T0/T1 boundary pulses differently than T1/T2
            const tierImportance = tierIdx === 0 ? 0.6 : 0.85;
            const ringPulse = 1 + Math.sin(time * (2.5 + tierIdx) + tierIdx * Math.PI) * 0.12 * tierImportance;
            child.scale.set(ringPulse, ringPulse, 1);

            if (child.material) {
                // Glow intensity varies with tier importance
                const baseOpacity = 0.35 + tierImportance * 0.25;
                const glowPulse = Math.sin(time * 2 + tierIdx * 1.5) * 0.2;
                child.material.opacity = baseOpacity + Math.abs(glowPulse);
            }
        }
    });

    // Subtle camera bob for depth perception
    const bobY = Math.sin(time * 0.3) * 0.1;
    TOPO_MINIMAP.camera.position.y = 3.5 + bobY;
    TOPO_MINIMAP.camera.lookAt(0, 0, 0);

    // Update dissolution particles
    updateDissolutionParticles(0.016);

    TOPO_MINIMAP.renderer.render(TOPO_MINIMAP.scene, TOPO_MINIMAP.camera);
    TOPO_MINIMAP.animationId = requestAnimationFrame(animateTopoMinimap);
}

function onTopoMouseMove(event) {
    if (!TOPO_MINIMAP.renderer) return;

    const rect = TOPO_MINIMAP.canvas.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(x, y), TOPO_MINIMAP.camera);

    // Include hub stars, particles, and all scene objects for intersection
    const allObjects = [...TOPO_MINIMAP.meshes, ...(TOPO_MINIMAP.solarSystems || []), ...(TOPO_MINIMAP.particles || [])];
    const intersects = raycaster.intersectObjects(allObjects.filter(Boolean));

    // Reset previous hover
    if (TOPO_MINIMAP.hoveredMesh && TOPO_MINIMAP.hoveredMesh.material) {
        TOPO_MINIMAP.hoveredMesh.material.emissiveIntensity =
            TOPO_MINIMAP.hoveredMesh.userData.baseEmissive || 0.3;
    }

    if (intersects.length > 0) {
        const mesh = intersects[0].object;
        const ud = mesh.userData;

        // Highlight hovered mesh
        if (mesh.material && mesh.material.emissiveIntensity !== undefined) {
            ud.baseEmissive = ud.baseEmissive || mesh.material.emissiveIntensity;
            mesh.material.emissiveIntensity = 0.8;
        }
        TOPO_MINIMAP.hoveredMesh = mesh;
        TOPO_MINIMAP.canvas.style.cursor = 'pointer';

        // Show semantic tooltip based on element type
        if (ud.type === 'cell') {
            const { tier, family } = ud;
            if (family && SMC_THEORY.families[family]) {
                showTopoTooltip('families', family, event.clientX, event.clientY);
            } else if (tier && SMC_THEORY.tiers[tier]) {
                showTopoTooltip('tiers', tier, event.clientX, event.clientY);
            }
        } else if (ud.type === 'shell') {
            const point = intersects[0].point;
            if (point.y < -0.3) showTopoTooltip('tiers', 'T0', event.clientX, event.clientY);
            else if (point.y < 0.3) showTopoTooltip('tiers', 'T1', event.clientX, event.clientY);
            else showTopoTooltip('tiers', 'T2', event.clientX, event.clientY);
        } else if (ud.type === 'hub-star') {
            showTopoTooltip('special', 'hub-star', event.clientX, event.clientY);
        } else if (ud.type === 'core') {
            showTopoTooltip('special', 'core', event.clientX, event.clientY);
        } else if (ud.type === 'elevator') {
            showTopoTooltip('special', 'elevator', event.clientX, event.clientY);
        } else if (ud.type === 'tier-boundary') {
            showTopoTooltip('tiers', ud.tier === 0 ? 'T1' : 'T2', event.clientX, event.clientY);
        } else if (ud.type === 'tier-ring') {
            showTopoTooltip('tiers', ['T0', 'T1', 'T2'][ud.tier] || 'T1', event.clientX, event.clientY);
        } else if (ud.type === 'meridian' && ud.family) {
            showTopoTooltip('families', ud.family, event.clientX, event.clientY);
        }
    } else {
        TOPO_MINIMAP.hoveredMesh = null;
        TOPO_MINIMAP.canvas.style.cursor = 'default';
        hideTopoTooltip();
    }
}

function onTopoMouseOut(event) { hideTopoTooltip(true); }

// ═══════════════════════════════════════════════════════════════════════
// EXPAND-ON-CLICK - Toggle fullscreen minimap view
// ═══════════════════════════════════════════════════════════════════════
function toggleMinimapExpand(event) {
    // Don't expand if clicking on interactive elements
    if (event.target.tagName === 'CANVAS') {
        const container = document.getElementById('topo-minimap');
        if (!container) return;

        const isExpanded = container.classList.toggle('expanded');

        // Resize renderer for better quality when expanded
        if (TOPO_MINIMAP.renderer && TOPO_MINIMAP.camera) {
            setTimeout(() => {
                const width = container.clientWidth;
                const height = container.clientHeight;
                TOPO_MINIMAP.renderer.setSize(width, height);
                TOPO_MINIMAP.camera.aspect = width / height;
                TOPO_MINIMAP.camera.updateProjectionMatrix();
            }, 50); // Wait for CSS transition to start
        }

        // Update hint
        const hint = container.querySelector('.topo-expand-hint');
        if (hint) hint.textContent = isExpanded ? 'Click to collapse' : 'Click to expand';

        // Escape key to close
        if (isExpanded) {
            const closeOnEscape = (e) => {
                if (e.key === 'Escape') {
                    container.classList.remove('expanded');
                    resizeMinimapRenderer();
                    document.removeEventListener('keydown', closeOnEscape);
                }
            };
            document.addEventListener('keydown', closeOnEscape);
        }
    }
}

function resizeMinimapRenderer() {
    const container = document.getElementById('topo-minimap');
    if (!container || !TOPO_MINIMAP.renderer || !TOPO_MINIMAP.camera) return;
    setTimeout(() => {
        const width = container.clientWidth;
        const height = container.clientHeight;
        TOPO_MINIMAP.renderer.setSize(width, height);
        TOPO_MINIMAP.camera.aspect = width / height;
        TOPO_MINIMAP.camera.updateProjectionMatrix();
    }, 400); // Wait for CSS transition to complete
}

function onTopoClick(event) {
    if (!TOPO_MINIMAP.renderer) return;

    const rect = TOPO_MINIMAP.canvas.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(new THREE.Vector2(x, y), TOPO_MINIMAP.camera);

    const intersects = raycaster.intersectObjects(TOPO_MINIMAP.meshes);

    if (intersects.length > 0) {
        const mesh = intersects[0].object;
        if (mesh.userData.type === 'cell') {
            const { tier, family } = mesh.userData;

            // Toggle this specific cell's tier and family in filters
            // For now, just show what was clicked
            showToast(`Clicked: ${tier} / ${family}`, 2000);

            // Filter to show only this tier+family
            // (Could implement solo/isolate mode here)
        }
    }
}

function collectCounts(items, keyFn) {
    const counts = new Map();
    items.forEach(item => {
        const key = keyFn(item);
        if (!key) return;
        counts.set(key, (counts.get(key) || 0) + 1);
    });
    return Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
}

function resolveDefaults(defaults, available) {
    if (!Array.isArray(defaults) || defaults.length === 0) {
        return available;
    }
    const availableSet = new Set(available);
    const intersection = defaults.filter(value => availableSet.has(value));
    return intersection.length ? intersection : available;
}

function buildCheckboxRow(container, id, label, count, checked, onChange) {
    const row = document.createElement('div');
    row.className = 'filter-item';
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.id = id;
    input.checked = checked;
    input.onchange = () => onChange(input.checked);
    const text = document.createElement('label');
    text.setAttribute('for', id);
    text.textContent = label;
    const countEl = document.createElement('span');
    countEl.className = 'filter-count';
    countEl.textContent = (typeof count === 'number') ? String(count) : '';
    row.appendChild(input);
    row.appendChild(text);
    if (countEl.textContent) {
        row.appendChild(countEl);
    }
    container.appendChild(row);
    return input;
}

function buildFilterGroup(containerId, items, stateSet, onUpdate) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    const allId = `${containerId}-all`;
    let allCheckbox = null;

    allCheckbox = buildCheckboxRow(container, allId, 'ALL', null, true, (checked) => {
        stateSet.clear();
        if (checked) {
            items.forEach(([value]) => stateSet.add(value));
        }
        container.querySelectorAll('input[type="checkbox"]').forEach(box => {
            if (box.id !== allId) box.checked = checked;
        });
        onUpdate();
    });

    items.forEach(([value, count], index) => {
        const id = `${containerId}-${index}`;
        const checked = stateSet.has(value);
        buildCheckboxRow(container, id, value, count, checked, (isChecked) => {
            if (isChecked) {
                stateSet.add(value);
            } else {
                stateSet.delete(value);
            }
            const allChecked = items.every(([v]) => stateSet.has(v));
            allCheckbox.checked = allChecked;
            onUpdate();
        });
    });
}

function normalizeDatamapConfig(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const id = String(raw.id || raw.key || raw.label || '').trim();
    if (!id) return null;
    const normalizeList = (value) => {
        if (!Array.isArray(value)) return [];
        return value.map(item => String(item).toUpperCase());
    };
    // Normalize tier list with aliases (CORE→T0, ARCH→T1, EXT→T2)
    const normalizeTierList = (value) => {
        if (!Array.isArray(value)) return [];
        return value.map(item => normalizeTier(item));
    };
    const match = raw.match || {};
    return {
        id: id.toUpperCase(),
        label: String(raw.label || raw.id || id).toUpperCase(),
        match: {
            atom_families: normalizeList(match.atom_families),  // NEW: canonical atom family
            atom_prefixes: normalizeList(match.atom_prefixes),  // backward compat
            tiers: normalizeTierList(match.tiers),  // applies aliases
            rings: normalizeList(match.rings),
            roles: normalizeList(match.roles)
        },
        default: Boolean(raw.default)
    };
}

function resolveDatamapConfigs(controlsConfig) {
    const fromTokens = Array.isArray(controlsConfig.datamaps) ? controlsConfig.datamaps : [];
    const normalized = fromTokens
        .map(normalizeDatamapConfig)
        .filter(Boolean);
    if (normalized.length) return normalized;

    const fallback = controlsConfig.buttons?.datamaps || {};
    return Object.entries(fallback).map(([label, config]) => {
        const prefix = config.filter || null;
        return normalizeDatamapConfig({
            id: label.toUpperCase(),
            label: label.toUpperCase(),
            match: prefix ? { atom_prefixes: [prefix] } : {},
            default: false
        });
    }).filter(Boolean);
}

function datamapMatches(node, config) {
    const match = config.match || {};
    const atomId = String(node.atom || '');
    const atomFamily = getNodeAtomFamily(node);  // canonical or inferred
    const tier = getNodeTier(node);  // canonical or inferred (with aliases)
    const ring = getNodeRing(node);
    const role = String(node.role || 'Unknown').toUpperCase();

    // NEW: atom_families matching (canonical field)
    if (Array.isArray(match.atom_families) && match.atom_families.length) {
        if (!match.atom_families.includes(atomFamily)) return false;
    }

    // Backward compat: atom_prefixes matches atom_family OR atom prefix
    if (Array.isArray(match.atom_prefixes) && match.atom_prefixes.length) {
        const matchesFamily = match.atom_prefixes.includes(atomFamily);
        const matchesPrefix = match.atom_prefixes.some(prefix => atomId.startsWith(prefix));
        if (!matchesFamily && !matchesPrefix) return false;
    }

    // Tier matching (aliases already normalized in config)
    if (Array.isArray(match.tiers) && match.tiers.length) {
        if (!match.tiers.includes(tier)) return false;
    }

    if (Array.isArray(match.rings) && match.rings.length) {
        if (!match.rings.includes(ring)) return false;
    }

    if (Array.isArray(match.roles) && match.roles.length) {
        if (!match.roles.includes(role)) return false;
    }
    return true;
}

function buildDatamapToggle(container, id, label, checked, count, onChange) {
    const wrapper = document.createElement('label');
    wrapper.className = 'datamap-toggle';
    wrapper.setAttribute('data-id', id);

    const input = document.createElement('input');
    input.type = 'checkbox';
    input.checked = checked;
    input.onchange = () => onChange(input.checked);

    const text = document.createElement('span');
    text.textContent = label;

    const countEl = document.createElement('span');
    countEl.className = 'datamap-count';
    countEl.textContent = (typeof count === 'number') ? String(count) : '';

    wrapper.appendChild(input);
    wrapper.appendChild(text);
    wrapper.appendChild(countEl);
    container.appendChild(wrapper);

    return { wrapper, input, count: countEl };
}

// Deprecated buildDatamapControls - replaced by UIManager

function buildExclusiveOptions(containerId, options, activeValue, onSelect) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    const inputs = [];
    options.forEach((option, index) => {
        const id = `${containerId}-${index}`;
        const input = buildCheckboxRow(
            container,
            id,
            option.label,
            null,
            option.value === activeValue,
            (checked) => {
                if (!checked) {
                    input.checked = true;
                    return;
                }
                inputs.forEach(other => {
                    if (other !== input) other.checked = false;
                });
                onSelect(option.value);
            }
        );
        inputs.push(input);
    });
}

function buildMetadataControls(containerId, metadata) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    const toggles = [
        { id: 'meta-labels', label: 'LABELS', key: 'showLabels' },
        { id: 'meta-file-panel', label: 'FILE PANEL', key: 'showFilePanel' },
        { id: 'meta-report', label: 'REPORT', key: 'showReportPanel' },
        { id: 'meta-edges', label: 'EDGES', key: 'showEdges' }
    ];

    toggles.forEach((toggle) => {
        buildCheckboxRow(container, toggle.id, toggle.label, null, metadata[toggle.key], (checked) => {
            metadata[toggle.key] = checked;
            applyMetadataVisibility();
            refreshGraph();
        });
    });
}

function buildAppearanceSliders(containerId, sliderConfigs) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    const resolveSlider = (key, fallback) => {
        const config = (sliderConfigs && sliderConfigs[key]) ? sliderConfigs[key] : {};
        return {
            label: config.label || fallback.label,
            min: (config.min !== undefined) ? config.min : fallback.min,
            max: (config.max !== undefined) ? config.max : fallback.max,
            step: (config.step !== undefined) ? config.step : fallback.step,
            default: (config.default !== undefined) ? config.default : fallback.value
        };
    };

    const sliderDefs = [
        (() => {
            const config = resolveSlider('edgeOpacity', {
                label: 'EDGE OPACITY',
                min: 0.02,
                max: 0.4,
                step: 0.01,
                value: EDGE_DEFAULT_OPACITY
            });
            return {
                id: 'edge-opacity',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: APPEARANCE_STATE.edgeOpacity ?? config.default,
                onChange: (val) => {
                    APPEARANCE_STATE.edgeOpacity = val;
                    applyEdgeMode();
                }
            };
        })(),
        (() => {
            const config = resolveSlider('nodeScale', {
                label: 'NODE SCALE',
                min: 0.6,
                max: 2.5,
                step: 0.1,
                value: 1
            });
            return {
                id: 'node-scale',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: APPEARANCE_STATE.nodeScale ?? config.default,
                onChange: (val) => {
                    APPEARANCE_STATE.nodeScale = val;
                    refreshGraph();
                }
            };
        })(),
        (() => {
            const config = resolveSlider('backgroundBrightness', {
                label: 'BACKGROUND',
                min: 0,
                max: 1,
                step: 0.05,
                value: 1
            });
            return {
                id: 'bg-brightness',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: APPEARANCE_STATE.backgroundBrightness ?? config.default,
                onChange: (val) => {
                    APPEARANCE_STATE.backgroundBrightness = val;
                    updateBackgroundBrightness();
                }
            };
        })(),
        (() => {
            const config = resolveSlider('fileLightness', {
                label: 'FILE LIGHT',
                min: 20,
                max: 80,
                step: 1,
                value: 50
            });
            return {
                id: 'file-lightness',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: APPEARANCE_STATE.fileLightness ?? config.default,
                onChange: (val) => {
                    FILE_COLOR_CONFIG.lightness = val;
                    APPEARANCE_STATE.fileLightness = val;
                    if (fileMode) {
                        applyFileVizMode();
                    }
                }
            };
        })(),
        (() => {
            const config = resolveSlider('hueShift', {
                label: 'HUE SHIFT',
                min: -180,
                max: 180,
                step: 1,
                value: 0
            });
            return {
                id: 'hue-shift',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: COLOR_TWEAKS.hueShift ?? config.default,
                onChange: (val) => {
                    COLOR_TWEAKS.hueShift = val;
                    Color.setTransform('hueShift', val);  // Sync to ColorOrchestrator
                    renderAllLegends();  // Re-render legends with new colors
                    refreshGraph();
                }
            };
        })(),
        (() => {
            const config = resolveSlider('chromaScale', {
                label: 'CHROMA SCALE',
                min: 0,
                max: 2,
                step: 0.05,
                value: 1
            });
            return {
                id: 'chroma-scale',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: COLOR_TWEAKS.chromaScale ?? config.default,
                onChange: (val) => {
                    COLOR_TWEAKS.chromaScale = val;
                    Color.setTransform('chromaScale', val);  // Sync to ColorOrchestrator
                    renderAllLegends();  // Re-render legends with new colors
                    refreshGraph();
                }
            };
        })(),
        (() => {
            const config = resolveSlider('lightnessShift', {
                label: 'LIGHT SHIFT',
                min: -20,
                max: 20,
                step: 1,
                value: 0
            });
            return {
                id: 'lightness-shift',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: COLOR_TWEAKS.lightnessShift ?? config.default,
                onChange: (val) => {
                    COLOR_TWEAKS.lightnessShift = val;
                    Color.setTransform('lightnessShift', val);  // Sync to ColorOrchestrator
                    renderAllLegends();  // Re-render legends with new colors
                    refreshGraph();
                }
            };
        })(),
        (() => {
            const config = resolveSlider('boundaryOpacity', {
                label: 'HULL OPACITY',
                min: 0.02,
                max: 0.25,
                step: 0.01,
                value: 0.1
            });
            return {
                id: 'boundary-fill',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: APPEARANCE_STATE.boundaryFill ?? config.default,
                onChange: (val) => {
                    APPEARANCE_STATE.boundaryFill = val;
                    if (fileMode && fileVizMode === 'hulls') {
                        drawFileBoundaries(null);  // Uses DM internally
                    }
                }
            };
        })(),
        (() => {
            const config = resolveSlider('hullWireOpacity', {
                label: 'HULL WIRE',
                min: 0.05,
                max: 0.6,
                step: 0.02,
                value: 0.35
            });
            return {
                id: 'boundary-wire',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: APPEARANCE_STATE.boundaryWire ?? config.default,
                onChange: (val) => {
                    APPEARANCE_STATE.boundaryWire = val;
                    if (fileMode && fileVizMode === 'hulls') {
                        drawFileBoundaries(null);  // Uses DM internally
                    }
                }
            };
        })(),
        (() => {
            const config = resolveSlider('clusterStrength', {
                label: 'CLUSTER FORCE',
                min: 0,
                max: 1,
                step: 0.1,
                value: 0.45
            });
            return {
                id: 'cluster-strength',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: APPEARANCE_STATE.clusterStrength ?? config.default,
                onChange: (val) => {
                    APPEARANCE_STATE.clusterStrength = val;
                    if (fileMode && fileVizMode === 'cluster') {
                        applyClusterForce(null);  // Uses DM internally
                    }
                }
            };
        })(),
        // ═══════════════════════════════════════════════════════════
        // AMPLIFIER SLIDER - Power law exponent for visual contrast
        // γ=1 linear, γ>1 amplifies small differences, γ<1 compresses
        // Formula: amplified = value^(1/γ)
        // ═══════════════════════════════════════════════════════════
        (() => {
            const config = resolveSlider('amplifier', {
                label: 'AMPLIFIER (γ)',
                min: 0.3,
                max: 5.0,
                step: 0.1,
                value: 1.0
            });
            return {
                id: 'amplifier',
                label: config.label,
                min: config.min,
                max: config.max,
                step: config.step,
                value: APPEARANCE_STATE.amplifier ?? config.default,
                className: 'meta-amplifier',  // Special styling for meta-slider
                description: 'γ>1 amplifies differences, γ<1 compresses',
                onChange: (val) => {
                    APPEARANCE_STATE.amplifier = val;
                    // Re-apply edge mode to update widths with new amplification
                    applyEdgeMode();
                    // If in flow mode, re-apply flow visualization
                    if (flowMode) {
                        applyFlowVisualization();
                    }
                }
            };
        })()
    ];

    sliderDefs.forEach(def => {
        const wrapper = document.createElement('div');
        wrapper.className = 'slider-row' + (def.className ? ' ' + def.className : '');

        // Header row with label and value
        const header = document.createElement('div');
        header.className = 'slider-header';
        const label = document.createElement('span');
        label.className = 'slider-label';
        label.textContent = def.label;
        const valueDisplay = document.createElement('span');
        valueDisplay.className = 'slider-value';
        valueDisplay.id = def.id + '-value';
        valueDisplay.textContent = def.value.toFixed(def.step < 1 ? 2 : 0);
        header.appendChild(label);
        header.appendChild(valueDisplay);

        // The slider input
        const input = document.createElement('input');
        input.type = 'range';
        input.className = 'slider-input';
        input.id = def.id;
        input.min = def.min;
        input.max = def.max;
        input.step = def.step;
        input.value = def.value;
        input.oninput = () => {
            const val = parseFloat(input.value);
            valueDisplay.textContent = val.toFixed(def.step < 1 ? 2 : 0);
            def.onChange(val);
        };

        wrapper.appendChild(header);
        wrapper.appendChild(input);

        // Optional description for meta-sliders
        if (def.description) {
            const desc = document.createElement('div');
            desc.className = 'slider-desc';
            desc.textContent = def.description;
            wrapper.appendChild(desc);
        }

        container.appendChild(wrapper);
    });
}

function updateBackgroundBrightness() {
    if (!Graph || !APPEARANCE_STATE.backgroundBase) return;
    const baseColor = new THREE.Color(APPEARANCE_STATE.backgroundBase);
    const brightness = APPEARANCE_STATE.backgroundBrightness ?? 1;
    const adjusted = baseColor.clone().multiplyScalar(brightness);
    Graph.backgroundColor(`#${adjusted.getHexString()}`);
}

function applyMetadataVisibility() {
    const reportPanel = document.getElementById('report-panel');
    const reportButton = document.getElementById('btn-report');
    const filePanel = document.getElementById('file-panel');
    if (!VIS_FILTERS.metadata.showReportPanel) {
        reportPanel.style.display = 'none';
        reportButton.classList.remove('active');
        reportButton.style.display = 'none';
    } else {
        reportButton.style.display = 'inline-flex';
    }
    if (!VIS_FILTERS.metadata.showFilePanel && filePanel) {
        filePanel.classList.remove('visible');
    }
}

// Deprecated setupSidebar - replaced by UIManager
// Deprecated buildDatamapControls - replaced by UIManager


// ═══════════════════════════════════════════════════════════════
// PRESET BUTTONS - Quick visualization mode selection (Tier, Family, etc.)
// ═══════════════════════════════════════════════════════════════
const presetGrid = document.getElementById('dock-presets');
const presetBtnGrid = document.getElementById('preset-grid');
if (presetBtnGrid) {
    presetBtnGrid.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const presetKey = btn.dataset.preset;
            const preset = VIS_PRESETS[presetKey];
            if (!preset) return;

            // Update active states
            presetBtnGrid.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
            const colorSchemeGridEl = document.getElementById('dock-schemes');
            if (colorSchemeGridEl) colorSchemeGridEl.querySelectorAll('.color-scheme-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            APPEARANCE_STATE.currentPreset = presetKey;
            APPEARANCE_STATE.colorMode = preset.colorBy;

            // Apply node color mode
            setNodeColorMode(preset.colorBy);

            // Apply edge mode
            const edgeModes = { 'type': 'gradient-tier', 'weight': 'weight', 'resolution': 'gradient-file' };
            EDGE_MODE = edgeModes[preset.edgeBy] || preset.edgeBy || 'gradient-tier';
            applyEdgeMode();

            // Handle flow mode for 'flow' preset
            if (presetKey === 'flow') {
                if (!flowMode && typeof toggleFlowMode === 'function') toggleFlowMode();
            } else if (flowMode && typeof disableFlowMode === 'function') {
                disableFlowMode();
            }

            // Refresh gradient edges to pick up new node colors
            if (typeof window.refreshGradientEdgeColors === 'function') {
                window.refreshGradientEdgeColors();
            }

            // Re-render legends
            if (typeof renderAllLegends === 'function') {
                renderAllLegends();
            }

            console.log('[Preset] Applied:', preset.name, '| colorBy:', preset.colorBy, '| edgeBy:', preset.edgeBy);
        });
    });
}

// ═══════════════════════════════════════════════════════════════
// OKLCH COLOR SCHEME BUTTONS - L, C, H move together coherently
// ═══════════════════════════════════════════════════════════════
const colorSchemeGrid = document.getElementById('dock-schemes');
if (colorSchemeGrid) {
    colorSchemeGrid.querySelectorAll('.color-scheme-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const presetKey = btn.dataset.preset;
            const preset = VIS_PRESETS[presetKey];
            if (!preset || !preset.isColorScheme) return;

            // Update active states
            colorSchemeGrid.querySelectorAll('.color-scheme-btn').forEach(b => b.classList.remove('active'));
            if (presetGrid) presetGrid.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            APPEARANCE_STATE.currentPreset = presetKey;
            APPEARANCE_STATE.colorMode = preset.colorBy;

            // Clear dimension filters to ensure consistent node count across schemes
            // This prevents stale tier/ring/family filters from affecting the new view
            VIS_FILTERS.tiers.clear();
            VIS_FILTERS.rings.clear();
            VIS_FILTERS.families.clear();
            VIS_FILTERS.roles.clear();
            VIS_FILTERS.files.clear();
            VIS_FILTERS.edges.clear();
            VIS_FILTERS.layers.clear();
            VIS_FILTERS.effects.clear();
            VIS_FILTERS.edgeFamilies.clear();
            // Update UI to reflect cleared filters
            document.querySelectorAll('.topo-legend-item.filtered').forEach(el => el.classList.remove('filtered'));
            document.querySelectorAll('.filter-chip.active').forEach(el => el.classList.remove('active'));
            console.log('[Preset] Cleared dimension filters for clean preset switch');

            // Apply node color mode
            setNodeColorMode(preset.colorBy === 'layer' ? 'tier' : preset.colorBy);

            // Apply edge mode
            const edgeModes = { 'type': 'gradient-tier', 'weight': 'weight', 'resolution': 'gradient-file' };
            EDGE_MODE = edgeModes[preset.edgeBy] || preset.edgeBy || 'gradient-tier';

            // OKLCH transforms - BOLD application
            if (preset.oklch) {
                const oklch = preset.oklch;
                const hue = document.getElementById('hue-shift');
                const chroma = document.getElementById('chroma-scale');
                const light = document.getElementById('light-shift');
                const bg = document.getElementById('background-brightness');

                // Apply hue shift
                if (oklch.H && hue) {
                    hue.value = oklch.H.shift || 0;
                    hue.dispatchEvent(new Event('input'));
                }
                // Apply chroma boost (use full value for dramatic effect)
                if (oklch.C && chroma) {
                    chroma.value = oklch.C.boost || 1;
                    chroma.dispatchEvent(new Event('input'));
                }
                // Apply lightness from preset
                if (light) {
                    const lightVal = preset.lightness !== undefined ? preset.lightness : 0;
                    light.value = lightVal;
                    light.dispatchEvent(new Event('input'));
                }
                // Apply background darkness
                if (oklch.bgL !== undefined && bg) {
                    bg.value = Math.min(1, oklch.bgL * 12);
                    bg.dispatchEvent(new Event('input'));
                }
            }

            // Apply amplifier (higher = more contrast)
            if (preset.amplifier) {
                const amp = document.getElementById('amplifier');
                if (amp) {
                    amp.value = preset.amplifier;
                    amp.dispatchEvent(new Event('input'));
                }
            }

            applyEdgeMode();

            // Refresh gradient edges to pick up new node colors
            if (typeof window.refreshGradientEdgeColors === 'function') {
                window.refreshGradientEdgeColors();
            }

            // Re-render legends with updated colors from ColorOrchestrator
            if (typeof renderAllLegends === 'function') {
                renderAllLegends();
            }

            // Handle flow mode
            if (preset.edgeBy === 'weight' || preset.edgeBy === 'gradient-flow') {
                if (!flowMode && typeof toggleFlowMode === 'function') toggleFlowMode();
            } else if (flowMode && typeof disableFlowMode === 'function') {
                disableFlowMode();
            }

            console.log('[OKLCH] Applied:', preset.name, '| Color.transform:', Color.transform);
        });
    });
}

// ═══════════════════════════════════════════════════════════════
// LAYOUT BUTTONS - Graph layout presets with perpetual motion
// ═══════════════════════════════════════════════════════════════
const layoutGrid = document.getElementById('layout-grid');
if (layoutGrid) {
    layoutGrid.querySelectorAll('.layout-btn').forEach(btn => {
        const layoutKey = btn.dataset.layout;
        // Assign ID if missing for Registry
        if (!btn.id) btn.id = `layout-btn-${layoutKey}`;

        REGISTRY.register(btn.id, () => {
            if (!layoutKey || !LAYOUT_PRESETS[layoutKey]) return;

            // Update active state
            layoutGrid.querySelectorAll('.layout-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Apply the layout
            applyLayoutPreset(layoutKey, true);

            console.log('[Layout] Applied:', LAYOUT_PRESETS[layoutKey].name);
        }, { desc: `Activate ${layoutKey} layout` });
    });
}

// VIEW section controls
buildExclusiveOptions('filter-node-color', [
    { label: 'TIER', value: 'tier' },
    { label: 'RING', value: 'ring' },
    { label: 'FAMILY', value: 'family' },
    { label: 'LAYER', value: 'layer' },
    { label: 'FILE', value: 'file' }
], NODE_COLOR_MODE, setNodeColorMode);
buildExclusiveOptions('filter-edge-mode', [
    { label: 'GRAD-FILE', value: 'gradient-file' },
    { label: 'GRAD-TIER', value: 'gradient-tier' },
    { label: 'GRAD-FLOW', value: 'gradient-flow' },
    { label: 'TYPE', value: 'type' },
    { label: 'WEIGHT', value: 'weight' },
    { label: 'MONO', value: 'mono' }
], EDGE_MODE, setEdgeMode);
buildMetadataControls('filter-metadata', VIS_FILTERS.metadata);
buildAppearanceSliders('appearance-sliders', {}); // controlsConfig removed - sliders built dynamically

applyMetadataVisibility();
updateBackgroundBrightness();
refreshGraph();

function setupCollapsibleSections() {
    // Standard sidebar sections
    const titles = document.querySelectorAll('.side-title.collapsible');
    titles.forEach(title => {
        title.onclick = () => {
            const targetId = title.dataset.target;
            const content = document.getElementById(targetId);
            const icon = title.querySelector('.collapse-icon');
            if (content) {
                const isCollapsed = content.classList.toggle('collapsed');
                title.classList.toggle('collapsed', isCollapsed);
                if (icon) icon.textContent = isCollapsed ? '▶' : '▼';
            }
        };
    });

    // Topology section collapsibles (GEOMETRY panel)
    const topoTitles = document.querySelectorAll('.topo-section-title.collapsible');
    topoTitles.forEach(title => {
        title.onclick = () => {
            const targetId = title.dataset.target;
            const content = document.getElementById(targetId);
            const icon = title.querySelector('.collapse-icon');
            if (content) {
                const isCollapsed = content.classList.toggle('collapsed');
                title.classList.toggle('expanded', !isCollapsed);
                if (icon) icon.textContent = isCollapsed ? '▶' : '▼';
            }
        };
    });
}

function setupReport(data) {
    const panel = document.getElementById('report-panel');
    const content = document.getElementById('report-content');
    const report = (data && data.brain_download) ? data.brain_download : '';
    content.textContent = report || 'No report available.';
}

function setupAIInsights(data) {
    const panel = document.getElementById('insights-panel');
    const content = document.getElementById('insights-content');
    const btn = document.getElementById('btn-insights');

    const insights = (data && data.ai_insights) ? data.ai_insights : null;

    if (!insights) {
        // Hide the button if no insights available
        if (btn) btn.style.display = 'none';
        return;
    }

    // Show the button
    if (btn) btn.style.display = 'inline-flex';

    // Render insights
    let html = '';

    // Executive Summary
    if (insights.executive_summary) {
        html += `<div class="insights-section">
            <div class="insights-section-title">Executive Summary</div>
            <div class="insights-summary">${escapeHtml(insights.executive_summary)}</div>
        </div>`;
    }

    // Patterns Detected
    if (insights.patterns_detected && insights.patterns_detected.length > 0) {
        html += `<div class="insights-section">
            <div class="insights-section-title">Patterns Detected</div>`;
        for (const pattern of insights.patterns_detected) {
            const confidencePercent = Math.round((pattern.confidence || 0) * 100);
            html += `<div class="insights-pattern">
                <div class="insights-pattern-header">
                    <span class="insights-pattern-name">${escapeHtml(pattern.pattern_name || 'Unknown')}</span>
                    <span class="insights-pattern-type ${pattern.pattern_type || ''}">${escapeHtml(pattern.pattern_type || '')}</span>
                </div>
                <div class="insights-confidence">
                    <div class="insights-confidence-bar">
                        <div class="insights-confidence-fill" style="width: ${confidencePercent}%"></div>
                    </div>
                    <span>${confidencePercent}%</span>
                </div>
                ${pattern.evidence ? `<div class="insights-pattern-evidence">${escapeHtml(pattern.evidence)}</div>` : ''}
                ${pattern.recommendation ? `<div class="insights-pattern-evidence" style="color: var(--color-accent-secondary);">💡 ${escapeHtml(pattern.recommendation)}</div>` : ''}
            </div>`;
        }
        html += '</div>';
    }

    // Refactoring Opportunities
    if (insights.refactoring_opportunities && insights.refactoring_opportunities.length > 0) {
        html += `<div class="insights-section">
            <div class="insights-section-title">Refactoring Opportunities</div>`;
        for (const refactor of insights.refactoring_opportunities) {
            html += `<div class="insights-refactor">
                <div class="insights-refactor-title">
                    ${escapeHtml(refactor.title || 'Untitled')}
                    <span class="insights-refactor-priority ${refactor.priority || 'LOW'}">${refactor.priority || 'LOW'}</span>
                </div>
                ${refactor.description ? `<div class="insights-refactor-desc">${escapeHtml(refactor.description)}</div>` : ''}
                ${refactor.affected_files && refactor.affected_files.length > 0 ?
                    `<div class="insights-refactor-desc" style="margin-top: 4px; color: var(--color-text-muted);">Files: ${refactor.affected_files.slice(0, 3).map(f => escapeHtml(f)).join(', ')}${refactor.affected_files.length > 3 ? '...' : ''}</div>` : ''}
            </div>`;
        }
        html += '</div>';
    }

    // Topology Analysis
    if (insights.topology_analysis) {
        const topo = insights.topology_analysis;
        html += `<div class="insights-section">
            <div class="insights-section-title">Topology Analysis</div>
            ${topo.shape_interpretation ? `<div class="insights-summary">${escapeHtml(topo.shape_interpretation)}</div>` : ''}
            ${topo.health_assessment ? `<div class="insights-pattern-evidence">🏥 Health: ${escapeHtml(topo.health_assessment)}</div>` : ''}
            ${topo.coupling_analysis ? `<div class="insights-pattern-evidence">🔗 Coupling: ${escapeHtml(topo.coupling_analysis)}</div>` : ''}
        </div>`;
    }

    // Risk Areas
    if (insights.risk_areas && insights.risk_areas.length > 0) {
        html += `<div class="insights-section">
            <div class="insights-section-title">Risk Areas</div>`;
        for (const risk of insights.risk_areas) {
            html += `<div class="insights-risk">
                <span class="insights-risk-level ${risk.risk_level || 'LOW'}">${risk.risk_level || 'LOW'}</span>
                <div class="insights-risk-content">
                    <div class="insights-risk-area">${escapeHtml(risk.area || 'Unknown')}</div>
                    ${risk.description ? `<div class="insights-risk-desc">${escapeHtml(risk.description)}</div>` : ''}
                    ${risk.mitigation ? `<div class="insights-risk-desc" style="color: var(--color-accent-secondary); margin-top: 4px;">💡 ${escapeHtml(risk.mitigation)}</div>` : ''}
                </div>
            </div>`;
        }
        html += '</div>';
    }

    // Meta information
    if (insights.meta) {
        const meta = insights.meta;
        html += `<div class="insights-meta">
            Generated: ${meta.generated_at ? new Date(meta.generated_at).toLocaleString() : 'Unknown'}
            | Model: ${escapeHtml(meta.model || 'Unknown')}
            ${meta.confidence ? ` | Confidence: ${Math.round(meta.confidence * 100)}%` : ''}
        </div>`;
    }

    content.innerHTML = html || '<div class="insights-placeholder">No insights data available.</div>';
}

// Helper function for HTML escaping (if not already defined)
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setupMetrics(data) {
    const kpis = (data && data.kpis) ? data.kpis : {};
    const setText = (id, value) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.textContent = value;
    };
    const asNumber = (val) => {
        const num = Number(val);
        return Number.isFinite(num) ? num : null;
    };
    const formatPercent = (val) => {
        const num = asNumber(val);
        return num === null ? '--' : `${num.toFixed(1)}%`;
    };
    const formatCount = (val) => {
        const num = asNumber(val);
        return num === null ? '--' : `${Math.round(num)}`;
    };
    const formatScore = (val) => {
        const num = asNumber(val);
        return num === null ? '--' : `${num.toFixed(1)}/10`;
    };

    setText('metric-edge-resolution', formatPercent(kpis.edge_resolution_percent));
    setText('metric-call-ratio', formatPercent(kpis.call_ratio_percent));
    setText('metric-reachability', formatPercent(kpis.reachability_percent));
    setText('metric-dead-code', formatPercent(kpis.dead_code_percent));
    setText('metric-knot-score', formatScore(kpis.knot_score));
    setText('metric-topology', kpis.topology_shape || 'UNKNOWN');
    setText('metric-orphans', formatCount(kpis.orphan_count));
    setText('metric-top-hubs', formatCount(kpis.top_hub_count));

    // Set health indicators (traffic light bars)
    const setHealth = (id, level) => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.remove('good', 'medium', 'bad', 'neutral');
            el.classList.add(level);
        }
    };

    // Edge Resolution: >90% good, 70-90% medium, <70% bad
    const edgeRes = asNumber(kpis.edge_resolution_percent);
    setHealth('health-edge-resolution', edgeRes === null ? 'neutral' : edgeRes >= 90 ? 'good' : edgeRes >= 70 ? 'medium' : 'bad');

    // Call Ratio: >60% good, 40-60% medium, <40% bad
    const callRatio = asNumber(kpis.call_ratio_percent);
    setHealth('health-call-ratio', callRatio === null ? 'neutral' : callRatio >= 60 ? 'good' : callRatio >= 40 ? 'medium' : 'bad');

    // Reachability: >90% good, 70-90% medium, <70% bad
    const reach = asNumber(kpis.reachability_percent);
    setHealth('health-reachability', reach === null ? 'neutral' : reach >= 90 ? 'good' : reach >= 70 ? 'medium' : 'bad');

    // Dead Code: <5% good, 5-15% medium, >15% bad (INVERTED - lower is better)
    const dead = asNumber(kpis.dead_code_percent);
    setHealth('health-dead-code', dead === null ? 'neutral' : dead <= 5 ? 'good' : dead <= 15 ? 'medium' : 'bad');

    // Knot Score: <3 good, 3-6 medium, >6 bad (INVERTED - lower is better)
    const knot = asNumber(kpis.knot_score);
    setHealth('health-knot-score', knot === null ? 'neutral' : knot <= 3 ? 'good' : knot <= 6 ? 'medium' : 'bad');

    // Topology: neutral (informational only)
    setHealth('health-topology', 'neutral');

    // Orphans: <10 good, 10-50 medium, >50 bad (INVERTED - lower is better)
    const orphans = asNumber(kpis.orphan_count);
    setHealth('health-orphans', orphans === null ? 'neutral' : orphans <= 10 ? 'good' : orphans <= 50 ? 'medium' : 'bad');

    // Top Hubs: neutral (informational only)
    setHealth('health-top-hubs', 'neutral');
}

function setupHudFade() {
    const idleDelay = 2200;
    let timer = null;
    const activate = () => {
        document.body.classList.remove('hud-quiet');
        if (timer) {
            clearTimeout(timer);
        }
        timer = setTimeout(() => {
            document.body.classList.add('hud-quiet');
        }, idleDelay);
    };
    ['mousemove', 'mousedown', 'keydown', 'touchstart'].forEach((evt) => {
        window.addEventListener(evt, activate, { passive: true });
    });
    activate();
}

// =================================================================
// HUD STATS: Update all header and stats panel elements
// =================================================================
function updateHudStats(data) {
    if (!data) return;

    // Stats panel: NODES, EDGES, ENTROPY
    const nodeCount = (data.nodes || []).length;
    const edgeCount = (data.links || []).length;

    const statNodes = document.getElementById('stat-nodes');
    const statEdges = document.getElementById('stat-edges');
    const statEntropy = document.getElementById('stat-entropy');

    if (statNodes) statNodes.textContent = nodeCount.toLocaleString();
    if (statEdges) statEdges.textContent = edgeCount.toLocaleString();
    if (statEntropy) {
        const entropy = data.meta?.entropy ?? data.entropy ?? '--';
        statEntropy.textContent = typeof entropy === 'number' ? entropy.toFixed(2) : entropy;
    }

    // Header panel: target name and timestamp
    const targetName = document.getElementById('target-name');
    const timestamp = document.getElementById('timestamp');

    if (targetName) {
        const target = data.meta?.target || data.target || 'Unknown';
        // Show just the last part of the path
        const shortTarget = target.split('/').pop() || target;
        targetName.textContent = shortTarget;
    }

    if (timestamp) {
        const ts = data.meta?.timestamp || data.timestamp || '';
        // Format: 2024-01-15T10:30:00 -> 2024-01-15 10:30
        const formatted = ts.replace('T', ' ').substring(0, 16);
        timestamp.textContent = formatted || 'Live';
    }
}

function showToast(message) {
    const toast = document.getElementById('hud-toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('visible');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
        toast.classList.remove('visible');
    }, 2200);
}

function updateDatamapControls() {
    if (!DM) return;  // ALL DATA FROM DM
    const datamapEnabled = GRAPH_MODE === 'atoms';
    const base = filterGraph(null, CURRENT_DENSITY, new Set(), VIS_FILTERS);  // DM used internally
    const nodes = base.nodes || [];
    const totalCount = nodes.length;

    const allUI = DATAMAP_UI.get('__ALL__');
    if (allUI) {
        allUI.input.checked = ACTIVE_DATAMAPS.size === 0;
        if (allUI.count) {
            allUI.count.textContent = datamapEnabled ? String(totalCount) : '--';
        }
        allUI.input.disabled = !datamapEnabled;
        allUI.wrapper.classList.toggle('disabled', !datamapEnabled);
        allUI.wrapper.classList.toggle('active', datamapEnabled && ACTIVE_DATAMAPS.size === 0);
    }

    DATAMAP_CONFIGS.forEach((config) => {
        const count = nodes.reduce((acc, node) => acc + (datamapMatches(node, config) ? 1 : 0), 0);
        const ui = DATAMAP_UI.get(config.id);
        if (!ui) return;
        if (ui.count) {
            ui.count.textContent = datamapEnabled ? String(count) : '--';
        }
        ui.input.disabled = !datamapEnabled || count === 0;
        ui.wrapper.classList.toggle('disabled', !datamapEnabled || count === 0);
        ui.input.checked = ACTIVE_DATAMAPS.has(config.id);
        ui.wrapper.classList.toggle('active', datamapEnabled && ACTIVE_DATAMAPS.has(config.id));
    });
}

// Callable function for direct invocation (no proxy click needed)
function toggleDimensions() {
    if (DIMENSION_TRANSITION) return;
    DIMENSION_TRANSITION = true;
    const target3d = !IS_3D;
    const button = document.getElementById('btn-dimensions');
    animateDimensionChange(target3d, () => {
        IS_3D = target3d;
        DIMENSION_TRANSITION = false;
        if (button) button.textContent = IS_3D ? '2D' : '3D';
        if (fileMode && GRAPH_MODE === 'atoms') {
            applyFileVizMode();
        }
    });
}

function setupDimensionToggle() {
    const button = document.getElementById('btn-dimensions');
    const updateLabel = () => {
        button.textContent = IS_3D ? '2D' : '3D';
    };
    updateLabel();
    button.onclick = () => toggleDimensions();
}

function stableSeed(node, salt) {
    const id = String(node.id || node.name || '');
    const combined = `${id}|${salt}`;
    let hash = 0;
    for (let i = 0; i < combined.length; i++) {
        hash = ((hash << 5) - hash + combined.charCodeAt(i)) | 0;
    }
    return ((hash >>> 0) % 1000) / 1000;
}

function stableZ(node) {
    const normalized = stableSeed(node, 'z');
    return (normalized - 0.5) * 60;
}

function animateDimensionChange(target3d, done) {
    const nodes = (Graph && Graph.graphData().nodes) ? Graph.graphData().nodes : [];
    const startTime = performance.now();
    const duration = 3000;
    const delayMin = 0;
    const delayMax = 2000;
    const lockPositionsAfterTransition = true;
    const easeInOutSine = (t) => 0.5 - 0.5 * Math.cos(Math.PI * t);
    const starStart = STARFIELD ? STARFIELD.material.opacity : 0;
    const starTarget = target3d ? STARFIELD_OPACITY : 0;
    const bloomStart = BLOOM_PASS ? BLOOM_PASS.strength : 0;
    const bloomTarget = BLOOM_PASS ? (target3d ? BLOOM_STRENGTH : 0) : 0;
    const previousVelocityDecay = (Graph && Graph.d3VelocityDecay) ? Graph.d3VelocityDecay() : null;
    const previousAlphaTarget = (Graph && Graph.d3AlphaTarget) ? Graph.d3AlphaTarget() : null;
    const previousCooldownTicks = (Graph && Graph.cooldownTicks) ? Graph.cooldownTicks() : null;
    const previousCooldownTime = (Graph && Graph.cooldownTime) ? Graph.cooldownTime() : null;
    if (Graph && Graph.cooldownTicks) {
        Graph.cooldownTicks(Infinity);
    }
    if (Graph && Graph.cooldownTime) {
        Graph.cooldownTime(Infinity);
    }
    if (Graph && Graph.d3VelocityDecay) {
        Graph.d3VelocityDecay(1);
    }
    if (Graph && Graph.d3AlphaTarget) {
        Graph.d3AlphaTarget(0);
    }
    if (Graph && Graph.d3ReheatSimulation) {
        Graph.d3ReheatSimulation();
    }

    nodes.forEach((node) => {
        node.__xStart = node.x || 0;
        node.__yStart = node.y || 0;
        node.__zStart = node.z || 0;
        node.__delay = delayMin + (stableSeed(node, 'delay') * (delayMax - delayMin));
        node.fx = node.__xStart;
        node.fy = node.__yStart;
        node.vx = 0;
        node.vy = 0;
        node.vz = 0;
        if (target3d) {
            if (node.__z3d === undefined || node.__z3d === null) {
                node.__z3d = node.__zStart || stableZ(node);
            }
        } else {
            node.__z3d = node.__zStart;
        }
    });

    const maxDistance = nodes.reduce((acc, node) => Math.max(acc, Math.abs(node.__zStart || 0)), 1);

    Graph.numDimensions(3);

    const animate = (now) => {
        const elapsed = now - startTime;
        const t = Math.min(1, elapsed / duration);
        const eased = easeInOutSine(t);

        nodes.forEach((node) => {
            const startZ = node.__zStart || 0;
            const targetZ = target3d ? (node.__z3d || 0) : 0;
            const delay = node.__delay || 0;
            const localDuration = Math.max(600, duration - delay);
            const localElapsed = Math.max(0, elapsed - delay);
            const localT = Math.min(1, localElapsed / localDuration);
            const localEase = easeInOutSine(localT);
            const distanceRatio = maxDistance > 0 ? Math.abs(startZ) / maxDistance : 0;
            const distanceCurve = 0.6 + (1 - distanceRatio) * 0.6;
            const progress = Math.pow(localEase, distanceCurve);
            const nextZ = startZ + (targetZ - startZ) * progress;
            node.z = nextZ;
            node.fz = nextZ;
            node.vz = 0;
        });

        if (STARFIELD) {
            const nextOpacity = starStart + (starTarget - starStart) * eased;
            STARFIELD.material.opacity = nextOpacity;
            STARFIELD.visible = nextOpacity > 0.02;
        }
        if (BLOOM_PASS) {
            BLOOM_PASS.strength = bloomStart + (bloomTarget - bloomStart) * eased;
        }

        if (t < 1) {
            requestAnimationFrame(animate);
        } else {
            nodes.forEach((node) => {
                delete node.fz;
                delete node.__zStart;
                delete node.__xStart;
                delete node.__yStart;
                delete node.__delay;
                if (!target3d) {
                    node.z = 0;
                    node.fz = 0;
                } else if (lockPositionsAfterTransition) {
                    node.z = node.__z3d || node.z || 0;
                    node.fz = node.z;
                } else {
                    delete node.fx;
                    delete node.fy;
                }
            });
            Graph.numDimensions(target3d ? 3 : 2);
            if (!target3d && STARFIELD) {
                STARFIELD.visible = false;
            }
            if (Graph && Graph.d3VelocityDecay && previousVelocityDecay !== null) {
                Graph.d3VelocityDecay(previousVelocityDecay);
            }
            if (Graph && Graph.d3AlphaTarget && previousAlphaTarget !== null) {
                Graph.d3AlphaTarget(previousAlphaTarget);
            }
            if (Graph && Graph.cooldownTicks && previousCooldownTicks !== null) {
                Graph.cooldownTicks(previousCooldownTicks);
            }
            if (Graph && Graph.cooldownTime && previousCooldownTime !== null) {
                Graph.cooldownTime(previousCooldownTime);
            }
            if (done) done();
        }
    };

    requestAnimationFrame(animate);
}

// ====================================================================
// EDGE VISUALIZATION MODES - GRADIENT & DATA-DRIVEN SYSTEM
// ====================================================================
// NEW: Edge modes with gradients showing data progression & regions
const EDGE_MODE_ORDER = [
    'gradient-tier',      // Source→Target tier flow (architecture layers)
    'gradient-file',      // File boundaries (module regions)
    'gradient-flow',      // Markov probability (hot paths)
    'gradient-depth',     // Call depth progression
    'gradient-semantic',  // Semantic distance (type similarity)
    'type',               // Classic type-based
    'weight',             // Weight intensity
    'mono'                // Minimal monochrome
];
const EDGE_MODE_LABELS = {
    'gradient-tier': '▼ TIER FLOW',
    'gradient-file': '▼ FILE REGIONS',
    'gradient-flow': '▼ HOT PATHS',
    'gradient-depth': '▼ CALL DEPTH',
    'gradient-semantic': '▼ SEMANTIC',
    type: 'EDGE: TYPE',
    weight: 'EDGE: WEIGHT',
    mono: 'EDGE: MONO'
};
const EDGE_MODE_HINTS = {
    'gradient-tier': 'Gradient by architecture tier (T0→T1→T2)',
    'gradient-file': 'Color by file region - shows module boundaries',
    'gradient-flow': 'Hot paths - markov probability gradient',
    'gradient-depth': 'Color by call chain depth',
    'gradient-semantic': 'Color by semantic similarity of endpoints',
    type: 'Edge color by type (calls, imports, etc.)',
    weight: 'Edge width & color by weight',
    mono: 'Minimal monochrome'
};

// Gradient color palettes for different modes
const GRADIENT_PALETTES = {
    tier: {
        // Cool to Warm: Entry (blue) → Core (purple) → Exit (orange)
        T0: { h: 210, s: 70, l: 55 },  // Blue - entry points
        T1: { h: 280, s: 65, l: 50 },  // Purple - core logic
        T2: { h: 30, s: 80, l: 50 },   // Orange - utilities/exit
        UNKNOWN: { h: 0, s: 0, l: 40 } // Gray
    },
    file: {
        // Rainbow hues distributed across files
        saturation: 65,
        lightness: 48
    },
    flow: {
        // Cold (low prob) to Hot (high prob)
        cold: { h: 220, s: 60, l: 45 },   // Blue
        warm: { h: 45, s: 85, l: 50 },    // Yellow
        hot: { h: 0, s: 90, l: 55 }       // Red
    },
    depth: {
        // Shallow (bright) to Deep (dark, saturated)
        shallow: { h: 180, s: 50, l: 65 },  // Light cyan
        mid: { h: 260, s: 70, l: 50 },      // Purple
        deep: { h: 320, s: 80, l: 40 }      // Magenta
    },
    semantic: {
        // Similar (harmonious) to Different (contrasting)
        similar: { h: 150, s: 60, l: 50 },    // Green - same type
        related: { h: 200, s: 65, l: 48 },    // Cyan - related
        different: { h: 340, s: 75, l: 50 }   // Pink - different
    }
};

// Build file hue map for consistent coloring
let FILE_HUE_MAP = new Map();
function buildFileHueMap() {
    if (!DM) return;  // ALL DATA FROM DM
    const files = DM.getFileBoundaries();
    const goldenAngle = 137.508;  // Golden angle for good distribution
    files.forEach((file, idx) => {
        const hue = (idx * goldenAngle) % 360;
        FILE_HUE_MAP.set(idx, hue);
    });
}

// Get node tier value (0=T0, 1=T1, 2=T2)
function getNodeTierValue(node) {
    if (!node) return 1;
    const tier = getNodeTier(node);
    if (tier === 'T0') return 0;
    if (tier === 'T1') return 1;
    if (tier === 'T2') return 2;
    return 1;
}

// Get node depth (distance from entry points)
function getNodeDepth(node) {
    // Use y-position as proxy for depth (force layout tends to layer)
    if (node && typeof node.y === 'number') {
        return Math.abs(node.y) / 500;  // Normalize
    }
    return 0.5;
}

// Get semantic similarity between two nodes
function getSemanticSimilarity(srcNode, tgtNode) {
    if (!srcNode || !tgtNode) return 0.5;
    let score = 0;
    // Same type = high similarity
    if (srcNode.type === tgtNode.type) score += 0.4;
    // Same file = high similarity
    if (srcNode.fileIdx === tgtNode.fileIdx) score += 0.3;
    // Same tier = moderate similarity
    if (getNodeTier(srcNode) === getNodeTier(tgtNode)) score += 0.2;
    // Same ring/layer
    if (srcNode.ring === tgtNode.ring) score += 0.1;
    return score;
}

// Interpolate between two HSL colors
function interpolateHSL(hsl1, hsl2, t) {
    t = clamp01(t);
    // Handle hue interpolation (shortest path on color wheel)
    let h1 = hsl1.h, h2 = hsl2.h;
    let dh = h2 - h1;
    if (Math.abs(dh) > 180) {
        if (dh > 0) h1 += 360;
        else h2 += 360;
    }
    const h = (h1 + (h2 - h1) * t) % 360;
    const s = hsl1.s + (hsl2.s - hsl1.s) * t;
    const l = hsl1.l + (hsl2.l - hsl1.l) * t;
    return hslColor(h, s, l);
}

// Create gradient color for edge based on source and target
function getGradientEdgeColor(link, mode) {
    const srcNode = typeof link.source === 'object' ? link.source :
        (Graph?.graphData()?.nodes?.find(n => n.id === link.source));
    const tgtNode = typeof link.target === 'object' ? link.target :
        (Graph?.graphData()?.nodes?.find(n => n.id === link.target));

    if (mode === 'gradient-tier') {
        // Color by tier transition: T0(blue) → T1(purple) → T2(orange)
        const srcTier = getNodeTierValue(srcNode);
        const tgtTier = getNodeTierValue(tgtNode);
        const avgTier = (srcTier + tgtTier) / 2;

        // Blend based on tier flow direction
        const palette = GRADIENT_PALETTES.tier;
        let color;
        if (avgTier < 0.5) {
            color = interpolateHSL(palette.T0, palette.T1, avgTier * 2);
        } else if (avgTier < 1.5) {
            color = interpolateHSL(palette.T0, palette.T1, (avgTier - 0.5));
        } else {
            color = interpolateHSL(palette.T1, palette.T2, (avgTier - 1) / 2);
        }

        // Highlight tier transitions (edges crossing tiers)
        if (srcTier !== tgtTier) {
            // Make cross-tier edges brighter/more saturated
            return hslColor(
                parseInt(color.slice(4)),
                75,  // Higher saturation
                55   // Brighter
            );
        }
        return color;
    }

    if (mode === 'gradient-file') {
        // Color by file - each file gets unique hue
        const srcFile = srcNode?.fileIdx ?? -1;
        const tgtFile = tgtNode?.fileIdx ?? -1;
        const palette = GRADIENT_PALETTES.file;

        if (srcFile === tgtFile && srcFile >= 0) {
            // Same file: use file's hue
            const hue = FILE_HUE_MAP.get(srcFile) ?? (srcFile * 37 % 360);
            return hslColor(hue, palette.saturation, palette.lightness);
        } else {
            // Cross-file: blend hues or use distinct "boundary" color
            const srcHue = FILE_HUE_MAP.get(srcFile) ?? 0;
            const tgtHue = FILE_HUE_MAP.get(tgtFile) ?? 180;
            // Use midpoint hue with reduced saturation (shows boundary)
            let midHue = (srcHue + tgtHue) / 2;
            if (Math.abs(srcHue - tgtHue) > 180) {
                midHue = (midHue + 180) % 360;
            }
            return hslColor(midHue, palette.saturation * 0.6, palette.lightness * 1.1);
        }
    }

    if (mode === 'gradient-flow') {
        // Color by markov weight (probability flow)
        const mw = link.markov_weight ?? link.weight ?? 0;
        const palette = GRADIENT_PALETTES.flow;

        if (mw < 0.3) {
            return interpolateHSL(palette.cold, palette.warm, mw / 0.3);
        } else if (mw < 0.7) {
            return interpolateHSL(palette.warm, palette.hot, (mw - 0.3) / 0.4);
        } else {
            // Very hot - extra bright
            return hslColor(palette.hot.h, palette.hot.s + 10, palette.hot.l + 10);
        }
    }

    if (mode === 'gradient-depth') {
        // Color by call depth (position in graph)
        const srcDepth = getNodeDepth(srcNode);
        const tgtDepth = getNodeDepth(tgtNode);
        const avgDepth = (srcDepth + tgtDepth) / 2;
        const palette = GRADIENT_PALETTES.depth;

        if (avgDepth < 0.33) {
            return interpolateHSL(palette.shallow, palette.mid, avgDepth * 3);
        } else if (avgDepth < 0.66) {
            return interpolateHSL(palette.mid, palette.deep, (avgDepth - 0.33) * 3);
        } else {
            return hslColor(palette.deep.h, palette.deep.s, palette.deep.l - 10);
        }
    }

    if (mode === 'gradient-semantic') {
        // Color by semantic similarity
        const similarity = getSemanticSimilarity(srcNode, tgtNode);
        const palette = GRADIENT_PALETTES.semantic;

        if (similarity > 0.7) {
            return interpolateHSL(palette.related, palette.similar, (similarity - 0.7) / 0.3);
        } else if (similarity > 0.3) {
            return interpolateHSL(palette.different, palette.related, (similarity - 0.3) / 0.4);
        } else {
            return hslColor(palette.different.h, palette.different.s + 10, palette.different.l);
        }
    }

    // Fallback
    return '#444444';
}

function clamp01(value) {
    return Math.max(0, Math.min(1, value));
}

function clampValue(value, min, max) {
    return Math.max(min, Math.min(max, value));
}

function hslColor(hue, saturation, lightness) {
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

function parseOklchString(value) {
    if (typeof value !== 'string') return null;
    const match = value.trim().match(/^oklch\(\s*([\d.]+)%\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\s*\)$/i);
    if (!match) return null;
    return {
        L: parseFloat(match[1]),
        C: parseFloat(match[2]),
        H: parseFloat(match[3]),
        A: match[4] !== undefined ? parseFloat(match[4]) : 1
    };
}

function applyColorTweaks(lightness, chroma, hue, alpha = 1) {
    const L = clampValue(lightness + (COLOR_TWEAKS.lightnessShift || 0), 0, 100);
    const C = clampValue(chroma * (COLOR_TWEAKS.chromaScale || 1), 0, 0.4);
    const H = (hue + (COLOR_TWEAKS.hueShift || 0) + 360) % 360;
    return [L, C, H, alpha];
}

function oklchToSrgb(L, C, H) {
    const hRad = (H * Math.PI) / 180;
    const a = C * Math.cos(hRad);
    const b = C * Math.sin(hRad);

    const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
    const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
    const s_ = L - 0.0894841775 * a - 1.2914855480 * b;

    const l = l_ ** 3;
    const m = m_ ** 3;
    const s = s_ ** 3;

    let r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s;
    let g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
    let bChan = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s;

    const linearToSrgb = (channel) => {
        if (channel <= 0.0031308) {
            return 12.92 * channel;
        }
        return 1.055 * Math.pow(channel, 1 / 2.4) - 0.055;
    };

    r = linearToSrgb(r);
    g = linearToSrgb(g);
    bChan = linearToSrgb(bChan);

    if (![r, g, bChan].every(Number.isFinite)) {
        return [0.5, 0.5, 0.5];
    }

    return [
        Math.min(1, Math.max(0, r)),
        Math.min(1, Math.max(0, g)),
        Math.min(1, Math.max(0, bChan))
    ];
}

function oklchColor(lightness, chroma, hue, alpha = 1) {
    const rawL = (typeof lightness === 'number') ? lightness : 50;
    const rawC = (typeof chroma === 'number') ? chroma : 0.1;
    const rawH = (typeof hue === 'number') ? hue : 0;
    const [LAdj, CAdj, HAdj, alphaAdj] = applyColorTweaks(rawL, rawC, rawH, alpha);
    const L = LAdj / 100;
    const C = CAdj;
    const H = HAdj;
    const [r, g, b] = oklchToSrgb(L, C, H);
    const rByte = Math.round(r * 255);
    const gByte = Math.round(g * 255);
    const bByte = Math.round(b * 255);
    if (![rByte, gByte, bByte].every(Number.isFinite)) {
        return 'rgb(128, 128, 128)';
    }
    if (alphaAdj < 1) {
        return `rgba(${rByte}, ${gByte}, ${bByte}, ${alphaAdj})`;
    }
    return `rgb(${rByte}, ${gByte}, ${bByte})`;
}

function normalizeColorInput(color, fallback = 'rgb(128, 128, 128)') {
    if (color === null || color === undefined) {
        return fallback;
    }
    if (typeof color !== 'string') {
        return color;
    }
    const parsed = parseOklchString(color);
    if (parsed) {
        return oklchColor(parsed.L, parsed.C, parsed.H, parsed.A);
    }
    return color;
}

function toColorNumber(color, fallback = '#777777') {
    // Returns CSS hex string (polished-compatible) instead of JS hex int
    if (typeof color === 'number') {
        // Convert JS hex int to CSS hex string
        return '#' + color.toString(16).padStart(6, '0');
    }
    if (typeof color !== 'string') {
        return fallback;
    }
    const normalized = normalizeColorInput(color);
    if (typeof normalized === 'string') {
        color = normalized;
    }
    if (color.startsWith('#') || color.startsWith('rgb') || color.startsWith('hsl')) {
        return color;  // Already valid CSS color
    }
    try {
        // Convert any valid color to CSS hex string
        const hex = new THREE.Color(color).getHex();
        return '#' + hex.toString(16).padStart(6, '0');
    } catch (err) {
        return fallback;
    }
}

function updateEdgeRanges() {
    const links = (Graph && Graph.graphData().links) ? Graph.graphData().links : [];
    let minWeight = Infinity;
    let maxWeight = -Infinity;
    let minConf = Infinity;
    let maxConf = -Infinity;
    links.forEach(link => {
        const weight = typeof link.weight === 'number' ? link.weight : 1;
        const confidence = typeof link.confidence === 'number' ? link.confidence : 1;
        minWeight = Math.min(minWeight, weight);
        maxWeight = Math.max(maxWeight, weight);
        minConf = Math.min(minConf, confidence);
        maxConf = Math.max(maxConf, confidence);
    });
    EDGE_RANGES = {
        weight: {
            min: isFinite(minWeight) ? minWeight : 1,
            max: isFinite(maxWeight) ? maxWeight : 1
        },
        confidence: {
            min: isFinite(minConf) ? minConf : 1,
            max: isFinite(maxConf) ? maxConf : 1
        }
    };
}

function refreshNodeFileIndex() {
    NODE_FILE_INDEX = new Map();
    const nodes = (Graph && Graph.graphData().nodes) ? Graph.graphData().nodes : [];
    nodes.forEach(node => {
        if (node && node.id) {
            NODE_FILE_INDEX.set(node.id, node.fileIdx ?? -1);
        }
    });
}

function getLinkFileIdx(link, side) {
    const endpoint = link?.[side];
    if (endpoint && typeof endpoint === 'object') {
        return endpoint.fileIdx ?? -1;
    }
    if (endpoint) {
        return NODE_FILE_INDEX.get(endpoint) ?? -1;
    }
    return -1;
}

function normalizeMetric(value, range) {
    // If range is degenerate (all same values), return based on absolute value:
    // - For 0-1 metrics like confidence: return the value itself
    // - This prevents "all low" coloring when all edges have same high confidence
    if (!range || range.max <= range.min) {
        return clamp01(value);
    }
    return clamp01((value - range.min) / (range.max - range.min));
}

function getEdgeColor(link) {
    // ═══════════════════════════════════════════════════════════════════
    // ALL EDGE COLORS NOW COME FROM ColorOrchestrator (aliased as Color)
    // This ensures legend colors match visualization colors exactly
    // OKLCH transforms are applied automatically
    // ═══════════════════════════════════════════════════════════════════

    // NEW GRADIENT MODES (default!)
    if (EDGE_MODE.startsWith('gradient-')) {
        return getGradientEdgeColor(link, EDGE_MODE);
    }

    const edgeKey = String(link.edge_type || link.type || 'unknown').toLowerCase();

    if (EDGE_MODE === 'type') {
        return Color.get('edgeType', edgeKey);  // FROM ColorOrchestrator
    }

    if (EDGE_MODE === 'weight') {
        const weight = typeof link.weight === 'number' ? link.weight : 1;
        const t = normalizeMetric(weight, EDGE_RANGES.weight);
        return Color.getInterval('weight', t);  // FROM ColorOrchestrator intervals
    }

    if (EDGE_MODE === 'confidence') {
        const confidence = typeof link.confidence === 'number' ? link.confidence : 1;
        const t = normalizeMetric(confidence, EDGE_RANGES.confidence);
        return Color.getInterval('confidence', t);  // FROM ColorOrchestrator intervals
    }

    if (EDGE_MODE === 'mono') {
        return Color.get('edgeType', 'unknown');  // Neutral from ColorOrchestrator
    }

    // Default: type-based coloring
    return Color.get('edgeType', edgeKey);  // FROM ColorOrchestrator
}

function getEdgeWidth(link) {
    // ═══════════════════════════════════════════════════════════════════
    // EDGE WIDTH: Constrained to narrow range for visual coherence
    // Min: 0.6px, Max: 2.2px - prevents chaotic thin/thick variance
    // ═══════════════════════════════════════════════════════════════════
    const MIN_WIDTH = 0.6;
    const MAX_WIDTH = 2.2;
    const BASE_WIDTH = 1.0;

    // For most modes, return uniform width for visual consistency
    if (EDGE_MODE !== 'weight' && EDGE_MODE !== 'confidence') {
        return BASE_WIDTH;
    }

    // Weight/confidence modes: subtle variation within tight bounds
    let t = 0.5;  // Default middle
    if (EDGE_MODE === 'weight') {
        const weight = typeof link.weight === 'number' ? link.weight : 1;
        t = normalizeMetric(weight, EDGE_RANGES.weight);
    } else if (EDGE_MODE === 'confidence') {
        const confidence = typeof link.confidence === 'number' ? link.confidence : 1;
        t = normalizeMetric(confidence, EDGE_RANGES.confidence);
    }

    // Linear interpolation within tight bounds (no amplifier blowup)
    return MIN_WIDTH + (t * (MAX_WIDTH - MIN_WIDTH));
}

function applyEdgeMode() {
    updateEdgeRanges();
    refreshNodeFileIndex();
    buildFileHueMap();  // Build hue map for gradient-file mode
    if (Graph) {
        Graph.linkColor(link => toColorNumber(getEdgeColor(link), 0x222222));
        Graph.linkOpacity(link => {
            const overrideOpacity = (typeof APPEARANCE_STATE.edgeOpacity === 'number')
                ? APPEARANCE_STATE.edgeOpacity
                : null;
            const baseOpacity = (overrideOpacity !== null)
                ? overrideOpacity
                : (link.opacity ?? EDGE_DEFAULT_OPACITY);
            if (fileMode && GRAPH_MODE === 'atoms') {
                const srcIdx = getLinkFileIdx(link, 'source');
                const tgtIdx = getLinkFileIdx(link, 'target');
                if (srcIdx >= 0 && tgtIdx >= 0 && srcIdx !== tgtIdx) {
                    const dimFactor = EDGE_MODE_CONFIG.dim?.interfile_factor ?? 0.25;
                    return baseOpacity * dimFactor;
                }
            }
            return baseOpacity;
        });
        if (!flowMode) {
            Graph.linkWidth(link => getEdgeWidth(link));
        }
    }
}

function cycleEdgeMode() {
    const currentIndex = EDGE_MODE_ORDER.indexOf(EDGE_MODE);
    const nextIndex = (currentIndex + 1) % EDGE_MODE_ORDER.length;
    setEdgeMode(EDGE_MODE_ORDER[nextIndex]);
}

function setEdgeMode(mode) {
    if (!EDGE_MODE_ORDER.includes(mode)) return;
    EDGE_MODE = mode;
    const button = document.getElementById('btn-edge-mode');
    if (button) {
        button.textContent = EDGE_MODE_LABELS[EDGE_MODE] || 'EDGE';
    }
    applyEdgeMode();
    // Update legend to reflect edge mode colors
    if (typeof renderAllLegends === 'function') {
        renderAllLegends();
    }
    // Show mode toast hint
    showModeToast(EDGE_MODE_HINTS[mode] || `Edge mode: ${mode}`);
}

// Datamap toggles are wired in buildDatamapControls().
document.getElementById('btn-report').onclick = () => {
    const panel = document.getElementById('report-panel');
    const btn = document.getElementById('btn-report');
    const isOpen = panel.style.display === 'block';
    panel.style.display = isOpen ? 'none' : 'block';
    btn.classList.toggle('active', !isOpen);
};

// AI INSIGHTS PANEL TOGGLE
const btnInsights = document.getElementById('btn-insights');
if (btnInsights) {
    btnInsights.onclick = () => {
        const panel = document.getElementById('insights-panel');
        const btn = document.getElementById('btn-insights');
        if (!panel) return;
        const isOpen = panel.style.display === 'block';
        panel.style.display = isOpen ? 'none' : 'block';
        btn.classList.toggle('active', !isOpen);
    };
}

// ====================================================================
// STARFIELD TOGGLE: Show/hide background stars (with localStorage)
// ====================================================================
const STARS_STORAGE_KEY = 'collider_stars_visible';

function setStarsVisible(visible) {
    const btn = document.getElementById('btn-stars');
    if (btn) btn.classList.toggle('active', visible);
    if (STARFIELD) {
        STARFIELD.visible = visible;
        STARFIELD.material.opacity = visible ? STARFIELD_OPACITY : 0;
    }
    try {
        localStorage.setItem(STARS_STORAGE_KEY, visible ? '1' : '0');
    } catch (e) { /* localStorage unavailable */ }
}

// Initialize from localStorage (default: visible)
try {
    const stored = localStorage.getItem(STARS_STORAGE_KEY);
    if (stored === '0') {
        // Defer to after STARFIELD is initialized
        setTimeout(() => setStarsVisible(false), 100);
    }
} catch (e) { /* localStorage unavailable */ }

document.getElementById('btn-stars').onclick = () => {
    const btn = document.getElementById('btn-stars');
    const isActive = btn.classList.contains('active');
    setStarsVisible(!isActive);
};

// Reset Layout button - explicitly re-run physics
document.getElementById('btn-reset-layout').onclick = () => {
    resetLayout();
};

// Hints toggle - enable/disable mode toasts
document.getElementById('btn-hints').onclick = () => {
    const btn = document.getElementById('btn-hints');
    HINTS_ENABLED = !HINTS_ENABLED;
    btn.classList.toggle('active', HINTS_ENABLED);
    if (HINTS_ENABLED) {
        showModeToast('Hints enabled');
    }
};

document.getElementById('btn-edge-mode').onclick = () => cycleEdgeMode();

// ====================================================================
// FLOW MODE: Markov Chain Visualization (Token-Driven)
// ====================================================================
// flowMode hoisted to top
let originalLinkWidths = new Map();
let highEntropyNodes = new Set();
// FLOW_CONFIG is set in initGraph() from THE REMOTE CONTROL tokens

// Flow Mode Presets - cycle through by clicking FLOW button repeatedly
const FLOW_PRESETS = [
    {
        name: 'EMBER',
        highlightColor: '#ff8c00',
        particleColor: '#ffaa00',
        dimColor: '#331100',
        edgeColor: '#ff6600',
        particleCount: 3,
        particleWidth: 2.5,
        particleSpeed: 0.008,
        edgeWidthScale: 3.0,
        sizeMultiplier: 1.8,
        edgeOpacityMin: 0.3,
        dimOpacity: 0.05
    },
    {
        name: 'OCEAN',
        highlightColor: '#00d4ff',
        particleColor: '#4df0ff',
        dimColor: '#001122',
        edgeColor: '#0088cc',
        particleCount: 4,
        particleWidth: 2.0,
        particleSpeed: 0.006,
        edgeWidthScale: 2.5,
        sizeMultiplier: 1.6,
        edgeOpacityMin: 0.25,
        dimOpacity: 0.03
    },
    {
        name: 'PLASMA',
        highlightColor: '#ff00ff',
        particleColor: '#ff66ff',
        dimColor: '#110011',
        edgeColor: '#cc00cc',
        particleCount: 5,
        particleWidth: 3.0,
        particleSpeed: 0.012,
        edgeWidthScale: 4.0,
        sizeMultiplier: 2.0,
        edgeOpacityMin: 0.35,
        dimOpacity: 0.04
    },
    {
        name: 'MATRIX',
        highlightColor: '#00ff00',
        particleColor: '#88ff88',
        dimColor: '#001100',
        edgeColor: '#00cc00',
        particleCount: 6,
        particleWidth: 1.5,
        particleSpeed: 0.015,
        edgeWidthScale: 2.0,
        sizeMultiplier: 1.4,
        edgeOpacityMin: 0.2,
        dimOpacity: 0.02
    },
    {
        name: 'PULSE',
        highlightColor: '#ff4444',
        particleColor: '#ff8888',
        dimColor: '#110000',
        edgeColor: '#cc2222',
        particleCount: 2,
        particleWidth: 4.0,
        particleSpeed: 0.004,
        edgeWidthScale: 5.0,
        sizeMultiplier: 2.2,
        edgeOpacityMin: 0.4,
        dimOpacity: 0.06
    },
    {
        name: 'AURORA',
        highlightColor: '#33ccbb',
        particleColor: '#66ffee',
        dimColor: '#002222',
        edgeColor: '#22aa99',
        particleCount: 4,
        particleWidth: 2.2,
        particleSpeed: 0.007,
        edgeWidthScale: 3.5,
        sizeMultiplier: 1.7,
        edgeOpacityMin: 0.28,
        dimOpacity: 0.04
    }
];
let currentFlowPreset = 0;

// Callable function for direct invocation (no proxy click needed)
function toggleFlowMode() {
    // If already in flow mode, cycle to next preset
    if (flowMode) {
        currentFlowPreset = (currentFlowPreset + 1) % FLOW_PRESETS.length;
        const preset = FLOW_PRESETS[currentFlowPreset];
        console.log(`[Flow] Cycling to preset: ${preset.name}`);
        applyFlowVisualization();
        showModeToast(`FLOW: ${preset.name}`);
        return;
    }

    flowMode = true;
    currentFlowPreset = 0;
    console.log('[Flow] Toggled to:', flowMode);

    // Sync BOTH potential buttons (Dock vs CommandBar)
    const btnDock = document.getElementById('btn-flow');
    if (btnDock) btnDock.classList.toggle('active', flowMode);

    const btnCmd = document.getElementById('cmd-flow2');
    if (btnCmd) btnCmd.classList.toggle('active', flowMode);

    // Show/hide flow legend
    const legend = document.getElementById('flow-legend');
    if (legend) legend.classList.toggle('visible', flowMode);

    // EXCLUSIVE MODE: Clear other visual noise
    clearAllFileModes();
    // Ensure standard file/hull buttons are off
    document.querySelectorAll('.file-mode-btn').forEach(b => b.classList.remove('active'));

    applyFlowVisualization();
    const preset = FLOW_PRESETS[currentFlowPreset];
    showModeToast(`FLOW: ${preset.name}`);
}

// Turn off flow mode completely
function disableFlowMode() {
    if (!flowMode) return;
    flowMode = false;
    currentFlowPreset = 0;

    const btnDock = document.getElementById('btn-flow');
    if (btnDock) btnDock.classList.remove('active');

    const btnCmd = document.getElementById('cmd-flow2');
    if (btnCmd) btnCmd.classList.remove('active');

    const legend = document.getElementById('flow-legend');
    if (legend) legend.classList.remove('visible');

    clearFlowVisualization();
    showModeToast('Flow mode off');
}

// NOTE: btn-flow onclick moved to setupControls() for proper DOM timing

function applyFlowVisualization() {
    // Guard: Ensure Graph is ready
    if (!Graph || !DM) {
        console.warn('[Flow] Graph or DM not ready');
        return;
    }

    // Get current preset settings
    const preset = FLOW_PRESETS[currentFlowPreset];
    const markov = DM ? DM.getMarkov() : {};  // ALL DATA FROM DM
    const highEntropy = markov.high_entropy_nodes || [];

    // Use preset values (fallback to FLOW_CONFIG for topK/minWeight if not in preset)
    const flowCfg = FLOW_CONFIG || {};
    const highlightColor = preset.highlightColor;
    const particleColor = preset.particleColor;
    const sizeMult = preset.sizeMultiplier;
    const edgeScale = preset.edgeWidthScale;
    const particleCount = preset.particleCount;
    const particleWidth = preset.particleWidth;
    const particleSpeed = preset.particleSpeed;
    const edgeOpacityMin = preset.edgeOpacityMin;
    const dimOpacity = preset.dimOpacity;
    const topK = flowCfg.topKEdges || 3;  // Show only top K outgoing edges per node
    const minWeight = flowCfg.minWeight || 0.01;

    // Build set of high entropy node names
    highEntropyNodes.clear();
    highEntropy.forEach(n => highEntropyNodes.add(n.node));

    const graphNodes = Graph.graphData().nodes;
    const graphLinks = Graph.graphData().links;

    // THRESHOLDING: Build a map of top-K outgoing edges per source node
    const edgesBySource = new Map();
    graphLinks.forEach(link => {
        const srcId = typeof link.source === 'object' ? link.source.id : link.source;
        if (!edgesBySource.has(srcId)) {
            edgesBySource.set(srcId, []);
        }
        edgesBySource.get(srcId).push(link);
    });

    // For each source, keep only top-K by markov_weight (transition probability)
    const visibleEdges = new Set();
    edgesBySource.forEach((edges, srcId) => {
        const sorted = edges
            .filter(e => (e.markov_weight || 0) >= minWeight)
            .sort((a, b) => (b.markov_weight || 0) - (a.markov_weight || 0))
            .slice(0, topK);
        sorted.forEach(e => visibleEdges.add(e));
    });

    // Store original colors and sizes, then apply flow coloring
    graphNodes.forEach(node => {
        if (!originalNodeColors.has(node.id)) {
            originalNodeColors.set(node.id, node.color);
        }
        // Restore original size first (in case switching presets)
        if (node._originalVal) {
            node.val = node._originalVal;
        } else {
            node._originalVal = node.val || 1;
        }
        // High entropy nodes highlighted (decision points)
        if (highEntropyNodes.has(node.name)) {
            node.color = highlightColor;
            node.val = node._originalVal * sizeMult;
        }
    });

    // Update link widths based on markov_weight (with amplification)
    const maxMarkov = Math.max(0.001, ...graphLinks.map(l => l.markov_weight || 0));

    Graph.linkWidth(link => {
        if (!visibleEdges.has(link)) return 0.1;  // Dim non-top edges
        const mw = link.markov_weight || 0;
        const normalized = mw / maxMarkov;
        const amplified = amplify(normalized);
        return 0.5 + amplified * edgeScale * 2;
    });

    // Update link opacity to emphasize important edges
    Graph.linkOpacity(link => {
        if (!visibleEdges.has(link)) return dimOpacity;
        const mw = link.markov_weight || 0;
        const normalized = mw / maxMarkov;
        const amplified = amplify(normalized);
        return edgeOpacityMin + amplified * (1.0 - edgeOpacityMin);
    });

    // Add directional particles only on visible edges
    Graph.linkDirectionalParticles(link => {
        if (!visibleEdges.has(link)) return 0;
        return particleCount;
    });
    Graph.linkDirectionalParticleWidth(particleWidth);
    Graph.linkDirectionalParticleSpeed(particleSpeed);
    Graph.linkDirectionalParticleColor(() => particleColor);

    // Update node coloring
    Graph.nodeColor(n => toColorNumber(n.color, '#888888'));

    updateSelectionVisuals();

    // Debug: count edges with markov weights
    const edgesWithMarkov = graphLinks.filter(l => l.markov_weight > 0).length;
    console.log(`[Flow] Preset: ${preset.name} | ${highEntropyNodes.size} high entropy nodes, ${visibleEdges.size} visible edges (top-${topK}), ${edgesWithMarkov}/${graphLinks.length} edges with markov`);
}

function clearFlowVisualization() {
    // Guard: Ensure Graph is ready
    if (!Graph) return;

    const graphNodes = Graph.graphData().nodes;

    // Restore original node colors and sizes
    graphNodes.forEach(node => {
        if (originalNodeColors.has(node.id)) {
            node.color = originalNodeColors.get(node.id);
        }
        // Restore original size from saved value
        if (node._originalVal) {
            node.val = node._originalVal;
            delete node._originalVal;
        }
    });

    // Reset link widths
    Graph.linkWidth(1);

    // Reset link opacity
    Graph.linkOpacity(0.6);

    // Remove directional particles
    Graph.linkDirectionalParticles(0);

    // Update coloring
    Graph.nodeColor(n => toColorNumber(n.color, '#888888'));

    highEntropyNodes.clear();
    applyEdgeMode();
    updateSelectionVisuals();
}

function setDatamap(prefix) {
    const nextSet = new Set(ACTIVE_DATAMAPS);
    if (!prefix) {
        nextSet.clear();
    } else if (nextSet.has(prefix)) {
        nextSet.delete(prefix);
    } else {
        nextSet.add(prefix);
    }

    if (!DM) {  // ALL DATA FROM DM
        ACTIVE_DATAMAPS = nextSet;
        updateDatamapControls();
        return;
    }

    const subset = filterGraph(null, CURRENT_DENSITY, nextSet, VIS_FILTERS);  // DM used internally
    if (!subset.nodes.length) {
        showToast('No nodes for that datamap selection.');
        updateDatamapControls();
        return;
    }

    ACTIVE_DATAMAPS = nextSet;
    updateDatamapControls();
    refreshGraph();
}

function setNodeColorMode(mode) {
    NODE_COLOR_MODE = mode;
    // Update legend to reflect current color mode
    if (typeof renderAllLegends === 'function') {
        renderAllLegends();
    }
    refreshGraph();
    // Refresh gradient edges to reflect new node colors
    if (typeof window.refreshGradientEdgeColors === 'function') {
        window.refreshGradientEdgeColors();
    }
}

function applyDatamap(prefix) {
    setDatamap(prefix);
}

// ====================================================================
// FILE BOUNDARIES & HOVER SYSTEM
// ====================================================================
// NOTE: fileBoundaryMeshes, fileMode, fileVizMode, etc. declared at top of file

function hashToUnit(value) {
    const str = String(value || '');
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash |= 0;
    }
    return (hash >>> 0) / 0xffffffff;
}

function getFileHue(fileIdx, totalFiles, fileName) {
    const strategy = FILE_COLOR_CONFIG.strategy || 'golden-angle';
    if (strategy === 'sequential') {
        const denom = Math.max(1, totalFiles);
        return (fileIdx / denom) * 360;
    }
    if (strategy === 'hash') {
        const seed = fileName || String(fileIdx);
        return hashToUnit(seed) * 360;
    }
    const angle = FILE_COLOR_CONFIG.angle ?? 137.5;
    return (fileIdx * angle) % 360;
}

function getFileColor(fileIdx, totalFiles, fileName, lightnessOverride = null) {
    const saturation = FILE_COLOR_CONFIG.saturation ?? 70;
    const lightness = (lightnessOverride !== null)
        ? lightnessOverride
        : (FILE_COLOR_CONFIG.lightness ?? 50);
    const hue = getFileHue(fileIdx, totalFiles, fileName);
    if (typeof FILE_COLOR_CONFIG.chroma === 'number') {
        return oklchColor(lightness, FILE_COLOR_CONFIG.chroma, hue);
    }
    const adjustedHue = hue + (COLOR_TWEAKS.hueShift || 0);
    const adjustedLightness = clampValue(lightness + (COLOR_TWEAKS.lightnessShift || 0), 0, 100);
    return `hsl(${adjustedHue}, ${saturation}%, ${adjustedLightness}%)`;
}

// Track last hovered node to avoid unnecessary re-renders
// (variable declared early at top of file to avoid TDZ)

function updateHoverPanel(node) {
    const hoverPanel = document.getElementById('hover-panel');
    if (!hoverPanel) return;

    if (!node) {
        // Mouse left node - hide panel after delay
        setTimeout(() => {
            if (_lastHoveredNodeId === null) {
                hoverPanel.classList.remove('visible');
            }
        }, 200);
        _lastHoveredNodeId = null;
        return;
    }

    // Only update if node changed (performance)
    const nodeId = node.id || node.name || '';
    if (nodeId === _lastHoveredNodeId) return;
    _lastHoveredNodeId = nodeId;

    // Update hover panel content with canonical taxonomy fields
    document.getElementById('hover-name').textContent = node.name || node.id || 'Unknown';
    document.getElementById('hover-kind').textContent = node.kind || node.symbol_kind || 'node';
    document.getElementById('hover-atom').textContent = node.atom || '--';
    document.getElementById('hover-family').textContent = getNodeAtomFamily(node);
    document.getElementById('hover-ring').textContent = getNodeRing(node);
    document.getElementById('hover-tier').textContent = getNodeTier(node);
    document.getElementById('hover-role').textContent = node.role || '--';

    // Show file path (truncated if long)
    const filePath = node.file_path || node.file || '';
    const shortPath = filePath.length > 50 ? '...' + filePath.slice(-47) : filePath;
    document.getElementById('hover-file').textContent = shortPath || '--';

    // Show panel and trigger smart placement
    hoverPanel.classList.add('visible');
    HudLayoutManager.reflow();
}

function buildDatasetKey(data) {
    const meta = (data && data.meta) ? data.meta : {};
    const target = meta.target || meta.project || 'dataset';
    const version = meta.version || '';
    const nodeCount = Array.isArray(data?.nodes) ? data.nodes.length : 0;
    const edgeCount = Array.isArray(data?.links)
        ? data.links.length
        : (Array.isArray(data?.edges) ? data.edges.length : 0);
    const raw = `${target}|${nodeCount}|${edgeCount}|${version}`;
    return raw.replace(/[^a-zA-Z0-9_.-]/g, '_').slice(0, 180);
}

function loadGroups() {
    GROUPS = [];
    try {
        const stored = localStorage.getItem(GROUPS_STORAGE_KEY);
        if (stored) {
            const parsed = JSON.parse(stored);
            if (Array.isArray(parsed)) {
                GROUPS = parsed;
            }
        }
    } catch (e) {
        // localStorage unavailable
    }
    GROUPS = GROUPS.filter(group => group && group.id && Array.isArray(group.node_ids));
    GROUPS.forEach(group => {
        if (group.visible === undefined) group.visible = true;
    });
}

function saveGroups() {
    try {
        localStorage.setItem(GROUPS_STORAGE_KEY, JSON.stringify(GROUPS));
    } catch (e) {
        // localStorage unavailable
    }
}

function getNextGroupColor() {
    const hue = (GROUPS.length * 137.5) % 360;
    return hslColor(hue, 65, 55);
}

function getGroupById(groupId) {
    return GROUPS.find(group => group.id === groupId) || null;
}

function getPrimaryGroupForNode(nodeId) {
    const visibleGroups = GROUPS.filter(group =>
        group.visible !== false && Array.isArray(group.node_ids) && group.node_ids.includes(nodeId)
    );
    if (!visibleGroups.length) return null;
    if (ACTIVE_GROUP_ID) {
        const active = visibleGroups.find(group => group.id === ACTIVE_GROUP_ID);
        if (active) return active;
    }
    return visibleGroups[0];
}

function renderGroupList() {
    const container = document.getElementById('group-list');
    if (!container) return;
    container.innerHTML = '';

    if (!GROUPS.length) {
        const empty = document.createElement('div');
        empty.style.fontSize = '9px';
        empty.style.color = 'rgba(255,255,255,0.4)';
        empty.textContent = 'No groups yet';
        container.appendChild(empty);
        return;
    }

    GROUPS.forEach(group => {
        const row = document.createElement('div');
        row.className = 'group-item';
        row.classList.toggle('active', group.id === ACTIVE_GROUP_ID);

        const dot = document.createElement('span');
        dot.className = 'group-color';
        dot.style.background = group.color || '#6fe8ff';

        const name = document.createElement('span');
        name.className = 'group-name';
        name.textContent = group.name || 'Group';

        const count = document.createElement('span');
        count.className = 'group-count';
        count.textContent = String((group.node_ids || []).length);

        const toggle = document.createElement('input');
        toggle.type = 'checkbox';
        toggle.className = 'group-toggle';
        toggle.checked = group.visible !== false;
        toggle.onchange = (e) => {
            e.stopPropagation();
            group.visible = toggle.checked;
            saveGroups();
            updateSelectionVisuals();
            renderGroupList();
        };

        row.onclick = (e) => {
            if (e.target === toggle) return;
            ACTIVE_GROUP_ID = group.id;
            renderGroupList();
            setSelection(group.node_ids || []);
            updateSelectionVisuals();
        };

        row.appendChild(dot);
        row.appendChild(name);
        row.appendChild(count);
        row.appendChild(toggle);
        container.appendChild(row);
    });
}

function updateGroupButtonState() {
    const btn = document.getElementById('btn-create-group');
    if (!btn) return;
    const hasSelection = SELECTED_NODE_IDS.size > 0;
    btn.classList.toggle('disabled', !hasSelection);
    btn.disabled = !hasSelection;
}

function createGroupFromSelection() {
    if (SELECTED_NODE_IDS.size === 0) return;
    const nodeIds = Array.from(SELECTED_NODE_IDS);
    const groupId = `group_${Date.now().toString(36)}`;
    const groupName = `Group ${GROUPS.length + 1}`;
    const groupColor = getNextGroupColor();
    GROUPS.push({
        id: groupId,
        name: groupName,
        color: groupColor,
        node_ids: nodeIds,
        visible: true
    });
    ACTIVE_GROUP_ID = groupId;
    saveGroups();
    renderGroupList();
    updateSelectionVisuals();
    showToast(`Created ${groupName} (${nodeIds.length})`);
}

function getSelectedNodes() {
    if (!Graph || !Graph.graphData) return [];
    const nodes = Graph.graphData().nodes || [];
    return nodes.filter(node => node && node.id && SELECTED_NODE_IDS.has(node.id));
}

function setSelection(ids, additive = false) {
    if (!additive) {
        SELECTED_NODE_IDS.clear();
    }
    (ids || []).forEach(id => {
        if (id) SELECTED_NODE_IDS.add(id);
    });
    updateSelectionPanel();
    updateSelectionVisuals();
    updateGroupButtonState();
}

function toggleSelection(node) {
    if (!node || !node.id) return;
    if (SELECTED_NODE_IDS.has(node.id)) {
        SELECTED_NODE_IDS.delete(node.id);
    } else {
        SELECTED_NODE_IDS.add(node.id);
    }
    updateSelectionPanel();
    updateSelectionVisuals();
    updateGroupButtonState();
}

function clearSelection() {
    SELECTED_NODE_IDS.clear();
    updateSelectionPanel();
    updateSelectionVisuals();
    updateGroupButtonState();
}

function maybeClearSelection() {
    const now = Date.now();
    if (MARQUEE_ACTIVE) return;
    if (now - LAST_MARQUEE_END_TS < 250) return;
    clearSelection();
}

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
            appendSelectionRow(item, 'Family', getNodeAtomFamily(node));
            appendSelectionRow(item, 'Ring', getNodeRing(node));
            appendSelectionRow(item, 'Tier', getNodeTier(node));
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

        const families = collectCounts(nodes, n => getNodeAtomFamily(n));
        const rings = collectCounts(nodes, n => getNodeRing(n));
        const tiers = collectCounts(nodes, n => getNodeTier(n));

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

    HudLayoutManager.reflow();
}

// ═══════════════════════════════════════════════════════════════════════
// SELECTION DETAIL MODAL: Consolidated view of selected nodes
// ═══════════════════════════════════════════════════════════════════════
function showSelectionModal() {
    const nodes = getSelectedNodes();
    if (!nodes.length) {
        showToast('No nodes selected');
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
    const levelCounts = {};

    nodes.forEach(node => {
        totalTokens += Number(node.tokens) || 0;
        totalBytes += Number(node.bytes) || 0;
        totalLoc += Number(node.loc || node.lines || node.lines_of_code) || 0;

        const tier = getNodeTier(node);
        const ring = getNodeRing(node);
        const family = getNodeAtomFamily(node);
        const level = node.level || node.scale_level || 'L3';

        tierCounts[tier] = (tierCounts[tier] || 0) + 1;
        ringCounts[ring] = (ringCounts[ring] || 0) + 1;
        familyCounts[family] = (familyCounts[family] || 0) + 1;
        levelCounts[level] = (levelCounts[level] || 0) + 1;
    });

    // Calculate max relevance for normalization
    const maxVal = Math.max(...nodes.map(n => n.val || n.size || 1));

    // Update title
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
        const tier = getNodeTier(node);
        const ring = getNodeRing(node);
        const family = getNodeAtomFamily(node);
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

    // Show modal
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

    // Click on selection panel title to open modal
    if (selectionTitle) {
        selectionTitle.style.cursor = 'pointer';
        selectionTitle.addEventListener('click', showSelectionModal);
    }

    // Keyboard shortcut: 'i' for info when nodes selected
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

function updateOverlayScale(node) {
    const base = Math.max(0.6, (node.val || 1) * (APPEARANCE_STATE.nodeScale || 1));
    const selectionScale = base * 2.5;  // BIGGER halo - was 1.9
    const groupScale = base * 1.8;      // Slightly bigger group halo
    if (node.__selectionHalo) {
        node.__selectionHalo.scale.set(selectionScale, selectionScale, selectionScale);
    }
    if (node.__groupHalo) {
        node.__groupHalo.scale.set(groupScale, groupScale, groupScale);
    }
}

function ensureNodeOverlays(node) {
    if (!node) return null;
    if (node.__overlayGroup) return node.__overlayGroup;

    const group = new THREE.Group();

    const selectionMaterial = new THREE.MeshBasicMaterial({
        color: 0x00ffff,      // BRIGHT CYAN - unmissable!
        transparent: true,
        opacity: 0.85,        // MUCH BRIGHTER - was 0.35
        depthWrite: false
    });
    const selectionHalo = new THREE.Mesh(SELECTION_HALO_GEOMETRY, selectionMaterial);
    selectionHalo.visible = false;
    selectionHalo.renderOrder = 3;

    const groupMaterial = new THREE.MeshBasicMaterial({
        color: 0xffffff,
        transparent: true,
        opacity: 0.45,        // BRIGHTER - was 0.18
        depthWrite: false
    });
    const groupHalo = new THREE.Mesh(GROUP_HALO_GEOMETRY, groupMaterial);
    groupHalo.visible = false;
    groupHalo.renderOrder = 2;

    group.add(selectionHalo);
    group.add(groupHalo);

    node.__selectionHalo = selectionHalo;
    node.__groupHalo = groupHalo;
    node.__overlayGroup = group;
    return group;
}

// Store original colors/sizes for selection restore
// (selectionOriginals declared early at top of file to avoid TDZ)
// SELECTION_SIZE_MULT moved to top
// PENDULUM moved to top

// Initialize from Config (if available)
// We call this immediately to load overrides from the graph data
if (typeof graph !== 'undefined' && graph.appearance && graph.appearance.animation) {
    const cfg = graph.appearance.animation;
    if (cfg.hue) Object.assign(PENDULUM.hue, cfg.hue);
    if (cfg.chroma) Object.assign(PENDULUM.chroma, cfg.chroma);
    if (cfg.lightness) Object.assign(PENDULUM.lightness, cfg.lightness);
    if (cfg.ripple) Object.assign(PENDULUM.ripple, cfg.ripple);
    console.log("Animation Config Loaded:", PENDULUM);
}

// Store original colors for dimming non-selected nodes
// NOTE: originalColorsForDim declared at top of file

// OKLCH to sRGB conversion (simplified, clamped)
function oklchToHex(L, C, H) {
    // Convert OKLCH to OKLab
    const hRad = H * Math.PI / 180;
    const a = C * Math.cos(hRad);
    const b = C * Math.sin(hRad);

    // OKLab to linear sRGB (approximate)
    const l_ = L / 100 + 0.3963377774 * a + 0.2158037573 * b;
    const m_ = L / 100 - 0.1055613458 * a - 0.0638541728 * b;
    const s_ = L / 100 - 0.0894841775 * a - 1.2914855480 * b;

    const l = l_ * l_ * l_;
    const m = m_ * m_ * m_;
    const s = s_ * s_ * s_;

    // Linear sRGB
    let rLin = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s;
    let gLin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
    let bLin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s;

    // Gamma correction & clamp
    const gamma = x => x <= 0 ? 0 : x >= 1 ? 1 : x < 0.0031308 ? 12.92 * x : 1.055 * Math.pow(x, 1 / 2.4) - 0.055;
    let rOut = Math.round(gamma(rLin) * 255);
    let gOut = Math.round(gamma(gLin) * 255);
    let bOut = Math.round(gamma(bLin) * 255);

    // Clamp to valid range
    rOut = Math.max(0, Math.min(255, rOut));
    gOut = Math.max(0, Math.min(255, gOut));
    bOut = Math.max(0, Math.min(255, bOut));

    return '#' + [rOut, gOut, bOut].map(x => x.toString(16).padStart(2, '0')).join('');
}

function updatePendulums(dt) {
    const p1 = PENDULUM.hue;
    const p2 = PENDULUM.chroma;

    // Pendulum 1: Modulates the SPEED of hue rotation (organic variation)
    const accel1 = -(p1.gravity / p1.length) * Math.sin(p1.angle);
    p1.velocity += accel1 * dt;
    p1.velocity *= p1.damping;
    p1.angle += p1.velocity * dt;

    // Hue rotates CONTINUOUSLY through full rainbow!
    // Pendulum modulates the speed for organic feel
    const speedMod = 1 + Math.sin(p1.angle) * 0.5;  // 0.5x to 1.5x speed
    PENDULUM.currentHue = (PENDULUM.currentHue + p1.rotationSpeed * speedMod * (dt / 16)) % 360;

    // Pendulum 2: Controls chroma with coupling to hue pendulum
    const coupling = 0.00015 * Math.sin(p1.angle);
    const accel2 = -(p2.gravity / p2.length) * Math.sin(p2.angle) + coupling;
    p2.velocity += accel2 * dt;
    p2.velocity *= p2.damping;
    p2.angle += p2.velocity * dt;

    // Update lightness phase (pulsing brightness)
    PENDULUM.lightness.phase += PENDULUM.lightness.speed * dt;
}

// Get selection color with optional spatial phase offset
// Brightness reduced 17% from original (center 62 instead of 75)
// Get selection color with optional spatial phase offset
// Dynamic brightness/chroma based on PENDULUM config
function getSelectionColor(phaseOffset = 0) {
    const p2 = PENDULUM.chroma;
    const p3 = PENDULUM.lightness;

    // Full rainbow hue (continuous rotation) + Ripple offset (45 degrees spread)
    const H = (PENDULUM.currentHue + phaseOffset * 45) % 360;

    // Chroma with gentle spatial variation (Ripple)
    const C = Math.max(0.18, p2.center + Math.sin(p2.angle + phaseOffset * Math.PI * 2) * p2.amplitude);

    // Bright lightness with Ripple pulse
    const L = p3.center + Math.sin(p3.phase + phaseOffset * Math.PI * 4) * p3.amplitude;

    return oklchToHex(L, C, H);
}

// Calculate spatial phase for RIPPLE EFFECT based on distance from center
function getNodeSpatialPhase(node) {
    const x = node.x || 0;
    const y = node.y || 0;
    const z = node.z || 0;

    // Calculate distance from origin (radial ripple)
    const distance = Math.sqrt(x * x + y * y + z * z);

    // Normalize distance to create concentric ripples
    // Ripples expand outward from center
    const scale = PENDULUM.ripple ? (PENDULUM.ripple.scale || 200) : 200;
    const ripplePhase = (distance / scale) % 1;

    // Add subtle angular variation for more organic feel
    const angle = Math.atan2(y, x);
    const angularOffset = Math.sin(angle * 3) * 0.1;  // Subtle angular modulation

    return (ripplePhase + angularOffset + 1) % 1;
}

// Dim a color by reducing its lightness (for non-selected nodes)
function dimColor(hexColor, factor = 0.33) {
    // Simple approach: reduce RGB values
    const hex = hexColor.replace('#', '');
    const r = Math.round(parseInt(hex.substr(0, 2), 16) * (1 - factor));
    const g = Math.round(parseInt(hex.substr(2, 2), 16) * (1 - factor));
    const b = Math.round(parseInt(hex.substr(4, 2), 16) * (1 - factor));
    return '#' + [r, g, b].map(x => Math.max(0, Math.min(255, x)).toString(16).padStart(2, '0')).join('');
}

function animateSelectionColors(timestamp) {
    if (!PENDULUM.running) return;

    const dt = PENDULUM.lastTime ? Math.min(timestamp - PENDULUM.lastTime, 50) : 16;
    PENDULUM.lastTime = timestamp;

    // Update physics
    updatePendulums(dt);

    // Apply color to selected nodes with SPATIAL VARIATION
    // Each node gets a different phase based on its position
    if (SELECTED_NODE_IDS.size > 0 && Graph && Graph.graphData) {
        const nodes = Graph.graphData().nodes || [];

        nodes.forEach(node => {
            if (SELECTED_NODE_IDS.has(node.id)) {
                // SELECTED: Rainbow color with spatial phase offset
                // Different regions of the selection pulse at different phases
                const spatialPhase = getNodeSpatialPhase(node);
                node.color = getSelectionColor(spatialPhase);
            }
            // Non-selected nodes stay dimmed (set in updateSelectionVisuals)
        });

        Graph.nodeColor(n => toColorNumber(n.color, 0x888888));
    }

    requestAnimationFrame(animateSelectionColors);
}

function startSelectionAnimation() {
    if (!PENDULUM.running) {
        PENDULUM.running = true;
        // Give pendulums initial push
        PENDULUM.hue.velocity = 0.02 + Math.random() * 0.01;
        PENDULUM.chroma.velocity = 0.015 + Math.random() * 0.01;
        PENDULUM.lastTime = 0;
        requestAnimationFrame(animateSelectionColors);
    }
}

function stopSelectionAnimation() {
    PENDULUM.running = false;
}

function updateSelectionVisuals() {
    if (!Graph || !Graph.graphData) return;
    const nodes = Graph.graphData().nodes || [];
    const hasSelection = SELECTED_NODE_IDS.size > 0;

    nodes.forEach(node => {
        const isSelected = SELECTED_NODE_IDS.has(node.id);

        // Save original color/size for ALL nodes when selection starts
        if (hasSelection && !originalColorsForDim.has(node.id)) {
            originalColorsForDim.set(node.id, {
                color: node.color,
                val: node.val || 1
            });
        }

        // Also track selected nodes separately for size restore
        if (isSelected && !selectionOriginals.has(node.id)) {
            selectionOriginals.set(node.id, {
                color: node.color,
                val: node.val || 1
            });
        }

        // Apply styling based on selection state
        if (hasSelection) {
            if (isSelected) {
                // SELECTED: Make bigger, color will be animated
                const orig = selectionOriginals.get(node.id);
                node.val = (orig?.val || 1) * SELECTION_SIZE_MULT;
            } else {
                // NOT SELECTED: Dim by 33%
                const orig = originalColorsForDim.get(node.id);
                if (orig) {
                    node.color = dimColor(orig.color, 0.33);
                }
            }
        } else {
            // NO SELECTION: Restore all original colors and sizes
            if (originalColorsForDim.has(node.id)) {
                const orig = originalColorsForDim.get(node.id);
                node.color = orig.color;
                node.val = orig.val;
            }
            if (selectionOriginals.has(node.id)) {
                const orig = selectionOriginals.get(node.id);
                node.color = orig.color;
                node.val = orig.val;
                selectionOriginals.delete(node.id);
            }
        }

        // Also update overlays (halos)
        ensureNodeOverlays(node);
        updateOverlayScale(node);
        if (node.__selectionHalo) {
            node.__selectionHalo.visible = isSelected;
        }
        if (node.__groupHalo) {
            const group = getPrimaryGroupForNode(node.id);
            if (group) {
                node.__groupHalo.visible = group.visible !== false;
                node.__groupHalo.material.color.set(group.color || '#88d0ff');
                node.__groupHalo.material.opacity =
                    (group.id === ACTIVE_GROUP_ID) ? 0.7 : 0.45;
            } else {
                node.__groupHalo.visible = false;
            }
        }
    });

    // Clear dim cache when no selection
    if (!hasSelection) {
        originalColorsForDim.clear();
    }

    // Start/stop animation based on selection state
    if (hasSelection) {
        startSelectionAnimation();
    } else {
        stopSelectionAnimation();
    }

    // Force re-render with new colors
    Graph.nodeColor(n => toColorNumber(n.color, 0x888888));
}

function syncSelectionAfterGraphUpdate() {
    if (!Graph || !Graph.graphData) return;
    const visibleIds = new Set((Graph.graphData().nodes || []).map(n => n.id));
    let changed = false;
    Array.from(SELECTED_NODE_IDS).forEach(id => {
        if (!visibleIds.has(id)) {
            SELECTED_NODE_IDS.delete(id);
            changed = true;
        }
    });
    if (changed) {
        updateSelectionPanel();
    }
    updateSelectionVisuals();
    updateGroupButtonState();
}

function updateSelectionBox(rect) {
    if (!SELECTION_BOX) return;
    SELECTION_BOX.style.display = 'block';
    SELECTION_BOX.style.left = `${rect.left}px`;
    SELECTION_BOX.style.top = `${rect.top}px`;
    SELECTION_BOX.style.width = `${rect.width}px`;
    SELECTION_BOX.style.height = `${rect.height}px`;
}

function getBoxRect(start, end) {
    const left = Math.min(start.x, end.x);
    const top = Math.min(start.y, end.y);
    const width = Math.abs(start.x - end.x);
    const height = Math.abs(start.y - end.y);
    return {
        left,
        top,
        width,
        height,
        right: left + width,
        bottom: top + height
    };
}

function getNodeScreenPosition(node) {
    if (!Graph || !Graph.camera || !node) return null;
    if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return null;
    const camera = Graph.camera();
    const vector = new THREE.Vector3(node.x, node.y, node.z || 0);
    vector.project(camera);
    const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
    const y = (-vector.y * 0.5 + 0.5) * window.innerHeight;
    return { x, y };
}

function selectNodesInBox(rect, additive = true) {
    if (!Graph || !Graph.graphData) return;
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
        setSelection(selected, additive);
    }
}

function setupSelectionInteractions() {
    const clearBtn = document.getElementById('selection-clear');
    if (clearBtn) {
        clearBtn.onclick = () => clearSelection();
    }

    const groupBtn = document.getElementById('btn-create-group');
    if (groupBtn) {
        groupBtn.onclick = () => createGroupFromSelection();
    }

    SELECTION_BOX = document.getElementById('selection-box');
    if (!Graph || !Graph.renderer || !SELECTION_BOX) return;

    const canvas = Graph.renderer().domElement;
    if (!canvas) return;

    const onPointerDown = (e) => {
        // Left-drag = marquee selection (space+drag reserved for pan)
        if (e.button !== 0) return;
        if (SPACE_PRESSED) return;
        if (e.target !== canvas) return;
        if (HOVERED_NODE) return;
        MARQUEE_ACTIVE = true;
        MARQUEE_ADDITIVE = !!e.shiftKey;
        MARQUEE_START = { x: e.clientX, y: e.clientY };
        updateSelectionBox(getBoxRect(MARQUEE_START, MARQUEE_START));
        if (Graph.controls()) {
            Graph.controls().enabled = false;
        }
        e.preventDefault();
    };

    const onPointerMove = (e) => {
        if (!MARQUEE_ACTIVE || !MARQUEE_START) return;
        updateSelectionBox(getBoxRect(MARQUEE_START, { x: e.clientX, y: e.clientY }));
    };

    const finishSelection = (e) => {
        if (!MARQUEE_ACTIVE || !MARQUEE_START) return;
        const rect = getBoxRect(MARQUEE_START, { x: e.clientX, y: e.clientY });
        SELECTION_BOX.style.display = 'none';
        const additive = MARQUEE_ADDITIVE;
        MARQUEE_ACTIVE = false;
        MARQUEE_START = null;
        MARQUEE_ADDITIVE = false;
        if (Graph.controls()) {
            Graph.controls().enabled = true;
        }
        const didDrag = rect.width > 4 && rect.height > 4;
        if (didDrag) {
            LAST_MARQUEE_END_TS = Date.now();
            selectNodesInBox(rect, additive);
        }
    };

    canvas.addEventListener('pointerdown', onPointerDown, { passive: false });
    canvas.addEventListener('pointermove', onPointerMove, { passive: true });
    canvas.addEventListener('pointerup', finishSelection, { passive: true });
    canvas.addEventListener('pointerleave', finishSelection, { passive: true });
}

function initSelectionState(data) {
    DATASET_KEY = buildDatasetKey(data);
    GROUPS_STORAGE_KEY = `collider_groups_${DATASET_KEY}`;
    loadGroups();
    renderGroupList();
    updateSelectionPanel();
    updateGroupButtonState();
}

function handleNodeHover(node, data) {
    const filePanel = document.getElementById('file-panel');
    HOVERED_NODE = node || null;

    // Always update hover panel (separate from file panel)
    updateHoverPanel(node);

    if (!VIS_FILTERS.metadata.showFilePanel) {
        filePanel.classList.remove('visible');
        return;
    }

    if (!node) {
        // Mouse left node - hide panel after delay
        setTimeout(() => {
            if (!fileMode) filePanel.classList.remove('visible');
        }, 300);
        return;
    }

    // Get file info from boundaries
    const boundaries = data.file_boundaries || [];
    const fileIdx = node.fileIdx;

    if (fileIdx < 0 || fileIdx >= boundaries.length) {
        return;
    }

    const fileInfo = boundaries[fileIdx];

    // Update panel content
    document.getElementById('file-name').textContent = fileInfo.file_name || 'unknown';
    document.getElementById('file-cohesion').textContent =
        `Cohesion: ${(fileInfo.cohesion * 100).toFixed(0)}%`;
    document.getElementById('file-purpose').textContent = fileInfo.purpose || '--';
    document.getElementById('file-atom-count').textContent = fileInfo.atom_count || 0;
    document.getElementById('file-lines').textContent =
        fileInfo.line_range ? `${fileInfo.line_range[0]}-${fileInfo.line_range[1]}` : '--';
    document.getElementById('file-classes').textContent =
        (fileInfo.classes || []).join(', ') || 'none';
    document.getElementById('file-functions').textContent =
        'Functions: ' + ((fileInfo.functions || []).slice(0, 8).join(', ') || 'none');

    // Show code preview from node body
    const code = node.body || '// no source available';
    document.getElementById('file-code').textContent = code;

    // Show panel and trigger smart placement
    filePanel.classList.add('visible');
    HudLayoutManager.reflow();
}

function handleNodeClick(node, event) {
    if (!node) return;
    const additive = event && event.shiftKey;
    if (additive) {
        toggleSelection(node);
        return;
    }
    if (node.id) {
        setSelection([node.id]);
    }
    if ((GRAPH_MODE === 'files' || GRAPH_MODE === 'hybrid') && node.isFileNode) {
        toggleFileExpand(node.fileIdx);
    }
}

function toggleFileExpand(fileIdx) {
    if (!Number.isFinite(fileIdx)) return;
    captureFileNodePositions();
    const fileInfo = DM ? DM.getFile(fileIdx) : {};  // ALL DATA FROM DM
    const fileLabel = fileInfo?.file_name || fileInfo?.file || `file-${fileIdx}`;
    if (EXPANDED_FILES.has(fileIdx)) {
        EXPANDED_FILES.delete(fileIdx);
        showToast(`Collapsed ${fileLabel}`);
    } else {
        EXPANDED_FILES.clear();
        EXPANDED_FILES.add(fileIdx);
        showToast(`Expanded ${fileLabel}`);
    }
    GRAPH_MODE = (EXPANDED_FILES.size > 0) ? 'hybrid' : 'files';
    refreshGraph();
}

function sampleFileNodes(nodes, maxPoints) {
    if (nodes.length <= maxPoints) return nodes;
    const step = Math.ceil(nodes.length / maxPoints);
    return nodes.filter((_, idx) => idx % step === 0);
}

function buildHull2D(points) {
    if (points.length < 3) return null;
    const unique = new Map();
    points.forEach(p => {
        const key = `${p.x.toFixed(4)},${p.y.toFixed(4)}`;
        if (!unique.has(key)) unique.set(key, p);
    });
    const pts = Array.from(unique.values()).sort((a, b) => {
        if (a.x === b.x) return a.y - b.y;
        return a.x - b.x;
    });
    if (pts.length < 3) return null;
    const cross = (o, a, b) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
    const lower = [];
    for (const p of pts) {
        while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {
            lower.pop();
        }
        lower.push(p);
    }
    const upper = [];
    for (let i = pts.length - 1; i >= 0; i--) {
        const p = pts[i];
        while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {
            upper.pop();
        }
        upper.push(p);
    }
    upper.pop();
    lower.pop();
    return lower.concat(upper);
}

function computeCentroid(points) {
    const centroid = new THREE.Vector3();
    points.forEach(p => centroid.add(p));
    return centroid.divideScalar(Math.max(1, points.length));
}

function quantile(values, q) {
    if (!values.length) return 0;
    const sorted = values.slice().sort((a, b) => a - b);
    const pos = (sorted.length - 1) * q;
    const base = Math.floor(pos);
    const rest = pos - base;
    if (sorted[base + 1] !== undefined) {
        return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
    }
    return sorted[base];
}

function drawFileBoundaries(data) {
    // ALL DATA FROM DM - the rendering pipeline
    let drawn = 0;
    const boundaryConfig = data?.appearance?.boundary || {};
    const fillOpacity =
        (typeof APPEARANCE_STATE.boundaryFill === 'number')
            ? APPEARANCE_STATE.boundaryFill
            : (boundaryConfig.fill_opacity || 0.08);
    const wireOpacity =
        (typeof APPEARANCE_STATE.boundaryWire === 'number')
            ? APPEARANCE_STATE.boundaryWire
            : (boundaryConfig.wire_opacity || 0.3);
    const padding = boundaryConfig.padding || 1.2;
    const minExtent = boundaryConfig.min_extent || 6;
    const quantileRange = boundaryConfig.quantile || 0.9;
    const lowQ = Math.max(0, (1 - quantileRange) / 2);
    const highQ = Math.min(1, 1 - lowQ);
    const boundaryPhysics = data?.physics?.boundary || {};
    const hullType = String(boundaryPhysics.hullType || 'convex').toLowerCase();
    const fileBoundaries = DM ? DM.getFileBoundaries() : (data?.file_boundaries || []);
    const totalFiles = fileBoundaries.length;

    const graphNodes = DM ? DM.getVisibleNodes() : (Graph?.graphData()?.nodes || []);
    const scene = Graph.scene();

    // Clear existing boundary meshes
    fileBoundaryMeshes.forEach(mesh => scene.remove(mesh));
    fileBoundaryMeshes = [];

    if (!fileMode) return drawn;

    // Group nodes by file (only use nodes with stable positions)
    const fileGroups = {};
    const validNodes = graphNodes.filter(node => {
        if (!node) return false;
        if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return false;
        if (IS_3D && !Number.isFinite(node.z)) return false;
        return true;
    });

    if (!validNodes.length) return drawn;

    validNodes.forEach(node => {
        const idx = node.fileIdx;
        if (idx >= 0) {
            if (!fileGroups[idx]) fileGroups[idx] = [];
            fileGroups[idx].push(node);
        }
    });

    // Draw boundary for each file group
    Object.entries(fileGroups).forEach(([fileIdx, nodes]) => {
        const sampled = sampleFileNodes(nodes, 180);
        const xs = sampled.map(n => n.x || 0);
        const ys = sampled.map(n => n.y || 0);
        const zs = sampled.map(n => n.z || 0);

        const minX = quantile(xs, lowQ);
        const maxX = quantile(xs, highQ);
        const minY = quantile(ys, lowQ);
        const maxY = quantile(ys, highQ);
        const minZ = quantile(zs, lowQ);
        const maxZ = quantile(zs, highQ);

        const filtered = sampled.filter(n => {
            const x = n.x || 0;
            const y = n.y || 0;
            const z = n.z || 0;
            return x >= minX && x <= maxX && y >= minY && y <= maxY && z >= minZ && z <= maxZ;
        });
        const hullNodes = filtered.length >= 3 ? filtered : sampled;
        const positions = hullNodes.map(n => new THREE.Vector3(n.x || 0, n.y || 0, n.z || 0));
        const centroid = computeCentroid(positions);
        const zRange = maxZ - minZ;
        const extentX = Math.max(0.001, maxX - minX);
        const extentY = Math.max(0.001, maxY - minY);
        const extentZ = Math.max(0.001, maxZ - minZ);
        const scaleFixX = Math.max(1, minExtent / extentX);
        const scaleFixY = Math.max(1, minExtent / extentY);
        const scaleFixZ = IS_3D ? Math.max(1, minExtent / extentZ) : 1;
        const scaleX = padding * scaleFixX;
        const scaleY = padding * scaleFixY;
        const scaleZ = padding * scaleFixZ;
        const sizeX = extentX * scaleX;
        const sizeY = extentY * scaleY;
        const sizeZ = extentZ * scaleZ;

        const fileIndex = Number.parseInt(fileIdx, 10);
        const safeFileIdx = Number.isFinite(fileIndex) ? fileIndex : 0;
        const fileInfo = (data.file_boundaries || [])[safeFileIdx] || {};
        const fileLabel = fileInfo.file || fileInfo.file_name || fileIdx;
        const color = new THREE.Color(
            getFileColor(safeFileIdx, totalFiles, fileLabel)
        );

        let mesh = null;
        let wireMesh = null;

        if (nodes.length < 3) {
            const rawPositions = nodes.map(n => new THREE.Vector3(n.x || 0, n.y || 0, n.z || 0));
            const smallCentroid = computeCentroid(rawPositions);
            const maxRadius = rawPositions.reduce((acc, p) => {
                return Math.max(acc, p.distanceTo(smallCentroid));
            }, 0);
            const bubbleRadius = Math.max(minExtent * 0.5, maxRadius + minExtent * 0.35);
            const material = new THREE.MeshBasicMaterial({
                color: color,
                transparent: true,
                opacity: fillOpacity,
                wireframe: false,
                side: THREE.DoubleSide
            });
            if (IS_3D) {
                const geometry = new THREE.SphereGeometry(bubbleRadius, 14, 10);
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.copy(smallCentroid);
                const wireMaterial = new THREE.LineBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: wireOpacity
                });
                const edges = new THREE.EdgesGeometry(geometry);
                wireMesh = new THREE.LineSegments(edges, wireMaterial);
                wireMesh.position.copy(mesh.position);
            } else {
                const geometry = new THREE.CircleGeometry(bubbleRadius, 32);
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(smallCentroid.x, smallCentroid.y, smallCentroid.z);
                const wireMaterial = new THREE.LineBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: wireOpacity
                });
                const edges = new THREE.EdgesGeometry(geometry);
                wireMesh = new THREE.LineSegments(edges, wireMaterial);
                wireMesh.position.copy(mesh.position);
            }
        }

        if (!mesh && hullType === 'convex') {
            if (IS_3D && zRange > 0.001 && positions.length >= 4) {
                const ConvexCtor =
                    (typeof ConvexGeometry !== 'undefined')
                        ? ConvexGeometry
                        : (THREE.ConvexGeometry || null);
                const relPoints = positions.map(p => p.clone().sub(centroid));
                let boundaryGeometry = null;
                if (ConvexCtor) {
                    try {
                        boundaryGeometry = new ConvexCtor(relPoints);
                    } catch (err) {
                        boundaryGeometry = null;
                    }
                }
                if (boundaryGeometry) {
                    const material = new THREE.MeshBasicMaterial({
                        color: color,
                        transparent: true,
                        opacity: fillOpacity,
                        wireframe: false,
                        side: THREE.DoubleSide
                    });
                    mesh = new THREE.Mesh(boundaryGeometry, material);
                    mesh.position.copy(centroid);
                    mesh.scale.set(scaleX, scaleY, scaleZ);

                    const wireMaterial = new THREE.LineBasicMaterial({
                        color: color,
                        transparent: true,
                        opacity: wireOpacity
                    });
                    const edges = new THREE.EdgesGeometry(boundaryGeometry);
                    wireMesh = new THREE.LineSegments(edges, wireMaterial);
                    wireMesh.position.copy(centroid);
                    wireMesh.scale.copy(mesh.scale);
                }
            }

            if (!mesh) {
                const hull2d = buildHull2D(positions.map(p => new THREE.Vector2(p.x, p.y)));
                if (!hull2d || hull2d.length < 3) return;
                const localHull = hull2d.map(p => new THREE.Vector2(p.x - centroid.x, p.y - centroid.y));
                const shape = new THREE.Shape(localHull);
                const boundaryGeometry = new THREE.ShapeGeometry(shape);
                const material = new THREE.MeshBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: fillOpacity,
                    wireframe: false,
                    side: THREE.DoubleSide
                });
                mesh = new THREE.Mesh(boundaryGeometry, material);
                mesh.position.set(centroid.x, centroid.y, centroid.z);
                mesh.scale.set(scaleX, scaleY, 1);

                const wireMaterial = new THREE.LineBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: wireOpacity
                });
                const wireGeometry = new THREE.BufferGeometry().setFromPoints(
                    localHull.map(p => new THREE.Vector3(p.x, p.y, 0))
                );
                wireMesh = new THREE.LineLoop(wireGeometry, wireMaterial);
                wireMesh.position.copy(mesh.position);
                wireMesh.scale.copy(mesh.scale);
            }
        } else if (!mesh && hullType === 'box') {
            const material = new THREE.MeshBasicMaterial({
                color: color,
                transparent: true,
                opacity: fillOpacity,
                wireframe: false,
                side: THREE.DoubleSide
            });
            if (IS_3D) {
                const geometry = new THREE.BoxGeometry(sizeX, sizeY, sizeZ);
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.copy(centroid);
                const wireMaterial = new THREE.LineBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: wireOpacity
                });
                const edges = new THREE.EdgesGeometry(geometry);
                wireMesh = new THREE.LineSegments(edges, wireMaterial);
                wireMesh.position.copy(mesh.position);
            } else {
                const geometry = new THREE.PlaneGeometry(sizeX, sizeY);
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(centroid.x, centroid.y, centroid.z);
                const wireMaterial = new THREE.LineBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: wireOpacity
                });
                const edges = new THREE.EdgesGeometry(geometry);
                wireMesh = new THREE.LineSegments(edges, wireMaterial);
                wireMesh.position.copy(mesh.position);
            }
        } else if (!mesh) {
            const radius = 0.5 * Math.max(sizeX, sizeY, IS_3D ? sizeZ : 0);
            const material = new THREE.MeshBasicMaterial({
                color: color,
                transparent: true,
                opacity: fillOpacity,
                wireframe: false,
                side: THREE.DoubleSide
            });
            if (IS_3D) {
                const geometry = new THREE.SphereGeometry(radius, 18, 14);
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.copy(centroid);
                const wireMaterial = new THREE.LineBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: wireOpacity
                });
                const edges = new THREE.EdgesGeometry(geometry);
                wireMesh = new THREE.LineSegments(edges, wireMaterial);
                wireMesh.position.copy(mesh.position);
            } else {
                const geometry = new THREE.CircleGeometry(radius, 40);
                mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(centroid.x, centroid.y, centroid.z);
                const wireMaterial = new THREE.LineBasicMaterial({
                    color: color,
                    transparent: true,
                    opacity: wireOpacity
                });
                const edges = new THREE.EdgesGeometry(geometry);
                wireMesh = new THREE.LineSegments(edges, wireMaterial);
                wireMesh.position.copy(mesh.position);
            }
        }

        if (!mesh) return;
        scene.add(mesh);
        fileBoundaryMeshes.push(mesh);
        drawn += 1;
        if (wireMesh) {
            scene.add(wireMesh);
            fileBoundaryMeshes.push(wireMesh);
        }
    });
    return drawn;
}

// ═══════════════════════════════════════════════════════════════════════
// FILE CONTAINMENT SYSTEM - Spherical fields with particle physics
// "Metaphysical force from another dimension" - holding particles together
// ═══════════════════════════════════════════════════════════════════════

const FILE_CONTAINMENT = {
    spheres: [],              // Three.js sphere meshes
    directoryTree: null,      // Parsed directory hierarchy
    particleActivity: {},    // FileIdx → activity level (0-1)
    boundariesPopped: false,  // Animation state
    popProgress: 0,           // 0 = contained, 1 = fully free
    slowMotionFactor: 0.15,   // Time multiplier for dreamy slow motion
    collisionEnabled: true,   // Enable soft collisions
    spatialGrid: null,        // For efficient collision detection
    gridCellSize: 20,         // Size of spatial hash cells
    animationFrame: null,
    isAnimating: false
};

// ═══════════════════════════════════════════════════════════════════════
// SPATIAL HASHING - O(n) collision detection instead of O(n²)
// ═══════════════════════════════════════════════════════════════════════

function buildSpatialGrid(nodes, cellSize) {
    const grid = new Map();

    nodes.forEach(node => {
        if (!node || !Number.isFinite(node.x)) return;
        const cellX = Math.floor(node.x / cellSize);
        const cellY = Math.floor(node.y / cellSize);
        const cellZ = IS_3D ? Math.floor((node.z || 0) / cellSize) : 0;
        const key = `${cellX},${cellY},${cellZ}`;

        if (!grid.has(key)) grid.set(key, []);
        grid.get(key).push(node);
    });

    FILE_CONTAINMENT.spatialGrid = grid;
    return grid;
}

function getNeighborCells(cellX, cellY, cellZ) {
    const neighbors = [];
    for (let dx = -1; dx <= 1; dx++) {
        for (let dy = -1; dy <= 1; dy++) {
            for (let dz = IS_3D ? -1 : 0; dz <= (IS_3D ? 1 : 0); dz++) {
                neighbors.push(`${cellX + dx},${cellY + dy},${cellZ + dz}`);
            }
        }
    }
    return neighbors;
}

// Soft collision - push particles apart smoothly
function applySoftCollisions(nodes, cellSize, repulsionStrength = 0.5) {
    if (!FILE_CONTAINMENT.collisionEnabled) return;

    const grid = buildSpatialGrid(nodes, cellSize);
    const minDist = 8;  // Minimum distance between particles
    const minDistSq = minDist * minDist;

    nodes.forEach(node => {
        if (!node || !Number.isFinite(node.x)) return;
        if (!node.__physics) {
            node.__physics = { vx: 0, vy: 0, vz: 0 };
        }

        const cellX = Math.floor(node.x / cellSize);
        const cellY = Math.floor(node.y / cellSize);
        const cellZ = IS_3D ? Math.floor((node.z || 0) / cellSize) : 0;
        const neighborKeys = getNeighborCells(cellX, cellY, cellZ);

        neighborKeys.forEach(key => {
            const cellNodes = grid.get(key);
            if (!cellNodes) return;

            cellNodes.forEach(other => {
                if (other === node) return;

                const dx = node.x - other.x;
                const dy = node.y - other.y;
                const dz = IS_3D ? ((node.z || 0) - (other.z || 0)) : 0;
                const distSq = dx * dx + dy * dy + dz * dz;

                if (distSq < minDistSq && distSq > 0.001) {
                    const dist = Math.sqrt(distSq);
                    const overlap = minDist - dist;
                    const force = (overlap / minDist) * repulsionStrength;

                    // Push apart
                    const nx = dx / dist;
                    const ny = dy / dist;
                    const nz = IS_3D ? dz / dist : 0;

                    node.__physics.vx += nx * force;
                    node.__physics.vy += ny * force;
                    if (IS_3D) node.__physics.vz += nz * force;
                }
            });
        });
    });
}

// Build directory tree from file paths
function buildDirectoryTree(fileBoundaries) {
    const tree = { name: '/', path: '', depth: 0, children: {}, files: [], totalNodes: 0 };

    fileBoundaries.forEach((file, idx) => {
        const filePath = file.file || file.file_name || '';
        const parts = filePath.split('/').filter(p => p);
        let current = tree;

        parts.forEach((part, partIdx) => {
            const isFile = partIdx === parts.length - 1;
            if (isFile) {
                current.files.push({
                    name: part, path: filePath, fileIdx: idx,
                    nodeCount: (file.atom_ids || []).length, activity: 0
                });
            } else {
                if (!current.children[part]) {
                    current.children[part] = {
                        name: part, path: parts.slice(0, partIdx + 1).join('/'),
                        depth: partIdx + 1, children: {}, files: [], totalNodes: 0
                    };
                }
                current = current.children[part];
            }
        });
    });

    FILE_CONTAINMENT.directoryTree = tree;
    return tree;
}

// Compute activity levels from markov transitions
function computeFileActivity(data) {
    const markov = data.markov || {};
    const highEntropy = markov.high_entropy_nodes || [];
    const transitions = markov.transitions || {};
    const fileActivity = {};

    (data.file_boundaries || []).forEach((file, idx) => {
        const atomIds = file.atom_ids || [];
        let activity = 0;
        atomIds.forEach(atomId => {
            if (highEntropy.some(h => h.node === atomId)) activity += 0.3;
            const fanout = Object.keys(transitions[atomId] || {}).length;
            activity += Math.min(fanout / 10, 0.5);
        });
        fileActivity[idx] = Math.min(1, activity / Math.max(1, atomIds.length));
    });

    FILE_CONTAINMENT.particleActivity = fileActivity;
    return fileActivity;
}

// Draw containment spheres
// Draw containment hulls (Optimized for performance and aesthetics)
function drawContainmentSpheres(data) {
    const scene = Graph.scene();
    if (!scene) return;
    const graphNodes = DM ? DM.getVisibleNodes() : (Graph?.graphData()?.nodes || []);

    // Clear existing
    FILE_CONTAINMENT.spheres.forEach(s => {
        if (s.mesh) scene.remove(s.mesh);
        if (s.wireframe) scene.remove(s.wireframe);
        if (s.glow) scene.remove(s.glow);
    });
    FILE_CONTAINMENT.spheres = [];

    // ONLY DRAW IF: 
    // 1. File Mode is ON
    // 2. We are NOT in Flow Mode (Flow is exclusive)
    // 3. Hulls button is active (explicit user choice)
    const hullsActive = document.getElementById('btn-file-hulls')?.classList.contains('active');

    if (!fileMode || flowMode || !hullsActive || FILE_CONTAINMENT.boundariesPopped) return;

    const fileBoundaries = DM ? DM.getFileBoundaries() : (data?.file_boundaries || []);

    // Group nodes by file
    const fileGroups = {};
    graphNodes.filter(n => n && Number.isFinite(n.x)).forEach(node => {
        if (node.fileIdx >= 0) {
            if (!fileGroups[node.fileIdx]) fileGroups[node.fileIdx] = [];
            fileGroups[node.fileIdx].push(node);
        }
    });

    Object.entries(fileGroups).forEach(([fileIdx, nodes]) => {
        if (nodes.length < 3) return; // Cull singletons/pairs

        // Calculate Bounding Box
        let minX = Infinity, maxX = -Infinity;
        let minY = Infinity, maxY = -Infinity;
        let minZ = Infinity, maxZ = -Infinity;

        nodes.forEach(n => {
            minX = Math.min(minX, n.x); maxX = Math.max(maxX, n.x);
            minY = Math.min(minY, n.y); maxY = Math.max(maxY, n.y);
            minZ = Math.min(minZ, n.z || 0); maxZ = Math.max(maxZ, n.z || 0);
        });

        // Add padding
        const pad = 10;
        const width = (maxX - minX) + pad * 2;
        const height = (maxY - minY) + pad * 2;
        const depth = (maxZ - minZ) + pad * 2;

        if (width < 5 || height < 5 || depth < 5) return;

        const cx = (minX + maxX) / 2;
        const cy = (minY + maxY) / 2;
        const cz = (minZ + maxZ) / 2;

        const geometry = new THREE.BoxGeometry(width, height, depth);
        const color = new THREE.Color(nodes[0].color || '#4488ff');

        const material = new THREE.MeshLambertMaterial({
            color: color,
            transparent: true,
            opacity: 0.15,
            depthWrite: false,
            side: THREE.DoubleSide,
            blending: THREE.AdditiveBlending
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(cx, cy, cz);
        scene.add(mesh);

        // Wireframe
        const wireGeo = new THREE.EdgesGeometry(geometry);
        const wireMat = new THREE.LineBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.4,
            blending: THREE.AdditiveBlending
        });
        const wireframe = new THREE.LineSegments(wireGeo, wireMat);
        wireframe.position.set(cx, cy, cz);
        scene.add(wireframe);

        FILE_CONTAINMENT.spheres.push({
            mesh, wireframe,
            fileIdx: parseInt(fileIdx),
            velocity: new THREE.Vector3(0, 0, 0),
            // FIX: Add activity and nodes for animation (was missing, caused crashes)
            activity: FILE_CONTAINMENT.particleActivity[fileIdx] || 0,
            nodes: nodes.map(n => n.id)
        });
    });
}
// ═══════════════════════════════════════════════════════════════════════
// SLOW MOTION PARTICLE ANIMATION - Dreamy physics with collisions
// ═══════════════════════════════════════════════════════════════════════

function startContainmentAnimation() {
    if (FILE_CONTAINMENT.isAnimating) return;
    FILE_CONTAINMENT.isAnimating = true;

    function animate() {
        if (!FILE_CONTAINMENT.isAnimating) return;

        const time = Date.now() * 0.001 * FILE_CONTAINMENT.slowMotionFactor;
        const graphNodes = Graph.graphData().nodes;

        if (FILE_CONTAINMENT.boundariesPopped) {
            // FREE PARTICLE MODE - Brownian motion with collisions
            applySoftCollisions(graphNodes, FILE_CONTAINMENT.gridCellSize, 0.4);

            graphNodes.forEach(node => {
                if (!node || !node.__physics) return;
                const p = node.__physics;

                // Perlin-like wandering
                const wander = 0.08;
                p.vx += (Math.sin(time * 0.7 + (node.__wanderPhase || 0)) - 0.5) * wander;
                p.vy += (Math.cos(time * 0.5 + (node.__wanderPhase || 0) * 1.3) - 0.5) * wander;
                if (IS_3D) p.vz += (Math.sin(time * 0.6 + (node.__wanderPhase || 0) * 0.7) - 0.5) * wander;

                // Damping
                p.vx *= 0.985;
                p.vy *= 0.985;
                p.vz *= 0.985;

                // Apply velocity
                node.x += p.vx;
                node.y += p.vy;
                if (IS_3D) node.z = (node.z || 0) + p.vz;
            });

        } else {
            // CONTAINED MODE - Activity-based oscillation inside spheres
            FILE_CONTAINMENT.spheres.forEach(sphere => {
                const activity = sphere.activity;

                // Pulse sphere opacity
                const pulse = Math.sin(time * 2 + sphere.fileIdx) * 0.5 + 0.5;
                if (sphere.mesh?.material) {
                    sphere.mesh.material.opacity = 0.04 + activity * 0.12 * pulse;
                }
                if (sphere.wireframe?.material) {
                    sphere.wireframe.material.opacity = 0.08 + activity * 0.2 * pulse;
                }

                if (activity < 0.05) return;

                // Perturb particles inside based on activity
                sphere.nodes.forEach(nodeId => {
                    const node = graphNodes.find(n => n.id === nodeId);
                    if (!node || !Number.isFinite(node.x)) return;

                    if (!node.__activityPhase) {
                        node.__activityPhase = {
                            x: Math.random() * Math.PI * 2,
                            y: Math.random() * Math.PI * 2,
                            z: Math.random() * Math.PI * 2
                        };
                    }

                    const amp = activity * 0.4;
                    const freq = 0.5 + activity * 0.5;
                    const phase = node.__activityPhase;

                    node.__renderOffsetX = Math.sin(time * freq + phase.x) * amp;
                    node.__renderOffsetY = Math.sin(time * freq * 1.2 + phase.y) * amp;
                    if (IS_3D) node.__renderOffsetZ = Math.sin(time * freq * 0.9 + phase.z) * amp;
                });
            });
        }

        if (Graph) Graph.refresh();
        FILE_CONTAINMENT.animationFrame = requestAnimationFrame(animate);
    }

    animate();
}

function stopContainmentAnimation() {
    FILE_CONTAINMENT.isAnimating = false;
    if (FILE_CONTAINMENT.animationFrame) {
        cancelAnimationFrame(FILE_CONTAINMENT.animationFrame);
    }
}

// ═══════════════════════════════════════════════════════════════════════
// POP THE BOUNDARIES - Release particles into free Brownian motion
// ═══════════════════════════════════════════════════════════════════════

function popBoundaries(duration = 3000) {
    if (FILE_CONTAINMENT.boundariesPopped) {
        restoreBoundaries(duration);
        return;
    }

    console.log('[Containment] Popping boundaries...');
    FILE_CONTAINMENT.boundariesPopped = true;
    const startTime = Date.now();
    const scene = Graph.scene();
    const graphNodes = Graph.graphData().nodes;

    // Initialize physics for each node
    graphNodes.forEach(node => {
        if (!node || !Number.isFinite(node.x)) return;
        node.__physics = {
            vx: (Math.random() - 0.5) * 1.5,
            vy: (Math.random() - 0.5) * 1.5,
            vz: IS_3D ? (Math.random() - 0.5) * 1.5 : 0
        };
        node.__wanderPhase = Math.random() * Math.PI * 2;
    });

    function animatePop() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(1, elapsed / duration);
        FILE_CONTAINMENT.popProgress = progress;
        const eased = 1 - Math.pow(1 - progress, 3);

        // Fade out spheres
        FILE_CONTAINMENT.spheres.forEach(s => {
            if (s.mesh?.material) s.mesh.material.opacity = (1 - eased) * 0.1;
            if (s.wireframe?.material) s.wireframe.material.opacity = (1 - eased) * 0.25;
            if (s.glow?.material) s.glow.material.opacity = (1 - eased) * 0.08;
        });

        if (progress < 1) {
            requestAnimationFrame(animatePop);
        } else {
            // Remove spheres
            FILE_CONTAINMENT.spheres.forEach(s => {
                if (s.mesh) scene.remove(s.mesh);
                if (s.wireframe) scene.remove(s.wireframe);
                if (s.glow) scene.remove(s.glow);
            });
            FILE_CONTAINMENT.spheres = [];
            console.log('[Containment] Particles now FREE - Brownian motion with collisions');
        }

        if (Graph) Graph.refresh();
    }

    animatePop();
    startContainmentAnimation();
}

function restoreBoundaries(duration = 2000) {
    if (!FILE_CONTAINMENT.boundariesPopped) return;

    console.log('[Containment] Restoring boundaries...');
    const startTime = Date.now();
    const graphNodes = Graph.graphData().nodes;

    graphNodes.forEach(node => {
        if (!node || !Number.isFinite(node.x)) return;
        node.__freePos = { x: node.x, y: node.y, z: node.z || 0 };
    });

    function animateRestore() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(1, elapsed / duration);
        FILE_CONTAINMENT.popProgress = 1 - progress;
        const eased = Math.pow(progress, 2);

        graphNodes.forEach(node => {
            if (!node || !node.__freePos || !node.__originalPos) return;
            node.x = node.__freePos.x + (node.__originalPos.x - node.__freePos.x) * eased;
            node.y = node.__freePos.y + (node.__originalPos.y - node.__freePos.y) * eased;
            if (IS_3D) node.z = node.__freePos.z + ((node.__originalPos.z || 0) - node.__freePos.z) * eased;
        });

        if (progress < 1) {
            requestAnimationFrame(animateRestore);
        } else {
            FILE_CONTAINMENT.boundariesPopped = false;
            if (DM) drawContainmentSpheres(null);  // Uses DM internally
            console.log('[Containment] Boundaries restored');
        }

        if (Graph) Graph.refresh();
    }

    animateRestore();
}

// Expose to global for button binding
window.popBoundaries = popBoundaries;
window.restoreBoundaries = restoreBoundaries;
window.FILE_CONTAINMENT = FILE_CONTAINMENT;

// ====================================================================
// FILE MODE HANDLERS
// ====================================================================

// FILES button - toggle file mode on/off
function setFileModeState(enabled) {
    fileMode = enabled;
    const cmdBtn = document.getElementById('cmd-files');
    if (cmdBtn) cmdBtn.classList.toggle('active', fileMode);
    const dockBtn = document.getElementById('btn-files');
    if (dockBtn) dockBtn.classList.toggle('active', fileMode);

    const filePanel = document.getElementById('file-panel');
    const modeControls = document.getElementById('file-mode-controls');
    const expandControls = document.getElementById('file-expand-controls');

    if (fileMode) {
        filePanel.classList.add('visible');
        modeControls.classList.add('visible');
        expandControls.classList.toggle('visible', fileVizMode === 'map');
        applyFileVizMode();
        applyEdgeMode();
        HudLayoutManager.reflow();
    } else {
        filePanel.classList.remove('visible');
        modeControls.classList.remove('visible');
        expandControls.classList.remove('visible');
        EXPANDED_FILES.clear();
        GRAPH_MODE = 'atoms';
        HudLayoutManager.reflow();
        clearAllFileModes();
        applyEdgeMode();
        refreshGraph();
    }
}

document.getElementById('btn-files').onclick = () => {
    setFileModeState(!fileMode);
};

// COLOR mode - atoms colored by file
document.getElementById('btn-file-color').onclick = () => {
    setFileVizMode('color');
};

// HULLS mode - draw boundary spheres
document.getElementById('btn-file-hulls').onclick = () => {
    setFileVizMode('hulls');
};

// CLUSTER mode - force clustering by file
document.getElementById('btn-file-cluster').onclick = () => {
    setFileVizMode('cluster');
};

// MAP mode - show file nodes
document.getElementById('btn-file-map').onclick = () => {
    setFileVizMode('map');
};

// SPHERES mode - show containment spheres (button may be hidden)
const spheresBtn = document.getElementById('btn-file-spheres');
if (spheresBtn) spheresBtn.onclick = () => setFileVizMode('spheres');

// POP button - toggle boundary pop/restore (button may be hidden)
const popBtn = document.getElementById('btn-file-pop');
if (popBtn) {
    popBtn.onclick = () => {
        if (!FILE_CONTAINMENT.boundariesPopped) {
            popBoundaries(3000);
            popBtn.classList.add('active');
            popBtn.textContent = 'RESTORE';
            showToast('Boundaries popped! Particles in slow-motion chaos...');
        } else {
            restoreBoundaries(2000);
            popBtn.classList.remove('active');
            popBtn.textContent = 'POP!';
            showToast('Boundaries restored. Order from chaos.');
        }
    };
}

// Expand mode toggles (only relevant in MAP mode)
document.getElementById('btn-expand-inline').onclick = () => {
    FILE_EXPAND_MODE = 'inline';
    updateExpandButtons();
    if (GRAPH_MODE === 'hybrid') {
        refreshGraph();
    }
};

document.getElementById('btn-expand-detach').onclick = () => {
    FILE_EXPAND_MODE = 'detach';
    updateExpandButtons();
    if (GRAPH_MODE === 'hybrid') {
        refreshGraph();
    }
};

function updateExpandButtons() {
    document.getElementById('btn-expand-inline').classList.toggle('active', FILE_EXPAND_MODE === 'inline');
    document.getElementById('btn-expand-detach').classList.toggle('active', FILE_EXPAND_MODE === 'detach');
}

function setFileVizMode(mode) {
    fileVizMode = mode;
    // Update button states
    document.querySelectorAll('.file-mode-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById('btn-file-' + mode).classList.add('active');
    const expandControls = document.getElementById('file-expand-controls');
    expandControls.classList.toggle('visible', fileVizMode === 'map');
    if (fileVizMode === 'map') {
        updateExpandButtons();
    }
    if (fileVizMode === 'map') {
        GRAPH_MODE = (EXPANDED_FILES.size > 0) ? 'hybrid' : 'files';
    } else {
        EXPANDED_FILES.clear();
        GRAPH_MODE = 'atoms';
    }
    if (!fileMode) {
        setFileModeState(true);
    } else if (fileVizMode === 'map') {
        applyFileVizMode();
    } else {
        refreshGraph();
    }
}

function applyFileVizMode() {
    if (!fileMode) return;

    // Clear previous state
    clearFileBoundaries();
    if (fileVizMode !== 'hulls') {
        hullRedrawAttempts = 0;
    }

    // ALL DATA FROM DM
    const graphNodes = DM ? DM.getVisibleNodes() : (Graph?.graphData()?.nodes || []);

    // FILE COHESION: Auto-activate for color/hulls/cluster modes (precise file separation)
    if (fileVizMode === 'color' || fileVizMode === 'hulls' || fileVizMode === 'cluster') {
        const physicsPayload = { physics: DM.raw.physics, config: DM.raw.config };
        applyFileCohesion(physicsPayload);  // Uses DM internally + Token Config
    }

    if (fileVizMode === 'color') {
        // Color mode is already applied via node colors
        // Just ensure nodes have file colors
        applyFileColors(graphNodes);
    }
    else if (fileVizMode === 'hulls') {
        // Draw boundary hulls (cohesion force already applied above)
        applyFileColors(graphNodes);
        scheduleHullRedraw(1500);  // Delay to let cohesion settle
    }
    else if (fileVizMode === 'cluster') {
        // Apply clustering force
        applyFileColors(graphNodes);
        applyClusterForce(DM.raw);  // FIX: was undefined `data`, now uses DM.raw
    }
    else if (fileVizMode === 'map') {
        // File map uses file nodes + optional expansion
        GRAPH_MODE = (EXPANDED_FILES.size > 0) ? 'hybrid' : 'files';
        refreshGraph();
        showToast('File map active. Click a file node to expand.');
    }
    else if (fileVizMode === 'spheres') {
        // Containment spheres mode - particles held by transparent force fields
        applyFileColors(graphNodes);

        // Build directory tree and compute activity levels
        // FIX: was undefined `data`, now uses DM.raw
        buildDirectoryTree(DM.raw);
        computeFileActivity(DM.raw, graphNodes);

        // Draw containment spheres
        drawContainmentSpheres(DM.raw, graphNodes);

        // Start the slow-motion animation with collisions
        startContainmentAnimation();

        showToast('Containment spheres active. Files as force fields. Click POP! to release.');
    }
}

function scheduleHullRedraw(delayMs = 1200) {
    if (hullRedrawTimer) {
        clearTimeout(hullRedrawTimer);
    }
    hullRedrawTimer = setTimeout(() => {
        if (!(fileMode && fileVizMode === 'hulls')) {
            hullRedrawAttempts = 0;
            return;
        }
        const drawn = drawFileBoundaries(null);  // Uses DM internally
        if (drawn === 0 && hullRedrawAttempts < 3) {
            hullRedrawAttempts += 1;
            scheduleHullRedraw(1200 + (hullRedrawAttempts * 700));
        } else {
            hullRedrawAttempts = 0;
        }
    }, delayMs);
}

function applyFileColors(graphNodes) {
    // Generate file colors and apply to nodes - ALL DATA FROM DM
    const boundaries = DM ? DM.getFileBoundaries() : [];
    const totalFiles = boundaries.length;
    graphNodes.forEach(node => {
        if (node.fileIdx >= 0) {
            const fileInfo = boundaries[node.fileIdx] || {};
            const fileLabel = fileInfo.file || fileInfo.file_name || node.fileIdx;
            node.color = getFileColor(node.fileIdx, totalFiles, fileLabel);
        }
    });
    Graph.nodeColor(n => toColorNumber(n.color, 0x888888));
}

function clearFileBoundaries() {
    const scene = Graph.scene();
    fileBoundaryMeshes.forEach(mesh => scene.remove(mesh));
    fileBoundaryMeshes = [];
}

function clearAllFileModes() {
    clearFileBoundaries();
    // Reset file cohesion force if active
    clearFileCohesion();
    // Reset cluster force if active
    if (clusterForceActive) {
        Graph.d3Force('cluster', null);
        clusterForceActive = false;
        if (DEFAULT_LINK_DISTANCE !== null) {
            Graph.d3Force('link').distance(DEFAULT_LINK_DISTANCE);
        }
        Graph.d3ReheatSimulation();
    }
    // Stop containment animation if active
    stopContainmentAnimation();
    // Clear containment spheres
    if (FILE_CONTAINMENT && FILE_CONTAINMENT.spheres) {
        const scene = Graph.scene();
        FILE_CONTAINMENT.spheres.forEach(s => {
            if (s.mesh) scene.remove(s.mesh);
        });
        FILE_CONTAINMENT.spheres = [];
        FILE_CONTAINMENT.boundariesPopped = false;
    }

    // Fix: Clear lingering filters that may have been auto-populated by defaults during File Mode
    if (VIS_FILTERS.rings.size > 0 || VIS_FILTERS.tiers.size > 0 || VIS_FILTERS.families.size > 0 || VIS_FILTERS.files.size > 0) {
        VIS_FILTERS.rings.clear();
        VIS_FILTERS.tiers.clear();
        VIS_FILTERS.families.clear();
        VIS_FILTERS.roles.clear();
        VIS_FILTERS.files.clear();
        VIS_FILTERS.edges.clear();
        VIS_FILTERS.layers.clear();
        VIS_FILTERS.effects.clear();
        VIS_FILTERS.edgeFamilies.clear();
        // Update UI chips
        document.querySelectorAll('.filter-chip.active').forEach(c => c.classList.remove('active'));
    }

    // Reset POP button state
    const popBtn = document.getElementById('btn-file-pop');
    if (popBtn) {
        popBtn.classList.remove('active');
        popBtn.textContent = 'POP!';
    }
}

function applyClusterForce(data) {
    // ALL DATA FROM DM - the physics pipeline
    const clusterConfig = data?.physics?.cluster || {};
    const modeStrength =
        (typeof clusterConfig.modes?.strong === 'number') ? clusterConfig.modes.strong : null;
    const sliderStrength =
        (typeof APPEARANCE_STATE.clusterStrength === 'number') ? APPEARANCE_STATE.clusterStrength : null;
    const clusterStrength =
        (typeof sliderStrength === 'number')
            ? sliderStrength
            : ((typeof modeStrength === 'number')
                ? modeStrength
                : ((typeof clusterConfig.strength === 'number') ? clusterConfig.strength : 0.3));
    const clusterRadius =
        (typeof clusterConfig.radius === 'number') ? clusterConfig.radius : 150;
    const clusterZSpacing =
        (typeof clusterConfig.zSpacing === 'number') ? clusterConfig.zSpacing : 30;
    const linkDistance =
        (typeof clusterConfig.linkDistance === 'number')
            ? clusterConfig.linkDistance
            : (data?.physics?.forces?.link?.distance || 50);

    const graphNodes = DM ? DM.getVisibleNodes() : (Graph?.graphData()?.nodes || []);
    const boundaries = DM ? DM.getFileBoundaries() : (data?.file_boundaries || []);
    const numFiles = boundaries.length;

    // FIXED TARGET POSITIONS: Arrange files in a circular pattern
    // This creates CLEAR visual separation instead of clustering around mixed centroids
    const radius = clusterRadius;  // Separation radius
    const fileTargets = {};

    for (let i = 0; i < numFiles; i++) {
        fileTargets[i] = getFileTarget(i, numFiles, radius, clusterZSpacing);
    }

    // Reduce link distance to keep intra-file nodes tighter
    Graph.d3Force('link').distance(linkDistance);

    // Apply strong clustering force toward fixed targets
    Graph.d3Force('cluster', (alpha) => {
        const k = alpha * clusterStrength;
        graphNodes.forEach(node => {
            const target = fileTargets[node.fileIdx];
            if (target) {
                node.vx = (node.vx || 0) + (target.x - node.x) * k;
                node.vy = (node.vy || 0) + (target.y - node.y) * k;
                if (IS_3D) {
                    node.vz = (node.vz || 0) + (target.z - node.z) * k;
                }
            }
        });
    });

    clusterForceActive = true;
    Graph.d3ReheatSimulation();

    // Also draw hulls after clustering settles
    scheduleHullRedraw(1500);
}

// ════════════════════════════════════════════════════════════════════════
// FILE COHESION FORCE - TOKEN-DRIVEN precise file separation
// ════════════════════════════════════════════════════════════════════════
let fileCohesionActive = false;

function applyFileCohesion(data) {
    if (fileCohesionActive) return;

    // TOKEN-DRIVEN: config from payload, APPEARANCE_STATE override, then defaults
    const config = data?.physics?.fileCohesion || {};
    const strength = (typeof APPEARANCE_STATE.fileCohesionStrength === 'number')
        ? APPEARANCE_STATE.fileCohesionStrength
        : (config.strength ?? 0.15);
    const linkMult = config.interFileLinkMultiplier ?? 2.5;
    const minDist = config.minDistance ?? 20;

    const nodes = DM ? DM.getVisibleNodes() : (Graph?.graphData()?.nodes || []);
    if (!nodes.length) return;

    // Pre-compute file groups
    const groups = new Map();
    nodes.forEach(n => {
        const f = n.fileIdx ?? -1;
        if (f >= 0) (groups.get(f) || groups.set(f, []).get(f)).push(n);
    });

    // Intra-file centroid attraction
    Graph.d3Force('fileCohesion', (alpha) => {
        const k = strength * alpha;
        groups.forEach(g => {
            if (g.length < 2) return;
            let cx = 0, cy = 0, cz = 0;
            g.forEach(n => { cx += n.x || 0; cy += n.y || 0; cz += n.z || 0; });
            cx /= g.length; cy /= g.length; cz /= g.length;
            g.forEach(n => {
                const dx = cx - (n.x || 0), dy = cy - (n.y || 0), dz = cz - (n.z || 0);
                const d = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;
                if (d > minDist) {
                    const f = k * Math.min(1, d / 100);
                    n.vx = (n.vx || 0) + dx * f;
                    n.vy = (n.vy || 0) + dy * f;
                    if (IS_3D) n.vz = (n.vz || 0) + dz * f;
                }
            });
        });
    });

    // Inter-file links stretched
    const base = DEFAULT_LINK_DISTANCE || 50;
    Graph.d3Force('link').distance(link => {
        const s = typeof link.source === 'object' ? link.source : nodes.find(n => n.id === link.source);
        const t = typeof link.target === 'object' ? link.target : nodes.find(n => n.id === link.target);
        if (!s || !t) return base;
        const sf = s.fileIdx ?? -1, tf = t.fileIdx ?? -1;
        return (sf >= 0 && tf >= 0 && sf !== tf) ? base * linkMult : base;
    });

    fileCohesionActive = true;
    Graph.d3ReheatSimulation();
}

function clearFileCohesion() {
    if (!fileCohesionActive) return;
    Graph.d3Force('fileCohesion', null);
    if (DEFAULT_LINK_DISTANCE !== null) Graph.d3Force('link').distance(DEFAULT_LINK_DISTANCE);
    fileCohesionActive = false;
    Graph.d3ReheatSimulation();
}

// ════════════════════════════════════════════════════════════════════════
// OKLCH COLOR PICKER - Embedded (self-contained)
// ════════════════════════════════════════════════════════════════════════
const oklchState = { l: 70, c: 0.15, h: 220, a: 100 };

function oklchToRgb(l, c, h) {
    // Convert OKLCH to sRGB (simplified)
    const L = l / 100;
    const hr = h * Math.PI / 180;
    const a = c * Math.cos(hr);
    const b = c * Math.sin(hr);
    // Oklab to LMS
    const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
    const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
    const s_ = L - 0.0894841775 * a - 1.2914855480 * b;
    const lms = [l_ * l_ * l_, m_ * m_ * m_, s_ * s_ * s_];
    // LMS to XYZ
    const x = 1.2270138511 * lms[0] - 0.5577999807 * lms[1] + 0.281256149 * lms[2];
    const y = -0.0405801784 * lms[0] + 1.1122568696 * lms[1] - 0.0716766787 * lms[2];
    const z = -0.0763812845 * lms[0] - 0.4214819784 * lms[1] + 1.5861632204 * lms[2];
    // XYZ to linear RGB
    let rl = 3.2409699419 * x - 1.5373831776 * y - 0.4986107603 * z;
    let gl = -0.9692436363 * x + 1.8759675015 * y + 0.0415550574 * z;
    let bl = 0.0556300797 * x - 0.2039769589 * y + 1.0569715142 * z;
    // Linear to sRGB
    const toSrgb = v => v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(Math.abs(v), 1 / 2.4) - 0.055;
    return {
        r: Math.round(Math.max(0, Math.min(1, toSrgb(rl))) * 255),
        g: Math.round(Math.max(0, Math.min(1, toSrgb(gl))) * 255),
        b: Math.round(Math.max(0, Math.min(1, toSrgb(bl))) * 255),
        inGamut: rl >= -0.001 && rl <= 1.001 && gl >= -0.001 && gl <= 1.001 && bl >= -0.001 && bl <= 1.001
    };
}

function updateOklchPicker() {
    const { l, c, h, a } = oklchState;
    const rgb = oklchToRgb(l, c, h);
    const hex = '#' + [rgb.r, rgb.g, rgb.b].map(v => v.toString(16).padStart(2, '0')).join('');

    // Update swatch
    const swatch = document.getElementById('oklch-swatch');
    if (swatch) swatch.style.background = `oklch(${l}% ${c} ${h} / ${a}%)`;

    // Update CSS output
    const cssInput = document.getElementById('oklch-css');
    if (cssInput) cssInput.value = a < 100
        ? `oklch(${l}% ${c.toFixed(3)} ${h} / ${a}%)`
        : `oklch(${l}% ${c.toFixed(3)} ${h})`;

    // Update value displays
    const lVal = document.getElementById('oklch-l-val');
    const cVal = document.getElementById('oklch-c-val');
    const hVal = document.getElementById('oklch-h-val');
    const aVal = document.getElementById('oklch-a-val');
    if (lVal) lVal.textContent = l + '%';
    if (cVal) cVal.textContent = c.toFixed(3);
    if (hVal) hVal.textContent = h + '°';
    if (aVal) aVal.textContent = a + '%';

    // Update gamut info
    const gamutInfo = document.getElementById('oklch-gamut');
    if (gamutInfo) {
        if (rgb.inGamut) {
            gamutInfo.textContent = 'sRGB ✓';
            gamutInfo.classList.remove('out-of-gamut');
        } else {
            gamutInfo.textContent = 'Outside sRGB (P3/Rec2020)';
            gamutInfo.classList.add('out-of-gamut');
        }
    }

    // Update hue gradient background
    const cSlider = document.getElementById('oklch-c');
    if (cSlider) cSlider.style.background = `linear-gradient(90deg, #888, oklch(${l}% 0.4 ${h}))`;
    const aSlider = document.getElementById('oklch-a');
    if (aSlider) aSlider.style.background = `linear-gradient(90deg, transparent, oklch(${l}% ${c} ${h}))`;

    // Draw 2D canvas (L vs H at current C)
    drawOklch2D();
}

function drawOklch2D() {
    const canvas = document.getElementById('oklch-canvas-2d');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width = canvas.clientWidth * 2;
    const h = canvas.height = canvas.clientHeight * 2;
    const c = oklchState.c;

    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            const hue = (x / w) * 360;
            const lightness = 100 - (y / h) * 100;
            const rgb = oklchToRgb(lightness, c, hue);
            ctx.fillStyle = rgb.inGamut
                ? `rgb(${rgb.r},${rgb.g},${rgb.b})`
                : `rgba(${rgb.r},${rgb.g},${rgb.b},0.3)`;
            ctx.fillRect(x, y, 1, 1);
        }
    }

    // Draw current position marker
    const markerX = (oklchState.h / 360) * w;
    const markerY = ((100 - oklchState.l) / 100) * h;
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(markerX, markerY, 8, 0, Math.PI * 2);
    ctx.stroke();
}

function initOklchPicker() {
    ['l', 'c', 'h', 'a'].forEach(key => {
        const slider = document.getElementById('oklch-' + key);
        if (slider) {
            slider.value = oklchState[key];
            slider.oninput = function () {
                oklchState[key] = parseFloat(this.value);
                updateOklchPicker();
            };
        }
    });

    // Canvas click to pick color
    const canvas = document.getElementById('oklch-canvas-2d');
    if (canvas) {
        canvas.onclick = function (e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            oklchState.h = Math.round((x / rect.width) * 360);
            oklchState.l = Math.round(100 - (y / rect.height) * 100);
            document.getElementById('oklch-h').value = oklchState.h;
            document.getElementById('oklch-l').value = oklchState.l;
            updateOklchPicker();
        };
    }

    updateOklchPicker();
}

function toggleOklchPicker() {
    const picker = document.getElementById('oklch-picker');
    const isVisible = picker.classList.toggle('visible');
    const btn = document.getElementById('cmd-oklch');
    if (btn) btn.classList.toggle('active', isVisible);
    if (isVisible && !picker.dataset.init) {
        picker.dataset.init = 'true';
        initOklchPicker();
    }
}

// ════════════════════════════════════════════════════════════════════════
// SURFACE PARITY HANDLERS - Architectural Enforcements
// ════════════════════════════════════════════════════════════════════════

// Panel Handlers
function togglePanelView() { togglePanel('view'); }
function togglePanelFilter() { togglePanel('filter'); }
function togglePanelStyle() { togglePanel('style'); }
function togglePanelSettings() { togglePanel('settings'); }

// Command Bar Handlers
function handleCmdView() { togglePanelView(); }
function handleCmdFilter() { togglePanelFilter(); }
function handleCmdStyle() { togglePanelStyle(); }
function handleCmdSettings() { togglePanelSettings(); }
function handleCmdOklch() { toggleOklchPicker(); }

// Action Handlers
function handleCmdFiles() {
    const btn = document.getElementById('cmd-files');
    const isActive = btn ? btn.classList.contains('active') : false;
    setFileModeState(!isActive);
}
function handleCmdFlow() { toggleFlowMode(); }
function handleCmd3d() { toggleDimensions(); }

// ════════════════════════════════════════════════════════════════════════
// PANEL DRAG & RESIZE - Make panels movable and resizable
// ════════════════════════════════════════════════════════════════════════

const PanelManager = {
    panels: new Map(),
    activePanel: null,
    dragState: null,
    resizeState: null,
    storageKey: 'collider-panel-positions',

    init() {
        // Initialize draggable/resizable panels (use actual element IDs)
        this.initPanel('side-dock', { draggable: true, resizable: true, minWidth: 150, maxWidth: 400 });
        this.initPanel('header-panel', { draggable: true, resizable: false });
        this.initPanel('stats-panel', { draggable: true, resizable: false });
        this.initPanel('metrics-panel', { draggable: true, resizable: true, minWidth: 180, maxWidth: 350 });

        // Restore saved positions
        this.restorePositions();

        // Global mouse handlers
        document.addEventListener('mousemove', (e) => this.onMouseMove(e));
        document.addEventListener('mouseup', (e) => this.onMouseUp(e));
    },

    initPanel(id, options = {}) {
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

        this.panels.set(id, config);

        // Make panel positioned if not already
        const style = window.getComputedStyle(panel);
        if (style.position === 'static') {
            panel.style.position = 'absolute';
        }

        // Add drag handle (the panel header or title)
        if (config.draggable) {
            const header = panel.querySelector('.side-title, .hud-title, .panel-header') || panel;
            header.style.cursor = 'move';
            header.addEventListener('mousedown', (e) => this.startDrag(e, id));
        }

        // Add resize handle
        if (config.resizable) {
            const handle = document.createElement('div');
            handle.className = 'panel-resize-handle';
            handle.addEventListener('mousedown', (e) => this.startResize(e, id));
            panel.appendChild(handle);
            panel.style.position = 'absolute'; // Required for resize
        }
    },

    startDrag(e, panelId) {
        // Don't drag if clicking on interactive elements
        if (e.target.closest('input, button, select, .collapsible-content, .preset-btn, .layout-btn, .color-scheme-btn')) {
            return;
        }

        const config = this.panels.get(panelId);
        if (!config) return;

        e.preventDefault();
        const rect = config.el.getBoundingClientRect();

        this.dragState = {
            panelId,
            startX: e.clientX,
            startY: e.clientY,
            startLeft: rect.left,
            startTop: rect.top
        };

        config.el.classList.add('panel-dragging');
    },

    startResize(e, panelId) {
        const config = this.panels.get(panelId);
        if (!config) return;

        e.preventDefault();
        e.stopPropagation();

        const rect = config.el.getBoundingClientRect();

        this.resizeState = {
            panelId,
            startX: e.clientX,
            startY: e.clientY,
            startWidth: rect.width,
            startHeight: rect.height
        };

        config.el.classList.add('panel-resizing');
    },

    onMouseMove(e) {
        if (this.dragState) {
            const config = this.panels.get(this.dragState.panelId);
            if (!config) return;

            const dx = e.clientX - this.dragState.startX;
            const dy = e.clientY - this.dragState.startY;

            let newLeft = this.dragState.startLeft + dx;
            let newTop = this.dragState.startTop + dy;

            // Keep within viewport
            newLeft = Math.max(0, Math.min(window.innerWidth - 50, newLeft));
            newTop = Math.max(0, Math.min(window.innerHeight - 50, newTop));

            config.el.style.left = newLeft + 'px';
            config.el.style.top = newTop + 'px';
            config.el.style.right = 'auto';
            config.el.style.bottom = 'auto';
        }

        if (this.resizeState) {
            const config = this.panels.get(this.resizeState.panelId);
            if (!config) return;

            const dx = e.clientX - this.resizeState.startX;
            const dy = e.clientY - this.resizeState.startY;

            let newWidth = this.resizeState.startWidth + dx;
            let newHeight = this.resizeState.startHeight + dy;

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
    },

    onMouseUp(e) {
        if (this.dragState) {
            const config = this.panels.get(this.dragState.panelId);
            if (config) {
                config.el.classList.remove('panel-dragging');
                this.savePositions();
            }
            this.dragState = null;
        }

        if (this.resizeState) {
            const config = this.panels.get(this.resizeState.panelId);
            if (config) {
                config.el.classList.remove('panel-resizing');
                this.savePositions();
            }
            this.resizeState = null;
        }
    },

    savePositions() {
        const positions = {};
        this.panels.forEach((config, id) => {
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
            localStorage.setItem(this.storageKey, JSON.stringify(positions));
        } catch (e) {
            console.warn('[PanelManager] Could not save positions:', e);
        }
    },

    restorePositions() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (!saved) return;

            const positions = JSON.parse(saved);
            Object.entries(positions).forEach(([id, pos]) => {
                const config = this.panels.get(id);
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
            console.warn('[PanelManager] Could not restore positions:', e);
        }
    },

    resetPositions() {
        try {
            localStorage.removeItem(this.storageKey);
            location.reload();
        } catch (e) {
            console.warn('[PanelManager] Could not reset positions:', e);
        }
    }
};

// Initialize after DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => PanelManager.init());
} else {
    // Small delay to ensure all panels are rendered
    setTimeout(() => PanelManager.init(), 100);
}

// Expose for debugging
window.PanelManager = PanelManager;
