"""Core geometry types and the abstract Node base class."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..style.computed import ComputedStyle
from ..style.parser import AUTO, AutoValue


# ---------------------------------------------------------------------------
# Geometry primitives
# ---------------------------------------------------------------------------

@dataclass
class Rect:
    """An axis-aligned rectangle (top-left origin, y-axis points down)."""

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def copy(self) -> "Rect":
        return Rect(self.x, self.y, self.width, self.height)

    def __repr__(self) -> str:
        return f"Rect(x={self.x:.1f}, y={self.y:.1f}, w={self.width:.1f}, h={self.height:.1f})"


@dataclass
class LayoutConstraints:
    """Constraints passed from parent to child during layout."""

    available_width: Optional[float] = None
    available_height: Optional[float] = None


# ---------------------------------------------------------------------------
# Placement hints (Grid positioning)
# ---------------------------------------------------------------------------

@dataclass
class PlacementHint:
    """Grid placement information for a child node."""

    row_start: Optional[int] = None
    row_span: int = 1
    col_start: Optional[int] = None
    col_span: int = 1
    area: Optional[str] = None


# ---------------------------------------------------------------------------
# Node base class
# ---------------------------------------------------------------------------

class Node:
    """Abstract base for all layoutable elements.

    Subclasses must implement :meth:`measure` and :meth:`layout`.
    """

    def __init__(self, style: Optional[Dict[str, Any]] = None, parent: Optional["Node"] = None) -> None:
        parent_computed = parent.style if parent else None
        self.style: ComputedStyle = ComputedStyle(style, parent_style=parent_computed)
        self.parent: Optional[Node] = parent
        self.children: List[Node] = []

        # Populated after layout
        self.border_box: Rect = Rect()
        self.padding_box: Rect = Rect()
        self.content_box: Rect = Rect()

        # Grid placement (set via ``add()``)
        self.placement: PlacementHint = PlacementHint()

    # -----------------------------------------------------------------
    # Tree manipulation
    # -----------------------------------------------------------------

    def add(self, child: "Node", *, row: Optional[int] = None, col: Optional[int] = None,
            row_span: int = 1, col_span: int = 1, area: Optional[str] = None) -> "Node":
        """Append *child* to this node and optionally set grid placement.

        ``row`` and ``col`` use 1-based line numbers consistent with CSS Grid.
        ``area`` places the child in a named grid area defined by
        ``grid-template-areas`` on the container.
        """
        child.parent = self
        # Re-compute style with parent inheritance
        if isinstance(child.style, ComputedStyle):
            child.style._rebind_parent(self.style)
        else:
            child.style = ComputedStyle(None, parent_style=self.style)

        child.placement = PlacementHint(
            row_start=row,
            row_span=row_span,
            col_start=col,
            col_span=col_span,
            area=area,
        )

        # Also honour grid-row / grid-column / grid-area from the child's own style
        gr = child.style.get("grid-row")
        gc = child.style.get("grid-column")
        ga = child.style.get("grid-area")
        if gr is not None and isinstance(gr, tuple):
            child.placement.row_start = gr[0]
            child.placement.row_span = gr[1]
        if gc is not None and isinstance(gc, tuple):
            child.placement.col_start = gc[0]
            child.placement.col_span = gc[1]
        if ga is not None and isinstance(ga, str) and ga != "auto":
            child.placement.area = ga

        self.children.append(child)
        return child

    # -----------------------------------------------------------------
    # Measurement & layout (to be overridden)
    # -----------------------------------------------------------------

    def measure(self, constraints: LayoutConstraints) -> Tuple[float, float, float]:
        """Return ``(min_content_width, max_content_width, intrinsic_height)``.

        Called by the grid solver to determine how much space this node needs.
        Default implementation returns zero sizes.
        """
        return (0.0, 0.0, 0.0)

    def layout(self, constraints: LayoutConstraints) -> None:
        """Compute ``border_box``, ``padding_box``, and ``content_box``.

        Must be implemented by subclasses.
        """
        pass

    # -----------------------------------------------------------------
    # Box model helpers
    # -----------------------------------------------------------------

    def _resolve_box_model(self, content_width: float, content_height: float,
                           x: float = 0.0, y: float = 0.0) -> None:
        """Compute the three box rects from inside out.

        *x*, *y* are the position of the border-box top-left corner
        in the parent's coordinate system.
        """
        s = self.style

        bw_t = s.border_top_width
        bw_r = s.border_right_width
        bw_b = s.border_bottom_width
        bw_l = s.border_left_width
        pt = s.padding_top
        pr = s.padding_right
        pb = s.padding_bottom
        pl = s.padding_left

        self.content_box = Rect(
            x=x + bw_l + pl,
            y=y + bw_t + pt,
            width=content_width,
            height=content_height,
        )
        self.padding_box = Rect(
            x=x + bw_l,
            y=y + bw_t,
            width=pl + content_width + pr,
            height=pt + content_height + pb,
        )
        self.border_box = Rect(
            x=x,
            y=y,
            width=bw_l + pl + content_width + pr + bw_r,
            height=bw_t + pt + content_height + pb + bw_b,
        )

    def _resolve_width(self, constraints: LayoutConstraints) -> Optional[float]:
        """Resolve the explicit ``width`` property to a pixel value, or ``None`` for auto.

        When ``box-sizing`` is ``border-box``, the returned value is the
        *border-box* width (i.e. it includes padding and border).
        When ``content-box`` (default), it is the *content* width.
        """
        w = self.style.get("width")
        if w is None or isinstance(w, AutoValue) or w == "auto":
            return None
        if isinstance(w, (int, float)):
            return float(w)
        return None

    def _resolve_height(self, constraints: LayoutConstraints) -> Optional[float]:
        """Resolve the explicit ``height`` property to a pixel value, or ``None`` for auto.

        When ``box-sizing`` is ``border-box``, the returned value is the
        *border-box* height (i.e. it includes padding and border).
        When ``content-box`` (default), it is the *content* height.
        """
        h = self.style.get("height")
        if h is None or isinstance(h, AutoValue) or h == "auto":
            return None
        if isinstance(h, (int, float)):
            return float(h)
        return None

    def _is_border_box(self) -> bool:
        """Return True when ``box-sizing`` is ``border-box``."""
        return self.style.get("box-sizing") == "border-box"

    def _width_to_content(self, explicit_w: float) -> float:
        """Convert an explicit width to content width.

        If ``box-sizing: border-box``, subtract padding + border.
        Otherwise return as-is (content-box).
        """
        if self._is_border_box():
            return max(0.0, explicit_w - self.style.padding_horizontal - self.style.border_horizontal)
        return explicit_w

    def _height_to_content(self, explicit_h: float) -> float:
        """Convert an explicit height to content height.

        If ``box-sizing: border-box``, subtract padding + border.
        Otherwise return as-is (content-box).
        """
        if self._is_border_box():
            return max(0.0, explicit_h - self.style.padding_vertical - self.style.border_vertical)
        return explicit_h

    def _content_available_width(self, constraints: LayoutConstraints) -> Optional[float]:
        """Content-area available width after subtracting padding + border."""
        explicit_w = self._resolve_width(constraints)
        if explicit_w is not None:
            return self._width_to_content(explicit_w)
        if constraints.available_width is not None:
            return max(
                0.0,
                constraints.available_width
                - self.style.padding_horizontal
                - self.style.border_horizontal
                - self.style.margin_horizontal,
            )
        return None
