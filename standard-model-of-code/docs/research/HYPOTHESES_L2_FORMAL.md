# L2 Hypotheses: Formal Specification

> **Status:** L2 (Calibration-Derived, Pending 100+ Validation)
> **Evidence Pack:** `artifacts/atom-research/2026-01-23-calibration/2026-01-23/`
> **Seal:** `MANIFEST.sha256` (236 entries, verified)
> **Calibration Sample:** n=33 repos, 77,265 nodes, 6 languages

---

## H1: Top-4 Mass Concentration

### H1a: Central Tendency Claim

**Population:**
- Repos: Public GitHub repositories with ≥100 stars, active in last 2 years
- Exclusions: Generated code >50%, vendored dependencies, forks
- Stratification: 6 languages × ~17 repos each

**Measurement:**
- Metric: `top_4_mass` = (sum of top-4 atom counts) / (total nodes) × 100
- Computation: Mode A deterministic (no AI enrichment)
- Unit: Per-repo percentage

**Statistic:**
- Central tendency: median(top_4_mass) across all repos
- Uncertainty: Bootstrap 95% CI (1000 iterations)

**Decision Rule:**
```
PASS IF:
  median(top_4_mass) ≥ 90%
  AND CI95_lower_bound ≥ 85%

FAIL IF:
  CI95_lower_bound < 85%
```

**Falsifier:**
- Bootstrap CI95 lower bound falls below 85%

**Calibration Evidence (n=33):**
- Median: 98.8%
- Min: 85.0%, Max: 100.0%
- Estimated CI95: [95.2%, 99.5%] (needs bootstrap confirmation)

---

### H1b: Tail Robustness Claim

**Population:** Same as H1a

**Measurement:** Same as H1a

**Statistic:**
- Tail proportion: P(top_4_mass < 80%)

**Decision Rule:**
```
PASS IF:
  P(top_4_mass < 80%) ≤ 10%
  (i.e., at most 10% of repos have top_4_mass below 80%)

FAIL IF:
  P(top_4_mass < 80%) > 10%
```

**Falsifier:**
- More than 10% of repos have top_4_mass < 80%

**Calibration Evidence (n=33):**
- Repos with top_4_mass < 80%: 0/33 (0%)
- Repos with top_4_mass < 90%: 3/33 (9.1%)
- Lowest: fastapi at 85.0%

---

## H2: Function Atom Dominance

**Population:** Same as H1a

**Measurement:**
- Metric: `dominant_atom` = atom with highest count per repo
- Secondary: `LOG_FNC_M_is_dominant` = boolean (1 if LOG.FNC.M is top-1, 0 otherwise)
- Computation: Mode A deterministic

**Statistic:**
- Global: proportion of repos where LOG.FNC.M is dominant
- Per-language: proportion within each language stratum

**Decision Rule:**
```
PASS IF:
  P(LOG.FNC.M is dominant) ≥ 50% globally
  AND P(LOG.FNC.M is dominant | language) ≥ 30% for each language

FAIL IF:
  Global proportion < 50%
  OR any language stratum < 30%
```

**Falsifier:**
- LOG.FNC.M dominates fewer than 50% of repos globally
- OR any language has <30% LOG.FNC.M dominance

**Calibration Evidence (n=33):**
- Global: LOG.FNC.M dominates 19/33 (57.6%)
- By language:
  - Python: 4/5 (80%) ✓
  - TypeScript: 6/6 (100%) ✓
  - JavaScript: 3/4 (75%) ✓
  - Rust: 4/6 (67%) ✓
  - Go: 1/6 (17%) ⚠️ (EXT.GO.* atoms dominate)
  - Java: 1/5 (20%) ⚠️ (ORG.AGG.M dominates)

**Note:** Go and Java may fail the 30% per-language threshold. This is a known risk.

---

## H3: Language Effect Bound

**Population:** Same as H1a

**Measurement:**
- Metric: `median_top_4_mass_by_language` for each of 6 language strata
- Computation: Mode A deterministic

**Statistic:**
- Spread: max(median_by_lang) - min(median_by_lang)
- Optional: CI overlap test

**Decision Rule:**
```
PASS IF:
  max(median_by_lang) - min(median_by_lang) ≤ 15pp

FAIL IF:
  Spread > 15pp
```

**Falsifier:**
- Any two language strata differ by more than 15 percentage points in median top_4_mass

**Calibration Evidence (n=33):**
| Language | n | Median Top-4 |
|----------|---|--------------|
| Java | 5 | 100.0% |
| TypeScript | 6 | 99.9% |
| JavaScript | 4 | 98.7% |
| Python | 5 | 98.3% |
| Rust | 6 | 94.5% |
| Go | 6 | 93.0% |

- Current spread: 100.0% - 93.0% = **7.0pp** ✓

**Warning:** Java's 100% may reflect fallback parser degeneracy (see Assumption Audit below).

---

## H4: Unknown Rate Bound

**Population:** Same as H1a

**Measurement:**
- Metric: `unknown_rate` = (nodes with atom='Unknown') / (total nodes) × 100
- Computation: Mode A deterministic

