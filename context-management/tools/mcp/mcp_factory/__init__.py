"""
MCP Factory - Meta-Circular Processor Factory

A modular system for creating, managing, and testing MCP (Model Context Protocol)
servers that wrap external APIs with JSON-RPC 2.0 over stdio.

Usage:
    from mcp_factory import MCPServer, MCPRegistry, create_server

    # Create a new MCP server from template
    create_server("my-api-wrapper", api_provider="custom_rest")

    # Discover and list all installed MCP servers
    registry = MCPRegistry()
    for name, metadata in registry.list_servers().items():
        print(f"{name}: {metadata.description}")
"""

from .core.server import MCPServer, JSONRPCRequest, JSONRPCResponse, JSONRPCError
from .core.registry import MCPRegistry, ServerMetadata
from .core.client import ResilientAPIClient
from .core.persistence import AppendOnlyLog

__version__ = "0.1.0"
__all__ = [
    "MCPServer",
    "MCPRegistry",
    "ServerMetadata",
    "ResilientAPIClient",
    "AppendOnlyLog",
    "JSONRPCRequest",
    "JSONRPCResponse",
    "JSONRPCError",
]
