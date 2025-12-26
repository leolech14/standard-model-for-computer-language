#!/bin/bash
# Batch extract summaries from all chat transcript files
# Usage: ./tools/batch_extract.sh [output_dir]

OUTPUT_DIR="${1:-output/chat_summaries}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ELEMENTS_DIR="/Users/lech/PROJECTS_all/PROJECT_elements"

mkdir -p "$OUTPUT_DIR"

echo "Extracting chat summaries to $OUTPUT_DIR..."

# List of known chat transcript files
declare -a FILES=(
    "$ELEMENTS_DIR/0-Code's Unified Theory.md"
    "$ELEMENTS_DIR/0-Defining Code Cosmology.md"
    "$ELEMENTS_DIR/0-EXPANDED-MAP.md"
    "$ELEMENTS_DIR/0-Refining Code Visual Language.md"
)

for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        basename=$(basename "$file" .md)
        safe_name=$(echo "$basename" | tr " '" "_")

        echo "Processing: $basename"

        # Full summary
        python3 "$SCRIPT_DIR/extract_chat_insights.py" "$file" --mode summary -o "$OUTPUT_DIR/${safe_name}_summary.md"

        # JSON stats
        python3 "$SCRIPT_DIR/extract_chat_insights.py" "$file" --mode stats --json > "$OUTPUT_DIR/${safe_name}_stats.json"

        # Decisions
        python3 "$SCRIPT_DIR/extract_chat_insights.py" "$file" --mode decisions -o "$OUTPUT_DIR/${safe_name}_decisions.md"

        echo "  -> Created ${safe_name}_summary.md, _stats.json, _decisions.md"
    else
        echo "Warning: File not found: $file"
    fi
done

# Create combined summary
echo ""
echo "Creating combined summary..."
cat > "$OUTPUT_DIR/COMBINED_SUMMARY.md" << 'HEADER'
# Combined Chat Transcript Summaries

This document contains extracted insights from all project chat transcripts.

---

HEADER

for file in "$OUTPUT_DIR"/*_summary.md; do
    if [[ -f "$file" ]]; then
        echo "" >> "$OUTPUT_DIR/COMBINED_SUMMARY.md"
        cat "$file" >> "$OUTPUT_DIR/COMBINED_SUMMARY.md"
        echo "" >> "$OUTPUT_DIR/COMBINED_SUMMARY.md"
        echo "---" >> "$OUTPUT_DIR/COMBINED_SUMMARY.md"
    fi
done

echo ""
echo "Done! Summaries saved to $OUTPUT_DIR/"
echo "  - Individual summaries: *_summary.md"
echo "  - Stats: *_stats.json"
echo "  - Decisions: *_decisions.md"
echo "  - Combined: COMBINED_SUMMARY.md"
echo "  - Browser: index.html"
echo ""
echo "To view in browser:"
echo "  open $OUTPUT_DIR/index.html"
