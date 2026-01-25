# Autonomous Enrichment Pipeline (AEP)

> **Status:** SPECIFICATION
> **Created:** 2026-01-23
> **Vision:** Tasks by definition are READY TO EXECUTE. Validated.

---

## The Principle

**A TASK in this repository means: VALIDATED, READY TO EXECUTE.**

No more:
- "Boost confidence" workflows
- Manual research to fill gaps
- Human decision on when to promote

The pipeline does this automatically, continuously, in the cloud.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GCP CLOUD (24/7)                            │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   INBOX     │───▶│  ENRICHMENT │───▶│  PROMOTION  │         │
│  │  (OPPs)     │    │   ENGINE    │    │    GATE     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│        │                  │                  │                  │
│        │                  ▼                  ▼                  │
│        │           ┌─────────────┐    ┌─────────────┐          │
│        │           │  RESEARCH   │    │   TASKS     │          │
│        │           │   LOOPS     │    │  (READY)    │          │
│        │           │             │    │             │          │
│        │           │ • Gemini    │    │ • Validated │          │
│        │           │ • Perplexity│    │ • Steps     │          │
│        │           │ • Collider  │    │ • Evidence  │          │
│        │           └─────────────┘    └─────────────┘          │
│        │                  │                  │                  │
│        ▼                  ▼                  ▼                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              CONTEXT CACHE (Gemini)                      │   │
│  │         Keyed by commit SHA, RepoPack format             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   LOCAL REPO    │
                    │                 │
                    │ .agent/registry │
                    │   /active/      │
                    │   TASK-XXX.yaml │
                    │   (VALIDATED)   │
                    └─────────────────┘
```

---

## Enrichment Engine

The engine runs continuously, processing OPPs through research loops:

### Input: Raw Opportunity
```yaml
id: OPP-XXX
title: "Some idea or task"
confidence:
  factual: ???
  alignment: ???
  current: ???
  onwards: ???
  overall: ???
```

### Process: Research Loops

1. **Factual Grounding** (Perplexity)
   - "Is this technically valid?"
   - "What are the academic foundations?"
   - Citations required

2. **Alignment Check** (Gemini + Local Context)
   - "Does this serve the project mission?"
   - Compare against ROADMAP, THEORY, ARCHITECTURE

3. **Current Fit** (Collider Analysis)
   - "Does this fit the codebase as it exists?"
   - Run targeted analysis on affected files
   - Check for conflicts with existing code

4. **Onwards Projection** (Gemini Reasoning)
   - "Does this fit where we're heading?"
   - Compare against ROADMAP phases
   - Check architectural alignment

### Output: Enriched Opportunity
```yaml
id: OPP-XXX
title: "Some idea or task"
confidence:
  factual: 0.92
  alignment: 0.95
  current: 0.88
  onwards: 0.90
  overall: 0.88  # min()
evidence:
  perplexity: "path/to/research.md"
  gemini: "path/to/analysis.json"
  collider: "path/to/unified_analysis.json"
gaps_filled:
  - "Added academic citations"
  - "Validated against current codebase"
  - "Confirmed roadmap alignment"
