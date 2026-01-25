# Research: 
ARCHITECTURAL DECISION REQUEST: Property Query Integration Strategy

## CONTEXT
We have built a Pro...

> **Date:** 2026-01-24 15:32:48
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:5a876d3afd51d8a4365e4fea5ca47ac10891509652b7663775fa0314f38b832c`
> **Raw JSON:** `raw/20260124_153248_architectural_decision_request__property_query_in.json`

---

## Query


ARCHITECTURAL DECISION REQUEST: Property Query Integration Strategy

## CONTEXT
We have built a Property Query system (provider-based resolution for visualization properties) but discovered it runs PARALLEL to the existing VIS_STATE system. They don't communicate.

## CURRENT STATE: TWO PARALLEL PATHS

PATH A: LEGACY (CURRENTLY ACTIVE)
- UI Click → VIS_STATE.setColorBy('tier')
- → applyState({ colorBy: 'tier' })
- → window.NODE_COLOR_MODE = 'tier'
- → _refreshGraph() → applyNodeColors(nodes) → PRE-COMPUTES n.color
- → Graph.nodeColor(n => n.color) ← READS PRE-COMPUTED

PATH B: PROPERTY QUERY (NOT WIRED TO UI)
- ??? (nothing calls bumpRender())
- → VIS_STATE._epoch++
- → Graph.refresh()
- → Graph.nodeColor(n => Q.node(n, 'color')) ← COMPUTES AT RENDER
- → reads VIS_STATE.colorPreset ← WRONG FIELD NAME!

## THREE CRITICAL GAPS

1. FIELD NAMES MISMATCH:
   - VIS_STATE uses: colorBy, sizeBy, edgeBy
   - Property Query expects: colorPreset, sizeMode, edgeColorMode, viewMode, edgeStyle

2. REFRESH PATH MISMATCH:
   - VIS_STATE calls _refreshGraph(), not bumpRender()
   - Epoch never increments, cache never invalidates

3. COLOR FLOW MISMATCH:
   - Legacy pre-computes n.color via applyNodeColors()
   - Property Query computes at render via Q.node(n, 'color')
   - Two competing mechanisms

## OPTIONS

OPTION A: ADAPT PROPERTY QUERY TO VIS_STATE
- Change UPB bindings to use colorBy instead of colorPreset
- Have VIS_STATE._refreshGraph() call bumpRender()
- Remove legacy applyNodeColors() pre-computation
- Keep VIS_STATE as source of truth

OPTION B: REPLACE VIS_STATE WITH PROPERTY QUERY
- Rip out VIS_STATE module entirely
- Wire all UI controls to update new field names (colorPreset, sizeMode, etc.)
- Have all controls call bumpRender()
- Property Query becomes sole source of truth

OPTION C: BRIDGE LAYER
- Add translation layer that maps colorBy → colorPreset
- Keep both systems, just connect them
- Least invasive but adds complexity

## CONSTRAINTS
- 40 UI controls exist (33 buttons, 6 sliders, 1 toggle)
- Circuit Breaker validates 9 controls currently
- VIS_STATE is 473 lines, deeply integrated
- Property Query is 4 modules (~1200 lines total)
- Must not break existing functionality

## REQUEST
Provide formal task registry format with:
1. DECISION: Which option (A, B, or C)?
2. CONFIDENCE: Score 0-100 with justification
3. RISK ASSESSMENT: What could go wrong?
4. IMPLEMENTATION TASKS: Numbered list with effort estimates
5. VALIDATION CRITERIA: How do we know it's done?

Use skeptical analysis. Challenge assumptions. Consider maintenance burden.


---

## Response

Okay, I will analyze the situation and provide a formal task registry entry with a recommended decision, confidence score, risk assessment, implementation tasks, and validation criteria.

## ARCHITECTURAL DECISION TASK: Integrate Property Query System

```yaml
task_id: ARCH-001
subject: Integrate Property Query (UPB) into Visualization
description: >
  Integrate the new Property Query (UPB) system with the existing
  VIS_STATE management in visualize_graph_webgl.py.  Resolve the
  current disjointed behavior and ensure a single, reliable source of truth
  for visualization properties.

