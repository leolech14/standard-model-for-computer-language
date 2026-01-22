const UPB_ENDPOINTS = (function () {
    'use strict';

    /**
     * UNIVERSAL PROPERTY BINDER - ENDPOINTS MODULE
     * Definitions/Schema for all Data Sources (inputs) and Visual Targets (outputs).
     */

    // =========================================================================
    // AVAILABLE DATA SOURCES (Mappings FROM)
    // =========================================================================
    const SOURCES = {
        // Structural metrics
        size_bytes: { label: 'File Size (bytes)', type: 'continuous', domain: 'file' },
        token_estimate: { label: 'Token Count', type: 'continuous', domain: 'file' },
        line_count: { label: 'Line Count', type: 'continuous', domain: 'file' },
        code_lines: { label: 'Code Lines', type: 'continuous', domain: 'file' },
        complexity_density: { label: 'Complexity Density', type: 'continuous', domain: 'file' },
        cohesion: { label: 'Cohesion', type: 'continuous', domain: 'file' },
        code_ratio: { label: 'Code Ratio', type: 'continuous', domain: 'file' },

        // Structural
        token_estimate: {
            Type: 'continuous',
            domain: 'file',
            label: 'Token Count',
            tags: ['structural', 'quantitative', 'size']
        },
        line_count: {
            Type: 'continuous',
            domain: 'file',
            label: 'Line Count',
            tags: ['structural', 'quantitative', 'verticality']
        },
        size_bytes: {
            Type: 'continuous',
            domain: 'file',
            label: 'File Size',
            tags: ['structural', 'quantitative', 'weight']
        },
        code_lines: {
            Type: 'continuous',
            domain: 'file',
            label: 'Code Lines',
            tags: ['structural', 'quantitative', 'density']
        },
        complexity_density: {
            Type: 'continuous',
            domain: 'file',
            label: 'Complexity',
            tags: ['structural', 'qualitative', 'entropy']
        },
        cohesion: {
            Type: 'continuous',
            domain: 'file',
            label: 'Cohesion',
            tags: ['structural', 'qualitative', 'unity']
        },

        // Temporal
        age_days: {
            Type: 'continuous',
            domain: 'file',
            label: 'Age (Days)',
            tags: ['temporal', 'quantitative', 'decay']
        },

        // Graph / Topology
        in_degree: {
            Type: 'continuous',
            domain: 'node',
            label: 'In-Degree',
            tags: ['topological', 'quantitative', 'popularity']
        },
        out_degree: {
            Type: 'continuous',
            domain: 'node',
            label: 'Out-Degree',
            tags: ['topological', 'quantitative', 'dependency']
        },

        // Categorical
        tier: {
            Type: 'discrete',
            domain: 'node',
            label: 'Tier (Layer)',
            tags: ['architectural', 'categorical', 'hierarchy']
        },
        role: {
            Type: 'discrete',
            domain: 'node',
            label: 'Role',
            tags: ['semantic', 'categorical', 'purpose']
        },
        format_category: {
            Type: 'discrete',
            domain: 'file',
            label: 'Format',
            tags: ['technical', 'categorical', 'syntax']
        },

        // Boolean
        is_test: {
            Type: 'boolean',
            domain: 'file',
            label: 'Is Test',
            tags: ['functional', 'boolean', 'quality']
        },
        is_stale: {
            Type: 'boolean',
            domain: 'file',
            label: 'Is Stale',
            tags: ['temporal', 'boolean', 'risk']
        },

        // =====================================================================
        // TREE-SITTER ANALYSIS (T2-T6)
        // =====================================================================

        // T2: Purity Score (D6:EFFECT - continuous)
        D6_pure_score: {
            Type: 'continuous',
            domain: 'node',
            label: 'Purity Score',
            range: [0, 1],
            tags: ['theory', 'D6', 'purity', 'effect', 'tree-sitter']
        },

        // T3: Purity Rating (D6:EFFECT - categorical)
        D6_EFFECT: {
            Type: 'discrete',
            domain: 'node',
            label: 'Purity Rating',
            values: ['pure', 'mostly_pure', 'mixed', 'mostly_impure', 'impure'],
            tags: ['theory', 'D6', 'purity', 'categorical', 'tree-sitter']
        },

        // T4: PageRank (graph centrality)
        pagerank: {
            Type: 'continuous',
            domain: 'node',
            label: 'PageRank',
            range: [0, 1],
            tags: ['topological', 'centrality', 'influence', 'quantitative']
        },

        // T5: Betweenness Centrality (bridge nodes)
        betweenness_centrality: {
            Type: 'continuous',
            domain: 'node',
            label: 'Betweenness',
            range: [0, 1],
            tags: ['topological', 'centrality', 'bridge', 'quantitative']
        },

        // T6: Topology Role (categorical)
        topology_role: {
            Type: 'discrete',
            domain: 'node',
            label: 'Topology Role',
            values: ['orphan', 'root', 'leaf', 'hub', 'internal'],
            tags: ['topological', 'categorical', 'structure']
        },

        // =====================================================================
        // CONTROL FLOW METRICS (P3-09)
        // =====================================================================

        // Cyclomatic Complexity (McCabe metric)
        cyclomatic_complexity: {
            Type: 'continuous',
            domain: 'node',
            label: 'Cyclomatic Complexity',
            range: [1, 50],
            tags: ['complexity', 'control-flow', 'quantitative', 'tree-sitter']
        },

        // Complexity Rating (categorical)
        complexity_rating: {
            Type: 'discrete',
            domain: 'node',
            label: 'Complexity Rating',
            values: ['simple', 'moderate', 'complex', 'very_complex'],
            tags: ['complexity', 'control-flow', 'categorical']
        },

        // Max Nesting Depth
        max_nesting_depth: {
            Type: 'continuous',
            domain: 'node',
            label: 'Nesting Depth',
            range: [0, 10],
            tags: ['complexity', 'control-flow', 'quantitative', 'tree-sitter']
        },

        // Nesting Rating (categorical)
        nesting_rating: {
            Type: 'discrete',
            domain: 'node',
            label: 'Nesting Rating',
            values: ['shallow', 'moderate', 'deep', 'very_deep'],
            tags: ['complexity', 'control-flow', 'categorical']
        },

        // =====================================================================
        // RPBL SCORES (P4-05/07/08) - Theory Character Dimensions
        // =====================================================================

        // Responsibility (R) - How much does this node do?
        rpbl_responsibility: {
            Type: 'continuous',
            domain: 'node',
            label: 'Responsibility (R)',
            range: [0, 10],
            tags: ['rpbl', 'theory', 'D3', 'quantitative']
        },

        // Purity (P) - How pure is this node?
        rpbl_purity: {
            Type: 'continuous',
            domain: 'node',
            label: 'Purity (P)',
            range: [0, 10],
            tags: ['rpbl', 'theory', 'D6', 'quantitative']
        },

        // Boundary (B) - How exposed is this node?
        rpbl_boundary: {
            Type: 'continuous',
            domain: 'node',
            label: 'Boundary (B)',
            range: [0, 10],
            tags: ['rpbl', 'theory', 'D4', 'quantitative']
        },

        // Lifecycle (L) - What lifecycle stage?
        rpbl_lifecycle: {
            Type: 'continuous',
            domain: 'node',
            label: 'Lifecycle (L)',
            range: [0, 10],
            tags: ['rpbl', 'theory', 'D7', 'quantitative']
        }
    };

    // =========================================================================
    // AVAILABLE TARGETS (Mappings TO)
    // =========================================================================
    const TARGETS = {
        // Geometric
        nodeSize: {
            category: 'geometry',
            range: [1, 30],
            minOutput: 1,           // Prevent zero-size nodes
            blendMode: 'max',       // Multiple bindings → take largest
            label: 'Node Size',
            tags: ['visual', 'geometric', 'magnitude', 'importance']
        },
        xPosition: {
            category: 'geometry',
            range: [-1000, 1000],
            blendMode: 'average',   // Blend positions via average
            label: 'X Position',
            tags: ['visual', 'geometric', 'spatial', 'horizontal']
        },
        yPosition: { label: 'Y Position', category: 'position', range: [-500, 500], blendMode: 'average' },
        zPosition: { label: 'Z Position (depth)', category: 'position', range: [-300, 300], blendMode: 'average' },
        radius: { label: 'Radial Distance', category: 'position', range: [50, 400], minOutput: 50, blendMode: 'max' },

        // Chromatic
        hue: {
            category: 'color',
            range: [0, 360],
            blendMode: 'replace',   // Hue doesn't blend well
            label: 'Color Hue',
            tags: ['visual', 'chromatic', 'identity', 'cyclical']
        },
        saturation: {
            category: 'color',
            range: [0, 100],
            blendMode: 'average',
            label: 'Saturation',
            tags: ['visual', 'chromatic', 'intensity', 'purity']
        },
        lightness: {
            category: 'color',
            range: [0, 100],
            minOutput: 10,          // Prevent invisible (black) nodes
            blendMode: 'average',
            label: 'Lightness',
            tags: ['visual', 'chromatic', 'brightness', 'fade']
        },
        opacity: {
            category: 'color',
            range: [0.1, 1.0],
            minOutput: 0.1,         // Prevent fully transparent nodes
            blendMode: 'multiply',  // Stacked effects multiply
            label: 'Opacity',
            tags: ['visual', 'chromatic', 'presence', 'ghost']
        },

        // Physics / Simulation
        charge: {
            category: 'physics',
            range: [-500, 0],
            blendMode: 'add',       // Charges accumulate
            label: 'Repulsion',
            tags: ['simulation', 'force', 'space', 'isolation']
        },
        collisionRadius: {
            category: 'physics',
            range: [1, 50],
            minOutput: 1,           // Minimum collision body
            blendMode: 'max',
            label: 'Collision Body',
            tags: ['simulation', 'force', 'substance', 'barrier']
        },
        linkStrength: { label: 'Link Strength', category: 'physics', range: [0, 1], blendMode: 'average' },
        mass: { label: 'Mass (inertia)', category: 'physics', range: [1, 10], minOutput: 1, blendMode: 'add' },

        // Animation
        pulseSpeed: { label: 'Pulse Speed', category: 'animation', range: [0, 5], blendMode: 'max' },
        rotationSpeed: { label: 'Rotation Speed', category: 'animation', range: [0, 2], blendMode: 'max' },

        // Edge-specific targets
        edgeHue: {
            category: 'edge-color',
            range: [0, 360],
            blendMode: 'replace',
            label: 'Edge Hue',
            tags: ['visual', 'chromatic', 'edge', 'cyclical']
        },
        edgeSaturation: {
            category: 'edge-color',
            range: [0, 100],
            blendMode: 'average',
            label: 'Edge Saturation',
            tags: ['visual', 'chromatic', 'edge', 'intensity']
        },
        edgeLightness: {
            category: 'edge-color',
            range: [0, 100],
            minOutput: 10,
            blendMode: 'average',
            label: 'Edge Lightness',
            tags: ['visual', 'chromatic', 'edge', 'brightness']
        },
        edgeOpacity: {
            category: 'edge-color',
            range: [0.01, 1.0],
            minOutput: 0.01,
            blendMode: 'multiply',
            label: 'Edge Opacity',
            tags: ['visual', 'chromatic', 'edge', 'presence']
        },
        edgeWidth: {
            category: 'edge-geometry',
            range: [0.5, 5],
            minOutput: 0.5,
            blendMode: 'max',
            label: 'Edge Width',
            tags: ['visual', 'geometric', 'edge', 'thickness']
        }
    };

    function getSource(name) {
        return SOURCES[name] || null;
    }

    function getTarget(name) {
        return TARGETS[name] || null;
    }

    function listSources(typeFilter) {
        if (!typeFilter) return Object.keys(SOURCES);
        return Object.keys(SOURCES).filter(k => SOURCES[k].type === typeFilter);
    }

    function listTargets(categoryFilter) {
        if (!categoryFilter) return Object.keys(TARGETS);
        return Object.keys(TARGETS).filter(k => TARGETS[k].category === categoryFilter);
    }

    return {
        SOURCES,
        TARGETS,
        getSource,
        getTarget,
        listSources,
        listTargets
    };
})();

// Export
if (typeof window !== 'undefined') window.UPB_ENDPOINTS = UPB_ENDPOINTS;
if (typeof module !== 'undefined') module.exports = UPB_ENDPOINTS;
