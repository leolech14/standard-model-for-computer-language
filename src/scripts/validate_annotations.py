#!/usr/bin/env python3
"""
Annotation Validator

Compare manual annotations against Collider predictions and compute accuracy metrics.
"""

import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def load_annotations(csv_path: Path) -> List[Dict]:
    """Load annotation CSV."""
    annotations = []
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only include rows with manual annotations
            if row['annotated_role'].strip():
                annotations.append(row)
    return annotations

def compute_metrics(annotations: List[Dict]) -> Dict:
    """Compute accuracy metrics."""
    total = len(annotations)
    
    # Overall accuracy
    role_correct = sum(1 for a in annotations 
                      if a['predicted_role'].lower() == a['annotated_role'].lower())
    
    # Per-role metrics
    role_stats = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0})
    
    for a in annotations:
        predicted = a['predicted_role'].lower()
        actual = a['annotated_role'].lower()
        
        if predicted == actual:
            role_stats[actual]['tp'] += 1
        else:
            role_stats[predicted]['fp'] += 1
            role_stats[actual]['fn'] += 1
    
    # Compute precision, recall, F1 per role
    role_metrics = {}
    for role, stats in role_stats.items():
        tp, fp, fn = stats['tp'], stats['fp'], stats['fn']
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        role_metrics[role] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': tp + fn
        }
    
    # Confusion matrix (most common errors)
    confusion = defaultdict(int)
    for a in annotations:
        if a['predicted_role'].lower() != a['annotated_role'].lower():
            pair = (a['annotated_role'], a['predicted_role'])
            confusion[pair] += 1
    
    return {
        'total': total,
        'correct': role_correct,
        'accuracy': role_correct / total if total > 0 else 0,
        'role_metrics': role_metrics,
        'confusion': dict(sorted(confusion.items(), key=lambda x: x[1], reverse=True)[:10])
    }

def generate_report(metrics: Dict, output_path: Path) -> None:
    """Generate markdown report."""
    with open(output_path, 'w') as f:
        f.write("# Mini-Validation Results\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Total samples**: {metrics['total']}\n")
        f.write(f"- **Correct predictions**: {metrics['correct']}\n")
        f.write(f"- **Accuracy**: {metrics['accuracy']:.1%}\n\n")
        
        # Verdict
        if metrics['accuracy'] >= 0.85:
            f.write("✅ **PASS**: Accuracy ≥ 85% - Claims validated!\n\n")
            f.write("**Recommendation**: Proceed confidence to full benchmark (Roadmap 1)\n\n")
        elif metrics['accuracy'] >= 0.75:
            f.write("⚠️ **MARGINAL**: Accuracy 75-85% - Needs improvement\n\n")
            f.write("**Recommendation**: Refine patterns, re-test before full benchmark\n\n")
        else:
            f.write("❌ **FAIL**: Accuracy < 75% - Significant issues\n\n")
            f.write("**Recommendation**: Debug patterns before proceeding\n\n")
        
        # Per-role metrics
        f.write("## Per-Role Performance\n\n")
        f.write("| Role | Precision | Recall | F1 | Support |\n")
        f.write("|------|-----------|--------|----|---------|\n")
        
        for role, stats in sorted(metrics['role_metrics'].items(), 
                                 key=lambda x: x[1]['support'], reverse=True):
            f.write(f"| {role} | {stats['precision']:.1%} | {stats['recall']:.1%} | "
                   f"{stats['f1']:.1%} | {stats['support']} |\n")
        
        # Common errors
        f.write("\n## Most Common Errors\n\n")
        f.write("| Actual | Predicted | Count |\n")
        f.write("|--------|-----------|-------|\n")
        
        for (actual, predicted), count in list(metrics['confusion'].items())[:10]:
            f.write(f"| {actual} | {predicted} | {count} |\n")
        
        f.write("\n---\n\n")
        f.write("**Next Steps:**\n")
        if metrics['accuracy'] >= 0.85:
            f.write("1. Start Roadmap 1 (Benchmark Dataset)\n")
            f.write("2. Use these results in paper draft\n")
        else:
            f.write("1. Analyze errors (see table above)\n")
            f.write("2. Refine pattern matching rules\n")
            f.write("3. Re-sample and re-test\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate manual annotations')
    parser.add_argument('--input', type=Path, 
                       default=Path('data/mini_validation_samples.csv'),
                       help='Annotated CSV file')
    parser.add_argument('--output', type=Path,
                       default=Path('results/mini_validation_report.md'),
                       help='Output report path')
    
    args = parser.parse_args()
    
    # Load annotations
    print(f"Loading annotations from {args.input}...")
    annotations = load_annotations(args.input)
    
    if len(annotations) == 0:
        print("❌ No annotations found!")
        print("Make sure you've filled in the 'annotated_role' column")
        return
    
    print(f"Found {len(annotations)} annotated samples")
    
    # Compute metrics
    print("Computing metrics...")
    metrics = compute_metrics(annotations)
    
    # Generate report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    generate_report(metrics, args.output)
    
    print(f"\n✅ Report generated: {args.output}")
    print(f"\n📊 Results:")
    print(f"  Accuracy: {metrics['accuracy']:.1%}")
    print(f"  Samples: {metrics['correct']}/{metrics['total']}")
    
    if metrics['accuracy'] >= 0.85:
        print(f"\n✅ VALIDATION PASSED - Claims confirmed!")
    elif metrics['accuracy'] >= 0.75:
        print(f"\n⚠️  MARGINAL - Consider refinement")
    else:
        print(f"\n❌ VALIDATION FAILED - Needs work")

if __name__ == '__main__':
    main()
