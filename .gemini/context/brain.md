# Brain (AI/Context) Context

## AI Analysis Tool

Location: `context-management/tools/ai/analyze.py`

### Authentication

```bash
gcloud auth application-default login
gcloud config set project elements-archive-2026
```

### Usage

```bash
# Standard analysis
python analyze.py "your question" --set brain_core

# Forensic mode (requires line citations)
python analyze.py "find all imports" --mode forensic

# Architect mode (theory-aware)
python analyze.py "explain topology" --mode architect
```

### Analysis Sets

Defined in `config/analysis_sets.yaml`:
- `brain_core`: AI tools and analysis code
- `body`: Collider implementation
- `theory`: Documentation and specs

## Cloud Mirror

Tool: `tools/archive/archive.py`

```bash
# Sync to GCS
python archive.py mirror

# Check status
python archive.py status
```

Bucket: `gs://elements-archive-2026/repository_mirror/`

## Rate Limits

- Model: `gemini-2.0-flash-001`
- Context: 1M tokens
- Concurrent requests: 3
- Built-in retry with exponential backoff