```

---

## Promotion Gate

### Risk Factors (Decision Matrix)

| Grade | Overall Confidence | Auto-Promotion | Requirements |
|-------|-------------------|----------------|--------------|
| **A++** | >= 95% | ✅ IMMEDIATE | Steps auto-generated |
| **A+** | >= 90% | ✅ IMMEDIATE | Steps auto-generated |
| **A** | >= 85% | ✅ WITH REVIEW | Steps suggested |
| **B** | >= 75% | ❌ HOLD | Needs more enrichment |
| **C** | >= 50% | ❌ DEFER | Major gaps |
| **F** | < 50% | ❌ REJECT | Archive |

### Auto-Promotion Process

When confidence >= threshold:

1. **Generate Steps** (Gemini)
   - Analyze the task description
   - Break into atomic actions
   - Each step has: file, action, confidence

2. **Validate Steps** (Collider)
   - Check affected files exist
   - Verify no breaking changes
   - Confirm dependencies

3. **Create TASK** (Automatic)
   - Move from inbox to active
   - Assign to appropriate sprint
   - All steps mapped at 85%+ confidence

4. **Notify** (Optional)
   - Webhook or log
   - "TASK-XXX promoted and ready"

---

## No More Boost Workflow

### Old Way (ABOLISHED)
```
OPP created → Manual review → Boost confidence → Research → Review → Promote → Map steps → Execute
```

### New Way (AEP)
```
OPP created → [CLOUD ENRICHMENT] → TASK ready → Execute
```

The human/agent interaction is:
1. Create OPP (rough idea, low confidence OK)
2. Wait (cloud processes)
3. Execute TASK (fully validated, steps mapped)

---

## Implementation Path

### EXISTING TOOLS (Use These - Don't Recreate!)

| Tool | Purpose | Command |
|------|---------|---------|
| `triage_inbox.py` | Score opportunities, find duplicates | `./triage_inbox.py --score` |
| `confidence_validator.py` | 4D AI assessment with Gemini | `./confidence_validator.py --all` |
| `batch_promote.py` | Promote by threshold/category | `./batch_promote.py --threshold 90` |
| `promote_opportunity.py` | Single opportunity promotion | `./promote_opportunity.py OPP-XXX` |
| `add_task_steps.py` | Add steps to promoted tasks | `./add_task_steps.py TASK-XXX` |

### Orchestrator

The `enrichment_orchestrator.py` chains these tools:
```bash
python .agent/tools/enrichment_orchestrator.py        # Full pipeline
python .agent/tools/enrichment_orchestrator.py --dry-run  # Preview
```

### Phase 1: Local Cron
```bash
# Add to crontab
0 * * * * cd /path/to/PROJECT_elements && python .agent/tools/enrichment_orchestrator.py >> /tmp/enrichment.log 2>&1
```

### Phase 2: Cloud Function
Deploy `enrichment_orchestrator.py` to GCP Cloud Functions with:
- Trigger: Cloud Scheduler (every 15 min) or Pub/Sub (on git push)
- Secrets: GEMINI_API_KEY from Secret Manager
- Writes back via `git commit && git push`

### Phase 3: Full Autonomy
- Add Gemini context caching (TASK-019)
- Add webhook notifications
- Auto-assign to sprints based on category

---

## Integration Points

| System | Role |
|--------|------|
| **ACI** | Routes queries to appropriate tier |
| **HSL** | Detects drift, triggers re-enrichment |
| **BARE** | This IS BARE Phase 2 |
| **Decision Deck** | Cards for validated actions only |
| **Gemini Cache** | Reuses context across enrichment runs |

---

## Definition: TASK

From this point forward in PROJECT_elements:

> **TASK** = An opportunity that has:
> 1. 4D Confidence >= 85% (Grade A or higher)
> 2. All gaps filled with evidence
> 3. Steps mapped at 85%+ confidence each
> 4. Validated against current codebase
> 5. Ready to execute immediately

**There is no other kind of TASK.**

---

## Next Steps

1. [x] Spec written (this document)
2. [x] Create OPP-060 for AEP MVP
3. [x] Orchestrator created (enrichment_orchestrator.py)
4. [x] Centripetal scan tool created (centripetal_scan.py)
5. [ ] Run full centripetal scan (needs API quota reset)
6. [ ] Deploy to Cloud Function
7. [ ] Enable auto-promotion gate

## Centripetal Scan Tool

12-round progressive resolution analysis using FLASH_DEEP:

| Rounds | Level | Focus |
|--------|-------|-------|
| 1-3 | MACRO | Directories, realms, entry points |
| 4-6 | MESO | Modules, data flow, integration |
| 7-9 | MICRO | Core files, configs, patterns |
| 10-12 | NANO | Invariants, edge cases, synthesis |

```bash
# Run when API quota available
doppler run -- python .agent/tools/centripetal_scan.py
```
