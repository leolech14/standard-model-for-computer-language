# Implementation Proposal: Collider AI Insights Integration

**Author:** Claude + Leonardo
**Date:** 2026-01-19
**Status:** DRAFT
**Priority:** HIGH

---

## 1. EXECUTIVE SUMMARY

### Problem
Collider generates comprehensive code analysis (topology, metrics, RPBL scores) but lacks **contextual AI-powered insights** that connect findings to known patterns, anti-patterns, and refactoring strategies.

### Solution
Integrate Google Cloud Vertex AI into the Collider pipeline to enrich HTML reports with semantic analysis, pattern recognition, and actionable recommendations grounded in software architecture knowledge.

### Scope
- Add new `insights` mode to existing `analyze.py`
- Create structured insights schema
- Inject AI insights into HTML report generation
- Maintain single-file HTML output (no external dependencies)

---

## 2. CURRENT STATE ANALYSIS

### 2.1 Existing Infrastructure (context-management/)

| Component | Location | Status |
|-----------|----------|--------|
| Vertex AI Client | `tools/ai/analyze.py` | ✅ Working |
| GCS Mirror | `gs://elements-archive-2026` | ✅ Working |
| Analysis Sets | `config/analysis_sets.yaml` | ✅ Configured |
| Three-Role Architecture | Librarian, Surgeon, Architect | ✅ Documented |

### 2.2 Existing Analysis Modes

```python
MODES = {
    "standard":  # General analysis
    "forensic":  # Line-level citations
    "architect": # Theory-aware (RPBL, Atoms)
}
```

### 2.3 Collider HTML Generation (standard-model-of-code/)

| Component | Location | Purpose |
|-----------|----------|---------|
| Pipeline Orchestrator | `src/core/full_analysis.py` | 11-stage analysis |
| HTML Generator | `tools/visualize_graph_webgl.py` | JSON → HTML |
| Template | `src/core/viz/assets/template.html` | HTML scaffold |
| JavaScript | `src/core/viz/assets/app.js` | 3D graph + UI |
| Report Section | `src/core/brain_download.py` | Markdown report |

### 2.4 Data Flow (Current)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  full_analysis  │ ──▶ │ unified_analysis │ ──▶ │ visualize_graph │
│     .py         │     │     .json        │     │   _webgl.py     │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │ collider_report │
                                                 │     .html       │
                                                 └─────────────────┘
```

---

## 3. PROPOSED ARCHITECTURE

### 3.1 Data Flow (New)

```
┌─────────────────┐     ┌──────────────────┐
│  full_analysis  │ ──▶ │ unified_analysis │
│     .py         │     │     .json        │
└─────────────────┘     └────────┬─────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
           ┌───────────────┐         ┌───────────────┐
           │  [EXISTING]   │         │    [NEW]      │
           │ visualize_    │         │  insights_    │
           │ graph_webgl   │         │  generator    │
           └───────┬───────┘         └───────┬───────┘
                   │                         │
                   │    ┌────────────┐       │
                   │    │  Vertex AI │◀──────┘
                   │    │  (Gemini)  │
                   │    └─────┬──────┘
                   │          │
                   │          ▼
                   │    ┌────────────┐
                   │    │ ai_insights│
                   │    │   .json    │
                   │    └─────┬──────┘
                   │          │
                   ▼          ▼
              ┌─────────────────────┐
              │  collider_report    │
              │  .html (enriched)   │
              └─────────────────────┘
```

### 3.2 New Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Insights Generator | `tools/ai/insights_generator.py` | Orchestrates AI analysis |
| Insights Mode | `tools/ai/analyze.py` (extended) | New `--mode insights` |
| Insights Schema | `config/insights_schema.json` | Structured output format |
| HTML Panel | `src/core/viz/assets/template.html` | AI Insights UI panel |
| JS Handler | `src/core/viz/assets/app.js` | Render insights data |

---

## 4. DETAILED DESIGN

### 4.1 Insights Schema (`config/insights_schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "meta": {
      "type": "object",
      "properties": {
        "generated_at": { "type": "string", "format": "date-time" },
        "model": { "type": "string" },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "patterns_detected": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "pattern_name": { "type": "string" },
          "pattern_type": { "enum": ["design_pattern", "anti_pattern", "architectural"] },
          "confidence": { "type": "number" },
          "affected_nodes": { "type": "array", "items": { "type": "string" } },
          "evidence": { "type": "string" },
          "recommendation": { "type": "string" }
        }
      }
    },
    "refactoring_opportunities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": { "type": "string" },
          "priority": { "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"] },
          "category": { "type": "string" },
          "description": { "type": "string" },
          "affected_files": { "type": "array", "items": { "type": "string" } },
          "estimated_impact": { "type": "string" }
        }
      }
    },
    "topology_analysis": {
      "type": "object",
      "properties": {
        "shape_interpretation": { "type": "string" },
        "health_assessment": { "type": "string" },
        "comparison": { "type": "string" }
      }
    },
    "executive_summary": { "type": "string" }
  }
}
```

### 4.2 Insights Mode Prompt Template

```python
INSIGHTS_PROMPT = """
You are a SOFTWARE ARCHITECTURE ANALYST specializing in pattern recognition.

CONTEXT:
- Codebase: {target_name}
- Nodes: {node_count}
- Edges: {edge_count}
- Topology: {topology_shape}
- Knot Score: {knot_score}/10 (cyclic complexity)
- Dead Code: {dead_code_percent}%
- Top Hubs: {top_hubs}
- RPBL Profile: R={r}, P={p}, B={b}, L={l}

EXISTING RECOMMENDATIONS:
{existing_recommendations}

TASK:
1. Identify design patterns present (Factory, Repository, Observer, etc.)
2. Detect anti-patterns (God Object, Spaghetti, Anemic Domain Model, etc.)
3. Suggest 3 specific refactoring opportunities with priority
4. Interpret the topology shape in architectural terms
5. Provide a 2-sentence executive summary

OUTPUT FORMAT:
Return valid JSON matching the insights schema. Be specific and cite node names.
"""
```

### 4.3 Integration Points

#### 4.3.1 In `tools/ai/analyze.py`

```python
# Add to MODES dict (line ~132)
"insights": {
    "prompt": INSIGHTS_PROMPT,
    "output_format": "json",
    "schema": "config/insights_schema.json"
}
```

#### 4.3.2 In `tools/visualize_graph_webgl.py`

```python
# After line ~295 (KPI calculation), before graph_data assembly:

