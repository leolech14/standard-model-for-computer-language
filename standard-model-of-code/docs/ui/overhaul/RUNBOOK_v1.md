# Collider UI OVERHAUL Runbook v1.0

## 0) Purpose

Turn the current Collider UI (baseline build + screenshot corpus) into a **measurable, testable, token-sovereign UI system** that can be safely redesigned and iterated—culminating in a **Confidence Task Registry** that only unlocks tasks with evidence.

## 1) The Overhaul Stack (what must stay true)

Your architecture needs to remain legible and auditable through the UI:

**UPB (Binding):** what visual channel connects to what data field
**DTE (Exchange):** how values transform across domains
**Property Query:** which provider wins (Overrides → UPB → Raw → Defaults)
**OKLCH Engine:** perceptual output + telemetry
**Pixel Sovereignty:** no hard-coded colors bypassing token system

This is non-negotiable: the UI is the user's interface to this chain.

---

# 2) Gates (must be green at every phase boundary)

### Hard gates

* `pytest` passes
* `validate_ui.py` passes

  * `CIRCUIT.runAll()` passes
  * `COLOR_TEST.runAll()` passes
* UI builds (`./collider full`) succeed

### Soft gates (tracked, not blocking until Phase 4)

* UI score improves or stays stable per variant
* Screenshot diff passes or change is explained

---

# 3) Inputs (what we have now)

## A) ZIP corpus (you uploaded)

* Baseline HTML build (`output_human-readable_...html`)
* Dark HUD screenshots
* Watercolor variants (multiple styles)

## B) Local repo source (for later phases)

* `standard-model-of-code/src/core/viz/assets/modules/*`
* `tools/validate_ui.py`, `tools/visualize_graph_webgl.py`, `./collider`

---

# 4) Output directory standard

Create (or use) this structure:

```
standard-model-of-code/docs/ui/overhaul/
  ROR_v1.md
  RUNBOOK_v1.md              (this doc)

standard-model-of-code/docs/ui/corpus/v1/
  manifest.json
  builds/
    baseline.html
  screenshots/
    dark/
    aquarela/
  extracted/
    tokens.json
    dom_controls.json
    bindings.json
    layout_containers.json
  analysis/
    gaps_report.md
    bypass_report.md
    region_map.md

standard-model-of-code/docs/ui/score/
  schema_v1.json
  runs/
    <date>_baseline.json
    <date>_variant_aquarela_d.json
  reports/
    <date>_comparison.md

standard-model-of-code/docs/ui/tasks/
  task_registry_v1.yaml
  unlocked/
    <date>_unlocked.md
```

---

# 5) Phase plan (multi-phase, agent-executable)

## Phase 1 — Corpus bootstrap (no code changes)

**Goal:** ground truth on disk, not vibes.

### Steps

