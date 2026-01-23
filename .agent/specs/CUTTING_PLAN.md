# CUTTING PLAN: From Bulk to Lean

**Status:** PROPOSED
**Version:** 1.1
**Date:** 2026-01-23
**Philosophy:** "Worse is Better" - Simple implementations that work beat complex ones that don't

> **CARDINAL RULE: We never delete. Only archive.**

---

## Forensic Archive Protocol

### Archive Location & Structure

```
archive/agent_cuts/
└── 2026-01-23/                          # Date of cutting operation
    ├── MANIFEST.md                       # Human-readable inventory
    ├── PROVENANCE.yaml                   # Machine-readable lineage
    ├── truths_history/                   # Archived from .agent/intelligence/truths/history/
    │   ├── truths_20260123_052327.yaml
    │   └── truths_20260123_052436.yaml
    ├── workflows/                        # Archived workflow docs
    │   ├── testing_suite.md
    │   └── publish.md
    ├── orientation/                      # Archived orientation files
    │   └── *.md
    └── OPEN_CONCERNS.md                  # Superseded design doc
```

### Traceability Requirements

Every archived file MUST have:

| Field | Description | Example |
|-------|-------------|---------|
| **Original Path** | Where the file lived before archiving | `.agent/intelligence/truths/history/` |
| **Archive Path** | Where the file now lives | `archive/agent_cuts/2026-01-23/truths_history/` |
| **Archive Date** | ISO 8601 timestamp | `2026-01-23T07:15:00Z` |
| **Archive Reason** | Why it was cut | `DEAD_WEIGHT`, `SUPERSEDED`, `CONSOLIDATED`, `MISPLACED` |
| **Archived By** | Agent or human who performed the cut | `claude-opus-4-5-20251101` |
| **Git Commit** | Commit SHA that performed the archive | `abc123...` |
| **Restore Command** | How to undo if needed | `mv archive/...  .agent/...` |

### PROVENANCE.yaml Schema

```yaml
# archive/agent_cuts/2026-01-23/PROVENANCE.yaml
# Machine-readable archive provenance for forensic traceability

archive_operation:
  id: "CUT-2026-01-23-001"
  date: "2026-01-23T07:15:00Z"
  operator: "claude-opus-4-5-20251101"
  git_commit: null  # Populated after commit
  plan_reference: ".agent/specs/CUTTING_PLAN.md"

rationale: |
  Bulk-to-lean cutting phase. Removing dead weight, consolidating
  overlapping docs, simplifying state machine. Archive preserves
  full history for potential restoration.

files:
  - original_path: ".agent/intelligence/truths/history/truths_20260123_052327.yaml"
    archive_path: "truths_history/truths_20260123_052327.yaml"
    reason: "DEAD_WEIGHT"
    reason_detail: "Historical snapshots with no consumer. BARE doesn't use them."
    sha256_at_archive: null  # Computed during archive
    restore_command: "mv archive/agent_cuts/2026-01-23/truths_history/truths_20260123_052327.yaml .agent/intelligence/truths/history/"

  - original_path: ".agent/intelligence/truths/history/truths_20260123_052436.yaml"
    archive_path: "truths_history/truths_20260123_052436.yaml"
    reason: "DEAD_WEIGHT"
    reason_detail: "Historical snapshots with no consumer. BARE doesn't use them."
    sha256_at_archive: null
    restore_command: "mv archive/agent_cuts/2026-01-23/truths_history/truths_20260123_052436.yaml .agent/intelligence/truths/history/"

  - original_path: ".agent/workflows/testing_suite.md"
    archive_path: "workflows/testing_suite.md"
    reason: "MISPLACED"
    reason_detail: "Describes 100+ repo experiment - not core agent workflow."
    sha256_at_archive: null
    restore_command: "mv archive/agent_cuts/2026-01-23/workflows/testing_suite.md .agent/workflows/"

  - original_path: ".agent/OPEN_CONCERNS.md"
    archive_path: "OPEN_CONCERNS.md"
    reason: "SUPERSEDED"
    reason_detail: "Content migrated to sprints/README.md and BARE roadmap section."
    sha256_at_archive: null
    successor_files:
      - ".agent/sprints/README.md"
      - ".agent/specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md#roadmap"
    restore_command: "mv archive/agent_cuts/2026-01-23/OPEN_CONCERNS.md .agent/"

version_control:
  pre_archive_branch: "main"
  archive_commit_message: |
    chore(archive): Cut bulk phase artifacts to archive/agent_cuts/2026-01-23/

    CUTTING_PLAN Phase 1 execution:
    - Archived truths/history/ (dead weight - no consumer)
    - Archived testing_suite.md (misplaced experiment doc)
    - Archived OPEN_CONCERNS.md (superseded by consolidated docs)

    All files preserved with full provenance in PROVENANCE.yaml.
    Restore commands documented for each file.

    Refs: .agent/specs/CUTTING_PLAN.md
```

