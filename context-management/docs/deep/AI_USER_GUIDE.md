# AI User Guide: The Alien Architecture

> "We are building the Standard Model of Code. This requires tools that can see the hypercomplex topology."

## The Core Problem: Context Amnesia
Standard AI tools (IDE Chat) have a limited view. They see only what is open. They cannot reason about the "Global Topology" of 10,000 files, nor can they rigorously verify "line-level evidence" across the entire repo.

## The Solution: Three Specialized Roles

We have deployed a "Triad" of AI capabilities to solve this.

### 1. The Librarian (Exploration & Discovery)
**Tool**: Vertex AI Agent Builder (Web Interface)
**Best For**: "Where is X?", Onboarding, finding the "needle in the haystack".
**Mechanism**: Search Index (RAG).
**Usage**:
- Go to [Agent Builder Console](https://console.cloud.google.com/gen-app-builder/data-stores?project=elements-archive-2026).
- Ask: *"Where is the retry logic for GCS uploads?"*
- Result: Returns specific file chunks and summaries.

### 2. The Surgeon (Forensic Traceability)
**Tool**: `context-management/tools/ai/analyze.py --mode forensic`
**Best For**: Verification, Auditing, "Prove it".
**Mechanism**: Gemini 2.0 Flash with strict citation instructions.
**Usage**:
```bash
python context-management/tools/ai/analyze.py "List all hardcoded timeout values in the archive tool" --dir context-management/tools/archive --mode forensic
```
**Why it works**: The system prompt forces the AI to output:
> `[context-management/tools/archive/archive.py:L45-L48]` "timeout=30"

### 3. The Architect (Global Reasoning)
**Tool**: `context-management/tools/ai/analyze.py --mode architect`
**Best For**: High-level design, Theory-vs-Implementation checks.
**Mechanism**: Injects `metadata/COLLIDER_ARCHITECTURE.md` into the context window automatically.
**Usage**:
```bash
python context-management/tools/ai/analyze.py "Does the archive tool violate the 'Atom' isolation principle?" --mode architect
```
**Why it works**: The model "reads" your theory definitions before looking at the code, ensuring it speaks your language (Rings, Atoms, Tiers).

### 5. The Holographic-Socratic Layer (Continuous Validation)
**Tool**: `context-management/tools/ai/analyze.py --verify`
**Best For**: Automated semantic auditing, Antimatter Law enforcement, codebase health monitoring.
**Mechanism**: File-change triggers + scheduled runs + SocraticValidator class.
**Usage**:
```bash
# Audit a domain against Antimatter Laws
python context-management/tools/ai/analyze.py --verify pipeline

# Audit specific candidate file
python context-management/tools/ai/analyze.py --verify pipeline --candidate path/to/file.py
```
**Why it works**: The layer reconstructs full context from any partial query (Holographic) and perpetually questions code against invariants (Socratic). See [HOLOGRAPHIC_SOCRATIC_LAYER.md](./HOLOGRAPHIC_SOCRATIC_LAYER.md) for full documentation.

### 4. The Live Collaborator (Local Development)
**Tool**: `context-management/tools/ai/analyze.py`
**Best For**: Active development, Debugging, "Chat with my code".

**Three Modes of Operation**:
1.  **Tier 1 (Vertex AI)**: Deep reasoning, long-context (1M+ tokens).
2.  **Tier 2 (File Search)**: Fast, cheap RAG with citations (requires `GEMINI_API_KEY`).
3.  **Tier 3 (Socratic Verification)**: Automated semantic auditing and guardrail enforcement.

**Usage**:

**Tier 1: Deep Reasoning (Vertex)**
```bash
# Chat with your local changes (uses .tools_venv)
python context-management/tools/ai/analyze.py --interactive --set body
```

**Tier 2: Fast RAG (File Search)**
```bash
# 1. Index a set (e.g. 'renderer') to a store
export GEMINI_API_KEY="..."
python context-management/tools/ai/analyze.py --index --set renderer --store-name renderer-v1

# 2. Ask questions with citations
python context-management/tools/ai/analyze.py --search "How are textures loaded?" --store-name renderer-v1
```

**Tier 3: Socratic Verification (The Critic)**
```bash
# Audit a domain against Antimatter Laws
python context-management/tools/ai/analyze.py --verify pipeline

# Check a specific candidate file
python context-management/tools/ai/analyze.py --verify pipeline --candidate standard-model-of-code/src/core/violation_stage.py
```

**Insights (Structured Output)**
```bash
python context-management/tools/ai/analyze.py --mode insights --file "README.md" --output "report.json"
```

## The Workflows

### A. The Cloud Audit Loop (for Merged Code)

1.  **Mirror the Brain**:
    ```bash
    python context-management/tools/archive/archive.py mirror
    ```
    *Builds the global context in the cloud.*

2.  **Consult the Architect**:
    ```bash
    .tools_venv/bin/python context-management/tools/ai/analyze.py "Review tools/archive for compliance with the Standard Model" --mode architect
    ```

### B. The Local Dev Loop (for Active Work)

1.  **Code & Save**: (No mirroring needed)

2.  **Ask for Help**:
    ```bash
    .tools_venv/bin/python context-management/tools/ai/analyze.py --interactive
    ```
    *Interactive session loads your local files instantly.*
