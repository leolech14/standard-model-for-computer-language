# Sprawl Consolidation Plan

**Created:** 2026-01-23
**Status:** READY FOR EXECUTION
**Risk Level:** HIGH - 5 consecutive days of sprawl

---

## Executive Summary

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Total Files | 56,361 | ~3,000 | -94.7% |
| Real Code Files | 2,771 | 2,771 | 0% (protected) |
| Cache Files | 53,590 | 0 | -100% |
| Report Directories | 9 | 2 | -78% |
| Disk Usage (cache) | 1.03 GB | 0 | -100% |

---

## Phase 1: Immediate Cache Cleanup (P0)

### 1.1 Archive Calibration Cache to GCS

```bash
# Archive all repos_cache directories to GCS
gsutil -m cp -r standard-model-of-code/artifacts/atom-research/.repos_cache/ \
  gs://elements-archive-2026/calibration/repos_cache_root_2026-01-23/

gsutil -m cp -r standard-model-of-code/artifacts/atom-research/2026-01-23-calibration/.repos_cache/ \
  gs://elements-archive-2026/calibration/repos_cache_calibration_2026-01-23/

# Verify upload success (must return 0)
gsutil ls gs://elements-archive-2026/calibration/ | wc -l

# Remove local caches (ONLY after GCS verification)
rm -rf standard-model-of-code/artifacts/atom-research/.repos_cache
rm -rf standard-model-of-code/artifacts/atom-research/2026-01-23-calibration/.repos_cache
```

**Files removed:** 43,873
**Disk recovered:** 1.03 GB

### 1.2 Fix Recursion Bug

The path `jackson-core/artifacts/atom-research/2026-01-23-calibration/.repos_cache` indicates the calibration script is copying entire project structure into downloaded repos.

**Root Cause:** Likely in `standard-model-of-code/tools/research/` or calibration scripts
**Action:** Add `.repos_cache` to exclusion patterns in calibration scripts

---

## Phase 2: Report Directory Consolidation (P1)

### Current State (9 directories)

| Directory | Files | Purpose | Action |
|-----------|-------|---------|--------|
| `architecture_report/` | ? | Legacy | ARCHIVE |
| `roadmap_report/` | ? | Legacy | ARCHIVE |
| `evolution_report/` | ? | Legacy | ARCHIVE |
| `standard-model-of-code/.archive/html_reports/` | ? | Old outputs | ARCHIVE |
| `standard-model-of-code/docs/reports/` | 12 | Active reports | KEEP |
| `context-management/docs/reports/` | ? | Brain reports | KEEP |
| `context-management/reports/` | ? | Duplicate? | MERGE |
| `.agent/intelligence/triage_reports/` | ? | Agent output | ARCHIVE monthly |
| `.agent/intelligence/confidence_reports/` | ? | Agent output | ARCHIVE monthly |

### Target State (2 directories)

| Directory | Purpose |
|-----------|---------|
| `standard-model-of-code/docs/reports/` | Collider/Body reports |
| `context-management/docs/reports/` | Brain/AI reports |

### Consolidation Script

```bash
# Archive legacy report directories
mkdir -p archive/reports_2026-01-23/
mv architecture_report/ archive/reports_2026-01-23/
mv roadmap_report/ archive/reports_2026-01-23/
mv evolution_report/ archive/reports_2026-01-23/

# Merge context-management reports
mv context-management/reports/* context-management/docs/reports/ 2>/dev/null || true
rmdir context-management/reports/ 2>/dev/null || true

# Upload archive to GCS
gsutil -m cp -r archive/reports_2026-01-23/ gs://elements-archive-2026/archive/
```

---

## Phase 3: Documentation Audit (P2)

### Current State

| Metric | Count |
|--------|-------|
| Total .md files | 528 |
| Created in last 7 days | 403 |
| In `docs/` directories | ~200 |
| In `archive/` | ~150 |
| Scattered elsewhere | ~178 |

### Audit Checklist

1. **Identify duplicates:**
   ```bash
   # Find files with similar names
   find . -name "*.md" | xargs -I{} basename {} | sort | uniq -d
   ```

2. **Check for stale docs:**
   ```bash
   # Find .md files not modified in 30+ days
   find . -name "*.md" -mtime +30 -type f | head -20
   ```

3. **Consolidate by category:**
   - Specs → `standard-model-of-code/docs/specs/`
   - Reports → `standard-model-of-code/docs/reports/`
   - Research → `standard-model-of-code/docs/research/`
   - Workflows → `context-management/docs/workflows/`
   - Operations → `context-management/docs/operations/`

---

## Phase 4: Prevention (P3)

### 4.1 .gitignore Updates (DONE)

```gitignore
# Added 2026-01-23
.repos_cache/
**/.repos_cache/
**/calibration_repos/
```

### 4.2 CI Sprawl Alert (TODO)

Add to CI pipeline:

```yaml
sprawl-check:
  script: |
    TOTAL=$(find . -type f | wc -l)
    if [ "$TOTAL" -gt 5000 ]; then
      echo "SPRAWL ALERT: $TOTAL files (threshold: 5000)"
      exit 1
    fi
```

### 4.3 Weekly Timestamp Regeneration

```bash
# Add to cron or agent boot sequence
python3 standard-model-of-code/scripts/generate_repo_timestamps.py
```

---

## Execution Order

| Step | Command | Risk |
|------|---------|------|
| 1 | Run Phase 1.1 (archive to GCS) | LOW (reversible) |
| 2 | Run Phase 2 (consolidate reports) | LOW (reversible) |
| 3 | Commit .gitignore changes | LOW |
| 4 | Regenerate timestamps CSV | LOW |
| 5 | Run Phase 3 (doc audit) | MEDIUM (needs review) |

---

## Validation

After consolidation, verify:

```bash
# Total file count should be ~3,000
find . -type f | wc -l

# No .repos_cache locally
find . -name ".repos_cache" -type d | wc -l  # Should be 0

# Report directories reduced
find . -maxdepth 3 -type d -name "*report*" | wc -l  # Should be <= 4

# GCS backup exists
gsutil ls gs://elements-archive-2026/calibration/
gsutil ls gs://elements-archive-2026/archive/
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Lose calibration data | GCS backup BEFORE local delete |
| Break calibration scripts | Keep one local repo for testing |
| Lose important docs | Archive before delete, never hard-delete |

---

## Related Documents

- `docs/OPEN_CONCERNS.md` - OC-009 (Scope Leakage) triggered this plan
- `context-management/docs/workflows/TIMESTAMP_WORKFLOW.md` - File tracking
- `.agent/registry/INDEX.md` - Task registry
