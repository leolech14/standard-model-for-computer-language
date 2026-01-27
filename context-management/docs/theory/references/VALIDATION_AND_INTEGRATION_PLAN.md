# Reference Library - Validation & Integration Plan

> **Created:** 2026-01-27
> **Purpose:** Systematic validation, LLM analysis, and seamless integration into PROJECT_elements
> **Status:** Phase 1 (Extraction) COMPLETE, Phase 2 (Analysis) PENDING

---

## Current State

```
references/
├── pdf/              82 source PDFs (322 MB)
├── txt/              82 enhanced TXT with image markers (~26 MB)
├── images/           64+ folders, 12,070+ extracted figures
├── metadata/         63+ JSON stubs (awaiting LLM enrichment)
├── index/            catalog.json (master index)
├── md/               82 basic markdown (legacy)
├── library_schema.json          (metadata schema)
├── holon_hierarchy_schema.json  (holon-specific schema)
├── process_library.py           (extraction pipeline)
└── analyze_ref.py               (LLM analysis generator)
```

---

## Phase 1: Extraction (COMPLETE)

✅ PDFs organized into `pdf/`
✅ Images extracted with metadata (`images/REF-XXX/metadata.json`)
✅ Enhanced TXT generated with placeholders for SMoC relevance
✅ Metadata stubs created (`metadata/REF-XXX.json`)
✅ Master catalog built (`index/catalog.json`)

**Validation:**
- [x] All 82 PDFs have corresponding TXT file
- [x] Image counts match metadata.json entries
- [x] No corrupted PDFs (all converted successfully)
- [x] Filenames follow naming convention

---

## Phase 2: LLM Analysis (NEXT)

### Priority Tier 1 (Essential - Analyze First)

| Ref ID | Author | Title | Why Priority 1 |
|--------|--------|-------|----------------|
| REF-001 | Lawvere | Diagonal Arguments | Proves CODOME/CONTEXTOME partition |
| REF-002 | Kan | Adjoint Functors | Analysis ⊣ Synthesis duality |
| REF-040 | Friston | Free Energy Principle | d𝒫/dt = -∇Incoherence source |
| KOESTLER-1967 | Koestler | Ghost in the Machine | Holons, 16-level hierarchy |
| REF-081 | Simon | Architecture of Complexity | Near-decomposability |
| REF-080 | Ashby | Introduction to Cybernetics | Requisite variety |
| ASHBY-1970 | Ashby | Good Regulator Theorem | Observation principle |
| REF-025 | Shannon | Mathematical Theory of Communication | Information theory foundation |
| REF-088 | Gentner | Structure-Mapping | Analogy engine |
| GIBSON-1979 | Gibson | Ecological Approach | Affordances |

### Workflow Per Reference

```bash
# For each priority reference:
cd /Users/lech/PROJECTS_all/PROJECT_elements/context-management/docs/theory/references

# 1. Generate analysis prompt
python3 analyze_ref.py REF-001

# 2. Feed to Gemini 2.5 Pro (2M context window fits most papers)
./pe ask --file metadata/REF-001_analysis_prompt.txt --model gemini-3-pro-preview --output metadata/REF-001_analysis.json

# 3. Merge analysis into metadata stub
python3 merge_analysis.py REF-001 metadata/REF-001_analysis.json

# 4. Insert SMoC relevance into TXT file
python3 inject_relevance.py REF-001

# 5. Validate schema compliance
python3 validate_metadata.py REF-001
```

### Automation

Create `batch_analyze.sh`:

```bash
#!/bin/bash
PRIORITY_1="REF-001 REF-002 REF-040 KOESTLER-1967 REF-081 REF-080 ASHBY-1970 REF-025 REF-088 GIBSON-1979"

for ref_id in $PRIORITY_1; do
    echo "=== Analyzing $ref_id ==="
    python3 analyze_ref.py "$ref_id"
    ./pe ask --file "metadata/${ref_id}_analysis_prompt.txt" \
             --model gemini-3-pro-preview \
             --output "metadata/${ref_id}_analysis.json"
    python3 merge_analysis.py "$ref_id" "metadata/${ref_id}_analysis.json"
    python3 inject_relevance.py "$ref_id"
    python3 validate_metadata.py "$ref_id"
    echo ""
done
```

---

## Phase 3: Holon Hierarchy Extraction

### Target References for Holon Extraction

| Ref ID | Author | Hierarchy Type |
|--------|--------|----------------|
| KOESTLER-1967 | Koestler | Original holon theory (bio, social, neural) |
| REF-081 | Simon | Near-decomposable systems hierarchy |
| ASHBY-1956 | Ashby | Regulatory levels |
| FRISTON-2019 | Friston | Nested free energy minimization |
| REF-094 | Engeström | Activity systems levels |
| HUTCHINS-1995 | Hutchins | Distributed cognition scales |

