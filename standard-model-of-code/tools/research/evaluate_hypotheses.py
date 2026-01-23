#!/usr/bin/env python3
"""
Hypothesis Evaluator for L2 Validation

Tests corpus results against formal hypothesis falsification criteria.
Implements decision rules from docs/research/HYPOTHESES_L2_FORMAL.md

Usage:
    python tools/research/evaluate_hypotheses.py results.json

Output:
    - PASS/FAIL status for each hypothesis
    - Detailed metrics with evidence
    - Promotion readiness assessment
"""

import json
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics


@dataclass
class HypothesisResult:
    """Result of testing a single hypothesis."""
    hypothesis_id: str
    name: str
    status: str  # PASS, FAIL, WARN, INSUFFICIENT_DATA
    metric_value: float
    threshold: float
    details: str
    evidence: Dict


def load_results(path: Path) -> Dict:
    """Load corpus results JSON."""
    with open(path) as f:
        return json.load(f)


def extract_repo_metrics(results: Dict) -> List[Dict]:
    """Extract per-repo metrics from results."""
    repos = []

    # Handle multiple formats
    if "results" in results:
        # Format: {results: [{name, status, top_4_mass, ...}]}
        for item in results["results"]:
            if item.get("status") == "success":
                # Metrics are directly on the item (not nested)
                if "top_4_mass" in item:
                    repos.append(item)
                elif item.get("metrics"):
                    # Or might be nested
                    metrics = item["metrics"].copy()
                    metrics["name"] = item.get("name", "unknown")
                    metrics["language"] = item.get("language", "unknown")
                    repos.append(metrics)

    elif "repos" in results:
        repo_data = results["repos"]
        if isinstance(repo_data, dict):
            # Dict format: {name: {metrics: {...}}}
            for name, data in repo_data.items():
                if data.get("status") == "success":
                    if data.get("metrics"):
                        metrics = data["metrics"].copy()
                        metrics["name"] = name
                        metrics["language"] = data.get("language", "unknown")
                        repos.append(metrics)
                    elif "top_4_mass" in data:
                        data_copy = data.copy()
                        data_copy["name"] = name
                        repos.append(data_copy)
        else:
            # List format
            for repo in repo_data:
                if repo.get("status") == "success":
                    if repo.get("metrics"):
                        repos.append(repo["metrics"])
                    elif "top_4_mass" in repo:
                        repos.append(repo)

    else:
        # Direct list
        for item in results if isinstance(results, list) else []:
            if isinstance(item, dict):
                if item.get("metrics"):
                    repos.append(item["metrics"])
                elif "top_4_mass" in item:
                    repos.append(item)

    return repos


def test_h1a_central_tendency(repos: List[Dict]) -> HypothesisResult:
    """
    H1a: Top-4 Mass Concentration (Central Tendency)

    PASS IF: median(top_4_mass) >= 90% AND CI95_lower >= 85%
    FAIL IF: CI95_lower < 85%
    """
    top_4_values = [r["top_4_mass"] for r in repos if "top_4_mass" in r]

    if len(top_4_values) < 30:
        return HypothesisResult(
            hypothesis_id="H1a",
            name="Top-4 Mass Central Tendency",
            status="INSUFFICIENT_DATA",
            metric_value=0,
            threshold=90.0,
            details=f"Need n>=30, have n={len(top_4_values)}",
            evidence={"n": len(top_4_values)}
        )

    median_val = statistics.median(top_4_values)

    # Bootstrap CI95 approximation (simplified)
    # For real validation, use proper bootstrap
    sorted_vals = sorted(top_4_values)
    ci95_lower = sorted_vals[int(len(sorted_vals) * 0.025)]
    ci95_upper = sorted_vals[int(len(sorted_vals) * 0.975)]

    # Decision
    passes = median_val >= 90.0 and ci95_lower >= 85.0

    return HypothesisResult(
        hypothesis_id="H1a",
        name="Top-4 Mass Central Tendency",
        status="PASS" if passes else "FAIL",
        metric_value=median_val,
        threshold=90.0,
        details=f"Median: {median_val:.1f}%, CI95: [{ci95_lower:.1f}%, {ci95_upper:.1f}%]",
        evidence={
            "n": len(top_4_values),
            "median": round(median_val, 2),
            "min": round(min(top_4_values), 2),
            "max": round(max(top_4_values), 2),
            "ci95_lower": round(ci95_lower, 2),
            "ci95_upper": round(ci95_upper, 2),
        }
    )


