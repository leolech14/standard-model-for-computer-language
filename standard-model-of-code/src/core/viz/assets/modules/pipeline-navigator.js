/**
 * Pipeline Navigator Module
 *
 * Interactive visualization of the 27-stage Collider pipeline.
 * Shows data flow, timing, and stage-by-stage transformations.
 *
 * Keyboard: P to toggle
 */

// ============================================================================
// CONSTANTS
// ============================================================================

const PIPELINE_PHASES = [
    { name: 'EXTRACTION', stages: ['survey', 'base_analysis', 'standard_model'], color: '#4CAF50' },
    { name: 'ENRICHMENT', stages: ['ecosystem_discovery', 'dimension_classification', 'scope_analysis', 'control_flow', 'pattern_detection', 'data_flow_analysis'], color: '#2196F3' },
    { name: 'ANALYSIS', stages: ['purpose_field', 'organelle_purpose', 'system_purpose', 'edge_extraction', 'markov_matrix', 'knot_detection', 'graph_analytics', 'statistical_metrics', 'codome_boundary'], color: '#9C27B0' },
    { name: 'INTELLIGENCE', stages: ['data_flow_macro', 'performance_prediction', 'constraint_validation', 'purpose_intelligence'], color: '#FF9800' },
    { name: 'OUTPUT', stages: ['roadmap_evaluation', 'topology_reasoning', 'semantic_cortex', 'ai_insights', 'output_generation'], color: '#F44336' },
];

const STAGE_LABELS = {
    'survey': 'Survey',
    'base_analysis': 'Base',
    'standard_model': 'Model',
    'ecosystem_discovery': 'Eco',
    'dimension_classification': 'Dims',
    'scope_analysis': 'Scope',
    'control_flow': 'CF',
    'pattern_detection': 'Pattern',
    'data_flow_analysis': 'DFlow',
    'purpose_field': 'Purpose',
    'organelle_purpose': 'π₃',
    'system_purpose': 'π₄',
    'edge_extraction': 'Edges',
    'markov_matrix': 'Markov',
    'knot_detection': 'Knots',
    'graph_analytics': 'Graph',
    'statistical_metrics': 'Stats',
    'codome_boundary': 'Codome',
    'data_flow_macro': 'Macro',
    'performance_prediction': 'Perf',
    'constraint_validation': 'Constr',
    'purpose_intelligence': 'Q',
    'roadmap_evaluation': 'Road',
    'topology_reasoning': 'Topo',
    'semantic_cortex': 'Cortex',
    'ai_insights': 'AI',
    'output_generation': 'Out',
};

// ============================================================================
// STATE
// ============================================================================

let pipelineState = {
    isOpen: false,
    selectedStage: null,
    snapshot: null,  // Pipeline snapshot data from JSON
};

// ============================================================================
// UI CREATION
// ============================================================================

function createPipelineNavigator() {
    // Check if already exists
    if (document.getElementById('pipeline-navigator')) return;

    const navigator = document.createElement('div');
    navigator.id = 'pipeline-navigator';
    navigator.className = 'pipeline-navigator hidden';
    navigator.innerHTML = `
        <div class="pipeline-header">
            <h2>Pipeline Navigator</h2>
            <div class="pipeline-summary">
                <span class="stat" id="pn-total-stages">27 stages</span>
                <span class="stat" id="pn-duration">--ms</span>
                <span class="stat success" id="pn-success">-- OK</span>
                <span class="stat error" id="pn-failed">-- ERR</span>
            </div>
            <button class="close-btn" onclick="togglePipelineNavigator()">×</button>
        </div>
        <div class="pipeline-flow" id="pipeline-flow">
            <!-- Stage nodes will be inserted here -->
        </div>
        <div class="pipeline-detail" id="pipeline-detail">
            <div class="detail-placeholder">
                Click a stage to see details
            </div>
        </div>
    `;

    document.body.appendChild(navigator);
    injectPipelineStyles();
    renderPipelineFlow();
}

