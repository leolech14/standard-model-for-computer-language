# PROJECT_elements

## Start Here
```bash
./concierge
```

## Rules (Priority 0)
- Never leave uncommitted changes
- Run tests before claiming done
- Provide summary with rationale

## Commands
| Task | Command |
|------|---------|
| Analyze | `./collider full <path> --output <dir>` |
| Test | `cd standard-model-of-code && pytest tests/ -q` |
| AI Query | `doppler run -- python context-management/tools/ai/analyze.py "query"` |
| Archive | `python context-management/tools/archive/archive.py mirror` |

## Projectome (Navigation Topology)

```
P = C ⊔ X    (disjoint union - MECE partition)
```

| Universe | Definition | Doc |
|----------|------------|-----|
| **CODOME** | All executable code | `context-management/docs/CODOME.md` |
| **CONTEXTOME** | All non-executable content | `context-management/docs/CONTEXTOME.md` |
| **PROJECTOME** | Complete project contents | `context-management/docs/PROJECTOME.md` |
| **DOMAINS** | Vertical slices through both | `context-management/docs/DOMAINS.md` |
| **GLOSSARY** | All terminology | `context-management/docs/GLOSSARY.md` |

## Essential Docs
| Doc | Purpose |
|-----|---------|
| `context-management/docs/operations/AGENT_KERNEL.md` | Core rules, micro-loop |
| `context-management/docs/agent_school/DOD.md` | Definition of Done |
| `context-management/docs/agent_school/WORKFLOWS.md` | Git, commit, PR workflows |

## Domain Entry Points
| Domain | File |
|--------|------|
| Collider (analysis engine) | `standard-model-of-code/CLAUDE.md` |
| Context (AI tools) | `context-management/docs/deep/AI_USER_GUIDE.md` |

## Deep Docs
Theory, architecture, research: `context-management/docs/deep/`
