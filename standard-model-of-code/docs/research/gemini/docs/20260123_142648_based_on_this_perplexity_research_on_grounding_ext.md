# Research: Based on this Perplexity research on grounding external queries:

PERPLEXITY RECOMMENDATIONS:
1. Use...

> **Date:** 2026-01-23 14:26:48
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:cc6437fa97a2cab0569b90fbfbfc5d4cf483e7487a520df28ec0cb84f19dd4e0`
> **Raw JSON:** `raw/20260123_142648_based_on_this_perplexity_research_on_grounding_ext.json`

---

## Query

Based on this Perplexity research on grounding external queries:

PERPLEXITY RECOMMENDATIONS:
1. Use HYBRID approach: Static template + LLM refinement
2. Context prefix should be 300-600 tokens
3. Structure: YAML/markdown block with markers (---context---)
4. Include: project domain, key constraints, stack, 1-2 code examples
5. Have Gemini extract query-relevant context before sending to Perplexity

Given our existing analyze.py architecture:
1. Where exactly should the context injection code go?
2. What existing functions/modules can we reuse?
3. Should this be a new module or integrated into existing flow?
4. What's the minimal change to implement this properly?

Provide specific file paths and function names from the codebase.

---

## Response

Based on the analysis of your codebase and the Perplexity recommendations, here is the architectural plan and minimal implementation guide.

### 1. Architecture: The Hybrid Grounding Flow

Instead of sending the raw query directly to Perplexity, we will interject a "Grounding Phase" using the existing Gemini client in `analyze.py`.

**Flow:**
1.  **ACI Routing:** Detects `Tier.PERPLEXITY`.
2.  **Context Loading:** Load `semantic_models.yaml` (Antimatter Laws/Domain) + `analysis_sets.yaml` (Stack definitions).
3.  **Gemini Extraction:** Ask Gemini to "Rewrite this query for an external researcher, appending minimal relevant context (Stack, Domain, Constraints) from our project."
4.  **Perplexity Execution:** Send the *grounded* query to `perplexity_research.py`.

### 2. Implementation Answers

#### 1. Where exactly should the context injection code go?
The logic belongs in **`context-management/tools/ai/analyze.py`**. Specifically, inside the `main()` function within the `if decision.tier == Tier.PERPLEXITY:` block (approx line 1228).

#### 2. What existing functions/modules can we reuse?
*   **`load_semantic_models()`**: (Line 1076 in `analyze.py`) To fetch Domain definitions and Antimatter Laws.
*   **`create_client()`**: (Line 923 in `analyze.py`) To initialize Gemini for the extraction step.
*   **`semantic_models.yaml`**: As the source of "Project Domain" and "Constraints".

#### 3. Should this be a new module?
**No.** It should be a helper function within `analyze.py` or integrated directly into the `main` flow. Creating a new module for ~20 lines of "glue code" is over-engineering.

#### 4. Minimal Change Implementation
We need to:
1.  Hoist `create_client()` (or call it on demand) inside the Perplexity block.
2.  Read `semantic_models.yaml`.
3.  Run a quick "One-Shot" Gemini call to generate the grounded prompt.

---

### 3. Implementation Plan

Here are the specific changes for **`context-management/tools/ai/analyze.py`**.

#### A. Add Helper Function
Add this function near `load_semantic_models` (approx line 1082) to construct the context packet recommended by Perplexity (YAML/Markdown block).

```python
def generate_grounded_perplexity_query(client, user_query, project_root):
    """
    Uses Gemini to rewrite the user query with a 'Context Prefix' 
    based on semantic models (Stack, Domain, Constraints).
    """
    # 1. Load Sources
    semantic_config = load_semantic_models()
    
    # 2. Extract High-Level Context (Domain & Constraints)
    # We map 'antimatter' laws to 'Constraints' and definitions to 'Domain'
    domain_context = {
        "domain_definitions": list(semantic_config.get('definitions', {}).keys()),
        "constraints": [law['name'] for law in semantic_config.get('antimatter', [])],
        "tech_stack": ["Python 3", "Gemini API", "Vertex AI", "FastAPI"] # Could be dynamic, but static is safer for now
    }
    
    context_str = yaml.dump(domain_context, default_flow_style=False)

    # 3. Prompt Gemini to fuse them (The Hybrid Approach)
    prompt = f"""
    You are a Research Proxy. Prepare a query for an external search engine (Perplexity).
    
    USER QUERY: "{user_query}"
    
    PROJECT CONTEXT (YAML):
    {context_str}
    
    INSTRUCTIONS:
    1. Rewrite the user query to be self-contained.
    2. Append a Markdown block named "---context---" containing ONLY relevant stack details and constraints from the YAML above.
    3. Keep the total length under 600 tokens.
    4. Do NOT answer the question. Just output the refined query string.
    """
    
    try:
        response = client.models.generate_content(
            model=FAST_MODEL, # Use Flash for speed
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Warning: Grounding failed ({e}). Using raw query.", file=sys.stderr)
        return user_query
```

#### B. Modify the Perplexity Block
Update the `if decision.tier == Tier.PERPLEXITY:` block in `main()` (approx line 1228).

```python
        # TIER 3: PERPLEXITY - External research
        if decision.tier == Tier.PERPLEXITY:
            print("[PERPLEXITY] External research tier selected.", file=sys.stderr)
            
            # --- START NEW GROUNDING LOGIC ---
            print("[PERPLEXITY] Grounding query with local context...", file=sys.stderr)
            
            # 1. Initialize Gemini Client (needed for grounding step)
            # Note: We ignore project_id here as we just need the client
            grounding_client, _ = create_client()
            
            # 2. Generate Grounded Query
            grounded_query = generate_grounded_perplexity_query(
                grounding_client, 
                args.prompt, 
                PROJECT_ROOT
            )
            
            if args.aci_debug:
                print(f"\n[Grounding] Rewritten Query:\n{grounded_query}\n", file=sys.stderr)
            # --- END NEW GROUNDING LOGIC ---

            if not HAS_PERPLEXITY:
                print("Perplexity module not available. Falling back to LONG_CONTEXT.", file=sys.stderr)
                decision = analyze_and_route(args.prompt, force_tier="long_context")
            else:
                start_time = time.time()
                try:
                    print(f"[PERPLEXITY] Executing research query...", file=sys.stderr)
                    
                    # CHANGED: Pass grounded_query instead of args.prompt
                    result = perplexity_research(grounded_query) 
                    
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Display results (Existing code follows...)
                    print("\n" + "=" * 60)
                    print("PERPLEXITY RESEARCH RESULTS")
                    # ... rest of existing block
```

### 4. Summary of Changes

| File | Change | Purpose |
| :--- | :--- | :--- |
| `analyze.py` | Add `generate_grounded_perplexity_query` | Implements the "Hybrid" static template + LLM refinement logic. |
| `analyze.py` | Update `Tier.PERPLEXITY` block | Initializes Gemini client early to rewrite the query before sending to Perplexity. |
| `semantic_models.yaml` | (Read-only access) | Used as the single source of truth for the "Context Prefix". |

This implementation satisfies the Perplexity recommendation of sending a structured `---context---` block while leveraging your existing `semantic_models.yaml` as the source of truth, without requiring new files or heavy refactoring.

---

## Citations

_No citations provided_
