/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * FLASH UI - PROJECT_elements Integration
 * Full Gemini engine with Copycat feature + Design Token intelligence
 *
 * Original: ammaar@google.com
 * Integration: PROJECT_elements OKLCH system
 */

import { GoogleGenAI } from '@google/genai';
import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import ReactDOM from 'react-dom/client';

import { Artifact, Session, ComponentVariation, OKLCHColor, SemanticCategory } from './types';
import {
    INITIAL_PLACEHOLDERS,
    EASING_OPTIONS,
    SEMANTIC_PRESETS,
    DEFAULT_BRAND_COLORS,
    ANIMATION_DEFAULTS,
    FLOW_PRESETS
} from './constants';
import { generateId } from './utils';

// PROJECT_elements Token Bridge
import {
    getTokenBridge,
    initTokenBridge,
    toOKLCHString,
    toHex,
    generateStates,
    getAccessibleTextColor
} from '../tokens-bridge';

import DottedGlowBackground from './components/DottedGlowBackground';
import ArtifactCard from './components/ArtifactCard';
import SideDrawer from './components/SideDrawer';
import OKLCHColorPicker from './components/OKLCHColorPicker';
import {
    ThinkingIcon,
    CodeIcon,
    SparklesIcon,
    ArrowLeftIcon,
    ArrowRightIcon,
    ArrowUpIcon,
    GridIcon,
    AttachmentIcon,
    CloseIcon,
    CopyIcon,
    CheckIcon,
    SettingsIcon,
    WindIcon,
    MirrorIcon
} from './components/Icons';

// =============================================================================
// DESIGN TOKEN SYSTEM PROMPT
// =============================================================================

const DESIGN_SYSTEM_PROMPT = `
You are Flash UI, an expert Design Technologist using the PROJECT_elements OKLCH Design Token System.

## OKLCH COLOR SPACE (MANDATORY)
All colors MUST use native CSS oklch() syntax:
- oklch(L% C H) where L=lightness (0-100%), C=chroma (0-0.4), H=hue (0-360)
- Example: oklch(70% 0.15 250) = vibrant blue

## SEMANTIC COLOR TOKENS
Use these exact values from our design system:

### Tier Colors (Architecture Layers)
- T0 Core: oklch(70.25% 0.1364 236.02) - Blue
- T1 Arch: oklch(77.72% 0.1521 87.78) - Yellow
- T2 Eco: oklch(54.72% 0.2500 310.47) - Purple
- T3 Discovered: oklch(55.93% 0.1426 38.53) - Orange

### Family Colors (Functional Categories)
- LOG (Logic): oklch(87.71% 0.1492 201.19) - Cyan
- DAT (Data): oklch(87.99% 0.2100 156.86) - Green
- ORG (Organization): oklch(82.72% 0.1711 80.53) - Gold
- EXE (Execution): oklch(63.54% 0.2541 15.46) - Red
- EXT (External): oklch(53.38% 0.2503 301.37) - Purple

### Ring Colors (Architectural Zones)
- DOMAIN: oklch(82.72% 0.1711 80.53) - Gold
- APPLICATION: oklch(87.71% 0.1492 201.19) - Cyan
- PRESENTATION: oklch(87.99% 0.2100 156.86) - Green
- INTERFACE: oklch(70.25% 0.1364 236.02) - Blue
- INFRASTRUCTURE: oklch(63.54% 0.2541 15.46) - Red

### UI Colors
- Background: oklch(0% 0 0) - Pure black
- Panel: oklch(16.56% 0.0132 248.65 / 0.85) - Dark glass
- Accent: oklch(87.71% 0.1492 201.19) - Cyan
- Highlight Selected: oklch(90% 0.20 60) - Bright yellow
- Highlight Hover: oklch(85% 0.15 200) - Bright cyan

## ANIMATION PARAMETERS
- Use sophisticated motion curves: cubic-bezier(0.16, 1, 0.3, 1)
- Implement micro-interactions with subtle transforms
- Apply orchestrated stagger delays for multi-element reveals

## OUTPUT REQUIREMENTS
- Return ONLY raw HTML with inline styles
- Use oklch() for ALL color definitions
- Include hover states using :hover pseudo-classes
- Implement responsive design with clamp() and min/max
`;

// =============================================================================
// COPYCAT PROTOCOL PROMPT
// =============================================================================

const COPYCAT_PROTOCOL_PROMPT = `
## COPYCAT PROTOCOL - PIXEL-PERFECT REPLICATION

You are performing a COPYCAT operation. Your mission:
1. ANALYZE the uploaded image with forensic precision
2. EXTRACT exact visual properties:
   - Layout grid and spacing (translate to CSS grid/flex)
   - Colors (convert ALL to OKLCH color space)
   - Typography (font sizes, weights, line heights)
   - Shadows and depth (box-shadow, layering)
   - Border radii and shapes
   - Micro-interactions implied by the design

3. REPLICATE with 99% accuracy using:
   - OKLCH for all colors (even extracted from image)
   - CSS Grid/Flexbox for layout
   - CSS custom properties for consistency
   - Smooth transitions and hover states

OUTPUT: Return ONLY raw HTML that visually matches the source image.
`;

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

