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

    def _font_chain(self) -> list:
        """Return an ordered list of font paths (fallback chain).

        Supports comma-separated ``font-family`` values such as
        ``"Times New Roman, SimSun, serif"`` — each family is resolved
        independently so that characters missing in the primary font
        can be measured with a fallback.
        """
        fm = FontManager.instance()
        families = self._parse_font_families()
        weight = self.style.get("font-weight") or "normal"
        fstyle = self.style.get("font-style") or "normal"
        return fm.find_font_chain(families, weight=weight, style=fstyle)

    def _parse_font_families(self) -> list:
        """Parse the ``font-family`` value into a flat list of family names."""
        family = self.style.get("font-family")
        if family is None:
            return ["sans-serif"]
        if isinstance(family, list):
            result = []
            for f in family:
                if isinstance(f, str):
                    result.extend(
                        x.strip().strip('"').strip("'")
                        for x in f.split(",")
                    )
            return [x for x in result if x] or ["sans-serif"]
        if isinstance(family, str):
            return [
                x.strip().strip('"').strip("'")
                for x in family.split(",")
                if x.strip()
            ] or ["sans-serif"]
        return ["sans-serif"]

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
        font_chain = self._font_chain()
        if not font_chain:
            return (0.0, 0.0, 0.0)

        size = self._font_size_int()
        ws = self.style.get("white-space") or "normal"
        ow = self.style.get("overflow-wrap") or "normal"
        fm = FontManager.instance()

        min_w = get_min_content_width(self.text, font_chain, size, ws, fm=fm)
        max_w = get_max_content_width(self.text, font_chain, size, ws, fm=fm)

        # Intrinsic height at max-content width (single line for normal)
        lines = break_lines(self.text, max_w + 1, font_chain, size, ws, ow, fm=fm)
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
        font_chain = self._font_chain()
        size = self._font_size_int()
        ws = self.style.get("white-space") or "normal"
        ow = self.style.get("overflow-wrap") or "normal"
        fm = FontManager.instance()

        content_w = self._content_available_width(constraints)
        if content_w is None:
            content_w = constraints.available_width or 800.0

        # Store resolved font info for rendering
        self._resolved_font_chain = font_chain
        if font_chain:
            names = []
            for fp in font_chain:
                n = fm.font_family_name(fp)
                if n and n not in names:
                    names.append(n)
            self._resolved_font_family = ", ".join(names) if names else None
        else:
            self._resolved_font_family = None

        if not font_chain:
            # No font available — empty box
            self._resolve_box_model(content_w, 0.0)
            self.lines = []
            return

        # Break lines
        self.lines = break_lines(self.text, content_w, font_chain, size, ws, ow, fm=fm)

        # Align
        text_align = self.style.get("text-align") or "left"
        self.lines = align_lines(self.lines, content_w, text_align)

        # Compute content height
        lh = self._line_height()
        _, text_block_h = compute_text_block_size(self.lines, lh, float(size))
        content_h = text_block_h

        # Handle explicit width/height
        explicit_w = self._resolve_width(constraints)
        if explicit_w is not None:
            content_w = max(0.0, explicit_w - self.style.padding_horizontal - self.style.border_horizontal)
        explicit_h = self._resolve_height(constraints)
        if explicit_h is not None:
            content_h = max(0.0, explicit_h - self.style.padding_vertical - self.style.border_vertical)

        # Stretch: if the grid solver provided available_height and there
        # is no explicit height, expand content_h to fill the cell.
        if explicit_h is None and constraints.available_height is not None:
            stretched_h = max(0.0, constraints.available_height
                              - self.style.padding_vertical
                              - self.style.border_vertical)
            if stretched_h > content_h:
                content_h = stretched_h

        # Vertical text alignment inside the content box.
        # Mimics CSS ``display: flex; align-items: center/end``.
        display = self.style.get("display")
        align_items = self.style.get("align-items")
        self._text_y_offset = 0.0
        if display in ("flex", "grid") and content_h > text_block_h:
            if align_items == "center":
                self._text_y_offset = (content_h - text_block_h) / 2.0
            elif align_items == "end":
                self._text_y_offset = content_h - text_block_h

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
