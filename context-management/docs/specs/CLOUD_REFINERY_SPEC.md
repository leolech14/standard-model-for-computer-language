# Cloud Refinery Specification

> **Status:** DRAFT
> **Created:** 2026-01-25
> **Author:** Claude + Leonardo
> **Location:** Wave Hemisphere (context-management)

---

## Overview

The **Cloud Refinery** is a 24/7 cloud intelligence layer that continuously processes Collider output into a refined, queryable knowledge corpus called the **Projectome**.

```
LOCAL                              CLOUD
─────                              ─────
Collider (Particle)         →      Cloud Refinery (Processing)
unified_analysis.json       →      Projectome (Corpus)
Local Consumers             ←      Gates (Query API)
```

---

## Architecture Position

| Layer | Name | Role |
|-------|------|------|
| **Particle** | Collider | Measures code → unified_analysis.json |
| **Wave** | Cloud Refinery | Refines knowledge 24/7 |
| **Observer** | .agent/ | Decides what to measure, acts on insights |

Cloud Refinery sits between Particle (raw measurement) and Observer (action), providing the refined intelligence that informs decisions.

---

## Theoretical Foundation

The Cloud Refinery is grounded in two complementary frameworks:

### Peirce's Triadic Semiotics

| Peirce Term | Projectome Mapping |
|-------------|-------------------|
| Sign (Representamen) | Codome (code artifacts) |
| Interpretant | Contextome (docs, specs, theory) |
| Object | Runtime behavior |
| **Semiosis** | **Cloud Refinery** (interpretation process) |

The Refinery performs **semiosis** - the continuous interpretation that transforms signs into meaning.

### Friston's Free Energy Principle (Active Inference)

| Cognitive Concept | Cloud Refinery Mapping |
|-------------------|----------------------|
| Generative model | Projectome knowledge corpus |
| Sensory input | New unified_analysis.json |
| Prediction error | Anomalies, drift detection |
| Free energy minimization | Distillation (R0→R5) |
| Background processing | 24/7 continuous refinement |

The Refinery operates like the **subconscious mind**: processing continuously in the background, generating predictions, minimizing surprise, and surfacing insights on demand via Gates.

> See `standard-model-of-code/docs/theory/PROJECTOME_THEORY.md` for full theoretical treatment.

---

## Core Principles

1. **Single Writer**: Only Collider produces raw state
2. **Continuous Refinement**: Cloud processes 24/7, not on-demand
3. **Layered Distillation**: Raw → Indexed → Normalized → Enriched → Distilled → Emergent
4. **Gated Access**: Precision queries via defined gates (NEEDLE, SLICE, DIGEST, COMPILE)
5. **Composable Output**: Build larger context from smaller, verified pieces

---

## Distillation Layers

| Layer | ID | Contents | Update Frequency |
|-------|-----|----------|------------------|
| **Raw** | R0 | unified_analysis.json snapshots | On commit/push |
| **Indexed** | R1 | Searchable, tagged, timestamped | On R0 arrival |
| **Normalized** | R2 | Schema-aligned, deduplicated, linked | Daily |
| **Enriched** | R3 | AI-annotated, relationships inferred | Daily |
| **Distilled** | R4 | Summaries, patterns, insights | Daily |
| **Emergent** | R5 | Purpose field, trends, predictions | Weekly |

### Layer Details

#### R0: Raw
- Direct copy of unified_analysis.json
- Timestamped snapshots
- No processing, pure preservation
- Enables time-travel queries

#### R1: Indexed
- JSONL format for streaming
- Tags: file type, language, atom type, role
- Full-text search index
- Timestamp normalization (ISO 8601)

#### R2: Normalized
- Schema validation against particle.schema.json
- Deduplication (same node across snapshots)
- Cross-reference linking (node → file → edge)
- Canonical ID assignment

#### R3: Enriched
- Gemini/Vertex AI annotations
- Relationship inference (implicit dependencies)
- Semantic clustering
- Embedding generation for vector search

#### R4: Distilled
- Per-file summaries
- Per-module summaries
- Architecture pattern detection
- Anomaly flagging

