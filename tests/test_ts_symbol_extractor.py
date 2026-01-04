import json
import os
import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
TS_EXTRACTOR = REPO_ROOT / "src" / "tools" / "ts_symbol_extractor.cjs"
FIXTURES = REPO_ROOT / "tests" / "fixtures_ts"
REQUIRE_TS = os.getenv("SMOC_REQUIRE_TS_TESTS") == "1"


def _require_or_skip(reason: str) -> None:
    if REQUIRE_TS:
        raise AssertionError(reason)
    pytest.skip(reason)


def _have_node() -> bool:
    return shutil.which("node") is not None


def _check_node_and_typescript() -> None:
    if not _have_node():
        _require_or_skip("node is not available")

    proc = subprocess.run(
        ["node", "-e", "require('typescript'); console.log('ok')"],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        _require_or_skip("typescript package not resolvable from repo")


@lru_cache(maxsize=1)
def _extractor_source() -> str:
    return TS_EXTRACTOR.read_text("utf8")


def _is_valid_kind(kind: str) -> bool:
    """Kinds must be lowercase with optional underscores (no random string matches)."""
    return bool(re.fullmatch(r"[a-z][a-z0-9_]*", kind))


@lru_cache(maxsize=1)
def _allowed_symbol_kinds() -> set[str]:
    src = _extractor_source()
    # Word boundary + support both single and double quotes
    values = set(re.findall(r"\bsymbolKind\s*:\s*['\"]([^'\"]+)['\"]", src))
    assert values, "Could not derive symbol kinds from extractor source"
    # Sanity check: all kinds must follow naming convention
    for kind in values:
        assert _is_valid_kind(kind), f"Invalid symbol kind format: {kind!r}"
    return values


@lru_cache(maxsize=1)
def _allowed_import_kinds() -> set[str]:
    src = _extractor_source()
    # Word boundary + support both single and double quotes
    values = set(
        re.findall(r"pushImport\(\s*\{.*?\bkind\s*:\s*['\"]([^'\"]+)['\"]", src, flags=re.S)
    )
    assert values, "Could not derive import kinds from extractor source"
    # Sanity check: all kinds must follow naming convention
    for kind in values:
        assert _is_valid_kind(kind), f"Invalid import kind format: {kind!r}"
    return values


def _run_ts_extract(fixture_name: str) -> dict:
    _check_node_and_typescript()
    fixture_root = FIXTURES / fixture_name
    assert fixture_root.exists(), f"Missing fixture: {fixture_root}"
    assert TS_EXTRACTOR.exists(), f"Missing extractor: {TS_EXTRACTOR}"

    cmd = ["node", str(TS_EXTRACTOR), str(fixture_root)]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(
            "ts_symbol_extractor failed\n"
            f"cmd: {' '.join(cmd)}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}\n"
        )

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            "ts_symbol_extractor returned invalid JSON\n"
            f"error: {exc}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}\n"
        )
    assert payload.get("ok") is True, payload
    return payload


def _get_file_entry(payload: dict, rel_path: str) -> dict:
    for entry in payload.get("files", []):
        if entry.get("file_path") == rel_path:
            return entry
    raise AssertionError(f"Missing file entry: {rel_path}")


def _assert_no_unknown_contract(payload: dict) -> None:
    files = payload.get("files", [])
    assert isinstance(files, list)
    allowed_languages = {"typescript", "javascript"}
    allowed_symbol_kinds = _allowed_symbol_kinds()
    allowed_import_kinds = _allowed_import_kinds()
    for entry in files:
        assert isinstance(entry, dict)
        file_path = entry.get("file_path")
        if file_path is not None:
            assert file_path != "unknown"

        language = entry.get("language")
        if language is not None:
            assert language in allowed_languages

        for particle in entry.get("particles", []):
            symbol_kind = particle.get("symbol_kind")
            if symbol_kind is not None:
                assert symbol_kind in allowed_symbol_kinds

        for imp in entry.get("raw_imports", []):
            kind = imp.get("kind")
            if kind is not None:
                assert kind in allowed_import_kinds
            target = imp.get("target")
            if target is not None:
                assert target != "unknown"
                assert "::" not in target


def test_ts_extractor_enum_derivation_is_nonempty():
    """
    Always-run guard: ensures our regex derivation stays valid even when the
    Node/TypeScript-dependent tests are skipped.
    """
    assert _allowed_symbol_kinds()
    assert _allowed_import_kinds()


