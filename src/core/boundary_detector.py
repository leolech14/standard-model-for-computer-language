#!/usr/bin/env python3
"""
Boundary Detector — Wraps import-linter for WHERE dimension detection.

Detects architectural layer violations and boundary crossings.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class BoundaryViolation:
    """A detected boundary violation."""
    source_module: str
    forbidden_module: str
    contract_name: str
    layer_source: str  # domain/application/infrastructure/presentation
    layer_target: str


class BoundaryDetector:
    """
    Detects architectural boundary violations using import-linter.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or ".import-linter.ini"
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if import-linter is available."""
        try:
            result = subprocess.run(
                ["import-linter", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def analyze(self, repo_path: str) -> Dict:
        """
        Analyze a repository for boundary violations.
        
        Returns:
            {
                "available": bool,
                "violations": List[BoundaryViolation],
                "layer_map": Dict[str, str]  # module -> layer
            }
        """
        if not self.available:
            return {
                "available": False,
                "violations": [],
                "layer_map": {}
            }
        
        # Run import-linter
        try:
            result = subprocess.run(
                ["import-linter", "--config", self.config_path],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            violations = self._parse_output(result.stdout)
            layer_map = self._infer_layers(repo_path)
            
            return {
                "available": True,
                "violations": violations,
                "layer_map": layer_map
            }
        
        except Exception as e:
            print(f"⚠️  Boundary detection failed: {e}")
            return {
                "available": False,
                "violations": [],
                "layer_map": {}
            }
    
    def _parse_output(self, output: str) -> List[BoundaryViolation]:
        """Parse import-linter output into structured violations."""
        violations = []
        
        # import-linter output format:
        # "myapp.domain.entities imports myapp.infrastructure.db"
        
        for line in output.split('\n'):
            if 'imports' in line and '->' not in line:
                parts = line.strip().split()
                if len(parts) >= 3:
                    source = parts[0]
                    target = parts[2]
                    
                    violations.append(BoundaryViolation(
                        source_module=source,
                        forbidden_module=target,
                        contract_name="boundary-rule",
                        layer_source=self._extract_layer(source),
                        layer_target=self._extract_layer(target)
                    ))
        
        return violations
    
    def _extract_layer(self, module_path: str) -> str:
        """Extract architectural layer from module path."""
        lower = module_path.lower()
        
        if 'domain' in lower or 'entities' in lower or 'model' in lower:
            return "domain"
        elif 'application' in lower or 'usecase' in lower or 'service' in lower:
            return "application"
        elif 'infrastructure' in lower or 'repository' in lower or 'gateway' in lower:
            return "infrastructure"
        elif 'presentation' in lower or 'api' in lower or 'controller' in lower:
            return "presentation"
        else:
            return "unknown"
    
    def _infer_layers(self, repo_path: str) -> Dict[str, str]:
        """
        Build a map of all Python files to their inferred layer.
        
        Returns: {file_path: layer}
        """
        layer_map = {}
        repo = Path(repo_path)
        
        for py_file in repo.rglob("*.py"):
            if any(x in str(py_file) for x in ["__pycache__", ".venv", "venv"]):
                continue
            
            rel_path = str(py_file.relative_to(repo))
            layer = self._extract_layer(rel_path)
            layer_map[rel_path] = layer
        
        return layer_map


# CLI for testing
if __name__ == "__main__":
    import sys
    
    detector = BoundaryDetector()
    
    if detector.available:
        print("✅ import-linter is available")
    else:
        print("❌ import-linter not found. Install: pip install import-linter")
        sys.exit(1)
    
    # Test on current directory
    result = detector.analyze(".")
    
    print(f"\n📊 Analysis Results:")
    print(f"   Violations: {len(result['violations'])}")
    print(f"   Layer Map size: {len(result['layer_map'])}")
    
    if result['violations']:
        print("\n⚠️  Detected Violations:")
        for v in result['violations'][:5]:
            print(f"   {v.layer_source} → {v.layer_target}: {v.source_module} imports {v.forbidden_module}")
