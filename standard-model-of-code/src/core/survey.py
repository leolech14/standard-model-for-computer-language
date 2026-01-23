"""
CODOME DEFINITION LAYER (Stage 0)
==================================

This module defines the ONTOLOGY of the target system before analysis begins.
It is not merely an optimization (exclusion); it is a DEFINITION.

"Before you measure a thing, you must define what the thing IS."

The Survey answers 5 fundamental questions:

1. IDENTITY: What IS this system?
   - Primary language (Python, TypeScript, Go...)
   - Dominant framework (Django, Next.js, FastAPI...)
   - Archetype (Monolith, Monorepo, Microservices, Library)

2. BOUNDARIES: Where does it START and END?
   - What is OURS vs VENDOR vs GENERATED?
   - Spatial boundaries (directories to include/exclude)

3. NATURE: What is the TEXTURE of this codebase?
   - Code vs Config vs Data ratios
   - File type distribution

4. POLLUTION: What VIOLATES the physics of this repo?
   - Vendor code in src/
   - Minified files without markers
   - Binary artifacts in source tree

5. ADAPTATION: How must the INSTRUMENTS be calibrated?
   - Which parsers to use
   - What thresholds apply
   - Expected patterns

Output: CodomeManifest - the complete ontological definition

Usage:
    from survey import run_survey, CodomeManifest

    manifest = run_survey("/path/to/repo")
    print(f"Identity: {manifest.identity}")
    print(f"Boundaries: {len(manifest.boundary_constraints)} exclusions")

See also:
    - docs/specs/CODOME_BOUNDARY_DEFINITION.md
    - docs/specs/CODOME_COMPLETENESS_INDEX.md
    - docs/specs/CODOME_HEALTH_INDEX.md

Phase: 10 (Adaptive Intelligence Layer)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os
import fnmatch
import yaml
import time


# ============================================================
# CONFIGURATION
# ============================================================

# Default patterns for exclusion detection
DEFAULT_DIRECTORY_PATTERNS = [
    "node_modules/",
    "vendor/",
    ".vendor/",
    "lib/",
    "dist/",
    "build/",
    "out/",
    ".git/",
    "__pycache__/",
    ".venv/",
    "venv/",
    "coverage/",
    ".nyc_output/",
    ".next/",
    ".nuxt/",
]

DEFAULT_FILE_PATTERNS = [
    "*.min.js",
    "*.min.css",
    "*.bundle.js",
    "*.chunk.js",
    "*.generated.*",
    "*.pb.go",
    "*.pb.ts",
    "*.pb.js",
    "*_pb2.py",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
]

# Heuristics for minification detection
MINIFIED_THRESHOLDS = {
    "single_line_size_kb": 10,      # Single-line file > 10KB = likely minified
    "avg_line_length": 500,          # Avg line > 500 chars = likely minified
    "max_reasonable_line": 1000,     # Any line > 1000 chars = suspicious
    "whitespace_ratio_min": 0.05,    # Less than 5% whitespace = likely minified
}


# ============================================================
# DATA STRUCTURES - ONTOLOGICAL (The 5 Questions)
# ============================================================

# Q1: IDENTITY - What IS this system?
@dataclass
class SystemIdentity:
    """The fundamental identity of the codebase (Question 1).

    Archetype values: monolith, monorepo, microservices, library, cli, unknown
    """
    primary_language: str = "unknown"
    secondary_languages: list[str] = field(default_factory=list)
    dominant_framework: str = "unknown"
    archetype: str = "unknown"  # NOT topology! See terminology guide.
    confidence: float = 0.0

    def __str__(self) -> str:
        langs = f"{self.primary_language}"
        if self.secondary_languages:
            langs += f" (+{', '.join(self.secondary_languages)})"
        framework = f" / {self.dominant_framework}" if self.dominant_framework != "unknown" else ""
        return f"{langs}{framework} ({self.archetype})"


# Q3: NATURE - What is the TEXTURE?
@dataclass
class CodomeComposition:
    """The composition breakdown of the codebase (Question 3)."""
    source_files: int = 0
    config_files: int = 0
    data_files: int = 0
    doc_files: int = 0
    binary_files: int = 0
    other_files: int = 0

    @property
    def total(self) -> int:
        return (self.source_files + self.config_files + self.data_files +
                self.doc_files + self.binary_files + self.other_files)

    @property
    def source_ratio(self) -> float:
        return self.source_files / self.total if self.total > 0 else 0.0

    def as_percentages(self) -> dict[str, float]:
        t = self.total or 1
        return {
            "source": self.source_files / t,
            "config": self.config_files / t,
            "data": self.data_files / t,
            "docs": self.doc_files / t,
            "binary": self.binary_files / t,
            "other": self.other_files / t,
        }


# Q4: POLLUTION - What shouldn't be here?
@dataclass
class PollutionAlert:
    """A detected pollution issue (Question 4)."""
    path: str
    pollution_type: str  # vendor_in_src, minified_unmarked, binary_in_source, etc.
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    recommendation: str


# ============================================================
# DATA STRUCTURES - DETECTION RESULTS
# ============================================================

@dataclass
class ExclusionMatch:
    """A single exclusion detection result."""
    path: str
    pattern: str
    reason: str
    confidence: float  # 0.0 - 1.0
    file_count: int = 0
    total_size_kb: float = 0.0


@dataclass
class MinifiedFile:
    """A detected minified file."""
    path: str
    reason: str
    size_kb: float
    line_count: int
    avg_line_length: float


@dataclass
class CCIMetrics:
    """Codome Completeness Index metrics.

    Measures how complete and accurate our code analysis is:
    - Sensitivity (Recall): What % of source code did we capture?
    - Specificity: What % of vendor code did we exclude?
    - Precision: What % of analyzed nodes are actually ours?
    - F2 Score: Recall-weighted harmonic mean (prioritizes completeness)

    See: docs/specs/CODOME_COMPLETENESS_INDEX.md
    """
    # Core classification counts
    true_positives: int = 0   # SOURCE correctly analyzed
    false_positives: int = 0  # VENDOR incorrectly analyzed
    true_negatives: int = 0   # VENDOR correctly excluded
    false_negatives: int = 0  # SOURCE incorrectly excluded

    # Derived metrics (calculated from counts)
    sensitivity: float = 0.0  # TP / (TP + FN) - Recall
    specificity: float = 0.0  # TN / (TN + FP)
    precision: float = 0.0    # TP / (TP + FP)
    f1_score: float = 0.0     # Harmonic mean
    f2_score: float = 0.0     # Recall-weighted (recommended)
    gmean: float = 0.0        # sqrt(Sensitivity * Specificity)

    # Overall score and interpretation
    cci: float = 0.0          # Primary CCI score (F2 * 100)
    verdict: str = "UNKNOWN"  # EXCELLENT/GOOD/FAIR/POOR


def calculate_cci(
    total_source_files: int,
    analyzed_source_files: int,
    total_vendor_files: int,
    analyzed_vendor_files: int,
) -> CCIMetrics:
    """Calculate Codome Completeness Index from classification results.

    Args:
        total_source_files: Ground truth count of source files
        analyzed_source_files: Source files we actually analyzed (TP)
        total_vendor_files: Ground truth count of vendor/generated files
        analyzed_vendor_files: Vendor files we incorrectly analyzed (FP)

    Returns:
        CCIMetrics with all calculated values
    """
    import math

    metrics = CCIMetrics()

    # Classification counts
    metrics.true_positives = analyzed_source_files
    metrics.false_positives = analyzed_vendor_files
    metrics.true_negatives = total_vendor_files - analyzed_vendor_files
    metrics.false_negatives = total_source_files - analyzed_source_files

    tp, fp, tn, fn = (
        metrics.true_positives,
        metrics.false_positives,
        metrics.true_negatives,
        metrics.false_negatives,
    )

    # Sensitivity (Recall) = TP / (TP + FN)
    if tp + fn > 0:
        metrics.sensitivity = tp / (tp + fn)

    # Specificity = TN / (TN + FP)
    if tn + fp > 0:
        metrics.specificity = tn / (tn + fp)

    # Precision = TP / (TP + FP)
    if tp + fp > 0:
        metrics.precision = tp / (tp + fp)

    # F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
    if metrics.precision + metrics.sensitivity > 0:
        metrics.f1_score = (
            2 * metrics.precision * metrics.sensitivity
        ) / (metrics.precision + metrics.sensitivity)

    # F2 Score = 5 * (Precision * Recall) / (4 * Precision + Recall)
    if 4 * metrics.precision + metrics.sensitivity > 0:
        metrics.f2_score = (
            5 * metrics.precision * metrics.sensitivity
        ) / (4 * metrics.precision + metrics.sensitivity)

    # G-Mean = sqrt(Sensitivity * Specificity)
    metrics.gmean = math.sqrt(metrics.sensitivity * metrics.specificity)

    # CCI = F2 * 100 (recommended metric)
    metrics.cci = metrics.f2_score * 100

    # Verdict
    if metrics.cci >= 95:
        metrics.verdict = "EXCELLENT"
    elif metrics.cci >= 85:
        metrics.verdict = "GOOD"
    elif metrics.cci >= 70:
        metrics.verdict = "FAIR"
    else:
        metrics.verdict = "POOR"

    return metrics


@dataclass
class SurveyResult:
    """Complete survey results for a directory."""
    root_path: str
    scan_time_ms: float

    # Counts
    total_files: int = 0
    total_dirs: int = 0
    total_size_kb: float = 0.0

    # Exclusions
    directory_exclusions: list[ExclusionMatch] = field(default_factory=list)
    file_exclusions: list[ExclusionMatch] = field(default_factory=list)
    minified_files: list[MinifiedFile] = field(default_factory=list)

    # Estimates (after exclusions)
    estimated_source_files: int = 0
    estimated_nodes: int = 0  # Rough estimate: ~75 nodes per source file

    # Recommendations
    recommended_excludes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Codome Completeness Index (optional - populated after analysis comparison)
    cci: Optional[CCIMetrics] = None

    @property
    def exclusion_count(self) -> int:
        return len(self.directory_exclusions) + len(self.file_exclusions) + len(self.minified_files)

    @property
    def signal_to_noise_ratio(self) -> float:
        """Ratio of source files to total files (higher = better)."""
        if self.total_files == 0:
            return 1.0
        return self.estimated_source_files / self.total_files


# ============================================================
# PATTERN DETECTION
# ============================================================

def path_matches_pattern(path: str, pattern: str) -> bool:
    """
    Check if a path matches an exclusion pattern.

    Supports:
    - Directory patterns: "vendor/" matches any path containing /vendor/
    - File patterns: "*.min.js" matches files ending in .min.js
    - Glob patterns: "**/*.generated.*" for recursive matching
    """
    path_lower = path.lower()
    pattern_lower = pattern.lower()

    # Directory pattern (ends with /)
    if pattern_lower.endswith('/'):
        dir_name = pattern_lower.rstrip('/')
        # Match /dirname/ anywhere in path
        return f"/{dir_name}/" in f"/{path_lower}/" or path_lower.startswith(f"{dir_name}/")

    # File pattern (contains *)
    if '*' in pattern:
        filename = os.path.basename(path)
        return fnmatch.fnmatch(filename.lower(), pattern_lower)

    # Exact match
    return path_lower == pattern_lower or path_lower.endswith(f"/{pattern_lower}")


def scan_for_exclusions(
    root: Path,
    dir_patterns: list[str] = None,
    file_patterns: list[str] = None,
    max_depth: int = 10
) -> tuple[list[ExclusionMatch], list[ExclusionMatch]]:
    """
    Scan directory for exclusion candidates.

    Returns:
        (directory_exclusions, file_exclusions)
    """
    dir_patterns = dir_patterns or DEFAULT_DIRECTORY_PATTERNS
    file_patterns = file_patterns or DEFAULT_FILE_PATTERNS

    dir_exclusions = []
    file_exclusions = []

    # Track already-matched directories to avoid duplicate counting
    matched_dirs = set()

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        depth = rel_dir.count(os.sep) if rel_dir != '.' else 0

        if depth > max_depth:
            dirnames.clear()  # Don't descend further
            continue

        # Check directory patterns
        for pattern in dir_patterns:
            if path_matches_pattern(rel_dir, pattern):
                if rel_dir not in matched_dirs:
                    matched_dirs.add(rel_dir)

                    # Count files and size in this directory
                    file_count = 0
                    total_size = 0
                    for dp, _, fns in os.walk(dirpath):
                        file_count += len(fns)
                        for fn in fns:
                            try:
                                total_size += os.path.getsize(os.path.join(dp, fn))
                            except OSError:
                                pass

                    dir_exclusions.append(ExclusionMatch(
                        path=rel_dir,
                        pattern=pattern,
                        reason=_get_pattern_reason(pattern),
                        confidence=1.0,
                        file_count=file_count,
                        total_size_kb=total_size / 1024
                    ))

                    # Don't descend into excluded directories
                    dirnames.clear()
                    break

        # Check file patterns (only if directory not excluded)
        if rel_dir not in matched_dirs:
            for filename in filenames:
                rel_path = os.path.join(rel_dir, filename) if rel_dir != '.' else filename
                for pattern in file_patterns:
                    if path_matches_pattern(filename, pattern):
                        try:
                            size = os.path.getsize(os.path.join(dirpath, filename)) / 1024
                        except OSError:
                            size = 0

                        file_exclusions.append(ExclusionMatch(
                            path=rel_path,
                            pattern=pattern,
                            reason=_get_pattern_reason(pattern),
                            confidence=0.95,
                            file_count=1,
                            total_size_kb=size
                        ))
                        break

    return dir_exclusions, file_exclusions


def _get_pattern_reason(pattern: str) -> str:
    """Get human-readable reason for a pattern."""
    reasons = {
        "node_modules/": "npm dependencies",
        "vendor/": "vendored dependencies",
        ".vendor/": "vendored dependencies",
        "dist/": "build output",
        "build/": "build output",
        "out/": "build output",
        ".git/": "git internals",
        "__pycache__/": "Python bytecode cache",
        ".venv/": "Python virtual environment",
        "venv/": "Python virtual environment",
        "coverage/": "test coverage data",
        ".nyc_output/": "test coverage data",
        ".next/": "Next.js build cache",
        ".nuxt/": "Nuxt.js build cache",
        "lib/": "library dependencies",
        "*.min.js": "minified JavaScript",
        "*.min.css": "minified CSS",
        "*.bundle.js": "bundled JavaScript",
        "*.chunk.js": "code-split chunk",
        "*.generated.*": "generated code",
        "*.pb.go": "protobuf generated (Go)",
        "*.pb.ts": "protobuf generated (TypeScript)",
        "*.pb.js": "protobuf generated (JavaScript)",
        "*_pb2.py": "protobuf generated (Python)",
        "*.lock": "lock file",
        "package-lock.json": "npm lock file",
        "yarn.lock": "yarn lock file",
        "pnpm-lock.yaml": "pnpm lock file",
    }
    return reasons.get(pattern, "matched exclusion pattern")


# ============================================================
# MINIFICATION DETECTION
# ============================================================

def detect_minified_files(
    root: Path,
    extensions: list[str] = None,
    exclude_dirs: list[str] = None
) -> list[MinifiedFile]:
    """
    Detect minified files using heuristics.

    Heuristics:
    1. Single-line file > 10KB
    2. Average line length > 500 characters
    3. Very low whitespace ratio
    """
    extensions = extensions or ['.js', '.css', '.ts']
    exclude_dirs = exclude_dirs or DEFAULT_DIRECTORY_PATTERNS

    minified = []

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)

        # Skip excluded directories
        skip = False
        for pattern in exclude_dirs:
            if path_matches_pattern(rel_dir, pattern):
                skip = True
                dirnames.clear()
                break
        if skip:
            continue

        for filename in filenames:
            # Skip already-marked minified files
            if '.min.' in filename or '.bundle.' in filename:
                continue

            # Check extension
            ext = os.path.splitext(filename)[1].lower()
            if ext not in extensions:
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.join(rel_dir, filename) if rel_dir != '.' else filename

            result = _check_minified(filepath)
            if result:
                minified.append(MinifiedFile(
                    path=rel_path,
                    reason=result['reason'],
                    size_kb=result['size_kb'],
                    line_count=result['line_count'],
                    avg_line_length=result['avg_line_length']
                ))

    return minified


def _check_minified(filepath: str) -> Optional[dict]:
    """
    Check if a file appears to be minified.

    Returns dict with details if minified, None otherwise.
    """
    try:
        size_bytes = os.path.getsize(filepath)
        size_kb = size_bytes / 1024

        # Small files are unlikely to be problematically minified
        if size_kb < 5:
            return None

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(500_000)  # Read first 500KB max

        lines = content.split('\n')
        line_count = len(lines)

        # Single line file > threshold
        if line_count <= 2 and size_kb > MINIFIED_THRESHOLDS['single_line_size_kb']:
            return {
                'reason': f"Single-line file ({size_kb:.1f}KB)",
                'size_kb': size_kb,
                'line_count': line_count,
                'avg_line_length': len(content) / max(line_count, 1)
            }

        # Average line length check
        avg_line_len = len(content) / max(line_count, 1)
        if avg_line_len > MINIFIED_THRESHOLDS['avg_line_length']:
            return {
                'reason': f"Very long lines (avg {avg_line_len:.0f} chars)",
                'size_kb': size_kb,
                'line_count': line_count,
                'avg_line_length': avg_line_len
            }

        # Whitespace ratio check (for larger files)
        if size_kb > 20:
            whitespace_count = sum(1 for c in content if c in ' \t\n')
            whitespace_ratio = whitespace_count / len(content) if content else 0
            if whitespace_ratio < MINIFIED_THRESHOLDS['whitespace_ratio_min']:
                return {
                    'reason': f"Low whitespace ({whitespace_ratio*100:.1f}%)",
                    'size_kb': size_kb,
                    'line_count': line_count,
                    'avg_line_length': avg_line_len
                }

        return None

    except (OSError, IOError):
        return None


# ============================================================
# MAIN SURVEY FUNCTION
# ============================================================

def run_survey(
    path: str,
    dir_patterns: list[str] = None,
    file_patterns: list[str] = None,
    detect_minified: bool = True
) -> SurveyResult:
    """
    Run a complete survey of a directory.

    Args:
        path: Directory to survey
        dir_patterns: Directory exclusion patterns (default: DEFAULT_DIRECTORY_PATTERNS)
        file_patterns: File exclusion patterns (default: DEFAULT_FILE_PATTERNS)
        detect_minified: Whether to run minification detection heuristics

    Returns:
        SurveyResult with all findings and recommendations
    """
    start_time = time.time()
    root = Path(path).resolve()

    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root}")

    # Initialize result
    result = SurveyResult(
        root_path=str(root),
        scan_time_ms=0
    )

    # Count totals first (quick pass)
    for dirpath, dirnames, filenames in os.walk(root):
        result.total_dirs += len(dirnames)
        result.total_files += len(filenames)
        for fn in filenames:
            try:
                result.total_size_kb += os.path.getsize(os.path.join(dirpath, fn)) / 1024
            except OSError:
                pass

    # Scan for pattern-based exclusions
    dir_exclusions, file_exclusions = scan_for_exclusions(
        root, dir_patterns, file_patterns
    )
    result.directory_exclusions = dir_exclusions
    result.file_exclusions = file_exclusions

    # Detect minified files
    if detect_minified:
        excluded_dirs = [e.path for e in dir_exclusions]
        result.minified_files = detect_minified_files(
            root,
            exclude_dirs=excluded_dirs + (dir_patterns or DEFAULT_DIRECTORY_PATTERNS)
        )

    # Calculate estimates
    excluded_file_count = sum(e.file_count for e in dir_exclusions)
    excluded_file_count += len(file_exclusions)
    excluded_file_count += len(result.minified_files)

    result.estimated_source_files = max(0, result.total_files - excluded_file_count)
    result.estimated_nodes = result.estimated_source_files * 75  # Rough estimate

    # Build recommendations
    result.recommended_excludes = []
    for excl in dir_exclusions:
        result.recommended_excludes.append(excl.path)
    for excl in file_exclusions:
        result.recommended_excludes.append(excl.path)
    for mf in result.minified_files:
        result.recommended_excludes.append(mf.path)

    # Add warnings
    if result.estimated_nodes > 10000:
        result.warnings.append(
            f"Large codebase: estimated {result.estimated_nodes:,} nodes. "
            "Consider using --exclude to focus on specific directories."
        )

    if len(result.minified_files) > 0:
        total_minified_kb = sum(mf.size_kb for mf in result.minified_files)
        result.warnings.append(
            f"Found {len(result.minified_files)} minified files ({total_minified_kb:.0f}KB). "
            "These will be excluded by default."
        )

    result.scan_time_ms = (time.time() - start_time) * 1000
    return result


# ============================================================
# CONFIG FILE SUPPORT
# ============================================================

def load_exclusion_config(config_path: str = None) -> dict:
    """
    Load exclusion configuration from YAML file.

    If no path provided, looks for:
    1. .collider/exclusions.yaml in current directory
    2. Built-in defaults
    """
    if config_path:
        path = Path(config_path)
    else:
        # Look for config in current directory
        path = Path('.collider/exclusions.yaml')
        if not path.exists():
            path = Path('collider.yaml')

    if path.exists():
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    # Return defaults
    return {
        'version': '1.0',
        'directory_patterns': DEFAULT_DIRECTORY_PATTERNS,
        'file_patterns': DEFAULT_FILE_PATTERNS,
    }


def generate_analysis_config(survey_result: SurveyResult) -> dict:
    """
    Generate an analysis configuration from survey results.

    This config can be passed to Collider's full analysis.
    """
    return {
        'version': '1.0',
        'generated_from': 'survey',
        'root_path': survey_result.root_path,
        'exclude_paths': survey_result.recommended_excludes,
        'estimated_nodes': survey_result.estimated_nodes,
        'warnings': survey_result.warnings,
        'survey_stats': {
            'total_files': survey_result.total_files,
            'excluded_files': survey_result.total_files - survey_result.estimated_source_files,
            'signal_to_noise_ratio': survey_result.signal_to_noise_ratio,
            'scan_time_ms': survey_result.scan_time_ms,
        }
    }


# ============================================================
# CLI SUPPORT (for ./collider survey command)
# ============================================================

def print_survey_report(result: SurveyResult, verbose: bool = False):
    """Print a human-readable survey report."""
    print("\n" + "=" * 60)
    print("COLLIDER SURVEY REPORT")
    print("=" * 60)
    print(f"Path: {result.root_path}")
    print(f"Scan time: {result.scan_time_ms:.0f}ms")
    print()

    print(f"Total files:     {result.total_files:,}")
    print(f"Total dirs:      {result.total_dirs:,}")
    print(f"Total size:      {result.total_size_kb/1024:.1f}MB")
    print()

    if result.directory_exclusions:
        print("DIRECTORY EXCLUSIONS:")
        for excl in result.directory_exclusions:
            print(f"  - {excl.path}")
            print(f"    Pattern: {excl.pattern}")
            print(f"    Reason: {excl.reason}")
            print(f"    Files: {excl.file_count:,}, Size: {excl.total_size_kb/1024:.1f}MB")
        print()

    if result.minified_files and verbose:
        print("MINIFIED FILES DETECTED:")
        for mf in result.minified_files[:10]:  # Show first 10
            print(f"  - {mf.path}")
            print(f"    Reason: {mf.reason}")
        if len(result.minified_files) > 10:
            print(f"  ... and {len(result.minified_files) - 10} more")
        print()

    print("ESTIMATES (after exclusions):")
    print(f"  Source files:  {result.estimated_source_files:,}")
    print(f"  Est. nodes:    {result.estimated_nodes:,}")
    print(f"  Signal/Noise:  {result.signal_to_noise_ratio:.1%}")
    print()

    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")
        print()

    # CCI Metrics (if available)
    if result.cci:
        cci = result.cci
        print("CODOME COMPLETENESS INDEX (CCI):")
        print(f"  CCI Score:     {cci.cci:.1f}% ({cci.verdict})")
        print(f"  Sensitivity:   {cci.sensitivity:.1%}  (Recall - found all source?)")
        print(f"  Specificity:   {cci.specificity:.1%}  (Excluded vendor?)")
        print(f"  Precision:     {cci.precision:.1%}  (No noise?)")
        print(f"  F2 Score:      {cci.f2_score:.3f}  (Completeness-weighted)")
        if verbose:
            print(f"  F1 Score:      {cci.f1_score:.3f}  (Balanced)")
            print(f"  G-Mean:        {cci.gmean:.3f}  (Geometric)")
            print(f"  TP={cci.true_positives}, FP={cci.false_positives}, "
                  f"TN={cci.true_negatives}, FN={cci.false_negatives}")
        print()

    print("=" * 60)


if __name__ == '__main__':
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    verbose = '-v' in sys.argv or '--verbose' in sys.argv

    result = run_survey(path)
    print_survey_report(result, verbose=verbose)
