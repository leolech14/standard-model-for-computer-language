/**
 * UNLIT NODES MODULE
 *
 * Creates MeshBasicMaterial spheres for data-pure color encoding.
 *
 * Problem: Standard 3D lighting (MeshLambertMaterial) corrupts data encoding:
 * - Shadows darken nodes (lightness no longer reflects recency)
 * - Highlights brighten nodes (chroma interpretation changes)
 * - Ambient occlusion adds unintended darkness
 *
 * Solution: Use MeshBasicMaterial which ignores all lighting.
 * Colors display exactly as specified in OKLCH space.
 *
 * Depth cues maintained via:
 * - Fog (atmospheric depth)
 * - Size attenuation (perspective)
 * - Outline shaders (optional)
 *
 * Usage:
 *   UNLIT.createNode(node, color, radius)  // Create unlit sphere
 *   UNLIT.setFogEnabled(true)              // Enable depth fog
 *   UNLIT.getNodeMaterial(color)           // Get cached material
 *
 * Integration:
 *   Graph.nodeThreeObject(node => UNLIT.createNode(node, node.color, node.val))
 *   Graph.nodeThreeObjectExtend(false)  // Replace default, don't extend
 *
 * Research validated by Perplexity (2026-01-23):
 * - MeshBasicMaterial preserves exact RGB values
 * - Fog adds depth cues without altering object colors
 * - Source: discourse.threejs.org, dustinpfister.github.io
 */

