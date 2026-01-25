#!/usr/bin/env python3
"""
Context Cache
=============
SMoC Role: Cache | Domain: Context

Manages the lifecycle of cached contexts for the FLASH_DEEP tier.
Enables "expensive per snapshot, cheap per question" pattern.

Part of S3 (ACI subsystem).

Usage:
    from aci.context_cache import CacheRegistry

    registry = CacheRegistry()

    # Check for existing cache
    cache = registry.get_valid_cache(model="gemini-2.0-flash", workspace_key="abc123")

    # Register new cache
    registry.register(
        cache_name="cachedContents/abc123",
        model="gemini-2.0-flash",
        workspace_key="abc123",
        ttl_seconds=3600
    )
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Cache registry location
REGISTRY_FILE = Path(__file__).parent.parent.parent.parent / "intelligence" / "cache_registry.json"


@dataclass
class CacheEntry:
    """Single cached context entry."""
    cache_name: str           # Gemini cache resource name (cachedContents/xxx)
    model: str                # Model the cache is for (gemini-2.0-flash, etc.)
    workspace_key: str        # Hash of (commit SHA + dirty state)
    created_at: float         # Unix timestamp
    expires_at: float         # Unix timestamp when cache expires
    token_count: int = 0      # Number of tokens in cached context

    @property
    def is_valid(self) -> bool:
        """Check if cache is still valid (not expired)."""
        return time.time() < self.expires_at

    @property
    def ttl_remaining(self) -> int:
        """Seconds until expiration."""
        return max(0, int(self.expires_at - time.time()))


class CacheRegistry:
    """Registry for tracking Gemini context caches."""

    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.registry_path = registry_path
        self.entries: Dict[str, CacheEntry] = {}
        self._load()

    def _load(self):
        """Load registry from disk."""
        if self.registry_path.exists():
            try:
                data = json.loads(self.registry_path.read_text())
                for key, entry_data in data.get("entries", {}).items():
                    self.entries[key] = CacheEntry(**entry_data)
            except Exception:
                self.entries = {}

    def _save(self):
        """Persist registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "updated_at": datetime.now().isoformat(),
            "entries": {k: asdict(v) for k, v in self.entries.items()}
        }
        self.registry_path.write_text(json.dumps(data, indent=2))

    def _make_key(self, model: str, workspace_key: str) -> str:
        """Generate registry key for model+workspace combination."""
        return f"{model}::{workspace_key}"

    def register(
        self,
        cache_name: str,
        model: str,
        workspace_key: str,
        ttl_seconds: int = 3600,
        token_count: int = 0
    ) -> CacheEntry:
        """
        Register a new cache entry.

        Args:
            cache_name: Gemini cache resource name (cachedContents/xxx)
            model: Model name (gemini-2.0-flash, etc.)
            workspace_key: Hash of workspace state (commit + dirty)
            ttl_seconds: Time to live in seconds (default 1 hour)
            token_count: Number of tokens in cached context

        Returns:
            The created CacheEntry
        """
        now = time.time()
        entry = CacheEntry(
            cache_name=cache_name,
            model=model,
            workspace_key=workspace_key,
            created_at=now,
            expires_at=now + ttl_seconds,
            token_count=token_count
        )
        key = self._make_key(model, workspace_key)
        self.entries[key] = entry
        self._save()
        return entry

    def get_valid_cache(self, model: str, workspace_key: str) -> Optional[CacheEntry]:
        """
        Get a valid (non-expired) cache for the given model and workspace.

        Args:
            model: Model name
            workspace_key: Workspace state hash

        Returns:
            CacheEntry if valid cache exists, None otherwise
        """
        key = self._make_key(model, workspace_key)
        entry = self.entries.get(key)

        if entry and entry.is_valid:
            return entry

        # Clean up expired entry
        if entry:
            del self.entries[key]
            self._save()

        return None

    def invalidate(self, model: str, workspace_key: str) -> bool:
        """
        Invalidate (remove) a cache entry.

        Returns:
            True if entry was found and removed
        """
        key = self._make_key(model, workspace_key)
        if key in self.entries:
            del self.entries[key]
            self._save()
            return True
        return False

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [k for k, v in self.entries.items() if not v.is_valid]
        for key in expired_keys:
            del self.entries[key]
        if expired_keys:
            self._save()
        return len(expired_keys)

    def list_all(self) -> Dict[str, CacheEntry]:
        """Get all entries (including expired)."""
        return dict(self.entries)

    def list_valid(self) -> Dict[str, CacheEntry]:
        """Get only valid (non-expired) entries."""
        return {k: v for k, v in self.entries.items() if v.is_valid}

    def stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        valid = self.list_valid()
        expired = len(self.entries) - len(valid)
        total_tokens = sum(e.token_count for e in valid.values())

        return {
            "total_entries": len(self.entries),
            "valid_entries": len(valid),
            "expired_entries": expired,
            "total_cached_tokens": total_tokens,
            "models": list(set(e.model for e in valid.values()))
        }


def get_workspace_key() -> str:
    """
    Generate a workspace key based on git state.

    Combines:
    - Current commit SHA (HEAD)
    - Dirty state hash (uncommitted changes)

    Returns:
        String key like "abc1234_dirty" or "abc1234_clean"
    """
    import subprocess

    try:
        # Get current commit SHA (short)
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        commit = result.stdout.strip() if result.returncode == 0 else "unknown"

        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5
        )
        is_dirty = bool(result.stdout.strip())

        return f"{commit}_{'dirty' if is_dirty else 'clean'}"

    except Exception:
        return f"unknown_{int(time.time())}"


if __name__ == "__main__":
    # Demo/test
    registry = CacheRegistry()

    print("=== Cache Registry Demo ===")
    print(f"Registry file: {registry.registry_path}")
    print(f"Current stats: {registry.stats()}")

    # Get workspace key
    ws_key = get_workspace_key()
    print(f"Workspace key: {ws_key}")

    # Check for existing cache
    cache = registry.get_valid_cache("gemini-2.0-flash", ws_key)
    if cache:
        print(f"Found valid cache: {cache.cache_name} (TTL: {cache.ttl_remaining}s)")
    else:
        print("No valid cache found")
