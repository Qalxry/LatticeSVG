"""SVG renderer — converts the laid-out node tree to SVG (and optionally PNG)."""

from __future__ import annotations

import os
import tempfile
from typing import Optional, TYPE_CHECKING

import drawsvg as dw

if TYPE_CHECKING:
    from ..nodes.base import Node


class Renderer:
    """Render a laid-out node tree to SVG using *drawsvg*.

    Usage::

        renderer = Renderer()
        renderer.render(root_node, "output.svg")
        renderer.render_png(root_node, "output.png", scale=2)
    """

    def __init__(self) -> None:
        self.drawing: Optional[dw.Drawing] = None

    # =================================================================
    # Public API
    # =================================================================

    def render(self, node: "Node", output_path: str) -> dw.Drawing:
        """Render *node* and its descendants to an SVG file.

        Returns the ``drawsvg.Drawing`` instance for further use.
        """
        bb = node.border_box
        self.drawing = dw.Drawing(bb.width, bb.height)
        self._render_node(node, offset_x=-bb.x, offset_y=-bb.y)
        self.drawing.save_svg(output_path)
        return self.drawing

    def render_to_string(self, node: "Node") -> str:
        """Render *node* to an SVG string (no file I/O)."""
        bb = node.border_box
        self.drawing = dw.Drawing(bb.width, bb.height)
        self._render_node(node, offset_x=-bb.x, offset_y=-bb.y)
        return self.drawing.as_svg()

    def render_png(
        self,
        node: "Node",
        output_path: str,
        scale: float = 1.0,
    ) -> None:
        """Render to SVG, then convert to PNG via *cairosvg*."""
        try:
            import cairosvg  # type: ignore
        except ImportError:
            raise ImportError(
                "cairosvg is required for PNG output. "
                "Install it with: pip install cairosvg"
            )

        svg_string = self.render_to_string(node)
        bb = node.border_box
        cairosvg.svg2png(
            bytestring=svg_string.encode("utf-8"),
            write_to=output_path,
            output_width=int(bb.width * scale),
            output_height=int(bb.height * scale),
        )

    # =================================================================
    # Internal rendering dispatch
    # =================================================================

    def _render_node(self, node: "Node", offset_x: float = 0.0, offset_y: float = 0.0) -> None:
        """Recursively render *node* and its children."""
        from ..nodes.grid import GridContainer
        from ..nodes.text import TextNode
        from ..nodes.image import ImageNode
        from ..nodes.mpl import MplNode
        from ..nodes.svg import SVGNode

        assert self.drawing is not None

        bb = node.border_box
        x = bb.x + offset_x
        y = bb.y + offset_y

        # --- Clip path for overflow: hidden ---
        clip = None
        overflow = node.style.get("overflow")
        if overflow == "hidden":
            clip = dw.ClipPath()
            clip.append(dw.Rectangle(x, y, bb.width, bb.height))
            self.drawing.append(clip)

        # Create a group for this node
        group = dw.Group()
        if clip:
            group = dw.Group(clip_path=clip)

        # --- Background ---
        bg = node.style.get("background-color")
        if bg and bg != "none":
            opacity = node.style.get("opacity")
            op = float(opacity) if isinstance(opacity, (int, float)) else 1.0
            rect = dw.Rectangle(
                x, y, bb.width, bb.height,
                fill=bg,
                opacity=op,
            )
            group.append(rect)

        # --- Border ---
        self._draw_borders(group, node, x, y, bb.width, bb.height)

        # --- Content ---
        if isinstance(node, GridContainer):
            # Grid container: render children
            for child in node.children:
                self._render_node(child, offset_x=offset_x, offset_y=offset_y)
            self.drawing.append(group)
            return

        if isinstance(node, TextNode):
            self._render_text(group, node, offset_x, offset_y)
        elif isinstance(node, ImageNode):
            self._render_image(group, node, offset_x, offset_y)
        elif isinstance(node, MplNode):
            self._render_mpl(group, node, offset_x, offset_y)
        elif isinstance(node, SVGNode):
            self._render_svg_node(group, node, offset_x, offset_y)

        self.drawing.append(group)

    # -----------------------------------------------------------------
    # Border drawing
    # -----------------------------------------------------------------

    def _draw_borders(
        self,
        group: dw.Group,
        node: "Node",
        x: float,
        y: float,
        w: float,
        h: float,
    ) -> None:
        """Draw individual borders as lines."""
        s = node.style

        sides = [
            ("top", s.border_top_width, s.get("border-top-color"),
             x, y, x + w, y),
            ("right", s.border_right_width, s.get("border-right-color"),
             x + w, y, x + w, y + h),
            ("bottom", s.border_bottom_width, s.get("border-bottom-color"),
             x, y + h, x + w, y + h),
            ("left", s.border_left_width, s.get("border-left-color"),
             x, y, x, y + h),
        ]

        for name, width, color, x1, y1, x2, y2 in sides:
            if width > 0 and color and color != "none":
                line = dw.Line(
                    x1, y1, x2, y2,
                    stroke=color,
                    stroke_width=width,
                )
                group.append(line)

    # -----------------------------------------------------------------
    # Text rendering
    # -----------------------------------------------------------------

    def _render_text(
        self,
        group: dw.Group,
        node: "TextNode",
        offset_x: float,
        offset_y: float,
    ) -> None:
        """Render text lines."""
        cb = node.content_box
        x0 = cb.x + offset_x
        y0 = cb.y + offset_y

        font_size = node._font_size_int()
        color = node.style.get("color") or "#000000"
        font_family = node.style.get("font-family")
        if isinstance(font_family, list):
            font_family = ", ".join(font_family)
        font_weight = node.style.get("font-weight") or "normal"
        font_style = node.style.get("font-style") or "normal"

        lh_val = node._line_height()
        if lh_val <= 5.0:
            line_h = font_size * lh_val
        else:
            line_h = lh_val

        # Handle text-overflow: ellipsis
        text_overflow = node.style.get("text-overflow")
        overflow = node.style.get("overflow")

        for i, line in enumerate(node.lines):
            text = line.text
            lx = x0 + line.x_offset
            # Baseline position: top of line + ascender offset
            ly = y0 + i * line_h + font_size * 0.85  # approximate baseline

            if overflow == "hidden" and text_overflow == "ellipsis":
                # Check if this line is within visible area
                if (i + 1) * line_h > cb.height and i > 0:
                    # This line would overflow — skip it
                    break
                if i == len(node.lines) - 1 or (i + 1) * line_h >= cb.height:
                    # Potentially truncate with ellipsis
                    if line.width > cb.width:
                        text = self._truncate_with_ellipsis(text, cb.width, font_size)

            t = dw.Text(
                text,
                font_size,
                lx,
                ly,
                fill=color,
                font_family=font_family,
                font_weight=font_weight,
                font_style=font_style,
            )
            group.append(t)

    @staticmethod
    def _truncate_with_ellipsis(text: str, max_width: float, font_size: float) -> str:
        """Simple truncation — approximate chars that fit."""
        approx_char_w = font_size * 0.6  # rough average
        max_chars = int(max_width / approx_char_w) - 1
        if max_chars < 1:
            return "…"
        return text[:max_chars] + "…"

    # -----------------------------------------------------------------
    # Image rendering
    # -----------------------------------------------------------------

    def _render_image(
        self,
        group: dw.Group,
        node: "ImageNode",
        offset_x: float,
        offset_y: float,
    ) -> None:
        """Render an embedded image."""
        cb = node.content_box
        ir = getattr(node, "image_rect", None)
        if ir is None:
            return

        x = cb.x + offset_x + ir.x
        y = cb.y + offset_y + ir.y

        # Prefer base64 embedding for portability
        try:
            href = node.get_base64()
        except Exception:
            href = node.src

        img = dw.Image(
            x, y, ir.width, ir.height,
            href=href,
            embed=True,
        )
        group.append(img)

    # -----------------------------------------------------------------
    # Matplotlib rendering
    # -----------------------------------------------------------------

    def _render_mpl(
        self,
        group: dw.Group,
        node: "MplNode",
        offset_x: float,
        offset_y: float,
    ) -> None:
        """Embed a Matplotlib figure as an SVG fragment."""
        cb = node.content_box
        x = cb.x + offset_x
        y = cb.y + offset_y

        svg_fragment = node.get_svg_fragment()

        # Wrap in a positioned group
        raw = dw.Raw(
            f'<g transform="translate({x},{y})">{svg_fragment}</g>'
        )
        group.append(raw)

    # -----------------------------------------------------------------
    # SVG node rendering
    # -----------------------------------------------------------------

    def _render_svg_node(
        self,
        group: dw.Group,
        node: "SVGNode",
        offset_x: float,
        offset_y: float,
    ) -> None:
        """Embed external SVG content."""
        cb = node.content_box
        x = cb.x + offset_x
        y = cb.y + offset_y

        sx = getattr(node, "scale_x", 1.0)
        sy = getattr(node, "scale_y", 1.0)

        raw = dw.Raw(
            f'<g transform="translate({x},{y}) scale({sx},{sy})">'
            f"{node.svg_content}"
            f"</g>"
        )
        group.append(raw)