function injectPipelineStyles() {
    if (document.getElementById('pipeline-navigator-styles')) return;

    const styles = document.createElement('style');
    styles.id = 'pipeline-navigator-styles';
    styles.textContent = `
        .pipeline-navigator {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(10, 15, 30, 0.98);
            z-index: 10000;
            display: flex;
            flex-direction: column;
            font-family: 'SF Mono', 'Consolas', monospace;
            color: #e0e0e0;
            backdrop-filter: blur(10px);
        }
        .pipeline-navigator.hidden {
            display: none;
        }
        .pipeline-header {
            display: flex;
            align-items: center;
            padding: 16px 24px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            background: rgba(0,0,0,0.3);
        }
        .pipeline-header h2 {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
            color: #fff;
        }
        .pipeline-summary {
            display: flex;
            gap: 16px;
            margin-left: 32px;
        }
        .pipeline-summary .stat {
            font-size: 13px;
            padding: 4px 12px;
            border-radius: 4px;
            background: rgba(255,255,255,0.1);
        }
        .pipeline-summary .stat.success { color: #4CAF50; }
        .pipeline-summary .stat.error { color: #F44336; }
        .close-btn {
            margin-left: auto;
            background: none;
            border: none;
            color: #888;
            font-size: 24px;
            cursor: pointer;
            padding: 4px 12px;
        }
        .close-btn:hover { color: #fff; }

        .pipeline-flow {
            flex: 0 0 auto;
            padding: 24px;
            overflow-x: auto;
            background: rgba(0,0,0,0.2);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .phase-row {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }
        .phase-label {
            width: 100px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.7;
        }
        .phase-stages {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        .stage-node {
            width: 56px;
            height: 56px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            border: 2px solid transparent;
            position: relative;
        }
        .stage-node:hover {
            transform: scale(1.1);
            z-index: 1;
        }
        .stage-node.selected {
            border-color: #fff;
            box-shadow: 0 0 20px rgba(255,255,255,0.3);
        }
        .stage-node.ok { background: rgba(76, 175, 80, 0.3); border-color: rgba(76, 175, 80, 0.5); }
        .stage-node.error { background: rgba(244, 67, 54, 0.3); border-color: rgba(244, 67, 54, 0.5); }
        .stage-node.skip { background: rgba(158, 158, 158, 0.2); border-color: rgba(158, 158, 158, 0.3); opacity: 0.5; }
        .stage-label {
            font-size: 10px;
            font-weight: 600;
            text-align: center;
        }
        .stage-time {
            font-size: 9px;
            opacity: 0.7;
            margin-top: 2px;
        }
        .stage-connector {
            width: 16px;
            height: 2px;
            background: rgba(255,255,255,0.2);
        }
        .phase-connector {
            width: 24px;
            height: 2px;
            background: linear-gradient(90deg, var(--from-color) 0%, var(--to-color) 100%);
            margin: 0 8px;
        }

        .pipeline-detail {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
        }
        .detail-placeholder {
            color: #666;
            font-size: 14px;
            text-align: center;
            padding: 48px;
        }
        .detail-content {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 24px;
        }
        .detail-section {
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 16px;
        }
        .detail-section h3 {
            margin: 0 0 12px 0;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.7;
        }
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 13px;
        }
        .detail-row:last-child { border-bottom: none; }
        .detail-label { opacity: 0.7; }
        .detail-value { font-weight: 500; }
        .detail-value.positive { color: #4CAF50; }
        .detail-value.negative { color: #F44336; }

        .field-list {
            max-height: 200px;
            overflow-y: auto;
        }
        .field-item {
            display: flex;
            justify-content: space-between;
            padding: 4px 8px;
            margin: 2px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
            font-size: 12px;
        }
        .field-name { color: #64B5F6; }
        .field-count { color: #81C784; }

        .sample-node {
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        .sample-node pre {
            margin: 0;
            font-size: 11px;
            white-space: pre-wrap;
            word-break: break-all;
        }
    `;
    document.head.appendChild(styles);
}

function renderPipelineFlow() {
    const container = document.getElementById('pipeline-flow');
    if (!container) return;

    container.innerHTML = '';

    PIPELINE_PHASES.forEach((phase, phaseIdx) => {
        const row = document.createElement('div');
        row.className = 'phase-row';

        // Phase label
        const label = document.createElement('div');
        label.className = 'phase-label';
        label.style.color = phase.color;
        label.textContent = phase.name;
        row.appendChild(label);

        // Stages container
        const stagesContainer = document.createElement('div');
        stagesContainer.className = 'phase-stages';

        phase.stages.forEach((stageName, stageIdx) => {
            // Stage node
            const node = createStageNode(stageName, phase.color);
            stagesContainer.appendChild(node);

            // Connector (except after last stage in phase)
            if (stageIdx < phase.stages.length - 1) {
                const connector = document.createElement('div');
                connector.className = 'stage-connector';
                connector.style.background = phase.color + '40';
                stagesContainer.appendChild(connector);
            }
        });

        row.appendChild(stagesContainer);

        // Phase connector (except after last phase)
        if (phaseIdx < PIPELINE_PHASES.length - 1) {
            const phaseConn = document.createElement('div');
            phaseConn.className = 'phase-connector';
            phaseConn.style.setProperty('--from-color', phase.color);
            phaseConn.style.setProperty('--to-color', PIPELINE_PHASES[phaseIdx + 1].color);
            row.appendChild(phaseConn);
        }

        container.appendChild(row);
    });
}

