# MCP Server Best Practices

> Guidelines for building Python MCP servers in this project.
> Based on: perplexity_mcp_server.py (reference implementation)

---

## Architecture

### Directory Structure

```
context-management/tools/mcp/
├── mcp_factory/
│   ├── templates/
│   │   └── python_stdio_server.py    # Base template
│   ├── scaffold.py                   # Generator script
│   ├── BEST_PRACTICES.md             # This file
│   └── core/                         # Shared utilities
│       └── server.py
├── perplexity_mcp_server.py          # Reference implementation
├── {new_server}_mcp_server.py        # Generated servers
└── ...
```

### Server Naming

| Component | Convention | Example |
|-----------|------------|---------|
| File | `{id}_mcp_server.py` | `weather_mcp_server.py` |
| Server ID | snake_case | `weather`, `code_search` |
| Server Name | Title Case | `Weather`, `Code Search` |

---

## Protocol Implementation

### Required Methods

Every MCP server must handle:

```python
def handle_initialize(params) -> dict:
    """Return server capabilities."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": SERVER_ID, "version": SERVER_VERSION}
    }

def handle_tools_list() -> dict:
    """Return available tools."""
    return {"tools": [...]}

def handle_tool_call(name, arguments) -> dict:
    """Execute a tool and return result."""
    return {"content": [{"type": "text", "text": result}]}
```

### Message Format

MCP uses JSON-RPC 2.0 over stdio:

```python
# Reading (stdin)
{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}

# Writing (stdout)
{"jsonrpc": "2.0", "id": 1, "result": {...}}

# Error response
{"jsonrpc": "2.0", "id": 1, "error": {"code": -32603, "message": "..."}}
```

---

## Tool Definition

### Schema Pattern

```python
{
    "name": "server_action",           # {server_id}_{action}
    "description": "Clear description with auto-save note",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "What to process"
            },
            "options": {
                "type": "object",
                "description": "Optional parameters"
            }
        },
        "required": ["query"]
    }
}
```

### Return Format

```python
def handle_tool_call(name, arguments):
    # Success
    return {
        "content": [{"type": "text", "text": "Result text"}]
    }

    # Error
    return {
        "content": [{"type": "text", "text": f"Error: {msg}"}],
        "isError": True
    }
```

---

## Auto-Save Pipeline

### Purpose

**Zero information loss.** Every API response is persisted:
- `raw/{timestamp}_{slug}.json` - Full response with SHA-256 checksum
- `docs/{timestamp}_{slug}.md` - Human-readable markdown

### Implementation

```python
from utils.output_formatters import DualFormatSaver

SAVER = DualFormatSaver(base_path=RESEARCH_BASE)

def auto_save_response(query, response, model):
    result = SAVER.save(
        query=query,
        response=response,
        source=f"{SERVER_ID}-mcp",
        model=model
    )
    return f"_Auto-saved: {result.md_path.name}_"
```

### When to Save

- **Always:** API responses (external data)
- **Optional:** Computed results (can be regenerated)
- **Never:** Errors, empty responses

---

## API Key Management

### Priority Order

1. **Doppler** (production) - Recommended
2. **Environment variable** - Fallback
3. **Fail** - Never hardcode keys

```python
def get_api_key(key_name: str) -> str:
    # Try Doppler first
    try:
        result = subprocess.run(
            ["doppler", "secrets", "get", key_name, "--plain",
             "--project", "ai-tools", "--config", "dev"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    # Fall back to environment
    key = os.environ.get(key_name)
    if key:
        return key

    raise ValueError(f"No {key_name} found")
```

---

## Error Handling

### Logging

Use stderr for logs (stdout is reserved for JSON-RPC):

```python
sys.stderr.write(f"[{SERVER_ID}] Info message\n")
sys.stderr.flush()
```

### Error Responses

```python
try:
    result = process_request(...)
except SpecificError as e:
    return {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
except Exception as e:
    sys.stderr.write(f"[{SERVER_ID}] Unexpected: {e}\n")
    return {"content": [{"type": "text", "text": "Internal error"}], "isError": True}
```

---

## Testing

### Manual Testing

```bash
# Start server
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python my_server.py

# List tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python my_server.py

# Call tool
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"my_tool","arguments":{"query":"test"}}}' | python my_server.py
```

### Claude Integration Testing

Add to `~/.claude.json`:
```json
{
    "projects": {
        "/path/to/project": {
            "mcpServers": {
                "my_server": {
                    "type": "stdio",
                    "command": "python3",
                    "args": ["/path/to/my_server_mcp_server.py"]
                }
            }
        }
    }
}
```

---

## Checklist

### Before Release

- [ ] Server starts without errors
- [ ] `initialize` returns valid capabilities
- [ ] `tools/list` returns valid tool definitions
- [ ] Each tool handles success and error cases
- [ ] Auto-save pipeline works (if applicable)
- [ ] API keys retrieved from Doppler/env
- [ ] Logs go to stderr, not stdout
- [ ] No hardcoded secrets

### Documentation

- [ ] Docstring in server file
- [ ] Tool descriptions are clear
- [ ] Usage example in comments

---

## Quick Reference

### Scaffold New Server

```bash
cd context-management/tools/mcp/mcp_factory
python scaffold.py my_service "My service description"
```

### Template Variables

| Variable | Replaced With |
|----------|---------------|
| `{{SERVER_NAME}}` | Title Case name |
| `{{SERVER_ID}}` | snake_case ID |
| `{{DESCRIPTION}}` | One-line description |

### Common Imports

```python
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any
```

---

## Version

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Created | 2026-01-23 |
| Reference | perplexity_mcp_server.py |
