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
let DM = null;  // DataManager instance - initialized in initGraph()
let Legend = null;  // LegendManager instance - initialized in initGraph()
let CURRENT_DENSITY = 1; // Default: show all nodes
let ACTIVE_DATAMAPS = new Set();
let DATAMAP_CONFIGS = [];
let DATAMAP_INDEX = {};
let DATAMAP_UI = new Map();
let HOVERED_NODE = null;
// SELECTED_NODE_IDS - provided by selection.js module (getter to SELECT.ids)
let DATASET_KEY = 'default';
let GROUPS_STORAGE_KEY = 'collider_groups_default';
let GROUPS = [];
let ACTIVE_GROUP_ID = null;
// MARQUEE_ACTIVE, MARQUEE_START, MARQUEE_ADDITIVE, LAST_MARQUEE_END_TS - provided by selection.js module
let SELECTION_BOX = null;
const SELECTION_HALO_GEOMETRY = new THREE.SphereGeometry(1, 12, 12);
const GROUP_HALO_GEOMETRY = new THREE.SphereGeometry(1, 12, 12);
let SPACE_PRESSED = false;
let IS_3D = true;
let DIMENSION_TRANSITION = false;
// STARFIELD REMOVED - nodes ARE the stars, no need for confusing background dots
let BLOOM_PASS = null;
let BLOOM_STRENGTH = 0;
// EDGE_MODE - provided by edge-system.js module
let EDGE_DEFAULT_OPACITY = null;  // Initialized from appearance.tokens at runtime (token value: 0.08)

// PERF_MONITOR - provided by perf-monitor.js module (window.PERF, window.PERF_MONITOR)

// Initialize after DOM ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => PERF_MONITOR.init(), 100);
    // Initialize SidebarManager facade for sidebar controls
    if (typeof SIDEBAR !== 'undefined' && SIDEBAR.init) {
        SIDEBAR.init();
    }
});
let DEFAULT_LINK_DISTANCE = null;

// =================================================================
// THEME CONFIGURATION: Loaded from payload at runtime
// =================================================================
let THEME_CONFIG = {
    available: ['dark'],
    default: 'dark',
    current: 'dark',
    colors: {
        edge: {},
        viz: {},
        console: {},
        schemes: {}
    }
};

// Default color configs - will be overridden by payload tokens
// Edge mode configuration - populated from appearance.tokens at runtime
// Fallback values are defined in appearance.tokens.json:131-204
let EDGE_MODE_CONFIG = {
    resolution: {},
    weight: {},
    confidence: {},
    width: {},
    dim: {},
    opacity: null
};
// Edge type colors - populated from theme.tokens.json:501-512 at runtime
let EDGE_COLOR_CONFIG = {};
// FILE_COLOR_CONFIG, EDGE_RANGES, NODE_FILE_INDEX - provided by modules (file-viz.js, edge-system.js)
let NODE_COLOR_CONFIG = { tier: {}, ring: {}, unknown: '#666666' };

// Console logging colors - populated from theme config
let CONSOLE_COLORS = {
    success: '#4ade80',
    error: '#f87171',
    warning: '#ffaa00',
    info: '#4dd4ff'
};

// Viz colors for canvas and fallbacks - populated from theme config
let VIZ_COLORS = {
    canvasBg: '#03040a',
    nodeFallback: '#888888',
    edgeFallback: '#333333',
    groupHalo: '#88d0ff'
};
let FLOW_CONFIG = {};  // Flow mode settings from THE REMOTE CONTROL
window.GRAPH_MODE = 'atoms'; // atoms | files | hybrid - on window for FILE_VIZ access

// Layout stability: cache node positions to prevent re-randomization on toggles
let NODE_POSITION_CACHE = new Map();
let LAYOUT_FROZEN = false;  // When true, don't reheat simulation
let HINTS_ENABLED = true;   // Show mode toasts

// FILE_GRAPH, FILE_NODE_IDS, EXPANDED_FILES, FILE_EXPAND_MODE - provided by file-viz.js module
let LAST_FILTER_SUMMARY = null;
let FILE_NODE_POSITIONS = new Map();
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
    nodeOpacity: 1,
    labelSize: 1,
    showLabels: true,
    highlightSelected: true,
    edgeOpacity: null,
    edgeWidth: 1,
    edgeCurvature: 0,
    showArrows: false,
    gradientEdges: true,
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
// fileBoundaryMeshes, fileMode, fileVizMode - provided by file-viz.js module
let originalNodeColors = new Map();
let clusterForceActive = false;
let hullRedrawTimer = null;
let hullRedrawAttempts = 0;
const originalColorsForDim = new Map();
let flowMode = false; // Hoisted from line 7333

// REGISTRY - provided by registry.js module (window.REGISTRY)


// =================================================================
// GLOBAL CONSTANTS (Hoisted for safety)
// =================================================================
const SELECTION_SIZE_MULT = 2.2;    // Make selected nodes BIGGER

// OKLCH PENDULUM COLOR OSCILLATOR - FULL RAINBOW EDITION
const PENDULUM = {
    hue: {
        angle: Math.random() * Math.PI * 2,
        velocity: 0,
        damping: null,        // Set from appearance.tokens
        gravity: null,        // Set from appearance.tokens
        length: 1.0,
        rotationSpeed: null   // Set from appearance.tokens
    },
    chroma: {
        angle: Math.random() * Math.PI * 2,
        velocity: 0,
        damping: null,
        gravity: null,
        length: 1.0,
        center: null,
        amplitude: null
    },
    lightness: {
        phase: 0,
        speed: null,
        center: null,
        amplitude: null
    },
    ripple: {
        speed: null,
        scale: null
    },
    currentHue: Math.random() * 360,
    lastTime: 0,
    running: false
};
// =====================================================================
// HOVER & SELECTION STATE (declared early to avoid TDZ errors)
// =====================================================================
let _lastHoveredNodeId = null;
const selectionOriginals = new Map();

