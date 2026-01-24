/**
 * COLOR TELEMETRY ENGINE (CTE)
 *
 * Observability layer for the OKLCH color system.
 * Treats every OKLCH->hex conversion as a measurable "emission event".
 *
 * Two realms:
 * - OKLCH Ideal Realm: continuous, mathematical, device-independent
 * - Physical Display Realm: bounded by gamut (sRGB/P3/Rec2020), quantized
 *
 * Metrics:
 * - unique_oklch: distinct intended colors (quantized)
 * - unique_output: distinct emitted hex colors
 * - collapse_ratio: unique_output / unique_oklch (information loss)
 * - clip_rate: out-of-gamut colors / total emissions
 *
 * Usage:
 *   COLOR_TELEM.capture(() => { ...render colors... })  // Snapshot mode
 *   COLOR_TELEM.startLive(); COLOR_TELEM.hud.toggle();  // Live mode + HUD
 *
 * @module COLOR_TELEM
 * @version 1.0.0
 */
(function () {
    'use strict';

    const TELEM = {
        enabled: false,
        mode: 'off', // 'off' | 'capture' | 'live'
        frameId: 0,

        // Capture quantization (precise uniqueness; used with Sets)
        captureQ: { l: 0.001, c: 0.001, h: 0.1 },

        // Live quantization (cheap per-frame uniqueness; used with bitsets)
        liveQ: { l: 0.01, c: 0.01, h: 1.0, cMax: 0.4 },

        // Counters
        _events: 0,
        _uniqueOk: 0,
        _uniqueOut: 0,
        _clipped: 0,
        _startTs: 0,

        // Capture-only structures
        _cap_okSet: null,
        _cap_outSet: null,
        _cap_bySource: null, // Map(source -> {events, okSet, outSet, clipped})

        // Live-only structures (bitsets)
        _live_okBits: null,
        _live_okTouchedWords: null,
        _live_okTouchedPtr: 0,
        _live_outBits: null,
        _live_outTouchedWords: null,
        _live_outTouchedPtr: 0,
        _live_okMeta: null,

        _last: null
    };

    // =========================================================================
    // HELPERS
    // =========================================================================

    function now() {
        return (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
    }

    function parseHex24(hex) {
        if (typeof hex === 'number') return (hex >>> 0) & 0xFFFFFF;
        if (!hex || hex[0] !== '#' || hex.length !== 7) return null;
        return parseInt(hex.slice(1), 16) & 0xFFFFFF;
    }

    function hueWrap(h) {
        return ((h % 360) + 360) % 360;
    }

    // Pack quantized OKLCH into a 32-bit key (capture mode)
    // Lq: 0..1023, Cq: 0..1023, Hq: 0..4095
    function packOkKey(l, c, h) {
        const Lq = Math.max(0, Math.min(1023, Math.round(l / TELEM.captureQ.l)));
        const Cq = Math.max(0, Math.min(1023, Math.round(c / TELEM.captureQ.c)));
        const Hq = Math.max(0, Math.min(4095, Math.round(hueWrap(h) / TELEM.captureQ.h)));
        return ((Lq << 22) | (Cq << 12) | Hq) >>> 0;
    }

    // =========================================================================
    // BITSET UTILITIES (Live Mode - Zero Allocation)
    // =========================================================================

    function makeBitset(bitCount) {
        return new Uint32Array(((bitCount + 31) / 32) | 0);
    }

    function testAndSetBit(bitset, bitIndex) {
        const wordIndex = bitIndex >>> 5;
        const mask = 1 << (bitIndex & 31);
        const before = bitset[wordIndex];
        if (before & mask) return { changed: false, wordIndex, before };
        bitset[wordIndex] = before | mask;
        return { changed: true, wordIndex, before };
    }

    function touchWord(touchedArrRef, ptrRefName, wordIndex, beforeWordValue) {
        // Only record the word if it was previously 0 -> now non-zero.
        if (beforeWordValue !== 0) return;

        let arr = TELEM[touchedArrRef];
        let ptr = TELEM[ptrRefName];

        if (ptr >= arr.length) {
            const bigger = new Uint32Array(arr.length * 2);
            bigger.set(arr);
            arr = bigger;
            TELEM[touchedArrRef] = arr;
        }

        arr[ptr] = wordIndex;
        TELEM[ptrRefName] = ptr + 1;
    }

    function clearTouched(bitset, touchedWords, ptr) {
        for (let i = 0; i < ptr; i++) bitset[touchedWords[i]] = 0;
    }

    function ensureLiveBitsets() {
        // Output color bitset: 24-bit RGB => 16,777,216 bits => 524,288 words (~2MB)
        if (!TELEM._live_outBits) {
            TELEM._live_outBits = makeBitset(1 << 24);
            TELEM._live_outTouchedWords = new Uint32Array(4096);
            TELEM._live_outTouchedPtr = 0;
        }

        // OKLCH bitset: quantized grid size
        if (!TELEM._live_okBits) {
            const Lbins = Math.floor(1 / TELEM.liveQ.l) + 1;
            const Cbins = Math.floor(TELEM.liveQ.cMax / TELEM.liveQ.c) + 1;
            const Hbins = Math.floor(360 / TELEM.liveQ.h);

            TELEM._live_okMeta = { Lbins, Cbins, Hbins };
            TELEM._live_okBits = makeBitset(Lbins * Cbins * Hbins);
            TELEM._live_okTouchedWords = new Uint32Array(4096);
            TELEM._live_okTouchedPtr = 0;
        }
    }

    // =========================================================================
    // GAMUT DETECTION
    // =========================================================================

    TELEM.detectGamut = function () {
        if (typeof window === 'undefined' || !window.matchMedia) return 'unknown';
        if (window.matchMedia('(color-gamut: rec2020)').matches) return 'rec2020';
        if (window.matchMedia('(color-gamut: p3)').matches) return 'p3';
        if (window.matchMedia('(color-gamut: srgb)').matches) return 'srgb';
        return 'unknown';
    };

    TELEM.watchGamut = function (onChange) {
        if (typeof window === 'undefined' || !window.matchMedia) return () => {};
        const mq = window.matchMedia('(color-gamut: p3)');

        const handler = () => onChange && onChange(TELEM.detectGamut());

        if (mq.addEventListener) {
            mq.addEventListener('change', handler);
        } else if (mq.addListener) {
            mq.addListener(handler);
        }

        return () => {
            if (mq.removeEventListener) {
                mq.removeEventListener('change', handler);
            } else if (mq.removeListener) {
                mq.removeListener(handler);
            }
        };
    };

    // =========================================================================
    // FRAME LIFECYCLE
    // =========================================================================

    TELEM.begin = function (frameId = null) {
        TELEM.frameId = frameId != null ? frameId : (TELEM.frameId + 1);
        TELEM._events = 0;
        TELEM._uniqueOk = 0;
        TELEM._uniqueOut = 0;
        TELEM._clipped = 0;
        TELEM._startTs = now();
    };

    TELEM.end = function () {
        const ms = now() - TELEM._startTs;
        const collapse = TELEM._uniqueOk ? (TELEM._uniqueOut / TELEM._uniqueOk) : 1;
        const clipRate = TELEM._events ? (TELEM._clipped / TELEM._events) : 0;

        const metrics = {
            frameId: TELEM.frameId,
            ms,
            gamut: TELEM.detectGamut(),
            events: TELEM._events,
            unique_oklch: TELEM._uniqueOk,
            unique_output: TELEM._uniqueOut,
            collapse_ratio: collapse,
            clipped_events: TELEM._clipped,
            clip_rate: clipRate
        };

        TELEM._last = metrics;
        if (TELEM.hud && TELEM.hud._enabled) TELEM.hud.render(metrics);

        // Cleanup live bitsets
        if (TELEM.mode === 'live') {
            clearTouched(TELEM._live_outBits, TELEM._live_outTouchedWords, TELEM._live_outTouchedPtr);
            clearTouched(TELEM._live_okBits, TELEM._live_okTouchedWords, TELEM._live_okTouchedPtr);
            TELEM._live_outTouchedPtr = 0;
            TELEM._live_okTouchedPtr = 0;
        }

        // Cleanup capture sets
        if (TELEM.mode === 'capture') {
            TELEM._cap_okSet = null;
            TELEM._cap_outSet = null;
            TELEM._cap_bySource = null;
            TELEM.enabled = false;
            TELEM.mode = 'off';
        }

        return metrics;
    };

    // =========================================================================
    // CAPTURE MODE (Snapshot - One-shot census)
    // =========================================================================

    TELEM.capture = function (fn, { frameId = null, perSource = true } = {}) {
        TELEM.enabled = true;
        TELEM.mode = 'capture';
        TELEM._cap_okSet = new Set();
        TELEM._cap_outSet = new Set();
        TELEM._cap_bySource = perSource ? new Map() : null;

        TELEM.begin(frameId);

        try {
            fn();
        } finally {
            // Finalize counts from sets
            TELEM._uniqueOk = TELEM._cap_okSet.size;
            TELEM._uniqueOut = TELEM._cap_outSet.size;
        }

        const m = TELEM.end();

        // Add per-source breakdown if requested
        if (perSource && TELEM._cap_bySource && TELEM._cap_bySource.size > 0) {
            m.bySource = {};
            for (const [src, data] of TELEM._cap_bySource) {
                m.bySource[src] = {
                    events: data.events,
                    unique_oklch: data.okSet.size,
                    unique_output: data.outSet.size,
                    collapse_ratio: data.okSet.size ? (data.outSet.size / data.okSet.size) : 1,
                    clipped: data.clipped
                };
            }
        }

        return m;
    };

    // =========================================================================
    // EMIT (Called by COLOR engine at wormhole boundary)
    // =========================================================================

    TELEM.emit = function (source, l, c, h, out, clipped = false) {
        if (!TELEM.enabled) return;

        TELEM._events++;
        if (clipped) TELEM._clipped++;

        if (TELEM.mode === 'capture') {
            TELEM._cap_okSet.add(packOkKey(l, c, h));
            const rgb24 = parseHex24(out);
            if (rgb24 != null) TELEM._cap_outSet.add(rgb24);

            if (TELEM._cap_bySource) {
                const key = String(source || 'unknown');
                let s = TELEM._cap_bySource.get(key);
                if (!s) {
                    s = { events: 0, clipped: 0, okSet: new Set(), outSet: new Set() };
                    TELEM._cap_bySource.set(key, s);
                }
                s.events++;
                if (clipped) s.clipped++;
                s.okSet.add(packOkKey(l, c, h));
                if (rgb24 != null) s.outSet.add(rgb24);
            }
            return;
        }

        if (TELEM.mode === 'live') {
            ensureLiveBitsets();

            // Output unique (exact 24-bit)
            const rgb24 = parseHex24(out);
            if (rgb24 != null) {
                const r = testAndSetBit(TELEM._live_outBits, rgb24);
                if (r.changed) {
                    TELEM._uniqueOut++;
                    touchWord('_live_outTouchedWords', '_live_outTouchedPtr', r.wordIndex, r.before);
                }
            }

            // OKLCH unique (quantized grid)
            const meta = TELEM._live_okMeta;
            const Lbin = Math.max(0, Math.min(meta.Lbins - 1, Math.round(l / TELEM.liveQ.l)));
            const Cbin = Math.max(0, Math.min(meta.Cbins - 1, Math.round(c / TELEM.liveQ.c)));
            const Hbin = Math.max(0, Math.min(meta.Hbins - 1, Math.floor(hueWrap(h) / TELEM.liveQ.h)));
            const idx = ((Lbin * meta.Cbins + Cbin) * meta.Hbins + Hbin) | 0;

            const r2 = testAndSetBit(TELEM._live_okBits, idx);
            if (r2.changed) {
                TELEM._uniqueOk++;
                touchWord('_live_okTouchedWords', '_live_okTouchedPtr', r2.wordIndex, r2.before);
            }
        }
    };

    // =========================================================================
    // LIVE MODE (Continuous monitoring)
    // =========================================================================

    TELEM.startLive = function () {
        TELEM.enabled = true;
        TELEM.mode = 'live';
        ensureLiveBitsets();

        let started = false;

        const loop = (ts) => {
            if (TELEM.mode !== 'live') return;

            if (!started) {
                TELEM.begin(ts);
                started = true;
            } else {
                TELEM.end();      // Closes the previous frame
                TELEM.begin(ts);  // Opens the next frame
            }

            requestAnimationFrame(loop);
        };

        requestAnimationFrame(loop);
        console.log('[COLOR_TELEM] Live mode started');
    };

    TELEM.stop = function () {
        if (TELEM.mode === 'live') {
            TELEM.end();
        }
        TELEM.enabled = false;
        TELEM.mode = 'off';
        console.log('[COLOR_TELEM] Stopped');
    };

    // =========================================================================
    // HUD OVERLAY
    // =========================================================================

    TELEM.hud = {
        _enabled: false,
        _el: null,

        toggle() {
            this._enabled = !this._enabled;
            if (this._enabled) this.mount();
            else this.unmount();
            if (TELEM._last) this.render(TELEM._last);
            return this._enabled;
        },

        mount() {
            if (this._el) return;
            const el = document.createElement('div');
            el.id = 'color-telemetry-hud';
            el.style.cssText = [
                'position:fixed',
                'right:12px',
                'bottom:12px',
                'z-index:99999',
                'padding:10px 14px',
                'border-radius:8px',
                'background:rgba(0,0,0,0.85)',
                'backdrop-filter:blur(8px)',
                'border:1px solid rgba(255,255,255,0.1)',
                'color:#fff',
                'font:11px/1.4 ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace',
                'pointer-events:none',
                'white-space:pre',
                'box-shadow:0 4px 20px rgba(0,0,0,0.4)'
            ].join(';');
            el.textContent = 'COLOR_TELEM\nInitializing...';
            document.body.appendChild(el);
            this._el = el;
        },

        unmount() {
            this._el?.remove();
            this._el = null;
        },

        render(m) {
            if (!this._el) return;

            const gamutColor = m.gamut === 'p3' ? '#4ade80' : m.gamut === 'rec2020' ? '#a78bfa' : '#94a3b8';
            const collapseColor = m.collapse_ratio > 0.9 ? '#4ade80' : m.collapse_ratio > 0.5 ? '#fbbf24' : '#f87171';
            const clipColor = m.clip_rate < 0.01 ? '#4ade80' : m.clip_rate < 0.1 ? '#fbbf24' : '#f87171';

            this._el.innerHTML =
                `<span style="color:#60a5fa;font-weight:600">COLOR_TELEM</span>\n` +
                `<span style="color:${gamutColor}">gamut: ${m.gamut}</span>\n` +
                `events: ${m.events.toLocaleString()}\n` +
                `unique OKLCH: ${m.unique_oklch.toLocaleString()}\n` +
                `unique output: ${m.unique_output.toLocaleString()}\n` +
                `<span style="color:${collapseColor}">collapse: ${(m.collapse_ratio * 100).toFixed(1)}%</span>\n` +
                `<span style="color:${clipColor}">clip: ${(m.clip_rate * 100).toFixed(2)}% (${m.clipped_events})</span>\n` +
                `frame: ${m.ms.toFixed(2)}ms`;
        }
    };

    // =========================================================================
    // DEBUG / UTILITIES
    // =========================================================================

    TELEM.getLast = function () {
        return TELEM._last;
    };

    TELEM.debug = function () {
        console.log('[COLOR_TELEM] State:', {
            enabled: TELEM.enabled,
            mode: TELEM.mode,
            frameId: TELEM.frameId,
            gamut: TELEM.detectGamut(),
            last: TELEM._last
        });
    };

    // =========================================================================
    // EXPORT
    // =========================================================================

    window.COLOR_TELEM = TELEM;

    console.log('[Module] COLOR_TELEM loaded - OKLCH color observability engine');
})();
