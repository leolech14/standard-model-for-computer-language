#!/usr/bin/env python3
"""
Perplexity MCP Server with Auto-Save

A local MCP server that wraps Perplexity API and auto-saves all research
to standard-model-of-code/docs/research/perplexity/

This replaces the external Perplexity MCP server to ensure all research
is persisted to the repository.

Usage:
    # Add to ~/.claude/settings.json mcpServers:
    "perplexity-local": {
        "command": "python3",
        "args": ["/path/to/perplexity_mcp_server.py"]
    }
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# === Configuration ===
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
RESEARCH_DIR = PROJECT_ROOT / "standard-model-of-code" / "docs" / "research" / "perplexity"

# === API Key Management ===
def get_api_key() -> str:
    """Get Perplexity API key from Doppler or environment."""
    # Try Doppler first
    try:
        result = subprocess.run(
            ["doppler", "secrets", "get", "PERPLEXITY_API_KEY", "--plain",
             "--project", "ai-tools", "--config", "dev"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    # Fall back to environment
    key = os.environ.get("PERPLEXITY_API_KEY")
    if key:
        return key

    raise ValueError("No PERPLEXITY_API_KEY found in Doppler or environment")


# === Auto-Save ===
def auto_save_research(query: str, result: dict, model: str) -> Path:
    """Auto-save research output to the standard location."""
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = "".join(c if c.isalnum() else "_" for c in query[:50]).strip("_").lower()
    filename = f"{timestamp}_{slug}.md"

    content = f"""# Perplexity Research: {query[:100]}{'...' if len(query) > 100 else ''}

> **Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> **Model:** {model}
> **Source:** MCP Server (auto-saved)

---

## Query

{query}

---

## Response

{result.get('content', 'No content')}

---

## Citations

"""
    citations = result.get('citations', [])
    if citations:
        for i, citation in enumerate(citations, 1):
            content += f"{i}. {citation}\n"
    else:
        content += "_No citations provided_\n"

    filepath = RESEARCH_DIR / filename
    filepath.write_text(content)
    return filepath


# === Perplexity API ===
def call_perplexity(messages: list, model: str = "sonar-pro") -> dict:
    """Call Perplexity API."""
    import httpx

    api_key = get_api_key()

    response = httpx.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": messages,
            "return_citations": True
        },
        timeout=300.0
    )
    response.raise_for_status()
    return response.json()


# === MCP Protocol ===
def read_message() -> Optional[dict]:
    """Read a JSON-RPC message from stdin."""
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)


def write_message(msg: dict):
    """Write a JSON-RPC message to stdout."""
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle_initialize(_params: dict) -> dict:
    """Handle initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "perplexity-local",
            "version": "1.0.0"
        }
    }


def handle_tools_list() -> dict:
    """Return available tools."""
    return {
        "tools": [
            {
                "name": "perplexity_ask",
                "description": "Ask Perplexity a question. Auto-saves response to docs/research/perplexity/",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "messages": {
                            "type": "array",
                            "description": "Array of conversation messages",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"},
                                    "content": {"type": "string"}
                                },
                                "required": ["role", "content"]
                            }
                        }
                    },
                    "required": ["messages"]
                }
            },
            {
                "name": "perplexity_research",
                "description": "Deep research using Perplexity. Auto-saves response to docs/research/perplexity/",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "messages": {
                            "type": "array",
                            "description": "Array of conversation messages",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"},
                                    "content": {"type": "string"}
                                },
                                "required": ["role", "content"]
                            }
                        }
                    },
                    "required": ["messages"]
                }
            },
            {
                "name": "perplexity_search",
                "description": "Web search using Perplexity. Auto-saves response to docs/research/perplexity/",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    }


def handle_tool_call(name: str, arguments: dict) -> dict:
    """Handle a tool call."""
    try:
        if name == "perplexity_ask":
            messages = arguments.get("messages", [])
            model = "sonar-pro"
        elif name == "perplexity_research":
            messages = arguments.get("messages", [])
            model = "sonar-deep-research"
        elif name == "perplexity_search":
            query = arguments.get("query", "")
            messages = [{"role": "user", "content": query}]
            model = "sonar-pro"
        else:
            return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

        # Extract query for saving
        query_text = messages[-1].get("content", "") if messages else ""

        # Call Perplexity
        response = call_perplexity(messages, model)

        # Extract result
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        citations = response.get("citations", [])

        result = {
            "content": content,
            "citations": citations,
            "model": model
        }

        # Auto-save
        try:
            saved_path = auto_save_research(query_text, result, model)
            save_note = f"\n\n---\n_Auto-saved to: {saved_path.relative_to(PROJECT_ROOT)}_"
        except Exception as e:
            save_note = f"\n\n---\n_Auto-save failed: {e}_"

        # Format response
        response_text = content
        if citations:
            response_text += "\n\n**Sources:**\n"
            for i, citation in enumerate(citations, 1):
                response_text += f"{i}. {citation}\n"
        response_text += save_note

        return {"content": [{"type": "text", "text": response_text}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def main():
    """Main MCP server loop."""
    # Log startup
    sys.stderr.write(f"[perplexity-local] Starting MCP server\n")
    sys.stderr.write(f"[perplexity-local] Research dir: {RESEARCH_DIR}\n")
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

            if msg_id is not None:
                write_message({"jsonrpc": "2.0", "id": msg_id, "result": result})

        except Exception as e:
            sys.stderr.write(f"[perplexity-local] Error: {e}\n")
            sys.stderr.flush()
            if msg_id is not None:
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32603, "message": str(e)}
                })


if __name__ == "__main__":
    main()
