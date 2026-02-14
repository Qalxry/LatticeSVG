"""Math backend protocol and QuickJax implementation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Optional, Protocol, Tuple, runtime_checkable


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class SVGFragment:
    """Result of rendering a LaTeX expression to SVG."""

    svg_content: str
    """Inner SVG markup (without outer ``<svg>`` wrapper)."""

    width: float
    """Precise width in px."""

    height: float
    """Precise height in px."""

    depth: float = 0.0
    """Depth below baseline in px (for inline alignment)."""


# ---------------------------------------------------------------------------
# Backend protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class MathBackend(Protocol):
    """Abstract interface for math rendering backends."""

    def render(self, latex: str, font_size: float) -> SVGFragment:
        """Render *latex* at *font_size* and return an SVG fragment."""
        ...

    def available(self) -> bool:
        """Return ``True`` if this backend's dependencies are satisfied."""
        ...


# ---------------------------------------------------------------------------
# QuickJax backend (default)
# ---------------------------------------------------------------------------

# 1 ex ≈ x-height of the font.  MathJax uses 1 ex = font_size × 0.4315
# as its internal conversion factor for the default TeX font metrics.
_EX_RATIO = 0.4315


def _ex_to_px(ex_val: float, font_size: float) -> float:
    """Convert MathJax *ex* units to pixels at *font_size*."""
    return ex_val * font_size * _EX_RATIO


_RE_WIDTH = re.compile(r'width="([\d.]+)ex"')
_RE_HEIGHT = re.compile(r'height="([\d.]+)ex"')
_RE_VALIGN = re.compile(r'vertical-align:\s*([-\d.]+)ex')
_RE_VIEWBOX = re.compile(r'viewBox="([^"]+)"')
_RE_SVG_INNER = re.compile(r'<svg[^>]*>(.*)</svg>', re.DOTALL)


class QuickJaxBackend:
    """Render LaTeX math via QuickJax (in-process MathJax v4).

    QuickJax runs MathJax inside an embedded QuickJS engine — no
    Node.js, no subprocess, no network.  It is the recommended and
    default backend.
    """

    def __init__(self) -> None:
        self._renderer = None
        self._cache: Dict[Tuple[str, float, bool], SVGFragment] = {}

    def available(self) -> bool:
        try:
            import quickjax  # noqa: F401
            return True
        except ImportError:
            return False

    def render(
        self,
        latex: str,
        font_size: float,
        *,
        display: bool = False,
    ) -> SVGFragment:
        key = (latex, font_size, display)
        if key in self._cache:
            return self._cache[key]

        from quickjax import MathJaxRenderer

        if self._renderer is None:
            self._renderer = MathJaxRenderer()

        svg_str = self._renderer.render(latex, display=display)

        # --- Parse metrics from the SVG ---
        w_match = _RE_WIDTH.search(svg_str)
        h_match = _RE_HEIGHT.search(svg_str)
        va_match = _RE_VALIGN.search(svg_str)

        w_ex = float(w_match.group(1)) if w_match else 0.0
        h_ex = float(h_match.group(1)) if h_match else 0.0
        va_ex = float(va_match.group(1)) if va_match else 0.0

        width = _ex_to_px(w_ex, font_size)
        height = _ex_to_px(h_ex, font_size)
        depth = _ex_to_px(abs(va_ex), font_size)

        # --- Convert to embeddable fragment ---
        inner = self._to_embeddable(svg_str, width, height)

        frag = SVGFragment(
            svg_content=inner,
            width=width,
            height=height,
            depth=depth,
        )
        self._cache[key] = frag
        return frag

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_embeddable(svg: str, width_px: float, height_px: float) -> str:
        """Convert a standalone ``<svg>`` to an embeddable fragment.

        We keep the outer ``<svg>`` tag but rewrite its dimensions from
        ex units to px so it can be nested inside another SVG drawing
        with predictable sizing.
        """
        # Rewrite width/height to px
        svg = _RE_WIDTH.sub(f'width="{width_px:.2f}"', svg)
        svg = _RE_HEIGHT.sub(f'height="{height_px:.2f}"', svg)
        # Remove xmlns (will be inherited from parent SVG)
        svg = svg.replace(' xmlns="http://www.w3.org/2000/svg"', '')
        svg = svg.replace(" xmlns:xlink='http://www.w3.org/1999/xlink'", '')
        svg = svg.replace(' xmlns:xlink="http://www.w3.org/1999/xlink"', '')
        return svg
