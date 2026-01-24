#!/usr/bin/env python3
"""
RepoPack - Deterministic Repository Context Formatter

Creates structured, cacheable context snapshots for Gemini FLASH_DEEP tier.
Same repo state produces identical RepoPack output for cache efficiency.

Format v1:
1. REPO_ID - Git commit, branch, timestamp
2. FILE_TREE - Directory structure (depth-limited)
3. SUBSYSTEMS - ACI analysis sets
4. PUBLIC_API - Exported functions/classes
5. COLLIDER_FACTS - Analysis results
6. DOCS - Key documentation
7. HOT_CODE - Recently modified files
8. QUESTION - User query (last, for cache reuse)
"""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

REPOPACK_VERSION = "1.0"


def get_repo_id(repo_path: Path) -> Dict:
    """Get repository identification info."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=repo_path
        ).stdout.strip()[:12]

        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=repo_path
        ).stdout.strip()

        return {
            "commit": commit,
            "branch": branch,
            "timestamp": datetime.now().isoformat(),
            "version": REPOPACK_VERSION
        }
    except Exception:
        return {"commit": "unknown", "branch": "unknown", "timestamp": datetime.now().isoformat(), "version": REPOPACK_VERSION}


def get_file_tree(repo_path: Path, max_depth: int = 3, max_files: int = 200) -> str:
    """Get directory structure as tree string."""
    lines = []
    count = 0

    def walk(path: Path, prefix: str = "", depth: int = 0):
        nonlocal count
        if depth > max_depth or count > max_files:
            return

        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return

        dirs = [e for e in entries if e.is_dir() and not e.name.startswith('.')]
        files = [e for e in entries if e.is_file() and not e.name.startswith('.')]

        for d in dirs[:20]:  # Limit dirs per level
            lines.append(f"{prefix}{d.name}/")
            walk(d, prefix + "  ", depth + 1)

        for f in files[:30]:  # Limit files per level
            count += 1
            if count <= max_files:
                lines.append(f"{prefix}{f.name}")

    walk(repo_path)
    return "\n".join(lines[:max_files])


def get_hot_files(repo_path: Path, limit: int = 10) -> List[Dict]:
    """Get recently modified files with content."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~5", "HEAD"],
            capture_output=True, text=True, cwd=repo_path
        )
        files = result.stdout.strip().split("\n")[:limit]

        hot = []
        for f in files:
            if not f:
                continue
            path = repo_path / f
            if path.exists() and path.stat().st_size < 50000:  # Max 50KB
                try:
                    content = path.read_text(errors='ignore')[:10000]  # Max 10K chars
                    hot.append({"path": f, "content": content})
                except Exception:
                    pass
        return hot
    except Exception:
        return []


def format_repopack(
    repo_path: Path,
    question: str = "",
    include_hot_code: bool = True,
    max_tree_depth: int = 3
) -> str:
    """
    Generate RepoPack v1 formatted context.

    Args:
        repo_path: Root of repository
        question: User query (placed last for cache reuse)
        include_hot_code: Include recently modified files
        max_tree_depth: Depth limit for file tree

    Returns:
        Formatted RepoPack string
    """
    repo_path = Path(repo_path)
    sections = []

    # Section 1: REPO_ID
    repo_id = get_repo_id(repo_path)
    sections.append(f"""## REPO_ID
commit: {repo_id['commit']}
branch: {repo_id['branch']}
timestamp: {repo_id['timestamp']}
repopack_version: {repo_id['version']}""")

    # Section 2: FILE_TREE
    tree = get_file_tree(repo_path, max_depth=max_tree_depth)
    sections.append(f"""## FILE_TREE
```
{tree}
```""")

    # Section 3: HOT_CODE (optional)
    if include_hot_code:
        hot_files = get_hot_files(repo_path)
        if hot_files:
            hot_section = "## HOT_CODE\nRecently modified files:\n"
            for hf in hot_files:
                hot_section += f"\n### {hf['path']}\n```\n{hf['content']}\n```\n"
            sections.append(hot_section)

    # Section N: QUESTION (always last)
    if question:
        sections.append(f"""## QUESTION
{question}""")

    return "\n\n".join(sections)


def get_cache_key(repo_path: Path) -> str:
    """Generate deterministic cache key for repo state."""
    repo_id = get_repo_id(Path(repo_path))

    # Check for uncommitted changes
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=repo_path
        )
        is_dirty = bool(result.stdout.strip())
    except Exception:
        is_dirty = True

    return f"{repo_id['commit']}_{'dirty' if is_dirty else 'clean'}"


if __name__ == "__main__":
    import sys

    repo = Path.cwd()
    if len(sys.argv) > 1:
        repo = Path(sys.argv[1])

    print("=== RepoPack Demo ===")
    print(f"Repo: {repo}")
    print(f"Cache key: {get_cache_key(repo)}")
    print("\n" + "="*50 + "\n")

    pack = format_repopack(repo, question="What is the architecture?")
    print(pack[:2000] + "\n...[truncated]" if len(pack) > 2000 else pack)
