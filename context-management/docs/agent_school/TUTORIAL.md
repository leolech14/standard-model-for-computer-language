# Agent Tutorial - Your First Task

> This walkthrough takes you through a real task, start to finish.

## Step 1: Boot

```bash
./concierge
```

You'll see:
```
╔══════════════════════════════════════════════════════════════╗
║  PROJECT ELEMENTS                                    v2.1     ║
╠══════════════════════════════════════════════════════════════╣
║  WHY: See code as ARCHITECTURE, not text.                    ║
║  HOW: Collider analyzes → you act on structured insights.    ║
╠══════════════════════════════════════════════════════════════╣
║  Status: 3 uncommitted
║  Branch: main
║  Meters: F:5 R:5 D:2
║                                                              ║
║  YOUR OPTIONS:                                              ║
║  [1] Resume TASK-066: "Handle Gemini API Rate Limitin..."
║  [2] Pick from inbox (60 total)
║      • OPP-003: Consolidate research directories
║      • OPP-004: Document registry architecture
║      • OPP-005: Token System Refactoring
║  [3] Start fresh - describe your task
║  [D] Deal cards (Decision Deck)
╚══════════════════════════════════════════════════════════════╝
```

**What you learned:**
- Status tells you if there's uncommitted work
- Meters show health (Focus, Rigor, Drift)
- Options give you choices, not commands

## Step 2: Pick a Task

Let's pick option `[3]` - start fresh.

**Your task:** "Fix the typo in GLOSSARY_QUICK.md"

Before touching anything:

```bash
git status                    # Verify clean state
```

If dirty, deal with it first. Never pile changes on top of uncommitted work.

## Step 3: Find and Fix

```bash
# Read the file first
cat context-management/docs/GLOSSARY_QUICK.md

# Find the typo (let's say "anlaysis" instead of "analysis")
# Edit it
```

Make the change. One logical change at a time.

## Step 4: Validate

```bash
# Check what changed
git diff

# Run tests (even for docs - confirms nothing broke)
pytest tests/ -q

# Verify status
git status
```

**Expected output:**
```
modified: context-management/docs/GLOSSARY_QUICK.md
```

## Step 5: Commit

```bash
git add context-management/docs/GLOSSARY_QUICK.md
git commit -m "fix(docs): Correct typo in GLOSSARY_QUICK.md"
```

**Commit message format:**
- `fix`: Bug fix
- `feat`: New feature
- `docs`: Documentation only
- `chore`: Maintenance
- `refactor`: Code restructure (no behavior change)

## Step 6: Summary

After every task, provide:

```markdown
## Summary

### What Changed
- `context-management/docs/GLOSSARY_QUICK.md`: Fixed "anlaysis" → "analysis"

### Why
Typo made the document look unprofessional.

### How to Verify
1. `cat context-management/docs/GLOSSARY_QUICK.md | grep analysis`
2. Confirm correct spelling

### Repo State
- Branch: main
- Status: clean
- Tests: pass
- Commit: abc1234 "fix(docs): Correct typo in GLOSSARY_QUICK.md"
```

---

## The Micro-Loop (Your Heartbeat)

Every task follows this pattern:

```
┌─────────────────────────────────────────────────────┐
│  1. SCAN    →  git status, understand current state │
├─────────────────────────────────────────────────────┤
│  2. PLAN    →  What will you change? (3-7 bullets)  │
├─────────────────────────────────────────────────────┤
│  3. EXECUTE →  Make the change (one chunk at a time)│
├─────────────────────────────────────────────────────┤
│  4. VALIDATE→  git diff, tests, lint                │
├─────────────────────────────────────────────────────┤
│  5. COMMIT  →  git add + git commit                 │
├─────────────────────────────────────────────────────┤
│  6. REPEAT  →  Until task is complete               │
└─────────────────────────────────────────────────────┘
```

---

## Common Mistakes (Avoid These)

| Mistake | Why It's Bad | Fix |
|---------|--------------|-----|
| Editing without reading first | You might break something | Always `cat` or `Read` before editing |
| Multiple unrelated changes | Hard to review, risky to revert | One logical change per commit |
| Skipping tests | Breaks stuff silently | `pytest tests/ -q` is fast |
| No summary | No audit trail | Always explain what/why |
| Uncommitted changes at end | Dirty repo = chaos | Never leave repo dirty |

---

## When You're Stuck

1. **Can't find a file?** Use `./collider full .` to analyze the repo
2. **Don't understand a concept?** Check `GLOSSARY_QUICK.md` first
3. **Tests failing?** Read the error. Trace the cause. Don't guess.
4. **Not sure if done?** Run the DOD checklist:
   - [ ] git status → clean
   - [ ] tests → pass
   - [ ] summary → provided

---

## Next Steps

After completing your first task:

1. Try picking from inbox: `[2]` in concierge
2. Learn the Decision Deck: `[D]` for pre-defined action cards
3. Read the full workflows: `docs/agent_school/WORKFLOWS.md`

---

*Tutorial complete. You're ready to work.*
