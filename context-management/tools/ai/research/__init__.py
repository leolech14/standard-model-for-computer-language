"""
Research tools for external knowledge acquisition.

This module provides precision context fetching capabilities using external
AI services (Perplexity SONAR-PRO) to fill knowledge gaps identified by
the Codome Completeness Index (CCI).
"""

from .precision_fetcher import (
    PrecisionContextFetcher,
    GapProfile,
    ActionableGuidance,
    ResearchResult,
    fetch_guidance_for_gap,
    fetch_guidance_sync,
)

__all__ = [
    'PrecisionContextFetcher',
    'GapProfile',
    'ActionableGuidance',
    'ResearchResult',
    'fetch_guidance_for_gap',
    'fetch_guidance_sync',
]
