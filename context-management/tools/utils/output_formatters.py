"""
Dual-Format Output Formatter with SHA-256 Checksum

Extracted from perplexity_mcp_server.py for reuse across MCP servers.
Part of MCP Factory knowledge base.

Features:
    - Dual-format save: raw JSON + human-readable Markdown
    - SHA-256 checksums for fixity verification (archival compliance)
    - Deterministic filenames from timestamp + query slug
    - Zero information loss design

Usage:
    from tools.utils.output_formatters import DualFormatSaver

    saver = DualFormatSaver(base_path="/path/to/research")
    result = saver.save(
        query="What is X?",
        response=api_response_dict,
        source="perplexity",
        model="sonar-pro"
    )
    # Returns: {"raw_path": ..., "md_path": ..., "checksum": "sha256:..."}
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional


@dataclass
class SaveResult:
    """Result of a dual-format save operation."""
    raw_path: Path
    md_path: Path
    checksum: str  # Format: "sha256:{hash}"
    filename: str


def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Generate URL-safe slug from text.

    Args:
        text: Input text (e.g., query string)
        max_length: Maximum slug length

    Returns:
        Lowercase alphanumeric slug with underscores
    """
    slug = "".join(c if c.isalnum() else "_" for c in text[:max_length])
    return slug.strip("_").lower()


def compute_checksum(content: str, algorithm: str = "sha256") -> str:
    """
    Compute checksum of content.

    Args:
        content: String content to hash
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Checksum string in format "{algorithm}:{hash}"
    """
    hasher = hashlib.new(algorithm)
    hasher.update(content.encode("utf-8"))
    return f"{algorithm}:{hasher.hexdigest()}"


class DualFormatSaver:
    """
    Saves research outputs in dual format: raw JSON + human-readable Markdown.

    Directory structure:
        {base_path}/
            raw/      # Complete JSON responses
            docs/     # Human-readable markdown

    Example:
        saver = DualFormatSaver(Path("./research"))
        result = saver.save(query="test", response={...}, source="perplexity", model="sonar")
    """

    def __init__(
        self,
        base_path: Path,
        raw_subdir: str = "raw",
        docs_subdir: str = "docs",
        md_formatter: Optional[Callable] = None
    ):
        """
        Initialize the saver.

        Args:
            base_path: Root directory for saved files
            raw_subdir: Subdirectory for raw JSON files
            docs_subdir: Subdirectory for markdown files
            md_formatter: Optional custom markdown formatter function
        """
        self.base_path = Path(base_path)
        self.raw_dir = self.base_path / raw_subdir
        self.docs_dir = self.base_path / docs_subdir
        self.md_formatter = md_formatter or self._default_md_formatter

    def _generate_filename(self, query: str) -> str:
        """Generate deterministic filename from timestamp and query."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = generate_slug(query)
        return f"{timestamp}_{slug}"

    def _save_raw_json(
        self,
        filename: str,
        query: str,
        response: dict,
        source: str,
        model: str
    ) -> tuple[Path, str]:
        """
        Save complete response as JSON with metadata.

        Returns:
            Tuple of (file_path, checksum)
        """
        self.raw_dir.mkdir(parents=True, exist_ok=True)

        raw_data = {
            "_meta": {
                "saved_at": datetime.now().isoformat(),
                "source": source,
                "model": model,
                "query": query,
                "query_length": len(query),
            },
            "response": response
        }

        content = json.dumps(raw_data, indent=2, ensure_ascii=False)
        checksum = compute_checksum(content)

        # Add checksum to metadata
        raw_data["_meta"]["checksum"] = checksum
        content = json.dumps(raw_data, indent=2, ensure_ascii=False)

        filepath = self.raw_dir / f"{filename}.json"
        filepath.write_text(content)

        return filepath, checksum

    def _default_md_formatter(
        self,
        query: str,
        response: dict,
        source: str,
        model: str,
        raw_filename: str,
        checksum: str
    ) -> str:
        """
        Default markdown formatter for research outputs.

        Override via md_formatter parameter for custom formatting.
        """
        # Extract common fields (works for Perplexity-style responses)
        content = ""
        citations = []
        usage = {}

        # Handle Perplexity API format
        if "choices" in response:
            choice = response.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            citations = response.get("citations", [])
            usage = response.get("usage", {})
        # Handle simple format
        elif "content" in response:
            content = response.get("content", "")
            citations = response.get("citations", [])
        # Handle raw text
        elif isinstance(response, str):
            content = response

        # Build markdown
        title = query[:100] + ("..." if len(query) > 100 else "")
        md = f"""# Research: {title}

> **Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> **Source:** {source}
> **Model:** {model}
> **Checksum:** `{checksum}`
> **Raw JSON:** `raw/{raw_filename}.json`

---

## Query

{query}

---

## Response

{content}

---

## Citations

"""
        if citations:
            for i, citation in enumerate(citations, 1):
                md += f"{i}. {citation}\n"
        else:
            md += "_No citations provided_\n"

        # Add usage stats if available
        if usage:
            md += f"""
---

## Usage Stats

- Prompt tokens: {usage.get('prompt_tokens', 'N/A')}
- Completion tokens: {usage.get('completion_tokens', 'N/A')}
- Total tokens: {usage.get('total_tokens', 'N/A')}
"""

        return md

    def _save_markdown(
        self,
        filename: str,
        query: str,
        response: dict,
        source: str,
        model: str,
        checksum: str
    ) -> Path:
        """Save human-readable markdown."""
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        content = self.md_formatter(
            query=query,
            response=response,
            source=source,
            model=model,
            raw_filename=filename,
            checksum=checksum
        )

        filepath = self.docs_dir / f"{filename}.md"
        filepath.write_text(content)

        return filepath

    def save(
        self,
        query: str,
        response: dict,
        source: str,
        model: str
    ) -> SaveResult:
        """
        Save response in dual format with checksum.

        Args:
            query: Original query text
            response: API response dictionary
            source: Source identifier (e.g., "perplexity", "gemini")
            model: Model identifier (e.g., "sonar-pro", "gemini-2.5-pro")

        Returns:
            SaveResult with paths and checksum

        Example:
            result = saver.save(
                query="What is MCP?",
                response={"choices": [...]},
                source="perplexity",
                model="sonar-pro"
            )
            print(f"Saved to {result.raw_path}, checksum: {result.checksum}")
        """
        filename = self._generate_filename(query)

        # Save raw JSON first (generates checksum)
        raw_path, checksum = self._save_raw_json(
            filename, query, response, source, model
        )

        # Save markdown with checksum reference
        md_path = self._save_markdown(
            filename, query, response, source, model, checksum
        )

        return SaveResult(
            raw_path=raw_path,
            md_path=md_path,
            checksum=checksum,
            filename=filename
        )

    def verify_checksum(self, filepath: Path) -> bool:
        """
        Verify file integrity using stored checksum.

        Args:
            filepath: Path to JSON file to verify

        Returns:
            True if checksum matches, False otherwise
        """
        content = filepath.read_text()
        data = json.loads(content)

        stored_checksum = data.get("_meta", {}).get("checksum", "")
        if not stored_checksum:
            return False

        # Remove checksum from data for verification
        data["_meta"].pop("checksum", None)
        content_without_checksum = json.dumps(data, indent=2, ensure_ascii=False)

        computed = compute_checksum(content_without_checksum)
        return computed == stored_checksum
