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
        sanitize_sets,
    )
    from aci.feedback_loop import log_aci_query, get_feedback_loop
    HAS_ACI = True
except ImportError:
    HAS_ACI = False

# Import Industrial UI for styled output
try:
    from industrial_ui import GeminiUI, Colors as C
    HAS_INDUSTRIAL_UI = True
except ImportError:
    HAS_INDUSTRIAL_UI = False
    GeminiUI = None  # type: ignore
    C = None  # type: ignore

# Import Perplexity research for Tier 3 queries
try:
    from perplexity_research import research as perplexity_research, auto_save_research
    HAS_PERPLEXITY = True
except ImportError:
    HAS_PERPLEXITY = False

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

# Session logging - prints structured turn logs to stderr for visibility
# Set SESSION_LOG=1 to see timestamped user/assistant turns
SESSION_LOG = os.environ.get('SESSION_LOG') == '1'

# Session log collector for auto-save
_session_turns = []
_session_start_time = None
_session_model = None

# Architecture docs to auto-inject for architect mode

# Architecture docs to auto-inject for architect mode
# Point to canonical MODEL.md
ARCHITECT_DOCS = [
    "context-management/docs/COLLIDER_ARCHITECTURE.md",
    "standard-model-of-code/docs/MODEL.md",
]

# Load prompts and modes
# Model versions (check for deprecation at https://ai.google.dev/models)
if PROMPTS_CONFIG_PATH.exists():
    with open(PROMPTS_CONFIG_PATH) as f:
        _prompts_data = yaml.safe_load(f)
        PRICING = _prompts_data.get("pricing", {})
        # DEFAULT_MODEL: Primary model for complex reasoning (best capability)
        # Preferred: gemini-3-pro-preview (current flagship)
        # Alternative: gemini-2.5-pro (stable, still supported)
        DEFAULT_MODEL = _prompts_data.get("default_model", "gemini-3-pro-preview")
        # FAST_MODEL: Fast, cost-effective model for routine queries
        # Current: gemini-2.0-flash-001
        # Note: gemini-2.0-flash (base) deprecated 2026-03-31
        FAST_MODEL = _prompts_data.get("fast_model", "gemini-2.0-flash-001")
        # FALLBACK_MODELS: Escalation chain if primary unavailable
        # Order matters: tried left-to-right
        FALLBACK_MODELS = _prompts_data.get("fallback_models", ["gemini-2.5-pro", "gemini-2.0-flash-001"])
        MODES = _prompts_data.get("analysis_prompts", {}).get("modes", {})
        # Prefer "insights_source" for raw file analysis
        INSIGHTS_PROMPT = _prompts_data.get("analysis_prompts", {}).get("insights_source") or _prompts_data.get("analysis_prompts", {}).get("insights")
        # Role validation prompt
        ROLE_VALIDATION_PROMPT = _prompts_data.get("analysis_prompts", {}).get("role_validation")
        # Plan validation prompt
        PLAN_VALIDATION_PROMPT = _prompts_data.get("analysis_prompts", {}).get("plan_validation")
        # Backend configuration (vertex or aistudio)
        _CONFIGURED_BACKEND = _prompts_data.get("backend", "vertex")
        _VERTEX_PROJECT = _prompts_data.get("vertex_project")  # None = use gcloud config
        _VERTEX_LOCATION = _prompts_data.get("vertex_location", "us-central1")
else:
    # Fallback when config file is missing
    # See above comments for model selection rationale
    PRICING = {}
    DEFAULT_MODEL = "gemini-3-pro-preview"  # Best reasoning capability
    FAST_MODEL = "gemini-2.0-flash-001"     # Cost-effective (deprecated 2026-03-31)
    FALLBACK_MODELS = ["gemini-2.5-pro", "gemini-2.0-flash-001"]
    MODES = {}
    INSIGHTS_PROMPT = None
    ROLE_VALIDATION_PROMPT = None
    PLAN_VALIDATION_PROMPT = None
    _CONFIGURED_BACKEND = "vertex"
    _VERTEX_PROJECT = None
    _VERTEX_LOCATION = "us-central1"

# Environment variable overrides for backend selection
# GEMINI_BACKEND=vertex|aistudio overrides config file
GEMINI_BACKEND_ENV = "GEMINI_BACKEND"
BACKEND = os.environ.get(GEMINI_BACKEND_ENV, _CONFIGURED_BACKEND).lower()


def load_sets_config():
    if not SETS_CONFIG_PATH.exists():
        return {}
    with open(SETS_CONFIG_PATH) as f:
        return yaml.safe_load(f)


def count_tokens(content: str, model: str = "gemini-2.0-flash-001") -> int:
    """
    Count tokens in content using Gemini API.

    Args:
        content: Text to count tokens for
        model: Model to use for tokenization

    Returns:
        Token count, or -1 on error
    """
    try:
        client = genai.Client()
        result = client.models.count_tokens(model=model, contents=content)
        return result.total_tokens
    except Exception as e:
        # Fallback: return -1 to signal error (caller will estimate)
        return -1


def validate_context_size(content: str, model: str, max_tokens: int = None) -> tuple:
    """
    Validate context size before sending to API.

    Args:
        content: Text content to validate
        model: Model to validate for
        max_tokens: Maximum allowed tokens (None = use model default)

    Returns:
        (is_valid, token_count) - is_valid is True if under limit
    """
    if max_tokens is None:
        # Default limits per model
        if "flash" in model.lower():
            max_tokens = MAX_FLASH_DEEP_TOKENS
        else:
            max_tokens = MAX_CONTEXT_TOKENS

    token_count = count_tokens(content, model)
    if token_count < 0:
        # Fallback: estimate ~4 chars per token
        token_count = len(content) // 4

    is_valid = token_count < max_tokens
    return is_valid, token_count


# Token limits per tier
MAX_CONTEXT_TOKENS = 1_000_000       # Gemini 3 Pro (Long Context tier)
MAX_FLASH_DEEP_TOKENS = 2_000_000    # Gemini 2.0 Flash (Flash Deep tier)
INTERACTIVE_THRESHOLD = 50_000       # Auto-interactive above this

