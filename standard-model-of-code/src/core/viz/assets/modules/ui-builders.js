/**
 * ═══════════════════════════════════════════════════════════════════════════
 * UI-BUILDERS MODULE - DOM element construction utilities
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Factory functions for building common UI elements: checkboxes, toggles,
 * filter groups, and option selectors.
 *
 * @module UI_BUILDERS
 * @version 1.0.0
 */

window.UI_BUILDERS = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // COUNT COLLECTION
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Collect counts by key from items
     * @param {Array} items - Items to count
     * @param {Function} keyFn - Function to extract key from item
     * @returns {Array} Array of [key, count] pairs sorted by count desc
     */
    function collectCounts(items, keyFn) {
        const counts = new Map();
        items.forEach(item => {
            const key = keyFn(item);
            if (!key) return;
            counts.set(key, (counts.get(key) || 0) + 1);
        });
        return Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CHECKBOX ROW
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build a checkbox row element
     * @param {HTMLElement} container - Parent container
     * @param {string} id - Element ID
     * @param {string} label - Display label
     * @param {number|null} count - Optional count to display
     * @param {boolean} checked - Initial checked state
     * @param {Function} onChange - Callback when checkbox changes
     * @returns {HTMLInputElement} The checkbox input element
     */
    function buildCheckboxRow(container, id, label, count, checked, onChange) {
        const row = document.createElement('div');
        row.className = 'filter-item';

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.id = id;
        input.checked = checked;
        input.onchange = () => onChange(input.checked);

        const text = document.createElement('label');
        text.setAttribute('for', id);
        text.textContent = label;

        const countEl = document.createElement('span');
        countEl.className = 'filter-count';
        countEl.textContent = (typeof count === 'number') ? String(count) : '';

        row.appendChild(input);
        row.appendChild(text);
        if (countEl.textContent) {
            row.appendChild(countEl);
        }
        container.appendChild(row);

        return input;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // FILTER GROUP
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build a filter group with ALL checkbox and individual items
     * @param {string} containerId - Container element ID
     * @param {Array} items - Array of [value, count] pairs
     * @param {Set} stateSet - Set to track selected values
     * @param {Function} onUpdate - Callback when selection changes
     */
    function buildFilterGroup(containerId, items, stateSet, onUpdate) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';

        const allId = `${containerId}-all`;
        let allCheckbox = null;

        allCheckbox = buildCheckboxRow(container, allId, 'ALL', null, true, (checked) => {
            stateSet.clear();
            if (checked) {
                items.forEach(([value]) => stateSet.add(value));
            }
            container.querySelectorAll('input[type="checkbox"]').forEach(box => {
                if (box.id !== allId) box.checked = checked;
            });
            onUpdate();
        });

        items.forEach(([value, count], index) => {
            const id = `${containerId}-${index}`;
            const checked = stateSet.has(value);
            buildCheckboxRow(container, id, value, count, checked, (isChecked) => {
                if (isChecked) {
                    stateSet.add(value);
                } else {
                    stateSet.delete(value);
                }
                const allChecked = items.every(([v]) => stateSet.has(v));
                allCheckbox.checked = allChecked;
                onUpdate();
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DATAMAP TOGGLE
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build a datamap toggle element
     * @param {HTMLElement} container - Parent container
     * @param {string} id - Toggle ID
     * @param {string} label - Display label
     * @param {boolean} checked - Initial checked state
     * @param {number|null} count - Optional count to display
     * @param {Function} onChange - Callback when toggle changes
     * @returns {Object} Object with wrapper, input, and count elements
     */
    function buildDatamapToggle(container, id, label, checked, count, onChange) {
        const wrapper = document.createElement('label');
        wrapper.className = 'datamap-toggle';
        wrapper.setAttribute('data-id', id);

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.checked = checked;
        input.onchange = () => onChange(input.checked);

        const text = document.createElement('span');
        text.textContent = label;

        const countEl = document.createElement('span');
        countEl.className = 'datamap-count';
        countEl.textContent = (typeof count === 'number') ? String(count) : '';

        wrapper.appendChild(input);
        wrapper.appendChild(text);
        wrapper.appendChild(countEl);
        container.appendChild(wrapper);

        return { wrapper, input, count: countEl };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // EXCLUSIVE OPTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build exclusive (radio-like) options using checkboxes
     * @param {string} containerId - Container element ID
     * @param {Array} options - Array of {label, value} objects
     * @param {*} activeValue - Currently active value
     * @param {Function} onSelect - Callback when option is selected
     */
    function buildExclusiveOptions(containerId, options, activeValue, onSelect) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';

        const inputs = [];
        options.forEach((option, index) => {
            const id = `${containerId}-${index}`;
            const input = buildCheckboxRow(
                container,
                id,
                option.label,
                null,
                option.value === activeValue,
                (checked) => {
                    if (!checked) {
                        input.checked = true;
                        return;
                    }
                    inputs.forEach(other => {
                        if (other !== input) other.checked = false;
                    });
                    onSelect(option.value);
                }
            );
            inputs.push(input);
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CHIP GROUP BUILDER - Filter chips with ALL toggle
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build chip buttons for filter groups
     * @param {string} containerId - Container element ID
     * @param {Map} items - Map of key -> count
     * @param {Set} stateSet - Set tracking selected items
     * @param {Function} onUpdate - Callback when selection changes
     */
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

    // ═══════════════════════════════════════════════════════════════════════
    // METADATA CONTROLS - Visibility toggles
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build metadata visibility controls
     * @param {string} containerId - Container element ID
     * @param {Object} metadata - Metadata state object with boolean flags
     */
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
                if (typeof applyMetadataVisibility === 'function') applyMetadataVisibility();
                if (typeof refreshGraph === 'function') refreshGraph();
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // APPEARANCE SLIDERS - Pure UI builder (decoupled from global state)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Build appearance sliders - PURE UI, no global dependencies
     *
     * @param {string} containerId - Container element ID
     * @param {Array} sliderDefs - Array of slider definitions:
     *   { id, label, min, max, step, value, onChange?, description?, className? }
     * @param {Function} globalOnChange - Optional global callback: (sliderId, newValue) => void
     *
     * Supports two patterns:
     * 1. Individual: Each sliderDef has its own onChange(value) handler
     * 2. Global: A single globalOnChange(sliderId, value) handles all
     */
    function buildAppearanceSliders(containerId, sliderDefs, globalOnChange) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';

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
            const safeValue = def.value ?? def.min ?? 0;
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
                // Support both patterns: individual onChange or global
                if (def.onChange) def.onChange(val);
                if (globalOnChange) globalOnChange(def.id, val);
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
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        collectCounts: collectCounts,
        buildCheckboxRow: buildCheckboxRow,
        buildFilterGroup: buildFilterGroup,
        buildDatamapToggle: buildDatamapToggle,
        buildExclusiveOptions: buildExclusiveOptions,
        buildChipGroup: buildChipGroup,
        buildMetadataControls: buildMetadataControls,
        buildAppearanceSliders: buildAppearanceSliders
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.collectCounts = UI_BUILDERS.collectCounts;
window.buildCheckboxRow = UI_BUILDERS.buildCheckboxRow;
window.buildFilterGroup = UI_BUILDERS.buildFilterGroup;
window.buildDatamapToggle = UI_BUILDERS.buildDatamapToggle;
window.buildExclusiveOptions = UI_BUILDERS.buildExclusiveOptions;
window.buildChipGroup = UI_BUILDERS.buildChipGroup;
window.buildMetadataControls = UI_BUILDERS.buildMetadataControls;
// Note: buildAppearanceSliders shim is in app.js (orchestration layer)

console.log('[Module] UI_BUILDERS loaded - 8 functions (appearance sliders decoupled)');