### Versioning Protocol

| Version Event | Action |
|---------------|--------|
| **Initial Archive** | Create `PROVENANCE.yaml` with `v1.0` |
| **Partial Restore** | Increment patch: `v1.1`, log in `restoration_history` |
| **Full Restore** | Archive the archive: `archive/agent_cuts/2026-01-23_RESTORED/` |
| **Re-cut** | New date directory: `archive/agent_cuts/2026-01-24/` |

### Integrity Verification

```bash
# Verify archive integrity (run anytime)
cd archive/agent_cuts/2026-01-23/
for f in $(find . -type f -not -name "PROVENANCE.yaml" -not -name "MANIFEST.md"); do
  sha256sum "$f"
done

# Compare with PROVENANCE.yaml sha256_at_archive values
```

### Recovery Protocol

```bash
# To restore a single file:
mv archive/agent_cuts/2026-01-23/workflows/testing_suite.md .agent/workflows/

# To restore entire archive (undo the cut):
cp -r archive/agent_cuts/2026-01-23/* .agent/
# Then manually move files to correct locations per PROVENANCE.yaml

# Log restoration in PROVENANCE.yaml:
# restoration_history:
#   - date: "2026-01-25T10:00:00Z"
#     file: "workflows/testing_suite.md"
#     reason: "Needed for new experiment"
```

---

## Executive Summary

PROJECT_elements has completed its **bulk phase** - extensive design documents, multiple registries, ambitious automation specs. Now it's time to **cut** - eliminate redundancy, consolidate overlap, and simplify to a minimal viable system.

**Core Principle:** Design artifacts should not co-mingle with operational artifacts. Move aspirations to roadmaps, keep only what's actively running.

---

## Research Sources

All research auto-saved to `standard-model-of-code/docs/research/perplexity/`:

| Query | Key Insight |
|-------|-------------|
| Registry of Registries patterns | SSOT with YAML > distributed markdown tables |
| Cutting complexity best practices | Delete obsolete code, extract repeated logic, remove redundancy |
| Minimal viable registry patterns | 5 essential fields only: name, version, source, license, deps |
| Format comparison | TOML > YAML > JSON for minimal human-readable configs |

**"Worse is Better" Examples:** `package.json`, `Cargo.toml`, `pyproject.toml` - tiny files that power massive ecosystems.

---

## The Cutting Audit

### FILES TO ARCHIVE

| File | Archive To | Justification |
|------|------------|---------------|
| `.agent/intelligence/truths/history/*.yaml` | `archive/agent_cuts/2026-01-23/truths_history/` | **DEAD WEIGHT.** Historical snapshots with no consumer. BARE doesn't use them. Only `repo_truths.yaml` matters. |
| `.agent/workflows/testing_suite.md` | `archive/agent_cuts/2026-01-23/workflows/` | **MISPLACED.** Describes a 100+ repo experiment - not core agent workflow. |
| `context-management/.agent/orientation/*` | `archive/agent_cuts/2026-01-23/orientation/` | **STALE.** Git shows these as deleted but tracked. Archive properly. |
| `context-management/.agent/workflows/publish.md` | `archive/agent_cuts/2026-01-23/workflows/` | **STALE.** Also shows as deleted in git status. |
| `OPEN_CONCERNS.md` (after extraction) | `archive/agent_cuts/2026-01-23/` | **SUPERSEDED.** Content migrated to sprints/README.md and BARE roadmap. |

