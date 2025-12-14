#!/usr/bin/env python3
"""
🚀 SPECTROMETER V12 - Universal Pattern Detector
Minimal core that orchestrates all components
============================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any

from tree_sitter_engine import TreeSitterUniversalEngine
from particle_classifier import ParticleClassifier
from stats_generator import StatsGenerator
from dependency_analyzer import DependencyAnalyzer
from report_generator import ReportGenerator
from god_class_detector_lite import GodClassDetectorLite

class UniversalPatternDetector:
    """Main orchestrator for universal pattern detection"""

    def __init__(self):
        self.tree_sitter_engine = TreeSitterUniversalEngine()
        self.particle_classifier = ParticleClassifier()
        self.stats_generator = StatsGenerator()
        self.dependency_analyzer = DependencyAnalyzer()
        self.report_generator = ReportGenerator()
        self.god_class_detector = GodClassDetectorLite()

    def analyze_repository(self, repo_path: str, *, output_dir: str | Path | None = None) -> Dict[str, Any]:
        """Analyze entire repository for universal patterns"""
        print(f"🔬 Analyzing repository: {repo_path}")

        # Step 1: Parse all files with Tree-sitter
        print("📂 Parsing files with universal engine...")
        analysis_results = self.tree_sitter_engine.analyze_directory(repo_path)

        # Step 1.5: Extract dependencies (internal/external/stdlib)
        print("🔗 Analyzing dependencies...")
        dependency_summary = self.dependency_analyzer.analyze_repository(repo_path, analysis_results)

        # Step 2: Classify particles with RPBL scores
        print("🔬 Classifying particles with RPBL scores...")
        for result in analysis_results:
            classified_particles = []
            for particle in result.get('particles', []):
                classified = self.particle_classifier.classify_particle(particle)
                classified_particles.append(classified)
            result['particles'] = classified_particles

        # Step 3: Generate comprehensive statistics
        print("📊 Generating comprehensive statistics...")
        comprehensive_results = self.stats_generator.generate_comprehensive_stats(analysis_results)
        comprehensive_results['dependencies'] = dependency_summary
        
        # Step 3.5: God Class Detection
        print("☢️  Scanning for Antimatter (God Classes)...")
        god_results = self.god_class_detector.analyze_repository(repo_path)
        # Convert dataclass instances to dicts for JSON serialization
        from dataclasses import asdict
        comprehensive_results['god_classes'] = [asdict(gc) for gc in god_results['god_classes']]
        comprehensive_results['god_class_summary'] = god_results['summary']
        
        # Merge God Class recommendations
        if 'recommendations' not in comprehensive_results: comprehensive_results['recommendations'] = {}
        comprehensive_results['recommendations']['antimatter'] = god_results['recommendations']

        # Step 4: Save all results
        resolved_output_dir = Path(output_dir) if output_dir is not None else (Path(__file__).parent.parent / "output")
        output_dir = resolved_output_dir.resolve()
        output_files = self.stats_generator.save_results(output_dir)
        report_files = self.report_generator.generate(
            repo_root=repo_path,
            analysis_results=analysis_results,
            comprehensive_results=comprehensive_results,
            output_dir=output_dir,
        )
        output_files.update(report_files)

        print(f"✅ Analysis complete! Results saved to: {output_dir}")

        return {
            'comprehensive_results': comprehensive_results,
            'output_files': output_files,
            'summary': {
                'files_processed': len(analysis_results),
                'particles_detected': len(comprehensive_results['particles']),
                'output_formats': ['JSON', 'TXT', 'CSV']
            }
        }

    def get_quick_stats(self) -> Dict[str, Any]:
        """Get quick statistics about detector capabilities"""
        particle_types = self.particle_classifier.get_all_particle_types()
        supported_languages = self.tree_sitter_engine.supported_languages

        return {
            'detector_version': 'V12.1',
            'supported_languages': list(supported_languages.values()),
            'number_of_languages': len(supported_languages),
            'particle_types_supported': len(particle_types),
            'universal_touchpoints': 22,
            'rpbl_dimensions': 4,
            'output_formats': ['JSON', 'TXT', 'CSV'],
            'performance_target': '1205+ files/second'
        }
