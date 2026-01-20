"""Tests for file_utils module."""

import pytest
from src.core.file_utils import detect_encoding, read_file_safe, is_binary_file


class TestDetectEncoding:
    """Tests for detect_encoding function."""

    def test_utf8_file(self, tmp_path):
        """UTF-8 file should be detected."""
        test_file = tmp_path / "utf8.txt"
        test_file.write_text("Hello, World!", encoding='utf-8')

        encoding = detect_encoding(str(test_file))
        # Without chardet, defaults to utf-8
        assert encoding.lower() in ('utf-8', 'ascii')

    def test_empty_file(self, tmp_path):
        """Empty file should default to UTF-8."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        encoding = detect_encoding(str(test_file))
        assert encoding == 'utf-8'

    def test_nonexistent_file(self, tmp_path):
        """Nonexistent file should return UTF-8 default."""
        encoding = detect_encoding(str(tmp_path / "nope.txt"))
        assert encoding == 'utf-8'


class TestReadFileSafe:
    """Tests for read_file_safe function."""

    def test_read_normal_file(self, tmp_path):
        """Normal file should be read successfully."""
        test_file = tmp_path / "normal.py"
        test_file.write_text("x = 42")

        content, encoding = read_file_safe(str(test_file))
        assert content == "x = 42"
        assert encoding is not None

    def test_read_nonexistent_file(self, tmp_path):
        """Nonexistent file should return None."""
        content, encoding = read_file_safe(str(tmp_path / "nope.txt"))
        assert content is None

    def test_read_file_with_unicode(self, tmp_path):
        """File with unicode should be read correctly."""
        test_file = tmp_path / "unicode.py"
        test_file.write_text("greeting = 'Hello, World!'", encoding='utf-8')

        content, encoding = read_file_safe(str(test_file))
        assert content is not None
        assert "greeting" in content


class TestIsBinaryFile:
    """Tests for is_binary_file function."""

    def test_text_file(self, tmp_path):
        """Text file should not be detected as binary."""
        test_file = tmp_path / "text.py"
        test_file.write_text("def hello(): pass")

        assert is_binary_file(str(test_file)) is False

    def test_binary_file(self, tmp_path):
        """Binary file should be detected."""
        test_file = tmp_path / "binary.bin"
        test_file.write_bytes(b'\x00\x01\x02\x03\x04\x05')

        assert is_binary_file(str(test_file)) is True

    def test_empty_file(self, tmp_path):
        """Empty file should not be detected as binary."""
        test_file = tmp_path / "empty.txt"
        test_file.write_bytes(b'')

        assert is_binary_file(str(test_file)) is False

    def test_nonexistent_file(self, tmp_path):
        """Nonexistent file should return False."""
        assert is_binary_file(str(tmp_path / "nope.txt")) is False
