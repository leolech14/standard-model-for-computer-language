#!/usr/bin/env python3
"""
Analyzes failures for a specific repository to pinpoint 'Why we couldn't map it'.
"""
import csv
import sys
from pathlib import Path
from collections import defaultdict

# Root setup
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core.atom_classifier import AtomClassifier

# Validation Map (Must match train_serial.py)
ROLE_MAP = {
    'Test': 'Test',
    'TestDouble': 'Test',
    'Fixture': 'Test',
    'Entity': 'Entity',
    'ValueObject': 'Entity', 
    'DTO': 'Entity',
    'Service': 'Service',
    'UseCase': 'Service',
    'Controller': 'Controller',
    'Repository': 'Repository',
    'Utility': 'Utility',
    'ImpureFunction': 'Utility',
    'PureFunction': 'Utility',
    'Factory': 'Factory',
    'Mapper': 'Mapper',
    'Configuration': 'Configuration',
    'Class': 'Entity',
    'Validator': 'Utility',
    'EventHandler': 'Utility',
    'Builder': 'Factory',
    'TestModule': 'Test',
    'TestDouble': 'Test',
    'Observer': 'EventHandler',
    'Specification': 'Service',
    'Configuration': 'Configuration',
}

def normalize(subtype):
    return ROLE_MAP.get(subtype, subtype)

def analyze_repo(target_repo):
    csv_path = root_dir / "data/benchmark/ground_truth_v1.csv"
    classifier = AtomClassifier()
    
    print(f"🔍 Deep Dive: {target_repo}")
    print(f"{'Name':<40} | {'Path':<50} | {'Annotated':<15} | {'Predicted (Atom -> Norm)':<30}")
    print("-" * 140)
    
    failures = 0
    total = 0
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if target_repo not in row['file']:
                continue
                
            total += 1
            name = row['name']
            file_path = row['file']
            annotated = row['annotated_role']
            
            # Classification
            pred = classifier.classify_by_name(name, file_path=file_path, language="python")
            atom = pred.subtype
            norm = normalize(atom)
            
            if norm != annotated:
                failures += 1
                # Print usage
                print(f"{name:<40} | {file_path[-50:]:<50} | {annotated:<15} | {atom} -> {norm}")

    print("-" * 140)
    print(f"Failures: {failures}/{total} ({100 - (failures/total*100):.1f}% Accuracy)")

if __name__ == "__main__":
    analyze_repo("pydantic")