// amplify, amplifyContrast - provided by core.js module

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
// FLOATING PANEL CONTROL SYSTEM - CONSOLIDATED INTO modules/panels.js
// =====================================================================
// openPanel, closePanel, togglePanel, initCommandBar - ALL IN panels.js
// (backward compat shims in panels.js)


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

// renderLegendSection, renderAllLegends - MOVED TO modules/legend-manager.js

// Debounce wrapper to prevent DOM thrashing during rapid updates
let _legendDebounceTimer = null;
const _originalRenderAllLegends = renderAllLegends;
renderAllLegends = function () {
    if (_legendDebounceTimer) clearTimeout(_legendDebounceTimer);
    _legendDebounceTimer = setTimeout(() => {
        _originalRenderAllLegends();
        _legendDebounceTimer = null;
    }, 100); // 100ms debounce
};

// =====================================================================
// HUD LAYOUT MANAGER: MIGRATED TO modules/layout.js
// =====================================================================
// HudLayoutManager (390 lines) has been migrated to modules/layout.js
// which provides the LAYOUT module with:
//   - All original panel placement functionality
//   - NEW: Toast/control-bar collision detection
//   - NEW: Min-width graph validation
//   - NEW: Debug overlay (Ctrl+Shift+L)
//   - NEW: Component registration system
//
// Backward compatibility: window.HudLayoutManager = LAYOUT (alias)
// =====================================================================

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
        window.GRAPH_MODE = 'atoms';
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
    canvas.style.background = VIZ_COLORS.canvasBg;
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
        return c || VIZ_COLORS.nodeFallback;
    }

    function render() {
        ctx.fillStyle = VIZ_COLORS.canvasBg;
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
    // SIDEBAR: Populate filter chips from loaded data
    // =================================================================
    if (typeof SIDEBAR !== 'undefined' && SIDEBAR.populateFilterChips) {
        SIDEBAR.populateFilterChips(data);
    }

    // =================================================================
    // SIDEBAR: Apply deferred view mode (files mode if saved in localStorage)
    // =================================================================
    if (typeof SIDEBAR !== 'undefined' && SIDEBAR.applyDeferredViewMode) {
        SIDEBAR.applyDeferredViewMode();
    }

    // =================================================================
    // TOKEN-DRIVEN CONFIG: Extract from payload
    // =================================================================
    const physicsConfig = data.physics || {};
    const appearanceConfig = data.appearance || {};
    window.APPEARANCE_CONFIG = appearanceConfig;

    // =================================================================
    // THEME CONFIG: Load theme configuration for runtime switching
    // =================================================================
    if (data.theme_config) {
        THEME_CONFIG = {
            ...THEME_CONFIG,
            available: data.theme_config.available || ['dark'],
            default: data.theme_config.default || 'dark',
            current: data.theme_config.default || 'dark',
            colors: data.theme_config.colors || THEME_CONFIG.colors
        };

        // Apply edge colors from theme config
        if (THEME_CONFIG.colors.edge) {
            EDGE_COLOR_CONFIG = { ...EDGE_COLOR_CONFIG, ...THEME_CONFIG.colors.edge };
        }

        // Apply viz colors from theme config
        if (THEME_CONFIG.colors.viz) {
            const viz = THEME_CONFIG.colors.viz;
            VIZ_COLORS = {
                canvasBg: viz['canvas-bg'] || VIZ_COLORS.canvasBg,
                nodeFallback: viz['node-fallback'] || VIZ_COLORS.nodeFallback,
                edgeFallback: viz['edge-fallback'] || VIZ_COLORS.edgeFallback,
                groupHalo: viz['group-halo'] || VIZ_COLORS.groupHalo
            };
        }

        // Apply console colors from theme config
        if (THEME_CONFIG.colors.console) {
            CONSOLE_COLORS = { ...CONSOLE_COLORS, ...THEME_CONFIG.colors.console };
        }

        console.log(`%c[Theme] Loaded: ${THEME_CONFIG.available.join(', ')}`, `color: ${CONSOLE_COLORS.info}; font-weight: bold`);
    }
    const simulation = physicsConfig.simulation || {};
    const background = appearanceConfig.background || {};
    // const stars = background.stars || {};  // REMOVED - starfield feature deleted
    const bloom = background.bloom || {};
    // NEW: Render, highlight, flow_mode from THE REMOTE CONTROL
    const renderConfig = appearanceConfig.render || {};
    const highlightConfig = appearanceConfig.highlight || {};
    FLOW_CONFIG = appearanceConfig.flow_mode || {};

    // Merge animation tokens into PENDULUM (T004)
    const animationConfig = appearanceConfig.animation || {};
    if (animationConfig.hue) {
        PENDULUM.hue.damping = animationConfig.hue.damping ?? 0.9995;
        PENDULUM.hue.gravity = animationConfig.hue.speed ?? 0.0008;
        PENDULUM.hue.rotationSpeed = animationConfig.hue.rotation ?? 0.8;
    }
    if (animationConfig.chroma) {
        PENDULUM.chroma.damping = animationConfig.chroma.damping ?? 0.998;
        PENDULUM.chroma.gravity = animationConfig.chroma.gravity ?? 0.0004;
        PENDULUM.chroma.center = animationConfig.chroma.center ?? 0.32;
        PENDULUM.chroma.amplitude = animationConfig.chroma.amplitude ?? 0.08;
    }
    if (animationConfig.lightness) {
        PENDULUM.lightness.speed = animationConfig.lightness.speed ?? 0.02;
        PENDULUM.lightness.center = animationConfig.lightness.center ?? 82;
        PENDULUM.lightness.amplitude = animationConfig.lightness.amplitude ?? 10;
    }
    if (animationConfig.ripple) {
        PENDULUM.ripple.speed = animationConfig.ripple.speed ?? 0.035;
        PENDULUM.ripple.scale = animationConfig.ripple.scale ?? 200;
    }
    const edgeModes = appearanceConfig.edge_modes || {};
    EDGE_MODE_CONFIG = {
        resolution: edgeModes.resolution || { internal: '#4dd4ff', external: '#ff6b6b', unresolved: '#9aa0a6', unknown: '#666666' },
        weight: edgeModes.weight || { hue_min: 210, hue_max: 50, saturation: 45, lightness: 42 },
        confidence: edgeModes.confidence || { hue_min: 20, hue_max: 120, saturation: 45, lightness: 44 },
        width: edgeModes.width || { base: 0.6, weight_scale: 2.0, confidence_scale: 1.5 },
        dim: edgeModes.dim || { interfile_factor: 0.25 },
        opacity: (typeof edgeModes.opacity === 'number') ? edgeModes.opacity : 0.08
    };

    FILE_COLOR_CONFIG = Object.assign({}, FILE_COLOR_CONFIG, appearanceConfig.file_color || {});
    // Token value 0.08 from appearance.tokens.json:202, fallback only if token system fails
    EDGE_DEFAULT_OPACITY =
        (typeof EDGE_MODE_CONFIG.opacity === 'number') ? EDGE_MODE_CONFIG.opacity : 0.08;
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
    EDGE_COLOR_CONFIG = {
        default: edgeColor.default || '#333333',
        calls: edgeColor.calls || '#4dd4ff',
        contains: edgeColor.contains || '#00ff9d',
        uses: edgeColor.uses || '#ffb800',
        imports: edgeColor.imports || '#9aa0a6',
        inherits: edgeColor.inherits || '#ff6b6b'
    };

    // Initial Filter: show full graph
    const filtered = filterGraph(data, CURRENT_DENSITY, ACTIVE_DATAMAPS, VIS_FILTERS);

    // ═══════════════════════════════════════════════════════════════════
    // DATA PREP FOR ANIMATIONS: Assign file indices for wave patterns
    // ═══════════════════════════════════════════════════════════════════
    const fileMap = new Map();
    let nextFileIdx = 0;
    filtered.nodes.forEach(node => {
        // Extract filename from ID (assuming file path is in ID or explicit file prop)
        const file = node.file || (node.id.includes('/') ? node.id.split(':')[0] : 'unknown');
        if (!fileMap.has(file)) fileMap.set(file, nextFileIdx++);
        node.file_idx = fileMap.get(file);
    });

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
            // ═══════════════════════════════════════════════════════════════════
            // GROUP DRAG: Move all selected nodes together, maintaining offsets
            // Note: onNodeDragStart doesn't exist - detect start via flag
            // ═══════════════════════════════════════════════════════════════════
            .onNodeDrag((node, translate) => {
                // Only handle group drag if multiple nodes selected and this node is selected
                if (SELECTED_NODE_IDS.size > 1 && SELECTED_NODE_IDS.has(node.id)) {
                    // First drag frame: store relative offsets
                    if (!window._groupDragActive) {
                        window._groupDragActive = true;
                        window._groupDragOffsets = new Map();
                        const nodes = Graph.graphData().nodes;
                        nodes.forEach(n => {
                            if (SELECTED_NODE_IDS.has(n.id) && n.id !== node.id) {
                                window._groupDragOffsets.set(n.id, {
                                    dx: (n.x || 0) - (node.x || 0),
                                    dy: (n.y || 0) - (node.y || 0),
                                    dz: (n.z || 0) - (node.z || 0)
                                });
                            }
                        });
                    }
                    // Move all other selected nodes with their offsets
                    if (window._groupDragOffsets) {
                        const nodes = Graph.graphData().nodes;
                        nodes.forEach(n => {
                            const offset = window._groupDragOffsets.get(n.id);
                            if (offset) {
                                n.fx = node.x + offset.dx;
                                n.fy = node.y + offset.dy;
                                n.fz = node.z + offset.dz;
                            }
                        });
                    }
                }
            })
            .onNodeDragEnd(node => {
                // Clear group drag state
                window._groupDragActive = false;
                window._groupDragOffsets = null;
                // Fix all selected nodes at their final positions
                if (SELECTED_NODE_IDS.size > 0) {
                    const nodes = Graph.graphData().nodes;
                    nodes.forEach(n => {
                        if (SELECTED_NODE_IDS.has(n.id)) {
                            n.fx = n.x; n.fy = n.y; n.fz = n.z;
                        }
                    });
                }
            })
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
    // STARFIELD REMOVED - Nodes ARE the stars
    // Rationale: Adding background dots creates visual confusion with actual data nodes.
    // The cosmos metaphor works better when the data itself forms the starfield.
    // =================================================================

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

    // Test 1: Core UI structure (dual-sidebar layout)

    // Main layout containers
    test('header-exists', !!document.getElementById('header'));
    test('left-sidebar-exists', !!document.getElementById('left-sidebar'));
    test('right-sidebar-exists', !!document.getElementById('right-sidebar'));
    test('graph-container-exists', !!document.getElementById('3d-graph'));

    // Header stats
    test('stat-nodes-exists', !!document.getElementById('stat-nodes'));
    test('stat-edges-exists', !!document.getElementById('stat-edges'));
    test('target-name-exists', !!document.getElementById('target-name'));

    // Left sidebar configuration sections
    test('section-node-config-exists', !!document.getElementById('section-node-config'));
    test('section-edge-config-exists', !!document.getElementById('section-edge-config'));
    test('section-layout-exists', !!document.getElementById('section-layout'));
    test('section-physics-exists', !!document.getElementById('section-physics'));
    test('section-filters-exists', !!document.getElementById('section-filters'));
    test('section-actions-exists', !!document.getElementById('section-actions'));

    // Left sidebar action buttons
    test('btn-reset-exists', !!document.getElementById('btn-reset'));
    test('btn-screenshot-exists', !!document.getElementById('btn-screenshot'));
    test('btn-2d-exists', !!document.getElementById('btn-2d'));
    test('btn-freeze-exists', !!document.getElementById('btn-freeze'));

    // Right sidebar panels
    test('hover-panel-exists', !!document.getElementById('hover-panel'));
    test('section-schemes-exists', !!document.getElementById('section-schemes'));
    test('section-color-exists', !!document.getElementById('section-color'));

    // Selection elements
    test('selection-count-exists', !!document.getElementById('selection-count'));
    test('selection-list-exists', !!document.getElementById('selection-list'));

    // Stats panel
    test('stats-nodes-exists', !!document.getElementById('stats-nodes'));
    test('stats-edges-exists', !!document.getElementById('stats-edges'));

    // Performance HUD
    test('perf-hud-exists', !!document.getElementById('perf-hud'));
    test('perf-fps-exists', !!document.getElementById('perf-fps'));

    // Test 1b: Color mode buttons exist
    const colorButtons = document.querySelectorAll('.color-btn[data-preset]');
    test('color-mode-buttons-exist', colorButtons.length >= 4);

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

    // Test 2: Header stats populated (stat-* elements - these are set early)
    const headerNodes = document.getElementById('stat-nodes');
    const headerEdges = document.getElementById('stat-edges');
    test('header-nodes-populated', headerNodes && headerNodes.textContent !== '0');
    test('header-edges-populated', headerEdges && headerEdges.textContent !== '0');

    // Test 3: Data integrity
    test('nodes-count-positive', data.nodes && data.nodes.length > 0);
    test('links-count-positive', data.links && data.links.length > 0);
    test('graph-initialized', !!window.Graph);

    // Test 4: Controls config loaded
    test('controls-config-exists', !!data.controls);
    test('appearance-config-exists', !!data.appearance);
    test('physics-config-exists', !!data.physics);

    // Test 5: Initial state correct
    const physicsCharge = document.getElementById('physics-charge');
    test('physics-slider-has-value', physicsCharge && physicsCharge.value !== undefined);
    test('3d-mode-default', IS_3D === true);

    // Test 6: VIS_STATE module loaded
    test('vis-state-module-exists', typeof VIS_STATE !== 'undefined');
    test('vis-state-has-applyState', typeof VIS_STATE?.applyState === 'function');
    test('vis-state-has-getState', typeof VIS_STATE?.getState === 'function');

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

// TIER_ALIASES, normalizeTier, getNodeTier, getNodeAtomFamily, normalizeRingValue,
// getNodeRing, getNodeLayer, getNodeEffect - provided by node-accessors.js module

// getNodeColorByMode, getSubsystem, getPhase, getFileType, getRoleCategory, applyNodeColors - MOVED TO modules/node-helpers.js
// normalize - MOVED TO modules/utils.js

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
    let visibleNodes = allNodes.filter(n => (n.val ?? 1) >= minVal);

    if (datamapSet && datamapSet.size > 0) {
        visibleNodes = visibleNodes.filter(n => {
            for (const id of datamapSet) {
                const config = DATAMAP_INDEX[id];
                if (config && datamapMatches(n, config)) return true;
            }
            return false;
        });
    }

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
// LAYOUT STABILITY: saveNodePositions, restoreNodePositions, freezeLayout, unfreezeLayout, resetLayout - MOVED TO modules/layout-helpers.js
// showModeToast - MOVED TO modules/tooltips.js
// getLinkEndpointId, getFileTarget - MOVED TO modules/layout-helpers.js
// stableOffset - MOVED TO modules/utils.js

// buildFileGraph - MOVED TO modules/file-viz.js (shim delegates to FILE_VIZ.buildFileGraph)
// captureFileNodePositions - MOVED TO modules/file-viz.js (shim delegates to FILE_VIZ.captureFileNodePositions)

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

    // HudLayoutManager.init() - REMOVED: Now handled by LAYOUT.init() in main.js
    // The LAYOUT module is initialized via initializeModules() to avoid double-init

    // Initialize Command Bar and Floating Panels
    initCommandBar();

    // Initialize Selection Detail Modal
    initSelectionModal();

    // Initialize Node & Edge Config Controls (PRIME SECTIONS)
    setupConfigControls();

    // Render color-coded legends with counts
    renderAllLegends();

    // Flow mode button (attached here for proper DOM timing)
    const btnFlow = document.getElementById('btn-flow');
    if (btnFlow) btnFlow.onclick = () => toggleFlowMode();
}

