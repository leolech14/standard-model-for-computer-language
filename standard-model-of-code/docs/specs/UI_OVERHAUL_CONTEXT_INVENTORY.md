# UI Overhaul Context Inventory (ROR)

**Registry of Resources for the Collider UI Overhaul**

**Date:** 2026-01-25
**Term Decision:** **OVERHAUL** (not refactor)
**Status:** Context Gathering Phase

---

## Why "Overhaul" Not "Refactor"

| Term | Definition | Applies? |
|------|------------|----------|
| **Refactor** | Restructure existing code without changing behavior | NO |
| **Overhaul** | Comprehensive redesign of architecture and UX | **YES** |

**This is an OVERHAUL because:**
- New architectural layer (DTE) being added
- New user interface paradigm (Floating Mapper)
- Fundamental change to pixel control (Semantic Sovereignty)
- Canvas behavior redefined (origin, infinite bounds)
- Component library potentially changing (React/Blueprint)

---

## 1. Causality Chain: How We Got Here

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CAUSALITY CHAIN                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PAST: app.js Monolith (12K lines)                                  │
│        │                                                             │
│        │ Problem: God class, unmaintainable                         │
│        ▼                                                             │
│  2026-01: Modularization (12K → 3K lines)                           │
│        │  Created: 48 modules in src/core/viz/assets/modules/       │
│        │                                                             │
│        │ Problem: Scattered binding logic, hardcoded colors         │
│        ▼                                                             │
│  2026-01: Design Token System                                        │
│        │  Created: token files, token resolver, appearance engine   │
│        │  Finding: 75% tokenized, 25% violations                    │
│        │                                                             │
│        │ Problem: No unified binding architecture                    │
│        ▼                                                             │
│  2026-01: UPB (Universal Property Binder)                           │
│        │  Created: endpoints, bindings, scales, blenders            │
│        │  Constraint: Max 300 lines/module, 7 files total           │
│        │                                                             │
│        │ Problem: UPB binds WHAT, but HOW to transform?             │
│        ▼                                                             │
│  2026-01-25: DTE (Data Trade Exchange) - NEW                        │
│        │  Purpose: Central exchange for value conversions           │
│        │  Validated: 9/10 architectural coherence                   │
│        │                                                             │
│        │ Need: User interface to expose these systems               │
│        ▼                                                             │
│  NOW: UI OVERHAUL                                                    │
│        │                                                             │
│        ├── Floating Mapper (DTE's UI)                               │
│        ├── Pixel Sovereignty (100% control)                         │
│        ├── Canvas Specs (foundation)                                │
│        └── Visual Style (pending your input)                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Document Inventory

### 2.1 Architecture Documents

| Document | Path | Purpose | Status |
|----------|------|---------|--------|
| **UPB Spec** | `specs/UNIVERSAL_PROPERTY_BINDER.md` | Binding architecture | ACTIVE |
| **UPB Implementation** | `specs/UPB_IMPLEMENTATION_PLAN.md` | Extraction roadmap | ACTIVE |
| **UPB Task Registry** | `specs/UPB_TASK_REGISTRY.md` | Implementation tasks | ACTIVE |
| **UPB Legacy Sprawl** | `specs/UPB_LEGACY_SPRAWL.md` | Affected modules | ACTIVE |
| **Viz UI Spec** | `specs/VISUALIZATION_UI_SPEC.md` | Module architecture | ACTIVE |
| **UI Layout Architecture** | `specs/UI_LAYOUT_ARCHITECTURE.md` | Layout system | ACTIVE |

### 2.2 Token/Design System Documents

| Document | Path | Purpose | Status |
|----------|------|---------|--------|
| **Token System Audit** | `reports/DESIGN_TOKEN_SYSTEM_AUDIT.md` | Full audit (75% compliant) | VALIDATED |
| **Token Verification Protocol** | `reports/TOKEN_SYSTEM_VERIFICATION_PROTOCOL.md` | How to verify | ACTIVE |
| **Token Task Registry** | `reports/TOKEN_SYSTEM_TASK_REGISTRY.md` | Fix tasks | ACTIVE |

### 2.3 Overhaul Documents (This Session)

| Document | Path | Purpose | Status |
|----------|------|---------|--------|
| **Vision** | `specs/UI_REFACTOR_VISION.md` | Requirements, CRs | UPDATED |
| **Validation** | `specs/UI_ARCHITECTURE_VALIDATION_CONSOLIDATED.md` | Architecture proof | COMPLETE |
| **Logic** | `specs/UI_REFACTOR_IMPLEMENTATION_LOGIC.md` | Dependencies, phases | COMPLETE |
| **Controls Schema** | `specs/UI_CONTROLS_SCHEMA.md` | 82-control target | COMPLETE |
| **This Inventory** | `specs/UI_OVERHAUL_CONTEXT_INVENTORY.md` | Master index | ACTIVE |

### 2.4 Research Documents

| Document | Path | Purpose | Status |
|----------|------|---------|--------|
| **DTE Research** | `research/DTE_SEMANTIC_MATCHING_RESEARCH.md` | Exchange patterns | COMPLETE |
| **Component Library** | `research/UI_COMPONENT_LIBRARY_RESEARCH.md` | Blueprint/React options | COMPLETE |
| **Multi-Parallel Validation** | `research/MULTI_PARALLEL_VALIDATION_REPORT.md` | 9-query validation | COMPLETE |

### 2.5 Corpus Artifacts

| File | Path | Contents |
|------|------|----------|
| **Control Inventory** | `ui/corpus/v1/ui_control_inventory.json` | 60 controls, 5 categories |
| **Controls Schema** | `ui/corpus/v1/ui_controls_schema.json` | 82 controls target |
| **Findings** | `ui/corpus/v1/findings.json` | Critical fixes |
| **Layout Model** | `ui/corpus/v1/ui_layout_model.json` | 9-square grid |
| **Tokens** | `ui/corpus/v1/ui_tokens.json` | CSS variables |
| **README** | `ui/corpus/v1/README.md` | Corpus index |

### 2.6 External Research (Auto-saved)

| Topic | Gemini | Perplexity |
|-------|--------|------------|
| DTE Architecture | `gemini/docs/20260125_024349_*.md` | `perplexity/docs/20260125_025547_*.md` |
| Theoretical Soundness | `gemini/docs/20260125_024342_*.md` | - |
| Pixel Sovereignty | `gemini/docs/20260125_024338_*.md` | - |
| Design Tokens | - | `perplexity/docs/20260125_025557_*.md` |
| OKLCH Color | - | `perplexity/docs/20260125_025628_*.md` |
| Visual Grammar | - | `perplexity/docs/20260125_025709_*.md` |
| Provider Chain | - | `perplexity/docs/20260125_025746_*.md` |

---

## 3. Architecture Components

### 3.1 Validated Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     VISUALIZATION STACK                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   USER INTERFACE (Pending your input)                       │
│   ════════════════════════════════════                      │
│   ├── Floating Mapper (CR#1)                                │
│   ├── Sidebars (CR#4, CR#5)                                │
│   └── Visual Style (CR#2) ◄─── AWAITING SPECS              │
│                         │                                    │
│                         ▼                                    │
│   UPB (Binding Layer) ─────────────────────── 9/10 READY   │
│   ├── endpoints.js (sources/targets)                        │
│   ├── bindings.js (graph logic)                             │
│   └── scales.js (transform functions)                       │
│                         │                                    │
│                         ▼                                    │
│   DTE (Exchange Layer) ────────────────────── 9/10 DESIGNED│
│   ├── Domain Registry                                       │
│   ├── Exchange Registry                                     │
│   └── QUOTE/TRADE/BATCH/AUDIT                              │
│                         │                                    │
│                         ▼                                    │
│   PROPERTY-QUERY (Resolution) ─────────────── 9.5/10 READY │
│   ├── Provider chain (100→80→20→0)                         │
│   └── Epoch-based cache                                     │
│                         │                                    │
│                         ▼                                    │
│   OKLCH COLOR ENGINE ──────────────────────── VALIDATED    │
│   └── Perceptually uniform output                           │
│                         │                                    │
│                         ▼                                    │
│   PIXEL (Final Output)                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Current State Metrics

| Metric | Value | Source |
|--------|-------|--------|
| **Pixel Sovereignty** | 75% | Validation audit |
| **Token Coverage** | 75% | Design Token Audit |
| **Module Count** | 48 | viz/assets/modules/ |
| **app.js Size** | ~3K lines | Down from 12K |
| **Control Inventory** | 60 actual | ui_control_inventory.json |
| **Control Target** | 82 ideal | ui_controls_schema.json |

---

## 4. Change Requests Summary

| CR# | Name | Architecture Link | Status |
|-----|------|-------------------|--------|
| CR#1 | Floating Mapper | DTE user interface | SPEC COMPLETE |
| CR#2 | De-glamorize Colors | Pixel Sovereignty | AWAITING STYLE SPECS |
| CR#3 | Remove Stars | Canvas Foundation | SPEC COMPLETE |
| CR#4 | Section Resize | Layout System | SPEC COMPLETE |
| CR#5 | Sidebar Resize | Layout System | SPEC COMPLETE |

---

## 5. Foundational Specs

| Spec | Status | Key Decision |
|------|--------|--------------|
| **Canvas Size** | CONFIRMED | 100% of dedicated section |
| **Canvas Bounds** | CONFIRMED | Infinite (pannable) |
| **Canvas X Origin** | CONFIRMED | Center |
| **Canvas Y Origin** | PENDING | 50%, 33%, or 66%? |
| **Pixel Sovereignty** | 75% → 100% | Fix violations in app.js |
| **DTE Operations** | DESIGNED | QUOTE, TRADE, BATCH, REGISTER, AUDIT |

---

## 6. Pending Input (From You)

| Item | Purpose | Impact |
|------|---------|--------|
| **UI Style Specifications** | Color palette, spacing, typography | CR#2, overall look |
| **"Boring UI" Reference** | macOS? Windows? Material? Custom? | De-glamorize direction |
| **Canvas Y Origin** | Vertical position of (0,0,0) | Camera defaults |
| **Component Library Decision** | Blueprint? Custom? Hybrid? | Implementation approach |

---

## 7. Validation Summary

| Component | Internal | External | Score |
|-----------|----------|----------|-------|
| UPB | Aligned | Grammar of Graphics | 9/10 |
| DTE | Coherent | Broker patterns | 9/10 |
| Property-Query | Ready | AWS/Microsoft patterns | 9.5/10 |
| OKLCH | Integrated | Academic consensus | VALIDATED |
| Pixel Sovereignty | 75% | W3C Design Tokens | NEEDS WORK |

---

## 8. Next Actions

**Waiting for your input:**
1. UI Style Specifications
2. Visual reference for "boring" UI
3. Any additional context

**Ready to proceed when you are:**
- Phase 0: Remove stars (clean slate)
- Phase 1: Pixel Sovereignty (fix violations)
- Phase 2: DTE Core (exchange engine)
- Phase 3: User-facing features

---

## 9. Quick Reference

### Key Files
```
docs/specs/UI_OVERHAUL_CONTEXT_INVENTORY.md  ← YOU ARE HERE
docs/specs/UI_REFACTOR_VISION.md             ← Requirements
docs/specs/UI_ARCHITECTURE_VALIDATION_CONSOLIDATED.md ← Proof
docs/specs/UI_REFACTOR_IMPLEMENTATION_LOGIC.md ← Phases
docs/specs/UNIVERSAL_PROPERTY_BINDER.md      ← UPB Architecture
docs/research/DTE_SEMANTIC_MATCHING_RESEARCH.md ← DTE Design
```

### Key Commands
```bash
# Regenerate after changes
./collider full . --output .collider

# Validate controls
python tools/validate_ui.py .collider/collider_report.html

# Check hardcoded colors
grep -rE "(#[0-9a-fA-F]{6}|rgb\()" src/core/viz/assets/modules/
```

