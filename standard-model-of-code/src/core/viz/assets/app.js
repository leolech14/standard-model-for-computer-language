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

// ═══════════════════════════════════════════════════════════════════════
// REAL-TIME PERFORMANCE MONITOR - Actual frame delivery diagnostics
// ═══════════════════════════════════════════════════════════════════════
const PERF_MONITOR = {
    enabled: true,
    fps: 0,
    frameTime: 0,
    lastFrameTime: 0,
    frameTimes: [],
    maxFrames: 60,
    renderCalls: 0,
    droppedFrames: 0,
    lastSecond: 0,
    framesThisSecond: 0,
    hudElement: null,

    init() {
        if (!this.enabled) return;
        // Create HUD element
        this.hudElement = document.createElement('div');
        this.hudElement.id = 'perf-hud';
        this.hudElement.style.cssText = `
            position: fixed; top: 10px; right: 10px; z-index: 99999;
            background: rgba(0,0,0,0.85); color: #0f0; font-family: monospace;
            font-size: 11px; padding: 8px 12px; border-radius: 4px;
            border: 1px solid #333; min-width: 140px; pointer-events: none;
        `;
        document.body.appendChild(this.hudElement);
        this.startMonitoring();
    },

    startMonitoring() {
        const monitor = () => {
            const now = performance.now();

            // Calculate frame time
            if (this.lastFrameTime > 0) {
                this.frameTime = now - this.lastFrameTime;
                this.frameTimes.push(this.frameTime);
                if (this.frameTimes.length > this.maxFrames) this.frameTimes.shift();

                // Detect dropped frames (>50ms = <20fps)
                if (this.frameTime > 50) this.droppedFrames++;
            }
            this.lastFrameTime = now;

            // Calculate FPS every second
            const second = Math.floor(now / 1000);
            if (second !== this.lastSecond) {
                this.fps = this.framesThisSecond;
                this.framesThisSecond = 0;
                this.lastSecond = second;
            }
            this.framesThisSecond++;

            // Update HUD
            this.updateHUD();
            requestAnimationFrame(monitor);
        };
        requestAnimationFrame(monitor);
    },

    updateHUD() {
        if (!this.hudElement) return;
        const avgFrameTime = this.frameTimes.length > 0
            ? (this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length).toFixed(1)
            : '0.0';

        // Color code FPS
        let fpsColor = '#0f0';  // Green = good
        if (this.fps < 30) fpsColor = '#ff0';  // Yellow = warning
        if (this.fps < 15) fpsColor = '#f00';  // Red = bad

        // Animation state
        const animating = LAYOUT_ANIMATION_ID ? '▶ ANIMATING' : '■ IDLE';
        const animColor = LAYOUT_ANIMATION_ID ? '#0ff' : '#666';

        this.hudElement.innerHTML = `
            <div style="color:${fpsColor};font-size:14px;font-weight:bold">${this.fps} FPS</div>
            <div>Frame: ${avgFrameTime}ms</div>
            <div>Dropped: <span style="color:${this.droppedFrames > 10 ? '#f00' : '#0f0'}">${this.droppedFrames}</span></div>
            <div style="color:${animColor}">${animating}</div>
            <div style="font-size:9px;color:#666;margin-top:4px">Pattern: ${CURRENT_STAGGER_PATTERN || 'none'}</div>
        `;
    },

    // Call this to log a resistance point
    logResistance(location, duration) {
        if (duration > 16) {
            console.warn(`[PERF RESISTANCE] ${location}: ${duration.toFixed(1)}ms (>${Math.floor(duration / 16.67)} frames)`);
        }
    }
};

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
// FLOATING PANEL CONTROL SYSTEM
// =====================================================================
// openPanel, closePanel, togglePanel - MOVED TO modules/panels.js
// (backward compat shims in panels.js)

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
    test('section-schemes-exists', !!document.getElementById('section-schemes'));

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
    // test('btn-stars-exists', ...);  // REMOVED - starfield feature deleted
    test('btn-dimensions-exists', !!document.getElementById('btn-dimensions'));

    // Graph state - STARFIELD test removed

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
        if (Graph) Graph.linkOpacity(val);
    });

    // Edge Width - ENHANCED: Thicker default
    bindSlider('cfg-edge-width', 'cfg-edge-width-val', (val) => {
        APPEARANCE_STATE.edgeWidth = val;
        if (Graph) Graph.linkWidth(link => Math.max(0.5, (link.width || 1) * val));
    });

    // Edge Curvature
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

        // Stars Toggle - REMOVED (starfield feature deleted)
        // Rationale: nodes ARE the stars - background dots cause visual confusion

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
        const safeValue = def.value ?? def.min ?? 0;  // Fallback to min or 0 if value is null
        valueDisplay.textContent = safeValue.toFixed(def.step < 1 ? 2 : 0);
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
        input.value = safeValue;
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
            // Also clear scheme buttons when switching presets
            document.querySelectorAll('.scheme-btn').forEach(b => b.classList.remove('active'));
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

// normalizeMetric - MOVED TO modules/utils.js
// getEdgeColor, getEdgeWidth, applyEdgeMode, cycleEdgeMode, setEdgeMode - MOVED TO modules/edge-system.js
// (backward compat shims in edge-system.js)

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

// setStarsVisible, STARS_STORAGE_KEY, stars toggle binding - MOVED TO modules/stars.js
// Call STARS.init() to initialize (done in modules/main.js)

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
        // Wave Pattern Cycling
        if (e.key === 'w' || e.key === 'W') {
            const activeEl = document.activeElement;
            if (!activeEl || (activeEl.tagName !== 'INPUT' && activeEl.tagName !== 'TEXTAREA')) {
                cycleStaggerPattern();
            }
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

// oklchToHex - MOVED TO modules/color-engine.js (use COLOR.get() instead)
// updatePendulums, getSelectionColor, getNodeSpatialPhase, animateSelectionColors - MOVED TO modules/selection.js
// startSelectionAnimation, stopSelectionAnimation - MOVED TO modules/selection.js (shims provide global names)
// dimColor - MOVED TO modules/color-helpers.js

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
    const idsToRemove = [];
    Array.from(SELECTED_NODE_IDS).forEach(id => {
        if (!visibleIds.has(id)) {
            idsToRemove.push(id);
        }
    });
    if (idsToRemove.length > 0) {
        // Use SELECT.remove() for proper module integration
        // This triggers updateSelectionVisuals via the hook
        SELECT.remove(idsToRemove);
    } else {
        // No changes to selection, but still need to update visuals
        updateSelectionVisuals();
    }
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

// getBoxRect - MOVED TO modules/utils.js

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
    window.GRAPH_MODE = (EXPANDED_FILES.size > 0) ? 'hybrid' : 'files';
    refreshGraph();
}

// sampleFileNodes, buildHull2D, computeCentroid - MOVED TO modules/spatial.js
// quantile - MOVED TO modules/utils.js

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

// SPATIAL HASHING: buildSpatialGrid, getNeighborCells, applySoftCollisions - MOVED TO modules/spatial.js

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

// setFileModeState - MOVED TO modules/file-viz.js (shim delegates to FILE_VIZ.setEnabled)

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
    const inlineBtn = document.getElementById('btn-expand-inline');
    const detachBtn = document.getElementById('btn-expand-detach');
    if (inlineBtn) inlineBtn.classList.toggle('active', FILE_EXPAND_MODE === 'inline');
    if (detachBtn) detachBtn.classList.toggle('active', FILE_EXPAND_MODE === 'detach');
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
        if (e.target.closest('input, button, select, .collapsible-content, .preset-btn, .layout-btn, .scheme-btn')) {
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