/**
 * =================================================================
 * setupConfigControls: Initialize NODE CONFIG and EDGE CONFIG panels
 * =================================================================
 * These are the "prime position" controls at the top of the sidebar
 */
function setupConfigControls() {
    // Helper: Bind slider with value display
    const bindSlider = (id, valueId, onChange, decimals = 1) => {
        const slider = document.getElementById(id);
        const valueEl = document.getElementById(valueId);
        if (!slider) return;
        slider.addEventListener('input', () => {
            const val = parseFloat(slider.value);
            if (valueEl) valueEl.textContent = decimals === 0 ? val.toString() : val.toFixed(decimals);
            onChange(val);
        });
    };

    // Helper: Bind toggle switch
    const bindToggle = (id, initialState, onChange) => {
        const toggle = document.getElementById(id);
        if (!toggle) return;
        if (initialState) toggle.classList.add('active');
        else toggle.classList.remove('active');
        toggle.addEventListener('click', () => {
            const isActive = toggle.classList.toggle('active');
            onChange(isActive);
        });
    };

    // Helper: Bind button group (radio-like selection)
    const bindButtonGroup = (container, dataAttr, onChange) => {
        const buttons = container.querySelectorAll(`[${dataAttr}]`);
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                onChange(btn.getAttribute(dataAttr));
            });
        });
    };

    // ═══════════════════════════════════════════════════════════════════
    // NODE CONFIG
    // ═══════════════════════════════════════════════════════════════════

    // Size Mode Selector
    const nodeCfg = document.getElementById('section-node-config');
    if (nodeCfg) {
        bindButtonGroup(nodeCfg, 'data-size-mode', (mode) => {
            APPEARANCE_STATE.sizeMode = mode;
            applyNodeSizeMode(mode);
            console.log('[CONFIG] Size mode:', mode);
        });
    }

    // Node Base Size
    bindSlider('cfg-node-size', 'cfg-node-size-val', (val) => {
        APPEARANCE_STATE.nodeScale = val;
        applyNodeSizeMode(APPEARANCE_STATE.sizeMode || 'uniform');
    });

    // Node Opacity
    bindSlider('cfg-node-opacity', 'cfg-node-opacity-val', (val) => {
        APPEARANCE_STATE.nodeOpacity = val;
        if (Graph) Graph.nodeOpacity(val);
    });

    // Node Resolution (sphere segments)
    bindSlider('cfg-node-res', 'cfg-node-res-val', (val) => {
        APPEARANCE_STATE.nodeResolution = Math.round(val);
        if (Graph) Graph.nodeResolution(Math.round(val));
    }, 0);

    // Label Size
    bindSlider('cfg-label-size', 'cfg-label-size-val', (val) => {
        APPEARANCE_STATE.labelSize = val;
        if (Graph && APPEARANCE_STATE.showLabels) {
            Graph.nodeLabel(node => val > 0.2 ? (node.name || node.id) : null);
        }
    });

    // Show Labels Toggle
    bindToggle('cfg-toggle-labels', APPEARANCE_STATE.showLabels, (active) => {
        APPEARANCE_STATE.showLabels = active;
        if (Graph) Graph.nodeLabel(node => active ? (node.name || node.id) : null);
    });

    // Highlight Selected Toggle
    bindToggle('cfg-toggle-highlight', APPEARANCE_STATE.highlightSelected, (active) => {
        APPEARANCE_STATE.highlightSelected = active;
        if (typeof updateSelectionVisuals === 'function') updateSelectionVisuals();
    });

    // Pulse Animation Toggle
    bindToggle('cfg-toggle-pulse', false, (active) => {
        APPEARANCE_STATE.pulseAnimation = active;
        console.log('[CONFIG] Pulse animation:', active ? 'ON' : 'OFF');
    });

    // 3D Depth Shading Toggle
    bindToggle('cfg-toggle-depth', true, (active) => {
        APPEARANCE_STATE.depthShading = active;
        console.log('[CONFIG] Depth shading:', active ? 'ON' : 'OFF');
    });

    // ═══════════════════════════════════════════════════════════════════
    // EDGE CONFIG - Enhanced with better visibility and flow animation
    // ═══════════════════════════════════════════════════════════════════

    // Edge Style Selector
    const edgeCfg = document.getElementById('section-edge-config');
    if (edgeCfg) {
        bindButtonGroup(edgeCfg, 'data-edge-style', (style) => {
            APPEARANCE_STATE.edgeStyle = style;
            applyEdgeStyle(style);
            console.log('[CONFIG] Edge style:', style);
        });
    }

    // Edge Opacity - ENHANCED: Higher default for visibility
    bindSlider('cfg-edge-opacity', 'cfg-edge-opacity-val', (val) => {
        APPEARANCE_STATE.edgeOpacity = val;
        // Use applyEdgeMode to ensure consistent function-based opacity
        if (typeof applyEdgeMode === 'function') applyEdgeMode();
    });

    // Edge Width - ENHANCED: Thicker default
    bindSlider('cfg-edge-width', 'cfg-edge-width-val', (val) => {
        APPEARANCE_STATE.edgeWidth = val;
        // Use applyEdgeMode to ensure consistent function-based width
        if (typeof applyEdgeMode === 'function') applyEdgeMode();
    });

    // Edge Curvature - Direct Graph API (not handled by EDGE module)
    bindSlider('cfg-edge-curve', 'cfg-edge-curve-val', (val) => {
        APPEARANCE_STATE.edgeCurvature = val;
        if (Graph) Graph.linkCurvature(val);
    });

    // Particle Speed - For FLOW visualization
    bindSlider('cfg-particle-speed', 'cfg-particle-speed-val', (val) => {
        APPEARANCE_STATE.particleSpeed = val;
        if (Graph) Graph.linkDirectionalParticleSpeed(val);
    }, 3);

    // Particle Density - For FLOW visualization
    bindSlider('cfg-particle-count', 'cfg-particle-count-val', (val) => {
        APPEARANCE_STATE.particleCount = Math.round(val);
        if (Graph) Graph.linkDirectionalParticles(Math.round(val));
    }, 0);

    // Show Arrows Toggle
    bindToggle('cfg-toggle-arrows', APPEARANCE_STATE.showArrows, (active) => {
        APPEARANCE_STATE.showArrows = active;
        if (Graph) {
            Graph.linkDirectionalArrowLength(active ? 6 : 0);
            Graph.linkDirectionalArrowRelPos(0.9);
        }
    });

    // Gradient Colors Toggle
    bindToggle('cfg-toggle-gradient', APPEARANCE_STATE.gradientEdges, (active) => {
        APPEARANCE_STATE.gradientEdges = active;
        if (typeof applyEdgeMode === 'function') applyEdgeMode();
    });

    // Highlight Edges on Hover Toggle
    bindToggle('cfg-toggle-edge-hover', true, (active) => {
        APPEARANCE_STATE.edgeHoverHighlight = active;
    });

    // ═══════════════════════════════════════════════════════════════════
    // Section Collapse Handlers
    // ═══════════════════════════════════════════════════════════════════
    document.querySelectorAll('.section-header[data-section]').forEach(header => {
        header.addEventListener('click', () => {
            const sectionId = header.dataset.section;
            const content = document.getElementById(`section-${sectionId}`);
            if (!content) return;
            const isCollapsed = header.classList.toggle('collapsed');
            content.classList.toggle('collapsed', isCollapsed);
        });
    });

    console.log('[CONFIG] Node & Edge config controls initialized');
}

