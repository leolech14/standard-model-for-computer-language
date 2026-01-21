/**
 * SIDEBAR MODULE
 *
 * Manages sidebar controls including color presets, layout presets,
 * physics controls, appearance controls, filters, and panel updates.
 *
 * Depends on: ANIM (for layouts), REFRESH (for throttled updates)
 *
 * Usage:
 *   SIDEBAR.init()                         // Initialize after DOM ready
 *   SIDEBAR.setColorMode('tier')           // Change color mode
 *   SIDEBAR.setLayout('force')             // Change layout
 *   SIDEBAR.setPhysicsPreset('tight')      // Apply physics preset
 *   SIDEBAR.updateStats(nodes, edges)      // Update stat displays
 */

// Note: Using window assignment instead of const to avoid duplicate declaration with app.js
window.SIDEBAR = (function () {
    'use strict';

    // =========================================================================
    // STATE
    // =========================================================================

    let _refreshTimer = null;
    let _bound = false;

    // =========================================================================
    // INITIALIZATION
    // =========================================================================

    /**
     * Initialize sidebar - call after DOM is ready
     */
    function init() {
        if (_bound) return;
        _bound = true;

        // Initialize unified state manager first
        if (typeof VIS_STATE !== 'undefined') {
            VIS_STATE.init();
        }

        _bindSectionHeaders();
        _bindColorPresets();
        _bindLayoutPresets();
        _bindPhysicsControls();
        _bindAppearanceControls();
        _bindActionButtons();
        initSchemeNavigator();
        initViewModeToggle();
        initSectionResize();   // Enable vertical section resizing
        initSidebarResize();   // Enable horizontal sidebar resizing

        // Sync UI to initial state
        if (typeof VIS_STATE !== 'undefined') {
            VIS_STATE.syncUIFromState();
        }

        console.log('[SIDEBAR] Initialized');
    }

    // =========================================================================
    // SECTION COLLAPSE/EXPAND
    // =========================================================================

    function _bindSectionHeaders() {
        document.querySelectorAll('.section-header[data-section]').forEach(header => {
            header.addEventListener('click', () => {
                const sectionId = header.dataset.section;
                const content = document.getElementById(`section-${sectionId}`);
                if (!content) return;

                const isCollapsed = header.classList.toggle('collapsed');
                content.classList.toggle('collapsed', isCollapsed);
            });
        });
    }

    // =========================================================================
    // COLOR PRESETS (TIER, FAMILY, LAYER, RING, FILE, FLOW)
    // =========================================================================

    // =========================================================================
    // COLOR PRESETS: SMART SIDEBAR CONFIGURATION
    // =========================================================================

    const PRESET_CONFIG = [
        {
            category: 'Architecture',
            presets: [
                { id: 'tier', label: 'Tier', desc: 'Auto-detected architectural height' },
                { id: 'layer', label: 'Layer', desc: 'Business logic strata' },
                { id: 'subsystem', label: 'Subsystem', desc: 'Functional domain grouping' },
                { id: 'boundary_score', label: 'Boundary', desc: 'Internal vs External (1-9)' },
                { id: 'phase', label: 'Phase', desc: 'Data-Logic-Org-Exec (MIPO)' }
            ]
        },
        {
            category: 'Taxonomy',
            presets: [
                { id: 'atom', label: 'Atom', desc: 'Function, Class, Module types' },
                { id: 'family', label: 'Family', desc: 'Logic, Data, Execution' },
                { id: 'role', label: 'Role', desc: 'Service, Repo, Controller' },
                { id: 'roleCategory', label: 'Role Cat', desc: 'Query, Command, Event' },
                { id: 'fileType', label: 'File Type', desc: 'Extension-based coloring' }
            ]
        },
        {
            category: 'Metrics',
            presets: [
                { id: 'complexity', label: 'Complexity', desc: 'Cyclomatic complexity' },
                { id: 'loc', label: 'LOC', desc: 'Lines of Code' },
                { id: 'fan_in', label: 'Fan-In', desc: 'Incoming dependencies' },
                { id: 'fan_out', label: 'Fan-Out', desc: 'Outgoing dependencies' },
                { id: 'trust', label: 'Trust', desc: 'Detection confidence' }
            ]
        },
        {
            category: 'RPBL DNA',
            presets: [
                { id: 'responsibility', label: 'Responsibility', desc: 'SRP alignment (1-9)' },
                { id: 'purity', label: 'Purity', desc: 'Side-effect profile (1-9)' },
                { id: 'lifecycle_score', label: 'Lifecycle', desc: 'Static vs Dynamic (1-9)' },
                { id: 'state', label: 'State', desc: 'Stateful vs Stateless' },
                { id: 'visibility', label: 'Visibility', desc: 'Public vs Private' }
            ]
        },
        {
            category: 'Topology',
            presets: [
                { id: 'centrality', label: 'Centrality', desc: 'Graph importance' },
                { id: 'rank', label: 'PageRank', desc: 'Algorithmic influence' }, // mapped to centrality logic or similar
                { id: 'ring', label: 'Ring', desc: 'Concentric architecture rings' },
                { id: 'flow', label: 'Flow', desc: 'Dependency direction' }
            ]
        },
        {
            category: 'Evolution',
            presets: [
                { id: 'churn', label: 'Churn', desc: 'Change frequency (Simulated)' },
                { id: 'age', label: 'Age', desc: 'Time since creation (Simulated)' }
            ]
        }
    ];

    // =========================================================================
    // SCHEME NAVIGATOR: 33 Named Color Schemes
    // =========================================================================

    const SCHEME_CONFIG = [
        // PART A: Famous Scientific (15)
        { category: 'Sequential', schemes: ['viridis', 'plasma', 'magma', 'inferno', 'cividis', 'turbo', 'mako', 'rocket'] },
        { category: 'Diverging', schemes: ['coolwarm', 'spectral'] },
        { category: 'Thematic', schemes: ['thermal', 'nightvision', 'ocean', 'terrain', 'electric'] },

        // PART B: Role-Semantic (18 key roles)
        { category: 'Access', schemes: ['query', 'finder'] },
        { category: 'Mutation', schemes: ['command', 'creator', 'destroyer'] },
        { category: 'Construction', schemes: ['factory'] },
        { category: 'Storage', schemes: ['repository', 'cache'] },
        { category: 'Control', schemes: ['service', 'orchestrator'] },
        { category: 'Validation', schemes: ['validator', 'guard'] },
        { category: 'Transform', schemes: ['transformer', 'parser'] },
        { category: 'Events', schemes: ['handler', 'emitter'] },
        { category: 'Support', schemes: ['utility', 'lifecycle'] },

        // PART C: OKLCH Geometry (Mathematical paths through color space)
        { category: 'Loops', schemes: ['rainbow-loop', 'rainbow-bright', 'rainbow-dark'] },
        { category: 'Arcs', schemes: ['arc-warm', 'arc-cool', 'arc-nature'] },
        { category: 'Spirals', schemes: ['spiral-up', 'spiral-down', 'spiral-chroma'] },
        { category: 'Waves', schemes: ['wave-lightness', 'wave-chroma', 'pulse'] },
        { category: 'Ramps', schemes: ['ramp-hue', 'ramp-lightness', 'ramp-chroma'] },
        { category: 'Paths', schemes: ['helix', 'convergent', 'divergent', 'bicone'] }
    ];

    function _bindColorPresets() {
        // Init Smart Sidebar
        const container = document.getElementById('section-color');
        if (!container) return;

        // Clear existing static buttons if any (except header)
        const contentDiv = container.querySelector('.section-content');
        if (contentDiv) {
            contentDiv.innerHTML = ''; // Rebuild from scratch
            renderSmartSidebar(contentDiv);
        }
    }

    function renderSmartSidebar(container) {
        // Search bar
        const searchContainer = document.createElement('div');
        searchContainer.style.cssText = 'padding-bottom: 8px; margin-bottom: 8px; border-bottom: 1px solid var(--border);';
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Filter Presets...';
        searchInput.style.cssText = 'width: 100%; background: rgba(0,0,0,0.2); border: 1px solid var(--border); padding: 4px 8px; color: var(--text); border-radius: 4px; font-size: 10px;';

        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('.preset-category').forEach(cat => {
                let hasMatch = false;
                cat.querySelectorAll('.btn').forEach(btn => {
                    const match = btn.textContent.toLowerCase().includes(term) || btn.title.toLowerCase().includes(term);
                    btn.style.display = match ? 'block' : 'none';
                    if (match) hasMatch = true;
                });
                cat.style.display = hasMatch ? 'block' : 'none';
            });
        });

        searchContainer.appendChild(searchInput);
        container.appendChild(searchContainer);

        // Render Categories
        PRESET_CONFIG.forEach(section => {
            const catDiv = document.createElement('div');
            catDiv.className = 'preset-category';
            catDiv.style.marginBottom = '12px';

            const catTitle = document.createElement('div');
            catTitle.textContent = section.category;
            catTitle.style.cssText = 'font-size: 9px; opacity: 0.5; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;';
            catDiv.appendChild(catTitle);

            const grid = document.createElement('div');
            grid.className = 'btn-grid btn-grid-3'; // Default to 3-col

            section.presets.forEach(p => {
                const btn = document.createElement('button');
                btn.className = 'btn color-btn';
                btn.textContent = p.label;
                btn.title = p.desc;
                btn.dataset.preset = p.id;

                // Click handler - VIS_STATE.syncUIFromState() handles active states
                btn.addEventListener('click', () => {
                    setColorMode(p.id);
                });

                grid.appendChild(btn);
            });

            catDiv.appendChild(grid);
            container.appendChild(catDiv);
        });
    }

    // =========================================================================
    // SCHEME NAVIGATOR RENDERER
    // =========================================================================

    function renderSchemeNavigator(container) {
        if (!container) return;
        container.innerHTML = '';

        // Search bar
        const searchContainer = document.createElement('div');
        searchContainer.style.cssText = 'padding-bottom: 8px; margin-bottom: 8px; border-bottom: 1px solid var(--border);';
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Filter Schemes...';
        searchInput.style.cssText = 'width: 100%; background: rgba(0,0,0,0.2); border: 1px solid var(--border); padding: 4px 8px; color: var(--text); border-radius: 4px; font-size: 10px;';

        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('.scheme-category').forEach(cat => {
                let hasMatch = false;
                cat.querySelectorAll('.scheme-btn').forEach(btn => {
                    const match = btn.dataset.scheme.toLowerCase().includes(term) ||
                        (btn.title && btn.title.toLowerCase().includes(term));
                    btn.style.display = match ? 'inline-block' : 'none';
                    if (match) hasMatch = true;
                });
                cat.style.display = hasMatch ? 'block' : 'none';
            });
        });

        // Clear button
        const clearBtn = document.createElement('button');
        clearBtn.textContent = 'Clear';
        clearBtn.title = 'Remove scheme, use default colors';
        clearBtn.style.cssText = 'margin-left: 8px; padding: 4px 8px; font-size: 9px; background: rgba(255,100,100,0.2); border: 1px solid rgba(255,100,100,0.3); color: var(--text); border-radius: 4px; cursor: pointer;';
        clearBtn.addEventListener('click', clearColorScheme);

        searchContainer.appendChild(searchInput);
        searchContainer.appendChild(clearBtn);
        container.appendChild(searchContainer);

        // Render Categories
        SCHEME_CONFIG.forEach(section => {
            const catDiv = document.createElement('div');
            catDiv.className = 'scheme-category';
            catDiv.style.marginBottom = '12px';

            const catTitle = document.createElement('div');
            catTitle.textContent = section.category;
            catTitle.style.cssText = 'font-size: 9px; opacity: 0.5; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;';
            catDiv.appendChild(catTitle);

            const grid = document.createElement('div');
            grid.className = 'scheme-grid';
            grid.style.cssText = 'display: flex; flex-wrap: wrap; gap: 4px;';

            section.schemes.forEach(schemeName => {
                const btn = document.createElement('button');
                btn.className = 'scheme-btn';
                btn.dataset.scheme = schemeName;

                // Get scheme info from COLOR engine
                let info = { name: schemeName, semantic: '' };
                if (typeof COLOR !== 'undefined' && COLOR.getSchemeInfo) {
                    info = COLOR.getSchemeInfo(schemeName);
                }

                btn.title = info.semantic || schemeName;

                // Create clean color swatches (5 stops) instead of ugly gradient
                const swatchContainer = document.createElement('div');
                swatchContainer.className = 'scheme-swatches';

                if (typeof COLOR !== 'undefined' && COLOR.getSchemeColor) {
                    // Sample 5 colors from the scheme path
                    [0, 0.25, 0.5, 0.75, 1].forEach(t => {
                        const swatch = document.createElement('span');
                        swatch.className = 'scheme-swatch';
                        swatch.style.backgroundColor = COLOR.getSchemeColor(schemeName, t);
                        swatchContainer.appendChild(swatch);
                    });
                }

                btn.appendChild(swatchContainer);

                // Label below swatches
                const label = document.createElement('span');
                label.className = 'scheme-label';
                label.textContent = info.name;
                btn.appendChild(label);

                // Click handler - VIS_STATE.syncUIFromState() handles active states
                btn.addEventListener('click', () => {
                    applyColorScheme(schemeName);
                });

                grid.appendChild(btn);
            });

            catDiv.appendChild(grid);
            container.appendChild(catDiv);
        });
    }

    /**
     * Apply a named color scheme (palette)
     *
     * NEW BEHAVIOR (via VIS_STATE):
     * - Palette is "armed" but does NOT auto-switch colorBy mode
     * - Palette only visually applies when colorBy is an interval mode
     * - When user switches to interval mode, the armed palette becomes active
     */
    function applyColorScheme(schemeName) {
        // Use VIS_STATE for unified state management
        if (typeof VIS_STATE !== 'undefined') {
            VIS_STATE.setPalette(schemeName);
            return;
        }

        // Fallback for when VIS_STATE not loaded yet
        if (typeof COLOR !== 'undefined' && COLOR.applyScheme) {
            COLOR.applyScheme(schemeName);
        }

        try {
            localStorage.setItem('collider_scheme', schemeName);
        } catch (e) { /* ignore */ }

        _refreshGraphColors();
        console.log('[SIDEBAR] Applied scheme:', schemeName);
    }

    /**
     * Clear active scheme, return to default interval colors
     */
    function clearColorScheme() {
        // Use VIS_STATE for unified state management
        if (typeof VIS_STATE !== 'undefined') {
            VIS_STATE.setPalette(null);
            return;
        }

        // Fallback
        if (typeof COLOR !== 'undefined' && COLOR.applyScheme) {
            COLOR.applyScheme(null);
        }

        try {
            localStorage.removeItem('collider_scheme');
        } catch (e) { /* ignore */ }

        document.querySelectorAll('.scheme-btn').forEach(b => b.classList.remove('active'));

        _refreshGraphColors();

        console.log('[SIDEBAR] Cleared color scheme');
    }

    /**
     * Internal: Refresh all node colors and re-render the graph
     */
    function _refreshGraphColors() {
        if (typeof Graph === 'undefined' || !Graph) return;

        // Get current nodes from DataManager or Graph
        const DM = window.DM;
        const nodes = DM ? DM.getNodes() : (Graph.graphData ? Graph.graphData().nodes : []);

        // Recompute colors using current mode
        if (typeof window.applyNodeColors === 'function' && nodes.length > 0) {
            window.applyNodeColors(nodes);
        }

        // Trigger WebGL re-render
        Graph.nodeColor(Graph.nodeColor());

        // Also refresh edges if in gradient mode
        if (typeof window.refreshGradientEdgeColors === 'function') {
            window.refreshGradientEdgeColors();
        }
    }

    /**
     * Initialize scheme navigator in sidebar
     */
    function initSchemeNavigator() {
        const container = document.getElementById('section-schemes');
        if (container) {
            renderSchemeNavigator(container);
        }

        // Setup collapsible header for schemes panel
        const collapsibleHeaders = document.querySelectorAll('.info-panel-header.collapsible');
        collapsibleHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const targetId = header.dataset.target;
                const content = document.getElementById(targetId);
                if (content) {
                    const isCollapsed = content.classList.toggle('collapsed');
                    header.classList.toggle('collapsed', isCollapsed);
                }
            });
        });

        // Setup color mode buttons (for right sidebar)
        const colorBtns = document.querySelectorAll('.color-panel .color-btn');
        colorBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const preset = btn.dataset.preset;
                if (!preset) return;

                // Apply color mode via VIS_STATE (handles UI sync)
                setColorMode(preset);
            });
        });

        // NOTE: Saved preferences are now loaded by VIS_STATE.init()
        // UI sync is handled by VIS_STATE.syncUIFromState()
    }

    // =========================================================================
    // VIEW MODE TOGGLE (ATOMS vs FILES)
    // =========================================================================

    let _currentViewMode = 'atoms';
    let _deferredViewMode = null;  // Stores mode to apply after data loads

    /**
     * Initialize the view mode toggle (Atoms vs Files)
     * Note: Only sets up event handlers and button visual state.
     * Actual mode application for 'files' is deferred until data is loaded.
     */
    function initViewModeToggle() {
        const toggle = document.getElementById('view-mode-toggle');
        if (!toggle) return;

        const buttons = toggle.querySelectorAll('.view-mode-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = btn.dataset.mode;
                if (!mode || mode === _currentViewMode) return;

                setViewMode(mode);
            });
        });

        // Load saved preference - but only update button state, defer actual mode switch
        try {
            const saved = localStorage.getItem('collider_view_mode');
            if (saved && (saved === 'atoms' || saved === 'files')) {
                // Update button visual state immediately
                buttons.forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.mode === saved);
                });
                _currentViewMode = saved;

                // If files mode, defer application until data is loaded
                if (saved === 'files') {
                    _deferredViewMode = 'files';
                    console.log('[SIDEBAR] Files mode saved - deferring until data loads');
                }
            }
        } catch (e) { /* ignore */ }
    }

    /**
     * Apply deferred view mode after data is loaded
     * Call this from initGraph() after DM.init() completes
     */
    function applyDeferredViewMode() {
        if (_deferredViewMode === 'files') {
            console.log('[SIDEBAR] Applying deferred files mode now that data is loaded');
            _deferredViewMode = null;  // Clear to prevent re-application

            // Apply files mode (data is now available)
            if (typeof FILE_VIZ !== 'undefined') {
                FILE_VIZ.buildFileGraph();
                window.GRAPH_MODE = 'files';
                FILE_VIZ.graphMode = 'files';
                FILE_VIZ.setMode('map');
                FILE_VIZ.setEnabled(true);
                console.log('[SIDEBAR] View mode: FILES - showing file nodes');

                if (typeof showToast === 'function') {
                    showToast('FILE VIEW: Each node is a file. Click to expand.');
                }
            }
        }
    }

    /**
     * Set the view mode (atoms or files)
     */
    function setViewMode(mode) {
        if (mode !== 'atoms' && mode !== 'files') return;
        _currentViewMode = mode;

        // Update button states
        const buttons = document.querySelectorAll('.view-mode-btn');
        buttons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });

        // Save preference
        try {
            localStorage.setItem('collider_view_mode', mode);
        } catch (e) { /* ignore */ }

        // Apply view mode via FILE_VIZ module
        if (mode === 'files') {
            // Switch to file-nodes view
            if (typeof FILE_VIZ !== 'undefined') {
                // Build the file graph first (required before switching mode)
                FILE_VIZ.buildFileGraph();
                window.GRAPH_MODE = 'files';
                FILE_VIZ.graphMode = 'files';
                FILE_VIZ.setMode('map');
                FILE_VIZ.setEnabled(true);
            } else if (typeof window.GRAPH_MODE !== 'undefined') {
                window.GRAPH_MODE = 'files';
                if (typeof buildFileGraph === 'function') buildFileGraph(null);
                if (typeof refreshGraph === 'function') refreshGraph();
            }
            console.log('[SIDEBAR] View mode: FILES - showing file nodes');
        } else {
            // Switch to atoms view
            if (typeof FILE_VIZ !== 'undefined') {
                FILE_VIZ.graphMode = 'atoms';
                FILE_VIZ.setEnabled(false);
            } else if (typeof window.GRAPH_MODE !== 'undefined') {
                window.GRAPH_MODE = 'atoms';
                if (typeof refreshGraph === 'function') refreshGraph();
            }
            console.log('[SIDEBAR] View mode: ATOMS - showing individual atoms');
        }

        // Show toast notification
        if (typeof showToast === 'function') {
            const msg = mode === 'files'
                ? 'FILE VIEW: Each node is a file. Click to expand.'
                : 'ATOM VIEW: Each node is a code element.';
            showToast(msg);
        }
    }

    /**
     * Get current view mode
     */
    function getViewMode() {
        return _currentViewMode;
    }

    function setColorMode(mode) {
        // Use VIS_STATE for unified state management
        if (typeof VIS_STATE !== 'undefined') {
            VIS_STATE.setColorBy(mode);
            return;
        }

        // Fallback for when VIS_STATE not loaded yet
        if (typeof APPEARANCE_STATE !== 'undefined') {
            APPEARANCE_STATE.colorMode = mode;
            APPEARANCE_STATE.currentPreset = mode;
        }

        if (typeof setNodeColorMode === 'function') {
            setNodeColorMode(mode);
        }

        // Handle flow mode specially
        if (mode === 'flow') {
            if (typeof flowMode !== 'undefined' && !flowMode && typeof toggleFlowMode === 'function') {
                toggleFlowMode();
            }
        } else if (typeof flowMode !== 'undefined' && flowMode && typeof disableFlowMode === 'function') {
            disableFlowMode();
        }

        if (typeof window !== 'undefined' && typeof window.refreshGradientEdgeColors === 'function') {
            window.refreshGradientEdgeColors();
        }

        if (typeof renderAllLegends === 'function') {
            renderAllLegends();
        }

        console.log('[SIDEBAR] Color mode:', mode);
    }

    // =========================================================================
    // LAYOUT PRESETS (FORCE, RADIAL, ORBITAL, SPHERE, GRID, SPIRAL)
    // =========================================================================

    function _bindLayoutPresets() {
        const container = document.getElementById('section-layout');
        if (!container) return;

        container.querySelectorAll('.btn[data-layout]').forEach(btn => {
            btn.addEventListener('click', () => {
                const layout = btn.dataset.layout;
                setLayout(layout);

                // Update active state
                container.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }

    function setLayout(layout) {
        // Prefer ANIM module if available
        if (typeof ANIM !== 'undefined' && ANIM.applyLayout) {
            ANIM.applyLayout(layout, true);
        } else if (typeof applyLayoutPreset === 'function') {
            applyLayoutPreset(layout, true);
        }
        console.log('[SIDEBAR] Layout:', layout);
    }

    // =========================================================================
    // PHYSICS CONTROLS
    // =========================================================================

    const PHYSICS_PRESETS = {
        default: { charge: -120, link: 50, center: 0.05, damping: 0.4 },
        tight: { charge: -80, link: 30, center: 0.1, damping: 0.5 },
        loose: { charge: -200, link: 80, center: 0.02, damping: 0.3 },
        explosive: { charge: -400, link: 120, center: 0.01, damping: 0.2 }
    };

    function _bindPhysicsControls() {
        // Charge (repulsion)
        _bindSlider('physics-charge', (val) => {
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.d3Force('charge').strength(val);
                Graph.d3ReheatSimulation();
            }
        });

        // Link distance
        _bindSlider('physics-link', (val) => {
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.d3Force('link').distance(val);
                Graph.d3ReheatSimulation();
            }
        });

        // Center pull
        _bindSlider('physics-center', (val) => {
            if (typeof Graph !== 'undefined' && Graph) {
                const center = Graph.d3Force('center');
                if (center && center.strength) center.strength(val);
                Graph.d3ReheatSimulation();
            }
        });

        // Damping (velocity decay)
        _bindSlider('physics-damping', (val) => {
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.d3VelocityDecay(val);
                Graph.d3ReheatSimulation();
            }
        });

        // Physics presets
        const container = document.getElementById('section-physics');
        if (container) {
            container.querySelectorAll('.btn[data-physics]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const preset = btn.dataset.physics;
                    setPhysicsPreset(preset);
                });
            });
        }
    }

    function setPhysicsPreset(preset) {
        const p = PHYSICS_PRESETS[preset];
        if (!p) return;

        // Update sliders
        _setSliderValue('physics-charge', p.charge);
        _setSliderValue('physics-link', p.link);
        _setSliderValue('physics-center', p.center);
        _setSliderValue('physics-damping', p.damping);

        // Apply to graph
        if (typeof Graph !== 'undefined' && Graph) {
            Graph.d3Force('charge').strength(p.charge);
            Graph.d3Force('link').distance(p.link);
            const center = Graph.d3Force('center');
            if (center && center.strength) center.strength(p.center);
            Graph.d3VelocityDecay(p.damping);
            Graph.d3ReheatSimulation();
        }

        console.log('[SIDEBAR] Physics preset:', preset);
    }

    // =========================================================================
    // APPEARANCE CONTROLS
    // =========================================================================

    function _bindAppearanceControls() {
        // Auto-bind all sliders that have a matching numeric input
        // This covers cfg-node-size, cfg-node-opacity, etc.
        const ranges = document.querySelectorAll('input[type="range"]');
        ranges.forEach(range => {
            if (range.id) {
                _bindSlider(range.id, (val) => {
                    // Dispatch to specific handlers based on ID
                    // This creates a centralized handler dispatch
                    _handleSliderChange(range.id, val);
                });
            }
        });

        // Toggles
        _bindToggle('cfg-toggle-labels', (active) => {
            if (typeof VIS_FILTERS !== 'undefined' && VIS_FILTERS.metadata) {
                VIS_FILTERS.metadata.showLabels = active;
            }
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.nodeLabel(n => active ? n.name : null);
            }
        });

        _bindToggle('cfg-toggle-highlight', (active) => {
            // Handled by VIS_STATE or interactions
        });

        _bindToggle('cfg-toggle-pulse', (active) => {
            if (typeof ANIM !== 'undefined') {
                ANIM.togglePulse(active);
            }
        });

        _bindToggle('cfg-toggle-depth', (active) => {
            // 3D shading toggle
        });

        _bindToggle('cfg-toggle-arrows', (active) => {
            if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.showArrows = active;
            if (typeof Graph !== 'undefined' && Graph) {
                Graph.linkDirectionalArrowLength(active ? 6 : 0);
                Graph.linkDirectionalArrowRelPos(0.9);
            }
        });

        _bindToggle('cfg-toggle-gradient', (active) => {
            if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.gradientEdges = active;
            if (typeof applyEdgeMode === 'function') applyEdgeMode();
            window.refreshGradientEdgeColors && window.refreshGradientEdgeColors();
        });
    }

    // Centralized handler for all sliders
    function _handleSliderChange(id, val) {
        // Map ID to logic
        switch (id) {
            // Node Config
            case 'cfg-node-size':
                if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.nodeScale = val;
                if (typeof Graph !== 'undefined' && Graph) Graph.nodeVal(n => (n.val || 1) * val);
                break;
            case 'cfg-node-opacity':
                if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.nodeOpacity = val;
                if (typeof applyEdgeMode === 'function') applyEdgeMode(); // Re-apply colors with new alpha
                break;
            case 'cfg-node-res':
                if (typeof Graph !== 'undefined' && Graph) Graph.nodeResolution(val);
                break;
            case 'cfg-label-size':
                // Note: 3d-force-graph doesn't have a direct dynamic label size multiplier, 
                // but we can trigger a re-render or update state.
                break;

            // Edge Config    
            case 'cfg-edge-opacity':
                if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.edgeOpacity = val;
                if (typeof applyEdgeMode === 'function') applyEdgeMode();
                break;
            case 'cfg-edge-width':
                if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.edgeWidth = val;
                if (typeof Graph !== 'undefined' && Graph) Graph.linkWidth(val);
                break;
            case 'cfg-edge-curve':
                if (typeof APPEARANCE_STATE !== 'undefined') APPEARANCE_STATE.edgeCurvature = val;
                if (typeof Graph !== 'undefined' && Graph) Graph.linkCurvature(val);
                break;
            case 'cfg-particle-speed':
                if (typeof Graph !== 'undefined' && Graph) Graph.linkDirectionalParticleSpeed(val);
                break;
            case 'cfg-particle-count':
                if (typeof Graph !== 'undefined' && Graph) Graph.linkDirectionalParticles(val);
                break;

            // Physics (Updated IDs)
            case 'physics-charge':
                if (typeof Graph !== 'undefined' && Graph) {
                    Graph.d3Force('charge').strength(val);
                    Graph.d3ReheatSimulation();
                }
                break;
            case 'physics-link':
                if (typeof Graph !== 'undefined' && Graph) {
                    Graph.d3Force('link').distance(val);
                    Graph.d3ReheatSimulation();
                }
                break;
        }
    }


    // =========================================================================
    // ACTION BUTTONS
    // =========================================================================

    function _bindActionButtons() {
        // Reset view
        const resetBtn = document.getElementById('btn-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                if (typeof Graph !== 'undefined' && Graph) {
                    Graph.cameraPosition({ x: 0, y: 0, z: 500 }, { x: 0, y: 0, z: 0 }, 1000);
                }
            });
        }

        // Screenshot
        const screenshotBtn = document.getElementById('btn-screenshot');
        if (screenshotBtn) {
            screenshotBtn.addEventListener('click', () => {
                if (typeof takeScreenshot === 'function') {
                    takeScreenshot();
                } else if (typeof Graph !== 'undefined' && Graph) {
                    const link = document.createElement('a');
                    link.download = 'collider-screenshot.png';
                    link.href = Graph.renderer().domElement.toDataURL('image/png');
                    link.click();
                }
            });
        }

        // Toggle 2D
        const toggle2dBtn = document.getElementById('btn-2d');
        if (toggle2dBtn) {
            toggle2dBtn.addEventListener('click', () => {
                if (typeof toggle2DMode === 'function') toggle2DMode();
            });
        }

        // Freeze simulation
        const freezeBtn = document.getElementById('btn-freeze');
        if (freezeBtn) {
            freezeBtn.addEventListener('click', () => {
                if (typeof toggleFreeze === 'function') {
                    toggleFreeze();
                } else if (typeof Graph !== 'undefined' && Graph) {
                    // Simple freeze toggle
                    const alpha = Graph.d3AlphaTarget();
                    Graph.d3AlphaTarget(alpha === 0 ? 0.3 : 0);
                    freezeBtn.classList.toggle('active', alpha !== 0);
                }
            });
        }
    }

    // =========================================================================
    // FILTER CHIPS
    // =========================================================================

    function populateFilterChips(data) {
        if (!data || !data.nodes) return;

        // Tiers
        const tiers = [...new Set(data.nodes.map(n => n.tier).filter(Boolean))].sort();
        _populateChipGroup('filter-tiers', tiers, 'tiers');

        // Rings
        const rings = [...new Set(data.nodes.map(n => n.ring).filter(Boolean))].sort();
        _populateChipGroup('filter-rings', rings, 'rings');

        // Edge types
        const edgeTypes = [...new Set(data.links?.map(e => e.type).filter(Boolean) || [])].sort();
        _populateChipGroup('filter-edges', edgeTypes, 'edges');
    }

    function _populateChipGroup(containerId, items, filterKey) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        items.forEach(item => {
            const chip = document.createElement('div');
            chip.className = 'chip';
            chip.textContent = item;
            chip.addEventListener('click', () => {
                const isActive = chip.classList.toggle('active');
                setFilter(filterKey, item, !isActive); // active = filtered OUT
                _scheduleRefresh();
            });
            container.appendChild(chip);
        });
    }

    function setFilter(dimension, value, visible) {
        if (typeof VIS_FILTERS === 'undefined') return;
        const set = VIS_FILTERS[dimension];
        if (!set) return;

        if (visible) {
            set.delete(value); // Remove from filter = show
        } else {
            set.add(value);    // Add to filter = hide
        }
    }

    // =========================================================================
    // HOVER PANEL
    // =========================================================================

    function showHoverPanel(node) {
        const panel = document.getElementById('hover-panel');
        if (!panel || !node) return;

        const setField = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value || '--';
        };

        setField('hover-name', node.name);
        setField('hover-kind', node.kind || node.type || 'unknown');
        setField('hover-atom', node.atom);
        setField('hover-family', node.family || (node.atom ? node.atom.split('.')[0] : null));
        setField('hover-ring', node.ring);
        setField('hover-tier', node.tier);
        setField('hover-role', node.role);

        const fileEl = document.getElementById('hover-file');
        if (fileEl) fileEl.textContent = node.file_path || node.file || '';

        panel.classList.add('visible');
    }

    function hideHoverPanel() {
        const panel = document.getElementById('hover-panel');
        if (panel) panel.classList.remove('visible');
    }

    // =========================================================================
    // SELECTION PANEL
    // =========================================================================

    function updateSelectionPanel(selectedNodes) {
        const panel = document.getElementById('selection-panel');
        const title = document.getElementById('selection-title');
        const list = document.getElementById('selection-list');
        const clearBtn = document.getElementById('selection-clear');

        if (!panel || !list) return;

        if (!selectedNodes || selectedNodes.length === 0) {
            panel.classList.remove('visible');
            return;
        }

        if (title) title.textContent = `SELECTED (${selectedNodes.length})`;

        list.innerHTML = selectedNodes.slice(0, 20).map(n =>
            `<div class="selection-item">${n.name || n.id}</div>`
        ).join('');

        if (selectedNodes.length > 20) {
            list.innerHTML += `<div class="selection-item" style="opacity:0.5">...and ${selectedNodes.length - 20} more</div>`;
        }

        panel.classList.add('visible');

        // Bind clear button
        if (clearBtn) {
            clearBtn.onclick = () => {
                if (typeof SELECT !== 'undefined') {
                    SELECT.clear();
                } else if (typeof clearSelection === 'function') {
                    clearSelection();
                }
                panel.classList.remove('visible');
            };
        }
    }

    // =========================================================================
    // STATS DISPLAY
    // =========================================================================

    function updateStats(nodes, edges, entropy) {
        const nodeEl = document.getElementById('stat-nodes');
        const edgeEl = document.getElementById('stat-edges');
        const entropyEl = document.getElementById('stat-entropy');

        if (nodeEl) nodeEl.textContent = nodes?.toLocaleString() || '0';
        if (edgeEl) edgeEl.textContent = edges?.toLocaleString() || '0';
        if (entropyEl) entropyEl.textContent = entropy?.toFixed(2) || '--';
    }

    // =========================================================================
    // HELPER: SLIDERS
    // =========================================================================

    function _bindSlider(id, callback) {
        const slider = document.getElementById(id);
        const numberInput = document.getElementById(`${id}-num`);

        // Handle deprecated value span if it exists (for backward compat)
        const valSpan = document.getElementById(`${id}-val`);

        if (!slider) return;

        // Slider -> Number
        slider.addEventListener('input', () => {
            const val = parseFloat(slider.value);
            if (numberInput) numberInput.value = val;
            if (valSpan) valSpan.textContent = val;
            callback(val);
        });

        // Number -> Slider
        if (numberInput) {
            numberInput.addEventListener('change', () => { // Change triggers on enter/blur
                let val = parseFloat(numberInput.value);

                // Clamp
                if (slider.min) val = Math.max(parseFloat(slider.min), val);
                if (slider.max) val = Math.min(parseFloat(slider.max), val);

                numberInput.value = val;
                slider.value = val;
                if (valSpan) valSpan.textContent = val;
                callback(val);
            });

            // Optional: Live update while typing? Maybe too heavy. Use change for now.
        }
    }

    function _setSliderValue(id, value) {
        const slider = document.getElementById(id);
        const numberInput = document.getElementById(`${id}-num`);
        const valSpan = document.getElementById(`${id}-val`);

        if (slider) slider.value = value;
        if (numberInput) numberInput.value = value;
        if (valSpan) valSpan.textContent = value;
    }

    // =========================================================================
    // HELPER: TOGGLES
    // =========================================================================

    function _bindToggle(id, callback) {
        const toggle = document.getElementById(id);
        if (!toggle) {
            console.warn('[SIDEBAR] _bindToggle: element not found:', id);
            return;
        }

        toggle.addEventListener('click', () => {
            const isActive = toggle.classList.toggle('active');
            callback(isActive);
        });
        console.log('[SIDEBAR] _bindToggle: bound', id);
    }

    // =========================================================================
    // DEBOUNCED REFRESH
    // =========================================================================

    function _scheduleRefresh() {
        clearTimeout(_refreshTimer);
        _refreshTimer = setTimeout(() => {
            if (typeof REFRESH !== 'undefined') {
                REFRESH.throttled();
            } else if (typeof refreshGraph === 'function') {
                refreshGraph();
            }
        }, 16); // ~1 frame
    }

    // =========================================================================
    // SECTION RESIZING - Vertical drag handles
    // =========================================================================

    const SECTION_HEIGHT_KEY = 'viz_section_heights';
    let _resizeState = { active: false, section: null, startY: 0, startHeight: 0 };

    function initSectionResize() {
        // Add resize handles to each section
        document.querySelectorAll('.section-content').forEach(content => {
            const sectionId = content.id;
            if (!sectionId) return;

            // Make content resizable
            content.classList.add('resizable');

            // Create resize handle
            const handle = document.createElement('div');
            handle.className = 'section-resize-handle';
            handle.dataset.section = sectionId;

            // Insert after section-content (before next section)
            const section = content.closest('.section');
            if (section && section.nextElementSibling) {
                section.parentNode.insertBefore(handle, section.nextElementSibling);
            }

            // Bind drag events
            handle.addEventListener('mousedown', _startResize);
        });

        // Global mouse events
        document.addEventListener('mousemove', _onResize);
        document.addEventListener('mouseup', _endResize);

        // Restore saved heights
        _restoreSectionHeights();

        console.log('[SIDEBAR] Section resize initialized');
    }

    function _startResize(e) {
        const sectionId = e.target.dataset.section;
        const content = document.getElementById(sectionId);
        if (!content) return;

        _resizeState = {
            active: true,
            section: content,
            startY: e.clientY,
            startHeight: content.offsetHeight
        };

        e.target.classList.add('dragging');
        document.body.style.cursor = 'ns-resize';
        e.preventDefault();
    }

    function _onResize(e) {
        if (!_resizeState.active || !_resizeState.section) return;

        const delta = e.clientY - _resizeState.startY;
        const newHeight = Math.max(60, Math.min(400, _resizeState.startHeight + delta));

        _resizeState.section.style.maxHeight = newHeight + 'px';
    }

    function _endResize() {
        if (!_resizeState.active) return;

        // Save height
        if (_resizeState.section) {
            _saveSectionHeight(_resizeState.section.id, _resizeState.section.style.maxHeight);
        }

        // Cleanup
        document.querySelectorAll('.section-resize-handle.dragging').forEach(h => {
            h.classList.remove('dragging');
        });
        document.body.style.cursor = '';

        _resizeState = { active: false, section: null, startY: 0, startHeight: 0 };
    }

    function _saveSectionHeight(sectionId, height) {
        try {
            const heights = JSON.parse(localStorage.getItem(SECTION_HEIGHT_KEY) || '{}');
            heights[sectionId] = height;
            localStorage.setItem(SECTION_HEIGHT_KEY, JSON.stringify(heights));
        } catch (e) {
            console.warn('[SIDEBAR] Could not save section height:', e);
        }
    }

    function _restoreSectionHeights() {
        try {
            const heights = JSON.parse(localStorage.getItem(SECTION_HEIGHT_KEY) || '{}');
            Object.entries(heights).forEach(([sectionId, height]) => {
                const content = document.getElementById(sectionId);
                if (content && height) {
                    content.style.maxHeight = height;
                }
            });
        } catch (e) {
            console.warn('[SIDEBAR] Could not restore section heights:', e);
        }
    }

    // =========================================================================
    // SIDEBAR RESIZING - Horizontal drag handles
    // =========================================================================

    const SIDEBAR_WIDTH_KEY = 'viz_sidebar_widths';
    let _sidebarResizeState = { active: false, side: null, startX: 0, startWidth: 0 };

    function initSidebarResize() {
        const leftHandle = document.getElementById('left-resize-handle');
        const rightHandle = document.getElementById('right-resize-handle');

        if (leftHandle) {
            leftHandle.addEventListener('mousedown', (e) => _startSidebarResize(e, 'left'));
        }
        if (rightHandle) {
            rightHandle.addEventListener('mousedown', (e) => _startSidebarResize(e, 'right'));
        }

        // Global mouse events
        document.addEventListener('mousemove', _onSidebarResize);
        document.addEventListener('mouseup', _endSidebarResize);

        // Restore saved widths
        _restoreSidebarWidths();

        console.log('[SIDEBAR] Sidebar resize initialized');
    }

    function _startSidebarResize(e, side) {
        const cssVar = side === 'left' ? '--sidebar-width' : '--right-panel-width';
        const currentWidth = parseInt(getComputedStyle(document.documentElement).getPropertyValue(cssVar)) || 280;

        _sidebarResizeState = {
            active: true,
            side: side,
            startX: e.clientX,
            startWidth: currentWidth
        };

        e.target.classList.add('dragging');
        document.body.style.cursor = 'ew-resize';
        e.preventDefault();
    }

    function _onSidebarResize(e) {
        if (!_sidebarResizeState.active) return;

        const { side, startX, startWidth } = _sidebarResizeState;
        const delta = side === 'left' ? (e.clientX - startX) : (startX - e.clientX);
        const minWidth = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--min-sidebar-width')) || 200;
        const maxWidth = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--max-sidebar-width')) || 400;
        const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth + delta));

        const cssVar = side === 'left' ? '--sidebar-width' : '--right-panel-width';
        document.documentElement.style.setProperty(cssVar, newWidth + 'px');

        // Update handle position
        const handle = document.getElementById(`${side}-resize-handle`);
        if (handle) {
            if (side === 'left') {
                handle.style.left = (newWidth - 3) + 'px';
            } else {
                handle.style.right = (newWidth - 3) + 'px';
            }
        }
    }

    function _endSidebarResize() {
        if (!_sidebarResizeState.active) return;

        // Save widths
        _saveSidebarWidths();

        // Cleanup
        document.querySelectorAll('.sidebar-resize-handle.dragging').forEach(h => {
            h.classList.remove('dragging');
        });
        document.body.style.cursor = '';

        _sidebarResizeState = { active: false, side: null, startX: 0, startWidth: 0 };
    }

    function _saveSidebarWidths() {
        try {
            const left = getComputedStyle(document.documentElement).getPropertyValue('--sidebar-width');
            const right = getComputedStyle(document.documentElement).getPropertyValue('--right-panel-width');
            localStorage.setItem(SIDEBAR_WIDTH_KEY, JSON.stringify({ left, right }));
        } catch (e) {
            console.warn('[SIDEBAR] Could not save sidebar widths:', e);
        }
    }

    function _restoreSidebarWidths() {
        try {
            const widths = JSON.parse(localStorage.getItem(SIDEBAR_WIDTH_KEY) || '{}');
            if (widths.left) {
                document.documentElement.style.setProperty('--sidebar-width', widths.left);
                const leftHandle = document.getElementById('left-resize-handle');
                if (leftHandle) leftHandle.style.left = `calc(${widths.left} - 3px)`;
            }
            if (widths.right) {
                document.documentElement.style.setProperty('--right-panel-width', widths.right);
                const rightHandle = document.getElementById('right-resize-handle');
                if (rightHandle) rightHandle.style.right = `calc(${widths.right} - 3px)`;
            }
        } catch (e) {
            console.warn('[SIDEBAR] Could not restore sidebar widths:', e);
        }
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        // Initialization
        init,
        initSectionResize,
        initSidebarResize,

        // Color modes
        setColorMode,

        // Color Schemes (33 named gradients)
        applyColorScheme,
        clearColorScheme,
        renderSchemeNavigator,
        initSchemeNavigator,
        SCHEME_CONFIG,

        // Layouts
        setLayout,

        // Physics
        setPhysicsPreset,
        PHYSICS_PRESETS,

        // Filters
        populateFilterChips,
        setFilter,
        renderSmartSidebar, // Export for debug/manual re-render

        // Panels
        showHoverPanel,
        hideHoverPanel,
        updateSelectionPanel,

        // Stats
        updateStats,

        // View Mode (ATOMS/FILES toggle)
        initViewModeToggle,
        setViewMode,
        getViewMode,
        applyDeferredViewMode
    };
})();

// Backward compatibility - SidebarManager class is defined in app.js, not duplicated here
// The SIDEBAR module provides all functionality via SIDEBAR.* calls
