# Research: what command should I use to create a zip file containing all documentation files from this reposito...

> **Date:** 2026-01-26 23:57:14
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:7004b944ce14ae02fc66f8196963330c7df966d7d14c9334fe5cd66303fd4d0f`
> **Raw JSON:** `raw/20260126_235714_what_command_should_i_use_to_create_a_zip_file_con.json`

---

## Query

what command should I use to create a zip file containing all documentation files from this repository for external audit?

---

## Response

Based on the `context-management/docs/ORIENTATION_FILES.md` documentation, the system has a dedicated tool for exporting key context and documentation into a zip file for external sharing or AI context loading.

To create the zip file (`orientation-files.zip`), run the following command from the project root:

```bash
./standard-model-of-code/scripts/sync-orientation-files.sh --zip
```

### Details
*   **What it does:** Collects core documentation (`README.md`, `VISION.md`, `THEORY.md`, `TOOL.md`, specs, schemas) from the working directory.
*   **Output Location:** Creates `~/Downloads/orientation-files.zip` (and a corresponding folder).
*   **Content:** Contains the "Contextome" essentials needed for an external agent or collaborator to understand the project without the full codebase.

**Note:** If you want to continuously sync these files to a folder as you edit them (for a local context pack), you can use the `--watch` flag instead.

---

## Citations

_No citations provided_
