const UPB_SCALES = (function () {
    'use strict';

    /**
     * UNIVERSAL PROPERTY BINDER - SCALES MODULE
     * Pure functions for mapping data values to normalized [0,1] ranges.
     */

    const SCALES = {
        // Linear mapping (standard)
        linear: (v, min, max) => (v - min) / (max - min || 1),

        // Logarithmic mapping (good for power-law distributions like LoC)
        log: (v, min, max) => {
            const logMin = Math.log10(Math.max(1, min));
            const logMax = Math.log10(Math.max(1, max));
            const logVal = Math.log10(Math.max(1, v));
            return (logVal - logMin) / (logMax - logMin || 1);
        },

        // Square root mapping (good for area/size to radius)
        sqrt: (v, min, max) => {
            const sqrtMin = Math.sqrt(Math.max(0, min));
            const sqrtMax = Math.sqrt(Math.max(0, max));
            const sqrtVal = Math.sqrt(Math.max(0, v));
            return (sqrtVal - sqrtMin) / (sqrtMax - sqrtMin || 1);
        },

        // Inverse linear (higher value = lower output)
        inverse: (v, min, max) => 1 - ((v - min) / (max - min || 1)),

        // Exponential (emphasizes extremes)
        exp: (v, min, max) => {
            const norm = (v - min) / (max - min || 1);
            return Math.pow(norm, 2);
        },

        // Discrete/Categorical mapping
        // Assumes value is an index or exact match in domain
        discrete: (v, min, max, domain) => {
            if (Array.isArray(domain)) {
                const idx = domain.indexOf(v);
                if (idx === -1) return 0.5; // Fallback
                return idx / Math.max(1, domain.length - 1);
            }
            return 0;
        },

        // Rank-based/Percentile (placeholder - requires sorted dataset context)
        percentile: (v, min, max) => (v - min) / (max - min || 1)
    };

    const SCALE_NAMES = Object.keys(SCALES);

    /**
     * Universal applicator
     * @param {string} name - Name of scale function
     * @param {number} value - Raw value to map
     * @param {number} min - Domain minimum
     * @param {number} max - Domain maximum
     * @param {Array} [domain] - Optional domain for discrete scales
     */
    function applyScale(name, value, min, max, domain) {
        const fn = SCALES[name] || SCALES.linear;
        // Clamp result to [0, 1] for safety
        const result = fn(value, min, max, domain);
        return Math.max(0, Math.min(1, result));
    }

    return {
        SCALES,
        SCALE_NAMES,
        applyScale
    };
})();

// Export to window for browser
if (typeof window !== 'undefined') window.UPB_SCALES = UPB_SCALES;
if (typeof module !== 'undefined') module.exports = UPB_SCALES;
