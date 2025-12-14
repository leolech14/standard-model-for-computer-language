#!/usr/bin/env python3
"""
🧠 LLM CLASSIFIER — Evidence-Anchored Component Role Inference

This module implements the "escalation layer" for components that can't be 
classified with high confidence by heuristics alone.

Key principle: The LLM is NOT an extractor — it's an evidence-bound annotator.
It can only classify from a closed set of roles and must cite literal evidence.
"""

import json
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from pathlib import Path


# =============================================================================
# CLOSED ROLE SET (The LLM can ONLY choose from these)
# =============================================================================

ALLOWED_ROLES = [
    # Domain Layer
    "Entity",
    "ValueObject", 
    "AggregateRoot",
    "DomainEvent",
    "DomainService",
    "Specification",
    
    # Application Layer
    "UseCase",
    "Command",
    "Query",
    "EventHandler",
    "Policy",
    
    # Infrastructure Layer
    "Repository",
    "RepositoryImpl",
    "Gateway",
    "Client",
    "Adapter",
    "Provider",
    
    # Presentation Layer
    "Controller",
    "Endpoint",
    "View",
    "Presenter",
    
    # Cross-cutting
    "Factory",
    "Builder",
    "Mapper",
    "Converter",
    "Validator",
    "Configuration",
    "Exception",
    "Utility",
    "Test",
    
    # Fallback
    "Unknown",
]


# =============================================================================
# COMPONENT CARD (What we feed the LLM)
# =============================================================================

@dataclass
class ComponentCard:
    """A bounded context packet for LLM classification."""
    node_id: str
    file_path: str
    name: str
    kind: str  # class, function, module
    start_line: int
    end_line: int
    
    # Code content (bounded)
    code_excerpt: str  # max ~200 lines
    signature: str
    docstring: str
    
    # Structural context
    decorators: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    
    # Graph context
    outgoing_edges: List[Dict] = field(default_factory=list)  # calls/uses
    incoming_edges: List[Dict] = field(default_factory=list)  # called by/used by
    
    # Location context
    folder_layer: Optional[str] = None  # inferred from path
    
    # Heuristic pre-classification
    heuristic_role: Optional[str] = None
    heuristic_confidence: float = 0.0
    heuristic_evidence: List[Dict] = field(default_factory=list)


# =============================================================================
# LLM OUTPUT SCHEMA (What we require back)
# =============================================================================

@dataclass
class ClassificationEvidence:
    """A single piece of evidence supporting the classification."""
    evidence_type: str  # import, decorator, base_class, method_shape, naming, docstring, path
    quote: str          # MUST exist verbatim in the provided code
    file: str
    line_start: int
    line_end: int


@dataclass
class ClassificationResult:
    """The LLM's classification output."""
    node_id: str
    role: str  # MUST be in ALLOWED_ROLES
    confidence: float  # 0.0-1.0
    evidence: List[ClassificationEvidence] = field(default_factory=list)
    reasoning: str = ""
    needs_more_context: bool = False
    questions: List[str] = field(default_factory=list)  # What would help classify?


# =============================================================================
# PROMPT TEMPLATE
# =============================================================================

SYSTEM_PROMPT = """You are a precise software architecture classifier. Your job is to identify the architectural role of code components.

CRITICAL RULES:
1. You can ONLY choose roles from the allowed set below. No custom roles.
2. Every classification MUST include evidence quotes that exist VERBATIM in the provided code.
3. If you cannot find sufficient evidence, set role to "Unknown" and explain what's missing.
4. Never invent dependencies, assume runtime behavior, or guess architectural intent.
5. Confidence must reflect how strong the evidence is, not how confident you feel.

ALLOWED ROLES:
{roles}

CONFIDENCE CALIBRATION:
- 0.9-1.0: Multiple strong signals (decorator + base class + path + naming all agree)
- 0.7-0.89: Clear primary signal (base class or decorator) with supporting context
- 0.5-0.69: Single strong signal OR multiple weak signals
- 0.3-0.49: Suggestive naming or path only
- 0.0-0.29: Insufficient evidence (should usually be "Unknown")

OUTPUT FORMAT:
You must respond with valid JSON matching this schema:
{{
  "node_id": "<from input>",
  "role": "<one of ALLOWED_ROLES>",
  "confidence": <0.0-1.0>,
  "evidence": [
    {{
      "evidence_type": "<import|decorator|base_class|method_shape|naming|docstring|path>",
      "quote": "<EXACT text from code, including whitespace>",
      "file": "<file path>",
      "line_start": <int>,
      "line_end": <int>
    }}
  ],
  "reasoning": "<brief explanation of classification logic>",
  "needs_more_context": <true|false>,
  "questions": ["<optional: what additional context would help?>"]
}}
"""

