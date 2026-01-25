"""
Precision Context Fetcher - Just-in-time external knowledge acquisition.

When CCI attribution reveals OUR_FAULT gaps (parser blind spots, missing patterns),
this module fetches pinpoint external knowledge from Perplexity SONAR-PRO to
provide actionable guidance for fixing the gap.

Architecture:
    Gap Detector → Gap Profile → Cache Check → Prompt Engineer →
    Perplexity API (sonar-pro) → Guidance Parser → Knowledge Store

Usage:
    from precision_fetcher import PrecisionContextFetcher, GapProfile

    fetcher = PrecisionContextFetcher()
    gap = GapProfile(
        language="javascript",
        missing_atom="LOG.MOD.IIFE",
        context_snippet="(function() { ... })();",
        error_type="MISSING_DETECTION"
    )
    result = await fetcher.resolve_gap(gap)
"""

import os
import json
import hashlib
import time
import asyncio
from typing import List, Optional, Literal
from pathlib import Path
from dataclasses import dataclass, asdict
import httpx
import yaml

# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

ErrorType = Literal["MISSING_DETECTION", "MISCLASSIFICATION", "BOUNDARY_ERROR"]

# =============================================================================
# DATA MODELS (Dataclass-based for broader compatibility)
# =============================================================================

@dataclass
class GapProfile:
    """Defines the specific 'Our Fault' gap detected by CCI."""
    language: str
    missing_atom: str  # e.g., "LOG.MOD.IIFE"
    context_snippet: str  # The raw code we failed to capture
    error_type: ErrorType
    file_path: Optional[str] = None
    start_line: Optional[int] = None

@dataclass
class ActionableGuidance:
    """Structured knowledge returned by Sonar-Pro."""
    pattern_name: str
    detection_regex: Optional[str]
    tree_sitter_query: Optional[str]
    edge_cases: List[str]
    implementation_tips: str
    confidence: float

@dataclass
class ResearchResult:
    gap_id: str
    timestamp: float
    guidance: ActionableGuidance
    source_urls: List[str]

# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================

class FetcherConfig:
    """Manages API keys, rate limits, and model settings."""

    DEFAULT_CONFIG = {
        'model': 'sonar-pro',
        'max_retries': 3,
        'timeout_seconds': 60,
        'temperature': 0.1,  # Low for factual precision
        'cache_ttl_hours': 168,  # 1 week
        'max_monthly_budget_usd': 5.00,
    }

    def __init__(self, config_path: Optional[str] = None):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")

        # Find project root
        self.project_root = self._find_project_root()

        # Default config path
        resolved_config_path: Path
        if config_path is None:
            resolved_config_path = self.project_root / "context-management/config/aci_config.yaml"
        else:
            resolved_config_path = Path(config_path)

        # Load config from YAML if exists
        self.settings = self.DEFAULT_CONFIG.copy()
        if resolved_config_path.exists():
            with open(resolved_config_path) as f:
                aci_config = yaml.safe_load(f)
                if aci_config and 'research' in aci_config:
                    self.settings.update(aci_config['research'])

        # Cache directory
        self.cache_dir = self.project_root / ".agent/intelligence/external_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Usage tracking file
        self.usage_file = self.cache_dir / "usage_tracking.json"

    def _find_project_root(self) -> Path:
        """Walk up to find PROJECT_elements root."""
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            if (parent / "CLAUDE.md").exists():
                return parent
        return Path.cwd()

    @property
    def model(self) -> str:
        return self.settings['model']

    @property
    def max_retries(self) -> int:
        return self.settings['max_retries']

    @property
    def timeout(self) -> int:
        return self.settings['timeout_seconds']

    @property
    def temperature(self) -> float:
        return self.settings['temperature']

# =============================================================================
# RATE LIMITING & BUDGET CONTROL
# =============================================================================

class BudgetController:
    """Simple token-bucket style budget tracking."""

    def __init__(self, config: FetcherConfig):
        self.config = config
        self.usage_file = config.usage_file

    def _load_usage(self) -> dict:
        if self.usage_file.exists():
            try:
                return json.loads(self.usage_file.read_text())
            except json.JSONDecodeError:
                pass
        return {
            'month': time.strftime('%Y-%m'),
            'total_cost': 0.0,
            'query_count': 0
        }

    def _save_usage(self, usage: dict):
        self.usage_file.write_text(json.dumps(usage, indent=2))

    def check_budget(self) -> tuple[bool, float]:
        """Returns (can_proceed, remaining_budget)."""
        usage = self._load_usage()

        # Reset if new month
        current_month = time.strftime('%Y-%m')
        if usage.get('month') != current_month:
            usage = {'month': current_month, 'total_cost': 0.0, 'query_count': 0}
            self._save_usage(usage)

        max_budget = self.config.settings['max_monthly_budget_usd']
        remaining = max_budget - usage['total_cost']
        return remaining > 0, remaining

    def record_query(self, estimated_cost: float = 0.02):
        """Record a query's estimated cost (~$0.02 for sonar-pro)."""
        usage = self._load_usage()
        usage['total_cost'] += estimated_cost
        usage['query_count'] += 1
        self._save_usage(usage)

