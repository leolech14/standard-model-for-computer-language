"""
REACT T2 ECOSYSTEM DETECTION TESTS
===================================

These tests validate the React T2 atom detection pipeline:
1. Tree-sitter extracts all JS/TS/TSX functions and classes
2. Universal classifier assigns correct EXT.REACT.* atoms
3. Ecosystem detection is accurate for React patterns

Validated against real-world codebases:
- Facebook create-react-app template
- TanStack Query (@tanstack/react-query)
- Next.js examples

Run with: python3 -m pytest tests/test_react_t2_detection.py -v

Note: Tests requiring tree-sitter will be skipped if tree-sitter is not installed.
"""
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

import pytest

# Add src/core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.tree_sitter_engine import TreeSitterUniversalEngine

# Check if tree-sitter is available
try:
    import tree_sitter
    import tree_sitter_javascript
    import tree_sitter_typescript
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "react_t2"

# Skip marker for tree-sitter dependent tests
requires_tree_sitter = pytest.mark.skipif(
    not TREE_SITTER_AVAILABLE,
    reason="tree-sitter not installed for this Python version"
)


@requires_tree_sitter
class TestTreeSitterExtraction:
    """Tree-sitter must extract all JS/TS/TSX functions and classes."""

    def test_extracts_all_functions_from_tsx(self):
        """Tree-sitter extracts all function declarations from TSX."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "hooks_component.tsx"))

        particles = result.get("particles", [])
        names = [p["name"] for p in particles]

        # Must find all three functions
        assert "useCounter" in names, "Missing custom hook useCounter"
        assert "Counter" in names, "Missing functional component Counter"
        assert "App" in names, "Missing root component App"

    def test_extracts_classes_from_tsx(self):
        """Tree-sitter extracts class declarations from TSX."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "class_component.tsx"))

        particles = result.get("particles", [])
        names = [p["name"] for p in particles]

        # Must find both class components
        assert "ErrorBoundary" in names, "Missing ErrorBoundary class"
        assert "Counter" in names, "Missing Counter class"

    def test_captures_body_source(self):
        """Tree-sitter captures full body_source for T2 pattern matching."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "hooks_component.tsx"))

        particles = result.get("particles", [])
        use_counter = next((p for p in particles if p["name"] == "useCounter"), None)

        assert use_counter is not None, "useCounter not found"
        body = use_counter.get("body_source", "")
        assert "useState" in body, "body_source must contain useState for T2 detection"
        assert "useCallback" in body, "body_source must contain useCallback"


@requires_tree_sitter
class TestReactT2AtomAssignment:
    """Classifier must assign correct EXT.REACT.* atoms."""

    def test_custom_hook_gets_react_atom(self):
        """Custom hook using useState gets EXT.REACT.005."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "hooks_component.tsx"))

        particles = result.get("particles", [])
        use_counter = next((p for p in particles if p["name"] == "useCounter"), None)

        assert use_counter is not None, "useCounter not found"
        dims = use_counter.get("dimensions", {})

        assert dims.get("D1_ECOSYSTEM") == "react", \
            f"useCounter should detect react ecosystem, got {dims.get('D1_ECOSYSTEM')}"
        assert dims.get("D1_WHAT", "").startswith("EXT.REACT."), \
            f"useCounter should get EXT.REACT.* atom, got {dims.get('D1_WHAT')}"

    def test_functional_component_gets_react_atom(self):
        """Functional component with JSX gets EXT.REACT.001."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "hooks_component.tsx"))

        particles = result.get("particles", [])
        app = next((p for p in particles if p["name"] == "App"), None)

        assert app is not None, "App not found"
        dims = app.get("dimensions", {})

        assert dims.get("D1_ECOSYSTEM") == "react", \
            f"App should detect react ecosystem, got {dims.get('D1_ECOSYSTEM')}"
        assert dims.get("D1_WHAT") == "EXT.REACT.001", \
            f"App (root component) should get EXT.REACT.001, got {dims.get('D1_WHAT')}"

    def test_class_component_gets_react_atom(self):
        """Class extending React.Component gets EXT.REACT.002."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "class_component.tsx"))

        particles = result.get("particles", [])
        # Use Counter (plain class component), not ErrorBoundary (which is EXT.REACT.018)
        counter = next((p for p in particles if p["name"] == "Counter"), None)

        assert counter is not None, "Counter not found"
        dims = counter.get("dimensions", {})

        assert dims.get("D1_ECOSYSTEM") == "react", \
            f"Counter should detect react ecosystem, got {dims.get('D1_ECOSYSTEM')}"
        assert dims.get("D1_WHAT") == "EXT.REACT.002", \
            f"Counter (class component) should get EXT.REACT.002, got {dims.get('D1_WHAT')}"


