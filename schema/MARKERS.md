# Theory Document Marker System

## Purpose

Enable programmatic analysis, validation, and reorganization of theory documents.

---

## Marker Syntax

All markers are HTML comments with a specific format:

```
<!-- @MARKER_NAME: value -->
```

---

## Available Markers

### Section Markers (Required)

| Marker | Purpose | Example |
|--------|---------|---------|
| `@SECTION` | Section ID (unique) | `<!-- @SECTION: humble_beginning -->` |
| `@END_SECTION` | Closes a section | `<!-- @END_SECTION: humble_beginning -->` |

### Metadata Markers (Optional but recommended)

| Marker | Purpose | Values |
|--------|---------|--------|
| `@TOPIC` | Topic classification | `epistemic_stance`, `abstraction_levels`, etc. |
| `@ORDER` | Position in hierarchy | `1.0`, `1.1`, `2.0`, `3.1.2` |
| `@DEPENDS_ON` | Prerequisites | Comma-separated section IDs or `none` |
| `@PROVIDES` | Concepts introduced | Comma-separated concept names |
| `@VERSION` | Content version | Semantic version like `1.0.0` |
| `@STATUS` | Content status | `draft`, `review`, `stable` |
| `@SOURCES` | Scientific validation | Comma-separated citations (e.g., `Popper1959`, `Kuhn1962`) |

---

## Section Registry

### PART I: The Humble Beginning
| Section ID | Topic | Order | Provides |
|------------|-------|-------|----------|
| `humble_beginning` | epistemic_stance | 1.0 | epistemic_humility |
| `what_this_is_not` | negative_definition | 1.1 | boundaries |
| `what_this_is` | positive_definition | 1.2 | purpose |
| `operating_principles` | principles | 1.3 | open_world, unknown_first_class |

### PART II: The Problem of Software
| Section ID | Topic | Order | Depends On | Provides |
|------------|-------|-------|------------|----------|
| `problem_of_software` | motivation | 2.0 | humble_beginning | problem_statement |
| `the_question` | central_question | 2.1 | problem_of_software | inquiry_focus |
| `why_no_one_before` | gap_analysis | 2.2 | the_question | three_planes_intro |

### PART III: The Power of Analogies
| Section ID | Topic | Order | Depends On | Provides |
|------------|-------|-------|------------|----------|
| `power_of_analogies` | methodology | 3.0 | humble_beginning | universal_analogy |
| `analogies_we_use` | examples | 3.1 | power_of_analogies | analogy_table |
| `why_analogies_work` | justification | 3.2 | analogies_we_use | isomorphism |

### PART IV: The Layers of Abstraction
| Section ID | Topic | Order | Depends On | Provides |
|------------|-------|-------|------------|----------|
| `layers_of_abstraction` | hierarchy | 4.0 | why_analogies_work | layer_concept |
| `inheritance_chain` | intellectual_ancestry | 4.1 | layers_of_abstraction | lineage |
| `sixteen_levels` | abstraction_scale | 4.2 | layers_of_abstraction | L-3_to_L12 |

### PART V: The Three Bodies
| Section ID | Topic | Order | Depends On | Provides |
|------------|-------|-------|------------|----------|
| `three_bodies` | planes_of_existence | 5.0 | sixteen_levels | three_planes |
| `three_planes` | plane_definitions | 5.1 | three_bodies | physical_virtual_semantic |
| `flow_between_planes` | plane_relationships | 5.2 | three_planes | encoding_interpretation |
| `converging_to_entity` | unification | 5.3 | flow_between_planes | node_as_fundamental |

### PART VI: The Periodic Table
| Section ID | Topic | Order | Depends On | Provides |
|------------|-------|-------|------------|----------|
| `periodic_table` | atom_organization | 6.0 | converging_to_entity | 200_atoms |
| `the_200_atoms` | atom_inventory | 6.1 | periodic_table | phases_families |
| `why_organization_works` | justification | 6.2 | the_200_atoms | coverage_validation |
| `the_33_roles` | role_taxonomy | 6.3 | why_organization_works | role_categories |

### PART VII: The Octahedral Atom
| Section ID | Topic | Order | Depends On | Provides |
|------------|-------|-------|------------|----------|
| `octahedral_atom` | geometric_model | 7.0 | the_200_atoms | octahedron_shape |
| `why_octahedron` | geometry_justification | 7.1 | octahedral_atom | 8_faces |
| `eight_dimensions` | dimension_definitions | 7.2 | why_octahedron | D1_to_D8 |
| `dual_dimensions` | opposite_faces | 7.3 | eight_dimensions | dualities |
| `dual_nature` | lens_dimension_duality | 7.4 | eight_dimensions | epistemic_ontological |
| `eight_lenses` | lens_definitions | 7.4.1 | dual_nature | R1_to_R8 |
| `lens_dimension_question` | open_question | 7.4.2 | eight_lenses, eight_dimensions | research_direction |

### PART VIII: The Relationships
| Section ID | Topic | Order | Depends On | Provides |
|------------|-------|-------|------------|----------|
| `relationships` | edge_types | 8.0 | octahedral_atom | edge_taxonomy |
| `edge_types` | edge_definitions | 8.1 | relationships | structural_dependency_etc |
| `graph_of_code` | graph_model | 8.2 | edge_types | code_as_graph |

### PART IX: The Validation
| Section ID | Topic | Order | Depends On | Provides |
|------------|-------|-------|------------|----------|
| `validation` | empirical_testing | 9.0 | graph_of_code | validation_approach |
| `empirical_coverage` | coverage_stats | 9.1 | validation | language_coverage |
| `what_validated` | positive_results | 9.2 | empirical_coverage | confirmed_hypotheses |
| `what_not_validated` | limitations | 9.3 | what_validated | open_questions |

### PART X: The Open Frontier
| Section ID | Topic | Order | Depends On | Provides |
|------------|-------|-------|------------|----------|
| `open_frontier` | unknown | 10.0 | what_not_validated | frontier_acknowledgment |
| `what_not_mapped` | gaps | 10.1 | open_frontier | gap_inventory |
| `the_98_percent_problem` | junk_code_hypothesis | 10.2 | what_not_mapped | research_hypothesis |
| `the_invitation` | contribution | 10.3 | the_98_percent_problem | open_contribution |

---

## Dependency Graph

```
humble_beginning
    ├── what_this_is_not
    ├── what_this_is
    └── operating_principles
            └── problem_of_software
                    └── the_question
                            └── power_of_analogies
                                    └── layers_of_abstraction
                                            ├── inheritance_chain
                                            └── sixteen_levels
                                                    └── three_bodies
                                                            └── periodic_table
                                                                    └── octahedral_atom
                                                                            └── relationships
                                                                                    └── validation
                                                                                            └── open_frontier
```

---

## Script Commands (Future)

```bash
# Validate all sections have required markers
./scripts/validate_markers.py docs/theory_v2.md

# Extract sections to individual files
./scripts/extract_sections.py docs/theory_v2.md --output-dir sections/

# Reorder sections by dependencies
./scripts/reorder_by_deps.py docs/theory_v2.md

# Generate summary from markers
./scripts/generate_summary.py docs/theory_v2.md

# Check for circular dependencies
./scripts/check_cycles.py docs/theory_v2.md
```

---

## Version

- **Schema Version:** 1.0.0
- **Created:** 2025-12-26
