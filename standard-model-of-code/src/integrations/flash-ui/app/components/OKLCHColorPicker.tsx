/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * OKLCH Color Picker - PROJECT_elements Integration
 * Enhanced with semantic presets from appearance.tokens.json
 */

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { OKLCHColor, SemanticCategory } from '../types';
import {
    toOKLCHString,
    toHex,
    SEMANTIC_PRESETS,
    getAccessibleTextColor,
    generateStates
} from '../../tokens-bridge';

interface OKLCHColorPickerProps {
    color: OKLCHColor;
    onChange: (color: OKLCHColor) => void;
    showPresets?: boolean;
    presetCategory?: SemanticCategory;
}

const OKLCHColorPicker = ({
    color,
    onChange,
    showPresets = true,
    presetCategory = 'tier'
}: OKLCHColorPickerProps) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [activeCategory, setActiveCategory] = useState<SemanticCategory>(presetCategory);

    // Get presets for current category
    const presets = useMemo(() => {
        const category = SEMANTIC_PRESETS[activeCategory as keyof typeof SEMANTIC_PRESETS];
        if (!category) return [];
        return Object.entries(category).map(([key, value]) => ({
            key,
            color: value as OKLCHColor,
            label: (value as any).label || key,
            semantic: (value as any).semantic
        }));
    }, [activeCategory]);

    // Generate state variants
    const states = useMemo(() => generateStates(color), [color]);
    const textColor = useMemo(() => getAccessibleTextColor(color), [color]);

    // Draw the chroma/hue plane at the current lightness
    const drawSpace = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        // Canvas drawing delegated to CSS gradients for performance
    }, [color.l]);

    useEffect(() => {
        drawSpace();
    }, [drawSpace]);

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
            c: (1 - y) * 0.4
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

    const applyPreset = (preset: OKLCHColor) => {
        onChange({
            l: preset.l,
            c: preset.c,
            h: preset.h
        });
    };

    return (
        <div className="oklch-picker-container">
            {/* Main Hue-Chroma Plane */}
            <div
                className="oklch-main-plane"
                ref={containerRef}
                onMouseDown={onMouseDown}
                style={{
                    background: `
                        linear-gradient(to top, oklch(${color.l * 100}% 0 0), transparent),
                        linear-gradient(to right,
                            oklch(${color.l * 100}% 0.4 0),
                            oklch(${color.l * 100}% 0.4 60),
                            oklch(${color.l * 100}% 0.4 120),
                            oklch(${color.l * 100}% 0.4 180),
                            oklch(${color.l * 100}% 0.4 240),
                            oklch(${color.l * 100}% 0.4 300),
                            oklch(${color.l * 100}% 0.4 360)
                        )
                    `
                }}
            >
                <div
                    className="oklch-marker"
                    style={{
                        left: `${(color.h / 360) * 100}%`,
                        top: `${(1 - (color.c / 0.4)) * 100}%`,
                        backgroundColor: toOKLCHString(color),
                        boxShadow: `0 0 10px ${toOKLCHString({ ...color, alpha: 0.5 })}`
                    }}
                />
            </div>

            {/* Controls */}
            <div className="oklch-controls">
                {/* Lightness Slider */}
                <div className="oklch-slider-row">
                    <span>L</span>
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
                    <span className="val">{Math.round(color.l * 100)}%</span>
                </div>

                {/* Chroma Slider */}
                <div className="oklch-slider-row">
                    <span>C</span>
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
                    <span className="val">{color.c.toFixed(3)}</span>
                </div>

                {/* Preview Row */}
                <div className="oklch-preview-row">
                    <div
                        className="swatch"
                        style={{ background: toOKLCHString(color) }}
                    >
                        <span style={{ color: toOKLCHString(textColor) }}>Aa</span>
                    </div>
                    <div className="color-codes">
                        <code className="val">{toOKLCHString(color)}</code>
                        <code className="hex">{toHex(color)}</code>
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
                                className={`preset-tab ${activeCategory === cat ? 'active' : ''}`}
                                onClick={() => setActiveCategory(cat)}
                            >
                                {cat}
                            </button>
                        ))}
                    </div>
                    <div className="preset-grid">
                        {presets.map(({ key, color: presetColor, label, semantic }) => (
                            <button
                                key={key}
                                className="preset-swatch"
                                onClick={() => applyPreset(presetColor)}
                                title={`${label} - ${semantic}`}
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

            {/* State Preview */}
            <div className="oklch-states">
                <div className="state-row">
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
        </div>
    );
};

export default OKLCHColorPicker;
