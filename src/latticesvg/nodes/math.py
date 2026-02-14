"""MathNode — a leaf node that renders LaTeX math as SVG."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .base import LayoutConstraints, Node, Rect


class MathNode(Node):
    """Node that renders a LaTeX math expression to SVG.

    By default the QuickJax backend (in-process MathJax v4) is used.
    A different backend can be selected per-node or globally via
    :func:`latticesvg.math.set_default_backend`.

    Usage::

        formula = MathNode(r"E = mc^2", style={"font-size": "20px"})
    """

    def __init__(
        self,
        latex: str,
        *,
        style: Optional[Dict[str, Any]] = None,
        backend: Optional[str] = None,
        display: bool = True,
        parent: Optional[Node] = None,
    ) -> None:
        super().__init__(style=style or {}, parent=parent)
        self.latex: str = latex
        self.display: bool = display
        self._backend_name: Optional[str] = backend
        self._svg_cache: Optional[object] = None  # SVGFragment
        self.scale_x: float = 1.0
        self.scale_y: float = 1.0

    # ------------------------------------------------------------------
    # Backend access
    # ------------------------------------------------------------------

    def _get_backend(self):
        """Return the active math backend instance."""
        from ..math import get_backend
        return get_backend(self._backend_name)

    def _get_fragment(self):
        """Render (or return cached) SVG fragment."""
        if self._svg_cache is not None:
            return self._svg_cache
        backend = self._get_backend()
        font_size = self._font_size()
        frag = backend.render(self.latex, font_size, display=self.display)
        self._svg_cache = frag
        return frag

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _font_size(self) -> float:
        fs = self.style.get("font-size")
        if isinstance(fs, (int, float)):
            return max(1.0, float(fs))
        return 16.0

    # ------------------------------------------------------------------
    # Measurement
    # ------------------------------------------------------------------

    def measure(self, constraints: LayoutConstraints) -> Tuple[float, float, float]:
        frag = self._get_fragment()
        ph = self.style.padding_horizontal + self.style.border_horizontal
        pv = self.style.padding_vertical + self.style.border_vertical
        return (frag.width + ph, frag.width + ph, frag.height + pv)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def layout(self, constraints: LayoutConstraints) -> None:
        frag = self._get_fragment()

        content_w = self._content_available_width(constraints)
        if content_w is None:
            content_w = frag.width
        else:
            # Don't stretch beyond natural size; only shrink if constrained
            content_w = min(content_w, frag.width)

        explicit_w = self._resolve_width(constraints)
        if explicit_w is not None:
            content_w = max(0.0, explicit_w
                           - self.style.padding_horizontal
                           - self.style.border_horizontal)

        explicit_h = self._resolve_height(constraints)
        if explicit_h is not None:
            content_h = max(0.0, explicit_h
                           - self.style.padding_vertical
                           - self.style.border_vertical)
        else:
            # Maintain aspect ratio
            if frag.width > 0:
                content_h = frag.height * (content_w / frag.width)
            else:
                content_h = frag.height

        # Compute scale factors for the SVG fragment
        self.scale_x = content_w / frag.width if frag.width > 0 else 1.0
        self.scale_y = content_h / frag.height if frag.height > 0 else 1.0

        # Invalidate cache if size changed (re-render at new size)
        self._svg_cache = None
        self._svg_cache = self._get_fragment()

        self._resolve_box_model(content_w, content_h)

    # ------------------------------------------------------------------
    # SVG export
    # ------------------------------------------------------------------

    def get_svg_fragment(self) -> str:
        """Return the rendered SVG content for embedding."""
        frag = self._get_fragment()
        return frag.svg_content

    def __repr__(self) -> str:
        preview = self.latex[:30] + ("…" if len(self.latex) > 30 else "")
        return f'MathNode("{preview}")'
