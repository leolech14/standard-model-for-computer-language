#!/usr/bin/env python3
"""
Professional Code Analysis Tool
===============================
Leverages Google Cloud Vertex AI (Gemini Models) to analyze the mirrored codebase.
Features:
- Reads directly from GCS Mirror (no local download).
- Cost-aware: Estimates tokens before running.
- Flexible: Supports file patterns, directory filtering.
- Models: Gemini 1.5 Pro (Deep Reasoning) or Gemini 2.0 Flash (Fast/Cheap).

Usage:
  python tools/ai/analyze.py "Explain the architecture of the archive tool"
  python tools/ai/analyze.py --dir tools/archive "How does file discovery work?"
  python tools/ai/analyze.py --files "README.md,implementation_plan.md" "Summarize status"
"""

import argparse
import sys
import yaml
import fnmatch
import time
import random
from pathlib import Path
from google import genai
from google.genai.types import Part
import subprocess
import json

# --- Config & Setup ---
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "context-management/tools/archive/config.yaml"
SETS_CONFIG_PATH = PROJECT_ROOT / "context-management/config/analysis_sets.yaml"

# Pricing Estimates (USD per 1M tokens) - approximate
PRICING = {
    "gemini-2.0-flash-001": {"input": 0.10, "output": 0.40},
    "gemini-2.5-pro":       {"input": 1.25, "output": 5.00},
    "gemini-1.5-pro-001":   {"input": 1.25, "output": 5.00},
    "gemini-1.5-pro-002":   {"input": 1.25, "output": 5.00}
}
DEFAULT_MODEL = "gemini-2.0-flash-001"  # 1M context, works with current quotas

def load_config():
    if not CONFIG_PATH.exists():
        print("Error: config.yaml not found.")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def load_sets_config():
    if not SETS_CONFIG_PATH.exists():
        # Fallback if config is missing
        return {}
    with open(SETS_CONFIG_PATH) as f:
        return yaml.safe_load(f)

def get_gcloud_project():
    try:
        res = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return None

def get_access_token():
    try:
        res = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return None

