#!/usr/bin/env python3
"""
🔬 SPECTROMETER V12 - God Class Antimatter Detector
Detects oversized classes violating single responsibility across polyglot codebases
============================================================================
"""

import json
import re
import math
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

@dataclass
class GodClassMetrics:
    """Metrics for detecting God Classes"""
    class_name: str
    file_path: str
    line_number: int
    language: str

    # Core metrics
    lines_of_code: int
    method_count: int
    responsibility_count: int
    dependency_count: int
    touchpoint_overload: float

    # Touchpoint analysis
    coordination_touchpoints: int
    business_logic_touchpoints: int
    data_access_touchpoints: int
    ui_touchpoints: int
    infrastructure_touchpoints: int

    # Risk assessment
    antimatter_risk_score: float
    is_god_class: bool
    suggested_refactors: List[str]

class GodClassDetector:
    """Universal God Class detector using Tree-sitter and touchpoint analysis"""

    def __init__(self):
        # Touchpoint indicators for God Class detection
        self.god_class_touchpoints = {
            'coordination': [
                r'\b(manage|coordinate|orchestrate|control|supervise)\b',
                r'\b(handle|process|execute|perform|run)\b'
            ],
            'business_logic': [
                r'\b(calculate|compute|validate|verify|transform)\b',
                r'\b(process|apply|enforce|implement)\b'
            ],
            'data_access': [
                r'\b(save|load|find|delete|query|persist)\b',
                r'\b(database|db|sql|repository|dao)\b'
            ],
            'ui_interaction': [
                r'\b(render|display|show|present|view)\b',
                r'\b(gui|ui|interface|component|widget)\b'
            ],
            'infrastructure': [
                r'\b(network|http|api|rest|soap)\b',
                r'\b(file|io|system|config|log)\b'
            ],
            'validation': [
                r'\b(check|ensure|verify|validate)\b',
                r'\b(assert|require|guard)\b'
            ]
        }

        # Language-specific patterns
        self.language_patterns = {
            'python': {
                'class_pattern': r'^\s*class\s+(\w+).*:',
                'method_pattern': r'^\s*def\s+(\w+)\s*\(',
                'import_pattern': r'^\s*(import|from)\s+',
                'comment_pattern': r'#.*$'
            },
            'java': {
                'class_pattern': r'^\s*(public\s+)?(private\s+)?(protected\s+)?class\s+(\w+)',
                'method_pattern': r'^\s*(public\s+)?(private\s+)?(protected\s+)?(static\s+)?(\w+)\s*\(',
                'import_pattern': r'^\s*import\s+',
                'comment_pattern': r'//.*$|/\*.*?\*/'
            },
            'typescript': {
                'class_pattern': r'^\s*(export\s+)?(abstract\s+)?class\s+(\w+)',
                'method_pattern': r'^\s*(public\s+)?(private\s+)?(protected\s+)?(async\s+)?(\w+)\s*\(',
                'import_pattern': r'^\s*import\s+.*from\s+',
                'comment_pattern': r'//.*$|/\*.*?\*/'
            },
            'go': {
                'class_pattern': r'^\s*type\s+(\w+)\s+struct\s*{',
                'method_pattern': r'^\s*func\s+\([^)]*\)\s*(\w+)\s*\(',
                'import_pattern': r'^\s*import\s+',
                'comment_pattern': r'//.*$'
            }
        }

    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze entire repository for God Classes"""
        print(f"🔍 Analyzing repository: {repo_path}")

        results = {
            'metadata': {
                'repository_path': repo_path,
                'analysis_date': '2025-12-04',
                'detector_version': 'V12.1'
            },
            'summary': {
                'total_classes_analyzed': 0,
                'god_classes_found': 0,
                'antimatter_risk_classes': 0,
                'languages_detected': set(),
                'average_risk_score': 0.0
            },
            'god_classes': [],
            'risk_distribution': {
                'low_risk': 0,
                'medium_risk': 0,
                'high_risk': 0,
                'critical_risk': 0
            },
            'recommendations': {}
        }

        # Find all source files
        source_files = self._find_source_files(repo_path)
        print(f"📁 Found {len(source_files)} source files")

        # Analyze each file
        for file_path in source_files:
            language = self._detect_language(file_path)
            if language:
                results['summary']['languages_detected'].add(language)
                god_classes = self._analyze_file(file_path, language)
                results['god_classes'].extend(god_classes)

        # Update summary statistics
        results['summary']['total_classes_analyzed'] = len(results['god_classes'])
        results['summary']['god_classes_found'] = len([gc for gc in results['god_classes'] if gc.is_god_class])
        results['summary']['antimatter_risk_classes'] = len([gc for gc in results['god_classes'] if gc.antimatter_risk_score > 80])
        results['summary']['languages_detected'] = list(results['summary']['languages_detected'])

        if results['god_classes']:
            avg_risk = sum(gc.antimatter_risk_score for gc in results['god_classes']) / len(results['god_classes'])
            results['summary']['average_risk_score'] = avg_risk

        # Categorize risk distribution
        for gc in results['god_classes']:
            if gc.antimatter_risk_score > 90:
                results['risk_distribution']['critical_risk'] += 1
            elif gc.antimatter_risk_score > 80:
                results['risk_distribution']['high_risk'] += 1
            elif gc.antimatter_risk_score > 60:
                results['risk_distribution']['medium_risk'] += 1
            else:
                results['risk_distribution']['low_risk'] += 1

        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results['god_classes'])

        print(f"🎯 Analysis complete: {results['summary']['god_classes_found']} God Classes detected")
        return results

    def _find_source_files(self, repo_path: str) -> List[str]:
        """Find all relevant source files"""
        source_extensions = ['.py', '.java', '.ts', '.js', '.go', '.rs', '.kt', '.cs']
        source_files = []

        for root, dirs, files in Path(repo_path).walk():
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'target', 'build', 'dist']]

            for file in files:
                if any(file.endswith(ext) for ext in source_extensions):
                    source_files.append(str(root / file))

        return source_files

    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.java': 'java',
            '.ts': 'typescript',
            '.js': 'javascript',
            '.go': 'go',
            '.rs': 'rust',
            '.kt': 'kotlin',
            '.cs': 'c_sharp'
        }
        return language_map.get(ext)

    def _analyze_file(self, file_path: str, language: str) -> List[GodClassMetrics]:
        """Analyze a single file for God Classes"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
            return []

        lines = content.split('\n')
        patterns = self.language_patterns.get(language, self.language_patterns['python'])

        god_classes = []
        current_class = None
        class_start_line = 0
        class_lines = []

        for i, line in enumerate(lines, 1):
            # Skip comments and empty lines
            if not line.strip() or re.search(patterns['comment_pattern'], line):
                continue

            # Detect class definition
            class_match = re.search(patterns['class_pattern'], line)
            if class_match:
                # Save previous class if exists
                if current_class:
                    metrics = self._analyze_class(
                        current_class, '\n'.join(class_lines),
                        class_start_line, file_path, language
                    )
                    if metrics:
                        god_classes.append(metrics)

                # Start new class
                class_name = class_match.groups()[-1]
                current_class = class_name
                class_start_line = i
                class_lines = [line]
                continue

            # Add line to current class
            if current_class:
                class_lines.append(line)

        # Don't forget the last class
        if current_class:
            metrics = self._analyze_class(
                current_class, '\n'.join(class_lines),
                class_start_line, file_path, language
            )
            if metrics:
                god_classes.append(metrics)

        return god_classes

    def _analyze_class(self, class_name: str, class_content: str,
                      line_number: int, file_path: str, language: str) -> Optional[GodClassMetrics]:
        """Analyze a single class for God Class characteristics"""
        lines = class_content.split('\n')
        patterns = self.language_patterns.get(language, self.language_patterns['python'])

        # Count methods
        method_count = len(re.findall(patterns['method_pattern'], class_content))

        # Count imports/dependencies
        dependency_count = len(re.findall(patterns['import_pattern'], class_content))

        # Count lines of code (excluding empty lines and comments)
        loc_lines = [line for line in lines if line.strip() and not re.search(patterns['comment_pattern'], line)]
        lines_of_code = len(loc_lines)

        # Analyze touchpoints
        touchpoint_counts = defaultdict(int)
        class_content_lower = class_content.lower()

        for touchpoint, patterns_list in self.god_class_touchpoints.items():
            for pattern in patterns_list:
                matches = re.findall(pattern, class_content_lower)
                touchpoint_counts[touchpoint] += len(matches)

        # Calculate responsibility overload
        responsibility_count = sum(1 for count in touchpoint_counts.values() if count > 0)

        # Calculate touchpoint overload score
        total_touchpoints = sum(touchpoint_counts.values())
        max_expected_touchpoints = max(10, method_count * 2)  # Reasonable baseline
        touchpoint_overload = min(100, (total_touchpoints / max_expected_touchpoints) * 100)

        # Calculate antimatter risk score
        risk_factors = {
            'size_overload': min(30, (lines_of_code / 200) * 10),  # 30 points max
            'method_overload': min(25, (method_count / 20) * 10),  # 25 points max
            'responsibility_overload': min(25, responsibility_count * 5),  # 25 points max
            'touchpoint_overload': min(20, touchpoint_overload)  # 20 points max
        }

        antimatter_risk_score = sum(risk_factors.values())

        # Determine if it's a God Class
        is_god_class = (
            lines_of_code > 100 and
            method_count > 10 and
            responsibility_count >= 3 and
            antimatter_risk_score > 70
        )

        # Generate refactoring suggestions
        suggested_refactors = self._generate_refactor_suggestions(
            touchpoint_counts, method_count, lines_of_code
        )

        return GodClassMetrics(
            class_name=class_name,
            file_path=file_path,
            line_number=line_number,
            language=language,
            lines_of_code=lines_of_code,
            method_count=method_count,
            responsibility_count=responsibility_count,
            dependency_count=dependency_count,
            touchpoint_overload=touchpoint_overload,
            coordination_touchpoints=touchpoint_counts['coordination'],
            business_logic_touchpoints=touchpoint_counts['business_logic'],
            data_access_touchpoints=touchpoint_counts['data_access'],
            ui_touchpoints=touchpoint_counts['ui_interaction'],
            infrastructure_touchpoints=touchpoint_counts['infrastructure'],
            antimatter_risk_score=antimatter_risk_score,
            is_god_class=is_god_class,
            suggested_refactors=suggested_refactors
        )

    def _generate_refactor_suggestions(self, touchpoint_counts: Dict, method_count: int, loc: int) -> List[str]:
        """Generate refactoring suggestions based on touchpoint analysis"""
        suggestions = []

        if touchpoint_counts['data_access'] > 3:
            suggestions.append("Extract Repository pattern for data access")

        if touchpoint_counts['business_logic'] > 5:
            suggestions.append("Extract Domain Services for business logic")

        if touchpoint_counts['ui_interaction'] > 2:
            suggestions.append("Separate UI Controller from business logic")

        if touchpoint_counts['coordination'] > 4:
            suggestions.append("Extract Service Coordinator")

        if touchpoint_counts['infrastructure'] > 3:
            suggestions.append("Extract Infrastructure Layer")

        if method_count > 20:
            suggestions.append(f"Split into {math.ceil(method_count / 10)} focused classes")

        if loc > 300:
            suggestions.append("Consider Composite pattern for large class")

        # Domain-specific suggestions
        if touchpoint_counts['data_access'] > 0 and touchpoint_counts['business_logic'] > 0:
            suggestions.append("Apply DDD: Entity + Repository + Domain Service")

        return list(set(suggestions))  # Remove duplicates

    def _generate_recommendations(self, god_classes: List[GodClassMetrics]) -> Dict[str, Any]:
        """Generate high-level recommendations"""
        recommendations = {
            'priority_actions': [],
            'architectural_patterns': [],
            'risk_mitigation': [],
            'refactoring_strategy': []
        }

        # Count high-risk classes
        critical_classes = [gc for gc in god_classes if gc.antimatter_risk_score > 90]
        high_risk_classes = [gc for gc in god_classes if 80 < gc.antimatter_risk_score <= 90]

        if critical_classes:
            recommendations['priority_actions'].append(
                f"IMMEDIATE: Refactor {len(critical_classes)} critical God Classes (>90% risk)"
            )

        if high_risk_classes:
            recommendations['priority_actions'].append(
                f"HIGH: Address {len(high_risk_classes)} high-risk God Classes (80-90% risk)"
            )

        # Common patterns to apply
        all_refactors = [refactor for gc in god_classes for refactor in gc.suggested_refactors]
        refactor_counts = defaultdict(int)
        for refactor in all_refactors:
            refactor_counts[refactor] += 1

        # Top recommendations
        top_refactors = sorted(refactor_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        recommendations['architectural_patterns'] = [refactor for refactor, count in top_refactors]

        # Risk mitigation
        recommendations['risk_mitigation'] = [
            "Implement code review thresholds for class size (>200 LOC)",
            "Automated detection in CI/CD pipeline",
            "Architectural fitness functions for single responsibility",
            "Regular refactoring sprints for identified God Classes"
        ]

        # Strategy
        recommendations['refactoring_strategy'] = [
            "Start with highest risk classes first",
            "Extract one responsibility at a time",
            "Maintain test coverage during refactoring",
            "Apply Strangler Fig pattern for gradual extraction"
        ]

        return recommendations

    def generate_3d_visualization(self, god_classes: List[GodClassMetrics], output_path: str):
        """Generate 3D visualization with exploding nodes for God Classes"""
        print(f"📊 Generating 3D visualization...")

        fig = plt.figure(figsize=(16, 12))
        ax = fig.add_subplot(111, projection='3d')

        # Prepare data
        x = []  # Lines of Code
        y = []  # Method Count
        z = []  # Touchpoint Overload
        colors = []
        sizes = []

        for gc in god_classes:
            x.append(gc.lines_of_code)
            y.append(gc.method_count)
            z.append(gc.touchpoint_overload)

            # Color based on risk level
            if gc.antimatter_risk_score > 90:
                colors.append('red')  # Critical
            elif gc.antimatter_risk_score > 80:
                colors.append('orange')  # High
            elif gc.antimatter_risk_score > 60:
                colors.append('yellow')  # Medium
            else:
                colors.append('green')  # Low

            # Size based on risk score (exploding effect for high risk)
            base_size = 50
            explosion_factor = 1 + (gc.antimatter_risk_score / 100) * 3
            sizes.append(base_size * explosion_factor)

        # Create scatter plot
        scatter = ax.scatter(x, y, z, c=colors, s=sizes, alpha=0.7, edgecolors='black', linewidth=2)

        # Add labels for God Classes
        god_class_data = [(gc.lines_of_code, gc.method_count, gc.touchpoint_overload, gc.class_name)
                         for gc in god_classes if gc.is_god_class]

        for x_val, y_val, z_val, label in god_class_data:
            ax.text(x_val, y_val, z_val, label, fontsize=8, weight='bold')

        # Set labels and title
        ax.set_xlabel('Lines of Code', fontsize=12, weight='bold')
        ax.set_ylabel('Method Count', fontsize=12, weight='bold')
        ax.set_zlabel('Touchpoint Overload (%)', fontsize=12, weight='bold')
        ax.set_title('🔬 God Class Antimatter Detector - 3D Risk Visualization\n'
                   'Red: Critical (>90%) | Orange: High (80-90%) | Yellow: Medium (60-80%) | Green: Low',
                   fontsize=14, weight='bold', pad=20)

        # Add legend
        legend_elements = [
            plt.scatter([], [], c='red', s=200, label='Critical Risk (>90%)'),
            plt.scatter([], [], c='orange', s=150, label='High Risk (80-90%)'),
            plt.scatter([], [], c='yellow', s=100, label='Medium Risk (60-80%)'),
            plt.scatter([], [], c='green', s=50, label='Low Risk (<60%)')
        ]
        ax.legend(handles=legend_elements, loc='upper left')

        # Add grid
        ax.grid(True, alpha=0.3)

        # Adjust viewing angle for better visualization
        ax.view_init(elev=20, azim=45)

        # Save plot
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ 3D visualization saved to: {output_path}")

        # Also create a 2D risk distribution chart
        self._create_risk_distribution_chart(god_classes, output_path.replace('.png', '_risk_dist.png'))

    def _create_risk_distribution_chart(self, god_classes: List[GodClassMetrics], output_path: str):
        """Create 2D risk distribution chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Risk distribution histogram
        risk_scores = [gc.antimatter_risk_score for gc in god_classes]
        ax1.hist(risk_scores, bins=20, color='red', alpha=0.7, edgecolor='black')
        ax1.axvline(x=80, color='darkred', linestyle='--', linewidth=2, label='Antimatter Risk Threshold (80%)')
        ax1.set_xlabel('Antimatter Risk Score', fontsize=12, weight='bold')
        ax1.set_ylabel('Number of Classes', fontsize=12, weight='bold')
        ax1.set_title('Risk Score Distribution', fontsize=14, weight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Risk by language
        languages = list(set(gc.language for gc in god_classes))
        risk_by_language = {lang: [] for lang in languages}

        for gc in god_classes:
            risk_by_language[gc.language].append(gc.antimatter_risk_score)

        ax2.boxplot([risk_by_language[lang] for lang in languages], labels=languages)
        ax2.axhline(y=80, color='darkred', linestyle='--', linewidth=2, label='Antimatter Risk Threshold')
        ax2.set_xlabel('Programming Language', fontsize=12, weight='bold')
        ax2.set_ylabel('Antimatter Risk Score', fontsize=12, weight='bold')
        ax2.set_title('Risk Distribution by Language', fontsize=14, weight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Risk distribution chart saved to: {output_path}")

# Example usage and testing
if __name__ == "__main__":
    detector = GodClassDetector()

    # Test on current directory
    results = detector.analyze_repository('.')

    # Generate visualizations
    if results['god_classes']:
        detector.generate_3d_visualization(
            results['god_classes'],
            'god_class_analysis_3d.png'
        )

        # Save detailed results
        with open('god_class_analysis.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"Total Classes: {results['summary']['total_classes_analyzed']}")
        print(f"God Classes: {results['summary']['god_classes_found']}")
        print(f"Antimatter Risk: {results['summary']['antimatter_risk_classes']}")
        print(f"Average Risk Score: {results['summary']['average_risk_score']:.1f}%")