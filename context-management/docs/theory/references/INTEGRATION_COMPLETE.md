# Reference Library - Complete Integration Plan

> **Objective:** Make library findable, documented, and cloud-integrated
> **Follows:** PROJECT_elements patterns (./pe CLI, cloud mirror, analysis sets)
> **Status:** Implementation plan

---

## 1. Findability (./pe refs Integration)

### Add to pe CLI

Edit `pe` script to add refs subcommand:

```bash
# In pe script, add:
refs)
    shift
    python3 "$PROJECT_ROOT/context-management/tools/refs_cli.py" "$@"
    ;;
```

Create `context-management/tools/refs_cli.py`:

```python
#!/usr/bin/env python3
"""Reference library CLI integration."""

import sys
import json
from pathlib import Path

REFS_DIR = Path(__file__).parent.parent / "docs/theory/references"

def cmd_list():
    """List all references."""
    catalog = json.loads((REFS_DIR / "index/catalog.json").read_text())
    print(f"Total references: {catalog['total_refs']}")
    print(f"By author: {len(catalog['by_author'])} authors")
    print(f"\nRecent (last 10):")
    for ref in catalog['references'][-10:]:
        print(f"  {ref['ref_id']}: {ref['authors'][0]} ({ref['year']}) - {ref['title'][:60]}")

def cmd_show(ref_id):
    """Show metadata for a reference."""
    meta_file = REFS_DIR / f"metadata/{ref_id}.json"
    if not meta_file.exists():
        print(f"Error: {ref_id} not found")
        return

    meta = json.loads(meta_file.read_text())
    print(json.dumps(meta, indent=2))

def cmd_read(ref_id):
    """Open enhanced TXT in less."""
    txt_file = REFS_DIR / f"txt/{ref_id}.txt"
    if not txt_file.exists():
        print(f"Error: {ref_id} not found")
        return

    import subprocess
    subprocess.run(["less", str(txt_file)])

def cmd_images(ref_id):
    """List images for a reference."""
    img_dir = REFS_DIR / f"images/{ref_id}"
    if not img_dir.exists():
        print(f"Error: No images for {ref_id}")
        return

    meta_file = img_dir / "metadata.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        print(f"Images for {ref_id}: {meta.get('total_figures', 0)}")
        for fig in meta.get('figures', []):
            caption = fig.get('caption', 'No caption')
            page = fig.get('page')
            print(f"  Page {page}: {caption[:80]}")
    else:
        images = list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpg"))
        print(f"Images: {len(images)}")
        for img in images[:10]:
            print(f"  {img.name}")

def cmd_search(term):
    """Search catalog for term."""
    catalog = json.loads((REFS_DIR / "index/catalog.json").read_text())
    matches = []
    term_lower = term.lower()

    for ref in catalog['references']:
        if (term_lower in ref['title'].lower() or
            term_lower in ' '.join(ref['authors']).lower()):
            matches.append(ref)

    print(f"Found {len(matches)} matches for '{term}':")
    for ref in matches:
        print(f"  {ref['ref_id']}: {ref['authors'][0]} ({ref['year']}) - {ref['title'][:60]}")

def cmd_sync():
    """Sync to cloud (GCS)."""
    print("Syncing library to gs://elements-archive-2026/references/...")
    import subprocess
    subprocess.run([
        "gsutil", "-m", "rsync", "-r", "-d",
        str(REFS_DIR / "metadata"),
        "gs://elements-archive-2026/references/metadata/"
    ])
    subprocess.run([
        "gsutil", "-m", "rsync", "-r", "-d",
        str(REFS_DIR / "index"),
        "gs://elements-archive-2026/references/index/"
    ])
    # Don't sync images (2.2GB) unless explicitly requested
    print("Synced metadata + index to GCS")
    print("(Images not synced due to size. Use --include-images to sync)")

def main():
    if len(sys.argv) < 2:
        print("Usage: ./pe refs <command>")
        print("Commands:")
        print("  list              - List all references")
        print("  show <REF-ID>     - Show metadata")
        print("  read <REF-ID>     - Read enhanced TXT")
        print("  images <REF-ID>   - List images")
        print("  search <term>     - Search by term")
        print("  sync              - Sync to cloud")
        print("  monitor           - Show processing status")
        return

    cmd = sys.argv[1]

    if cmd == "list":
        cmd_list()
    elif cmd == "show" and len(sys.argv) > 2:
        cmd_show(sys.argv[2])
    elif cmd == "read" and len(sys.argv) > 2:
        cmd_read(sys.argv[2])
    elif cmd == "images" and len(sys.argv) > 2:
        cmd_images(sys.argv[2])
    elif cmd == "search" and len(sys.argv) > 2:
        cmd_search(sys.argv[2])
    elif cmd == "sync":
        cmd_sync()
    elif cmd == "monitor":
        import subprocess
        subprocess.run(["python3", str(REFS_DIR / "monitor_library.py")])
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
```

