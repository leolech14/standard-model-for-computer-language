# When You Return - Palace Status Report
**Purpose:** What to expect and how to access your knowledge library
**Updated:** 2026-01-27

---

## WHAT TO EXPECT WHEN YOU COME BACK

### The Palace Maintained Itself

While you were away, 26 butlers kept everything tidy:

```
Filesystem Watcher (if files changed)
    ↓
Detected changes → Waited 5 minutes → Ran wire.py
    ↓
Generated fresh chunks, recorded metrics, updated state
    ↓
Everything validated, timestamped, ready

Cloud Schedulers (4x daily: 00, 06, 12, 18 UTC)
    ↓
Ran socratic-audit-job → Analyzed codebase → Uploaded results
    ↓
Cloud intelligence accumulated

Post-Commit Hooks (if commits happened)
    ↓
Autopilot orchestrated → Enrichment ran → Fabric recorded
    ↓
Task confidence updated, opportunities scored

Background Daemons (LaunchAgents)
    ↓
File watcher monitored, HSL checked health hourly
    ↓
Continuous monitoring maintained
```

**Result:** Knowledge is FRESH, VALIDATED, READY.

---

## FIRST COMMAND WHEN YOU RETURN

```bash
./pe refinery report
```

**Shows:**
```
╔════════════════════════════════════════════════════════════════════╗
║                    REFINERY ACTIVITY REPORT                        ║
╚════════════════════════════════════════════════════════════════════╝

## CURRENT STATUS
  Last Updated: 2h ago (Git SHA: 8bd0ceb9)
  Total Chunks: 2,673
  Total Tokens: 539,176

## ACTIVITY LOG (Recent)
  File changes detected: 3
  Wire pipeline runs: 2

  Last 3 wire runs:
    [14:23] Wire completed successfully
    [16:45] Wire completed successfully
    [18:12] Wire completed successfully

## KNOWLEDGE LIBRARY
  Total entries: 2,673

  By chunk type:
    function               699 ( 26.2%)
    h3                     680 ( 25.4%)
    h2                     522 ( 19.5%)
    h1                     318 ( 11.9%)
    class                  253 (  9.5%)
    imports                151 (  5.7%)

## COMMANDS
  ./pe refinery search <query>   # Search knowledge
  ./pe refinery library          # Full library view
  ./pe refinery chunks           # Metadata

╚════================================================================╝
```

**This tells you:**
- How fresh the knowledge is
- What changed while you were gone
- How many updates ran
- What's in the library

---

## ACCESSING THE KNOWLEDGE LIBRARY

### Quick Search (Most Common)
```bash
./pe refinery search "Communication Fabric"
```

**Returns:**
```
Found 3 matches for: 'Communication Fabric'

1. [.agent/tools/autopilot.py:445]
   Type: function
   Relevance: 0.98 | Matches: 6
   Preview: ...Step 3: Communication Fabric - Recording state vector...

2. [.agent/tools/wire.py:178]
   Type: function
   Relevance: 0.98 | Matches: 3
   Preview: ...Communication Fabric metrics...

3. [.agent/tools/autopilot.py:308]
   Type: function
   Relevance: 0.95 | Matches: 3
   Preview: ...Record Communication Fabric state vector...
```

**Use cases:**
- "Where is X implemented?"
- "Show me examples of Y"
- "Find all references to Z"

---

### Library View (Browse by File)
```bash
./pe refinery library
```

**Returns:**
```
Top 20 Files by Chunk Count (of 234 total):

  1. .agent/intelligence/comm_analysis/COMMUNICATION_FABRIC_RESEARCH_SYNTHESIS.md
      Chunks: 45 | Tokens: ~12,340
      Types: 28 h3, 12 h2, 5 h1

  2. .agent/tools/autopilot.py
      Chunks: 23 | Tokens: ~5,890
      Types: 23 function

  3. .agent/tools/wire.py
      Chunks: 8 | Tokens: ~2,100
      Types: 8 function

  ... (17 more)

Total: 2,673 chunks across 234 files
```

