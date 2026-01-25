# Promotion Effort Metrics

> Tracking OPP → TASK promotion performance in the Cloud Refinery pipeline.

## Summary Statistics

| Metric | Value |
|--------|-------|
| Average Confidence Boost | +22% per OPP |
| Average Refinement Steps | 2 steps |
| Average Tools per Promotion | 2.3 tools |
| Estimated Time per OPP | 20-40 min |

## Promotion Thresholds

| Grade | Confidence | Auto-Promotion |
|-------|------------|----------------|
| A | 85% | Eligible |
| A+ | 95% | Priority |
| A++ | 99% | Critical Path |

## Detailed Promotion History

### OPP-061: HSL Daemon Fix
**Status:** PROMOTED → TASK-020 (COMPLETE)

| Phase | Confidence | Delta |
|-------|------------|-------|
| Initial | 55% | - |
| Forensic Analysis | 75% | +20% |
| Perplexity Validation | 90% | +15% |
| Final Refinement | 95% | +5% |

**Refinement Steps:** 3
**Tools Used:** 4 (Read, Grep, Perplexity, Gemini)
**Root Cause:** drift_guard.py (formerly hsl_daemon.py) subprocess calls missing Doppler wrapper
**Fix:** Updated plist ProgramArguments with Doppler injection

---

### OPP-064: Hierarchical Tree Layout
**Status:** REGISTERED (85%)

| Phase | Confidence | Delta |
|-------|------------|-------|
| Initial | 70% | - |
| Perplexity Validation | 85% | +15% |

**Refinement Steps:** 1
**Tools Used:** 1 (Perplexity)
**Key Finding:** Root at TOP, entering directory = DOWN/IN (industry standard)
**Blocks:** None (independent track)

---

### OPP-066: Rate Limiting Handler
**Status:** PROMOTION_READY (95%)

| Phase | Confidence | Delta |
|-------|------------|-------|
| Initial | 85% | - |
| Root Cause Analysis | 90% | +5% |
| Cost Impact Analysis | 95% | +5% |

**Refinement Steps:** 2
**Tools Used:** 2 (Forensic, Cost Analysis)
**Root Cause:** Thundering herd - multiple daemons hitting API concurrently
**Emergency Action:** Daemons disabled (2026-01-23 17:24)
**Blocks:** OPP-065

---

## Refinement Tools

| Tool | Purpose | Confidence Impact |
|------|---------|-------------------|
| Forensic Read | Root cause identification | +10-20% |
| Perplexity Sonar Pro | External validation | +10-15% |
| Gemini Flash | Quick assessment | +5-10% |
| Gemini Pro | Deep analysis | +10-15% |
| Cost Analysis | Business impact | +5-10% |

## Cost of Poor Refinement

**OPP-066 Case Study:**
- 70 rate limit errors before discovery
- Estimated waste: $17-25
- Daemons disabled to stop bleeding
- Lesson: Validate daemon interactions BEFORE deployment

## Formula

```
Promotion Readiness = min(Factual, Alignment, Current, Onwards)

Where:
- Factual: Evidence-backed claims (%)
- Alignment: Matches user intent (%)
- Current: Addresses present state (%)
- Onwards: Future-proof solution (%)
```

---

*Last Updated: 2026-01-23*
*Source: Session 6b2bb597-b703-4785-91b8-41366c1a59ea*
