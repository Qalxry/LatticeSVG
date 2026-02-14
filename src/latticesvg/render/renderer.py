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
        d = self.render_to_drawing(node)
        d.save_svg(output_path)
        return d

    def render_to_drawing(self, node: "Node") -> dw.Drawing:
        """Render *node* to a ``drawsvg.Drawing`` without writing any file.

        Useful when you want to further manipulate the drawing — add
        watermarks, merge multiple layouts, etc.
        """
        bb = node.border_box
        self.drawing = dw.Drawing(bb.width, bb.height)
        self._render_node(node, offset_x=-bb.x, offset_y=-bb.y)
        return self.drawing

    def render_to_string(self, node: "Node") -> str:
        """Render *node* to an SVG string (no file I/O)."""
        return self.render_to_drawing(node).as_svg()

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

    def _render_node(
        self,
        node: "Node",
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        target: Optional[dw.Group] = None,
    ) -> None:
        """Recursively render *node* and its children.

        *target* is the drawsvg container to append into; defaults to
        ``self.drawing``.
        """
        from ..nodes.grid import GridContainer
        from ..nodes.text import TextNode
        from ..nodes.image import ImageNode
        from ..nodes.mpl import MplNode
        from ..nodes.svg import SVGNode

        assert self.drawing is not None
        if target is None:
            target = self.drawing

        bb = node.border_box
        x = bb.x + offset_x
        y = bb.y + offset_y

        # --- Clip path for overflow: hidden ---
        clip = None
        overflow = node.style.get("overflow")
        raw_radius = node.style.get("border-radius")
        radius = float(raw_radius) if isinstance(raw_radius, (int, float)) else 0.0

        if overflow == "hidden":
            clip = dw.ClipPath()
            clip_kwargs: dict = {}
            if radius > 0:
                clip_kwargs["rx"] = radius
                clip_kwargs["ry"] = radius
            clip.append(dw.Rectangle(x, y, bb.width, bb.height, **clip_kwargs))
            self.drawing.append(clip)

        # Create a group for this node
        group = dw.Group()
        if clip:
            group = dw.Group(clip_path=clip)

        # --- Border radius (already resolved above) ---

        # --- Background ---
        bg = node.style.get("background-color")
        if bg and bg != "none":
            opacity = node.style.get("opacity")
            op = float(opacity) if isinstance(opacity, (int, float)) else 1.0
            bg_kwargs: dict = dict(fill=bg, opacity=op)
            if radius > 0:
                bg_kwargs["rx"] = radius
                bg_kwargs["ry"] = radius
            rect = dw.Rectangle(x, y, bb.width, bb.height, **bg_kwargs)
            group.append(rect)

        # --- Border ---
        self._draw_borders(group, node, x, y, bb.width, bb.height, radius)

        # --- Content ---
        if isinstance(node, GridContainer):
            # Grid container: render children *into this group*
            # so that the background is painted first, then children on top.
            for child in node.children:
                self._render_node(child, offset_x=offset_x, offset_y=offset_y, target=group)
            target.append(group)
            return

        if isinstance(node, TextNode):
            self._render_text(group, node, offset_x, offset_y)
        elif isinstance(node, ImageNode):
            self._render_image(group, node, offset_x, offset_y)
        elif isinstance(node, MplNode):
            self._render_mpl(group, node, offset_x, offset_y)
        elif isinstance(node, SVGNode):
            self._render_svg_node(group, node, offset_x, offset_y)

        target.append(group)

    # -----------------------------------------------------------------
    # Border drawing
    # -----------------------------------------------------------------

    @staticmethod
    def _dash_array(style: str, width: float) -> str | None:
        """Return ``stroke-dasharray`` for the given border style, or *None*."""
        if style == "dashed":
            seg = max(3 * width, 4)
            gap = max(2 * width, 2)
            return f"{seg},{gap}"
        if style == "dotted":
            dot = max(width, 1)
            return f"{dot},{dot}"
        return None  # solid / none

    def _draw_borders(
        self,
        group: dw.Group,
        node: "Node",
        x: float,
        y: float,
        w: float,
        h: float,
        radius: float = 0.0,
    ) -> None:
        """Draw borders — as a rounded rect when *radius* > 0, else as lines."""
        s = node.style

        if radius > 0:
            # Unified rounded-rect border.
            # Pick the first available border side's properties.
            for side in ("top", "right", "bottom", "left"):
                bw = s._float(f"border-{side}-width")
                bc = s.get(f"border-{side}-color")
                bs = s.get(f"border-{side}-style") or "solid"
                if bw > 0 and bc and bc != "none":
                    kwargs: dict = dict(
                        fill="none",
                        stroke=bc,
                        stroke_width=bw,
                        rx=radius,
                        ry=radius,
                    )
                    da = self._dash_array(bs, bw)
                    if da:
                        kwargs["stroke_dasharray"] = da
                    group.append(dw.Rectangle(x, y, w, h, **kwargs))
                    break
            return

        # No radius — per-side lines (supports different widths/colors/styles).
        sides = [
            ("top", s.border_top_width, s.get("border-top-color"),
             s.get("border-top-style"),
             x, y, x + w, y),
            ("right", s.border_right_width, s.get("border-right-color"),
             s.get("border-right-style"),
             x + w, y, x + w, y + h),
            ("bottom", s.border_bottom_width, s.get("border-bottom-color"),
             s.get("border-bottom-style"),
             x, y + h, x + w, y + h),
            ("left", s.border_left_width, s.get("border-left-color"),
             s.get("border-left-style"),
             x, y, x, y + h),
        ]

        for name, width, color, bstyle, x1, y1, x2, y2 in sides:
            if width > 0 and color and color != "none":
                line_kw: dict = dict(
                    stroke=color,
                    stroke_width=width,
                )
                da = self._dash_array(bstyle or "solid", width)
                if da:
                    line_kw["stroke_dasharray"] = da
                group.append(dw.Line(x1, y1, x2, y2, **line_kw))

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
        y0 = cb.y + offset_y + getattr(node, '_text_y_offset', 0.0)

        font_size = node._font_size_int()
        color = node.style.get("color") or "#000000"

        # Prefer the resolved font-family from FreeType to match measurement
        font_family = getattr(node, '_resolved_font_family', None)
        if font_family is None:
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

        # Compute precise ascender for baseline positioning.
        # The baseline sits at: top_of_line + half_leading + ascender
        # where half_leading = (line_h - (ascender + |descender|)) / 2
        font_chain = getattr(node, '_resolved_font_chain', None)
        if font_chain:
            from ..text.font import FontManager as _FM
            fm = _FM.instance()
            fp0 = font_chain[0] if isinstance(font_chain, list) else font_chain
            _ascender = fm.ascender(fp0, font_size)
            _descender = fm.descender(fp0, font_size)  # negative
            em_height = _ascender - _descender  # total glyph height
            half_leading = (line_h - em_height) / 2.0
            baseline_offset = half_leading + _ascender
        else:
            baseline_offset = font_size * 0.85  # fallback approximation

        # Handle text-overflow: ellipsis
        text_overflow = node.style.get("text-overflow")
        overflow = node.style.get("overflow")
        ws = node.style.get("white-space") or "normal"

        for i, line in enumerate(node.lines):
            text = line.text
            lx = x0 + line.x_offset
            # Baseline position: top of line + precise ascender offset
            ly = y0 + i * line_h + baseline_offset

            if overflow == "hidden" and text_overflow == "ellipsis":
                # Check if this line is within visible area
                if (i + 1) * line_h > cb.height and i > 0:
                    # This line would overflow — skip it
                    break
                if i == len(node.lines) - 1 or (i + 1) * line_h >= cb.height:
                    # Potentially truncate with ellipsis
                    if line.width > cb.width:
                        # Use font chain for precise measurement
                        fp = ""
                        chain = getattr(node, '_resolved_font_chain', None)
                        if chain:
                            fp = chain[0] if isinstance(chain, list) else chain
                        text = self._truncate_with_ellipsis(text, cb.width, font_size, font_path=fp)

            # For pre/pre-wrap, use xml:space="preserve" so the SVG
            # viewer keeps leading/trailing/multiple whitespace intact.
            extra_attrs = {}
            if ws in ("pre", "pre-wrap"):
                extra_attrs["xml:space"] = "preserve"

            text_kwargs = dict(
                fill=color,
                font_family=font_family,
                font_weight=font_weight,
                font_style=font_style,
            )
            opacity = node.style.get("opacity")
            op = float(opacity) if isinstance(opacity, (int, float)) else 1.0
            if op < 1.0:
                text_kwargs["opacity"] = op

            t = dw.Text(
                text,
                font_size,
                lx,
                ly,
                **text_kwargs,
            )
            if extra_attrs:
                t.args.update(extra_attrs)
            group.append(t)

    @staticmethod
    def _truncate_with_ellipsis(
        text: str,
        max_width: float,
        font_size: float,
        font_path: str = "",
    ) -> str:
        """Truncate *text* so that it plus an ellipsis fits within *max_width*.

        Uses precise glyph measurement when *font_path* is available,
        falling back to an approximation otherwise.
        """
        from ..text.shaper import measure_text as _mt

        if font_path:
            ellipsis_w = _mt("…", font_path, int(font_size))
            target_w = max_width - ellipsis_w
            if target_w <= 0:
                return "…"
            # Binary-ish search: walk backwards from full text
            from ..text.font import FontManager as _FM
            fm = _FM.instance()
            accum = 0.0
            cut = 0
            for i, ch in enumerate(text):
                cw = fm.glyph_metrics(font_path, int(font_size), ch).advance_x
                if accum + cw > target_w:
                    break
                accum += cw
                cut = i + 1
            if cut < 1:
                return "…"
            return text[:cut] + "…"
        else:
            # Fallback: approximate
            approx_char_w = font_size * 0.6
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
            data_uri = node.get_base64()
            # Use data parameter for base64 data URIs
            img = dw.Image(
                x, y, ir.width, ir.height,
                data=data_uri,
            )
        except Exception:
            # Fallback to path if base64 fails
            img = dw.Image(
                x, y, ir.width, ir.height,
                path=node.src if isinstance(node.src, str) else None,
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

        # Strip the outer <svg> wrapper to avoid nested viewport issues
        inner = node.get_inner_svg()

        # Account for viewBox origin offset
        vb_x = getattr(node, "_vb_min_x", 0.0)
        vb_y = getattr(node, "_vb_min_y", 0.0)
        transform = f"translate({x},{y}) scale({sx},{sy})"
        if vb_x or vb_y:
            transform += f" translate({-vb_x},{-vb_y})"

        raw = dw.Raw(
            f'<g transform="{transform}">'
            f"{inner}"
            f"</g>"
        )
        group.append(raw)
