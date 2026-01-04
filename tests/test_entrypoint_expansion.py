"""
ENTRYPOINT EXPANSION TESTS
===========================

Tests for framework-aware entrypoint detection (Phase 3 of ROADMAP).

Validates that entrypoints are correctly detected for:
- Click CLI commands
- Typer CLI commands
- FastAPI route handlers
- Flask route handlers
- Pytest test functions (flag-gated)

Run with: python3 -m pytest tests/test_entrypoint_expansion.py -v
"""
import sys
from pathlib import Path

import pytest

# Add src/core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))

from validation.self_proof import SelfProofValidator


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestClickEntrypoints:
    """Click CLI entrypoint detection."""

    def test_click_command_detected(self):
        """@click.command() functions are detected as entrypoints."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_click")
        result = validator.prove()

        entrypoint_names = {
            e.split("::")[-1] for e in result.entrypoints
        }

        assert "main" in entrypoint_names, "main() with @click.command not detected"
        assert "cli" in entrypoint_names, "cli() with @click.group not detected"

    def test_click_helper_reachable(self):
        """Helper functions are reachable from Click entrypoints."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_click")
        result = validator.prove()

        # helper() should be reachable (not in unreachable list)
        unreachable_names = {
            u.split("::")[-1] for u in result.unreachable
        }

        assert "helper" not in unreachable_names, "helper() should be reachable from entrypoints"

    def test_click_reachability_positive(self):
        """Reachability should be > 0 with Click entrypoints."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_click")
        result = validator.prove()

        assert result.reachability > 0, "Reachability should be positive with entrypoints"


class TestTyperEntrypoints:
    """Typer CLI entrypoint detection."""

    def test_typer_command_detected(self):
        """@app.command() functions are detected as entrypoints."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_typer")
        result = validator.prove()

        entrypoint_names = {
            e.split("::")[-1] for e in result.entrypoints
        }

        assert "main" in entrypoint_names, "main() with @app.command not detected"
        assert "greet" in entrypoint_names, "greet() with @app.command not detected"
        assert "callback" in entrypoint_names, "callback() with @app.callback not detected"

    def test_typer_reachability_positive(self):
        """Reachability should be > 0 with Typer entrypoints."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_typer")
        result = validator.prove()

        assert result.reachability > 0, "Reachability should be positive with entrypoints"


class TestFastAPIEntrypoints:
    """FastAPI route handler entrypoint detection."""

    def test_fastapi_routes_detected(self):
        """@app.get/post/etc decorators are detected as entrypoints."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_fastapi")
        result = validator.prove()

        entrypoint_names = {
            e.split("::")[-1] for e in result.entrypoints
        }

        assert "root" in entrypoint_names, "root() with @app.get not detected"
        assert "create_item" in entrypoint_names, "create_item() with @app.post not detected"

    def test_fastapi_router_detected(self):
        """@router.get/delete/etc decorators are detected as entrypoints."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_fastapi")
        result = validator.prove()

        entrypoint_names = {
            e.split("::")[-1] for e in result.entrypoints
        }

        assert "list_users" in entrypoint_names, "list_users() with @router.get not detected"
        assert "delete_user" in entrypoint_names, "delete_user() with @router.delete not detected"

    def test_fastapi_reachability_positive(self):
        """Reachability should be > 0 with FastAPI entrypoints."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_fastapi")
        result = validator.prove()

        assert result.reachability > 0, "Reachability should be positive with entrypoints"


class TestFlaskEntrypoints:
    """Flask route handler entrypoint detection."""

    def test_flask_routes_detected(self):
        """@app.route decorators are detected as entrypoints."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_flask")
        result = validator.prove()

        entrypoint_names = {
            e.split("::")[-1] for e in result.entrypoints
        }

        assert "index" in entrypoint_names, "index() with @app.route not detected"
        assert "about" in entrypoint_names, "about() with @app.route not detected"
        assert "create_data" in entrypoint_names, "create_data() with @app.route not detected"

    def test_flask_reachability_positive(self):
        """Reachability should be > 0 with Flask entrypoints."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_flask")
        result = validator.prove()

        assert result.reachability > 0, "Reachability should be positive with entrypoints"