### Workflow

```bash
python3 extract_holons.py KOESTLER-1967 --output metadata/HOL-KOESTLER-1967.json
```

This generates a JSON file following `holon_hierarchy_schema.json`.

---

## Phase 4: Integration with PROJECT_elements

### 4.1 Link to Theory Docs

Update existing theory docs to reference the library:

- `INTELLECTUAL_FOUNDATIONS.md` → Add "See: references/REF-XXX" for each citation
- `CODESPACE_ALGEBRA.md` → Link Lawvere proof to REF-001
- `MODEL.md` → Link holons to KOESTLER-1967

### 4.2 pe CLI Integration

Add commands to `./pe`:

```bash
./pe refs list                    # Show catalog
./pe refs show REF-001            # Display metadata
./pe refs read REF-001            # Open enhanced TXT
./pe refs images REF-001          # List extracted figures
./pe refs search "free energy"    # Full-text search
./pe refs analyze REF-042         # Trigger LLM analysis
./pe refs validate                # Validate all metadata schemas
```

### 4.3 Analysis Set Integration

Create new analysis set in `config/research_schemas.yaml`:

```yaml
foundations:
  description: "Intellectual foundations reference library"
  patterns:
    - "context-management/docs/theory/references/txt/*.txt"
    - "context-management/docs/theory/references/metadata/*.json"
  critical_files:
    - "context-management/docs/theory/INTELLECTUAL_FOUNDATIONS.md"
    - "context-management/docs/theory/REFERENCE_LIBRARY.md"
  auto_interactive: true
```

Then:

```bash
./pe ask "How does Lawvere's fixed-point theorem inform the CODOME/CONTEXTOME partition?" --set foundations
```

---

## Phase 5: Validation

### 5.1 Schema Validation

Create `validate_metadata.py`:

```python
import json
import jsonschema

def validate_ref(ref_id):
    schema = json.loads(Path("library_schema.json").read_text())
    metadata = json.loads(Path(f"metadata/{ref_id}.json").read_text())
    jsonschema.validate(instance=metadata, schema=schema)
    print(f"✓ {ref_id} valid")
```

### 5.2 Content Validation

- [ ] All TXT files have SMoC relevance sections filled
- [ ] All metadata.json have non-stub values
- [ ] All images referenced in metadata exist on filesystem
- [ ] catalog.json totals match actual file counts
- [ ] Cross-references resolve (REF-IDs exist)

### 5.3 Holon Validation

- [ ] All holon hierarchies validate against `holon_hierarchy_schema.json`
- [ ] Recursive nesting doesn't exceed reasonable depth
- [ ] holon_ids are unique within each hierarchy
- [ ] Boundary mechanisms are specified

---

## Phase 6: Background Job Monitoring

### Automation Layer (Thin)

Create `monitor_analysis.py`:

```python
"""
Thin automation layer to monitor background LLM analysis jobs.
Displays progress without full orchestration complexity.
"""

import json
from pathlib import Path
import subprocess
import time

METADATA_DIR = Path("metadata")

def get_pending_analyses():
    """Find refs with stub metadata (not yet analyzed)."""
    pending = []
    for meta_file in METADATA_DIR.glob("*.json"):
        if "_analysis_prompt" in meta_file.name or "_analysis" in meta_file.name:
            continue
        meta = json.loads(meta_file.read_text())
        if meta.get("summary") == "[TO BE GENERATED BY LLM]":
            pending.append(meta["ref_id"])
    return pending

def display_progress():
    """Show analysis completion status."""
    total = len(list(METADATA_DIR.glob("*.json")))
    pending = get_pending_analyses()
    done = total - len(pending)

    print(f"Analysis Progress: {done}/{total} complete")
    if pending:
        print(f"Pending: {', '.join(pending[:10])}")
        if len(pending) > 10:
            print(f"  ... and {len(pending) - 10} more")

def submit_analysis_job(ref_id):
    """Submit one analysis to Gemini in background."""
    subprocess.Popen([
        "./pe", "ask",
        "--file", f"metadata/{ref_id}_analysis_prompt.txt",
        "--model", "gemini-3-pro-preview",
        "--output", f"metadata/{ref_id}_analysis.json"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"  Submitted: {ref_id}")

# Run as monitor
if __name__ == "__main__":
    while True:
        display_progress()
        time.sleep(10)
```

Run periodically:
```bash
watch -n 10 python3 monitor_analysis.py
```

---

## Phase 7: Documentation & Findability

