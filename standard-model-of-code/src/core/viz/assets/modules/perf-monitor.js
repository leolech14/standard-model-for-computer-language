/**
 * @module perf-monitor
 * @description Real-time performance monitoring and FPS diagnostics
 * @responsibility Track frame delivery, detect dropped frames, display HUD
 */

// NOTE: Named _PerfMonitorImpl to avoid conflict with performance.js PERF
const _PerfMonitorImpl = (function() {
    'use strict';

    // Configuration
    const _config = {
        enabled: true,
        maxFrames: 60,
        droppedFrameThreshold: 50  // ms (>50ms = <20fps)
    };

    // State
    const _state = {
        fps: 0,
        frameTime: 0,
        lastFrameTime: 0,
        frameTimes: [],
        renderCalls: 0,
        droppedFrames: 0,
        lastSecond: 0,
        framesThisSecond: 0,
        hudElement: null,
        monitoring: false
    };

    /**
     * Initialize the performance monitor
     */
    function init() {
        if (!_config.enabled) return;

        // Create HUD element
        _state.hudElement = document.createElement('div');
        _state.hudElement.id = 'perf-hud';
        _state.hudElement.style.cssText = `
            position: fixed; top: 10px; right: 10px; z-index: 99999;
            background: rgba(0,0,0,0.85); color: #0f0; font-family: monospace;
            font-size: 11px; padding: 8px 12px; border-radius: 4px;
            border: 1px solid #333; min-width: 140px; pointer-events: none;
        `;
        document.body.appendChild(_state.hudElement);
        _startMonitoring();
    }

    /**
     * Start the monitoring loop
     */
    function _startMonitoring() {
        if (_state.monitoring) return;
        _state.monitoring = true;

        const monitor = () => {
            if (!_state.monitoring) return;

            const now = performance.now();

            // Calculate frame time
            if (_state.lastFrameTime > 0) {
                _state.frameTime = now - _state.lastFrameTime;
                _state.frameTimes.push(_state.frameTime);
                if (_state.frameTimes.length > _config.maxFrames) {
                    _state.frameTimes.shift();
                }

                // Detect dropped frames
                if (_state.frameTime > _config.droppedFrameThreshold) {
                    _state.droppedFrames++;
                }
            }
            _state.lastFrameTime = now;

            // Calculate FPS every second
            const second = Math.floor(now / 1000);
            if (second !== _state.lastSecond) {
                _state.fps = _state.framesThisSecond;
                _state.framesThisSecond = 0;
                _state.lastSecond = second;
            }
            _state.framesThisSecond++;

            // Update HUD
            _updateHUD();
            requestAnimationFrame(monitor);
        };
        requestAnimationFrame(monitor);
    }

    /**
     * Update the HUD display
     */
    function _updateHUD() {
        if (!_state.hudElement) return;

        const avgFrameTime = _state.frameTimes.length > 0
            ? (_state.frameTimes.reduce((a, b) => a + b, 0) / _state.frameTimes.length).toFixed(1)
            : '0.0';

        // Color code FPS
        let fpsColor = '#0f0';  // Green = good
        if (_state.fps < 30) fpsColor = '#ff0';  // Yellow = warning
        if (_state.fps < 15) fpsColor = '#f00';  // Red = bad

        // Animation state - use ANIM module if available
        const isAnimating = typeof ANIM !== 'undefined' && ANIM.isAnimating;
        const animating = isAnimating ? '▶ ANIMATING' : '■ IDLE';
        const animColor = isAnimating ? '#0ff' : '#666';
        const staggerPattern = (typeof ANIM !== 'undefined' && ANIM.staggerPattern) || 'none';

        _state.hudElement.innerHTML = `
            <div style="color:${fpsColor};font-size:14px;font-weight:bold">${_state.fps} FPS</div>
            <div>Frame: ${avgFrameTime}ms</div>
            <div>Dropped: <span style="color:${_state.droppedFrames > 10 ? '#f00' : '#0f0'}">${_state.droppedFrames}</span></div>
            <div style="color:${animColor}">${animating}</div>
            <div style="font-size:9px;color:#666;margin-top:4px">Pattern: ${staggerPattern}</div>
        `;
    }

    /**
     * Log a performance resistance point
     * @param {string} location - Where the resistance occurred
     * @param {number} duration - Duration in milliseconds
     */
    function logResistance(location, duration) {
        if (duration > 16) {
            console.warn(`[PERF RESISTANCE] ${location}: ${duration.toFixed(1)}ms (>${Math.floor(duration / 16.67)} frames)`);
        }
    }

    /**
     * Stop monitoring
     */
    function stop() {
        _state.monitoring = false;
        if (_state.hudElement && _state.hudElement.parentNode) {
            _state.hudElement.parentNode.removeChild(_state.hudElement);
        }
        _state.hudElement = null;
    }

    /**
     * Reset statistics
     */
    function reset() {
        _state.fps = 0;
        _state.frameTime = 0;
        _state.frameTimes = [];
        _state.droppedFrames = 0;
        _state.framesThisSecond = 0;
    }

    /**
     * Toggle HUD visibility
     */
    function toggle() {
        if (_state.hudElement) {
            _state.hudElement.style.display =
                _state.hudElement.style.display === 'none' ? 'block' : 'none';
        }
    }

    /**
     * Enable/disable monitoring
     * @param {boolean} enabled
     */
    function setEnabled(enabled) {
        _config.enabled = enabled;
        if (!enabled) {
            stop();
        } else if (!_state.monitoring) {
            init();
        }
    }

    // Public API
    return {
        init,
        stop,
        reset,
        toggle,
        setEnabled,
        logResistance,
        // Read-only state access
        get fps() { return _state.fps; },
        get frameTime() { return _state.frameTime; },
        get droppedFrames() { return _state.droppedFrames; },
        get enabled() { return _config.enabled; },
        get monitoring() { return _state.monitoring; }
    };
})();

// Export as PERF_MONITOR (PERF is provided by performance.js)
const PERF_MONITOR = _PerfMonitorImpl;

// Expose globally - only PERF_MONITOR, PERF comes from performance.js
window.PERF_MONITOR = PERF_MONITOR;
