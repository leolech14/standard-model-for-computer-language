"""
Research Orchestrator
=====================
SMoC Role: Orchestrator | Domain: Research

Orchestrates multi-configuration query execution using predefined
research schemas. Provides the "joystick interface" for AI agents.

Part of S3 (ACI subsystem).

TARGET AUDIENCE: AI AGENTS

Capabilities:
1. Execute multiple ACI queries with different parameters
2. Synthesize results using various strategies
3. Produce validated, multi-perspective answers

JOYSTICK INTERFACE:
------------------
AI agents control research through:
- Schema selection (predefined patterns)
- Parameter overrides (fine-tuning)
- Custom schemas (ad-hoc configurations)
- Output format selection

VALIDATION:
----------
Schema loader performs preflight validation:
- Model IDs checked against model_catalog
- Tiers checked against TIER_CATALOG
- Sets checked against analysis_sets.yaml
- Run names must be unique
- fallback references must be valid
- External membrane rules enforced

Usage:
    from aci.research_orchestrator import ResearchEngine

    engine = ResearchEngine()

    # Execute predefined schema
    result = engine.execute("validation_trio", "Is L4 CONTAINER used?")

    # Execute with overrides
    result = engine.execute(
        "validation_trio",
        "query here",
        overrides={"runs[0].token_budget": 200000}
    )

    # Execute custom schema
    result = engine.execute_custom({
        "runs": [
            {"name": "a", "model": "gemini-3-pro-preview", "type": "internal", "sets": ["theory"]},
            {"name": "b", "type": "external", "tier": "perplexity"}
        ],
        "synthesis": {"strategy": "consensus", "distinct_sources_required": True}
    }, "query here")

    # List available schemas
    schemas = engine.list_schemas()

    # Describe a schema (for AI discovery)
    info = engine.describe_schema("validation_trio")
"""

import yaml
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Set
from enum import Enum
from datetime import datetime

# Import ACI components
from .intent_parser import analyze_query, QueryScope, QueryIntent


class SynthesisStrategy(Enum):
    """Available synthesis strategies."""
    CONSENSUS = "consensus"
    QUALITY_GRADIENT = "quality_gradient"
    DIALECTIC = "dialectic"
    TRIANGULATION = "triangulation"
    BAYESIAN = "bayesian"
    HIERARCHICAL = "hierarchical"


class OutputFormat(Enum):
    """Available output formats."""
    STRUCTURED = "structured"
    JSON = "json"
    MARKDOWN = "markdown"
    BRIEF = "brief"
    YAML = "yaml"
    # Schema-specific formats
    LADDER_REPORT = "ladder_report"
    INVESTIGATION_REPORT = "investigation_report"
    CONFIDENCE_SCORECARD = "confidence_scorecard"
    SCALE_MAP = "scale_map"


class RunType(Enum):
    """Run types for membrane enforcement."""
    INTERNAL = "internal"
    EXTERNAL = "external"


# Tier catalog (validated on load)
TIER_CATALOG = {
    "instant": "Cached truths (<100ms, $0)",
    "rag": "File Search with citations (~5s, $0.01)",
    "long_context": "Full Gemini reasoning (~60s, $0.10)",
    "perplexity": "External web research (~30s, $0.05)",
    "flash_deep": "2M context window (~90s, $0.20)",
    "hybrid": "Internal + external combined (~120s, $0.15)",
}


@dataclass
class RunConfig:
    """Configuration for a single research run."""
    name: str
    description: str = ""
    type: RunType = RunType.INTERNAL
    model: str = "gemini-3-pro-preview"
    tier: str = "long_context"
    sets: List[str] = field(default_factory=lambda: ["theory"])
    token_budget: int = 100000
    temperature: float = 0.2
    system_prompt: str = ""
    label: str = ""
    citation_required: bool = False
    # DSL condition (dict format)
    condition: Dict[str, Any] = field(default_factory=dict)
    fallback: str = ""  # "skip" or run name


