/**
 * @module AxialLayout
 * @description Physics engine that arranges nodes into a 3D Axial Holarchy ("The Tower").
 * @see visualization_architecture.md
 */

const AxialLayout = (function () {
    'use strict';

    // Configuration for the Tower Layout
    const CONFIG = {
        levelHeight: 100,      // Vertical distance between levels (Z-axis)
        radialConstraint: 500, // Maximum radius for X/Y spread
        centerGravity: 0.1,    // Pull towards the center axis (0,0,z)
        linkDistance: 30,      // Default length of links
        repulsion: -200        // Charge strength (repulsion)
    };

    /**
     * Initializes and runs the force simulation.
     * @param {Object} graphData - The graph data with nodes and links.
     * @param {Object} d3 - The d3 library instance (injected).
     * @returns {Object} The simulation instance.
     */
    function createSimulation(graphData, d3) {
        console.log('AxialLayout: Initializing Tower physics...');

        // 1. Initialize Z-Positions based on Holarchy Level
        // This is the "Axial" part - Z is DETERMINISTIC, not simulated (mostly)
        graphData.nodes.forEach(node => {
            if (node.holarchy) {
                // Map level ID (-3 to 12) to Z-coordinate
                // Shift so L0 (Token) is at Z=0 for the "Floor"
                const levelIndex = node.holarchy.level;
                node.fz = levelIndex * CONFIG.levelHeight; // Fixed Z
                node.z = node.fz; // Initial Z
            }
        });

        // 2. Configure Forces (2D Plane forces + Vertical Links)
        const simulation = d3.forceSimulation(graphData.nodes, 3) // 3D simulation
            .numDimensions(3)

            // Link Force: Connects nodes
            .force('link', d3.forceLink(graphData.links)
                .id(d => d.id)
                .distance(CONFIG.linkDistance)
            )

            // Charge: Nodes repel each other to avoid overlap
            .force('charge', d3.forceManyBody()
                .strength(CONFIG.repulsion)
            )

            // Center: Pulls everything to the middle (Axis)
            .force('center', d3.forceCenter(0, 0, 0)) // Centers the whole mass

            // Radial: Constrains the tower width
            .force('radial', d3.forceRadial(
                0,              // Target radius (0 = axis)
                0,              // X center
                0               // Y center (Z is ignored in standard d3 radial, need check)
            ).strength(CONFIG.centerGravity))

            // Custom Z-Constraint Force: Keeps nodes on their Level Platform
            .force('z-strata', alpha => {
                graphData.nodes.forEach(node => {
                    // Soft constraint: nudge towards target Z
                    // As alpha decays, the nudge gets weaker, but we want it strong?
                    // Actually, for a "Tower", we might want HARD Z constraints.
                    // Let's perform a hard reset of Z every tick for now to ensure perfect stratification.
                    if (node.fz !== undefined) {
                        // Lerp towards fixed Z to allow some "springiness" but ultimate stability
                        node.z += (node.fz - node.z) * 0.5 * alpha;
                    }
                });
            });

        return simulation;
    }

    return {
        CONFIG,
        createSimulation
    };

})();

// Export
if (typeof window !== 'undefined') window.AxialLayout = AxialLayout;
if (typeof module !== 'undefined') module.exports = AxialLayout;