# =============================================================================
# CORE ENGINE
# =============================================================================

class PrecisionContextFetcher:
    """
    Fetches precision context from Perplexity SONAR-PRO when CCI
    identifies OUR_FAULT gaps (parser blind spots, missing patterns).
    """

    SYSTEM_PROMPT = """
You are a Senior Compiler Engineer and AST Expert specializing in code pattern detection.
Your goal is to provide concrete, implementable details for detecting code patterns.

CONTEXT: The user has a code analysis tool that failed to detect a specific pattern.
They need precise guidance on how to fix their parser/extractor.

OUTPUT FORMAT:
Return ONLY valid JSON matching this exact schema:
{
    "pattern_name": "The standard/canonical name of this pattern",
    "detection_regex": "A Python-safe regex to find this pattern textually (or null if not feasible)",
    "tree_sitter_query": "The S-expression query for Tree-Sitter to capture this node (or null if N/A)",
    "edge_cases": ["List of 3-5 common ways parsing this pattern can fail"],
    "implementation_tips": "Concrete advice for implementing the extractor, including which AST node types to look for",
    "confidence": 0.0 to 1.0 (how confident you are in this guidance)
}

Be specific. Provide real regex patterns and real tree-sitter queries, not placeholders.
"""

    def __init__(self):
        self.config = FetcherConfig()
        self.budget = BudgetController(self.config)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client."""
        if self._client is None:
            if not self.config.api_key:
                raise ValueError(
                    "PERPLEXITY_API_KEY not set. "
                    "Get one at https://perplexity.ai/settings/api"
                )
            self._client = httpx.AsyncClient(
                base_url="https://api.perplexity.ai",
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                timeout=self.config.timeout
            )
        return self._client

    def _get_cache_key(self, gap: GapProfile) -> str:
        """Create deterministic hash for the gap."""
        payload = f"{gap.language}:{gap.missing_atom}:{gap.error_type}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    async def _check_cache(self, cache_key: str) -> Optional[ResearchResult]:
        """Check if we have cached guidance for this gap."""
        cache_file = self.config.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                # Check TTL
                ttl_hours = self.config.settings['cache_ttl_hours']
                if time.time() - data['timestamp'] < ttl_hours * 3600:
                    guidance = ActionableGuidance(**data['guidance'])
                    return ResearchResult(
                        gap_id=data['gap_id'],
                        timestamp=data['timestamp'],
                        guidance=guidance,
                        source_urls=data.get('source_urls', [])
                    )
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        return None

    def _construct_user_prompt(self, gap: GapProfile) -> str:
        """Build the query for the specific gap."""
        location_info = ""
        if gap.file_path:
            location_info = f"\nFILE: {gap.file_path}"
            if gap.start_line:
                location_info += f" (line {gap.start_line})"

        return f"""
TASK: We failed to detect a '{gap.missing_atom}' pattern in {gap.language} code.

ERROR TYPE: {gap.error_type}
{location_info}

CODE SNIPPET THAT WAS MISSED:
```{gap.language}
{gap.context_snippet}
```

