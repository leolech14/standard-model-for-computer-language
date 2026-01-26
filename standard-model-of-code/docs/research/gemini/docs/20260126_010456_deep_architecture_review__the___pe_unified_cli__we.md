# Research: DEEP ARCHITECTURE REVIEW: The ./pe Unified CLI

We just built a two-layer abstraction for PROJECT_el...

> **Date:** 2026-01-26 01:04:56
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:21c7c4834164c9adeda6d068dc7f0820f412ddf85207b75c83065761cf995873`
> **Raw JSON:** `raw/20260126_010456_deep_architecture_review__the___pe_unified_cli__we.json`

---

## Query

DEEP ARCHITECTURE REVIEW: The ./pe Unified CLI

We just built a two-layer abstraction for PROJECT_elements:

LAYER 1: UNIFIED CLI (./pe)
- Single entry point for all tools
- Eliminates: venv activation, path memorization, tool discovery
- Commands: status, ask, collider, autopilot, tdj, boot, test

LAYER 2: INTENT ROUTING  
- Natural language → tool routing
- Priority: Pattern matching (<50ms) → Ollama (~100ms) → AI fallback (1-2s)
- Patterns: status, analyze, fix, explain, recent, stale, test, commit, drift

REVIEW QUESTIONS:

1. ARCHITECTURAL COHERENCE
   - Does ./pe fit the Wave/Particle/Observer model?
   - Where does it belong ontologically?
   - Is it a Module, Automation, or Infrastructure?

2. COMPLETENESS
   - What tools are NOT accessible via ./pe?
   - What common workflows are missing?
   - What intents should be added?

3. DESIGN FLAWS
   - Are there anti-patterns in the current implementation?
   - Security concerns? (shell injection in intent routing?)
   - Failure modes we haven't considered?

4. EVOLUTION PATH
   - What's the natural next step for ./pe?
   - Should it become a Python script for more power?
   - Should it integrate with Claude Code / MCP?

5. THE META QUESTION
   - ./pe is an AI-assistant's AI-assistant
   - Should Claude Code use ./pe directly?
   - How do we document this for AI consumption?

Provide a comprehensive architectural review with specific recommendations.

---

## Response

This is a comprehensive architectural review of the `./pe` Unified CLI and Intent Routing layer, analyzed against the **Standard Model of Code** and **PROJECT_elements** theoretical framework.

---

# ARCHITECTURAL REVIEW: The `./pe` Unified CLI

**Review Date:** 2026-01-25
**Subject:** Unified Command Interface (`./pe`) & Intent Router
**Framework:** Standard Model of Code (Wave/Particle/Observer)

## 1. Architectural Coherence

### Ontological Placement
Does `./pe` fit the Wave/Particle/Observer model? Yes, but it occupies a unique position.

In the **Codespace Algebra** (`CODESPACE_ALGEBRA.md`), we define three realms:
*   **Particle** (`standard-model-of-code`): Measurement/Implementation.
*   **Wave** (`context-management`): Context/Potential.
*   **Observer** (`.agent`): Governance/Decision.

`./pe` is **not** a realm. It is the **Interface Layer** (L1 in the Tarski Hierarchy discussed in `CODESPACE_ALGEBRA.md`). It is the mechanism by which the **Observer** collapses the **Wave** into **Particle** action.

### Phase Classification
*   **Is it a Module?** No. It contains no core capability logic.
*   **Is it Automation?** Yes (2nd Order). It decides *when* and *how* to run tools based on intent.
*   **Is it Infrastructure?** Yes (0th Order). It provides the environment (venv management, path resolution).

**Verdict:** `./pe` is the **Control Plane**. It acts as the **hypervisor** for the Projectome. It enforces the "Stone Tool Principle" (Axiom H4) by shaping the complex underlying machinery into a grip-able handle for both humans and AI agents.

---

## 2. Completeness Analysis

The current command set (`status, ask, collider, autopilot, tdj, boot, test`) covers the "Daily Driver" loop but misses critical "Governance" and "Deep Science" workflows defined in the docs.

### Missing Tools (Gap Analysis)
Based on `ASSET_INVENTORY.md` and `BACKGROUND_AI_LAYER_MAP.md`, the following are inaccessible:

1.  **The Mirror**: `archive.py mirror` (Critical for Cloud sync/backup).
2.  **The Socratic Layer**: `analyze.py --verify` (HSL). This is crucial for checking Antimatter Laws (`AM001`-`AM003`).
3.  **Research Orchestrator**: `analyze.py --research <schema>` (Deep research schemas defined in `research_schemas.yaml`).
4.  **Refinery**: `refinery.py` (Context atomization).

### Missing Workflows
1.  **"Sync"**: Push/Pull orientation files and cloud mirrors (`ORIENTATION_FILES.md`).
2.  **"Audit"**: Trigger a full HSL audit or Socratic verification.
3.  **"Visualize"**: Start the WebGL server (`collider viz`).

### Recommended Intents
Add these to Layer 2 routing:
*   `verify` / `audit` → `analyze.py --verify`
*   `research` / `deep dive` → `analyze.py --research`
*   `sync` / `push` → `archive.py mirror`
*   `graph` / `see` → `collider viz`

---

## 3. Design Flaws & Risks

### Anti-Patterns
1.  **The Shell wrapper Trap**: If `./pe` is purely Bash, handling complex argument parsing (flags pass-through) and intent routing logic becomes brittle.
2.  **Hidden Environment Dependency**: If `./pe` assumes `.tools_venv` exists without self-healing (auto-creation), it violates the "Boot Protocol" philosophy (`AGENT_KERNEL.md`).

### Security Concerns (Critical)
**Shell Injection via Intent Routing**:
If Layer 2 takes natural language and naively constructs shell commands, this is a vulnerability.
*   *Risk:* `pe "analyze file; rm -rf /"`
*   *Mitigation:* The Intent Router must output **Structured Intent** (JSON), not executable strings. The CLI then maps JSON -> Safe Command. Never `eval` the output of an LLM/Ollama directly in the shell.

### Failure Modes
1.  **Ollama/AI Downtime**: If the routing layer *requires* LLM for basic commands, the tool becomes unusable offline.
    *   *Fix:* Ensure "Fast Path" (Pattern Matching) covers 100% of deterministic commands (`status`, `test`, `boot`). AI should only handle ambiguity.
2.  **Latency Fatigue**: 1-2s fallback latency is too high for CLI muscle memory. AI routing should be an *opt-in* or *fallback-only* path, not the default for known keywords.

---

## 4. Evolution Path

### Immediate Next Step: Python Migration
Bash is insufficient for Layer 2. `./pe` should transition from a shell script to a Python entry point (using `Typer` or `Click`) that:
1.  Bootstraps the environment (fast).
2.  Imports the Intent Router as a module.
3.  Dispatches to other Python tools *internally* (import and run `main()`) rather than spawning subprocesses, saving startup time.

### Integration with Claude Code / MCP
This is the highest-value evolution. `./pe` is effectively a **Local MCP Server**.
*   **Recommendation**: Expose `./pe` functions via an MCP server (`mcp-server-pe`).
*   **Benefit**: Claude Desktop can "see" the tools as native functions (`pe_analyze`, `pe_collider`) rather than hallucinating bash commands.

---

## 5. The Meta Question (AI Usage)

> *Should Claude Code use `./pe` directly?*

**YES. Axiom H3 (Optimization Target) states: "Optimize for AI_AGENT consumption."**

`./pe` acts as a **Context Compressor** for the agent.
*   **Without `./pe`**: Agent must know: "Activate .tools_venv, then python context-management/tools/ai/analyze.py --aci ..." (High token cost, high error probability).
*   **With `./pe`**: Agent types: `./pe ask "..."` (Low token cost, high reliability).

### Documentation for AI
You need a specific file: `context-management/docs/agent_school/CLI_GRAMMAR.md`.
This file should contain:
1.  The exact syntax of `./pe`.
2.  The capabilities of the Intent Router.
3.  Examples of mapping "Human thought" -> "PE Command".

Inject this grammar into the Agent Context (via `aci_config.yaml` or `CLAUDE.md`).

---

## Summary Recommendations

1.  **Formalize**: Move `./pe` from a shell script to a Python package (`src/cli/main.py`) that manages the venv internally.
2.  **Expand**: Add `verify`, `research`, and `sync` commands to cover HSL and Cloud workflows.
3.  **Secure**: Ensure Intent Routing outputs an abstract intent enum, not an executable string.
4.  **Document**: Create `CLI_GRAMMAR.md` specifically to teach Claude Code how to use its new hands.
5.  **Interface**: Treat `./pe` as the implementation of the **Stone Tool Principle**—a tool specifically shaped for the AI hand.

---

## Citations

_No citations provided_
