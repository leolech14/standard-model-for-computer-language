#!/usr/bin/env python3
"""
Local Codebase Analysis Tool v3
=================================
A headless AI tool that reads files directly from the local filesystem,
with proper secret exclusions, line-numbered output, and chat session reuse.

v3 Features:
- ACI (Adaptive Context Intelligence): Auto-select tier and context for any query
- Token budget awareness (warns if exceeding 1M limit)
- Set composition via 'includes' in analysis_sets.yaml
- Auto-interactive mode for large contexts
- Smart query-to-set recommendations
- FILE SEARCH (RAG): Index files once, query many times with citations
- .agent/ context sets: agent_kernel, agent_tasks, agent_intelligence, agent_specs, agent_full

Usage:
  # ACI MODE (Recommended) - Auto-selects tier and context
  python analyze.py --aci "how does atom classification work"
  python analyze.py --aci "what tasks are ready to execute"
  python analyze.py --aci "how many Python files in the repo"

  # Force specific tier with ACI
  python analyze.py --aci --tier perplexity "latest Python type hint best practices 2026"
  python analyze.py --aci --tier long_context "explain the pipeline architecture"

  # Debug ACI routing decision
  python analyze.py --aci --aci-debug "how does edge extraction work"

  # One-shot mode (Tier 2: Long Context)
  python analyze.py "Explain the architecture"

  # Interactive mode With Caching (Automatic for large contexts)
  python analyze.py --interactive --set pipeline

  # FILE SEARCH MODE (Tier 1: RAG with Citations)
  # Index files to a store
  python analyze.py --index --set pipeline --store-name collider-pipeline

  # Query with File Search (citations included)
  python analyze.py --search "How does edge extraction work?" --store-name collider-pipeline

  # List existing stores
  python analyze.py --list-stores

  # Delete a store
  python analyze.py --delete-store collider-pipeline

  # Insights Report (Source Code Analysis)
  python analyze.py --mode insights --file "src/main.py" --output report.json

  # List available sets
  python analyze.py --list-sets

  # Get set recommendations for a query
  python analyze.py --recommend "how does classification work"

ACI Tiers:
  - INSTANT (Tier 0): Cached truths for counts/stats (<100ms)
  - RAG (Tier 1): File Search for targeted lookups (~5s)
  - LONG_CONTEXT (Tier 2): Full context Gemini reasoning (~60s)
  - PERPLEXITY (Tier 3): External web research (~30s)

IMPORTANT: This script requires the .tools_venv virtual environment.
"""

import sys
import os
from pathlib import Path

# --- Auto-detect and use correct venv ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
TOOLS_VENV = PROJECT_ROOT / ".tools_venv"
VENV_PYTHON = TOOLS_VENV / "bin" / "python"


def _in_correct_venv():
    """Check if we're running from .tools_venv"""
    return TOOLS_VENV.as_posix() in sys.prefix


if not _in_correct_venv():
    if VENV_PYTHON.exists():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)
    else:
        print("=" * 60)
        print("ERROR: Required virtual environment not found!")
        print("=" * 60)
        print(f"Expected: {TOOLS_VENV}")
        print()
        print("To fix, run from PROJECT_elements root:")
        print("  python -m venv .tools_venv")
        print("  source .tools_venv/bin/activate")
        print("  pip install google-genai pyyaml")
        print("=" * 60)
        sys.exit(1)

# --- Now safe to import deps (we're in correct venv) ---
import argparse
import yaml
import fnmatch
import time
import random
import subprocess
import json
from google import genai
from google.genai.types import Part, Content

# Import DualFormatSaver for auto-save functionality
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.output_formatters import DualFormatSaver
    HAS_DUAL_FORMAT_SAVER = True
except ImportError:
    HAS_DUAL_FORMAT_SAVER = False

# Import ACI (Adaptive Context Intelligence) module
try:
    from aci import (
        analyze_and_route,
        tier_from_string,
        format_routing_decision,
        load_repo_truths,
        answer_from_truths,
        optimize_context,
        format_context_summary,
        Tier,
    )
    from aci.feedback_loop import log_aci_query, get_feedback_loop
    HAS_ACI = True
except ImportError:
    HAS_ACI = False

# --- Config & Setup ---
SETS_CONFIG_PATH = PROJECT_ROOT / "context-management/config/analysis_sets.yaml"
PROMPTS_CONFIG_PATH = PROJECT_ROOT / "context-management/config/prompts.yaml"
SEMANTIC_MODELS_PATH = PROJECT_ROOT / "context-management/config/semantic_models.yaml"

# --- Environment Detection ---
# Detect if running in an interactive terminal or a headless agent/CI environment
IS_INTERACTIVE_ENV = sys.stdin.isatty() and not (
    os.environ.get('ANTIGRAVITY_AGENT') == '1' or 
    os.environ.get('CI') == 'true' or
    os.environ.get('NONINTERACTIVE') == 'true'
)

# Architecture docs to auto-inject for architect mode

# Architecture docs to auto-inject for architect mode
# Point to canonical MODEL.md
ARCHITECT_DOCS = [
    "context-management/docs/COLLIDER_ARCHITECTURE.md",
    "standard-model-of-code/docs/MODEL.md",
]

# Load prompts and modes
if PROMPTS_CONFIG_PATH.exists():
    with open(PROMPTS_CONFIG_PATH) as f:
        _prompts_data = yaml.safe_load(f)
        PRICING = _prompts_data.get("pricing", {})
        DEFAULT_MODEL = _prompts_data.get("default_model", "gemini-2.5-pro")
        MODES = _prompts_data.get("analysis_prompts", {}).get("modes", {})
        # Prefer "insights_source" for raw file analysis
        INSIGHTS_PROMPT = _prompts_data.get("analysis_prompts", {}).get("insights_source") or _prompts_data.get("analysis_prompts", {}).get("insights")
        # Role validation prompt
        ROLE_VALIDATION_PROMPT = _prompts_data.get("analysis_prompts", {}).get("role_validation")
        # Plan validation prompt
        PLAN_VALIDATION_PROMPT = _prompts_data.get("analysis_prompts", {}).get("plan_validation")
else:
    PRICING = {}
    DEFAULT_MODEL = "gemini-2.5-pro"
    MODES = {}
    INSIGHTS_PROMPT = None
    ROLE_VALIDATION_PROMPT = None
    PLAN_VALIDATION_PROMPT = None


def load_sets_config():
    if not SETS_CONFIG_PATH.exists():
        return {}
    with open(SETS_CONFIG_PATH) as f:
        return yaml.safe_load(f)


# Token limits
MAX_CONTEXT_TOKENS = 1_000_000  # Gemini 2.0 Flash limit
INTERACTIVE_THRESHOLD = 50_000  # Auto-interactive above this

# File Search configuration
# NOTE: File Search requires the Gemini Developer API (ai.google.dev), not Vertex AI
# Set GEMINI_API_KEY environment variable to use File Search features
FILE_SEARCH_MODEL = "gemini-2.5-pro"  # File Search requires 2.5+ models
FILE_SEARCH_CHUNK_SIZE = 512  # Tokens per chunk
FILE_SEARCH_CHUNK_OVERLAP = 50  # Overlap tokens between chunks
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"  # Environment variable for Developer API key

# Auto-save configuration for Gemini responses
GEMINI_RESEARCH_PATH = PROJECT_ROOT / "standard-model-of-code/docs/research/gemini"
AUTO_SAVE_ENABLED = True  # Set to False to disable auto-save

# Initialize DualFormatSaver for Gemini responses
_gemini_saver = None
if HAS_DUAL_FORMAT_SAVER and AUTO_SAVE_ENABLED:
    _gemini_saver = DualFormatSaver(base_path=GEMINI_RESEARCH_PATH)


def auto_save_gemini_response(query: str, response_text: str, model: str, mode: str = "standard") -> str:
    """
    Auto-save Gemini response using DualFormatSaver.

    Args:
        query: Original query text
        response_text: Response text from Gemini
        model: Model used (e.g., "gemini-2.5-pro")
        mode: Analysis mode (e.g., "standard", "insights", "forensic")

    Returns:
        Path to saved markdown file, or empty string if save failed/disabled
    """
    if not _gemini_saver:
        return ""

    try:
        # Build response dict compatible with DualFormatSaver
        response_dict = {
            "content": response_text,
            "mode": mode,
        }

        result = _gemini_saver.save(
            query=query,
            response=response_dict,
            source="gemini",
            model=model
        )

        print(f"  [Auto-saved: {result.md_path.name}]", file=sys.stderr)
        return str(result.md_path)
    except Exception as e:
        print(f"  [Auto-save failed: {e}]", file=sys.stderr)
        return ""


def resolve_set(set_name: str, analysis_sets: dict, resolved: set = None) -> dict:
    """
    Resolve a set definition, expanding any 'includes' recursively.

    Returns a dict with:
      - patterns: list of glob patterns
      - max_tokens: token budget
      - auto_interactive: whether to auto-enable interactive mode
      - description: human-readable description
      - critical_files: list of files to position strategically
      - positional_strategy: 'sandwich' or 'front-load'
    """
    if resolved is None:
        resolved = set()

    if set_name in resolved:
        # Circular dependency protection
        return {'patterns': [], 'max_tokens': 0, 'auto_interactive': False, 'description': '',
                'critical_files': [], 'positional_strategy': None}

    resolved.add(set_name)

    if set_name not in analysis_sets:
        return {'patterns': [], 'max_tokens': 0, 'auto_interactive': False, 'description': f'Unknown set: {set_name}',
                'critical_files': [], 'positional_strategy': None}

    set_def = analysis_sets[set_name]
    patterns = list(set_def.get('patterns', []))
    max_tokens = set_def.get('max_tokens', 100_000)
    auto_interactive = set_def.get('auto_interactive', False)
    description = set_def.get('description', '')
    critical_files = list(set_def.get('critical_files', []))
    positional_strategy = set_def.get('positional_strategy', None)

    # Resolve includes
    for included_set in set_def.get('includes', []):
        included = resolve_set(included_set, analysis_sets, resolved)
        patterns.extend(included['patterns'])
        max_tokens = max(max_tokens, included['max_tokens'])
        auto_interactive = auto_interactive or included['auto_interactive']
        # Merge critical_files from included sets (parent set takes precedence)
        for cf in included.get('critical_files', []):
            if cf not in critical_files:
                critical_files.append(cf)
        # Parent strategy takes precedence over included
        if not positional_strategy and included.get('positional_strategy'):
            positional_strategy = included['positional_strategy']

    # Remove duplicates while preserving order
    seen = set()
    unique_patterns = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            unique_patterns.append(p)

    return {
        'patterns': unique_patterns,
        'max_tokens': max_tokens,
        'auto_interactive': auto_interactive,
        'description': description,
        'critical_files': critical_files,
        'positional_strategy': positional_strategy
    }


