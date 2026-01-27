"""
Pipeline Package for Collider.

Provides:
- BaseStage: Abstract base class for all pipeline stages
- PipelineManager: Orchestrates stage execution
- create_default_pipeline(): Factory for standard analysis pipeline
- create_full_pipeline(): Factory for complete 27-stage pipeline

The 27-stage Collider pipeline processes codebases through 5 phases:

PHASE 1: EXTRACTION (Stages 0-2)
PHASE 2: ENRICHMENT (Stages 2.5-2.11)
PHASE 3: ANALYSIS (Stages 3-6.8)
PHASE 4: INTELLIGENCE (Stages 7-8.6)
PHASE 5: OUTPUT (Stages 9-12)

Note: Import CodebaseState from data_management directly.
"""

from typing import Dict, Any, Optional, List

from .base_stage import BaseStage
from .manager import PipelineManager
from .stages import STAGE_ORDER


def create_default_pipeline(
    options: Optional[Dict[str, Any]] = None,
    stages: Optional[List[str]] = None,
    hub=None,
) -> PipelineManager:
    """
    Create the default Collider analysis pipeline (5 core stages).

    Args:
        options: Analysis options passed to stages
        stages: Optional list of stage names to include (default: core 5)
        hub: Optional Hub reference for EventBus integration

    Returns:
        PipelineManager configured with selected stages
    """
    from .stages import (
        BaseAnalysisStage,
        StandardModelStage,
        PurposeFieldStage,
        EdgeExtractionStage,
        GraphAnalyticsStage,
    )

    # Default stage registry (core 5 stages)
    all_stages = {
        "base_analysis": BaseAnalysisStage(options),
        "standard_model": StandardModelStage(),
        "purpose_field": PurposeFieldStage(),
        "edge_extraction": EdgeExtractionStage(),
        "graph_analytics": GraphAnalyticsStage(),
    }

    # Default execution order
    default_order = [
        "base_analysis",
        "standard_model",
        "purpose_field",
        "edge_extraction",
        "graph_analytics",
    ]

    # Select stages
    if stages:
        selected = [all_stages[name] for name in stages if name in all_stages]
    else:
        selected = [all_stages[name] for name in default_order]

    return PipelineManager(selected, hub=hub)


def create_full_pipeline(
    options: Optional[Dict[str, Any]] = None,
    stages: Optional[List[str]] = None,
    skip_survey: bool = False,
    skip_ai: bool = True,
    roadmap: Optional[str] = None,
    output_dir: Optional[str] = None,
    hub=None,
) -> PipelineManager:
    """
    Create the complete 27-stage Collider analysis pipeline.

    Args:
        options: Analysis options passed to stages
        stages: Optional list of stage names to include (default: all 27)
        skip_survey: Skip Stage 0 survey
        skip_ai: Skip Stage 11b AI insights (default: True)
        roadmap: Roadmap name for Stage 9 (optional)
        output_dir: Output directory for Stage 12
        hub: Optional Hub reference for EventBus integration

    Returns:
        PipelineManager configured with all 27 stages
    """
    from .stages import (
        # Phase 1: Extraction
        SurveyStage,
        BaseAnalysisStage,
        StandardModelStage,
        # Phase 2: Enrichment
        EcosystemDiscoveryStage,
        DimensionClassificationStage,
        ScopeAnalysisStage,
        ControlFlowStage,
        PatternDetectionStage,
        DataFlowAnalysisStage,
        # Phase 3: Analysis
        PurposeFieldStage,
        OrganellePurposeStage,
        SystemPurposeStage,
        EdgeExtractionStage,
        MarkovMatrixStage,
        KnotDetectionStage,
        GraphAnalyticsStage,
        StatisticalMetricsStage,
        CodomeBoundaryStage,
        # Phase 4: Intelligence
        DataFlowMacroStage,
        PerformancePredictionStage,
        ConstraintValidationStage,
        PurposeIntelligenceStage,
        # Phase 5: Output
        RoadmapEvaluationStage,
        TopologyReasoningStage,
        SemanticCortexStage,
        AIInsightsStage,
        OutputGenerationStage,
    )

    # Full stage registry
    all_stages = {
        # Phase 1: Extraction
        "survey": SurveyStage(skip=skip_survey),
        "base_analysis": BaseAnalysisStage(options),
        "standard_model": StandardModelStage(),
        # Phase 2: Enrichment
        "ecosystem_discovery": EcosystemDiscoveryStage(),
        "dimension_classification": DimensionClassificationStage(),
        "scope_analysis": ScopeAnalysisStage(),
        "control_flow": ControlFlowStage(),
        "pattern_detection": PatternDetectionStage(),
        "data_flow_analysis": DataFlowAnalysisStage(),
        # Phase 3: Analysis
        "purpose_field": PurposeFieldStage(),
        "organelle_purpose": OrganellePurposeStage(),
        "system_purpose": SystemPurposeStage(),
        "edge_extraction": EdgeExtractionStage(),
        "markov_matrix": MarkovMatrixStage(),
        "knot_detection": KnotDetectionStage(),
        "graph_analytics": GraphAnalyticsStage(),
        "statistical_metrics": StatisticalMetricsStage(),
        "codome_boundary": CodomeBoundaryStage(),
        # Phase 4: Intelligence
        "data_flow_macro": DataFlowMacroStage(),
        "performance_prediction": PerformancePredictionStage(),
        "constraint_validation": ConstraintValidationStage(),
        "purpose_intelligence": PurposeIntelligenceStage(),
        # Phase 5: Output
        "roadmap_evaluation": RoadmapEvaluationStage(roadmap_name=roadmap),
        "topology_reasoning": TopologyReasoningStage(),
        "semantic_cortex": SemanticCortexStage(),
        "ai_insights": AIInsightsStage(enabled=not skip_ai),
        "output_generation": OutputGenerationStage(output_dir=output_dir),
    }

    # Select stages
    if stages:
        selected = [all_stages[name] for name in stages if name in all_stages]
    else:
        selected = [all_stages[name] for name in STAGE_ORDER]

    return PipelineManager(selected, hub=hub)


__all__ = [
    "BaseStage",
    "PipelineManager",
    "create_default_pipeline",
    "create_full_pipeline",
    "STAGE_ORDER",
]
