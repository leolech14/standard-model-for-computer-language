# Research: DESIGN AN 'EVER WAS, ALWAYS BEEN' ARCHITECTURE.

We have three fragmented systems that need unificat...

> **Date:** 2026-01-24 18:20:46
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:d1776f71c4ff54692e3edec0ed758f3bb0e9b82efb65e783e2223e57ebceb4a5`
> **Raw JSON:** `raw/20260124_182046_design_an__ever_was__always_been__architecture___w.json`

---

## Query

DESIGN AN 'EVER WAS, ALWAYS BEEN' ARCHITECTURE.

We have three fragmented systems that need unification:
- System A (Agent): context-management/tools/ai/ - queries, routing
- System B (Scientist): standard-model-of-code/tools/research/ - corpus validation
- System C (Librarian): context-management/tools/refinery/ - inventory, chunking

Current state: 65/100 coherence. A+C integrated, B orphaned via file I/O only.

CONSTRAINTS:
1. Must feel INEVITABLE - not 'bolted-on'
2. Must respect Wave-Particle separation (don't merge what shouldn't merge)
3. Must have SINGLE source of truth for architecture
4. Must allow Agent to invoke Scientist programmatically
5. Must resolve naming collisions (Refinery, Research, Atom)

DESIGN:
1. What is the MINIMAL change that creates maximum coherence?
2. What should the UNIFIED INTERFACE look like?
3. Where should the bridge live? What should it expose?
4. What naming convention resolves the collisions?
5. Draw the TARGET architecture diagram.

Make it feel like 'it always should have been this way.'

---

## Response

This is a classic "Interface Segregation" and "Domain Boundary" problem masquerading as an integration task.

The friction exists because **System B (Scientist)** is currently acting as an *external executable* (CLI/Scripts) rather than an *internal library* (API). In a mature architecture, the "Scientist" is the **Laboratory**—a distinct module within the Particle realm that the Wave realm can consult via a typed protocol.

Here is the **"Ever Was, Always Been"** design.

### 1. The Core Concept: The Laboratory Bridge

To solve the "Orphaned Scientist" problem without violating Wave-Particle duality, we introduce the **Laboratory Layer**.

- **Particle Realm (`standard-model-of-code/`)** is the physics engine.
- **Wave Realm (`context-management/`)** is the intelligence.
- **The Bridge:** We do not merge them. We expose the **Laboratory** within the Particle realm as a strictly typed Python API.

The Agent (Wave) does not "run scripts." The Agent **commissions experiments** via the Laboratory API.

### 2. The Minimal Change (Maximum Coherence)

We perform a **Code Promotion**:
1.  Move `standard-model-of-code/tools/research/` → `standard-model-of-code/src/laboratory/`.
2.  Add `__init__.py` to expose a Unified Inquiry Interface.

This changes System B from a "bag of scripts" to a "first-class module."

### 3. Naming Collisions: The "Isotopes" Resolution

We resolve collisions by strictly defining the *state* of the matter:

| Concept | Particle Name (Physics) | Wave Name (Knowledge) | Definition |
|:---:|:---:|:---:|---|
| **Smallest Unit** | `CodeAtom` | `ContextNode` | `CodeAtom` is AST/Syntax. `ContextNode` is Semantic/Embedding. |
| **Processing** | `Collider` | `Refinery` | `Collider` parses structure. `Refinery` summarizes meaning. |
| **Output** | `Metric` | `Insight` | `Metric` is a number (84% coverage). `Insight` is the interpretation. |

### 4. The Unified Interface

The Agent (System A) imports the Laboratory (System B) directly. No subprocesses, no file watching.

**File:** `standard-model-of-code/src/laboratory/__init__.py`

```python
"""
THE LABORATORY
The interface where Wave (Intelligence) requests measurements from Particle (Physics).
"""
from dataclasses import dataclass
from typing import List, Optional
from ..core.atoms import CodeAtom  # The Physics Atom

@dataclass
class ExperimentRequest:
    target_path: str
    hypothesis: str  # e.g., "Pareto distribution of complexity"
    granularity: str # "file", "function", "block"

@dataclass
class ExperimentResult:
    confirmed: bool
    metrics: dict
    anomalies: List[CodeAtom]
    confidence: float

class ChiefScientist:
    """The programmatic entry point for the Agent."""
    
    @staticmethod
    def measure_coverage(path: str) -> float:
        """Direct access to System B metrics."""
        pass

    @staticmethod
    def run_experiment(request: ExperimentRequest) -> ExperimentResult:
        """Complex validation logic from research tools."""
        pass
```

**Usage in Agent (System A):**

```python
# context-management/tools/ai/orchestrator.py

# "It always should have been this way..."
from standard_model.laboratory import ChiefScientist, ExperimentRequest

def verify_hypothesis(repo_path: str):
    # Agent (Wave) asks Scientist (Particle)
    result = ChiefScientist.run_experiment(ExperimentRequest(
        target_path=repo_path,
        hypothesis="T2_saturation",
        granularity="function"
    ))
    
    # Agent sends result to Librarian (Refinery) for long-term storage
    from .aci.refinery import Refinery
    Refinery.archive(result)
```

### 5. Target Architecture Diagram

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           THE "EVENT HORIZON"                                 ║
║         (Where Probability collapses into Measurement)                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   WAVE REALM (Context & Intelligence)          PARTICLE REALM (Code & Physics)║
║   path: context-management/                    path: standard-model-of-code/  ║
║                                                                               ║
║   ┌─────────────────────────────┐              ┌───────────────────────────┐  ║
║   │      SYSTEM A: AGENT        │              │    SYSTEM B: SCIENTIST    │  ║
║   │ (The Observer)              │   IMPORTS    │ (The Laboratory)          │  ║
║   │                             ├─────────────►│ src/laboratory/           │  ║
║   │  • ACI (Brain)              │              │ • Experiment Protocols    │  ║
║   │  • Intent Router            │    RETURNS   │ • Metric Engines          │  ║
║   │  • Strategy                 │◄─────────────┤ • Validation Logic        │  ║
║   └─────────────┬───────────────┘    DATA      └─────────────┬─────────────┘  ║
║                 │                                            │                ║
║                 │ "Store this"                               │ Uses           ║
║                 ▼                                            ▼                ║
║   ┌─────────────────────────────┐              ┌───────────────────────────┐  ║
║   │    SYSTEM C: LIBRARIAN      │              │         COLLIDER          │  ║
║   │ (The Refinery)              │              │ (The Engine)              │  ║
║   │                             │              │                           │  ║
║   │  • ContextNodes (Semantics) │              │  • CodeAtoms (AST)        │  ║
║   │  • Vector Store             │              │  • Graph Generation       │  ║
║   │  • RAG Cache                │              │  • Parsing                │  ║
║   └─────────────────────────────┘              └───────────────────────────┘  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Summary of Changes

1.  **Refactor:** Rename/Move `standard-model-of-code/tools/research` to `standard-model-of-code/src/laboratory`.
2.  **Unify:** Create `ChiefScientist` class in `laboratory/__init__.py` as the Facade Pattern for all research scripts.
3.  **Integrate:** Update `context-management` requirements to install `standard-model-of-code` in editable mode (`-e .`), allowing direct imports.
4.  **Rename:** Ensure `Refinery` (Wave) inputs `ContextNode` and `Laboratory` (Particle) outputs `CodeAtom`.

This design makes the system feel inevitable: **The Agent thinks (Wave), the Scientist measures (Particle), and the Librarian remembers (Synthesis).**

---

## Citations

_No citations provided_