REQUIREMENTS:
1. Identify the specific syntax pattern shown in the snippet.
2. Provide the Tree-sitter S-expression query to capture this node type.
3. Provide a fallback regex for when AST parsing fails.
4. List edge cases where this pattern might be confused with similar constructs.
5. Explain the key AST node types involved.
"""

    async def resolve_gap(self, gap: GapProfile) -> ResearchResult:
        """
        Main entry point - fetch context for a gap.

        Args:
            gap: The GapProfile describing what we missed

        Returns:
            ResearchResult with actionable guidance

        Raises:
            ValueError: If API key not set or budget exceeded
            httpx.HTTPError: If API request fails
        """
        cache_key = self._get_cache_key(gap)

        # 1. Cache Layer
        cached = await self._check_cache(cache_key)
        if cached:
            print(f"[PrecisionFetch] Cache hit for {gap.missing_atom}")
            return cached

        # 2. Budget Check
        can_proceed, remaining = self.budget.check_budget()
        if not can_proceed:
            raise ValueError(
                f"Monthly budget exceeded. Remaining: ${remaining:.2f}. "
                "Increase max_monthly_budget_usd in aci_config.yaml"
            )

        print(f"[PrecisionFetch] Querying Sonar-Pro for {gap.missing_atom}...")

        # 3. API Execution
        client = await self._get_client()

        response: Optional[httpx.Response] = None
        for attempt in range(self.config.max_retries):
            try:
                response = await client.post(
                    "/chat/completions",
                    json={
                        "model": self.config.model,
                        "messages": [
                            {"role": "system", "content": self.SYSTEM_PROMPT},
                            {"role": "user", "content": self._construct_user_prompt(gap)}
                        ],
                        "temperature": self.config.temperature
                    }
                )
                response.raise_for_status()
                break
            except httpx.HTTPStatusError as e:
                if attempt < self.config.max_retries - 1 and e.response.status_code >= 500:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise

        # 4. Parse Response
        if response is None:
            raise RuntimeError("Failed to get response after retries")
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]

        # Extract JSON from potential markdown blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        try:
            guidance_data = json.loads(content.strip())
        except json.JSONDecodeError as e:
            print(f"[PrecisionFetch] Warning: Could not parse JSON response: {e}")
            # Create a minimal guidance object
            guidance_data = {
                "pattern_name": gap.missing_atom,
                "detection_regex": None,
                "tree_sitter_query": None,
                "edge_cases": ["Parse error - raw response stored"],
                "implementation_tips": content,  # Store raw response
                "confidence": 0.3
            }

        guidance = ActionableGuidance(**guidance_data)

        result = ResearchResult(
            gap_id=cache_key,
            timestamp=time.time(),
            guidance=guidance,
            source_urls=response_data.get("citations", [])
        )

        # 5. Record Usage
        self.budget.record_query()

        # 6. Write Cache
        cache_file = self.config.cache_dir / f"{cache_key}.json"
        cache_data = {
            'gap_id': result.gap_id,
            'timestamp': result.timestamp,
            'guidance': asdict(result.guidance),
            'source_urls': result.source_urls
        }
        cache_file.write_text(json.dumps(cache_data, indent=2))

        print(f"[PrecisionFetch] Got guidance: {guidance.pattern_name} (confidence: {guidance.confidence})")
        return result

    async def close(self):
        """Clean up HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def fetch_guidance_for_gap(
    language: str,
    missing_atom: str,
    context_snippet: str,
    error_type: ErrorType = "MISSING_DETECTION"
) -> ActionableGuidance:
    """
    Simple async function to fetch guidance for a gap.

    Example:
        guidance = await fetch_guidance_for_gap(
            "javascript",
            "LOG.MOD.IIFE",
            "(function() { console.log('hidden'); })();"
        )
        print(guidance.tree_sitter_query)
    """
    fetcher = PrecisionContextFetcher()
    try:
        gap = GapProfile(
            language=language,
            missing_atom=missing_atom,
            context_snippet=context_snippet,
            error_type=error_type
        )
        result = await fetcher.resolve_gap(gap)
        return result.guidance
    finally:
        await fetcher.close()

def fetch_guidance_sync(
    language: str,
    missing_atom: str,
    context_snippet: str,
    error_type: ErrorType = "MISSING_DETECTION"
) -> ActionableGuidance:
    """Synchronous wrapper for fetch_guidance_for_gap."""
    return asyncio.run(fetch_guidance_for_gap(
        language=language,
        missing_atom=missing_atom,
        context_snippet=context_snippet,
        error_type=error_type
    ))

# =============================================================================
# CLI INTERFACE
# =============================================================================

async def main():
    """Example usage and CLI test."""
    import argparse

    parser = argparse.ArgumentParser(description="Precision Context Fetcher")
    parser.add_argument("--language", default="javascript", help="Language of the code")
    parser.add_argument("--atom", default="LOG.MOD.IIFE", help="Missing atom type")
    parser.add_argument("--snippet", help="Code snippet that was missed")
    parser.add_argument("--test", action="store_true", help="Run with test data")

    args = parser.parse_args()

    if args.test or not args.snippet:
        # Test with IIFE pattern (our known blind spot)
        snippet = """(function() {
    'use strict';

    function initApp() {
        console.log('App initialized');
    }

    window.MyApp = {
        init: initApp
    };
})();"""
    else:
        snippet = args.snippet

    fetcher = PrecisionContextFetcher()

    try:
        gap = GapProfile(
            language=args.language,
            missing_atom=args.atom,
            context_snippet=snippet,
            error_type="MISSING_DETECTION"
        )

        result = await fetcher.resolve_gap(gap)

        print("\n" + "=" * 60)
        print("PRECISION CONTEXT FETCHING RESULT")
        print("=" * 60)
        print(f"\nPattern: {result.guidance.pattern_name}")
        print(f"Confidence: {result.guidance.confidence:.0%}")

        if result.guidance.tree_sitter_query:
            print(f"\nTree-sitter Query:\n{result.guidance.tree_sitter_query}")

        if result.guidance.detection_regex:
            print(f"\nFallback Regex:\n{result.guidance.detection_regex}")

        print(f"\nEdge Cases:")
        for i, case in enumerate(result.guidance.edge_cases, 1):
            print(f"  {i}. {case}")

        print(f"\nImplementation Tips:\n{result.guidance.implementation_tips}")

        if result.source_urls:
            print(f"\nSources:")
            for url in result.source_urls:
                print(f"  - {url}")

    finally:
        await fetcher.close()

if __name__ == "__main__":
    asyncio.run(main())
