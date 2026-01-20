# Infallible Plan: Documentation Cleanup

> Haiku-deployable instructions for TASK-003 and TASK-005.

**Created:** 2026-01-20
**Status:** READY FOR DEPLOYMENT
**Confidence:** 95%+ (context gaps filled)

---

## Pre-Deployment Verification

These facts were verified before plan creation:

| Fact | Verification Method | Result |
|------|---------------------|--------|
| 12 PNGs at docs root | `ls context-management/docs/*.png \| wc -l` | 12 confirmed |
| 26 PNGs in assets/ | `ls context-management/docs/assets/*.png \| wc -l` | 26 confirmed |
| No PNG refs in root .md files | `grep -r "\.png" context-management/docs/*.md \| grep -v assets/` | Only registry example |
| AGENT_INITIATION.md line 21 broken | `grep AI_OPERATING_MANUAL context-management/docs/operations/` | Confirmed broken |
| AI_USER_GUIDE.md exists | `ls context-management/docs/AI_USER_GUIDE.md` | Exists |

---

## TASK-003: Move Top-Level PNGs to assets/

### Overview

| Property | Value |
|----------|-------|
| Files to move | 12 PNG files |
| Source | `context-management/docs/*.png` |
| Destination | `context-management/docs/assets/` |
| Risk | LOW - no markdown refs to break |
| Reversibility | HIGH - git mv preserves history |

### Step-by-Step Instructions

**Total Steps: 6**

#### Step 1: Verify starting state
```bash
cd /Users/lech/PROJECTS_all/PROJECT_elements
ls context-management/docs/*.png | wc -l
```
**Expected output:** `12`
**If not 12:** STOP. State has changed. Re-verify.

#### Step 2: Verify destination exists
```bash
ls -d context-management/docs/assets/
```
**Expected output:** `context-management/docs/assets/`
**If error:** Run `mkdir -p context-management/docs/assets/`

#### Step 3: Move files with git
```bash
git mv context-management/docs/*.png context-management/docs/assets/
```
**Expected output:** No output (success)
**If error:** Check file permissions, git status

#### Step 4: Verify files moved
```bash
ls context-management/docs/*.png 2>&1
```
**Expected output:** `ls: context-management/docs/*.png: No such file or directory`

#### Step 5: Verify destination count
```bash
ls context-management/docs/assets/*.png | wc -l
```
**Expected output:** `38` (26 original + 12 moved)

#### Step 6: Stage verification
```bash
git status --short | grep "R  context-management/docs/"
```
**Expected output:** 12 lines showing renames

### Definition of Done

- [ ] Zero PNG files at `context-management/docs/` root
- [ ] 38 PNG files in `context-management/docs/assets/`
- [ ] Git status shows 12 renames (R)
- [ ] No broken image refs in markdown files

### Commit Template

```bash
git commit -m "$(cat <<'EOF'
chore: move 12 top-level PNGs to assets/ folder

## CHANGES
| File | Description |
|------|-------------|
| context-management/docs/*.png → assets/ | Consolidate visual assets |

## VERIFICATION
- Source: 0 PNGs at docs root
- Destination: 38 PNGs in assets/
- Broken refs: None (verified via grep)

## FINDING CODE
ls context-management/docs/assets/*.png

Co-Authored-By: Claude Haiku <noreply@anthropic.com>
EOF
)"
```

---

## TASK-005: Fix Broken AI_OPERATING_MANUAL.md References

### Overview

| Property | Value |
|----------|-------|
| Broken references | 6 files |
| Manual fixes needed | 1 file |
| Auto-regenerating | 5 files |
| Risk | LOW - simple text replacement |
| Reversibility | HIGH - single line change |

### Reference Classification

| File | Type | Action |
|------|------|--------|
| `docs/operations/AGENT_INITIATION.md:21` | Manual | **FIX NOW** |
| `registry/REGISTRY.json:2222-2225` | Semi-auto | Fix or regenerate |
| `registry/REGISTRY_REPORT.md:323` | Auto | Regenerates from REGISTRY.json |
| `output/analysis_sets_report.md:44` | Auto | Regenerates on next run |
| `output/file_metadata_audit.csv:4978` | Auto | Regenerates on next run |
| `docs/proposals/COLLIDER_AI_INSIGHTS_PROPOSAL.md:341` | Historical | Skip (archive doc) |

### Step-by-Step Instructions

**Total Steps: 5**

#### Step 1: Verify current broken state
```bash
cd /Users/lech/PROJECTS_all/PROJECT_elements
grep -n "AI_OPERATING_MANUAL" context-management/docs/operations/AGENT_INITIATION.md
```
**Expected output:** `21:1.  **Read the Manual**: [AI_OPERATING_MANUAL.md](...`

#### Step 2: Fix AGENT_INITIATION.md
Replace line 21 content:

**OLD:**
```markdown
1.  **Read the Manual**: [AI_OPERATING_MANUAL.md](file:///Users/lech/PROJECTS_all/PROJECT_elements/context-management/docs/AI_OPERATING_MANUAL.md).
```

**NEW:**
```markdown
1.  **Read the Manual**: [AI_USER_GUIDE.md](AI_USER_GUIDE.md).
```

**Note:** Also simplified the path from absolute `file:///...` to relative `AI_USER_GUIDE.md` for portability.

#### Step 3: Verify fix applied
```bash
grep -n "AI_USER_GUIDE" context-management/docs/operations/AGENT_INITIATION.md
```
**Expected output:** `21:1.  **Read the Manual**: [AI_USER_GUIDE.md](AI_USER_GUIDE.md).`

#### Step 4: Verify no remaining broken refs in ops docs
```bash
grep -r "AI_OPERATING_MANUAL" context-management/docs/operations/
```
**Expected output:** No output (no matches)

#### Step 5: Optional - Update REGISTRY.json
If clean registry is desired:
```bash
# Option A: Manual edit lines 2222-2225
# Option B: Regenerate registry
python context-management/tools/archive/archive.py mirror
```

### Definition of Done

- [ ] AGENT_INITIATION.md line 21 references AI_USER_GUIDE.md
- [ ] `grep AI_OPERATING_MANUAL context-management/docs/operations/` returns empty
- [ ] Link uses relative path (portable)

### Commit Template

```bash
git commit -m "$(cat <<'EOF'
fix: update broken AI_OPERATING_MANUAL.md reference

## CHANGES
| File | Description |
|------|-------------|
| context-management/docs/operations/AGENT_INITIATION.md | Fix line 21 reference |

## DETAIL
- OLD: AI_OPERATING_MANUAL.md (deleted file)
- NEW: AI_USER_GUIDE.md (current file)
- Also: simplified absolute path to relative for portability

## VERIFICATION
grep -r "AI_OPERATING_MANUAL" context-management/docs/operations/
# Expected: no output

Co-Authored-By: Claude Haiku <noreply@anthropic.com>
EOF
)"
```

---

## Combined Execution Order

| Order | Task | Steps | Time |
|-------|------|-------|------|
| 1 | TASK-005: Fix broken refs | 5 | ~2 min |
| 2 | TASK-003: Move PNGs | 6 | ~3 min |
| 3 | Commit both | 2 | ~1 min |

### Single Combined Commit Alternative

If preferred, combine into one commit:

```bash
git add -A
git commit -m "$(cat <<'EOF'
chore: docs cleanup - fix broken refs and consolidate assets

## CHANGES
| File | Description |
|------|-------------|
| docs/operations/AGENT_INITIATION.md | Fix broken AI_OPERATING_MANUAL.md ref |
| docs/*.png → docs/assets/ | Move 12 PNGs to assets folder |

## VERIFICATION
- Broken refs fixed: grep AI_OPERATING_MANUAL docs/operations/ returns empty
- PNG consolidation: 38 files now in assets/, 0 at root

Co-Authored-By: Claude Haiku <noreply@anthropic.com>
EOF
)"
```

---

## Rollback Procedure

If anything goes wrong:

```bash
# Undo all uncommitted changes
git checkout -- .

# If already committed, revert
git revert HEAD
```

---

## Haiku Agent Deployment Notes

When deploying to Haiku sub-agent:

1. **Provide this file as context**
2. **Specify task**: "Execute TASK-003 and TASK-005 from INFALLIBLE_PLAN_DOCS_CLEANUP.md"
3. **Validation**: Agent must output verification results for each step
4. **Commit**: Agent commits with provided template
5. **Report**: Agent outputs completion summary with git log of commit

### Expected Agent Output Format

```
EXECUTION REPORT
================
Task: TASK-003 + TASK-005
Status: COMPLETE

Step Results:
- TASK-005 Step 1: PASS (found broken ref at line 21)
- TASK-005 Step 2: PASS (replaced with AI_USER_GUIDE.md)
- TASK-005 Step 3: PASS (verified new ref exists)
- TASK-005 Step 4: PASS (no remaining broken refs)
- TASK-003 Step 1: PASS (12 PNGs found)
- TASK-003 Step 2: PASS (assets/ exists)
- TASK-003 Step 3: PASS (git mv complete)
- TASK-003 Step 4: PASS (0 PNGs at root)
- TASK-003 Step 5: PASS (38 PNGs in assets/)
- TASK-003 Step 6: PASS (12 renames staged)

Commit: [hash]
Message: chore: docs cleanup - fix broken refs and consolidate assets

Definition of Done:
- [x] Zero PNG files at docs root
- [x] 38 PNG files in assets/
- [x] AGENT_INITIATION.md references AI_USER_GUIDE.md
- [x] No broken refs in operations/
```