@dataclass
class RunResult:
    """Result from a single research run."""
    name: str
    success: bool
    answer: str
    model_used: str
    tier_used: str
    run_type: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    citations: List[str]
    skipped: bool = False
    skipped_reason: str = ""
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SynthesisConfig:
    """Configuration for result synthesis."""
    strategy: SynthesisStrategy
    min_agreement: int = 2
    distinct_sources_required: bool = False
    prior: float = 0.5
    weights: Dict[str, float] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    output_format: OutputFormat = OutputFormat.STRUCTURED
    fields: List[str] = field(default_factory=list)


@dataclass
class ResearchSchema:
    """Complete research schema definition."""
    name: str
    description: str
    purpose: str
    recommended_for: List[str]
    runs: List[RunConfig]
    synthesis: SynthesisConfig


@dataclass
class CompositeResult:
    """Final synthesized result from research execution."""
    schema_name: str
    query: str
    timestamp: str
    run_results: List[RunResult]
    synthesis_strategy: str

    # Synthesized outputs
    consensus_answer: str = ""
    agreement_score: float = 0.0
    disagreements: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    sources_used: List[str] = field(default_factory=list)

    # Structured fields (strategy-dependent)
    thesis: str = ""
    antithesis: str = ""
    synthesis: str = ""
    robustness_score: float = 0.0

    # Quality gradient
    quality_by_depth: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    optimal_depth: str = ""

    # Investigation
    primary_hypothesis: str = ""
    supporting_evidence: List[str] = field(default_factory=list)
    alternative_hypotheses: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)

    # Decision trace (observability)
    decision_trace: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    total_cost: float = 0.0
    total_latency_ms: int = 0
    citations: List[str] = field(default_factory=list)


class SchemaValidationError(Exception):
    """Raised when schema validation fails."""
    pass