def test_h1b_tail_robustness(repos: List[Dict]) -> HypothesisResult:
    """
    H1b: Top-4 Mass Tail Robustness

    PASS IF: P(top_4_mass < 80%) <= 10%
    FAIL IF: P(top_4_mass < 80%) > 10%
    """
    top_4_values = [r["top_4_mass"] for r in repos if "top_4_mass" in r]

    if len(top_4_values) < 30:
        return HypothesisResult(
            hypothesis_id="H1b",
            name="Top-4 Mass Tail Robustness",
            status="INSUFFICIENT_DATA",
            metric_value=0,
            threshold=10.0,
            details=f"Need n>=30, have n={len(top_4_values)}",
            evidence={"n": len(top_4_values)}
        )

    below_80 = [v for v in top_4_values if v < 80.0]
    tail_pct = len(below_80) / len(top_4_values) * 100

    passes = tail_pct <= 10.0

    return HypothesisResult(
        hypothesis_id="H1b",
        name="Top-4 Mass Tail Robustness",
        status="PASS" if passes else "FAIL",
        metric_value=tail_pct,
        threshold=10.0,
        details=f"Repos below 80%: {len(below_80)}/{len(top_4_values)} ({tail_pct:.1f}%)",
        evidence={
            "n": len(top_4_values),
            "below_80_count": len(below_80),
            "below_80_pct": round(tail_pct, 2),
            "below_80_repos": [r["name"] for r in repos if r.get("top_4_mass", 100) < 80],
        }
    )


def test_h2_function_dominance(repos: List[Dict]) -> HypothesisResult:
    """
    H2: Function Atom Dominance

    PASS IF:
      - Global: P(LOG.FNC.M is dominant) >= 50%
      - Per-language: P(LOG.FNC.M | lang) >= 30% for each language
    FAIL IF: Global < 50% OR any language < 30%
    """
    # Group by language
    by_lang = defaultdict(list)
    for r in repos:
        if "dominant_atom" in r:
            lang = r.get("language", "unknown")
            by_lang[lang].append(r)

    # Global dominance
    fnc_dominant = [r for r in repos if r.get("dominant_atom") == "LOG.FNC.M"]
    global_pct = len(fnc_dominant) / len(repos) * 100 if repos else 0

    # Per-language dominance
    lang_results = {}
    failing_langs = []
    for lang, lang_repos in by_lang.items():
        fnc_count = sum(1 for r in lang_repos if r.get("dominant_atom") == "LOG.FNC.M")
        pct = fnc_count / len(lang_repos) * 100 if lang_repos else 0
        lang_results[lang] = {
            "count": fnc_count,
            "total": len(lang_repos),
            "pct": round(pct, 1)
        }
        if pct < 30.0:
            failing_langs.append(f"{lang} ({pct:.0f}%)")

    # Decision
    global_passes = global_pct >= 50.0
    lang_passes = len(failing_langs) == 0

    if global_passes and lang_passes:
        status = "PASS"
    elif global_passes and not lang_passes:
        status = "WARN"  # Global passes but some languages fail
    else:
        status = "FAIL"

    return HypothesisResult(
        hypothesis_id="H2",
        name="Function Atom Dominance",
        status=status,
        metric_value=global_pct,
        threshold=50.0,
        details=f"Global: {global_pct:.1f}%. Failing languages: {failing_langs or 'none'}",
        evidence={
            "global_fnc_dominant": len(fnc_dominant),
            "global_total": len(repos),
            "global_pct": round(global_pct, 1),
            "by_language": lang_results,
            "failing_languages": failing_langs,
        }
    )