def recommend_sets(query: str, recommendations: dict) -> list:
    """
    Match a query against recommendation patterns and return suggested sets.

    Uses glob-style matching where * matches any words.
    """
    query_lower = query.lower()
    matches = []

    for pattern, sets in recommendations.items():
        # Convert "how does * work" to regex-like matching
        pattern_lower = pattern.lower()
        # Split pattern into parts around *
        parts = pattern_lower.split('*')

        # Check if query matches pattern
        pos = 0
        matched = True
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            idx = query_lower.find(part, pos)
            if idx == -1:
                matched = False
                break
            pos = idx + len(part)

        if matched:
            for s in sets:
                if s not in matches:
                    matches.append(s)

    return matches



def list_available_workflows() -> list:
    """Scan .agent/workflows for available workflow definitions."""
    workflows_dir = PROJECT_ROOT / ".agent/workflows"
    if not workflows_dir.exists():
        return []
    
    workflows = []
    for f in workflows_dir.glob("*.md"):
        # Parse frontmatter for description
        desc = "No description"
        try:
            with open(f, 'r') as file:
                content = file.read()
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        import yaml
                        frontmatter = yaml.safe_load(parts[1])
                        desc = frontmatter.get('description', desc)
        except Exception:
            pass
        
        workflows.append({
            'name': f.stem,
            'description': desc,
            'path': str(f.relative_to(PROJECT_ROOT))
        })
    return sorted(workflows, key=lambda x: x['name'])


def get_hsl_status() -> dict:
    """Check status of the Holographic Socratic Layer (HSL)."""
    if SEMANTIC_MODELS_PATH.exists():
        try:
            with open(SEMANTIC_MODELS_PATH) as f:
                config = yaml.safe_load(f)
                count = len(config.get('antimatter', []))
                return {'status': 'ACTIVE', 'laws': count, 'path': str(SEMANTIC_MODELS_PATH.relative_to(PROJECT_ROOT))}
        except:
            return {'status': 'ERROR', 'laws': 0, 'path': str(SEMANTIC_MODELS_PATH.relative_to(PROJECT_ROOT))}
    return {'status': 'INACTIVE', 'laws': 0, 'path': 'N/A'}


def print_briefing(analysis_sets: dict) -> None:
    """Print a System Briefing for Agent Orientation."""
    print("\n" + "=" * 80)
    print("SYSTEM BRIEFING: AGENT ORIENTATION")
    print("=" * 80)
    
    # 1. HSL Status (The Third Mirror)
    hsl = get_hsl_status()
    print(f"\n[1] HOLOGRAPHIC SOCRATIC LAYER (HSL)")
    print(f"    Status: {hsl['status']}")
    print(f"    Laws:   {hsl['laws']} Antimatter Laws loaded")
    print(f"    Config: {hsl['path']}")
    print(f"    Usage:  Use --verify <domain> to query the semantic mirror.")

    # 2. Workflows (Standard Operating Procedures)
    workflows = list_available_workflows()
    print(f"\n[2] AVAILABLE WORKFLOWS (Standard Operating Procedures)")
    if workflows:
        for w in workflows:
            print(f"    - {w['name']:<20} : {w['description']}")
            print(f"      (Path: {w['path']})")
    else:
        print("    (No workflows found in .agent/workflows)")

    # 3. Data Sets (Context Windows)
    print(f"\n[3] ANALYSIS DATA SETS (Context Windows)")
    # Reuse list logic but condensed
    core_sets = []
    task_sets = []
    for name, config in analysis_sets.items():
        desc = config.get('description', '')
        max_tokens = config.get('max_tokens', 0)
        tokens_str = f"{max_tokens/1000:.0f}k" if max_tokens < 1000000 else f"{max_tokens/1000000:.1f}M"
        if max_tokens <= 100_000 and not config.get('includes'):
            core_sets.append(f"{name} ({tokens_str})")
        else:
            task_sets.append(f"{name} ({tokens_str})")
            
    print(f"    Core: {', '.join(core_sets[:5])}...")
    print(f"    Task: {', '.join(task_sets[:5])}...")
    print(f"    (Use --list-sets for full details)")

    print("\n" + "=" * 80 + "\n")


def list_available_sets(analysis_sets: dict) -> None:
    """Print a formatted list of available analysis sets."""
    print("\n" + "=" * 70)
    print("AVAILABLE ANALYSIS SETS")
    print("=" * 70)

    # Group by category based on description markers
    core_sets = []
    composed_sets = []
    task_sets = []
    legacy_sets = []

    for name, config in analysis_sets.items():
        desc = config.get('description', '')
        max_tokens = config.get('max_tokens', 0)
        has_includes = bool(config.get('includes'))
        auto_int = config.get('auto_interactive', False)

        entry = {
            'name': name,
            'description': desc,
            'max_tokens': max_tokens,
            'auto_interactive': auto_int,
            'has_includes': has_includes
        }

        if '[LARGE]' in desc or '[EXCEEDS LIMIT]' in desc or '[DANGEROUS]' in desc:
            legacy_sets.append(entry)
        elif has_includes:
            composed_sets.append(entry)
        elif max_tokens <= 100_000:
            core_sets.append(entry)
        else:
            task_sets.append(entry)

    def print_section(title: str, sets: list):
        if not sets:
            return
        print(f"\n{title}:")
        print("-" * 50)
        for s in sets:
            tokens_str = f"{s['max_tokens']:,}" if s['max_tokens'] < 1_000_000 else f"{s['max_tokens']/1_000_000:.1f}M"
            flags = []
            if s['auto_interactive']:
                flags.append('auto-interactive')
            if s['has_includes']:
                flags.append('composed')
            if s['max_tokens'] > MAX_CONTEXT_TOKENS:
                flags.append('EXCEEDS LIMIT')
            flags_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"  {s['name']:20} {tokens_str:>10} tokens  {s['description']}{flags_str}")

    print_section("CORE SETS (Well-sized, commonly used)", core_sets)
    print_section("COMPOSED SETS (Combinations)", composed_sets)
    print_section("TASK-SPECIFIC SETS", task_sets)
    print_section("LEGACY SETS (Use with caution)", legacy_sets)

    print("\n" + "=" * 70)
    print("Usage: python local_analyze.py --set <name> \"Your question\"")
    print("       python local_analyze.py --recommend \"your question\" (get suggestions)")
    print("=" * 70 + "\n")


# =============================================================================
# FILE SEARCH (RAG) FUNCTIONS
# =============================================================================

def list_file_search_stores(client) -> list:
    """List all File Search stores."""
    try:
        stores = list(client.file_search_stores.list())
        return stores
    except Exception as e:
        print(f"Error listing stores: {e}")
        return []


def get_or_create_store(client, store_name: str) -> str:
    """Get existing store by name or create new one. Returns store resource name."""
    # List existing stores
    stores = list_file_search_stores(client)
    
    matches = [s for s in stores if s.display_name == store_name]

    if len(matches) > 1:
        print(f"  WARNING: Multiple stores found with name '{store_name}'. Using the most recent.")
        # Sort by create_time desc if possible, or just take first. 
        # API returns generic objects, assuming standard list order for now.
        return matches[0].name
    
    if len(matches) == 1:
        print(f"  Found existing store: {matches[0].name}")
        return matches[0].name

    # Create new store
    print(f"  Creating new store: {store_name}")
    store = client.file_search_stores.create(
        config={'display_name': store_name}
    )
    print(f"  Created: {store.name}")
    return store.name


def index_files_to_store(client, store_name: str, files: list, base_dir: Path) -> dict:
    """
    Upload and index files to a File Search store.

    Returns dict with stats: {indexed: int, failed: int, errors: list}
    """
    stats = {'indexed': 0, 'failed': 0, 'errors': [], 'files': [], 'skipped': 0}

    for file_path in files:
        rel_path = str(file_path.relative_to(base_dir))
        
        # Check for unsupported file types (YAML often fails in current API)
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            print(f"  Skipping: {rel_path} (YAML files not fully supported)", flush=True)
            stats['skipped'] += 1
            continue

        try:
            print(f"  Indexing: {rel_path}...", end=" ", flush=True)

            # Upload and index the file
            result = client.file_search_stores.upload_to_file_search_store(
                file=str(file_path),
                file_search_store_name=store_name,
                config={
                    'display_name': rel_path,
                }
            )

            # SDK Compatibility: failure to wait for operation can cause missing docs
            # If result is an Operation (has .result method), we should wait.
            if hasattr(result, 'result'):
                result.result() 

            stats['indexed'] += 1
            stats['files'].append(rel_path)
            print("OK")

        except Exception as e:
            stats['failed'] += 1
            stats['errors'].append(f"{rel_path}: {e}")
            print(f"FAILED: {e}")

    return stats


