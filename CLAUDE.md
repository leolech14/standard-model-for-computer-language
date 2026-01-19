# CLAUDE.md - PROJECT_elements

> **The effort to find the basic constituents of computer programs.**

---

## QUICK ORIENTATION (Read This First)

This is a **two-hemisphere** system:

| Hemisphere | Directory | Purpose | When to Use |
|------------|-----------|---------|-------------|
| **BODY** | `standard-model-of-code/` | The Collider engine - parses and analyzes code | Implementation, parsing, analysis |
| **BRAIN** | `context-management/` | AI tools, theory docs, cloud mirror | Research, AI queries, archival |

**Rule:** Know which hemisphere you're working in. Each has its own CLAUDE.md.

---

## INSTANT COMMANDS

```bash
# Analyze any codebase (THE PRIMARY TOOL)
cd standard-model-of-code && ./collider full /path/to/repo --output /tmp/analysis

# Ask AI about this codebase (requires GCP auth)
python context-management/tools/ai/analyze.py "your question here" --set brain_core

# Run tests
cd standard-model-of-code && pytest tests/

# Sync to cloud mirror
python context-management/tools/archive/archive.py mirror
```

---

## THE PROJECT IN ONE PARAGRAPH

PROJECT_elements seeks to define a **"Standard Model of Code"** - a periodic table of software constructs. The theory identifies **167 atoms** (fundamental code particles like `function_def`, `class_decl`, `import_stmt`) organized into tiers. The **Collider** tool applies this theory to real codebases, producing structured analysis reports. The **Brain** hemisphere manages AI-assisted research and cloud context.

---

## DIRECTORY MAP

```
PROJECT_elements/
├── CLAUDE.md                    # YOU ARE HERE
├── README.md                    # Project overview
├── PROJECT_MAP.md               # Visual architecture diagram
│
├── standard-model-of-code/      # THE BODY (Implementation)
│   ├── CLAUDE.md                # Body-specific agent instructions
│   ├── cli.py                   # Entry point: ./collider
│   ├── src/core/                # Collider engine
│   ├── schema/                  # Atom definitions (YAML)
│   ├── docs/                    # Theory documentation
│   └── tests/                   # Test suite
│
├── context-management/          # THE BRAIN (Intelligence)
│   ├── tools/ai/analyze.py      # AI analysis tool (Gemini)
│   ├── tools/archive/           # Cloud mirror system
│   ├── docs/                    # Theory, manuals, roadmaps
│   └── config/                  # Analysis set definitions
│
├── archive/                     # Historical artifacts (36% of repo)
└── related/                     # Adjacent experiments
```

---

## ROUTING TABLE

| You want to... | Go to... | Read... |
|----------------|----------|---------|
| Run the Collider | `standard-model-of-code/` | `CLAUDE.md` there |
| Modify parsing logic | `standard-model-of-code/src/core/` | `full_analysis.py` |
| Add new atoms | `standard-model-of-code/schema/` | YAML files |
| Ask AI questions | `context-management/tools/ai/` | `analyze.py --help` |
| Understand the theory | `standard-model-of-code/docs/` | `THEORY_MAP.md` |
| Debug HTML visualization | `standard-model-of-code/src/core/viz/` | Regenerate first! |

---

## CRITICAL RULES

### 1. Never Trust Old Outputs
If debugging HTML/visualizations, **always regenerate**:
```bash
cd standard-model-of-code && ./collider full . --output .collider
```

### 2. Know Your Hemisphere
- Editing `src/core/*.py`? You're in the **Body**.
- Editing `tools/ai/*.py`? You're in the **Brain**.
- Don't mix concerns.

### 3. Archive is Read-Only
The `archive/` directory (36% of repo) is historical. Don't modify it. Large outputs are in GCS:
```
gs://elements-archive-2026/large_outputs/
```

### 4. Tests Before Commit
```bash
cd standard-model-of-code && pytest tests/ -q
```

---

## THE THEORY (Condensed)

### Atoms
The 167 fundamental code constructs, organized by tier:
- **Tier 0 (Core):** `function_def`, `class_def`, `import`, `variable`, `call`
- **Tier 1 (Stdlib):** `async_function`, `decorator`, `comprehension`, `generator`
- **Tier 2 (Ecosystem):** Framework-specific patterns

### The RPBL Dimensions
Every code unit has four measurable properties:
- **R**esponsibility: What it does (data, logic, IO, orchestration)
- **P**urity: Side effects (pure, impure, mixed)
- **B**oundary: Exposure (internal, exported, entry point)
- **L**ifecycle: State (stateless, stateful, singleton)

### The 16-Level Scale
From bit to universe:
```
Bit → Byte → Token → Expression → Statement → Block →
Function → Class → Module → Package → Service →
System → Platform → Ecosystem → Industry → Universe
```

---

## GCP CONFIGURATION

This project uses Google Cloud for AI and storage:

| Resource | Value |
|----------|-------|
| Project | `elements-archive-2026` |
| Billing | `PROJECT_elements Billing Account` |
| AI Model | `gemini-2.0-flash-001` (1M context) |
| Storage | `gs://elements-archive-2026/` |

```bash
# Verify auth
gcloud auth list
gcloud config get-value project
```

---

## SPECIALIZED CLAUDE.md FILES

For deep work, read the hemisphere-specific instructions:

| Location | Focus |
|----------|-------|
| `standard-model-of-code/CLAUDE.md` | Collider implementation, output format, key files |
| `context-management/.agent/orientation/CLAUDE.md` | AI tools, analysis modes |

---

## OWNER

Leonardo Lech (leonardo.lech@gmail.com)

---

*Last updated: 2026-01-19*
