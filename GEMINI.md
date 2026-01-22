# PROJECT_elements

> The effort to find the basic constituents of computer programs.

## Architecture

| Hemisphere | Path | Purpose |
|------------|------|---------|
| **Body** | `standard-model-of-code/` | Collider engine - parses code |
| **Brain** | `context-management/` | AI tools, cloud mirror |

## Commands

```bash
# Primary: Analyze a codebase
cd standard-model-of-code && ./collider full /path/to/repo --output /tmp/out

# AI query (this project uses Gemini)
python context-management/tools/ai/analyze.py "query" --set brain

# Socratic Verification (Antimatter Law Check)
python context-management/tools/ai/analyze.py --verify pipeline

# Tests
cd standard-model-of-code && pytest tests/ -q
```

## Coding Style

- Python 3.10+ required
- 4-space indentation
- Type hints for public functions
- Docstrings for modules and classes
- No `print()` in production code - use logging

## Key Paths

| Task | Location |
|------|----------|
| Collider engine | `standard-model-of-code/src/core/` |
| Atom schemas | `standard-model-of-code/schema/*.yaml` |
| AI tools | `context-management/tools/ai/` |
| Theory docs | `standard-model-of-code/docs/` |

## Rules

- Regenerate before debugging HTML: `./collider full . --output .collider`
- Run tests before commit
- Archive is read-only (large files in GCS)
- Know your hemisphere before editing

## Holographic-Socratic Layer

24/7 AI guardian detecting documentation/implementation drift.
- **Command**: `python context-management/tools/ai/analyze.py --verify pipeline`
- **Config**: `context-management/config/semantic_models.yaml`
- **Output**: `gs://elements-archive-2026/intelligence/`


## GCP

- Project: `elements-archive-2026`
- Model: `gemini-2.0-flash-001` (1M tokens)
- Bucket: `gs://elements-archive-2026/`

## Extended Context

@.gemini/context/body.md
@.gemini/context/brain.md