**Use cases:**
- "What files have the most knowledge?"
- "Browse by module"
- "Understand knowledge distribution"

---

### Chunk Metadata (Quick Stats)
```bash
./pe refinery chunks
```

**Returns:**
```
Generated: 2026-01-27T06:26:55
Git SHA: c913e631...
Total chunks: 2,673
Total tokens: 539,176
```

**Use cases:**
- "Is knowledge fresh?"
- "What git version?"
- "Quick size check"

---

### Recent Changes (Activity Log)
```bash
./pe refinery changes
```

**Returns:**
```
REFINERY RECENT ACTIVITY

Last 10 events from filesystem watcher:
  [14:23] File changes detected, starting quiet period...
  [14:28] Quiet for 300s, running wire...
  [14:29] Wire completed successfully
  [16:42] File changes detected, starting quiet period...
  [16:47] Quiet for 300s, running wire...
  [16:48] Wire completed successfully

Last chunk regeneration: 2h ago
Git SHA: 8bd0ceb9
```

**Use cases:**
- "What happened while I was away?"
- "Did the watcher work?"
- "When did refinery last run?"

---

### Full Corpus State
```bash
./pe refinery stats
```

**Returns:**
```
Synthesizing global state...

State Synthesis Complete:
  Files:       2,899
  Boundaries:  38
  Atoms:       295
  Changes:     14 pending
  Health:      All fresh
```

**Use cases:**
- "Complete system overview"
- "How many files tracked?"
- "Boundary structure"

---

## THE ORGANIZED LIBRARY

### Structure

```
.agent/intelligence/chunks/
├── agent_chunks.json      1,967 chunks from .agent/
│   ├── Tools (autopilot, wire, enrichment)
│   ├── Intelligence (LOL, comm_analysis, triage_reports)
│   ├── Registry (tasks, opportunities, inbox)
│   ├── Specs (subsystems, schemas, roadmaps)
│   └── State (autopilot_state, circuit_breakers)
│
├── core_chunks.json       598 chunks from Collider core
│   ├── Pipeline (full_analysis, stages)
│   ├── Analysis (graph_metrics, topology_reasoning)
│   ├── Graph (edge_extractor, graph_analyzer)
│   └── Viz (visualization assets)
│
├── aci_chunks.json        108 chunks from ACI tools
│   ├── Research (orchestrator, schemas)
│   ├── Refinery (this system)
│   ├── Tier Router (context routing)
│   └── Feedback Store
│
└── metadata.json          Generation metadata
    ├── timestamp (when generated)
    ├── git_sha (code version)
    └── stats (chunk/token counts per module)
```

### Access Patterns

**By Location:**
```bash
# Find chunks from specific module
./pe refinery search ".agent/tools/autopilot"
→ Returns all chunks from autopilot.py

# Find chunks from specific type
./pe refinery library
→ Browse by file, see types
```

**By Content:**
```bash
# Semantic search
./pe refinery search "how to add a butler"
→ Searches ALL chunks for relevant code/docs

# Topic search
./pe refinery search "pipeline stages"
→ Finds chunks discussing pipeline
```

**By Type:**
```bash
# (Future) Filter by chunk type
./pe refinery search "function" --type function
./pe refinery search "class" --type class
```

---

## WHAT THE LIBRARY CONTAINS

### From .agent/ (1,967 chunks):
- **Butlers:** autopilot, wire, trigger_engine, enrichment, etc.
- **Intelligence:** LOL, Communication Fabric, triage reports
- **Decisions:** Decision Deck cards, task registry
- **State:** Circuit breakers, autopilot state, meters
- **Specs:** Subsystem docs, schemas, roadmaps

### From Collider Core (598 chunks):
- **Pipeline:** full_analysis, stages, manager
- **Analysis:** graph_metrics, topology_reasoning
- **Extractors:** edge_extractor, intent_extractor
- **Graph:** graph_analyzer, centrality calculations

