# WAVE AI SUBSYSTEM - EMERGENCY MAP

> **Status:** CRITICAL - Infrastructure exists but disconnected
> **Created:** 2026-01-26
> **Author:** Claude Opus 4.5 (onboarding diagnostic)
> **Confidence:** HIGH (verified via process checks, file reads, log inspection)

---

## EXECUTIVE SUMMARY

The AI subsystem (Wave realm) has sophisticated infrastructure that is **built but not running**. Real-time context was designed but operates in stale batch mode. The user experiences this as: AI answers based on old data without knowing it's old.

```
SEVERITY: CRITICAL
IMPACT:   AI queries return stale/incomplete information
ROOT:     Daemons idle + tree-sitter broken + no feedback loop
```

---

## 1. COMPONENT STATUS MATRIX

| Component | Location | Designed For | Actual State | Blocker |
|-----------|----------|--------------|--------------|---------|
| **hsl-daemon** | launchd | Real-time file watching | IDLE (PID: -) | Not started |
| **socratic-audit** | launchd | Continuous validation | IDLE (PID: -) | Not started |
| **activity_watcher.py** | tools/ | Debounced change detection | NOT RUNNING | No daemon trigger |
| **continuous_cartographer.py** | tools/ | "Never >15s behind" | NOT RUNNING | No daemon trigger |
| **repo_truths.yaml** | .agent/intelligence/ | Live fact cache | STALE | No updater running |
| **unified_analysis.json** | .collider/ | Fresh semantic graph | STALE/EMPTY | tree-sitter broken |
| **ACI (Adaptive Context)** | tools/ai/aci/ | Smart query routing | WORKING but reads stale data | Upstream stale |
| **analyze.py** | tools/ai/ | AI queries | WORKING | Reads stale context |
| **laboratory_bridge.py** | tools/ai/ | Wave→Particle bridge | WORKING | Collider broken |

---

## 2. LAUNCHD DAEMON STATUS

```bash
$ launchctl list | grep element
-    0    com.elements.hsl
-    0    com.elements.hsl-daemon
-    0    com.elements.socratic-audit
```

**Legend:** First column is PID. `-` means NOT RUNNING.

### Daemon Configurations

| Daemon | Plist Location | Trigger | Payload |
|--------|----------------|---------|---------|
| hsl-daemon | ~/Library/LaunchAgents/com.elements.hsl-daemon.plist | WatchPaths (file changes) | activity_watcher.py → hsl_daemon.py |
| socratic-audit | ~/Library/LaunchAgents/com.elements.socratic-audit.plist | WatchPaths | activity_watcher.py → audit |
| hsl | ~/Library/LaunchAgents/com.elements.hsl.plist | Unknown | Unknown |

### Last Known Activity

```
hsl_daemon_state.json:
{
  "audit_count": 643,           // HAS worked in the past
  "violation_count": 4,
  "updated": "2026-01-26T02:51:52"  // ~30 mins before diagnostic
}

activity_watcher.log (last entries):
[2026-01-26 03:06:50] hsl-daemon: Changes this poll: 2, Total: 2
[2026-01-26 03:06:51] socratic-audit: Changes this poll: 0, Total: 2
(then silence)
```

---

## 3. DATA FLOW ANALYSIS

### DESIGNED Flow (Real-Time)

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ File Change  │───►│ WatchPaths   │───►│ Activity     │───►│ Cartographer │
│ (user edits) │    │ (launchd)    │    │ Watcher      │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                   │
                                                                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ AI Answer    │◄───│ ACI Router   │◄───│ repo_truths  │◄───│ unified_     │
│ (fresh)      │    │              │    │ .yaml        │    │ analysis.json│
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
        │                                                          │
        └────────────── <15 second latency ────────────────────────┘
```

### ACTUAL Flow (Broken)

```
┌──────────────┐    ┌──────────────┐
│ File Change  │───►│ WatchPaths   │───► (daemon not running, nothing happens)
│ (user edits) │    │ (launchd)    │
└──────────────┘    └──────────────┘

                    ┌──────────────┐    ┌──────────────┐
                    │ repo_truths  │◄───│ unified_     │
                    │ .yaml        │    │ analysis.json│
                    │ (STALE)      │    │ (STALE/EMPTY)│
                    └──────────────┘    └──────────────┘
                           │
                           ▼