# File Search configuration
# NOTE: File Search requires the Gemini Developer API (ai.google.dev), not Vertex AI
# Set GEMINI_API_KEY environment variable to use File Search features
# File Search configuration uses Gemini 3 Pro for best semantic understanding
# Gemini 3 Pro Preview: Best reasoning (up to 1M context tokens)
# Check model availability: https://ai.google.dev/models
FILE_SEARCH_MODEL = "gemini-3-pro-preview"  # Upgraded to Gemini 3 Pro (2026-01-23)
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
            Note: gemini-2.0-flash (base) deprecated 2026-03-31
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


# =============================================================================
# PHASE 1: UNIFIED EXECUTION + PERPLEXITY MEMBRANE
# =============================================================================

def prepare_perplexity_query(query: str) -> str:
    """
    Prepare a clean query for Perplexity external search.

    Phase 1 membrane: NO internal context injection.
    Perplexity search is driven by user prompt only - any injected
    repo context pollutes the search and causes hallucinated results.

    Returns:
        Clean query string for Perplexity API
    """
    return query.strip()


def execute_analysis(
    *,
    client,
    query: str,
    context: str,
    model: str,
    mode: str = "standard",
    system_prompt: str = None,
    extra_context: str = None,
    tier: str = None,
    sets: list = None,
) -> dict:
    """
    Unified execution point for all INTERNAL LLM calls.

    This is the "always been" abstraction - all internal tiers funnel through here:
    - LONG_CONTEXT: context from sets
    - FLASH_DEEP: larger context, same path
    - HYBRID: context + extra_context (external evidence)

    Args:
        client: Gemini API client
        query: User's question
        context: Internal codebase context
        model: Model to use
        mode: Analysis mode (standard, forensic, etc.)
        system_prompt: Optional system prompt override
        extra_context: External evidence (HYBRID injects here)
        tier: Tier name for logging
        sets: Set names for logging

    Returns:
        dict with 'text', 'usage', 'model', 'mode', 'saved_path'
    """
    # Build full context (internal + optional external evidence)
    full_context = context
    if extra_context:
        full_context = f"{context}\n\n{extra_context}"

    # Get system prompt from mode if not provided
    if system_prompt is None:
        system_prompt = MODES.get(mode, {}).get('prompt', '')

    # Build the full prompt
    full_prompt = f"{system_prompt}\n\nCODEBASE CONTEXT:\n{full_context}\n\nUSER QUERY: {query}"

    _log_turn("user", query)
    tier_label = f"[{tier}] " if tier else ""
    print(f"\n{tier_label}--- Analyzing ---", file=sys.stderr)

    def make_request():
        return client.models.generate_content(
            model=model,
            contents=[Part.from_text(text=full_prompt)]
        )

    try:
        response = retry_with_backoff(make_request)
        response_text = response.text or ""

        _log_turn("assistant", response_text)

        # Auto-save
        saved_path = auto_save_gemini_response(query, response_text, model, mode)

        # Usage stats
        usage = None
        if response.usage_metadata:
            usage = {
                'input_tokens': response.usage_metadata.prompt_token_count,
                'output_tokens': response.usage_metadata.candidates_token_count,
            }
            print("\n-----------------", file=sys.stderr)
            print(f"Tokens Used: {usage['input_tokens']:,} Input, {usage['output_tokens']:,} Output", file=sys.stderr)
            est = estimate_cost(usage['input_tokens'], usage['output_tokens'], model)
            print(f"Estimated Cost: ${est:.4f}", file=sys.stderr)

        return {
            'text': response_text,
            'usage': usage,
            'model': model,
            'mode': mode,
            'saved_path': saved_path,
            'tier': tier,
            'sets': sets,
        }

    except Exception as e:
        print(f"Error during generation: {e}", file=sys.stderr)
        raise


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

    def make_request():
        return client.models.generate_content(
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

    response = retry_with_backoff(make_request)

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



def _find_doppler():
    """Find doppler executable in PATH or common locations."""
    import shutil
    if shutil.which("doppler"):
        return "doppler"

    # Common locations on macOS/Linux
    candidates = [
        os.path.expanduser("~/.local/bin/doppler"),
        "/usr/local/bin/doppler",
        "/opt/homebrew/bin/doppler",
        "/usr/bin/doppler"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "doppler"


def get_doppler_secret(key: str) -> str | None:
    """Fetch a secret from Doppler. Returns None if unavailable."""
    try:
        doppler_exe = _find_doppler()
        # print(f"DEBUG: doppler_exe found: {doppler_exe}", flush=True)
        result = subprocess.run(
            [doppler_exe, "secrets", "get", key, "--plain"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            print(f"DEBUG: doppler command failed: {result.stderr}", flush=True)

        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"DEBUG: doppler execution error: {e}", flush=True)
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


def create_gemini_cache(content: str, model: str, display_name: str = "repopack_cache") -> str:
    """
    Create a Gemini context cache for expensive content.

    Uses cached_contents API to store large context snapshots that can be
    reused across multiple queries without re-transmission costs.

    Args:
        content: Content to cache (RepoPack formatted)
        model: Model name (e.g., 'gemini-2.0-flash-001')
            Note: gemini-2.0-flash (base) deprecated 2026-03-31
        display_name: Human-readable cache name for tracking

    Returns:
        Cache resource name (cachedContents/xxx) if successful, empty string otherwise
    """
    try:
        from google import genai
        from google.genai import types

        client = genai.Client()

        # Create cache with 1 hour TTL (3600 seconds)
        # Gemini will store this for later reuse
        cache = client.caches.create(
            model=model,
            config=types.CreateCachedContentConfig(
                display_name=display_name,
                contents=[content],
                ttl="3600s"  # 1 hour validity
            )
        )

        return cache.name
    except Exception as e:
        print(f"[Cache creation failed] {e}", file=sys.stderr)
        return ""


def get_or_create_cache(repo_path: str, model: str, force_new: bool = False) -> str:
    """
    Get existing valid cache or create a new one for current repo state.

    Implements the "expensive per snapshot, cheap per question" pattern:
    - Check cache_registry for valid cache
    - If found and valid, reuse it
    - If not found or expired, create new cache from RepoPack
    - Register new cache in registry

    Args:
        repo_path: Path to repository root
        model: Model name
        force_new: Force creation of new cache (ignore existing)

    Returns:
        Cache resource name if available, empty string otherwise
    """
    try:
        from aci.cache_registry import CacheRegistry
        from aci.repopack import format_repopack, get_cache_key

        repo_path = Path(repo_path)
        registry = CacheRegistry()
        workspace_key = get_cache_key(repo_path)

        # Check for existing valid cache (unless force_new)
        if not force_new:
            existing = registry.get_valid_cache(model, workspace_key)
            if existing:
                print(f"[Cache hit] Using existing cache: {existing.cache_name}", file=sys.stderr)
                return existing.cache_name

        # Cache miss - create new cache from RepoPack
        print(f"[Cache miss] Creating new cache for {workspace_key}", file=sys.stderr)

        # Format repo as RepoPack (deterministic, cacheable format)
        repopack = format_repopack(repo_path)

        # Create cache
        cache_name = create_gemini_cache(repopack, model)

        if cache_name:
            # Count tokens for registry tracking
            token_count = count_tokens(repopack, model)

            # Register cache in local registry
            registry.register(
                cache_name=cache_name,
                model=model,
                workspace_key=workspace_key,
                ttl_seconds=3600,  # 1 hour
                token_count=token_count if token_count > 0 else 0
            )
            print(f"[Cache created] {cache_name} ({token_count} tokens)", file=sys.stderr)

        return cache_name
    except Exception as e:
        print(f"[Cache error] {e}", file=sys.stderr)
        return ""


def enrich_query_for_perplexity(query: str, decision, analysis_sets: dict) -> str:
    """
    Enrich a query with local context before sending to Perplexity.

    This implements the Context Injection pattern recommended for external research:
    1. Extract key definitions from local glossary/theory
    2. Include critical file excerpts from ACI-selected sets
    3. Frame the query with local context

    Args:
        query: Original user query
        decision: ACI RoutingDecision with primary_sets
        analysis_sets: Loaded analysis sets configuration

    Returns:
        Enriched query string with local context injected
    """
    context_parts = []
    max_context_chars = 2000  # Keep context concise for Perplexity

    # 1. Try to load key definitions from glossary
    glossary_path = PROJECT_ROOT / "standard-model-of-code/docs/GLOSSARY.yaml"
    if glossary_path.exists():
        try:
            with open(glossary_path, 'r') as f:
                glossary = yaml.safe_load(f) or {}

            # Extract terms mentioned in query (case-insensitive)
            query_lower = query.lower()
            relevant_terms = []
            for term, definition in glossary.items():
                if term.lower() in query_lower or term.lower().replace('_', ' ') in query_lower:
                    if isinstance(definition, dict):
                        desc = definition.get('definition') or definition.get('description', '')
                    else:
                        desc = str(definition)
                    if desc:
                        relevant_terms.append(f"- {term}: {desc[:200]}")

            if relevant_terms:
                context_parts.append("LOCAL DEFINITIONS:\n" + "\n".join(relevant_terms[:5]))
        except Exception:
            pass

    # 2. Extract critical files from ACI-selected sets
    if decision and hasattr(decision, 'primary_sets') and decision.primary_sets:
        critical_files = []
        for set_name in decision.primary_sets[:3]:  # Limit to 3 sets
            set_def = analysis_sets.get(set_name, {})
            for cf in set_def.get('critical_files', [])[:2]:  # Max 2 per set
                full_path = PROJECT_ROOT / cf
                if full_path.exists() and str(full_path) not in critical_files:
                    critical_files.append(str(full_path))

        # Read excerpts from critical files
        file_excerpts = []
        chars_used = 0
        for fpath in critical_files[:3]:  # Max 3 files
            if chars_used >= max_context_chars:
                break
            try:
                content = read_file_content(fpath)
                # Take first 500 chars as excerpt
                excerpt = content[:500].strip()
                if excerpt:
                    fname = Path(fpath).name
                    file_excerpts.append(f"[{fname}]: {excerpt}...")
                    chars_used += len(excerpt)
            except Exception:
                pass

        if file_excerpts:
            context_parts.append("LOCAL CODEBASE CONTEXT:\n" + "\n".join(file_excerpts))

    # 3. Build enriched query
    if context_parts:
        enriched = f"""CONTEXT FROM LOCAL CODEBASE (Standard Model of Code project):

{chr(10).join(context_parts)}

---

RESEARCH QUESTION:
{query}

Please validate or research the above question, considering the local context provided. Focus on academic/industry standards and best practices."""
        return enriched

    # If no context available, at least frame the query
    return f"""Research question about the "Standard Model of Code" project (a meta-language for representing code structure):

{query}

Please provide academic/industry validation or relevant research."""


def generate_grounded_perplexity_query(client, query: str, verbose: bool = False) -> str:
    """
    Generate a context-grounded query for Perplexity using Gemini Flash.

    This function implements intelligent grounding by:
    1. Loading domain definitions from semantic_models.yaml
    2. Using Gemini Flash to rewrite the query with relevant local context
    3. Producing a well-structured query with clear context/question separation

    Args:
        client: Gemini client instance
        query: Original user query
        verbose: Print debug info if True

    Returns:
        Grounded query string with ---context--- and ---question--- markers
        Falls back to basic framing if Gemini unavailable
    """
    from google.genai import types

    # Load semantic models for domain context
    context_summary = []

    if SEMANTIC_MODELS_PATH.exists():
        try:
            with open(SEMANTIC_MODELS_PATH, 'r') as f:
                models = yaml.safe_load(f) or {}

            # Extract domain definitions
            for domain_name, domain_config in models.items():
                if domain_name == 'antimatter':
                    continue  # Skip antimatter laws for grounding

                scope = domain_config.get('scope', '')
                definitions = domain_config.get('definitions', {})

                if definitions:
                    domain_concepts = []
                    for concept, details in list(definitions.items())[:3]:  # Max 3 per domain
                        desc = details.get('description', '')
                        if desc:
                            domain_concepts.append(f"- {concept}: {desc[:100]}")

                    if domain_concepts:
                        context_summary.append(f"[{domain_name.upper()}]\n" + "\n".join(domain_concepts))
        except Exception as e:
            if verbose:
                print(f"[GROUNDING] Failed to load semantic_models.yaml: {e}", file=sys.stderr)

    # Load key terms from glossary
    glossary_path = PROJECT_ROOT / "standard-model-of-code/docs/GLOSSARY.yaml"
    if glossary_path.exists():
        try:
            with open(glossary_path, 'r') as f:
                glossary = yaml.safe_load(f) or {}

            # Extract terms mentioned in query (relaxed matching)
            query_lower = query.lower()
            relevant_terms = []
            for term, definition in list(glossary.items())[:20]:  # Check up to 20 terms
                term_lower = term.lower().replace('_', ' ')
                if term_lower in query_lower or any(word in query_lower for word in term_lower.split()):
                    if isinstance(definition, dict):
                        desc = definition.get('definition') or definition.get('description', '')
                    else:
                        desc = str(definition)
                    if desc and len(relevant_terms) < 5:
                        relevant_terms.append(f"- {term}: {desc[:150]}")

            if relevant_terms:
                context_summary.append("[GLOSSARY TERMS]\n" + "\n".join(relevant_terms))
        except Exception:
            pass

    # If we have no context or no client, use basic framing
    if not context_summary or not client:
        base_context = """PROJECT: Standard Model of Code
TYPE: Meta-language for representing code structure
KEY CONCEPTS: Atoms (code units), Dimensions (classification axes), Roles (semantic types), Layers (architectural levels)
TOOL: Collider (analysis pipeline)"""
        return f"""---context---
{base_context}

---question---
{query}

Please provide academic/industry validation or relevant research."""

    # Use Gemini Flash to intelligently generate grounded query
    grounding_prompt = f"""You are a research query optimizer. Your task is to rewrite a research query with relevant context from a local codebase, so an external research API (Perplexity) can provide better answers.

LOCAL CODEBASE CONTEXT:
{chr(10).join(context_summary)}

ORIGINAL QUERY: {query}

INSTRUCTIONS:
1. Identify which local concepts are most relevant to this query
2. Create a concise context block (200-400 tokens) that:
   - States the project name and purpose
   - Includes ONLY the most relevant definitions/concepts
   - Omits irrelevant domain details
3. Reformat the query to be clear and specific

OUTPUT FORMAT (use exactly this structure):
---context---
[Your concise context here]

---question---
[The refined research question]

Please provide academic/industry validation or relevant research."""

    try:
        def make_request():
            return client.models.generate_content(
                model=FAST_MODEL,
                contents=grounding_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Low temperature for consistent output
                    max_output_tokens=800
                )
            )

        response = retry_with_backoff(make_request)
        grounded = response.text.strip()

        # Validate output has expected markers
        if "---context---" in grounded and "---question---" in grounded:
            if verbose:
                print(f"[GROUNDING] Successfully grounded query ({len(grounded)} chars)", file=sys.stderr)
            return grounded
        else:
            if verbose:
                print(f"[GROUNDING] Gemini output missing markers, using as-is", file=sys.stderr)
            # Return raw output if it looks reasonable
            if len(grounded) > 100:
                return grounded

    except Exception as e:
        if verbose:
            print(f"[GROUNDING] Gemini Flash failed: {e}", file=sys.stderr)

    # Fallback: build static grounded query
    return f"""---context---
PROJECT: Standard Model of Code (meta-language for representing code structure)
{chr(10).join(context_summary[:2])}

---question---
{query}

Please provide academic/industry validation or relevant research."""


def create_client():
    """Create Gemini client based on configured backend.

    Backend selection (in order of precedence):
    1. GEMINI_BACKEND env var (vertex|aistudio)
    2. Config file (prompts.yaml -> backend)
    3. Default: aistudio (simpler, just needs API key)

    AI Studio: Requires GEMINI_API_KEY env var
    Vertex AI: Requires gcloud auth + project
    """
    # Check for backend override
    backend = BACKEND  # Already resolved from env/config

    if backend == "aistudio":
        # AI Studio (Developer API) - simple API key auth
        api_key = get_doppler_secret(GEMINI_API_KEY_ENV) or os.environ.get(GEMINI_API_KEY_ENV)
        if not api_key:
            print(f"\n{'='*60}")
            print("GEMINI API KEY REQUIRED")
            print(f"{'='*60}")
            print(f"\nBackend: AI Studio (Developer API)")
            print(f"Model: {DEFAULT_MODEL}")
            print()
            print("Setup:")
            print("  1. Get API key from: https://aistudio.google.com/apikey")
            print(f"  2. export {GEMINI_API_KEY_ENV}='your-api-key'")
            print()
            print("Or use Vertex AI backend:")
            print("  export GEMINI_BACKEND=vertex")
            print(f"{'='*60}\n")
            sys.exit(1)

        client = genai.Client(api_key=api_key)
        return client, "aistudio"

    elif backend == "vertex":
        # Vertex AI - GCP enterprise auth
        project_id = _VERTEX_PROJECT or get_gcloud_project()
        if not project_id:
            print("Error: No gcloud project set.")
            print("Run: gcloud config set project <YOUR_PROJECT_ID>")
            print("Or set vertex_project in prompts.yaml")
            sys.exit(1)

        access_token = get_access_token()
        if not access_token:
            print("Error: Could not get access token.")
            print("Run: gcloud auth application-default login")
            sys.exit(1)

        from google.oauth2 import credentials as oauth2_credentials
        creds = oauth2_credentials.Credentials(token=access_token)

        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=_VERTEX_LOCATION,
            credentials=creds
        )

        return client, project_id

    else:
        print(f"Error: Unknown backend '{backend}'. Use 'aistudio' or 'vertex'.")
        sys.exit(1)


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


def _log_turn(role: str, content: str, truncate: int = 500, tokens_in: int = 0, tokens_out: int = 0):
    """Log a turn to stderr and collect for auto-save.

    When SESSION_LOG=1, prints structured turn markers that can be parsed.
    All turns are collected for auto-save at session end.
    """
    global _session_turns, _session_start_time

    timestamp_epoch = time.time()
    timestamp_str = time.strftime('%H:%M:%S')

    # Always collect for auto-save (full content)
    turn_record = {
        "timestamp": timestamp_epoch,
        "timestamp_str": time.strftime('%Y-%m-%d %H:%M:%S'),
        "role": role,
        "content": content,
    }
    if tokens_in or tokens_out:
        turn_record["tokens_in"] = tokens_in
        turn_record["tokens_out"] = tokens_out
    _session_turns.append(turn_record)

    if _session_start_time is None:
        _session_start_time = timestamp_epoch

    # Print to stderr if SESSION_LOG is enabled
    if not SESSION_LOG:
        return

    # Truncate long content for readability in terminal
    display = content if len(content) <= truncate else content[:truncate] + f"... [{len(content) - truncate} more chars]"

    # Color codes
    colors = {
        'user': '\033[92m',      # Green
        'assistant': '\033[94m', # Blue
        'system': '\033[93m',    # Yellow
        'error': '\033[91m',     # Red
    }
    reset = '\033[0m'
    color = colors.get(role, '\033[0m')

    print(f"\n{color}[{timestamp_str}] {role.upper()}{reset}", file=sys.stderr)
    print(f"{display}", file=sys.stderr)


def _save_session_log(model: str = None, total_tokens_in: int = 0, total_tokens_out: int = 0):
    """Auto-save the full session log to a JSON file."""
    global _session_turns, _session_start_time, _session_model

    if not _session_turns:
        return

    # Build session record
    session = {
        "session_start": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(_session_start_time)) if _session_start_time else None,
        "session_end": time.strftime('%Y-%m-%d %H:%M:%S'),
        "model": model or _session_model or "unknown",
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "turn_count": len(_session_turns),
        "turns": _session_turns
    }

    # Save to research/gemini directory
    save_dir = PROJECT_ROOT / "standard-model-of-code" / "docs" / "research" / "gemini" / "sessions"
    save_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    # Get first user query for filename
    first_query = next((t["content"][:50] for t in _session_turns if t["role"] == "user"), "session")
    slug = "".join(c if c.isalnum() else "_" for c in first_query.lower()).strip("_")[:40]
    filename = f"{timestamp}_{slug}.json"

    filepath = save_dir / filename
    with open(filepath, 'w') as f:
        json.dump(session, f, indent=2)

    print(f"  [Session saved: {filepath.relative_to(PROJECT_ROOT)}]", file=sys.stderr)

    # Clear for next session
    _session_turns = []
    _session_start_time = None


