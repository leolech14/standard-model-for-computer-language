---
paths:
  - "context-management/**"
---

# Wave (AI/Context) Rules

## AI Analysis Tool
- Location: `tools/ai/analyze.py`
- Model: `gemini-3-pro-preview` (default, best reasoning)
- Backend: AI Studio (default) or Vertex AI (optional)

### Setup (AI Studio - Recommended)
```bash
export GEMINI_API_KEY="your-key"  # from aistudio.google.com
doppler run -- python analyze.py "your query"
```

### Setup (Vertex AI - Enterprise)
```bash
export GEMINI_BACKEND=vertex
gcloud auth application-default login
python analyze.py "your query"
```

## Analysis Sets
- Defined in: `config/analysis_sets.yaml`
- Use `--set brain` for Wave (AI tools) analysis
- Use `--set body` for Particle (Collider) analysis

## Cloud Mirror
- Tool: `tools/archive/archive.py`
- Bucket: `gs://elements-archive-2026/`
- Large outputs stored in GCS, not git

## Analysis Modes
- `--mode standard`: General analysis
- `--mode forensic`: Line-level citations required
- `--mode architect`: Theory-aware analysis

## Retry Logic
- Built-in exponential backoff for rate limits
- Max 5 retries with jitter
