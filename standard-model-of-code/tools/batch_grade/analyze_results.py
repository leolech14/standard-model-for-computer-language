#!/usr/bin/env python3
"""
Batch Grade Results Analyzer

Processes batch_grade output JSON and produces statistical analysis.
Closes HIGH-002: No batch results analyzer exists.

Usage:
    python analyze_results.py <results.json>
    python analyze_results.py <results.json> --format markdown
    python analyze_results.py <results.json> --output report.md
    python analyze_results.py <results.json> --golden-repos 10

Library usage:
    from analyze_results import BatchAnalyzer
    analyzer = BatchAnalyzer.from_file("final_results.json")
    print(analyzer.grade_distribution)
    print(analyzer.component_correlations())
"""

import json
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
import statistics


@dataclass
class RepoResult:
    """Single repo analysis result."""
    name: str
    url: str
    language: str
    stars: int
    size_kb: int
    status: str
    grade: Optional[str]
    health_index: Optional[float]
    error: Optional[str]
    duration_sec: Optional[float]
    nodes: Optional[int] = None
    edges: Optional[int] = None
    component_scores: dict = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    @property
    def edge_node_ratio(self) -> Optional[float]:
        if self.nodes and self.nodes > 0 and self.edges is not None:
            return self.edges / self.nodes
        return None