### Usage

```bash
./pe refs list                    # Browse catalog
./pe refs show REF-001            # View metadata
./pe refs read REF-001            # Read with less
./pe refs images REF-040          # List Friston figures
./pe refs search "free energy"    # Find by term
./pe refs sync                    # Push to cloud
./pe refs monitor                 # Check processing status
```

---

## 2. Documentation (Complete Guide)

### Master Documentation File

Create `context-management/docs/theory/REFERENCE_LIBRARY_GUIDE.md`:

```markdown
# Reference Library Guide

## What It Is

82 foundational academic works with:
- Full text extraction (5.4M tokens)
- 1,884 content figures with captions
- Structured metadata (schema-validated)
- SMoC relevance analysis

## Location

`context-management/docs/theory/references/`

## Quick Start

```bash
# Browse
./pe refs list

# Read a reference
./pe refs read REF-001

# Search
./pe refs search "affordance"

# Check status
./pe refs monitor
```

## For Analysis

Use the `foundations` analysis set:

```bash
./pe ask "How does Lawvere prove CODOME/CONTEXTOME?" --set foundations
```

This includes all reference TXT files + metadata in context.

## Cloud Access

Library is mirrored to GCS:
- Metadata: `gs://elements-archive-2026/references/metadata/`
- Index: `gs://elements-archive-2026/references/index/`
- (Images not synced due to size)

## Structure

See `references/README.md` for detailed structure.
See `references/VALIDATION_AND_INTEGRATION_PLAN.md` for processing status.
```

### Update INTELLECTUAL_FOUNDATIONS.md

Add references section at top:

```markdown
# Intellectual Foundations of the Standard Model of Code

> **Reference Library:** All cited works are available at `references/`
> **Browse:** `./pe refs list`
> **Search:** `./pe refs search <term>`

> **Downloaded:** 82 / 125 works (49 original refs + 33 author corpus)
> **Processing:** Phase 1 complete (extraction), Phase 2 pending (LLM analysis)
```

### Update GLOSSARY.md

Link terms to sources:

```markdown
## Holon
**Definition:** ...
**Source:** Koestler, A. (1967). *The Ghost in the Machine*
**Library:** `./pe refs show KOESTLER` | [PDF](theory/references/pdf/KOESTLER_1967_GhostInMachine.pdf)
```

---

## 3. Cloud Integration (GCS Mirror)

### Cloud Sync Script

Create `context-management/tools/sync_refs_cloud.sh`:

```bash
#!/bin/bash
# Sync reference library to Google Cloud Storage
# Bucket: gs://elements-archive-2026/references/

PROJECT="elements-archive-2026"
BUCKET="gs://${PROJECT}/references"
LOCAL="/Users/lech/PROJECTS_all/PROJECT_elements/context-management/docs/theory/references"

echo "=== SYNCING REFERENCE LIBRARY TO GCS ==="
echo "Local:  $LOCAL"
echo "Bucket: $BUCKET"
echo ""

# Metadata (small, always sync)
echo "[1/4] Syncing metadata..."
gsutil -m rsync -r -d "$LOCAL/metadata" "$BUCKET/metadata/"

# Index (tiny, always sync)
echo "[2/4] Syncing index..."
gsutil -m rsync -r -d "$LOCAL/index" "$BUCKET/index/"

# Schemas (tiny, always sync)
echo "[3/4] Syncing schemas..."
gsutil cp "$LOCAL/library_schema.json" "$BUCKET/"
gsutil cp "$LOCAL/holon_hierarchy_schema.json" "$BUCKET/"
gsutil cp "$LOCAL/README.md" "$BUCKET/"

