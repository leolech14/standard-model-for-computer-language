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
# 1. Run the boot script (from repo root)
bash context-management/tools/maintenance/boot.sh --json

# 2. Display Decision Deck (see available actions)
python .agent/tools/deal_cards_ui.py --chill
```

**Decision Deck:** After boot, you MUST display the deck and select a card.
This uses the Primacy Effect — first interaction embeds the mental model.

| Card Type | Purpose |
|-----------|---------|
| `[1-5]` | Pre-defined actions with preconditions |
| `[W]` | Wildcard (escape hatch, logged) |

**Primary doc:** `context-management/docs/agent_school/AGENT_BOOT.md`
**Deck spec:** `.agent/specs/DECISION_DECK_LAYER.md`

## Definition of Done

- [ ] Working tree clean (`git status`)
- [ ] Tests pass (or documented exception)
- [ ] Changes committed (or impossible + explained)
- [ ] Summary: what changed, where, why, how to verify

## Deep Docs Index

| Doc | Purpose |
|-----|---------|
| `docs/agent_school/INDEX.md` | Boot checklist + report format |
| `docs/agent_school/WORKFLOWS.md` | Git, test, review procedures |
| `docs/agent_school/REPO_FACTS.md` | Commands, paths, environment |
| `docs/agent_school/DOD.md` | Full Definition of Done |
| `docs/workflows/TIMESTAMP_WORKFLOW.md` | File history, temporal analysis |

## Emergency Contacts

- Primary: leonardo.lech@gmail.com
- Infra docs: See `gcp-infrastructure/CLAUDE.md` (NOT loaded globally)