function createStageNode(stageName, phaseColor) {
    const node = document.createElement('div');
    node.className = 'stage-node';
    node.dataset.stage = stageName;

    // Get stage data if available
    const stageData = getStageData(stageName);
    if (stageData) {
        if (stageData.error) {
            node.classList.add('error');
        } else if (stageData.skipped) {
            node.classList.add('skip');
        } else {
            node.classList.add('ok');
        }
    } else {
        // Default styling when no data
        node.style.background = phaseColor + '30';
        node.style.borderColor = phaseColor + '50';
    }

    // Label
    const label = document.createElement('div');
    label.className = 'stage-label';
    label.textContent = STAGE_LABELS[stageName] || stageName;
    node.appendChild(label);

    // Timing
    const time = document.createElement('div');
    time.className = 'stage-time';
    if (stageData && stageData.duration_ms !== undefined) {
        time.textContent = formatDuration(stageData.duration_ms);
    } else {
        time.textContent = '--';
    }
    node.appendChild(time);

    // Click handler
    node.onclick = () => selectStage(stageName);

    return node;
}

// ============================================================================
// INTERACTION
// ============================================================================

function selectStage(stageName) {
    // Update selection
    pipelineState.selectedStage = stageName;

    // Update visual selection
    document.querySelectorAll('.stage-node').forEach(n => {
        n.classList.toggle('selected', n.dataset.stage === stageName);
    });

    // Update detail panel
    renderStageDetail(stageName);
}