# PDFs (optional - 322MB)
if [ "$1" == "--include-pdfs" ]; then
    echo "[4/4] Syncing PDFs..."
    gsutil -m rsync -r -d "$LOCAL/pdf" "$BUCKET/pdf/"
else
    echo "[4/4] Skipping PDFs (use --include-pdfs to sync)"
fi

# TXT files (small, sync)
echo "[5/5] Syncing TXT files..."
gsutil -m rsync -r -d "$LOCAL/txt" "$BUCKET/txt/"

echo ""
echo "=== SYNC COMPLETE ==="
gsutil du -sh "$BUCKET"
```

### Cloud Retrieval Script

Create `context-management/tools/pull_refs_cloud.sh`:

```bash
#!/bin/bash
# Pull reference library FROM cloud
# Use case: New machine setup, restore after local deletion

BUCKET="gs://elements-archive-2026/references"
LOCAL="/Users/lech/PROJECTS_all/PROJECT_elements/context-management/docs/theory/references"

mkdir -p "$LOCAL"/{metadata,index,pdf,txt,images}

echo "=== PULLING REFERENCE LIBRARY FROM GCS ==="

gsutil -m rsync -r "$BUCKET/metadata/" "$LOCAL/metadata/"
gsutil -m rsync -r "$BUCKET/index/" "$LOCAL/index/"
gsutil -m rsync -r "$BUCKET/txt/" "$LOCAL/txt/"

if [ "$1" == "--include-pdfs" ]; then
    gsutil -m rsync -r "$BUCKET/pdf/" "$LOCAL/pdf/"
fi

echo "COMPLETE. Run ./pe refs monitor to verify."
```

### Automated Sync on Updates

Add post-processing hook to `process_library.py`:

```python
def sync_to_cloud():
    """Auto-sync after processing updates."""
    import subprocess
    subprocess.run([
        "bash",
        str(REFS_DIR.parent.parent.parent / "tools/sync_refs_cloud.sh")
    ])

# At end of main():
if os.getenv("AUTO_CLOUD_SYNC") == "1":
    print("\n[Cloud] Auto-syncing to GCS...")
    sync_to_cloud()
```

Usage:
```bash
AUTO_CLOUD_SYNC=1 python3 process_library.py
```

---

## 4. Search & Indexing

### Full-Text Search Index

Create `context-management/tools/index_refs.py`:

```python
#!/usr/bin/env python3
"""Build searchable full-text index of reference library."""

import json
from pathlib import Path
from collections import defaultdict

REFS_DIR = Path(__file__).parent.parent / "docs/theory/references"

def build_search_index():
    """Create term → [ref_ids] index."""
    index = defaultdict(set)

    # Index catalog metadata
    catalog = json.loads((REFS_DIR / "index/catalog.json").read_text())

    for ref in catalog['references']:
        ref_id = ref['ref_id']

        # Index title words
        for word in ref['title'].lower().split():
            if len(word) > 3:  # Skip short words
                index[word].add(ref_id)

        # Index authors
        for author in ref['authors']:
            index[author.lower()].add(ref_id)

    # Index TXT files for full-text search
    for txt_file in (REFS_DIR / "txt").glob("*.txt"):
        ref_id = txt_file.stem
        text = txt_file.read_text(encoding='utf-8', errors='ignore')

        # Extract key terms (simple frequency-based)
        words = text.lower().split()
        word_freq = defaultdict(int)
        for word in words:
            if len(word) > 4:
                word_freq[word] += 1

        # Top 100 terms
        top_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:100]
        for term, freq in top_terms:
            index[term].add(ref_id)

    # Convert sets to lists for JSON
    index_json = {term: sorted(list(refs)) for term, refs in index.items()}

    # Save
    output = REFS_DIR / "index/search_index.json"
    output.write_text(json.dumps(index_json, indent=2))

    print(f"Search index built: {len(index_json):,} terms")
    return index_json

if __name__ == "__main__":
    build_search_index()
