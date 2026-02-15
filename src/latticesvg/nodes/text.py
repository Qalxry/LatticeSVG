"""TextNode — a leaf node that renders text with automatic line breaking."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List

from .base import LayoutConstraints, Node, Rect
from ..text.font import FontManager
from ..text.shaper import (
    Line,
    RichLine,
    SpanFragment,
    align_lines,
    align_lines_rich,
    break_lines,
    break_lines_rich,
    compute_text_block_size,
    compute_rich_block_size,
    get_max_content_width,
    get_max_content_width_rich,
    get_min_content_width,
    get_min_content_width_rich,
    measure_text,
)


class TextNode(Node):
    """A node that displays text content.

    The text is measured using FreeType (or Pillow fallback) and
    automatically wrapped according to the ``white-space`` property.

    When *markup* is ``"html"`` or ``"markdown"``, inline tags/syntax
    are parsed to produce styled spans (bold, italic, colour, …).
    """

    def __init__(
        self,
        text: str,
        style: Optional[Dict[str, Any]] = None,
        parent: Optional[Node] = None,
        markup: str = "none",
    ) -> None:
        super().__init__(style=style, parent=parent)
        self.text: str = text
        self.markup: str = markup
        self.lines: List[Line] = []  # populated after layout (plain mode)

        # Rich-text fields (populated when markup != "none")
        self._spans: Optional[list] = None
        self._rich_lines: Optional[List[RichLine]] = None

        if markup in ("html", "markdown"):
            from ..markup.parser import parse_markup
            self._spans = parse_markup(text, markup)


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

    def _spacing_values(self) -> Tuple[float, float]:
        """Return ``(letter_spacing, word_spacing)`` as floats.

        The CSS value ``"normal"`` maps to ``0.0``.
        """
        ls = self.style.get("letter-spacing")
        ws = self.style.get("word-spacing")
        ls_val = 0.0 if (ls is None or ls == "normal") else float(ls)
        ws_val = 0.0 if (ws is None or ws == "normal") else float(ws)
        return (ls_val, ws_val)

    def _hyphens_value(self) -> str:
        """Return the resolved ``hyphens`` value (``none``, ``manual``, or ``auto``)."""
        val = self.style.get("hyphens")
        if val in ("auto", "manual"):
            return val
        return "none"

    def _lang_value(self) -> str:
        """Return the resolved ``lang`` value for hyphenation dictionaries."""
        val = self.style.get("lang")
        return val if isinstance(val, str) and val else "en"

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
        ls_val, ws_val = self._spacing_values()
        hyph = self._hyphens_value()
        lang_v = self._lang_value()

        if self._spans is not None:
            # Rich text measurement
            math_be = self._math_backend()
            min_w = get_min_content_width_rich(self._spans, font_chain, size, ws, fm=fm, math_backend=math_be,
                                               letter_spacing=ls_val, word_spacing=ws_val,
                                               hyphens=hyph, lang=lang_v)
            max_w = get_max_content_width_rich(self._spans, font_chain, size, ws, fm=fm, math_backend=math_be,
                                               letter_spacing=ls_val, word_spacing=ws_val)
            lines = break_lines_rich(self._spans, max_w + 1, font_chain, size, ws, ow, fm=fm, math_backend=math_be,
                                     letter_spacing=ls_val, word_spacing=ws_val,
                                     hyphens=hyph, lang=lang_v)
            lh = self._line_height()
            _, h = compute_rich_block_size(lines, lh, float(size))
        else:
            min_w = get_min_content_width(self.text, font_chain, size, ws, fm=fm,
                                          letter_spacing=ls_val, word_spacing=ws_val,
                                          hyphens=hyph, lang=lang_v)
            max_w = get_max_content_width(self.text, font_chain, size, ws, fm=fm,
                                          letter_spacing=ls_val, word_spacing=ws_val)

            # Intrinsic height at max-content width (single line for normal)
            lines = break_lines(self.text, max_w + 1, font_chain, size, ws, ow, fm=fm,
                                letter_spacing=ls_val, word_spacing=ws_val,
                                hyphens=hyph, lang=lang_v)
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
            # Append a generic family as ultimate fallback so that
            # devices without the embedded font still avoid serif.
            _GENERICS = {"sans-serif", "serif", "monospace", "cursive",
                         "fantasy", "system-ui"}
            user_families = self._parse_font_families()
            generic = next(
                (f for f in user_families if f.lower() in _GENERICS),
                "sans-serif",
            )
            if generic not in names:
                names.append(generic)
            self._resolved_font_family = ", ".join(names) if names else None
        else:
            self._resolved_font_family = None

        if not font_chain:
            # No font available — empty box
            self._resolve_box_model(content_w, 0.0)
            self.lines = []
            self._rich_lines = None
            return

        if self._spans is not None:
            # ---- Rich text layout ----
            math_be = self._math_backend()
            ls_val, ws_val = self._spacing_values()
            hyph = self._hyphens_value()
            lang_v = self._lang_value()
            self._rich_lines = break_lines_rich(
                self._spans, content_w, font_chain, size, ws, ow,
                fm=fm, math_backend=math_be,
                letter_spacing=ls_val, word_spacing=ws_val,
                hyphens=hyph, lang=lang_v,
            )
            text_align = self.style.get("text-align") or "left"
            self._rich_lines = align_lines_rich(self._rich_lines, content_w, text_align)
            lh = self._line_height()
            _, text_block_h = compute_rich_block_size(self._rich_lines, lh, float(size))
            content_h = text_block_h
            self.lines = []  # unused in rich mode
        else:
            # ---- Plain text layout (original path) ----
            self._rich_lines = None
            ls_val, ws_val = self._spacing_values()
            hyph = self._hyphens_value()
            lang_v = self._lang_value()
            self.lines = break_lines(self.text, content_w, font_chain, size, ws, ow, fm=fm,
                                     letter_spacing=ls_val, word_spacing=ws_val,
                                     hyphens=hyph, lang=lang_v)
            text_align = self.style.get("text-align") or "left"
            self.lines = align_lines(self.lines, content_w, text_align)
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

    def _math_backend(self):
        """Return the active math backend, or *None* if unavailable."""
        try:
            from ..math import get_backend
            return get_backend(None)
        except Exception:
            return None

    def __repr__(self) -> str:
        preview = self.text[:30] + ("…" if len(self.text) > 30 else "")
        return f'TextNode("{preview}")'