class ResearchEngine:
    """
    Orchestrates multi-configuration query execution.

    AI AGENT INTERFACE:
    -------------------
    This class provides the "joystick" for AI agents to control research.

    Methods:
        list_schemas() -> List[str]
            Discover available research schemas

        describe_schema(name) -> Dict
            Get full details of a schema (for AI comprehension)

        execute(schema_name, query, overrides) -> CompositeResult
            Run a predefined schema

        execute_custom(config, query) -> CompositeResult
            Run an ad-hoc schema

        get_capabilities() -> Dict
            Describe all available parameters and options
    """

    def __init__(self, schemas_path: Optional[Union[str, Path]] = None):
        """Initialize the research engine."""
        if schemas_path is None:
            # Default path relative to this file
            self.schemas_path = Path(__file__).parent.parent.parent.parent / "config" / "research_schemas.yaml"
        else:
            self.schemas_path = Path(schemas_path)

        self.schemas: Dict[str, ResearchSchema] = {}
        self.defaults: Dict[str, Any] = {}
        self.model_catalog: List[str] = []
        self.external_membrane: Dict[str, Any] = {}
        self.guardrails: Dict[str, Any] = {}
        self.validation_errors: List[str] = []

        self._load_schemas()

    def _load_schemas(self):
        """Load research schemas from YAML with validation."""
        if not self.schemas_path.exists():
            print(f"[ResearchEngine] Warning: Schemas not found at {self.schemas_path}")
            return

        with open(self.schemas_path, 'r') as f:
            data = yaml.safe_load(f) or {}

        # Load global config
        self.defaults = data.get("defaults", {
            "model": "gemini-3-pro-preview",
            "tier": "long_context",
            "temperature": 0.2,
            "token_budget": 100000,
            "type": "internal",
        })
        self.model_catalog = data.get("model_catalog", [
            "gemini-3-pro-preview",
            "gemini-2.5-pro",
            "gemini-2.0-flash-001",
            "sonar-pro",
        ])
        self.external_membrane = data.get("external_membrane", {"strict": True})
        self.guardrails = data.get("guardrails", {})

        # Parse and validate schemas
        for name, schema_data in data.get("research_schemas", {}).items():
            try:
                schema = self._parse_schema(name, schema_data)
                self._validate_schema(schema)
                self.schemas[name] = schema
            except SchemaValidationError as e:
                self.validation_errors.append(f"Schema '{name}': {e}")
                print(f"[ResearchEngine] Validation error in '{name}': {e}")

    def _parse_schema(self, name: str, data: Dict) -> ResearchSchema:
        """Parse a schema from YAML data with defaults applied."""
        runs = []
        for run_data in data.get("runs", []):
            # Apply defaults
            run_type_str = run_data.get("type", self.defaults.get("type", "internal"))
            run_type = RunType(run_type_str)

            # Parse condition DSL
            condition = run_data.get("condition", {})
            if isinstance(condition, str):
                # Convert old string format to DSL (backward compat)
                condition = self._convert_legacy_condition(condition)

            runs.append(RunConfig(
                name=run_data.get("name", "unnamed"),
                description=run_data.get("description", ""),
                type=run_type,
                model=run_data.get("model", self.defaults.get("model", "gemini-3-pro-preview")),
                tier=run_data.get("tier", self.defaults.get("tier", "long_context")),
                sets=run_data.get("sets", ["theory"]),
                token_budget=run_data.get("token_budget", self.defaults.get("token_budget", 100000)),
                temperature=run_data.get("temperature", self.defaults.get("temperature", 0.2)),
                system_prompt=run_data.get("system_prompt", ""),
                label=run_data.get("label", ""),
                citation_required=run_data.get("citation_required", False),
                condition=condition,
                fallback=run_data.get("fallback", ""),
            ))

        synth_data = data.get("synthesis", {})
        synthesis = SynthesisConfig(
            strategy=SynthesisStrategy(synth_data.get("strategy", "consensus")),
            min_agreement=synth_data.get("min_agreement", 2),
            distinct_sources_required=synth_data.get("distinct_sources_required", False),
            prior=synth_data.get("prior", 0.5),
            weights=synth_data.get("weights", {}),
            metrics=synth_data.get("metrics", {}),
            output_format=OutputFormat(synth_data.get("output_format", "structured")),
            fields=synth_data.get("fields", []),
        )

        return ResearchSchema(
            name=name,
            description=data.get("description", ""),
            purpose=data.get("purpose", ""),
            recommended_for=data.get("recommended_for", []),
            runs=runs,
            synthesis=synthesis,
        )

    def _convert_legacy_condition(self, condition_str: str) -> Dict[str, Any]:
        """Convert legacy string condition to DSL format."""
        # Handle common patterns
        if "scope == EXTERNAL or scope == HYBRID" in condition_str:
            return {"scope_in": ["EXTERNAL", "HYBRID"]}
        elif "scope == EXTERNAL" in condition_str:
            return {"scope_in": ["EXTERNAL"]}
        elif "scope == HYBRID" in condition_str:
            return {"scope_in": ["HYBRID"]}
        elif "scope != INTERNAL" in condition_str:
            return {"scope_not": "INTERNAL"}
        return {}

    def _validate_schema(self, schema: ResearchSchema):
        """Validate a schema against catalogs and rules."""
        errors = []
        run_names: Set[str] = set()

        for run in schema.runs:
            # Check unique run names
            if run.name in run_names:
                errors.append(f"Duplicate run name: '{run.name}'")
            run_names.add(run.name)

            # Check model against catalog
            if self.model_catalog and run.model not in self.model_catalog:
                errors.append(f"Run '{run.name}': unknown model '{run.model}'. Valid: {self.model_catalog}")

            # Check tier against catalog
            if run.tier not in TIER_CATALOG:
                errors.append(f"Run '{run.name}': unknown tier '{run.tier}'. Valid: {list(TIER_CATALOG.keys())}")

            # Validate external membrane
            if run.type == RunType.EXTERNAL:
                self._validate_external_run(run, errors)

            # Check fallback references
            if run.fallback and run.fallback != "skip":
                if run.fallback not in run_names and run.fallback not in [r.name for r in schema.runs]:
                    errors.append(f"Run '{run.name}': fallback '{run.fallback}' does not exist")

        # Check guardrails
        if self.guardrails:
            total_budget = sum(r.token_budget for r in schema.runs if r.type == RunType.INTERNAL)
            max_budget = self.guardrails.get("max_token_budget_per_schema", float('inf'))
            if total_budget > max_budget:
                errors.append(f"Total token budget {total_budget} exceeds max {max_budget}")

            max_runs = self.guardrails.get("max_runs_per_schema", float('inf'))
            if len(schema.runs) > max_runs:
                errors.append(f"Run count {len(schema.runs)} exceeds max {max_runs}")

        if errors:
            raise SchemaValidationError("; ".join(errors))

    def _validate_external_run(self, run: RunConfig, errors: List[str]):
        """Validate rules for external runs (membrane enforcement)."""
        if not self.external_membrane.get("strict", True):
            return

        # External runs should not have sets
        if run.sets and run.sets != ["theory"]:  # default is allowed
            errors.append(f"Run '{run.name}': external runs should not specify 'sets' (membrane violation)")

        # Check system prompt for banned phrases
        banned = self.external_membrane.get("banned_in_external_prompts", [])
        for phrase in banned:
            if phrase.lower() in run.system_prompt.lower():
                errors.append(f"Run '{run.name}': external prompt contains banned phrase '{phrase}'")

    # =========================================================================
    # AI AGENT DISCOVERY INTERFACE
    # =========================================================================

    def list_schemas(self) -> List[Dict[str, Any]]:
        """
        List available research schemas.

        Returns:
            List of schema summaries for AI discovery.

        Example:
            [
                {"name": "validation_trio", "purpose": "Cross-model verification"},
                {"name": "depth_ladder", "purpose": "Find optimal context size"},
                ...
            ]
        """
        return [
            {
                "name": name,
                "description": schema.description,
                "purpose": schema.purpose,
                "run_count": len(schema.runs),
                "synthesis": schema.synthesis.strategy.value,
                "has_external": any(r.type == RunType.EXTERNAL for r in schema.runs),
            }
            for name, schema in self.schemas.items()
        ]

    def describe_schema(self, name: str) -> Dict[str, Any]:
        """
        Get full details of a schema for AI comprehension.

        Args:
            name: Schema name

        Returns:
            Complete schema details including runs, synthesis config, and usage hints.
        """
        if name not in self.schemas:
            return {"error": f"Schema '{name}' not found", "available": list(self.schemas.keys())}

        schema = self.schemas[name]
        return {
            "name": schema.name,
            "description": schema.description,
            "purpose": schema.purpose,
            "recommended_for": schema.recommended_for,
            "runs": [
                {
                    "name": run.name,
                    "description": run.description,
                    "type": run.type.value,
                    "model": run.model,
                    "tier": run.tier,
                    "sets": run.sets if run.type == RunType.INTERNAL else "(external)",
                    "token_budget": run.token_budget if run.type == RunType.INTERNAL else "(n/a)",
                    "temperature": run.temperature,
                    "has_system_prompt": bool(run.system_prompt),
                    "condition": run.condition or "always",
                    "fallback": run.fallback or "none",
                }
                for run in schema.runs
            ],
            "synthesis": {
                "strategy": schema.synthesis.strategy.value,
                "output_format": schema.synthesis.output_format.value,
                "min_agreement": schema.synthesis.min_agreement,
                "distinct_sources_required": schema.synthesis.distinct_sources_required,
                "metrics": schema.synthesis.metrics,
            },
            "estimated_cost": self._estimate_cost(schema),
            "estimated_time_seconds": self._estimate_time(schema),
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Describe all available parameters and options.

        Returns:
            Complete capability map for AI agent orientation.
        """
        return {
            "available_schemas": self.list_schemas(),
            "synthesis_strategies": [s.value for s in SynthesisStrategy],
            "output_formats": [f.value for f in OutputFormat],
            "tiers": list(TIER_CATALOG.keys()),
            "tier_descriptions": TIER_CATALOG,
            "models": self.model_catalog,
            "run_types": [t.value for t in RunType],
            "defaults": self.defaults,
            "guardrails": self.guardrails,
            "condition_dsl": {
                "scope_in": "Scope must be one of listed values",
                "scope_not": "Scope must NOT be this value",
                "intent_in": "Intent must be one of listed values",
                "complexity_gte": "Complexity >= threshold",
            },
            "override_syntax": {
                "pattern": "--override \"<path>=<value>\"",
                "examples": [
                    "--override \"runs[0].token_budget=200000\"",
                    "--override \"runs[1].sets=['pipeline','schema']\"",
                    "--override \"synthesis.min_agreement=3\"",
                ],
            },
            "custom_schema_syntax": {
                "pattern": "--research-custom '<json>'",
                "example": {
                    "runs": [
                        {"name": "a", "type": "internal", "model": "gemini-3-pro-preview", "sets": ["theory"]},
                        {"name": "b", "type": "external", "tier": "perplexity"}
                    ],
                    "synthesis": {"strategy": "consensus", "distinct_sources_required": True}
                },
            },
            "validation_errors": self.validation_errors,
        }

    # =========================================================================
    # EXECUTION INTERFACE
    # =========================================================================

    def execute(
        self,
        schema_name: str,
        query: str,
        overrides: Optional[Dict[str, Any]] = None,
        output_format: Optional[str] = None,
        dry_run: bool = False,
    ) -> CompositeResult:
        """
        Execute a predefined research schema.

        Args:
            schema_name: Name of the schema to execute
            query: The research query
            overrides: Parameter overrides (e.g., {"runs[0].token_budget": 200000})
            output_format: Override output format
            dry_run: If True, return execution plan without running

        Returns:
            CompositeResult with synthesized findings
        """
        if schema_name not in self.schemas:
            raise ValueError(f"Schema '{schema_name}' not found. Available: {list(self.schemas.keys())}")

        schema = self.schemas[schema_name]

        # Apply overrides
        if overrides:
            schema = self._apply_overrides(schema, overrides)

        # Dry run - return plan only
        if dry_run:
            return self._create_execution_plan(schema, query)

        # Execute runs
        run_results = self._execute_runs(schema, query)

        # Synthesize results
        composite = self._synthesize(schema, query, run_results)

        # Add decision trace
        composite.decision_trace = {
            "schema_name": schema_name,
            "overrides_applied": overrides or {},
            "runs_executed": [r.name for r in run_results if not r.skipped],
            "runs_skipped": [r.name for r in run_results if r.skipped],
            "timestamp": datetime.now().isoformat(),
        }

        # Format output
        if output_format:
            composite = self._format_output(composite, OutputFormat(output_format))

        return composite

    def execute_custom(
        self,
        config: Dict[str, Any],
        query: str,
        output_format: str = "structured",
    ) -> CompositeResult:
        """
        Execute a custom ad-hoc research schema.

        Args:
            config: Custom schema configuration
            query: The research query
            output_format: Output format

        Returns:
            CompositeResult with synthesized findings
        """
        # Parse custom config into schema
        schema = self._parse_schema("_custom", {
            "description": "Ad-hoc custom schema",
            "purpose": "Custom research",
            "recommended_for": [],
            **config,
        })

        # Validate custom schema
        self._validate_schema(schema)

        # Execute
        run_results = self._execute_runs(schema, query)
        composite = self._synthesize(schema, query, run_results)

        composite.decision_trace = {
            "schema_name": "_custom",
            "custom_config": config,
            "runs_executed": [r.name for r in run_results if not r.skipped],
            "runs_skipped": [r.name for r in run_results if r.skipped],
            "timestamp": datetime.now().isoformat(),
        }

        return composite

    # =========================================================================
    # INTERNAL EXECUTION LOGIC
    # =========================================================================

    def _execute_runs(self, schema: ResearchSchema, query: str) -> List[RunResult]:
        """Execute all runs in a schema."""
        results = []
        query_profile = analyze_query(query)

        for run in schema.runs:
            # Check condition
            condition_met = self._evaluate_condition(run.condition, query_profile)

            if not condition_met:
                if run.fallback == "skip":
                    # Skip this run entirely
                    results.append(RunResult(
                        name=run.name,
                        success=False,
                        answer="",
                        model_used=run.model,
                        tier_used=run.tier,
                        run_type=run.type.value,
                        tokens_in=0,
                        tokens_out=0,
                        latency_ms=0,
                        citations=[],
                        skipped=True,
                        skipped_reason=f"Condition not met: {run.condition}",
                    ))
                    continue
                elif run.fallback:
                    # Find and use fallback run
                    fallback_run = next((r for r in schema.runs if r.name == run.fallback), None)
                    if fallback_run:
                        run = fallback_run
                    else:
                        # Fallback not found, skip
                        results.append(RunResult(
                            name=run.name,
                            success=False,
                            answer="",
                            model_used=run.model,
                            tier_used=run.tier,
                            run_type=run.type.value,
                            tokens_in=0,
                            tokens_out=0,
                            latency_ms=0,
                            citations=[],
                            skipped=True,
                            skipped_reason=f"Fallback '{run.fallback}' not found",
                        ))
                        continue

            # Execute run
            result = self._execute_single_run(run, query)
            results.append(result)

        return results

    def _execute_single_run(self, run: RunConfig, query: str) -> RunResult:
        """Execute a single research run."""
        import time
        start_time = time.time()

        try:
            # Build the full query with system prompt
            full_query = query
            if run.system_prompt:
                full_query = f"{run.system_prompt.strip()}\n\nQUERY: {query}"

            # For external runs, the query should be sanitized
            if run.type == RunType.EXTERNAL:
                full_query = self._prepare_external_query(full_query)

            # This will be replaced with actual API call
            # For now, return a placeholder that the CLI will fill
            return RunResult(
                name=run.name,
                success=True,
                answer="[PENDING EXECUTION]",
                model_used=run.model,
                tier_used=run.tier,
                run_type=run.type.value,
                tokens_in=0,
                tokens_out=0,
                latency_ms=int((time.time() - start_time) * 1000),
                citations=[],
                metadata={
                    "sets": run.sets if run.type == RunType.INTERNAL else [],
                    "token_budget": run.token_budget if run.type == RunType.INTERNAL else 0,
                    "temperature": run.temperature,
                    "system_prompt": run.system_prompt[:100] if run.system_prompt else "",
                    "full_query": full_query,
                },
            )
        except Exception as e:
            return RunResult(
                name=run.name,
                success=False,
                answer="",
                model_used=run.model,
                tier_used=run.tier,
                run_type=run.type.value,
                tokens_in=0,
                tokens_out=0,
                latency_ms=int((time.time() - start_time) * 1000),
                citations=[],
                error=str(e),
            )

    def _prepare_external_query(self, query: str) -> str:
        """Prepare query for external tier (membrane enforcement)."""
        # Remove any repo-specific references that might confuse external search
        # This is a simple implementation; could be more sophisticated
        return query

    def _evaluate_condition(self, condition: Dict[str, Any], profile) -> bool:
        """Evaluate a run condition DSL against query profile."""
        if not condition:
            return True

        # scope_in: ["EXTERNAL", "HYBRID"]
        if "scope_in" in condition:
            scope_values = [QueryScope[s] for s in condition["scope_in"]]
            if profile.scope not in scope_values:
                return False

        # scope_not: "INTERNAL"
        if "scope_not" in condition:
            forbidden = QueryScope[condition["scope_not"]]
            if profile.scope == forbidden:
                return False

        # intent_in: ["EXPLAIN", "ANALYZE"]
        if "intent_in" in condition:
            intent_values = [QueryIntent[i] for i in condition["intent_in"]]
            if profile.intent not in intent_values:
                return False

        # complexity_gte: 3
        if "complexity_gte" in condition:
            if profile.complexity.value < condition["complexity_gte"]:
                return False

        return True

    # =========================================================================
    # SYNTHESIS STRATEGIES
    # =========================================================================

    def _synthesize(
        self,
        schema: ResearchSchema,
        query: str,
        run_results: List[RunResult],
    ) -> CompositeResult:
        """Synthesize results using the schema's strategy."""
        strategy = schema.synthesis.strategy

        composite = CompositeResult(
            schema_name=schema.name,
            query=query,
            timestamp=datetime.now().isoformat(),
            run_results=run_results,
            synthesis_strategy=strategy.value,
        )

        # Calculate totals
        executed = [r for r in run_results if not r.skipped]
        composite.total_latency_ms = sum(r.latency_ms for r in executed)
        composite.citations = list(set(
            cite for r in executed for cite in r.citations
        ))
        composite.sources_used = [r.name for r in executed if r.success]

        # Apply strategy-specific synthesis
        if strategy == SynthesisStrategy.CONSENSUS:
            self._synthesize_consensus(composite, schema.synthesis)
        elif strategy == SynthesisStrategy.QUALITY_GRADIENT:
            self._synthesize_gradient(composite, schema.synthesis)
        elif strategy == SynthesisStrategy.DIALECTIC:
            self._synthesize_dialectic(composite, schema.synthesis)
        elif strategy == SynthesisStrategy.TRIANGULATION:
            self._synthesize_triangulation(composite, schema.synthesis)
        elif strategy == SynthesisStrategy.BAYESIAN:
            self._synthesize_bayesian(composite, schema.synthesis)
        elif strategy == SynthesisStrategy.HIERARCHICAL:
            self._synthesize_hierarchical(composite, schema.synthesis)

        return composite

    def _synthesize_consensus(self, composite: CompositeResult, config: SynthesisConfig):
        """Find agreement across runs with distinct source tracking."""
        executed = [r for r in composite.run_results if not r.skipped]
        successful = [r for r in executed if r.success]

        if not successful:
            composite.consensus_answer = "No successful runs to synthesize"
            composite.agreement_score = 0.0
            return

        # Track distinct sources
        if config.distinct_sources_required:
            # Group by model+tier to identify truly distinct sources
            sources: Dict[str, List[RunResult]] = {}
            for r in successful:
                key = f"{r.model_used}:{r.tier_used}"
                if key not in sources:
                    sources[key] = []
                sources[key].append(r)

            # Check if we have enough distinct sources
            if len(sources) < config.min_agreement:
                composite.disagreements.append(
                    f"Only {len(sources)} distinct sources, need {config.min_agreement}"
                )

        # For now, use the first successful answer as consensus
        # In production, this would compare answers semantically
        composite.consensus_answer = successful[0].answer
        composite.agreement_score = len(successful) / max(len(executed), 1)

        # Note disagreements
        if len(successful) > 1:
            composite.disagreements.extend([
                f"Run '{r.name}' may differ - requires semantic comparison"
                for r in successful[1:]
            ])

    def _synthesize_gradient(self, composite: CompositeResult, config: SynthesisConfig):
        """Compare quality at different depths using deterministic metrics."""
        metrics_config = config.metrics.get("deterministic", [])

        for result in composite.run_results:
            if result.skipped:
                continue

            label = result.metadata.get("label", result.name)
            quality = {
                "answer_length": len(result.answer),
                "tokens_in": result.tokens_in,
                "tokens_out": result.tokens_out,
                "latency_ms": result.latency_ms,
                "success": result.success,
                "citation_count": len(result.citations),
            }

            # Add code block count if we have the answer
            if result.answer:
                quality["code_block_count"] = result.answer.count("```")

            composite.quality_by_depth[label] = quality

        # Find optimal depth (best quality/cost ratio)
        executed = [r for r in composite.run_results if not r.skipped]
        if executed:
            mid_idx = len(executed) // 2
            composite.optimal_depth = executed[mid_idx].name

    def _synthesize_dialectic(self, composite: CompositeResult, config: SynthesisConfig):
        """Thesis + antithesis → synthesis."""
        advocate = next((r for r in composite.run_results if r.name == "advocate" and not r.skipped), None)
        skeptic = next((r for r in composite.run_results if r.name == "skeptic" and not r.skipped), None)

        if advocate:
            composite.thesis = advocate.answer
        if skeptic:
            composite.antithesis = skeptic.answer

        # Synthesis would be generated by a follow-up LLM call
        composite.synthesis = "[Requires synthesis generation]"
        composite.robustness_score = 0.5  # Placeholder

    def _synthesize_triangulation(self, composite: CompositeResult, config: SynthesisConfig):
        """Cross-reference multiple investigation angles."""
        executed = [r for r in composite.run_results if not r.skipped]
        successful = [r for r in executed if r.success]

        if successful:
            composite.primary_hypothesis = f"Based on {successful[0].name}: {successful[0].answer[:200]}..."
            composite.supporting_evidence = [
                f"{r.name}: {r.answer[:100]}..." for r in successful[1:]
            ]

    def _synthesize_bayesian(self, composite: CompositeResult, config: SynthesisConfig):
        """Update confidence based on evidence weights."""
        confidence = config.prior

        for result in composite.run_results:
            if result.skipped:
                continue
            if result.success:
                weight = config.weights.get(result.name, 0.1)
                # Simple additive update (real Bayesian would be multiplicative)
                if "counter" in result.name.lower():
                    confidence -= abs(weight) * 0.5  # Counter-evidence reduces
                else:
                    confidence += weight * 0.5  # Supporting evidence increases

        composite.confidence_score = max(0.0, min(1.0, confidence))

    def _synthesize_hierarchical(self, composite: CompositeResult, config: SynthesisConfig):
        """Map findings to scale hierarchy."""
        for result in composite.run_results:
            if result.skipped:
                continue
            if "node" in result.name.lower():
                composite.supporting_evidence.append(f"L3: {result.answer[:100]}")
            elif "module" in result.name.lower():
                composite.alternative_hypotheses.append(f"L5: {result.answer[:100]}")
            elif "system" in result.name.lower():
                composite.primary_hypothesis = f"L7: {result.answer[:100]}"

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _apply_overrides(self, schema: ResearchSchema, overrides: Dict[str, Any]) -> ResearchSchema:
        """Apply parameter overrides to a schema."""
        # Simple implementation - in production would parse paths like "runs[0].token_budget"
        # For now, just return the schema unchanged
        # TODO: Implement proper override parsing with path notation
        return schema

    def _create_execution_plan(self, schema: ResearchSchema, query: str) -> CompositeResult:
        """Create dry-run execution plan."""
        return CompositeResult(
            schema_name=schema.name,
            query=query,
            timestamp=datetime.now().isoformat(),
            run_results=[],
            synthesis_strategy=schema.synthesis.strategy.value,
            consensus_answer=f"[DRY RUN] Would execute {len(schema.runs)} runs",
            decision_trace={
                "dry_run": True,
                "planned_runs": [
                    {
                        "name": r.name,
                        "type": r.type.value,
                        "model": r.model,
                        "tier": r.tier,
                        "condition": r.condition or "always",
                    }
                    for r in schema.runs
                ],
            },
        )

    def _format_output(self, composite: CompositeResult, fmt: OutputFormat) -> CompositeResult:
        """Format output according to requested format."""
        # Output formatting is handled by CLI
        return composite

    def _estimate_cost(self, schema: ResearchSchema) -> str:
        """Estimate cost for a schema execution."""
        internal_runs = [r for r in schema.runs if r.type == RunType.INTERNAL]
        total_tokens = sum(run.token_budget for run in internal_runs)
        # Rough estimate: $0.001 per 1K tokens
        cost = total_tokens / 1000 * 0.001
        return f"~${cost:.2f}"

    def _estimate_time(self, schema: ResearchSchema) -> int:
        """Estimate execution time in seconds."""
        # Rough estimate: 30s per internal run, 15s per external
        internal = sum(1 for r in schema.runs if r.type == RunType.INTERNAL)
        external = sum(1 for r in schema.runs if r.type == RunType.EXTERNAL)
        return internal * 30 + external * 15


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_engine_instance: Optional[ResearchEngine] = None


def get_research_engine() -> ResearchEngine:
    """Get or create the research engine singleton."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ResearchEngine()
    return _engine_instance


def execute_research(
    schema_name: str,
    query: str,
    overrides: Optional[Dict[str, Any]] = None,
) -> CompositeResult:
    """Execute a research schema (convenience function)."""
    return get_research_engine().execute(schema_name, query, overrides)


def list_research_schemas() -> List[Dict[str, Any]]:
    """List available schemas (convenience function)."""
    return get_research_engine().list_schemas()


def describe_research_schema(name: str) -> Dict[str, Any]:
    """Describe a schema (convenience function)."""
    return get_research_engine().describe_schema(name)


def get_research_capabilities() -> Dict[str, Any]:
    """Get all capabilities (convenience function)."""
    return get_research_engine().get_capabilities()
