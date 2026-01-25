/**
 * OKLCH COLOR PICKER - PROJECT_elements Integration
 *
 * Enhanced color picker that integrates with the PROJECT_elements
 * design token system and COLOR engine.
 *
 * Features:
 * - 3D OKLCH plane (Hue x Chroma with Lightness slider)
 * - Semantic preset selection from appearance.tokens.json
 * - Gamut boundary visualization
 * - Accessibility contrast preview
 *
 * @license Apache-2.0
 */

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import {
    OKLCHColor,
    toOKLCHString,
    toHex,
    parseOKLCH,
    SEMANTIC_PRESETS,
    generateStates,
    getAccessibleTextColor,
    type SemanticCategory
} from './tokens-bridge';

// =============================================================================
// TYPES
// =============================================================================

interface OKLCHColorPickerProps {
    color: OKLCHColor;
    onChange: (color: OKLCHColor) => void;
    showPresets?: boolean;
    presetCategory?: SemanticCategory;
    showAccessibility?: boolean;
    showGamut?: boolean;
    compact?: boolean;
}

// =============================================================================
// GAMUT DETECTION
// =============================================================================

/**
 * Check if OKLCH color is within sRGB gamut
 * Uses CSS.supports for browser-native detection
 */
function isInGamut(color: OKLCHColor): boolean {
    if (typeof CSS === 'undefined' || !CSS.supports) {
        // Fallback: approximate check
        // High chroma + mid-lightness = likely out of gamut
        const criticalChroma = 0.4 - Math.abs(color.l - 0.5) * 0.5;
        return color.c <= criticalChroma;
    }

    const cssColor = toOKLCHString(color);
    return CSS.supports('color', cssColor);
}

/**
 * Get max chroma for a given hue and lightness in sRGB
 */
