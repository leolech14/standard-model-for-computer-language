#!/usr/bin/env python3
"""
Fetch top GitHub repos for batch grading.
Target: 999 repos across Python, JavaScript, TypeScript, Go.
"""

import requests
import json
import time
from pathlib import Path

LANGUAGES = ["Python", "JavaScript", "TypeScript", "Go"]
REPOS_PER_LANG = 250  # 250 × 4 = 1000, we'll take 999

def fetch_top_repos(language: str, count: int = 250) -> list[dict]:
    """Fetch top repos for a language using GitHub search API."""
    repos = []
    per_page = 100
    pages = (count // per_page) + 1

    for page in range(1, pages + 1):
        url = f"https://api.github.com/search/repositories"
        params = {
            "q": f"language:{language} stars:>100",
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }

        print(f"  Fetching {language} page {page}...")
        resp = requests.get(url, params=params)

        if resp.status_code == 403:
            print("  Rate limited. Waiting 60s...")
            time.sleep(60)
            resp = requests.get(url, params=params)

        if resp.status_code != 200:
            print(f"  Error: {resp.status_code}")
            break

        data = resp.json()
        items = data.get("items", [])

        for item in items:
            repos.append({
                "name": item["full_name"],
                "url": item["clone_url"],
                "stars": item["stargazers_count"],
                "language": language,
                "size_kb": item["size"]
            })

        if len(repos) >= count:
            break

        time.sleep(2)  # Rate limit courtesy

    return repos[:count]


def main():
    all_repos = []

    for lang in LANGUAGES:
        print(f"Fetching {lang} repos...")
        repos = fetch_top_repos(lang, REPOS_PER_LANG)
        all_repos.extend(repos)
        print(f"  Got {len(repos)} repos")

    # Take first 999
    all_repos = all_repos[:999]

    # Sort by stars (quality signal)
    all_repos.sort(key=lambda r: r["stars"], reverse=True)

    # Save
    output_dir = Path(__file__).parent

    # JSON with metadata
    with open(output_dir / "repos_999.json", "w") as f:
        json.dump(all_repos, f, indent=2)

    # Simple text list (clone URLs)
    with open(output_dir / "repos_999.txt", "w") as f:
        for repo in all_repos:
            f.write(f"{repo['url']}\n")

    print(f"\nSaved {len(all_repos)} repos to repos_999.json and repos_999.txt")

    # Stats
    by_lang = {}
    for r in all_repos:
        by_lang[r["language"]] = by_lang.get(r["language"], 0) + 1
    print(f"Distribution: {by_lang}")


if __name__ == "__main__":
    main()
