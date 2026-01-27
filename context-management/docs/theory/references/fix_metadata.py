#!/usr/bin/env python3
"""Fix metadata stubs with correct values from REFERENCE_LIBRARY.md."""

import json
from pathlib import Path

REFS_DIR = Path(__file__).parent.absolute()
METADATA_DIR = REFS_DIR / "metadata"
LIBRARY_MD = REFS_DIR.parent / "REFERENCE_LIBRARY.md"

# Parse REFERENCE_LIBRARY.md to get correct values
ref_data = {}

with open(LIBRARY_MD) as f:
    for line in f:
        if line.startswith("| REF-") or ("|" in line and "199" in line or "200" in line or "198" in line):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 7 and parts[1].startswith("REF-"):
                ref_id = parts[1]
                authors = parts[2]
                year = parts[3]
                title = parts[4]
                src_type = parts[5]  # paper or book
                category = parts[6]

                ref_data[ref_id] = {
                    "authors": [authors],
                    "year": int(year) if year.isdigit() else None,
                    "title": title,
                    "source_type": src_type,
                    "category": category
                }

# Fix all metadata files
for meta_file in METADATA_DIR.glob("*.json"):
    if "_analysis" in meta_file.name:
        continue

    meta = json.loads(meta_file.read_text())
    ref_id = meta["ref_id"]

    # Update with correct values if available
    if ref_id in ref_data:
        meta.update(ref_data[ref_id])

    # Fix author-named files (KOESTLER, FRISTON, etc.)
    if not ref_id.startswith("REF-"):
        # Infer from filename
        pdf_files = list(Path(REFS_DIR / "pdf").glob(f"{ref_id}*.pdf"))
        if pdf_files:
            pdf_name = pdf_files[0].stem
            parts = pdf_name.split("_")
            if len(parts) >= 3:
                author = parts[0]
                year_str = parts[1]
                meta["authors"] = [author]
                meta["year"] = int(year_str) if year_str.isdigit() else None

        # Infer type from page count
        if meta.get("page_count", 0) > 100:
            meta["source_type"] = "book"
        else:
            meta["source_type"] = "paper"

        # Default category
        if meta.get("category") == "unknown":
            meta["category"] = "V.1 General Systems"  # Default for foundational works

    # Save
    meta_file.write_text(json.dumps(meta, indent=2))
    print(f"Fixed {ref_id}")

print(f"\nFixed {len(list(METADATA_DIR.glob('*.json')))} metadata files")
