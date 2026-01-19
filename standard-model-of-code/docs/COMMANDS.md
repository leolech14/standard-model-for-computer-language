# Command Reference

[Home](../README.md) > [Docs](./README.md) > **Commands**

---

## FOR AI: When to Read This
- Read when: need to run Collider, check syntax, find flags
- All commands copy-paste ready

---

## Primary Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `./collider full <path>` | Complete analysis | `./collider full src/` |
| `./collider full <path> --output <dir>` | Analysis with custom output | `./collider full . --output .collider` |
| `./collider full <path> --ai-insights` | Analysis with AI enrichment | `./collider full src/ --ai-insights` |
| `./collider analyze <path>` | Canonical analysis | `./collider analyze /path/to/repo` |

---

## Graph Analysis Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `./collider doctor <path>` | Pipeline + output validation | `./collider doctor src/` |
| `./collider graph <graph.json>` | Analyze code graph | `./collider graph .collider/unified_analysis.json` |
| `./collider graph <graph.json> --bottlenecks` | Show bottleneck analysis | `./collider graph graph.json --bottlenecks` |
| `./collider graph <graph.json> --shortest-path <a:b>` | Find path between functions | `./collider graph graph.json --shortest-path main:validate` |

---

## Visualization Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `./collider viz <graph.json>` | Generate HTML visualization | `./collider viz .collider/unified_analysis.json` |
| `./collider viz <graph.json> --3d` | 3D visualization | `./collider viz graph.json --3d` |

---

## Development Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `pip install -e .` | Install in dev mode | `pip install -e .` |
| `pytest tests/` | Run test suite | `pytest tests/ -v` |
| `pytest tests/ -q` | Quick test run | `pytest tests/ -q` |

---

## Self-Check Commands

| Command | Purpose |
|---------|---------|
| `./collider full src/core --output /tmp/self_check` | Self-analyze Collider |
| `./collider full . --output .collider` | Full repo check |

---

## Cloud/AI Commands

| Command | Purpose |
|---------|---------|
| `gcloud auth application-default login` | Authenticate for AI |
| `python tools/ai/analyze.py "<query>"` | Query codebase with AI |

---

## Flags Reference

| Flag | Description |
|------|-------------|
| `--output`, `-o` | Output directory for results |
| `--ai-insights` | Enable LLM enrichment layer |
| `--verbose`, `-v` | Detailed logging |
| `--timing` | Enable pipeline timing |
| `--verbose-timing` | Per-stage timing |
| `--bottlenecks` | Show only bottleneck analysis |
| `--3d` | Use 3D visualization |
| `--help`, `-h` | Show help |

---

## Output Files

| File | Purpose |
|------|---------|
| `unified_analysis.json` | Structured graph data |
| `output.md` | Brain Download report |
| `collider_report.html` | Interactive 3D visualization |

---

## Common Workflows

### Quick Analysis
```bash
./collider full . --output .collider
```

### With AI Insights
```bash
gcloud auth application-default login
./collider full . --ai-insights --output .collider
```

### Self-Check (debugging)
```bash
./collider full src/core --output /tmp/self_check
```

### Find Bottlenecks
```bash
./collider full . --output analysis
./collider graph analysis/unified_analysis.json --bottlenecks
```