// applyNodeSizeMode - MOVED TO modules/node-helpers.js

/**
 * Apply edge style - controls edge rendering mode
 */
function applyEdgeStyle(style) {
    if (!Graph) return;
    const opacity = APPEARANCE_STATE.edgeOpacity || 0.4;
    const speed = APPEARANCE_STATE.particleSpeed || 0.01;
    const count = APPEARANCE_STATE.particleCount || 0;

    switch (style) {
        case 'solid':
            Graph.linkLineDash(null);
            Graph.linkOpacity(opacity);
            Graph.linkDirectionalParticles(count);
            break;
        case 'dashed':
            Graph.linkLineDash([4, 4]);
            Graph.linkOpacity(opacity);
            Graph.linkDirectionalParticles(count);
            break;
        case 'particle':
            // Particle mode: dim lines, bright particles for flow effect
            Graph.linkLineDash(null);
            Graph.linkOpacity(Math.max(0.1, opacity * 0.3));
            Graph.linkDirectionalParticles(Math.max(4, count));
            Graph.linkDirectionalParticleSpeed(speed);
            Graph.linkDirectionalParticleWidth(3);
            Graph.linkDirectionalParticleColor(link => {
                // Use source node color for particles
                if (link.source && typeof link.source === 'object') {
                    return link.source.__threeObj?.material?.color?.getStyle() || '#00d4ff';
                }
                return '#00d4ff';
            });
            break;
    }
}

