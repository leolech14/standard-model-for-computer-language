# Git Hooks

Git hooks for PROJECT_elements.

## Installation

```bash
# Copy all hooks to .git/hooks/
cp .agent/hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

## Hooks

### post-commit (AUTOPILOT)

Runs after every commit via the **Autopilot** orchestrator:

1. **TDJ** - Updates Timestamp Daily Journal (temporal index)
2. **Trigger Engine** - Checks and executes macro triggers
3. **Circuit Breakers** - Graceful degradation if systems fail

**Features:**
- Lightweight execution (~100ms)
- Circuit breakers prevent cascade failures
- Graceful degradation (4 levels: FULL → PARTIAL → MANUAL → EMERGENCY)
- Idempotent (safe to run multiple times)

**Commands:**
```bash
.agent/tools/autopilot.py status    # Show all systems status
.agent/tools/autopilot.py disable   # Disable automation
.agent/tools/autopilot.py enable    # Re-enable automation
.agent/tools/autopilot.py health    # Deep health check
.agent/tools/autopilot.py recover   # Reset after failures
.agent/tools/autopilot.py run       # Manual full cycle
```

**Legacy Fallback:** If autopilot is unavailable, falls back to GCS mirror only.

## Adding New Hooks

1. Create the hook script in `.agent/hooks/`
2. Document it in this README
3. Copy to `.git/hooks/` and make executable
