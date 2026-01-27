"""Knowledge Library Endpoints - Search and browse consolidated chunks."""

from fastapi import APIRouter, Query, HTTPException
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json
from typing import List, Dict, Any

router = APIRouter()

PROJECT_ROOT = Path(__file__).parent.parent.parent
CHUNKS_DIR = PROJECT_ROOT / ".agent" / "intelligence" / "chunks"


def load_all_chunks() -> List[Dict[str, Any]]:
    """Load all chunks from all chunk files."""
    all_chunks = []

    for chunk_file in ["agent_chunks.json", "core_chunks.json", "aci_chunks.json"]:
        path = CHUNKS_DIR / chunk_file
        if not path.exists():
            continue

        try:
            with open(path) as f:
                data = json.load(f)
                for node in data.get("nodes", []):
                    node["source_module"] = chunk_file.replace("_chunks.json", "")
                    all_chunks.append(node)
        except Exception:
            continue

    return all_chunks


@router.get("/search")
def search_knowledge(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    chunk_type: str = Query(None, description="Filter by chunk type")
):
    """Search consolidated knowledge chunks."""

    all_chunks = load_all_chunks()

    if not all_chunks:
        return {"query": q, "total_matches": 0, "returned": 0, "results": []}

    # Search
    query_lower = q.lower()
    matches = []

    for chunk in all_chunks:
        content = chunk.get("content", "").lower()

        if query_lower in content:
            # Filter by type if specified
            if chunk_type and chunk.get("chunk_type") != chunk_type:
                continue

            # Calculate match score
            match_count = content.count(query_lower)
            base_relevance = chunk.get("relevance_score", 0.5)
            match_score = base_relevance + (match_count * 0.1)

            # Extract preview
            match_index = content.index(query_lower)
            preview_start = max(0, match_index - 50)
            preview_end = min(len(chunk.get("content", "")), match_index + 150)
            preview = chunk.get("content", "")[preview_start:preview_end]

            matches.append({
                "chunk_id": chunk.get("chunk_id"),
                "source_file": chunk.get("source_file"),
                "chunk_type": chunk.get("chunk_type"),
                "start_line": chunk.get("start_line"),
                "relevance": chunk.get("relevance_score"),
                "match_count": match_count,
                "match_score": match_score,
                "preview": preview.strip(),
                "full_content_endpoint": f"/api/knowledge/chunks/{chunk.get('chunk_id')}"
            })

    # Sort by match score
    matches.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "query": q,
        "total_matches": len(matches),
        "returned": min(limit, len(matches)),
        "results": matches[:limit]
    }


@router.get("/library")
def get_library(
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("chunks", regex="^(chunks|tokens|name)$")
):
    """Get organized library view."""

    all_chunks = load_all_chunks()

    if not all_chunks:
        return {"total_files": 0, "total_chunks": 0, "files": []}

    # Group by source file
    by_file = defaultdict(list)
    for chunk in all_chunks:
        source = chunk.get("source_file", "unknown")
        by_file[source].append(chunk)

    # Build file summaries
    files = []
    for filepath, chunks in by_file.items():
        chunk_count = len(chunks)
        total_tokens = sum(c.get("metadata", {}).get("token_estimate", 0) or
                          len(c.get("content", "")) // 4 for c in chunks)

        # Count chunk types
        types = defaultdict(int)
        for c in chunks:
            types[c.get("chunk_type", "unknown")] += 1

        files.append({
            "path": filepath,
            "chunks": chunk_count,
            "tokens": total_tokens,
            "types": dict(types),
            "chunks_endpoint": f"/api/knowledge/files/{filepath}"
        })

    # Sort
    if sort == "chunks":
        files.sort(key=lambda x: x["chunks"], reverse=True)
    elif sort == "tokens":
        files.sort(key=lambda x: x["tokens"], reverse=True)
    else:  # name
        files.sort(key=lambda x: x["path"])

    total_chunks = sum(f["chunks"] for f in files)
    total_tokens = sum(f["tokens"] for f in files)

    return {
        "total_files": len(files),
        "total_chunks": total_chunks,
        "total_tokens": total_tokens,
        "files": files[:limit]
    }


@router.get("/chunks/{chunk_id}")
def get_chunk(chunk_id: str):
    """Get full content of specific chunk."""

    all_chunks = load_all_chunks()

    for chunk in all_chunks:
        if chunk.get("chunk_id") == chunk_id:
            return chunk

    raise HTTPException(status_code=404, detail=f"Chunk '{chunk_id}' not found")


@router.get("/stats")
def get_knowledge_stats():
    """Get knowledge library statistics."""

    metadata_file = CHUNKS_DIR / "metadata.json"

    if not metadata_file.exists():
        return {"error": "No metadata found"}

    try:
        with open(metadata_file) as f:
            metadata = json.load(f)

        all_chunks = load_all_chunks()

        # Count by type
        by_type = defaultdict(int)
        for chunk in all_chunks:
            by_type[chunk.get("chunk_type", "unknown")] += 1

        # Check freshness
        last_gen = datetime.fromisoformat(metadata["timestamp"])
        age_minutes = (datetime.now() - last_gen).total_seconds() / 60

        freshness = "current" if age_minutes < 60 else "stale" if age_minutes < 1440 else "very_stale"

        return {
            "last_generated": metadata["timestamp"],
            "git_sha": metadata["git_sha"],
            "total_chunks": metadata["total_chunks"],
            "total_tokens": metadata["total_tokens"],
            "by_module": metadata.get("chunks", {}),
            "by_type": dict(by_type),
            "freshness": freshness,
            "age_minutes": int(age_minutes)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
