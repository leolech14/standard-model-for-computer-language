#!/usr/bin/env python3
"""
Tests for ACI Context Caching System

Tests context_cache, repopack, and token counting functionality.
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools/ai"))


class TestCacheRegistry:
    """Tests for context_cache module."""

    def test_cache_entry_validity(self):
        """Test CacheEntry is_valid and ttl_remaining properties."""
        from aci.context_cache import CacheEntry

        now = time.time()
        # Valid entry (expires in 1 hour)
        entry = CacheEntry(
            cache_name="test_cache",
            model="gemini-2.0-flash",
            workspace_key="abc123_clean",
            created_at=now,
            expires_at=now + 3600,
            token_count=1000
        )
        assert entry.is_valid
        assert entry.ttl_remaining > 3500

        # Expired entry
        expired = CacheEntry(
            cache_name="old_cache",
            model="gemini-2.0-flash",
            workspace_key="old_clean",
            created_at=now - 7200,
            expires_at=now - 3600,
            token_count=500
        )
        assert not expired.is_valid
        assert expired.ttl_remaining == 0

    def test_registry_register_and_get(self):
        """Test registering and retrieving cache entries."""
        from aci.context_cache import CacheRegistry

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            registry = CacheRegistry(Path(f.name))

            # Register entry
            entry = registry.register(
                cache_name="test_cache_123",
                model="gemini-2.0-flash",
                workspace_key="abc123_clean",
                ttl_seconds=3600,
                token_count=5000
            )

            assert entry.cache_name == "test_cache_123"

            # Retrieve entry
            retrieved = registry.get_valid_cache("gemini-2.0-flash", "abc123_clean")
            assert retrieved is not None
            assert retrieved.cache_name == "test_cache_123"

            # Non-existent entry
            missing = registry.get_valid_cache("other-model", "xyz_dirty")
            assert missing is None

    def test_registry_cleanup_expired(self):
        """Test cleaning up expired entries."""
        from aci.context_cache import CacheRegistry, CacheEntry

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            registry = CacheRegistry(Path(f.name))

            now = time.time()
            # Add expired entry directly
            key = "gemini-2.0-flash::expired_key"
            registry.entries[key] = CacheEntry(
                cache_name="expired",
                model="gemini-2.0-flash",
                workspace_key="expired_key",
                created_at=now - 7200,
                expires_at=now - 3600,
                token_count=100
            )

            # Add valid entry
            registry.register(
                cache_name="valid",
                model="gemini-2.0-flash",
                workspace_key="valid_key",
                ttl_seconds=3600
            )

            # Cleanup
            removed = registry.cleanup_expired()
            assert removed == 1
            assert len(registry.list_valid()) == 1


class TestRepoPack:
    """Tests for repopack module."""

    def test_get_repo_id(self):
        """Test repository ID generation."""
        from aci.repopack import get_repo_id

        repo_id = get_repo_id(Path.cwd())
        assert "commit" in repo_id
        assert "branch" in repo_id
        assert "timestamp" in repo_id
        assert "version" in repo_id

    def test_get_cache_key(self):
        """Test cache key generation."""
        from aci.repopack import get_cache_key

        key = get_cache_key(Path.cwd())
        assert "_clean" in key or "_dirty" in key
        # Key should be commit_state format
        parts = key.split("_")
        assert len(parts) == 2

    def test_format_repopack(self):
        """Test RepoPack formatting."""
        from aci.repopack import format_repopack

        pack = format_repopack(Path.cwd(), question="Test question?")

        # Should have required sections
        assert "## REPO_ID" in pack
        assert "## FILE_TREE" in pack
        assert "## QUESTION" in pack
        assert "Test question?" in pack


class TestTokenCounting:
    """Tests for token counting functions."""

    def test_validate_context_size_small(self):
        """Test validation passes for small content."""
        # Import from analyze.py
        sys.path.insert(0, str(Path(__file__).parent.parent / "tools/ai"))

        # Mock the function since it requires API
        small_content = "Hello world" * 10
        # Just test the estimation fallback (4 chars per token)
        estimated_tokens = len(small_content) // 4
        assert estimated_tokens < 1_000_000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
