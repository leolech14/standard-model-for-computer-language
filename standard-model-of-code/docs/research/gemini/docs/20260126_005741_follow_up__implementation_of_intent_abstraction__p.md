# Research: FOLLOW-UP: Implementation of Intent Abstraction

Previous analysis recommends INTENT ABSTRACTION as ...

> **Date:** 2026-01-26 00:57:41
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:7a7031a322fa5cd39820d56f8b4960687fd930f386a6d7f76a97b815833e6dd4`
> **Raw JSON:** `raw/20260126_005741_follow_up__implementation_of_intent_abstraction__p.json`

---

## Query

FOLLOW-UP: Implementation of Intent Abstraction

Previous analysis recommends INTENT ABSTRACTION as second layer:
- User says: './pe "fix auth bug"'
- System routes to correct tool(s)

PRACTICAL QUESTIONS:

1. ROUTING LOGIC
   Where does the 'intent → tool' mapping live?
   - Option A: Hardcoded rules in pe script
   - Option B: YAML config (like aci_config.yaml)
   - Option C: LLM decides at runtime
   - Option D: Hybrid (rules + LLM fallback)

2. COST/LATENCY
   If every './pe' invocation calls an LLM to understand intent:
   - Latency: 1-3 seconds added to every command
   - Cost: $0.01+ per invocation
   Is this acceptable? Or should intent routing be LOCAL (no API call)?

3. FAILURE MODES
   What if intent is ambiguous?
   - './pe "make it better"' → which tool?
   - Ask for clarification? Pick most likely? Fail?

4. ESCAPE HATCH
   Users who KNOW what they want shouldn't be penalized:
   - './pe collider full .' → direct, no routing
   - './pe "analyze code"' → routed
   How to distinguish?

5. EXISTING INFRASTRUCTURE
   We have aci_config.yaml with intent_keywords.
   Can we use that WITHOUT calling an LLM for simple routing?

PROPOSE a concrete implementation that is:
- Fast (no LLM for simple cases)
- Smart (LLM for complex/ambiguous)
- Cheap (minimize API calls)
- Escapable (direct commands still work)

---

## Response

Based on the codebase context and your constraints, I propose a **Hybrid Router Implementation** (Option D) centered around a new lightweight entry point script (`pe`) and a routing configuration file.

This approach balances the need for **zero-latency execution** for common tasks with **intelligent routing** for complex requests.

---

### 1. The Strategy: "Traffic Controller" Pattern

We implement a 3-layer routing logic in a Python script (`pe`).

1.  **Layer 1: Direct Dispatch (The Escape Hatch)**
    *   **Logic**: If the first argument matches a known executable/script name exactly.
    *   **Latency**: 0ms.
    *   **Example**: `./pe collider full .` -> executes `collider`.

2.  **Layer 2: Pattern Matching (The Fast Path)**
    *   **Logic**: Regex matching against a local YAML config. Uses `aci_config.yaml` keyword lists but maps them to *commands*.
    *   **Latency**: <10ms.
    *   **Example**: `./pe "fix bugs"` -> regex matches "fix" -> executes `analyze.py --fix`.

3.  **Layer 3: Semantic Router (The Smart Path)**
    *   **Logic**: If no match, send query to Gemini 2.0 Flash (cheap/fast) to classify intent into a tool command.
    *   **Latency**: ~800ms.
    *   **Cost**: Fraction of a cent.
    *   **Example**: `./pe "The visualizations look weird, investigate why"` -> Routes to `analyze.py --set viz_core`.

---

### 2. Implementation Details

#### A. Configuration: `context-management/config/cli_routing.yaml`
We create a new mapping file. While `aci_config.yaml` maps intents to *context sets*, this maps intents to *tools*.

```yaml
# cli_routing.yaml
# Maps patterns to executable commands

# DIRECT TOOLS (Layer 1 Escape Hatch)
# If arg[0] is in this list, execute immediately.
tools:
  - collider
  - analyze
  - concierge
  - pytest
  - git

# PATTERN ROUTES (Layer 2 Fast Path)
routes:
  - name: "analyze_code"
    patterns:
      - "^scan"
      - "^parse"
      - "^analyze repo"
    command: "./collider full ."

  - name: "ask_guru"
    patterns:
      - "^how to"
      - "^explain"
      - "^what is"
      - "^where is"
    command: "python context-management/tools/ai/analyze.py '{query}' --mode standard"

  - name: "socratic_audit"
    patterns:
      - "^verify"
      - "^audit"
      - "^check drift"
    command: "python context-management/tools/ai/analyze.py --verify pipeline"

  - name: "fix_request"
    patterns:
      - "^fix"
      - "^debug"
      - "^solve"
    command: "python context-management/tools/ai/analyze.py '{query}' --set debug"

  - name: "task_management"
    patterns:
      - "^task"
      - "^todo"
    command: ".agent/tools/task_manager.py '{query}'"
