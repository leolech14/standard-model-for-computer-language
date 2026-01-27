#!/usr/bin/env python3
"""
Extract images WITH captions from PDFs deterministically.

Based on Perplexity research findings:
- Use get_text("dict") for coordinate-based text extraction
- Use get_image_info() for complete image detection
- Match by spatial proximity (captions within ~113 points of image)
- Pattern match for Figure/Fig/FIG variations
- Multi-line caption expansion using font consistency
- Expected accuracy: 70-85%
"""

import pymupdf
import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple

REFS_DIR = Path(__file__).parent.absolute()
PDF_DIR = REFS_DIR / "pdf"
IMAGES_DIR = REFS_DIR / "images"


@dataclass
class ImageBlock:
    """Image with position."""
    xref: int
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    page_num: int
    width: float
    height: float


@dataclass
class TextBlock:
    """Text block with position."""
    bbox: Tuple[float, float, float, float]
    text: str
    block_num: int
    page_num: int


class CaptionDetector:
    """Detect captions using pattern matching."""

    # Comprehensive patterns for caption prefixes
    CAPTION_PATTERNS = [
        re.compile(r'^(?:Fig(?:ure)?s?\.?|FIG\.?)\s*[0-9.]+', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^(?:Panel|Panels?)\s*[A-Z0-9]+', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^(?:Plate|PL\.?)\s*[0-9]+', re.IGNORECASE | re.MULTILINE),
        re.compile(r'^(?:Diagram|Schematic)\s*[0-9]+', re.IGNORECASE | re.MULTILINE),
    ]

    @staticmethod
    def is_caption_header(text: str) -> bool:
        """Check if text starts with a caption prefix."""
        first_line = text.split('\n')[0].strip() if '\n' in text else text.strip()
        return any(pattern.match(first_line) for pattern in CaptionDetector.CAPTION_PATTERNS)

    @staticmethod
    def extract_caption_number(text: str) -> Optional[str]:
        """Extract figure number from caption."""
        match = re.search(r'(?:Fig(?:ure)?s?\.?|FIG\.?)\s*([0-9.]+)', text, re.IGNORECASE)
        return match.group(1) if match else None


def extract_images_with_bbox(doc: pymupdf.Document, page_num: int) -> List[ImageBlock]:
    """Extract all images with bounding boxes using get_image_info()."""
    page = doc[page_num]
    images = []

    # Use get_image_info() for complete detection including inline images
    try:
        image_info_list = page.get_image_info()
    except:
        # Fallback to get_images() if get_image_info() fails
        image_info_list = []
        for img in page.get_images(full=True):
            # Build minimal info
            image_info_list.append({
                'xref': img[0],
                'bbox': (0, 0, 100, 100)  # Unknown bbox
            })

    for img_info in image_info_list:
        bbox = img_info.get('bbox', (0, 0, 100, 100))
        xref = img_info.get('xref', -1)

        img_width = bbox[2] - bbox[0]
        img_height = bbox[3] - bbox[1]

        images.append(ImageBlock(
            xref=xref,
            bbox=bbox,
            page_num=page_num,
            width=img_width,
            height=img_height
        ))

    return images


def extract_text_blocks_with_bbox(doc: pymupdf.Document, page_num: int) -> List[TextBlock]:
    """Extract text blocks with bounding boxes using get_text('dict')."""
    page = doc[page_num]
    text_blocks = []

    try:
        dict_output = page.get_text("dict")
    except:
        return []

    for block_num, block in enumerate(dict_output.get('blocks', [])):
        if block.get('type') == 0:  # Text block (not image)
            # Reconstruct full text from lines/spans
            full_text = ""
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    full_text += span.get('text', '')
                full_text += "\n"

            full_text = full_text.strip()
            if full_text:
                text_blocks.append(TextBlock(
                    bbox=tuple(block['bbox']),
                    text=full_text,
                    block_num=block_num,
                    page_num=page_num
                ))

    return text_blocks


def calculate_spatial_distance(img_bbox: Tuple, text_bbox: Tuple) -> float:
    """Calculate vertical distance between image and text.

    Returns:
        - Negative if text is above image
        - Positive if text is below image
        - 0 if overlapping
    """
    img_x0, img_y0, img_x1, img_y1 = img_bbox
    txt_x0, txt_y0, txt_x1, txt_y1 = text_bbox

    if img_y1 < txt_y0:  # Image above text (caption below)
        return txt_y0 - img_y1
    elif txt_y1 < img_y0:  # Text above image
        return -(img_y0 - txt_y1)
    else:
        return 0


