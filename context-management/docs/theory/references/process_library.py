#!/usr/bin/env python3
"""
Complete reference library processing pipeline.

Transforms raw PDFs into structured SMoC reference library:
1. Organize PDFs into pdf/ folder
2. Extract images to images/REF-XXX/ with metadata
3. Generate enhanced TXT with SMoC relevance markers
4. Create structured JSON metadata per reference
5. Build master catalog index
"""

import pymupdf
import os
import json
from pathlib import Path
from datetime import datetime

REFS_DIR = Path(__file__).parent.absolute()
PDF_DIR = REFS_DIR / "pdf"
TXT_DIR = REFS_DIR / "txt"
IMAGES_DIR = REFS_DIR / "images"
METADATA_DIR = REFS_DIR / "metadata"
INDEX_DIR = REFS_DIR / "index"

# Create all directories
for d in [PDF_DIR, TXT_DIR, IMAGES_DIR, METADATA_DIR, INDEX_DIR]:
    d.mkdir(exist_ok=True)


def parse_ref_id(filename: str) -> dict:
    """Extract metadata from filename: REF-001_Lawvere_1969_Title.pdf"""
    stem = Path(filename).stem
    parts = stem.split("_")

    ref_id = parts[0] if parts else stem
    author = parts[1] if len(parts) > 1 else "Unknown"
    year = parts[2] if len(parts) > 2 else None
    title = " ".join(parts[3:]) if len(parts) > 3 else stem

    return {
        "ref_id": ref_id,
        "author": author,
        "year": int(year) if year and year.isdigit() else None,
        "title": title.replace("_", " ")
    }


