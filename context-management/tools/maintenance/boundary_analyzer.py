#!/usr/bin/env python3
"""
Boundary Analyzer - PROJECT_elements Internal Organization Validator

Part of the Maintenance Layer. Validates that declared boundaries
(CODOME/CONTEXTOME/DOMAINS) match actual directory structure.

Usage:
    python boundary_analyzer.py                    # Full analysis
    python boundary_analyzer.py --quick            # Quick check (exit code only)
    python boundary_analyzer.py --fix              # Generate fix suggestions
    python boundary_analyzer.py --json             # JSON output for CI
    python boundary_analyzer.py --watch            # Continuous monitoring

Integration:
    - Called by: boot.sh, pre-commit hooks, CI pipeline
    - Outputs to: .agent/intelligence/boundary_analysis.json
    - Logs to: .agent/intelligence/boundary_scan_log.txt
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, field, asdict

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent

# Canonical boundary definitions
REALMS = {
    "PARTICLE": {
        "path": "standard-model-of-code/",
        "description": "Collider engine, atoms, schemas, theory",
        "contains_codome": True,
        "contains_contextome": True,
    },
    "WAVE": {
        "path": "context-management/",
        "description": "AI tools, planning, research",
        "contains_codome": True,
        "contains_contextome": True,
    },
    "OBSERVER": {
        "path": ".agent/",
        "description": "Task registry, intelligence, governance",
        "contains_codome": True,
        "contains_contextome": True,
    },
}

# Declared domains from DOMAINS.md
DECLARED_DOMAINS = {
    "Pipeline": {
        "codome": ["standard-model-of-code/src/core/"],
        "contextome": ["standard-model-of-code/docs/specs/"],
    },
    "Visualization": {
        "codome": ["standard-model-of-code/src/core/viz/"],
        "contextome": ["standard-model-of-code/docs/specs/VISUALIZATION*.md"],
    },
    "Governance": {
        "codome": [".agent/tools/"],
        "contextome": [".agent/registry/", ".agent/specs/"],
    },
    "AI_Tools": {
        "codome": ["context-management/tools/ai/"],
        "contextome": ["context-management/config/"],
    },
    "Theory": {
        "codome": [],  # Theory has no code
        "contextome": ["standard-model-of-code/docs/MODEL.md"],
    },
    "Archive": {
        "codome": ["context-management/tools/archive/"],
        "contextome": ["context-management/tools/archive/config.yaml"],
    },
}

# File type classifications
CODOME_EXTENSIONS = {'.py', '.js', '.ts', '.go', '.rs', '.java', '.css', '.html', '.scm', '.sql', '.sh'}
CONTEXTOME_EXTENSIONS = {'.md', '.yaml', '.yml', '.json'}

# Known directories that should be declared
EXPECTED_DIRECTORIES = {
    "standard-model-of-code/src/",
    "standard-model-of-code/docs/",
    "standard-model-of-code/tools/",
    "standard-model-of-code/schema/",
    "standard-model-of-code/tests/",
    "context-management/tools/",
    "context-management/docs/",
    "context-management/config/",
    ".agent/registry/",
    ".agent/tools/",
    ".agent/specs/",
    ".agent/intelligence/",
}


@dataclass
class BoundaryIssue:
    """A single boundary violation or concern."""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # UNDECLARED, PHANTOM, DRIFT, ORPHAN
    path: str
    message: str
    suggestion: str = ""


@dataclass
class BoundaryReport:
    """Complete boundary analysis report."""
    timestamp: str = ""
    alignment_score: float = 0.0
    total_directories: int = 0
    declared_directories: int = 0
    undeclared_directories: int = 0
    phantom_declarations: int = 0
    issues: List[BoundaryIssue] = field(default_factory=list)
    realms_status: Dict[str, Any] = field(default_factory=dict)
    domains_status: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "alignment_score": self.alignment_score,
            "total_directories": self.total_directories,
            "declared_directories": self.declared_directories,
            "undeclared_directories": self.undeclared_directories,
            "phantom_declarations": self.phantom_declarations,
            "issues": [asdict(i) for i in self.issues],
            "realms_status": self.realms_status,
            "domains_status": self.domains_status,
            "recommendations": self.recommendations,
        }


class BoundaryAnalyzer:
    """Analyzes PROJECT_elements internal organization against declared boundaries."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.root = project_root
        self.report = BoundaryReport(timestamp=datetime.now().isoformat())

    def analyze(self) -> BoundaryReport:
        """Run complete boundary analysis."""
        self._analyze_realms()
        self._analyze_domains()
        self._find_undeclared_directories()
        self._find_phantom_declarations()
        self._check_partition_integrity()
        self._calculate_score()
        self._generate_recommendations()
        return self.report

    def _analyze_realms(self):
        """Check if declared realms exist and contain expected content."""
        for realm_name, realm_info in REALMS.items():
            realm_path = self.root / realm_info["path"]
            exists = realm_path.exists()

            codome_count = 0
            contextome_count = 0

            if exists:
                for f in realm_path.rglob("*"):
                    if f.is_file():
                        if f.suffix in CODOME_EXTENSIONS:
                            codome_count += 1
                        elif f.suffix in CONTEXTOME_EXTENSIONS:
                            contextome_count += 1

            self.report.realms_status[realm_name] = {
                "path": str(realm_info["path"]),
                "exists": exists,
                "codome_files": codome_count,
                "contextome_files": contextome_count,
                "status": "VALID" if exists else "MISSING",
            }

            if not exists:
                self.report.issues.append(BoundaryIssue(
                    severity="CRITICAL",
                    category="PHANTOM",
                    path=str(realm_info["path"]),
                    message=f"Declared realm {realm_name} does not exist",
                    suggestion=f"Create {realm_info['path']} or remove from REALMS declaration",
                ))

    def _analyze_domains(self):
        """Check if declared domains have both codome and contextome components."""
        for domain_name, domain_info in DECLARED_DOMAINS.items():
            codome_exists = []
            contextome_exists = []

            # Check codome paths
            for pattern in domain_info.get("codome", []):
                if "*" in pattern:
                    matches = list(self.root.glob(pattern))
                    codome_exists.extend([str(m.relative_to(self.root)) for m in matches])
                else:
                    path = self.root / pattern
                    if path.exists():
                        codome_exists.append(pattern)

            # Check contextome paths
            for pattern in domain_info.get("contextome", []):
                if "*" in pattern:
                    matches = list(self.root.glob(pattern))
                    contextome_exists.extend([str(m.relative_to(self.root)) for m in matches])
                else:
                    path = self.root / pattern
                    if path.exists():
                        contextome_exists.append(pattern)

            # Determine status
            has_code = len(codome_exists) > 0
            has_context = len(contextome_exists) > 0
            expected_code = len(domain_info.get("codome", [])) > 0

            if has_code and has_context:
                status = "SYMMETRIC"
            elif has_context and not expected_code:
                status = "CONTEXTOME_ONLY"  # Valid for Theory domain
            elif has_code and not has_context:
                status = "ORPHAN"
            elif has_context and not has_code and expected_code:
                status = "PHANTOM"
            else:
                status = "MISSING"

            self.report.domains_status[domain_name] = {
                "codome_paths": codome_exists,
                "contextome_paths": contextome_exists,
                "status": status,
            }

            # Report issues
            if status == "ORPHAN":
                self.report.issues.append(BoundaryIssue(
                    severity="HIGH",
                    category="ORPHAN",
                    path=domain_name,
                    message=f"Domain {domain_name} has code but no documentation",
                    suggestion=f"Add documentation to {domain_info.get('contextome', ['docs/'])[0]}",
                ))
            elif status == "PHANTOM" and expected_code:
                self.report.issues.append(BoundaryIssue(
                    severity="MEDIUM",
                    category="PHANTOM",
                    path=domain_name,
                    message=f"Domain {domain_name} has documentation but no code",
                    suggestion="Implement the documented features or mark as planned",
                ))
            elif status == "MISSING":
                self.report.issues.append(BoundaryIssue(
                    severity="HIGH",
                    category="DRIFT",
                    path=domain_name,
                    message=f"Domain {domain_name} is completely missing",
                    suggestion="Create domain or remove from DOMAINS declaration",
                ))

    def _find_undeclared_directories(self):
        """Find directories that exist but aren't formally declared."""
        # Get all top-level directories and first-level subdirectories
        actual_dirs: Set[str] = set()

        # Top level
        for item in self.root.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in {'node_modules', '__pycache__', '.git', '.venv', '.tools_venv'}:
                actual_dirs.add(item.name + "/")
                # First level subdirs
                for subitem in item.iterdir():
                    if subitem.is_dir() and not subitem.name.startswith('__'):
                        actual_dirs.add(f"{item.name}/{subitem.name}/")

        # Add .agent explicitly
        agent_dir = self.root / ".agent"
        if agent_dir.exists():
            actual_dirs.add(".agent/")
            for subitem in agent_dir.iterdir():
                if subitem.is_dir():
                    actual_dirs.add(f".agent/{subitem.name}/")

        # Build set of declared directories
        declared_dirs: Set[str] = set()
        for realm_info in REALMS.values():
            declared_dirs.add(realm_info["path"])
        for domain_info in DECLARED_DOMAINS.values():
            for path in domain_info.get("codome", []) + domain_info.get("contextome", []):
                if not "*" in path:
                    declared_dirs.add(path.rstrip("/") + "/" if not path.endswith("/") else path)

        # Add expected directories
        declared_dirs.update(EXPECTED_DIRECTORIES)

        # Find undeclared
        undeclared = actual_dirs - declared_dirs
        self.report.total_directories = len(actual_dirs)
        self.report.declared_directories = len(declared_dirs & actual_dirs)
        self.report.undeclared_directories = len(undeclared)

        # Filter out known acceptable undeclared directories
        ignored = {'archive/', 'node_modules/', '.collider/', 'dist/', 'build/'}
        significant_undeclared = {d for d in undeclared if not any(d.startswith(i.rstrip('/')) for i in ignored)}

        for dir_path in sorted(significant_undeclared):
            # Determine severity based on content
            full_path = self.root / dir_path
            file_count = sum(1 for _ in full_path.rglob("*") if _.is_file()) if full_path.exists() else 0

            severity = "HIGH" if file_count > 10 else "MEDIUM" if file_count > 0 else "LOW"

            self.report.issues.append(BoundaryIssue(
                severity=severity,
                category="UNDECLARED",
                path=dir_path,
                message=f"Directory exists but is not declared ({file_count} files)",
                suggestion=f"Add to DOMAINS.md or .agent/CODOME_MANIFEST.yaml",
            ))

    def _find_phantom_declarations(self):
        """Find declared paths that don't exist."""
        phantom_count = 0

        for domain_name, domain_info in DECLARED_DOMAINS.items():
            for path in domain_info.get("codome", []) + domain_info.get("contextome", []):
                if "*" not in path:
                    full_path = self.root / path
                    if not full_path.exists():
                        phantom_count += 1
                        self.report.issues.append(BoundaryIssue(
                            severity="MEDIUM",
                            category="PHANTOM",
                            path=path,
                            message=f"Declared in {domain_name} but doesn't exist",
                            suggestion=f"Create {path} or remove from domain declaration",
                        ))

        self.report.phantom_declarations = phantom_count

    def _check_partition_integrity(self):
        """Verify CODOME ∩ CONTEXTOME = ∅ (disjoint partition)."""
        # Sample check - verify no file is classified as both
        violations = []

        for realm_info in REALMS.values():
            realm_path = self.root / realm_info["path"]
            if realm_path.exists():
                for f in realm_path.rglob("*"):
                    if f.is_file():
                        is_codome = f.suffix in CODOME_EXTENSIONS
                        is_contextome = f.suffix in CONTEXTOME_EXTENSIONS

                        # Check for edge cases (e.g., .json could be config or data)
                        if f.suffix == '.json':
                            # JSON in src/ is likely data/config used by code
                            if 'src/' in str(f) or 'config/' in str(f):
                                continue  # Acceptable

                        if is_codome and is_contextome:
                            violations.append(str(f.relative_to(self.root)))

        if violations:
            self.report.issues.append(BoundaryIssue(
                severity="HIGH",
                category="DRIFT",
                path="PARTITION",
                message=f"Found {len(violations)} files that violate CODOME/CONTEXTOME partition",
                suggestion="Review file classifications in CODOME.md and CONTEXTOME.md",
            ))

    def _calculate_score(self):
        """Calculate alignment score (0-100)."""
        # Start with base score
        score = 100.0

        # Realm health (30 points)
        realm_score = 30.0
        for status in self.report.realms_status.values():
            if status["status"] != "VALID":
                realm_score -= 10
        score = score - (30 - realm_score)

        # Domain health (40 points)
        domain_score = 40.0
        domain_count = len(self.report.domains_status)
        for status in self.report.domains_status.values():
            if status["status"] == "SYMMETRIC":
                pass  # Full points
            elif status["status"] == "CONTEXTOME_ONLY":
                domain_score -= (40 / domain_count) * 0.2  # Minor deduction
            elif status["status"] in ["ORPHAN", "PHANTOM"]:
                domain_score -= (40 / domain_count) * 0.5
            elif status["status"] == "MISSING":
                domain_score -= (40 / domain_count)
        score = score - (40 - domain_score)

        # Issue deductions (20 points max)
        issue_deduction = 0
        for issue in self.report.issues:
            if issue.severity == "CRITICAL":
                issue_deduction += 2
            elif issue.severity == "HIGH":
                issue_deduction += 1
            elif issue.severity == "MEDIUM":
                issue_deduction += 0.5
            # LOW issues don't deduct
        score -= min(20, issue_deduction)

        # Undeclared ratio bonus/penalty (10 points)
        if self.report.total_directories > 0:
            declared_ratio = self.report.declared_directories / self.report.total_directories
            # At 50% declared, no bonus/penalty; above 50% gets bonus
            ratio_adjustment = (declared_ratio - 0.5) * 20  # -10 to +10
            score += ratio_adjustment

        self.report.alignment_score = max(0, min(100, score))

    def _generate_recommendations(self):
        """Generate actionable recommendations."""
        recs = []

        # Count issues by category
        by_category = {}
        for issue in self.report.issues:
            by_category[issue.category] = by_category.get(issue.category, 0) + 1

        if by_category.get("UNDECLARED", 0) > 5:
            recs.append("HIGH: Update .agent/CODOME_MANIFEST.yaml to declare undeclared directories")

        if by_category.get("PHANTOM", 0) > 0:
            recs.append("MEDIUM: Remove or implement phantom declarations in DOMAINS.md")

        if by_category.get("ORPHAN", 0) > 0:
            recs.append("MEDIUM: Add documentation for orphan code domains")

        if self.report.alignment_score < 80:
            recs.append("CRITICAL: Boundary drift detected - schedule consolidation sprint")

        if not recs:
            recs.append("OK: Boundaries are well-aligned. Continue monitoring.")

        self.report.recommendations = recs


