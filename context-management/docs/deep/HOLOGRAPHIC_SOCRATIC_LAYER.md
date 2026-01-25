# The Holographic-Socratic Layer

> **Holographic**: Every partial query reconstructs the whole truth.
> **Socratic**: Perpetual questioning that refines understanding.

**Implementation:** `analyze.py --verify` | **Integration:** `.agent/SUBSYSTEM_INTEGRATION.md`

## What Is It?

The Holographic-Socratic Layer is a **self-maintaining semantic validation system** that ensures codebase integrity against defined invariants (Antimatter Laws). Unlike static linters, it:

1. **Reconstructs context** from any partial query
2. **Questions continuously** via scheduled and file-triggered audits  
3. **Updates the single source of truth** with every run

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  semantic_models.yaml                        │
│              (The Single Source of Truth)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
   SCHEDULED          WATCHPATH            MANUAL
   (Daily 6AM)        (File Changes)       (--verify)
      │                    │                    │
      └────────────────────┴────────────────────┘
                           │
                           ▼
                 ┌─────────────────┐
                 │   analyze.py    │
                 │ SocraticValidator│
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ reports/latest  │
                 │ (Living Output) │
                 └─────────────────┘
```

## Commands

```bash
# Manual audit
python context-management/tools/ai/analyze.py --verify pipeline

# Audit specific file
python context-management/tools/ai/analyze.py --verify pipeline --candidate path/to/file.py

# View latest report
cat context-management/reports/socratic_audit_latest.md
```

## Antimatter Laws (Violations Detected)

| ID | Name | Description |
|----|------|-------------|
| AM001 | Context Myopia | Missing imports/definitions |
| AM002 | Architectural Drift | Layer boundary violations |
| AM003 | Supply Chain Hallucination | Phantom package imports |

## Automation

The layer runs automatically via LaunchAgent:

- **Agent**: `com.elements.socratic-audit`
- **Schedule**: Daily at 6:00 AM
- **Watch Triggers**: `semantic_models.yaml`, `src/core/`
- **Throttle**: 5 minutes (debounce during active editing)

```bash
# Check status
sentinel list | grep socratic

# Reload after editing plist
sentinel reload com.elements.socratic-audit
```

## Files

| File | Purpose |
|------|---------|
| `analyze.py` | Main tool with `--verify` mode |
| `semantic_models.yaml` | Antimatter Laws + Domain definitions |
| `socratic_audit_latest.md` | Living output report |
| `com.elements.socratic-audit.plist` | LaunchAgent config |
