# Research: I have MCP server duplication across 3 config files in my Claude Code CLI setup. Help me understand ...

> **Date:** 2026-01-27 04:55:11
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:c4979c6194b7d64fc980db5bb8852195c9525c5cd6eddac2451f30bb6c93a702`
> **Raw JSON:** `raw/20260127_045511_i_have_mcp_server_duplication_across_3_config_file.json`

---

## Query

I have MCP server duplication across 3 config files in my Claude Code CLI setup. Help me understand the correct architecture:

FILE 1: ~/.claude/settings.json contains mcpServers with 'val3d' and 'perplexity'
FILE 2: ~/.claude.json contains global mcpServers (chrome-devtools, browser) AND project-scoped mcpServers under 'projects' key (perplexity and deepwebresearch for PROJECT_elements, val3d for PROJECT_val3d)
FILE 3: ~/.config/claude/mcp.json contains mcpServers (sniper-gun, central-mcp-cloud, chrome-devtools, browser)

Current running servers (from claude mcp list): chrome-devtools, browser, perplexity, deepwebresearch - all connected.
val3d is configured but NOT running (Blender not active).

Questions:
1. Which file is the canonical source for Claude Code CLI?
2. Should I remove mcpServers from settings.json since they're duplicated in ~/.claude.json?
3. Is ~/.config/claude/mcp.json for Claude Desktop only?
4. How to safely deduplicate without breaking anything?
5. Should I remove deprecated entries (central-mcp-cloud pointing to dead VM, localbrain-task-registry for abandoned project)?

---

## Response

Okay, Senior Engineer, this is a classic configuration sprawl scenario – especially common in environments with multiple tools (CLI, Desktop, IDE plugins) all trying to manage shared resources like MCP servers. Based on the provided codebase context, which heavily emphasizes `context-management` and a clear `Particle/Wave/Observer` architecture with specific `AGENT` roles and a `BARE` (Background Auto-Refinement Engine) for validation and cleanup, we can infer the best practices for your Claude Code CLI setup.

The project's philosophy strongly advocates for clear, validated, and de-duplicated configurations, especially with `BARE` and `ACI` (Adaptive Context Intelligence) mechanisms in place.

Here's an analysis of your `mcpServers` configuration and a plan for deduplication:

### Inferred Configuration Hierarchy for Claude Code

1.  **`~/.claude.json`**:
    *   **Primary Source for Claude Code CLI.** This file's structure, allowing for `global mcpServers` and `project-scoped mcpServers` under a `projects` key, is typical for CLI tools that need both general settings and context-aware overrides. The fact that `perplexity` and `deepwebresearch` (critical for `PROJECT_elements`'s `context-management` tools) are explicitly here and reported as running by `claude mcp list` confirms its active role for the CLI.

2.  **`~/.claude/settings.json`**:
    *   **General User Settings, potentially less specific for CLI `mcpServers`.** This file likely holds broader user preferences for Claude Code, which might include *some* `mcpServers` configuration but often serves as a fallback or a simpler initial setup. Duplication here suggests it's not the primary source for the CLI's operational `mcpServers`.

3.  **`~/.config/claude/mcp.json`**:
    *   **Likely for Claude Desktop and/or Shared Backend Services.** The `~/.config/` path typically follows the XDG Base Directory Specification, common for desktop applications or shared system-level configurations. The specific `sniper-gun` and `central-mcp-cloud` entries (which are *not* running according to your `claude mcp list` output) strongly suggest these are either for a desktop UI, a background service, or a different mode of operation entirely, and not directly managed by the *CLI's active server list*. `chrome-devtools` and `browser` being present here *and* in `~/.claude.json` globally, and *also* running, indicates potential merging or `~/.claude.json` pulling from global defaults.

---

### Answers to Your Questions

#### 1. Which file is the canonical source for Claude Code CLI?

**`~/.claude.json`** is the canonical source for your Claude Code CLI's `mcpServers` configuration. It supports both global and project-specific (`PROJECT_elements`, `PROJECT_val3d`) server definitions, which is essential for `PROJECT_elements`'s multi-project context management.

#### 2. Should I remove `mcpServers` from `settings.json` since they're duplicated in `~/.claude.json`?

**Yes, you absolutely should.**
This aligns with `PROJECT_elements`'s philosophy of maintaining a clean, validated state (`BARE` engine). Duplication introduces:
*   **Confusion:** Which config takes precedence?
*   **Maintenance overhead:** Changes need to be applied in multiple places.
*   **Potential for inconsistency:** Easy to forget updating one file, leading to subtle bugs.

The `mcpServers` section in `~/.claude/settings.json` should be removed once you've confirmed all necessary entries are correctly consolidated into `~/.claude.json`.

#### 3. Is `~/.config/claude/mcp.json` for Claude Desktop only?

**Most likely, yes.**
The `~/.config` location, combined with the presence of servers not listed as running by your CLI (`sniper-gun`, `central-mcp-cloud`), strongly suggests this file serves the Claude Desktop application or a shared background service that the CLI might *optionally* integrate with but doesn't primarily drive its active `mcpServers` list.
The `chrome-devtools` and `browser` servers being in both `~/.config/claude/mcp.json` and `~/.claude.json` (globally) implies either:
    a) `~/.claude.json` explicitly copies/overrides these.
    b) The Claude CLI merges configurations, with `~/.claude.json` taking precedence for project-specific or more granular settings. Given the goal of deduplication, ensure `~/.claude.json` holds all CLI-relevant servers.

#### 4. How to safely deduplicate without breaking anything?

Follow these steps precisely:

1.  **Backup All Configs:** This is the most critical step.
    ```bash
    mkdir -p ~/claude_config_backup_$(date +%Y%m%d%H%M%S)
    cp ~/.claude/settings.json ~/claude_config_backup_$(date +%Y%m%d%H%M%S)/
    cp ~/.claude.json ~/claude_config_backup_$(date +%Y%m%d%H%M%S)/
    cp ~/.config/claude/mcp.json ~/claude_config_backup_$(date +%Y%m%d%H%M%S)/
    ```

2.  **Consolidate to `~/.claude.json`:**
    *   **Edit `~/.claude.json`:**
        *   Ensure all **global `mcpServers`** you want the CLI to use (e.g., `chrome-devtools`, `browser`) are present and correctly configured under the global `mcpServers` key.
        *   Ensure all **project-scoped `mcpServers`** (e.g., `perplexity` and `deepwebresearch` for `PROJECT_elements`, `val3d` for `PROJECT_val3d`) are correctly defined under the `projects` key.
        *   For `val3d`, since it's configured but not running (Blender not active), its presence in `~/.claude.json` under `PROJECT_val3d` is the correct place to keep its configuration for when it *is* active.

3.  **Clean `~/.claude/settings.json`:**
    *   **Remove the entire `mcpServers` key** from `~/.claude/settings.json`. This file should now only contain general settings *not* related to specific MCP server connections.

4.  **Handle `~/.config/claude/mcp.json` (Desktop config):**
    *   For now, **leave it untouched,** except for removing deprecated entries (see next question). Your CLI's operation relies on `~/.claude.json`. If you remove `chrome-devtools` or `browser` from this file, and the CLI still works, it confirms `~/.claude.json` is the primary source. If the desktop app needs them, they'll remain there.

5.  **Test:**
    *   After each modification (especially after steps 2 and 3), run `claude mcp list`.
    *   Verify that `chrome-devtools`, `browser`, `perplexity`, and `deepwebresearch` are still listed as connected/active.
    *   Navigate to your `PROJECT_elements` directory and try a command that uses MCPs (e.g., `python context-management/tools/ai/analyze.py --aci "some query"`).

#### 5. Should I remove deprecated entries (central-mcp-cloud pointing to dead VM, localbrain-task-registry for abandoned project)?

**Yes, definitely remove them.**
This aligns perfectly with `PROJECT_elements`'s `BARE` engine philosophy of auto-refinement and cleanup. Outdated or dead configurations are sources of:
*   **Noise and cognitive load:** Confusing what's active vs. legacy.
*   **Potential errors:** If the CLI or desktop attempts to connect to a dead server, it can introduce delays or error messages.
*   **Security risks:** Outdated configurations can sometimes point to insecure endpoints or expose old credentials if not properly managed (though less likely for MCP connections).

**Action:**
*   Identify where `central-mcp-cloud` and `localbrain-task-registry` are located. They are most likely in `~/.config/claude/mcp.json` or potentially `~/.claude.json` under an old `projects` entry.
*   Carefully remove these specific server definitions from the respective JSON files.
*   **Test `claude mcp list`** after removing to ensure no unintended side effects.

By following this approach, you'll establish a clear, canonical source for your Claude Code CLI's MCP configurations, reduce redundancy, and clean up historical cruft, making your local development environment more robust and easier to manage, in line with the `PROJECT_elements`'s internal best practices.

---

## Citations

_No citations provided_