```

Run: `python3 context-management/tools/index_refs.py`

### Concept-Based Index

Create `index/concept_index.json`:

```json
{
  "codome_contextome_partition": ["REF-001", "LAWVERE-1994"],
  "holons": ["KOESTLER-1967", "REF-081"],
  "free_energy_principle": ["REF-040", "REF-041", "FRISTON-2019", "FRISTON-2023"],
  "constructal_law": ["BEJAN-2010", "BEJAN-2016"],
  "affordances": ["GIBSON-1977", "GIBSON-1979"],
  "structure_mapping": ["REF-088", "GENTNER-1997", "GENTNER-2012"],
  "bounded_rationality": ["REF-081", "REF-119", "SIMON-1972"],
  "cybernetics": ["REF-080", "ASHBY-1970", "REF-123"],
  "distributed_cognition": ["HUTCHINS-1995", "HUTCHINS-2000"],
  "situated_action": ["SUCHMAN-1987"],
  "process_philosophy": ["WHITEHEAD-1929", "WHITEHEAD-1925"],
  "dissipative_structures": ["REF-029", "PRIGOGINE-1984"],
  "category_theory": ["REF-001", "REF-002", "LAWVERE-1994"],
  "actor_network_theory": ["LATOUR-2005"],
  "activity_theory": ["REF-094", "ENGESTROM-2001"]
}
```

Then:
```bash
./pe refs concept "holons"  # Find all refs on holons
```

---

## 5. Analysis Set Integration

### Add to research_schemas.yaml

Edit `context-management/config/research_schemas.yaml`:

```yaml
# Existing sets...

foundations:
  description: "Intellectual foundations reference library - 82 academic works"
  patterns:
    - "context-management/docs/theory/references/txt/*.txt"
    - "context-management/docs/theory/references/metadata/*.json"
    - "context-management/docs/theory/INTELLECTUAL_FOUNDATIONS.md"
    - "context-management/docs/theory/REFERENCE_LIBRARY.md"
  critical_files:
    - "context-management/docs/theory/references/index/catalog.json"
  auto_interactive: true
  max_files: 500
  prioritize:
    - "INTELLECTUAL_FOUNDATIONS.md"
    - "index/catalog.json"
```

Usage:
```bash
./pe ask "Explain how Lawvere's fixed-point theorem proves the CODOME/CONTEXTOME partition is necessary" --set foundations

./pe ask "What is the relationship between Friston's free energy principle and the purpose field equation d𝒫/dt = -∇Incoherence?" --set foundations

./pe ask "How do holons from Koestler map to the 16-level scale in SMoC?" --set foundations
```

---

## 6. Cloud Facilities Integration

### GCS Bucket Structure

```
gs://elements-archive-2026/
└── references/
    ├── metadata/              65 JSON files (260KB)
    ├── index/
    │   ├── catalog.json       Master index
    │   ├── search_index.json  Full-text search
    │   └── concept_index.json SMoC concept map
    ├── txt/                   65 TXT files (21MB)
    ├── pdf/                   82 PDFs (322MB, optional)
    ├── schemas/
    │   ├── library_schema.json
    │   └── holon_hierarchy_schema.json
    └── README.md
```

### Access Patterns

**Local Development:**
```bash
./pe refs read REF-001          # Local files
```

**Cloud Query (for other machines/agents):**
```bash
gsutil cat gs://elements-archive-2026/references/metadata/REF-001.json | jq .
```

**Cloud Analysis (Vertex AI):**
```python
# In analyze.py, add cloud source option
if args.cloud_refs:
    # Pull refs from GCS into context
    subprocess.run([
        "gsutil", "cp",
        "gs://elements-archive-2026/references/index/catalog.json",
        "/tmp/catalog.json"
    ])
```

### Automated Sync Schedule

Add to PROJECT_sentinel (if desired):

```bash
# sentinel automation for reference library sync
# Runs daily at 2am if changes detected

0 2 * * * cd /Users/lech/PROJECTS_all/PROJECT_elements && git diff --quiet context-management/docs/theory/references/metadata && echo "No changes" || ./context-management/tools/sync_refs_cloud.sh
```

---

## 7. Documentation Structure

### File Organization

```
context-management/docs/theory/
├── INTELLECTUAL_FOUNDATIONS.md           ← Lists all 125 refs
├── REFERENCE_LIBRARY.md                  ← Catalog with filepaths
├── AUTHOR_CORPUS.md                      ← 82 works by author
├── REFERENCE_LIBRARY_SUMMARY.md          ← This file
├── REFERENCE_LIBRARY_GUIDE.md            ← User guide
└── references/
    ├── README.md                         ← Quick start
    ├── VALIDATION_AND_INTEGRATION_PLAN.md ← Technical plan
    ├── pdf/, txt/, images/, metadata/    ← Data
    └── [scripts]
