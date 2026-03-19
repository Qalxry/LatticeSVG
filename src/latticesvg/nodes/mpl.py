"""MplNode — adapter for embedding Matplotlib figures."""

from __future__ import annotations

import io
from typing import Any, Dict, List, Optional, Tuple

from .base import LayoutConstraints, Node, Rect


class MplNode(Node):
    """Node that embeds a Matplotlib figure as an SVG fragment.

    The figure is rendered to an in-memory SVG buffer during the render
    phase, so all Matplotlib customisation should be done *before*
    creating this node.

    Parameters
    ----------
    figure :
        A ``matplotlib.figure.Figure`` instance.
    style :
        Optional CSS-like style dictionary.
    parent :
        Optional parent node.
    auto_mpl_font :
        When ``True`` (default), the node reads the inherited
        ``font-family`` CSS property and configures matplotlib's font
        settings via ``rc_context`` so that text rendered inside the
        figure uses the same font family as surrounding
        :class:`TextNode` elements.
    tight_layout :
        When ``True`` (default), ``figure.tight_layout()`` is called
        inside the font ``rc_context`` before exporting, so that text
        metrics match the final font.  Set to ``False`` if you manage
        layout yourself or use ``constrained_layout``.
    """

    def __init__(
        self,
        figure: Any,  # matplotlib.figure.Figure
        style: Optional[Dict[str, Any]] = None,
        parent: Optional[Node] = None,
        auto_mpl_font: bool = True,
        tight_layout: bool = True,
    ) -> None:
        super().__init__(style=style, parent=parent)
        self.figure = figure
        self._auto_mpl_font = auto_mpl_font
        self._tight_layout = tight_layout
        self._svg_cache: Optional[str] = None

    # -----------------------------------------------------------------
    # Intrinsic size from figure
    # -----------------------------------------------------------------

    # Matplotlib's SVG backend always uses 72 DPI for its coordinate
    # system, regardless of the figure's screen DPI.  All sizing must
    # use this value so that the embedded SVG fragment fills the
    # allocated space exactly.
    _SVG_DPI: float = 72.0

    def _fig_size_px(self) -> Tuple[float, float]:
        """Return figure size in SVG coordinate units (72 DPI)."""
        w_in, h_in = self.figure.get_size_inches()
        return (w_in * self._SVG_DPI, h_in * self._SVG_DPI)

    # -----------------------------------------------------------------
    # Measurement
    # -----------------------------------------------------------------

    def measure(self, constraints: LayoutConstraints) -> Tuple[float, float, float]:
        fw, fh = self._fig_size_px()
        ph = self.style.padding_horizontal + self.style.border_horizontal
        pv = self.style.padding_vertical + self.style.border_vertical
        return (fw + ph, fw + ph, fh + pv)

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------

    def layout(self, constraints: LayoutConstraints) -> None:
        fw, fh = self._fig_size_px()

        content_w = self._content_available_width(constraints)
        if content_w is None:
            content_w = fw

        explicit_w = self._resolve_width(constraints)
        if explicit_w is not None:
            content_w = max(0.0, explicit_w - self.style.padding_horizontal - self.style.border_horizontal)

        explicit_h = self._resolve_height(constraints)
        if explicit_h is not None:
            content_h = max(0.0, explicit_h - self.style.padding_vertical - self.style.border_vertical)
        else:
            # Maintain aspect ratio
            if fw > 0:
                content_h = fh * (content_w / fw)
            else:
                content_h = fh

        # Resize the figure so the SVG output coordinate system
        # exactly matches the allocated content area.
        self.figure.set_size_inches(
            content_w / self._SVG_DPI,
            content_h / self._SVG_DPI,
        )

        # Invalidate cached SVG since the figure was resized
        self._svg_cache = None

        self._resolve_box_model(content_w, content_h)

    # -----------------------------------------------------------------
    # SVG export
    # -----------------------------------------------------------------

    def _resolve_mpl_font_rc(self) -> Tuple[Dict[str, Any], List[str]]:
        """Build matplotlib rcParams overrides and collect font paths.

        Returns ``(rc_dict, font_paths)`` where *font_paths* is a list
        of filesystem paths that must be registered with matplotlib's
        ``fontManager`` before the rc overrides take effect.

        Delegates to :func:`latticesvg.text._build_mpl_rc`.
        """
        from ..text import _build_mpl_rc

        css_font = self.style.get("font-family") or "sans-serif"
        weight = self.style.get("font-weight") or "normal"
        fstyle = self.style.get("font-style") or "normal"
        return _build_mpl_rc(css_font, weight=weight, style=fstyle)

    @staticmethod
    def _register_fonts_with_mpl(font_paths: List[str]) -> None:
        """Ensure each font path is known to matplotlib's fontManager.

        Delegates to :func:`latticesvg.text._register_mpl_fonts`.
        """
        from ..text import _register_mpl_fonts

        _register_mpl_fonts(font_paths)

    def get_svg_fragment(self) -> str:
        """Export the figure to an SVG string (cached).

        When *auto_mpl_font* is enabled the inherited ``font-family``
        CSS property is translated into matplotlib ``rcParams`` so that
        text inside the figure uses matching fonts.  ``svg.fonttype`` is
        always set to ``"path"`` so that glyphs are converted to vector
        paths for cross-platform consistency.
        """
        if self._svg_cache is None:
            import matplotlib as mpl

            rc_overrides: Dict[str, Any] = {"svg.fonttype": "path"}
            if self._auto_mpl_font:
                font_rc, font_paths = self._resolve_mpl_font_rc()
                self._register_fonts_with_mpl(font_paths)
                rc_overrides.update(font_rc)

            buf = io.BytesIO()
            with mpl.rc_context(rc_overrides):
                if self._tight_layout:
                    try:
                        self.figure.tight_layout()
                    except Exception:
                        pass
                self.figure.savefig(buf, format="svg", transparent=True)
            buf.seek(0)
            svg = buf.read().decode("utf-8")
            # Strip the XML declaration and outer <svg> tags for embedding
            self._svg_cache = self._strip_svg_wrapper(svg)
        return self._svg_cache

    @staticmethod
    def _strip_svg_wrapper(svg: str) -> str:
        """Remove XML declaration and outer ``<svg>...</svg>`` tags."""
        import re

        # Remove XML declaration
        svg = re.sub(r"<\?xml[^?]*\?>", "", svg)
        # Remove doctype
        svg = re.sub(r"<!DOCTYPE[^>]*>", "", svg)
        # Extract content inside <svg ...>...</svg>
        m = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.DOTALL)
        if m:
            return m.group(1).strip()
        return svg.strip()

    def __repr__(self) -> str:
        w, h = self._fig_size_px()
        return f"MplNode({w:.0f}x{h:.0f}px)"