function getMaxChroma(h: number, l: number): number {
    // Binary search for gamut boundary
    let min = 0, max = 0.4, mid = 0.2;
    for (let i = 0; i < 10; i++) {
        mid = (min + max) / 2;
        if (isInGamut({ l, c: mid, h })) {
            min = mid;
        } else {
            max = mid;
        }
    }
    return min;
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

const OKLCHColorPicker: React.FC<OKLCHColorPickerProps> = ({
    color,
    onChange,
    showPresets = true,
    presetCategory = 'tier',
    showAccessibility = true,
    showGamut = true,
    compact = false
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [activePresetCategory, setActivePresetCategory] = useState<SemanticCategory>(presetCategory);

    // Gamut boundary cache
    const gamutBoundary = useMemo(() => {
        if (!showGamut) return null;
        const boundary: number[] = [];
        for (let h = 0; h < 360; h += 5) {
            boundary.push(getMaxChroma(h, color.l));
        }
        return boundary;
    }, [color.l, showGamut]);

    // ==========================================================================
    // CANVAS RENDERING
    // ==========================================================================

    const drawColorSpace = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const width = canvas.width;
        const height = canvas.height;

        // Clear
        ctx.clearRect(0, 0, width, height);

        // Draw the hue-chroma plane using CSS gradients (performant)
        // X = Hue (0-360), Y = Chroma (0-0.4 inverted)

        // Create gradient for the color plane
        const gradient = ctx.createLinearGradient(0, 0, width, 0);
        const steps = 12;
        for (let i = 0; i <= steps; i++) {
            const h = (i / steps) * 360;
            const cssColor = `oklch(${color.l * 100}% 0.25 ${h})`;
            gradient.addColorStop(i / steps, cssColor);
        }

        // Fill with hue gradient
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);

        // Overlay chroma fade (top = high chroma, bottom = low chroma)
        const chromaGradient = ctx.createLinearGradient(0, 0, 0, height);
        chromaGradient.addColorStop(0, `oklch(${color.l * 100}% 0 0 / 0)`);
        chromaGradient.addColorStop(1, `oklch(${color.l * 100}% 0 0 / 1)`);
        ctx.fillStyle = chromaGradient;
        ctx.fillRect(0, 0, width, height);

        // Draw gamut boundary
        if (gamutBoundary && showGamut) {
            ctx.strokeStyle = 'rgba(255,255,255,0.3)';
            ctx.lineWidth = 1;
            ctx.beginPath();

            gamutBoundary.forEach((maxC, i) => {
                const h = i * 5;
                const x = (h / 360) * width;
                const y = (1 - maxC / 0.4) * height;
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });

            ctx.stroke();

            // Label
            ctx.fillStyle = 'rgba(255,255,255,0.5)';
            ctx.font = '10px system-ui';
            ctx.fillText('sRGB Gamut', 5, height - 5);
        }
    }, [color.l, gamutBoundary, showGamut]);

    useEffect(() => {
        drawColorSpace();
    }, [drawColorSpace]);

    // ==========================================================================
    // INTERACTION HANDLERS
    // ==========================================================================

    const handleInteract = (e: React.MouseEvent | React.TouchEvent | MouseEvent | TouchEvent) => {
        if (!containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        const clientX = 'touches' in e ? e.touches[0].clientX : (e as MouseEvent).clientX;
        const clientY = 'touches' in e ? e.touches[0].clientY : (e as MouseEvent).clientY;

        const x = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
        const y = Math.max(0, Math.min(1, (clientY - rect.top) / rect.height));

        onChange({
            ...color,
            h: x * 360,
            c: Math.min((1 - y) * 0.4, 0.4)
        });
    };

    const onMouseDown = (e: React.MouseEvent) => {
        setIsDragging(true);
        handleInteract(e);
    };

    useEffect(() => {
        const onMouseMove = (e: MouseEvent) => isDragging && handleInteract(e);
        const onMouseUp = () => setIsDragging(false);

        if (isDragging) {
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
        }
        return () => {
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
        };
    }, [isDragging]);

    // ==========================================================================
    // PRESET HANDLING
    // ==========================================================================

    const presets = useMemo(() => {
        const category = SEMANTIC_PRESETS[activePresetCategory as keyof typeof SEMANTIC_PRESETS];
        if (!category) return [];
        return Object.entries(category).map(([key, value]) => ({
            key,
            color: value as OKLCHColor,
            label: (value as any).label || key
        }));
    }, [activePresetCategory]);

    const applyPreset = (preset: OKLCHColor) => {
        onChange({
            l: preset.l,
            c: preset.c,
            h: preset.h
        });
    };

    // ==========================================================================
    // ACCESSIBILITY PREVIEW
    // ==========================================================================

    const states = useMemo(() => generateStates(color), [color]);
    const textColor = useMemo(() => getAccessibleTextColor(color), [color]);
    const isOutOfGamut = useMemo(() => !isInGamut(color), [color]);

    // ==========================================================================
    // RENDER
    // ==========================================================================

    return (
        <div className={`oklch-picker-v2 ${compact ? 'compact' : ''}`}>
            {/* Main Color Plane */}
            <div
                className="oklch-plane"
                ref={containerRef}
                onMouseDown={onMouseDown}
            >
                <canvas
                    ref={canvasRef}
                    width={compact ? 200 : 280}
                    height={compact ? 120 : 160}
                />

                {/* Color Marker */}
                <div
                    className={`oklch-marker ${isOutOfGamut ? 'out-of-gamut' : ''}`}
                    style={{
                        left: `${(color.h / 360) * 100}%`,
                        top: `${(1 - color.c / 0.4) * 100}%`,
                        backgroundColor: toOKLCHString(color),
                        boxShadow: `0 0 8px ${toOKLCHString(color)}`
                    }}
                >
                    {isOutOfGamut && <span className="gamut-warning">!</span>}
                </div>
            </div>

            {/* Controls */}
            <div className="oklch-controls">
                {/* Lightness Slider */}
                <div className="oklch-slider-row">
                    <span className="slider-label">L</span>
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={color.l}
                        onChange={(e) => onChange({ ...color, l: parseFloat(e.target.value) })}
                        style={{
                            background: `linear-gradient(to right,
                                oklch(0% ${color.c} ${color.h}),
                                oklch(50% ${color.c} ${color.h}),
                                oklch(100% ${color.c} ${color.h}))`
                        }}
                    />
                    <span className="slider-value">{Math.round(color.l * 100)}%</span>
                </div>

                {/* Chroma Slider */}
                <div className="oklch-slider-row">
                    <span className="slider-label">C</span>
                    <input
                        type="range"
                        min="0"
                        max="0.4"
                        step="0.005"
                        value={color.c}
                        onChange={(e) => onChange({ ...color, c: parseFloat(e.target.value) })}
                        style={{
                            background: `linear-gradient(to right,
                                oklch(${color.l * 100}% 0 ${color.h}),
                                oklch(${color.l * 100}% 0.2 ${color.h}),
                                oklch(${color.l * 100}% 0.4 ${color.h}))`
                        }}
                    />
                    <span className="slider-value">{color.c.toFixed(3)}</span>
                </div>

                {/* Hue Slider */}
                <div className="oklch-slider-row">
                    <span className="slider-label">H</span>
                    <input
                        type="range"
                        min="0"
                        max="360"
                        step="1"
                        value={color.h}
                        onChange={(e) => onChange({ ...color, h: parseFloat(e.target.value) })}
                        className="hue-slider"
                    />
                    <span className="slider-value">{Math.round(color.h)}°</span>
                </div>

                {/* Preview & Values */}
                <div className="oklch-preview-row">
                    <div
                        className="color-swatch"
                        style={{ backgroundColor: toOKLCHString(color) }}
                    >
                        <span style={{ color: toOKLCHString(textColor) }}>Aa</span>
                    </div>
                    <div className="color-values">
                        <code className="oklch-code">{toOKLCHString(color)}</code>
                        <code className="hex-code">{toHex(color)}</code>
                    </div>
                </div>
            </div>

            {/* Semantic Presets */}
            {showPresets && (
                <div className="oklch-presets">
                    <div className="preset-tabs">
                        {(['tier', 'family', 'ring', 'semanticRole'] as SemanticCategory[]).map((cat) => (
                            <button
                                key={cat}
                                className={`preset-tab ${activePresetCategory === cat ? 'active' : ''}`}
                                onClick={() => setActivePresetCategory(cat)}
                            >
                                {cat}
                            </button>
                        ))}
                    </div>
                    <div className="preset-grid">
                        {presets.map(({ key, color: presetColor, label }) => (
                            <button
                                key={key}
                                className="preset-swatch"
                                onClick={() => applyPreset(presetColor)}
                                title={label}
                                style={{ backgroundColor: toOKLCHString(presetColor) }}
                            >
                                <span style={{ color: toOKLCHString(getAccessibleTextColor(presetColor)) }}>
                                    {key}
                                </span>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Accessibility States */}
            {showAccessibility && !compact && (
                <div className="oklch-accessibility">
                    <div className="accessibility-label">States</div>
                    <div className="state-swatches">
                        <div className="state-swatch" style={{ backgroundColor: toOKLCHString(states.default) }}>
                            <span>default</span>
                        </div>
                        <div className="state-swatch" style={{ backgroundColor: toOKLCHString(states.hover) }}>
                            <span>hover</span>
                        </div>
                        <div className="state-swatch" style={{ backgroundColor: toOKLCHString(states.active) }}>
                            <span>active</span>
                        </div>
                        <div className="state-swatch" style={{ backgroundColor: toOKLCHString(states.disabled) }}>
                            <span>disabled</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default OKLCHColorPicker;

// =============================================================================
// STYLES (Inline for portability)
// =============================================================================

export const OKLCHPickerStyles = `
.oklch-picker-v2 {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 12px;
    background: oklch(18% 0.01 250 / 0.9);
    border-radius: 12px;
    font-family: system-ui, sans-serif;
    max-width: 320px;
}

.oklch-picker-v2.compact {
    max-width: 240px;
    padding: 8px;
    gap: 8px;
}

.oklch-plane {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    cursor: crosshair;
}

.oklch-plane canvas {
    display: block;
    width: 100%;
    height: auto;
}

.oklch-marker {
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid white;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    transition: box-shadow 0.15s;
}

.oklch-marker.out-of-gamut {
    border-color: #ff4444;
}

.oklch-marker .gamut-warning {
    position: absolute;
    top: -18px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 10px;
    color: #ff4444;
    font-weight: bold;
}

.oklch-controls {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.oklch-slider-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.slider-label {
    width: 14px;
    font-size: 11px;
    color: oklch(70% 0 0);
    font-weight: 500;
}

.oklch-slider-row input[type="range"] {
    flex: 1;
    height: 6px;
    -webkit-appearance: none;
    background: oklch(30% 0.02 250);
    border-radius: 3px;
}

.oklch-slider-row input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 14px;
    height: 14px;
    background: white;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
}

.hue-slider {
    background: linear-gradient(to right,
        oklch(65% 0.25 0),
        oklch(65% 0.25 60),
        oklch(65% 0.25 120),
        oklch(65% 0.25 180),
        oklch(65% 0.25 240),
        oklch(65% 0.25 300),
        oklch(65% 0.25 360)
    ) !important;
}

.slider-value {
    width: 42px;
    font-size: 11px;
    color: oklch(80% 0 0);
    text-align: right;
    font-variant-numeric: tabular-nums;
}

.oklch-preview-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px;
    background: oklch(12% 0.01 250);
    border-radius: 8px;
}

.color-swatch {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 600;
}

.color-values {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.color-values code {
    font-size: 11px;
    color: oklch(70% 0 0);
    font-family: 'SF Mono', 'Fira Code', monospace;
}

.hex-code {
    color: oklch(55% 0 0) !important;
}

.oklch-presets {
    border-top: 1px solid oklch(25% 0.02 250);
    padding-top: 10px;
}

.preset-tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 8px;
}

.preset-tab {
    padding: 4px 8px;
    font-size: 10px;
    background: oklch(22% 0.01 250);
    border: none;
    border-radius: 4px;
    color: oklch(60% 0 0);
    cursor: pointer;
    text-transform: capitalize;
}

.preset-tab.active {
    background: oklch(30% 0.02 250);
    color: oklch(85% 0 0);
}

.preset-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(48px, 1fr));
    gap: 6px;
}

.preset-swatch {
    height: 32px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 9px;
    font-weight: 500;
    transition: transform 0.1s;
}

.preset-swatch:hover {
    transform: scale(1.08);
}

.preset-swatch span {
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.oklch-accessibility {
    border-top: 1px solid oklch(25% 0.02 250);
    padding-top: 10px;
}

.accessibility-label {
    font-size: 10px;
    color: oklch(55% 0 0);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.state-swatches {
    display: flex;
    gap: 6px;
}

.state-swatch {
    flex: 1;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.state-swatch span {
    font-size: 9px;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}
`;