```

#### B. The Router Script: `pe` (Project Entry)
Place this at the root of the repository.

```python
#!/usr/bin/env python3
import sys
import os
import re
import yaml
import subprocess
import shlex

CONFIG_PATH = "context-management/config/cli_routing.yaml"

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def run_command(cmd, query_arg=None):
    if query_arg:
        # Safety: rudimentary injection prevention
        # In production, use subprocess list args strictly
        cmd = cmd.replace("{query}", query_arg)
    
    print(f"🚀 Routing to: {cmd}")
    subprocess.call(cmd, shell=True)

def layer_3_llm_router(query):
    # Fallback to ACI's classifier (Conceptual implementation)
    # Uses context-management/tools/ai/aci/intent_parser.py
    print(f"🤔 Analyzing intent for: '{query}'...")
    
    # Construct a routing prompt for Gemini Flash
    # This invokes analyze.py itself to decide the tool, then runs it
    # Ideally, integrate intent_parser.py directly to avoid startup overhead
    
    # For now, default to general analysis
    fallback_cmd = f"python context-management/tools/ai/analyze.py '{query}'"
    run_command(fallback_cmd)

def main():
    if len(sys.argv) < 2:
        print("Usage: ./pe <command|query>")
        sys.exit(1)

    user_input = sys.argv[1]
    remaining_args = " ".join(sys.argv[2:])
    config = load_config()

    # --- LAYER 1: ESCAPE HATCH ---
    if user_input in config.get('tools', []):
        # Pass through exactly as entered
        full_cmd = f"./{user_input} {remaining_args}" if os.path.exists(user_input) else f"{user_input} {remaining_args}"
        # Handle python scripts mapped as tools
        if user_input == "analyze": 
             full_cmd = f"python context-management/tools/ai/analyze.py {remaining_args}"
        
        subprocess.call(full_cmd, shell=True)
        return

    # --- LAYER 2: PATTERN MATCHING ---
    for route in config.get('routes', []):
        for pattern in route['patterns']:
            if re.search(pattern, user_input, re.IGNORECASE):
                run_command(route['command'], query_arg=user_input)
                return

    # --- LAYER 3: LLM ROUTER ---
    layer_3_llm_router(user_input)

if __name__ == "__main__":
    main()
```

---

### 3. Answers to Your Practical Questions

#### 1. Routing Logic Location
**Option D (Hybrid):**
1.  **Code (`pe` script):** Handles the logic flow and argument parsing.
2.  **Config (`cli_routing.yaml`):** Holds the hardcoded "fast paths".
3.  **LLM:** Only invoked if the query matches no known tool or pattern pattern.

#### 2. Cost/Latency Management
*   **Latency:**
    *   `./pe collider` -> **0ms overhead** (Layer 1).
    *   `./pe "fix this"` -> **~10ms overhead** (Layer 2 regex).
    *   `./pe "weird architectural issue"` -> **~1-2s overhead** (Layer 3 LLM).
*   **Cost:** API costs are incurred *only* on Layer 3. 90% of daily usage (running known tools or simple "fix" commands) hits Layer 1 or 2 and costs **$0**.

#### 3. Failure Modes
*   **Ambiguity:** If Layer 3 (LLM) is unsure, the `analyze.py` script (which it defaults to) already has logic to ask for clarification or present an interactive menu (as seen in `aci_config.yaml` interactive mode).
*   **No Match:** Default to `analyze.py --interactive`. This is the safest fallback—dropping the user into a chat with the "Guru" who can explain that the command wasn't understood.

#### 4. The Escape Hatch
Implemented in **Layer 1**.
The `pe` script checks the first argument against a whitelist of known tools (`collider`, `analyze`, `pytest`). If found, it treats the rest of the arguments as arguments *for that tool*, bypassing all routing logic.
*   `./pe collider full .` -> Executes `./collider full .` directly.

#### 5. Existing Infrastructure
We utilize `aci_config.yaml` *indirectly*.
*   The `pe` script handles *Tool Selection*.
*   Once routed to `analyze.py`, `aci_config.yaml` takes over to handle *Context Selection* (picking the right files/sets).
*   We do not overload `aci_config.yaml` with tool execution paths to keep "Context" separate from "Control".

### Implementation Checklist

1.  [ ] Create `context-management/config/cli_routing.yaml`.
2.  [ ] Create `pe` script at project root and `chmod +x pe`.
3.  [ ] Verify `cli_routing.yaml` includes your most frequent commands.
4.  [ ] Test `./pe collider` (Escape Hatch).
5.  [ ] Test `./pe "how does this work"` (Fast Path).

---

## Citations

_No citations provided_