def load_ai_insights(output_dir):
    """Load AI insights if available."""
    insights_path = Path(output_dir) / "ai_insights.json"
    if insights_path.exists():
        with open(insights_path) as f:
            return json.load(f)
    return None

# In generate_webgl_html():
ai_insights = load_ai_insights(output_dir)
if ai_insights:
    graph_data['ai_insights'] = ai_insights
```

#### 4.3.3 In `src/core/viz/assets/template.html`

```html
<!-- Add after report-panel (line ~84) -->
<div class="hud-panel ai-panel" id="ai-panel">
    <h1>AI Insights</h1>
    <div class="ai-content" id="ai-content">
        <div class="ai-loading">Analyzing...</div>
    </div>
</div>
```

#### 4.3.4 In `src/core/viz/assets/app.js`

```javascript
// Add render function for AI insights
function renderAIInsights(insights) {
    if (!insights) {
        document.getElementById('ai-content').innerHTML =
            '<div class="ai-empty">No AI insights available</div>';
        return;
    }

    let html = `<div class="ai-summary">${insights.executive_summary}</div>`;

    // Patterns
    if (insights.patterns_detected?.length) {
        html += '<h2>Patterns Detected</h2><ul>';
        for (const p of insights.patterns_detected) {
            const icon = p.pattern_type === 'anti_pattern' ? '⚠️' : '✓';
            html += `<li>${icon} <strong>${p.pattern_name}</strong> (${(p.confidence*100).toFixed(0)}%)<br/>
                     <small>${p.evidence}</small></li>`;
        }
        html += '</ul>';
    }

    // Refactoring
    if (insights.refactoring_opportunities?.length) {
        html += '<h2>Refactoring Opportunities</h2><ul>';
        for (const r of insights.refactoring_opportunities) {
            html += `<li><span class="priority-${r.priority.toLowerCase()}">${r.priority}</span>
                     <strong>${r.title}</strong><br/>${r.description}</li>`;
        }
        html += '</ul>';
    }

    document.getElementById('ai-content').innerHTML = html;
}
```

---

## 5. IMPLEMENTATION PHASES

### Phase 1: Schema & Mode (2 hours)

| Step | Task | Output |
|------|------|--------|
| 1.1 | Create `config/insights_schema.json` | Schema file |
| 1.2 | Add `insights` mode to `analyze.py` | Extended analyze.py |
| 1.3 | Create `insights_generator.py` wrapper | New file |
| 1.4 | Test with sample Collider output | Validated JSON |

**Deliverable:** `python analyze.py --mode insights --file unified_analysis.json "Analyze this codebase"`

### Phase 2: HTML Integration (2 hours)

| Step | Task | Output |
|------|------|--------|
| 2.1 | Add AI panel to `template.html` | Updated template |
| 2.2 | Add render function to `app.js` | Updated JS |
| 2.3 | Add CSS styles for AI panel | Updated styles |
| 2.4 | Modify `visualize_graph_webgl.py` to inject | Updated generator |

**Deliverable:** HTML report with AI Insights panel

### Phase 3: Pipeline Integration (1 hour)

| Step | Task | Output |
|------|------|--------|
| 3.1 | Add `--ai-insights` flag to Collider CLI | Updated CLI |
| 3.2 | Integrate into `full_analysis.py` pipeline | Updated pipeline |
| 3.3 | Add fallback for offline/no-GCP mode | Graceful degradation |

**Deliverable:** `./collider full /path --output /tmp --ai-insights`

### Phase 4: Testing & Documentation (1 hour)

| Step | Task | Output |
|------|------|--------|
| 4.1 | Test on standard-model-of-code itself | Self-analysis |
| 4.2 | Test on 3 benchmark repos | Validation |
| 4.3 | Document in CLAUDE.md | Updated docs |
| 4.4 | Add to AI_OPERATING_MANUAL.md | Updated manual |

**Deliverable:** Tested, documented feature

---

## 6. FILE CHANGES SUMMARY

### New Files (4)

| File | Purpose |
|------|---------|
| `config/insights_schema.json` | JSON schema for AI output |
| `tools/ai/insights_generator.py` | Orchestration wrapper |
| `docs/proposals/COLLIDER_AI_INSIGHTS_PROPOSAL.md` | This document |
| `tests/test_insights.py` | Unit tests |

### Modified Files (6)

| File | Changes |
|------|---------|
| `tools/ai/analyze.py` | Add `insights` mode |
| `tools/visualize_graph_webgl.py` | Load and inject insights |
| `src/core/viz/assets/template.html` | Add AI panel |
| `src/core/viz/assets/app.js` | Add render function |
| `src/core/viz/assets/styles.css` | Add AI panel styles |
| `cli.py` | Add `--ai-insights` flag |

---

## 7. COST ANALYSIS

### Per Analysis (Estimated)

| Item | Value |
|------|-------|
| Input tokens | ~50K (Collider JSON summary) |
| Output tokens | ~2K (structured insights) |
| Model | Gemini 2.0 Flash |
| Cost per analysis | ~$0.01 |

### Monthly (Projected)

| Usage | Cost |
|-------|------|
| 10 analyses/day | ~$3/month |
| 100 analyses/day | ~$30/month |

---

## 8. RISK ASSESSMENT

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Rate limiting | Medium | Low | Exponential backoff (exists) |
| Invalid JSON output | Medium | Medium | Schema validation + retry |
| GCP auth issues | Low | High | Clear error messages |
| Large codebase timeout | Low | Medium | Summarize before sending |
| Cost overrun | Low | Low | Cost estimation (exists) |

---

## 9. SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| AI insights generated | 100% of runs with `--ai-insights` |
| Schema validation pass | 100% |
| HTML render success | 100% |
| User satisfaction | Insights are "actionable" |
| Performance overhead | < 30 seconds added |

---

## 10. DECISION REQUIRED

### Option A: Full Integration (Recommended)
- All 4 phases
- ~6 hours total
- Complete pipeline integration

### Option B: Standalone Tool
- Phase 1 only
- ~2 hours
- Manual JSON → HTML workflow

### Option C: Defer
- Document for later
- 0 hours now
- No immediate benefit

---

## APPENDIX A: Example Output

```json
{
  "meta": {
    "generated_at": "2026-01-19T12:00:00Z",
    "model": "gemini-2.0-flash-001",
    "confidence": 0.85
  },
  "patterns_detected": [
    {
      "pattern_name": "Facade Pattern",
      "pattern_type": "design_pattern",
      "confidence": 0.92,
      "affected_nodes": ["TreeSitterUniversalEngine", "UnifiedAnalyzer"],
      "evidence": "TreeSitterUniversalEngine delegates to UniversalClassifier and PythonASTExtractor",
      "recommendation": "Well-implemented. Consider documenting the facade boundary."
    },
    {
      "pattern_name": "God Object",
      "pattern_type": "anti_pattern",
      "confidence": 0.78,
      "affected_nodes": ["full_analysis.py"],
      "evidence": "Orchestrates 11 stages with 47 direct dependencies",
      "recommendation": "Extract stage runners into separate modules."
    }
  ],
  "refactoring_opportunities": [
    {
      "title": "Extract Visualization Module",
      "priority": "MEDIUM",
      "category": "Separation of Concerns",
      "description": "Move HTML generation from tools/ to src/core/viz/",
      "affected_files": ["tools/visualize_graph_webgl.py"],
      "estimated_impact": "Cleaner architecture, easier testing"
    }
  ],
  "topology_analysis": {
    "shape_interpretation": "STAR_HUB topology centered on full_analysis.py",
    "health_assessment": "Moderate coupling. Consider dependency inversion.",
    "comparison": "Similar to early Django architecture before app extraction."
  },
  "executive_summary": "This codebase demonstrates a well-structured Facade pattern for parsing but exhibits God Object tendencies in its orchestration layer. Priority refactoring: extract stage runners from full_analysis.py."
}
```

---

## APPENDIX B: Command Examples

```bash
# Generate insights for a Collider analysis
python tools/ai/analyze.py \
  --mode insights \
  --file /tmp/analysis/unified_analysis.json \
  "Analyze patterns and suggest refactoring"

# Full pipeline with AI insights
./collider full /path/to/repo --output /tmp/out --ai-insights

# Validate insights schema
python -c "import json; json.load(open('ai_insights.json'))"
```

---

**END OF PROPOSAL**