def interactive_mode(client, model, context, system_prompt):
    """Run interactive REPL mode with caching support.

    Uses Vertex AI Context Caching if context is large, falling back to history-replay if small or failed.
    When SESSION_LOG=1, logs turns to stderr for real-time visibility.
    """
    if SESSION_LOG:
        _log_turn("system", f"Session started. Model: {model}")

    if not IS_INTERACTIVE_ENV:
        print("Error: Interactive mode requires a TTY.", file=sys.stderr)
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
                _log_turn("system", f"Session ended. {total_input_tokens:,} in, {total_output_tokens:,} out")
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
            _log_turn("user", user_input)

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
            _log_turn("assistant", response.text)

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
            _log_turn("system", f"Session interrupted. {total_input_tokens:,} in, {total_output_tokens:,} out")
            if cache:
                 try:
                     client.caches.delete(name=cache.name)
                 except: pass
            break
        except Exception as e:
            print(f"\nError: {e}")
            _log_turn("error", str(e))


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
            def make_request():
                return client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

            response = retry_with_backoff(make_request)
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

    def make_request():
        return vertex_client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=[Part.from_text(text=prompt)]
        )

    response = retry_with_backoff(make_request)
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
            def make_request():
                return client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

            response = retry_with_backoff(make_request)
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
    parser.add_argument("--tier", choices=["instant", "rag", "long_context", "perplexity", "flash_deep", "deep", "hybrid"], help="Force specific ACI tier (deep = flash_deep = 2M context, hybrid = internal + external)")
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
    # Initialize ACI tracking variables for feedback logging
    aci_decision = None
    aci_start_time = None

    if args.aci:
        if not HAS_ACI:
            print("Error: ACI module not available. Check aci/ directory.", file=sys.stderr)
            sys.exit(1)

        # Analyze and route the query
        force_tier = args.tier if args.tier else ""
        decision = analyze_and_route(args.prompt, force_tier=force_tier)

        # Industrial UI output (BLUE theme)
        if HAS_INDUSTRIAL_UI and GeminiUI is not None:
            ui = GeminiUI()
            ui.header("ADAPTIVE CONTEXT INTELLIGENCE")
            ui.aci_routing(
                tier=decision.tier.value.upper(),
                confidence=0.9,  # Default confidence (ACI doesn't track this yet)
                reason=decision.reasoning or "Auto-routed"
            )
            ui.blank()
            ui.section("QUERY")
            truncated_q = args.prompt[:80] + ('...' if len(args.prompt) > 80 else '')
            print(f"    {truncated_q}")
            ui.blank()
            ui.item("Sets", ', '.join(decision.primary_sets))
            if args.aci_debug:
                ui.blank()
                ui.section("DEBUG")
                print(format_routing_decision(decision), file=sys.stderr)
            ui.divider()
            print()
        else:
            # Fallback plain output
            print(f"\n{'='*60}", file=sys.stderr)
            print("ADAPTIVE CONTEXT INTELLIGENCE (ACI)", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)
            if args.aci_debug:
                print(f"\n{format_routing_decision(decision)}", file=sys.stderr)
            print(f"Query: {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}", file=sys.stderr)
            print(f"Tier:  {decision.tier.value.upper()}", file=sys.stderr)
            print(f"Sets:  {', '.join(decision.primary_sets)}", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)

        # TIER 0: INSTANT - Try to answer from cached truths
        if decision.tier == Tier.INSTANT or decision.use_truths:
            instant_start = time.time()
            truths = load_repo_truths(PROJECT_ROOT)
            if truths:
                instant_answer = answer_from_truths(args.prompt, truths)
                if instant_answer:
                    print(f"[INSTANT] {instant_answer}")
                    print(f"\n(Source: .agent/intelligence/truths/repo_truths.yaml)", file=sys.stderr)
                    # Log to feedback loop
                    if HAS_ACI:
                        from aci.query_analyzer import analyze_query as aci_analyze
                        profile = aci_analyze(args.prompt)
                        log_aci_query(
                            profile=profile,
                            decision=decision,
                            tokens_input=0,  # No API call
                            tokens_output=0,
                            success=True,
                            duration_ms=int((time.time() - instant_start) * 1000)
                        )
                    sys.exit(0)
                elif decision.tier == Tier.INSTANT:
                    print("Could not answer from truths. Falling back to RAG.", file=sys.stderr)
                    decision = analyze_and_route(args.prompt, force_tier="rag")

        # TIER 3: PERPLEXITY - External research
        if decision.tier == Tier.PERPLEXITY:
            print("[PERPLEXITY] External research tier selected.", file=sys.stderr)
            if not HAS_PERPLEXITY:
                print("Perplexity module not available. Falling back to LONG_CONTEXT.", file=sys.stderr)
                decision = analyze_and_route(args.prompt, force_tier="long_context")
            else:
                start_time = time.time()
                try:
                    # Phase 1 MEMBRANE: Clean query only - no internal context injection
                    # Perplexity search is driven by user prompt only. Injecting repo
                    # context pollutes the search and causes hallucinated results.
                    clean_query = prepare_perplexity_query(args.prompt)
                    print(f"[PERPLEXITY] Clean query ({len(clean_query)} chars) - membrane active", file=sys.stderr)
                    print(f"[PERPLEXITY] Executing research query...", file=sys.stderr)
                    result = perplexity_research(clean_query)
                    duration_ms = int((time.time() - start_time) * 1000)

                    # Display results (GREEN theme for Perplexity)
                    if HAS_INDUSTRIAL_UI:
                        from industrial_ui import PerplexityUI as PUI
                        pui = PUI()
                        pui.header("PERPLEXITY RESEARCH")
                        pui.model_info(result.get("model", "sonar-pro"))
                        pui.blank()
                        pui.section("RESPONSE")
                        print()
                        print(result.get("content", "No content returned"))
                        print()

                        # Display citations
                        citations = result.get("citations", [])
                        if citations:
                            pui.citations_section(citations)
                            pui.blank()

                        # Auto-save
                        saved_path = auto_save_research(args.prompt, result, result.get("model", "sonar-pro"))
                        pui.info(f"Saved: {saved_path}")
                        pui.footer()
                    else:
                        # Fallback plain output
                        print("\n" + "=" * 60)
                        print("PERPLEXITY RESEARCH RESULTS")
                        print("=" * 60)
                        print(result.get("content", "No content returned"))

                        # Display citations
                        citations = result.get("citations", [])
                        if citations:
                            print("\n" + "-" * 60)
                            print("CITATIONS:")
                            for i, cite in enumerate(citations, 1):
                                print(f"  [{i}] {cite}")

                        # Auto-save
                        saved_path = auto_save_research(args.prompt, result, result.get("model", "sonar-pro"))
                        print(f"\n[Auto-saved to: {saved_path}]", file=sys.stderr)

                    # Log to feedback loop if available
                    if HAS_ACI:
                        from aci.query_analyzer import analyze_query as aci_analyze
                        profile = aci_analyze(args.prompt)
                        usage = result.get("usage", {})
                        log_aci_query(
                            profile=profile,
                            decision=decision,
                            tokens_input=usage.get("prompt_tokens", 0),
                            tokens_output=usage.get("completion_tokens", 0),
                            success=True,
                            duration_ms=duration_ms
                        )

                    sys.exit(0)
                except Exception as e:
                    print(f"[PERPLEXITY] Error: {e}", file=sys.stderr)
                    print("Falling back to LONG_CONTEXT tier.", file=sys.stderr)
                    decision = analyze_and_route(args.prompt, force_tier="long_context")

        # TIER 4: FLASH_DEEP - Gemini 2.0 Flash with 2M context
        if decision.tier == Tier.FLASH_DEEP:
            print("[FLASH_DEEP] 2M context tier selected - checking for cached context...", file=sys.stderr)
            flash_start = time.time()

            try:
                # STEP 1: Try to get or create a cache for this repo state
                cache_name = get_or_create_cache(str(PROJECT_ROOT), FAST_MODEL)

                # Create Flash client
                flash_client, _ = create_client()
                from google.genai import types

                # STEP 2: Use cached context if available, otherwise fall back to full context
                if cache_name:
                    print(f"[FLASH_DEEP] Using cached context: {cache_name}", file=sys.stderr)

                    # Build query only (context comes from cache)
                    flash_prompt = f"""User query for comprehensive codebase analysis:

{args.prompt}

Please provide a thorough, comprehensive answer based on the full project context available."""

                    def make_cached_request():
                        return flash_client.models.generate_content(
                            model=FAST_MODEL,
                            contents=flash_prompt,
                            config=types.GenerateContentConfig(
                                cached_content=cache_name,
                                temperature=0.7,
                                max_output_tokens=8192  # Allow longer responses for comprehensive queries
                            )
                        )

                    response = retry_with_backoff(make_cached_request)
                    is_cached = True
                    estimated_tokens = 0  # Cache size tracking will be in cache registry
                else:
                    print("[FLASH_DEEP] Cache unavailable, building full context...", file=sys.stderr)

                    # Load ALL sets for comprehensive analysis
                    raw_sets = decision.primary_sets or [
                        "pipeline", "theory", "architecture_review",
                        "agent_full", "visualization", "classifiers"
                    ]

                    # Sanitize sets (FLASH_DEEP allows 10 sets for 2M context)
                    valid_set_names = set(analysis_sets.keys())
                    comprehensive_sets, dropped_sets = sanitize_sets(
                        raw_sets, valid_set_names, max_sets=10
                    )
                    if dropped_sets:
                        print(f"[FLASH_DEEP] Dropped invalid sets: {dropped_sets}", file=sys.stderr)

                    # Collect all files from all sets
                    all_files = []
                    all_patterns = []
                    for set_name in comprehensive_sets:
                        set_def = analysis_sets.get(set_name, {})
                        all_patterns.extend(set_def.get('patterns', []))
                        for cf in set_def.get('critical_files', []):
                            full_path = PROJECT_ROOT / cf
                            if full_path.exists():
                                all_files.append(str(full_path))
                        # Handle includes
                        for inc in set_def.get('includes', []):
                            inc_def = analysis_sets.get(inc, {})
                            all_patterns.extend(inc_def.get('patterns', []))

                    # Resolve glob patterns
                    all_patterns = list(set(all_patterns))  # dedupe
                    for pattern in all_patterns:
                        full_pattern = str(PROJECT_ROOT / pattern)
                        import glob as glob_module
                        matches = glob_module.glob(full_pattern, recursive=True)
                        all_files.extend([m for m in matches if Path(m).is_file()])

                    all_files = list(set(all_files))  # dedupe
                    print(f"[FLASH_DEEP] Loading {len(all_files)} files from {len(comprehensive_sets)} sets", file=sys.stderr)

                    # Build massive context
                    context_parts = []
                    total_chars = 0
                    max_chars = MAX_FLASH_DEEP_TOKENS * 4  # ~4 chars per token

                    for fpath in sorted(all_files):
                        if total_chars >= max_chars:
                            break
                        try:
                            content = read_file_content(fpath)
                            rel_path = Path(fpath).relative_to(PROJECT_ROOT)
                            file_block = f"\n{'='*60}\nFILE: {rel_path}\n{'='*60}\n{content}\n"
                            context_parts.append(file_block)
                            total_chars += len(file_block)
                        except Exception:
                            pass

                    context = "\n".join(context_parts)
                    estimated_tokens = len(context) // 4
                    print(f"[FLASH_DEEP] Context: {estimated_tokens:,} tokens (~{len(context):,} chars)", file=sys.stderr)

                    # Build prompt with full context
                    flash_prompt = f"""You are analyzing a comprehensive snapshot of the Standard Model of Code project.
You have access to {len(all_files)} files totaling ~{estimated_tokens:,} tokens.

COMPREHENSIVE CODEBASE CONTEXT:
{context}

{'='*60}
USER QUERY:
{args.prompt}

Please provide a thorough, comprehensive answer using the full context available."""

                    def make_request():
                        return flash_client.models.generate_content(
                            model=FAST_MODEL,
                            contents=flash_prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.7,
                                max_output_tokens=8192  # Allow longer responses for comprehensive queries
                            )
                        )

                    response = retry_with_backoff(make_request)
                    is_cached = False

                flash_result = response.text
                duration_ms = int((time.time() - flash_start) * 1000)

                # Display results
                print("\n" + "=" * 60)
                cache_note = " (cached)" if is_cached else ""
                print(f"FLASH_DEEP ANALYSIS ({FAST_MODEL}){cache_note}")
                if estimated_tokens > 0:
                    print(f"Context: {estimated_tokens:,} tokens")
                print("=" * 60)
                print(flash_result)

                # Auto-save
                saved_path = auto_save_gemini_response(args.prompt, flash_result, FAST_MODEL, "flash_deep")
                if saved_path:
                    print(f"\n[Auto-saved: {saved_path}]", file=sys.stderr)

                print(f"\n[FLASH_DEEP completed in {duration_ms/1000:.1f}s]", file=sys.stderr)

                # Log ACI feedback
                if HAS_ACI:
                    try:
                        from aci.query_analyzer import analyze_query as aci_analyze
                        flash_profile = aci_analyze(args.prompt)
                        usage = getattr(response, 'usage_metadata', None)
                        log_aci_query(
                            profile=flash_profile,
                            decision=decision,
                            tokens_input=getattr(usage, 'prompt_token_count', estimated_tokens) if usage else estimated_tokens,
                            tokens_output=getattr(usage, 'candidates_token_count', 0) if usage else 0,
                            success=True,
                            duration_ms=duration_ms
                        )
                    except Exception as log_err:
                        print(f"[FLASH_DEEP] ACI logging skipped: {log_err}", file=sys.stderr)

                sys.exit(0)

            except Exception as e:
                print(f"[FLASH_DEEP] Error: {e}", file=sys.stderr)
                print("Falling back to LONG_CONTEXT tier.", file=sys.stderr)
                decision = analyze_and_route(args.prompt, force_tier="long_context")

        # TIER HYBRID: Internal + External synthesis
        # Sequential: Perplexity (clean query) → Internal synthesis (with evidence)
        if decision.tier == Tier.HYBRID:
            print("[HYBRID] Internal + External synthesis tier selected.", file=sys.stderr)

            # Get valid set names for sanitization
            valid_set_names = set(analysis_sets.keys())

            # Sanitize sets BEFORE any processing
            sanitized_sets, dropped_sets = sanitize_sets(
                decision.primary_sets, valid_set_names, max_sets=5
            )
            if dropped_sets:
                print(f"[HYBRID] Dropped invalid sets: {dropped_sets}", file=sys.stderr)
            if sanitized_sets != decision.primary_sets:
                print(f"[HYBRID] Using sanitized sets: {sanitized_sets}", file=sys.stderr)

            # Build internal context from sanitized sets
            merged_patterns = []
            merged_critical = []
            for set_name in sanitized_sets:
                set_def = analysis_sets.get(set_name, {})
                merged_patterns.extend(set_def.get('patterns', []))
                merged_critical.extend(set_def.get('critical_files', []))
                for inc in set_def.get('includes', []):
                    inc_def = analysis_sets.get(inc, {})
                    merged_patterns.extend(inc_def.get('patterns', []))

            # Collect files
            hybrid_files = list_local_files(PROJECT_ROOT, list(set(merged_patterns)), None)
            if len(hybrid_files) > args.max_files:
                hybrid_files = hybrid_files[:args.max_files]

            # Build context
            hybrid_context, _ = build_context_from_files(
                hybrid_files, PROJECT_ROOT,
                with_line_numbers=True,
                critical_files=list(set(merged_critical)),
                positional_strategy='front-load'
            )

            # Phase 1: External research (CLEAN QUERY ONLY - membrane)
            external_evidence = ""
            if HAS_PERPLEXITY:
                try:
                    clean_query = prepare_perplexity_query(args.prompt)
                    print(f"[HYBRID] External phase: Perplexity query ({len(clean_query)} chars)", file=sys.stderr)

                    result = perplexity_research(clean_query, model="sonar-pro")
                    if isinstance(result, dict):
                        external_evidence = result.get('content', '')
                    else:
                        external_evidence = str(result)

                    if external_evidence:
                        print(f"[HYBRID] External evidence retrieved ({len(external_evidence)} chars)", file=sys.stderr)
                except Exception as e:
                    print(f"[HYBRID] External phase failed: {e}", file=sys.stderr)
                    external_evidence = ""
            else:
                print("[HYBRID] Perplexity not available, proceeding with internal only", file=sys.stderr)

            # Phase 2: Internal synthesis with external evidence
            extra_context = ""
            if external_evidence.strip():
                extra_context = "=== EXTERNAL_EVIDENCE (Perplexity) ===\n" + external_evidence.strip()

            # Create client and execute unified analysis
            hybrid_client, _ = create_client()

            result = execute_analysis(
                client=hybrid_client,
                query=args.prompt,
                context=hybrid_context,
                model=args.model,
                mode=args.mode,
                extra_context=extra_context if extra_context else None,
                tier="HYBRID",
                sets=sanitized_sets,
            )

            # Output result
            print(result['text'])
            sys.exit(0)

        # TIER 1 & 2: RAG and LONG_CONTEXT - Continue with normal flow
        # Override args.set with ACI-selected sets
        # Store ACI decision for later feedback logging
        aci_decision = decision
        aci_start_time = time.time()

        # Sanitize sets before processing (Phase 1: deterministic)
        if decision.primary_sets and not args.set:
            valid_set_names = set(analysis_sets.keys())
            sanitized_sets, dropped_sets = sanitize_sets(
                decision.primary_sets, valid_set_names, max_sets=5
            )
            if dropped_sets:
                print(f"[ACI] Dropped invalid sets: {dropped_sets}", file=sys.stderr)

            # Use sanitized sets
            decision.primary_sets[:] = sanitized_sets

        if decision.primary_sets and not args.set:
            # ACI returns multiple sets - merge them into a dynamic composite
            if len(decision.primary_sets) == 1:
                args.set = decision.primary_sets[0]
                print(f"ACI auto-selected set: {args.set}", file=sys.stderr)
            else:
                # Create a dynamic merged set from all ACI-selected sets
                merged_patterns = []
                merged_critical = []
                for set_name in decision.primary_sets:
                    set_def = analysis_sets.get(set_name, {})
                    merged_patterns.extend(set_def.get('patterns', []))
                    merged_critical.extend(set_def.get('critical_files', []))
                    # Also handle includes
                    for inc in set_def.get('includes', []):
                        inc_def = analysis_sets.get(inc, {})
                        merged_patterns.extend(inc_def.get('patterns', []))

                # Create dynamic set in memory
                analysis_sets['_aci_merged'] = {
                    'description': f"ACI merged: {', '.join(decision.primary_sets)}",
                    'patterns': list(set(merged_patterns)),  # dedupe
                    'critical_files': list(set(merged_critical)),
                    'max_tokens': 200000,
                    'positional_strategy': 'front-load'
                }
                args.set = '_aci_merged'
                print(f"ACI merged sets: {', '.join(decision.primary_sets)}", file=sys.stderr)

        # Inject agent context if needed (when using single set)
        if decision.inject_agent and args.set and not args.set.startswith('_aci_'):
            if not args.set.startswith("agent_"):
                # Merge agent sets with current set
                agent_patterns = []
                for agent_set in ['agent_kernel', 'agent_tasks']:
                    if agent_set in analysis_sets:
                        agent_patterns.extend(analysis_sets[agent_set].get('patterns', []))

                current_set = analysis_sets.get(args.set, {})
                analysis_sets['_aci_with_agent'] = {
                    'description': f"ACI: {args.set} + agent context",
                    'patterns': agent_patterns + current_set.get('patterns', []),
                    'critical_files': current_set.get('critical_files', []),
                    'max_tokens': 200000,
                    'positional_strategy': current_set.get('positional_strategy', 'front-load')
                }
                args.set = '_aci_with_agent'
                print(f"ACI injected agent context", file=sys.stderr)

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

        _log_turn("user", args.prompt or "")
        print("\n--- Analyzing ---", file=sys.stderr)

        def make_request():
            return client.models.generate_content(
                model=args.model,
                contents=[Part.from_text(text=full_prompt)]
            )

        try:
            response = retry_with_backoff(make_request)
            _log_turn("assistant", response.text or "")
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

                # Log to ACI feedback loop for LONG_CONTEXT tier
                if args.aci and HAS_ACI and aci_decision is not None:
                    try:
                        from aci.query_analyzer import analyze_query as aci_analyze
                        profile = aci_analyze(args.prompt)
                        duration_ms = int((time.time() - aci_start_time) * 1000) if aci_start_time else 0
                        log_aci_query(
                            profile=profile,
                            decision=aci_decision,
                            tokens_input=input_tokens,
                            tokens_output=output_tokens,
                            success=True,
                            duration_ms=duration_ms
                        )
                    except Exception:
                        pass  # Don't fail on feedback logging errors

                # Auto-save full session log
                _save_session_log(model=args.model, total_tokens_in=input_tokens, total_tokens_out=output_tokens)

        except Exception as e:
            print(f"Error: {e}")
            _save_session_log(model=args.model)  # Save even on error
            sys.exit(1)


if __name__ == "__main__":
    main()
