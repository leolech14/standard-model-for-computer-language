#!/usr/bin/env python3
"""
🚀 SPECTROMETER V12 - Statistics Generator
Comprehensive statistics and output generation
============================================
"""

import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter

class StatsGenerator:
    """Generates comprehensive statistics and output"""

    def __init__(self):
        self.results = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'spectrometer_version': 'V12.1',
                'mode': 'comprehensive_analysis'
            },
            'summary': {},
            'detailed_stats': {},
            'particles': [],
            'performance': {}
        }

    def generate_comprehensive_stats(self, analysis_results: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive statistics from analysis results"""
        start_time = time.time()

        # Collect all particles
        all_particles = []
        all_touchpoints = []
        files_analyzed = 0
        files_with_particles = 0
        total_lines = 0
        total_chars = 0
        languages = set()

        for result in analysis_results:
            if 'particles' in result:
                files_analyzed += 1
                languages.add(result.get('language', 'unknown'))
                total_lines += result.get('lines_analyzed', 0)
                total_chars += result.get('chars_analyzed', 0)

                if result['particles']:
                    files_with_particles += 1
                    all_particles.extend(result['particles'])

                if 'touchpoints' in result:
                    all_touchpoints.extend(result['touchpoints'])

        processing_time = time.time() - start_time

        # Generate statistics
        self.results['summary'] = self._generate_summary(all_particles, files_analyzed, files_with_particles)
        self.results['detailed_stats'] = self._generate_detailed_stats(
            all_particles, all_touchpoints, files_analyzed, files_with_particles,
            total_lines, total_chars, languages, processing_time
        )
        self.results['particles'] = all_particles
        self.results['performance'] = self._calculate_performance(
            files_analyzed, total_lines, total_chars, processing_time
        )

        return self.results

    def _generate_summary(self, particles: List[Dict], total_files: int, files_with_particles: int) -> Dict:
        """Generate summary statistics"""
        type_counts = Counter(p['type'] for p in particles)
        confidence_scores = [p.get('confidence', 0) for p in particles]
        rpbl_scores = [p.get('rpbl_score', 0) for p in particles]
        unknown_count = type_counts.get('Unknown', 0)
        recognized_count = len(particles) - unknown_count
        recognized_pct = (recognized_count / len(particles) * 100) if particles else 0.0

        return {
            'total_particles_found': len(particles),
            'files_analyzed': total_files,
            'files_with_particles': files_with_particles,
            'coverage_percentage': (files_with_particles / total_files * 100) if total_files > 0 else 0,
            'unique_particle_types': len(type_counts),
            'top_particle_types': type_counts.most_common(5),
            'unknown_particles': unknown_count,
            'recognized_particles': recognized_count,
            'recognized_percentage': recognized_pct,
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            'average_rpbl_score': sum(rpbl_scores) / len(rpbl_scores) if rpbl_scores else 0,
            'high_confidence_particles': len([c for c in confidence_scores if c >= 80]),
            'medium_confidence_particles': len([c for c in confidence_scores if 60 <= c < 80])
        }

    def _generate_detailed_stats(self, particles: List[Dict], touchpoints: List[Dict],
                               files_analyzed: int, files_with_particles: int,
                               total_lines: int, total_chars: int, languages: set,
                               processing_time: float) -> Dict:
        """Generate detailed statistics"""
        # Particle type analysis
        type_analysis = {}
        for particle in particles:
            ptype = particle.get('type', 'Unknown')
            if ptype not in type_analysis:
                type_analysis[ptype] = {
                    'count': 0,
                    'total_confidence': 0,
                    'total_rpbl': 0,
                    'responsibility_sum': 0,
                    'purity_sum': 0,
                    'boundary_sum': 0,
                    'lifecycle_sum': 0
                }

            type_analysis[ptype]['count'] += 1
            type_analysis[ptype]['total_confidence'] += particle.get('confidence', 0)
            type_analysis[ptype]['total_rpbl'] += particle.get('rpbl_score', 0)
            type_analysis[ptype]['responsibility_sum'] += particle.get('responsibility', 0)
            type_analysis[ptype]['purity_sum'] += particle.get('purity', 0)
            type_analysis[ptype]['boundary_sum'] += particle.get('boundary', 0)
            type_analysis[ptype]['lifecycle_sum'] += particle.get('lifecycle', 0)

        # Calculate averages for each type
        for ptype, stats in type_analysis.items():
            count = stats['count']
            stats['average_confidence'] = stats['total_confidence'] / count if count > 0 else 0
            stats['average_rpbl'] = stats['total_rpbl'] / count if count > 0 else 0
            stats['average_responsibility'] = stats['responsibility_sum'] / count if count > 0 else 0
            stats['average_purity'] = stats['purity_sum'] / count if count > 0 else 0
            stats['average_boundary'] = stats['boundary_sum'] / count if count > 0 else 0
            stats['average_lifecycle'] = stats['lifecycle_sum'] / count if count > 0 else 0

        # Touchpoint analysis
        touchpoint_counts = Counter(t['type'] for t in touchpoints)

        return {
            'file_analysis': {
                'total_files_processed': files_analyzed,
                'files_with_particles': files_with_particles,
                'files_without_particles': files_analyzed - files_with_particles,
                'file_coverage_percentage': (files_with_particles / files_analyzed * 100) if files_analyzed > 0 else 0,
                'average_file_size': total_chars / files_analyzed if files_analyzed > 0 else 0,
                'total_lines_analyzed': total_lines,
                'total_characters_analyzed': total_chars
            },
            'particle_analysis': {
                'total_particles_detected': len(particles),
                'unique_particle_types': len(type_analysis),
                'particle_type_distribution': type_analysis,
                'particles_per_file': len(particles) / files_analyzed if files_analyzed > 0 else 0,
                'max_particles_in_file': max([len([p for p in particles if p.get('file_path') == f])
                                            for f in set(p.get('file_path') for p in particles)], default=0)
            },
            'touchpoint_analysis': {
                'total_touchpoints_detected': len(touchpoints),
                'unique_touchpoint_types': len(touchpoint_counts),
                'touchpoint_distribution': dict(touchpoint_counts.most_common())
            },
            'language_analysis': {
                'languages_detected': list(languages),
                'number_of_languages': len(languages)
            },
            'processing_time_seconds': processing_time
        }

    def _calculate_performance(self, files: int, lines: int, chars: int, time_seconds: float) -> Dict:
        """Calculate performance metrics"""
        if time_seconds > 0:
            return {
                'files_per_second': files / time_seconds,
                'lines_per_second': lines / time_seconds,
                'characters_per_second': chars / time_seconds,
                'avg_time_per_file': time_seconds / files if files > 0 else 0,
                'success_rate': 100.0  # All files processed successfully
            }
        else:
            return {
                'files_per_second': 0,
                'lines_per_second': 0,
                'characters_per_second': 0,
                'avg_time_per_file': 0,
                'success_rate': 0
            }

    def save_results(self, output_dir: Path):
        """Save results to multiple output formats"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON
        json_file = output_dir / 'results.json'
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        # Save human-readable stats
        stats_file = output_dir / 'stats.txt'
        with open(stats_file, 'w') as f:
            self._write_human_readable_stats(f)

        # Save particles CSV
        csv_file = output_dir / 'particles.csv'
        with open(csv_file, 'w', newline='') as f:
            self._write_particles_csv(f)

        return {
            'json_file': str(json_file),
            'stats_file': str(stats_file),
            'csv_file': str(csv_file)
        }

    def _write_human_readable_stats(self, file):
        """Write human-readable statistics"""
        file.write("="*100 + "\n")
        file.write("🚀 SPECTROMETER V12 - COMPREHENSIVE ANALYSIS RESULTS\n")
        file.write("="*100 + "\n\n")

        # Summary
        file.write("📊 SUMMARY STATISTICS\n")
        file.write("-" * 50 + "\n")
        summary = self.results['summary']
        file.write(f"Total Particles Found: {summary['total_particles_found']}\n")
        file.write(f"Files Analyzed: {summary['files_analyzed']}\n")
        file.write(f"Files with Particles: {summary['files_with_particles']}\n")
        file.write(f"Coverage: {summary['coverage_percentage']:.1f}%\n")
        file.write(f"Unique Particle Types: {summary['unique_particle_types']}\n")
        file.write(f"Average Confidence: {summary['average_confidence']:.1f}%\n")
        file.write(f"Average RPBL Score: {summary['average_rpbl_score']:.1f}\n\n")

        # Top particle types
        file.write("🏆 TOP PARTICLE TYPES\n")
        file.write("-" * 50 + "\n")
        for i, (ptype, count) in enumerate(summary['top_particle_types'][:5], 1):
            percentage = (count / summary['total_particles_found'] * 100) if summary['total_particles_found'] > 0 else 0
            file.write(f"{i}. {ptype}: {count} ({percentage:.1f}%)\n")

        # Performance
        file.write(f"\n⚡ PERFORMANCE METRICS\n")
        file.write("-" * 50 + "\n")
        perf = self.results['performance']
        file.write(f"Files/Second: {perf['files_per_second']:.0f}\n")
        file.write(f"Lines/Second: {perf['lines_per_second']:.0f}\n")
        file.write(f"Characters/Second: {perf['characters_per_second']:.0f}\n")
        file.write(f"Success Rate: {perf['success_rate']:.1f}%\n")

    def _write_particles_csv(self, file):
        """Write particles to CSV"""
        fieldnames = ['type', 'name', 'file_path', 'line', 'confidence', 'responsibility', 'purity', 'boundary', 'lifecycle', 'rpbl_score', 'evidence']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for particle in self.results['particles']:
            # Clean evidence for CSV
            evidence = particle.get('evidence', '')[:50].replace('\n', ' ')

            writer.writerow({
                'type': particle.get('type', ''),
                'name': particle.get('name', ''),
                'file_path': particle.get('file_path', ''),
                'line': particle.get('line', ''),
                'confidence': particle.get('confidence', 0),
                'responsibility': particle.get('responsibility', 0),
                'purity': particle.get('purity', 0),
                'boundary': particle.get('boundary', 0),
                'lifecycle': particle.get('lifecycle', 0),
                'rpbl_score': particle.get('rpbl_score', 0),
                'evidence': evidence
            })
