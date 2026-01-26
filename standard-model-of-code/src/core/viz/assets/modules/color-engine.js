/**
 * COLOR ENGINE MODULE
 *
 * Centralized Color Intelligence System using OKLCH color space.
 * Single source of truth for ALL colors in the visualization.
 * Everything reads from here. OKLCH transforms apply here.
 *
 * Usage:
 *   COLOR.get('tier', 'T0')              // Get hex color for tier T0
 *   COLOR.getInterval('markov', 0.5)     // Get interpolated color
 *   COLOR.setTransform('hueShift', 30)   // Shift all hues by 30 degrees
 *   COLOR.subscribe(callback)            // React to transform changes
 */

const COLOR = (function () {
    'use strict';

    // =========================================================================
    // BASE PALETTE: Semantic color definitions (before OKLCH transforms)
    // =========================================================================

    const palette = {
        // NODE DIMENSIONS - VIVID BASE COLORS (high chroma for bold schemes)
        // NOTE: Chroma values are calibrated for sRGB gamut safety
        // Blue (h~220) and cyan (h~180) hues need lower chroma to stay in gamut
        tier: {
            'T0': { h: 142, c: 0.20, l: 0.68, label: 'Foundation', semantic: 'stable' },      // Green (safe)
            'T1': { h: 220, c: 0.11, l: 0.65, label: 'Domain', semantic: 'structure' },       // Blue (c=0.11 max for sRGB)
            'T2': { h: 330, c: 0.20, l: 0.68, label: 'Application', semantic: 'active' },     // Pink (safe)
            'UNKNOWN': { h: 0, c: 0.04, l: 0.50, label: 'Unknown', semantic: 'neutral' }      // Gray
        },
        family: {
            'LOG': { h: 220, c: 0.11, l: 0.62, label: 'Logic', semantic: 'computation' },     // Blue (c=0.11 max for sRGB)
            'DAT': { h: 142, c: 0.20, l: 0.68, label: 'Data', semantic: 'storage' },          // Green (safe)
            'ORG': { h: 280, c: 0.18, l: 0.60, label: 'Organization', semantic: 'structure' },// Purple (slight reduce)
            'EXE': { h: 15, c: 0.22, l: 0.62, label: 'Execution', semantic: 'action' },       // Red (safe)
            'EXT': { h: 35, c: 0.20, l: 0.65, label: 'External', semantic: 'boundary' },      // Orange (safe)
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
        atom: {
            // Function-like (Green-Cyan)
            'function': { h: 160, c: 0.20, l: 0.65, label: 'Function', semantic: 'logic' },
            'method': { h: 175, c: 0.20, l: 0.62, label: 'Method', semantic: 'logic' },
            'closure': { h: 190, c: 0.20, l: 0.60, label: 'Closure', semantic: 'logic' },
            // Class-like (Blue-Purple)
            'class': { h: 260, c: 0.22, l: 0.60, label: 'Class', semantic: 'structure' },
            'interface': { h: 280, c: 0.20, l: 0.65, label: 'Interface', semantic: 'abstraction' },
            'struct': { h: 240, c: 0.20, l: 0.60, label: 'Struct', semantic: 'data' },
            // Module/Package (Orange-Yellow)
            'module': { h: 45, c: 0.22, l: 0.70, label: 'Module', semantic: 'container' },
            'package': { h: 30, c: 0.24, l: 0.65, label: 'Package', semantic: 'container' },
            // Variables/Fields (Pink-Red)
            'variable': { h: 340, c: 0.18, l: 0.65, label: 'Variable', semantic: 'state' },
            'field': { h: 350, c: 0.18, l: 0.62, label: 'Field', semantic: 'state' },
            // Unknown
            'unknown': { h: 0, c: 0.04, l: 0.50, label: 'Unknown', semantic: 'neutral' }
        },
        roleCategory: {
            'Query': { h: 190, c: 0.20, l: 0.65, label: 'Query', semantic: 'read' },         // Cyan
            'Command': { h: 25, c: 0.24, l: 0.60, label: 'Command', semantic: 'write' },     // Orange/Red
            'Factory': { h: 280, c: 0.22, l: 0.60, label: 'Factory', semantic: 'create' },   // Purple
            'Storage': { h: 140, c: 0.20, l: 0.65, label: 'Storage', semantic: 'persist' },  // Green
            'Orchestration': { h: 240, c: 0.22, l: 0.60, label: 'Orchestration', semantic: 'manage' }, // Blue
            'Validation': { h: 45, c: 0.24, l: 0.70, label: 'Validation', semantic: 'check' }, // Yellow
            'Transform': { h: 320, c: 0.20, l: 0.60, label: 'Transform', semantic: 'change' }, // Pink
            'Event': { h: 260, c: 0.22, l: 0.65, label: 'Event', semantic: 'async' },        // Violet
            'Utility': { h: 200, c: 0.10, l: 0.70, label: 'Utility', semantic: 'helper' },   // Light Blue
            'Internal': { h: 0, c: 0.00, l: 0.60, label: 'Internal', semantic: 'private' },  // Gray
            'Unknown': { h: 0, c: 0.00, l: 0.50, label: 'Unknown', semantic: 'neutral' }
        },
        subsystem: {
            'Ingress': { h: 220, c: 0.24, l: 0.60, label: 'Ingress', semantic: 'entry' },
            'Egress': { h: 20, c: 0.24, l: 0.60, label: 'Egress', semantic: 'exit' },
            'Domain': { h: 260, c: 0.24, l: 0.55, label: 'Domain Core', semantic: 'core' },
            'Persistence': { h: 142, c: 0.22, l: 0.65, label: 'Persistence', semantic: 'store' },
            'Async': { h: 300, c: 0.22, l: 0.60, label: 'Async', semantic: 'bg' },
            'Presentation': { h: 190, c: 0.20, l: 0.65, label: 'Presentation', semantic: 'ui' },
            'Security': { h: 0, c: 0.26, l: 0.55, label: 'Security', semantic: 'guard' },
            'Observability': { h: 60, c: 0.22, l: 0.75, label: 'Observability', semantic: 'monitor' },
            'Config': { h: 290, c: 0.18, l: 0.65, label: 'config', semantic: 'setup' },
            'Delivery': { h: 30, c: 0.20, l: 0.70, label: 'Delivery', semantic: 'ops' },
            'Unknown': { h: 0, c: 0.00, l: 0.50, label: 'Unknown', semantic: 'neutral' }
        },
        phase: {
            'DATA': { h: 142, c: 0.22, l: 0.65, label: 'Data', semantic: 'structure' },
            'LOGIC': { h: 240, c: 0.24, l: 0.60, label: 'Logic', semantic: 'flow' },
            'ORGANIZATION': { h: 280, c: 0.22, l: 0.60, label: 'Organization', semantic: 'arch' },
            'EXECUTION': { h: 20, c: 0.26, l: 0.60, label: 'Execution', semantic: 'run' }
        },
        state: {
            'Stateless': { h: 220, c: 0.20, l: 0.70, label: 'Stateless', semantic: 'pure' }, // Light Blue
            'Stateful': { h: 20, c: 0.24, l: 0.60, label: 'Stateful', semantic: 'impure' }   // Orange
        },
        effect: {
            'Pure': { h: 142, c: 0.22, l: 0.70, label: 'Pure', semantic: 'safe' },          // Green
            'SideEffect': { h: 340, c: 0.22, l: 0.60, label: 'Side Effect', semantic: 'risk' } // Pink/Red
        },
        visibility: {
            'Public': { h: 220, c: 0.20, l: 0.65, label: 'Public', semantic: 'open' },
            'Private': { h: 0, c: 0.05, l: 0.55, label: 'Private', semantic: 'closed' },
            'Internal': { h: 280, c: 0.15, l: 0.60, label: 'Internal', semantic: 'module' }
        },
        // SEMANTIC ROLES: From PURPOSE = f(edges) analysis (Stage 6.7)
        semanticRole: {
            'utility': { h: 190, c: 0.18, l: 0.65, label: 'Utility', semantic: 'servant' },       // Cyan - serves many
            'orchestrator': { h: 280, c: 0.22, l: 0.60, label: 'Orchestrator', semantic: 'commander' }, // Purple - calls many
            'hub': { h: 30, c: 0.26, l: 0.65, label: 'Hub', semantic: 'critical' },               // Orange - central junction
            'leaf': { h: 220, c: 0.10, l: 0.55, label: 'Leaf', semantic: 'specialized' },         // Blue-gray - edge node
            'unknown': { h: 0, c: 0.02, l: 0.45, label: 'Unknown', semantic: 'neutral' }
        },
        fileType: {
            'js': { h: 60, c: 0.24, l: 0.70, label: 'JavaScript', semantic: 'code' },    // Yellow
            'ts': { h: 240, c: 0.22, l: 0.60, label: 'TypeScript', semantic: 'code' },    // Blue
            'py': { h: 220, c: 0.20, l: 0.62, label: 'Python', semantic: 'code' },        // Blue
            'go': { h: 190, c: 0.22, l: 0.68, label: 'Go', semantic: 'code' },            // Cyan
            'rs': { h: 30, c: 0.24, l: 0.60, label: 'Rust', semantic: 'code' },           // Orange
            'java': { h: 40, c: 0.24, l: 0.62, label: 'Java', semantic: 'code' },         // Orange/Red
            'c': { h: 210, c: 0.18, l: 0.60, label: 'C', semantic: 'code' },             // Blue
            'cpp': { h: 210, c: 0.20, l: 0.55, label: 'C++', semantic: 'code' },          // Blue
            'h': { h: 280, c: 0.16, l: 0.60, label: 'Header', semantic: 'code' },         // Purple
            'html': { h: 20, c: 0.25, l: 0.60, label: 'HTML', semantic: 'markup' },       // Orange
            'css': { h: 230, c: 0.24, l: 0.60, label: 'CSS', semantic: 'style' },         // Blue
            'json': { h: 60, c: 0.18, l: 0.75, label: 'JSON', semantic: 'data' },         // Yellow
            'yaml': { h: 300, c: 0.18, l: 0.65, label: 'YAML', semantic: 'config' },      // Magenta
            'md': { h: 0, c: 0.04, l: 0.70, label: 'Markdown', semantic: 'doc' },         // Gray
            'unknown': { h: 0, c: 0.02, l: 0.50, label: 'Unknown', semantic: 'neutral' }
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
    };

    // =========================================================================
    // OKLCH TRANSFORM STATE: Applied to all colors
    // =========================================================================

    const transform = {
        hueShift: 0,        // -180 to 180
        chromaScale: 1.0,   // 0 to 2
        lightnessShift: 0,  // -20 to 20 (percentage points)
        amplifier: 1.0      // Gamma for contrast
    };

    // =========================================================================
    // TELEMETRY: Cached reference to COLOR_TELEM (avoids window lookup in hot path)
    // =========================================================================

    let _telemetryRef = null;
    function _getTelemetry() {
        if (!_telemetryRef && typeof window !== 'undefined' && window.COLOR_TELEM) {
            _telemetryRef = window.COLOR_TELEM;
        }
        return _telemetryRef;
    }

    // =========================================================================
    // INTERVAL MAPPINGS: For numeric data -> color gradients
    // =========================================================================

    const intervals = {
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
        },
        complexity: {
            stops: [
                { value: 0.0, h: 142, c: 0.18, l: 0.70 },  // Low complexity (0) - Green
                { value: 0.3, h: 100, c: 0.18, l: 0.75 },  // Moderate (5-10) - Yellow-Green
                { value: 0.6, h: 50, c: 0.20, l: 0.70 },   // High (10-20) - Orange
                { value: 1.0, h: 15, c: 0.24, l: 0.60 }    // Very High (20+) - Red
            ]
        },
        churn: {
            stops: [
                { value: 0.0, h: 230, c: 0.10, l: 0.45 },  // Stale/Cold - Blue
                { value: 0.5, h: 300, c: 0.14, l: 0.60 },  // Active - Purple
                { value: 1.0, h: 30, c: 0.24, l: 0.65 }    // Hot - Orange/Red
            ]
        },
        loc: {
            stops: [
                { value: 0.0, h: 200, c: 0.10, l: 0.75 },  // Small - Light Blue
                { value: 0.3, h: 240, c: 0.18, l: 0.60 },  // Medium - Blue
                { value: 0.7, h: 280, c: 0.20, l: 0.50 },  // Large - Purple
                { value: 1.0, h: 320, c: 0.22, l: 0.40 }   // Massive - Dark Purple
            ]
        },
        trust: {
            stops: [
                { value: 0.0, h: 0, c: 0.24, l: 0.50 },    // Untrusted - Red
                { value: 0.5, h: 60, c: 0.20, l: 0.70 },   // Warning - Yellow
                { value: 1.0, h: 142, c: 0.22, l: 0.65 }   // Trusted - Green
            ]
        },
        responsibility: {
            stops: [
                { value: 0.0, h: 142, c: 0.20, l: 0.70 },  // Single Purpose (1) - Green
                { value: 0.5, h: 60, c: 0.18, l: 0.75 },   // Moderate (5) - Yellow
                { value: 1.0, h: 0, c: 0.24, l: 0.60 }     // God Object (9) - Red
            ]
        },
        purity: {
            stops: [
                { value: 0.0, h: 142, c: 0.20, l: 0.70 },  // Pure (1) - Green
                { value: 0.5, h: 220, c: 0.18, l: 0.65 },  // Mixed (5) - Blue
                { value: 1.0, h: 320, c: 0.24, l: 0.55 }   // I/O Heavy (9) - Purple/Red
            ]
        },
        boundary_score: {
            stops: [
                { value: 0.0, h: 240, c: 0.15, l: 0.65 },  // Internal (1) - Blue
                { value: 0.5, h: 280, c: 0.18, l: 0.60 },  // Module (5) - Purple
                { value: 1.0, h: 20, c: 0.24, l: 0.60 }    // External API (9) - Orange
            ]
        },
        lifecycle_score: {
            stops: [
                { value: 0.0, h: 180, c: 0.15, l: 0.70 },  // Ephemeral (1) - Cyan
                { value: 0.5, h: 220, c: 0.18, l: 0.60 },  // Managed (5) - Blue
                { value: 1.0, h: 280, c: 0.22, l: 0.50 }   // Singleton (9) - Purple
            ]
        },
        centrality: {
            stops: [
                { value: 0.0, h: 240, c: 0.05, l: 0.40 },  // Periphery - Gray/Blue
                { value: 0.5, h: 280, c: 0.20, l: 0.60 },  // Bridge - Purple
                { value: 1.0, h: 340, c: 0.25, l: 0.65 }   // Core - Pink/Red
            ]
        },
        fan_in: {
            stops: [
                { value: 0.0, h: 220, c: 0.10, l: 0.65 },  // Low - Blue
                { value: 0.5, h: 300, c: 0.18, l: 0.60 },  // Med - Purple
                { value: 1.0, h: 30, c: 0.24, l: 0.65 }    // High - Orange
            ]
        },
        fan_out: {
            stops: [
                { value: 0.0, h: 142, c: 0.15, l: 0.65 },  // Low - Green
                { value: 0.5, h: 60, c: 0.18, l: 0.70 },   // Med - Yellow
                { value: 1.0, h: 0, c: 0.24, l: 0.60 }     // High - Red
            ]
        }
    };

    // =========================================================================
    // SCHEME PATHS: 33 Named Color Gradients (OKLCH 3D Paths)
    // Each scheme is a path through OKLCH color space mapping normalized values to colors
    // =========================================================================

    const schemePaths = {
        // =====================================================================
        // PART A: FAMOUS SCIENTIFIC GRADIENTS (15 schemes)
        // Source: matplotlib/viridis family - perceptually uniform
        // =====================================================================

        // === SEQUENTIAL (monotonic lightness) ===
        viridis: {
            name: 'Viridis',
            semantic: 'The gold standard - blue→green→yellow',
            stops: [
                { value: 0.0, h: 280, c: 0.12, l: 0.25 },  // Dark purple
                { value: 0.25, h: 240, c: 0.16, l: 0.40 }, // Blue
                { value: 0.5, h: 170, c: 0.18, l: 0.55 },  // Teal
                { value: 0.75, h: 120, c: 0.20, l: 0.70 }, // Green
                { value: 1.0, h: 65, c: 0.22, l: 0.90 }    // Yellow
            ]
        },
        plasma: {
            name: 'Plasma',
            semantic: 'Purple→pink→orange→yellow arc',
            stops: [
                { value: 0.0, h: 280, c: 0.15, l: 0.20 },  // Deep purple
                { value: 0.25, h: 300, c: 0.22, l: 0.40 }, // Magenta
                { value: 0.5, h: 340, c: 0.25, l: 0.55 },  // Pink-red
                { value: 0.75, h: 30, c: 0.28, l: 0.72 },  // Orange
                { value: 1.0, h: 60, c: 0.24, l: 0.92 }    // Bright yellow
            ]
        },
        magma: {
            name: 'Magma',
            semantic: 'Black→purple→orange→white (lava)',
            stops: [
                { value: 0.0, h: 280, c: 0.04, l: 0.08 },  // Near black
                { value: 0.25, h: 300, c: 0.18, l: 0.30 }, // Deep purple
                { value: 0.5, h: 340, c: 0.24, l: 0.50 },  // Magenta
                { value: 0.75, h: 30, c: 0.26, l: 0.75 },  // Orange
                { value: 1.0, h: 60, c: 0.08, l: 0.98 }    // Near white
            ]
        },
        inferno: {
            name: 'Inferno',
            semantic: 'Black→purple→red→yellow (fire)',
            stops: [
                { value: 0.0, h: 280, c: 0.04, l: 0.05 },  // Black
                { value: 0.2, h: 300, c: 0.16, l: 0.25 },  // Purple
                { value: 0.4, h: 350, c: 0.24, l: 0.45 },  // Red-purple
                { value: 0.6, h: 20, c: 0.28, l: 0.60 },   // Red-orange
                { value: 0.8, h: 50, c: 0.26, l: 0.78 },   // Orange-yellow
                { value: 1.0, h: 65, c: 0.18, l: 0.95 }    // Bright yellow
            ]
        },
        cividis: {
            name: 'Cividis',
            semantic: 'Blue→yellow (colorblind optimized)',
            stops: [
                { value: 0.0, h: 240, c: 0.10, l: 0.25 },  // Dark blue
                { value: 0.33, h: 220, c: 0.08, l: 0.45 }, // Steel blue
                { value: 0.66, h: 80, c: 0.08, l: 0.65 },  // Olive
                { value: 1.0, h: 60, c: 0.14, l: 0.88 }    // Yellow
            ]
        },
        turbo: {
            name: 'Turbo',
            semantic: 'Improved rainbow (no banding)',
            stops: [
                { value: 0.0, h: 260, c: 0.18, l: 0.35 },  // Blue-purple
                { value: 0.2, h: 210, c: 0.22, l: 0.55 },  // Cyan-blue
                { value: 0.4, h: 150, c: 0.24, l: 0.65 },  // Green
                { value: 0.6, h: 60, c: 0.26, l: 0.75 },   // Yellow
                { value: 0.8, h: 30, c: 0.28, l: 0.65 },   // Orange
                { value: 1.0, h: 0, c: 0.24, l: 0.50 }     // Red
            ]
        },
        mako: {
            name: 'Mako',
            semantic: 'Deep ocean blue→teal',
            stops: [
                { value: 0.0, h: 260, c: 0.08, l: 0.12 },  // Abyss
                { value: 0.33, h: 240, c: 0.14, l: 0.35 }, // Deep blue
                { value: 0.66, h: 200, c: 0.18, l: 0.58 }, // Ocean blue
                { value: 1.0, h: 170, c: 0.16, l: 0.82 }   // Light teal
            ]
        },
        rocket: {
            name: 'Rocket',
            semantic: 'Dark→red→white (heat)',
            stops: [
                { value: 0.0, h: 280, c: 0.06, l: 0.10 },  // Dark
                { value: 0.33, h: 340, c: 0.20, l: 0.35 }, // Purple-red
                { value: 0.66, h: 15, c: 0.26, l: 0.60 },  // Red-orange
                { value: 1.0, h: 30, c: 0.08, l: 0.95 }    // Near white
            ]
        },

        // === DIVERGING (center-outward) ===
        coolwarm: {
            name: 'Coolwarm',
            semantic: 'Blue↔neutral↔red (diverging)',
            stops: [
                { value: 0.0, h: 230, c: 0.22, l: 0.45 },  // Cool blue
                { value: 0.25, h: 220, c: 0.12, l: 0.60 }, // Light blue
                { value: 0.5, h: 0, c: 0.02, l: 0.75 },    // Neutral gray
                { value: 0.75, h: 20, c: 0.14, l: 0.60 },  // Light red
                { value: 1.0, h: 15, c: 0.24, l: 0.45 }    // Warm red
            ]
        },
        spectral: {
            name: 'Spectral',
            semantic: 'Full rainbow diverging',
            stops: [
                { value: 0.0, h: 10, c: 0.22, l: 0.50 },   // Red
                { value: 0.25, h: 40, c: 0.24, l: 0.70 },  // Orange-yellow
                { value: 0.5, h: 60, c: 0.20, l: 0.85 },   // Yellow (center)
                { value: 0.75, h: 140, c: 0.20, l: 0.65 }, // Green
                { value: 1.0, h: 240, c: 0.18, l: 0.50 }   // Blue
            ]
        },

        // === APPLICATION-SPECIFIC ===
        thermal: {
            name: 'Thermal',
            semantic: 'Cold→hot temperature map',
            stops: [
                { value: 0.0, h: 240, c: 0.18, l: 0.30 },  // Cold blue
                { value: 0.25, h: 200, c: 0.20, l: 0.45 }, // Cool cyan
                { value: 0.5, h: 60, c: 0.22, l: 0.65 },   // Warm yellow
                { value: 0.75, h: 30, c: 0.26, l: 0.58 },  // Hot orange
                { value: 1.0, h: 0, c: 0.28, l: 0.50 }     // Burning red
            ]
        },
        nightvision: {
            name: 'Night Vision',
            semantic: 'Phosphor green display',
            stops: [
                { value: 0.0, h: 140, c: 0.02, l: 0.05 },  // Black
                { value: 0.33, h: 140, c: 0.12, l: 0.25 }, // Dark green
                { value: 0.66, h: 130, c: 0.22, l: 0.55 }, // Bright green
                { value: 1.0, h: 120, c: 0.28, l: 0.85 }   // Glowing green
            ]
        },
        ocean: {
            name: 'Ocean',
            semantic: 'Bathymetry depth map',
            stops: [
                { value: 0.0, h: 250, c: 0.12, l: 0.15 },  // Abyss
                { value: 0.33, h: 230, c: 0.18, l: 0.35 }, // Deep
                { value: 0.66, h: 200, c: 0.20, l: 0.55 }, // Mid-depth
                { value: 1.0, h: 180, c: 0.16, l: 0.80 }   // Shallow
            ]
        },
        terrain: {
            name: 'Terrain',
            semantic: 'Water→land→mountain',
            stops: [
                { value: 0.0, h: 220, c: 0.16, l: 0.40 },  // Water blue
                { value: 0.3, h: 140, c: 0.18, l: 0.55 },  // Lowland green
                { value: 0.5, h: 80, c: 0.16, l: 0.60 },   // Plains yellow-green
                { value: 0.7, h: 40, c: 0.14, l: 0.50 },   // Hills brown
                { value: 1.0, h: 0, c: 0.04, l: 0.90 }     // Snow white
            ]
        },
        electric: {
            name: 'Electric',
            semantic: 'Neon cyberpunk glow',
            stops: [
                { value: 0.0, h: 280, c: 0.25, l: 0.30 },  // Deep purple
                { value: 0.33, h: 320, c: 0.30, l: 0.50 }, // Hot pink
                { value: 0.66, h: 190, c: 0.28, l: 0.65 }, // Electric cyan
                { value: 1.0, h: 60, c: 0.26, l: 0.85 }    // Neon yellow
            ]
        },

        // =====================================================================
        // PART B: ROLE-SEMANTIC GRADIENTS (18 schemes)
        // Named after canonical roles with meaningful color journeys
        // =====================================================================

        // === GROUP 1: QUERIES & ACCESS (Cool blues/cyans - passive reads) ===
        query: {
            name: 'Query',
            semantic: 'Retrieve data calmly',
            stops: [
                { value: 0.0, h: 220, c: 0.08, l: 0.40 },  // Deep blue - start
                { value: 0.5, h: 200, c: 0.15, l: 0.55 },  // Sky blue - middle
                { value: 1.0, h: 190, c: 0.20, l: 0.70 }   // Light cyan - found
            ]
        },
        finder: {
            name: 'Finder',
            semantic: 'Search and seek',
            stops: [
                { value: 0.0, h: 200, c: 0.05, l: 0.35 },  // Dim - searching
                { value: 0.3, h: 180, c: 0.12, l: 0.50 },  // Teal - hunting
                { value: 0.7, h: 160, c: 0.18, l: 0.65 },  // Cyan-green - close
                { value: 1.0, h: 140, c: 0.24, l: 0.75 }   // Bright green - found!
            ]
        },

        // === GROUP 2: COMMANDS & MUTATIONS (Warm - active writes) ===
        command: {
            name: 'Command',
            semantic: 'Execute with authority',
            stops: [
                { value: 0.0, h: 30, c: 0.15, l: 0.45 },   // Amber ready
                { value: 0.5, h: 20, c: 0.22, l: 0.58 },   // Orange active
                { value: 1.0, h: 10, c: 0.28, l: 0.65 }    // Red-orange fired
            ]
        },
        creator: {
            name: 'Creator',
            semantic: 'Bring into existence',
            stops: [
                { value: 0.0, h: 180, c: 0.10, l: 0.40 },  // Seed teal
                { value: 0.4, h: 150, c: 0.18, l: 0.55 },  // Sprout green
                { value: 0.8, h: 120, c: 0.24, l: 0.68 },  // Growth lime
                { value: 1.0, h: 90, c: 0.28, l: 0.75 }    // Full bloom yellow-green
            ]
        },
        destroyer: {
            name: 'Destroyer',
            semantic: 'Remove from existence',
            stops: [
                { value: 0.0, h: 0, c: 0.08, l: 0.60 },    // Pale warning
                { value: 0.4, h: 10, c: 0.18, l: 0.50 },   // Red alert
                { value: 0.7, h: 350, c: 0.26, l: 0.40 },  // Crimson
                { value: 1.0, h: 340, c: 0.20, l: 0.25 }   // Dark destruction
            ]
        },

        // === GROUP 3: FACTORIES (Construction - blue→green) ===
        factory: {
            name: 'Factory',
            semantic: 'Assembly line production',
            stops: [
                { value: 0.0, h: 220, c: 0.10, l: 0.45 },  // Blueprint blue
                { value: 0.3, h: 200, c: 0.16, l: 0.55 },  // Processing
                { value: 0.6, h: 170, c: 0.20, l: 0.62 },  // Assembly
                { value: 1.0, h: 140, c: 0.24, l: 0.70 }   // Product green
            ]
        },

        // === GROUP 4: STORAGE (Solid, grounded - deep blues/purples) ===
        repository: {
            name: 'Repository',
            semantic: 'Deep data vault',
            stops: [
                { value: 0.0, h: 240, c: 0.12, l: 0.30 },  // Database depths
                { value: 0.5, h: 230, c: 0.18, l: 0.45 },  // Data layer
                { value: 1.0, h: 220, c: 0.22, l: 0.60 }   // Accessible
            ]
        },
        cache: {
            name: 'Cache',
            semantic: 'Fast temporary',
            stops: [
                { value: 0.0, h: 300, c: 0.08, l: 0.50 },  // Magenta flash
                { value: 0.5, h: 320, c: 0.16, l: 0.62 },  // Pink speed
                { value: 1.0, h: 340, c: 0.22, l: 0.75 }   // Hot pink hit
            ]
        },

        // === GROUP 5: ORCHESTRATION (Purple/magenta - control flow) ===
        service: {
            name: 'Service',
            semantic: 'Coordinate operations',
            stops: [
                { value: 0.0, h: 270, c: 0.08, l: 0.40 },  // Purple quiet
                { value: 0.5, h: 280, c: 0.16, l: 0.55 },  // Active violet
                { value: 1.0, h: 290, c: 0.22, l: 0.68 }   // Bright orchid
            ]
        },
        orchestrator: {
            name: 'Orchestrator',
            semantic: 'See all, conduct all',
            stops: [
                { value: 0.0, h: 200, c: 0.12, l: 0.40 },  // Start blue
                { value: 0.25, h: 270, c: 0.18, l: 0.50 }, // Through purple
                { value: 0.5, h: 330, c: 0.22, l: 0.58 },  // To pink
                { value: 0.75, h: 30, c: 0.24, l: 0.62 },  // Through orange
                { value: 1.0, h: 60, c: 0.26, l: 0.70 }    // End gold (full spectrum)
            ]
        },

        // === GROUP 6: VALIDATION (Yellow/green - pass/fail semantics) ===
        validator: {
            name: 'Validator',
            semantic: 'Check and verify',
            stops: [
                { value: 0.0, h: 0, c: 0.20, l: 0.50 },    // Red fail
                { value: 0.4, h: 45, c: 0.22, l: 0.65 },   // Yellow warning
                { value: 1.0, h: 140, c: 0.24, l: 0.70 }   // Green pass
            ]
        },
        guard: {
            name: 'Guard',
            semantic: 'Protect and defend',
            stops: [
                { value: 0.0, h: 350, c: 0.18, l: 0.40 },  // Dark red blocked
                { value: 0.5, h: 30, c: 0.20, l: 0.55 },   // Orange caution
                { value: 1.0, h: 120, c: 0.22, l: 0.65 }   // Green allowed
            ]
        },

        // === GROUP 7: TRANSFORMATION (Rainbow arc - any to any) ===
        transformer: {
            name: 'Transformer',
            semantic: 'Complete metamorphosis',
            stops: [
                { value: 0.0, h: 220, c: 0.14, l: 0.45 },  // Blue input
                { value: 0.3, h: 280, c: 0.18, l: 0.52 },  // Purple process
                { value: 0.6, h: 340, c: 0.22, l: 0.58 },  // Pink transition
                { value: 1.0, h: 30, c: 0.26, l: 0.65 }    // Orange output
            ]
        },
        parser: {
            name: 'Parser',
            semantic: 'Decode from wire',
            stops: [
                { value: 0.0, h: 0, c: 0.02, l: 0.85 },    // White wire
                { value: 0.5, h: 180, c: 0.10, l: 0.70 },  // Decoding
                { value: 1.0, h: 160, c: 0.20, l: 0.55 }   // Data teal
            ]
        },

        // === GROUP 8: EVENTS (Signals - purple/yellow pulses) ===
        handler: {
            name: 'Handler',
            semantic: 'React to event',
            stops: [
                { value: 0.0, h: 270, c: 0.08, l: 0.40 },  // Waiting purple
                { value: 0.5, h: 290, c: 0.18, l: 0.55 },  // Triggered
                { value: 1.0, h: 310, c: 0.26, l: 0.68 }   // Handling pink
            ]
        },
        emitter: {
            name: 'Emitter',
            semantic: 'Broadcast signal',
            stops: [
                { value: 0.0, h: 50, c: 0.18, l: 0.55 },   // Yellow charge
                { value: 0.5, h: 45, c: 0.24, l: 0.68 },   // Bright emit
                { value: 1.0, h: 40, c: 0.30, l: 0.78 }    // Golden broadcast
            ]
        },

        // === GROUP 9: UTILITIES (Neutral supporting - grays/pastels) ===
        utility: {
            name: 'Utility',
            semantic: 'General tool',
            stops: [
                { value: 0.0, h: 220, c: 0.04, l: 0.45 },  // Gray-blue tool
                { value: 0.5, h: 200, c: 0.08, l: 0.58 },  // Soft cyan
                { value: 1.0, h: 180, c: 0.12, l: 0.72 }   // Light teal
            ]
        },
        lifecycle: {
            name: 'Lifecycle',
            semantic: 'Birth to death cycle',
            stops: [
                { value: 0.0, h: 120, c: 0.20, l: 0.65 },  // Birth green
                { value: 0.25, h: 60, c: 0.22, l: 0.70 },  // Youth yellow
                { value: 0.5, h: 30, c: 0.24, l: 0.60 },   // Maturity orange
                { value: 0.75, h: 0, c: 0.20, l: 0.50 },   // Aging red
                { value: 1.0, h: 280, c: 0.10, l: 0.35 }   // Death purple
            ]
        },

        // =====================================================================
        // PART C: OKLCH GEOMETRY GENERATORS (Function-based paths)
        // These use mathematical functions instead of discrete stops.
        // Each has a `generator` function: (t) => { h, c, l }
        // =====================================================================

        // === LOOPS (Full 360° hue cycles) ===
        'rainbow-loop': {
            name: 'Rainbow Loop',
            semantic: 'Full hue circle at constant L/C',
            generator: (t) => ({
                h: t * 360,           // Full hue rotation
                c: 0.20,              // Constant chroma
                l: 0.65               // Constant lightness
            })
        },
        'rainbow-bright': {
            name: 'Rainbow Bright',
            semantic: 'Vivid rainbow with high chroma',
            generator: (t) => ({
                h: t * 360,
                c: 0.28,              // High chroma for vivid colors
                l: 0.70
            })
        },
        'rainbow-dark': {
            name: 'Rainbow Dark',
            semantic: 'Subdued rainbow for dark themes',
            generator: (t) => ({
                h: t * 360,
                c: 0.18,
                l: 0.45               // Lower lightness
            })
        },

        // === ARCS (Partial hue sweeps) ===
        'arc-warm': {
            name: 'Warm Arc',
            semantic: 'Red→Yellow→Orange (warm sector)',
            generator: (t) => ({
                h: 0 + t * 60,        // 0° to 60° (red to yellow)
                c: 0.24,
                l: 0.55 + t * 0.15    // Slight lightness increase
            })
        },
        'arc-cool': {
            name: 'Cool Arc',
            semantic: 'Cyan→Blue→Purple (cool sector)',
            generator: (t) => ({
                h: 180 + t * 100,     // 180° to 280° (cyan to purple)
                c: 0.22,
                l: 0.50 + t * 0.15
            })
        },
        'arc-nature': {
            name: 'Nature Arc',
            semantic: 'Green→Teal→Cyan (nature)',
            generator: (t) => ({
                h: 120 + t * 60,      // 120° to 180° (green to cyan)
                c: 0.20,
                l: 0.60 + t * 0.10
            })
        },

        // === SPIRALS (Hue + varying L or C) ===
        'spiral-up': {
            name: 'Spiral Up',
            semantic: 'Hue rotates as lightness increases',
            generator: (t) => ({
                h: t * 270,           // 3/4 hue rotation
                c: 0.18,
                l: 0.30 + t * 0.55    // Dark to light
            })
        },
        'spiral-down': {
            name: 'Spiral Down',
            semantic: 'Hue rotates as lightness decreases',
            generator: (t) => ({
                h: t * 270,
                c: 0.20,
                l: 0.85 - t * 0.55    // Light to dark
            })
        },
        'spiral-chroma': {
            name: 'Spiral Chroma',
            semantic: 'Hue rotates as saturation increases',
            generator: (t) => ({
                h: t * 360,
                c: 0.06 + t * 0.22,   // Gray to vivid
                l: 0.60
            })
        },

        // === SINUSOIDAL (Wave patterns) ===
        'wave-lightness': {
            name: 'Wave Lightness',
            semantic: 'Sinusoidal lightness oscillation',
            generator: (t) => ({
                h: t * 180,           // Half hue rotation
                c: 0.20,
                l: 0.50 + Math.sin(t * Math.PI * 2) * 0.20  // Wave between 0.30 and 0.70
            })
        },
        'wave-chroma': {
            name: 'Wave Chroma',
            semantic: 'Sinusoidal saturation oscillation',
            generator: (t) => ({
                h: t * 180,
                c: 0.15 + Math.sin(t * Math.PI * 2) * 0.12, // Wave between 0.03 and 0.27
                l: 0.60
            })
        },
        'pulse': {
            name: 'Pulse',
            semantic: 'Both L and C oscillate together',
            generator: (t) => {
                const wave = Math.sin(t * Math.PI * 3); // 1.5 full waves
                return {
                    h: t * 120,       // Partial hue sweep
                    c: 0.15 + wave * 0.10,
                    l: 0.55 + wave * 0.15
                };
            }
        },

        // === LINEAR RAMPS (Simple mathematical paths) ===
        'ramp-hue': {
            name: 'Hue Ramp',
            semantic: 'Pure hue change, constant L/C',
            generator: (t) => ({
                h: 220 + t * 140,     // Blue to pink (220° to 360°)
                c: 0.22,
                l: 0.60
            })
        },
        'ramp-lightness': {
            name: 'Lightness Ramp',
            semantic: 'Dark to light, constant H/C',
            generator: (t) => ({
                h: 220,               // Fixed blue
                c: 0.18,
                l: 0.25 + t * 0.60    // 0.25 to 0.85
            })
        },
        'ramp-chroma': {
            name: 'Chroma Ramp',
            semantic: 'Gray to vivid, constant H/L',
            generator: (t) => ({
                h: 280,               // Fixed purple
                c: 0.02 + t * 0.26,   // 0.02 to 0.28
                l: 0.60
            })
        },

        // === SPECIAL GEOMETRIC PATHS ===
        'helix': {
            name: 'Helix',
            semantic: 'Full 3D path through OKLCH cylinder',
            generator: (t) => ({
                h: t * 540,           // 1.5 hue rotations
                c: 0.10 + t * 0.15,   // Increasing chroma
                l: 0.30 + t * 0.50    // Rising lightness
            })
        },
        'convergent': {
            name: 'Convergent',
            semantic: 'Colors converge toward gray',
            generator: (t) => ({
                h: t * 180,           // Half rotation
                c: 0.26 * (1 - t),    // Chroma decreases to 0
                l: 0.55
            })
        },
        'divergent': {
            name: 'Divergent',
            semantic: 'Colors diverge from gray',
            generator: (t) => ({
                h: 180 + t * 180,     // Second half of hue wheel
                c: 0.26 * t,          // Chroma increases from 0
                l: 0.55
            })
        },
        'bicone': {
            name: 'Bicone',
            semantic: 'Center peak, edges dark (HSL-like)',
            generator: (t) => {
                // Lightness peaks at center, dark at edges
                const l = t < 0.5 ? 0.30 + t * 0.70 : 0.65 - (t - 0.5) * 0.70;
                return {
                    h: t * 360,
                    c: 0.20,
                    l: Math.max(0.30, l)
                };
            }
        }
    };

    // Current active scheme
    let _activeScheme = null;

// =========================================================================
// SUBSCRIBERS: Reactive notifications
// =========================================================================

let _subscribers = [];

function subscribe(callback) {
    _subscribers.push(callback);
    return () => {
        _subscribers = _subscribers.filter(cb => cb !== callback);
    };
}

function _notifySubscribers(event, data) {
    _subscribers.forEach(cb => cb(event, data));
}

// =========================================================================
// OKLCH -> HEX CONVERSION
// =========================================================================

function _toHex(oklch) {
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

    // TELEMETRY: Detect gamut clipping BEFORE clamping (with float tolerance)
    const clipped = r < -0.0001 || r > 1.0001 ||
                    g < -0.0001 || g > 1.0001 ||
                    bl < -0.0001 || bl > 1.0001;

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

    const hex = '#' + [r, g, bl].map(x => x.toString(16).padStart(2, '0')).join('');

    // Return object with hex and clipping info for telemetry
    return { hex, clipped };
}

/**
 * Convert HEX color to OKLCH
 * @param {string} hex - Hex color string (#RGB, #RRGGBB, or #RRGGBBAA)
 * @returns {object} {h, c, l} OKLCH values
 */
function hexToOklch(hex) {
    // Parse hex to RGB
    let r = 0, g = 0, b = 0;

    if (!hex || typeof hex !== 'string') {
        return { h: 0, c: 0, l: 0.5 }; // Gray fallback
    }

    // Remove # if present
    hex = hex.replace(/^#/, '');

    // Handle different hex formats
    if (hex.length === 3) {
        // #RGB -> #RRGGBB
        r = parseInt(hex[0] + hex[0], 16);
        g = parseInt(hex[1] + hex[1], 16);
        b = parseInt(hex[2] + hex[2], 16);
    } else if (hex.length >= 6) {
        r = parseInt(hex.slice(0, 2), 16);
        g = parseInt(hex.slice(2, 4), 16);
        b = parseInt(hex.slice(4, 6), 16);
    } else {
        return { h: 0, c: 0, l: 0.5 }; // Invalid hex, gray fallback
    }

    // Normalize to 0-1
    r /= 255;
    g /= 255;
    b /= 255;

    // Convert sRGB to linear RGB
    const toLinear = (x) => x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
    r = toLinear(r);
    g = toLinear(g);
    b = toLinear(b);

    // Linear RGB to OKLab (via LMS)
    const l_ = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
    const m_ = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
    const s_ = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);

    const L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_;
    const a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_;
    const bLab = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_;

    // OKLab to OKLCH
    const C = Math.sqrt(a * a + bLab * bLab);
    let H = Math.atan2(bLab, a) * 180 / Math.PI;
    if (H < 0) H += 360;

    return {
        h: H,
        c: C,
        l: L
    };
}

function _applyTransform(oklch, source = 'unknown') {
    const t = transform;

    // Apply transforms
    let h = (oklch.h + t.hueShift + 360) % 360;
    let c = Math.max(0, Math.min(0.4, oklch.c * t.chromaScale));
    let l = Math.max(0, Math.min(1, oklch.l + t.lightnessShift / 100));

    // Apply amplifier to chroma for contrast
    if (t.amplifier !== 1) {
        c = Math.pow(c / 0.4, 1 / t.amplifier) * 0.4;
    }

    // Get hex with clipping info
    const result = _toHex({ h, c, l });

    // TELEMETRY: Emit at wormhole boundary (OKLCH -> hex)
    const telem = _getTelemetry();
    if (telem?.enabled) {
        telem.emit(source, l, c, h, result.hex, result.clipped);
    }

    return result.hex;  // Backward compatible: still returns hex string
}

// =========================================================================
// CORE API
// =========================================================================

/**
 * Get color with transforms applied
 * @param {string} dimension - Palette dimension (tier, family, ring, layer, edgeType)
 * @param {string} category - Category within dimension
 * @returns {string} Hex color string
 */
function get(dimension, category) {
    const base = palette[dimension]?.[category];
    if (!base) {
        const fallback = _toHex({ h: 0, c: 0.02, l: 0.40 });
        return fallback.hex; // Fallback gray
    }
    return _applyTransform(base, `palette:${dimension}`);
}

/**
 * Get color for a numeric value using interval mapping
 * @param {string} intervalName - Interval name (markov, weight, confidence)
 * @param {number} value - Value (0-1)
 * @returns {string} Hex color string
 */
function getInterval(intervalName, value) {
    const v = Math.max(0, Math.min(1, value));

    // =========================================================================
    // SCHEME OVERRIDE: If an active scheme is selected, use it for ALL intervals
    // This makes the 33 named schemes (viridis, plasma, thermal, etc.) work
    // =========================================================================
    if (_activeScheme && schemePaths[_activeScheme]) {
        return getSchemeColor(_activeScheme, v);
    }

    // Fall back to hardcoded interval if no scheme active
    const interval = intervals[intervalName];
    if (!interval) {
        const fallback = _toHex({ h: 0, c: 0.02, l: 0.40 });
        return fallback.hex;
    }

    const stops = interval.stops;

    // Find surrounding stops
    let lower = stops[0];
    let upper = (stops && stops.length > 0) ? stops[stops.length - 1] : null;

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

    return _applyTransform(interpolated, `gradient:${intervalName}`);
}

/**
 * Interpolate between two hex colors in OKLCH space
 * @param {string} color1 - Hex color 1
 * @param {string} color2 - Hex color 2
 * @param {number} t - Interpolation factor (0-1)
 * @returns {string} Hex result
 */
function interpolate(color1, color2, t) {
    // We assume input hexes can be approximated back to OKLCH or treated as sRGB->OKLCH
    // For simplicity in this engine which mostly generates from OKLCH, we'll assume
    // specific OKLCH-derived palettes unless provided raw hex.
    // If we really need robust hex->oklch, we need a converter.
    // BUT, for edge gradients in app.js, we often have raw HSL or OKLCH objects.
    // Let's support passing Objects {h,c,l} or hex strings (naive interpolation for hex if needed).
    // Best approach: app.js should use COLOR.get() to get objects if possible, or we expose a helper
    // that takes our internal palette objects.

    // Actually, let's keep it simple: assume app.js will partial refactoring.
    // We will accept object {h,c,l} inputs for maximum precision.
    const c1 = (typeof color1 === 'string') ? parseOklchString(color1) || { h: 0, c: 0, l: 0.5 } : color1;
    const c2 = (typeof color2 === 'string') ? parseOklchString(color2) || { h: 0, c: 0, l: 0.5 } : color2;

    t = Math.max(0, Math.min(1, t));

    // Shortest path hue interpolation
    let h1 = c1.h || c1.H || 0;
    let h2 = c2.h || c2.H || 0;
    let dh = h2 - h1;
    if (Math.abs(dh) > 180) {
        if (dh > 0) h1 += 360;
        else h2 += 360;
    }

    const h = (h1 + (h2 - h1) * t) % 360;
    const c = (c1.c !== undefined ? c1.c : c1.C) + ((c2.c !== undefined ? c2.c : c2.C) - (c1.c !== undefined ? c1.c : c1.C)) * t;
    const l = (c1.l !== undefined ? c1.l : c1.L) + ((c2.l !== undefined ? c2.l : c2.L) - (c1.l !== undefined ? c1.l : c1.L)) * t;

    return _applyTransform({ h, c, l }, 'func:interpolate');
}

/**
 * Get raw OKLCH values (for advanced use)
 */
function getRaw(dimension, category) {
    return palette[dimension]?.[category] || { h: 0, c: 0.02, l: 0.40 };
}

/**
 * Get all categories for a dimension
 */
function getCategories(dimension) {
    return Object.keys(palette[dimension] || {});
}

/**
 * Get label for a category
 */
function getLabel(dimension, category) {
    return palette[dimension]?.[category]?.label || category;
}

// =========================================================================
// TRANSFORM CONTROLS
// =========================================================================

function setTransform(key, value) {
    if (key in transform) {
        transform[key] = value;
        _notifySubscribers('transform-change', { key, value });
    }
}

function setAllTransforms(transforms) {
    Object.assign(transform, transforms);
    _notifySubscribers('transform-change', transforms);
}

function resetTransforms() {
    transform.hueShift = 0;
    transform.chromaScale = 1.0;
    transform.lightnessShift = 0;
    transform.amplifier = 1.0;
    _notifySubscribers('transform-change', transform);
}

function getTransform() {
    return { ...transform };
}

// =========================================================================
// SCHEME API: Named Color Gradients
// =========================================================================

/**
 * List all available scheme names
 * @returns {string[]} Array of scheme names
 */
function listSchemes() {
    return Object.keys(schemePaths);
}

/**
 * Get scheme definition
 * @param {string} schemeName - Name of the scheme
 * @returns {object|null} Scheme definition with name, semantic, and stops
 */
function getScheme(schemeName) {
    return schemePaths[schemeName] || null;
}

/**
 * Get color at position t (0-1) along a scheme path
 * Supports both:
 *   - stops: Array of discrete points (interpolated)
 *   - generator: Function (t) => { h, c, l } (direct mathematical path)
 *
 * @param {string} schemeName - Name of the scheme
 * @param {number} t - Position along path (0-1)
 * @returns {string} Hex color string
 */
function getSchemeColor(schemeName, t) {
    const scheme = schemePaths[schemeName];
    if (!scheme) {
        const fallback = _toHex({ h: 0, c: 0.02, l: 0.40 });
        return fallback.hex;
    }

    const v = Math.max(0, Math.min(1, t));
    const source = `scheme:${schemeName}`;

    // GENERATOR MODE: Mathematical function (OKLCH geometry)
    if (scheme.generator && typeof scheme.generator === 'function') {
        const oklch = scheme.generator(v);
        return _applyTransform(oklch, source);
    }

    // STOPS MODE: Discrete points with interpolation
    const stops = scheme.stops;
    if (!stops || stops.length === 0) {
        const fallback = _toHex({ h: 0, c: 0.02, l: 0.40 });
        return fallback.hex;
    }

    // Find surrounding stops
    let lower = stops[0];
    let upper = (stops && stops.length > 0) ? stops[stops.length - 1] : null;

    for (let i = 0; i < stops.length - 1; i++) {
        if (v >= stops[i].value && v <= stops[i + 1].value) {
            lower = stops[i];
            upper = stops[i + 1];
            break;
        }
    }

    // Interpolate between stops
    const range = upper.value - lower.value;
    const interp = range > 0 ? (v - lower.value) / range : 0;

    const interpolated = {
        h: lower.h + (upper.h - lower.h) * interp,
        c: lower.c + (upper.c - lower.c) * interp,
        l: lower.l + (upper.l - lower.l) * interp
    };

    return _applyTransform(interpolated, source);
}

/**
 * Apply a scheme as the active color scheme
 * This sets transforms and notifies subscribers
 * @param {string} schemeName - Name of the scheme
 */
function applyScheme(schemeName) {
    // Allow null/undefined to clear the active scheme
    if (!schemeName) {
        _activeScheme = null;
        _notifySubscribers('scheme-change', { scheme: null, definition: null });
        console.log('[COLOR] Cleared active scheme, using default intervals');
        return;
    }

    const scheme = schemePaths[schemeName];
    if (!scheme) {
        console.warn('[COLOR] Unknown scheme:', schemeName);
        return;
    }

    _activeScheme = schemeName;
    _notifySubscribers('scheme-change', { scheme: schemeName, definition: scheme });
    console.log('[COLOR] Applied scheme:', schemeName, '-', scheme.semantic);
}

/**
 * Get the currently active scheme name
 * @returns {string|null} Active scheme name or null
 */
function getActiveScheme() {
    return _activeScheme;
}

/**
 * Generate a CSS gradient string for a scheme (for UI previews)
 * @param {string} schemeName - Name of the scheme
 * @param {string} direction - CSS gradient direction (default: 'to right')
 * @returns {string} CSS linear-gradient string
 */
function getSchemeGradientCSS(schemeName, direction = 'to right') {
    const scheme = schemePaths[schemeName];
    if (!scheme) return 'linear-gradient(to right, #333, #666)';

    const colorStops = scheme.stops.map(stop => {
        const color = _applyTransform(stop);
        const percent = Math.round(stop.value * 100);
        return `${color} ${percent}%`;
    });

    return `linear-gradient(${direction}, ${colorStops.join(', ')})`;
}

/**
 * Get scheme metadata (name, semantic description)
 * @param {string} schemeName - Name of the scheme
 * @returns {object} {name, semantic}
 */
function getSchemeInfo(schemeName) {
    const scheme = schemePaths[schemeName];
    if (!scheme) return { name: schemeName, semantic: 'Unknown' };
    return { name: scheme.name, semantic: scheme.semantic };
}

// =========================================================================
// PUBLIC toHex WRAPPER (backward compatible)
// =========================================================================

/**
 * Convert OKLCH to hex color (public API)
 * @param {object} oklch - {h, c, l} OKLCH values
 * @returns {string} Hex color string
 */
function toHex(oklch) {
    const result = _toHex(oklch);

    // Emit telemetry for public API calls
    const telem = _getTelemetry();
    if (telem?.enabled) {
        telem.emit('api:public', oklch.l, oklch.c, oklch.h, result.hex, result.clipped);
    }

    return result.hex;  // Return just the hex string for backward compatibility
}

// =========================================================================
// DEBUG
// =========================================================================

function debug() {
    console.log('[COLOR] Transform state:', transform);
    console.log('[COLOR] Palette dimensions:', Object.keys(palette));
    console.log('[COLOR] Interval mappings:', Object.keys(intervals));
    console.log('[COLOR] Schemes:', Object.keys(schemePaths).length, 'available');
    console.log('[COLOR] Active scheme:', _activeScheme);
}

// =========================================================================
// PUBLIC API
// =========================================================================

return {
    // Core API
    get,
    getInterval,
    getRaw,
    getCategories,
    getLabel,
    interpolate,

    // OKLCH Conversion (for UPB integration)
    toHex,
    hexToOklch,

    // Transform controls
    setTransform,
    setAllTransforms,
    resetTransforms,
    getTransform,

    // Scheme API (33 named color gradients)
    listSchemes,
    getScheme,
    getSchemeColor,
    applyScheme,
    getActiveScheme,
    getSchemeGradientCSS,
    getSchemeInfo,

    // Subscriptions
    subscribe,

    // Internal access (for migration)
    palette,
    intervals,
    transform,
    schemePaths,

    // Debug
    debug
};
}) ();

// Export to window for global access
window.COLOR = COLOR;

// Backward compatibility aliases - Using Object.defineProperty to avoid duplicate declarations
Object.defineProperty(window, 'ColorOrchestrator', { get: () => COLOR, configurable: true });
Object.defineProperty(window, 'Color', { get: () => COLOR, configurable: true });

console.log('[Module] COLOR loaded - OKLCH color engine with', Object.keys(COLOR.schemePaths || {}).length, 'schemes');