1. Unzip into `docs/ui/corpus/v1/` (don't overwrite existing; use `raw/` if needed).
2. Copy the baseline HTML build into `docs/ui/corpus/v1/builds/baseline.html`.
3. Sort screenshots into:

   * `screenshots/dark/`
   * `screenshots/aquarela/`

### Deliverable

* `docs/ui/corpus/v1/manifest.json` containing:

  * build filename
  * screenshot filenames + tags
  * date
  * notes ("dark HUD baseline", "aquarela paper", etc.)

### DoD

* Everything reproducible from corpus alone (no "I remember where it is").

---

## Phase 2 — Knowledge gap fill (analyze.py driven)

**Goal:** answer "what exists, what's wired, what's tokenized" with evidence.

### Required artifacts

1. `dom_controls.json`
   Every control (ids starting `cfg-`, buttons, chips, selects):

   * selector
   * label text
   * component type (slider/toggle/chip/button/select)
   * region (9-region assignment)
   * status: exists

2. `bindings.json`
   For every control:

   * binding mechanism (onclick/addEventListener/REGISTRY command)
   * handler location (file + line)
   * state mutated (VIS_STATE / APPEARANCE_STATE / Graph accessor)
   * status: wired / orphaned / dead handler

3. `tokens.json`
   From real source of truth:

   * extracted CSS `:root` variables
   * extracted token files (if any)
   * note overlap/conflicts between token sources

4. `bypass_report.md`
   Pixel sovereignty audit:

   * hard-coded rgba/hex occurrences
   * bypasses of COLOR engine
   * app.js monolith bypasses (if any remain)

### analyze.py command templates (agent copy/paste)

Run from repo root:

```bash
source .tools_venv/bin/activate

# A) Controls inventory / bindings
python context-management/tools/ai/analyze.py "
UI GAP FILL: Build a control inventory for Collider UI.
Output JSON schema:
- selector/id
- visible label text
- component type
- handler binding location (file+line)
- state mutated (VIS_STATE / APPEARANCE_STATE / Graph / COLOR)
- status: wired | orphaned | dead handler
Also list all cfg-* IDs and data-* attributes.
" --set viz_core

# B) Token extraction / conflicts / pixel sovereignty
python context-management/tools/ai/analyze.py "
UI GAP FILL: Token sovereignty audit.
Find:
- CSS :root variables and any theme token files
- hard-coded rgba()/hex colors in UI chrome
- conflicts between token sources
Deliver: tokens list + conflicts + top bypasses.
" --set docs_core

# C) Layout truth + responsiveness hooks
python context-management/tools/ai/analyze.py "
UI GAP FILL: Layout truth.
Identify:
- top-level layout containers
- layout variables (sidebar widths, header height)
- resizing/drag handles
- any layout engine modules (e.g., LAYOUT/HudLayoutManager)
Output: layout_containers.json + notes on responsiveness.
" --set viz_core
```

### DoD

* Those 4 artifacts exist and are referenced in `manifest.json`.

---

## Phase 3 — 9-Region Map (semantic 3×3)

**Goal:** create a stable "UI topology" that survives responsiveness.

### Rule

* **Geometry changes continuously**
* **Topology changes discretely** (at breakpoints)

### Deliverables

* `docs/ui/corpus/v1/analysis/region_map.md`
* `docs/ui/corpus/v1/extracted/layout_containers.json` updated to include region mapping

### Region names (recommended)

Don't use R1C1 etc in docs; use semantic IDs:

* `hud.left` (brand + primary mode)
* `hud.center` (perf/hardware cards)
* `hud.right` (selection counters)
* `rail.left.top` (scope/mapping/actions)
* `rail.left.body` (node/edge config)
* `canvas.main` (graph)
* `rail.right.top` (node info/selection)
* `rail.right.body` (schemes/modes)
* `dock.future` (reserved for timeline/command palette/overlay)

### DoD

* Every control in `dom_controls.json` maps to exactly one region.

---

## Phase 4 — UI Scoring Schema + runs

**Goal:** score and compare UI directions (dark vs aquarela variants) in a repeatable way.

### Deliverables

* `docs/ui/score/schema_v1.json`
* `docs/ui/score/runs/<date>_<variant>.json`
* `docs/ui/score/reports/<date>_comparison.md`

### Schema v1 (ready to drop in)

Use 0–5 per dimension, weighted to 100:

* clarity_readability (20)
* hierarchy_focus (15)
* affordance_discoverability (15)
* consistency_systemization (10)
* brand_material_fit (10)
* data_ui_separation (10)
* responsiveness (10)
* accessibility (10)

**Include a per-region breakdown** so you can see *where* the UI fails.

### DoD

* All variants have scores + notes, and the comparison doc states a recommended direction.

---

## Phase 5 — Confidence Task Registry "Unlocked"

**Goal:** no more "maybe tasks." Only tasks with evidence.

### Task unlock rule (must satisfy all)

A task is **Unlocked** iff it has:

* Evidence: control exists (`dom_controls.json`)
* Binding: wired/orphaned proven (`bindings.json`)
* Fix location: file+line known
* Acceptance: CIRCUIT test or screenshot diff plan
* Token impact: which tokens/components affected

### Deliverables

* `docs/ui/tasks/task_registry_v1.yaml`
* `docs/ui/tasks/unlocked/<date>_unlocked.md`

### Confidence score (simple)

Score each task 0–1:

* +0.20 DOM presence
* +0.25 binding proof
* +0.25 fix location
* +0.20 acceptance test plan
* +0.10 token impact defined

Threshold:

* **≥ 0.85** = Unlocked
* 0.60–0.84 = Candidate
* < 0.60 = Speculative (not allowed in registry)

---

## Phase 6 — Implementation wave plan (once style specs arrive)

This is where your pending "UI style specs" become the lock that enables actual implementation.

### Wave A — Interaction integrity (fix "button situation" permanently)

* Every control wired or removed/hidden
* Expand CIRCUIT coverage from 9 → 25+

### Wave B — Pixel sovereignty (tokenize everything)

* Remove hard-coded colors in UI chrome
* Unify token sources (no conflict)

### Wave C — "Aquarela" material layer (only after A+B)

* Backplates/scrims for readability
* Controlled tinting
* Calm motion rules

---

# 6) What I need from you next (to start Phase 6 safely)

Your style spec doesn't need to be huge; it needs to be **decisive**:

1. Material base: **paper** / **glass** / **hybrid**
2. Panel policy: always backplated? blur allowed? max blur radius?
3. Accent allocation: UI vs data vs status
4. Typography: contrast rules on textured backgrounds
5. Motion: what may animate + speed limits
6. Breakpoints: when rails become drawers/sheets

---

# 7) Proactive recommendation (based on your variants)

Use the scoring system to confirm it, but my call right now:

**Target direction:** "paper-clean base + controlled watercolor accents"
Not "full wash everywhere." Full wash makes the graph + UI compete and creates contrast drift.

So the OVERHAUL is:

* keep the pro-tool clarity grammar
* add aquarela as a *layer*, not as a flood