### From ACI (108 chunks):
- **Research:** Orchestrator, tier router, schemas
- **Refinery:** This knowledge consolidation system
- **Feedback:** Store, cache, context management
- **Routing:** Tier selection, ACI intelligence

---

## HOW TO READ THE LIBRARY

### Scenario 1: "Show me everything about X"
```bash
./pe refinery search "Communication Fabric" --limit 10 --context
```
- Returns: Top 10 chunks with FULL CONTENT
- Shows: Where it's implemented, discussed, documented

### Scenario 2: "What files should I read?"
```bash
./pe refinery library
```
- Returns: Files ranked by chunk count (most knowledge)
- Top file = most important for understanding

### Scenario 3: "What changed?"
```bash
./pe refinery changes
```
- Returns: Activity log (file changes, wire runs)
- Shows: What the watcher did

### Scenario 4: "Is knowledge fresh?"
```bash
./pe refinery chunks
```
- Returns: Metadata (timestamp, git SHA)
- Quick freshness check

---

## THE COMPLETE WORKFLOW

### When You Return:

**Step 1: Check Palace Status**
```bash
./pe status
```
Shows: Git, autopilot, TDJ summary

**Step 2: Check Refinery Activity**
```bash
./pe refinery report
```
Shows: What happened while away, knowledge freshness, library stats

**Step 3: Query Specific Knowledge**
```bash
./pe refinery search "your topic"
```
Returns: Relevant chunks instantly

**Step 4: Browse Library (Optional)**
```bash
./pe refinery library
```
Browse: All knowledge organized by file

**Step 5: Start Work**
With complete, fresh, organized knowledge at your fingertips.

---

## WHAT YOU'LL SEE (Examples)

### If Files Changed While Away:
```
Last Updated: 2h ago
Wire pipeline runs: 4
Result: Knowledge regenerated 4 times, stayed fresh
```

### If No Changes:
```
Last Updated: 12h ago (still current)
Wire pipeline runs: 0
Result: Knowledge converged, no wasteful re-processing
```

### If Watcher Had Issues:
```
Activity LOG: No activity logged (watcher may not be running)
Action: Restart with: screen -dmS watcher python3 .agent/tools/filesystem_watcher.py
```

---

## THE LIBRARY AS ORGANIZED KNOWLEDGE

**Think of it as:**

### Dewey Decimal System for Code
- agent_chunks.json = 000-099 (Automation & Orchestration)
- core_chunks.json = 100-199 (Analysis & Theory)
- aci_chunks.json = 200-299 (AI & Context)

### Table of Contents
```
metadata.json = Card catalog (where everything is)
query_chunks.py = Search engine (find by topic)
refinery_report.py = Librarian (organized views)
state_synthesizer.py = Inventory (complete catalog)
```

### Access Methods
- **Search:** Quick lookup by keyword
- **Library:** Browse by file/module
- **Report:** Activity summary
- **Stats:** Complete inventory

---

## HEALTH CHECKS

### Is Refinery Working?
```bash
./pe refinery chunks
# Should show: Generated within last few hours
```

### Is Watcher Running?
```bash
ps aux | grep filesystem_watcher
# Should show: Process active

screen -list
# Should show: watcher (Detached)
```

### Is Knowledge Fresh?
```bash
./pe refinery report
# Check: "Last Updated" should be recent
```

### Can I Query?
```bash
./pe refinery search "test query"
# Should return: Results in <1s
```

---

## IF SOMETHING BROKE WHILE AWAY

### Watcher Not Running:
```bash
screen -dmS watcher python3 .agent/tools/filesystem_watcher.py
```

### Chunks Stale:
```bash
./pe wire --quick
# Regenerates chunks immediately
```

### Knowledge Corrupted (Unlikely - Validation Prevents This):
```bash
# Delete chunks, regenerate
rm .agent/intelligence/chunks/*.json
./pe wire
```