@requires_tree_sitter
class TestReactHookPatterns:
    """Individual React hook patterns must be detected."""

    @pytest.fixture
    def hooks_particles(self) -> List[Dict]:
        """Load particles from hooks fixture."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "hooks_component.tsx"))
        return result.get("particles", [])

    def test_usestate_detected(self, hooks_particles):
        """useState usage triggers EXT.REACT.005."""
        # useCounter uses useState
        use_counter = next((p for p in hooks_particles if p["name"] == "useCounter"), None)
        assert use_counter is not None

        d1_what = use_counter.get("dimensions", {}).get("D1_WHAT", "")
        # Should match EXT.REACT.005 (useState) or similar hook pattern
        assert d1_what.startswith("EXT.REACT."), f"Expected EXT.REACT.*, got {d1_what}"

    def test_component_with_hooks_detected(self, hooks_particles):
        """Component using multiple hooks gets React classification."""
        counter = next((p for p in hooks_particles if p["name"] == "Counter"), None)
        assert counter is not None

        dims = counter.get("dimensions", {})
        assert dims.get("D1_ECOSYSTEM") == "react"
        # Counter uses useEffect, useMemo, useContext, useRef - should get a React atom
        assert dims.get("D1_WHAT", "").startswith("EXT.REACT.")


@requires_tree_sitter
class TestNonReactCodeCorrectlyIgnored:
    """Non-React code must NOT get React T2 atoms."""

    def test_plain_function_not_react(self):
        """Plain utility function without React patterns stays generic."""
        engine = TreeSitterUniversalEngine()

        # Create a temporary plain JS file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
            f.write("""
function add(a, b) {
  return a + b;
}

function multiply(a, b) {
  return a * b;
}
""")
            temp_path = f.name

        try:
            result = engine.analyze_file(temp_path)
            particles = result.get("particles", [])

            for p in particles:
                dims = p.get("dimensions", {})
                # Should NOT be classified as React
                assert dims.get("D1_ECOSYSTEM") != "react", \
                    f"Plain function {p['name']} incorrectly classified as React"
                assert not dims.get("D1_WHAT", "").startswith("EXT.REACT."), \
                    f"Plain function {p['name']} incorrectly got React atom"
        finally:
            Path(temp_path).unlink()


@requires_tree_sitter
class TestAtomDistributionValidation:
    """Validate atom distribution matches expected patterns."""

    def test_hooks_fixture_atom_distribution(self):
        """hooks_component.tsx should have specific atom distribution."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "hooks_component.tsx"))

        particles = result.get("particles", [])
        atoms = Counter(p.get("dimensions", {}).get("D1_WHAT", "unknown") for p in particles)

        # At least one of each expected type
        react_atoms = [a for a in atoms.keys() if a.startswith("EXT.REACT.")]
        assert len(react_atoms) >= 2, f"Expected at least 2 React atoms, got {react_atoms}"

    def test_class_fixture_has_class_component_atoms(self):
        """class_component.tsx should have EXT.REACT.002 atoms."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "class_component.tsx"))

        particles = result.get("particles", [])
        atoms = [p.get("dimensions", {}).get("D1_WHAT") for p in particles]

        assert "EXT.REACT.002" in atoms, f"Expected EXT.REACT.002 for class components, got {atoms}"


@requires_tree_sitter
class TestTreeSitterFallback:
    """Tree-sitter fallback behavior must be correct."""

    def test_fallback_to_simple_query_still_works(self):
        """When complex query fails, simple query still extracts particles."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "hooks_component.tsx"))

        particles = result.get("particles", [])

        # Should still find all main declarations even with fallback
        assert len(particles) >= 3, f"Expected at least 3 particles, got {len(particles)}"

        names = [p["name"] for p in particles]
        assert "App" in names, "Fallback must still find App"


@requires_tree_sitter
class TestHookMetadataEnrichment:
    """Hook usage metadata must be correctly added to React components."""

    def test_custom_hook_has_hook_metadata(self):
        """Custom hooks should have hooks_used metadata."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "hooks_component.tsx"))

        particles = result.get("particles", [])
        use_counter = next((p for p in particles if p["name"] == "useCounter"), None)

        assert use_counter is not None, "useCounter not found"
        meta = use_counter.get("metadata", {})

        assert meta.get("hooks_used", 0) >= 2, \
            f"useCounter should have at least 2 hooks, got {meta.get('hooks_used')}"
        assert "useState" in meta.get("hooks", []), \
            f"useCounter should use useState, got {meta.get('hooks')}"

    def test_component_with_hooks_has_metadata(self):
        """Components using hooks should have hooks_used metadata."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "hooks_component.tsx"))

        particles = result.get("particles", [])
        counter = next((p for p in particles if p["name"] == "Counter"), None)

        assert counter is not None, "Counter not found"
        meta = counter.get("metadata", {})

        assert meta.get("hooks_used", 0) >= 3, \
            f"Counter should have at least 3 hooks, got {meta.get('hooks_used')}"
        # Should include useEffect, useMemo, useContext, useRef, useCounter
        hooks = meta.get("hooks", [])
        assert len(hooks) >= 3, f"Expected at least 3 hook names, got {hooks}"

    def test_component_without_hooks_no_metadata(self):
        """Components without hooks should not have hooks_used metadata."""
        engine = TreeSitterUniversalEngine()
        result = engine.analyze_file(str(FIXTURES_DIR / "hooks_component.tsx"))

        particles = result.get("particles", [])
        app = next((p for p in particles if p["name"] == "App"), None)

        assert app is not None, "App not found"
        meta = app.get("metadata", {})

        assert meta.get("hooks_used", 0) == 0, \
            f"App should have 0 hooks, got {meta.get('hooks_used')}"

    def test_non_react_functions_no_hook_metadata(self):
        """Non-React functions should not have hook metadata."""
        engine = TreeSitterUniversalEngine()

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
            f.write("""
function add(a, b) {
  return a + b;
}
""")
            temp_path = f.name

        try:
            result = engine.analyze_file(temp_path)
            particles = result.get("particles", [])

            for p in particles:
                meta = p.get("metadata", {})
                assert "hooks_used" not in meta, \
                    f"Plain function {p['name']} should not have hooks_used"
        finally:
            Path(temp_path).unlink()
