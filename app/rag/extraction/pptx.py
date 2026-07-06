"""PPTX text extraction strategy."""
from __future__ import annotations

from io import BytesIO
from typing import ClassVar

from pptx import Presentation

from app.rag.extraction.base import TextExtractor


class PptxExtractor(TextExtractor):
    """Extract text from PowerPoint ``.pptx`` files using :mod:`python-pptx`."""

    extensions: ClassVar[frozenset[str]] = frozenset({".pptx"})

    def extract(self, data: bytes) -> str:
        presentation = Presentation(BytesIO(data))

        slides_text: list[str] = []
        for slide in presentation.slides:
            parts: list[str] = []
            for shape in slide.shapes:
                # Only shapes with a text frame carry readable text.
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        run_text = "".join(run.text for run in paragraph.runs)
                        if run_text:
                            parts.append(run_text)
            if parts:
                slides_text.append("\n".join(parts))

        # Separate slides with a blank line to preserve structure.
        return "\n\n".join(slides_text)
