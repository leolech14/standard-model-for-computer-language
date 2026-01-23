# MCP Server Best Practices

> Distilled from Perplexity research (sonar-deep-research) + Gemini analysis, 2026-01-22.

## Quick Reference

```yaml
# 5-minute checklist for new MCP servers
MUST:
  - Use stdio transport (stdin/stdout)
  - Implement JSON-RPC 2.0 correctly
  - Handle errors with proper codes (-32700, -32600, -32601, -32602, -32603)
  - Flush stdout after every response
  - Log to stderr (NEVER stdout)

SHOULD:
  - Auto-save all requests/responses (dual-format: JSON + Markdown)
  - Use exponential backoff with jitter for API calls
  - Distinguish transient vs permanent failures
  - Include request correlation IDs

AVOID:
  - Mixing logging with stdout
  - Blocking the event loop on stdin reads
  - Retrying 4xx client errors
  - Hardcoding API keys
```

---

## 1. Protocol: JSON-RPC 2.0 Over Stdio

### Request Structure

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "perplexity_search",
    "arguments": { "query": "example" }
  },
  "id": 1
}
```

### Response Structure

```json
// Success
{
  "jsonrpc": "2.0",
  "result": { "content": [...] },
  "id": 1
}

// Error
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": { "method": "unknown_method" }
  },
  "id": 1
}
```

### Standard Error Codes

| Code | Name | When |
|------|------|------|
| -32700 | Parse error | Invalid JSON received |
| -32600 | Invalid Request | Missing jsonrpc/method field |
| -32601 | Method not found | Unknown method name |
| -32602 | Invalid params | Wrong type or missing required param |
| -32603 | Internal error | Server-side exception |

### Critical Implementation Detail

```python
# CORRECT: Separate stdout (responses) from stderr (logs)
import sys
import json

def send_response(response: dict):
    json_line = json.dumps(response, separators=(',', ':'))
    sys.stdout.write(json_line + '\n')
    sys.stdout.flush()  # CRITICAL: Always flush

# Configure logging to stderr only
import logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
```

---

## 2. Server Architecture

### Recommended Structure

```
mcp_server_name/
├── __main__.py           # Entry point (stdio loop)
├── server.py             # MCPServer class
├── handlers.py           # Tool handlers (business logic)
├── client.py             # External API wrapper
├── persistence.py        # Auto-save logic
├── config.py             # Configuration loading
└── errors.py             # Custom exceptions
```

### Handler Pattern

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class MCPToolHandler(ABC):
    """Base class for MCP tool implementations."""

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Unique identifier for this tool."""
        pass

    @property
    @abstractmethod
    def tool_schema(self) -> Dict[str, Any]:
        """JSON Schema for tool input parameters."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass
```

### Tool Registration

```python
class MCPServer:
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}

    def register_handler(self, method: str, handler: Callable) -> None:
        self.handlers[method] = handler
        logging.info(f"Registered handler: {method}")

    async def dispatch(self, method: str, params: dict) -> Any:
        if method not in self.handlers:
            raise MethodNotFoundError(method)
        return await self.handlers[method](**params)
```

---

## 3. Resilient API Communication

### Exponential Backoff with Jitter

```python
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx
import asyncio
import random

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    reraise=True
)
async def call_external_api(client: httpx.AsyncClient, endpoint: str, **kwargs):
    """API call with automatic retry on transient failures."""
    response = await client.post(endpoint, **kwargs)

    # Handle rate limiting
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 60))
        # Add jitter to prevent thundering herd
        wait_time = retry_after + random.uniform(0, 5)
        await asyncio.sleep(wait_time)
        raise httpx.HTTPError("Rate limited, retry")

    # Retry 5xx, fail fast on 4xx
    if 500 <= response.status_code < 600:
        response.raise_for_status()  # Triggers retry

    response.raise_for_status()  # 4xx fails immediately
    return response.json()
```

### Error Classification

| Status | Action | Reason |
|--------|--------|--------|
| 429 | Retry with Retry-After | Rate limited |
| 500-599 | Retry with backoff | Transient server error |
| 400-499 | Fail immediately | Client error (fix code) |
| Network timeout | Retry | Transient |
| DNS resolution | Retry | Transient |

---

## 4. Auto-Save Pipeline (Zero Information Loss)

### Dual-Format Pattern

Every API interaction should be saved in two formats:
1. **Raw JSON** - Machine-readable, complete fidelity
2. **Markdown** - Human-readable, searchable

```python
import json
import hashlib
from datetime import datetime
from pathlib import Path

def auto_save(query: str, response: dict, base_path: Path) -> dict:
    """Save query/response in dual format with checksum."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(query[:50])
    filename = f"{timestamp}_{slug}"

    # Raw JSON (complete fidelity)
    raw_path = base_path / "raw" / f"{filename}.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_content = json.dumps({
        "query": query,
        "response": response,
        "timestamp": timestamp,
        "model": response.get("model", "unknown")
    }, indent=2)
    raw_path.write_text(raw_content)

    # SHA-256 checksum for fixity
    checksum = hashlib.sha256(raw_content.encode()).hexdigest()

    # Markdown (human-readable)
    md_path = base_path / "docs" / f"{filename}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_content = format_as_markdown(query, response, timestamp, raw_path, checksum)
    md_path.write_text(md_content)

    return {
        "raw_path": str(raw_path),
        "md_path": str(md_path),
        "checksum": checksum
    }
```

