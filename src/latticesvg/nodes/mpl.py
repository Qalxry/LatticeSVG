"""MplNode — adapter for embedding Matplotlib figures."""

from __future__ import annotations

import io
from typing import Any, Dict, Optional, Tuple

from .base import LayoutConstraints, Node, Rect


class MplNode(Node):
    """Node that embeds a Matplotlib figure as an SVG fragment.

    The figure is rendered to an in-memory SVG buffer during the render
    phase, so all Matplotlib customisation should be done *before*
    creating this node.
    """

    def __init__(
        self,
        figure: Any,  # matplotlib.figure.Figure
        style: Optional[Dict[str, Any]] = None,
        parent: Optional[Node] = None,
    ) -> None:
        super().__init__(style=style, parent=parent)
        self.figure = figure
        self._svg_cache: Optional[str] = None

    # -----------------------------------------------------------------
    # Intrinsic size from figure
    # -----------------------------------------------------------------

    def _fig_size_px(self) -> Tuple[float, float]:
        """Return figure size in pixels."""
        w_in, h_in = self.figure.get_size_inches()
        dpi = self.figure.get_dpi()
        return (w_in * dpi, h_in * dpi)

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

        # Resize the figure to match the allocated space
        dpi = self.figure.get_dpi()
        self.figure.set_size_inches(content_w / dpi, content_h / dpi)

        self._resolve_box_model(content_w, content_h)

    # -----------------------------------------------------------------
    # SVG export
    # -----------------------------------------------------------------

    def get_svg_fragment(self) -> str:
        """Export the figure to an SVG string (cached)."""
        if self._svg_cache is None:
            buf = io.BytesIO()
            self.figure.savefig(buf, format="svg", bbox_inches="tight", transparent=True)
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