def print_report(report: BoundaryReport, verbose: bool = False):
    """Print formatted report to stdout."""
    score = report.alignment_score
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           BOUNDARY ANALYSIS REPORT                           ║
║           {report.timestamp[:19]:<19}                        ║
╠══════════════════════════════════════════════════════════════╣
║  ALIGNMENT SCORE:  {score:>5.1f}/100  ({grade})                          ║
║  Total Directories:     {report.total_directories:>4}                              ║
║  Declared:              {report.declared_directories:>4}                              ║
║  Undeclared:            {report.undeclared_directories:>4}                              ║
║  Phantom:               {report.phantom_declarations:>4}                              ║
╠══════════════════════════════════════════════════════════════╣
║  REALMS STATUS:                                              ║""")

    for realm, status in report.realms_status.items():
        icon = "✓" if status["status"] == "VALID" else "✗"
        print(f"║    {icon} {realm:<12} {status['codome_files']:>4} code, {status['contextome_files']:>4} docs       ║")

    print(f"""╠══════════════════════════════════════════════════════════════╣
║  DOMAINS STATUS:                                             ║""")

    for domain, status in report.domains_status.items():
        icon = "✓" if status["status"] == "SYMMETRIC" else "◐" if status["status"] == "CONTEXTOME_ONLY" else "✗"
        print(f"║    {icon} {domain:<16} {status['status']:<20}     ║")

    if report.issues and verbose:
        print(f"""╠══════════════════════════════════════════════════════════════╣