async function callWithRetry<T>(
    fn: () => Promise<T>,
    maxRetries = 3,
    onRetry?: (count: number, wait: number) => void
): Promise<T> {
    let lastError: any;
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await fn();
        } catch (e: any) {
            lastError = e;
            const errorMsg = e?.message || String(e);
            const isQuotaError = errorMsg.includes('429') || errorMsg.includes('RESOURCE_EXHAUSTED');
            const isTransientError = errorMsg.includes('500') || errorMsg.includes('503') || errorMsg.includes('deadline');

            if (isQuotaError || isTransientError) {
                const wait = Math.pow(2, i) * 2000 + Math.random() * 1000;
                if (onRetry) onRetry(i + 1, wait);
                await new Promise(r => setTimeout(r, wait));
                continue;
            }
            throw e;
        }
    }
    throw lastError;
}

async function* parseJsonStream(responseStream: any) {
    let buffer = '';
    for await (const chunk of responseStream) {
        const text = chunk.text;
        if (typeof text !== 'string') continue;
        buffer += text;
        let start = buffer.indexOf('{');
        while (start !== -1) {
            let braceCount = 0;
            let end = -1;
            for (let i = start; i < buffer.length; i++) {
                if (buffer[i] === '{') braceCount++;
                else if (buffer[i] === '}') braceCount--;
                if (braceCount === 0 && i > start) {
                    end = i;
                    break;
                }
            }
            if (end !== -1) {
                const jsonString = buffer.substring(start, end + 1);
                try {
                    yield JSON.parse(jsonString);
                    buffer = buffer.substring(end + 1);
                    start = buffer.indexOf('{');
                } catch (e) {
                    start = buffer.indexOf('{', start + 1);
                }
            } else {
                break;
            }
        }
    }
}

// =============================================================================
// MAIN APP COMPONENT
// =============================================================================

