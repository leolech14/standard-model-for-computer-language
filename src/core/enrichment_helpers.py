"""
HOW/WHERE Enrichment Methods for LearningEngine.

These helper methods enrich semantic IDs with behavior (HOW) and context (WHERE) data.
"""

def _enrich_with_how(self, semantic_ids: List, purity_data: Dict):
    """
    Enrich semantic IDs with HOW dimension (purity/behavior).
    
    Args:
        semantic_ids: List of SemanticID objects
        purity_data: Result from PurityDetector.analyze()
    """
    if purity_data is None or not purity_data.get("available"):
        print("  ⚠️  Purity detection unavailable, using heuristics")
        purity_data = {}  # Initialize as empty dict to avoid further errors
    
    purity_map = purity_data.get("purity_map", {})
    issues = purity_data.get("issues", [])
    
    # Build issue map: file -> list of issues
    issues_by_file = {}
    for issue in issues:
        file_path = issue.file_path
        if file_path not in issues_by_file:
            issues_by_file[file_path] = []
        issues_by_file[file_path].append(issue)
    
    for sid in semantic_ids:
        # Extract file from module_path
        file_path = sid.module_path.replace(".", "/") + ".py"
        
        # Set purity
        sid.is_pure = purity_map.get(file_path, None)
        
        # Check for async
        sid.is_async = sid.properties.get("async", False)
        
        # Check for side effects
        file_issues = issues_by_file.get(file_path, [])
        sid.has_side_effects = len(file_issues) > 0
        
        # Heuristic: mutating if not pure or has I/O
        sid.is_mutating = not sid.is_pure if sid.is_pure is not None else None


def _enrich_with_where(self, semantic_ids: List, boundary_data: Dict):
    """
    Enrich semantic IDs with WHERE dimension (layer/boundary).
    
    Args:
        semantic_ids: List of SemanticID objects
        boundary_data: Result from BoundaryDetector.analyze()
    """
    if boundary_data is None or not boundary_data.get("available"):
        print("  ⚠️  Boundary detection unavailable, using path inference")
        boundary_data = {}
    
    layer_map = boundary_data.get("layer_map", {})
    violations = boundary_data.get("violations", [])
    
    # Build violation map: source module -> violation
    violations_by_module = {}
    for v in violations:
        violations_by_module[v.source_module] = v
    
    for sid in semantic_ids:
        # Extract file from module_path
        file_path = sid.module_path.replace(".", "/") + ".py"
        
        # Set architectural layer
        sid.architectural_layer = layer_map.get(file_path, "unknown")
        
        # Check if crosses boundary
        module_key = sid.module_path
        sid.crosses_boundary = module_key in violations_by_module


# Re-export WHY enrichment from intent_detector
def _enrich_with_why(engine, semantic_ids: List, intent_data: Dict):
    """
    Enrich semantic IDs with WHY dimension (intent/patterns).
    Delegated to intent_detector module.
    """
    from core.intent_detector import _enrich_with_why as enrich_why
    enrich_why(engine, semantic_ids, intent_data)
