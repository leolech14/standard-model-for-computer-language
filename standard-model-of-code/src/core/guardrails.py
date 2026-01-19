"""Resource guardrails for safe analysis execution."""

import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ResourceLimits:
    """Configuration for resource limits."""
    max_file_size_mb: float = 10.0
    max_files: int = 10000
    max_total_size_mb: float = 500.0
    parse_timeout_seconds: int = 30
    max_nodes: int = 100000
    max_edges: int = 500000


class ResourceLimitExceeded(Exception):
    """Raised when a resource limit is exceeded."""
    pass


class Guardrails:
    """Resource guardrails for analysis operations."""

    def __init__(self, limits: Optional[ResourceLimits] = None):
        self.limits = limits or ResourceLimits()
        self._file_count = 0
        self._total_size = 0
        self._node_count = 0
        self._edge_count = 0
        self._lock = threading.Lock()

    def check_file(self, file_path: str) -> bool:
        """Check if file can be processed within limits.

        Args:
            file_path: Path to file

        Returns:
            True if file can be processed

        Raises:
            ResourceLimitExceeded if limits would be exceeded
        """
        path = Path(file_path)

        if not path.exists():
            return False

        size_mb = path.stat().st_size / (1024 * 1024)

        # Check individual file size
        if size_mb > self.limits.max_file_size_mb:
            logger.warning(
                f"Skipping {file_path}: {size_mb:.2f}MB exceeds "
                f"{self.limits.max_file_size_mb}MB limit"
            )
            return False

        with self._lock:
            # Check file count
            if self._file_count >= self.limits.max_files:
                raise ResourceLimitExceeded(
                    f"File count limit ({self.limits.max_files}) exceeded"
                )

            # Check total size
            if self._total_size + size_mb > self.limits.max_total_size_mb:
                raise ResourceLimitExceeded(
                    f"Total size limit ({self.limits.max_total_size_mb}MB) exceeded"
                )

            self._file_count += 1
            self._total_size += size_mb

        return True

    def check_nodes(self, count: int) -> None:
        """Check if node count is within limits.

        Args:
            count: Number of nodes to add

        Raises:
            ResourceLimitExceeded if limit exceeded
        """
        with self._lock:
            if self._node_count + count > self.limits.max_nodes:
                raise ResourceLimitExceeded(
                    f"Node limit ({self.limits.max_nodes}) exceeded"
                )
            self._node_count += count

    def check_edges(self, count: int) -> None:
        """Check if edge count is within limits.

        Args:
            count: Number of edges to add

        Raises:
            ResourceLimitExceeded if limit exceeded
        """
        with self._lock:
            if self._edge_count + count > self.limits.max_edges:
                raise ResourceLimitExceeded(
                    f"Edge limit ({self.limits.max_edges}) exceeded"
                )
            self._edge_count += count

    def get_stats(self) -> dict:
        """Get current resource usage statistics."""
        with self._lock:
            return {
                "files_processed": self._file_count,
                "total_size_mb": round(self._total_size, 2),
                "nodes": self._node_count,
                "edges": self._edge_count,
                "limits": {
                    "max_files": self.limits.max_files,
                    "max_total_size_mb": self.limits.max_total_size_mb,
                    "max_nodes": self.limits.max_nodes,
                    "max_edges": self.limits.max_edges,
                }
            }

    def reset(self) -> None:
        """Reset all counters."""
        with self._lock:
            self._file_count = 0
            self._total_size = 0
            self._node_count = 0
            self._edge_count = 0


# Global default guardrails instance
default_guardrails = Guardrails()
