/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 *
 * Flash UI Types - PROJECT_elements Integration
 */

// Re-export OKLCH types from token bridge for compatibility
export type { OKLCHColor, OKLCHColorWithMeta, SemanticCategory } from '../tokens-bridge';

// Import for internal use
import type { OKLCHColor as _OKLCHColor, SemanticCategory as _SemanticCategory } from '../tokens-bridge';

export interface Artifact {
    id: string;
    styleName: string;
    html: string;
    status: 'streaming' | 'complete' | 'error';
}

export interface Session {
    id: string;
    prompt: string;
    timestamp: number;
    artifacts: Artifact[];
}

export interface ComponentVariation {
    name: string;
    html: string;
}

export interface LayoutOption {
    name: string;
    css: string;
    previewHtml: string;
}

// Design system configuration (PROJECT_elements aware)
export interface DesignSystemConfig {
    brandColor: _OKLCHColor;
    animSpeed: number;
    animEasing: string;
    presetCategory: _SemanticCategory;
}