**Statistic:**
- Central: median(unknown_rate)
- Worst-case: max(unknown_rate)

**Decision Rule:**
```
PASS IF:
  median(unknown_rate) ≤ 1%
  AND max(unknown_rate) ≤ 5%

FAIL IF:
  median > 1%
  OR max > 5%

CATASTROPHIC FAIL IF:
  Any repo > 10% unknown
```

**Falsifier:**
- Median unknown rate exceeds 1%
- OR any repo exceeds 5% unknown rate

**Calibration Evidence (n=33):**
- Median: 0.21%
- Max: 1.82% (express)
- All repos < 2% ✓

---

## H5: Domain Effect Bound

**Population:** Same as H1a

**Measurement:**
- Metric: `median_top_4_mass_by_domain` for each domain stratum
- Domains: library, web_backend, web_frontend, cli, systems, ml

**Statistic:**
- Spread: max(median_by_domain) - min(median_by_domain)

**Decision Rule:**
```
PASS IF:
  max(median_by_domain) - min(median_by_domain) ≤ 10pp
  AND each domain has n ≥ 3 repos

FAIL IF:
  Spread > 10pp
  OR insufficient sample in any domain
```

**Falsifier:**
- Domain spread exceeds 10 percentage points

**Calibration Evidence (n=33):**
| Domain | n | Median Top-4 |
|--------|---|--------------|
| library | 12 | 99.5% |
| web_frontend | 2 | 98.6% |
| ml | 1 | 98.3% |
| web_backend | 6 | 96.1% |
| cli | 8 | 95.4% |
| systems | 3 | 93.6% |

- Current spread: 99.5% - 93.6% = **5.9pp** ✓
- Warning: web_frontend (n=2) and ml (n=1) have insufficient sample

---

## H6: Metaprogramming Penalty (Exploratory)

**Status:** Not yet L2-grade (requires measurable proxy)

**Population:** Same as H1a

**Measurement:**
- Metric: `metaprogramming_density` (TBD - see options below)
- Options:
  1. Fraction of decorator/macro/template atoms
  2. Lexical token proxy (language-specific)
  3. Atom entropy as diversity proxy

**Statistic:**
- Correlation: Spearman ρ between metaprogramming_density and top_4_mass

**Decision Rule (proposed):**
```
PASS IF:
  Spearman ρ ≤ -0.3 with p < 0.05
  (negative correlation: more metaprogramming → lower top_4_mass)

FAIL IF:
  ρ ≈ 0 or positive
```

**Calibration Observation:**
- 7 outliers (top_4_mass < 95%) are disproportionately Go (3), Rust (3), Python (1)
- Pattern: fastapi (decorators), serde (macros), hugo/lazygit/k9s (templates)
- Hypothesis plausible but not yet testable

**Required for L2 promotion:**
- Implement `metaprogramming_density` metric in Collider
- Re-run calibration with metric
- Compute correlation

---

## Assumption Audit: Parser Fidelity

Before treating Java results as evidence for H3 (language invariance), validate parser output quality.

**Fidelity Metrics (per repo):**
| Metric | Purpose |
|--------|---------|
| `n_files_parsed` | Coverage |
| `nodes_per_1k_loc` | Density |
| `unique_atom_types` | Diversity |
| `pct_fallback_nodes` | Parser quality |

**Decision Rule:**
```
VALID PARSER IF:
  nodes_per_1k_loc ≥ 10
  AND unique_atom_types ≥ 3
  AND pct_fallback_nodes ≤ 50%

DEGENERATE PARSER IF:
  unique_atom_types ≤ 2
  OR nodes_per_1k_loc < 5
```

**Java Calibration Check (n=5):**
- All 5 Java repos show top_4_mass = 100%
- This is suspiciously uniform
- Need to verify: is this real concentration or parser artifact?

---

## Artifacts Required for Validation

For each hypothesis test, the following must be present and sealed:

```
corpus_NNN_validation/
├── corpus.yaml          # Repo definitions
├── results.json         # Computed metrics per repo
├── summary.csv          # Flat export for analysis
├── MANIFEST.sha256      # File hashes
├── SEAL.json            # Seal metadata
└── repos/
    └── {repo_name}/
        └── {sha}/
            ├── output_llm-oriented_*.json
            └── output_human-readable_*.html
```

**Validation Command:**
```bash
python3 tools/research/validate_audit_pack.py \
    artifacts/atom-research/corpus_NNN_validation/ \
    --strict
```

---

## Promotion Criteria: L2 → L3

To promote these hypotheses to L3 (stable theory):

| Hypothesis | L2 Status | L3 Requirement |
|------------|-----------|----------------|
| H1a | Pending | n≥100, CI95 ≥ 85% |
| H1b | Pending | n≥100, tail ≤ 10% |
| H2 | At risk (Go/Java) | Global ≥50%, per-lang ≥30% |
| H3 | Pending | Spread ≤ 15pp |
| H4 | Likely pass | max ≤ 5% |
| H5 | Pending | Spread ≤ 10pp, n≥3 per domain |
| H6 | Exploratory | Needs metric implementation |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-23 | Initial formal specification from calibration |
