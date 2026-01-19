# Orientation Files System

> Export key context files for AI agents and external sharing.

---

## What It Is

The **orientation files** are a curated subset of documentation that provides complete context for AI agents or collaborators without requiring access to the full repo.

**Use cases:**
- Load into an AI session for instant project context
- Share a zip with collaborators who need the conceptual foundation
- Keep a local "context pack" synced with the latest repo state

---

## What "Truth" Means

The sync copies from the **working directory** (files on disk), not from git-committed state.

| Layer | Description |
|-------|-------------|
| Git (committed) | Historical snapshots |
| **Working Directory** | Current state on disk ← **Source of truth for sync** |
| Orientation Folder | Copies for external use |
| Zip | Snapshot of orientation folder |

If you want the orientation folder to reflect only committed changes, commit first, then sync.

---

## Files Exported

| Source | Destination | Description |
|--------|-------------|-------------|
| `README.md` | `REPO_README.md` | Project overview |
| `CLAUDE.md` | `CLAUDE.md` | AI agent quick reference |
| `VISION.md` | `VISION.md` | Project vision |
| `ROADMAP.md` | `ROADMAP.md` | Development roadmap |
| `docs/README.md` | `DOCS_README.md` | Documentation index |
| `docs/TOOL.md` | `TOOL.md` | Collider implementation guide |
| `docs/theory/THEORY.md` | `THEORY.md` | Theoretical framework |
| `docs/GLOSSARY.md` | `GLOSSARY.md` | Terminology definitions |
| `docs/AGENT_CONTEXT.md` | `AGENT_CONTEXT.md` | Extended agent context |
| `.agent/AGENT_INSTRUCTIONS.md` | `AGENT_INSTRUCTIONS.md` | Agent instructions |
| `schema/*.json` | `*.json` | JSON schemas |
| `docs/roadmaps/*.md` | `C1_*.md, C2_*.md, C3_*.md` | Roadmap documents |

**Default destination:** `~/Downloads/orientation-files/`
**Internal mirror:** `.agent/orientation/` (git-ignored, always synced)

---

## Usage

### One-time sync (default)
```bash
./scripts/sync-orientation-files.sh
```

### Watch mode (continuous sync)
```bash
./scripts/sync-orientation-files.sh --watch
```
Changes to source files auto-sync to the destination.

### Generate zip
```bash
./scripts/sync-orientation-files.sh --zip
```
Creates/updates `~/Downloads/orientation-files.zip`.

### Override paths
```bash
# Custom destination
./scripts/sync-orientation-files.sh --dest /path/to/output

# Custom source (different repo)
./scripts/sync-orientation-files.sh --source /path/to/repo
```

### Combine flags
```bash
# Watch mode + auto-regenerate zip on changes
./scripts/sync-orientation-files.sh --watch --zip
```

---

## Requirements

### For watch mode
Requires `fswatch`:
```bash
brew install fswatch
```

---

## Making Watch Mode Persistent (launchd)

To auto-start watch mode at login:

1. Copy the example plist to LaunchAgents:
```bash
cp scripts/launchd/com.standardmodel.orientation-sync.plist.example \
   ~/Library/LaunchAgents/com.standardmodel.orientation-sync.plist
```

2. Edit the plist to set correct paths (if your repo is in a different location).

3. Load the agent:
```bash
launchctl load ~/Library/LaunchAgents/com.standardmodel.orientation-sync.plist
```

4. To stop:
```bash
launchctl unload ~/Library/LaunchAgents/com.standardmodel.orientation-sync.plist
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Zip is stale | Zip not regenerated after sync | Run `--zip` flag |
| Auto-update not happening | Watch mode not running | Start with `--watch` or load launchd agent |
| fswatch not found | Not installed | `brew install fswatch` |
| Files missing in destination | Source file doesn't exist | Check source paths; some files are optional |

### Verify sync integrity
```bash
# Compare hashes
shasum -a 256 docs/TOOL.md
shasum -a 256 ~/Downloads/orientation-files/TOOL.md
# Should match
```

### Verify zip integrity
```bash
unzip -q ~/Downloads/orientation-files.zip -d /tmp/verify
shasum -a 256 ~/Downloads/orientation-files/TOOL.md
shasum -a 256 /tmp/verify/orientation-files/TOOL.md
# Should match
rm -rf /tmp/verify
```

---

## Architecture

```
standard-model-of-code/          (repo - source of truth)
├── scripts/
│   ├── sync-orientation-files.sh    (main script)
│   └── launchd/
│       └── com.standardmodel.orientation-sync.plist.example
└── docs/
    └── ORIENTATION_FILES.md         (this file)

~/Downloads/
├── orientation-files/               (synced folder)
│   ├── REPO_README.md
│   ├── TOOL.md
│   ├── THEORY.md
│   └── ...
└── orientation-files.zip            (optional snapshot)

/Users/.../PROJECT_elements/
└── sync-orientation-files.sh        (backward compat wrapper, NOT in repo)
```

---

## Backward Compatibility

A wrapper script exists at the original location:
```
/Users/lech/PROJECTS_all/PROJECT_elements/sync-orientation-files.sh
```

This wrapper simply calls the repo-versioned script, so existing workflows continue to work.

---

*Last updated: 2026-01-16*