---

## SUMMARY

**When you return:**

1. **Run:** `./pe refinery report`
   - See what happened while away

2. **Check:** Timestamps, activity log
   - Verify butlers worked

3. **Query:** `./pe refinery search "topic"`
   - Access organized knowledge instantly

4. **Browse:** `./pe refinery library`
   - See complete knowledge catalog

**The palace maintains itself. You just harvest the knowledge.**

---

## 🆕 LATEST SESSION (2026-01-27 Visualization Debug)

### What Happened This Session

**Original Task:** Organize documentation for ChatGPT audit
**Detour:** Visualization unified graph + mouse controls (5 hours)
**Result:** Documentation complete ✅, Visualization partial ⚠️

### Documentation Completed ✅

| Artifact | Location | Status |
|----------|----------|--------|
| INDEX.md | Root | ✅ Front door |
| THEORY_MAP.md | Root | ✅ 479 files mapped |
| AUDIT_MANIFEST.md | Root | ✅ Audit ready |
| PROJECT_METADATA.md | Root | ✅ Timestamps |
| Zips (4) | ~/Downloads/ | ✅ Ready for ChatGPT |

### Visualization Work ⚠️

**Files Modified:** 7 viz modules (540 lines changed)

**Good Fixes (42 lines):**
- Stop selection animation when empty
- Disable PERF_MONITOR auto-start
- Remove REFRESH from 5 animation loops
- Skip redundant opacity updates
- Only transparent when opacity < 1

**Complex Features (498 lines):**
- Unified graph (atoms + files in one graph)
- Crossfade transitions (750ms animated)
- Mouse controls (LEFT=select, RIGHT=rotate, SPACE+LEFT=pan)

**Status:** Code integrated but NOT TESTED by user yet

**Test Build:** `/tmp/final-integrated/output_human-readable_standard-model-of-code_20260127_093531.html`

### Research Artifacts Created (6 docs)

All saved to `docs/research/`:
- UI Projectome (Gemini)
- Performance optimization patterns (Perplexity)
- Animation lifecycle (Gemini)
- HTML generation pipeline (Gemini)
- Minimal fix strategies (Gemini)

### Knowledge Base Built (8 docs in /tmp/)

| Document | Lines | Purpose |
|----------|-------|---------|
| VISUALIZATION_COMPLETE_KNOWLEDGE_BASE.md | 300 | Complete system map |
| VIZ_STATE_FREEZE.md | 200 | Session freeze point |
| COMPLETE_EDIT_TRACE.md | 200 | Every edit traced |
| UI_REFACTOR_COMPLETE_MAP.md | 280 | UI refactor inventory |
| NEXT_STEPS_CONFIDENCE_ASSESSMENT.md | 150 | Action confidence |
| FINAL_STATE_SUMMARY.md | 200 | Test checklist |
| UNIFIED_GRAPH_RESEARCH_NOTES.md | 418 | Research findings |
| UNIFIED_GRAPH_REFINED_PLAN.md | 400 | Implementation plan |

**Total:** 2,148 lines of stable documentation

**Should move to repo if viz work continues.**

### Decision Points

**If testing viz build:**
- Open `/tmp/final-integrated/` and check FPS, mouse controls, crossfade
- If works → Commit all changes
- If partial → Cherry-pick good fixes only (42 lines)
- If broken → Revert, keep only performance fixes

**If returning to original task:**
- Commit documentation work (INDEX, THEORY_MAP, etc.)
- Archive viz work for later dedicated sprint
- Complete ChatGPT audit preparation

### Root Cause Found 🔥

**Original bug (in HEAD commit):**
```javascript
controls.mouseButtons = {
  LEFT: 0,   // ROTATE
  RIGHT: 0   // ROTATE (BOTH SAME!)
}
```

Both buttons were set to ROTATE. My fix: `LEFT: 2` (PAN, but selection.js intercepts for marquee).

---