// UIManager - provided by ui-manager.js module (window.UI_MANAGER, window.UIManager)

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

// Tooltip state - shared with modules/tooltips.js
const TOOLTIP_STATE = { visible: false, currentKey: null, element: null, hideTimeout: null };

// initTooltips, showTopoTooltip, hideTopoTooltip - MOVED TO modules/tooltips.js

// ZONES define which levels belong to which visual band
const LEVEL_ZONES = {
    'COSMOLOGICAL': { levels: ['L12', 'L11', 'L10', 'L9', 'L8'], opacity: 0.2, blur: true },
    'ARCHITECTURAL': { levels: ['L7', 'L6', 'L5', 'L4'], opacity: 0.6, blur: false },
    'SEMANTIC': { levels: ['L3', 'L2', 'L1'], opacity: 1.0, blur: false },        // Primary focus
    'SYNTACTIC': { levels: ['L0'], opacity: 0.8, blur: false },                   // Event horizon
    'PHYSICAL': { levels: ['L-1', 'L-2', 'L-3'], opacity: 0.4, blur: true }
};

// ═══════════════════════════════════════════════════════════════════════
// getTopoColor - MOVED TO modules/color-helpers.js


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
    }
    // NOTE: Color schemes (viridis, plasma, thermal, etc.) are now in color-engine.js schemePaths
    // Access via COLOR.listSchemes(), COLOR.applyScheme(), COLOR.getSchemeColor()
};

