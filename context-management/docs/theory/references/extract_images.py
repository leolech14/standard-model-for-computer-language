#!/usr/bin/env python3
"""Extract all images from reference PDFs with structured metadata."""

import pymupdf
import os
import json
from pathlib import Path

REFS_DIR = Path(__file__).parent.absolute()
PDF_DIR = REFS_DIR / "pdf"
IMAGES_DIR = REFS_DIR / "images"

def extract_images_from_pdf(pdf_path: Path, images_base_dir: Path):
    """Extract all images from PDF with metadata."""
    ref_id = pdf_path.stem.split("_")[0]  # e.g., REF-001 or KOESTLER
    image_dir = images_base_dir / ref_id
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
                    "format": ext,
                    "xref": xref
                })
                image_count += 1
            except Exception as e:
                print(f"    WARN: Could not extract image {xref} from page {page_num+1}: {e}")

    doc.close()

    if metadata:
        (image_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
        return image_count, len(metadata)
    return 0, 0

def main():
    # Organize PDFs into pdf/ subfolder
    PDF_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)

    # Move any PDFs in root to pdf/
    moved = 0
    for pdf_file in REFS_DIR.glob("*.pdf"):
        if pdf_file.parent == REFS_DIR:
            pdf_file.rename(PDF_DIR / pdf_file.name)
            moved += 1

    if moved > 0:
        print(f"Organized {moved} PDFs into pdf/")
    print()

    # Extract images from all PDFs
    print(f"Extracting images from PDFs in {PDF_DIR}/")
    print()

    total_images = 0
    total_pdfs = 0

    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        img_count, meta_count = extract_images_from_pdf(pdf_path, IMAGES_DIR)
        if img_count > 0:
            print(f"  {pdf_path.name}: {img_count} images")
            total_images += img_count
            total_pdfs += 1

    print()
    print(f"=== RESULTS ===")
    print(f"PDFs processed: {total_pdfs}")
    print(f"Total images extracted: {total_images}")
    print(f"Image directories: {len(list(IMAGES_DIR.iterdir()))}")

if __name__ == "__main__":
    main()