class BatchAnalyzer:
    """Analyzer for batch grade results."""

    def __init__(self, meta: dict, results: list[RepoResult]):
        self.meta = meta
        self.results = results
        self._successful = [r for r in results if r.is_success]
        self._failed = [r for r in results if not r.is_success]

    @classmethod
    def from_file(cls, path: str | Path) -> "BatchAnalyzer":
        """Load from JSON file."""
        with open(path) as f:
            data = json.load(f)

        results = []
        for r in data.get("results", []):
            results.append(RepoResult(
                name=r.get("name", ""),
                url=r.get("url", ""),
                language=r.get("language", ""),
                stars=r.get("stars", 0),
                size_kb=r.get("size_kb", 0),
                status=r.get("status", "unknown"),
                grade=r.get("grade"),
                health_index=r.get("health_index"),
                error=r.get("error"),
                duration_sec=r.get("duration_sec"),
                nodes=r.get("nodes"),
                edges=r.get("edges"),
                component_scores=r.get("component_scores", {})
            ))

        return cls(data.get("meta", {}), results)

    # ============ Basic Statistics ============

    @property
    def total_repos(self) -> int:
        return len(self.results)

    @property
    def successful_count(self) -> int:
        return len(self._successful)

    @property
    def failed_count(self) -> int:
        return len(self._failed)

    @property
    def success_rate(self) -> float:
        return self.successful_count / self.total_repos if self.total_repos > 0 else 0

    # ============ Grade Distribution ============

    @property
    def grade_distribution(self) -> dict[str, int]:
        """Grade counts."""
        dist = defaultdict(int)
        for r in self._successful:
            if r.grade:
                dist[r.grade] += 1
        return dict(sorted(dist.items()))

    @property
    def grade_percentages(self) -> dict[str, float]:
        """Grade percentages of successful repos."""
        dist = self.grade_distribution
        total = sum(dist.values())
        if total == 0:
            return {}
        return {k: (v / total) * 100 for k, v in dist.items()}

    # ============ Health Statistics ============

    @property
    def health_stats(self) -> dict:
        """Health index statistics."""
        health_values = [r.health_index for r in self._successful if r.health_index is not None]
        if not health_values:
            return {}
        return {
            "min": min(health_values),
            "max": max(health_values),
            "mean": statistics.mean(health_values),
            "median": statistics.median(health_values),
            "stdev": statistics.stdev(health_values) if len(health_values) > 1 else 0
        }

    # ============ Component Analysis ============

    def component_stats_by_grade(self) -> dict[str, dict[str, float]]:
        """Average component scores per grade."""
        grade_components = defaultdict(lambda: defaultdict(list))

        for r in self._successful:
            if r.grade and r.component_scores:
                for comp, score in r.component_scores.items():
                    if score is not None:
                        grade_components[r.grade][comp].append(score)

        result = {}
        for grade, components in sorted(grade_components.items()):
            result[grade] = {
                comp: statistics.mean(scores)
                for comp, scores in components.items()
            }
        return result

    def component_variance(self) -> dict[str, float]:
        """Variance of each component across all successful repos.
        Higher variance = more discriminating power.
        """
        component_values = defaultdict(list)
        for r in self._successful:
            for comp, score in r.component_scores.items():
                if score is not None:
                    component_values[comp].append(score)

        return {
            comp: statistics.variance(values) if len(values) > 1 else 0
            for comp, values in component_values.items()
        }

    # ============ Language Analysis ============

    def stats_by_language(self) -> dict[str, dict]:
        """Statistics grouped by primary language."""
        lang_repos = defaultdict(list)
        for r in self._successful:
            lang_repos[r.language].append(r)

        result = {}
        for lang, repos in sorted(lang_repos.items(), key=lambda x: -len(x[1])):
            health_values = [r.health_index for r in repos if r.health_index]
            grade_dist = defaultdict(int)
            for r in repos:
                if r.grade:
                    grade_dist[r.grade] += 1

            result[lang] = {
                "count": len(repos),
                "avg_health": statistics.mean(health_values) if health_values else 0,
                "grades": dict(sorted(grade_dist.items()))
            }
        return result

    # ============ Failure Analysis ============

    def failure_breakdown(self) -> dict[str, int]:
        """Categorize failures by type."""
        categories = defaultdict(int)
        for r in self._failed:
            if "timeout" in (r.error or "").lower() or r.status == "timeout":
                categories["timeout"] += 1
            elif "too_large" in r.status or "size" in (r.error or "").lower():
                categories["skipped_too_large"] += 1
            elif r.status == "clone_failed":
                categories["clone_failed"] += 1
            elif r.status == "grade_failed":
                categories["grade_failed"] += 1
            else:
                categories["other"] += 1
        return dict(categories)

    # ============ Golden Repos ============

    def golden_repos(self, n: int = 10, grade: str = "B") -> list[RepoResult]:
        """Top N repos by health index for a given grade (default: B)."""
        candidates = [r for r in self._successful if r.grade == grade]
        return sorted(candidates, key=lambda r: r.health_index or 0, reverse=True)[:n]

    def worst_repos(self, n: int = 5) -> list[RepoResult]:
        """Bottom N repos by health index."""
        return sorted(
            [r for r in self._successful if r.health_index],
            key=lambda r: r.health_index or float('inf')
        )[:n]

    # ============ Anomaly Detection ============

    def high_connectivity_good_grade(self, ratio_threshold: float = 2.5) -> list[RepoResult]:
        """Repos with high edge/node ratio but good grades (C or better)."""
        return [
            r for r in self._successful
            if r.grade in ("A", "B", "C")
            and r.edge_node_ratio
            and r.edge_node_ratio > ratio_threshold
        ]

    def low_nodes_high_health(self, node_threshold: int = 20, health_threshold: float = 7.5) -> list[RepoResult]:
        """Small repos with high health."""
        return [
            r for r in self._successful
            if r.nodes and r.nodes < node_threshold
            and r.health_index and r.health_index > health_threshold
        ]

    # ============ Output Formatting ============

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            "# Batch Grade Analysis Report",
            "",
            f"**Generated from:** {self.meta.get('timestamp', 'unknown')}",
            f"**Total repos:** {self.total_repos}",
            f"**Successful:** {self.successful_count} ({self.success_rate:.1%})",
            f"**Failed:** {self.failed_count}",
            "",
            "---",
            "",
            "## Grade Distribution",
            "",
            "| Grade | Count | Percentage |",
            "|-------|-------|------------|",
        ]

        for grade, count in self.grade_distribution.items():
            pct = self.grade_percentages.get(grade, 0)
            lines.append(f"| {grade} | {count} | {pct:.1f}% |")

        lines.extend([
            "",
            "---",
            "",
            "## Health Statistics",
            "",
        ])

        stats = self.health_stats
        if stats:
            lines.extend([
                f"- **Min:** {stats['min']:.2f}",
                f"- **Max:** {stats['max']:.2f}",
                f"- **Mean:** {stats['mean']:.2f}",
                f"- **Median:** {stats['median']:.2f}",
                f"- **StdDev:** {stats['stdev']:.2f}",
            ])

        lines.extend([
            "",
            "---",
            "",
            "## Component Scores by Grade",
            "",
            "| Grade | cycles | elevation | gradients | coupling | isolation |",
            "|-------|--------|-----------|-----------|----------|-----------|",
        ])

        for grade, scores in self.component_stats_by_grade().items():
            row = f"| {grade} |"
            for comp in ["cycles", "elevation", "gradients", "coupling", "isolation"]:
                val = scores.get(comp, 0)
                row += f" {val:.2f} |"
            lines.append(row)

        lines.extend([
            "",
            "**Component Variance (discriminating power):**",
            "",
        ])
        for comp, var in sorted(self.component_variance().items(), key=lambda x: -x[1]):
            lines.append(f"- {comp}: {var:.2f}")

        lines.extend([
            "",
            "---",
            "",
            "## Language Performance",
            "",
            "| Language | Count | Avg Health |",
            "|----------|-------|------------|",
        ])

        for lang, data in list(self.stats_by_language().items())[:10]:
            lines.append(f"| {lang} | {data['count']} | {data['avg_health']:.2f} |")

        lines.extend([
            "",
            "---",
            "",
            "## Failure Breakdown",
            "",
            "| Type | Count |",
            "|------|-------|",
        ])

        for fail_type, count in self.failure_breakdown().items():
            lines.append(f"| {fail_type} | {count} |")

        lines.extend([
            "",
            "---",
            "",
            "## Golden Repos (Grade B)",
            "",
            "| Repo | Health | Nodes | Edges | Language |",
            "|------|--------|-------|-------|----------|",
        ])

        for r in self.golden_repos(10, "B"):
            lines.append(f"| {r.name} | {r.health_index:.2f} | {r.nodes or '-'} | {r.edges or '-'} | {r.language} |")

        lines.extend([
            "",
            "---",
            "",
            "## Worst Performers",
            "",
            "| Repo | Health | Grade | Edge Ratio |",
            "|------|--------|-------|------------|",
        ])

        for r in self.worst_repos(5):
            ratio = f"{r.edge_node_ratio:.1f}" if r.edge_node_ratio else "-"
            lines.append(f"| {r.name} | {r.health_index:.2f} | {r.grade} | {ratio} |")

        return "\n".join(lines)

    def to_json(self) -> dict:
        """Generate structured JSON output."""
        return {
            "meta": self.meta,
            "summary": {
                "total": self.total_repos,
                "successful": self.successful_count,
                "failed": self.failed_count,
                "success_rate": self.success_rate
            },
            "grade_distribution": self.grade_distribution,
            "health_stats": self.health_stats,
            "component_by_grade": self.component_stats_by_grade(),
            "component_variance": self.component_variance(),
            "language_stats": self.stats_by_language(),
            "failure_breakdown": self.failure_breakdown(),
            "golden_repos": [
                {"name": r.name, "health": r.health_index, "grade": r.grade}
                for r in self.golden_repos(10)
            ],
            "worst_repos": [
                {"name": r.name, "health": r.health_index, "grade": r.grade}
                for r in self.worst_repos(5)
            ]
        }


def main():
    parser = argparse.ArgumentParser(description="Analyze batch grade results")
    parser.add_argument("results_file", help="Path to final_results.json")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                        help="Output format (default: markdown)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--golden-repos", type=int, default=10,
                        help="Number of golden repos to show")

    args = parser.parse_args()

    if not Path(args.results_file).exists():
        print(f"Error: File not found: {args.results_file}", file=sys.stderr)
        sys.exit(1)

    analyzer = BatchAnalyzer.from_file(args.results_file)

    if args.format == "markdown":
        output = analyzer.to_markdown()
    else:
        output = json.dumps(analyzer.to_json(), indent=2)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Report written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
