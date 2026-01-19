[Home](../README.md) > [Docs](./README.md) > **Glossary**

---

# Glossary

Project-specific terms mapped to code locations and schema paths.

---

## Core Concepts

| Term | JSON Path | Valid Values | Where Computed |
|------|-----------|--------------|----------------|
| Atom | `$.particles[*].atom` | `string` (Phase.Family.Name) | `src/core/atom_classifier.py` |
| Codespace | `$.particles[*]` | Array of classified entities | `src/core/unified_analysis.py` |
| Collider | (Tool output) | `unified_analysis.json`, `output.md`, HTML | `src/core/full_analysis.py` |

## Phases & Families

| Term | JSON Path | Valid Values | Where Computed |
|------|-----------|--------------|----------------|
| DATA Phase | `$.particles[*].atom` starts with `DAT` | Primitives, Variables, Constants | `schema/particle.schema.json` |
| LOGIC Phase | `$.particles[*].atom` starts with `LOG` | Functions, Expressions, Statements | `schema/particle.schema.json` |
| ORGANIZATION Phase | `$.particles[*].atom` starts with `ORG` | Classes, Modules, Services | `schema/particle.schema.json` |
| EXECUTION Phase | `$.particles[*].atom` starts with `EXE` | Handlers, Initializers, Workers | `schema/particle.schema.json` |

## Graph Structure

| Term | JSON Path | Valid Values | Where Computed |
|------|-----------|--------------|----------------|
| Node | `$.particles[*]` | object with id, atom, location | `src/core/unified_analysis.py` |
| Edge | `$.particles[*].edges_out[*]` | object with source, target, type | `src/core/edge_extractor.py` |
| In-Degree | `$.particles[*].metrics.in_degree` | integer >= 0 | `src/core/graph_analyzer.py` |
| Out-Degree | `$.particles[*].metrics.out_degree` | integer >= 0 | `src/core/graph_analyzer.py` |

## Analysis Concepts

| Term | JSON Path | Valid Values | Where Computed |
|------|-----------|--------------|----------------|
| Antimatter | `$.particles[*].violations[*]` | violation_type, severity | `src/core/antimatter_evaluator.py` |
| Dead Code | `$.execution_flow.orphans[*]` | array of node IDs | `src/core/execution_flow.py` |
| Knot | `$.knots.cycles[*]` | array of node IDs | `src/core/topology_reasoning.py` |
| Layer | `$.particles[*].ddd.layer` | Domain, Application, Infrastructure, UI | `src/core/purpose_field.py` |
| Role | `$.particles[*].metadata.role` | Repository, Entity, Controller, Service | `src/core/heuristic_classifier.py` |
| Topology | `$.statistics.topology` | Star, Mesh, Hierarchical, Islands | `src/core/topology_reasoning.py` |

## RPBL Scoring

| Term | JSON Path | Valid Values | Where Computed |
|------|-----------|--------------|----------------|
| Responsibility | `$.rpbl_profile.responsibility` | float 0-10 | `src/core/unified_analysis.py` |
| Purity | `$.rpbl_profile.purity` | float 0-10 | `src/core/unified_analysis.py` |
| Boundary | `$.rpbl_profile.boundary` | float 0-10 | `src/core/unified_analysis.py` |
| Lifecycle | `$.rpbl_profile.lifecycle` | float 0-10 | `src/core/unified_analysis.py` |

## Execution & Flow

| Term | JSON Path | Valid Values | Where Computed |
|------|-----------|--------------|----------------|
| Entry Point | `$.execution_flow.entry_points[*]` | node IDs | `src/core/execution_flow.py` |
| Dead Code % | `$.coverage.dead_code_percent` | float 0-100 | `src/core/execution_flow.py` |

## Output Files

| Term | JSON Path | Valid Values | Where Computed |
|------|-----------|--------------|----------------|
| Unified Analysis | `unified_analysis.json` | Complete graph | `src/core/unified_analysis.py` |
| Brain Download | `output.md` | LLM-optimized report | `src/core/brain_download.py` |
| Collider Report | `collider_report.html` | 3D visualization | `src/core/viz/` |

---

See also: [THEORY_MAP](./THEORY_MAP.md) for conceptual relationships.