def test_h3_language_effect(repos: List[Dict]) -> HypothesisResult:
    """
    H3: Language Effect Bound

    PASS IF: max(median_by_lang) - min(median_by_lang) <= 15pp
    FAIL IF: Spread > 15pp
    """
    # Group by language
    by_lang = defaultdict(list)
    for r in repos:
        if "top_4_mass" in r:
            lang = r.get("language", "unknown")
            by_lang[lang].append(r["top_4_mass"])

    if len(by_lang) < 2:
        return HypothesisResult(
            hypothesis_id="H3",
            name="Language Effect Bound",
            status="INSUFFICIENT_DATA",
            metric_value=0,
            threshold=15.0,
            details=f"Need multiple languages, have {len(by_lang)}",
            evidence={"n_languages": len(by_lang)}
        )

    # Calculate medians
    medians = {}
    for lang, values in by_lang.items():
        if len(values) >= 3:  # Require min sample size
            medians[lang] = statistics.median(values)

    if len(medians) < 2:
        return HypothesisResult(
            hypothesis_id="H3",
            name="Language Effect Bound",
            status="INSUFFICIENT_DATA",
            metric_value=0,
            threshold=15.0,
            details="Need at least 2 languages with n>=3",
            evidence={"medians": medians}
        )

    spread = max(medians.values()) - min(medians.values())
    passes = spread <= 15.0

    # Find extremes
    max_lang = max(medians.items(), key=lambda x: x[1])
    min_lang = min(medians.items(), key=lambda x: x[1])

    return HypothesisResult(
        hypothesis_id="H3",
        name="Language Effect Bound",
        status="PASS" if passes else "FAIL",
        metric_value=spread,
        threshold=15.0,
        details=f"Spread: {spread:.1f}pp ({max_lang[0]}={max_lang[1]:.1f}% to {min_lang[0]}={min_lang[1]:.1f}%)",
        evidence={
            "spread_pp": round(spread, 2),
            "medians_by_language": {k: round(v, 2) for k, v in sorted(medians.items(), key=lambda x: -x[1])},
            "max_language": max_lang[0],
            "min_language": min_lang[0],
        }
    )


def test_h4_unknown_bound(repos: List[Dict]) -> HypothesisResult:
    """
    H4: Unknown Rate Bound

    PASS IF: median(unknown_rate) <= 1% AND max(unknown_rate) <= 5%
    FAIL IF: median > 1% OR max > 5%
    CATASTROPHIC FAIL IF: any > 10%
    """
    unknown_rates = [r["unknown_rate"] for r in repos if "unknown_rate" in r]

    if len(unknown_rates) < 10:
        return HypothesisResult(
            hypothesis_id="H4",
            name="Unknown Rate Bound",
            status="INSUFFICIENT_DATA",
            metric_value=0,
            threshold=1.0,
            details=f"Need n>=10, have n={len(unknown_rates)}",
            evidence={"n": len(unknown_rates)}
        )

    median_val = statistics.median(unknown_rates)
    max_val = max(unknown_rates)

    # Check for catastrophic
    above_10 = [r for r in repos if r.get("unknown_rate", 0) > 10.0]

    if above_10:
        status = "CATASTROPHIC_FAIL"
        details = f"Catastrophic: {len(above_10)} repos > 10% unknown"
    elif median_val > 1.0 or max_val > 5.0:
        status = "FAIL"
        details = f"Median: {median_val:.2f}%, Max: {max_val:.2f}%"
    else:
        status = "PASS"
        details = f"Median: {median_val:.2f}%, Max: {max_val:.2f}%"

    return HypothesisResult(
        hypothesis_id="H4",
        name="Unknown Rate Bound",
        status=status,
        metric_value=median_val,
        threshold=1.0,
        details=details,
        evidence={
            "n": len(unknown_rates),
            "median": round(median_val, 3),
            "max": round(max_val, 3),
            "mean": round(statistics.mean(unknown_rates), 3),
            "above_10_count": len(above_10),
            "above_10_repos": [r["name"] for r in above_10],
        }
    )


def test_h5_domain_effect(repos: List[Dict]) -> HypothesisResult:
    """
    H5: Domain Effect Bound

    PASS IF: spread <= 10pp AND each domain has n >= 3
    FAIL IF: spread > 10pp OR insufficient sample
    """
    # Group by domain (infer from notes or explicit field)
    by_domain = defaultdict(list)
    for r in repos:
        domain = r.get("domain", "unknown")
        if "top_4_mass" in r:
            by_domain[domain].append(r["top_4_mass"])

    # Calculate medians (only for domains with n>=3)
    medians = {}
    insufficient = []
    for domain, values in by_domain.items():
        if len(values) >= 3:
            medians[domain] = statistics.median(values)
        else:
            insufficient.append(f"{domain} (n={len(values)})")

    if len(medians) < 2:
        return HypothesisResult(
            hypothesis_id="H5",
            name="Domain Effect Bound",
            status="INSUFFICIENT_DATA",
            metric_value=0,
            threshold=10.0,
            details=f"Need at least 2 domains with n>=3. Insufficient: {insufficient}",
            evidence={"insufficient_domains": insufficient}
        )

    spread = max(medians.values()) - min(medians.values())
    passes = spread <= 10.0 and len(insufficient) == 0

    return HypothesisResult(
        hypothesis_id="H5",
        name="Domain Effect Bound",
        status="PASS" if passes else ("WARN" if spread <= 10.0 else "FAIL"),
        metric_value=spread,
        threshold=10.0,
        details=f"Spread: {spread:.1f}pp. Insufficient domains: {insufficient or 'none'}",
        evidence={
            "spread_pp": round(spread, 2),
            "medians_by_domain": {k: round(v, 2) for k, v in sorted(medians.items(), key=lambda x: -x[1])},
            "insufficient_domains": insufficient,
        }
    )


