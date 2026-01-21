const UPB_BLENDERS = (function () {
    'use strict';

    /**
     * UNIVERSAL PROPERTY BINDER - BLENDERS MODULE
     * Functions for combining multiple normalized [0,1] values into one.
     * Used when multiple data sources drive a single visual target.
     */

    const BLENDERS = {
        // Last one wins (Default legacy behavior)
        replace: (values) => {
            if (!values || values.length === 0) return 0;
            return values[values.length - 1];
        },

        // Average of all inputs
        average: (values, weights) => {
            if (!values || values.length === 0) return 0;
            let sum = 0;
            let weightSum = 0;

            for (let i = 0; i < values.length; i++) {
                const w = (weights && weights[i]) || 1;
                sum += values[i] * w;
                weightSum += w;
            }
            return sum / Math.max(1, weightSum);
        },

        // Additive (clamped to 1)
        add: (values, weights) => {
            if (!values || values.length === 0) return 0;
            let sum = 0;
            for (let i = 0; i < values.length; i++) {
                const w = (weights && weights[i]) || 1;
                sum += values[i] * w;
            }
            return Math.min(1, sum);
        },

        // Multiplicative
        multiply: (values, weights) => {
            if (!values || values.length === 0) return 0;
            let product = 1;
            for (let i = 0; i < values.length; i++) {
                // Determine effect strength by weight
                // w=1 -> full effect, w=0 -> no change (multiplier 1)
                const w = (weights && weights[i]) || 1;
                const v = values[i];
                // Interpolate between 1 (no effect) and v (full effect)
                const effectiveValue = 1 - (w * (1 - v));
                product *= effectiveValue;
            }
            return product;
        },

        // Maximum value (dominant signal wins)
        max: (values) => {
            if (!values || values.length === 0) return 0;
            return Math.max(...values);
        },

        // Minimum value
        min: (values) => {
            if (!values || values.length === 0) return 0;
            return Math.min(...values);
        }
    };

    /**
     * Apply blending mode
     */
    function blend(mode, values, weights) {
        const fn = BLENDERS[mode] || BLENDERS.replace;
        return fn(values, weights);
    }

    return {
        BLENDERS,
        blend
    };

})();

// Export
if (typeof window !== 'undefined') window.UPB_BLENDERS = UPB_BLENDERS;
if (typeof module !== 'undefined') module.exports = UPB_BLENDERS;
