#!/usr/bin/env python3
"""Reference library CLI for ./pe refs commands."""

import sys
import json
import subprocess
from pathlib import Path

# Determine project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
REFS_DIR = PROJECT_ROOT / "context-management/docs/theory/references"


def cmd_list(args):
    """List all references."""
    catalog_file = REFS_DIR / "index/catalog.json"
    if not catalog_file.exists():
        print("Error: Catalog not found. Run: python3 references/process_library.py")
        return 1

    catalog = json.loads(catalog_file.read_text())

    print(f"Total references: {catalog['total_refs']}")
    print(f"Total images: {catalog['total_images']:,}")
    print(f"Total tokens: {catalog['total_tokens_estimate']:,}")
    print(f"\nBy author: {len(catalog.get('by_author', {}))}")
    print(f"By year: {len(catalog.get('by_year', {}))}")
    print()

    # Show recent
    print("References (showing first 20):")
    for i, ref in enumerate(catalog['references'][:20], 1):
        authors = ', '.join(ref['authors'][:2])
        if len(ref['authors']) > 2:
            authors += f" et al."
        title = ref['title'][:50] + "..." if len(ref['title']) > 50 else ref['title']
        print(f"  {ref['ref_id']:<20} {authors:<20} ({ref.get('year', '????')}) {title}")

    if len(catalog['references']) > 20:
        print(f"\n  ... and {len(catalog['references']) - 20} more")
    return 0


def cmd_show(ref_id):
    """Show metadata for a reference."""
    meta_file = REFS_DIR / f"metadata/{ref_id}.json"
    if not meta_file.exists():
        print(f"Error: {ref_id} not found in metadata/")
        return 1

    meta = json.loads(meta_file.read_text())
    print(json.dumps(meta, indent=2))
    return 0


def cmd_read(ref_id):
    """Open enhanced TXT in pager."""
    txt_file = REFS_DIR / f"txt/{ref_id}.txt"
    if not txt_file.exists():
        print(f"Error: {ref_id} TXT not found")
        return 1

    subprocess.run(["less", str(txt_file)])
    return 0


def cmd_images(ref_id):
    """List images for a reference."""
    img_dir = REFS_DIR / f"images/{ref_id}"
    if not img_dir.exists():
        print(f"Error: No images for {ref_id}")
        return 1

    meta_file = img_dir / "metadata.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())
        total = meta.get('total_figures', len(meta.get('figures', [])))
        with_captions = sum(1 for f in meta.get('figures', []) if f.get('caption'))

        print(f"Images for {ref_id}: {total} total, {with_captions} with captions")
        print()

        for fig in meta.get('figures', [])[:20]:
            page = fig.get('page')
            caption = fig.get('caption', 'No caption')[:80]
            conf = fig.get('caption_confidence', 0)
            print(f"  Page {page:3d}: {caption}")
            if conf > 0:
                print(f"           (confidence: {conf:.2f})")

        if total > 20:
            print(f"\n  ... and {total - 20} more images")
    else:
        images = list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.jpeg"))
        print(f"Images: {len(images)}")
        for img in images[:10]:
            print(f"  {img.name}")
    return 0


def cmd_search(term):
    """Search references by term."""
    catalog_file = REFS_DIR / "index/catalog.json"
    if not catalog_file.exists():
        print("Error: Catalog not found")
        return 1

    catalog = json.loads(catalog_file.read_text())
    matches = []
    term_lower = term.lower()

    for ref in catalog['references']:
        if (term_lower in ref['title'].lower() or
            term_lower in ' '.join(ref['authors']).lower()):
            matches.append(ref)

    print(f"Found {len(matches)} matches for '{term}':")
    for ref in matches:
        authors = ', '.join(ref['authors'][:2])
        print(f"  {ref['ref_id']}: {authors} ({ref.get('year')}) - {ref['title'][:60]}")

    return 0


def cmd_sync():
    """Sync to cloud storage."""
    sync_script = PROJECT_ROOT / "context-management/tools/sync_refs_cloud.sh"
    if not sync_script.exists():
        print("Error: sync_refs_cloud.sh not found")
        return 1

    subprocess.run(["bash", str(sync_script)])
    return 0


def cmd_monitor():
    """Show processing status."""
    monitor_script = REFS_DIR / "monitor_library.py"
    if not monitor_script.exists():
        print("Error: monitor_library.py not found")
        return 1

    subprocess.run(["python3", str(monitor_script)])
    return 0


def cmd_concept(concept_name):
    """Find references by SMoC concept."""
    concept_index_file = REFS_DIR / "index/concept_index.json"
    if not concept_index_file.exists():
        print("Error: Concept index not found. Create index/concept_index.json first.")
        return 1

    concept_index = json.loads(concept_index_file.read_text())

    matches = concept_index.get(concept_name.lower().replace(" ", "_"), [])

    if matches:
        print(f"References for concept '{concept_name}': {len(matches)}")
        for ref_id in matches:
            print(f"  {ref_id}")
    else:
        print(f"No references found for concept '{concept_name}'")
        print(f"\nAvailable concepts:")
        for concept in sorted(concept_index.keys())[:20]:
            print(f"  {concept}")
        if len(concept_index) > 20:
            print(f"  ... and {len(concept_index) - 20} more")

    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: ./pe refs <command> [args]")
        print("\nCommands:")
        print("  list              - List all references")
        print("  show <REF-ID>     - Show metadata JSON")
        print("  read <REF-ID>     - Read enhanced TXT")
        print("  images <REF-ID>   - List extracted images")
        print("  search <term>     - Search by title/author")
        print("  concept <name>    - Find refs by SMoC concept")
        print("  sync              - Sync to cloud (GCS)")
        print("  monitor           - Show processing status")
        print("\nExamples:")
        print("  ./pe refs show REF-001")
        print("  ./pe refs search \"free energy\"")
        print("  ./pe refs concept holons")
        return 1

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "list": lambda: cmd_list(args),
        "show": lambda: cmd_show(args[0]) if args else print("Error: REF-ID required"),
        "read": lambda: cmd_read(args[0]) if args else print("Error: REF-ID required"),
        "images": lambda: cmd_images(args[0]) if args else print("Error: REF-ID required"),
        "search": lambda: cmd_search(args[0]) if args else print("Error: term required"),
        "concept": lambda: cmd_concept(args[0]) if args else print("Error: concept required"),
        "sync": cmd_sync,
        "monitor": cmd_monitor,
    }

    if cmd in commands:
        return commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print("Run './pe refs' for usage")
        return 1


if __name__ == "__main__":
    sys.exit(main())
