# AGENT KERNEL (Always Loaded)

> This file must stay under 2KB. It is loaded into EVERY agent session.

## Non-Negotiables

1. **Never leave repo dirty** — commit changes or explain why you cannot
2. **Verify before "done"** — run `git status`, tests, lint
3. **No silent refactors** — state file moves/renames explicitly
4. **No duplicates** — search before creating new modules
5. **Rationale required** — every change needs a written "why"

## Session Start: Boot Sequence

```bash
# Option A: Run the boot script (from repo root)
bash context-management/tools/maintenance/boot.sh

# Option B: Manual boot
# 1. Read context-management/docs/agent_school/INDEX.md
# 2. Follow the checklist
# 3. Output INITIATION_REPORT JSON
```

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

## Emergency Contacts

- Primary: leonardo.lech@gmail.com
- Infra docs: See `gcp-infrastructure/CLAUDE.md` (NOT loaded globally)