def search_with_file_search(client, store_name: str, query: str, model: str = None) -> dict:
    """
    Query using File Search and return response with citations.

    Returns dict with:
      - text: the response text
      - citations: list of {file, content} dicts
      - usage: token usage info
    """
    from google.genai import types

    model = model or FILE_SEARCH_MODEL

    response = client.models.generate_content(
        model=model,
        contents=query,
        config=types.GenerateContentConfig(
            tools=[types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store_name]
                )
            )]
        )
    )

    result = {
        'text': response.text,
        'citations': [],
        'usage': None
    }

    # Extract citations from grounding metadata
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
            gm = candidate.grounding_metadata
            # Extract grounding chunks (the actual citations)
            if hasattr(gm, 'grounding_chunks') and gm.grounding_chunks:
                for chunk in gm.grounding_chunks:
                    citation = {}
                    if hasattr(chunk, 'retrieved_context'):
                        ctx = chunk.retrieved_context
                        if hasattr(ctx, 'uri'):
                            citation['file'] = ctx.uri
                        if hasattr(ctx, 'title'):
                            citation['title'] = ctx.title
                    if hasattr(chunk, 'web') and chunk.web:
                        citation['web'] = chunk.web.uri if hasattr(chunk.web, 'uri') else str(chunk.web)
                    result['citations'].append(citation)

    # Get usage
    if response.usage_metadata:
        result['usage'] = {
            'input_tokens': response.usage_metadata.prompt_token_count,
            'output_tokens': response.usage_metadata.candidates_token_count
        }

    return result


def delete_file_search_store(client, store_name: str) -> bool:
    """Delete a File Search store by display name or resource name."""
    try:
        # If it looks like a resource name, delete directly
        if store_name.startswith('fileSearchStores/'):
            try:
                client.file_search_stores.delete(name=store_name)
                print(f"  Deleted: {store_name}")
                return True
            except Exception as e:
                if "400" in str(e) and "non-empty" in str(e).lower():
                    print(f"  Error: Store {store_name} is not empty.")
                    # TODO: Implement file deletion if API supports listing files in store nicely
                    print(f"  Please delete files from the store before deleting the store.")
                else:
                    print(f"  Error deleting store: {e}")
                return False

        # Otherwise, find by display name
        stores = list_file_search_stores(client)
        matches = [s for s in stores if s.display_name == store_name]
        
        if not matches:
             print(f"  Store not found: {store_name}")
             return False
        
        if len(matches) > 1:
             print(f"  WARNING: {len(matches)} stores found with name '{store_name}'.")
             print("  Please use the resource name (fileSearchStores/...) to be specific.")
             print("  Use --list-stores to see resource names.")
             return False

        target_store = matches[0]
        try:
            client.file_search_stores.delete(name=target_store.name)
            print(f"  Deleted: {target_store.name} ({target_store.display_name})")
            return True
        except Exception as e:
            if "400" in str(e) and "non-empty" in str(e).lower():
                print(f"  Error: Store '{store_name}' is not empty.")
                print(f"  The API requires stores to be empty before deletion.")
            else:
                print(f"  Error deleting store: {e}")
            return False

    except Exception as e:
        print(f"  Error finding store: {e}")
        return False


def print_stores_list(stores: list) -> None:
    """Print formatted list of File Search stores."""
    if not stores:
        print("\nNo File Search stores found.")
        return

    print("\n" + "=" * 70)
    print("FILE SEARCH STORES")
    print("=" * 70)

    for store in stores:
        name = store.name if hasattr(store, 'name') else 'unknown'
        display_name = store.display_name if hasattr(store, 'display_name') else 'unnamed'
        create_time = store.create_time if hasattr(store, 'create_time') else 'unknown'

        print(f"\n  Name: {display_name}")
        print(f"  Resource: {name}")
        print(f"  Created: {create_time}")

    print("\n" + "=" * 70)
    print("Commands:")
    print("  --search \"query\" --store-name <name>  Query a store")
    print("  --delete-store <name>                  Delete a store")
    print("=" * 70 + "\n")


