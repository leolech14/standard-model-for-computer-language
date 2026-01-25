# Sprawl Consolidation Plan

**Created:** 2026-01-23
**Status:** IN_PROGRESS
**Sprawl Risk:** HIGH (5 consecutive days)

## Problem Statement

Current state analysis revealed:
- 56,361 total files (95.1% cache/venv masking reality)
- 2,771 real code files
- 528 .md files (context sprawl)
- 57.6 markdown files/day creation rate
- No consolidation strategy

## Consolidation Phases

### Phase 1: Exclude Noise from Analysis (IMMEDIATE)

| Action | Target | Impact |
|--------|--------|--------|
| Update .gitignore | `.repos_cache/`, `*.pyc`, `__pycache__/` | Cleaner git status |
| Exclude from timestamps | Cache dirs, venv | Accurate sprawl metrics |
| Add to archive config | Large cache dirs | GCS offload candidates |

### Phase 2: Archive Large Directories to GCS

| Directory | Size | Action |
|-----------|------|--------|
| `.repos_cache/` | ~50K files | Offload to GCS |
| `archive/spectrometer_benchmarks_legacy/` | Legacy | Offload to GCS |
| `atom-research/calibration/` | Calibration data | Offload to GCS |

### Phase 3: Consolidate Report Directories

Current fragmentation:
```
.collider/
.collider_report/
.collider_analysis/
reports/
```

Consolidate to: `.collider/` (single output directory)

### Phase 4: Markdown Audit

528 .md files need classification:
- **Canonical:** Keep in place, reference in manifest
- **Duplicate:** Delete or merge
- **Stale:** Archive to GCS
- **Generated:** Move to `.generated/` or delete

## Immediate Actions (This Session)

1. [x] Create this consolidation plan
2. [x] Update archive config to include large cache dirs
3. [ ] Run archive offload for legacy dirs (deferred - needs GCS access)
4. [x] Audit top-level untracked .md files
5. [ ] Update CODOME_MANIFEST with cleanup results

## Completed This Session

| Action | Before | After |
|--------|--------|-------|
| Root .md files | 11 | 6 (essential only) |
| `orphans_report.md` | Root | `archive/reports/` |
| `validated_*.md` | Root | `archive/reports/` |
| `AGENTKNOWLEDGEDUMP.md` | Root | `context-management/docs/agent_school/` |
| Timestamp CSV | Not gitignored | Added to `.gitignore` |
| Archive config | Missing sprawl dirs | Added 4 offload targets |

## New Task Created

- **#10:** Implement Gemini context caching for FLASH_DEEP tier
  - Reference: `standard-model-of-code/docs/research/gemini/docs/20260123_gemini_long_context_blueprint.md`

## Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| Untracked files | 50+ | <10 |
| .md file sprawl | 528 | <200 |
| Orphan files | 1 | 0 |
| Daily sprawl risk | HIGH | LOW |

## Notes

- Do NOT delete anything without GCS backup first
- All deletions logged in this file
- Manifest updated after each phase
