# Project Map: State of the Topology

## The Core Architecture
```mermaid
graph TD
    Root[PROJECT_elements] --> Context[context-management]
    Root --> Body[standard-model-of-code]
    Root --> Assets[assets/]
    Root --> Archive[archive/]

    subgraph BRAIN ["The Brain (Context)"]
        Context --> Docs[docs/]
        Context --> CTools[tools/]
        Docs --> Manual[AI_OPERATING_MANUAL.md]
        Docs --> Theory[THEORY.md]
        Docs --> EvalLog[EVAL_LOG.md]
        CTools --> AI[ai/ (analyze.py)]
        CTools --> Mirror[archive/ (archive.py)]
    end

    subgraph BODY ["The Body (Implementation)"]
        Body --> Src[src/ (Collider Engine)]
        Body --> Tests[tests/]
        Body --> Exp[experiments/]
        Body --> BSchema[schema/]
    end

    subgraph STORAGE ["Storage"]
        Assets --> Contextpacks[*.zip contextpacks]
        Assets --> PDFs[Research PDFs]
        Assets --> CSVs[Timestamps, logs]
        Archive --> Orphaned[orphaned_* legacy]
        Archive --> Zombie[zombie_code]
    end

    style Context fill:#e3f2fd,stroke:#1565c0
    style Body fill:#e8f5e9,stroke:#2e7d32
    style Assets fill:#fff3e0,stroke:#ef6c00
    style Archive fill:#fce4ec,stroke:#c2185b
```

## Directory Structure

```
PROJECT_elements/
├── README.md                    # Entry point
├── WORKFLOWS.md                 # Orchestration
├── PROJECT_MAP.md               # This file
│
├── context-management/          # THE BRAIN
│   ├── docs/                    #   Theory, manuals, EVAL_LOG.md
│   ├── tools/                   #   AI tools, archive scripts
│   ├── config/                  #   Configuration
│   └── registry/                #   Registry data
│
├── standard-model-of-code/      # THE BODY
│   ├── src/core/                #   Collider engine
│   ├── schema/                  #   Type definitions
│   ├── tests/                   #   Test suite
│   └── .archive/                #   Repo-level archive (gitignored)
│
├── assets/                      # ARTIFACTS
│   ├── *.zip                    #   Contextpacks
│   ├── *.pdf                    #   Research papers
│   └── *.csv                    #   Timestamps, logs
│
├── archive/                     # COLD STORAGE
│   ├── orphaned_*               #   Legacy code by date
│   ├── spectrometer_*           #   Old tool versions
│   └── zombie_code/             #   Dead code
│
├── llm-threads/                 # SESSION LOGS
│   └── *.md                     #   Claude/Gemini chats
│
└── related/                     # EXTERNAL
    └── chrome-mcp/              #   MCP tooling
```

## Remaining Cleanup (Optional)

| Item | Status | Notes |
|------|--------|-------|
| `llm-threads/` | Keep | Valuable session history |
| `related/` | Keep | External dependencies |
| `archive/` | Keep | Cold storage, rarely touched |
