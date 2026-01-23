# MCP Factory Roadmap

> Strategic plan derived from session 2026-01-22: debugging, building, and analysis with Gemini + Perplexity.

## Vision

MCP Factory becomes the **canonical knowledge base and tooling** for creating, testing, and managing MCP servers - both for PROJECT_elements and potentially as a standalone resource for the community.

---

## Current State (2026-01-22)

```
COMPLETED:
├── perplexity_mcp_server.py      # Reference implementation with auto-save
├── INDEX.md                       # Entry point
├── CONFIG_PANEL.md                # Dependency injection pattern
└── knowledge/
    ├── CONFIGURATION.md           # Claude Code config bug documented
    ├── TROUBLESHOOTING.md         # Decision tree
    └── EXTERNAL_LINKS.md          # Curated resources

DISCOVERED:
├── Bug #4976: ~/.claude/settings.json ignores MCP configs
├── Correct location: ~/.claude.json → projects[path].mcpServers
└── 30 min debugging → tribal knowledge captured
```

---

## Phase 1: Foundation (Current)

**Goal:** Solidify knowledge base, prevent drift, enable reuse.

| Task | Priority | Effort | Status |
|------|----------|--------|--------|
| Write `BEST_PRACTICES.md` from Perplexity research | High | Medium | Pending |
| Integrate into HSL (`semantic_models.yaml`) | High | Low | Pending |
| Abstract dual-format save to `tools/utils/output_formatters.py` | Medium | Low | Pending |
| Document CONFIG_PANEL pattern in agent school | Medium | Low | Pending |
| Add SHA-256 checksums to auto-save (Perplexity recommendation) | Medium | Low | Pending |

**Milestone:** MCP Factory docs are validated by Holographic-Socratic Layer.

---

## Phase 2: Templates & Scaffolding

**Goal:** Make creating new MCP servers trivial.

| Task | Priority | Effort | Status |
|------|----------|--------|--------|
| Create `templates/python_stdio_server/` scaffold | High | Medium | Pending |
| Create `templates/node_stdio_server/` scaffold | Low | Medium | Pending |
| Build `tools/scaffold.py` - interactive generator | Medium | Medium | Pending |
| Add Copier/cookiecutter integration | Low | Medium | Pending |

**Milestone:** `python tools/scaffold.py my-new-server` creates working MCP in <1 min.

---

## Phase 3: Validation & Registry

**Goal:** Ensure quality and track deployed servers.

| Task | Priority | Effort | Status |
|------|----------|--------|--------|
| Build `tools/validate.py` - compliance tester | High | Medium | Pending |
| Build `tools/registry.py` - track deployed servers | Medium | Medium | Pending |
| Create MCP-specific prompt in `prompts.yaml` | Low | Low | Pending |
| Add pre-commit hook for MCP validation | Low | Low | Pending |

**Milestone:** All MCP servers pass automated compliance checks.

---

## Phase 4: Integration & Ecosystem

**Goal:** Connect MCP Factory to broader PROJECT_elements architecture.

| Task | Priority | Effort | Status |
|------|----------|--------|--------|
| MCP Factory consumes Collider output (`unified_analysis.json`) | Medium | High | Pending |
| Auto-generate MCPs from detected patterns | Low | High | Pending |
| Publish MCP Factory as standalone resource | Low | Medium | Pending |
| Contribute config bug findings back to Claude Code repo | Low | Low | Pending |

**Milestone:** Body (Collider) ↔ Brain (MCP Factory) integration complete.

---

## Dependencies

```
Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4
   │           │           │
   │           │           └── Requires: validation tooling
   │           └── Requires: best practices documented
   └── Requires: HSL integration for drift prevention
```

---

## Key Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| **Integrated** (not standalone) | Leverages Doppler, GCS, Perplexity pipeline | 2026-01-22 |
| **CONFIG_PANEL pattern** | Decouples MCP knowledge from project context | 2026-01-22 |
| **Dual-format save** | ZERO information loss (user requirement) | 2026-01-22 |

---

## Key Decisions Pending

| Decision | Options | Blocker |
|----------|---------|---------|
| Validation strictness | Warn vs Fail on violations | Need BEST_PRACTICES.md first |
| Registry storage | Local JSON vs GCS vs Both | Need to assess scale |
| Template language | Pure Python vs Copier vs Cookiecutter | Need to test options |

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Time to create new MCP server | <5 min | ~30 min |
| Documentation drift detected | 100% | 0% (no HSL integration) |
| MCP servers with auto-save | 100% | 1 (perplexity) |
| Research queries preserved | 100% | 100% (pipeline working) |

---

## Resources

| Resource | Location |
|----------|----------|
| Perplexity research (MCP design) | `${RESEARCH_DIR}/docs/20260122_MCP_FACTORY_DESIGN_FULL.md` |
| Perplexity research (architecture) | `${RESEARCH_DIR}/docs/20260122_160942_comprehensive_analysis_*.md` |
| Perplexity research (archival) | `${RESEARCH_DIR}/docs/20260122_155500_deterministic_archival_evaluation.md` |
| Gemini analysis | This session transcript |
| GitHub issues | #4976 (config bug), #3098 (CLI inconsistency) |

---

## Version

| Field | Value |
|-------|-------|
| Roadmap Version | 1.0.0 |
| Created | 2026-01-22 |
| Last Updated | 2026-01-22 |
| Authors | Claude + Leonardo |
