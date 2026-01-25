# Research: What background refinement processes exist? List auto-boost, cloud refinery systems. Are they deploy...

> **Date:** 2026-01-23 16:25:29
> **Source:** gemini
> **Model:** gemini-2.0-flash
> **Checksum:** `sha256:bb09548a35ae112659939f8c826657efff17c313d1ab56ed5a19d72369023e98`
> **Raw JSON:** `raw/20260123_162529_what_background_refinement_processes_exist__list_a.json`

---

## Query

What background refinement processes exist? List auto-boost, cloud refinery systems. Are they deployed and running?

---

## Response

```json
{
  "background_refinement_processes": [
    {
      "name": "TruthValidator",
      "description": "Validates core truths from roles.json and outputs repo_truths.yaml",
      "auto_boost": true,
      "cloud_refinery": true,
      "deployed": true,
      "running": true,
      "source_file": "context-management/tools/ai/analyze.py",
      "related_files": [
        "context-management/config/semantic_models.yaml",
        "context-management/config/aci_config.yaml"
      ]
    },
    {
      "name": "CrossValidator",
      "description": "Checks for code-docs drift by comparing code to associated documentation and checks documentation against Antimatter Laws",
      "auto_boost": true,
      "cloud_refinery": true,
      "deployed": true,
      "running": true,
      "source_file": "context-management/tools/ai/analyze.py",
      "related_files": [
        "context-management/config/semantic_models.yaml",
        "context-management/config/aci_config.yaml"
      ]
    },
    {
      "name": "ConceptMapper",
      "description": "Generates a semantic graph of code and its relationships and creates concept_graph.yaml",
      "auto_boost": true,
      "cloud_refinery": true,
      "deployed": false,
      "running": false,
      "source_file": "context-management/tools/ai/analyze.py",
      "related_files": [
        "context-management/config/semantic_models.yaml",
        "context-management/config/aci_config.yaml"
      ]
    }
  ],
  "justification": "Based on KERNEL.md, agent_intelligence/*, and HOLOGRAPHIC_SOCRATIC_LAYER.md. Status also checked against  .agent/registry/active. TODO: Check for activeLaunchAgent."
}
```

---

## Citations

_No citations provided_
