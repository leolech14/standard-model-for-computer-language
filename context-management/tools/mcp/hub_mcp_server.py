#!/usr/bin/env python3
"""
Elements Hub MCP Server
=======================

Exposes Elements Hub (RegistryOfRegistries + EventBus + Plugins) via MCP protocol.

AI agents can:
- Query registries (atoms, roles, patterns, schemas)
- Check system health
- List available events
- (Future) Classify code, emit events

Usage:
    # Test locally
    echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 hub_mcp_server.py

    # Add to ~/.claude.json:
    "elements-hub": {
        "type": "stdio",
        "command": "python3",
        "args": ["/full/path/to/hub_mcp_server.py"]
    }

Part of: MODULAR_ARCHITECTURE_SYNTHESIS.md
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
SMOC_SRC = PROJECT_ROOT / "standard-model-of-code" / "src"

sys.path.insert(0, str(SMOC_SRC))

# Import Hub
from core.registry.registry_of_registries import get_meta_registry


# === MCP Protocol Helpers ===
def read_message() -> Optional[dict]:
    """Read JSON-RPC message from stdin."""
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)


def write_message(msg: dict):
    """Write JSON-RPC message to stdout."""
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


# === MCP Handlers ===
def handle_initialize(_params: dict) -> dict:
    """Handle MCP initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {
            "name": "elements-hub",
            "version": "1.0.0"
        }
    }


def handle_tools_list() -> dict:
    """Return available tools."""
    return {
        "tools": [
            {
                "name": "hub_status",
                "description": "Get Hub health status (registries, event bus, services)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "list_roles",
                "description": "List all 33 canonical roles in the Standard Model",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_role_info",
                "description": "Get detailed information about a specific role",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "role": {
                            "type": "string",
                            "description": "Role name to lookup"
                        }
                    },
                    "required": ["role"]
                }
            },
            {
                "name": "query_atoms",
                "description": "Query the Atom Registry (3,525 atoms: 80 core + 3,445 T2)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tier": {
                            "type": "string",
                            "description": "Filter by tier (T0, T1, T2)",
                            "enum": ["T0", "T1", "T2"]
                        },
                        "limit": {
                            "type": "number",
                            "description": "Max results (default 50)",
                            "default": 50
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "list_events",
                "description": "List all registered events on the EventBus",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_patterns",
                "description": "Get role detection patterns (prefix, suffix, base classes)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    }


def handle_tool_call(name: str, arguments: dict, hub) -> dict:
    """Route tool calls to Hub methods."""
    try:
        if name == "hub_status":
            status = hub.status_report()
            registries = hub.list_registries()
            return {
                "content": [{
                    "type": "text",
                    "text": f"# Hub Status\n\n" +
                           f"Registries: {', '.join(registries)}\n\n" +
                           "\n".join([f"- **{k}**: {v}" for k, v in status.items()])
                }]
            }

        elif name == "list_roles":
            roles = hub.get('roles')
            if not roles:
                return {"content": [{"type": "text", "text": "RoleRegistry not available"}], "isError": True}

            role_names = roles.list_names()
            count = roles.count()
            return {
                "content": [{
                    "type": "text",
                    "text": f"# Canonical Roles ({count})\n\n" +
                           "\n".join([f"- {role}" for role in role_names])
                }]
            }

        elif name == "get_role_info":
            role_name = arguments.get('role')
            if not role_name:
                return {"content": [{"type": "text", "text": "Missing 'role' parameter"}], "isError": True}

            roles = hub.get('roles')
            if not roles:
                return {"content": [{"type": "text", "text": "RoleRegistry not available"}], "isError": True}

            canonical = roles.get_canonical(role_name)
            is_canonical = roles.is_canonical(role_name)

            return {
                "content": [{
                    "type": "text",
                    "text": f"# Role: {role_name}\n\n" +
                           f"**Canonical Form**: {canonical}\n" +
                           f"**Is Canonical**: {is_canonical}\n"
                }]
            }

        elif name == "query_atoms":
            atoms = hub.get('atoms')
            if not atoms:
                return {"content": [{"type": "text", "text": "AtomRegistry not available"}], "isError": True}

            tier = arguments.get('tier')
            limit = arguments.get('limit', 50)

            if tier == 'T2':
                results = list(atoms.t2_atoms.keys())[:limit]
                total = len(atoms.t2_atoms)
            else:
                results = [a.name for a in atoms.atoms.values()][:limit]
                total = len(atoms.atoms)

            return {
                "content": [{
                    "type": "text",
                    "text": f"# Atoms ({total} total, showing {len(results)})\n\n" +
                           "\n".join([f"- {atom}" for atom in results])
                }]
            }

        elif name == "list_events":
            events = hub.event_bus.get_events()
            counts = {
                event: hub.event_bus.get_handler_count(event)
                for event in events
            }

            return {
                "content": [{
                    "type": "text",
                    "text": f"# Registered Events ({len(events)})\n\n" +
                           "\n".join([f"- **{e}** ({counts[e]} handlers)" for e in events])
                }]
            }

        elif name == "get_patterns":
            patterns = hub.get('patterns')
            if not patterns:
                return {"content": [{"type": "text", "text": "PatternRegistry not available"}], "isError": True}

            prefix = patterns.get_prefix_patterns()
            suffix = patterns.get_suffix_patterns()

            return {
                "content": [{
                    "type": "text",
                    "text": f"# Role Detection Patterns\n\n" +
                           f"## Prefix Patterns ({len(prefix)})\n" +
                           "\n".join([f"- **{k}**: {', '.join(v)}" for k, v in list(prefix.items())[:10]]) +
                           f"\n\n## Suffix Patterns ({len(suffix)})\n" +
                           "\n".join([f"- **{k}**: {', '.join(v)}" for k, v in list(suffix.items())[:10]])
                }]
            }

        else:
            return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def main():
    """Main MCP server loop."""
    # Log startup
    sys.stderr.write("[elements-hub] Starting MCP server\n")
    sys.stderr.flush()

    # Initialize Hub
    hub = get_meta_registry()
    sys.stderr.write(f"[elements-hub] Hub initialized with {len(hub.list_registries())} registries\n")
    sys.stderr.flush()

    # Main loop
    while True:
        msg_id = None
        try:
            msg = read_message()
            if msg is None:
                break

            method = msg.get("method", "")
            params = msg.get("params", {})
            msg_id = msg.get("id")

            if method == "initialize":
                result = handle_initialize(params)
            elif method == "initialized":
                continue  # Notification, no response
            elif method == "tools/list":
                result = handle_tools_list()
            elif method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = handle_tool_call(tool_name, arguments, hub)
            else:
                result = {"error": {"code": -32601, "message": f"Method not found: {method}"}}

            if msg_id is not None:
                write_message({"jsonrpc": "2.0", "id": msg_id, "result": result})

        except Exception as e:
            sys.stderr.write(f"[elements-hub] Error: {e}\n")
            sys.stderr.flush()
            if msg_id is not None:
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32603, "message": str(e)}
                })


if __name__ == "__main__":
    main()