USER_PROMPT_TEMPLATE = """Classify this component:

NODE ID: {node_id}
FILE: {file_path}
NAME: {name}
KIND: {kind}
LINES: {start_line}-{end_line}

SIGNATURE:
```
{signature}
```

DOCSTRING:
```
{docstring}
```

DECORATORS: {decorators}
BASE CLASSES: {base_classes}
IMPORTS: {imports}

CODE EXCERPT:
```{language}
{code_excerpt}
```

FOLDER LAYER (heuristic): {folder_layer}
OUTGOING EDGES (calls/uses): {outgoing_edges}
INCOMING EDGES (called by): {incoming_edges}

HEURISTIC PRE-CLASSIFICATION:
- Role guess: {heuristic_role}
- Confidence: {heuristic_confidence}
- Evidence: {heuristic_evidence}

Please classify this component and provide evidence-anchored justification.
"""


def format_system_prompt() -> str:
    """Format the system prompt with the allowed roles."""
    roles_str = "\n".join(f"  - {role}" for role in ALLOWED_ROLES)
    return SYSTEM_PROMPT.format(roles=roles_str)


def format_user_prompt(card: ComponentCard, language: str = "python") -> str:
    """Format the user prompt from a ComponentCard."""
    return USER_PROMPT_TEMPLATE.format(
        node_id=card.node_id,
        file_path=card.file_path,
        name=card.name,
        kind=card.kind,
        start_line=card.start_line,
        end_line=card.end_line,
        signature=card.signature or "(no signature)",
        docstring=card.docstring or "(no docstring)",
        decorators=", ".join(card.decorators) or "(none)",
        base_classes=", ".join(card.base_classes) or "(none)",
        imports=", ".join(card.imports[:10]) or "(none)",  # Limit
        language=language,
        code_excerpt=card.code_excerpt,
        folder_layer=card.folder_layer or "(unknown)",
        outgoing_edges=json.dumps(card.outgoing_edges[:5], indent=2) if card.outgoing_edges else "[]",
        incoming_edges=json.dumps(card.incoming_edges[:5], indent=2) if card.incoming_edges else "[]",
        heuristic_role=card.heuristic_role or "Unknown",
        heuristic_confidence=f"{card.heuristic_confidence:.2f}",
        heuristic_evidence=json.dumps(card.heuristic_evidence, indent=2) if card.heuristic_evidence else "[]",
    )


# =============================================================================
# EVIDENCE VALIDATOR (Rejects hallucinations)
# =============================================================================

