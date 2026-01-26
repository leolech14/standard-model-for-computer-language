/**
 * ANIMATION MODULE
 *
 * Unified animation controller for all layout transitions and continuous motions.
 * Addresses ARCH-002 (O(n^2) flock), ARCH-003 (unthrottled refresh), ARCH-004 (conflicts).
 *
 * Key improvements:
 * - Single animation ownership prevents conflicts
 * - Spatial hashing reduces flock from O(n^2) to O(n)
 * - Integration with REFRESH module for throttled updates
 *
 * Usage:
 *   ANIM.applyLayout('orbital')           // Apply a layout preset
 *   ANIM.stop()                           // Stop all animations
 *   ANIM.setStaggerPattern('radial')      // Change wave pattern
 */

const ANIM = (function () {
    'use strict';

    // =========================================================================
    // CONFIGURATION
    // =========================================================================

    const CONFIG = {
        baseDuration: 1200,      // Base animation duration (ms)
        staggerSpread: 800,      // Stagger spread (ms)
        flockMaxNodes: 500,      // Max nodes for flock simulation
        spatialGridSize: 50,     // Grid cell size for spatial hashing
        motionFrameSkip: 0       // Skip frames for motion (0 = no skip)
    };

    // =========================================================================
    // STATE
    // =========================================================================

    let _currentLayout = 'force';
    let _animationId = null;
    let _layoutTime = 0;
    let _currentStaggerPattern = 'tier';
    let _owner = 'none';  // Current animation owner

    // =========================================================================
    // STAGGER PATTERNS - Wave-based node transitions
    // =========================================================================

    const STAGGER_PATTERNS = {
        // Radial ripple: center nodes move first, ripples outward
        radial: (node, startPos, targetPos) => {
            const dist = Math.sqrt(startPos.x ** 2 + startPos.y ** 2 + startPos.z ** 2);
            return Math.min(1, dist / 500);
        },
        // Tier cascade: T0 first, then T1, then T2
        tier: (node) => {
            const tier = NODE.getTier(node);
            const tierNum = tier === 'T0' ? 0 : tier === 'T1' ? 1 : 2;
            return tierNum / 2;
        },
        // Distance-based: shortest travel first
        distance: (node, startPos, targetPos) => {
            const dx = targetPos.x - startPos.x;
            const dy = targetPos.y - startPos.y;
            const dz = targetPos.z - startPos.z;
            const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
            return Math.min(1, dist / 400);
        },
        // File grouping: nodes in same file move together
        file: (node) => {
            const fileIdx = node.fileIdx ?? 0;
            return (fileIdx % 8) / 8;
        },
        // Spiral pattern
        spiral: (node, startPos) => {
            const angle = Math.atan2(startPos.y, startPos.x);
            const dist = Math.sqrt(startPos.x ** 2 + startPos.y ** 2);
            return ((angle + Math.PI) / (2 * Math.PI) + dist / 1000) % 1;
        },
        // Random stagger
        random: () => Math.random() * 0.6
    };

    // =========================================================================
    // LAYOUT PRESETS
    // =========================================================================

    const LAYOUT_PRESETS = {
        'force': {
            name: 'FORCE', icon: '?', description: 'Physics-based clustering',
            motion: 'settle', cooldown: 300, warmupTicks: 40, getPosition: null
        },
        'orbital': {
            name: 'ORBITAL', icon: '?', description: 'Planetary orbit bands',
            motion: 'orbit', cooldown: Infinity, orbitSpeed: 0.002,
            getPosition: (node, idx, total, time) => {
                const tier = NODE.getTier(node);
                const family = NODE.getFamily(node);
                const r = { T0: 80, T1: 160, T2: 280, UNKNOWN: 200 }[tier] || 200;
                const fOff = { LOG: 0, DAT: 1, ORG: 2, EXE: 3, EXT: 4, UNKNOWN: 2.5 }[family] || 0;
                const angle = (fOff / 5) * Math.PI * 2 + (idx / Math.max(1, total)) * Math.PI * 0.3 + (time || 0) * (0.5 + r * 0.001);
                const wobble = Math.sin(idx * 0.7 + (time || 0) * 2) * 15;
                return {
                    x: Math.cos(angle) * (r + wobble),
                    y: Math.sin(idx * 0.3) * 40 + (tier === 'T0' ? -50 : tier === 'T2' ? 50 : 0),
                    z: Math.sin(angle) * (r + wobble)
                };
            }
        },
        'radial': {
            name: 'RADIAL', icon: '?', description: 'Concentric tier rings',
            motion: 'static', cooldown: 0,
            getPosition: (node, idx, total, time, tierGroups) => {
                const tier = NODE.getTier(node);
                const r = { T0: 60, T1: 150, T2: 280, UNKNOWN: 220 }[tier] || 180;
                const tierNodes = tierGroups?.[tier] || [];
                const tierIdx = tierNodes.indexOf(node);
                const tierTotal = tierNodes.length || 1;
                const angle = (tierIdx / tierTotal) * Math.PI * 2;
                return { x: Math.cos(angle) * r, y: 0, z: Math.sin(angle) * r };
            }
        },
        'spiral': {
            name: 'SPIRAL', icon: '?', description: 'DNA-like helix',
            motion: 'rotate', cooldown: Infinity, rotateSpeed: 0.003,
            getPosition: (node, idx, total, time) => {
                const t = idx / Math.max(1, total);
                const angle = t * Math.PI * 2 * 4 + (time || 0);
                const r = 100 + t * 150;
                return { x: Math.cos(angle) * r, y: (t - 0.5) * 400, z: Math.sin(angle) * r };
            }
        },
        'sphere': {
            name: 'SPHERE', icon: '?', description: 'Globe surface',
            motion: 'rotate', cooldown: Infinity, rotateSpeed: 0.001,
            getPosition: (node, idx, total, time) => {
                const tier = NODE.getTier(node);
                const family = NODE.getFamily(node);
                const latBase = { T0: 0.8, T1: 0.5, T2: 0.2, UNKNOWN: 0.5 }[tier] || 0.5;
                const lat = (latBase + (idx % 10) * 0.02) * Math.PI;
                const lonBase = { LOG: 0, DAT: 72, ORG: 144, EXE: 216, EXT: 288, UNKNOWN: 180 }[family] || 0;
                const lon = ((lonBase + idx * 3) % 360) * Math.PI / 180 + (time || 0);
                const r = 200;
                return {
                    x: Math.sin(lat) * Math.cos(lon) * r,
                    y: Math.cos(lat) * r,
                    z: Math.sin(lat) * Math.sin(lon) * r
                };
            }
        },
        'grid': {
            name: 'GRID', icon: '?', description: '3D lattice',
            motion: 'static', cooldown: 0,
            getPosition: (node, idx, total) => {
                const tier = NODE.getTier(node);
                const family = NODE.getFamily(node);
                const tierX = { T0: -150, T1: 0, T2: 150, UNKNOWN: 0 }[tier] || 0;
                const famZ = { LOG: -120, DAT: -60, ORG: 0, EXE: 60, EXT: 120, UNKNOWN: 0 }[family] || 0;
                const row = Math.floor(idx / 15);
                const col = idx % 15;
                return { x: tierX + (col - 7) * 20, y: row * 25 - 100, z: famZ + Math.sin(idx * 0.5) * 20 };
            }
        },
        'flock': {
            name: 'FLOCK', icon: '?', description: 'Swarming birds',
            motion: 'flock', cooldown: Infinity,
            flockParams: { separation: 25, alignment: 0.05, cohesion: 0.01, maxSpeed: 2 },
            getPosition: null
        },
        'galaxy': {
            name: 'GALAXY', icon: '?', description: 'Spiral arms',
            motion: 'rotate', cooldown: Infinity, rotateSpeed: 0.001,
            getPosition: (node, idx, total, time) => {
                const family = NODE.getFamily(node);
                const tier = NODE.getTier(node);
                const armOff = { LOG: 0, DAT: 1, ORG: 2, EXE: 3, EXT: 4, UNKNOWN: 2.5 }[family] || 0;
                const baseAngle = (armOff / 5) * Math.PI * 2;
                const dist = 50 + (idx / total) * 250;
                const spiralAngle = baseAngle + dist * 0.015 + (time || 0);
                const tierY = { T0: -30, T1: 0, T2: 30, UNKNOWN: 0 }[tier] || 0;
                return {
                    x: Math.cos(spiralAngle) * dist,
                    y: tierY + Math.sin(idx * 0.5) * 20,
                    z: Math.sin(spiralAngle) * dist
                };
            }
        },
        'tree': {
            name: 'TREE', icon: '▼', description: 'Hierarchical tree (root top)',
            motion: 'static', cooldown: 0,
            getPosition: (node, idx, total, time, tierGroups) => {
                // Simple hierarchical layout: arrange by tier levels
                // T0 at top, T1 in middle, T2 at bottom
                const tier = NODE.getTier(node);
                const tierList = ['T0', 'T1', 'T2'];
                const tierIdx = tierList.indexOf(tier);
                const tierY = tierIdx * 150 - 150;  // T0=-150, T1=0, T2=150

                // Within each tier, spread nodes horizontally
                const tierNodes = tierGroups?.[tier] || [];
                const nodeInTierIdx = tierNodes.indexOf(node);
                const tierCount = tierNodes.length || 1;
                const spread = Math.min(400, tierCount * 40);
                const tierX = (nodeInTierIdx - tierCount / 2) * (spread / tierCount);

                return {
                    x: tierX,
                    y: tierY,
                    z: tierIdx * 30
                };
            }
        }
    };

    // =========================================================================
    // SPATIAL HASHING - O(n) neighbor lookup for flock simulation
    // =========================================================================

    function _buildSpatialGrid(nodes, cellSize) {
        const grid = new Map();

        nodes.forEach((node, idx) => {
            const x = node.x || 0;
            const y = node.y || 0;
            const z = node.z || 0;

            const cellX = Math.floor(x / cellSize);
            const cellY = Math.floor(y / cellSize);
            const cellZ = Math.floor(z / cellSize);
            const key = `${cellX},${cellY},${cellZ}`;

            if (!grid.has(key)) {
                grid.set(key, []);
            }
            grid.get(key).push({ node, idx });
        });

        return grid;
    }

    function _getNeighborsFromGrid(grid, node, cellSize, radius) {
        const x = node.x || 0;
        const y = node.y || 0;
        const z = node.z || 0;

        const cellX = Math.floor(x / cellSize);
        const cellY = Math.floor(y / cellSize);
        const cellZ = Math.floor(z / cellSize);

        const neighbors = [];
        const cellRadius = Math.ceil(radius / cellSize);

        // Check neighboring cells
        for (let dx = -cellRadius; dx <= cellRadius; dx++) {
            for (let dy = -cellRadius; dy <= cellRadius; dy++) {
                for (let dz = -cellRadius; dz <= cellRadius; dz++) {
                    const key = `${cellX + dx},${cellY + dy},${cellZ + dz}`;
                    const cell = grid.get(key);
                    if (cell) {
                        cell.forEach(entry => {
                            if (entry.node !== node) {
                                neighbors.push(entry.node);
                            }
                        });
                    }
                }
            }
        }

        return neighbors;
    }

    // =========================================================================
    // HELPER FUNCTIONS
    // =========================================================================

    function _groupNodesByTier(nodes) {
        const groups = { T0: [], T1: [], T2: [], UNKNOWN: [] };
        nodes.forEach(n => {
            const tier = NODE.getTier(n);
            (groups[tier] || groups.UNKNOWN).push(n);
        });
        return groups;
    }

    function _acquireOwnership(owner) {
        // Cancel any existing animation
        if (_animationId) {
            cancelAnimationFrame(_animationId);
            _animationId = null;
        }
        _owner = owner;
        return true;
    }

    function _releaseOwnership(owner) {
        if (_owner === owner) {
            if (_animationId) {
                cancelAnimationFrame(_animationId);
                _animationId = null;
            }
            _owner = 'none';
        }
    }

    // =========================================================================
    // LAYOUT APPLICATION
    // =========================================================================

    function applyLayout(presetKey, animate = true) {
        const preset = LAYOUT_PRESETS[presetKey];
        if (!preset) return;

        _currentLayout = presetKey;
        _acquireOwnership('layout');

        const nodes = Graph?.graphData()?.nodes || [];
        const total = nodes.length;
        const tierGroups = _groupNodesByTier(nodes);

        // Handle force layout specially
        if (presetKey === 'force') {
            nodes.forEach(n => {
                n.fx = undefined;
                n.fy = undefined;
                n.fz = undefined;
            });
            Graph.cooldownTicks(preset.cooldown);
            Graph.d3ReheatSimulation();
            _releaseOwnership('layout');
            if (typeof showModeToast === 'function') {
                showModeToast('? FORCE layout');
            }
            return;
        }

        // Handle flock specially
        if (preset.motion === 'flock') {
            _startFlockSimulation(preset.flockParams);
            Graph.cooldownTicks(preset.cooldown);
            if (typeof showModeToast === 'function') {
                showModeToast(`${preset.icon} ${preset.name} layout`);
            }
            return;
        }

        // Position-based layouts
        if (preset.getPosition) {
            const startPos = nodes.map(n => ({ x: n.x || 0, y: n.y || 0, z: n.z || 0 }));
            const targetPos = nodes.map((n, i) => preset.getPosition(n, i, total, 0, tierGroups));

            if (animate && total > 100) {
                // STAGGERED ANIMATION for large graphs
                _animateStaggered(nodes, startPos, targetPos, preset, tierGroups, presetKey);
            } else if (animate) {
                // SIMPLE ANIMATION for small graphs
                _animateSimple(nodes, startPos, targetPos, preset, presetKey);
            } else {
                // INSTANT
                nodes.forEach((n, i) => {
                    const p = targetPos[i];
                    n.fx = p.x;
                    n.fy = p.y;
                    n.fz = p.z;
                });
                if (typeof REFRESH !== 'undefined') {
                    REFRESH.force();
                } else if (Graph) {
                    REFRESH.throttled();
                }
                if (preset.motion === 'rotate' || preset.motion === 'orbit') {
                    _startLayoutMotion(presetKey);
                }
            }
        }

        Graph.cooldownTicks(preset.cooldown);
        if (typeof showModeToast === 'function') {
            showModeToast(`${preset.icon} ${preset.name} layout`);
        }
    }

    function _animateStaggered(nodes, startPos, targetPos, preset, tierGroups, presetKey) {
        const baseDuration = CONFIG.baseDuration;
        const staggerSpread = CONFIG.staggerSpread;
        const startTime = Date.now();

        // Hide edges during animation for performance
        Graph.linkOpacity(0);

        // Calculate delay for each node
        const pattern = STAGGER_PATTERNS[_currentStaggerPattern] || STAGGER_PATTERNS.tier;
        const delays = nodes.map((n, i) => pattern(n, startPos[i], targetPos[i]) * staggerSpread);

        function animateFrame() {
            if (_owner !== 'layout') return;

            const elapsed = Date.now() - startTime;

            nodes.forEach((n, i) => {
                const nodeStart = delays[i];
                const nodeElapsed = elapsed - nodeStart;

                if (nodeElapsed <= 0) {
                    n.fx = startPos[i].x;
                    n.fy = startPos[i].y;
                    n.fz = startPos[i].z;
                } else if (nodeElapsed >= baseDuration) {
                    n.fx = targetPos[i].x;
                    n.fy = targetPos[i].y;
                    n.fz = targetPos[i].z;
                } else {
                    const progress = nodeElapsed / baseDuration;
                    const eased = progress * progress * (3 - 2 * progress);
                    n.fx = startPos[i].x + (targetPos[i].x - startPos[i].x) * eased;
                    n.fy = startPos[i].y + (targetPos[i].y - startPos[i].y) * eased;
                    n.fz = startPos[i].z + (targetPos[i].z - startPos[i].z) * eased;
                }
            });

            if (typeof REFRESH !== 'undefined') {
                REFRESH.throttled();
            } else if (Graph) {
                REFRESH.throttled();
            }

            const totalDuration = baseDuration + staggerSpread;
            if (elapsed < totalDuration) {
                _animationId = requestAnimationFrame(animateFrame);
            } else {
                // Restore edges
                if (typeof applyEdgeMode === 'function') {
                    applyEdgeMode();
                }
                if (preset.motion === 'rotate' || preset.motion === 'orbit') {
                    _startLayoutMotion(presetKey);
                } else {
                    _releaseOwnership('layout');
                }
            }
        }

        _animationId = requestAnimationFrame(animateFrame);
    }

    function _animateSimple(nodes, startPos, targetPos, preset, presetKey) {
        const duration = 1500;
        const startTime = Date.now();

        function animateFrame() {
            if (_owner !== 'layout') return;

            const progress = Math.min(1, (Date.now() - startTime) / duration);
            const eased = progress * progress * (3 - 2 * progress);

            nodes.forEach((n, i) => {
                n.fx = startPos[i].x + (targetPos[i].x - startPos[i].x) * eased;
                n.fy = startPos[i].y + (targetPos[i].y - startPos[i].y) * eased;
                n.fz = startPos[i].z + (targetPos[i].z - startPos[i].z) * eased;
            });

            if (typeof REFRESH !== 'undefined') {
                REFRESH.throttled();
            } else if (Graph) {
                REFRESH.throttled();
            }

            if (progress < 1) {
                _animationId = requestAnimationFrame(animateFrame);
            } else if (preset.motion === 'rotate' || preset.motion === 'orbit') {
                _startLayoutMotion(presetKey);
            } else {
                _releaseOwnership('layout');
            }
        }

        _animationId = requestAnimationFrame(animateFrame);
    }

    function _startLayoutMotion(presetKey) {
        const preset = LAYOUT_PRESETS[presetKey];
        if (!preset || !preset.getPosition) return;

        _acquireOwnership('motion');

        const nodes = Graph?.graphData()?.nodes || [];
        const total = nodes.length;
        const tierGroups = _groupNodesByTier(nodes);
        const speed = preset.rotateSpeed || preset.orbitSpeed || 0.002;

        function animate() {
            if (_owner !== 'motion') return;

            _layoutTime += speed;

            nodes.forEach((n, i) => {
                const pos = preset.getPosition(n, i, total, _layoutTime, tierGroups);
                n.fx = pos.x;
                n.fy = pos.y;
                n.fz = pos.z;
            });

            if (typeof REFRESH !== 'undefined') {
                REFRESH.throttled();
            } else if (Graph) {
                REFRESH.throttled();
            }

            _animationId = requestAnimationFrame(animate);
        }

        _animationId = requestAnimationFrame(animate);
    }

    // =========================================================================
    // FLOCK SIMULATION - O(n) with spatial hashing
    // =========================================================================

    function _startFlockSimulation(params) {
        const nodes = Graph?.graphData()?.nodes || [];

        // Performance guard
        if (nodes.length > CONFIG.flockMaxNodes) {
            console.warn(`[ANIM] Flock disabled: ${nodes.length} nodes exceeds ${CONFIG.flockMaxNodes} limit`);
            if (typeof showModeToast === 'function') {
                showModeToast('Warning: Flock disabled (too many nodes)');
            }
            return;
        }

        _acquireOwnership('flock');

        const { separation, alignment, cohesion, maxSpeed } = params;

        // Initialize velocities
        nodes.forEach(n => {
            n._vx = (Math.random() - 0.5) * 2;
            n._vy = (Math.random() - 0.5) * 2;
            n._vz = (Math.random() - 0.5) * 2;
        });

        function flockStep() {
            if (_owner !== 'flock') return;

            // Build spatial grid for O(n) neighbor lookup
            const grid = _buildSpatialGrid(nodes, CONFIG.spatialGridSize);
            const neighborRadius = separation * 3;

            nodes.forEach(n => {
                // Get nearby neighbors from spatial grid (O(1) per node)
                const neighbors = _getNeighborsFromGrid(grid, n, CONFIG.spatialGridSize, neighborRadius);

                let sepX = 0, sepY = 0, sepZ = 0, sepCount = 0;
                let alignX = 0, alignY = 0, alignZ = 0, alignCount = 0;
                let cohX = 0, cohY = 0, cohZ = 0, cohCount = 0;

                const myFamily = NODE.getFamily(n);

                neighbors.forEach(other => {
                    const dx = (other.x || 0) - (n.x || 0);
                    const dy = (other.y || 0) - (n.y || 0);
                    const dz = (other.z || 0) - (n.z || 0);
                    const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) || 0.001;

                    // Separation
                    if (dist < separation * 2) {
                        sepX -= dx / dist;
                        sepY -= dy / dist;
                        sepZ -= dz / dist;
                        sepCount++;
                    }

                    // Alignment and cohesion (same family only)
                    if (NODE.getFamily(other) === myFamily && dist < 150) {
                        alignX += other._vx || 0;
                        alignY += other._vy || 0;
                        alignZ += other._vz || 0;
                        alignCount++;

                        cohX += other.x || 0;
                        cohY += other.y || 0;
                        cohZ += other.z || 0;
                        cohCount++;
                    }
                });

                // Apply forces
                if (sepCount > 0) {
                    n._vx += (sepX / sepCount) * separation * 0.05;
                    n._vy += (sepY / sepCount) * separation * 0.05;
                    n._vz += (sepZ / sepCount) * separation * 0.05;
                }
                if (alignCount > 0) {
                    n._vx += ((alignX / alignCount) - n._vx) * alignment;
                    n._vy += ((alignY / alignCount) - n._vy) * alignment;
                    n._vz += ((alignZ / alignCount) - n._vz) * alignment;
                }
                if (cohCount > 0) {
                    n._vx += (cohX / cohCount - (n.x || 0)) * cohesion;
                    n._vy += (cohY / cohCount - (n.y || 0)) * cohesion;
                    n._vz += (cohZ / cohCount - (n.z || 0)) * cohesion;
                }

                // Center attraction
                n._vx -= (n.x || 0) * 0.0005;
                n._vy -= (n.y || 0) * 0.0005;
                n._vz -= (n.z || 0) * 0.0005;

                // Speed limit
                const speed = Math.sqrt(n._vx * n._vx + n._vy * n._vy + n._vz * n._vz);
                if (speed > maxSpeed) {
                    n._vx = (n._vx / speed) * maxSpeed;
                    n._vy = (n._vy / speed) * maxSpeed;
                    n._vz = (n._vz / speed) * maxSpeed;
                }

                // Update position
                n.fx = (n.x || 0) + n._vx;
                n.fy = (n.y || 0) + n._vy;
                n.fz = (n.z || 0) + n._vz;
            });

            if (typeof REFRESH !== 'undefined') {
                REFRESH.throttled();
            } else if (Graph) {
                REFRESH.throttled();
            }

            _animationId = requestAnimationFrame(flockStep);
        }

        _animationId = requestAnimationFrame(flockStep);
    }

    // =========================================================================
    // PULSE ANIMATION
    // =========================================================================

    let _pulseId = null;

    function togglePulse(active) {
        if (active) {
            _startPulse();
        } else {
            _stopPulse();
        }
    }

    function _startPulse() {
        if (_pulseId) return;
        const startTime = Date.now();

        function loop() {
            const elapsed = Date.now() - startTime;
            // Oscillate lightness +/- 10%
            const val = Math.sin(elapsed * 0.003) * 10;

            if (typeof COLOR !== 'undefined') {
                COLOR.setTransform('lightnessShift', val);
                // Also breathe chroma a bit
                COLOR.setTransform('chromaScale', 1.0 + Math.sin(elapsed * 0.003) * 0.2);
            }

            if (typeof REFRESH !== 'undefined') {
                REFRESH.throttled();
            } else if (typeof Graph !== 'undefined' && Graph) {
                // Determine if we need to force re-coloring or if just re-rendering canvas is enough.
                // Since transforms affect color calculation, we likely need to re-apply colors.
                if (typeof window.applyNodeColors === 'function') {
                    const nodes = Graph.graphData().nodes;
                    window.applyNodeColors(nodes);
                    Graph.nodeColor(Graph.nodeColor()); // Trigger internal update
                }
            }

            _pulseId = requestAnimationFrame(loop);
        }
        _pulseId = requestAnimationFrame(loop);
        if (typeof showModeToast === 'function') showModeToast('Pulse Animation ON');
    }

    function _stopPulse() {
        if (_pulseId) {
            cancelAnimationFrame(_pulseId);
            _pulseId = null;
        }
        // Reset
        if (typeof COLOR !== 'undefined') {
            COLOR.setTransform('lightnessShift', 0);
            COLOR.setTransform('chromaScale', 1.0);
        }

        // Final refresh to clear artifacts
        if (typeof window.applyNodeColors === 'function' && typeof Graph !== 'undefined') {
            const nodes = Graph.graphData().nodes;
            window.applyNodeColors(nodes);
            Graph.nodeColor(Graph.nodeColor());
        }

        if (typeof showModeToast === 'function') showModeToast('Pulse Animation OFF');
    }

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    function stop() {
        if (_animationId) {
            cancelAnimationFrame(_animationId);
            _animationId = null;
        }
        _owner = 'none';
    }

    function setStaggerPattern(pattern) {
        if (STAGGER_PATTERNS[pattern]) {
            _currentStaggerPattern = pattern;
            if (typeof showModeToast === 'function') {
                showModeToast(`Wave pattern: ${pattern.toUpperCase()}`);
            }
        }
    }

    function cycleStaggerPattern() {
        const patterns = Object.keys(STAGGER_PATTERNS);
        if (!patterns || patterns.length === 0) return _currentStaggerPattern;
        const currentIdx = patterns.indexOf(_currentStaggerPattern);
        _currentStaggerPattern = patterns[(currentIdx + 1) % patterns.length];
        if (typeof showModeToast === 'function') {
            showModeToast(`Wave pattern: ${_currentStaggerPattern.toUpperCase()}`);
        }
        return _currentStaggerPattern;
    }

    return {
        // Layout control
        applyLayout,
        stop,

        // Stagger patterns
        setStaggerPattern,
        cycleStaggerPattern,
        togglePulse, // Added to public API
        get staggerPattern() { return _currentStaggerPattern; },
        get staggerPatterns() { return Object.keys(STAGGER_PATTERNS); },

        // State
        get currentLayout() { return _currentLayout; },
        get isAnimating() { return _animationId !== null; },
        get owner() { return _owner; },

        // Layout presets
        presets: LAYOUT_PRESETS,

        // Config
        config: CONFIG
    };
})();

// Backward compatibility aliases - Using Object.defineProperty to avoid duplicate declarations
// Note: CURRENT_LAYOUT, LAYOUT_ANIMATION_ID, LAYOUT_TIME, CURRENT_STAGGER_PATTERN
// are managed by app.js (separate animation system) - not duplicated here
Object.defineProperty(window, 'LAYOUT_PRESETS', { get: () => ANIM.presets, configurable: true });
Object.defineProperty(window, 'STAGGER_PATTERNS', { get: () => ANIM.staggerPatterns, configurable: true });

function applyLayoutPreset(presetKey, animate) {
    ANIM.applyLayout(presetKey, animate);
}

function cycleStaggerPattern() {
    ANIM.cycleStaggerPattern();
}

function startFlockSimulation(params) {
    // Handled internally by ANIM
    ANIM.applyLayout('flock');
}

function groupNodesByTier(nodes) {
    const groups = { T0: [], T1: [], T2: [], UNKNOWN: [] };
    nodes.forEach(n => {
        const tier = NODE.getTier(n);
        (groups[tier] || groups.UNKNOWN).push(n);
    });
    return groups;
}
