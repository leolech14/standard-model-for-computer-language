# Research: Verify the Laboratory Bridge implementation. Check laboratory.py and laboratory_bridge.py. Does this...

> **Date:** 2026-01-24 19:04:41
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:9d0bcc3ddda17653a2b193f7d934a3ee7a9453b002ff9a28d8e3b96f23d4c7bf`
> **Raw JSON:** `raw/20260124_190441_verify_the_laboratory_bridge_implementation__check.json`

---

## Query

Verify the Laboratory Bridge implementation. Check laboratory.py and laboratory_bridge.py. Does this solve the orphaned Scientist problem? What docs need updating?

---

## Response

Based on the provided codebase context, I have analyzed `tools/research/laboratory.py`. Note that **`laboratory_bridge.py` was not included in the file context**, so my analysis infers its role as the client-side (Agent) consumer of `laboratory.py`.

### 1. Verification of `laboratory.py` (The Scientist Facade)

The implementation of `tools/research/laboratory.py` serves as a robust **Anti-Corruption Layer** between the Agent (Wave) and the Research Scripts (Particle).

**Key Strengths:**
*   **Command Templating:** By using Jinja-like placeholders (`{python}`, `{repo_path}`, `{unified_analysis}`), it decouples the *intent* ("run collider") from the *implementation* ("python collider.py ..."). This allows researchers to refactor scripts without breaking the Agent, provided the template is updated.
*   **Standardized Output (`ExperimentResult`):** The Agent no longer needs to parse heterogeneous CLI stdout. It receives a strictly typed JSON object containing status, artifact paths, and summaries.
*   **Artifact Abstraction:** It manages `out_dir`, logging, and artifact persistence (`.laboratory_runs/`), keeping the repo clean and giving the Agent a reliable file system location to read results.
*   **Robustness:** Includes timeouts, error aggregation, and fallback logic for hypothesis confirmation (`_infer_confirmed`).

**Potential Weakness identified in `laboratory.py`:**
*   **Implicit Dependencies:** It assumes the existence of specific internal artifacts (like `unified_analysis.json`) for the happy path. If the underlying research tool changes its output filename format, `laboratory.py` logic (specifically lines 220-226) will need manual updates.

### 2. The Missing `laboratory_bridge.py`

Since `laboratory_bridge.py` is missing from the context, I cannot verify the client implementation. However, based on `laboratory.py`, a correct bridge should:
1.  **Wrap the CLI:** constructing `ExperimentRequest` objects.
2.  **Inject Templates:** Providing default templates (e.g., `LAB_COLLIDER_CMD_TEMPLATE`) via environment variables or configuration, so the Agent code remains agnostic to the specific shell commands.
3.  **Type Safety:** Convert the raw JSON output from `laboratory.py` back into Pydantic models for the Agent to use in reasoning loops.

### 3. Does this solve the "Orphaned Scientist" Problem?

**YES.**

The "Orphaned Scientist" problem occurs when research tooling evolves rapidly (changing arguments, output formats, script names), causing the Agent's hardcoded tool invocations to break, effectively "orphaning" the scientist's latest work from the Agent's capabilities.

`laboratory.py` solves this by:

1.  **Inversion of Control:** The Agent defines *what* it needs (a hypothesis test), but the configuration (templates) defines *how* to execute it.
2.  **Stable Contract:** The `ExperimentResult` JSON schema is the stable contract. As long as `laboratory.py` is maintained to output this JSON, the underlying scripts (`run_corpus.py`, `evaluate_hypotheses.py`) can change completely.
3.  **Dual Mode:** It supports both "generate analysis" (run collider) and "analyze existing" (pass `unified_analysis_path`), allowing the Agent to switch between generating expensive data and analyzing cached data without changing its logic.

### 4. Documentation Updates Required

To fully operationalize this bridge, the following documentation updates are necessary:

1.  **`docs/research/README.md`**:
    *   **Add:** A section on "The Laboratory Interface."
    *   **Explain:** How to run experiments via `laboratory.py` locally (for researchers to verify their scripts work with the Agent).
    *   **Define:** The standard command templates. Example:
        ```bash
        # Standard Collider Template
        export LAB_COLLIDER_CMD_TEMPLATE='["{python}", "tools/research/run_corpus.py", "{repo_path}", "--output", "{out_dir}"]'
        ```

2.  **`docs/architecture/WAVE_PARTICLE_BRIDGE.md` (New or Update)**:
    *   Formalize the `ExperimentRequest` -> `laboratory.py` -> `ExperimentResult` data flow.
    *   Explicitly state that Agents **must not** call `run_corpus.py` or `atom_coverage.py` directly anymore.

3.  **`tools/research/README.md`**:
    *   Update usage examples to favor `laboratory.py` as the entry point.

### 5. Recommendations

**A. Fix Hardcoded Filenames in `laboratory.py`**
Lines 220-226 hardcode `unified_analysis.json`.
*   *Recommendation:* Make the output filename configurable in the request or template context, defaulting to `unified_analysis.json`.

**B. Add `laboratory_bridge.py` Stub**
If `laboratory_bridge.py` does not exist, create it as a Python module that exposes a function `run_agent_experiment(...)` which wraps the `subprocess.run` call to `laboratory.py`.

**C. Verification Script**
Create a `tools/research/verify_lab.py` that runs a mock experiment using `laboratory.py` against a known repo (like one of the pilot repos) to ensure the full pipeline (Command -> Lab -> Script -> Output -> Lab -> JSON) works.

**Implementation of Missing `laboratory_bridge.py` (Draft):**

```python
# tools/research/laboratory_bridge.py
import subprocess
import json
import sys
from pathlib import Path
from typing import Optional
from .laboratory import ExperimentRequest, ExperimentResult

LAB_SCRIPT = Path(__file__).parent / "laboratory.py"

def run_experiment_sync(request: ExperimentRequest) -> ExperimentResult:
    """Synchronous bridge for Agents to call the Laboratory."""
    cmd = [sys.executable, str(LAB_SCRIPT), "run"]
    
    if request.repo_path:
        cmd.extend(["--repo", str(request.repo_path)])
    if request.unified_analysis_path:
        cmd.extend(["--unified-analysis", str(request.unified_analysis_path)])
    if request.hypothesis:
        cmd.extend(["--hypothesis", request.hypothesis])
    
    # Pass templates via Env or Args (Args preferred for explicit control)
    if request.collider_cmd_template:
        cmd.extend(["--collider-cmd-template", request.collider_cmd_template])
        
    try:
        # Capture stdout to get the artifact path
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        # The last line of stdout is the artifact path
        artifact_path = proc.stdout.strip().splitlines()[-1] if proc.stdout else ""
        
        if proc.returncode != 0 or not artifact_path.endswith(".json"):
            return ExperimentResult(
                run_id=request.run_id,
                created_at_utc="", 
                ok=False, 
                confirmed=None, 
                summary={}, 
                artifacts={}, 
                logs={"stderr": proc.stderr}, 
                errors=["Laboratory CLI failed", proc.stderr]
            )
            
        # Read the result file
        with open(artifact_path) as f:
            data = json.load(f)
            return ExperimentResult(**data)
            
    except Exception as e:
        return ExperimentResult(
            run_id=request.run_id,
            created_at_utc="",
            ok=False, 
            confirmed=None, 
            summary={}, 
            artifacts={}, 
            logs={}, 
            errors=[str(e)]
        )
```

---

## Citations

_No citations provided_
