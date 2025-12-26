"""
Universal Classification Engine
Extracted from TreeSitterUniversalEngine to separate concerns.
"""
import re
from typing import Dict, Any, Optional, List
try:
    from core.classification.ddd_mappings import DDD_BASE_CLASS_MAPPINGS
except ImportError:
    try:
        from classification.ddd_mappings import DDD_BASE_CLASS_MAPPINGS
    except ImportError:
        # Fallback for direct execution
        from ddd_mappings import DDD_BASE_CLASS_MAPPINGS
try:
    from core.type_registry import normalize_type
except ImportError:
    try:
        from type_registry import normalize_type
    except ImportError:
        def normalize_type(t): return t

try:
    from core.registry.pattern_repository import get_pattern_repository
except ImportError:
    try:
        from registry.pattern_repository import get_pattern_repository
    except ImportError:
        def get_pattern_repository(): return None


class UniversalClassifier:
    """Classifies code particles based on patterns, paths, and naming conventions."""

    def __init__(self):
        self.pattern_repo = get_pattern_repository()
        # V2: Initialize simplified Atom map (hardcoded for speed, could load from atoms.json)
        self.atom_map = {
            "class": "ORG.AGG.M", # Default Aggregate
            "function": "LOG.FNC.M", # Default Function
            "method": "LOG.FNC.M", # Method
            "variable": "DAT.VAR.A", # Variable
            "interface": "ORG.AGG.M", 
            "enum": "DAT.PRM.A",
        }

    def classify_class_pattern(self, line: str, line_num: int, file_path: str) -> Optional[Dict]:
        """Classify class-like patterns"""
        line_stripped = line.strip()

        # Extract name
        name_match = re.search(r'(class|interface|type)\s+(\w+)', line_stripped)
        if not name_match:
            return None

        class_name = name_match.group(2)

        # Determine particle type by location (strong signal in real-world repos)
        # Ensure path starts with / for consistent substring matching
        normalized_path = file_path.replace('\\', '/').lower()
        if not normalized_path.startswith("/"):
            normalized_path = "/" + normalized_path
        particle_type = None

        if '/domain/' in normalized_path and '/entities/' in normalized_path:
            particle_type = 'Entity'
        elif '/domain/' in normalized_path and '/value_objects/' in normalized_path:
            particle_type = 'ValueObject'
        elif '/usecase/' in normalized_path or '/use_case/' in normalized_path:
            particle_type = 'UseCase'
        elif '/domain/' in normalized_path and '/repositories/' in normalized_path:
            particle_type = 'Repository'
        elif '/infrastructure/' in normalized_path and 'repository' in class_name.lower():
            particle_type = 'RepositoryImpl'
        elif 'BaseModel' in line_stripped or '/schemas/' in normalized_path or '/error_messages/' in normalized_path:
            particle_type = 'DTO'
        elif '/presentation/' in normalized_path and ('/handlers/' in normalized_path or '/api/' in normalized_path):
            particle_type = 'Controller'
        elif '/tests/' in normalized_path or '/test/' in normalized_path:
            particle_type = 'Test'
        elif '/config/' in normalized_path or 'settings' in normalized_path:
            particle_type = 'Configuration'
        elif 'exception' in normalized_path or 'error' in normalized_path:
            particle_type = 'Exception'

        # Determine particle type by naming conventions
        if not particle_type:
            particle_type = self._get_particle_type_by_name(class_name)
        if not particle_type:
            # Try to detect by content patterns
            particle_type = self._detect_by_keywords(line_stripped)

        resolved_type = particle_type or 'Unknown'
        confidence = self._calculate_confidence(class_name, line_stripped) if particle_type else 30.0

        return {
            'type': resolved_type,
            'name': class_name,
            'symbol_kind': 'class',
            'file_path': file_path,
            'line': line_num,
            'confidence': confidence,
            'evidence': line_stripped[:100]
        }

    def classify_function_pattern(self, line: str, line_num: int, file_path: str, language: str) -> Optional[Dict]:
        """Classify function-like patterns"""
        line_stripped = line.strip()

        # Extract name
        func_name = self._extract_function_name(line_stripped, language)
        if not func_name:
            return None

        # Determine particle type
        particle_type = self._get_function_type_by_name(func_name)

        resolved_type = particle_type or 'Unknown'
        confidence = self._calculate_confidence(func_name, line_stripped) if particle_type else 30.0

        return {
            'type': resolved_type,
            'name': func_name,
            'symbol_kind': 'function',
            'file_path': file_path,
            'line': line_num,
            'confidence': confidence,
            'evidence': line_stripped[:100]
        }

    def classify_extracted_symbol(
        self,
        *,
        name: str,
        symbol_kind: str,
        file_path: str,
        line_num: int,
        evidence: str = "",
        parent: str = "",
        base_classes: List[str] = None,
        decorators: List[str] = None,
        # NEW: Lossless capture fields
        end_line: int = 0,
        body_source: str = "",
        params: List[Dict[str, str]] = None,  # [{"name": "x", "type": "int", "default": "0"}]
        return_type: str = "",
        docstring: str = "",
    ) -> Dict[str, Any]:
        evidence_line = (evidence or "").strip()
        base_classes = base_classes or []
        decorators = decorators or []

        # Ensure path starts with / for consistent substring matching (fixes relative path inputs)
        normalized_path = file_path.replace("\\", "/").lower()
        if not normalized_path.startswith("/"):
            normalized_path = "/" + normalized_path
        particle_type: Optional[str] = None
        confidence = 30.0  # Default low confidence
        
        # =============================================================================
        # TIER 0: FRAMEWORK-SPECIFIC OVERRIDES (99% confidence)
        # =============================================================================
        # Pytest / Conftest
        if "conftest.py" in normalized_path:
            if any(d for d in decorators if "fixture" in d) or name == "conftest":
                particle_type = "Configuration"
                confidence = 99.0
            else:
                particle_type = "Test" # Default for things in conftest
                confidence = 80.0
                
        if particle_type is None:
            for d in decorators:
                if "fixture" in d: # pytest.fixture
                    particle_type = "Configuration"
                    confidence = 90.0
                    break
                if "validator" in d.lower(): # pydantic validators, marshmallow
                    particle_type = "Validator"
                    confidence = 90.0
                    break
                if "command" in d.lower(): # click/typer commands
                    particle_type = "Command"
                    confidence = 90.0
                    break
                if d.endswith(".task") or d == "task": # celery.task
                    particle_type = "Job"
                    confidence = 90.0
                    break
                if "router" in d: # fastapi router
                    particle_type = "Controller"
                    confidence = 90.0
                    break

        # =============================================================================
        # TIER 0.5: STRUCTURAL ANCHORS (95% confidence) - "Pseudo-Decorators"
        # =============================================================================
        if particle_type is None and self.pattern_repo is not None:
            # Extract parameter types from params
            if params:
                param_types = [p.get("type", "") for p in params if p.get("type")]
                if param_types:
                    result = self.pattern_repo.classify_by_param_type(param_types)
                    if result and result[0] != "Unknown" and result[1] > 0:
                        particle_type = result[0]
                        confidence = float(result[1])
            
            # Check file path patterns
            if particle_type is None:
                result = self.pattern_repo.classify_by_path(file_path)
                if result and result[0] != "Unknown" and result[1] > 80:
                    particle_type = result[0]
                    confidence = float(result[1])

        # =============================================================================
        # TIER 1: INHERITANCE-BASED DETECTION (99% confidence)
        # =============================================================================
        if symbol_kind in {"class", "interface", "type", "enum"} and base_classes:
            for base in base_classes:
                if base in DDD_BASE_CLASS_MAPPINGS:
                    particle_type = DDD_BASE_CLASS_MAPPINGS[base]
                    confidence = 99.0  # Inheritance = highest confidence
                    break

        # =============================================================================
        # TIER 2: PATH-BASED DETECTION (90% confidence)
        # =============================================================================
        if particle_type is None and symbol_kind in {"class", "interface", "type", "enum"}:
            # Strong location signals (DDD/Clean folders, or UI layers).
            # Strong location signals (DDD/Clean folders, or UI layers).
            # Note: We check for "/segment" (start of segment) to avoid partial matches
            if "/domain/" in normalized_path and "/entities" in normalized_path:
                particle_type = "Entity"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/aggregates" in normalized_path or "/aggregate" in normalized_path):
                particle_type = "AggregateRoot"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/events" in normalized_path or "/event" in normalized_path):
                particle_type = "DomainEvent"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/value_objects" in normalized_path or "/valueobjects" in normalized_path):
                particle_type = "ValueObject"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/services" in normalized_path or "/domain_services" in normalized_path):
                particle_type = "DomainService"
                confidence = 90.0
            elif "/domain/" in normalized_path and "/repositories" in normalized_path:
                particle_type = "Repository"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/commands" in normalized_path or "/command" in normalized_path):
                particle_type = "Command"
                confidence = 90.0
            elif "/domain/" in normalized_path and ("/queries" in normalized_path or "/query" in normalized_path):
                particle_type = "Query"
                confidence = 90.0
            elif ("/application/" in normalized_path or "/usecases/" in normalized_path) and ("usecase" in normalized_path or "interactor" in normalized_path):
                particle_type = "UseCase"
                confidence = 90.0
            elif "/infrastructure/" in normalized_path and "repository" in name.lower():
                particle_type = "RepositoryImpl"
                confidence = 90.0
            elif (
                "/presentation/" in normalized_path
                or "/controllers" in normalized_path
                or "/api" in normalized_path
                or "/ro-finance/src/components" in normalized_path
                or "/ro-finance/src/pages" in normalized_path
            ):
                particle_type = "Controller"
                confidence = 85.0
            elif "BaseModel" in evidence_line or "/schemas" in normalized_path or "/error_messages" in normalized_path:
                particle_type = "DTO"
                confidence = 85.0
            elif "/tests/" in normalized_path or "/test" in normalized_path:
                particle_type = "Test"
                confidence = 80.0
            elif "/config/" in normalized_path or "settings" in normalized_path:
                particle_type = "Configuration"
                confidence = 80.0
            elif "exception" in normalized_path or "error" in normalized_path:
                particle_type = "Exception"
                confidence = 80.0
            elif "/utils/" in normalized_path or "/helpers" in normalized_path or "/common" in normalized_path:
                particle_type = "Utility"
                confidence = 75.0
            elif "/models/" in normalized_path and "/domain/" not in normalized_path:
                particle_type = "DTO"
                confidence = 75.0
            elif "/adapters/" in normalized_path:
                particle_type = "Adapter"
                confidence = 75.0
            elif "/clients/" in normalized_path or "/external/" in normalized_path:
                particle_type = "Client"
                confidence = 75.0
            elif "/gateways/" in normalized_path:
                particle_type = "Gateway"
                confidence = 75.0

        # =============================================================================
        # TIER 2.5: NAMING CONVENTIONS (Explicit Suffixes - High Confidence)
        # =============================================================================
        # Moved upwards because explicit suffixes (e.g. UseCase, Repository) are stronger
        # than learned prefix patterns (e.g. Create -> Factory).
        if particle_type is None and symbol_kind in {"class", "interface", "type", "enum"}:
            particle_type = self._get_particle_type_by_name(name)
            if particle_type:
                confidence = 85.0  # Boost confidence for explicit suffixes

        if symbol_kind in {"function", "method"}:
            # If we get "Class.method", classify primarily by the last segment.
            short_name = name.split(".")[-1] if "." in name else name
            
            if particle_type is None:
                particle_type = self._get_function_type_by_name(short_name)
                if particle_type:
                    confidence = 70.0

            if name == "main" or short_name.startswith("analyze") or short_name.startswith("run_"):
                particle_type = "EntryPoint"
                confidence = 90.0

            if short_name == "__init__":
                particle_type = "Constructor"
                confidence = 90.0

            # UI components: exported PascalCase functions/components
            if particle_type is None and (
                "/ro-finance/src/components/" in normalized_path or "/ro-finance/src/pages/" in normalized_path
            ):
                if short_name[:1].isupper():
                    particle_type = "Controller"
                    confidence = 70.0

        # =============================================================================
        # TIER 3: LEARNED PATTERNS (Weakest - Override only if empty or very low confidence)
        # =============================================================================
        if self.pattern_repo is not None:
            short_name = name.split(".")[-1] if "." in name else name
            
            # Try prefix patterns
            prefix_result = self.pattern_repo.classify_by_prefix(short_name)
            if prefix_result and prefix_result[0] != "Unknown":
                pattern_conf = float(prefix_result[1])
                # Override ONLY if we don't have a strong type yet
                # If we have "UseCase" (85.0) and Pattern says "Factory" (60.0), keep UseCase.
                if particle_type is None or pattern_conf > confidence:
                    particle_type = prefix_result[0]
                    confidence = pattern_conf
            
            # Try suffix patterns
            suffix_result = self.pattern_repo.classify_by_suffix(short_name)
            if suffix_result and suffix_result[0] != "Unknown":
                pattern_conf = float(suffix_result[1])
                if particle_type is None or pattern_conf > confidence:
                    particle_type = suffix_result[0]
                    confidence = pattern_conf

        resolved_type = normalize_type(particle_type or "Unknown")

        particle: Dict[str, Any] = {
            "type": resolved_type,
            "name": name,
            "symbol_kind": symbol_kind if symbol_kind else "unknown",
            "file_path": file_path,
            "line": line_num,
            "end_line": end_line if end_line else line_num,
            "confidence": confidence,
            "evidence": evidence_line[:200],
            # Lossless fields for code regeneration
            "body_source": body_source,
            "docstring": docstring,
            "return_type": return_type,
            "docstring": docstring,
            "return_type": return_type,
        }

        # V2: Derive 8 Dimensions
        particle["dimensions"] = self._derive_dimensions(particle)

        if parent:
            particle["parent"] = parent
        if base_classes:
            particle["base_classes"] = base_classes
        if decorators:
            particle["decorators"] = decorators
        if params:
            particle["params"] = params

        return particle

    def _get_particle_type_by_name(self, name: str) -> Optional[str]:
        """Infer particle type from name suffix/prefix."""
        lower_name = name.lower()
        if lower_name.endswith('entity'): return 'Entity'
        if lower_name.endswith('valueobject'): return 'ValueObject'
        if lower_name.endswith('repository'): return 'Repository'
        if lower_name.endswith('service'): return 'Service'
        if lower_name.endswith('controller'): return 'Controller'
        if lower_name.endswith('dtos') or lower_name.endswith('dto'): return 'DTO'
        if lower_name.endswith('policy'): return 'Policy'
        if lower_name.endswith('exception') or lower_name.endswith('error'): return 'Exception'
        if lower_name.endswith('command'): return 'Command'
        if lower_name.endswith('query'): return 'Query'
        if lower_name.endswith('event'): return 'DomainEvent'
        if lower_name.startswith('test') or lower_name.endswith('test'): return 'Test'
        if lower_name.endswith('aggregate'): return 'AggregateRoot'
        if lower_name.endswith('usecase') or lower_name.endswith('use_case'): return 'UseCase'
        if lower_name.endswith('factory'): return 'Factory'
        if lower_name.endswith('builder'): return 'Builder'
        if lower_name.endswith('adapter'): return 'Adapter'
        if lower_name.endswith('serializer'): return 'Transformer'
        return None

    def _get_function_type_by_name(self, name: str) -> Optional[str]:
        """Infer function type from name prefix."""
        if name.startswith('get_') or name.startswith('find_') or name.startswith('fetch_'): return 'Query'
        if name.startswith('create_') or name.startswith('update_') or name.startswith('delete_') or name.startswith('save_'): return 'Command'
        if name.startswith('validate_') or name.startswith('check_'): return 'Validator'
        if name.startswith('on_') or name.startswith('handle_'): return 'EventHandler'
        if name.startswith('to_') or name.startswith('from_') or name.startswith('convert_'): return 'Transformer'
        if name.startswith('is_') or name.startswith('has_') or name.startswith('can_'): return 'Specification'
        if name.startswith('test_'): return 'Test'
        return None

    def _calculate_confidence(self, name: str, evidence: str) -> float:
        """Calculate confidence score (simplified)."""
        return 70.0  # Baseline confidence for heuristics

    def _detect_by_keywords(self, line: str) -> Optional[str]:
        """Detect type by keywords in the line."""
        # Simple placeholder
        return None

    def _extract_function_name(self, line: str, language: str) -> Optional[str]:
        """Extract function name from declaration line."""
        if language == 'python':
            match = re.search(r'def\s+(\w+)', line)
            return match.group(1) if match else None
        # Add other languages as needed or keep generic regex
        match = re.search(r'(function|func|fn)\s+(\w+)', line)
        return match.group(2) if match else None

    # =============================================================================
    # V2: 8-DIMENSIONAL CLASSIFICATION
    # =============================================================================
    def _derive_dimensions(self, particle: Dict[str, Any]) -> Dict[str, str]:
        """Derive the 8 orthogonal dimensions for a particle."""
        dims = {}
        
        # D1: WHAT (Atom Type)
        # Using simplified mapping based on symbol_kind + role
        kind = particle.get("symbol_kind", "unknown")
        role = particle.get("type", "Unknown")
        
        if role == "Test":
            dims["what"] = "QUALITY.TST.A" # Approximate ID
        elif role == "DTO" or role == "ValueObject":
            dims["what"] = "ORG.AGG.M"
        else:
            dims["what"] = self.atom_map.get(kind, "UNKNOWN")

        # D2: LAYER
        path = particle.get("file_path", "").lower()
        if "/domain/" in path: dims["layer"] = "DOMAIN"
        elif "/application/" in path or "/services/" in path: dims["layer"] = "APPLICATION"
        elif "/infrastructure/" in path or "/adapters/" in path: dims["layer"] = "INFRASTRUCTURE"
        elif "/presentation/" in path or "/api/" in path: dims["layer"] = "PRESENTATION"
        elif "/test" in path: dims["layer"] = "TEST"
        elif "/core/" in path: dims["layer"] = "DOMAIN" # Default core to domain if ambiguous
        else: dims["layer"] = "CROSS_CUTTING" # Default for utils/config

        # D3: ROLE
        dims["role"] = role

        # D4: BOUNDARY
        if dims["layer"] in ["PRESENTATION", "INFRASTRUCTURE"]:
            if role in ["Controller", "Handler"]: dims["boundary"] = "Input"
            elif role in ["Client", "Gateway", "Repository"]: dims["boundary"] = "Output"
            else: dims["boundary"] = "Internal"
        else:
            dims["boundary"] = "Internal"
            
        # D5: STATE
        # Heuristic: Classes are stateful, functions are stateless (mostly)
        if kind == "class":
            dims["state"] = "Stateful"
        else:
            dims["state"] = "Stateless"
            
        # D6: EFFECT
        # Heuristic: Queries are Read, Commands are Write
        if role in ["Query", "Finder", "Loader", "Getter"]:
            dims["effect"] = "Read"
        elif role in ["Command", "Creator", "Mutator", "Destroyer"]:
            dims["effect"] = "Write"
        elif role in ["Validator", "Transformer", "Utility"]:
            dims["effect"] = "Pure"
        else:
            dims["effect"] = "ReadModify" # Default mixed

        # D7: ACTIVATION
        if role in ["EventHandler", "Listener", "Subscriber"]:
            dims["activation"] = "Event"
        elif role in ["CronJob", "Task"]:
            dims["activation"] = "Time"
        else:
            dims["activation"] = "Direct"

        # D8: LIFETIME
        if kind == "class":
            if role in ["Service", "Repository", "Factory"]:
                dims["lifetime"] = "Global" # Singletons usually
            elif role in ["Controller", "Handler"]:
                dims["lifetime"] = "Session" # Often per-request
            else:
                dims["lifetime"] = "Transient"
        else:
            dims["lifetime"] = "Transient"

        return dims
