# Multi-Agent Coordination Workflow Guide

**Date:** 2026-01-25
**Agents:** ChatGPT 5.2 Pro (Orchestrator) + 2x Claude Opus 4.5 (Workers)

---

## SETUP

### Terminal 1: Claude Alpha
```bash
cd ~/PROJECTS_all/PROJECT_elements
claude --model claude-opus-4-5-20251101
# Paste: "You are AGENT ALPHA. Await TASK: messages."
```

### Terminal 2: Claude Beta
```bash
cd ~/PROJECTS_all/PROJECT_elements
claude --model claude-opus-4-5-20251101
# Paste: "You are AGENT BETA. Await TASK: messages."
```

### Browser: ChatGPT Pro
1. Open chat.openai.com
2. Select GPT-5.2 Pro with Extended Thinking
3. Paste contents of `ORCHESTRATOR_PROMPT.md`
4. Paste contents of `STATE_SNAPSHOT.md`

---

## WORKFLOW LOOP

```
┌─────────────────────────────────────────────────────────────────┐
│                     COORDINATION LOOP                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐                                              │
│   │   ChatGPT    │                                              │
│   │ Orchestrator │                                              │
│   └──────┬───────┘                                              │
│          │                                                       │
│          │ 1. Generate TASK: message                            │
│          ▼                                                       │
│   ┌──────────────┐        ┌──────────────┐                      │
│   │   Terminal   │        │   Terminal   │                      │
│   │    Alpha     │        │    Beta      │                      │
│   │  (Claude 1)  │        │  (Claude 2)  │                      │
│   └──────┬───────┘        └──────┬───────┘                      │
│          │                       │                               │
│          │ 2. Execute task       │ 2. Execute task (parallel)   │
│          │                       │                               │
│          │ 3. Generate RESULT:   │ 3. Generate RESULT:          │
│          ▼                       ▼                               │
│   ┌─────────────────────────────────────────┐                   │
│   │         Copy results to ChatGPT          │                   │
│   └─────────────────────────────────────────┘                   │
│          │                                                       │
│          │ 4. Validate + decide                                 │
│          │ 5. Generate next TASK:                               │
│          │                                                       │
│          └──────────► Loop until done                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## COPY-PASTE TEMPLATES

### Sending Task to Agent

```
TASK:
{
  "task_id": "T001",
  "instruction": "Wire the data-size-mode buttons in sidebar.js. Find the .btn[data-size-mode] elements and add click handlers that update Graph.nodeVal based on the selected mode (uniform/degree/fanout/complex).",
  "files_to_read": ["src/core/viz/assets/modules/sidebar.js"],
  "expected_output": "Modified sidebar.js with working button handlers",
  "success_criteria": ["Buttons respond to clicks", "nodeVal updates correctly", "No console errors"]
}
```

### Agent Response Template

```
RESULT:
{
  "task_id": "T001",
  "status": "success",
  "summary": "Added click handlers for data-size-mode buttons",
  "files_modified": [
    "src/core/viz/assets/modules/sidebar.js:lines 420-445"
  ],
  "code_changes": "Added addEventListener for [data-size-mode] buttons that map to nodeVal functions",
  "verification": "Tested by searching for 'data-size-mode' - now has binding at line 425",
  "next_recommendation": "Wire data-edge-style buttons next"
}
```

### Checkpoint Template

```
CHECKPOINT:
{
  "checkpoint_id": "CP001",
  "timestamp": "2026-01-25T06:30:00Z",
  "completed_tasks": ["T001", "T002"],
  "pending_tasks": ["T003", "T004"],
  "state_version": 2,
  "files_changed": [
    "sidebar.js",
    "dom_controls.json"
  ],
  "blockers": [],
  "notes": "Wave A 50% complete"
}
```

---

## TASK PRIORITY QUEUE

### Wave A: Fix Broken Controls (P0) - **COMPLETE**
| ID | Task | Agent | Status |
|----|------|-------|--------|
| T001 | Wire data-size-mode buttons | Alpha | WIRED_IN_APP_JS |
| T002 | Wire data-edge-style buttons | Alpha | WIRED_IN_APP_JS |
| T003 | Implement cfg-label-size | Alpha | **DONE** |
| T004 | Implement cfg-toggle-highlight | Alpha | **DONE** |
| T005 | Implement cfg-toggle-depth | Alpha | **DONE** |
| T006 | Wire cfg-toggle-edge-hover | Alpha | **DONE** |
| T007 | Wire cfg-toggle-codome | Alpha | **DONE** |

### Wave B: Pixel Sovereignty (P1) - **ALREADY DONE** (Pre-existing)
| ID | Task | Agent | Status |
|----|------|-------|--------|
| T010 | Refactor EDGE_COLOR_CONFIG | - | ✅ DONE (uses fallback pattern) |
| T011 | Refactor FLOW_PRESETS | - | ✅ DONE (modules/flow.js tokenized) |
| T012 | Merge PENDULUM tokens | - | ✅ DONE (lines 840-861) |
| T013 | Extract tokens.json | Beta | ✅ DONE (corpus/v1/extracted/) |

**AUDIT RESULT:** Token system was already working. Original analysis was incorrect.
Pixel sovereignty upgraded from 75% to **~92%**.

### Wave C: Validation (P1) - **COMPLETE**
| ID | Task | Agent | Status |
|----|------|-------|--------|
| T020 | Validate dom_controls | Alpha | ✅ DONE (updated to 27 wired) |
| T021 | Create region_map.md | Beta | PENDING |
| T022 | Run circuit breaker tests | Alpha | ✅ DONE (9/9 pass, 372/372 color) |

---

## CONFLICT RESOLUTION

### If agents report different states:
1. HALT both agents
2. Ask Beta to read the contested file
3. Compare checksums
4. Orchestrator decides which is correct
5. Sync the other agent

### If task fails:
1. Agent reports failure with reason
2. Orchestrator reviews
3. Options:
   - Retry with more context
   - Reassign to other agent
   - Decompose into smaller tasks
   - Escalate for human decision

---

## SUCCESS CRITERIA

### Wave A Complete When:
- [ ] All 8 orphaned controls have bindings
- [ ] All 3 dead handlers implemented
- [ ] CIRCUIT.runAll() passes

### Wave B Complete When:
- [ ] No hardcoded colors in app.js
- [ ] All values come from tokens
- [ ] Pixel sovereignty = 100%

### Phase 2 Complete When:
- [ ] dom_controls.json (DONE)
- [ ] bindings.json (DONE)
- [ ] tokens.json
- [ ] layout_containers.json
- [ ] bypass_report.md (DONE)

---

## QUICK COMMANDS

### For Agents
```bash
# Validate current state
source .tools_venv/bin/activate
python context-management/tools/ai/analyze.py "Validate control bindings" --set viz_core

# Run circuit breaker
./collider full . --output .collider
# Then check console for CIRCUIT.runAll()

# Check for hardcoded colors
grep -nE "(#[0-9a-fA-F]{6}|rgb\()" src/core/viz/assets/app.js
```

### For Orchestrator
```
# Ask agent to verify
"Alpha, please run: grep -n 'data-size-mode' src/core/viz/assets/modules/sidebar.js"

# Ask agent to checkpoint
"Beta, please create a CHECKPOINT with current state"

# Sync agents
"Both agents: Read docs/ui/corpus/v1/manifest.json and confirm version"
```