function renderStageDetail(stageName) {
    const container = document.getElementById('pipeline-detail');
    if (!container) return;

    const stageData = getStageData(stageName);

    if (!stageData) {
        container.innerHTML = `
            <div class="detail-placeholder">
                No data available for stage: ${stageName}<br>
                <small>Run pipeline with snapshot capture enabled</small>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="detail-content">
            <div class="detail-section">
                <h3>Stage Info</h3>
                <div class="detail-row">
                    <span class="detail-label">Name</span>
                    <span class="detail-value">${stageName}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Status</span>
                    <span class="detail-value ${stageData.error ? 'negative' : 'positive'}">
                        ${stageData.error ? 'ERROR' : stageData.skipped ? 'SKIPPED' : 'OK'}
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Duration</span>
                    <span class="detail-value">${formatDuration(stageData.duration_ms)}</span>
                </div>
                ${stageData.error ? `
                <div class="detail-row">
                    <span class="detail-label">Error</span>
                    <span class="detail-value negative">${stageData.error}</span>
                </div>
                ` : ''}
            </div>

            <div class="detail-section">
                <h3>Data Flow</h3>
                <div class="detail-row">
                    <span class="detail-label">Nodes Before</span>
                    <span class="detail-value">${stageData.nodes_before}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Nodes After</span>
                    <span class="detail-value">${stageData.nodes_after}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Nodes Added</span>
                    <span class="detail-value ${stageData.nodes_added > 0 ? 'positive' : ''}">${stageData.nodes_added > 0 ? '+' : ''}${stageData.nodes_added}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Edges Before</span>
                    <span class="detail-value">${stageData.edges_before}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Edges After</span>
                    <span class="detail-value">${stageData.edges_after}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Edges Added</span>
                    <span class="detail-value ${stageData.edges_added > 0 ? 'positive' : ''}">${stageData.edges_added > 0 ? '+' : ''}${stageData.edges_added}</span>
                </div>
            </div>

            <div class="detail-section">
                <h3>Fields Added</h3>
                <div class="field-list">
                    ${renderFieldsList(stageData.fields_added || [])}
                </div>
            </div>
        </div>

        ${stageData.metadata_keys_added && stageData.metadata_keys_added.length > 0 ? `
        <div class="detail-section" style="margin-top: 16px;">
            <h3>Metadata Keys Added</h3>
            <div class="field-list">
                ${stageData.metadata_keys_added.map(k => `<div class="field-item"><span class="field-name">${k}</span></div>`).join('')}
            </div>
        </div>
        ` : ''}

        ${stageData.sample_node_after ? `
        <div class="detail-section" style="margin-top: 16px; grid-column: span 3;">
            <h3>Sample Node (After)</h3>
            <div class="sample-node">
                <pre>${JSON.stringify(stageData.sample_node_after, null, 2)}</pre>
            </div>
        </div>
        ` : ''}
    `;
}

function renderFieldsList(fields) {
    if (!fields || fields.length === 0) {
        return '<div class="detail-placeholder" style="padding: 8px;">No new fields</div>';
    }

    return fields.map(f => `
        <div class="field-item">
            <span class="field-name">${f.field_name}</span>
            <span class="field-count">${f.added_count > 0 ? '+' + f.added_count : ''}</span>
        </div>
    `).join('');
}

// ============================================================================
// DATA ACCESS
// ============================================================================

function getStageData(stageName) {
    if (!pipelineState.snapshot || !pipelineState.snapshot.stages) {
        return null;
    }
    return pipelineState.snapshot.stages.find(s => s.stage_name === stageName);
}

function loadPipelineSnapshot(snapshot) {
    pipelineState.snapshot = snapshot;
    updatePipelineSummary();
    renderPipelineFlow();
}

function updatePipelineSummary() {
    const snapshot = pipelineState.snapshot;
    if (!snapshot) return;

    const totalEl = document.getElementById('pn-total-stages');
    const durationEl = document.getElementById('pn-duration');
    const successEl = document.getElementById('pn-success');
    const failedEl = document.getElementById('pn-failed');

    if (totalEl) totalEl.textContent = `${snapshot.stages?.length || 27} stages`;
    if (durationEl) durationEl.textContent = formatDuration(snapshot.total_duration_ms);
    if (successEl) successEl.textContent = `${snapshot.stages_succeeded || 0} OK`;
    if (failedEl) failedEl.textContent = `${snapshot.stages_failed || 0} ERR`;
}

// ============================================================================
// UTILITIES
// ============================================================================

function formatDuration(ms) {
    if (ms === undefined || ms === null) return '--';
    if (ms < 1) return '<1ms';
    if (ms < 1000) return Math.round(ms) + 'ms';
    return (ms / 1000).toFixed(1) + 's';
}

// ============================================================================
// PUBLIC API
// ============================================================================

function togglePipelineNavigator() {
    const nav = document.getElementById('pipeline-navigator');
    if (!nav) {
        createPipelineNavigator();
        togglePipelineNavigator();
        return;
    }

    pipelineState.isOpen = !pipelineState.isOpen;
    nav.classList.toggle('hidden', !pipelineState.isOpen);

    // Try to load snapshot from global data
    // Data is in FULL_GRAPH (decompressed from COMPRESSED_PAYLOAD)
    if (pipelineState.isOpen && !pipelineState.snapshot) {
        const graphData = window.FULL_GRAPH;
        if (graphData && graphData.pipeline_snapshot) {
            loadPipelineSnapshot(graphData.pipeline_snapshot);
        }
    }
}

function isPipelineNavigatorOpen() {
    return pipelineState.isOpen;
}

// Keyboard shortcut
document.addEventListener('keydown', (e) => {
    if (e.key === 'p' || e.key === 'P') {
        if (!e.ctrlKey && !e.metaKey && !e.altKey) {
            const activeEl = document.activeElement;
            if (activeEl.tagName !== 'INPUT' && activeEl.tagName !== 'TEXTAREA') {
                e.preventDefault();
                togglePipelineNavigator();
            }
        }
    }
    // Escape to close
    if (e.key === 'Escape' && pipelineState.isOpen) {
        togglePipelineNavigator();
    }
});

// Export for module system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        togglePipelineNavigator,
        isPipelineNavigatorOpen,
        loadPipelineSnapshot,
        createPipelineNavigator,
    };
}

// Also expose globally
window.togglePipelineNavigator = togglePipelineNavigator;
window.loadPipelineSnapshot = loadPipelineSnapshot;