┌──────────────┐    ┌──────────────┐
│ AI Answer    │◄───│ ACI Router   │
│ (based on    │    │ (working but │
│  OLD data)   │    │  fed garbage)│
└──────────────┘    └──────────────┘
```

---

## 4. DEPENDENCY GRAPH

```
                    ┌─────────────────┐
                    │   tree-sitter   │ ◄── BROKEN (Python bindings)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Collider     │ ◄── DEGRADED (can't parse)
                    │    (S1)         │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ unified_analysis│ ◄── STALE/EMPTY
                    │     .json       │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
     │ Purpose     │  │ laboratory  │  │ Cartographer│
     │ Field       │  │ _bridge.py  │  │             │
     │ Stage 3.7   │  └─────────────┘  └──────┬──────┘
     └──────┬──────┘                          │
            │                                 ▼
            │                        ┌─────────────┐
            │                        │ repo_truths │ ◄── STALE
            │                        │   .yaml     │
            │                        └──────┬──────┘
            │                               │
            │                               ▼
            │                        ┌─────────────┐
            └───────────────────────►│    ACI      │
                                     │  (analyze)  │
                                     └──────┬──────┘
                                            │
                                            ▼
                                     ┌─────────────┐
                                     │  AI Answer  │ ◄── UNRELIABLE
                                     └─────────────┘
```

---

## 5. BLOCKERS (Priority Order)

### B1: tree-sitter Not Working [CRITICAL]

**Impact:** Collider cannot parse source code
**Symptom:** `./pe collider full` produces empty/minimal output
**Location:** Python tree-sitter bindings
**Fix:**
```bash
pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript
# or
uv pip install tree-sitter tree-sitter-languages
```

### B2: Daemons Not Running [CRITICAL]

**Impact:** No real-time updates happen
**Symptom:** PID shows `-` in launchctl
**Fix:**
```bash
launchctl load ~/Library/LaunchAgents/com.elements.hsl-daemon.plist
launchctl load ~/Library/LaunchAgents/com.elements.socratic-audit.plist
launchctl start com.elements.hsl-daemon
launchctl start com.elements.socratic-audit
```

### B3: unified_analysis.json Stale/Empty [HIGH]

**Impact:** All downstream consumers get no data
**Symptom:** POM reports `coherence = 0.0`
**Depends on:** B1 (tree-sitter)
**Fix:** Once B1 fixed:
```bash
./pe collider full . --output .collider
```

### B4: repo_truths.yaml Not Auto-Updated [HIGH]

**Impact:** ACI Tier 0 (instant) returns stale facts
**Depends on:** B2 (daemons), B3 (unified_analysis)
**Fix:** Daemons should update this, or manual:
```bash
python context-management/tools/hsl_daemon.py --once
```

### B5: Stage 3.7 Never Executed [MEDIUM]

**Impact:** Purpose coherence metrics not exported
**Symptom:** Code exists but `coherence_score` fields empty
**Depends on:** B1 (tree-sitter)
**Location:** `standard-model-of-code/src/core/full_analysis.py:1599-1629`

---

## 6. VERIFICATION COMMANDS

```bash
# Check daemon status
launchctl list | grep element

# Check if processes running
ps aux | grep -E "activity_watcher|hsl_daemon|cartographer" | grep -v grep

# Check last activity
cat /tmp/elements_activity_watcher.log | tail -20

# Check daemon state
cat context-management/intelligence/hsl_daemon_state.json

# Check truths freshness
head -20 .agent/intelligence/truths/repo_truths.yaml

# Check unified_analysis exists and has data
python3 -c "import json; d=json.load(open('.collider/unified_analysis.json')); print(f'Nodes: {len(d.get(\"nodes\",[]))}')" 2>/dev/null || echo "No unified_analysis.json"

# Test tree-sitter
python3 -c "import tree_sitter; print('tree-sitter OK')" 2>&1
```

---

## 7. RECOVERY PROCEDURE

### Phase 1: Fix tree-sitter (Unblocks Collider)

```bash
cd ~/PROJECTS_all/PROJECT_elements/standard-model-of-code
uv pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-typescript tree-sitter-go tree-sitter-rust

# Verify
uv run python -c "import tree_sitter; print('OK')"
```

### Phase 2: Regenerate unified_analysis.json

```bash
cd ~/PROJECTS_all/PROJECT_elements
./pe collider full . --output .collider

# Verify
python3 -c "import json; d=json.load(open('.collider/unified_analysis.json')); print(f'Nodes: {len(d[\"nodes\"])}')"
```

### Phase 3: Start Daemons

```bash
launchctl load ~/Library/LaunchAgents/com.elements.hsl-daemon.plist
launchctl load ~/Library/LaunchAgents/com.elements.socratic-audit.plist

# Verify
launchctl list | grep element
# Should show PIDs, not "-"
```

### Phase 4: Verify Real-Time Flow

```bash
# Make a file change
touch standard-model-of-code/src/core/purpose_field.py

# Wait 30 seconds, check log
sleep 30 && tail -5 /tmp/elements_activity_watcher.log

# Check truths updated
cat .agent/intelligence/truths/repo_truths.yaml | grep version
```

### Phase 5: Verify AI Answers Fresh

```bash
python context-management/tools/ai/analyze.py --aci "how many Python files in the repo"
# Should return current count, not stale
```

---

## 8. SUCCESS CRITERIA

| Metric | Current | Target |
|--------|---------|--------|
| Daemons running | 0/3 | 3/3 |
| unified_analysis.json nodes | 0 or stale | >1000 |
| repo_truths.yaml age | Unknown/stale | <5 minutes |
| coherence_score populated | NO | YES |
| ACI Tier 0 latency | N/A (stale) | <100ms with fresh data |

---

## 9. RELATED DOCUMENTS

| Document | Purpose |
|----------|---------|
| `.agent/handoffs/HANDOFF_2026-01-26_PURPOSE_FIELD_SESSION.md` | Previous session findings |
| `.agent/intelligence/TOOLS_REGISTRY.yaml` | Component interfaces |
| `context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md` | HSL design |
| `standard-model-of-code/docs/COLLIDER.md` | Collider usage |

---

## 10. OWNER & NEXT ACTION

**Owner:** Unassigned
**Next Action:** Fix tree-sitter (B1), then cascade fixes
**Estimated Effort:** 1-2 hours for full recovery
**Risk if Unfixed:** AI subsystem continues returning stale/wrong information

---

*This emergency map will be updated as fixes are applied.*
