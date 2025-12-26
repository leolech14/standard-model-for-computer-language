#!/usr/bin/env python3
"""Repository Curator - Collects diverse Python repos"""
import requests
import json
from pathlib import Path

GITHUB_API = "https://api.github.com/search/repositories"

# Simpler keyword strategy per category
CATEGORIES = {
    "web": "fastapi",
    "cli": "click", 
    "datascience": "pandas",
    "ml": "pytorch",
    "infra": "docker-py",
    "testing": "pytest",
    "utils": "requests",
    "domain": "django"
}

def search_github(keyword: str, per_category: int = 13):
    """Search GitHub for top repos with keyword"""
    query = f"language:python stars:>1000 {keyword} in:name,description"
    
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": per_category}
    
    response = requests.get(GITHUB_API, params=params)
    response.raise_for_status()
    
    return [{"name": r["full_name"], "url": r["clone_url"], "stars": r["stargazers_count"]} 
            for r in response.json()["items"]]

def curate_repos(per_category: int = 13):
    curated = {}
    for category, keyword in CATEGORIES.items():
        print(f"📦 {category}...")
        curated[category] = search_github(keyword, per_category)
        print(f"  → {len(curated[category])} repos")
    return curated

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-category", type=int, default=13)
    parser.add_argument("--output", default="data/benchmark/repo_list_v2")
    args = parser.parse_args()
    
    curated = curate_repos(args.per_category)
    
    # Save
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output.with_suffix('.json'), 'w') as f:
        json.dump(curated, f, indent=2)
    
    total = sum(len(repos) for repos in curated.values())
    print(f"\n✅ {total} repos saved to {output}.json")