def get_doppler_secret(key: str) -> str | None:
    """Fetch a secret from Doppler. Returns None if unavailable."""
    try:
        result = subprocess.run(
            ["doppler", "secrets", "get", key, "--plain"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def create_developer_client():
    """
    Create a Gemini Developer API client for File Search.

    Uses Doppler as the primary secrets source.
    Falls back to GEMINI_API_KEY env var if Doppler unavailable.
    """
    # Primary: Doppler (project: ai-tools, config: dev)
    api_key = get_doppler_secret("GEMINI_API_KEY")
    if api_key:
        print("  [Doppler] GEMINI_API_KEY loaded")
    else:
        # Fallback: environment variable
        api_key = os.environ.get(GEMINI_API_KEY_ENV)
        if api_key:
            print("  [Env] GEMINI_API_KEY loaded from environment")

    if not api_key:
        print(f"\n{'='*60}")
        print("FILE SEARCH REQUIRES GEMINI_API_KEY")
        print(f"{'='*60}")
        print()
        print("Setup Doppler (recommended):")
        print("   doppler setup --project ai-tools --config dev")
        print()
        print("Or set environment variable:")
        print(f"   export {GEMINI_API_KEY_ENV}='your-api-key'")
        print()
        print("Get API key from: https://aistudio.google.com/apikey")
        print(f"{'='*60}\n")
        return None

    client = genai.Client(api_key=api_key)
    return client


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


def list_local_files(base_dir, patterns=None, user_excludes=None):
    """List files from local filesystem matching patterns.
    
    Includes security-sensitive exclusions by default to prevent secret leakage.
    """
    base_path = Path(base_dir)
    all_files = []
    
    # SECURITY: Default excludes - prevents secret leakage
    default_excludes = [
        # Secrets and credentials
        ".env", ".env.*", "*.env", ".envrc",
        "*.key", "*.pem", "*.p12", "*.pfx", "*.crt",
        "credentials*", "secrets*", "*secret*",
        ".gcloud", ".aws", ".ssh",
        "service-account*.json", "*-credentials.json",
        
        # Build artifacts and caches
        "*.DS_Store", "__pycache__", "*.pyc", "*.pyo",
        ".git", "node_modules", ".npm", ".yarn",
        "*.zip", "*.tar", "*.gz", "*.rar",
        "*.lock", "package-lock.json", "yarn.lock",
        ".tools_venv", ".venv", "venv", "*.egg-info",
        
        # Binary files
        "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.webp",
        "*.mp3", "*.mp4", "*.wav", "*.avi",
        "*.pdf", "*.doc", "*.docx", "*.xls", "*.xlsx",
        "*.so", "*.dylib", "*.dll", "*.exe",
        
        # IDE and editor
        ".idea", ".vscode", "*.swp", "*.swo",
    ]
    excludes = default_excludes + (user_excludes or [])
    
    def should_exclude(path):
        name = path.name
        try:
            rel_path = str(path.relative_to(base_path))
        except ValueError:
            rel_path = str(path)
        
        for pattern in excludes:
            # Match against filename
            if fnmatch.fnmatch(name, pattern):
                return True
            # Match against relative path
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            # Match against path components
            if pattern in rel_path.split(os.sep):
                return True
        return False
    
    # Walk the directory (sorted for deterministic output)
    for root, dirs, files in os.walk(base_path):
        # Filter out excluded directories (modifies in-place)
        dirs[:] = sorted([d for d in dirs if not should_exclude(Path(root) / d)])
        
        for file in sorted(files):
            file_path = Path(root) / file
            if should_exclude(file_path):
                continue
            all_files.append(file_path)
    
    # Filter by patterns if provided
    if patterns:
        filtered = []
        for f in all_files:
            rel_path = str(f.relative_to(base_path))
            for pat in patterns:
                if fnmatch.fnmatch(rel_path, pat):
                    filtered.append(f)
                    break
        return filtered
    
    return all_files


def read_file_content(file_path, with_line_numbers=False):
    """Read file content, optionally with line numbers for forensic/interactive modes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception:
            return f"[Binary or unreadable file: {file_path}]"
    except Exception as e:
        return f"[Error reading {file_path}: {e}]"
    
    if with_line_numbers:
        lines = content.split('\n')
        numbered_lines = [f"{i+1:4d}: {line}" for i, line in enumerate(lines)]
        return '\n'.join(numbered_lines)
    
    return content


def estimate_cost(input_tokens, output_tokens, model):
    """Estimate cost including both input and output tokens."""
    rates = PRICING.get(model, PRICING.get(DEFAULT_MODEL, {"input": 0.10, "output": 0.40}))
    input_cost = (input_tokens / 1_000_000) * rates.get("input", 0.10)
    output_cost = (output_tokens / 1_000_000) * rates.get("output", 0.40)
    return input_cost + output_cost


def retry_with_backoff(func, max_retries=5, base_delay=1.0):
    """Execute function with exponential backoff on rate limit errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_str = str(e).lower()
            is_rate_limit = any(x in error_str for x in ['429', 'rate limit', 'quota', 'resource exhausted'])
            
            if not is_rate_limit or attempt == max_retries - 1:
                raise
            
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"  Rate limited. Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
            time.sleep(delay)
    
    raise Exception("Max retries exceeded")


def create_client():
    """Create authenticated Gemini client."""
    project_id = get_gcloud_project()
    if not project_id:
        print("Error: No gcloud project set.")
        print("Run: gcloud config set project <YOUR_PROJECT_ID>")
        sys.exit(1)
    
    access_token = get_access_token()
    if not access_token:
        print("Error: Could not get access token.")
        print("Run: gcloud auth login")
        sys.exit(1)
    
    from google.oauth2 import credentials as oauth2_credentials
    creds = oauth2_credentials.Credentials(token=access_token)
    
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location="us-central1",
        credentials=creds
    )
    
    return client, project_id


def create_cache(client, model, context_text, ttl_minutes=60):
    """Create a context cache for the session."""
    try:
        # Check if caching is supported in this SDK version
        if not hasattr(client, 'caches'):
            print("  (Caching API not available in this SDK version, fallback to standard chat)")
            return None

        print(f"  Creating context cache (TTL {ttl_minutes}m)...")
        cache = client.caches.create(
            model=model,
            contents=[Part.from_text(text=context_text)],
            config=genai.types.CreateCachedContentConfig(
                display_name=f"local_analyze_session_{int(time.time())}",
                ttl=f"{ttl_minutes * 60}s"
            )
        )
        print(f"  ✅ Cache created: {cache.name}")
        return cache
    except Exception as e:
        print(f"  ⚠️ Failed to create cache: {e}")
        return None


def build_context_from_files(files, base_dir, with_line_numbers=False,
                              critical_files=None, positional_strategy=None):
    """Build context string from local files with optional positional strategy.

    Args:
        files: List of file paths to include
        base_dir: Base directory for relative paths
        with_line_numbers: Add line numbers to file content
        critical_files: List of file paths (relative) to position strategically
        positional_strategy: 'sandwich' (begin+end) or 'front-load' (begin only)

    Context Engineering:
        LLMs have U-shaped attention - they recall beginning/end better than middle.
        - 'sandwich': Place critical files at START and duplicate summary at END
        - 'front-load': Place critical files at START only
    """
    context_parts = []
    total_chars = 0
    critical_files = critical_files or []

    # Identify critical file paths (match by relative path suffix)
    critical_paths = []
    regular_paths = []
    for file_path in files:
        rel_path = str(file_path.relative_to(base_dir))
        is_critical = any(rel_path.endswith(cf) or cf in rel_path for cf in critical_files)
        if is_critical:
            critical_paths.append(file_path)
        else:
            regular_paths.append(file_path)

    # Reorder based on strategy
    if positional_strategy == 'sandwich':
        # Critical at start, regular in middle, critical summary at end
        ordered_files = critical_paths + regular_paths
        print(f"  Positional strategy: SANDWICH ({len(critical_paths)} critical files at start+end)", file=sys.stderr)
    elif positional_strategy == 'front-load':
        # Critical at start only
        ordered_files = critical_paths + regular_paths
        print(f"  Positional strategy: FRONT-LOAD ({len(critical_paths)} critical files at start)", file=sys.stderr)
    else:
        ordered_files = files

    # Build context
    for file_path in ordered_files:
        rel_path = file_path.relative_to(base_dir)
        content = read_file_content(file_path, with_line_numbers=with_line_numbers)
        file_block = f"\n--- FILE: {rel_path} ---\n{content}\n--- END FILE ---\n"
        context_parts.append(file_block)
        total_chars += len(file_block)

    # Sandwich: Add critical file summaries at end
    if positional_strategy == 'sandwich' and critical_paths:
        context_parts.append("\n--- CRITICAL FILES REFERENCE (END ANCHOR) ---")
        for file_path in critical_paths:
            rel_path = file_path.relative_to(base_dir)
            context_parts.append(f"  - {rel_path}")
        context_parts.append("--- END CRITICAL FILES REFERENCE ---\n")

    return "\n".join(context_parts), total_chars


def interactive_mode(client, model, context, system_prompt):
    """Run interactive REPL mode with caching support.
    
    Uses Vertex AI Context Caching if context is large, falling back to history-replay if small or failed.
    """
    if not IS_INTERACTIVE_ENV:
        print("Error: Interactive mode requires a TTY and non-agent environment.", file=sys.stderr)
        return
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE (Chat Session)")
    print("=" * 60)
    print("Context loaded. Ask questions about the codebase.")
    print("Commands: 'exit' or Ctrl+C to quit, 'clear' to reset session")
    print("=" * 60)
    
    # Try to create cache if context is substantial
    cache = None
    system_instruction = [Part.from_text(text=system_prompt)]
    
    # Heuristic: Cache if > 32k tokens (approx 128k chars). 
    # Vertex has min cache size limits (32k tokens).
    if len(context) > 130000:
       cache = create_cache(client, model, context)
    
    # Initialize chat
    chat = client.chats.create(model=model, config=genai.types.GenerateContentConfig(system_instruction=system_instruction))
    
    # Strategy selection
    if not cache:
        print("  (Standard Context Injection - Context too small for cache or cache failed)")
        initial_context = f"CODEBASE CONTEXT:\n{context}\n\nI have loaded this codebase. Ready for questions."
        # Build conversation history manually with full context
        conversation_history = [
            Content(role="user", parts=[Part.from_text(text=initial_context)]),
            Content(role="model", parts=[Part.from_text(text="I've reviewed the codebase context. What would you like to know?")])
        ]
    else:
        print("  (Using Cached Content Strategy)")
        conversation_history = [] 
        # Context is in cache. We just append new messages.
    
    total_input_tokens = 0
    total_output_tokens = 0
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit', 'q']:
                print(f"\nSession stats: {total_input_tokens:,} input tokens, {total_output_tokens:,} output tokens")
                print("Goodbye!")
                if cache:
                     try:
                         client.caches.delete(name=cache.name)
                         print(f"  Cache {cache.name} deleted.")
                     except Exception as e:
                         print(f"  Error deleting cache: {e}")
                break

            if user_input.lower() == 'clear':
                 conversation_history = []
                 print("History cleared.")
                 continue
            
            # Add user message
            conversation_history.append(Content(role="user", parts=[Part.from_text(text=user_input)]))
            
            print("\nThinking...")
            
            def make_request():
                config = genai.types.GenerateContentConfig()
                if cache:
                     config.cached_content = cache.name
                
                return client.models.generate_content(
                    model=model,
                    contents=conversation_history,
                    config=config
                )
            
            response = retry_with_backoff(make_request)
            print(f"\n{response.text}")
            
            # Add assistant response
            conversation_history.append(Content(role="model", parts=[Part.from_text(text=response.text)]))
            
            if response.usage_metadata:
                total_input_tokens += response.usage_metadata.prompt_token_count
                total_output_tokens += response.usage_metadata.candidates_token_count
                # Note: Cached content tokens are billed differently and may not show up in prompt_token_count
                # in the same way, but this gives a proxy for "active" tokens.
                print(f"\n[Turn: {response.usage_metadata.prompt_token_count} in, {response.usage_metadata.candidates_token_count} out | Session: {total_input_tokens:,} total in]")
        
        except KeyboardInterrupt:
            print(f"\n\nSession stats: {total_input_tokens:,} input tokens, {total_output_tokens:,} output tokens")
            print("Goodbye!")
            if cache:
                 try:
                     client.caches.delete(name=cache.name)
                 except: pass
            break
        except Exception as e:
            print(f"\nError: {e}")


# -------------------------------------------------------------------------
# SOCRATIC VALIDATOR (The Critic)
# -------------------------------------------------------------------------
class SocraticValidator:
    """
    Acts as the 'Critic Agent' to detect AI liabilities (Antimatter Laws).
    """
    def __init__(self, semantic_config):
        self.laws = semantic_config.get('antimatter', [])
        
    def validate(self, client, model, code_context: str, concept_role: str) -> dict:
        """
        Runs a Socratic critique on the code context against Antimatter Laws.
        """
        if not self.laws:
            return {"status": "SKIPPED", "reason": "No Antimatter Laws defined"}

        # Construct the critique prompt
        prompt = f'''
        ACT AS: Socratic Supervisor (Senior Architect Auditor).
        TASK: Audit the following code candidate (Role: {concept_role}) for 'Antimatter' violations.
        
        CODE CONTEXT:
        {code_context[:30000]} # Limit context for safety (approx 30k chars)
        
        ANTIMATTER LAWS (Violations to detect):
        '''
        
        for law in self.laws:
            prompt += f"- [{law['id']}] {law['name']}: {law['description']}\n  Check: {law['detection_prompt']}\n"
            
        prompt += '''
        
        OUTPUT FORMAT (JSON):
        {
          "compliant": boolean,
          "violations": [
            {
              "law_id": "AMxxx",
              "severity": "HIGH/MEDIUM/LOW",
              "reasoning": "Why this is a violation..."
            }
          ],
          "critique_summary": "One sentence summary of the audit."
        }
        '''
        
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in Socratic Validation: {e}")
            return {"status": "ERROR", "error": str(e)}

def load_semantic_models():
    if not SEMANTIC_MODELS_PATH.exists():
        print(f"Error: Semantic models not found at {SEMANTIC_MODELS_PATH}")
        sys.exit(1)
    with open(SEMANTIC_MODELS_PATH) as f:
        return yaml.safe_load(f)

def generate_hypotheses(domain_config):
    """
    Convert domain definitions into testable hypotheses.
    Now includes anchors for file discovery.
    """
    hypotheses = []
    definitions = domain_config.get('definitions', {})
    domain_scope = domain_config.get('scope', '')
    
    for concept, details in definitions.items():
        desc = details.get('description', 'No description')
        invariants = details.get('invariants', [])
        anchors = details.get('anchors', [])  # NEW: File anchors for discovery
        
        # Formulate the "claim"
        claim = f"Hypothesis: The concept '{concept}' is implemented according to strict invariants."
        
        hypotheses.append({
            'concept': concept,
            'claim': claim,
            'description': desc,
            'invariants': invariants,
            'anchors': anchors,  # Include anchors for verify_hypothesis
            'scope': domain_scope
        })
    
    return hypotheses

def verify_hypothesis(dev_client, vertex_client, hypothesis, store_name, candidate_override=None):
    """
    Execute the Verification Loop:
    1. Search (Tier 2) for candidates
    2. Analyze (Tier 1) for compliance
    3. Monitor (Guardrail) for liabilities
    """
    concept = hypothesis['concept']
    invariants = hypothesis['invariants']
    
    print(f"Targeting Concept: {concept}")
    
    # Phase A: Discovery
    candidate_files = set()
    
    # Priority 1: Explicit candidate override
    if candidate_override:
        print(f"    [Explicit Candidate]: {candidate_override}")
        candidate_files.add(candidate_override)
    
    # Priority 2: Use anchors from semantic_models.yaml (Robustified)
    anchors = hypothesis.get('anchors', [])
    if anchors and not candidate_override:
        print(f"    [Anchor Discovery]: {len(anchors)} anchor patterns")
        import glob
        for anchor in anchors:
            pattern = anchor.get('file', '')
            if pattern:
                full_path = PROJECT_ROOT / pattern
                # If it's a direct file path (no wildcards), just check existence
                if '*' not in pattern and full_path.exists():
                     candidate_files.add(str(full_path))
                     print(f"      Found (Direct): {full_path.name}")
                else:
                    # It's a glob pattern
                    search_pattern = str(full_path)
                    matches = glob.glob(search_pattern, recursive=True)
                    for match in matches:
                        candidate_files.add(match)
                        print(f"      Found (Glob): {Path(match).name}")
    
    # Priority 3: Fall back to File Search
    if not candidate_files and store_name:
         # Only run expensive search if absolutely needed
         pass # Logic remains...
    
    if not candidate_files:
        print("    No candidates found.")
        return {'verified': False, 'reason': 'No candidates found'}
    
    # ... (rest of function) ...
    
    # Priority 3: Fall back to File Search (if no anchors or no matches)
    discovery_query = f"Find code that implements or represents the concept '{concept}'. List relevant classes or modules."
    if not candidate_files and store_name:
         print("    [File Search Fallback]")
         search_result = search_with_file_search(dev_client, store_name, discovery_query)
         if search_result.get('citations'):
            for cite in search_result['citations']:
                if 'file' in cite:
                    fpath = cite['file']
                    if fpath and fpath.startswith('file://'):
                        fpath = fpath[7:]
                    if fpath:
                        candidate_files.add(fpath)
    
    if not candidate_files:
        print("    No candidates found.")
        return {'verified': False, 'reason': 'No candidates found'}
    
    print(f"    Found {len(candidate_files)} candidates: {', '.join([Path(f).name for f in list(candidate_files)[:3]])}...")
    
    # Phase B: Deep Verification (Tier 1)
    files_context = ""
    valid_files = []
    
    # Read first N files to build verification context
    for fpath in list(candidate_files)[:5]: # Limit to 5 files
        full_path = Path(fpath)
        if not full_path.is_absolute():
            full_path = PROJECT_ROOT / fpath
        
        if full_path.exists():
            try:
                content = read_file_content(full_path)
                files_context += f"\\n--- FILE: {fpath} ---\\n{content}\\n"
                valid_files.append(fpath)
            except Exception as e:
                 pass

    if not files_context:
        return {'verified': False, 'reason': 'Could not read files'}

    print(f"  Phase B: Verifying Invariants...")
    
    prompt = f'''
    You are a Semantic Auditor. Your job is to verify if the code matches the Semantic Definition.
    
    CONCEPT: {concept}
    DESCRIPTION: {hypothesis['description']}
    
    INVARIANTS (MUST BE TRUE):
    {chr(10).join([f'- {i}' for i in invariants])}
    
    CODEBASE CONTEXT:
    {files_context[:50000]}
    
    TASK:
    1. Identify which classes/functions in the context correspond to '{concept}'.
    2. Check each against the invariants.
    3. Output a structured report.
    
    FORMAT:
    ### Findings
    - **Entity**: [Name]
    - **Status**: [Compliant / Non-Compliant]
    - **Evidence**: [Quote or reasoning]
    - **Deviation**: [If non-compliant, explain why]
    '''
    
    response = vertex_client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=[Part.from_text(text=prompt)]
    )
    analysis_result = response.text
    
    # Phase C: Socratic Validation (Semantic Guardrails)
    print("  Phase C: Running Socratic Validator (Antimatter Check)...")
    try:
        with open(SEMANTIC_MODELS_PATH, 'r') as f:
            full_config = yaml.safe_load(f)
        validator = SocraticValidator(full_config)
        socratic_result = validator.validate(vertex_client, DEFAULT_MODEL, files_context, concept)
    except Exception as e:
        print(f"  Warning: Socratic Validator failed: {e}")
        socratic_result = {"status": "ERROR", "error": str(e)}

    return {
        'verified': True,
        'candidates': list(candidate_files),
        'analysis': analysis_result,
        'guardrails': socratic_result
    }

