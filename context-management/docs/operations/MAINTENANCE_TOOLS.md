# Maintenance Tools

**Status:** ACTIVE
**Location:** `context-management/tools/maintenance/` and `context-management/tools/ai/`

---

## Overview

The Maintenance Layer provides automated health checks and diagnostics for PROJECT_elements. These tools integrate into the boot sequence and can be run independently.

## Tools

### 1. Boundary Analyzer

**Purpose:** Validates that declared boundaries (CODOME/CONTEXTOME/DOMAINS) match actual directory structure.

**Location:** `context-management/tools/maintenance/boundary_analyzer.py`

```bash
# Full analysis with verbose output
python3 boundary_analyzer.py --verbose

# Quick check (exit code only, for CI)
python3 boundary_analyzer.py --quick

# Save report to .agent/intelligence/
python3 boundary_analyzer.py --save

# JSON output for automation
python3 boundary_analyzer.py --json

# Set custom threshold (default: 70)
python3 boundary_analyzer.py --threshold 80
```

**Output:** `.agent/intelligence/boundary_analysis.json`

**Checks:**
- Realm existence (PARTICLE, WAVE, OBSERVER)
- Domain symmetry (code + docs for each domain)
- Undeclared directories
- Phantom declarations (declared but missing)
- CODOME/CONTEXTOME partition integrity

**Score Components:**
| Component | Weight | Description |
|-----------|--------|-------------|
| Realm Health | 30 | All three realms exist and populated |
| Domain Health | 40 | Domains have symmetric code/docs |
| Issue Deductions | 20 | Penalties for issues by severity |
| Declaration Ratio | 10 | Percentage of directories declared |

---

### 2. Gemini Status

**Purpose:** Real-time observability for Gemini API usage, quotas, and error diagnosis.

**Location:** `context-management/tools/ai/gemini_status.py`

```bash
# Show current status
python3 gemini_status.py

# Diagnose specific error
python3 gemini_status.py --error "429 RESOURCE_EXHAUSTED..."

# Continuous monitoring (refreshes every 10s)
python3 gemini_status.py --watch

# Show model recommendations
python3 gemini_status.py --recommend
```

**Tracks:**
- Total calls today
- Success/failure ratio
- Token usage (input/output)
- Per-model breakdown
- Rate status (last minute)
- Quota consumption

**Diagnoses:**
- 429 RESOURCE_EXHAUSTED errors
- Input token quota exceeded
- Request rate limits
- Retry delay extraction

---

### 3. Boot Script

**Purpose:** Agent initialization with health checks.

**Location:** `context-management/tools/maintenance/boot.sh`

```bash
# Run full boot sequence
bash context-management/tools/maintenance/boot.sh

# JSON output only (for automation)
bash context-management/tools/maintenance/boot.sh --json
```

**Sequence:**
1. Update timestamps CSV
2. Detect git status
3. Auto-detect commands (test, lint, build, run)
4. **Run boundary analyzer**
5. **Check Gemini API status**
6. Generate INITIATION_REPORT

---

## Integration Points

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: boundary-check
      name: Boundary Alignment Check
      entry: python3 context-management/tools/maintenance/boundary_analyzer.py --quick --threshold 60
      language: system
      pass_filenames: false
```

### CI Pipeline

```yaml
# GitHub Actions example
jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Boundary Analysis
        run: python3 context-management/tools/maintenance/boundary_analyzer.py --json --threshold 70
```

### Agent Boot

Called automatically by `boot.sh` during agent initialization.

---

## Output Locations

| Tool | Output File |
|------|-------------|
| Boundary Analyzer | `.agent/intelligence/boundary_analysis.json` |
| Gemini Status | (stdout only) |
| Boot Script | (stdout + INITIATION_REPORT JSON) |

---

## Troubleshooting

### Boundary Score Too Low

1. Check which directories are undeclared:
   ```bash
   python3 boundary_analyzer.py --verbose | grep UNDECLARED
   ```

2. Either:
   - Add to `EXPECTED_DIRECTORIES` in `boundary_analyzer.py`
   - Add to `.agent/CODOME_MANIFEST.yaml`
   - Add to `DOMAINS.md`

### Gemini 429 Errors

1. Check current status:
   ```bash
   python3 gemini_status.py
   ```

2. If rate limited:
   - Wait the specified retry delay
   - Or use `--model gemini-2.5-flash` (higher limits)

3. If daily quota exhausted:
   - Wait until tomorrow
   - Or upgrade to paid tier

---

## Traceability

| Reference | Location |
|-----------|----------|
| This doc | `context-management/docs/operations/MAINTENANCE_TOOLS.md` |
| Boundary Analyzer | `context-management/tools/maintenance/boundary_analyzer.py` |
| Gemini Status | `context-management/tools/ai/gemini_status.py` |
| Boot Script | `context-management/tools/maintenance/boot.sh` |
| Boundary Report | `.agent/intelligence/boundary_analysis.json` |
| CODOME/CONTEXTOME specs | `context-management/docs/CODOME.md`, `CONTEXTOME.md` |
| DOMAINS spec | `context-management/docs/DOMAINS.md` |

---

*Created: 2026-01-25*
*Part of: Maintenance Layer / Wave Realm*