def list_gcs_files(bucket, prefix):
    """List all files in the mirror latest directory."""
    try:
        cmd = ["gcloud", "storage", "ls", "-r", f"{bucket}/{prefix}/latest/**"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        files = []
        for line in res.stdout.splitlines():
            if line.endswith(":"): continue 
            if line.strip().endswith("/"): continue
            files.append(line.strip())
        return files
    except Exception as e:
        print(f"Error listing GCS files: {e}")
        return []

def filter_files(all_files, patterns=None, base_uri=""):
    """Filter GCS URIs based on patterns."""
    if not patterns:
        return all_files
    
    # patterns should be matched against relative paths
    filtered = []
    for f in all_files:
        if f.endswith(('.zip', '.png', '.jpg', '.jpeg', '.csv', '.lock', 'package-lock.json')):
            continue
        rel_path = f.replace(base_uri + "/", "")
        for pat in patterns:
            if fnmatch.fnmatch(rel_path, pat):
                filtered.append(f)
                break
    return filtered

def estimate_cost(token_count, model):
    rates = PRICING.get(model, PRICING[DEFAULT_MODEL])
    cost = (token_count / 1_000_000) * rates["input"]
    return cost


def retry_with_backoff(func, max_retries=5, base_delay=1.0):
    """Execute function with exponential backoff on rate limit errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = any(x in error_str for x in ['429', 'rate limit', 'quota', 'resource exhausted'])

            if not is_rate_limit or attempt == max_retries - 1:
                raise  # Re-raise if not a rate limit error or last attempt

            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"  Rate limited. Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
            time.sleep(delay)

    raise Exception("Max retries exceeded")


# --- System Prompts & Modes ---
INSIGHTS_PROMPT = """
You are a SOFTWARE ARCHITECTURE ANALYST specializing in pattern recognition and code quality assessment.

Your task is to analyze Collider output (a semantic graph of a codebase) and provide structured insights.

ANALYSIS CONTEXT (from Collider):
{context}

TASK:
1. Identify design patterns present (Factory, Repository, Observer, Facade, etc.)
2. Detect anti-patterns (God Object, Spaghetti Code, Anemic Domain Model, Feature Envy, etc.)
3. Suggest 3-5 specific refactoring opportunities with priority (CRITICAL/HIGH/MEDIUM/LOW)
4. Interpret the topology shape in architectural terms
5. Assess RPBL scores if present (Responsibility, Purity, Boundary, Lifecycle)
6. Identify risk areas and technical debt
7. Provide a 2-3 sentence executive summary

OUTPUT FORMAT:
Return ONLY valid JSON matching this structure (no markdown, no code blocks):
{{
  "meta": {{
    "generated_at": "<ISO timestamp>",
    "model": "<model name>",
    "target": "<codebase name>",
    "confidence": <0.0-1.0>
  }},
  "executive_summary": "<2-3 sentences>",
  "patterns_detected": [
    {{
      "pattern_name": "<name>",
      "pattern_type": "design_pattern|anti_pattern|architectural",
      "confidence": <0.0-1.0>,
      "affected_nodes": ["<node1>", "<node2>"],
      "evidence": "<why detected>",
      "recommendation": "<what to do>"
    }}
  ],
  "refactoring_opportunities": [
    {{
      "title": "<short name>",
      "priority": "CRITICAL|HIGH|MEDIUM|LOW",
      "category": "<type>",
      "description": "<what and why>",
      "affected_files": ["<file1>"],
      "estimated_impact": "<benefit>"
    }}
  ],
  "topology_analysis": {{
    "shape_interpretation": "<what the shape means>",
    "health_assessment": "<overall health>",
    "coupling_analysis": "<coupling assessment>"
  }},
  "risk_areas": [
    {{
      "area": "<name>",
      "risk_level": "HIGH|MEDIUM|LOW",
      "description": "<issue>",
      "mitigation": "<fix>"
    }}
  ]
}}

Be specific. Cite actual node names from the input. Do not hallucinate nodes that don't exist.
"""

MODES = {
    "standard": {
        "prompt": "You are a senior software engineer. Analyze the provided codebase context and answer the user's request.",
        "output_format": "text"
    },
    "forensic": {
        "prompt": """
You are a FORENSIC CODE ANALYST. Your goal is to provide precise, verifiable facts about the codebase.
RULES:
1. For every claim you make, you MUST cite the specific file path and line numbers.
2. Format citations as: `[path/to/file.py:L10-L15]`
3. Do not generalize. If you cannot find the specific implementation, state "Evidence not found in provided context."
4. Quote the exact code snippet when relevant.
""",
        "output_format": "text"
    },
    "architect": {
        "prompt": """
You are the CHIEF ARCHITECT of the 'Standard Model of Code' project.
Your analysis must be grounded in the project's theoretical framework (Atoms, Rings, Tiers, RPBL).
RULES:
1. Use the terminology defined in `metadata/COLLIDER_ARCHITECTURE.md` (e.g., "The UnifiedNode layer...", "The RPBL classification...").
2. Connect implementation details to the architectural vision.
3. Identify topological structures (knots, cycles, layers).
""",
        "output_format": "text"
    },
    "insights": {
        "prompt": INSIGHTS_PROMPT,
        "output_format": "json"
    }
}

def extract_collider_context(json_path):
    """Extract key metrics from Collider unified_analysis.json for insights prompt."""
    with open(json_path) as f:
        data = json.load(f)

    # Extract key sections
    context_parts = []

    # Target name (multiple possible locations)
    target = data.get('target_name') or data.get('meta', {}).get('target') or 'Unknown'
    context_parts.append(f"Target: {target}")

    # Counts (handle both structures)
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    counts = data.get('counts', {})

    node_count = counts.get('total_nodes') or len(nodes)
    edge_count = counts.get('total_edges') or len(edges)
    file_count = counts.get('files') or len(set(n.get('file_path', '') for n in nodes))

    context_parts.append(f"Nodes: {node_count}")
    context_parts.append(f"Edges: {edge_count}")
    context_parts.append(f"Files: {file_count}")

    # Architecture
    arch = data.get('architecture', {})
    if arch:
        # Handle nested graph_inference structure
        graph_inf = arch.get('graph_inference', {})
        topology = graph_inf.get('topology_shape') or arch.get('topology_shape', 'Unknown')
        context_parts.append(f"Topology Shape: {topology}")

        density = graph_inf.get('density') or arch.get('density')
        if density:
            context_parts.append(f"Graph Density: {density}")

        # Detected patterns
        patterns = arch.get('detected_patterns', [])
        if patterns:
            context_parts.append(f"Detected Patterns: {', '.join(patterns[:5])}")

        # Layer violations
        violations = arch.get('layer_violations', [])
        if violations:
            context_parts.append(f"Layer Violations: {len(violations)}")

    # RPBL (check multiple locations)
    rpbl = data.get('rpbl_profile', {}) or data.get('rpbl', {})
    if rpbl and any(rpbl.get(k) for k in ['R', 'P', 'B', 'L']):
        context_parts.append(f"RPBL Profile: R={rpbl.get('R', 0):.2f}, P={rpbl.get('P', 0):.2f}, B={rpbl.get('B', 0):.2f}, L={rpbl.get('L', 0):.2f}")

    # Top hubs (check multiple locations)
    hubs = data.get('top_hubs', []) or data.get('stats', {}).get('top_hubs', [])
    if hubs:
        hub_names = [h.get('name', h.get('id', 'Unknown')) for h in hubs[:10]]
        context_parts.append(f"Top Hubs: {', '.join(hub_names)}")

    # Orphans (dead code)
    orphans = data.get('orphans_list', []) or data.get('orphans', [])
    if orphans:
        context_parts.append(f"Dead Code (Orphans): {len(orphans)} nodes")

    # Dependencies / antimatter
    antimatter = data.get('antimatter', {})
    if antimatter:
        violations = antimatter.get('violations', [])
        if violations:
            context_parts.append(f"Antimatter Violations: {len(violations)}")

    # Classification stats
    classification = data.get('classification', {})
    if classification:
        role_dist = classification.get('role_distribution', {})
        if role_dist:
            top_roles = sorted(role_dist.items(), key=lambda x: x[1], reverse=True)[:5]
            role_summary = ', '.join([f"{r}: {c}" for r, c in top_roles])
            context_parts.append(f"Role Distribution: {role_summary}")

    # Sample nodes (for context)
    sample_nodes = nodes[:30] if nodes else []
    if sample_nodes:
        node_summary = []
        for n in sample_nodes:
            name = n.get('name', n.get('id', 'Unknown'))
            role = n.get('role', 'Unknown')
            kind = n.get('kind', '')
            node_summary.append(f"{name} ({role}/{kind})")
        context_parts.append(f"Sample Nodes: {', '.join(node_summary)}")

    return '\n'.join(context_parts)


def main():
    parser = argparse.ArgumentParser(description="Analyze codebase with Vertex AI")
    parser.add_argument("prompt", nargs='?', default="Analyze this codebase", help="The question or instruction for the AI")
    parser.add_argument("--dir", help="Filter by directory (e.g., 'tools/archive')")
    parser.add_argument("--file", help="Specific file(s) to include (comma separated)")
    parser.add_argument("--set", help="Analysis Set (brain, body, theory, legacy)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model to use")
    parser.add_argument("--mode", default="standard", choices=MODES.keys(), help="Analysis mode: standard, forensic, architect, or insights")
    parser.add_argument("--collider-json", help="Path to Collider unified_analysis.json (for insights mode)")
    parser.add_argument("--output", "-o", help="Output file path (for insights mode, saves JSON)")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip cost confirmation")
    args = parser.parse_args()

    # 1. Config & Auth
    config = load_config()
    bucket_url = config.get("mirror", {}).get("bucket")
    prefix = config.get("mirror", {}).get("prefix", "repository_mirror")
    mirror_base = f"{bucket_url}/{prefix}/latest"
    
    project_id = get_gcloud_project()
    if not project_id:
        print("Error: No gcloud project set.")
        sys.exit(1)

    print(f"Project: {project_id}")
    print(f"Model:   {args.model}")
    print(f"Mode:    {args.mode.upper()}")
    print("Fetching file list from Mirror...")

    # 2. File Selection
    all_files = list_gcs_files(bucket_url, prefix)
    selected_files = []
    
    if args.file:
        targets = args.file.split(",")
        selected_files = filter_files(all_files, targets, mirror_base)
    elif args.dir:
        selected_files = filter_files(all_files, [f"{args.dir}*"], mirror_base)
    elif args.set:
        sets_config = load_sets_config()
        analysis_sets = sets_config.get("analysis_sets", {})
        if args.set not in analysis_sets:
            print(f"Error: Unknown set '{args.set}'. Available: {list(analysis_sets.keys())}")
            sys.exit(1)
        
        print(f"Using Analysis Set: {args.set.upper()}")
        print(f"  {analysis_sets[args.set]['description']}")
        selected_files = filter_files(all_files, analysis_sets[args.set]['patterns'], mirror_base)
    else:
        # Default: Important docs and root files if no filter
        # In 'architect' mode, we MUST include the architecture docs
        defaults = ["README.md", "implementation_plan.md", "docs/*.md", "tools/*.py"]
        selected_files = filter_files(all_files, defaults, mirror_base)

    if args.mode == "architect":
        # Ensure architecture definitions are included
        arch_docs = filter_files(all_files, ["*COLLIDER_ARCHITECTURE.md", "*THEORY.md"], mirror_base)
        for d in arch_docs:
            if d not in selected_files:
                selected_files.insert(0, d) # High priority

    if not selected_files:
        print("No files matched your criteria.")
        sys.exit(1)

    print(f"\nSelected {len(selected_files)} files for context:")
    for f in selected_files[:5]:
        print(f" - {f.replace(mirror_base, '')}")
    if len(selected_files) > 5:
        print(f" ... and {len(selected_files)-5} more")

    # 3. Cost Estimation
    print(f"\nSending files from: {mirror_base}")
    if not args.yes:
        confirm = input("\nProceed with analysis? [Y/n] ")
        if confirm.lower() == 'n':
            sys.exit(0)

    # 4. Execution
    access_token = get_access_token()
    if not access_token:
        print("Error: Could not get access token.")
        print("Run: gcloud auth application-default login")
        sys.exit(1)

    from google.oauth2 import credentials as oauth2_credentials
    creds = oauth2_credentials.Credentials(token=access_token)
    
    client = genai.Client(
        vertexai=True, project=project_id, location="us-central1", credentials=creds
    )

    contents = [Part.from_uri(file_uri=f, mime_type="text/plain") for f in selected_files]

    # Handle insights mode specially
    if args.mode == "insights":
        if not args.collider_json:
            print("Error: --collider-json is required for insights mode")
            print("Usage: python analyze.py --mode insights --collider-json /path/to/unified_analysis.json")
            sys.exit(1)

        # Extract context from Collider output
        print(f"\nExtracting context from: {args.collider_json}")
        try:
            collider_context = extract_collider_context(args.collider_json)
            print(f"Context extracted ({len(collider_context)} chars)")
        except Exception as e:
            print(f"Error reading Collider JSON: {e}")
            sys.exit(1)

        # Build prompt with context injected
        full_prompt = MODES['insights']['prompt'].format(context=collider_context)
    else:
        # Standard prompt building
        full_prompt = f"{MODES[args.mode]['prompt']}\n\nUSER QUERY: {args.prompt}"

    contents.append(Part.from_text(text=full_prompt))

    print("\n--- Analyzing ---")
    try:
        # Wrap API call with retry logic for rate limits
        def make_request():
            return client.models.generate_content(
                model=args.model,
                contents=contents
            )

        response = retry_with_backoff(make_request)

        # Handle output based on mode
        output_format = MODES[args.mode].get('output_format', 'text')

        if output_format == 'json':
            # Parse and validate JSON for insights mode
            raw_text = response.text.strip()
            # Remove markdown code blocks if present
            if raw_text.startswith('```'):
                lines = raw_text.split('\n')
                raw_text = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])

            try:
                insights_data = json.loads(raw_text)
                print(json.dumps(insights_data, indent=2))

                # Save to file if --output specified
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(insights_data, f, indent=2)
                    print(f"\n✅ Insights saved to: {args.output}")
                else:
                    # Default output path
                    default_output = Path(args.collider_json).parent / "ai_insights.json"
                    with open(default_output, 'w') as f:
                        json.dump(insights_data, f, indent=2)
                    print(f"\n✅ Insights saved to: {default_output}")

            except json.JSONDecodeError as e:
                print(f"⚠️ Warning: Response is not valid JSON: {e}")
                print("Raw response:")
                print(raw_text)
        else:
            # Text output
            print(response.text)

        print("\n-----------------")
        if response.usage_metadata:
            print(f"Tokens Used: {response.usage_metadata.prompt_token_count} Input, {response.usage_metadata.candidates_token_count} Output")
            est = estimate_cost(response.usage_metadata.prompt_token_count, args.model)
            print(f"Estimated Cost: ${est:.4f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