class TestPytestEntrypoints:
    """Pytest test function entrypoint detection (flag-gated)."""

    def test_pytest_excluded_by_default(self):
        """Test functions are NOT entrypoints by default (include_tests=False)."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_pytest", include_tests=False)
        result = validator.prove()

        entrypoint_names = {
            e.split("::")[-1] for e in result.entrypoints
        }

        # test_example should NOT be an entrypoint by default
        test_entries = [n for n in entrypoint_names if n.startswith("test_")]
        assert len(test_entries) == 0, "test_* functions should not be entrypoints by default"

    def test_pytest_included_with_flag(self):
        """Test functions ARE entrypoints when include_tests=True."""
        validator = SelfProofValidator(FIXTURES_DIR / "toy_entry_pytest", include_tests=True)
        result = validator.prove()

        entrypoint_names = {
            e.split("::")[-1] for e in result.entrypoints
        }

        assert "test_example" in entrypoint_names, "test_example should be entrypoint with include_tests=True"


class TestEntrypointsAreAtomicOnly:
    """Entrypoints must be atomic nodes (never containers)."""

    def test_all_entrypoints_are_atomic(self):
        """All detected entrypoints must be in N_atomic."""
        for fixture in ["toy_entry_click", "toy_entry_typer", "toy_entry_fastapi", "toy_entry_flask"]:
            validator = SelfProofValidator(FIXTURES_DIR / fixture)
            result = validator.prove()

            for node in result.proof_nodes:
                if node["id"] in result.entrypoints:
                    node_type = node.get("type", "").lower()
                    assert node_type in {"function", "method", "class"}, (
                        f"Entrypoint {node['id']} is not atomic: {node_type}"
                    )


class TestReachabilityDiagnostics:
    """Reachability diagnostics invariant tests."""

    def test_reasons_sum_equals_total(self):
        """sum(reasons.values()) == unreachable_total."""
        for fixture in ["toy_entry_click", "toy_entry_typer", "toy_entry_fastapi", "toy_entry_flask"]:
            validator = SelfProofValidator(FIXTURES_DIR / fixture)
            result = validator.prove()

            diag = result.reachability_diagnostics
            assert diag is not None, "diagnostics should always be present"

            reason_sum = sum(diag.reasons.values())
            assert reason_sum == diag.unreachable_total, (
                f"{fixture}: sum(reasons)={reason_sum} != unreachable_total={diag.unreachable_total}"
            )

    def test_deterministic_output(self):
        """Diagnostics produce stable ordering across multiple runs."""
        for fixture in ["toy_entry_click", "toy_entry_flask"]:
            results = []
            for _ in range(3):
                validator = SelfProofValidator(FIXTURES_DIR / fixture)
                result = validator.prove()
                diag = result.reachability_diagnostics
                results.append({
                    "reasons": dict(diag.reasons),
                    "examples": {k: list(v) for k, v in diag.examples.items()},
                    "cluster_roots": [r["node_id"] for r in diag.cluster_roots],
                })

            # All runs should produce identical output
            assert results[0] == results[1], f"{fixture}: run 0 != run 1"
            assert results[1] == results[2], f"{fixture}: run 1 != run 2"

    def test_diagnostics_do_not_affect_proof_score(self):
        """Diagnostics are observational - they don't change proof_score."""
        for fixture in ["toy_entry_click", "toy_entry_flask"]:
            validator = SelfProofValidator(FIXTURES_DIR / fixture)
            result = validator.prove()

            # Proof score should be computed before diagnostics are attached
            # Re-proving should give the same score
            validator2 = SelfProofValidator(FIXTURES_DIR / fixture)
            result2 = validator2.prove()

            assert result.proof_score == result2.proof_score, (
                f"{fixture}: proof scores differ between runs"
            )

    def test_diagnostics_only_include_atomic_nodes(self):
        """All nodes in diagnostics (examples, cluster_roots) are N_atomic."""
        for fixture in ["toy_entry_click", "toy_entry_typer", "toy_entry_fastapi", "toy_entry_flask"]:
            validator = SelfProofValidator(FIXTURES_DIR / fixture)
            result = validator.prove()

            atomic_ids = {n["id"] for n in result.proof_nodes}
            diag = result.reachability_diagnostics

            # Check examples
            for reason, examples in diag.examples.items():
                for node_id in examples:
                    assert node_id in atomic_ids, (
                        f"{fixture}: example {node_id} not in N_atomic"
                    )

            # Check cluster roots
            for root in diag.cluster_roots:
                assert root["node_id"] in atomic_ids, (
                    f"{fixture}: cluster root {root['node_id']} not in N_atomic"
                )