### 7.1 README for Library

Create `references/README.md`:

```markdown
# SMoC Reference Library

82 academic works forming the intellectual foundation of the Standard Model of Code.

## Quick Start

```bash
# View catalog
cat index/catalog.json | jq .

# Read a reference (with SMoC relevance)
cat txt/REF-001.txt

# View metadata
cat metadata/REF-001.json | jq .

# See extracted figures
ls images/REF-001/
```

## Directory Structure

- `pdf/` - Original PDFs
- `txt/` - Enhanced text with SMoC relevance sections
- `images/` - Extracted figures with metadata
- `metadata/` - Structured JSON per reference
- `index/` - Master catalog

## Analysis Status

Run `python3 monitor_analysis.py` to see completion progress.
```

### 7.2 Integration with GLOSSARY

Cross-link terms:

```markdown
# GLOSSARY.md

## Holon
**Definition:** Entity that is simultaneously a whole and a part of a larger whole.
**Source:** Arthur Koestler (1967)
**Reference:** See `references/KOESTLER_1967_GhostInMachine.pdf`
**SMoC Application:** 16-level scale hierarchy
**Metadata:** `references/metadata/KOESTLER.json`
```

### 7.3 Search Index

Create `search_index.json`:

```json
{
  "terms": {
    "holon": ["KOESTLER-1967", "REF-081"],
    "free_energy": ["REF-040", "FRISTON-2019", "FRISTON-2023"],
    "affordance": ["GIBSON-1977", "GIBSON-1979"],
    "categorical": ["REF-001", "REF-002", "LAWVERE-1994"]
  }
}
```

---

## Implementation Checklist

### Phase 1: Extraction ✅
- [x] Extract images with metadata
- [x] Generate enhanced TXT with markers
- [x] Create metadata stubs
- [x] Build catalog

### Phase 2: Analysis (IN PROGRESS)
- [ ] Generate analysis prompts for all refs
- [ ] Run LLM analysis (Tier 1: 10 refs)
- [ ] Merge analysis JSON into metadata
- [ ] Inject relevance sections into TXT files
- [ ] Validate metadata schema compliance

### Phase 3: Holons
- [ ] Extract holon hierarchies from key refs
- [ ] Validate against holon schema
- [ ] Cross-link holon instances

### Phase 4: Integration
- [ ] Add `./pe refs` commands
- [ ] Create `foundations` analysis set
- [ ] Link from theory docs
- [ ] Update GLOSSARY cross-refs

### Phase 5: Monitoring
- [ ] Deploy monitor_analysis.py
- [ ] Set up background job display
- [ ] Completion notifications

### Phase 6: Documentation
- [ ] Write references/README.md
- [ ] Create search index
- [ ] Document analysis workflow

---

## Next Actions (Priority Order)

1. **Complete processing** (finish SUCHMAN, WHITEHEAD, build catalog) ← IN PROGRESS
2. **Analyze Tier 1 refs** (10 most critical refs) ← NEXT
3. **Validate metadata** (schema compliance check)
4. **Integrate with ./pe** (add refs subcommands)
5. **Extract holons** (from Koestler, Simon, Ashby, Friston)
6. **Deploy monitoring** (thin automation layer)
7. **Document system** (README + workflow guide)

---

## Files to Create

| File | Purpose | Status |
|------|---------|--------|
| `merge_analysis.py` | Merge LLM output into metadata | TODO |
| `inject_relevance.py` | Insert SMoC sections into TXT | TODO |
| `validate_metadata.py` | Schema validator | TODO |
| `extract_holons.py` | Generate holon hierarchy JSON | TODO |
| `monitor_analysis.py` | Background job monitor | TODO |
| `batch_analyze.sh` | Automate Tier 1 analysis | TODO |
| `README.md` | Library documentation | TODO |
| `search_index.json` | Term-based search | TODO |

---

## Success Criteria

**Validation:**
- All 82 metadata files pass schema validation
- All image paths resolve
- All cross-references exist
- TXT files have filled SMoC relevance sections

**Integration:**
- `./pe refs` commands work
- Analysis set `foundations` queries library
- Theory docs link to specific references
- GLOSSARY terms link to sources

**Findability:**
- catalog.json enables browsing by category/author/year
- Search index enables term-based lookup
- README provides clear entry point
- Monitor shows completion status

**Quality:**
- SMoC relevance sections are specific, not generic
- Concept mappings cite exact pages/quotes
- Holon hierarchies are complete and accurate
- Figures are described with SMoC context

---

*This is a systematic, validated approach following PROJECT_elements principles: structured schemas, explicit validation, seamless integration, findable documentation.*