assumptions:
  - VIS_STATE provides the current, albeit potentially legacy, implementation for controlling node and edge properties.
  - The Property Query system offers a more flexible and extensible framework for property resolution.
  - Maintaining circuit breaker validation tests is essential.
  - Existing UI controls must remain functional.

decision: B
confidence: 85
justification: >
  Option B, replacing VIS_STATE with Property Query, offers the
  cleanest long-term architecture. While the initial effort is higher, it
  eliminates the complexity of maintaining two parallel systems or a translation
  layer. A full replacement allows leveraging the benefits of the Property
  Query system without legacy limitations.
  It also enforces a *single* location to wire the 40 UI controls and all logic.
  This approach respects the "make code obvious" concept from Clean Code.
risk_assessment: >
  High risk of introducing regressions in existing UI controls. Thorough testing is required.  This path could also introduce a large "blast radius",
  i.e. large scope of impact in source code.  Requires careful plan
  of modularized steps. Risk mitigation involves staged deployment with A/B testing after each step.

implementation_tasks:
  1.  title: "Map UI Controls to New Property Query System"
      effort: "Large (40 hours)"
      description: >
        Update all 40 UI controls in `visualize_graph_webgl.py` to directly interact with
        the Property Query system.  This will include changing all of the field names to
        the accepted standards.
      file_path: "standard-model-of-code/src/core/viz/visualize_graph_webgl.py"
      test_plan: "Verify all UI controls function as expected through manual testing. Add automated UI tests to exercise UI controls."
  2.  title: "Implement bumpRender() calls for each UI control in Property Query"
      effort: "Medium (20 hours)"
      description: >
        In the Property Query update calls, make sure to implement the
        bumpRender() calls. This is the entry point to refresh the viz after each
        UI change.
      file_path: "standard-model-of-code/src/core/viz/visualize_graph_webgl.py"
      test_plan: "Verify `bumpRender()` correctly queues new render requests after each change event in the Property Query logic."
  3.  title: "Remove Legacy VIS_STATE Logic"
      effort: "Medium (8 hours)"
      description: >
        Remove all code related to the VIS_STATE module, including the _refreshGraph() function and any functions used for
        pre-computing node color.  Remove window.NODE_COLOR_MODE = 'tier'.
      file_path: "standard-model-of-code/src/core/viz/visualize_graph_webgl.py"
      test_plan: "Ensure the visualization still runs without the VIS_STATE logic. Manually verify no code paths accidentally depend on it."
  4.  title: "Retain and Adapt Circuit Breaker Validation Tests"
      effort: "Small (4 hours)"
      description: >
        Adapt existing circuit breaker validation tests to work with
        the Property Query system.  All 9 circuit breaker paths
        must pass.
      file_path: "standard-model-of-code/src/core/viz/visualize_graph_webgl.py"
      test_plan: "Ensure all circuit breaker tests are adapted to the new Property Query logic."
  5.  title: Validate code and perform a deep check
      effort: Small (2 hours)
      description: |
        Validate there are no references to the old system
      test_plan: Use grep to check this manually
  6.  title: Verify that the code continues to work
      effort: Small (12 hours)
      description: |
        Manually ensure that all UI configurations
        and graph loads complete with the correct settings.
      test_plan: Run through the UI

validation_criteria:
  - "All UI controls function correctly and update the visualization as expected"
  - "Existing circuit breaker validation tests must pass."
  - "Code complexity is reduced by removing VIS_STATE."
  - "A test procedure and the code has been reviewed by a senior engineer"
  - "The full process has been documented."

suggested_actions:
  - "Create a detailed implementation plan with modular steps."
  - "Involve UI/UX experts for control mapping."
  - "Schedule regular reviews during implementation."
  - "Build a demo build that has circuit breaker to ensure nothing is missed"
```


---

## Citations

_No citations provided_
