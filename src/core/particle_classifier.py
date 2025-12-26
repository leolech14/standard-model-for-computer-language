#!/usr/bin/env python3
"""
🚀 SPECTROMETER V12 - Particle Classifier
RPBL scoring system for particle classification
============================================
"""

import json
from pathlib import Path
from typing import Dict, List, Any

class ParticleClassifier:
    """Classifies particles with RPBL scores"""

    def __init__(self):
        # Load particle definitions
        particles_file = Path(__file__).parent.parent / 'patterns' / 'particle_defs.json'
        with open(particles_file) as f:
            self.particle_defs = json.load(f)

        # Create lookup dict
        self.particle_lookup = {
            p['id']: p for p in self.particle_defs['particle_types']
        }

    def classify_particle(self, particle_data: Dict) -> Dict[str, Any]:
        """Classify particle with RPBL scores"""
        particle_type = particle_data.get('type', 'Unknown')

        if particle_type in self.particle_lookup:
            definition = self.particle_lookup[particle_type]
            return {
                **particle_data,
                'responsibility': definition['responsibility'],
                'purity': definition['purity'],
                'boundary': definition['boundary'],
                'lifecycle': definition['lifecycle'],
                'rpbl_score': self._calculate_rpbl_score(definition),
                'description': definition['description']
            }
        else:
            # Default scores for unknown particles
            return {
                **particle_data,
                'responsibility': 5,
                'purity': 5,
                'boundary': 5,
                'lifecycle': 5,
                'rpbl_score': 5.0,
                'description': 'Unknown particle type'
            }

    def _calculate_rpbl_score(self, definition: Dict) -> float:
        """Calculate overall RPBL score"""
        scores = [
            definition['responsibility'],
            definition['purity'],
            definition['boundary'],
            definition['lifecycle']
        ]
        return sum(scores) / len(scores)

    def get_all_particle_types(self) -> List[Dict]:
        """Get all defined particle types"""
        return self.particle_defs['particle_types']

    def analyze_particle_distribution(self, particles: List[Dict]) -> Dict[str, Any]:
        """Analyze distribution of detected particles"""
        type_counts = {}
        rpbl_scores = []

        for particle in particles:
            particle_type = particle.get('type', 'Unknown')
            type_counts[particle_type] = type_counts.get(particle_type, 0) + 1

            if 'rpbl_score' in particle:
                rpbl_scores.append(particle['rpbl_score'])

        # Calculate statistics
        total_particles = len(particles)
        unique_types = len(type_counts)
        avg_rpbl = sum(rpbl_scores) / len(rpbl_scores) if rpbl_scores else 0

        return {
            'total_particles': total_particles,
            'unique_types': unique_types,
            'type_distribution': type_counts,
            'average_rpbl_score': avg_rpbl,
            'highest_rpbl': max(rpbl_scores) if rpbl_scores else 0,
            'lowest_rpbl': min(rpbl_scores) if rpbl_scores else 0
        }