const UNLIT = (function() {
    'use strict';

    // =========================================================================
    // CONFIGURATION
    // =========================================================================

    const config = {
        enabled: false,              // Toggle for gradual migration
        fogEnabled: true,            // Atmospheric depth cues
        fogColor: 0x000000,          // Black fog for dark theme
        fogNear: 100,                // Fog starts fading
        fogFar: 800,                 // Fog fully opaque
        defaultRadius: 4,            // Default sphere radius
        segments: 16,                // Sphere detail (performance vs quality)
        outlineEnabled: false,       // Edge outline for structure (future)
        outlineColor: 0x000000,      // Outline color
        outlineThickness: 0.1        // Outline width
    };

    // =========================================================================
    // MATERIAL CACHE
    // =========================================================================

    // Cache materials by hex color to avoid creating duplicates
    const _materialCache = new Map();

    /**
     * Get or create a cached MeshBasicMaterial for a color
     * @param {number|string} color - Hex color (0xRRGGBB or '#RRGGBB')
     * @returns {THREE.MeshBasicMaterial}
     */
    function getNodeMaterial(color) {
        // Normalize to hex number
        const hex = typeof color === 'string'
            ? parseInt(color.replace('#', ''), 16)
            : color;

        const cacheKey = hex;

        if (!_materialCache.has(cacheKey)) {
            const material = new THREE.MeshBasicMaterial({
                color: hex,
                transparent: true,
                opacity: 1.0,
                fog: config.fogEnabled  // Material respects scene fog
            });
            _materialCache.set(cacheKey, material);
        }

        return _materialCache.get(cacheKey);
    }

    // =========================================================================
    // GEOMETRY CACHE
    // =========================================================================

    // Cache sphere geometries by segment count
    const _geometryCache = new Map();

    function getSphereGeometry(radius, segments) {
        const key = `${radius.toFixed(2)}_${segments}`;

        if (!_geometryCache.has(key)) {
            _geometryCache.set(key, new THREE.SphereGeometry(radius, segments, segments));
        }

        return _geometryCache.get(key);
    }

    // =========================================================================
    // NODE CREATION
    // =========================================================================

    /**
     * Create an unlit sphere mesh for a node
     * @param {object} node - Node data object
     * @param {number|string} color - Node color
     * @param {number} radius - Sphere radius (default from node.val or config)
     * @returns {THREE.Mesh}
     */
    function createNode(node, color, radius) {
        if (!config.enabled) {
            return null;  // Let default rendering handle it
        }

        const r = radius || node.val || config.defaultRadius;
        const geometry = getSphereGeometry(r, config.segments);
        const material = getNodeMaterial(color || node.color || 0x888888);

        const mesh = new THREE.Mesh(geometry, material);

        // Store reference for updates
        mesh.userData.nodeId = node.id;
        mesh.userData.isUnlitNode = true;

        return mesh;
    }

    /**
     * Create an unlit node with outline (for enhanced depth perception)
     * Uses two meshes: inner solid + outer outline
     * @param {object} node - Node data
     * @param {number|string} color - Node color
     * @param {number} radius - Sphere radius
     * @returns {THREE.Group}
     */
    function createNodeWithOutline(node, color, radius) {
        const group = new THREE.Group();

        const r = radius || node.val || config.defaultRadius;

        // Inner sphere (data color)
        const innerMesh = createNode(node, color, r);
        if (innerMesh) {
            group.add(innerMesh);
        }

        // Outer outline (slightly larger, dark edge)
        if (config.outlineEnabled) {
            const outlineGeometry = getSphereGeometry(r * (1 + config.outlineThickness), config.segments);
            const outlineMaterial = new THREE.MeshBasicMaterial({
                color: config.outlineColor,
                side: THREE.BackSide,  // Render only back faces
                transparent: true,
                opacity: 0.3
            });
            const outlineMesh = new THREE.Mesh(outlineGeometry, outlineMaterial);
            group.add(outlineMesh);
        }

        group.userData.nodeId = node.id;
        group.userData.isUnlitNode = true;

        return group;
    }

    // =========================================================================
    // FOG MANAGEMENT
    // =========================================================================

    /**
     * Apply fog to scene for depth cues
     * @param {THREE.Scene} scene - The Three.js scene
     */
    function applyFog(scene) {
        if (!scene) return;

        if (config.fogEnabled) {
            scene.fog = new THREE.Fog(config.fogColor, config.fogNear, config.fogFar);
        } else {
            scene.fog = null;
        }
    }

    /**
     * Set fog enabled state
     * @param {boolean} enabled
     */
    function setFogEnabled(enabled) {
        config.fogEnabled = enabled;
        // Caller should re-apply fog to scene
    }

    /**
     * Configure fog parameters
     * @param {object} params - { color, near, far }
     */
    function configureFog(params) {
        if (params.color !== undefined) config.fogColor = params.color;
        if (params.near !== undefined) config.fogNear = params.near;
        if (params.far !== undefined) config.fogFar = params.far;
    }

    // =========================================================================
    // INTEGRATION HELPERS
    // =========================================================================

    /**
     * Enable unlit rendering mode
     * Call this before initializing the graph
     */
    function enable() {
        config.enabled = true;
        console.log('[UNLIT] Enabled unlit node rendering (MeshBasicMaterial)');
    }

    /**
     * Disable unlit rendering mode
     * Graph will use default 3d-force-graph rendering
     */
    function disable() {
        config.enabled = false;
        console.log('[UNLIT] Disabled unlit rendering, using default materials');
    }

    /**
     * Check if unlit mode is enabled
     * @returns {boolean}
     */
    function isEnabled() {
        return config.enabled;
    }

    /**
     * Clear material and geometry caches
     * Call when switching themes or major color changes
     */
    function clearCaches() {
        _materialCache.forEach(mat => mat.dispose());
        _materialCache.clear();
        _geometryCache.forEach(geo => geo.dispose());
        _geometryCache.clear();
        console.log('[UNLIT] Cleared material/geometry caches');
    }

    /**
     * Update node opacity (for selection/dimming)
     * @param {THREE.Mesh|THREE.Group} mesh - The node mesh
     * @param {number} opacity - New opacity (0-1)
     */
    function setNodeOpacity(mesh, opacity) {
        if (!mesh) return;

        if (mesh.material) {
            mesh.material.opacity = opacity;
            mesh.material.needsUpdate = true;
        }

        // Handle groups (nodes with outlines)
        if (mesh.children) {
            mesh.children.forEach(child => {
                if (child.material) {
                    child.material.opacity = opacity;
                    child.material.needsUpdate = true;
                }
            });
        }
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Core creation
        createNode,
        createNodeWithOutline,
        getNodeMaterial,

        // Fog management
        applyFog,
        setFogEnabled,
        configureFog,

        // Integration
        enable,
        disable,
        isEnabled,
        clearCaches,
        setNodeOpacity,

        // Config access (for UI controls)
        config
    };
})();

// Export to window
window.UNLIT = UNLIT;

console.log('[Module] UNLIT loaded - data-pure MeshBasicMaterial node rendering');