class EvidenceValidator:
    """
    Validates LLM classification outputs.
    
    Key job: ensure every quoted evidence ACTUALLY EXISTS in the provided code.
    """
    
    def __init__(self, strict: bool = True):
        self.strict = strict
        self.validation_errors: List[str] = []
    
    def validate(self, result: Dict, card: ComponentCard) -> ClassificationResult:
        """
        Validate and parse LLM output.
        
        Returns a ClassificationResult, potentially downgraded to Unknown
        if validation fails.
        """
        self.validation_errors = []
        
        # 1. Check role is in allowed set
        role = result.get("role", "Unknown")
        if role not in ALLOWED_ROLES:
            self.validation_errors.append(f"Invalid role: {role}")
            role = "Unknown"
        
        # 2. Check confidence is valid
        confidence = result.get("confidence", 0.0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            self.validation_errors.append(f"Invalid confidence: {confidence}")
            confidence = 0.0
        
        # 3. Validate each evidence quote exists in code
        validated_evidence = []
        for ev in result.get("evidence", []):
            quote = ev.get("quote", "")
            normalized_quote = self._normalize_whitespace(quote)
            normalized_code = self._normalize_whitespace(card.code_excerpt)
            
            if normalized_quote and normalized_quote in normalized_code:
                validated_evidence.append(ClassificationEvidence(
                    evidence_type=ev.get("evidence_type", "unknown"),
                    quote=quote,
                    file=ev.get("file", card.file_path),
                    line_start=ev.get("line_start", 0),
                    line_end=ev.get("line_end", 0),
                ))
            else:
                self.validation_errors.append(f"Quote not found in code: '{quote[:50]}...'")
        
        # 4. If no valid evidence and strict mode, downgrade to Unknown
        if self.strict and not validated_evidence and role != "Unknown":
            self.validation_errors.append("No valid evidence; downgrading to Unknown")
            role = "Unknown"
            confidence = min(confidence, 0.25)
        
        # 5. Clip confidence if evidence is weak
        if len(validated_evidence) == 0:
            confidence = min(confidence, 0.25)
        elif len(validated_evidence) == 1:
            confidence = min(confidence, 0.7)
        
        return ClassificationResult(
            node_id=result.get("node_id", card.node_id),
            role=role,
            confidence=confidence,
            evidence=validated_evidence,
            reasoning=result.get("reasoning", ""),
            needs_more_context=result.get("needs_more_context", False),
            questions=result.get("questions", []),
        )
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace for comparison."""
        return " ".join(text.split())
    
    def get_validation_report(self) -> Dict:
        """Get validation error report."""
        return {
            "valid": len(self.validation_errors) == 0,
            "errors": self.validation_errors,
        }


# =============================================================================
# CONFIDENCE FORMULA (Tunable heuristics)
# =============================================================================

class ConfidenceCalculator:
    """
    Calculates classification confidence from multiple signals.
    
    The formula is designed to be:
    1. Conservative (bias toward lower confidence)
    2. Evidence-weighted (more signals = more confidence)
    3. Tunable (weights can be adjusted)
    """
    
    # Signal weights (tune these based on empirical accuracy)
    WEIGHTS = {
        "decorator": 0.35,      # @repository, @controller are very strong
        "base_class": 0.30,     # Inheriting from Repository is strong
        "path_pattern": 0.15,   # /domain/entities/ is suggestive
        "naming": 0.10,         # UserRepository, CreateUserUseCase
        "method_shape": 0.05,   # execute(), handle(), to_dict()
        "imports": 0.05,        # from sqlalchemy, from fastapi
    }
    
    # Penalty factors
    CONFLICT_PENALTY = 0.3      # Multiple signals disagree
    SINGLE_SIGNAL_CAP = 0.65    # Max confidence with only one signal type
    NO_SIGNAL_CAP = 0.25        # Max confidence with no signals
    
    def calculate(self, evidence: List[Dict]) -> float:
        """
        Calculate confidence from evidence list.
        
        Each evidence item should have:
        - type: decorator, base_class, path_pattern, naming, method_shape, imports
        - strength: 0.0-1.0 (how strong this particular instance is)
        - role_suggested: what role this evidence points to
        """
        if not evidence:
            return 0.0
        
        # Group evidence by type
        by_type: Dict[str, List[Dict]] = {}
        for ev in evidence:
            ev_type = ev.get("type", "unknown")
            if ev_type not in by_type:
                by_type[ev_type] = []
            by_type[ev_type].append(ev)
        
        # Calculate weighted score
        total_score = 0.0
        for ev_type, items in by_type.items():
            weight = self.WEIGHTS.get(ev_type, 0.02)
            # Take the strongest item for each type
            max_strength = max(item.get("strength", 0.5) for item in items)
            total_score += weight * max_strength
        
        # Normalize to 0-1
        max_possible = sum(self.WEIGHTS.values())
        normalized = total_score / max_possible if max_possible > 0 else 0.0
        
        # Apply caps
        signal_types = len(by_type)
        if signal_types == 0:
            return min(normalized, self.NO_SIGNAL_CAP)
        elif signal_types == 1:
            return min(normalized, self.SINGLE_SIGNAL_CAP)
        
        # Check for conflicting signals
        roles_suggested = set()
        for items in by_type.values():
            for item in items:
                if "role_suggested" in item:
                    roles_suggested.add(item["role_suggested"])
        
        if len(roles_suggested) > 1:
            # Multiple roles suggested = conflict
            normalized *= (1 - self.CONFLICT_PENALTY)
        
        return min(normalized, 1.0)
    
    def should_escalate_to_llm(self, confidence: float, threshold: float = 0.55) -> bool:
        """Determine if this node should be escalated to LLM classification."""
        return confidence < threshold


# =============================================================================
# CLASSIFICATION PIPELINE
# =============================================================================

class LLMClassifier:
    """
    Orchestrates the hybrid static+LLM classification pipeline.
    """
    
    def __init__(self, llm_client=None, escalation_threshold: float = 0.55):
        self.validator = EvidenceValidator(strict=True)
        self.confidence_calc = ConfidenceCalculator()
        self.escalation_threshold = escalation_threshold
        self.llm_client = llm_client  # Inject your preferred LLM client
        
        # Stats
        self.stats = {
            "total_classified": 0,
            "heuristic_accepted": 0,
            "llm_escalated": 0,
            "llm_succeeded": 0,
            "validation_failures": 0,
            "final_unknown": 0,
        }
    
    def classify(self, card: ComponentCard) -> ClassificationResult:
        """
        Classify a component using the hybrid pipeline.
        
        1. Check if heuristic confidence is high enough
        2. If not, escalate to LLM
        3. Validate LLM output
        4. Return final result
        """
        self.stats["total_classified"] += 1
        
        # Stage 1: Check heuristic confidence
        if card.heuristic_confidence >= self.escalation_threshold:
            self.stats["heuristic_accepted"] += 1
            return ClassificationResult(
                node_id=card.node_id,
                role=card.heuristic_role or "Unknown",
                confidence=card.heuristic_confidence,
                evidence=[
                    ClassificationEvidence(
                        evidence_type=ev.get("type", "unknown"),
                        quote=ev.get("quote", ""),
                        file=card.file_path,
                        line_start=ev.get("line_start", 0),
                        line_end=ev.get("line_end", 0),
                    )
                    for ev in card.heuristic_evidence
                ],
                reasoning="Accepted from heuristics (high confidence)",
            )
        
        # Stage 2: Escalate to LLM
        if self.llm_client is None:
            # No LLM available, return heuristic result with low confidence
            self.stats["final_unknown"] += 1
            return ClassificationResult(
                node_id=card.node_id,
                role=card.heuristic_role or "Unknown",
                confidence=card.heuristic_confidence,
                evidence=[],
                reasoning="LLM escalation not available; using heuristic",
            )
        
        self.stats["llm_escalated"] += 1
        
        try:
            # Call LLM
            system_prompt = format_system_prompt()
            user_prompt = format_user_prompt(card)
            
            llm_response = self.llm_client.classify(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            
            # Parse JSON response
            result_dict = json.loads(llm_response)
            
            # Validate
            validated = self.validator.validate(result_dict, card)
            
            if self.validator.validation_errors:
                self.stats["validation_failures"] += 1
            else:
                self.stats["llm_succeeded"] += 1
            
            if validated.role == "Unknown":
                self.stats["final_unknown"] += 1
            
            return validated
            
        except Exception as e:
            self.stats["validation_failures"] += 1
            self.stats["final_unknown"] += 1
            return ClassificationResult(
                node_id=card.node_id,
                role="Unknown",
                confidence=0.1,
                evidence=[],
                reasoning=f"LLM classification failed: {e}",
            )
    
    def get_stats(self) -> Dict:
        """Get classification statistics."""
        return {
            **self.stats,
            "heuristic_rate": self.stats["heuristic_accepted"] / max(1, self.stats["total_classified"]),
            "llm_success_rate": self.stats["llm_succeeded"] / max(1, self.stats["llm_escalated"]),
            "unknown_rate": self.stats["final_unknown"] / max(1, self.stats["total_classified"]),
        }


# =============================================================================
# OLLAMA INTEGRATION
# =============================================================================

def create_ollama_classifier(model: str = "qwen2.5:7b-instruct", escalation_threshold: float = 0.55) -> LLMClassifier:
    """
    Create an LLMClassifier with Ollama backend.
    
    This is the recommended way to create a classifier for local inference.
    """
    from ollama_client import OllamaClient, OllamaConfig
    
    config = OllamaConfig(model=model)
    client = OllamaClient(config)
    
    return LLMClassifier(llm_client=client, escalation_threshold=escalation_threshold)


# =============================================================================
# CLI DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 LLM CLASSIFIER — Evidence-Anchored Component Role Inference")
    print("=" * 70)
    print()
    
    # Demo: Create a sample component card
    sample_card = ComponentCard(
        node_id="core.user_repo.UserRepository",
        file_path="infrastructure/user_repo.py",
        name="UserRepository",
        kind="class",
        start_line=10,
        end_line=50,
        code_excerpt='''class UserRepository:
    """Repository for User aggregate."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, user: User) -> None:
        self.session.add(user)
        self.session.commit()
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()
''',
        signature="class UserRepository:",
        docstring="Repository for User aggregate.",
        decorators=[],
        base_classes=[],
        imports=["from sqlalchemy.orm import Session", "from domain.user import User"],
        heuristic_role="Unknown",  # Low confidence to trigger LLM
        heuristic_confidence=0.3,
        heuristic_evidence=[
            {"type": "naming", "quote": "UserRepository", "strength": 0.5}
        ],
    )
    
    print("📦 SAMPLE COMPONENT CARD:")
    print("-" * 40)
    print(f"   Name: {sample_card.name}")
    print(f"   Heuristic: {sample_card.heuristic_role} ({sample_card.heuristic_confidence})")
    print()
    
    # Try to use Ollama
    try:
        print("🦙 Attempting Ollama integration...")
        classifier = create_ollama_classifier(model="qwen2.5:7b-instruct")
        
        if classifier.llm_client.is_available():
            print("✅ Ollama connected")
            print("📤 Classifying component (this may take 10-30s)...")
            
            result = classifier.classify(sample_card)
            
            print()
            print("📊 CLASSIFICATION RESULT:")
            print("-" * 40)
            print(f"   Role: {result.role}")
            print(f"   Confidence: {result.confidence:.2%}")
            print(f"   Reasoning: {result.reasoning}")
            print(f"   Evidence: {len(result.evidence)} items")
            for ev in result.evidence:
                print(f"     - [{ev.evidence_type}] \"{ev.quote[:50]}...\"")
            print()
            print("📈 Pipeline Stats:")
            for k, v in classifier.get_stats().items():
                print(f"   {k}: {v}")
        else:
            print("❌ Ollama not available. Run: ollama serve")
    except Exception as e:
        print(f"⚠️ Ollama test failed: {e}")
        print()
        
        # Fallback: demo without LLM
        print("📊 Running without LLM (heuristics only)...")
        classifier = LLMClassifier(llm_client=None, escalation_threshold=0.55)
        result = classifier.classify(sample_card)
        print(f"   Role: {result.role}")
        print(f"   Confidence: {result.confidence:.2%}")
        print(f"   Reasoning: {result.reasoning}")