### FILES TO MERGE

| Merge This | Into This | Justification |
|------------|-----------|---------------|
| `OPEN_CONCERNS.md` (vision parts) | `specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md` | Consolidate all future-facing design into BARE spec |
| `OPEN_CONCERNS.md` (sprint docs) | `sprints/README.md` (new) | Documentation lives with implementation |
| Multiple registry INDEX.md tables | `.agent/META_REGISTRY.yaml` (new) | Single machine-readable source of truth |

### SIMPLIFICATIONS

#### A. Simplify BARE Spec
- **Current:** 6-processor daemon spec, only TruthValidator runs
- **Action:** Main body = only what's implemented. Move other 5 processors to "Roadmap" section.

#### B. Simplify Task State Machine
- **Current:** `DISCOVERY → SCOPED → PLANNED → EXECUTING → VALIDATING → COMPLETE → ARCHIVED` (7 states)
- **Proposed:** `DISCOVERY → READY → EXECUTING → COMPLETE → ARCHIVED` (5 states)
- **Benefit:** Fewer states, simpler claim logic, lower procedural overhead

#### C. Remove Static Agent Capabilities
- **Current:** `manifest.yaml` lists static agent capabilities
- **Action:** Delete `agents` section. Derive capabilities from `runs/` history instead.

---

## The Minimal Viable Meta-Registry

### Design Constraints

| Constraint | Value |
|------------|-------|
| File count | **1** (single file) |
| Max lines | **50** |
| Automation | **None** (manually maintained initially) |
| Fields per entry | **3** (path, type, purpose) |
| Health checks | **None** |
| Checksums | **None** |
| **Purpose Alignment** | For entries mapping to a subsystem in `SUBSYSTEM_INTEGRATION.md`, the `purpose` field **MUST** use the exact string from that subsystem's `Purpose` column |

### The File: `.agent/META_REGISTRY.yaml`

```yaml
# .agent/META_REGISTRY.yaml
#
# Minimal index of key project registries and documents. Manually maintained.
# Replaces markdown tables for machine-readable agent discovery.
# Purpose fields ALIGNED with SUBSYSTEM_INTEGRATION.md canonical definitions.

registries:
  # Bootstrap & Configuration
  - path: .agent/KERNEL.md
    type: protocol
    purpose: Agent boot protocol and core principles

  - path: .agent/manifest.yaml
    type: manifest
    purpose: Machine-readable project metadata for tools

  # Strategic & Design
  - path: .agent/SUBSYSTEM_INTEGRATION.md
    type: map
    purpose: Canonical map of subsystem connections

  - path: .agent/specs/
    type: specs
    purpose: System specifications and designs (incl. BARE)

  - path: .agent/sprints/
    type: sprints
    purpose: Sprint definitions and tracking

  # Operational State (Aligned with S5 Task Registry)
  - path: .agent/registry/active/
    type: tasks
    purpose: Work item tracking  # ALIGNED: S5 Task Registry

  - path: .agent/registry/inbox/
    type: inbox
    purpose: Triage inbox for new opportunities

  - path: .agent/runs/
    type: runs
    purpose: Agent work session logs

  # Intelligence Output (Aligned with S6 BARE)
  - path: .agent/intelligence/truths/repo_truths.yaml
    type: truths
    purpose: Background auto-refinement  # ALIGNED: S6 BARE TruthValidator output

  # External Registries (Aligned with S1, S7)
  - path: standard-model-of-code/docs/specs/REGISTRY_OF_REGISTRIES.md
    type: theory
    purpose: Semantic code analysis  # ALIGNED: S1 Collider ontological ground truth

  - path: context-management/registry/REGISTRY.json
    type: archive-config
    purpose: Cloud sync  # ALIGNED: S7 Archive/Mirror (GCS)
```

