# BACKGROUND SERVICES - EMERGENCY MAP

> **Status:** FRAGMENTED - Some running, most idle, poor coordination
> **Created:** 2026-01-26
> **Author:** Claude Opus 4.5 (system crystallization)
> **Scope:** All launchd services across PROJECT_elements and PROJECT_sentinel

---

## EXECUTIVE SUMMARY

Background services are the **autonomic nervous system** - they should sense, react, and maintain without human intervention. Currently **11 services registered**, only **3 running**, and they don't coordinate with each other.

```
SEVERITY: HIGH
IMPACT:   No autonomous maintenance, manual intervention required
ROOT:     Services not started + no inter-service communication
```

---

## 1. SERVICE INVENTORY (Live Status)

```bash
$ launchctl list | grep -E "element|sentinel|claude|central|uiresearch|lech"
```

| Service | PID | Exit | Status | Owner |
|---------|-----|------|--------|-------|
| com.elements.hsl | - | -9 | **CRASHED** | elements |
| com.elements.hsl-daemon | - | 0 | IDLE | elements |
| com.elements.socratic-audit | 87559 | 0 | **RUNNING** | elements |
| com.central-mcp.midnight-day-close | - | 0 | IDLE | central-mcp |
| com.claude.activity-monitor | 858 | 0 | **RUNNING** | claude |
| com.claude.orphan-watcher | - | 0 | IDLE | claude |
| com.claude.workspace-sync | - | 0 | IDLE | claude |
| com.lech.claude-backup | - | 0 | IDLE | lech |
| com.uiresearch.multicloud.sync | - | 0 | IDLE | uiresearch |
| com.uiresearch.vaultsystem | 89043 | 0 | **RUNNING** | uiresearch |

### Status Legend

```
PID = Process ID (number = running, "-" = not running)
Exit = Last exit code (-9 = killed/crashed, 0 = clean exit)
```

### Summary

| State | Count | Services |
|-------|-------|----------|
| **RUNNING** | 3 | socratic-audit, activity-monitor, vaultsystem |
| **IDLE** | 7 | hsl-daemon, midnight-day-close, orphan-watcher, workspace-sync, claude-backup, multicloud.sync |
| **CRASHED** | 1 | hsl (exit -9) |

---

## 2. SERVICE DETAIL: PROJECT_elements

### com.elements.hsl-daemon

```yaml
Purpose: Watch for file changes, trigger HSL validation
Status: IDLE
Plist: ~/Library/LaunchAgents/com.elements.hsl-daemon.plist
       → symlink to PROJECT_sentinel/agents/

Trigger:
  WatchPaths:
    - context-management/config/semantic_models.yaml
    - standard-model-of-code/src/core/

Payload:
  activity_watcher.py
    --daemon hsl-daemon
    --watch-paths [config, src/core]
    --poll-interval 300      # 5 min
    --watch-window 1800      # 30 min
    --min-changes 2
    --on-activity → hsl_daemon.py --once

Throttle: 300 seconds (5 min)
KeepAlive: false
```

### com.elements.socratic-audit

```yaml
Purpose: Run AI verification on code changes
Status: RUNNING (PID 87559)
Plist: ~/Library/LaunchAgents/com.elements.socratic-audit.plist
       → symlink to PROJECT_sentinel/agents/

Trigger:
  WatchPaths:
    - context-management/config/semantic_models.yaml
    - standard-model-of-code/src/core/

Payload:
  activity_watcher.py
    --daemon socratic-audit
    --on-activity → analyze.py --verify pipeline

Output: context-management/reports/socratic_audit_latest.md

Throttle: 300 seconds (5 min)
RunAtLoad: false
```

### com.elements.hsl

```yaml
Purpose: Unknown (possibly legacy)
Status: CRASHED (exit -9)
Plist: ~/Library/LaunchAgents/com.elements.hsl.plist
       → NOT a symlink (local file)

Issue: Exit code -9 = SIGKILL (killed by system or OOM)
```

---

## 3. SERVICE DETAIL: PROJECT_sentinel

All symlinked from `~/PROJECTS_all/PROJECT_sentinel/agents/`

### com.claude.activity-monitor

```yaml
Purpose: Monitor Claude Code CLI activity
Status: RUNNING (PID 858)
Owner: sentinel
```

### com.claude.orphan-watcher

```yaml
Purpose: Watch for orphaned Claude processes
Status: IDLE
Owner: sentinel
```

### com.claude.workspace-sync

```yaml
Purpose: Sync Claude workspace state
Status: IDLE
Owner: sentinel
```

### com.lech.claude-backup

```yaml
Purpose: Backup Claude history
Status: IDLE
Owner: sentinel
```

