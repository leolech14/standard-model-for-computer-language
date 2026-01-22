# Atom Research Tooling Makefile
# Usage: make <target>

PYTHON ?= python3
PATTERNS_DIR ?= ../../src/patterns
ANALYSIS_FILE ?= ../../.collider/unified_analysis.json
ARTIFACTS_DIR ?= ../../artifacts/atom-research

.PHONY: all inventory coverage quality check self-analysis help

help:
	@echo "Atom Research Tooling"
	@echo ""
	@echo "Targets:"
	@echo "  inventory      Run atom inventory analysis"
	@echo "  coverage       Run coverage analysis on latest Collider output"
	@echo "  quality        Run quality checks (duplicates, overlaps)"
	@echo "  check          Run CI checks (fails on issues)"
	@echo "  self-analysis  Full self-analysis pipeline"
	@echo ""
	@echo "Variables:"
	@echo "  PATTERNS_DIR   Path to patterns (default: ../../src/patterns)"
	@echo "  ANALYSIS_FILE  Path to unified_analysis.json"
	@echo "  ARTIFACTS_DIR  Output directory for artifacts"

# Full inventory analysis
inventory:
	$(PYTHON) atom_inventory.py --patterns-dir $(PATTERNS_DIR) --output $(ARTIFACTS_DIR)/inventory.json

# Coverage analysis from existing Collider output
coverage:
	@if [ -f "$(ANALYSIS_FILE)" ]; then \
		$(PYTHON) atom_coverage.py $(ANALYSIS_FILE) --output $(ARTIFACTS_DIR)/coverage.json; \
	else \
		echo "Error: Analysis file not found. Run './collider full . --output .collider' first."; \
		exit 1; \
	fi

# Quality checks (informational)
quality:
	$(PYTHON) atom_inventory.py --patterns-dir $(PATTERNS_DIR)
	@echo ""
	@if [ -f "$(ANALYSIS_FILE)" ]; then \
		$(PYTHON) atom_coverage.py $(ANALYSIS_FILE); \
	fi

# CI checks (fails on issues)
check:
	$(PYTHON) atom_inventory.py --patterns-dir $(PATTERNS_DIR) --check-duplicates --quiet
	@echo "[PASS] No duplicate atom IDs"
	@if [ -f "$(ANALYSIS_FILE)" ]; then \
		$(PYTHON) atom_coverage.py $(ANALYSIS_FILE) --check-unknown 15 --quiet; \
		echo "[PASS] Unknown rate within threshold"; \
	fi

# Full self-analysis: run Collider then analyze
self-analysis:
	@echo "Running Collider self-analysis..."
	cd ../.. && ./collider full . --output .collider
	@echo ""
	@echo "Running research analysis..."
	@mkdir -p $(ARTIFACTS_DIR)
	$(PYTHON) atom_inventory.py --patterns-dir $(PATTERNS_DIR) --output $(ARTIFACTS_DIR)/inventory.json
	$(PYTHON) atom_coverage.py $(ANALYSIS_FILE) --output $(ARTIFACTS_DIR)/coverage.json
	@echo ""
	@echo "Artifacts saved to $(ARTIFACTS_DIR)/"

# Default: show help
all: help