**Total: 11 entries, ~45 lines**

### `META_REGISTRY.yaml` vs. `manifest.yaml`

These two files serve **distinct but complementary roles**:

| File | Role | Question It Answers |
|------|------|---------------------|
| **`manifest.yaml`** | Low-level machine configuration | "How do I configure myself to run?" |
| **`META_REGISTRY.yaml`** | High-level curated table of contents | "Where do I look to find X?" |

**`manifest.yaml`** provides:
- Specific data paths for tools/scripts
- Integration details (secrets, cloud config)
- Validation rules for execution

**`META_REGISTRY.yaml`** provides:
- First-read overview for agents/humans
- Strategic discovery of knowledge sources
- Replaces scattered markdown tables with single index

While some paths overlap, their **intended consumer and purpose differ**. `META_REGISTRY.yaml` is for strategic navigation; `manifest.yaml` is for operational configuration.

### Subsystem Alignment Matrix

Cross-reference between META_REGISTRY entries and SUBSYSTEM_INTEGRATION.md canonical definitions:

| META_REGISTRY Entry | Subsystem ID | Canonical Purpose (from S_I.md) | Type |
|---------------------|--------------|--------------------------------|------|
| `.agent/registry/active/` | S5 | Work item tracking | State |
| `.agent/intelligence/truths/` | S6 | Background auto-refinement | State |
| `standard-model-of-code/docs/specs/REGISTRY_OF_REGISTRIES.md` | S1 | Semantic code analysis | Engine |
| `context-management/registry/REGISTRY.json` | S7 | Cloud sync | Utility |
| `.agent/KERNEL.md` | S0 | Bootstrap/Protocol | Config |
| `.agent/manifest.yaml` | S0 | Bootstrap/Protocol | Config |
| `.agent/SUBSYSTEM_INTEGRATION.md` | S0 | Subsystem Integration | Doc |
| `.agent/specs/` | S6 | BARE specifications | Doc |
| `.agent/sprints/` | S5 | Sprint tracking | State |
| `.agent/registry/inbox/` | S5 | Opportunity triage | State |
| `.agent/runs/` | S5 | Session logs | State |

**Validation Rule:** If a META_REGISTRY entry maps to a subsystem, its `purpose` field must match or derive from the subsystem's canonical `Purpose` in SUBSYSTEM_INTEGRATION.md.

---

## Implementation Phases

### Phase 1: Archive Dead Weight (with Forensic Provenance)