### com.central-mcp.midnight-day-close

```yaml
Purpose: End-of-day processing for central-mcp
Status: IDLE
Note: central-mcp is DEPRECATED (resource only)
```

### com.uiresearch.multicloud.sync

```yaml
Purpose: Multi-cloud synchronization
Status: IDLE
Owner: sentinel
```

### com.uiresearch.vaultsystem

```yaml
Purpose: Vault/secrets management
Status: RUNNING (PID 89043)
Owner: sentinel
```

---

## 4. TOOLS CATEGORIZATION (SMoC Ontology)

From `BACKGROUND_SERVICES_ONTOLOGY.md` - tools mapped to 33 canonical roles:

### By Role

| Role | Tools | Purpose |
|------|-------|---------|
| **Loader** | FactLoader (truth_validator.py) | Load data from source |
| **Store** | TaskStore, FeedbackStore | Manage state |
| **Cache** | ContextCache | Performance caching |
| **Validator** | ConfidenceValidator, ChunkValidator | Verify constraints |
| **Guard** | DriftGuard (hsl_daemon.py) | Protect/enforce |
| **Parser** | IntentParser, ChunkParser | Parse input |
| **Finder** | SemanticFinder, ChunkFinder | Search data |
| **Builder** | ContextBuilder | Construct objects |
| **Orchestrator** | TierOrchestrator, ResearchOrchestrator, EnrichmentOrchestrator | Coordinate workflows |

### By Subsystem

```
S2: HSL
└── DriftGuard [Guard]

S3: ACI
├── IntentParser [Parser]
├── SemanticFinder [Finder]
├── TierOrchestrator [Orchestrator]
├── ContextBuilder [Builder]
├── ContextCache [Cache]
├── ChunkParser [Parser]
├── ChunkValidator [Validator]
├── ChunkFinder [Finder]
├── ResearchOrchestrator [Orchestrator]
└── FeedbackStore [Store]

S6: BARE
├── FactLoader [Loader]
├── ConfidenceValidator [Validator]
└── TaskStore [Store]

Cross-Subsystem:
└── EnrichmentOrchestrator [Orchestrator]
```

---

## 5. DEPENDENCY GRAPH

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BACKGROUND SERVICE DEPENDENCIES                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FILE CHANGES                                                              │
│        │                                                                    │
│        ▼                                                                    │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    launchd WatchPaths                                │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│        │                              │                                     │
│        ▼                              ▼                                     │
│   ┌─────────────┐              ┌─────────────┐                             │
│   │ hsl-daemon  │              │ socratic-   │                             │
│   │ (IDLE)      │              │ audit       │                             │
│   │             │              │ (RUNNING)   │                             │
│   └──────┬──────┘              └──────┬──────┘                             │
│          │                            │                                     │
│          ▼                            ▼                                     │
│   ┌─────────────┐              ┌─────────────┐                             │
│   │ activity_   │              │ activity_   │                             │
│   │ watcher.py  │              │ watcher.py  │                             │
│   └──────┬──────┘              └──────┬──────┘                             │
│          │                            │                                     │
│          │ (if sustained)             │ (if sustained)                      │
│          ▼                            ▼                                     │
│   ┌─────────────┐              ┌─────────────┐                             │
│   │ hsl_daemon  │              │ analyze.py  │                             │
│   │ .py --once  │              │ --verify    │                             │
│   └──────┬──────┘              └──────┬──────┘                             │
│          │                            │                                     │
│          ▼                            ▼                                     │
│   ┌─────────────┐              ┌─────────────┐                             │
│   │ DriftGuard  │              │ Socratic    │                             │
│   │ validation  │              │ audit       │                             │
│   └─────────────┘              │ report      │                             │
│                                └─────────────┘                             │
│                                                                             │
│   MISSING CONNECTIONS:                                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ hsl-daemon ──✗──► BARE (S6)     No task awareness                   │  │
│   │ socratic-audit ──✗──► TaskStore  Results not stored                 │  │
│   │ activity-monitor ──✗──► anything  Just monitors, doesn't act        │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. INTER-SERVICE COMMUNICATION (MISSING)

### What Should Exist

```
Service A detects event
     │
     ▼
Service A emits message to bus/file
     │
     ▼
Service B subscribes to message type
     │
     ▼
Service B takes action
```

### What Actually Exists

```
Service A detects event
     │
     ▼
Service A does its thing
     │
     ▼
∅ (nothing else happens)
```

### Proposed Communication Patterns

| Pattern | Mechanism | Example |
|---------|-----------|---------|
| File-based | Write to shared JSON/YAML | `daemon_state.json` |
| Event bus | Redis/SQLite pub/sub | Too complex for now |
| Sequential | Output of A is input of B | Current (but not wired) |

