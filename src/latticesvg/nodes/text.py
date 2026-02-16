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
    # Vertical text support
    Column,
    VerticalRun,
    align_columns,
    break_columns,
    compute_vertical_block_size,
    get_max_content_height,
    get_min_content_height,
    measure_text_vertical,
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

        The result is cached on the node because it depends only on
        style properties that do not change after construction.
        """
        cached = getattr(self, '_cached_font_chain', None)
        if cached is not None:
            return cached
        fm = FontManager.instance()
        families = self._parse_font_families()
        weight = self.style.get("font-weight") or "normal"
        fstyle = self.style.get("font-style") or "normal"
        result = fm.find_font_chain(families, weight=weight, style=fstyle)
        self._cached_font_chain = result
        return result

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

    def _writing_mode(self) -> str:
        """Return the resolved ``writing-mode`` value."""
        val = self.style.get("writing-mode")
        if val in ("vertical-rl", "vertical-lr", "sideways-rl", "sideways-lr"):
            return val
        return "horizontal-tb"

    def _text_orientation(self) -> str:
        """Return the resolved ``text-orientation`` value."""
        val = self.style.get("text-orientation")
        if val in ("upright", "sideways"):
            return val
        return "mixed"

    def _text_combine_upright(self) -> str:
        """Return the resolved ``text-combine-upright`` value."""
        val = self.style.get("text-combine-upright")
        if isinstance(val, str):
            val = val.strip().lower()
            if val == "all":
                return "all"
            if val.startswith("digits"):
                return val  # e.g. "digits 2", "digits 3", "digits 4"
        return "none"

    def _is_vertical(self) -> bool:
        """Return True when writing-mode is vertical or sideways."""
        return self._writing_mode() != "horizontal-tb"

    def _is_sideways_mode(self) -> bool:
        """Return True when writing-mode is sideways-rl or sideways-lr."""
        return self._writing_mode() in ("sideways-rl", "sideways-lr")

    # -----------------------------------------------------------------
    # Measurement
    # -----------------------------------------------------------------

    def measure(self, constraints: LayoutConstraints) -> Tuple[float, float, float]:
        """Return ``(min_content_width, max_content_width, intrinsic_height)``.

        For vertical/sideways writing modes the axes are swapped
        internally so that the grid solver always receives values in
        the physical (horizontal/vertical) coordinate system.

        The result is cached because it depends only on text content
        and style properties, not on *constraints*.
        """
        cached = getattr(self, '_measure_cache', None)
        if cached is not None:
            return cached
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
        wm = self._writing_mode()

        # Add padding + border
        ph = self.style.padding_horizontal + self.style.border_horizontal
        pv = self.style.padding_vertical + self.style.border_vertical

        # -- sideways-rl / sideways-lr --
        # Shape horizontally, then swap width ↔ height.
        if wm in ("sideways-rl", "sideways-lr"):
            if self._spans is not None:
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
                text_w, text_h = compute_rich_block_size(lines, lh, float(size))
            else:
                min_w = get_min_content_width(self.text, font_chain, size, ws, fm=fm,
                                              letter_spacing=ls_val, word_spacing=ws_val,
                                              hyphens=hyph, lang=lang_v)
                max_w = get_max_content_width(self.text, font_chain, size, ws, fm=fm,
                                              letter_spacing=ls_val, word_spacing=ws_val)
                lines = break_lines(self.text, max_w + 1, font_chain, size, ws, ow, fm=fm,
                                    letter_spacing=ls_val, word_spacing=ws_val,
                                    hyphens=hyph, lang=lang_v)
                lh = self._line_height()
                text_w, text_h = compute_text_block_size(lines, lh, float(size))
            # Swap axes: horizontal text_h becomes physical width,
            # horizontal text_w becomes physical height.
            result = (text_h + ph, text_h + ph, max_w + pv)
            self._measure_cache = result
            return result

        # -- vertical-rl / vertical-lr --
        if wm in ("vertical-rl", "vertical-lr"):
            orient = self._text_orientation()
            min_h = get_min_content_height(self.text, font_chain, size, ws, fm=fm,
                                           orientation=orient,
                                           letter_spacing=ls_val,
                                           word_spacing=ws_val)
            max_h = get_max_content_height(self.text, font_chain, size, ws, fm=fm,
                                           orientation=orient,
                                           letter_spacing=ls_val,
                                           word_spacing=ws_val)
            # Intrinsic: one column at max height
            cols = break_columns(self.text, max_h + 1, font_chain, size, ws, ow, fm=fm,
                                 orientation=orient, letter_spacing=ls_val,
                                 word_spacing=ws_val)
            lh = self._line_height()
            block_w, block_h = compute_vertical_block_size(cols, lh, float(size))
            # In physical coords: width = block_w, height = block_h (= max_h)
            result = (block_w + ph, block_w + ph, max_h + pv)
            self._measure_cache = result
            return result

        # -- horizontal-tb (default) --
        if self._spans is not None:
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
            lines = break_lines(self.text, max_w + 1, font_chain, size, ws, ow, fm=fm,
                                letter_spacing=ls_val, word_spacing=ws_val,
                                hyphens=hyph, lang=lang_v)
            lh = self._line_height()
            _, h = compute_text_block_size(lines, lh, float(size))

        result = (min_w + ph, max_w + ph, h + pv)
        self._measure_cache = result
        return result

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------

    def layout(self, constraints: LayoutConstraints) -> None:
        font_chain = self._font_chain()
        size = self._font_size_int()
        ws = self.style.get("white-space") or "normal"
        ow = self.style.get("overflow-wrap") or "normal"
        fm = FontManager.instance()
        wm = self._writing_mode()

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
            self._resolve_box_model(content_w, 0.0)
            self.lines = []
            self._rich_lines = None
            self._columns = None
            return

        # Store writing mode for renderer
        self._resolved_writing_mode = wm
        self._resolved_text_orientation = self._text_orientation()

        ls_val, ws_val = self._spacing_values()
        hyph = self._hyphens_value()
        lang_v = self._lang_value()
        lh = self._line_height()

        # ---- sideways-rl / sideways-lr ----
        # Shape text horizontally, then swap axes for the box model.
        if wm in ("sideways-rl", "sideways-lr"):
            self._columns = None
            # The physical height of the node becomes the horizontal
            # available width for line breaking.
            content_h_available = constraints.available_height
            if content_h_available is not None:
                shaping_width = max(0.0, content_h_available
                                    - self.style.padding_vertical
                                    - self.style.border_vertical)
            else:
                shaping_width = content_w  # fallback

            if self._spans is not None:
                math_be = self._math_backend()
                self._rich_lines = break_lines_rich(
                    self._spans, shaping_width, font_chain, size, ws, ow,
                    fm=fm, math_backend=math_be,
                    letter_spacing=ls_val, word_spacing=ws_val,
                    hyphens=hyph, lang=lang_v,
                )
                text_align = self.style.get("text-align") or "left"
                self._rich_lines = align_lines_rich(self._rich_lines, shaping_width, text_align)
                text_w, text_h = compute_rich_block_size(self._rich_lines, lh, float(size))
                self.lines = []
            else:
                self._rich_lines = None
                self.lines = break_lines(self.text, shaping_width, font_chain, size, ws, ow, fm=fm,
                                         letter_spacing=ls_val, word_spacing=ws_val,
                                         hyphens=hyph, lang=lang_v)
                text_align = self.style.get("text-align") or "left"
                self.lines = align_lines(self.lines, shaping_width, text_align)
                text_w, text_h = compute_text_block_size(self.lines, lh, float(size))

            # Swap: physical_w = text_h (number of lines × line_height),
            #        physical_h = shaping_width (text runs top to bottom).
            content_w_final = text_h
            content_h_final = text_w if text_w > 0 else shaping_width

            # Store the shaping_width so renderer can reconstruct
            self._sideways_shaping_width = shaping_width
            self._text_block_w = text_w
            self._text_block_h = text_h

            explicit_w = self._resolve_width(constraints)
            if explicit_w is not None:
                content_w_final = max(0.0, explicit_w - self.style.padding_horizontal - self.style.border_horizontal)
            explicit_h = self._resolve_height(constraints)
            if explicit_h is not None:
                content_h_final = max(0.0, explicit_h - self.style.padding_vertical - self.style.border_vertical)

            self._text_y_offset = 0.0
            self._resolve_box_model(content_w_final, content_h_final)
            return

        # ---- vertical-rl / vertical-lr ----
        if wm in ("vertical-rl", "vertical-lr"):
            self._rich_lines = None
            self.lines = []
            orient = self._resolved_text_orientation
            tcu = self._text_combine_upright()
            self._resolved_text_combine_upright = tcu

            # In vertical mode, the available_height constrains the
            # block-direction (top-to-bottom per column).
            content_h_available = constraints.available_height
            if content_h_available is not None:
                available_col_h = max(0.0, content_h_available
                                      - self.style.padding_vertical
                                      - self.style.border_vertical)
            else:
                available_col_h = 1e9  # unlimited

            self._columns = break_columns(
                self.text, available_col_h, font_chain, size, ws, ow,
                fm=fm, orientation=orient, letter_spacing=ls_val,
                word_spacing=ws_val,
                text_combine_upright=tcu,
            )
            text_align = self.style.get("text-align") or "left"
            self._columns = align_columns(self._columns, available_col_h, text_align)
            block_w, block_h = compute_vertical_block_size(self._columns, lh, float(size))

            content_w_final = block_w
            content_h_final = block_h

            explicit_w = self._resolve_width(constraints)
            if explicit_w is not None:
                content_w_final = max(0.0, explicit_w - self.style.padding_horizontal - self.style.border_horizontal)
            explicit_h = self._resolve_height(constraints)
            if explicit_h is not None:
                content_h_final = max(0.0, explicit_h - self.style.padding_vertical - self.style.border_vertical)

            # Stretch height
            if explicit_h is None and constraints.available_height is not None:
                stretched_h = max(0.0, constraints.available_height
                                  - self.style.padding_vertical
                                  - self.style.border_vertical)
                if stretched_h > content_h_final:
                    content_h_final = stretched_h

            self._text_y_offset = 0.0
            self._resolve_box_model(content_w_final, content_h_final)
            return

        # ---- horizontal-tb (default) ----
        self._columns = None

        if self._spans is not None:
            math_be = self._math_backend()
            self._rich_lines = break_lines_rich(
                self._spans, content_w, font_chain, size, ws, ow,
                fm=fm, math_backend=math_be,
                letter_spacing=ls_val, word_spacing=ws_val,
                hyphens=hyph, lang=lang_v,
            )
            text_align = self.style.get("text-align") or "left"
            self._rich_lines = align_lines_rich(self._rich_lines, content_w, text_align)
            _, text_block_h = compute_rich_block_size(self._rich_lines, lh, float(size))
            content_h = text_block_h
            self.lines = []
        else:
            self._rich_lines = None
            self.lines = break_lines(self.text, content_w, font_chain, size, ws, ow, fm=fm,
                                     letter_spacing=ls_val, word_spacing=ws_val,
                                     hyphens=hyph, lang=lang_v)
            text_align = self.style.get("text-align") or "left"
            self.lines = align_lines(self.lines, content_w, text_align)
            _, text_block_h = compute_text_block_size(self.lines, lh, float(size))
            content_h = text_block_h

        explicit_w = self._resolve_width(constraints)
        if explicit_w is not None:
            content_w = max(0.0, explicit_w - self.style.padding_horizontal - self.style.border_horizontal)
        explicit_h = self._resolve_height(constraints)
        if explicit_h is not None:
            content_h = max(0.0, explicit_h - self.style.padding_vertical - self.style.border_vertical)

        if explicit_h is None and constraints.available_height is not None:
            stretched_h = max(0.0, constraints.available_height
                              - self.style.padding_vertical
                              - self.style.border_vertical)
            if stretched_h > content_h:
                content_h = stretched_h

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
        """Return the resolved line-height in absolute px."""
        from ..style.parser import LineHeightMultiplier
        lh = self.style.get("line-height")
        fs = self._font_size_int()
        if isinstance(lh, LineHeightMultiplier):
            return lh.resolve(fs)
        if isinstance(lh, (int, float)):
            return float(lh)
        return fs * 1.2

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
