#!/usr/bin/env python3
"""Convert downloaded reference PDFs to markdown for LLM processing."""

import os
import sys
import pymupdf

REFS_DIR = os.path.dirname(os.path.abspath(__file__))
MD_DIR = os.path.join(REFS_DIR, "md")

def pdf_to_markdown(pdf_path: str) -> str:
    """Extract text from PDF and format as markdown."""
    doc = pymupdf.open(pdf_path)

    basename = os.path.basename(pdf_path).replace(".pdf", "")
    # Parse REF-NNN_Author_Year_Title from filename
    parts = basename.split("_", 3)
    ref_id = parts[0] if parts else basename
    author = parts[1] if len(parts) > 1 else "Unknown"
    year = parts[2] if len(parts) > 2 else "Unknown"
    title = parts[3].replace("_", " ") if len(parts) > 3 else basename

    lines = []
    lines.append(f"# {title}")
    lines.append(f"")
    lines.append(f"> **Reference:** {ref_id}")
    lines.append(f"> **Author:** {author}")
    lines.append(f"> **Year:** {year}")
    lines.append(f"> **Pages:** {len(doc)}")
    lines.append(f"> **Source:** `{os.path.basename(pdf_path)}`")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    for page_num, page in enumerate(doc):
        # Get text with better layout preservation
        text = page.get_text("text")

        if not text.strip():
            continue

        # Clean up common PDF artifacts
        cleaned = []
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                cleaned.append("")
                continue
            # Skip page numbers (standalone digits)
            if line.isdigit() and len(line) <= 4:
                continue
            cleaned.append(line)

        page_text = "\n".join(cleaned)

        # Add page marker
        if len(doc) > 1:
            lines.append(f"<!-- Page {page_num + 1} -->")
            lines.append("")

        lines.append(page_text)
        lines.append("")

    doc.close()
    return "\n".join(lines)


def main():
    os.makedirs(MD_DIR, exist_ok=True)

    pdfs = sorted([f for f in os.listdir(REFS_DIR) if f.endswith(".pdf")])

    if not pdfs:
        print("No PDFs found.")
        return

    print(f"Converting {len(pdfs)} PDFs to markdown...")
    print(f"Output: {MD_DIR}/")
    print()

    converted = 0
    failed = 0
    total_tokens_est = 0

    for pdf_file in pdfs:
        pdf_path = os.path.join(REFS_DIR, pdf_file)
        md_file = pdf_file.replace(".pdf", ".md")
        md_path = os.path.join(MD_DIR, md_file)

        try:
            md_content = pdf_to_markdown(pdf_path)

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            chars = len(md_content)
            tokens_est = chars // 4  # rough estimate
            total_tokens_est += tokens_est

            print(f"  OK  {pdf_file}")
            print(f"      -> {md_file} ({chars:,} chars, ~{tokens_est:,} tokens)")
            converted += 1

        except Exception as e:
            print(f"  FAIL {pdf_file}: {e}")
            failed += 1

    print()
    print(f"=== RESULTS ===")
    print(f"Converted: {converted}")
    print(f"Failed:    {failed}")
    print(f"Total estimated tokens: {total_tokens_est:,}")
    print(f"Average per document:   {total_tokens_est // max(converted, 1):,}")


if __name__ == "__main__":
    main()
