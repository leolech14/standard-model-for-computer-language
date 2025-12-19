#!/usr/bin/env python3
"""
Generate cluster details from Spectrometer analysis outputs.
"""
import json
import csv
from collections import defaultdict
from pathlib import Path

def load_prescription(path):
    """Load prescription.json"""
    with open(path) as f:
        return json.load(f)

def load_components(path):
    """Load components.csv"""
    components = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            components.append(row)
    return components

def generate_cluster_details(prescription_path, components_path):
    """Generate detailed cluster information"""
    
    prescription = load_prescription(prescription_path)
    components = load_components(components_path)
    
    # Map component IDs to component data
    comp_map = {c['component_id']: c for c in components}
    
    # Get cluster assignments from prescription
    clusters = prescription.get('clusters', {})
    cluster_nodes = prescription.get('cluster_nodes', {})
    
    details = {}
    
    for cluster_name, node_count in clusters.items():
        # Get nodes in this cluster
        nodes_in_cluster = cluster_nodes.get(cluster_name, [])
        
        # Get function names
        func_names = []
        for node_id in nodes_in_cluster[:20]:  # Limit to first 20
            if node_id in comp_map:
                comp = comp_map[node_id]
                name = comp.get('name', '')
                if name and name != cluster_name:
                    func_names.append(name)
        
        # Determine purpose based on cluster name
        purposes = {
            'core': "Main server orchestrator containing handleApi (God Function)",
            'connections': "Bank account connection lifecycle management",
            'accounts': "Financial accounts tracking and balance aggregation",
            'entities': "Identity entities (CPF/CNPJ) and relationship mapping",
            'transactions': "Transaction CRUD operations and filtering",
            'validation': "Input validation and data integrity checks",
            'transformation': "Data normalization and format conversion",
            'pluggy_integration': "Pluggy Open Banking API integration",
            'error_handling': "Centralized error handling and API responses",
            'io_input': "Request parsing and input handling",
            'io_output': "Response formatting and output handling",
            'caching': "In-memory caching for visualization data",
            'persistence': "Database file persistence layer",
            'computation': "Business logic calculations",
            'extraction': "Data field extraction utilities",
            'factory': "Object builder functions (Factory pattern)",
            'loans': "Loan account tracking and payment schedules",
            'billing': "Bill payment tracking and calendar",
            'finance': "High-level financial metrics aggregation",
            'diagnostics': "Event logging and performance tracking",
            'visualization': "Chart data transformation (Sankey, network)",
            'api_layer': "API metadata and endpoint routing",
            'assistant': "AI assistant integration (Ollama LLM)",
            'mocking': "Mock data generation for testing",
            'csv_import': "CSV file import functionality",
            'database': "Low-level database operations",
            'webhooks': "Webhook event handling",
            'identity': "User identity and profile management"
        }
        
        details[cluster_name] = {
            'purpose': purposes.get(cluster_name, f"Module handling {cluster_name} functionality"),
            'count': node_count,
            'functions': func_names
        }
    
    return details

if __name__ == '__main__':
    import sys
    
    prescription_path = Path('output/atman_full_analysis/prescription.json')
    components_path = Path('output/atman_full_analysis/components.csv')
    
    details = generate_cluster_details(prescription_path, components_path)
    
    # Output as JSON
    print(json.dumps(details, indent=2))
