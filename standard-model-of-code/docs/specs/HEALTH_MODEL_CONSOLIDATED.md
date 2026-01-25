# Health Model - Consolidated Specification

> **Status:** CANONICAL
> **Last Updated:** 2026-01-24

---

## One-Sentence Thesis

A codebase is a directed system whose health is the combination of:
1. **Structural shape and coupling dynamics** (Geometry lens)
2. **How faithfully each part behaves according to its declared purpose** (Semantics lens)

---

## The Formula

```
H(G) = 10 × (w_T×T + w_E×E + w_Gd×Gd + w_A×A)
```

| Component | Symbol | Weight | Measures |
|-----------|--------|--------|----------|
| Topology | T(G) | 0.25 | Cycles + modularity (Betti numbers) |
| Elevation | E(G) | 0.25 | Complexity terrain (CC, LOC, fan-out) |
| Gradients | Gd(G) | 0.25 | Coupling risk (uphill dependencies) |
| Alignment | A(G) | 0.25 | Purpose ↔ behavior fidelity |

**Output:** Score 0-10, Grade A-F

---

## Component Details

### T(G) - Topology

Combined cycle freedom (60%) + modularity (40%).

```
T = 0.6 × cycle_score + 0.4 × isolation_score

cycle_score:
  b₁ = 0      → 10.0
  b₁ ≤ 5     → 10.0 - (b₁ × 1.5)
  b₁ > 5     → max(1.0, 10.0 - (b₁ × 0.5))

isolation_score:
  ideal = sqrt(n)
  deviation = |b₀ - ideal| / ideal
  score = max(2.0, 10.0 - (deviation × 5))
```

### E(G) - Elevation

Lower average elevation = healthier.

```
E = max(0, 10.0 - avg_elevation)

elevation(node) = f(cyclomatic_complexity, fan_out, LOC, maintainability_index)
```

### Gd(G) - Gradients

Fewer uphill dependencies = healthier.

```
Gd = max(1.0, 10.0 - (problematic_ratio × 10))

problematic = edges with risk == 'HIGH' (steep uphill)
```

### A(G) - Alignment

Weighted PurityAlignmentScore.

```
A = (Σ w(v) × Q_purity(v)) / (Σ w(v)) × 10

w(v) = confidence(v) × (1 + pagerank_boost(v))
Q_purity(v) = D6_pure_score ∈ [0,1]
```

---

## Grade Scale

| Score | Grade | Meaning |
|-------|-------|---------|
| 9-10 | A | Excellent architecture |
| 8-9 | B | Good architecture |
| 7-8 | C | Acceptable |
| 5-7 | D | Needs improvement |
| <5 | F | Major issues |

---

## CLI Usage

```bash
# Basic
./collider grade <path>
# Output: Health: 5.4/10 (D)

# Verbose
./collider grade <path> -v
# Shows component breakdown

# JSON
./collider grade <path> --json
# Machine-readable output
```

---

## Implementation

| File | What |
|------|------|
| `src/core/topology_reasoning.py` | `LandscapeHealthIndex`, `LandscapeProfile` |
| `cli.py` | `grade` command handler |

---

## Version

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Last Updated | 2026-01-24 |