### Markdown Template

```markdown
# Perplexity Research: {topic}

> **Date:** {date}
> **Model:** {model}
> **Checksum:** {sha256}
> **Raw JSON:** `{raw_path}`

---

## Query

{query}

---

## Response

{response_text}

---

## Citations

{citations}
```

---

## 5. Testing Strategy

### Three Levels of Testing

| Level | What | How |
|-------|------|-----|
| **Unit** | Handler logic | Mock API client |
| **Integration** | JSON-RPC serialization | Mock stdin/stdout |
| **E2E** | Full server | Subprocess communication |

### Unit Test Pattern

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_api_client():
    client = AsyncMock()
    client.search.return_value = {"results": [{"title": "Test"}]}
    return client

@pytest.mark.asyncio
async def test_search_handler_success(mock_api_client):
    from my_mcp.handlers import SearchHandler

    handler = SearchHandler(mock_api_client)
    result = await handler.execute(query="test")

    assert "results" in result
    mock_api_client.search.assert_called_once()
```

### E2E Test Pattern

```python
import subprocess
import json
import sys

def test_full_server_cycle():
    process = subprocess.Popen(
        [sys.executable, "-m", "my_mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Send request
    request = {"jsonrpc": "2.0", "method": "search", "params": {"query": "test"}, "id": 1}
    process.stdin.write(json.dumps(request) + '\n')
    process.stdin.flush()

    # Read response
    response_line = process.stdout.readline()
    response = json.loads(response_line)

    assert response["id"] == 1
    assert "result" in response or "error" in response

    process.terminate()
```

### Manual Testing

```bash
# Initialize
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python -m my_mcp

# List tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python -m my_mcp

# Call tool
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search","arguments":{"query":"test"}}}' | python -m my_mcp
```

---

## 6. Anti-Patterns

### Do NOT Do

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **God-object server** | One class does parsing, validation, API calls, logging | Separate concerns into modules |
| **Logging to stdout** | Breaks JSON-RPC protocol | Log to stderr only |
| **Retrying 4xx errors** | Wastes resources, never succeeds | Fail fast on client errors |
| **Hardcoded API keys** | Security risk, no portability | Use env vars or Doppler |
| **Blocking stdin reads** | Freezes async server | Use `asyncio.run_in_executor` |
| **No request correlation** | Can't debug multi-request flows | Include request ID in logs |
| **Unbounded retries** | Can loop forever | Always set `stop_after_attempt` |
| **No jitter on backoff** | Thundering herd on rate limits | Add random delay |

### Tight Coupling Example

```python
# BAD: Tightly coupled - parser depends on handler implementation
class Server:
    def parse_and_handle(self, raw):
        data = json.loads(raw)
        if data["method"] == "search":
            # Business logic mixed with parsing
            result = self.api_client.search(data["params"]["query"])
            return {"jsonrpc": "2.0", "result": result, "id": data["id"]}
```

```python
# GOOD: Separated concerns
class Server:
    def parse(self, raw: str) -> dict:
        return json.loads(raw)

    def dispatch(self, method: str, params: dict):
        return self.handlers[method](**params)

    def format_response(self, result, request_id):
        return {"jsonrpc": "2.0", "result": result, "id": request_id}
```

---

## 7. Configuration

### Environment-Based (Standalone Mode)

```python
import os

API_KEY = os.environ.get("PERPLEXITY_API_KEY")
if not API_KEY:
    raise ValueError("PERPLEXITY_API_KEY environment variable required")
```

### Doppler-Based (Integrated Mode)

```python
import subprocess
import json

def get_secret(key: str) -> str:
    """Fetch secret from Doppler."""
    result = subprocess.run(
        ["doppler", "secrets", "get", key, "--plain"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise ValueError(f"Failed to get secret: {key}")
    return result.stdout.strip()
```

### Config Loading Order

1. Environment variables (highest priority)
2. Doppler secrets (if integrated mode)
3. Config file (lowest priority)

---

## 8. References

| Resource | URL |
|----------|-----|
| JSON-RPC 2.0 Spec | https://www.jsonrpc.org/specification |
| MCP Protocol Spec | https://modelcontextprotocol.io/docs |
| Tenacity (retry library) | https://tenacity.readthedocs.io |
| httpx (async HTTP) | https://www.python-httpx.org |

### Source Research

| Document | Location |
|----------|----------|
| MCP Factory Design (Full) | `${RESEARCH_DIR}/docs/20260122_MCP_FACTORY_DESIGN_FULL.md` |
| Architectural Best Practices | `${RESEARCH_DIR}/docs/20260122_160942_comprehensive_analysis_*.md` |

---

## Version

| Field | Value |
|-------|-------|
| Doc Version | 1.0.0 |
| Created | 2026-01-22 |
| Source | Perplexity sonar-deep-research |
| Research Lines | ~2,000 |
