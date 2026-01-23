# MCP Troubleshooting Guide

> Systematic approaches to debugging MCP server issues.

## Decision Tree

```
MCP server not working?
│
├─► Is server code correct?
│   └─► Test: echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 server.py
│       ├─► No response? → Server crash, check stderr
│       └─► Response OK? → Config issue, continue ↓
│
├─► Is config in correct file?
│   ├─► ~/.claude/settings.json? → WRONG! Move to ~/.claude.json
│   └─► ~/.claude.json? → Continue ↓
│
├─► Is config at correct key?
│   ├─► Global? → mcpServers (top-level)
│   └─► Project? → projects["/path"].mcpServers
│
├─► Is there a naming conflict?
│   ├─► Same name in .mcp.json? → .mcp.json wins
│   └─► Same name from npm package? → Check project config
│
└─► Did you restart Claude Code?
    └─► MCP changes require restart
```

---

## Common Issues

### Issue: Server Added But Not Loading

**Symptoms:**
- `claude mcp list` shows server
- Server tools not available in Claude Code
- Different server with same name being used

**Diagnosis:**
```bash
# Check what's actually configured
cat ~/.claude.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get('mcpServers',{}), indent=2))"

# Check project-specific
cat ~/.claude.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get('projects',{}).get('$(pwd)',{}).get('mcpServers',{}), indent=2))"
```

**Solution:**
Check for conflicting definitions at different scopes.

---

### Issue: Config in settings.json Ignored

**Symptoms:**
- Added server to `~/.claude/settings.json`
- Server never loads
- No error messages

**Root Cause:**
Bug #4976 - settings.json mcpServers key is ignored.

**Solution:**
Move config to `~/.claude.json`:

```bash
# Extract from wrong location
cat ~/.claude/settings.json | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin).get('mcpServers',{}), indent=2))"

# Add to correct location (manually edit ~/.claude.json)
```

---

### Issue: Server Crashes on Startup

**Symptoms:**
- Server listed but marked as failed
- No tools available

**Diagnosis:**
```bash
# Test server directly
python3 /path/to/server.py 2>&1

# Send initialize request
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 /path/to/server.py 2>&1
```

**Common Causes:**
1. Missing dependencies (`pip install` needed)
2. Missing environment variables
3. Syntax error in server code
4. Permission issues on executable

---

### Issue: Environment Variables Not Passed

**Symptoms:**
- Server starts but API calls fail
- "API key not found" errors

**Diagnosis:**
```bash
# Check config has env
cat ~/.claude.json | grep -A 10 "my-server"
```

**Solution:**
Add env to server config:

```json
{
  "my-server": {
    "command": "python3",
    "args": ["/path/to/server.py"],
    "env": {
      "API_KEY": "your-key-here"
    }
  }
}
```

**Alternative:** Use Doppler or other secret managers in server code.

---

### Issue: Project-Specific Server Used Globally

**Symptoms:**
- Server works in one project
- Same server name doesn't work elsewhere

**Root Cause:**
Server defined under `projects["/specific/path"].mcpServers`

**Solution:**
Move to global `mcpServers` if needed everywhere:

```bash
# Move from project-specific to global in ~/.claude.json
```

---

## Verification Commands

### Check Server Status

```bash
# In Claude Code
/mcp
```

### Test Server Manually

```bash
# Initialize
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 server.py

# List tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python3 server.py

# Call tool
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"tool_name","arguments":{}}}' | python3 server.py
```

### Verify Config File

```bash
# Validate JSON syntax
python3 -m json.tool ~/.claude.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON"

# Pretty print
python3 -m json.tool ~/.claude.json
```

---

## Debug Logging

### Add Logging to Server

```python
import sys

def log(msg):
    sys.stderr.write(f"[my-server] {msg}\n")
    sys.stderr.flush()

log("Server starting...")
log(f"Config loaded: {config}")
```

Stderr output visible in Claude Code logs.

### Check Claude Code Logs

```bash
# macOS
tail -f ~/Library/Logs/Claude\ Code/*.log

# Or check terminal output when running claude
```

---

## Case Study: Perplexity Server (2026-01-22)

### Timeline

| Time | Action | Result |
|------|--------|--------|
| T+0 | Created `perplexity_mcp_server.py` | Server code working |
| T+5 | Added to `~/.claude/settings.json` | **IGNORED** |
| T+10 | Restarted Claude Code | External npm package used |
| T+15 | Searched for config issues | Found bug #4976 |
| T+20 | Checked `~/.claude.json` | Found project-specific npm config |
| T+25 | Updated project mcpServers | Local server now active |
| T+30 | Tested auto-save | **SUCCESS** |

### Key Learnings

1. **Always use `claude mcp add`** - it knows the right file
2. **Check `~/.claude.json`** - both global AND project-specific
3. **Naming conflicts** - project config can override with different server
4. **Restart required** - always restart after config changes

---

## Links

| Resource | Description |
|----------|-------------|
| [INDEX.md](../INDEX.md) | MCP Factory entry point |
| [CONFIGURATION.md](./CONFIGURATION.md) | Config deep dive |
| [EXTERNAL_LINKS.md](./EXTERNAL_LINKS.md) | External resources |