def verify_domain(domain, store_name=None, output=None, index=False, candidate=None):
    """Run validation loop for a domain."""
    models = load_semantic_models()
    if domain not in models:
        print(f"Error: Domain '{domain}' not found in semantic_models.yaml")
        sys.exit(1)
    
    domain_config = models[domain]
    store_name = store_name or f"collider-{domain}"
    
    # Initialize Clients
    print("Initializing clients...")
    dev_client = create_developer_client() # Needed for File Search
    vertex_client, _ = create_client()     # Needed for Analysis
    
    if index:
        if not dev_client:
             print("Error: Indexing requires GEMINI_API_KEY")
             sys.exit(1)
        print(f"Indexing domain '{domain}'...")
        target_dir = None
        if domain == 'pipeline':
            target_dir = PROJECT_ROOT / "standard-model-of-code/src/core"
        elif domain == 'theory':
            target_dir = PROJECT_ROOT / "standard-model-of-code/docs/theory"
        
        if target_dir:
             store_res = get_or_create_store(dev_client, store_name)
             files = list_local_files(target_dir)
             index_files_to_store(dev_client, store_res, files, PROJECT_ROOT)
    
    # Resolve store if needed (only if we are NOT using explicit candidate exclusively)
    store_resource_name = None
    if not candidate and dev_client:
         print(f"Resolving store '{store_name}'...")
         stores = list_file_search_stores(dev_client)
         t_store = next((s for s in stores if s.display_name == store_name), None)
         if t_store:
             store_resource_name = t_store.name
             print(f"  Found store: {store_resource_name}")
         else:
             print(f"  Warning: Store '{store_name}' not found. Discovery may fail.")

    hypotheses = generate_hypotheses(domain_config)
    print(f"\\nLoaded {len(hypotheses)} hypotheses for domain '{domain}'")
    
    results = []
    for h in hypotheses:
        print("-" * 60)
        res = verify_hypothesis(dev_client, vertex_client, h, store_resource_name, candidate_override=candidate)
        results.append({'hypothesis': h, 'result': res})
        time.sleep(1)
    
    # Output logic similar to refine_context
    output_content = f"# Validated Semantic Map: {domain.upper()}\\n\\n"
    output_content += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n\\n"
    
    for item in results:
        h = item['hypothesis']
        res = item['result']
        output_content += f"## Concept: {h['concept']}\\n> {h['description']}\\n\\n"
        if res['verified']:
            output_content += res['analysis'] + "\\n\\n"
            gr = res.get('guardrails', {})
            output_content += "### Semantic Guardrails (Antimatter Check)\\n"
            if gr.get('compliant'):
                output_content += "**PASSED**: No liabilities detected.\\n"
            else:
                output_content += "**DETECTED LIABILITIES**:\\n"
                for v in gr.get('violations', []):
                    output_content += f"- 🔴 **[{v.get('law_id')}]**: {v.get('reasoning')} (Severity: {v.get('severity')})\\n"
            output_content += "\\n"
        else:
             output_content += f"**Verification Failed**: {res.get('reason')}\\n\\n"

    if output:
        with open(output, 'w') as f:
            f.write(output_content)
        print(f"\\nRefinement log saved to: {output}")
    else:
        print(output_content)

# -------------------------------------------------------------------------
# SOCRATIC VALIDATOR (The Critic)
# -------------------------------------------------------------------------
class SocraticValidator:
    """
    Acts as the 'Critic Agent' to detect AI liabilities (Antimatter Laws).
    """
    def __init__(self, semantic_config):
        self.laws = semantic_config.get('antimatter', [])
        
    def validate(self, client, model, code_context: str, concept_role: str) -> dict:
        """
        Runs a Socratic critique on the code context against Antimatter Laws.
        """
        if not self.laws:
            return {"status": "SKIPPED", "reason": "No Antimatter Laws defined"}

        # Construct the critique prompt
        prompt = f'''
        ACT AS: Socratic Supervisor (Senior Architect Auditor).
        TASK: Audit the following code candidate (Role: {concept_role}) for 'Antimatter' violations.
        
        CODE CONTEXT:
        {code_context[:30000]} # Limit context for safety (approx 30k chars)
        
        ANTIMATTER LAWS (Violations to detect):
        '''
        
        for law in self.laws:
            prompt += f"- [{law['id']}] {law['name']}: {law['description']}\n  Check: {law['detection_prompt']}\n"
            
        prompt += '''
        
        OUTPUT FORMAT (JSON):
        {
          "compliant": boolean,
          "violations": [
            {
              "law_id": "AMxxx",
              "severity": "HIGH/MEDIUM/LOW",
              "reasoning": "Why this is a violation..."
            }
          ],
          "critique_summary": "One sentence summary of the audit."
        }
        '''
        
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in Socratic Validation: {e}")
            return {"status": "ERROR", "error": str(e)}

def load_semantic_models():
    if not SEMANTIC_MODELS_PATH.exists():
        print(f"Error: Semantic models not found at {SEMANTIC_MODELS_PATH}")
        sys.exit(1)
    with open(SEMANTIC_MODELS_PATH) as f:
        return yaml.safe_load(f)