```bash
#!/bin/bash
# CUTTING_PLAN Phase 1 Execution Script
# Run from PROJECT_elements root

set -e  # Exit on error

ARCHIVE_DIR="archive/agent_cuts/2026-01-23"
OPERATOR="claude-opus-4-5-20251101"
DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create archive directory structure
mkdir -p "$ARCHIVE_DIR"/{truths_history,workflows,orientation}

# Function to archive with checksum
archive_file() {
    local src="$1"
    local dst="$2"
    if [ -f "$src" ]; then
        cp "$src" "$dst"
        echo "  Archived: $src -> $dst"
    fi
}

echo "=== Phase 1: Archive Dead Weight ==="
echo "Archive location: $ARCHIVE_DIR"
echo "Operator: $OPERATOR"
echo "Date: $DATE"
echo ""

# Archive history files
echo "Archiving truths/history/..."
for f in .agent/intelligence/truths/history/*.yaml; do
    [ -f "$f" ] && archive_file "$f" "$ARCHIVE_DIR/truths_history/$(basename $f)"
done

# Archive misplaced workflow
echo "Archiving workflows..."
archive_file ".agent/workflows/testing_suite.md" "$ARCHIVE_DIR/workflows/testing_suite.md"

# Archive stale context-management files (if they exist)
echo "Archiving stale orientation files..."
if [ -d "context-management/.agent/orientation" ]; then
    cp -r context-management/.agent/orientation/* "$ARCHIVE_DIR/orientation/" 2>/dev/null || true
fi
archive_file "context-management/.agent/workflows/publish.md" "$ARCHIVE_DIR/workflows/publish.md"

# Generate MANIFEST.md (human-readable)
cat > "$ARCHIVE_DIR/MANIFEST.md" << EOF
# Agent Cuts Archive - 2026-01-23

**Operation ID:** CUT-2026-01-23-001
**Date:** $DATE
**Operator:** $OPERATOR
**Plan Reference:** .agent/specs/CUTTING_PLAN.md

## Archived Files

| Original Location | Archive Location | Reason |
|-------------------|------------------|--------|
| .agent/intelligence/truths/history/*.yaml | truths_history/ | DEAD_WEIGHT - No consumer |
| .agent/workflows/testing_suite.md | workflows/ | MISPLACED - Experiment doc |
| context-management/.agent/orientation/* | orientation/ | STALE - Git shows deleted |
| context-management/.agent/workflows/publish.md | workflows/ | STALE - Git shows deleted |

## Restoration

See PROVENANCE.yaml for machine-readable restore commands.

\`\`\`bash
# Quick restore example:
cp archive/agent_cuts/2026-01-23/workflows/testing_suite.md .agent/workflows/
\`\`\`
EOF

# Generate PROVENANCE.yaml (machine-readable with checksums)
cat > "$ARCHIVE_DIR/PROVENANCE.yaml" << EOF
# Machine-readable archive provenance
# Generated: $DATE

archive_operation:
  id: "CUT-2026-01-23-001"
  date: "$DATE"
  operator: "$OPERATOR"
  git_commit: null  # Update after commit
  plan_reference: ".agent/specs/CUTTING_PLAN.md"

rationale: |
  Bulk-to-lean cutting phase. Removing dead weight, consolidating
  overlapping docs, simplifying state machine. Full provenance preserved.

files:
EOF

# Add each archived file with checksum
for f in $(find "$ARCHIVE_DIR" -type f -not -name "MANIFEST.md" -not -name "PROVENANCE.yaml"); do
    rel_path="${f#$ARCHIVE_DIR/}"
    sha=$(shasum -a 256 "$f" | cut -d' ' -f1)

    # Determine original path
    case "$rel_path" in
        truths_history/*) orig=".agent/intelligence/truths/history/$(basename $f)" ;;
        workflows/*)
            if [[ "$rel_path" == *"publish.md" ]]; then
                orig="context-management/.agent/workflows/publish.md"
            else
                orig=".agent/workflows/$(basename $f)"
            fi
            ;;
        orientation/*) orig="context-management/.agent/orientation/$(basename $f)" ;;
        *) orig="unknown" ;;
    esac

    cat >> "$ARCHIVE_DIR/PROVENANCE.yaml" << EOF
  - original_path: "$orig"
    archive_path: "$rel_path"
    sha256: "$sha"
    restore_command: "cp $ARCHIVE_DIR/$rel_path $orig"
EOF
done

# Add version info
cat >> "$ARCHIVE_DIR/PROVENANCE.yaml" << EOF

version: "1.0"
restoration_history: []
EOF

echo ""
echo "=== Archive Complete ==="
echo "Files archived to: $ARCHIVE_DIR"
echo "MANIFEST.md created (human-readable)"
echo "PROVENANCE.yaml created (machine-readable with checksums)"
echo ""
echo "Next: Review archive, then remove originals from .agent/"
```

**Effort:** 20 minutes
**Risk:** None (archive preserves everything with full provenance)

### Phase 2: Create Meta-Registry

```bash
# Create the minimal meta-registry file
# (content as specified above)
```

**Effort:** 10 minutes
**Risk:** None

### Phase 3: Consolidate OPEN_CONCERNS