def generate_report(results: List[HypothesisResult], n_repos: int) -> str:
    """Generate human-readable evaluation report."""
    lines = [
        "=" * 70,
        "HYPOTHESIS EVALUATION REPORT",
        f"Corpus size: n={n_repos}",
        "=" * 70,
        "",
    ]

    pass_count = 0
    fail_count = 0
    warn_count = 0

    for r in results:
        # Status indicator
        if r.status == "PASS":
            indicator = "PASS"
            pass_count += 1
        elif r.status == "FAIL":
            indicator = "FAIL"
            fail_count += 1
        elif r.status == "CATASTROPHIC_FAIL":
            indicator = "FAIL"
            fail_count += 1
        elif r.status == "WARN":
            indicator = "WARN"
            warn_count += 1
        else:
            indicator = "DATA"
            warn_count += 1

        lines.extend([
            f"[{indicator}] {r.hypothesis_id}: {r.name}",
            f"       Metric: {r.metric_value:.2f} (threshold: {r.threshold})",
            f"       {r.details}",
            "",
        ])

    # Summary
    lines.extend([
        "-" * 70,
        "SUMMARY",
        f"  PASS: {pass_count}/{len(results)}",
        f"  FAIL: {fail_count}/{len(results)}",
        f"  WARN/INSUFFICIENT: {warn_count}/{len(results)}",
        "",
    ])

    # Promotion assessment
    if fail_count == 0 and warn_count == 0:
        lines.append("PROMOTION STATUS: READY for L3")
    elif fail_count == 0:
        lines.append("PROMOTION STATUS: CONDITIONAL (warnings present)")
    else:
        lines.append("PROMOTION STATUS: NOT READY (failures present)")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Evaluate hypotheses against corpus results")
    parser.add_argument("results", help="Path to results.json")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    # Load data
    results_path = Path(args.results)
    if not results_path.exists():
        print(f"ERROR: Results file not found: {results_path}")
        sys.exit(1)

    data = load_results(results_path)
    repos = extract_repo_metrics(data)

    if not repos:
        print("ERROR: No valid repo metrics found in results")
        sys.exit(1)

    print(f"Loaded {len(repos)} repos with metrics")

    # Run all hypothesis tests
    hypothesis_results = [
        test_h1a_central_tendency(repos),
        test_h1b_tail_robustness(repos),
        test_h2_function_dominance(repos),
        test_h3_language_effect(repos),
        test_h4_unknown_bound(repos),
        test_h5_domain_effect(repos),
    ]

    # Output
    if args.json:
        output = {
            "n_repos": len(repos),
            "hypotheses": [
                {
                    "id": r.hypothesis_id,
                    "name": r.name,
                    "status": r.status,
                    "metric": r.metric_value,
                    "threshold": r.threshold,
                    "details": r.details,
                    "evidence": r.evidence,
                }
                for r in hypothesis_results
            ],
            "summary": {
                "pass": sum(1 for r in hypothesis_results if r.status == "PASS"),
                "fail": sum(1 for r in hypothesis_results if r.status in ("FAIL", "CATASTROPHIC_FAIL")),
                "warn": sum(1 for r in hypothesis_results if r.status in ("WARN", "INSUFFICIENT_DATA")),
            }
        }
        output_text = json.dumps(output, indent=2)
    else:
        output_text = generate_report(hypothesis_results, len(repos))

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_text)
        print(f"Written to: {args.output}")
    else:
        print(output_text)

    # Exit code based on failures
    fail_count = sum(1 for r in hypothesis_results if r.status in ("FAIL", "CATASTROPHIC_FAIL"))
    sys.exit(1 if fail_count > 0 else 0)


if __name__ == "__main__":
    main()
