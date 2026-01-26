# SYSTEM CRYSTALLIZATION INDEX

> **Purpose:** Master index of all emergency maps - the complete crystallized state
> **Created:** 2026-01-26
> **Author:** Claude Opus 4.5

---

## THE THREE REALMS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROJECT_elements CRYSTALLIZATION                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│      PARTICLE                    WAVE                    OBSERVER           │
│    (Deterministic)           (Probabilistic)           (Governance)         │
│                                                                             │
│   ┌─────────────┐          ┌─────────────┐          ┌─────────────┐        │
│   │  COLLIDER   │────────► │     ACI     │ ◄────────│    BARE     │        │
│   │   (S1)      │          │    (S3)     │          │    (S6)     │        │
│   │             │          │             │          │             │        │
│   │  DEGRADED   │          │  STALE DATA │          │  BLOCKED    │        │
│   └─────────────┘          └─────────────┘          └─────────────┘        │
│         │                        │                        │                 │
│         │                        │                        │                 │
│         ▼                        ▼                        ▼                 │
│   ┌─────────────┐          ┌─────────────┐          ┌─────────────┐        │
│   │ Purpose     │          │ repo_truths │          │ Task        │        │
│   │ Field       │          │   .yaml     │          │ Registry    │        │
│   │             │          │             │          │   (S5)      │        │
│   │  NEVER RAN  │          │    STALE    │          │  ISOLATED   │        │
│   └─────────────┘          └─────────────┘          └─────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## EMERGENCY MAPS

| Map | Realm | Status | Critical Blocker |
|-----|-------|--------|------------------|
| [PARTICLE-COLLIDER-EMERGENCY-MAP.md](./PARTICLE-COLLIDER-EMERGENCY-MAP.md) | Particle | DEGRADED | tree-sitter broken |
| [WAVE-AI-SUBSYSTEM-EMERGENCY-MAP.md](./WAVE-AI-SUBSYSTEM-EMERGENCY-MAP.md) | Wave | CRITICAL | Daemons idle, stale data |
| [OBSERVER-GOVERNANCE-EMERGENCY-MAP.md](./OBSERVER-GOVERNANCE-EMERGENCY-MAP.md) | Observer | PARTIAL | S5→S6 gap (SG-004) |

---

## THE CASCADE

```
ROOT CAUSE: tree-sitter not installed
     │
     ▼
EFFECT 1: Collider can't parse code
     │
     ▼
EFFECT 2: unified_analysis.json empty/stale
     │
     ├─────────────────────────────────────┐
     ▼                                     ▼
EFFECT 3a: Purpose Field                 EFFECT 3b: Cartographer
   Stage 3.7 never runs                    can't update repo_truths
     │                                     │
     ▼                                     ▼
EFFECT 4: POM reports                    EFFECT 5: ACI reads
   coherence = 0.0                         stale truths
     │                                     │
     └─────────────────────────────────────┘
                     │
                     ▼
             EFFECT 6: AI answers
                based on old data
                     │
                     ▼
             EFFECT 7: User gets
                wrong information
```

---

## GLOBAL BLOCKERS (Priority Order)

| ID | Blocker | Impact | Realm | Fix Complexity |
|----|---------|--------|-------|----------------|
| B1 | tree-sitter not working | Everything downstream | Particle | LOW (pip install) |
| B2 | Daemons not running | No real-time updates | Wave | LOW (launchctl) |
| B3 | unified_analysis.json stale | No fresh data | Particle | MEDIUM (needs B1) |
| B4 | S5→S6 gap (SG-004) | No autonomous refinement | Observer | MEDIUM (interface) |
| B5 | Stage 3.7 never executed | No coherence metrics | Particle | LOW (needs B1) |

---