// ═══════════════════════════════════════════════════════════════════════
// LAYOUT PRESETS - MOVED TO modules/animation.js
// ═══════════════════════════════════════════════════════════════════════
// LAYOUT_PRESETS, STAGGER_PATTERNS, CURRENT_LAYOUT, LAYOUT_ANIMATION_ID,
// LAYOUT_TIME, CURRENT_STAGGER_PATTERN, applyLayoutPreset, cycleStaggerPattern,
// startLayoutMotion, startFlockSimulation, groupNodesByTier
// All now provided by ANIM module with O(n) spatial hashing (fixes ARCH-002)








// Count nodes by tier and family







// Hermite basis functions for C¹ continuous color interpolation




// ═══════════════════════════════════════════════════════════════









// OKLCH-inspired colors (converted to linear RGB for Three.js)
// Chaos (bottom): OKLCH(0.25, 0.12, 240) ≈ deep cosmic blue




// ═══════════════════════════════════════════════════════════════


























// clearAllFilters - MOVED TO modules/visibility.js







// collectCounts, buildCheckboxRow, buildFilterGroup - MOVED TO modules/ui-builders.js
// resolveDefaults - MOVED TO modules/utils.js
// normalizeDatamapConfig, resolveDatamapConfigs, datamapMatches - MOVED TO modules/datamap.js
// buildDatamapToggle, buildExclusiveOptions - MOVED TO modules/ui-builders.js

// ═══════════════════════════════════════════════════════════════════════════
// APPEARANCE SLIDERS - Orchestration layer (uses UI_BUILDERS for pure UI)
// This function owns the business logic: what sliders exist, their values,
// and what happens when they change. UI_BUILDERS.buildAppearanceSliders
// handles the DOM creation.
// ═══════════════════════════════════════════════════════════════════════════

function buildAppearanceSliders(containerId, sliderConfigs) {

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

    // Use UI_BUILDERS for pure DOM creation (decoupled architecture)
    // Each sliderDef has its own onChange handler - business logic stays here
    UI_BUILDERS.buildAppearanceSliders(containerId, sliderDefs);
}

// ═══════════════════════════════════════════════════════════════════════
// PHYSICS CONTROLS - Real-time force simulation adjustment
// ═══════════════════════════════════════════════════════════════════════
const PHYSICS_STATE = {
    charge: -120,
    linkDistance: 50,
    centerStrength: 0.05,
    velocityDecay: 0.4
};

const PHYSICS_PRESETS = {
    default: { charge: -120, linkDistance: 50, centerStrength: 0.05, velocityDecay: 0.4, label: 'DEFAULT' },
    tight: { charge: -80, linkDistance: 30, centerStrength: 0.1, velocityDecay: 0.5, label: 'TIGHT' },
    loose: { charge: -200, linkDistance: 80, centerStrength: 0.02, velocityDecay: 0.3, label: 'LOOSE' },
    explosive: { charge: -400, linkDistance: 120, centerStrength: 0.01, velocityDecay: 0.2, label: 'EXPLOSIVE' }
};

// applyPhysicsState, applyPhysicsPreset, updatePhysicsSliders, buildPhysicsControls - MOVED TO modules/physics.js

// updateBackgroundBrightness, applyMetadataVisibility - MOVED TO modules/visibility.js

// Deprecated setupSidebar - replaced by UIManager
// Deprecated buildDatamapControls - replaced by UIManager


