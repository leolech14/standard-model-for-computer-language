/**
 * COLLIDER PERFORMANCE SUBSYSTEM
 *
 * Provides frame-budget-aware animation scheduling, adaptive quality management,
 * and real-time performance monitoring for the WebGL visualization.
 *
 * Architecture:
 *   PerformanceMonitor  → measures frame times, detects stuttering
 *   AnimationScheduler  → manages animation queue, enforces frame budget
 *   AdaptiveQuality     → degrades/upgrades quality based on performance
 *   PositionOwnership   → enforces single-owner invariant for node positions
 *
 * Usage:
 *   PERF.monitor.start()
 *   PERF.scheduler.requestTransition(nodes, targetPositions, duration)
 *   PERF.quality.current  // 'ultra' | 'high' | 'medium' | 'low' | 'minimal'
 */

const PERF = (function() {
    'use strict';

    // =========================================================================
    // CONFIGURATION (loaded from performance.tokens.json or defaults)
    // =========================================================================

    const CONFIG = {
        frameBudget: {
            targetFps: 60,
            targetFrameMs: 16.67,
            warningThreshold: 0.8,   // 80% of budget
            criticalThreshold: 1.5   // 150% of budget
        },
        nodeThresholds: {
            small: 100,
            medium: 500,
            large: 1000,
            massive: 5000
        },
        monitoring: {
            sampleWindowMs: 1000,
            sampleCount: 60,
            degradeAfterConsecutiveDrops: 10,
            upgradeAfterConsecutiveGood: 30
        }
    };

    // =========================================================================
    // PERFORMANCE MONITOR
    // Tracks frame times using a rolling window
    // =========================================================================

    const PerformanceMonitor = {
        _frameTimes: [],
        _lastFrameTime: 0,
        _frameCount: 0,
        _droppedFrames: 0,
        _consecutiveDrops: 0,
        _consecutiveGood: 0,
        _isRunning: false,
        _rafId: null,

        start() {
            if (this._isRunning) return;
            this._isRunning = true;
            this._lastFrameTime = performance.now();
            this._tick();
        },

        stop() {
            this._isRunning = false;
            if (this._rafId) {
                cancelAnimationFrame(this._rafId);
                this._rafId = null;
            }
        },

        _tick() {
            if (!this._isRunning) return;

            const now = performance.now();
            const frameTime = now - this._lastFrameTime;
            this._lastFrameTime = now;

            // Record frame time
            this._frameTimes.push(frameTime);
            if (this._frameTimes.length > CONFIG.monitoring.sampleCount) {
                this._frameTimes.shift();
            }

            this._frameCount++;

            // Check for dropped frame
            const budget = CONFIG.frameBudget.targetFrameMs;
            if (frameTime > budget * CONFIG.frameBudget.criticalThreshold) {
                this._droppedFrames++;
                this._consecutiveDrops++;
                this._consecutiveGood = 0;

                // Trigger quality degradation check
                if (this._consecutiveDrops >= CONFIG.monitoring.degradeAfterConsecutiveDrops) {
                    AdaptiveQuality.degrade();
                    this._consecutiveDrops = 0;
                }
            } else if (frameTime < budget * CONFIG.frameBudget.warningThreshold) {
                this._consecutiveGood++;
                this._consecutiveDrops = 0;

                // Trigger quality upgrade check
                if (this._consecutiveGood >= CONFIG.monitoring.upgradeAfterConsecutiveGood) {
                    AdaptiveQuality.upgrade();
                    this._consecutiveGood = 0;
                }
            }

            this._rafId = requestAnimationFrame(() => this._tick());
        },

        get fps() {
            if (this._frameTimes.length < 2) return 0;
            const avg = this._frameTimes.reduce((a, b) => a + b, 0) / this._frameTimes.length;
            return Math.round(1000 / avg);
        },

        get avgFrameTime() {
            if (this._frameTimes.length === 0) return 0;
            return this._frameTimes.reduce((a, b) => a + b, 0) / this._frameTimes.length;
        },

        get lastFrameTime() {
            return this._frameTimes[this._frameTimes.length - 1] || 0;
        },

        get droppedFramePercent() {
            if (this._frameCount === 0) return 0;
            return Math.round((this._droppedFrames / this._frameCount) * 100);
        },

        get stats() {
            return {
                fps: this.fps,
                avgFrameTime: this.avgFrameTime.toFixed(2),
                lastFrameTime: this.lastFrameTime.toFixed(2),
                droppedPercent: this.droppedFramePercent,
                quality: AdaptiveQuality.current,
                owner: PositionOwnership.current
            };
        },

        reset() {
            this._frameTimes = [];
            this._frameCount = 0;
            this._droppedFrames = 0;
            this._consecutiveDrops = 0;
            this._consecutiveGood = 0;
        }
    };

    // =========================================================================
    // ADAPTIVE QUALITY MANAGER
    // Adjusts rendering quality based on performance
    // =========================================================================

    const QUALITY_TIERS = ['minimal', 'low', 'medium', 'high', 'ultra'];

    const QUALITY_SETTINGS = {
        ultra:   { refreshEvery: 1, flockEnabled: true,  labelDensity: 1.0, animDuration: 1500 },
        high:    { refreshEvery: 1, flockEnabled: false, labelDensity: 0.8, animDuration: 1200 },
        medium:  { refreshEvery: 2, flockEnabled: false, labelDensity: 0.5, animDuration: 800  },
        low:     { refreshEvery: 3, flockEnabled: false, labelDensity: 0.2, animDuration: 500  },
        minimal: { refreshEvery: 5, flockEnabled: false, labelDensity: 0.1, animDuration: 200  }
    };

    const AdaptiveQuality = {
        _current: 'high',
        _locked: false,
        _nodeCount: 0,
        _callbacks: [],

        init(nodeCount) {
            this._nodeCount = nodeCount;
            // Auto-select initial tier based on node count
            if (nodeCount <= CONFIG.nodeThresholds.small) {
                this._current = 'ultra';
            } else if (nodeCount <= CONFIG.nodeThresholds.medium) {
                this._current = 'high';
            } else if (nodeCount <= CONFIG.nodeThresholds.large) {
                this._current = 'medium';
            } else if (nodeCount <= CONFIG.nodeThresholds.massive) {
                this._current = 'low';
            } else {
                this._current = 'minimal';
            }
            console.log(`[PERF] Quality auto-set to '${this._current}' for ${nodeCount} nodes`);
            this._notify();
        },

        get current() { return this._current; },

        get settings() { return QUALITY_SETTINGS[this._current]; },

        set(tier) {
            if (!QUALITY_TIERS.includes(tier)) {
                console.warn(`[PERF] Unknown quality tier: ${tier}`);
                return;
            }
            this._current = tier;
            console.log(`[PERF] Quality set to '${tier}'`);
            this._notify();
        },

        degrade() {
            if (this._locked) return;
            const idx = QUALITY_TIERS.indexOf(this._current);
            if (idx > 0) {
                this._current = QUALITY_TIERS[idx - 1];
                console.log(`[PERF] Quality degraded to '${this._current}'`);
                this._notify();
            }
        },

        upgrade() {
            if (this._locked) return;
            const idx = QUALITY_TIERS.indexOf(this._current);
            // Don't upgrade beyond what node count allows
            const maxTier = this._getMaxTierForNodeCount();
            const maxIdx = QUALITY_TIERS.indexOf(maxTier);
            if (idx < maxIdx) {
                this._current = QUALITY_TIERS[idx + 1];
                console.log(`[PERF] Quality upgraded to '${this._current}'`);
                this._notify();
            }
        },

        lock() { this._locked = true; },
        unlock() { this._locked = false; },

        _getMaxTierForNodeCount() {
            const n = this._nodeCount;
            if (n <= CONFIG.nodeThresholds.small) return 'ultra';
            if (n <= CONFIG.nodeThresholds.medium) return 'high';
            if (n <= CONFIG.nodeThresholds.large) return 'medium';
            if (n <= CONFIG.nodeThresholds.massive) return 'low';
            return 'minimal';
        },

        onChange(callback) {
            this._callbacks.push(callback);
        },

        _notify() {
            this._callbacks.forEach(cb => cb(this._current, this.settings));
        }
    };

    // =========================================================================
    // POSITION OWNERSHIP
    // Enforces single-owner invariant for node positions (fx/fy/fz)
    // =========================================================================

    const OWNERS = ['none', 'transition', 'motion', 'flock', 'force'];

    const PositionOwnership = {
        _current: 'none',
        _animationId: null,

        get current() { return this._current; },

        acquire(owner, animationId = null) {
            if (!OWNERS.includes(owner)) {
                console.warn(`[PERF] Unknown position owner: ${owner}`);
                return false;
            }

            // Cancel any existing animation
            if (this._animationId) {
                cancelAnimationFrame(this._animationId);
                this._animationId = null;
            }

            this._current = owner;
            this._animationId = animationId;
            console.log(`[PERF] Position ownership: ${owner}`);
            return true;
        },

        release(owner) {
            if (this._current === owner) {
                if (this._animationId) {
                    cancelAnimationFrame(this._animationId);
                    this._animationId = null;
                }
                this._current = 'none';
                console.log(`[PERF] Position ownership released by ${owner}`);
            }
        },

        setAnimationId(id) {
            this._animationId = id;
        },

        cancelAnimation() {
            if (this._animationId) {
                cancelAnimationFrame(this._animationId);
                this._animationId = null;
            }
        }
    };

    // =========================================================================
    // ANIMATION SCHEDULER
    // Frame-budget-aware animation with throttling
    // =========================================================================

    const AnimationScheduler = {
        _refreshFrameCounter: 0,

        /**
         * Run a layout transition with frame budget awareness
         * @param {Object} options
         * @param {Array} options.nodes - Array of node objects
         * @param {Function} options.getTargetPosition - (node, index, total) => {x, y, z}
         * @param {number} options.duration - Animation duration in ms
         * @param {Function} options.onFrame - Called each frame with progress (0-1)
         * @param {Function} options.onComplete - Called when animation finishes
         * @param {Function} options.refresh - Function to call to refresh the graph
         */
        runTransition(options) {
            const { nodes, getTargetPosition, duration, onFrame, onComplete, refresh } = options;

            // Acquire ownership
            PositionOwnership.acquire('transition');

            const total = nodes.length;
            const startPos = nodes.map(n => ({ x: n.x || 0, y: n.y || 0, z: n.z || 0 }));
            const targetPos = nodes.map((n, i) => getTargetPosition(n, i, total));

            const startTime = performance.now();
            const settings = AdaptiveQuality.settings;
            const actualDuration = Math.min(duration, settings.animDuration);

            this._refreshFrameCounter = 0;

            const animate = () => {
                // Check if we still own positions
                if (PositionOwnership.current !== 'transition') {
                    console.log('[PERF] Transition interrupted - lost ownership');
                    return;
                }

                const now = performance.now();
                const elapsed = now - startTime;
                const progress = Math.min(1, elapsed / actualDuration);

                // Smoothstep easing
                const eased = progress * progress * (3 - 2 * progress);

                // Update positions
                for (let i = 0; i < nodes.length; i++) {
                    const n = nodes[i];
                    const s = startPos[i];
                    const t = targetPos[i];
                    n.fx = s.x + (t.x - s.x) * eased;
                    n.fy = s.y + (t.y - s.y) * eased;
                    n.fz = s.z + (t.z - s.z) * eased;
                }

                // Throttled refresh based on quality settings
                this._refreshFrameCounter++;
                if (this._refreshFrameCounter >= settings.refreshEvery) {
                    this._refreshFrameCounter = 0;
                    if (refresh) refresh();
                }

                if (onFrame) onFrame(progress);

                if (progress < 1) {
                    const id = requestAnimationFrame(animate);
                    PositionOwnership.setAnimationId(id);
                } else {
                    PositionOwnership.release('transition');
                    if (onComplete) onComplete();
                }
            };

            const id = requestAnimationFrame(animate);
            PositionOwnership.setAnimationId(id);
        },

        /**
         * Run continuous motion (rotate/orbit) with throttling
         */
        runMotion(options) {
            const { nodes, getPosition, speed, refresh } = options;

            PositionOwnership.acquire('motion');

            const total = nodes.length;
            const settings = AdaptiveQuality.settings;
            let time = 0;

            this._refreshFrameCounter = 0;

            const animate = () => {
                if (PositionOwnership.current !== 'motion') {
                    console.log('[PERF] Motion interrupted - lost ownership');
                    return;
                }

                time += speed;

                for (let i = 0; i < nodes.length; i++) {
                    const pos = getPosition(nodes[i], i, total, time);
                    nodes[i].fx = pos.x;
                    nodes[i].fy = pos.y;
                    nodes[i].fz = pos.z;
                }

                // Throttled refresh
                this._refreshFrameCounter++;
                if (this._refreshFrameCounter >= settings.refreshEvery) {
                    this._refreshFrameCounter = 0;
                    if (refresh) refresh();
                }

                const id = requestAnimationFrame(animate);
                PositionOwnership.setAnimationId(id);
            };

            const id = requestAnimationFrame(animate);
            PositionOwnership.setAnimationId(id);
        },

        /**
         * Stop any running animation
         */
        stop() {
            PositionOwnership.cancelAnimation();
            PositionOwnership._current = 'none';
        }
    };

    // =========================================================================
    // HUD OVERLAY
    // Real-time performance display (toggleable)
    // =========================================================================

    const HUD = {
        _element: null,
        _visible: false,
        _updateInterval: null,

        init() {
            this._element = document.createElement('div');
            this._element.id = 'perf-hud';
            this._element.style.cssText = `
                position: fixed;
                bottom: 10px;
                left: 10px;
                background: rgba(0, 0, 0, 0.8);
                color: #0f0;
                font-family: 'SF Mono', Monaco, monospace;
                font-size: 11px;
                padding: 8px 12px;
                border-radius: 4px;
                z-index: 10000;
                display: none;
                min-width: 140px;
                border: 1px solid #333;
            `;
            document.body.appendChild(this._element);
        },

        show() {
            if (!this._element) this.init();
            this._element.style.display = 'block';
            this._visible = true;
            this._startUpdates();
        },

        hide() {
            if (this._element) {
                this._element.style.display = 'none';
            }
            this._visible = false;
            this._stopUpdates();
        },

        toggle() {
            if (this._visible) this.hide();
            else this.show();
        },

        _startUpdates() {
            if (this._updateInterval) return;
            this._updateInterval = setInterval(() => this._update(), 100);
        },

        _stopUpdates() {
            if (this._updateInterval) {
                clearInterval(this._updateInterval);
                this._updateInterval = null;
            }
        },

        _update() {
            if (!this._element || !this._visible) return;

            const stats = PerformanceMonitor.stats;
            const fpsColor = stats.fps >= 55 ? '#0f0' : stats.fps >= 30 ? '#ff0' : '#f00';

            this._element.innerHTML = `
                <div style="color: ${fpsColor}; font-weight: bold;">${stats.fps} FPS</div>
                <div style="color: #888;">Frame: ${stats.lastFrameTime}ms</div>
                <div style="color: #888;">Avg: ${stats.avgFrameTime}ms</div>
                <div style="color: #888;">Drops: ${stats.droppedPercent}%</div>
                <div style="color: #0af;">Quality: ${stats.quality}</div>
                <div style="color: #a0f;">Owner: ${stats.owner}</div>
            `;
        }
    };

    // =========================================================================
    // PUBLIC API
    // =========================================================================

    return {
        monitor: PerformanceMonitor,
        quality: AdaptiveQuality,
        ownership: PositionOwnership,
        scheduler: AnimationScheduler,
        hud: HUD,
        config: CONFIG,

        /**
         * Initialize the performance subsystem
         * @param {number} nodeCount - Number of nodes in the graph
         * @param {Object} tokens - Optional performance tokens from JSON
         */
        init(nodeCount, tokens = null) {
            if (tokens) {
                Object.assign(CONFIG, tokens);
            }
            AdaptiveQuality.init(nodeCount);
            PerformanceMonitor.start();
            HUD.init();
            console.log('[PERF] Performance subsystem initialized');
        },

        /**
         * Check if flock simulation should be enabled
         */
        isFlockAllowed() {
            return AdaptiveQuality.settings.flockEnabled;
        },

        /**
         * Get current animation duration (adjusted for quality)
         */
        getAnimationDuration(requested) {
            return Math.min(requested, AdaptiveQuality.settings.animDuration);
        }
    };
})();

// Export for module systems if available
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PERF;
}