def extract_images(pdf_path: Path) -> tuple[int, Path]:
    """Extract all images from PDF, return count and directory."""
    info = parse_ref_id(pdf_path.name)
    ref_id = info["ref_id"]

    image_dir = IMAGES_DIR / ref_id
    image_dir.mkdir(exist_ok=True)

    doc = pymupdf.open(pdf_path)
    metadata = []
    image_count = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"]
                width, height = base_image["width"], base_image["height"]

                image_name = f"fig_page_{page_num+1:03d}_{img_index:03d}.{ext}"
                image_path = image_dir / image_name
                image_path.write_bytes(image_bytes)

                metadata.append({
                    "image_name": image_name,
                    "page": page_num + 1,
                    "width": width,
                    "height": height,
                    "size_bytes": len(image_bytes),
                    "format": ext
                })
                image_count += 1
            except Exception as e:
                pass  # Skip broken images

    doc.close()

    if metadata:
        (image_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    return image_count, image_dir


def extract_text_enhanced(pdf_path: Path) -> str:
    """Extract text with image markers and structure preservation."""
    info = parse_ref_id(pdf_path.name)
    ref_id = info["ref_id"]

    doc = pymupdf.open(pdf_path)

    lines = []
    lines.append("=" * 80)
    lines.append(f"REFERENCE: {ref_id}")
    lines.append(f"TITLE: {info['title']}")
    lines.append(f"AUTHOR: {info['author']}")
    lines.append(f"YEAR: {info['year']}")
    lines.append(f"PAGES: {len(doc)}")
    lines.append(f"SOURCE: {pdf_path.name}")
    lines.append("=" * 80)
    lines.append("")
    lines.append("[SMoC RELEVANCE SECTION - TO BE GENERATED]")
    lines.append("")
    lines.append("This section will contain:")
    lines.append("- Why this work matters to Standard Model of Code")
    lines.append("- Key SMoC concepts it informs (e.g., holons, free energy, categorical structure)")
    lines.append("- Specific applications to CODOME/CONTEXTOME partition, atoms, layers, scales")
    lines.append("- Critical quotes and page references")
    lines.append("")
    lines.append("[END SMoC RELEVANCE]")
    lines.append("")
    lines.append("=" * 80)
    lines.append("FULL TEXT")
    lines.append("=" * 80)
    lines.append("")

    # Extract text page by page with image markers
    for page_num in range(len(doc)):
        page = doc[page_num]

        # Check for images on this page
        image_list = page.get_images(full=True)
        if image_list:
            lines.append(f"\n--- PAGE {page_num + 1} (contains {len(image_list)} image(s)) ---\n")
            for img_index in range(len(image_list)):
                lines.append(f"[IMAGE: images/{ref_id}/fig_page_{page_num+1:03d}_{img_index:03d}.*]")
            lines.append("")
        else:
            lines.append(f"\n--- PAGE {page_num + 1} ---\n")

        text = page.get_text("text")
        lines.append(text)
        lines.append("")

    doc.close()
    return "\n".join(lines)


def create_metadata_stub(pdf_path: Path, image_count: int) -> dict:
    """Create initial metadata JSON stub (to be enriched by LLM analysis)."""
    info = parse_ref_id(pdf_path.name)
    ref_id = info["ref_id"]

    doc = pymupdf.open(pdf_path)
    page_count = len(doc)
    doc.close()

    return {
        "ref_id": ref_id,
        "title": info["title"],
        "authors": [info["author"]],
        "year": info["year"],
        "source_type": "unknown",  # To be filled by LLM
        "category": "unknown",  # To be filled by LLM
        "original_file": f"pdf/{pdf_path.name}",
        "enhanced_txt": f"txt/{ref_id}.txt",
        "images_dir": f"images/{ref_id}/" if image_count > 0 else None,
        "markdown_file": f"md/{ref_id}.md",
        "page_count": page_count,
        "image_count": image_count,
        "token_count_estimate": None,  # To be calculated
        "summary": "[TO BE GENERATED BY LLM]",
        "smoc_relevance_summary": "[TO BE GENERATED BY LLM]",
        "key_smoc_concepts": [],  # To be filled by LLM
        "important_figures": [],  # To be filled by LLM
        "important_equations": [],  # To be filled by LLM
        "cross_references": [],  # To be filled by LLM
        "gaps_or_extensions": "[TO BE GENERATED BY LLM]",
        "priority_tier": None,  # To be assigned
        "generated_metadata": {
            "date": datetime.now().isoformat()[:10],
            "model": "stub",
            "analyst": "automated_extraction"
        }
    }


def process_single_pdf(pdf_path: Path) -> dict:
    """Process one PDF through full pipeline."""
    info = parse_ref_id(pdf_path.name)
    ref_id = info["ref_id"]

    print(f"\nProcessing {pdf_path.name}...")

    # 1. Extract images
    print(f"  [1/3] Extracting images...")
    image_count, image_dir = extract_images(pdf_path)
    print(f"        {image_count} images → {image_dir.name}/")

    # 2. Generate enhanced TXT
    print(f"  [2/3] Generating enhanced TXT...")
    enhanced_text = extract_text_enhanced(pdf_path)
    txt_path = TXT_DIR / f"{ref_id}.txt"
    txt_path.write_text(enhanced_text, encoding="utf-8")
    chars = len(enhanced_text)
    print(f"        {chars:,} chars → txt/{ref_id}.txt")

    # 3. Create metadata stub
    print(f"  [3/3] Creating metadata stub...")
    metadata = create_metadata_stub(pdf_path, image_count)
    metadata["token_count_estimate"] = chars // 4

    meta_path = METADATA_DIR / f"{ref_id}.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"        metadata/{ ref_id}.json")

    return metadata


def build_catalog(all_metadata: list[dict]) -> dict:
    """Build master searchable catalog."""
    catalog = {
        "generated": datetime.now().isoformat(),
        "total_refs": len(all_metadata),
        "total_images": sum(m.get("image_count", 0) for m in all_metadata),
        "total_tokens_estimate": sum(m.get("token_count_estimate", 0) for m in all_metadata),
        "by_category": {},
        "by_author": {},
        "by_year": {},
        "references": all_metadata
    }

    # Group by category
    for meta in all_metadata:
        cat = meta.get("category", "unknown")
        catalog["by_category"].setdefault(cat, []).append(meta["ref_id"])

    # Group by author (first author)
    for meta in all_metadata:
        auth = meta["authors"][0] if meta.get("authors") else "Unknown"
        catalog["by_author"].setdefault(auth, []).append(meta["ref_id"])

    # Group by year
    for meta in all_metadata:
        year = meta.get("year")
        if year:
            catalog["by_year"].setdefault(str(year), []).append(meta["ref_id"])

    return catalog


def main():
    print("=" * 80)
    print("SMoC REFERENCE LIBRARY PROCESSING PIPELINE")
    print("=" * 80)

    # Organize PDFs
    print("\n[Phase 1] Organizing PDFs into pdf/...")
    moved = 0
    for pdf_file in REFS_DIR.glob("*.pdf"):
        if pdf_file.parent == REFS_DIR:
            pdf_file.rename(PDF_DIR / pdf_file.name)
            moved += 1
    print(f"  Moved {moved} PDFs into pdf/")

    # Process all PDFs
    print("\n[Phase 2] Processing PDFs...")
    all_metadata = []

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    for i, pdf_path in enumerate(pdfs, 1):
        print(f"\n[{i}/{len(pdfs)}]", end=" ")
        meta = process_single_pdf(pdf_path)
        all_metadata.append(meta)

    # Build catalog
    print("\n\n[Phase 3] Building master catalog...")
    catalog = build_catalog(all_metadata)
    catalog_path = INDEX_DIR / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"  Catalog: index/catalog.json")

    # Summary
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"PDFs processed:     {len(all_metadata)}")
    print(f"Total images:       {catalog['total_images']:,}")
    print(f"Total tokens (est): {catalog['total_tokens_estimate']:,}")
    print(f"")
    print("Directory structure:")
    print(f"  pdf/       - {len(list(PDF_DIR.glob('*.pdf')))} PDFs")
    print(f"  txt/       - {len(list(TXT_DIR.glob('*.txt')))} enhanced TXT files")
    print(f"  images/    - {len(list(IMAGES_DIR.iterdir()))} image folders")
    print(f"  metadata/  - {len(list(METADATA_DIR.glob('*.json')))} JSON files (stubs)")
    print(f"  index/     - catalog.json (master index)")
    print("")
    print("Next step: LLM analysis to fill metadata fields")
    print("  - smoc_relevance_summary")
    print("  - key_smoc_concepts[]")
    print("  - important_figures[]")
    print("  - important_equations[]")


if __name__ == "__main__":
    main()