// ═══════════════════════════════════════════════════════════════
// PRESET BUTTONS - Quick visualization mode selection (Tier, Family, etc.)
// Uses VIS_STATE for unified state management
// ═══════════════════════════════════════════════════════════════
const presetGrid = document.getElementById('dock-presets');
const presetBtnGrid = document.getElementById('preset-grid');
if (presetBtnGrid) {
    presetBtnGrid.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const presetKey = btn.dataset.preset;

            // Use VIS_STATE for unified state management
            if (typeof VIS_STATE !== 'undefined') {
                VIS_STATE.applyPreset(presetKey);
                return;
            }

            // Fallback for when VIS_STATE not loaded
            const preset = VIS_PRESETS[presetKey];
            if (!preset) return;

            presetBtnGrid.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.scheme-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            APPEARANCE_STATE.currentPreset = presetKey;
            APPEARANCE_STATE.colorMode = preset.colorBy;

            setNodeColorMode(preset.colorBy);

            const edgeModes = { 'type': 'gradient-tier', 'weight': 'weight', 'resolution': 'gradient-file' };
            EDGE_MODE = edgeModes[preset.edgeBy] || preset.edgeBy || 'gradient-tier';
            applyEdgeMode();

            if (presetKey === 'flow') {
                if (!flowMode && typeof toggleFlowMode === 'function') toggleFlowMode();
            } else if (flowMode && typeof disableFlowMode === 'function') {
                disableFlowMode();
            }

            if (typeof window.refreshGradientEdgeColors === 'function') {
                window.refreshGradientEdgeColors();
            }

            if (typeof renderAllLegends === 'function') {
                renderAllLegends();
            }

            console.log('[Preset] Applied:', preset.name, '| colorBy:', preset.colorBy, '| edgeBy:', preset.edgeBy);
        });
    });
}

// ═══════════════════════════════════════════════════════════════
// NOTE: Color scheme buttons are now handled by sidebar.js via SIDEBAR.initSchemeNavigator()
// The 33 named schemes (viridis, plasma, thermal, etc.) are defined in color-engine.js schemePaths
// ═══════════════════════════════════════════════════════════════

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
    { label: 'FILE', value: 'file' },
    { label: 'ATOM', value: 'atom' },
    { label: 'COMPLEXITY', value: 'complexity' },
    { label: 'CHURN', value: 'churn' }
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
buildPhysicsControls('physics-sliders');  // Physics/forces controls

applyMetadataVisibility();
updateBackgroundBrightness();
refreshGraph();

// setupCollapsibleSections - MOVED TO modules/visibility.js

// setupReport, setupAIInsights, setupMetrics - MOVED TO modules/report.js

// escapeHtml - MOVED TO modules/utils.js

// setupHudFade, updateHudStats - MOVED TO modules/hud.js

// showToast - MOVED TO modules/tooltips.js
// updateDatamapControls - MOVED TO modules/datamap.js

// toggleDimensions, setupDimensionToggle, animateDimensionChange - MOVED TO modules/dimension.js

// stableSeed, stableZ - MOVED TO modules/utils.js

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

// FILE_HUE_MAP, buildFileHueMap - provided by edge-system.js module

// Get node tier value (0=T0, 1=T1, 2=T2)
// getNodeTierValue, getNodeDepth, getSemanticSimilarity - MOVED TO modules/node-helpers.js

// interpolateColor, applyColorTweaks, oklchToSrgb, oklchColor - MOVED TO modules/color-engine.js
// Use COLOR.interpolate() and COLOR.get() instead

// getGradientEdgeColor - MOVED TO modules/edge-system.js
// clamp01, clampValue - MOVED TO modules/utils.js
// hslColor REMOVED - Using OKLCH Native via Color.interpolate
// parseOklchString - MOVED TO modules/utils.js
// normalizeColorInput, toColorNumber - MOVED TO modules/color-helpers.js

// updateEdgeRanges, refreshNodeFileIndex, getLinkFileIdx - MOVED TO modules/edge-system.js
// (shims delegate to EDGE.updateRanges, EDGE.refreshNodeFileIndex; getLinkFileIdx is internal)

// normalizeMetric - MOVED TO modules/utils.js
// getEdgeColor, getEdgeWidth, applyEdgeMode, cycleEdgeMode, setEdgeMode - MOVED TO modules/edge-system.js
// (backward compat shims in edge-system.js)

// Datamap toggles are wired in buildDatamapControls().
const btnReport = document.getElementById('btn-report');
if (btnReport) {
    btnReport.onclick = () => {
        const panel = document.getElementById('report-panel');
        const btn = document.getElementById('btn-report');
        if (!panel) return;
        const isOpen = panel.style.display === 'block';
        panel.style.display = isOpen ? 'none' : 'block';
        btn.classList.toggle('active', !isOpen);
    };
}

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

// setStarsVisible, STARS_STORAGE_KEY, stars toggle binding - MOVED TO modules/stars.js
// Call STARS.init() to initialize (done in modules/main.js)

// Reset Layout button - explicitly re-run physics
const btnResetLayout = document.getElementById('btn-reset-layout');
if (btnResetLayout) {
    btnResetLayout.onclick = () => resetLayout();
}

// Hints toggle - enable/disable mode toasts
const btnHints = document.getElementById('btn-hints');
if (btnHints) {
    btnHints.onclick = () => {
        HINTS_ENABLED = !HINTS_ENABLED;
        btnHints.classList.toggle('active', HINTS_ENABLED);
        if (HINTS_ENABLED) {
            showModeToast('Hints enabled');
        }
    };
}

const btnEdgeMode = document.getElementById('btn-edge-mode');
if (btnEdgeMode) {
    btnEdgeMode.onclick = () => cycleEdgeMode();
}

// ====================================================================
// FLOW MODE: Markov Chain Visualization (Token-Driven)
// ====================================================================
// flowMode hoisted to top
let originalLinkWidths = new Map();
let highEntropyNodes = new Set();
// FLOW_CONFIG is set in initGraph() from THE REMOTE CONTROL tokens

// getFlowPresetColor, getFlowPresetValue - MOVED TO modules/flow.js

// FLOW_PRESETS, currentFlowPreset - MOVED TO modules/flow.js

// toggleFlowMode, disableFlowMode, applyFlowVisualization, clearFlowVisualization - MOVED TO modules/flow.js

// setDatamap, setNodeColorMode, applyDatamap - MOVED TO modules/datamap.js

