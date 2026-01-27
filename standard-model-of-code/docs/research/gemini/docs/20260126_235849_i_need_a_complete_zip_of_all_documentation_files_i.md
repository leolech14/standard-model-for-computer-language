# Research: I need a complete zip of ALL documentation files in the repository - every .md, .yaml config, and sc...

> **Date:** 2026-01-26 23:58:49
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:a0d39144a927e27c9601e5b2ea359d9e351bba2e6c7bff3f604e5aa4914c4fc8`
> **Raw JSON:** `raw/20260126_235849_i_need_a_complete_zip_of_all_documentation_files_i.json`

---

## Query

I need a complete zip of ALL documentation files in the repository - every .md, .yaml config, and schema file - not just orientation files. What's the best approach?

---

## Response

Based on the codebase context (specifically `TOPOLOGY_MAP.md` and `CLEANUP_PLAN.md`), you are asking to export the **Contextome** (all non-executable content) while excluding the massive generated data files (like the 800MB `unified_analysis.json`).

There is no pre-existing script for this specific "full context" dump (the existing `sync-orientation-files.sh` is too narrow).

Here is the best approach using standard tools to create a clean **Contextome Bundle**:

### The Command

Run this from the root of `PROJECT_elements`. It finds all documentation, config, and schema files while aggressively excluding build artifacts, python environments, and massive analysis outputs.

```bash
find . -type f \
    \( -name "*.md" -o -name "*.yaml" -o -name "*.json" \) \
    -not -path "*/.git/*" \
    -not -path "*/.venv/*" \
    -not -path "*/.tools_venv/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/output/*" \
    -not -path "*/collider_output/*" \
    -not -path "*/.data/*" \
    -not -path "*/.collider/*" \
    -print0 | xargs -0 zip -r full_contextome.zip
```

### What this includes (The "Wave" & "Observer" Realms)
1.  **Documentation**: All `.md` files from `context-management/docs/`, `standard-model-of-code/docs/`, and `.agent/`.
2.  **Configuration**: All `.yaml` files (including `aci_config.yaml`, `semantic_models.yaml`, `analysis_sets.yaml`).
3.  **Schemas**: All `.json` schemas from `standard-model-of-code/schema/`.
4.  **Agent State**: All task registries and sprint logs in `.agent/`.

### What this excludes (To save space)
1.  **Analysis Artifacts**: `unified_analysis.json` (often ~800MB).
2.  **Virtual Envs**: `.tools_venv`, `node_modules`.
3.  **Build Outputs**: `collider_output/`, `.collider/`.

### Verification
To verify the contents before zipping, you can run a dry-list:

```bash
find . -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.json" \) \
    -not -path "*/.git/*" -not -path "*/.venv/*" -not -path "*/.tools_venv/*" \
    -not -path "*/node_modules/*" -not -path "*/output/*" -not -path "*/collider_output/*" \
    -not -path "*/.data/*" -not -path "*/.collider/*" | sort
```

### Why not use `archive.py`?
The tool `context-management/tools/archive/archive.py` (referenced in `ASSET_INVENTORY.md`) is designed to mirror the repository to Google Cloud Storage (GCS) for AI retrieval. While it handles the "Brain" logic, it doesn't currently support a local zip export of the full Contextome without also trying to push to the cloud.

---

## Citations

_No citations provided_
