# Research: MCP FACTORY → HUB INTEGRATION VALIDATION

DISCOVERY: We have COMPLETE MCP infrastructure already bui...

> **Date:** 2026-01-27 09:55:14
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:3bb30498305dc07d0826c4a1d8b43fc79dc7a0742b3739262695e0281fa7a5e7`
> **Raw JSON:** `raw/20260127_095514_mcp_factory___hub_integration_validation__discover.json`

---

## Query

MCP FACTORY → HUB INTEGRATION VALIDATION

DISCOVERY: We have COMPLETE MCP infrastructure already built!

Location: context-management/tools/mcp/mcp_factory/

Components Found:
1. MCPServer (core/server.py) - JSON-RPC 2.0 stdio server
2. Scaffold tool (scaffold.py) - Generates new MCP servers
3. Templates (templates/python_stdio_server.py)
4. Example (perplexity_mcp_server.py) - Working production server
5. Knowledge base (knowledge/*.md) - Complete docs

PROPOSED INTEGRATION:

Create hub_mcp_server.py that exposes THE HUB via MCP protocol:



VALIDATION QUESTIONS:

1. ARCHITECTURE ALIGNMENT:
   - Does MCPServer class align with BasePlugin pattern?
   - Should MCPServer BE a plugin, or should it WRAP plugins?
   - Evidence: Examine server.py structure

2. EXISTING INTEGRATION PATTERNS:
   - How does perplexity_mcp_server.py work currently?
   - Does it already use any registries/services?
   - Evidence: Show code snippets

3. TOOL REGISTRATION:
   - What's the best way to expose Hub registries as MCP tools?
   - Should we auto-generate tools from registry introspection?
   - Or manually declare each tool?

4. EVENT BUS EXPOSURE:
   - Should AI agents be able to emit events via MCP?
   - Security implications?
   - Use cases?

5. WHAT'S MISSING:
   - Does MCPServer need modification to work with Hub?
   - Are there any incompatibilities?
   - What additional infrastructure needed?

PROVIDE FORENSIC ANALYSIS:
- File paths and line numbers
- Code snippets showing patterns
- Integration points where MCP touches existing code
- Recommended architecture (MCPServer as plugin vs wrapper)
- Implementation effort estimate


---

## Response

Based on the provided codebase context for the **Standard Model of Code (Hub)** and the user-supplied details about the **MCP Factory**, here is the forensic analysis and validation for the integration.

### FORENSIC ANALYSIS: Hub ↔ MCP Integration

#### 1. ARCHITECTURE ALIGNMENT
**Question:** Should `MCPServer` be a plugin or wrap the Hub?
**Verdict:** **WRAPPER (Host)**.

The Hub (`RegistryOfRegistries`) is designed as a passive singleton registry manager, while an MCP Server typically requires control of the process `stdio` loop to communicate with the client (Claude/Cursor).

**Evidence:**
*   **Hub Structure:** `RegistryOfRegistries` is initialized via `get_instance()` and stores data in memory. It does not have a main process loop; it relies on an external driver (like `full_analysis.py` or a CLI).
    *   `[standard-model-of-code/src/core/registry/registry_of_registries.py:68-80]`
*   **Plugin Contract:** `BasePlugin` assumes the Hub is already running and calls `initialize(hub)`. If the MCP Server were a plugin, the Hub would need a mechanism to run the MCP event loop, which it currently lacks.
    *   `[standard-model-of-code/src/core/plugin/base_plugin.py:42-57]`

**Recommended Pattern:**
Create `hub_mcp_server.py` as an executable entry point. It should:
1.  Instantiate `RegistryOfRegistries`.
2.  Load standard plugins/registries.
3.  Map Hub methods to MCP Tools.
4.  Start the MCP stdio loop.

---

#### 2. EXISTING INTEGRATION PATTERNS
**Question:** How does it connect?
**Analysis:** The Hub already provides a centralized access point that is perfect for MCP exposure.

**Evidence:**
*   The Hub allows string-based lookup of all internal systems. This maps 1:1 with how MCP Tools (which are string-invoked functions) operate.
    *   `hub.get('roles')` -> returns `RoleRegistry`.
    *   `[standard-model-of-code/src/core/registry/registry_of_registries.py:116-117]`
*   The Hub has a `status_report()` method which serves as an excellent "Readiness Probe" tool for MCP.
    *   `[standard-model-of-code/src/core/registry/registry_of_registries.py:123-150]`

---

#### 3. TOOL REGISTRATION
**Question:** Auto-generate or Manual?
**Verdict:** **Hybrid / Selective Manual**.

Auto-generation is risky because Registry APIs are not strictly uniform (some have `list_names`, others `all_types`). You should manually wrap the high-value accessors as tools to ensure type safety for the LLM.

**Proposed Tool Mapping (High Value):**

1.  **Tool:** `lookup_role`
    *   **Source:** `RoleRegistry.get_canonical(role)`
    *   **Code:** `[standard-model-of-code/src/core/registry/role_registry.py:166]`
    *   **Description:** "Normalize a coding role to its Standard Model canonical form."

2.  **Tool:** `check_atom`
    *   **Source:** `AtomRegistry.detect_ecosystem(file_path, content)`
    *   **Code:** `[standard-model-of-code/src/core/atom_registry.py:715]`
    *   **Description:** "Detect the ecosystem and potential atoms for a given file."

3.  **Tool:** `list_patterns`
    *   **Source:** `PatternRegistry.get_prefix_patterns()`
    *   **Code:** `[standard-model-of-code/src/core/registry/pattern_registry.py:530]`

---

#### 4. EVENT BUS EXPOSURE
**Question:** Should AI agents emit events?
**Verdict:** **YES**.

This allows the AI to trigger system behaviors (like "reload patterns" or "register service") without direct code access.

**Evidence:**
*   The `EventBus` is already decoupled and robust.
    *   `[standard-model-of-code/src/core/event_bus.py:68]` (`emit` method)
*   **Security:** The AI acts as a user. Since this is a local analysis tool, allowing the AI to emit `analysis:request` or `patterns:updated` poses minimal risk and enables dynamic system evolution.

**Use Case:**
*   Agent sees a new pattern in code -> Agent calls tool `emit_event("patterns:new", {...})` -> `PatternRegistry` (listening) updates itself.

---

#### 5. WHAT'S MISSING (Implementation Plan)

Since `MCP Factory` code was not provided in the context, I cannot validate its internals, but I can define the **Bridge Script** required to link them.

**File:** `standard-model-of-code/src/server/hub_mcp.py` (Proposed)

```python
import asyncio
# Import the Hub
from core.registry.registry_of_registries import get_meta_registry

# 1. Initialize Hub
hub = get_meta_registry()

# 2. Define Tools (Wrappers around Hub Registries)
async def tool_lookup_role(role_name: str) -> str:
    """Standardizes a role name to the SMoC canonical definitions."""
    roles = hub.get('roles')
    if not roles: return "Error: Role Registry not loaded"
    return roles.get_canonical(role_name)

async def tool_get_status() -> dict:
    """Returns the health status of all Collider subsystems."""
    return hub.status_report()

# 3. Define MCP Server (Pseudocode - requires MCP Factory imports)
# from mcp.server import Server
# server = Server("Collider Hub")
# server.register_tool("lookup_role", tool_lookup_role)
# server.register_tool("get_status", tool_get_status)
# server.serve_stdio()
```

### EFFORT ESTIMATE
*   **Low Effort (1-2 hours):** The Hub structure is perfectly set up for this. It is a singleton with string-based accessors, making it trivial to wrap in an MCP interface.
*   **Recommendation:** Proceed immediately. This will allow the Agent to introspect the system it is working on.

---

## Citations

_No citations provided_