## RECOVERY SEQUENCE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RECOVERY SEQUENCE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   PHASE 1: FIX PARTICLE (Collider)                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ 1. Install tree-sitter: uv pip install tree-sitter tree-sitter-*   │  │
│   │ 2. Verify: uv run python -c "import tree_sitter"                    │  │
│   │ 3. Run Collider: ./pe collider full . --output .collider            │  │
│   │ 4. Verify nodes: Check unified_analysis.json has >2000 nodes        │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│   PHASE 2: FIX WAVE (AI Subsystem)                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ 1. Start daemons: launchctl load ~/Library/LaunchAgents/com.elem*  │  │
│   │ 2. Verify: launchctl list | grep element (should show PIDs)         │  │
│   │ 3. Trigger update: python tools/hsl_daemon.py --once                │  │
│   │ 4. Verify truths: Check repo_truths.yaml updated                    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│   PHASE 3: FIX OBSERVER (Governance)                                       │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ 1. Create S5 export interface: tasks_exporter.py                    │  │
│   │ 2. Update BARE to consume S5 export                                 │  │
│   │ 3. Test: Make change, verify BARE sees related tasks                │  │
│   │ 4. Enable post-commit hook for BARE                                 │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│   PHASE 4: VERIFY FULL LOOP                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ 1. Make a code change                                               │  │
│   │ 2. Verify: Collider updates (via daemon)                            │  │
│   │ 3. Verify: ACI gets fresh data                                      │  │
│   │ 4. Verify: BARE sees task relationship                              │  │
│   │ 5. Verify: Autonomous refinement suggested                          │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CONNECTIONS MATRIX

| From | To | Interface | Status |
|------|-----|-----------|--------|
| Collider (S1) | unified_analysis.json | File output | DEGRADED |
| unified_analysis.json | Purpose Field | JSON read | BLOCKED |
| unified_analysis.json | POM | JSON read | BLOCKED |
| unified_analysis.json | Laboratory Bridge (S9b) | JSON read | BLOCKED |
| Cartographer | repo_truths.yaml | YAML write | NOT RUNNING |
| repo_truths.yaml | ACI | YAML read | STALE |
| ACI | AI answers | Model call | WORKING (bad input) |
| Task Registry (S5) | BARE (S6) | ??? | MISSING |
| BARE (S6) | Task Registry (S5) | ??? | MISSING |
| Hygiene (S8) | Git commits | Hooks | WORKING |
| Macro Registry (S13) | ??? | ??? | NOT CONNECTED |

---

## SUCCESS STATE

When everything works:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUCCESS STATE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Developer edits code                                                      │
│         │                                                                   │
│         ▼                                                                   │
│   File watcher detects (within 15 seconds)                                  │
│         │                                                                   │
│         ▼                                                                   │
│   Collider re-analyzes (tree-sitter working)                               │
│         │                                                                   │
│         ▼                                                                   │
│   unified_analysis.json updated                                             │
│         │                                                                   │
│         ├──────────────────────────────────────────────┐                   │
│         ▼                                              ▼                    │
│   Cartographer updates                          Purpose Field               │
│   repo_truths.yaml                              Stage 3.7 runs              │
│         │                                              │                    │
│         ▼                                              ▼                    │
│   ACI gets fresh facts                          POM gets coherence > 0     │
│         │                                              │                    │
│         ▼                                              │                    │
│   AI answers are accurate                              │                    │
│                                                        │                    │
│   Developer commits                                    │                    │
│         │                                              │                    │
│         ▼                                              │                    │
│   BARE (S6) triggers                                   │                    │
│         │                                              │                    │
│         ▼                                              │                    │
│   BARE reads Task Registry (S5)                        │                    │
│         │                                              │                    │
│         ▼                                              │                    │
│   BARE matches changes to tasks                        │                    │
│         │                                              │                    │
│         ▼                                              │                    │
│   Auto-suggests refinements                            │                    │
│         │                                              │                    │
│         ▼                                              │                    │
│   Pattern recorded in Macro Registry (S13)             │                    │
│                                                        │                    │
│   ◄──────────────── LOOP CLOSES ──────────────────────┘                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## QUICK VERIFICATION COMMANDS

```bash
# === PARTICLE ===
# Check tree-sitter
cd ~/PROJECTS_all/PROJECT_elements/standard-model-of-code
uv run python -c "import tree_sitter; print('OK')"

# Check Collider output
ls -la .collider/unified_analysis.json

# Check nodes count
python3 -c "import json; print(len(json.load(open('.collider/unified_analysis.json')).get('nodes',[])))"

# === WAVE ===
# Check daemons
launchctl list | grep element

# Check truths freshness
head -5 .agent/intelligence/truths/repo_truths.yaml

# Check activity log
tail -10 /tmp/elements_activity_watcher.log

# === OBSERVER ===
# Check task count
echo "Active: $(ls .agent/registry/active/*.yaml 2>/dev/null | wc -l)"

# Check hooks
cat .git/hooks/pre-commit | head -5
```

---

## TIMESTAMP

```
Crystallization completed: 2026-01-26
Maps created: 3
Total blockers identified: 5
Recovery phases: 4
Estimated fix time: 2-4 hours
```

---

*This index will be updated as emergency maps are resolved.*
