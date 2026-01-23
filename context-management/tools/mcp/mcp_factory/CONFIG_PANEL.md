# MCP Factory - Configuration Panel

> Single source of truth for all integration bindings. Change these values to adapt MCP Factory to any context.

---

## Current Binding

```yaml
mode: INTEGRATED
host_project: PROJECT_elements
host_repo: https://github.com/leolech14/standard-model-of-code
```

---

## Path Variables

| Variable | Current Value | Standalone Default |
|----------|---------------|-------------------|
| `${MCP_FACTORY_ROOT}` | `context-management/tools/mcp/mcp_factory/` | `./` |
| `${SERVERS_DIR}` | `context-management/tools/mcp/` | `./servers/` |
| `${TOOLS_DIR}` | `context-management/tools/` | `./tools/` |
| `${RESEARCH_DIR}` | `standard-model-of-code/docs/research/perplexity/` | `./docs/research/` |
| `${SECRETS_MANAGER}` | Doppler (`ai-tools/dev`) | Environment variables |
| `${ARCHIVE_BUCKET}` | `gs://elements-archive-2026/` | Local `./archive/` |

---

## Integration Points

| Feature | Integrated Binding | Standalone Alternative |
|---------|-------------------|----------------------|
| **Secrets** | `doppler secrets get KEY --project ai-tools --config dev` | `os.environ.get('KEY')` |
| **Archival** | GCS bucket via `archive.py` | Local filesystem |
| **Research Auto-Save** | Perplexity pipeline → `${RESEARCH_DIR}` | Optional, disable |
| **Documentation** | Part of Brain hemisphere docs | Self-contained |

---

## Dependencies

### Required (Any Mode)

```
python >= 3.10
```

### Integrated Mode

```
doppler-cli          # Secrets management
google-cloud-storage # GCS archival
```

### Standalone Mode

```
# No external dependencies beyond Python stdlib
# Secrets via environment variables
# Archival via local filesystem
```

---

## Feature Flags

```yaml
# Toggle features based on mode
features:
  auto_save_research: true      # Save Perplexity outputs automatically
  gcs_archival: true            # Mirror to cloud storage
  doppler_secrets: true         # Use Doppler for API keys
  registry_tracking: true       # Track deployed servers in registry

# Standalone overrides (when mode: STANDALONE)
standalone_overrides:
  auto_save_research: true      # Still works, saves locally
  gcs_archival: false           # Disabled
  doppler_secrets: false        # Use env vars instead
  registry_tracking: true       # Local registry file
```

---

## Reference Implementation

| Server | Path | Description |
|--------|------|-------------|
| **Perplexity** | `${SERVERS_DIR}/perplexity_mcp_server.py` | Auto-save pipeline reference |

---

## How to Use This Panel

### Reading Documentation

All MCP Factory docs use `${VARIABLE}` syntax. Mentally substitute:
- If **integrated**: Use "Current Value" column
- If **standalone**: Use "Standalone Default" column

### Extracting to Standalone

1. Copy `mcp_factory/` to new repo
2. Update this panel: `mode: STANDALONE`
3. Replace Doppler calls with `os.environ.get()`
4. Replace GCS paths with local paths
5. Run `tools/validate.py` to check

### Adapting to Different Host

1. Update `host_project` and `host_repo`
2. Update path variables to match new structure
3. Update integration points if host has different infra

---

## Version

| Field | Value |
|-------|-------|
| Panel Version | 1.0.0 |
| Last Updated | 2026-01-22 |
| Updated By | Claude + Leonardo |