def verify_domain(domain, store_name=None, output=None, index=False, candidate=None):
    """Run validation loop for a domain."""
    models = load_semantic_models()
    if domain not in models:
        print(f"Error: Domain '{domain}' not found in semantic_models.yaml")
        sys.exit(1)
    
    domain_config = models[domain]
    store_name = store_name or f"collider-{domain}"
    
    # Initialize Clients
    print("Initializing clients...")
    dev_client = create_developer_client() # Needed for File Search
    vertex_client, _ = create_client()     # Needed for Analysis
    
    if index:
        if not dev_client:
             print("Error: Indexing requires GEMINI_API_KEY")
             sys.exit(1)
        print(f"Indexing domain '{domain}'...")
        target_dir = None
        if domain == 'pipeline':
            target_dir = PROJECT_ROOT / "standard-model-of-code/src/core"
        elif domain == 'theory':
            target_dir = PROJECT_ROOT / "standard-model-of-code/docs/theory"
        
        if target_dir:
             store_res = get_or_create_store(dev_client, store_name)
             files = list_local_files(target_dir)
             index_files_to_store(dev_client, store_res, files, PROJECT_ROOT)
    
    # Resolve store if needed (only if we are NOT using explicit candidate exclusively)
    store_resource_name = None
    if not candidate and dev_client:
         print(f"Resolving store '{store_name}'...")
         stores = list_file_search_stores(dev_client)
         t_store = next((s for s in stores if s.display_name == store_name), None)
         if t_store:
             store_resource_name = t_store.name
             print(f"  Found store: {store_resource_name}")
         else:
             print(f"  Warning: Store '{store_name}' not found. Discovery may fail.")

    hypotheses = generate_hypotheses(domain_config)
    print(f"\\nLoaded {len(hypotheses)} hypotheses for domain '{domain}'")
    
    results = []
    for h in hypotheses:
        print("-" * 60)
        res = verify_hypothesis(dev_client, vertex_client, h, store_resource_name, candidate_override=candidate)
        results.append({'hypothesis': h, 'result': res})
        time.sleep(1)
    
    # Output logic similar to refine_context
    output_content = f"# Validated Semantic Map: {domain.upper()}\\n\\n"
    output_content += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n\\n"
    
    for item in results:
        h = item['hypothesis']
        res = item['result']
        output_content += f"## Concept: {h['concept']}\\n> {h['description']}\\n\\n"
        if res['verified']:
            # Handle string analysis (from old logic) or dict (from new)
            analysis_text = res['analysis'].get('summary', str(res['analysis'])) if isinstance(res['analysis'], dict) else str(res['analysis'])
            output_content += analysis_text + "\\n\\n"
            
            gr = res.get('guardrails', {})
            output_content += "### Semantic Guardrails (Antimatter Check)\\n"
            if gr.get('compliant'):
                output_content += "**PASSED**: No liabilities detected.\\n"
            else:
                output_content += "**DETECTED LIABILITIES**:\\n"
                for v in gr.get('violations', []):
                    output_content += f"- 🔴 **[{v.get('law_id')}]**: {v.get('reasoning')} (Severity: {v.get('severity')})\\n"
            output_content += "\\n"
        else:
             output_content += f"**Verification Failed**: {res.get('reason')}\\n\\n"

    # OUTPUT MANAGEMENT LIBRARY - INTELLIGENCE STORAGE
    # Storing structured output for future query-the-query capabilities
    intelligence_dir = PROJECT_ROOT / "context-management/intelligence"
    intelligence_dir.mkdir(exist_ok=True)
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    json_output_path = intelligence_dir / f"socratic_audit_{domain}_{timestamp}.json"
    
    # Generation tracking for meta-analysis awareness
    intelligence_data = {
        'timestamp': timestamp,
        'domain': domain,
        'execution_id': f"{domain}-{timestamp}",
        'generation': 1,  # First-level analysis of code
        'parent_execution_id': None,  # No parent for primary analysis
        'analysis_type': 'primary',  # vs 'meta' for analysis-of-analysis
        'source': {
            'type': 'repository',
            'location': str(PROJECT_ROOT)
        },
        'results': results
    }
    
    with open(json_output_path, 'w') as f:
        json.dump(intelligence_data, f, indent=2, default=str)
    
    print(f"\\n[Output Management] Intelligence stored at: {json_output_path}")
    
    # GCS SYNC - Upload to cloud storage
    GCS_BUCKET = "gs://elements-archive-2026/intelligence"
    gcs_path = f"{GCS_BUCKET}/{domain}/socratic_audit_{domain}_{timestamp}.json"
    try:
        sync_result = subprocess.run(
            ["gsutil", "cp", str(json_output_path), gcs_path],
            capture_output=True, text=True, timeout=30
        )
        if sync_result.returncode == 0:
            print(f"[Cloud Sync] Uploaded to: {gcs_path}")
        else:
            print(f"[Cloud Sync] Warning: Upload failed - {sync_result.stderr[:100]}")
    except Exception as e:
        print(f"[Cloud Sync] Warning: {e}")

    final_output = output or f"context-management/reports/socratic_audit_latest.md"

    if output:
        with open(output, 'w') as f:
            f.write(output_content)
        print(f"\\nRefinement log saved to: {output}")
    else:
        print(output_content)
