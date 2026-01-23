#!/usr/bin/env python3
"""
{{SERVER_NAME}} MCP Server
{{DESCRIPTION}}

A local MCP server implementing the stdio protocol with:
- Deterministic auto-save pipeline (via DualFormatSaver)
- JSON-RPC 2.0 message handling
- Configurable API integration
- Comprehensive error handling

Pipeline:
    1. Receive query via JSON-RPC (stdin)
    2. Process request (call API, compute, etc.)
    3. DETERMINISTIC SAVE (if enabled):
       - raw/{timestamp}_{slug}.json  (full response + SHA-256 checksum)
       - docs/{timestamp}_{slug}.md   (human-readable markdown)
    4. Return response via JSON-RPC (stdout)

Usage:
    # Add to ~/.claude.json projects[path].mcpServers:
    "{{SERVER_ID}}": {
        "type": "stdio",
        "command": "python3",
        "args": ["/path/to/{{SERVER_ID}}_mcp_server.py"]
    }

Template Version: 1.0.0
Based on: perplexity_mcp_server.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# === Configuration ===
# Adjust these paths based on your project structure
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent  # Adjust depth as needed

# Server metadata
SERVER_NAME = "{{SERVER_NAME}}"
SERVER_ID = "{{SERVER_ID}}"
SERVER_VERSION = "1.0.0"

# Auto-save configuration
AUTO_SAVE_ENABLED = True  # Set to False to disable auto-save
RESEARCH_BASE = PROJECT_ROOT / "docs" / "research" / SERVER_ID  # Output directory

# Optional: Import DualFormatSaver for auto-save pipeline
SAVER = None
if AUTO_SAVE_ENABLED:
    try:
        # Add parent to path for utils import
        sys.path.insert(0, str(SCRIPT_DIR.parent.parent))
        from utils.output_formatters import DualFormatSaver
        SAVER = DualFormatSaver(base_path=RESEARCH_BASE)
    except ImportError:
        sys.stderr.write(f"[{SERVER_ID}] Warning: DualFormatSaver not available, auto-save disabled\n")
        AUTO_SAVE_ENABLED = False


# === API Key Management ===
def get_api_key(key_name: str) -> str:
    """
    Get API key from Doppler or environment.

    Args:
        key_name: Name of the secret (e.g., "OPENAI_API_KEY")

    Returns:
        API key string

    Raises:
        ValueError: If key not found in any source
    """
    # Try Doppler first (recommended for production)
    try:
        result = subprocess.run(
            ["doppler", "secrets", "get", key_name, "--plain",
             "--project", "ai-tools", "--config", "dev"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    # Fall back to environment variable
    key = os.environ.get(key_name)
    if key:
        return key

    raise ValueError(f"No {key_name} found in Doppler or environment")


# === Auto-Save Pipeline ===
def auto_save_response(query: str, response: Dict[str, Any], model: str = "default") -> str:
    """
    Save response using DualFormatSaver if enabled.

    Args:
        query: Original query text
        response: Full API response dict
        model: Model name for metadata

    Returns:
        Save note string to append to response
    """
    if not AUTO_SAVE_ENABLED or SAVER is None:
        return ""

    try:
        result = SAVER.save(
            query=query,
            response=response,
            source=f"{SERVER_ID}-mcp",
            model=model
        )
        return (
            f"\n\n---\n"
            f"_Auto-saved (SHA-256: {result.checksum[:20]}...):_\n"
            f"- Raw: `{result.raw_path.relative_to(PROJECT_ROOT)}`\n"
            f"- Doc: `{result.md_path.relative_to(PROJECT_ROOT)}`"
        )
    except Exception as e:
        return f"\n\n---\n_Auto-save failed: {e}_"


# === MCP Protocol Implementation ===
def read_message() -> Optional[Dict[str, Any]]:
    """
    Read a JSON-RPC message from stdin.

    Returns:
        Parsed message dict, or None if stdin closed
    """
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)


def write_message(msg: Dict[str, Any]) -> None:
    """
    Write a JSON-RPC message to stdout.

    Args:
        msg: Message dict to serialize and write
    """
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle_initialize(_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle MCP initialize request.

    Args:
        params: Initialize parameters from client

    Returns:
        Server capabilities and info
    """
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": SERVER_ID,
            "version": SERVER_VERSION
        }
    }


def handle_tools_list() -> Dict[str, Any]:
    """
    Return available tools.

    Returns:
        Dict with "tools" list containing tool definitions
    """
    return {
        "tools": [
            # === DEFINE YOUR TOOLS HERE ===
            {
                "name": f"{SERVER_ID}_query",
                "description": f"Query {SERVER_NAME}. Returns processed response.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query to process"
                        },
                        "options": {
                            "type": "object",
                            "description": "Optional parameters",
                            "properties": {
                                "model": {"type": "string", "description": "Model to use"},
                                "format": {"type": "string", "description": "Output format"}
                            }
                        }
                    },
                    "required": ["query"]
                }
            },
            # Add more tools as needed
        ]
    }


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a tool call.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        Tool result with content array
    """
    try:
        # === IMPLEMENT YOUR TOOL HANDLERS HERE ===
        if name == f"{SERVER_ID}_query":
            return handle_query_tool(arguments)
        else:
            return {
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                "isError": True
            }

    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }


def handle_query_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the main query tool.

    Args:
        arguments: Tool arguments containing query and options

    Returns:
        Tool result
    """
    query = arguments.get("query", "")
    options = arguments.get("options", {})
    model = options.get("model", "default")

    # === IMPLEMENT YOUR LOGIC HERE ===
    # Example: Call an external API
    # response = call_external_api(query, model)

    # Placeholder response
    response = {
        "result": f"Processed query: {query}",
        "model": model,
        "metadata": {}
    }

    # Auto-save if enabled
    save_note = auto_save_response(query, response, model)

    # Format response text
    response_text = response.get("result", "No result")
    response_text += save_note

    return {"content": [{"type": "text", "text": response_text}]}


# === Main Server Loop ===
def main():
    """Main MCP server loop."""
    # Log startup
    sys.stderr.write(f"[{SERVER_ID}] Starting MCP server v{SERVER_VERSION}\n")
    if AUTO_SAVE_ENABLED and SAVER:
        sys.stderr.write(f"[{SERVER_ID}] Auto-save enabled: {RESEARCH_BASE}\n")
    else:
        sys.stderr.write(f"[{SERVER_ID}] Auto-save disabled\n")
    sys.stderr.flush()

    while True:
        msg_id = None
        try:
            msg = read_message()
            if msg is None:
                break

            method = msg.get("method", "")
            params = msg.get("params", {})
            msg_id = msg.get("id")

            # Route to appropriate handler
            if method == "initialize":
                result = handle_initialize(params)
            elif method == "initialized":
                continue  # Notification, no response needed
            elif method == "tools/list":
                result = handle_tools_list()
            elif method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = handle_tool_call(tool_name, arguments)
            else:
                result = {"error": {"code": -32601, "message": f"Method not found: {method}"}}

            # Send response if request had an ID
            if msg_id is not None:
                write_message({"jsonrpc": "2.0", "id": msg_id, "result": result})

        except json.JSONDecodeError as e:
            sys.stderr.write(f"[{SERVER_ID}] JSON parse error: {e}\n")
            sys.stderr.flush()
            if msg_id is not None:
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32700, "message": f"Parse error: {e}"}
                })
        except Exception as e:
            sys.stderr.write(f"[{SERVER_ID}] Error: {e}\n")
            sys.stderr.flush()
            if msg_id is not None:
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32603, "message": str(e)}
                })


if __name__ == "__main__":
    main()
