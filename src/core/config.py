
import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Tuple
from pathlib import Path

@dataclass(frozen=True)
class AnalyzerConfig:
    """
    Single Truth Configuration.
    
    This object captures the exact state of the analyzer (rules, taxonomy, parser versions)
    to ensure reproducibility. Its hash should be recorded with every analysis output.
    """
    # Versioning (The Contract)
    taxonomy_version: str = "1.1.0"
    ruleset_version: str = "2025.12.20-Confidence"
    
    # Parser Versions (The Engine)
    # Using tuple of tuples for immutability and hash stability
    parser_versions: Tuple[Tuple[str, str], ...] = field(default_factory=lambda: (
        ("tree-sitter", "0.20+"),
        ("python", "0.20+"),
        ("javascript", "0.20+"),
        ("typescript", "0.20+"),
        ("go", "0.20+"),
        ("java", "0.20+")
    ))
    
    # Runtime Settings
    use_llm: bool = False           # Whether to use LLM for unknown resolution
    llm_model: Optional[str] = None # Model name if use_llm is True
    strict_mode: bool = False       # If True, fail on ambiguity
    auto_learn: bool = True         # Whether to enable discovery engine
    
    @property
    def config_hash(self) -> str:
        """Generate a stable SHA256 hash of the configuration."""
        # Convert to dict
        data = asdict(self)
        
        # Create a canonical JSON representation (sorted keys are crucial)
        # Tuple is naturally ordered in JSON as list, which works for stability
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()
        
    def save(self, path: Path):
        """Save config to a JSON file."""
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2, sort_keys=True)
            
    def __str__(self):
        return f"AnalyzerConfig(ver={self.taxonomy_version}, rules={self.ruleset_version}, hash={self.config_hash[:8]})"
