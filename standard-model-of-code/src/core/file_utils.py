"""File utility functions for robust file handling."""

import logging
from pathlib import Path
from typing import Optional, Tuple

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False
    logging.warning("chardet not installed. Using UTF-8 fallback for encoding detection.")


def detect_encoding(file_path: str, sample_size: int = 10000) -> str:
    """Detect file encoding using chardet.

    Args:
        file_path: Path to the file
        sample_size: Number of bytes to sample for detection

    Returns:
        Detected encoding (defaults to 'utf-8' if detection fails)
    """
    if not HAS_CHARDET:
        return 'utf-8'

    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(sample_size)

        if not raw_data:
            return 'utf-8'

        result = chardet.detect(raw_data)
        encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0)

        # Fall back to UTF-8 for low confidence
        if confidence < 0.7 or encoding is None:
            return 'utf-8'

        return encoding

    except Exception as e:
        logging.warning(f"Encoding detection failed for {file_path}: {e}")
        return 'utf-8'


def read_file_safe(file_path: str) -> Tuple[Optional[str], str]:
    """Read file with automatic encoding detection.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (content, encoding_used)
        Content is None if file cannot be read
    """
    encoding = detect_encoding(file_path)

    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            return f.read(), encoding
    except Exception as e:
        logging.error(f"Failed to read {file_path}: {e}")
        return None, encoding


def is_binary_file(file_path: str, sample_size: int = 8192) -> bool:
    """Check if file appears to be binary.

    Args:
        file_path: Path to the file
        sample_size: Number of bytes to check

    Returns:
        True if file appears to be binary
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(sample_size)

        # Check for null bytes (common in binary files)
        if b'\x00' in chunk:
            return True

        # Check ratio of non-text bytes
        text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
        non_text = sum(1 for byte in chunk if byte not in text_chars)

        return non_text / len(chunk) > 0.30 if chunk else False

    except Exception:
        return False
