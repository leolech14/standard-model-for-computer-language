#!/usr/bin/env python3
"""
Map technical clusters to business domains for visualization grouping.
"""

BUSINESS_DOMAINS = {
    "Banking & Open Banking": {
        "icon": "🏦",
        "color": "#3b82f6",  # Blue
        "clusters": ["pluggy_integration", "connections", "webhooks"],
        "description": "Bank integration and connection management"
    },
    "Financial Accounts": {
        "icon": "💰",
        "color": "#10b981",  # Green
        "clusters": ["accounts", "loans", "billing", "investments", "finance"],
        "description": "Account tracking and financial aggregation"
    },
    "Transactions": {
        "icon": "💸",
        "color": "#f59e0b",  # Amber
        "clusters": ["transactions", "csv_import"],
        "description": "Transaction management and import"
    },
    "Identity & Entities": {
        "icon": "👤",
        "color": "#8b5cf6",  # Purple
        "clusters": ["entities"],
        "description": "CPF/CNPJ identity management"
    },
    "Data & Visualization": {
        "icon": "📊",
        "color": "#ec4899",  # Pink
        "clusters": ["visualization", "caching"],
        "description": "Chart data and caching"
    },
    "AI Assistant": {
        "icon": "🤖",
        "color": "#06b6d4",  # Cyan
        "clusters": ["assistant"],
        "description": "LLM-powered financial advice"
    },
    "Infrastructure": {
        "icon": "🔧",
        "color": "#6b7280",  # Gray
        "clusters": [
            "validation", "transformation", "extraction", "computation",
            "error_handling", "diagnostics", "mocking", "factory",
            "api_layer", "io_input", "io_output", "persistence", "database"
        ],
        "description": "Core utilities and infrastructure"
    },
    "God Class": {
        "icon": "⚠️",
        "color": "#ef4444",  # Red
        "clusters": ["core", "handler", "execution", "unclustered"],
        "description": "Monolithic god class requiring refactoring"
    }
}

def get_domain_for_cluster(cluster_name: str) -> tuple[str, dict]:
    """Get business domain for a given cluster."""
    for domain_name, domain_info in BUSINESS_DOMAINS.items():
        if cluster_name in domain_info["clusters"]:
            return domain_name, domain_info
    return "Unknown", {"icon": "❓", "color": "#9ca3af", "description": "Uncategorized"}

def generate_domain_mapping():
    """Generate a mapping of cluster -> domain."""
    mapping = {}
    for cluster in sum([d["clusters"] for d in BUSINESS_DOMAINS.values()], []):
        domain_name, domain_info = get_domain_for_cluster(cluster)
        mapping[cluster] = {
            "domain": domain_name,
            "icon": domain_info["icon"],
            "color": domain_info["color"],
            "description": domain_info["description"]
        }
    return mapping

if __name__ == "__main__":
    import json
    mapping = generate_domain_mapping()
    print(json.dumps({
        "domains": BUSINESS_DOMAINS,
        "cluster_to_domain": mapping
    }, indent=2))