// ====================================================================
// FILE BOUNDARIES & HOVER SYSTEM
// ====================================================================
// NOTE: fileBoundaryMeshes, fileMode, fileVizMode, etc. declared at top of file

// hashToUnit - MOVED TO modules/utils.js
// getFileHue, getFileColor - MOVED TO modules/color-helpers.js
// updateHoverPanel, handleNodeHover, handleNodeClick - MOVED TO modules/hover.js
// buildDatasetKey - MOVED TO modules/utils.js
// loadGroups, saveGroups, getNextGroupColor, getGroupById, getPrimaryGroupForNode - MOVED TO modules/groups.js
// renderGroupList, updateGroupButtonState, createGroupFromSelection - MOVED TO modules/groups.js

// getSelectedNodes, setSelection, toggleSelection, clearSelection, maybeClearSelection - MOVED TO modules/selection.js
// Use SELECT.getSelectedNodes(), SELECT.set(), SELECT.toggle(), SELECT.clear(), SELECT.maybeClear()
// Shims in selection.js provide global function names for backward compatibility


function handleNodeHover(node, data) {
    const filePanel = document.getElementById('file-panel');
    HOVERED_NODE = node || null;

    // Always update hover panel (separate from file panel)
    updateHoverPanel(node);

    // Guard: file-panel may not exist in minimal template
    if (!filePanel) return;

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

    // Update panel content (with null checks for minimal template)
    const setEl = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };
    setEl('file-name', fileInfo.file_name || 'unknown');
    setEl('file-cohesion', `Cohesion: ${(fileInfo.cohesion * 100).toFixed(0)}%`);
    setEl('file-purpose', fileInfo.purpose || '--');
    setEl('file-atom-count', fileInfo.atom_count || 0);
    setEl('file-lines', fileInfo.line_range ? `${fileInfo.line_range[0]}-${fileInfo.line_range[1]}` : '--');
    setEl('file-classes', (fileInfo.classes || []).join(', ') || 'none');
    setEl('file-functions', 'Functions: ' + ((fileInfo.functions || []).slice(0, 8).join(', ') || 'none'));

    // Show code preview from node body
    const code = node.body || '// no source available';
    setEl('file-code', code);

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


// ====================================================================
// FILE MODE HANDLERS
// ====================================================================

// setFileModeState - MOVED TO modules/file-viz.js (shim delegates to FILE_VIZ.setEnabled)

const btnFiles = document.getElementById('btn-files');
if (btnFiles) btnFiles.onclick = () => setFileModeState(!fileMode);

// COLOR mode - atoms colored by file
const btnFileColor = document.getElementById('btn-file-color');
if (btnFileColor) btnFileColor.onclick = () => setFileVizMode('color');

// HULLS mode - draw boundary spheres
const btnFileHulls = document.getElementById('btn-file-hulls');
if (btnFileHulls) btnFileHulls.onclick = () => setFileVizMode('hulls');

// CLUSTER mode - force clustering by file
const btnFileCluster = document.getElementById('btn-file-cluster');
if (btnFileCluster) btnFileCluster.onclick = () => setFileVizMode('cluster');

// MAP mode - show file nodes
const btnFileMap = document.getElementById('btn-file-map');
if (btnFileMap) btnFileMap.onclick = () => setFileVizMode('map');

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
const btnExpandInline = document.getElementById('btn-expand-inline');
if (btnExpandInline) {
    btnExpandInline.onclick = () => {
        FILE_EXPAND_MODE = 'inline';
        updateExpandButtons();
        if (GRAPH_MODE === 'hybrid') {
            refreshGraph();
        }
    };
}

const btnExpandDetach = document.getElementById('btn-expand-detach');
if (btnExpandDetach) {
    btnExpandDetach.onclick = () => {
        FILE_EXPAND_MODE = 'detach';
        updateExpandButtons();
        if (GRAPH_MODE === 'hybrid') {
            refreshGraph();
        }
    };
}


// setFileVizMode - MOVED TO modules/file-viz.js (shim delegates to FILE_VIZ.setMode)

// applyFileVizMode - MOVED TO modules/file-viz.js (shim delegates to FILE_VIZ.apply)

// scheduleHullRedraw - MOVED TO modules/file-viz.js (shim delegates to FILE_VIZ.scheduleHullRedraw)

// applyFileColors - MOVED TO modules/file-viz.js (shim delegates to FILE_VIZ.applyColors)

// clearFileBoundaries - MOVED TO modules/file-viz.js (shim delegates to FILE_VIZ.clearBoundaries)

// Moved here to avoid temporal dead zone issue
let fileCohesionActive = false;

// clearAllFileModes - MOVED TO modules/file-viz.js (shim delegates to FILE_VIZ.clearAllModes)

// applyClusterForce, applyFileCohesion, clearFileCohesion - MOVED TO modules/file-viz.js

// ════════════════════════════════════════════════════════════════════════
// SURFACE PARITY HANDLERS - Architectural Enforcements
// ════════════════════════════════════════════════════════════════════════

// Panel Handlers - use togglePanel('view') etc. or PANELS.toggle('view')
// togglePanelView/Filter/Style/Settings - simplified via modules/panels.js


// Action Handlers
function handleCmdFlow() { toggleFlowMode(); }
function handleCmd3d() { toggleDimensions(); }

// PanelManager - provided by panels.js module (window.PANEL_DRAG, window.PanelManager)

// =================================================================
// THEME SWITCHING - MOVED TO modules/theme.js
// setTheme, getTheme, getAvailableThemes, cycleTheme, initTheme

// Initialize theme on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Small delay to ensure CSS vars are loaded
        setTimeout(initTheme, 50);
    });
} else {
    setTimeout(initTheme, 50);
}

// Expose theme functions globally
window.setTheme = setTheme;
window.getTheme = getTheme;
window.getAvailableThemes = getAvailableThemes;
window.cycleTheme = cycleTheme;
window.THEME_CONFIG = THEME_CONFIG;

// Expose filtering/graph globals for module access
window.VIS_FILTERS = VIS_FILTERS;
window.refreshGraph = refreshGraph;
