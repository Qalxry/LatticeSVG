"""TextNode — a leaf node that renders text with automatic line breaking."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List

from .base import LayoutConstraints, Node, Rect
from ..text.font import FontManager
from ..text.shaper import (
    Line,
    align_lines,
    break_lines,
    compute_text_block_size,
    get_max_content_width,
    get_min_content_width,
    measure_text,
)


class TextNode(Node):
    """A node that displays text content.

    The text is measured using FreeType (or Pillow fallback) and
    automatically wrapped according to the ``white-space`` property.
    """

    def __init__(
        self,
        text: str,
        style: Optional[Dict[str, Any]] = None,
        parent: Optional[Node] = None,
    ) -> None:
        super().__init__(style=style, parent=parent)
        self.text: str = text
        self.lines: List[Line] = []  # populated after layout

    # -----------------------------------------------------------------
    # Font resolution helpers
    # -----------------------------------------------------------------

    def _font_path(self) -> Optional[str]:
        fm = FontManager.instance()
        family = self.style.get("font-family")
        if isinstance(family, str):
            family = [family]
        weight = self.style.get("font-weight") or "normal"
        fstyle = self.style.get("font-style") or "normal"
        return fm.find_font(family, weight=weight, style=fstyle)

    def _font_size_int(self) -> int:
        fs = self.style.get("font-size")
        if isinstance(fs, (int, float)):
            return max(1, int(fs))
        return 16

    # -----------------------------------------------------------------
    # Measurement
    # -----------------------------------------------------------------

    def measure(self, constraints: LayoutConstraints) -> Tuple[float, float, float]:
        """Return ``(min_content_width, max_content_width, intrinsic_height)``."""
        font_path = self._font_path()
        if font_path is None:
            return (0.0, 0.0, 0.0)

        size = self._font_size_int()
        ws = self.style.get("white-space") or "normal"
        fm = FontManager.instance()

        min_w = get_min_content_width(self.text, font_path, size, ws, fm=fm)
        max_w = get_max_content_width(self.text, font_path, size, ws, fm=fm)

        # Intrinsic height at max-content width (single line for normal)
        lines = break_lines(self.text, max_w + 1, font_path, size, ws, fm=fm)
        lh = self._line_height()
        _, h = compute_text_block_size(lines, lh, float(size))

        # Add padding + border
        ph = self.style.padding_horizontal + self.style.border_horizontal
        pv = self.style.padding_vertical + self.style.border_vertical
        return (min_w + ph, max_w + ph, h + pv)

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------

    def layout(self, constraints: LayoutConstraints) -> None:
        font_path = self._font_path()
        size = self._font_size_int()
        ws = self.style.get("white-space") or "normal"
        fm = FontManager.instance()

        content_w = self._content_available_width(constraints)
        if content_w is None:
            content_w = constraints.available_width or 800.0

        # Store resolved font info for rendering
        self._resolved_font_path = font_path
        self._resolved_font_family = None
        if font_path is not None:
            self._resolved_font_family = fm.font_family_name(font_path)

        if font_path is None:
            # No font available — empty box
            self._resolve_box_model(content_w, 0.0)
            self.lines = []
            return

        # Break lines
        self.lines = break_lines(self.text, content_w, font_path, size, ws, fm=fm)

        # Align
        text_align = self.style.get("text-align") or "left"
        self.lines = align_lines(self.lines, content_w, text_align)

        # Compute content height
        lh = self._line_height()
        _, content_h = compute_text_block_size(self.lines, lh, float(size))

        # Handle explicit width/height
        explicit_w = self._resolve_width(constraints)
        if explicit_w is not None:
            content_w = max(0.0, explicit_w - self.style.padding_horizontal - self.style.border_horizontal)
        explicit_h = self._resolve_height(constraints)
        if explicit_h is not None:
            content_h = max(0.0, explicit_h - self.style.padding_vertical - self.style.border_vertical)

        self._resolve_box_model(content_w, content_h)

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    def _line_height(self) -> float:
        lh = self.style.get("line-height")
        if isinstance(lh, (int, float)):
            return float(lh)
        return 1.2

    def __repr__(self) -> str:
        preview = self.text[:30] + ("…" if len(self.text) > 30 else "")
        return f'TextNode("{preview}")'
