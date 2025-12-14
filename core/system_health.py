#!/usr/bin/env python3
"""
🛡️ SYSTEM HEALTH - Mandatory Pre-Flight Checklist
Ensures the environment is ready for Spectrometer analysis.
"""

import sys
import importlib
import platform
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class HealthStatus:
    is_healthy: bool
    checks: List[Tuple[str, bool, str]]  # (Name, Passed, Message)
    warnings: List[str]

class SystemHealth:
    """Validator for system integrity and dependencies."""
    
    REQUIRED_PACKAGES = {
        "tree_sitter": "Core Parsing Engine",
        "tree_sitter_python": "Python Language Support",
        # Optional but recommended
        "tree_sitter_typescript": "TypeScript/JS Support",
        "tree_sitter_go": "Go Support",
        "tree_sitter_java": "Java Support",
    }

    @staticmethod
    def check_all(mode: str = "full") -> HealthStatus:
        checks = []
        warnings = []
        all_passed = True
        
        # 1. Check Python Version
        py_ver = sys.version_info
        if py_ver.major == 3 and py_ver.minor >= 8:
            checks.append(("Python Version", True, f"{platform.python_version()}"))
        else:
            checks.append(("Python Version", False, f"Found {platform.python_version()}, need 3.8+"))
            all_passed = False
            
        # 2. Check Core Bindings
        for pkg, desc in SystemHealth.REQUIRED_PACKAGES.items():
            is_critical = (mode == "full") and (pkg in ["tree_sitter", "tree_sitter_python"])
            
            try:
                importlib.import_module(pkg)
                checks.append((f"{desc} ({pkg})", True, "Installed"))
            except ImportError:
                if not is_critical:
                    checks.append((f"{desc} ({pkg})", False, "Missing (Optional/Skipped)"))
                    warnings.append(f"Missing binding: {pkg} (Mode: {mode})")
                else:
                    checks.append((f"{desc} ({pkg})", False, "MISSING - CRITICAL"))
                    all_passed = False
        
        # 3. File System Check
        try:
            with open(".health_check_tmp", "w") as f:
                f.write("test")
            import os
            os.remove(".health_check_tmp")
            checks.append(("File System Write", True, "Writable"))
        except Exception as e:
            checks.append(("File System Write", False, f"Failed: {e}"))
            all_passed = False
            
        return HealthStatus(is_healthy=all_passed, checks=checks, warnings=warnings)

    @staticmethod
    def print_checklist(mode: str = "full", exit_on_fail: bool = True):
        """Run checks and print ASCII checklist."""
        print(f"\n🛡️  PRE-FLIGHT SYSTEM CHECK (Mode: {mode})")
        print("=" * 60)
        
        status = SystemHealth.check_all(mode)
        
        for name, passed, msg in status.checks:
            icon = "✅" if passed else "❌"
            # Special case for optional missing
            if not passed and ("Optional" in msg or "Skipped" in msg):
                icon = "⚠️ "
            
            print(f"{icon} {name:<30} : {msg}")
            
        print("-" * 60)
        
        if status.warnings:
            print("\n⚠️  WARNINGS:")
            for w in status.warnings:
                print(f"   - {w}")
                
        if not status.is_healthy:
            print("\n❌ SYSTEM UNHEALTHY. ABORTING LAUNCH.")
            print("Please install missing dependencies.")
            if exit_on_fail:
                sys.exit(1)
        else:
            print("🚀 SYSTEM READY. ENGINES IGNITED.\n")

if __name__ == "__main__":
    SystemHealth.print_checklist()
