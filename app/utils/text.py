"""Text normalization helpers.

Kept dependency-free and pure so they can be reused by any extractor strategy
and unit-tested in isolation.
"""
from __future__ import annotations

import re
import unicodedata

# Matches runs of horizontal whitespace (spaces, tabs) but not newlines, so we
# can collapse spacing while preserving paragraph structure.
_HORIZONTAL_WS_RE = re.compile(r"[ \t\f\v]+")
# Matches 3 or more consecutive newlines (with optional surrounding spaces),
# used to collapse excessive blank lines down to a single blank line.
_MULTI_NEWLINE_RE = re.compile(r"\n\s*\n\s*\n+")
# Common zero-width / non-breaking characters that add noise to extracted text.
_ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\ufeff]")


def clean_text(text: str) -> str:
    """Normalize and clean raw extracted text.

    The cleaning pipeline:

    1. Normalizes Unicode to NFKC form (e.g. ligatures, full-width chars).
    2. Standardizes line endings to ``\\n``.
    3. Removes zero-width and BOM characters.
    4. Collapses horizontal whitespace within each line.
    5. Trims trailing spaces on each line.
    6. Collapses 3+ blank lines into a single blank line.
    7. Strips leading/trailing whitespace from the whole document.

    Args:
        text: Raw text to clean.

    Returns:
        The cleaned text (an empty string if ``text`` is falsy).
    """
    if not text:
        return ""

    # 1. Unicode normalization.
    text = unicodedata.normalize("NFKC", text)

    # 2. Normalize line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Strip zero-width / BOM characters.
    text = _ZERO_WIDTH_RE.sub("", text)

    # 4 & 5. Collapse horizontal whitespace and trim each line's trailing space.
    lines = [
        _HORIZONTAL_WS_RE.sub(" ", line).strip()
        for line in text.split("\n")
    ]
    text = "\n".join(lines)

    # 6. Collapse excessive blank lines.
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)

    # 7. Final trim.
    return text.strip()
