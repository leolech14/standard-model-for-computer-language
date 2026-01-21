const UPB = (function () {
    'use strict';

    /**
     * UNIVERSAL PROPERTY BINDER - INDEX (AGGREGATOR)
     * Public API for the visualization intelligence layer.
     */

    // Dependency check
    const SCALES = window.UPB_SCALES;
    const ENDPOINTS = window.UPB_ENDPOINTS;
    const BLENDERS = window.UPB_BLENDERS;
    const BINDINGS = window.UPB_BINDINGS;

    if (!SCALES || !ENDPOINTS || !BLENDERS || !BINDINGS) {
        console.error('[UPB] Missing dependencies. Ensure all UPB modules are loaded.');
        return {};
    }

    // Public API
    return {
        // Version
        VERSION: '1.0.0',

        // Modules Access
        SCALES: SCALES,
        ENDPOINTS: ENDPOINTS,
        BLENDERS: BLENDERS,
        BINDINGS: BINDINGS,

        // Quick Aliases for Legacy Compatibility
        DATA_SOURCES: ENDPOINTS.SOURCES,
        VISUAL_TARGETS: ENDPOINTS.TARGETS,

        // Core Actions
        /**
         * Create a new binding
         * @param {string} sourceKey 
         * @param {string} targetKey 
         * @param {object} options 
         */
        bind: function (sourceKey, targetKey, options) {
            return BINDINGS.defaultGraph.bind(sourceKey, targetKey, options);
        },

        /**
         * Remove mappings
         * @param {string} sourceKey 
         * @param {string} targetKey 
         */
        unbind: function (sourceKey, targetKey) {
            return BINDINGS.defaultGraph.unbind(sourceKey, targetKey);
        },

        /**
         * Evaluate visual state for a node
         * @param {object} node 
         */
        evaluate: function (node) {
            return BINDINGS.defaultGraph.evaluate(node);
        },

        /**
         * Bulk evaluation
         * @param {Array} nodes 
         */
        apply: function (nodes) {
            // Note: Data ranges should be set on BINDINGS.defaultGraph before calling this
            // usually by the DataManager
            return BINDINGS.defaultGraph.evaluateAll(nodes);
        },

        /**
         * Initializer - call when data is ready
         */
        init: function (dataRanges) {
            if (dataRanges) {
                BINDINGS.defaultGraph.setDataRanges(dataRanges);
            }
            console.log('[UPB] Universal Property Binder Initialized');
        }
    };

})();

// Export 
if (typeof window !== 'undefined') window.UPB = UPB;
if (typeof module !== 'undefined') module.exports = UPB;
