/**
 * @module HolarchyMapper
 * @description Transforms raw graph nodes into the 16-Level Holarchic Scale.
 * @see visualization_architecture.md
s */

const HolarchyMapper = (function () {

    // The 16 Levels of the Standard Model of Code
    const LEVELS = {
        L12: { id: 12, name: 'Universe', type: 'context' },
        L11: { id: 11, name: 'Domain', type: 'context' },
        L10: { id: 10, name: 'Organization', type: 'context' },
        L9: { id: 9, name: 'Platform', type: 'context' },
        L8: { id: 8, name: 'Ecosystem', type: 'context' },
        L7: { id: 7, name: 'System', type: 'structure' },
        L6: { id: 6, name: 'Package', type: 'structure' },
        L5: { id: 5, name: 'File', type: 'structure' },
        L4: { id: 4, name: 'Container', type: 'structure' },
        L3: { id: 3, name: 'Node', type: 'agent' },
        L2: { id: 2, name: 'Block', type: 'micro' },
        L1: { id: 1, name: 'Statement', type: 'micro' },
        L0: { id: 0, name: 'Token', type: 'micro' },
        L_1: { id: -1, name: 'Character', type: 'substrate' },
        L_2: { id: -2, name: 'Byte', type: 'substrate' },
        L_3: { id: -3, name: 'Bit', type: 'substrate' }
    };

    /**
     * Determines the Holarchic Level of a node based on its properties.
     * @param {Object} node - The graph node.
     * @returns {Object} The Level object (e.g., LEVELS.L5).
     */
    function determineLevel(node) {
        // L7 System: The Root or whole graph context (usually implied, but explicit in some viz)
        if (node.type === 'system' || node.id === 'root') return LEVELS.L7;

        // L6 Package: Directories or Modules maps
        if (node.type === 'directory' || node.type === 'package') return LEVELS.L6;

        // L5 File: Source files
        if (node.type === 'file') return LEVELS.L5;

        // L4 Container: Classes, Structs, Interfaces
        if (node.type === 'class' || node.type === 'struct' || node.type === 'interface') return LEVELS.L4;

        // L3 Node: Functions, Methods (The active agents)
        if (node.type === 'function' || node.type === 'method') return LEVELS.L3;

        // L2 Block: (Future) - If we parse blocks
        if (node.type === 'block') return LEVELS.L2;

        // Fallback for unknown types - treat as Generic Nodes (L3) or catch-all
        return LEVELS.L3;
    }

    /**
     * Enhances a graph with holarchic data.
     * @param {Object} graphData - { nodes, links }
     * @returns {Object} Enhanced graph with .holarchy property on nodes.
     */
    function mapGraph(graphData) {
        console.log('HolarchyMapper: Mapping ' + graphData.nodes.length + ' nodes...');

        graphData.nodes.forEach(node => {
            const level = determineLevel(node);

            node.holarchy = {
                level: level.id,
                levelName: level.name,
                levelType: level.type,
                // height is normalized 0-1 relative to total levels (for Z-axis)
                normalizedHeight: (level.id + 3) / 16,
            };
        });

        return graphData;
    }

    return {
        LEVELS,
        determineLevel,
        mapGraph
    };

})();

// Export for usage
if (typeof window !== 'undefined') window.HolarchyMapper = HolarchyMapper;
if (typeof module !== 'undefined') module.exports = HolarchyMapper;
