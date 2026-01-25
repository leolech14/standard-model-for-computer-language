# AGENT KERNEL (Always Loaded)

> This file must stay under 2KB. It is loaded into EVERY agent session.

## Non-Negotiables

1. **Never leave repo dirty** — commit changes or explain why you cannot
2. **Verify before "done"** — run `git status`, tests, lint
3. **No silent refactors** — state file moves/renames explicitly
4. **No duplicates** — search before creating new modules
5. **Rationale required** — every change needs a written "why"
6. **Never stop without path forward** — provide priority matrix with confidence scores

## Session Start: Boot Sequence

```bash
# Run concierge (from repo root)
./concierge
```

Shows: status, meters, options, P0 rules. Everything you need to start.

| Option | Action |
|--------|--------|
| `[1]` | Resume active task |
| `[2]` | Pick from inbox (top 3 shown) |
| `[3]` | Start fresh task |
| `[D]` | Deal cards (Decision Deck) |

**Deck spec:** `.agent/specs/DECISION_DECK_LAYER.md`

## Definition of Done

- [ ] Working tree clean (`git status`)
- [ ] Tests pass (or documented exception)
- [ ] Changes committed (or impossible + explained)
- [ ] Summary: what changed, where, why, how to verify

## Deep Docs Index

| Doc | Purpose |
|-----|---------|
| `docs/agent_school/WORKFLOWS.md` | Git, test, review procedures |
| `docs/agent_school/DOD.md` | Full Definition of Done |
| `docs/deep/INDEX.md` | Theory, architecture, research docs |

## Emergency Contacts

- Primary: leonardo.lech@gmail.com
- Infra docs: See `gcp-infrastructure/CLAUDE.md` (NOT loaded globally)