---

## 7. LOGS & STATE FILES

### Log Locations

| Service | stdout | stderr |
|---------|--------|--------|
| hsl-daemon | `context-management/intelligence/logs/hsl_daemon_stdout.log` | `...stderr.log` |
| socratic-audit | `PROJECT_sentinel/logs/socratic-audit.out.log` | `...err.log` |
| activity_watcher | `/tmp/elements_activity_watcher.log` | (same) |

### State Files

| File | Purpose | Location |
|------|---------|----------|
| `hsl_daemon_state.json` | Audit counts, violations | `context-management/intelligence/` |
| `trigger_state.yaml` | Macro trigger state | `.agent/macros/` |
| `circuit_breakers.yaml` | Service health | `.agent/state/` |

---

## 8. BLOCKERS

### B1: Most Services Idle

```
7 of 11 services not running
Root cause: Not started / not configured for RunAtLoad
```

### B2: hsl Crashed (exit -9)

```
com.elements.hsl exited with -9 (SIGKILL)
Needs investigation - memory issue? infinite loop?
```

### B3: No Inter-Service Communication

```
Services operate in silos
No shared state, no event bus, no coordination
```

### B4: Duplicate Purpose

```
hsl vs hsl-daemon - what's the difference?
Both seem to do HSL validation
```

### B5: Stale Outputs

```
Services that DO run produce outputs that nothing reads
Example: socratic_audit_latest.md sits unused
```

---

## 9. RECOVERY PROCEDURE

### Phase 1: Start Essential Services

```bash
# Start hsl-daemon
launchctl load ~/Library/LaunchAgents/com.elements.hsl-daemon.plist
launchctl start com.elements.hsl-daemon

# Verify
launchctl list | grep hsl-daemon
# Should show PID instead of "-"
```

### Phase 2: Investigate Crashed Service

```bash
# Check hsl logs
cat ~/Library/Logs/com.elements.hsl.* 2>/dev/null
# Or system logs
log show --predicate 'senderImagePath CONTAINS "hsl"' --last 1h

# If corrupted, unload and reload
launchctl unload ~/Library/LaunchAgents/com.elements.hsl.plist
# Fix plist if needed
launchctl load ~/Library/LaunchAgents/com.elements.hsl.plist
```

### Phase 3: Wire Service Outputs

```bash
# Example: Make socratic-audit output trigger BARE
# In socratic-audit plist, add post-action:
# --on-complete "python .agent/tools/bare_trigger.py"
```

### Phase 4: Add Health Monitoring

```bash
# Create health check script
# Runs periodically, restarts crashed services
# Updates circuit_breakers.yaml
```

---

## 10. SUCCESS CRITERIA

| Metric | Current | Target |
|--------|---------|--------|
| Services running | 3/11 | 8/11 (exclude deprecated) |
| Services crashed | 1 | 0 |
| Inter-service links | 0 | 3+ |
| Output consumed | ~0% | >80% |
| Auto-recovery | NO | YES |

---

## 11. SERVICE CATEGORIES

### By Purpose

| Category | Services | Status |
|----------|----------|--------|
| **Code Analysis** | hsl-daemon, socratic-audit, hsl | 1 running, 1 idle, 1 crashed |
| **Claude/AI Management** | activity-monitor, orphan-watcher, workspace-sync, claude-backup | 1 running, 3 idle |
| **Infrastructure** | vaultsystem, multicloud.sync | 1 running, 1 idle |
| **Legacy/Deprecated** | midnight-day-close | idle (should disable) |

### By Owner Project

| Project | Services | Running |
|---------|----------|---------|
| PROJECT_elements | 3 | 1 |
| PROJECT_sentinel | 7 | 2 |
| PROJECT_central-mcp | 1 | 0 (deprecated) |

---

## 12. TOOL REGISTRY INTEGRATION

These services should be registered in `TOOLS_REGISTRY.yaml`:

```yaml
background_services:
  - id: BG001
    name: hsl-daemon
    invoke: launchctl start com.elements.hsl-daemon
    status: idle
    outputs: [hsl_daemon_state.json]

  - id: BG002
    name: socratic-audit
    invoke: launchctl start com.elements.socratic-audit
    status: running
    outputs: [socratic_audit_latest.md]

  # ... etc
```

---

## 13. RELATED EMERGENCY MAPS

| Map | Relationship |
|-----|--------------|
| `WAVE-AI-SUBSYSTEM-EMERGENCY-MAP.md` | Daemons feed Wave with fresh data |
| `OBSERVER-GOVERNANCE-EMERGENCY-MAP.md` | BARE should be triggered by services |

---

*Background services are the heartbeat. They need to beat together.*