def main():
    parser = argparse.ArgumentParser(
        description="Analyze local codebase with Gemini AI (v2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Explain the architecture" --set pipeline
  %(prog)s --interactive --set constraints
  %(prog)s --list-sets
  %(prog)s --recommend "how does classification work"
        """
    )
    parser.add_argument("prompt", nargs='?', default="Analyze this codebase", help="The question or instruction for the AI")
    parser.add_argument("--dir", help="Directory to analyze (relative to PROJECT_ROOT)")
    parser.add_argument("--file", help="Specific file(s) to include (comma separated)")
    parser.add_argument("--set", help="Analysis Set (use --list-sets to see available)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model to use")
    parser.add_argument("--mode", default="standard", choices=list(MODES.keys()) + ['interactive', 'insights', 'role_validation', 'plan_validation'], help="Analysis mode")
    parser.add_argument("--interactive", "-i", action="store_true", help="Enter interactive chat mode")
    parser.add_argument("--exclude", help="Additional exclude patterns (comma separated)")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    parser.add_argument("--output", "-o", help="Output file path (for insights mode)")
    parser.add_argument("--max-files", type=int, default=50, help="Maximum files to include")
    parser.add_argument("--line-numbers", "-n", action="store_true", help="Include line numbers in file content")
    # v2 arguments
    parser.add_argument("--list-sets", action="store_true", help="List available analysis sets and exit")
    parser.add_argument("--recommend", metavar="QUERY", help="Get set recommendations for a query")
    parser.add_argument("--force-oneshot", action="store_true", help="Force one-shot mode even if auto_interactive is set")
    # File Search (RAG) arguments
    parser.add_argument("--index", action="store_true", help="Index files to a File Search store (requires --store-name)")
    parser.add_argument("--search", metavar="QUERY", help="Query using File Search with citations (requires --store-name)")
    parser.add_argument("--store-name", help="Name of the File Search store to use")
    parser.add_argument("--list-stores", action="store_true", help="List all File Search stores")
    parser.add_argument("--delete-store", metavar="NAME", help="Delete a File Search store by name")
    # Verify / Socratic Layer arguments
    parser.add_argument("--verify", metavar="DOMAIN", help="Run semantic verification/Socratic check on a domain")
    parser.add_argument("--candidate", help="Target file for verification (overrides search)")
    parser.add_argument("--briefing", action="store_true", help="Print system briefing for agent orientation")
    # ACI (Adaptive Context Intelligence) arguments
    parser.add_argument("--aci", action="store_true", help="Enable Adaptive Context Intelligence (auto-select tier and context)")
    parser.add_argument("--tier", choices=["instant", "rag", "long_context", "perplexity"], help="Force specific ACI tier")
    parser.add_argument("--aci-debug", action="store_true", help="Show detailed ACI routing decision")
    args = parser.parse_args()

    # Load config early for --list-sets and --recommend
    sets_config = load_sets_config()
    analysis_sets = sets_config.get("analysis_sets", {})
    recommendations_config = sets_config.get("recommendations", {})

    # Handle --briefing (Agent Orientation)
    if args.briefing:
        print_briefing(analysis_sets)
        sys.exit(0)

    # Handle --verify (Socratic Layer)
    if args.verify:
        verify_domain(
            args.verify,
            store_name=args.store_name,
            output=args.output,
            index=args.index,
            candidate=args.candidate
        )
        sys.exit(0)

    # =========================================================================
    # ACI (Adaptive Context Intelligence) MODE
    # =========================================================================
    if args.aci:
        if not HAS_ACI:
            print("Error: ACI module not available. Check aci/ directory.", file=sys.stderr)
            sys.exit(1)

        print(f"\n{'='*60}", file=sys.stderr)
        print("ADAPTIVE CONTEXT INTELLIGENCE (ACI)", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        # Analyze and route the query
        force_tier = args.tier if args.tier else ""
        decision = analyze_and_route(args.prompt, force_tier=force_tier)

        if args.aci_debug:
            print(f"\n{format_routing_decision(decision)}", file=sys.stderr)

        print(f"Query: {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}", file=sys.stderr)
        print(f"Tier:  {decision.tier.value.upper()}", file=sys.stderr)
        print(f"Sets:  {', '.join(decision.primary_sets)}", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)

        # TIER 0: INSTANT - Try to answer from cached truths
        if decision.tier == Tier.INSTANT or decision.use_truths:
            truths = load_repo_truths(PROJECT_ROOT)
            if truths:
                instant_answer = answer_from_truths(args.prompt, truths)
                if instant_answer:
                    print(f"[INSTANT] {instant_answer}")
                    print(f"\n(Source: .agent/intelligence/truths/repo_truths.yaml)", file=sys.stderr)
                    sys.exit(0)
                elif decision.tier == Tier.INSTANT:
                    print("Could not answer from truths. Falling back to RAG.", file=sys.stderr)
                    decision = analyze_and_route(args.prompt, force_tier="rag")

        # TIER 3: PERPLEXITY - External research
        if decision.tier == Tier.PERPLEXITY:
            print("[PERPLEXITY] External research tier selected.", file=sys.stderr)
            print("Use the Perplexity MCP server for this query:", file=sys.stderr)
            print(f"  Query: {args.prompt}", file=sys.stderr)
            print("\nOr use --tier long_context to search internally.", file=sys.stderr)
            # Could integrate with Perplexity MCP here in future
            sys.exit(0)

        # TIER 1 & 2: RAG and LONG_CONTEXT - Continue with normal flow
        # Override args.set with ACI-selected sets
        if decision.primary_sets and not args.set:
            # Use the first set as primary
            args.set = decision.primary_sets[0]
            print(f"ACI auto-selected set: {args.set}", file=sys.stderr)

        # Inject agent context if needed
        if decision.inject_agent and args.set:
            if not args.set.startswith("agent_"):
                print(f"ACI injecting agent context alongside {args.set}", file=sys.stderr)
                # We'll handle this in the set resolution below

    # Handle --list-sets
    if args.list_sets:
        list_available_sets(analysis_sets)
        sys.exit(0)

    # Handle --recommend
    if args.recommend:
        suggested = recommend_sets(args.recommend, recommendations_config)
        if suggested:
            print(f"\nRecommended sets for: \"{args.recommend}\"")
            print("-" * 40)
            for s in suggested:
                desc = analysis_sets.get(s, {}).get('description', '')
                print(f"  --set {s:20} {desc}")
            print()
        else:
            print(f"\nNo specific recommendations for: \"{args.recommend}\"")
            print("Try: --list-sets to see all available sets\n")
        sys.exit(0)

    # =========================================================================
    # FILE SEARCH COMMANDS
    # =========================================================================

    # Handle --list-stores (needs Developer API client)
    if args.list_stores:
        client = create_developer_client()
        if not client:
            sys.exit(1)
        print("Connected to Gemini Developer API")
        stores = list_file_search_stores(client)
        print_stores_list(stores)
        sys.exit(0)

    # Handle --delete-store (needs Developer API client)
    if args.delete_store:
        client = create_developer_client()
        if not client:
            sys.exit(1)
        print("Connected to Gemini Developer API")
        print(f"\nDeleting store: {args.delete_store}")
        success = delete_file_search_store(client, args.delete_store)
        sys.exit(0 if success else 1)

    # Handle --search (query with File Search)
    if args.search:
        if not args.store_name:
            print("Error: --search requires --store-name")
            print("Use --list-stores to see available stores")
            sys.exit(1)

        client = create_developer_client()
        if not client:
            sys.exit(1)
        print("Connected to Gemini Developer API")

        # Find the store
        stores = list_file_search_stores(client)
        store_resource_name = None
        for store in stores:
            if store.display_name == args.store_name:
                store_resource_name = store.name
                break

        if not store_resource_name:
            print(f"Error: Store '{args.store_name}' not found")
            print("Use --list-stores to see available stores")
            sys.exit(1)

        print(f"\n{'='*60}")
        print(f"FILE SEARCH QUERY")
        print(f"{'='*60}")
        print(f"Store: {args.store_name}")
        print(f"Model: {FILE_SEARCH_MODEL}")
        print(f"Query: {args.search}")
        print(f"{'='*60}\n")

        try:
            result = search_with_file_search(client, store_resource_name, args.search)

            # Print response
            print("RESPONSE:")
            print("-" * 40)
            print(result['text'])

            # Print citations
            if result['citations']:
                print("\n" + "-" * 40)
                print("CITATIONS:")
                for i, cite in enumerate(result['citations'], 1):
                    # Prefer showing Title AND File URI if both exist
                    title = cite.get('title')
                    file_uri = cite.get('file')
                    web_uri = cite.get('web')

                    if file_uri:
                        if title and title != file_uri:
                             print(f"  [{i}] {title} ({file_uri})")
                        else:
                             print(f"  [{i}] {file_uri}")
                    elif web_uri:
                        if title:
                            print(f"  [{i}] {title} ({web_uri})")
                        else:
                            print(f"  [{i}] {web_uri}")
                    else:
                        print(f"  [{i}] {title or 'Unknown Source'}")

            # Print usage
            if result['usage']:
                print("\n" + "-" * 40)
                print(f"Tokens: {result['usage']['input_tokens']:,} in, {result['usage']['output_tokens']:,} out")
                cost = estimate_cost(result['usage']['input_tokens'], result['usage']['output_tokens'], FILE_SEARCH_MODEL)
                print(f"Estimated cost: ${cost:.4f}")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

        sys.exit(0)

    # Handle --index (index files to store)
    if args.index:
        if not args.store_name:
            print("Error: --index requires --store-name")
            sys.exit(1)

        # Need to collect files first, so continue to file collection logic below
        # but mark that we're in index mode
        pass

    # =========================================================================
    # STANDARD FLOW (Long Context / Interactive / One-shot)
    # =========================================================================

    # Determine base directory
    if args.dir:
        base_dir = PROJECT_ROOT / args.dir
    else:
        base_dir = PROJECT_ROOT
    
    if not base_dir.exists():
        print(f"Error: Directory not found: {base_dir}")
        sys.exit(1)
    
    print(f"Project Root: {PROJECT_ROOT}", file=sys.stderr)
    print(f"Analyzing:    {base_dir}", file=sys.stderr)
    print(f"Model:        {args.model}", file=sys.stderr)
    print(f"Mode:         {'INTERACTIVE' if args.interactive else args.mode.upper()}", file=sys.stderr)
    
    # User excludes
    user_excludes = [p.strip() for p in args.exclude.split(",")] if args.exclude else None

    # Track set metadata for auto-interactive decisions
    set_auto_interactive = False
    set_max_tokens = 100_000
    set_critical_files = []
    set_positional_strategy = None

    # Collect files
    patterns = None
    if args.file:
        patterns = [p.strip() for p in args.file.split(",")]
    elif args.set:
        if args.set not in analysis_sets:
            print(f"Error: Unknown set '{args.set}'. Available: {list(analysis_sets.keys())}", file=sys.stderr)
            print(f"Use --list-sets to see descriptions", file=sys.stderr)
            sys.exit(1)

        # Use resolve_set to handle includes
        resolved = resolve_set(args.set, analysis_sets)
        patterns = resolved['patterns']
        set_auto_interactive = resolved['auto_interactive']
        set_max_tokens = resolved['max_tokens']
        set_critical_files = resolved.get('critical_files', [])
        set_positional_strategy = resolved.get('positional_strategy', None)

        # Show resolution info
        print(f"Using Set:    {args.set.upper()} - {resolved['description']}", file=sys.stderr)
        if resolved.get('patterns') and len(patterns) > len(analysis_sets[args.set].get('patterns', [])):
            included_sets = analysis_sets[args.set].get('includes', [])
            print(f"  Composed from: {', '.join(included_sets)}", file=sys.stderr)

        # Warn about token budget
        if set_max_tokens > MAX_CONTEXT_TOKENS:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"WARNING: Set '{args.set}' has budget {set_max_tokens:,} tokens", file=sys.stderr)
            print(f"         This EXCEEDS the {MAX_CONTEXT_TOKENS:,} token context limit!", file=sys.stderr)
            print(f"         Consider using a smaller, more focused set.", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)
    
    selected_files = list_local_files(base_dir, patterns, user_excludes)
    
    # Auto-inject architecture docs for architect mode
    if args.mode == 'architect':
        for doc_path in ARCHITECT_DOCS:
            full_path = PROJECT_ROOT / doc_path
            if full_path.exists() and full_path not in selected_files:
                selected_files.insert(0, full_path)
                print(f"Auto-injected: {doc_path}")
    
    # Limit files
    if len(selected_files) > args.max_files:
        print(f"\nWarning: Found {len(selected_files)} files, limiting to {args.max_files}")
        selected_files = selected_files[:args.max_files]
    
    if not selected_files:
        print("No files matched your criteria.")
        sys.exit(1)
    
    print(f"\nSelected {len(selected_files)} files:", file=sys.stderr)
    for f in selected_files[:5]:
        try:
            print(f"  - {f.relative_to(PROJECT_ROOT)}", file=sys.stderr)
        except ValueError:
            print(f"  - {f}", file=sys.stderr)
    if len(selected_files) > 5:
        print(f"  ... and {len(selected_files) - 5} more", file=sys.stderr)

    # =========================================================================
    # INDEX MODE: Index files to File Search store
    # =========================================================================
    if args.index:
        print(f"\n{'='*60}")
        print("FILE SEARCH INDEXING")
        print(f"{'='*60}")
        print(f"Store: {args.store_name}")
        print(f"Files: {len(selected_files)}")

        if not args.yes and IS_INTERACTIVE_ENV:
            confirm = input("\nProceed with indexing? [Y/n] ")
            if confirm.lower() == 'n':
                sys.exit(0)
        elif not args.yes and not IS_INTERACTIVE_ENV:
             print("Non-interactive mode detected: Auto-confirming indexing.", file=sys.stderr)

        client = create_developer_client()
        if not client:
            sys.exit(1)
        print("Connected to Gemini Developer API")

        # Get or create store
        store_resource_name = get_or_create_store(client, args.store_name)

        # Index files
        print(f"\nIndexing {len(selected_files)} files...")
        stats = index_files_to_store(client, store_resource_name, selected_files, PROJECT_ROOT)

        # Print summary
        print(f"\n{'='*60}")
        print("INDEXING COMPLETE")
        print(f"{'='*60}")
        print(f"  Indexed: {stats['indexed']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Failed:  {stats['failed']}")

        if stats['errors']:
            print("\nErrors:")
            for err in stats['errors'][:5]:
                print(f"  - {err}")
            if len(stats['errors']) > 5:
                print(f"  ... and {len(stats['errors']) - 5} more")

        print(f"\nTo query this store:")
        print(f"  python local_analyze.py --search \"your question\" --store-name {args.store_name}")
        print(f"{'='*60}\n")

        sys.exit(0 if stats['failed'] == 0 else 1)

    # =========================================================================
    # LONG CONTEXT MODE: Build context and continue
    # =========================================================================

    # Determine if line numbers should be added
    use_line_numbers = args.line_numbers or args.mode in ['forensic', 'interactive'] or args.interactive
    
    # Build context
    print("\nBuilding context from local files...", file=sys.stderr)
    context, total_chars = build_context_from_files(
        selected_files, PROJECT_ROOT,
        with_line_numbers=use_line_numbers,
        critical_files=set_critical_files,
        positional_strategy=set_positional_strategy
    )
    estimated_tokens = total_chars // 4  # Rough estimate
    print(f"Context size: ~{estimated_tokens:,} tokens ({total_chars:,} chars)", file=sys.stderr)
    if use_line_numbers:
        print("Line numbers: enabled", file=sys.stderr)

    # Token limit warnings
    if estimated_tokens > MAX_CONTEXT_TOKENS:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"CRITICAL: Context ({estimated_tokens:,} tokens) EXCEEDS", file=sys.stderr)
        print(f"          the {MAX_CONTEXT_TOKENS:,} token limit!", file=sys.stderr)
        print(f"          The API call will likely fail or truncate.", file=sys.stderr)
        print(f"          Use --set with a smaller set or --max-files", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
    elif estimated_tokens > MAX_CONTEXT_TOKENS * 0.8:
        print(f"  Warning: Context is at {estimated_tokens / MAX_CONTEXT_TOKENS * 100:.0f}% of limit", file=sys.stderr)

    # Determine effective mode: auto-interactive if set specifies it or context is large
    use_interactive = args.interactive or args.mode == 'interactive'

    if not use_interactive and not args.force_oneshot:
        # Auto-enable interactive for large contexts or if set specifies it
        if set_auto_interactive:
            print(f"\n  Auto-interactive: enabled (set '{args.set}' specifies auto_interactive)", file=sys.stderr)
            use_interactive = True
        elif estimated_tokens > INTERACTIVE_THRESHOLD:
            print(f"\n  Auto-interactive: enabled (context > {INTERACTIVE_THRESHOLD:,} tokens)", file=sys.stderr)
            print(f"                    Use --force-oneshot to override", file=sys.stderr)
            use_interactive = True

    if not IS_INTERACTIVE_ENV:
        if use_interactive:
            print("Review: Non-interactive environment detected. Disabling interactive mode.", file=sys.stderr)
            use_interactive = False
    
    if not args.yes and IS_INTERACTIVE_ENV:
        mode_str = "INTERACTIVE" if use_interactive else "ONE-SHOT"
        confirm = input(f"\nProceed with {mode_str} mode? [Y/n] ")
        if confirm.lower() == 'n':
            sys.exit(0)

    # Create client
    client, project_id = create_client()
    print(f"Connected to project: {project_id}", file=sys.stderr)

    # Get system prompt
    if use_interactive:
        system_prompt = MODES.get('interactive', {}).get('prompt', MODES.get('standard', {}).get('prompt', ''))
        if not system_prompt:
            system_prompt = "You are an expert software engineer. Answer questions about the provided codebase. Cite file paths and line numbers."
        interactive_mode(client, args.model, context, system_prompt)
    if args.set == 'archeology' or args.mode == 'trace':
        # Evolutionary Trace Mode
        print("\n--- Generating Evolutionary Trace (Generation 2) ---", file=sys.stderr)
        
        trace_prompt = """
        You are an Archeological Code Analyst (Generation 2).
        Your task is to trace the evolution of the concept 'ATOM' through the provided legacy documentation.

        Context provided:
        {context}

        Output Strategy:
        1. Identify the earliest definition of 'Atom' in the provided text (look at 2025/2026 timestamps).
        2. Trace how the definition changed in subsequent documents.
        3. Identify the "Pivot Point" when the definitions shifted significantly.
        4. Summarize the final state of the concept in the latest provided doc.

        Format your response as markdown:
        # Evolutionary Trace: The Atom
        ## Timeline
        - [Date] [Source]: [Definition Summary]
        ...
        ## Analysis
        [Deep conceptual analysis of the drift]
        """
        
        try:
             full_prompt = trace_prompt.format(context=context)
        except Exception:
             full_prompt = trace_prompt.replace("{context}", context)

        def make_request():
            return client.models.generate_content(
                model=args.model,
                contents=[Part.from_text(text=full_prompt)]
            )
        
        try:
            response = retry_with_backoff(make_request)
            print(response.text)

            # Auto-save trace response
            auto_save_gemini_response(
                query=f"[TRACE MODE] {args.prompt or 'execution trace'}",
                response_text=response.text or "",
                model=args.model,
                mode="trace"
            )

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(response.text or "")
                print(f"Stats saved to {args.output}")
        except Exception as e:
            print(f"Error during generation: {e}", file=sys.stderr)
            sys.exit(1)

        sys.exit(0)

    elif args.mode == 'insights':
        # Insights mode (Structured JSON)
        if not INSIGHTS_PROMPT:
            print("Error: 'insights' prompt not found in prompts.yaml (or usage of insights_source failed)")
            sys.exit(1)
        
        # Inject context into the prompt placeholder
        # Note: If context has braces, format might fail. TODO: Safe format or Template.
        try:
             full_prompt = INSIGHTS_PROMPT.format(context=context)
        except Exception:
             # Fallback for safe formatting if context contains braces
             full_prompt = INSIGHTS_PROMPT.replace("{context}", context)

        print("\n--- Generating Insights (JSON) ---", file=sys.stderr)
        
        def make_request():
            return client.models.generate_content(
                model=args.model,
                contents=[Part.from_text(text=full_prompt)],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
        
        try:
            response = retry_with_backoff(make_request)
            
            # Save or print
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(response.text or "")
                print(f"\n✅ Insights saved to: {args.output}")
            else:
                print(response.text)

            # Auto-save insights response
            auto_save_gemini_response(
                query="[INSIGHTS MODE] Structured analysis",
                response_text=response.text or "",
                model=args.model,
                mode="insights"
            )

            print("\n-----------------")
            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                print(f"Tokens Used: {input_tokens:,} Input, {output_tokens:,} Output")
                est = estimate_cost(input_tokens, output_tokens, args.model)
                print(f"Estimated Cost: ${est:.4f}")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.mode == 'role_validation':
        # Role Validation mode (Structured JSON for RoleRegistry audit)
        if not ROLE_VALIDATION_PROMPT:
            print("Error: 'role_validation' prompt not found in prompts.yaml")
            sys.exit(1)

        try:
            full_prompt = ROLE_VALIDATION_PROMPT.format(context=context)
        except Exception:
            full_prompt = ROLE_VALIDATION_PROMPT.replace("{context}", context)

        print("\n--- Role Validation Analysis (JSON) ---", file=sys.stderr)

        def make_request():
            return client.models.generate_content(
                model=args.model,
                contents=[Part.from_text(text=full_prompt)],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

        try:
            response = retry_with_backoff(make_request)

            # Save or print
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(response.text or "")
                print(f"\n✅ Role validation report saved to: {args.output}")
            else:
                print(response.text)

            # Auto-save role validation response
            auto_save_gemini_response(
                query="[ROLE_VALIDATION MODE] Registry audit",
                response_text=response.text or "",
                model=args.model,
                mode="role_validation"
            )

            print("\n-----------------")
            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                print(f"Tokens Used: {input_tokens:,} Input, {output_tokens:,} Output")
                est = estimate_cost(input_tokens, output_tokens, args.model)
                print(f"Estimated Cost: ${est:.4f}")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.mode == 'plan_validation':
        # Plan Validation mode (Structured JSON for verifying implementation plans)
        if not PLAN_VALIDATION_PROMPT:
            print("Error: 'plan_validation' prompt not found in prompts.yaml")
            sys.exit(1)

        try:
            full_prompt = PLAN_VALIDATION_PROMPT.format(context=context)
        except Exception:
            full_prompt = PLAN_VALIDATION_PROMPT.replace("{context}", context)

        print("\n--- Plan Validation Analysis (JSON) ---", file=sys.stderr)

        def make_request():
            return client.models.generate_content(
                model=args.model,
                contents=[Part.from_text(text=full_prompt)],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

        try:
            response = retry_with_backoff(make_request)

            # Save or print
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(response.text or "")
                print(f"\n✅ Plan validation report saved to: {args.output}")
            else:
                print(response.text)

            # Auto-save plan validation response
            auto_save_gemini_response(
                query="[PLAN_VALIDATION MODE] Implementation plan verification",
                response_text=response.text or "",
                model=args.model,
                mode="plan_validation"
            )

            print("\n-----------------")
            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                print(f"Tokens Used: {input_tokens:,} Input, {output_tokens:,} Output")
                est = estimate_cost(input_tokens, output_tokens, args.model)
                print(f"Estimated Cost: ${est:.4f}")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    else:
        # One-shot mode
        system_prompt = MODES.get(args.mode, {}).get('prompt', '')
        full_prompt = f"{system_prompt}\n\nCODEBASE CONTEXT:\n{context}\n\nUSER QUERY: {args.prompt}"

        print("\n--- Analyzing ---", file=sys.stderr)
        
        def make_request():
            return client.models.generate_content(
                model=args.model,
                contents=[Part.from_text(text=full_prompt)]
            )
        
        try:
            response = retry_with_backoff(make_request)
            print(response.text)

            # Auto-save Gemini response
            auto_save_gemini_response(
                query=args.prompt or "query",
                response_text=response.text or "",
                model=args.model,
                mode=args.mode
            )

            print("\n-----------------")

            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                print(f"Tokens Used: {input_tokens:,} Input, {output_tokens:,} Output")
                est = estimate_cost(input_tokens, output_tokens, args.model)
                print(f"Estimated Cost: ${est:.4f}")

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
