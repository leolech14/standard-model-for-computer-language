#!/bin/bash
# Agent Boot Script
# Generates INITIATION_REPORT for agent sessions
# Usage: bash context-management/tools/maintenance/boot.sh [--json]
#
# Flags:
#   --json    Output only JSON (no decorative text)

set -e

# Parse flags
JSON_ONLY=false
for arg in "$@"; do
    case $arg in
        --json) JSON_ONLY=true ;;
    esac
done

if [ "$JSON_ONLY" = false ]; then
    echo "=== AGENT BOOT SEQUENCE ==="
    echo ""
fi

# Update timestamps CSV
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/update_timestamps.sh" ]; then
    if [ "$JSON_ONLY" = false ]; then
        echo "Updating file timestamps..."
    fi
    "$SCRIPT_DIR/update_timestamps.sh" --quiet 2>/dev/null || true
    if [ "$JSON_ONLY" = false ]; then
        echo "Timestamps updated."
        echo ""
    fi
fi

# Get repo root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
if [ "$JSON_ONLY" = false ]; then
    echo "Repo Root: $REPO_ROOT"
fi

# Get current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "not_a_git_repo")
if [ "$JSON_ONLY" = false ]; then
    echo "Branch: $BRANCH"
fi

# Get git status
if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
    STATUS="clean"
else
    STATUS="dirty"
fi
if [ "$JSON_ONLY" = false ]; then
    echo "Status: $STATUS"
fi

# Detect commands (look for common patterns)
detect_command() {
    local type=$1

    case $type in
        test)
            if [ -f "package.json" ] && grep -q '"test"' package.json 2>/dev/null; then
                echo "npm test"
            elif [ -f "pytest.ini" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
                echo "pytest"
            elif [ -f "Makefile" ] && grep -q '^test:' Makefile 2>/dev/null; then
                echo "make test"
            elif [ -f "go.mod" ]; then
                echo "go test ./..."
            else
                echo "not_found"
            fi
            ;;
        lint)
            if [ -f "package.json" ] && grep -q '"lint"' package.json 2>/dev/null; then
                echo "npm run lint"
            elif [ -f "pyproject.toml" ] && grep -q 'ruff' pyproject.toml 2>/dev/null; then
                echo "ruff check ."
            elif [ -f ".eslintrc" ] || [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ]; then
                echo "eslint ."
            else
                echo "not_found"
            fi
            ;;
        format)
            if [ -f "package.json" ] && grep -q '"format"' package.json 2>/dev/null; then
                echo "npm run format"
            elif [ -f "pyproject.toml" ] && grep -q 'black' pyproject.toml 2>/dev/null; then
                echo "black ."
            elif [ -f ".prettierrc" ] || [ -f ".prettierrc.js" ]; then
                echo "prettier --write ."
            else
                echo "not_found"
            fi
            ;;
        build)
            if [ -f "package.json" ] && grep -q '"build"' package.json 2>/dev/null; then
                echo "npm run build"
            elif [ -f "Makefile" ] && grep -q '^build:' Makefile 2>/dev/null; then
                echo "make build"
            elif [ -f "go.mod" ]; then
                echo "go build ./..."
            else
                echo "not_found"
            fi
            ;;
        run)
            if [ -f "package.json" ] && grep -q '"start"' package.json 2>/dev/null; then
                echo "npm start"
            elif [ -f "main.py" ]; then
                echo "python main.py"
            elif [ -f "Makefile" ] && grep -q '^run:' Makefile 2>/dev/null; then
                echo "make run"
            else
                echo "not_found"
            fi
            ;;
    esac
}

# PROJECT_elements specific overrides (check for collider)
if [ -f "$REPO_ROOT/collider" ] || [ -f "$REPO_ROOT/standard-model-of-code/cli.py" ]; then
    # This is PROJECT_elements - use known commands
    TEST_CMD="cd standard-model-of-code && pytest tests/ -q"
    LINT_CMD="cd standard-model-of-code && ruff check src/"
    FORMAT_CMD="cd standard-model-of-code && black src/ --check"
    BUILD_CMD="cd standard-model-of-code && pip install -e ."
    RUN_CMD="./collider full <path> --output <dir>"
else
    # Generic detection
    TEST_CMD=$(detect_command test)
    LINT_CMD=$(detect_command lint)
    FORMAT_CMD=$(detect_command format)
    BUILD_CMD=$(detect_command build)
    RUN_CMD=$(detect_command run)
fi

if [ "$JSON_ONLY" = false ]; then
    echo ""
    echo "Commands detected:"
    echo "  test:   $TEST_CMD"
    echo "  lint:   $LINT_CMD"
    echo "  format: $FORMAT_CMD"
    echo "  build:  $BUILD_CMD"
    echo "  run:    $RUN_CMD"
fi

# Generate timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ "$JSON_ONLY" = false ]; then
    echo ""
    echo "=== INITIATION_REPORT ==="
    echo ""
fi

# Output JSON
cat <<EOF
{
  "initiated": true,
  "timestamp": "$TIMESTAMP",
  "repo_root": "$REPO_ROOT",
  "branch": "$BRANCH",
  "status": "$STATUS",
  "commands": {
    "test": "$TEST_CMD",
    "lint": "$LINT_CMD",
    "format": "$FORMAT_CMD",
    "build": "$BUILD_CMD",
    "run": "$RUN_CMD"
  },
  "policies_acknowledged": {
    "commit_discipline": true,
    "no_dirty_end": true,
    "test_before_done": true,
    "summary_required": true
  },
  "notes": []
}
EOF

if [ "$JSON_ONLY" = false ]; then
    echo ""
    echo "=== HEALTH CHECKS ==="
    echo ""

    # Run boundary analyzer if available (PROJECT_elements only)
    BOUNDARY_ANALYZER="$REPO_ROOT/context-management/tools/maintenance/boundary_analyzer.py"
    if [ -f "$BOUNDARY_ANALYZER" ]; then
        echo "Running boundary analyzer..."
        python3 "$BOUNDARY_ANALYZER" --save --threshold 60 2>/dev/null || {
            echo "  ⚠️  Boundary alignment below threshold (see .agent/intelligence/boundary_analysis.json)"
        }
        echo ""
    fi

    # Run Gemini status if available
    GEMINI_STATUS="$REPO_ROOT/context-management/tools/ai/gemini_status.py"
    if [ -f "$GEMINI_STATUS" ]; then
        echo "Checking Gemini API status..."
        python3 "$GEMINI_STATUS" --quick 2>/dev/null && echo "  ✓ Gemini API OK" || echo "  ⚠️  Gemini API issues detected"
        echo ""
    fi

    echo "=== BOOT COMPLETE ==="
    echo ""
    echo "Next steps:"
    echo "1. Review context-management/docs/agent_school/ for workflows"
    echo "2. Review standard-model-of-code/CLAUDE.md for tool details"
    echo "3. Begin your task using: SCAN → PLAN → EXECUTE → VALIDATE → COMMIT"
    echo ""
    echo "Maintenance tools:"
    echo "  python3 context-management/tools/maintenance/boundary_analyzer.py  # Boundary check"
    echo "  python3 context-management/tools/ai/gemini_status.py               # API status"
fi