#### R5: Emergent
- Purpose field computation (why does this code exist?)
- Trend analysis (what's changing?)
- Drift detection (divergence from spec)
- Predictions (what will break?)

---

## Gates (Query API)

| Gate | Purpose | Input | Output |
|------|---------|-------|--------|
| **NEEDLE** | Exact lookup | ID or path | Single record |
| **SLICE** | Filtered range | Filter criteria | Record set |
| **DIGEST** | Topic summary | Topic/area | Prose summary |
| **COMPILE** | Composed set | Set names | Merged context |

### Gate Examples

```bash
# NEEDLE: Find specific node
GET /gates/needle?id=UserService.validate

# SLICE: All orphaned files from last 7 days
GET /gates/slice?filter=orphan:true&days=7

# DIGEST: Summarize pipeline architecture
GET /gates/digest?topic=pipeline

# COMPILE: Build context for tree-sitter work
GET /gates/compile?sets=tree_sitter,queries,tests
```

---

## GCP Infrastructure

### Services

| Service | Role | Tier |
|---------|------|------|
| **Cloud Storage** | Projectome storage | Standard |
| **Cloud Functions** | R0→R1, R1→R2 processing | Gen2 |
| **Vertex AI** | R2→R3→R4→R5 enrichment | Pay-per-use |
| **Cloud Run** | Gates API | Min instances: 1 |
| **Cloud Scheduler** | Trigger daily/weekly jobs | - |
| **Eventarc** | Event routing | - |

### Bucket Structure

```
gs://elements-archive-2026/
└── projectome/
    ├── R0_raw/
    │   └── YYYY-MM-DD/
    │       └── unified_analysis.json
    ├── R1_indexed/
    │   ├── files.jsonl
    │   ├── nodes.jsonl
    │   ├── edges.jsonl
    │   └── metadata.json
    ├── R2_normalized/
    │   └── canonical.json
    ├── R3_enriched/
    │   ├── annotations.json
    │   └── embeddings.jsonl
    ├── R4_distilled/
    │   ├── summaries/
    │   ├── patterns/
    │   └── anomalies/
    ├── R5_emergent/
    │   ├── purpose_field.json
    │   ├── trends.json
    │   └── predictions.json
    └── gates/
        └── cache/
```

---

## Data Flow

```
1. LOCAL: ./collider full . --output .collider
      │
      ▼
2. LOCAL: unified_analysis.json created
      │
      ▼
3. LOCAL: archive.py mirror (or git hook)
      │
      ▼
4. CLOUD: gs://elements-archive-2026/projectome/R0_raw/
      │
      ▼ (Eventarc trigger)
5. CLOUD: Cloud Function: index_raw()
      │
      ▼
6. CLOUD: R1_indexed/ populated
      │
      ▼ (Cloud Scheduler: daily)
7. CLOUD: Cloud Function: normalize()
      │
      ▼
8. CLOUD: R2_normalized/ populated
      │
      ▼ (Cloud Scheduler: daily)
9. CLOUD: Vertex AI Pipeline: enrich()
      │
      ▼
10. CLOUD: R3_enriched/, R4_distilled/ populated
      │
      ▼ (Cloud Scheduler: weekly)
11. CLOUD: Vertex AI Pipeline: emerge()
      │
      ▼
12. CLOUD: R5_emergent/ populated
      │
      ▼
13. LOCAL: analyze.py --refinery "query"
      │
      ▼
14. CLOUD: Gates API responds with refined knowledge
```

---

## Local Integration

### analyze.py Extension

```bash
# Query Cloud Refinery instead of local context
python analyze.py --refinery "What changed in the pipeline this week?"

# Force specific gate
python analyze.py --refinery --gate digest "Summarize tree-sitter status"

# Compile custom context from Projectome
python analyze.py --refinery --gate compile --sets "pipeline,tests,tasks"
```

### Maintenance Module Integration

```bash
# Hygiene checks use R4 anomalies
./maintain hygiene --source refinery

# Archive decisions informed by R5 predictions
./maintain archive --check-refinery
```

---

## Implementation Phases

| Phase | Deliverable | Dependencies | Effort |
|-------|-------------|--------------|--------|
| **P1** | archive.py → R0 push | GCS bucket exists | 2h |
| **P2** | Cloud Function: R0 → R1 | P1 | 4h |
| **P3** | Gates API (NEEDLE, SLICE) | P2 | 8h |
| **P4** | Vertex AI: R1 → R3 | P2, Vertex setup | 8h |
| **P5** | R3 → R4 → R5 pipelines | P4 | 8h |
| **P6** | analyze.py --refinery | P3 | 4h |
| **P7** | DIGEST, COMPILE gates | P4 | 6h |

**Total: ~40 hours**

---

## Security & Access

| Resource | Access |
|----------|--------|
| GCS Bucket | Service account only |
| Cloud Functions | Internal only (no public) |
| Gates API | Authenticated (API key or IAM) |
| Vertex AI | Service account |

### Secrets

| Secret | Location |
|--------|----------|
| GCP Service Account | Doppler: `GCP_SERVICE_ACCOUNT_JSON` |
| Gemini API Key | Doppler: `GEMINI_API_KEY` |
| Gates API Key | Doppler: `REFINERY_API_KEY` |

---

## Monitoring

| Metric | Alert Threshold |
|--------|-----------------|
| R0 upload failures | > 0 |
| R1 indexing latency | > 5 min |
| R3 enrichment errors | > 10% |
| Gates API latency | > 2s p95 |
| Storage growth | > 10GB/month |

---

## Cost Estimates

| Service | Est. Monthly |
|---------|--------------|
| Cloud Storage (10GB) | $0.20 |
| Cloud Functions (1M invocations) | $0.40 |
| Cloud Run (min instance) | $5.00 |
| Vertex AI (Gemini, moderate use) | $20.00 |
| **Total** | **~$26/month** |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Query latency (NEEDLE) | < 200ms |
| Query latency (DIGEST) | < 5s |
| R0 → R1 latency | < 1 min |
| R1 → R5 freshness | < 24h |
| Uptime | 99.5% |

---

## Related Documents

| Document | Relationship |
|----------|--------------|
| `ARCHITECTURE_MAP.md` | Parent architecture |
| `SUBSYSTEM_INTEGRATION.md` | Integration points |
| `archive.py` | Ingestion mechanism |
| `sync_registry.py` | Sync pattern reference |
| `../../../standard-model-of-code/docs/specs/REGISTRY_OF_REGISTRIES.md` | What gets indexed |
| `PROJECTOME_THEORY.md` | Theoretical foundation (semiotics, active inference) |
| `ANALOGY_SCORING_METHODOLOGY.md` | Methodology for validating architectural analogies |

---

## Open Questions

1. **Embedding model**: Use Gemini embeddings or separate model?
2. **Retention policy**: How long to keep R0 snapshots?
3. **Multi-project**: Scale to other PROJECT_* repos?
4. **Real-time**: WebSocket for live updates vs polling?

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-25 | Initial draft |
| 0.2.0 | 2026-01-25 | Added theoretical foundation (Peirce, Friston) |

---

*Part of PROJECT_elements - Wave Hemisphere*
