"""
Workflow Registry

Tracks standard system workflows (the "big list of lists").
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Workflow:
    """A standard system workflow definition."""
    id: str
    name: str
    description: str
    steps: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    path: Optional[str] = None  # Path to workflow definition file


class WorkflowRegistry:
    """
    Registry for standard system workflows.
    """
    
    _instance: Optional['WorkflowRegistry'] = None
    
    def __init__(self):
        self._workflows: Dict[str, Workflow] = {}
        
    @classmethod
    def get_instance(cls) -> 'WorkflowRegistry':
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def register(self, workflow: Workflow) -> None:
        """Register a new workflow."""
        self._workflows[workflow.id] = workflow
        
    def get(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return self._workflows.get(workflow_id)
        
    def list_all(self) -> List[Workflow]:
        """List all registered workflows."""
        return list(self._workflows.values())
        
    def load_from_directory(self, directory: Path) -> int:
        """
        Load workflows from a directory of markdown files.
        (Future implementation for parsing .agent/workflows)
        """
        # Placeholder for future implementation
        return 0


def get_workflow_registry() -> WorkflowRegistry:
    """Get the workflow registry singleton."""
    return WorkflowRegistry.get_instance()


# =============================================================================
# DEFAULT WORKFLOWS (Populated 2026-01-25)
# =============================================================================

def _register_default_workflows(registry: WorkflowRegistry) -> None:
    """Register the standard pipeline workflows."""

    # Standard Analysis (default CI/CD)
    registry.register(Workflow(
        id="standard",
        name="Standard Analysis",
        description="Default analysis workflow for CI/CD pipelines",
        steps=[
            "survey",              # Stage 0: Define codome boundary
            "tree_sitter_parse",   # Stage 1-2: AST parsing
            "symbol_extraction",   # Stage 3: Extract functions/classes
            "atom_classification", # Stage 4: Map to Periodic Table
            "role_detection",      # Stage 5: Assign semantic roles
            "edge_extraction",     # Stage 6: Build call graph
            "metrics_computation", # Stage 7: Calculate complexity
            "topology_analysis",   # Stage 8: Detect shape
            "graph_construction",  # Stage 9: Build unified graph
            "report_generation",   # Stage 13: Create output.md
            "visualization",       # Stage 14: Generate HTML
        ],
        tags=["default", "ci", "complete"]
    ))

    # Deep Scan (nightly architectural audit)
    registry.register(Workflow(
        id="deep_scan",
        name="Deep Architectural Scan",
        description="Comprehensive analysis including antimatter detection and community analysis",
        steps=[
            "survey",
            "tree_sitter_parse",
            "symbol_extraction",
            "atom_classification",
            "role_detection",
            "edge_extraction",
            "codome_boundaries",   # Stage 6.8: Add synthetic boundary nodes
            "metrics_computation",
            "topology_analysis",
            "temporal_enrichment", # Stage 8.5: Git timestamps
            "purpose_intelligence",# Stage 8.6: Q-scores
            "graph_construction",
            "pagerank",            # Stage 10: Centrality
            "community_detection", # Stage 11: Find clusters
            "antimatter_detection",# Stage 12: Find violations
            "report_generation",
            "visualization",
        ],
        tags=["nightly", "audit", "comprehensive"]
    ))

    # Fast Lint (pre-commit hook)
    registry.register(Workflow(
        id="fast_lint",
        name="Fast Lint Check",
        description="Quick heuristic check for pre-commit hooks",
        steps=[
            "survey",
            "heuristic_classification",  # Skip AST, use naming patterns
            "metrics_computation",
            "report_generation",
        ],
        tags=["fast", "pre-commit", "lint"]
    ))

    # Antimatter Only (specific violation scan)
    registry.register(Workflow(
        id="antimatter",
        name="Antimatter Detection Only",
        description="Targeted scan for God Classes and architectural violations",
        steps=[
            "survey",
            "tree_sitter_parse",
            "symbol_extraction",
            "god_class_detection",
            "antimatter_detection",
            "report_generation",
        ],
        tags=["focused", "violations", "antimatter"]
    ))


# Initialize default workflows on module load
_registry = get_workflow_registry()
_register_default_workflows(_registry)