def test_ts_basic_symbols_and_imports():
    payload = _run_ts_extract("toy_ts_basic")
    _assert_no_unknown_contract(payload)

    assert isinstance(payload.get("files"), list)

    a_path = (FIXTURES / "toy_ts_basic" / "a.ts").relative_to(REPO_ROOT).as_posix()
    b_path = (FIXTURES / "toy_ts_basic" / "b.ts").relative_to(REPO_ROOT).as_posix()
    c_path = (FIXTURES / "toy_ts_basic" / "c.ts").relative_to(REPO_ROOT).as_posix()

    a_entry = _get_file_entry(payload, a_path)
    b_entry = _get_file_entry(payload, b_path)
    c_entry = _get_file_entry(payload, c_path)

    assert a_entry.get("language") == "typescript"
    assert b_entry.get("language") == "typescript"
    assert c_entry.get("language") == "typescript"

    a_symbols = {p.get("name") for p in a_entry.get("particles", [])}
    b_symbols = {p.get("name") for p in b_entry.get("particles", [])}
    c_symbols = {p.get("name") for p in c_entry.get("particles", [])}

    assert "f" in a_symbols
    assert "g" in b_symbols
    assert "C" in c_symbols
    assert "C.foo" in c_symbols
    assert "C.bar" in c_symbols

    a_imports = a_entry.get("raw_imports", [])
    targets = {imp.get("target") for imp in a_imports}
    assert "./b" in targets
    assert "axios" in targets

    rel_flags = {imp.get("target"): imp.get("is_relative") for imp in a_imports}
    assert rel_flags.get("./b") is True
    assert rel_flags.get("axios") is False


def test_ts_import_ambiguous_fixture_lists_both_candidates():
    payload = _run_ts_extract("toy_ts_import_ambiguous")
    _assert_no_unknown_contract(payload)

    a_path = (FIXTURES / "toy_ts_import_ambiguous" / "a.ts").relative_to(REPO_ROOT).as_posix()
    mod_path = (FIXTURES / "toy_ts_import_ambiguous" / "mod.ts").relative_to(REPO_ROOT).as_posix()
    index_path = (FIXTURES / "toy_ts_import_ambiguous" / "mod" / "index.ts").relative_to(REPO_ROOT).as_posix()

    a_entry = _get_file_entry(payload, a_path)
    _get_file_entry(payload, mod_path)
    _get_file_entry(payload, index_path)

    a_imports = a_entry.get("raw_imports", [])
    assert any(imp.get("target") == "./mod" for imp in a_imports)


def test_ts_import_constants_includes_module_file():
    payload = _run_ts_extract("toy_ts_import_constants")
    _assert_no_unknown_contract(payload)

    a_path = (FIXTURES / "toy_ts_import_constants" / "a.ts").relative_to(REPO_ROOT).as_posix()
    consts_path = (FIXTURES / "toy_ts_import_constants" / "consts.ts").relative_to(REPO_ROOT).as_posix()

    a_entry = _get_file_entry(payload, a_path)
    consts_entry = _get_file_entry(payload, consts_path)

    a_imports = a_entry.get("raw_imports", [])
    assert any(imp.get("target") == "./consts" for imp in a_imports)
    consts_symbols = {p.get("name") for p in consts_entry.get("particles", [])}
    assert "X" in consts_symbols


# =============================================================================
# Always-run tests (no Node/TS dependency)
# =============================================================================
# These tests verify the enum derivation helpers work even when Node/TypeScript
# isn't installed, ensuring the regex patterns stay valid.


def test_ts_extractor_enum_derivation_is_nonempty():
    """Enum derivation must produce non-empty sets even without Node/TS."""
    symbol_kinds = _allowed_symbol_kinds()
    import_kinds = _allowed_import_kinds()

    assert symbol_kinds, "symbol kinds derivation broke"
    assert import_kinds, "import kinds derivation broke"

    # Verify expected minimum kinds are present
    assert "function" in symbol_kinds, "missing 'function' symbol kind"
    assert "class" in symbol_kinds, "missing 'class' symbol kind"
    assert "method" in symbol_kinds, "missing 'method' symbol kind"
    assert "import" in import_kinds, "missing 'import' import kind"
    assert "require" in import_kinds, "missing 'require' import kind"
