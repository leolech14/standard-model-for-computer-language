# MCP Configuration Deep Dive

> Critical knowledge about where MCP servers are configured in Claude Code.

## The Configuration Maze

Claude Code has multiple configuration files. This creates confusion about where MCP servers should be defined.

### File Hierarchy

```
~/.claude.json                    # MAIN CONFIG - MCP servers go here
├── mcpServers: {}                # Global MCP servers (all projects)
├── projects:
│   └── "/path/to/project":
│       └── mcpServers: {}        # Project-specific MCP servers

~/.claude/settings.json           # PERMISSIONS & SETTINGS - NOT for MCPs
├── permissions: {}
├── mcpServers: {}                # IGNORED! (Bug #4976)
└── enabledPlugins: {}

~/.claude/settings.local.json     # LOCAL OVERRIDES - NOT for MCPs

.mcp.json                         # PROJECT ROOT - Team-shared MCPs
└── mcpServers: {}                # Requires trust approval
```

---

## The Bug: settings.json is Ignored

**GitHub Issue:** [#4976](https://github.com/anthropics/claude-code/issues/4976)

### What Happens

```json
// ~/.claude/settings.json - THIS DOES NOT WORK
{
  "mcpServers": {
    "my-server": {
      "command": "python3",
      "args": ["/path/to/server.py"]
    }
  }
}
```

Result: Server is **never loaded**. Claude Code completely ignores this.

### Why It's Confusing

1. `settings.json` is the documented location for many settings
2. The file accepts `mcpServers` without error
3. No warning is shown that MCPs are ignored
4. Other settings in the same file DO work

### The Fix

```json
// ~/.claude.json - THIS WORKS
{
  "mcpServers": {
    "my-server": {
      "command": "python3",
      "args": ["/path/to/server.py"]
    }
  }
}
```

---

## Configuration Scopes

### Global (User-Level)

**File:** `~/.claude.json`
**Key:** `mcpServers` (top-level)

```json
{
  "mcpServers": {
    "global-server": {
      "type": "stdio",
      "command": "node",
      "args": ["/path/to/server.js"]
    }
  }
}
```

**Use for:** Servers you want in ALL projects.

### Project-Specific

**File:** `~/.claude.json`
**Key:** `projects["/path/to/project"].mcpServers`

```json
{
  "projects": {
    "/Users/me/my-project": {
      "mcpServers": {
        "project-server": {
          "type": "stdio",
          "command": "python3",
          "args": ["/path/to/server.py"]
        }
      }
    }
  }
}
```

**Use for:** Servers specific to one project but stored in your personal config.

### Team-Shared

**File:** `.mcp.json` (project root)

```json
{
  "mcpServers": {
    "shared-server": {
      "command": "/path/to/server",
      "args": []
    }
  }
}
```

**Use for:** Servers the whole team should have. Committed to git.

---

## Server Definition Schema

```json
{
  "server-name": {
    "type": "stdio",           // "stdio" or "http"
    "command": "python3",      // Executable
    "args": [                  // Arguments array
      "/path/to/server.py",
      "--flag",
      "value"
    ],
    "env": {                   // Environment variables
      "API_KEY": "secret",
      "DEBUG": "true"
    }
  }
}
```

### Type: stdio (Most Common)

- Server communicates via stdin/stdout
- Claude Code spawns the process
- JSON-RPC 2.0 messages

### Type: http

- Server runs as HTTP service
- Claude Code connects to URL
- Supports SSE for streaming

```json
{
  "http-server": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_KEY}"
    }
  }
}
```

---

## Precedence Rules

When the same server name exists in multiple locations:

1. **Project `.mcp.json`** (highest - team shared)
2. **Project-specific in `~/.claude.json`**
3. **Global in `~/.claude.json`** (lowest)

### Conflict Example

```
~/.claude.json:
  mcpServers.perplexity → npm package

~/.claude.json:
  projects["/my/project"].mcpServers.perplexity → local Python

.mcp.json:
  mcpServers.perplexity → team server
```

In `/my/project`: The `.mcp.json` version wins.

---

## CLI Commands

### Add Server (Recommended)

```bash
# Global scope
claude mcp add my-server --scope user -- python3 /path/to/server.py

# Project scope (stored in ~/.claude.json under projects)
claude mcp add my-server --scope project -- python3 /path/to/server.py

# With environment variables
claude mcp add my-server --scope user -e API_KEY=secret -- python3 /path/to/server.py
```

### List Servers

```bash
claude mcp list
```

### Remove Server

```bash
claude mcp remove my-server --scope user
```

### Add from JSON

```bash
claude mcp add-json my-server '{"type":"stdio","command":"python3","args":["/path/to/server.py"]}'
```

---

## Troubleshooting Checklist

When MCP server doesn't load:

- [ ] Check `~/.claude.json` (NOT `~/.claude/settings.json`)
- [ ] Verify JSON syntax is valid
- [ ] Check server name doesn't conflict with existing
- [ ] Verify command path is absolute
- [ ] Test server manually: `echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 server.py`
- [ ] Restart Claude Code after config changes
- [ ] Check `/mcp` command output in Claude Code

---

## Links

| Resource | Description |
|----------|-------------|
| [INDEX.md](../INDEX.md) | MCP Factory entry point |
| [GitHub #4976](https://github.com/anthropics/claude-code/issues/4976) | settings.json bug |
| [GitHub #3098](https://github.com/anthropics/claude-code/issues/3098) | Config inconsistency |
| [Claude Code MCP Docs](https://code.claude.com/docs/en/mcp) | Official documentation |

---

## Version History

| Date | Change |
|------|--------|
| 2026-01-22 | Initial creation from troubleshooting session |