def find_caption_for_image(image: ImageBlock,
                          text_blocks: List[TextBlock],
                          max_distance_points: float = 113) -> Tuple[Optional[str], float]:
    """
    Find caption for an image using spatial proximity + pattern matching.

    Returns: (caption_text, confidence_score)
    """
    candidates = []

    for text_block in text_blocks:
        distance = calculate_spatial_distance(image.bbox, text_block.bbox)

        # Prefer captions below image (positive distance)
        # But also check above for some formats
        if -56 <= distance <= max_distance_points:
            is_caption = CaptionDetector.is_caption_header(text_block.text)

            if is_caption:
                # Calculate confidence
                confidence = 0.7  # Base for pattern match
                if 0 <= distance <= 56:
                    confidence += 0.3  # Perfect proximity
                elif 56 < distance <= 113:
                    confidence += 0.2  # Good proximity

                if 10 <= len(text_block.text) <= 500:
                    confidence += 0.1  # Reasonable length

                candidates.append((text_block.text, min(confidence, 1.0), distance))

    if not candidates:
        return None, 0.0

    # Sort by confidence, then by distance
    candidates.sort(key=lambda x: (-x[1], abs(x[2])))
    return candidates[0][0], candidates[0][1]


def extract_images_and_captions(pdf_path: Path) -> dict:
    """
    Extract all images with their captions from a PDF.

    Returns dict with images, captions, metadata.
    """
    doc = pymupdf.open(pdf_path)
    ref_id = pdf_path.stem.split("_")[0]

    image_dir = IMAGES_DIR / ref_id
    image_dir.mkdir(exist_ok=True)

    all_figures = []
    image_count = 0

    for page_num in range(len(doc)):
        # Extract images and text from this page
        images = extract_images_with_bbox(doc, page_num)
        text_blocks = extract_text_blocks_with_bbox(doc, page_num)

        for img_index, img in enumerate(images):
            # Find caption for this image
            caption, confidence = find_caption_for_image(img, text_blocks)
            caption_number = CaptionDetector.extract_caption_number(caption) if caption else None

            # Extract image data if possible
            image_data = None
            image_name = None
            if img.xref > 0:
                try:
                    base_image = doc.extract_image(img.xref)
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]

                    image_name = f"fig_page_{page_num+1:03d}_{img_index:03d}.{ext}"
                    image_path = image_dir / image_name
                    image_path.write_bytes(image_bytes)

                    image_data = {
                        "width": base_image["width"],
                        "height": base_image["height"],
                        "size_bytes": len(image_bytes),
                        "format": ext
                    }
                except Exception:
                    pass  # Some images can't be extracted

            # Build metadata entry
            figure_meta = {
                "image_name": image_name,
                "page": page_num + 1,
                "bbox": list(img.bbox),
                "caption": caption if caption else "",
                "caption_number": caption_number,
                "caption_confidence": confidence,
                "xref": img.xref
            }

            if image_data:
                figure_meta.update(image_data)

            all_figures.append(figure_meta)
            if image_name:
                image_count += 1

    doc.close()

    # Save metadata
    metadata = {
        "ref_id": ref_id,
        "pdf_file": pdf_path.name,
        "total_figures": len(all_figures),
        "figures_with_images": image_count,
        "figures": all_figures
    }

    (image_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    return metadata


def main():
    """Process all PDFs, extracting images and captions."""
    print("=" * 80)
    print("CAPTION EXTRACTION PIPELINE (Deterministic)")
    print("=" * 80)
    print()

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    total_figures = 0
    total_with_captions = 0
    total_high_confidence = 0

    for i, pdf_path in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] {pdf_path.name}")

        try:
            meta = extract_images_and_captions(pdf_path)
            figs = len(meta["figures"])
            with_captions = sum(1 for f in meta["figures"] if f.get("caption"))
            high_conf = sum(1 for f in meta["figures"] if f.get("caption_confidence", 0) >= 0.7)

            print(f"  Figures: {figs}, Captions: {with_captions}, High-confidence: {high_conf}")

            total_figures += figs
            total_with_captions += with_captions
            total_high_confidence += high_conf

        except Exception as e:
            print(f"  ERROR: {e}")

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"PDFs processed:        {len(pdfs)}")
    print(f"Total figures:         {total_figures:,}")
    print(f"With captions:         {total_with_captions:,} ({100*total_with_captions/max(total_figures,1):.1f}%)")
    print(f"High confidence (>0.7): {total_high_confidence:,} ({100*total_high_confidence/max(total_figures,1):.1f}%)")
    print()
    print("Expected deterministic accuracy: 70-85% (per Sonar research)")


if __name__ == "__main__":
    main()
