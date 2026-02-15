"""SVG renderer — converts the laid-out node tree to SVG (and optionally PNG)."""

from __future__ import annotations

import math
import os
import tempfile
from typing import Optional, Tuple, TYPE_CHECKING

import drawsvg as dw

from ..style.parser import (
    ClipCircle, ClipEllipse, ClipPolygon, ClipInset, _Percentage,
    LinearGradientValue, RadialGradientValue,
)

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

    def render(
        self,
        node: "Node",
        output_path: str,
        *,
        embed_fonts: bool = False,
    ) -> dw.Drawing:
        """Render *node* and its descendants to an SVG file.

        Parameters
        ----------
        embed_fonts:
            If *True*, subset and embed all used fonts as WOFF2
            ``@font-face`` rules inside the SVG, making it fully
            self-contained.  Requires the ``fonttools`` package.

        Returns the ``drawsvg.Drawing`` instance for further use.
        """
        d = self.render_to_drawing(node, embed_fonts=embed_fonts)
        d.save_svg(output_path)
        return d

    def render_to_drawing(
        self,
        node: "Node",
        *,
        embed_fonts: bool = False,
    ) -> dw.Drawing:
        """Render *node* to a ``drawsvg.Drawing`` without writing any file.

        Useful when you want to further manipulate the drawing — add
        watermarks, merge multiple layouts, etc.

        Parameters
        ----------
        embed_fonts:
            If *True*, subset and embed all used fonts as WOFF2
            ``@font-face`` rules.
        """
        bb = node.border_box
        self.drawing = dw.Drawing(bb.width, bb.height)
        self._render_node(node, offset_x=-bb.x, offset_y=-bb.y)
        if embed_fonts:
            from ..text.embed import embed_fonts as _embed
            _embed(self.drawing, node)
        return self.drawing

    def render_to_string(
        self,
        node: "Node",
        *,
        embed_fonts: bool = False,
    ) -> str:
        """Render *node* to an SVG string (no file I/O)."""
        return self.render_to_drawing(node, embed_fonts=embed_fonts).as_svg()

    def render_png(
        self,
        node: "Node",
        output_path: str,
        scale: float = 1.0,
        *,
        embed_fonts: bool = False,
    ) -> None:
        """Render to SVG, then convert to PNG via *cairosvg*.

        Parameters
        ----------
        embed_fonts:
            If *True*, embed subsetted fonts into the intermediate SVG
            before rasterising.  This ensures *cairosvg* uses the exact
            same glyphs that were measured during layout.
        """
        try:
            import cairosvg  # type: ignore
        except ImportError:
            raise ImportError(
                "cairosvg is required for PNG output. "
                "Install it with: pip install cairosvg"
            )

        svg_string = self.render_to_string(node, embed_fonts=embed_fonts)
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
        from ..nodes.math import MathNode

        assert self.drawing is not None
        if target is None:
            target = self.drawing

        bb = node.border_box
        x = bb.x + offset_x
        y = bb.y + offset_y

        # --- Resolve four-corner border-radius ---
        radii = self._clamp_radii(
            *node.style.border_radii, bb.width, bb.height
        )
        any_radius = any(r > 0 for r in radii)
        uniform_radius = radii[0] == radii[1] == radii[2] == radii[3]

        # --- Clip path for overflow: hidden ---
        clip = None
        overflow = node.style.get("overflow")

        if overflow == "hidden":
            clip = dw.ClipPath()
            if any_radius and not uniform_radius:
                clip.append(self._rounded_rect_path(
                    x, y, bb.width, bb.height, *radii))
            elif any_radius:
                clip.append(dw.Rectangle(
                    x, y, bb.width, bb.height,
                    rx=radii[0], ry=radii[0]))
            else:
                clip.append(dw.Rectangle(x, y, bb.width, bb.height))
            self.drawing.append(clip)

        # --- CSS clip-path property ---
        css_clip = None
        clip_path_val = node.style.get("clip-path")
        if clip_path_val and clip_path_val != "none" and not isinstance(clip_path_val, str):
            css_clip = self._make_clip_path(clip_path_val, x, y, bb.width, bb.height)
            if css_clip is not None:
                self.drawing.append(css_clip)

        # Create a group for this node
        # If both overflow clip and CSS clip-path exist, nest groups.
        if clip and css_clip:
            outer = dw.Group(clip_path=clip)
            group = dw.Group(clip_path=css_clip)
        elif clip:
            outer = None
            group = dw.Group(clip_path=clip)
        elif css_clip:
            outer = None
            group = dw.Group(clip_path=css_clip)
        else:
            outer = None
            group = dw.Group()

        # --- Background ---
        bg = node.style.get("background-image")
        if not bg or bg == "none":
            bg = node.style.get("background-color")
        if bg and bg != "none":
            opacity = node.style.get("opacity")
            op = float(opacity) if isinstance(opacity, (int, float)) else 1.0
            # Resolve gradient or solid color
            if isinstance(bg, LinearGradientValue):
                fill = self._create_linear_gradient(bg, x, y, bb.width, bb.height)
            elif isinstance(bg, RadialGradientValue):
                fill = self._create_radial_gradient(bg, x, y, bb.width, bb.height)
            else:
                fill = bg
            bg_kwargs: dict = dict(fill=fill, opacity=op)
            if any_radius and not uniform_radius:
                group.append(self._rounded_rect_path(
                    x, y, bb.width, bb.height, *radii, **bg_kwargs))
            elif any_radius:
                bg_kwargs["rx"] = radii[0]
                bg_kwargs["ry"] = radii[0]
                group.append(dw.Rectangle(x, y, bb.width, bb.height, **bg_kwargs))
            else:
                group.append(dw.Rectangle(x, y, bb.width, bb.height, **bg_kwargs))

        # --- Border ---
        self._draw_borders(group, node, x, y, bb.width, bb.height, radii)

        # --- Content ---
        if isinstance(node, GridContainer):
            for child in node.children:
                self._render_node(child, offset_x=offset_x, offset_y=offset_y, target=group)
            if outer:
                outer.append(group)
                target.append(outer)
            else:
                target.append(group)
            self._draw_outline(target, node, x, y, bb.width, bb.height, radii)
            return

        if isinstance(node, TextNode):
            self._render_text(group, node, offset_x, offset_y)
        elif isinstance(node, ImageNode):
            self._render_image(group, node, offset_x, offset_y)
        elif isinstance(node, MplNode):
            self._render_mpl(group, node, offset_x, offset_y)
        elif isinstance(node, SVGNode):
            self._render_svg_node(group, node, offset_x, offset_y)
        elif isinstance(node, MathNode):
            self._render_math(group, node, offset_x, offset_y)

        if outer:
            outer.append(group)
            target.append(outer)
        else:
            target.append(group)
        self._draw_outline(target, node, x, y, bb.width, bb.height, radii)

    # -----------------------------------------------------------------
    # Geometry helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _clamp_radii(
        r_tl: float, r_tr: float, r_br: float, r_bl: float,
        w: float, h: float,
    ) -> Tuple[float, float, float, float]:
        """Clamp four corner radii so adjacent pairs don't exceed side length.

        Implements the CSS *corner overlap* algorithm (§5.3 of CSS
        Backgrounds and Borders Level 3).
        """
        if w <= 0 or h <= 0:
            return (0.0, 0.0, 0.0, 0.0)
        f = 1.0
        for sum_r, side in [
            (r_tl + r_tr, w),   # top edge
            (r_br + r_bl, w),   # bottom edge
            (r_tl + r_bl, h),   # left edge
            (r_tr + r_br, h),   # right edge
        ]:
            if sum_r > 0:
                f = min(f, side / sum_r)
        if f < 1.0:
            return (r_tl * f, r_tr * f, r_br * f, r_bl * f)
        return (r_tl, r_tr, r_br, r_bl)

    @staticmethod
    def _rounded_rect_path(
        x: float, y: float, w: float, h: float,
        r_tl: float, r_tr: float, r_br: float, r_bl: float,
        **kwargs,
    ) -> dw.Path:
        """Return a ``dw.Path`` drawing a rectangle with independent corner radii.

        Parameters are the four corner radii (top-left, top-right,
        bottom-right, bottom-left).  Extra *kwargs* (fill, stroke, …)
        are forwarded to ``dw.Path``.
        """
        p = dw.Path(**kwargs)
        # Start at top-left corner, after the TL arc
        p.M(x + r_tl, y)
        # Top edge → TR arc
        p.L(x + w - r_tr, y)
        if r_tr > 0:
            p.A(r_tr, r_tr, 0, 0, 1, x + w, y + r_tr)
        else:
            p.L(x + w, y)
        # Right edge → BR arc
        p.L(x + w, y + h - r_br)
        if r_br > 0:
            p.A(r_br, r_br, 0, 0, 1, x + w - r_br, y + h)
        else:
            p.L(x + w, y + h)
        # Bottom edge → BL arc
        p.L(x + r_bl, y + h)
        if r_bl > 0:
            p.A(r_bl, r_bl, 0, 0, 1, x, y + h - r_bl)
        else:
            p.L(x, y + h)
        # Left edge → TL arc
        p.L(x, y + r_tl)
        if r_tl > 0:
            p.A(r_tl, r_tl, 0, 0, 1, x + r_tl, y)
        p.Z()
        return p

    # -----------------------------------------------------------------
    # Gradient helpers  (P2-4)
    # -----------------------------------------------------------------

    def _create_linear_gradient(
        self,
        grad: LinearGradientValue,
        x: float,
        y: float,
        w: float,
        h: float,
    ) -> dw.LinearGradient:
        """Create a ``dw.LinearGradient`` from a parsed :class:`LinearGradientValue`.

        Converts the CSS angle convention to SVG ``(x1, y1, x2, y2)``
        coordinates in ``userSpaceOnUse`` units.
        """
        # CSS gradient angles: 0deg = to top, 90deg = to right, 180deg = to bottom
        # Convert to radians — CSS angle 0° points up, measuring clockwise
        angle_rad = math.radians(grad.angle)
        # Unit vector in CSS direction (0° = up = (0, -1), 90° = right = (1, 0))
        dx = math.sin(angle_rad)
        dy = -math.cos(angle_rad)
        # Project onto the box — the gradient line passes through center and
        # extends to the corners of the bounding box.
        cx = x + w / 2
        cy = y + h / 2
        # Half-length of the gradient line (corner-to-corner projection)
        half_len = abs(dx) * w / 2 + abs(dy) * h / 2
        x1 = cx - dx * half_len
        y1 = cy - dy * half_len
        x2 = cx + dx * half_len
        y2 = cy + dy * half_len

        svg_grad = dw.LinearGradient(x1, y1, x2, y2)
        for stop in grad.stops:
            pos = stop.position if stop.position is not None else 0
            svg_grad.add_stop(pos, stop.color)
        return svg_grad

    def _create_radial_gradient(
        self,
        grad: RadialGradientValue,
        x: float,
        y: float,
        w: float,
        h: float,
    ) -> dw.RadialGradient:
        """Create a ``dw.RadialGradient`` from a parsed :class:`RadialGradientValue`."""
        cx = x + w * grad.cx
        cy = y + h * grad.cy
        # Radius: use the larger half-dimension for circle,
        # or average for ellipse
        if grad.shape == "circle":
            r = max(w, h) / 2
        else:
            r = (w + h) / 4  # reasonable default for ellipse
        svg_grad = dw.RadialGradient(cx, cy, r)
        for stop in grad.stops:
            pos = stop.position if stop.position is not None else 0
            svg_grad.add_stop(pos, stop.color)
        return svg_grad

    # -----------------------------------------------------------------
    # clip-path helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _resolve_clip_value(val, ref: float) -> float:
        """Resolve a clip-path value (float or _Percentage) against *ref*."""
        if isinstance(val, _Percentage):
            return val.resolve(ref)
        if isinstance(val, (int, float)):
            return float(val)
        return 0.0

    def _make_clip_path(
        self,
        clip_val,
        x: float,
        y: float,
        w: float,
        h: float,
    ) -> Optional[dw.ClipPath]:
        """Create a ``dw.ClipPath`` element from a parsed clip-path value."""
        rv = self._resolve_clip_value  # shorthand

        if isinstance(clip_val, ClipCircle):
            # CSS spec: circle percentage resolves against
            # sqrt(w² + h²) / sqrt(2)
            ref_r = math.hypot(w, h) / math.sqrt(2)
            r = rv(clip_val.radius, ref_r)
            cx = x + rv(clip_val.cx, w)
            cy = y + rv(clip_val.cy, h)
            cp = dw.ClipPath()
            cp.append(dw.Circle(cx, cy, r))
            return cp

        if isinstance(clip_val, ClipEllipse):
            rx = rv(clip_val.rx, w)
            ry = rv(clip_val.ry, h)
            cx = x + rv(clip_val.cx, w)
            cy = y + rv(clip_val.cy, h)
            cp = dw.ClipPath()
            cp.append(dw.Ellipse(cx, cy, rx, ry))
            return cp

        if isinstance(clip_val, ClipPolygon):
            if len(clip_val.points) < 3:
                return None
            p = dw.Path()
            for i, (px, py) in enumerate(clip_val.points):
                abs_x = x + rv(px, w)
                abs_y = y + rv(py, h)
                if i == 0:
                    p.M(abs_x, abs_y)
                else:
                    p.L(abs_x, abs_y)
            p.Z()
            cp = dw.ClipPath()
            cp.append(p)
            return cp

        if isinstance(clip_val, ClipInset):
            it = rv(clip_val.top, h)
            ir = rv(clip_val.right, w)
            ib = rv(clip_val.bottom, h)
            il = rv(clip_val.left, w)
            ix = x + il
            iy = y + it
            iw = w - il - ir
            ih = h - it - ib
            if iw <= 0 or ih <= 0:
                return None
            cp = dw.ClipPath()
            if clip_val.round_radii:
                rr = tuple(
                    rv(r, min(iw, ih)) for r in clip_val.round_radii
                )
                rr = self._clamp_radii(*rr, iw, ih)
                if any(r > 0 for r in rr):
                    cp.append(self._rounded_rect_path(
                        ix, iy, iw, ih, *rr))
                else:
                    cp.append(dw.Rectangle(ix, iy, iw, ih))
            else:
                cp.append(dw.Rectangle(ix, iy, iw, ih))
            return cp

        return None

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
        radii: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0),
    ) -> None:
        """Draw borders — as a rounded path/rect when radii > 0, else as lines."""
        s = node.style

        radii = self._clamp_radii(*radii, w, h)
        any_radius = any(r > 0 for r in radii)
        uniform = radii[0] == radii[1] == radii[2] == radii[3]

        if any_radius:
            # Rounded border — pick the first available border side's properties.
            for side in ("top", "right", "bottom", "left"):
                bw = s._float(f"border-{side}-width")
                bc = s.get(f"border-{side}-color")
                bs = s.get(f"border-{side}-style") or "solid"
                if bw > 0 and bc and bc != "none":
                    kwargs: dict = dict(
                        fill="none",
                        stroke=bc,
                        stroke_width=bw,
                    )
                    da = self._dash_array(bs, bw)
                    if da:
                        kwargs["stroke_dasharray"] = da
                    if uniform:
                        kwargs["rx"] = radii[0]
                        kwargs["ry"] = radii[0]
                        group.append(dw.Rectangle(x, y, w, h, **kwargs))
                    else:
                        group.append(self._rounded_rect_path(
                            x, y, w, h, *radii, **kwargs))
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

    def _draw_outline(
        self,
        group: dw.Group,
        node: "Node",
        x: float,
        y: float,
        w: float,
        h: float,
        radii: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0),
    ) -> None:
        """Draw CSS outline (outside the border-box, doesn't affect layout)."""
        s = node.style
        ow = s._float("outline-width")
        oc = s.get("outline-color") or s.get("color") or "#000000"
        os_ = s.get("outline-style") or "none"
        offset = s._float("outline-offset")

        if ow <= 0 or os_ == "none" or oc == "none":
            return

        total_offset = offset + ow / 2.0
        ox = x - total_offset
        oy = y - total_offset
        ow_rect = w + 2 * total_offset
        oh_rect = h + 2 * total_offset

        any_radius = any(r > 0 for r in radii)
        outline_radii = tuple(
            max(0.0, r + offset + ow / 2.0) if r > 0 else 0.0
            for r in radii
        )
        any_outline_r = any(r > 0 for r in outline_radii)
        uniform_outline = outline_radii[0] == outline_radii[1] == outline_radii[2] == outline_radii[3]

        kwargs: dict = dict(
            fill="none",
            stroke=oc,
            stroke_width=ow,
        )
        da = self._dash_array(os_, ow)
        if da:
            kwargs["stroke_dasharray"] = da

        if any_outline_r and not uniform_outline:
            group.append(self._rounded_rect_path(
                ox, oy, ow_rect, oh_rect, *outline_radii, **kwargs))
        elif any_outline_r:
            kwargs["rx"] = outline_radii[0]
            kwargs["ry"] = outline_radii[0]
            group.append(dw.Rectangle(ox, oy, ow_rect, oh_rect, **kwargs))
        else:
            group.append(dw.Rectangle(ox, oy, ow_rect, oh_rect, **kwargs))

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
        """Render text lines (plain or rich)."""
        rich_lines = getattr(node, "_rich_lines", None)
        if rich_lines:
            self._render_rich_text(group, node, offset_x, offset_y)
        else:
            self._render_plain_text(group, node, offset_x, offset_y)

    def _render_plain_text(
        self,
        group: dw.Group,
        node: "TextNode",
        offset_x: float,
        offset_y: float,
    ) -> None:
        """Render plain (non-markup) text lines."""
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
        text_decoration = node.style.get("text-decoration") or "none"

        lh_val = node._line_height()
        if lh_val <= 5.0:
            line_h = font_size * lh_val
        else:
            line_h = lh_val

        # Compute precise ascender for baseline positioning.
        font_chain = getattr(node, '_resolved_font_chain', None)
        if font_chain:
            from ..text.font import FontManager as _FM
            fm = _FM.instance()
            fp0 = font_chain[0] if isinstance(font_chain, list) else font_chain
            _ascender = fm.ascender(fp0, font_size)
            _descender = fm.descender(fp0, font_size)  # negative
            em_height = _ascender - _descender
            half_leading = (line_h - em_height) / 2.0
            baseline_offset = half_leading + _ascender
        else:
            fp0 = ""
            fm = None
            baseline_offset = font_size * 0.85

        # Handle text-overflow: ellipsis
        text_overflow = node.style.get("text-overflow")
        overflow = node.style.get("overflow")
        ws = node.style.get("white-space") or "normal"

        # letter-spacing / word-spacing SVG attributes
        ls_raw = node.style.get("letter-spacing")
        ws_raw = node.style.get("word-spacing")
        ls_px = 0.0 if (ls_raw is None or ls_raw == "normal") else float(ls_raw)
        ws_px = 0.0 if (ws_raw is None or ws_raw == "normal") else float(ws_raw)

        for i, line in enumerate(node.lines):
            text = line.text
            lx = x0 + line.x_offset
            ly = y0 + i * line_h + baseline_offset

            if overflow == "hidden" and text_overflow == "ellipsis":
                if (i + 1) * line_h > cb.height and i > 0:
                    break
                if i == len(node.lines) - 1 or (i + 1) * line_h >= cb.height:
                    if line.width > cb.width:
                        _fp = ""
                        chain = getattr(node, '_resolved_font_chain', None)
                        if chain:
                            _fp = chain[0] if isinstance(chain, list) else chain
                        text = self._truncate_with_ellipsis(text, cb.width, font_size, font_path=_fp)

            extra_attrs: dict = {}
            if ws in ("pre", "pre-wrap"):
                extra_attrs["xml:space"] = "preserve"

            text_kwargs = dict(
                fill=color,
                font_family=font_family,
                font_weight=font_weight,
                font_style=font_style,
            )
            if text_decoration and text_decoration != "none":
                text_kwargs["text_decoration"] = text_decoration
            if ls_px:
                extra_attrs["letter-spacing"] = f"{ls_px}"
            if ws_px:
                extra_attrs["word-spacing"] = f"{ws_px}"

            opacity = node.style.get("opacity")
            op = float(opacity) if isinstance(opacity, (int, float)) else 1.0
            if op < 1.0:
                text_kwargs["opacity"] = op

            # --- Justify rendering ---
            if getattr(line, 'justified', False) and line.word_spacing_justify > 0:
                if ' ' in text:
                    # Western text: use SVG word-spacing attribute.
                    # word_spacing_justify is the *extra* gap per space;
                    # SVG word-spacing adds to the glyph advance of U+0020,
                    # so the total matches the shaper's computation exactly.
                    justify_ws = ws_px + line.word_spacing_justify
                    j_attrs = dict(extra_attrs)
                    j_attrs["word-spacing"] = f"{justify_ws}"
                    t = dw.Text(text, font_size, lx, ly, **text_kwargs)
                    t.args.update(j_attrs)
                    group.append(t)
                elif text:
                    # CJK text (no spaces): per-character <text> elements.
                    # Each <text> has one char so SVG letter-spacing has
                    # no effect — add it manually to the advance.
                    cur_x = lx
                    n_chars = len(text)
                    for ci, ch in enumerate(text):
                        t = dw.Text(ch, font_size, cur_x, ly, **text_kwargs)
                        if extra_attrs:
                            t.args.update(extra_attrs)
                        group.append(t)
                        if ci < n_chars - 1:
                            if fm and fp0:
                                ch_w = fm.glyph_metrics(fp0, font_size, ch).advance_x
                            else:
                                ch_w = font_size * 0.6
                            cur_x += ch_w + line.word_spacing_justify + ls_px
                else:
                    t = dw.Text(text, font_size, lx, ly, **text_kwargs)
                    if extra_attrs:
                        t.args.update(extra_attrs)
                    group.append(t)
                continue

            # --- Normal rendering: single <text> per line ---
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

    def _render_rich_text(
        self,
        group: dw.Group,
        node: "TextNode",
        offset_x: float,
        offset_y: float,
    ) -> None:
        """Render rich (multi-span) text lines using ``<tspan>``."""
        from ..markup.parser import TextSpan as _TS

        cb = node.content_box
        x0 = cb.x + offset_x
        y0 = cb.y + offset_y + getattr(node, '_text_y_offset', 0.0)

        font_size = node._font_size_int()
        base_color = node.style.get("color") or "#000000"
        base_family = getattr(node, '_resolved_font_family', None)
        if base_family is None:
            base_family = node.style.get("font-family")
        if isinstance(base_family, list):
            base_family = ", ".join(base_family)
        base_weight = node.style.get("font-weight") or "normal"
        base_style = node.style.get("font-style") or "normal"

        lh_val = node._line_height()
        line_h = font_size * lh_val if lh_val <= 5.0 else lh_val

        # Baseline offset
        font_chain = getattr(node, '_resolved_font_chain', None)
        if font_chain:
            from ..text.font import FontManager as _FM
            fm = _FM.instance()
            fp0 = font_chain[0] if isinstance(font_chain, list) else font_chain
            _ascender = fm.ascender(fp0, font_size)
            _descender = fm.descender(fp0, font_size)
            em_height = _ascender - _descender
            half_leading = (line_h - em_height) / 2.0
            baseline_offset = half_leading + _ascender
        else:
            baseline_offset = font_size * 0.85

        spans = node._spans or []
        rich_lines = node._rich_lines or []

        # letter-spacing / word-spacing SVG attributes
        ls_raw = node.style.get("letter-spacing")
        ws_raw = node.style.get("word-spacing")
        ls_px = 0.0 if (ls_raw is None or ls_raw == "normal") else float(ls_raw)
        ws_px = 0.0 if (ws_raw is None or ws_raw == "normal") else float(ws_raw)

        opacity = node.style.get("opacity")
        op = float(opacity) if isinstance(opacity, (int, float)) else 1.0

        for i, rline in enumerate(rich_lines):
            lx = x0 + rline.x_offset
            ly = y0 + i * line_h + baseline_offset

            # Phase 1 — Merge consecutive text fragments that share the
            # same span_index into unified runs.  This keeps spaces
            # inside a single <text> element so that text-decoration
            # (e.g. strikethrough) and background-color (e.g. <code>)
            # span continuously across word boundaries.
            # Math fragments remain as individual items.
            runs: list = []  # list of dicts
            cur_x = lx
            is_cjk_j = getattr(rline, 'justified', False) and getattr(rline, '_cjk_justify', False)
            n_frags = len(rline.fragments)
            for fi, frag in enumerate(rline.fragments):
                if frag.svg_fragment is not None:
                    runs.append({
                        "kind": "math", "x": cur_x, "frag": frag,
                    })
                    cur_x += frag.width
                    continue
                # Text fragment — try to merge with the previous run
                # (skip merging for CJK justify so each char keeps its own x)
                if (runs
                        and runs[-1]["kind"] == "text"
                        and runs[-1]["span_index"] == frag.span_index
                        and not is_cjk_j):
                    runs[-1]["text"] += frag.text
                    runs[-1]["width"] += frag.width
                else:
                    runs.append({
                        "kind": "text",
                        "x": cur_x,
                        "text": frag.text,
                        "width": frag.width,
                        "span_index": frag.span_index,
                        "font_size": frag.font_size,
                    })
                cur_x += frag.width
                # Justify: add extra gap at word boundaries
                if (getattr(rline, 'justified', False)
                        and rline.word_spacing_justify > 0
                        and frag.svg_fragment is None):
                    if not frag.text.strip():
                        # Western text: space fragment = word boundary
                        cur_x += rline.word_spacing_justify
                    elif is_cjk_j and fi < n_frags - 1:
                        # CJK text: distribute gap after every
                        # non-last text fragment
                        cur_x += rline.word_spacing_justify

            # Phase 2 — Render each run with absolute positioning.
            for run in runs:
                if run["kind"] == "math":
                    frag = run["frag"]
                    svg_frag = frag.svg_fragment
                    math_y = ly - svg_frag.height + getattr(svg_frag, "depth", 0.0)
                    raw = dw.Raw(
                        f'<g transform="translate({run["x"]},{math_y})">'
                        f"{svg_frag.svg_content}"
                        f"</g>"
                    )
                    group.append(raw)
                    continue

                text = run["text"]
                # Whitespace-only runs between *different* spans:
                # skip rendering — their width is already baked into
                # the absolute x positions.
                if not text.strip():
                    continue

                span_src = (spans[run["span_index"]]
                            if run["span_index"] < len(spans) else None)

                # Resolve styling for this run
                color = base_color
                family = base_family
                weight = base_weight
                f_style = base_style
                fsize: float = font_size
                text_y = ly
                td = "none"

                if span_src:
                    color = span_src.color or base_color
                    if span_src.font_weight:
                        weight = span_src.font_weight
                    if span_src.font_style:
                        f_style = span_src.font_style
                    if span_src.font_family:
                        # Resolve to FreeType family names so that
                        # the name matches @font-face declarations.
                        from ..text.font import FontManager as _FM2
                        _fm = _FM2.instance()
                        _sfam = [f.strip().strip('"').strip("'")
                                 for f in span_src.font_family.split(",")
                                 if f.strip()]
                        _schain = _fm.find_font_chain(
                            _sfam,
                            weight=span_src.font_weight or "normal",
                            style=span_src.font_style or "normal",
                        )
                        if _schain:
                            _snames = []
                            for _fp in _schain:
                                _n = _fm.font_family_name(_fp)
                                if _n and _n not in _snames:
                                    _snames.append(_n)
                            _GENS = {"sans-serif", "serif", "monospace",
                                     "cursive", "fantasy", "system-ui"}
                            _gen = next(
                                (f for f in _sfam if f.lower() in _GENS),
                                "sans-serif",
                            )
                            if _gen not in _snames:
                                _snames.append(_gen)
                            family = ", ".join(_snames) if _snames else span_src.font_family
                        else:
                            family = span_src.font_family
                    if span_src.font_size is not None:
                        fsize = span_src.font_size
                    if span_src.baseline_shift:
                        if span_src.baseline_shift == "super":
                            text_y = ly - font_size * 0.35
                            if span_src.font_size is None:
                                fsize = font_size * 0.7
                        elif span_src.baseline_shift == "sub":
                            text_y = ly + font_size * 0.2
                            if span_src.font_size is None:
                                fsize = font_size * 0.7
                    if span_src.text_decoration and span_src.text_decoration != "none":
                        td = span_src.text_decoration

                    # Background highlight (e.g. <code>)
                    if span_src.background_color:
                        bg_y = ly - baseline_offset + (line_h - font_size) / 2.0
                        bg_h = font_size * 1.2
                        bg_rect = dw.Rectangle(
                            run["x"], bg_y, run["width"], bg_h,
                            fill=span_src.background_color,
                            rx=2, ry=2,
                        )
                        group.append(bg_rect)

                text_kw: dict = dict(
                    fill=color,
                    font_family=family,
                    font_weight=weight,
                    font_style=f_style,
                )
                if td != "none":
                    text_kw["text_decoration"] = td
                if op < 1.0:
                    text_kw["opacity"] = op

                t = dw.Text(text, fsize, run["x"], text_y, **text_kw)
                # Preserve whitespace so that librsvg/Inkscape do not
                # strip spaces inside the text run (SVG 1.1 default
                # behaviour strips leading/trailing spaces from <text>).
                t.args["xml:space"] = "preserve"
                if ls_px:
                    t.args["letter-spacing"] = f"{ls_px}"
                if ws_px:
                    t.args["word-spacing"] = f"{ws_px}"
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
    # Math node rendering
    # -----------------------------------------------------------------

    @staticmethod
    def _render_math(
        group: dw.Group,
        node: "MathNode",
        offset_x: float,
        offset_y: float,
    ) -> None:
        """Embed a LaTeX math formula as an SVG fragment."""
        cb = node.content_box
        x = cb.x + offset_x + getattr(node, "_formula_x_offset", 0.0)
        y = cb.y + offset_y

        sx = getattr(node, "scale_x", 1.0)
        sy = getattr(node, "scale_y", 1.0)

        svg_fragment = node.get_svg_fragment()
        transform = f"translate({x},{y}) scale({sx},{sy})"

        raw = dw.Raw(
            f'<g transform="{transform}">{svg_fragment}</g>'
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
