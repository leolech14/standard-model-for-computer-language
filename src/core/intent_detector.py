#!/usr/bin/env python3
"""
Intent Detector — Wraps LLM Classifier for WHY dimension detection.

Detects:
- Patterns: Factory, Repository, Strategy, Observer, Singleton, etc.
- Roles: Entity, ValueObject, Service, Controller, UseCase (DDD/Clean)
- Smells: God Class, Feature Envy, Long Method, etc.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class IntentAnalysis:
    """Result of intent/pattern analysis for a component."""
    name: str
    file_path: str
    
    # Pattern detection
    detected_pattern: Optional[str] = None  # Factory, Repository, Singleton...
    pattern_confidence: float = 0.0
    
    # Role detection (DDD/Clean)
    detected_role: Optional[str] = None  # Entity, UseCase, Service...
    role_confidence: float = 0.0
    
    # Smell detection
    detected_smells: List[str] = None  # ["GodClass", "FeatureEnvy"]
    smell_severity: float = 0.0
    
    # LLM reasoning
    reasoning: str = ""
    
    def __post_init__(self):
        if self.detected_smells is None:
            self.detected_smells = []


# Known patterns with detection heuristics
PATTERNS = {
    "Factory": {
        "name_hints": ["factory", "create", "make", "build"],
        "returns_new_instance": True,
    },
    "Repository": {
        "name_hints": ["repository", "repo", "store", "dao"],
        "methods": ["save", "find", "delete", "get_by_id"],
    },
    "Service": {
        "name_hints": ["service", "manager", "handler"],
        "has_io": True,
    },
    "Strategy": {
        "interface_pattern": True,
        "name_hints": ["strategy", "policy", "algorithm"],
    },
    "Observer": {
        "name_hints": ["observer", "listener", "subscriber", "watcher"],
        "methods": ["on_", "handle", "notify"],
    },
    "Singleton": {
        "name_hints": ["singleton"],
        "class_methods": ["get_instance", "instance"],
    },
}

# Known smells with detection heuristics
SMELLS = {
    "GodClass": {
        "method_count_threshold": 15,
        "line_count_threshold": 300,
        "dependency_threshold": 10,
    },
    "LongMethod": {
        "line_count_threshold": 50,
    },
    "FeatureEnvy": {
        "external_calls_ratio": 0.6,  # 60%+ calls are to other classes
    },
    "DataClass": {
        "method_ratio": 0.2,  # <20% methods vs fields
    },
}


class IntentDetector:
    """
    Detects patterns, roles, and smells using LLM + heuristics.
    """
    
    def __init__(self, llm_classifier=None):
        self.llm_classifier = llm_classifier
        self.available = llm_classifier is not None
    
    def analyze(self, semantic_ids: List, file_contents: Dict[str, str] = None) -> Dict:
        """
        Analyze semantic IDs for intent.
        
        Args:
            semantic_ids: List of SemanticID objects
            file_contents: Optional dict of {file_path: content} for deeper analysis
            
        Returns:
            {
                "available": bool,
                "analyses": List[IntentAnalysis],
                "patterns_detected": Dict[str, int],
                "smells_detected": Dict[str, int],
            }
        """
        analyses = []
        patterns_count = {}
        smells_count = {}
        
        for sid in semantic_ids:
            analysis = self._analyze_single(sid, file_contents)
            analyses.append(analysis)
            
            # Count patterns
            if analysis.detected_pattern:
                patterns_count[analysis.detected_pattern] = \
                    patterns_count.get(analysis.detected_pattern, 0) + 1
            
            # Count smells
            for smell in analysis.detected_smells:
                smells_count[smell] = smells_count.get(smell, 0) + 1
        
        return {
            "available": True,
            "analyses": analyses,
            "patterns_detected": patterns_count,
            "smells_detected": smells_count,
        }
    
    def _analyze_single(self, sid, file_contents: Dict = None) -> IntentAnalysis:
        """Analyze a single semantic ID for intent."""
        name = sid.name
        props = sid.properties
        file_path = sid.module_path.replace(".", "/") + ".py"
        
        analysis = IntentAnalysis(name=name, file_path=file_path)
        
        # 1. Pattern detection via heuristics
        detected_pattern, pattern_conf = self._detect_pattern_heuristic(name, props)
        analysis.detected_pattern = detected_pattern
        analysis.pattern_confidence = pattern_conf
        
        # 2. Role detection (from existing classification)
        if "type" in props:
            analysis.detected_role = props["type"]
            analysis.role_confidence = props.get("confidence", 50) / 100.0
        
        # 3. Smell detection
        smells = self._detect_smells_heuristic(name, props)
        analysis.detected_smells = smells
        analysis.smell_severity = len(smells) * 0.3  # Simple severity
        
        # 4. Optional: LLM enrichment for low-confidence cases
        if self.llm_classifier and pattern_conf < 0.5:
            llm_result = self._escalate_to_llm(sid, file_contents)
            if llm_result:
                if llm_result.get("pattern"):
                    analysis.detected_pattern = llm_result["pattern"]
                    analysis.pattern_confidence = llm_result.get("confidence", 0.7)
                analysis.reasoning = llm_result.get("reasoning", "")
        
        return analysis
    
    def _detect_pattern_heuristic(self, name: str, props: Dict) -> Tuple[Optional[str], float]:
        """Detect pattern using name-based heuristics."""
        name_lower = name.lower()
        
        for pattern, hints in PATTERNS.items():
            name_hints = hints.get("name_hints", [])
            if any(hint in name_lower for hint in name_hints):
                confidence = 0.7
                
                # Boost confidence if method patterns match
                methods = hints.get("methods", [])
                if methods and any(m in str(props) for m in methods):
                    confidence = 0.9
                
                return pattern, confidence
        
        return None, 0.0
    
    def _detect_smells_heuristic(self, name: str, props: Dict) -> List[str]:
        """Detect code smells using heuristics."""
        smells = []
        
        # God Class detection
        method_count = props.get("methods", 0)
        lines = props.get("lines", 0)
        
        if method_count > SMELLS["GodClass"]["method_count_threshold"]:
            smells.append("GodClass")
        elif lines > SMELLS["GodClass"]["line_count_threshold"]:
            smells.append("GodClass")
        
        # Long Method detection
        if lines > SMELLS["LongMethod"]["line_count_threshold"]:
            smells.append("LongMethod")
        
        return smells
    
    def _escalate_to_llm(self, sid, file_contents: Dict = None) -> Optional[Dict]:
        """Escalate to LLM for intent analysis."""
        if not self.llm_classifier:
            return None
        
        # This would call the existing LLM classifier
        # For now, return None to indicate escalation not performed
        return None


# Enrichment helper function
def _enrich_with_why(engine, semantic_ids: List, intent_data: Dict):
    """
    Enrich semantic IDs with WHY dimension (intent/patterns).
    
    Args:
        engine: LearningEngine instance
        semantic_ids: List of SemanticID objects
        intent_data: Result from IntentDetector.analyze()
    """
    analyses = intent_data.get("analyses", [])
    
    # Build lookup by name
    analysis_by_name = {a.name: a for a in analyses}
    
    for sid in semantic_ids:
        analysis = analysis_by_name.get(sid.name)
        if analysis:
            # Add detected pattern
            if analysis.detected_pattern:
                sid.properties["pattern"] = analysis.detected_pattern
                sid.properties["pattern_confidence"] = analysis.pattern_confidence
            
            # Add detected smells
            if analysis.detected_smells:
                sid.properties["smells"] = ",".join(analysis.detected_smells)
                sid.properties["smell_severity"] = analysis.smell_severity


# CLI for testing
if __name__ == "__main__":
    print("=== Intent Detector Test ===")
    
    detector = IntentDetector()
    
    # Create mock semantic IDs
    class MockSID:
        def __init__(self, name, props):
            self.name = name
            self.properties = props
            self.module_path = "test.module"
    
    test_ids = [
        MockSID("UserRepository", {"methods": 5, "lines": 100}),
        MockSID("OrderFactory", {"methods": 2, "lines": 30}),
        MockSID("GodService", {"methods": 25, "lines": 500}),
        MockSID("SimpleDTO", {"methods": 0, "lines": 10}),
    ]
    
    result = detector.analyze(test_ids)
    
    print(f"\n Patterns Detected: {result['patterns_detected']}")
    print(f" Smells Detected: {result['smells_detected']}")
    
    for a in result['analyses']:
        print(f"\n   {a.name}:")
        print(f"     Pattern: {a.detected_pattern} ({a.pattern_confidence:.1%})")
        print(f"     Smells: {a.detected_smells or 'None'}")
