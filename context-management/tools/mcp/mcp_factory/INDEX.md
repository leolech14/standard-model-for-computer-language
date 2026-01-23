# MCP Factory

> A structured knowledge base and tooling for creating, testing, and managing MCP servers.

## Quick Start

```bash
# See current integration context
cat CONFIG_PANEL.md

# Core knowledge (standalone-readable)
cat knowledge/CONFIGURATION.md      # Where MCP configs live
cat knowledge/TROUBLESHOOTING.md    # Debug decision tree
cat knowledge/BEST_PRACTICES.md     # Design patterns
```

---

## How This Documentation Works

MCP Factory docs are **context-agnostic**. All project-specific bindings live in one place:

| File | Purpose |
|------|---------|
| **[CONFIG_PANEL.md](./CONFIG_PANEL.md)** | All variables, paths, integrations - **edit this to adapt** |
| Everything else | Pure MCP knowledge - reads as standalone |

When you see `${VARIABLE}` in docs, look up its value in CONFIG_PANEL.md.

---

## Knowledge Graph

```
MCP_FACTORY/
├── INDEX.md                          # This file - entry point
├── CONFIG_PANEL.md                   # Integration bindings (edit to adapt)
├── ROADMAP.md                        # Strategic plan with phases
├── TASK_CONFIDENCE_REGISTRY.md       # 4D-scored task queue
├── TASK_STEP_LOG.md                  # Step-level execution tracking
├── knowledge/
│   ├── CONFIGURATION.md              # Where configs live, pitfalls
│   ├── BEST_PRACTICES.md             # Design patterns, anti-patterns
│   ├── TROUBLESHOOTING.md            # Common issues and fixes
│   └── EXTERNAL_LINKS.md             # Curated external resources
├── templates/
│   ├── python_stdio_server/          # Python MCP server template (pending)
│   └── node_stdio_server/            # Node.js MCP server template (rejected)
├── examples/
│   └── ${SERVERS_DIR}/perplexity_mcp_server.py  # Reference implementation
└── tools/
    ├── ${TOOLS_DIR}/utils/output_formatters.py  # Dual-format saver (done)
    ├── scaffold.py                   # Generate new MCP servers (pending)
    ├── validate.py                   # Test MCP server compliance (pending)
    └── registry.py                   # Track deployed servers (deferred)
```

---

## Core Knowledge (Context-Free)

### Config Locations (Claude Code)

```
CORRECT:
~/.claude.json                           # Global MCPs at root "mcpServers"
~/.claude.json → projects[path].mcpServers  # Project-specific MCPs
.mcp.json                                # Project root (shared with team)

IGNORED (Bug #4976):
~/.claude/settings.json                  # Does NOT load MCP servers
~/.claude/settings.local.json            # Does NOT load MCP servers
```

### Adding MCP Servers

```bash
# CLI method (recommended - handles config automatically)
claude mcp add <name> --scope user -- <command> [args...]
claude mcp add <name> --scope project -- <command> [args...]

# Manual method (must edit correct file)
# Edit ~/.claude.json for global/project-specific
# Edit .mcp.json for team-shared project config
```

### Testing MCP Servers

```bash
# Initialize test
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 server.py

# List tools test
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python3 server.py

# MCP Inspector (visual testing)
npx @anthropic-ai/mcp-inspector
```

---

## External Resources

| Resource | URL | Why It Matters |
|----------|-----|----------------|
| **MCP Specification** | https://modelcontextprotocol.io/docs | Official protocol docs |
| **Claude Code MCP Docs** | https://code.claude.com/docs/en/mcp | How Claude Code loads MCPs |
| **GitHub Issue #4976** | https://github.com/anthropics/claude-code/issues/4976 | Config location bug |
| **GitHub Issue #3098** | https://github.com/anthropics/claude-code/issues/3098 | CLI vs file config inconsistency |
| **MCP Inspector** | https://modelcontextprotocol.io/docs/tools/inspector | Testing tool |

See [EXTERNAL_LINKS.md](./knowledge/EXTERNAL_LINKS.md) for complete curated list.

---

## Bootstrap Story

This knowledge base was born from a troubleshooting session on 2026-01-22:

1. Created local Perplexity MCP server with auto-save pipeline
2. Added to `~/.claude/settings.json` (WRONG)
3. Server never loaded - external npm package used instead
4. Discovered: settings.json is IGNORED for MCP configs
5. Found correct location: `~/.claude.json` under `projects[path].mcpServers`
6. Fixed config, tested, confirmed auto-save working

**Time spent debugging:** ~30 minutes
**Root cause:** Undocumented/buggy config location
**Lesson:** Always use `claude mcp add` or know the correct file

---

## Roadmap

See **[ROADMAP.md](./ROADMAP.md)** for the full strategic plan with phases, priorities, and milestones.

**Quick Status:**

| Phase | Focus | Status |
|-------|-------|--------|
| **1** | Foundation (HSL integration, best practices) | In Progress |
| **2** | Templates & Scaffolding | Pending |
| **3** | Validation & Registry | Pending |
| **4** | Ecosystem Integration | Pending |

---

## Usage Modes

### As Integrated Module

Current mode. See CONFIG_PANEL.md for bindings to host project.

### As Standalone

1. Copy `mcp_factory/` directory
2. Edit `CONFIG_PANEL.md`: set `mode: STANDALONE`
3. Update path variables
4. Replace external dependencies with alternatives

### As Reference

Read the `knowledge/` docs without copying anything. All MCP concepts are universal.
