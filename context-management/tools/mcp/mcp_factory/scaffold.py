#!/usr/bin/env python3
"""
MCP Server Scaffold

Generates a new Python MCP server from the stdio template.

Usage:
    python scaffold.py my_service "My Service Description"

This creates:
    - my_service_mcp_server.py (ready to customize)

Template Variables:
    {{SERVER_NAME}}  -> Human-readable name (e.g., "My Service")
    {{SERVER_ID}}    -> Machine ID (e.g., "my_service")
    {{DESCRIPTION}}  -> One-line description

Version: 1.0.0
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent.resolve()
TEMPLATE_PATH = SCRIPT_DIR / "templates" / "python_stdio_server.py"
OUTPUT_DIR = SCRIPT_DIR.parent  # context-management/tools/mcp/


def slugify(name: str) -> str:
    """Convert name to snake_case slug."""
    # Replace spaces and dashes with underscores
    slug = re.sub(r'[\s\-]+', '_', name.lower())
    # Remove non-alphanumeric (except underscores)
    slug = re.sub(r'[^a-z0-9_]', '', slug)
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    return slug


def title_case(slug: str) -> str:
    """Convert slug to Title Case."""
    return ' '.join(word.capitalize() for word in slug.split('_'))


def scaffold_server(server_id: str, description: str, output_dir: Optional[Path] = None) -> Path:
    """
    Generate a new MCP server from template.

    Args:
        server_id: Machine-readable ID (snake_case)
        description: Human-readable description
        output_dir: Directory to write server file

    Returns:
        Path to generated file
    """
    output_dir = output_dir or OUTPUT_DIR

    # Read template
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

    template = TEMPLATE_PATH.read_text()

    # Apply substitutions
    server_name = title_case(server_id)
    content = template.replace("{{SERVER_NAME}}", server_name)
    content = content.replace("{{SERVER_ID}}", server_id)
    content = content.replace("{{DESCRIPTION}}", description)

    # Write output
    output_path = output_dir / f"{server_id}_mcp_server.py"
    output_path.write_text(content)
    output_path.chmod(0o755)  # Make executable

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new Python MCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scaffold.py weather "Weather forecast API integration"
    python scaffold.py code_search "Search code repositories"
    python scaffold.py llm_gateway "Gateway to multiple LLM providers"

The server_id should be snake_case (e.g., my_service, not my-service).
        """
    )
    parser.add_argument("server_id", help="Server ID in snake_case (e.g., weather, code_search)")
    parser.add_argument("description", help="One-line description of the server")
    parser.add_argument("--output", "-o", type=Path, help="Output directory (default: mcp/)")

    args = parser.parse_args()

    # Validate server_id
    if not re.match(r'^[a-z][a-z0-9_]*$', args.server_id):
        print(f"Error: server_id must be snake_case (lowercase, underscores)")
        print(f"Got: {args.server_id}")
        sys.exit(1)

    try:
        output_path = scaffold_server(
            server_id=args.server_id,
            description=args.description,
            output_dir=args.output
        )
        print(f"Created: {output_path}")
        print()
        print("Next steps:")
        print(f"  1. Edit {output_path.name}")
        print(f"  2. Implement handle_query_tool() or add new tools")
        print(f"  3. Add to ~/.claude.json:")
        print(f'     "{args.server_id}": {{')
        print(f'         "type": "stdio",')
        print(f'         "command": "python3",')
        print(f'         "args": ["{output_path}"]')
        print(f'     }}')

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