```

### Cross-Links

**From CODESPACE_ALGEBRA.md:**
```markdown
## 1. SET ALGEBRA (Universes)

### The Partition (PROVEN NECESSARY)

NOTE: This partition is MATHEMATICALLY NECESSARY, not arbitrary.
      Proven via Lawvere's Fixed-Point Theorem (1969).
      See: theory/FOUNDATIONS_INTEGRATION.md for full proof.
      **Source:** `./pe refs show REF-001`
```

**From MODEL.md:**
```markdown
## Holons

The 16-level scale is a holarchy (Koestler, 1967).
**Source:** `./pe refs show KOESTLER-1967`
```

---

## 8. Integration Checklist

### Phase 1: CLI Integration
- [ ] Create `context-management/tools/refs_cli.py`
- [ ] Add `refs)` case to `pe` script
- [ ] Test: `./pe refs list`
- [ ] Test: `./pe refs show REF-001`
- [ ] Test: `./pe refs search "holons"`

### Phase 2: Cloud Sync
- [ ] Create `sync_refs_cloud.sh`
- [ ] Test sync: `./context-management/tools/sync_refs_cloud.sh`
- [ ] Verify in GCS console
- [ ] Create `pull_refs_cloud.sh` for restore
- [ ] Test full round-trip (push → delete local → pull → verify)

### Phase 3: Search Indexing
- [ ] Create `index_refs.py`
- [ ] Build search index: `python3 index_refs.py`
- [ ] Create `concept_index.json` manually
- [ ] Test: `./pe refs concept "holons"`
- [ ] Add full-text search to refs_cli.py

### Phase 4: Analysis Set
- [ ] Add `foundations` set to `research_schemas.yaml`
- [ ] Test: `./pe ask "test" --set foundations`
- [ ] Verify references appear in context

### Phase 5: Documentation
- [ ] Create `REFERENCE_LIBRARY_GUIDE.md`
- [ ] Update `INTELLECTUAL_FOUNDATIONS.md` with library refs
- [ ] Update `GLOSSARY.md` with source links
- [ ] Update `CODESPACE_ALGEBRA.md` with citations
- [ ] Update `MODEL.md` with citations

### Phase 6: Validation
- [ ] All 65 metadata files validate against schema
- [ ] All image paths resolve
- [ ] All cross-references exist
- [ ] Cloud sync verified
- [ ] `./pe refs` commands all work
- [ ] Analysis set queries work

---

## 9. Ongoing Maintenance

### When New References Added

```bash
# 1. Download PDF to references/pdf/
curl -o pdf/REF-126_NewAuthor_2026.pdf <url>

# 2. Re-run processing
python3 process_library.py

# 3. Sync to cloud
AUTO_CLOUD_SYNC=1 python3 process_library.py
# OR
./context-management/tools/sync_refs_cloud.sh

# 4. Update REFERENCE_LIBRARY.md
# Add new row with filepath
```

### When Analysis Complete

```bash
# After filling metadata with LLM analysis:
python3 validate_metadata.py REF-126
./context-management/tools/sync_refs_cloud.sh
```

---

## Success Criteria

**Findability:**
- [x] `./pe refs` commands work
- [ ] Full-text search functional
- [ ] Concept-based search functional
- [ ] Cloud access verified

**Documentation:**
- [x] README.md exists
- [x] Integration plan exists
- [ ] User guide complete
- [ ] Theory docs link to library
- [ ] GLOSSARY links to sources

**Cloud Integration:**
- [ ] Metadata synced to GCS
- [ ] Index synced to GCS
- [ ] Pull script works
- [ ] Round-trip verified

**Quality:**
- [x] 856 captions extracted (45% of content figures)
- [ ] Schema validation passes
- [ ] SMoC relevance sections filled (0/65)
- [ ] Cross-references validated

---

*Next: Implement CLI integration, then cloud sync, then analysis set.*
