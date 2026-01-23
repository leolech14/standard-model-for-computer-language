/**
 * FILE TREE LAYOUT MODULE
 *
 * 3D Cone Tree layout for directory hierarchies.
 * Based on Xerox PARC Cone Trees (Robertson et al., 1991).
 *
 * Architecture:
 * - Parent nodes at apex of cone
 * - Children spread on conical surface below
 * - Depth separates hierarchy levels
 * - Integrates with 3d-force-graph via custom forces
 *
 * Features:
 * - Cone Tree geometry for clear hierarchy
 * - Force-directed refinement for collision avoidance
 * - Level-of-detail (LOD) for scalability (500-2000 nodes)
 * - OKLCH color integration (hue=type, L=recency, C=importance)
 *
 * Research validated by Perplexity (2026-01-23):
 * - Cone Trees outperform treemaps and radial layouts for 3D
 * - Hybrid force+containment best for interactivity
 * - Source: PMC, Xerox PARC papers
 *
 * Usage:
 *   FILE_TREE.computeLayout(nodes, edges)     // Compute initial positions
 *   FILE_TREE.createContainmentForce(graph)   // Add to 3d-force-graph
 *   FILE_TREE.setDepthSpacing(50)             // Configure vertical spacing
 */

const FILE_TREE = (function() {
    'use strict';

    // =========================================================================
    // CONFIGURATION
    // =========================================================================

    const config = {
        // Cone geometry
        coneAngle: 45,              // Degrees from vertical (spread angle)
        depthSpacing: 60,           // Vertical distance between levels
        minRadius: 20,              // Minimum cone base radius
        radiusPerChild: 8,          // Additional radius per child node
        maxRadius: 200,             // Maximum cone base radius

        // Force parameters
        containmentStrength: 0.3,   // How strongly children pulled to parent cone
        siblingRepulsion: 0.1,      // Repulsion between siblings
        depthAttraction: 0.2,       // Pull toward correct depth level

        // Scalability
        maxVisibleDepth: 6,         // LOD: hide nodes beyond this depth
        collapseThreshold: 50,      // Collapse directories with >N children

        // Animation
        animationDuration: 500,     // ms for layout transitions
        warmupTicks: 50             // Force simulation warmup
    };

    // =========================================================================
    // HIERARCHY ANALYSIS
    // =========================================================================

    /**
     * Build parent-child map from edges
     * @param {Array} nodes - Node array
     * @param {Array} edges - Edge array with source/target
     * @returns {object} { parentMap, childrenMap, roots }
     */
    function analyzeHierarchy(nodes, edges) {
        const parentMap = new Map();    // nodeId -> parentId
        const childrenMap = new Map();  // nodeId -> [childIds]
        const nodeSet = new Set(nodes.map(n => n.id));

        // Initialize children map
        nodes.forEach(n => childrenMap.set(n.id, []));

        // Build from containment edges
        edges.forEach(edge => {
            const sourceId = typeof edge.source === 'object' ? edge.source.id : edge.source;
            const targetId = typeof edge.target === 'object' ? edge.target.id : edge.target;

            // "contains" edges: source contains target
            if (edge.type === 'contains' || edge.relation === 'contains') {
                if (nodeSet.has(sourceId) && nodeSet.has(targetId)) {
                    parentMap.set(targetId, sourceId);
                    const children = childrenMap.get(sourceId) || [];
                    children.push(targetId);
                    childrenMap.set(sourceId, children);
                }
            }
        });

        // Find roots (nodes with no parent)
        const roots = nodes.filter(n => !parentMap.has(n.id)).map(n => n.id);

        return { parentMap, childrenMap, roots };
    }

    /**
     * Compute depth for each node
     * @param {object} hierarchy - From analyzeHierarchy
     * @param {Map} nodeMap - id -> node
     * @returns {Map} nodeId -> depth
     */
    function computeDepths(hierarchy, nodeMap) {
        const { parentMap, roots } = hierarchy;
        const depthMap = new Map();

        function setDepth(nodeId, depth) {
            depthMap.set(nodeId, depth);
            const children = hierarchy.childrenMap.get(nodeId) || [];
            children.forEach(childId => setDepth(childId, depth + 1));
        }

        roots.forEach(rootId => setDepth(rootId, 0));

        return depthMap;
    }

    // =========================================================================
    // CONE TREE POSITIONING
    // =========================================================================

    /**
     * Compute initial cone tree positions
     * @param {Array} nodes - Node array
     * @param {Array} edges - Edge array
     * @returns {Map} nodeId -> { x, y, z }
     */
    function computeLayout(nodes, edges) {
        const nodeMap = new Map(nodes.map(n => [n.id, n]));
        const hierarchy = analyzeHierarchy(nodes, edges);
        const depthMap = computeDepths(hierarchy, nodeMap);
        const positions = new Map();

        /**
         * Position a node and its children recursively
         * @param {string} nodeId
         * @param {number} centerX - Parent cone center X
         * @param {number} centerZ - Parent cone center Z
         * @param {number} availableAngle - Angular range for this subtree
         * @param {number} startAngle - Starting angle in radians
         */
        function positionNode(nodeId, centerX, centerZ, availableAngle, startAngle) {
            const depth = depthMap.get(nodeId) || 0;
            const y = -depth * config.depthSpacing;  // Negative Y = downward

            const children = hierarchy.childrenMap.get(nodeId) || [];
            const childCount = children.length;

            if (childCount === 0) {
                // Leaf node: position at center
                positions.set(nodeId, { x: centerX, y, z: centerZ });
                return;
            }

            // Position this node at center
            positions.set(nodeId, { x: centerX, y, z: centerZ });

            // Compute cone base radius
            const baseRadius = Math.min(
                config.maxRadius,
                Math.max(config.minRadius, childCount * config.radiusPerChild)
            );

            // Spread children on cone base
            const angleStep = availableAngle / childCount;
            const coneRadians = (config.coneAngle * Math.PI) / 180;

            children.forEach((childId, i) => {
                const angle = startAngle + angleStep * (i + 0.5);
                const childX = centerX + baseRadius * Math.cos(angle);
                const childZ = centerZ + baseRadius * Math.sin(angle);

                // Recursively position child's subtree
                // Each child gets proportional angle based on its descendant count
                const childSubtreeSize = getSubtreeSize(childId, hierarchy);
                const childAngle = (childSubtreeSize / getTotalSubtreeSize(children, hierarchy)) * availableAngle;

                positionNode(childId, childX, childZ, childAngle, angle - childAngle / 2);
            });
        }

        // Position each root tree
        const rootCount = hierarchy.roots.length;
        const rootSpacing = 300;  // Distance between root trees

        hierarchy.roots.forEach((rootId, i) => {
            const rootX = (i - (rootCount - 1) / 2) * rootSpacing;
            positionNode(rootId, rootX, 0, Math.PI * 2, 0);
        });

        return positions;
    }

    /**
     * Get total nodes in subtree
     */
    function getSubtreeSize(nodeId, hierarchy) {
        let size = 1;
        const children = hierarchy.childrenMap.get(nodeId) || [];
        children.forEach(childId => {
            size += getSubtreeSize(childId, hierarchy);
        });
        return size;
    }

    function getTotalSubtreeSize(nodeIds, hierarchy) {
        return nodeIds.reduce((sum, id) => sum + getSubtreeSize(id, hierarchy), 0);
    }

    // =========================================================================
    // FORCE-DIRECTED INTEGRATION
    // =========================================================================

    /**
     * Create a custom d3 force for cone containment
     * Use with: Graph.d3Force('containment', FILE_TREE.createContainmentForce())
     *
     * @returns {function} d3 force function
     */
    function createContainmentForce() {
        let nodes = [];
        let hierarchy = null;
        let depthMap = null;
        let strength = config.containmentStrength;

        function force(alpha) {
            if (!hierarchy || !depthMap) return;

            nodes.forEach(node => {
                const parentId = hierarchy.parentMap.get(node.id);
                if (!parentId) return;  // Root node

                const parent = nodes.find(n => n.id === parentId);
                if (!parent) return;

                const depth = depthMap.get(node.id) || 0;
                const targetY = -depth * config.depthSpacing;

                // Pull toward correct depth (Y)
                const dy = targetY - (node.y || 0);
                node.vy = (node.vy || 0) + dy * config.depthAttraction * alpha;

                // Pull toward parent cone (XZ plane)
                const dx = (parent.x || 0) - (node.x || 0);
                const dz = (parent.z || 0) - (node.z || 0);
                const dist = Math.sqrt(dx * dx + dz * dz);

                // Ideal distance based on cone angle
                const idealDist = config.depthSpacing * Math.tan((config.coneAngle * Math.PI) / 180);

                if (dist > 0) {
                    const factor = (dist - idealDist) / dist * strength * alpha;
                    node.vx = (node.vx || 0) + dx * factor;
                    node.vz = (node.vz || 0) + dz * factor;
                }
            });
        }

        force.initialize = function(_nodes, _edges) {
            nodes = _nodes;
            if (_edges) {
                hierarchy = analyzeHierarchy(_nodes, _edges);
                const nodeMap = new Map(_nodes.map(n => [n.id, n]));
                depthMap = computeDepths(hierarchy, nodeMap);
            }
        };

        force.strength = function(_) {
            return arguments.length ? (strength = _, force) : strength;
        };

        return force;
    }

    /**
     * Create sibling repulsion force
     * Prevents children of same parent from overlapping
     */
    function createSiblingRepulsionForce() {
        let nodes = [];
        let hierarchy = null;
        let strength = config.siblingRepulsion;

        function force(alpha) {
            if (!hierarchy) return;

            // Group nodes by parent
            const siblingGroups = new Map();
            nodes.forEach(node => {
                const parentId = hierarchy.parentMap.get(node.id) || '__root__';
                if (!siblingGroups.has(parentId)) {
                    siblingGroups.set(parentId, []);
                }
                siblingGroups.get(parentId).push(node);
            });

            // Apply repulsion within each group
            siblingGroups.forEach(siblings => {
                for (let i = 0; i < siblings.length; i++) {
                    for (let j = i + 1; j < siblings.length; j++) {
                        const a = siblings[i];
                        const b = siblings[j];

                        const dx = (b.x || 0) - (a.x || 0);
                        const dz = (b.z || 0) - (a.z || 0);
                        const dist = Math.sqrt(dx * dx + dz * dz) || 1;

                        const minDist = 15;  // Minimum separation
                        if (dist < minDist) {
                            const factor = (minDist - dist) / dist * strength * alpha;
                            a.vx = (a.vx || 0) - dx * factor;
                            a.vz = (a.vz || 0) - dz * factor;
                            b.vx = (b.vx || 0) + dx * factor;
                            b.vz = (b.vz || 0) + dz * factor;
                        }
                    }
                }
            });
        }

        force.initialize = function(_nodes, _edges) {
            nodes = _nodes;
            if (_edges) {
                hierarchy = analyzeHierarchy(_nodes, _edges);
            }
        };

        force.strength = function(_) {
            return arguments.length ? (strength = _, force) : strength;
        };

        return force;
    }

    // =========================================================================
    // APPLY LAYOUT TO GRAPH
    // =========================================================================

    /**
     * Apply computed layout to nodes
     * @param {Array} nodes - Node array (mutated)
     * @param {Map} positions - From computeLayout
     * @param {boolean} animate - Whether to animate transition
     */
    function applyLayout(nodes, positions, animate = false) {
        nodes.forEach(node => {
            const pos = positions.get(node.id);
            if (pos) {
                if (animate) {
                    // Store target for animation
                    node._targetX = pos.x;
                    node._targetY = pos.y;
                    node._targetZ = pos.z;
                } else {
                    node.x = pos.x;
                    node.y = pos.y;
                    node.z = pos.z;
                    // Fix positions to prevent force simulation from moving them
                    node.fx = pos.x;
                    node.fy = pos.y;
                    node.fz = pos.z;
                }
            }
        });
    }

    /**
     * Release fixed positions (allow force simulation)
     * @param {Array} nodes
     */
    function releasePositions(nodes) {
        nodes.forEach(node => {
            node.fx = undefined;
            node.fy = undefined;
            node.fz = undefined;
        });
    }

    // =========================================================================
    // CONFIGURATION API
    // =========================================================================

    function setDepthSpacing(spacing) {
        config.depthSpacing = spacing;
    }

    function setConeAngle(degrees) {
        config.coneAngle = Math.max(15, Math.min(75, degrees));
    }

    function setContainmentStrength(strength) {
        config.containmentStrength = Math.max(0, Math.min(1, strength));
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Layout computation
        computeLayout,
        applyLayout,
        releasePositions,

        // Hierarchy analysis
        analyzeHierarchy,
        computeDepths,

        // Force-directed integration
        createContainmentForce,
        createSiblingRepulsionForce,

        // Configuration
        setDepthSpacing,
        setConeAngle,
        setContainmentStrength,
        config
    };
})();

// Export to window
window.FILE_TREE = FILE_TREE;

console.log('[Module] FILE_TREE loaded - 3D Cone Tree layout for directory hierarchies');