function App() {
    // Session state
    const [sessions, setSessions] = useState<Session[]>([]);
    const [currentSessionIndex, setCurrentSessionIndex] = useState<number>(-1);
    const [focusedArtifactIndex, setFocusedArtifactIndex] = useState<number | null>(null);

    // Input state
    const [inputValue, setInputValue] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [loadingPhase, setLoadingPhase] = useState<string>('');
    const [placeholderIndex, setPlaceholderIndex] = useState(0);
    const [placeholders, setPlaceholders] = useState<string[]>(INITIAL_PLACEHOLDERS);

    // Image/Copycat state
    const [selectedImage, setSelectedImage] = useState<{ data: string; mimeType: string } | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [copycatAnalysis, setCopycatAnalysis] = useState<string | null>(null);

    // UI state
    const [copyFeedback, setCopyFeedback] = useState<string | null>(null);
    const [showSettings, setShowSettings] = useState(false);
    const [errorNotification, setErrorNotification] = useState<{ message: string, type: 'error' | 'warning' } | null>(null);

    // Design System Controls (PROJECT_elements integrated)
    const [animSpeed, setAnimSpeed] = useState(1.0);
    const [animEasing, setAnimEasing] = useState(EASING_OPTIONS[0].value);
    const [brandColor, setBrandColor] = useState<OKLCHColor>(DEFAULT_BRAND_COLORS.tier);
    const [presetCategory, setPresetCategory] = useState<SemanticCategory>('tier');

    // Drawer state
    const [drawerState, setDrawerState] = useState<{
        isOpen: boolean;
        mode: 'code' | 'variations' | 'analysis' | null;
        title: string;
        data: any;
    }>({ isOpen: false, mode: null, title: '', data: null });

    const [componentVariations, setComponentVariations] = useState<ComponentVariation[]>([]);

    // Refs
    const inputRef = useRef<HTMLInputElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const gridScrollRef = useRef<HTMLDivElement>(null);

    // Initialize token bridge
    useEffect(() => {
        initTokenBridge('/schema/viz/tokens/appearance.tokens.json').catch(() => {
            console.warn('[Flash UI] Could not load design tokens, using defaults');
        });
    }, []);

    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    useEffect(() => {
        if (focusedArtifactIndex !== null && window.innerWidth <= 1024) {
            if (gridScrollRef.current) {
                gridScrollRef.current.scrollTop = 0;
            }
            window.scrollTo(0, 0);
        }
    }, [focusedArtifactIndex]);

    useEffect(() => {
        const interval = setInterval(() => {
            setPlaceholderIndex(prev => (prev + 1) % placeholders.length);
        }, 3000);
        return () => clearInterval(interval);
    }, [placeholders.length]);

    // Dynamic placeholders from Gemini
    useEffect(() => {
        const fetchDynamicPlaceholders = async () => {
            try {
                const apiKey = process.env.API_KEY;
                if (!apiKey) return;
                const ai = new GoogleGenAI({ apiKey });
                const response = await ai.models.generateContent({
                    model: 'gemini-2.0-flash',
                    contents: `Generate 15 UI component prompts for a code visualization tool. Examples:
                    - "3D force-directed graph with OKLCH tier coloring"
                    - "Glassmorphic metrics dashboard"
                    - "Atom classification card grid"
                    Return ONLY a raw JSON array of strings.`
                });
                const text = response.text || '[]';
                const jsonMatch = text.match(/\[[\s\S]*\]/);
                if (jsonMatch) {
                    const newPlaceholders = JSON.parse(jsonMatch[0]);
                    if (Array.isArray(newPlaceholders) && newPlaceholders.length > 0) {
                        const shuffled = newPlaceholders.sort(() => 0.5 - Math.random()).slice(0, 10);
                        setPlaceholders(prev => [...prev, ...shuffled]);
                    }
                }
            } catch (e) {
                console.warn("Could not fetch dynamic placeholders", e);
            }
        };
        setTimeout(fetchDynamicPlaceholders, 1500);
    }, []);

    // ==========================================================================
    // FILE HANDLING
    // ==========================================================================

    const processFile = (file: File) => {
        if (!file.type.startsWith('image/')) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            const base64 = e.target?.result as string;
            const data = base64.split(',')[1];
            setSelectedImage({ data, mimeType: file.type });
            setCopycatAnalysis(null); // Reset analysis for new image
        };
        reader.readAsDataURL(file);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) processFile(file);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file) processFile(file);
    };

    // ==========================================================================
    // CLIPBOARD & CODE ACTIONS
    // ==========================================================================

    const handleCopyCode = useCallback((code: string, id: string) => {
        if (!code) return;
        navigator.clipboard.writeText(code).then(() => {
            setCopyFeedback(id);
            setTimeout(() => setCopyFeedback(null), 2000);
        });
    }, []);

    const handleShowCode = () => {
        const currentSession = sessions[currentSessionIndex];
        if (currentSession && focusedArtifactIndex !== null) {
            const artifact = currentSession.artifacts[focusedArtifactIndex];
            setDrawerState({ isOpen: true, mode: 'code', title: 'Source Code', data: artifact.html });
        }
    };

    // ==========================================================================
    // COPYCAT ANALYSIS (Image → Design Spec)
    // ==========================================================================

    const analyzeImageForCopycat = useCallback(async (imageData: { data: string; mimeType: string }) => {
        const apiKey = process.env.API_KEY;
        if (!apiKey) throw new Error("API_KEY is not configured.");
        const ai = new GoogleGenAI({ apiKey });

        setLoadingPhase('Extracting Visual DNA...');

        const analysisPrompt = `
${COPYCAT_PROTOCOL_PROMPT}

Perform a FORENSIC VISUAL AUDIT of this image:

1. **LAYOUT ANALYSIS**
   - Grid structure (columns, rows, gaps)
   - Spacing rhythm (margins, padding)
   - Alignment patterns

2. **COLOR EXTRACTION** (Convert ALL to OKLCH)
   - Primary colors → oklch(L% C H)
   - Secondary colors → oklch(L% C H)
   - Background colors → oklch(L% C H)
   - Accent colors → oklch(L% C H)
   - Text colors → oklch(L% C H)

3. **TYPOGRAPHY**
   - Font sizes (use clamp() for responsive)
   - Font weights
   - Line heights
   - Letter spacing

4. **DEPTH & EFFECTS**
   - Shadow values (box-shadow)
   - Border radii
   - Blur effects
   - Gradients (use oklch())

5. **COMPONENTS IDENTIFIED**
   - List each UI component
   - Describe its structure

OUTPUT: Return a detailed "Design Specification Brief" that can be used to recreate this UI.
`;

        const response = await ai.models.generateContent({
            model: 'gemini-2.0-flash',
            contents: {
                parts: [
                    { inlineData: { data: imageData.data, mimeType: imageData.mimeType } },
                    { text: analysisPrompt }
                ]
            }
        });

        return response.text || "";
    }, []);

    // ==========================================================================
    // VARIATION GENERATION
    // ==========================================================================

    const handleGenerateVariations = useCallback(async () => {
        const currentSession = sessions[currentSessionIndex];
        if (!currentSession || focusedArtifactIndex === null) return;
        const currentArtifact = currentSession.artifacts[focusedArtifactIndex];

        setIsLoading(true);
        setErrorNotification(null);
        setComponentVariations([]);
        setDrawerState({ isOpen: true, mode: 'variations', title: 'Design Variations', data: currentArtifact.id });

        try {
            const apiKey = process.env.API_KEY;
            if (!apiKey) throw new Error("API_KEY is not configured.");
            const ai = new GoogleGenAI({ apiKey });

            const brandColorCSS = toOKLCHString(brandColor);

            const prompt = `
${DESIGN_SYSTEM_PROMPT}

Generate 3 ARCHITECTURAL VARIATIONS of: "${currentSession.prompt}"

**VARIATION PROTOCOL:**
1. **Identity Mirror** - Closest to original, refined
2. **Eclipse Variant** - Darker, more dramatic
3. **Luminous Shift** - Lighter, ethereal

**DESIGN CONSTRAINTS:**
- Brand Color: ${brandColorCSS}
- Animation Speed: ${animSpeed}x
- Easing: ${animEasing}

**OUTPUT FORMAT:**
Return each variation as: { "name": "Variant Name", "html": "..." }
`;

            const runGeneration = async () => {
                const responseStream = await ai.models.generateContentStream({
                    model: 'gemini-2.0-flash',
                    contents: { parts: [{ text: prompt }] },
                    config: { temperature: 1.1 }
                });
                for await (const variation of parseJsonStream(responseStream)) {
                    if (variation.name && variation.html) {
                        setComponentVariations(prev => [...prev, variation]);
                    }
                }
            };

            await callWithRetry(runGeneration, 3, (count, wait) => {
                console.warn(`Quota reached. Retrying variations (${count}/3)...`);
            });

        } catch (e: any) {
            console.error("Error generating variations:", e);
            setErrorNotification({
                message: String(e).includes('429') ? 'Service limit reached. Please wait.' : 'Failed to generate variations.',
                type: 'error'
            });
        } finally {
            setIsLoading(false);
        }
    }, [sessions, currentSessionIndex, focusedArtifactIndex, animSpeed, animEasing, brandColor]);

    const applyVariation = (html: string) => {
        if (focusedArtifactIndex === null) return;
        setSessions(prev => prev.map((sess, i) =>
            i === currentSessionIndex ? {
                ...sess,
                artifacts: sess.artifacts.map((art, j) =>
                    j === focusedArtifactIndex ? { ...art, html, status: 'complete' as const } : art
                )
            } : sess
        ));
        setDrawerState(s => ({ ...s, isOpen: false }));
    };

    // ==========================================================================
    // MAIN GENERATION ENGINE
    // ==========================================================================

    const handleSendMessage = useCallback(async (manualPrompt?: string, mode: 'default' | 'copycat' = 'default') => {
        const promptToUse = manualPrompt || inputValue;
        const trimmedInput = promptToUse.trim();

        if (!trimmedInput && !selectedImage) return;
        if (isLoading) return;

        setErrorNotification(null);
        if (!manualPrompt) setInputValue('');
        const imageToUse = selectedImage;
        setSelectedImage(null);

        setIsLoading(true);
        setLoadingPhase(mode === 'copycat' ? 'Initiating Copycat Protocol...' : 'Analyzing Design Intent...');
        const baseTime = Date.now();
        const sessionId = generateId();

        // Create placeholder artifacts
        const placeholderArtifacts: Artifact[] = [0, 1, 2].map((i) => ({
            id: `${sessionId}_${i}`,
            styleName: mode === 'copycat' ? ['Identity Mirror', 'Eclipse Variant', 'Luminous Shift'][i] : 'Synthesizing...',
            html: '',
            status: 'streaming' as const,
        }));

        const newSession: Session = {
            id: sessionId,
            prompt: mode === 'copycat' ? "Copycat Mode" : (trimmedInput || "Design Synthesis"),
            timestamp: baseTime,
            artifacts: placeholderArtifacts
        };

        setSessions(prev => {
            const next = [...prev, newSession];
            setCurrentSessionIndex(next.length - 1);
            return next;
        });
        setFocusedArtifactIndex(null);

        try {
            const apiKey = process.env.API_KEY;
            if (!apiKey) throw new Error("API_KEY is not configured.");
            const ai = new GoogleGenAI({ apiKey });

            let designSpecification = "";

            // =================================================================
            // PHASE 1: Visual Analysis (Copycat or Reference)
            // =================================================================
            if (imageToUse) {
                if (mode === 'copycat') {
                    setLoadingPhase('Extracting Visual DNA...');
                    designSpecification = await callWithRetry(
                        () => analyzeImageForCopycat(imageToUse),
                        3,
                        (c, w) => setLoadingPhase(`Retrying analysis (${c}/3)...`)
                    );
                    setCopycatAnalysis(designSpecification);
                } else {
                    setLoadingPhase('Analyzing Reference Image...');
                    const analysisPrompt = `
You are a Design Analyst. Examine this reference image and extract:
1. Color palette (convert to OKLCH)
2. Layout patterns
3. Typography styles
4. Visual mood and aesthetic
5. Component structure

Output a concise "Design Brief" to guide UI generation.
`;
                    const response = await ai.models.generateContent({
                        model: 'gemini-2.0-flash',
                        contents: {
                            parts: [
                                { inlineData: { data: imageToUse.data, mimeType: imageToUse.mimeType } },
                                { text: analysisPrompt }
                            ]
                        }
                    });
                    designSpecification = response.text || "";
                }
            }

            // =================================================================
            // PHASE 2: Style Synthesis
            // =================================================================
            setLoadingPhase(mode === 'copycat' ? 'Generating Replicas...' : 'Synthesizing Styles...');

            const styleParts: any[] = [];
            if (imageToUse) {
                styleParts.push({ inlineData: { data: imageToUse.data, mimeType: imageToUse.mimeType } });
            }

            const stylePrompt = mode === 'copycat'
                ? `Based on the Copycat analysis, generate 3 style directions:
                   1. "Identity Mirror" - 99% accurate replica
                   2. "Eclipse Variant" - Same layout, darker palette
                   3. "Luminous Shift" - Same layout, lighter palette
                   Return ONLY a raw JSON array of 3 direction names.`
                : `Create 3 professional UI directions for: "${trimmedInput}"
                   Context: ${designSpecification}
                   Return ONLY a raw JSON array of 3 sophisticated direction titles.`;

            styleParts.push({ text: stylePrompt });

            let generatedStyles: string[] = [];
            const getStyles = async () => {
                const styleResponse = await ai.models.generateContent({
                    model: 'gemini-2.0-flash',
                    contents: { parts: styleParts }
                });
                const styleText = styleResponse.text || '[]';
                const jsonMatch = styleText.match(/\[[\s\S]*\]/);
                if (jsonMatch) return JSON.parse(jsonMatch[0]);
                return null;
            };

            generatedStyles = await callWithRetry(getStyles, 3, (c, w) => {
                setLoadingPhase(`Retrying styles (${c}/3)...`);
            }) || [];

            if (!generatedStyles || generatedStyles.length < 3) {
                generatedStyles = mode === 'copycat'
                    ? ["Identity Mirror", "Eclipse Variant", "Luminous Shift"]
                    : ["Systematic Core", "Fluid Dynamics", "Atmospheric Depth"];
            }

            generatedStyles = generatedStyles.slice(0, 3);

            // Update artifact names
            setSessions(prev => prev.map(s => {
                if (s.id !== sessionId) return s;
                return {
                    ...s,
                    artifacts: s.artifacts.map((art, i) => ({
                        ...art,
                        styleName: generatedStyles[i]
                    }))
                };
            }));

            // =================================================================
            // PHASE 3: Artifact Generation (Parallel)
            // =================================================================
            setLoadingPhase(mode === 'copycat' ? 'Building Replicas...' : 'Generating Artifacts...');

            const generateArtifact = async (artifact: Artifact, styleInstruction: string) => {
                try {
                    const innerParts: any[] = [];
                    if (imageToUse) {
                        innerParts.push({ inlineData: { data: imageToUse.data, mimeType: imageToUse.mimeType } });
                    }

                    const brandColorCSS = toOKLCHString(brandColor);

                    const artifactPrompt = mode === 'copycat'
                        ? `
${COPYCAT_PROTOCOL_PROMPT}

**DESIGN SPECIFICATION:**
${designSpecification}

**VARIATION:** ${styleInstruction}
${styleInstruction === 'Identity Mirror' ? 'Replicate the source with 99% accuracy.' :
                            styleInstruction === 'Eclipse Variant' ? 'Same structure, shift all colors darker (reduce lightness by 20%).' :
                                'Same structure, shift all colors lighter (increase lightness by 20%).'}

**OUTPUT:** Return ONLY raw HTML with all colors in oklch() format.
`
                        : `
${DESIGN_SYSTEM_PROMPT}

**BUILD REQUEST:** "${trimmedInput}"

**DESIGN CONTEXT:**
${designSpecification}

**VARIATION STYLE:** ${styleInstruction}

**BRAND COLOR:** ${brandColorCSS}
**ANIMATION SPEED:** ${animSpeed}x
**EASING:** ${animEasing}

**OUTPUT:** Return ONLY raw HTML. Use oklch() for all colors.
`;

                    innerParts.push({ text: artifactPrompt });

                    const runArtifactGen = async () => {
                        const aiInternal = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });
                        const responseStream = await aiInternal.models.generateContentStream({
                            model: 'gemini-2.0-flash',
                            contents: { parts: innerParts },
                        });

                        let accumulatedHtml = '';
                        for await (const chunk of responseStream) {
                            const text = chunk.text;
                            if (typeof text === 'string') {
                                accumulatedHtml += text;
                                setSessions(prev => prev.map(sess =>
                                    sess.id === sessionId ? {
                                        ...sess,
                                        artifacts: sess.artifacts.map(art =>
                                            art.id === artifact.id ? { ...art, html: accumulatedHtml } : art
                                        )
                                    } : sess
                                ));
                            }
                        }
                        return accumulatedHtml;
                    };

                    let finalHtml = await callWithRetry(runArtifactGen, 3, (c, w) => {
                        console.warn(`Quota hit for artifact ${artifact.id}. Retry ${c}/3...`);
                    });

                    // Clean markdown fences
                    finalHtml = finalHtml.trim();
                    if (finalHtml.startsWith('```html')) finalHtml = finalHtml.substring(7).trimStart();
                    if (finalHtml.startsWith('```')) finalHtml = finalHtml.substring(3).trimStart();
                    if (finalHtml.endsWith('```')) finalHtml = finalHtml.substring(0, finalHtml.length - 3).trimEnd();

                    setSessions(prev => prev.map(sess =>
                        sess.id === sessionId ? {
                            ...sess,
                            artifacts: sess.artifacts.map(art =>
                                art.id === artifact.id ? { ...art, html: finalHtml, status: finalHtml ? 'complete' : 'error' as const } : art
                            )
                        } : sess
                    ));

                } catch (e: any) {
                    console.error('Error in artifact generation:', e);
                    setSessions(prev => prev.map(sess =>
                        sess.id === sessionId ? {
                            ...sess,
                            artifacts: sess.artifacts.map(art =>
                                art.id === artifact.id ? { ...art, status: 'error' as const } : art
                            )
                        } : sess
                    ));
                }
            };

            // Generate all artifacts in parallel
            await Promise.all(placeholderArtifacts.map((art, i) => generateArtifact(art, generatedStyles[i])));

        } catch (e: any) {
            console.error("Fatal error in generation pipeline", e);
            setErrorNotification({
                message: String(e).includes('429') ? 'Service limit exceeded. Please wait.' : 'Generation failed. Please try again.',
                type: 'error'
            });
            setIsLoading(false);
        } finally {
            setIsLoading(false);
            setLoadingPhase('');
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [inputValue, isLoading, selectedImage, animSpeed, animEasing, brandColor, analyzeImageForCopycat]);

    // ==========================================================================
    // UI HANDLERS
    // ==========================================================================

    const handleSurpriseMe = () => {
        const currentPrompt = placeholders[placeholderIndex];
        setInputValue(currentPrompt);
        handleSendMessage(currentPrompt);
    };

    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter' && !isLoading) {
            event.preventDefault();
            handleSendMessage();
        } else if (event.key === 'Tab' && !inputValue && !isLoading) {
            event.preventDefault();
            setInputValue(placeholders[placeholderIndex]);
        }
    };

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(event.target.value);
    };

    const nextItem = useCallback(() => {
        if (focusedArtifactIndex !== null) {
            if (focusedArtifactIndex < 2) setFocusedArtifactIndex(focusedArtifactIndex + 1);
        } else {
            if (currentSessionIndex < sessions.length - 1) setCurrentSessionIndex(currentSessionIndex + 1);
        }
    }, [currentSessionIndex, sessions.length, focusedArtifactIndex]);

    const prevItem = useCallback(() => {
        if (focusedArtifactIndex !== null) {
            if (focusedArtifactIndex > 0) setFocusedArtifactIndex(focusedArtifactIndex - 1);
        } else {
            if (currentSessionIndex > 0) setCurrentSessionIndex(currentSessionIndex - 1);
        }
    }, [currentSessionIndex, focusedArtifactIndex]);

    // ==========================================================================
    // COMPUTED STATE
    // ==========================================================================

    const isLoadingDrawer = isLoading && drawerState.mode === 'variations' && componentVariations.length === 0;
    const hasStarted = sessions.length > 0 || isLoading;
    const currentSession = sessions[currentSessionIndex];
    const focusedArtifact = currentSession?.artifacts[focusedArtifactIndex ?? -1];

    let canGoBack = false;
    let canGoForward = false;

    if (hasStarted) {
        if (focusedArtifactIndex !== null) {
            canGoBack = focusedArtifactIndex > 0;
            canGoForward = focusedArtifactIndex < (currentSession?.artifacts.length || 0) - 1;
        } else {
            canGoBack = currentSessionIndex > 0;
            canGoForward = currentSessionIndex < sessions.length - 1;
        }
    }

    // ==========================================================================
    // RENDER
    // ==========================================================================

    return (
        <>
            <a href="https://x.com/ammaar" target="_blank" rel="noreferrer" className={`creator-credit ${hasStarted ? 'hide-on-mobile' : ''}`}>
                created by @ammaar | enhanced by PROJECT_elements
            </a>

            {errorNotification && (
                <div className={`notification-banner ${errorNotification.type}`}>
                    <div className="notification-content">
                        <CloseIcon />
                        <span>{errorNotification.message}</span>
                    </div>
                    <button className="notification-close" onClick={() => setErrorNotification(null)}>&times;</button>
                </div>
            )}

            <SideDrawer
                isOpen={drawerState.isOpen}
                onClose={() => setDrawerState(s => ({ ...s, isOpen: false }))}
                title={drawerState.title}
                headerActions={drawerState.mode === 'code' && (
                    <button
                        className="header-action-btn"
                        onClick={() => handleCopyCode(drawerState.data, 'drawer_copy')}
                    >
                        {copyFeedback === 'drawer_copy' ? <CheckIcon /> : <CopyIcon />}
                        {copyFeedback === 'drawer_copy' ? 'Copied' : 'Copy'}
                    </button>
                )}
            >
                {isLoadingDrawer && (
                    <div className="loading-state">
                        <ThinkingIcon />
                        Designing variations...
                    </div>
                )}

                {drawerState.mode === 'code' && (
                    <pre className="code-block"><code>{drawerState.data}</code></pre>
                )}

                {drawerState.mode === 'analysis' && (
                    <div className="analysis-content">
                        <pre>{drawerState.data}</pre>
                    </div>
                )}

                {drawerState.mode === 'variations' && (
                    <div className="sexy-grid">
                        {componentVariations.map((v, i) => (
                            <div key={i} className="sexy-card" onClick={() => applyVariation(v.html)}>
                                <div className="sexy-preview">
                                    <iframe srcDoc={v.html} title={v.name} sandbox="allow-scripts allow-same-origin" />
                                </div>
                                <div className="sexy-label">{v.name}</div>
                            </div>
                        ))}
                    </div>
                )}
            </SideDrawer>

            <div
                className={`immersive-app ${isDragging ? 'is-dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <DottedGlowBackground
                    gap={24}
                    radius={1.5}
                    color="rgba(255, 255, 255, 0.02)"
                    glowColor="rgba(255, 255, 255, 0.15)"
                    speedScale={0.5}
                />

                {isDragging && (
                    <div className="drag-overlay">
                        <div className="drag-content">
                            <SparklesIcon />
                            <h2>Drop to analyze or replicate</h2>
                            <p>Use as reference or activate Copycat mode</p>
                        </div>
                    </div>
                )}

                <div className={`stage-container ${focusedArtifactIndex !== null ? 'mode-focus' : 'mode-split'}`}>
                    <div className={`empty-state ${hasStarted ? 'fade-out' : ''}`}>
                        <div className="empty-content">
                            <h1>Flash UI</h1>
                            <p>PROJECT_elements Design Token Engine</p>
                            <button className="surprise-button" onClick={handleSurpriseMe} disabled={isLoading}>
                                <SparklesIcon /> Surprise Me
                            </button>
                        </div>
                    </div>

                    {sessions.map((session, sIndex) => {
                        let positionClass = 'hidden';
                        if (sIndex === currentSessionIndex) positionClass = 'active-session';
                        else if (sIndex < currentSessionIndex) positionClass = 'past-session';
                        else if (sIndex > currentSessionIndex) positionClass = 'future-session';

                        return (
                            <div key={session.id} className={`session-group ${positionClass}`}>
                                <div className="artifact-grid" ref={sIndex === currentSessionIndex ? gridScrollRef : null}>
                                    {session.artifacts.map((artifact, aIndex) => {
                                        const isFocused = focusedArtifactIndex === aIndex;

                                        return (
                                            <ArtifactCard
                                                key={artifact.id}
                                                artifact={artifact}
                                                isFocused={isFocused}
                                                onClick={() => setFocusedArtifactIndex(aIndex)}
                                            />
                                        );
                                    })}
                                </div>
                            </div>
                        );
                    })}
                </div>

                {canGoBack && (
                    <button className="nav-handle left" onClick={prevItem} aria-label="Previous">
                        <ArrowLeftIcon />
                    </button>
                )}
                {canGoForward && (
                    <button className="nav-handle right" onClick={nextItem} aria-label="Next">
                        <ArrowRightIcon />
                    </button>
                )}

                <div className={`action-bar ${focusedArtifactIndex !== null ? 'visible' : ''}`}>
                    <div className="active-prompt-label">
                        {currentSession?.prompt}
                    </div>
                    <div className="action-buttons">
                        <button onClick={() => setFocusedArtifactIndex(null)}>
                            <GridIcon /> Grid View
                        </button>
                        <button onClick={handleGenerateVariations} disabled={isLoading}>
                            <SparklesIcon /> Variations
                        </button>
                        <button onClick={handleShowCode}>
                            <CodeIcon /> Source
                        </button>
                        {copycatAnalysis && (
                            <button onClick={() => setDrawerState({ isOpen: true, mode: 'analysis', title: 'Copycat Analysis', data: copycatAnalysis })}>
                                <MirrorIcon /> Analysis
                            </button>
                        )}
                        <button onClick={() => focusedArtifact && handleCopyCode(focusedArtifact.html, 'bar_copy')}>
                            {copyFeedback === 'bar_copy' ? <CheckIcon /> : <CopyIcon />}
                            {copyFeedback === 'bar_copy' ? 'Copied' : 'Copy HTML'}
                        </button>
                    </div>
                </div>

                <div className="floating-input-container">
                    {showSettings && (
                        <div className="settings-panel">
                            <div className="settings-main-area">
                                <div className="settings-sidebar">
                                    <div className="settings-group">
                                        <label><WindIcon /> Motion Speed</label>
                                        <div className="slider-container">
                                            <input
                                                type="range"
                                                min="0.2"
                                                max="3.0"
                                                step="0.1"
                                                value={animSpeed}
                                                onChange={(e) => setAnimSpeed(parseFloat(e.target.value))}
                                            />
                                            <span className="value-badge">{animSpeed.toFixed(1)}x</span>
                                        </div>
                                    </div>
                                    <div className="settings-group">
                                        <label>Easing Curve</label>
                                        <select value={animEasing} onChange={(e) => setAnimEasing(e.target.value)}>
                                            {EASING_OPTIONS.map(opt => (
                                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                                <div className="settings-divider" />
                                <div className="settings-brand-area">
                                    <label>OKLCH Brand Color</label>
                                    <OKLCHColorPicker
                                        color={brandColor}
                                        onChange={setBrandColor}
                                        showPresets={true}
                                        presetCategory={presetCategory}
                                    />
                                </div>
                            </div>
                            <button className="settings-close-x" onClick={() => setShowSettings(false)}>
                                <CloseIcon />
                            </button>
                        </div>
                    )}

                    {selectedImage && (
                        <div className="image-preview-thumbnail">
                            <img src={`data:${selectedImage.mimeType};base64,${selectedImage.data}`} alt="preview" />
                            <div className="image-actions">
                                <button className="copycat-overlay-btn" onClick={() => handleSendMessage(undefined, 'copycat')}>
                                    <MirrorIcon /> Copycat
                                </button>
                                <button className="reference-overlay-btn" onClick={() => handleSendMessage()}>
                                    <SparklesIcon /> Reference
                                </button>
                            </div>
                            <button className="remove-image-btn" onClick={() => setSelectedImage(null)}>
                                <CloseIcon />
                            </button>
                        </div>
                    )}

                    <div className={`input-wrapper ${isLoading ? 'loading' : ''}`}>
                        <input
                            type="file"
                            ref={fileInputRef}
                            style={{ display: 'none' }}
                            accept="image/*"
                            onChange={handleFileChange}
                        />

                        {!isLoading && (
                            <div className="input-prefix-actions">
                                <button className="attachment-button" onClick={() => fileInputRef.current?.click()}>
                                    <AttachmentIcon />
                                </button>
                                <button className={`settings-toggle ${showSettings ? 'active' : ''}`} onClick={() => setShowSettings(!showSettings)}>
                                    <SettingsIcon />
                                </button>
                            </div>
                        )}

                        {(!inputValue && !isLoading) && (
                            <div className="animated-placeholder" key={placeholderIndex}>
                                <span className="placeholder-text">{placeholders[placeholderIndex]}</span>
                                <span className="tab-hint">Tab</span>
                            </div>
                        )}

                        {!isLoading ? (
                            <input
                                ref={inputRef}
                                type="text"
                                value={inputValue}
                                onChange={handleInputChange}
                                onKeyDown={handleKeyDown}
                                disabled={isLoading}
                            />
                        ) : (
                            <div className="input-generating-label">
                                <span className="generating-prompt-text">{loadingPhase || currentSession?.prompt}</span>
                                <ThinkingIcon />
                            </div>
                        )}

                        <button
                            className="send-button"
                            onClick={() => handleSendMessage()}
                            disabled={isLoading || (!inputValue.trim() && !selectedImage)}
                        >
                            <ArrowUpIcon />
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
}

// =============================================================================
// BOOTSTRAP
// =============================================================================

const rootElement = document.getElementById('root');
if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    root.render(<React.StrictMode><App /></React.StrictMode>);
}
