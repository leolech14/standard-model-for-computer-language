#!/usr/bin/env python3
"""
Purity Detector — Wraps bandit for HOW dimension detection.

Detects side effects, I/O operations, and impurity markers.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class PurityIssue:
    """A detected purity/side-effect issue."""
    file_path: str
    line_number: int
    issue_type: str  # file_io, network, eval, mutation
    severity: str    # high, medium, low
    confidence: str  # high, medium, low
    description: str


class PurityDetector:
    """
    Detects function purity and side effects using bandit + heuristics.
    """
    
    # Bandit test IDs that indicate side effects
    SIDE_EFFECT_TESTS = {
        "B101",  # assert_used
        "B102",  # exec_used
        "B103",  # set_bad_file_permissions
        "B108",  # hardcoded_temp_file
        "B110",  # try_except_pass
        "B304",  # insecure_transport (network)
        "B310",  # urllib_urlopen (network)
        "B311",  # random (impure)
        "B320",  # xml parsing (I/O)
        "B321",  # ftplib (network)
        "B322",  # input (I/O)
        "B323",  # unverified_context (network)
        "B324",  # hashlib (deterministic but flagged)
        "B403",  # import_pickle (I/O)
        "B404",  # import_subprocess (process I/O)
        "B601",  # paramiko_calls (network)
        "B602",  # subprocess_popen (process I/O)
        "B603",  # subprocess_without_shell (process I/O)
        "B605",  # start_process_with_shell (process I/O)
        "B607",  # start_process_with_partial_path (process I/O)
    }
    
    def __init__(self):
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if bandit is available."""
        try:
            result = subprocess.run(
                ["bandit", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def analyze(self, repo_path: str) -> Dict:
        """
        Analyze a repository for purity violations.
        
        Returns:
            {
                "available": bool,
                "issues": List[PurityIssue],
                "purity_map": Dict[str, bool]  # file -> is_pure
            }
        """
        if not self.available:
            return self._fallback_analysis(repo_path)
        
        try:
            # Run bandit in JSON mode
            output_file = Path(repo_path) / ".bandit_output.json"
            
            subprocess.run(
                ["bandit", "-r", repo_path, "-f", "json", "-o", str(output_file)],
                capture_output=True,
                timeout=60
            )
            
            if output_file.exists():
                with open(output_file) as f:
                    bandit_data = json.load(f)
                
                output_file.unlink()  # Clean up
                
                issues = self._parse_bandit_output(bandit_data)
                purity_map = self._build_purity_map(repo_path, issues)
                
                return {
                    "available": True,
                    "issues": issues,
                    "purity_map": purity_map
                }
        
        except Exception as e:
            print(f"⚠️  Purity detection failed: {e}")
            return self._fallback_analysis(repo_path)
    
    def _parse_bandit_output(self, data: Dict) -> List[PurityIssue]:
        """Parse bandit JSON output into structured issues."""
        issues = []
        
        for result in data.get("results", []):
            test_id = result.get("test_id", "")
            
            # Only keep side-effect related tests
            if test_id in self.SIDE_EFFECT_TESTS:
                issue_type = self._categorize_issue(test_id, result.get("issue_text", ""))
                
                issues.append(PurityIssue(
                    file_path=result.get("filename", ""),
                    line_number=result.get("line_number", 0),
                    issue_type=issue_type,
                    severity=result.get("issue_severity", "").lower(),
                    confidence=result.get("issue_confidence", "").lower(),
                    description=result.get("issue_text", "")
                ))
        
        return issues
    
    def _categorize_issue(self, test_id: str, text: str) -> str:
        """Categorize the type of side effect."""
        text_lower = text.lower()
        
        if any(x in text_lower for x in ["file", "open", "read", "write"]):
            return "file_io"
        elif any(x in text_lower for x in ["network", "socket", "url", "http", "ftp"]):
            return "network"
        elif "exec" in text_lower or "eval" in text_lower:
            return "eval"
        elif "subprocess" in text_lower or "process" in text_lower:
            return "process_io"
        else:
            return "mutation"
    
    def _build_purity_map(self, repo_path: str, issues: List[PurityIssue]) -> Dict[str, bool]:
        """
        Build a map of files to purity status.
        
        Returns: {file_path: is_pure}
        """
        # Files with issues are impure
        impure_files = {issue.file_path for issue in issues}
        
        # Map all Python files
        purity_map = {}
        repo = Path(repo_path)
        
        for py_file in repo.rglob("*.py"):
            if any(x in str(py_file) for x in ["__pycache__", ".venv", "venv"]):
                continue
            
            rel_path = str(py_file.relative_to(repo))
            purity_map[rel_path] = rel_path not in impure_files
        
        return purity_map
    
    def _fallback_analysis(self, repo_path: str) -> Dict:
        """
        Heuristic-based purity detection (when bandit unavailable).
        """
        print("⚠️  Using heuristic purity detection (bandit not available)")
        
        purity_map = {}
        repo = Path(repo_path)
        
        for py_file in repo.rglob("*.py"):
            if any(x in str(py_file) for x in ["__pycache__", ".venv", "venv"]):
                continue
            
            try:
                content = py_file.read_text()
                is_pure = self._heuristic_check(content)
                
                rel_path = str(py_file.relative_to(repo))
                purity_map[rel_path] = is_pure
            except:
                pass
        
        return {
            "available": False,
            "issues": [],
            "purity_map": purity_map
        }
    
    def _heuristic_check(self, code: str) -> bool:
        """Simple heuristic: check for common impure patterns."""
        impure_markers = [
            "open(",
            "file(",
            "print(",
            "input(",
            "requests.",
            "urllib.",
            "socket.",
            "os.system",
            "subprocess.",
            "eval(",
            "exec(",
            "global ",
        ]
        
        code_lower = code.lower()
        return not any(marker.lower() in code_lower for marker in impure_markers)


# CLI for testing
if __name__ == "__main__":
    import sys
    
    detector = PurityDetector()
    
    if detector.available:
        print("✅ bandit is available")
    else:
        print("⚠️  bandit not found. Using heuristics. Install: pip install bandit")
    
    # Test on current directory
    result = detector.analyze(".")
    
    print(f"\n📊 Purity Analysis:")
    print(f"   Total files analyzed: {len(result['purity_map'])}")
    print(f"   Pure files: {sum(1 for p in result['purity_map'].values() if p)}")
    print(f"   Impure files: {sum(1 for p in result['purity_map'].values() if not p)}")
    print(f"   Issues found: {len(result['issues'])}")
    
    if result['issues']:
        print("\n⚠️  Top Purity Issues:")
        for issue in result['issues'][:5]:
            print(f"   {issue.file_path}:{issue.line_number} - {issue.issue_type} ({issue.severity})")
