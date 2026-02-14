"""SVGNode — embed external SVG content."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from .base import LayoutConstraints, Node, Rect


class SVGNode(Node):
    """Node that embeds raw SVG content (from a string or file).

    The SVG's ``viewBox`` or ``width``/``height`` attributes are used to
    determine its intrinsic size.  During rendering the content is scaled
    to fit the allocated space.

    Parameters
    ----------
    svg : str
        SVG source:
        - File path (when is_file=True)
        - URL starting with 'http://' or 'https://'
        - Raw SVG string
    style : dict, optional
        Style properties
    parent : Node, optional
        Parent node
    is_file : bool, optional
        If True, treat svg as a file path. Default False.
    """

    def __init__(
        self,
        svg: str,
        *,
        style: Optional[Dict[str, Any]] = None,
        parent: Optional[Node] = None,
        is_file: bool = False,
    ) -> None:
        super().__init__(style=style, parent=parent)
        
        # Load SVG content from various sources
        if is_file:
            with open(svg, "r", encoding="utf-8") as f:
                self.svg_content: str = f.read()
        elif svg.startswith('http://') or svg.startswith('https://'):
            # Load from URL
            import urllib.request
            with urllib.request.urlopen(svg) as response:
                self.svg_content = response.read().decode('utf-8')
        else:
            self.svg_content = svg
        
        self._intrinsic: Optional[Tuple[float, float]] = None
        self._vb_min_x: float = 0.0
        self._vb_min_y: float = 0.0

    # -----------------------------------------------------------------
    # Intrinsic size parsing
    # -----------------------------------------------------------------

    def _parse_intrinsic(self) -> Tuple[float, float]:
        if self._intrinsic is not None:
            return self._intrinsic

        w, h = 300.0, 150.0  # default

        # Try viewBox first
        vb = re.search(r'viewBox\s*=\s*"([^"]+)"', self.svg_content)
        if vb:
            parts = vb.group(1).split()
            if len(parts) >= 4:
                self._vb_min_x = float(parts[0])
                self._vb_min_y = float(parts[1])
                w = float(parts[2])
                h = float(parts[3])
                self._intrinsic = (w, h)
                return self._intrinsic

        # Try width/height attributes
        wm = re.search(r'\bwidth\s*=\s*"(\d+(?:\.\d+)?)"', self.svg_content)
        hm = re.search(r'\bheight\s*=\s*"(\d+(?:\.\d+)?)"', self.svg_content)
        if wm:
            w = float(wm.group(1))
        if hm:
            h = float(hm.group(1))

        self._intrinsic = (w, h)
        return self._intrinsic

    @property
    def intrinsic_width(self) -> float:
        return self._parse_intrinsic()[0]

    @property
    def intrinsic_height(self) -> float:
        return self._parse_intrinsic()[1]

    # -----------------------------------------------------------------
    # Measurement
    # -----------------------------------------------------------------

    def measure(self, constraints: LayoutConstraints) -> Tuple[float, float, float]:
        iw, ih = self._parse_intrinsic()
        ph = self.style.padding_horizontal + self.style.border_horizontal
        pv = self.style.padding_vertical + self.style.border_vertical
        return (iw + ph, iw + ph, ih + pv)

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------

    def layout(self, constraints: LayoutConstraints) -> None:
        iw, ih = self._parse_intrinsic()

        content_w = self._content_available_width(constraints)
        if content_w is None:
            content_w = iw

        explicit_w = self._resolve_width(constraints)
        if explicit_w is not None:
            content_w = max(0.0, explicit_w - self.style.padding_horizontal - self.style.border_horizontal)

        explicit_h = self._resolve_height(constraints)
        if explicit_h is not None:
            content_h = max(0.0, explicit_h - self.style.padding_vertical - self.style.border_vertical)
        else:
            # Maintain aspect ratio
            if iw > 0:
                content_h = ih * (content_w / iw)
            else:
                content_h = ih

        self._resolve_box_model(content_w, content_h)

        # Scale factor for rendering
        self.scale_x = content_w / iw if iw > 0 else 1.0
        self.scale_y = content_h / ih if ih > 0 else 1.0

    # -----------------------------------------------------------------
    # SVG content helpers
    # -----------------------------------------------------------------

    def get_inner_svg(self) -> str:
        """Return SVG content with the outer ``<svg>`` wrapper stripped.

        This is used for embedding inside another SVG document.
        Presentation attributes (fill, stroke, etc.) from the outer
        ``<svg>`` element are preserved by wrapping inner content in
        a ``<g>`` that carries those attributes forward.
        """
        content = self.svg_content
        # Remove XML declaration
        content = re.sub(r'<\?xml[^?]*\?>\s*', '', content)
        # Remove DOCTYPE
        content = re.sub(r'<!DOCTYPE[^>]*>\s*', '', content)
        # Remove HTML comments (license headers etc.)
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        # Extract content inside <svg ...>...</svg>
        m = re.search(r'<svg([^>]*)>(.*)</svg>', content, re.DOTALL)
        if m:
            svg_attrs = m.group(1)
            inner = m.group(2).strip()
            # Extract presentation attributes from <svg> to carry forward
            pres_attrs = []
            for attr in ('fill', 'stroke', 'stroke-width', 'stroke-linecap',
                         'stroke-linejoin', 'opacity', 'color'):
                match = re.search(rf'\b{attr}\s*=\s*"([^"]*)"', svg_attrs)
                if match:
                    val = match.group(1)
                    # Replace currentColor with a usable default
                    if val == 'currentColor':
                        val = '#000000'
                    pres_attrs.append(f'{attr}="{val}"')
            if pres_attrs:
                attrs_str = ' '.join(pres_attrs)
                return f'<g {attrs_str}>{inner}</g>'
            return inner
        return content.strip()

    def __repr__(self) -> str:
        return f"SVGNode({self.intrinsic_width:.0f}x{self.intrinsic_height:.0f})"
