# Drift Guard Setup (launchd)

## Overview

The Drift Guard (SMoC Role: Guard) runs periodic code analysis audits to detect semantic drift. It requires `GEMINI_API_KEY` to function.

## Installation

The Drift Guard is managed via macOS launchd and automatically started at boot.

### Prerequisites

1. Virtual environment: `.tools_venv`
2. Doppler configured: `doppler setup --project ai-tools --config dev`
3. `GEMINI_API_KEY` available from Doppler

### Setup Steps

1. **Get the API key:**
   ```bash
   doppler secrets get GEMINI_API_KEY --plain --project ai-tools --config dev
   ```

2. **Create the launchd plist:**
   - File: `~/Library/LaunchAgents/com.elements.hsl.plist`
   - Template: See below
   - Replace `INSERT_KEY_HERE` with actual key from step 1

3. **Load the service:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.elements.hsl.plist
   ```

### Launchd Plist Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.elements.hsl</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/lech/PROJECTS_all/PROJECT_elements/.tools_venv/bin/python</string>
        <string>/Users/lech/PROJECTS_all/PROJECT_elements/context-management/tools/drift_guard.py</string>
        <string>--once</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>EnvironmentVariables</key>
    <dict>
        <key>GEMINI_API_KEY</key>
        <string>INSERT_KEY_HERE</string>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/drift_guard.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/drift_guard.err</string>
    <key>WorkingDirectory</key>
    <string>/Users/lech/PROJECTS_all/PROJECT_elements</string>
</dict>
</plist>
```

## Verification

Test the daemon runs successfully:

```bash
/Users/lech/PROJECTS_all/PROJECT_elements/.tools_venv/bin/python \
  /Users/lech/PROJECTS_all/PROJECT_elements/context-management/tools/drift_guard.py --once
```

Expected output:
```
[timestamp] ✅ Audit completed successfully
```

## Management

### View status:
```bash
launchctl list | grep hsl
```

### View logs:
```bash
tail -f /tmp/drift_guard.out
tail -f /tmp/drift_guard.err
```

### Reload (after plist changes):
```bash
launchctl unload ~/Library/LaunchAgents/com.elements.hsl.plist
launchctl load ~/Library/LaunchAgents/com.elements.hsl.plist
```

### Disable temporarily:
```bash
launchctl unload ~/Library/LaunchAgents/com.elements.hsl.plist
```

### Re-enable:
```bash
launchctl load ~/Library/LaunchAgents/com.elements.hsl.plist
```

## Troubleshooting

### Daemon not running
1. Check plist syntax: `plutil -lint ~/Library/LaunchAgents/com.elements.hsl.plist`
2. View error logs: `cat /tmp/drift_guard.err`
3. Re-load service: `launchctl unload ... && launchctl load ...`

### API key errors
- Verify key is set in plist: `grep -A 1 GEMINI_API_KEY ~/Library/LaunchAgents/com.elements.hsl.plist`
- Test manually: `GEMINI_API_KEY="..." python context-management/tools/drift_guard.py --once`

### Missing dependencies
- Ensure `.tools_venv` is activated and dependencies installed
- Run: `pip install -e .` from `standard-model-of-code/`

## Environment Variables

The plist injects `GEMINI_API_KEY` via `EnvironmentVariables` section. This is more reliable than shell startup files (.bashrc, .zshrc) which launchd bypasses.

### Why not use shell?
- launchd runs agents directly, not through a shell
- No shell initialization files are sourced
- Must specify env vars in plist explicitly

### Why not use Doppler in launchd?
- Doppler requires shell invocation which is complex in launchd
- Storing key directly avoids subprocess overhead
- Secret is already protected by system keychain policies

## Security Notes

1. The API key is stored in plaintext in the plist file
2. File permissions: `-rw-r--r--` (standard for LaunchAgent configs)
3. Consider replacing with Doppler injection once it's integrated with launchd
4. Rotate API key periodically via Doppler

## Related Files

- Drift Guard: `context-management/tools/drift_guard.py`
- Analysis tool: `context-management/tools/ai/analyze.py`
- State file: `context-management/intelligence/drift_guard_state.json`