1. Extract sprint documentation → `sprints/README.md`
2. Extract future vision → append to `specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md` as "Roadmap" section
3. Archive `OPEN_CONCERNS.md` → `archive/agent_cuts/2026-01-23/OPEN_CONCERNS.md`

**Effort:** 30 minutes
**Risk:** Low (document reorganization, original preserved in archive)

### Phase 4: Simplify State Machine

Update `KERNEL.md` task lifecycle:

```diff
- DISCOVERY → SCOPED → PLANNED → EXECUTING → VALIDATING → COMPLETE → ARCHIVED
+ DISCOVERY → READY → EXECUTING → COMPLETE → ARCHIVED
```

Update `claim_task.sh` to claim `READY` tasks.

**Effort:** 1 hour
**Risk:** Medium (behavior change)

### Phase 5: Trim BARE Spec

Edit `specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md`:
- Move unimplemented processors to "## Future Roadmap" section
- Main body describes only TruthValidator (what's running)

**Effort:** 30 minutes
**Risk:** Low

---

## Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| Files in `.agent/intelligence/truths/history/` | 2+ | 0 (archived) |
| Task states | 7 | 5 |
| Design docs with implementation overlap | 2+ | 0 (consolidated) |
| Machine-readable registry index | 0 | 1 |
| Lines in META_REGISTRY.yaml | N/A | <50 |
| Files in `archive/agent_cuts/2026-01-23/` | 0 | 5+ (preserved history) |

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| **Archive, never delete** | Preserve history; enables recovery; respects past work |
| **Purpose alignment with SUBSYSTEM_INTEGRATION.md** | Single source of truth for subsystem definitions; prevents semantic drift |
| **META_REGISTRY.yaml complements (not duplicates) manifest.yaml** | Different consumers: strategic navigation vs operational config |
| YAML over TOML | Project already uses YAML everywhere; consistency > optimal format |
| No automation initially | "Worse is better" - manual maintenance is fine until it isn't |
| No health checks | YAGNI - add when there's a consumer that needs them |
| Single file | Atomic, easy to version, no assembly needed |
| Directory paths allowed | `.agent/registry/active/` is a valid registry location |
| Archive location: `archive/agent_cuts/` | Centralized, dated, with MANIFEST for context |
| Subsystem ID references (S0-S7) | Enables traceability to canonical subsystem definitions |

---

## References

### Research Queries (Perplexity)
| File | Query Topic |
|------|-------------|
| `docs/research/perplexity/20260123_064049_*` | Registry of Registries patterns (DataHub, Consul, Schema Registry) |
| `docs/research/perplexity/20260123_065832_*` | Cutting complexity best practices |
| `docs/research/perplexity/20260123_070024_*` | Minimal viable registry patterns (Cargo.toml, package.json) |

### Analysis Queries (Gemini via analyze.py)
| File | Analysis Topic |
|------|----------------|
| `docs/research/gemini/docs/20260123_064244_*` | MRS design synthesis |
| `docs/research/gemini/docs/20260123_065122_*` | Critical evaluation (usefulness score 8/10) |
| `docs/research/gemini/docs/20260123_065929_*` | Cutting audit (files to archive/merge/simplify) |
| `docs/research/gemini/docs/20260123_070110_*` | Minimal META_REGISTRY proposal |
| `docs/research/gemini/docs/20260123_071446_*` | Alignment with repo truths and subsystems |

### Canonical Sources
| Document | Path |
|----------|------|
| SUBSYSTEM_INTEGRATION.md | `.agent/SUBSYSTEM_INTEGRATION.md` |
| manifest.yaml | `.agent/manifest.yaml` |
| repo_truths.yaml | `.agent/intelligence/truths/repo_truths.yaml` |
| REGISTRY_OF_REGISTRIES | `standard-model-of-code/docs/specs/REGISTRY_OF_REGISTRIES.md` |
| BARE Spec | `.agent/specs/BACKGROUND_AUTO_REFINEMENT_ENGINE.md` |

---

*"Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."* - Antoine de Saint-Exupery