║  ISSUES ({len(report.issues)}):                                              ║""")
        for issue in report.issues[:10]:  # Limit to 10
            sev_icon = "🔴" if issue.severity in ["CRITICAL", "HIGH"] else "🟡" if issue.severity == "MEDIUM" else "🟢"
            print(f"║  {sev_icon} [{issue.category}] {issue.path[:35]:<35}  ║")

    print(f"""╠══════════════════════════════════════════════════════════════╣
║  RECOMMENDATIONS:                                            ║""")
    for rec in report.recommendations[:3]:
        print(f"║    • {rec[:52]:<52} ║")

    print(f"╚══════════════════════════════════════════════════════════════╝")


def save_report(report: BoundaryReport, output_path: Path):
    """Save report to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report.to_dict(), f, indent=2)
    print(f"  Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Boundary Analyzer - Validate PROJECT_elements internal organization"
    )
    parser.add_argument('--quick', '-q', action='store_true',
                        help="Quick check - return exit code only")
    parser.add_argument('--json', '-j', action='store_true',
                        help="Output JSON to stdout")
    parser.add_argument('--save', '-s', action='store_true',
                        help="Save report to .agent/intelligence/")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Show detailed issues")
    parser.add_argument('--fix', '-f', action='store_true',
                        help="Generate fix suggestions")
    parser.add_argument('--threshold', '-t', type=int, default=70,
                        help="Minimum alignment score (default: 70)")

    args = parser.parse_args()

    analyzer = BoundaryAnalyzer()
    report = analyzer.analyze()

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    elif not args.quick:
        print_report(report, verbose=args.verbose or args.fix)

    if args.save:
        output_path = PROJECT_ROOT / ".agent/intelligence/boundary_analysis.json"
        save_report(report, output_path)

    # Exit code based on threshold
    if report.alignment_score < args.threshold:
        if not args.json:
            print(f"\n  ⚠️  Alignment score {report.alignment_score:.1f} below threshold {args.threshold}")
        sys.exit(1)
    else:
        if not args.json and not args.quick:
            print(f"\n  ✓ Alignment score {report.alignment_score:.1f} meets threshold {args.threshold}")
        sys.exit(0)


if __name__ == "__main__":
    main()
