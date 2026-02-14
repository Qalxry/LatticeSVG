"""CSS Grid Level 1 layout solver.

Implements track sizing, item placement, coordinate computation, and
alignment — the heart of the LatticeSVG layout engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from ..style.parser import AUTO, AutoValue, FrValue, MinContent, MaxContent, MinMaxValue, _Percentage, AreaMapping

if TYPE_CHECKING:
    from ..nodes.base import LayoutConstraints, Node, Rect
    from ..nodes.grid import GridContainer


# ---------------------------------------------------------------------------
# Internal data structures
# ---------------------------------------------------------------------------

class SizeType(Enum):
    FIXED = auto()
    PERCENT = auto()
    FR = auto()
    AUTO = auto()
    MIN_CONTENT = auto()
    MAX_CONTENT = auto()
    MINMAX = auto()


@dataclass
class TrackDef:
    """Parsed definition for one grid track (column or row)."""
    size_type: SizeType
    value: float = 0.0  # px for FIXED, fraction for FR, percent for PERCENT
    min_track: Optional["TrackDef"] = None  # for MINMAX
    max_track: Optional["TrackDef"] = None  # for MINMAX

    @classmethod
    def from_parsed(cls, val: Any) -> "TrackDef":
        if isinstance(val, MinMaxValue):
            return cls(
                SizeType.MINMAX,
                min_track=cls.from_parsed(val.min_val),
                max_track=cls.from_parsed(val.max_val),
            )
        if isinstance(val, FrValue):
            return cls(SizeType.FR, val.value)
        if isinstance(val, (int, float)):
            return cls(SizeType.FIXED, float(val))
        if isinstance(val, _Percentage):
            return cls(SizeType.PERCENT, val.value)
        if isinstance(val, MinContent):
            return cls(SizeType.MIN_CONTENT)
        if isinstance(val, MaxContent):
            return cls(SizeType.MAX_CONTENT)
        if isinstance(val, AutoValue) or val is AUTO:
            return cls(SizeType.AUTO)
        # Fallback
        return cls(SizeType.AUTO)


@dataclass
class Track:
    """Runtime state for a single track during sizing."""
    definition: TrackDef
    base_size: float = 0.0
    growth_limit: float = float("inf")
    final_size: float = 0.0

    def clamp(self) -> None:
        if self.growth_limit < self.base_size:
            self.growth_limit = self.base_size


@dataclass
class GridItem:
    """A child node with its resolved grid placement."""
    node: "Node"
    row_start: int   # 0-based index
    row_end: int     # exclusive
    col_start: int   # 0-based index
    col_end: int     # exclusive

    @property
    def row_span(self) -> int:
        return self.row_end - self.row_start

    @property
    def col_span(self) -> int:
        return self.col_end - self.col_start


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

class GridSolver:
    """Performs CSS Grid layout on a :class:`GridContainer`."""

    def __init__(self, container: "GridContainer") -> None:
        self.container = container
        self.col_tracks: List[Track] = []
        self.row_tracks: List[Track] = []
        self.items: List[GridItem] = []
        self._col_gap: float = 0.0
        self._row_gap: float = 0.0

    # =================================================================
    # Public API
    # =================================================================

    def solve(self, constraints: "LayoutConstraints") -> None:
        """Run the complete grid layout algorithm."""
        from ..nodes.base import LayoutConstraints as LC, Rect

        s = self.container.style

        # ---- Resolve container width --------------------------------
        container_w = self.container._resolve_width(constraints)
        if container_w is None:
            container_w = constraints.available_width or 800.0
            # available_width is always a border-box concept
            content_w = max(
                0.0,
                container_w - s.padding_horizontal - s.border_horizontal,
            )
        else:
            # _resolve_width returns the raw value; convert via box-sizing
            content_w = self.container._width_to_content(container_w)

        # ---- Gap ----------------------------------------------------
        self._col_gap = s._float("column-gap")
        self._row_gap = s._float("row-gap")

        # ---- Parse track templates ----------------------------------
        col_defs = self._parse_track_defs(s.get("grid-template-columns"))
        row_defs = self._parse_track_defs(s.get("grid-template-rows"))

        # ---- Parse grid-template-areas & ensure track counts ---------
        area_mapping = s.get("grid-template-areas")
        if isinstance(area_mapping, AreaMapping):
            while len(col_defs) < area_mapping.num_cols:
                col_defs.append(self._implicit_track_def("col"))
            while len(row_defs) < area_mapping.num_rows:
                row_defs.append(self._implicit_track_def("row"))

        # ---- Place items --------------------------------------------
        self.items = self._place_items(col_defs, row_defs, area_mapping)

        # Ensure enough tracks exist for all items
        max_col = max((it.col_end for it in self.items), default=len(col_defs))
        max_row = max((it.row_end for it in self.items), default=len(row_defs))
        while len(col_defs) < max_col:
            col_defs.append(self._implicit_track_def("col"))
        while len(row_defs) < max_row:
            row_defs.append(self._implicit_track_def("row"))

        self.col_tracks = [Track(d) for d in col_defs]
        self.row_tracks = [Track(d) for d in row_defs]

        # ---- Column sizing ------------------------------------------
        self._resolve_tracks_axis(
            self.col_tracks,
            content_w,
            self._col_gap,
            axis="col",
        )

        # ---- Row sizing (depends on column widths for text reflow) --
        # First compute item content heights given column widths
        raw_h = self.container._resolve_height(constraints)
        content_h_for_rows = (
            self.container._height_to_content(raw_h) if raw_h is not None else None
        )
        self._resolve_tracks_axis(
            self.row_tracks,
            content_h_for_rows,
            self._row_gap,
            axis="row",
        )

        total_row_height = (
            sum(t.final_size for t in self.row_tracks)
            + self._row_gap * max(0, len(self.row_tracks) - 1)
        )

        # ---- Container height ---------------------------------------
        container_h = self.container._resolve_height(constraints)
        if container_h is None:
            content_h = total_row_height
        else:
            content_h = self.container._height_to_content(container_h)

        # ---- Resolve container boxes --------------------------------
        self.container._resolve_box_model(content_w, content_h)

        # ---- Compute child positions --------------------------------
        self._compute_positions()

        # ---- Layout children recursively ----------------------------
        for item in self.items:
            cell_w = self._item_column_width(item)
            cell_h = self._item_row_height(item)

            # Determine alignment — non-stretch items should layout at
            # their intrinsic size, not the full cell size.
            ns = item.node.style
            cs = self.container.style
            justify = ns.get("justify-self")
            if justify is None or justify == "auto" or isinstance(justify, AutoValue):
                justify = cs.get("justify-items") or "stretch"
            align = ns.get("align-self")
            if align is None or align == "auto" or isinstance(align, AutoValue):
                align = cs.get("align-items") or "stretch"

            if justify != "stretch":
                # Use the child's intrinsic width
                c_meas = LC(available_width=cell_w)
                _, max_w, _ = item.node.measure(c_meas)
                layout_w = min(max_w, cell_w)
            else:
                layout_w = cell_w

            if align != "stretch":
                c_meas = LC(available_width=layout_w)
                _, _, intr_h = item.node.measure(c_meas)
                layout_h = min(intr_h, cell_h)
            else:
                layout_h = cell_h

            child_constraints = LC(
                available_width=layout_w,
                available_height=layout_h,
            )
            item.node.layout(child_constraints)

            # Apply alignment to position within the cell
            self._apply_alignment(item)

            # Apply min/max width/height constraints (after alignment,
            # so that stretch doesn't override the clamp).
            self._clamp_min_max(item.node)

    @staticmethod
    def _clamp_min_max(node: "Node") -> None:
        """Apply min-width/max-width/min-height/max-height constraints.

        Adjusts the node's border_box, padding_box, and content_box
        according to the CSS min/max sizing properties.
        The values follow the same ``box-sizing`` as ``width``/``height``.
        """
        s = node.style

        min_w_raw = s.get("min-width")
        max_w_raw = s.get("max-width")
        min_h_raw = s.get("min-height")
        max_h_raw = s.get("max-height")

        min_w = float(min_w_raw) if isinstance(min_w_raw, (int, float)) else 0.0
        max_w = float(max_w_raw) if isinstance(max_w_raw, (int, float)) else float("inf")
        min_h = float(min_h_raw) if isinstance(min_h_raw, (int, float)) else 0.0
        max_h = float(max_h_raw) if isinstance(max_h_raw, (int, float)) else float("inf")

        # Skip if no effective constraints
        if min_w <= 0 and max_w == float("inf") and min_h <= 0 and max_h == float("inf"):
            return

        # Convert min/max to border-box for comparison with border_box rect
        if node._is_border_box():
            bb_min_w = min_w
            bb_max_w = max_w
            bb_min_h = min_h
            bb_max_h = max_h
        else:
            # content-box: the given min/max are content sizes
            bb_min_w = min_w + s.padding_horizontal + s.border_horizontal if min_w > 0 else 0.0
            bb_max_w = max_w + s.padding_horizontal + s.border_horizontal if max_w != float("inf") else float("inf")
            bb_min_h = min_h + s.padding_vertical + s.border_vertical if min_h > 0 else 0.0
            bb_max_h = max_h + s.padding_vertical + s.border_vertical if max_h != float("inf") else float("inf")

        bb = node.border_box
        new_w = max(bb_min_w, min(bb.width, bb_max_w))
        new_h = max(bb_min_h, min(bb.height, bb_max_h))

        if new_w != bb.width or new_h != bb.height:
            content_w = max(0.0, new_w - s.padding_horizontal - s.border_horizontal)
            content_h = max(0.0, new_h - s.padding_vertical - s.border_vertical)
            node._resolve_box_model(content_w, content_h, x=bb.x, y=bb.y)

    def measure(self, constraints: "LayoutConstraints") -> Tuple[float, float, float]:
        """Measure the grid container's intrinsic sizes."""
        s = self.container.style
        col_defs = self._parse_track_defs(s.get("grid-template-columns"))
        row_defs = self._parse_track_defs(s.get("grid-template-rows"))

        self._col_gap = s._float("column-gap")
        self._row_gap = s._float("row-gap")

        # ---- Parse grid-template-areas & ensure track counts ---------
        area_mapping = s.get("grid-template-areas")
        if isinstance(area_mapping, AreaMapping):
            while len(col_defs) < area_mapping.num_cols:
                col_defs.append(self._implicit_track_def("col"))
            while len(row_defs) < area_mapping.num_rows:
                row_defs.append(self._implicit_track_def("row"))

        self.items = self._place_items(col_defs, row_defs, area_mapping)

        max_col = max((it.col_end for it in self.items), default=len(col_defs))
        max_row = max((it.row_end for it in self.items), default=len(row_defs))
        while len(col_defs) < max_col:
            col_defs.append(self._implicit_track_def("col"))
        while len(row_defs) < max_row:
            row_defs.append(self._implicit_track_def("row"))

        self.col_tracks = [Track(d) for d in col_defs]
        self.row_tracks = [Track(d) for d in row_defs]

        # Min-content: resolve columns at min sizes
        self._resolve_tracks_min_content(self.col_tracks, self._col_gap, axis="col")
        min_w = (
            sum(t.final_size for t in self.col_tracks)
            + self._col_gap * max(0, len(self.col_tracks) - 1)
        )

        # Max-content: resolve columns at max sizes
        self._resolve_tracks_max_content(self.col_tracks, self._col_gap, axis="col")
        max_w = (
            sum(t.final_size for t in self.col_tracks)
            + self._col_gap * max(0, len(self.col_tracks) - 1)
        )

        # Height at max-content width
        self._resolve_tracks_axis(self.row_tracks, None, self._row_gap, axis="row")
        h = (
            sum(t.final_size for t in self.row_tracks)
            + self._row_gap * max(0, len(self.row_tracks) - 1)
        )

        ph = s.padding_horizontal + s.border_horizontal
        pv = s.padding_vertical + s.border_vertical
        return (min_w + ph, max_w + ph, h + pv)

    # =================================================================
    # Track template parsing
    # =================================================================

    @staticmethod
    def _parse_track_defs(raw: Any) -> List[TrackDef]:
        if raw is None:
            return []
        if isinstance(raw, list):
            return [TrackDef.from_parsed(v) for v in raw]
        return [TrackDef.from_parsed(raw)]

    def _implicit_track_def(self, axis: str) -> TrackDef:
        """Return the *TrackDef* for implicit tracks on *axis* (``'col'``/``'row'``)."""
        prop = "grid-auto-columns" if axis == "col" else "grid-auto-rows"
        raw = self.container.style.get(prop)
        if isinstance(raw, list) and raw:
            return TrackDef.from_parsed(raw[0])
        return TrackDef(SizeType.AUTO)

    # =================================================================
    # Item placement
    # =================================================================

    def _place_items(
        self,
        col_defs: List[TrackDef],
        row_defs: List[TrackDef],
        area_mapping: Any = None,
    ) -> List[GridItem]:
        """Place all child nodes on the grid."""
        children = self.container.children
        if not children:
            return []

        # Resolve area mapping
        areas: Dict[str, Tuple[int, int, int, int]] = {}
        if isinstance(area_mapping, AreaMapping):
            areas = area_mapping.areas

        flow = self.container.style.get("grid-auto-flow") or "row"
        dense = "dense" in flow if isinstance(flow, str) else False
        flow_axis = "column" if isinstance(flow, str) and "column" in flow else "row"

        num_cols = len(col_defs) if col_defs else 1
        num_rows = len(row_defs) if row_defs else 0

        items: List[GridItem] = []
        occupied: Set[Tuple[int, int]] = set()

        # Pass 1: explicitly placed items (including area-placed)
        for child in children:
            p = child.placement

            # Resolve area name to explicit placement
            if p.area and p.area in areas:
                r, c, rs, cs = areas[p.area]
                item = GridItem(child, r, r + rs, c, c + cs)
                items.append(item)
                for rr in range(r, r + rs):
                    for cc in range(c, c + cs):
                        occupied.add((rr, cc))
                continue

            if p.row_start is not None and p.col_start is not None:
                r = p.row_start - 1  # convert 1-based → 0-based
                c = p.col_start - 1
                rs = p.row_span
                cs = p.col_span
                item = GridItem(child, r, r + rs, c, c + cs)
                items.append(item)
                for rr in range(r, r + rs):
                    for cc in range(c, c + cs):
                        occupied.add((rr, cc))

        # Pass 2: auto-placed items
        cursor_r, cursor_c = 0, 0
        for child in children:
            p = child.placement
            if p.area and p.area in areas:
                continue  # placed by area in pass 1
            if p.row_start is not None and p.col_start is not None:
                continue  # already placed

            rs = p.row_span
            cs = p.col_span

            if p.row_start is not None:
                r = p.row_start - 1
                c = self._find_col(r, cs, occupied, num_cols)
                item = GridItem(child, r, r + rs, c, c + cs)
            elif p.col_start is not None:
                c = p.col_start - 1
                r = self._find_row(c, rs, occupied)
                item = GridItem(child, r, r + rs, c, c + cs)
            else:
                # Fully auto
                if flow_axis == "row":
                    r, c = self._auto_place_row(
                        cursor_r, cursor_c, rs, cs, occupied, num_cols, dense
                    )
                else:
                    r, c = self._auto_place_col(
                        cursor_r, cursor_c, rs, cs, occupied, num_rows, dense
                    )
                item = GridItem(child, r, r + rs, c, c + cs)
                # Advance cursor
                if flow_axis == "row":
                    cursor_r, cursor_c = r, c + cs
                    if cursor_c >= num_cols:
                        cursor_r += 1
                        cursor_c = 0
                else:
                    cursor_r, cursor_c = r + rs, c

            items.append(item)
            for rr in range(item.row_start, item.row_end):
                for cc in range(item.col_start, item.col_end):
                    occupied.add((rr, cc))

        return items

    def _find_col(
        self, row: int, col_span: int, occupied: Set[Tuple[int, int]], num_cols: int
    ) -> int:
        for c in range(num_cols):
            if all((row, c + dc) not in occupied for dc in range(col_span)):
                return c
        return num_cols  # expand implicitly

    def _find_row(
        self, col: int, row_span: int, occupied: Set[Tuple[int, int]]
    ) -> int:
        for r in range(200):  # reasonable upper bound
            if all((r + dr, col) not in occupied for dr in range(row_span)):
                return r
        return 0

    def _auto_place_row(
        self,
        start_r: int,
        start_c: int,
        rs: int,
        cs: int,
        occupied: Set[Tuple[int, int]],
        num_cols: int,
        dense: bool,
    ) -> Tuple[int, int]:
        r, c = (0, 0) if dense else (start_r, start_c)
        for _ in range(10000):
            if c + cs > num_cols:
                r += 1
                c = 0
                continue
            conflict = False
            for dr in range(rs):
                for dc in range(cs):
                    if (r + dr, c + dc) in occupied:
                        conflict = True
                        break
                if conflict:
                    break
            if not conflict:
                return (r, c)
            c += 1
        return (r, 0)

    def _auto_place_col(
        self,
        start_r: int,
        start_c: int,
        rs: int,
        cs: int,
        occupied: Set[Tuple[int, int]],
        num_rows: int,
        dense: bool,
    ) -> Tuple[int, int]:
        r, c = (0, 0) if dense else (start_r, start_c)
        max_r = num_rows if num_rows > 0 else 200
        for _ in range(10000):
            if r + rs > max_r:
                c += 1
                r = 0
                continue
            conflict = False
            for dr in range(rs):
                for dc in range(cs):
                    if (r + dr, c + dc) in occupied:
                        conflict = True
                        break
                if conflict:
                    break
            if not conflict:
                return (r, c)
            r += 1
        return (0, c)

    # =================================================================
    # Track sizing
    # =================================================================

    def _resolve_tracks_axis(
        self,
        tracks: List[Track],
        available: Optional[float],
        gap: float,
        axis: str,   # "col" or "row"
    ) -> None:
        """Full track sizing algorithm for one axis."""
        if not tracks:
            return

        from ..nodes.base import LayoutConstraints

        total_gap = gap * max(0, len(tracks) - 1)

        # Helper: resolve a fixed-ish TrackDef to a px value
        def _resolve_definite(td: Optional[TrackDef], ref: Optional[float]) -> Optional[float]:
            if td is None:
                return None
            if td.size_type == SizeType.FIXED:
                return td.value
            if td.size_type == SizeType.PERCENT:
                return td.value / 100.0 * (ref or 0.0)
            return None

        # Pass 1: Fixed / percent tracks (including minmax definite parts)
        for t in tracks:
            d = t.definition
            if d.size_type == SizeType.FIXED:
                t.base_size = d.value
                t.growth_limit = d.value
            elif d.size_type == SizeType.PERCENT:
                ref = available if available else 0.0
                t.base_size = d.value / 100.0 * ref
                t.growth_limit = t.base_size
            elif d.size_type == SizeType.MINMAX:
                # Set base_size from min (if definite)
                min_px = _resolve_definite(d.min_track, available)
                if min_px is not None:
                    t.base_size = min_px
                # Set growth_limit from max (if definite and not fr)
                if d.max_track and d.max_track.size_type == SizeType.FR:
                    t.growth_limit = float("inf")  # handled in Pass 4
                else:
                    max_px = _resolve_definite(d.max_track, available)
                    if max_px is not None:
                        t.growth_limit = max_px
                    # else stays inf for intrinsic max, resolved in Pass 2

        # Collect size types that need intrinsic sizing (Pass 2)
        _INTRINSIC = (SizeType.AUTO, SizeType.MIN_CONTENT, SizeType.MAX_CONTENT)

        def _needs_intrinsic(d: TrackDef) -> bool:
            if d.size_type in _INTRINSIC:
                return True
            if d.size_type == SizeType.MINMAX:
                min_intr = d.min_track and d.min_track.size_type in _INTRINSIC
                max_intr = d.max_track and d.max_track.size_type in (*_INTRINSIC, SizeType.FR)
                return bool(min_intr or max_intr)
            return False

        def _intrinsic_base_type(d: TrackDef) -> SizeType:
            """Return the effective intrinsic sizing mode for base_size."""
            if d.size_type == SizeType.MINMAX and d.min_track:
                return d.min_track.size_type
            return d.size_type

        def _intrinsic_limit_type(d: TrackDef) -> SizeType:
            """Return the effective intrinsic sizing mode for growth_limit."""
            if d.size_type == SizeType.MINMAX and d.max_track:
                return d.max_track.size_type
            return d.size_type

        # Pass 2: Intrinsic tracks (auto/min-content/max-content) —
        #          use non-spanning items to set base_size and growth_limit
        for item in self.items:
            if axis == "col" and item.col_span == 1:
                idx = item.col_start
                if idx < len(tracks):
                    t = tracks[idx]
                    if _needs_intrinsic(t.definition):
                        c = LayoutConstraints(available_width=available)
                        min_w, max_w, min_h = item.node.measure(c)
                        bt = _intrinsic_base_type(t.definition)
                        lt = _intrinsic_limit_type(t.definition)
                        # base_size (only update if min side is intrinsic)
                        if bt in _INTRINSIC:
                            if bt == SizeType.MIN_CONTENT:
                                t.base_size = max(t.base_size, min_w)
                            elif bt == SizeType.MAX_CONTENT:
                                t.base_size = max(t.base_size, max_w)
                            else:  # AUTO
                                t.base_size = max(t.base_size, min_w)
                        # growth_limit (only update if max side is intrinsic, not fr)
                        if lt in _INTRINSIC:
                            gl = t.growth_limit if t.growth_limit != float("inf") else 0
                            if lt == SizeType.MIN_CONTENT:
                                t.growth_limit = max(gl, min_w)
                            elif lt == SizeType.MAX_CONTENT:
                                t.growth_limit = max(gl, max_w)
                            else:  # AUTO
                                t.growth_limit = max(gl, max_w)
            elif axis == "row" and item.row_span == 1:
                idx = item.row_start
                if idx < len(tracks):
                    t = tracks[idx]
                    if _needs_intrinsic(t.definition):
                        # For rows, we need to know the column widths to reflow text
                        item_w = self._item_column_width(item)
                        c = LayoutConstraints(available_width=item_w)
                        min_w, max_w, min_h = item.node.measure(c)
                        # Row track: base_size and growth_limit are heights
                        # Re-measure with actual available width to get correct height
                        item.node.layout(c)
                        item_h = item.node.border_box.height
                        t.base_size = max(t.base_size, item_h)
                        if t.growth_limit == float("inf"):
                            t.growth_limit = t.base_size
                        else:
                            t.growth_limit = max(t.growth_limit, item_h)

        # Clamp growth_limits
        for t in tracks:
            t.clamp()
            if t.growth_limit == float("inf"):
                t.growth_limit = t.base_size

        # Pass 3: Spanning items — distribute excess to spanned tracks
        for item in self.items:
            if axis == "col" and item.col_span > 1:
                self._distribute_spanning(tracks, item.col_start, item.col_end, gap, item, axis)
            elif axis == "row" and item.row_span > 1:
                self._distribute_spanning(tracks, item.row_start, item.row_end, gap, item, axis)

        # Helper functions for fr track identification
        def _is_fr_track(t: Track) -> bool:
            d = t.definition
            if d.size_type == SizeType.FR:
                return True
            if d.size_type == SizeType.MINMAX and d.max_track and d.max_track.size_type == SizeType.FR:
                return True
            return False

        def _fr_value(t: Track) -> float:
            d = t.definition
            if d.size_type == SizeType.FR:
                return d.value
            if d.size_type == SizeType.MINMAX and d.max_track and d.max_track.size_type == SizeType.FR:
                return d.max_track.value
            return 0.0

        # Pass 3.5: Maximize non-fr tracks — grow base_size towards
        #           growth_limit using any remaining free space.
        #           This implements the CSS Grid "maximize tracks" step
        #           so that e.g. minmax(100px, 300px) can grow beyond its min.
        if available is not None:
            for _ in range(20):  # iterate to convergence
                current_sum = sum(t.base_size for t in tracks) + total_gap
                free = available - current_sum
                if free <= 0:
                    break
                growable = [t for t in tracks
                            if not _is_fr_track(t) and t.growth_limit > t.base_size]
                if not growable:
                    break
                share = free / len(growable)
                for t in growable:
                    room = t.growth_limit - t.base_size
                    t.base_size += min(share, room)

        # Pass 4: Distribute remaining space to fr tracks
        #         (includes minmax tracks whose max is fr)

        non_fr_sum = sum(
            t.base_size for t in tracks if not _is_fr_track(t)
        )
        fr_tracks = [t for t in tracks if _is_fr_track(t)]
        if fr_tracks and available is not None:
            remaining = available - non_fr_sum - total_gap
            total_fr = sum(_fr_value(t) for t in fr_tracks)
            if total_fr > 0 and remaining > 0:
                for t in fr_tracks:
                    fr_size = (_fr_value(t) / total_fr) * remaining
                    t.base_size = max(t.base_size, fr_size)
                    t.growth_limit = t.base_size

        # Finalise
        for t in tracks:
            t.final_size = t.base_size

    def _distribute_spanning(
        self,
        tracks: List[Track],
        start: int,
        end: int,
        gap: float,
        item: GridItem,
        axis: str,
    ) -> None:
        """Distribute extra space needed by a spanning item across its spanned tracks."""
        from ..nodes.base import LayoutConstraints

        spanned = tracks[start:end]
        if not spanned:
            return

        span_gap = gap * (len(spanned) - 1)
        current_sum = sum(t.base_size for t in spanned) + span_gap

        # Determine needed size
        if axis == "col":
            c = LayoutConstraints(available_width=None)
            min_w, max_w, _ = item.node.measure(c)
            needed = min_w
        else:
            item_w = self._item_column_width(item)
            c = LayoutConstraints(available_width=item_w)
            _, _, min_h = item.node.measure(c)
            item.node.layout(c)
            needed = item.node.border_box.height

        excess = needed - current_sum
        if excess <= 0:
            return

        # Prefer distributing to fr tracks, then auto, then fixed
        fr_spanned = [t for t in spanned if t.definition.size_type == SizeType.FR]
        auto_spanned = [t for t in spanned if t.definition.size_type in (SizeType.AUTO, SizeType.MIN_CONTENT, SizeType.MAX_CONTENT)]
        targets = fr_spanned or auto_spanned or spanned

        share = excess / len(targets)
        for t in targets:
            t.base_size += share
            t.clamp()

    def _resolve_tracks_min_content(self, tracks: List[Track], gap: float, axis: str) -> None:
        """Resolve tracks using min-content sizes (for measuring)."""
        from ..nodes.base import LayoutConstraints
        for t in tracks:
            d = t.definition
            if d.size_type == SizeType.FIXED:
                t.final_size = d.value
            elif d.size_type == SizeType.PERCENT:
                t.final_size = 0  # no reference
            else:
                t.final_size = 0
        for item in self.items:
            if axis == "col" and item.col_span == 1:
                idx = item.col_start
                if idx < len(tracks):
                    c = LayoutConstraints()
                    min_w, _, _ = item.node.measure(c)
                    tracks[idx].final_size = max(tracks[idx].final_size, min_w)

    def _resolve_tracks_max_content(self, tracks: List[Track], gap: float, axis: str) -> None:
        """Resolve tracks using max-content sizes (for measuring)."""
        from ..nodes.base import LayoutConstraints
        for t in tracks:
            d = t.definition
            if d.size_type == SizeType.FIXED:
                t.final_size = d.value
            elif d.size_type == SizeType.PERCENT:
                t.final_size = 0
            else:
                t.final_size = 0
        for item in self.items:
            if axis == "col" and item.col_span == 1:
                idx = item.col_start
                if idx < len(tracks):
                    c = LayoutConstraints()
                    _, max_w, _ = item.node.measure(c)
                    tracks[idx].final_size = max(tracks[idx].final_size, max_w)

    def _item_column_width(self, item: GridItem) -> float:
        """Compute the total width allocated to a grid item from column tracks."""
        if not self.col_tracks:
            return 0.0
        w = 0.0
        for i in range(item.col_start, min(item.col_end, len(self.col_tracks))):
            w += self.col_tracks[i].final_size
        w += self._col_gap * max(0, item.col_span - 1)
        return w

    def _item_row_height(self, item: GridItem) -> float:
        """Compute the total height allocated to a grid item from row tracks."""
        if not self.row_tracks:
            return 0.0
        h = 0.0
        for i in range(item.row_start, min(item.row_end, len(self.row_tracks))):
            h += self.row_tracks[i].final_size
        h += self._row_gap * max(0, item.row_span - 1)
        return h

    # =================================================================
    # Position computation
    # =================================================================

    def _compute_positions(self) -> None:
        """Set ``border_box`` on each child based on track positions."""
        from ..nodes.base import Rect

        # Column start positions (relative to container content box)
        col_starts: List[float] = []
        x = 0.0
        for i, t in enumerate(self.col_tracks):
            col_starts.append(x)
            x += t.final_size + self._col_gap

        # Row start positions
        row_starts: List[float] = []
        y = 0.0
        for i, t in enumerate(self.row_tracks):
            row_starts.append(y)
            y += t.final_size + self._row_gap

        cx = self.container.content_box.x
        cy = self.container.content_box.y

        for item in self.items:
            # Cell position
            cell_x = col_starts[item.col_start] if item.col_start < len(col_starts) else 0
            cell_y = row_starts[item.row_start] if item.row_start < len(row_starts) else 0
            cell_w = self._item_column_width(item)
            cell_h = self._item_row_height(item)

            item.node.border_box = Rect(
                x=cx + cell_x,
                y=cy + cell_y,
                width=cell_w,
                height=cell_h,
            )

    # =================================================================
    # Alignment
    # =================================================================

    def _apply_alignment(self, item: GridItem) -> None:
        """Apply justify-self / align-self within the cell."""
        from ..nodes.base import Rect

        cs = self.container.style
        ns = item.node.style

        # Cell dimensions
        cell_w = self._item_column_width(item)
        cell_h = self._item_row_height(item)

        # Resolve alignment values
        justify = ns.get("justify-self")
        if justify is None or justify == "auto" or isinstance(justify, AutoValue):
            justify = cs.get("justify-items") or "stretch"
        align = ns.get("align-self")
        if align is None or align == "auto" or isinstance(align, AutoValue):
            align = cs.get("align-items") or "stretch"

        # The child's actual dimensions
        child_w = item.node.border_box.width
        child_h = item.node.border_box.height

        # If stretch, expand to cell size
        if justify == "stretch":
            child_w = cell_w
        if align == "stretch":
            child_h = cell_h

        # Compute offset within cell
        dx = 0.0
        if justify == "center":
            dx = (cell_w - child_w) / 2
        elif justify == "end":
            dx = cell_w - child_w

        dy = 0.0
        if align == "center":
            dy = (cell_h - child_h) / 2
        elif align == "end":
            dy = cell_h - child_h

        # Update the child's boxes
        cx = self.container.content_box.x
        cy = self.container.content_box.y

        col_starts = self._col_starts()
        row_starts = self._row_starts()
        cell_x = col_starts[item.col_start] if item.col_start < len(col_starts) else 0
        cell_y = row_starts[item.row_start] if item.row_start < len(row_starts) else 0

        # Remember old position before re-resolving (needed for nested grids)
        old_x = item.node.border_box.x
        old_y = item.node.border_box.y

        new_x = cx + cell_x + dx
        new_y = cy + cell_y + dy

        item.node._resolve_box_model(
            max(0, child_w - item.node.style.padding_horizontal - item.node.style.border_horizontal),
            max(0, child_h - item.node.style.padding_vertical - item.node.style.border_vertical),
            x=new_x,
            y=new_y,
        )

        # Shift all descendant positions by the delta so nested grid
        # children stay correctly positioned inside their container.
        shift_x = new_x - old_x
        shift_y = new_y - old_y
        if (shift_x != 0 or shift_y != 0) and item.node.children:
            self._shift_descendants(item.node, shift_x, shift_y)

    @staticmethod
    def _shift_descendants(node: "Node", dx: float, dy: float) -> None:
        """Recursively shift all descendant box positions by *(dx, dy)*."""
        for child in node.children:
            child.border_box.x += dx
            child.border_box.y += dy
            child.padding_box.x += dx
            child.padding_box.y += dy
            child.content_box.x += dx
            child.content_box.y += dy
            if child.children:
                GridSolver._shift_descendants(child, dx, dy)

    def _col_starts(self) -> List[float]:
        starts: List[float] = []
        x = 0.0
        for t in self.col_tracks:
            starts.append(x)
            x += t.final_size + self._col_gap
        return starts

    def _row_starts(self) -> List[float]:
        starts: List[float] = []
        y = 0.0
        for t in self.row_tracks:
            starts.append(y)
            y += t.final_size + self._row_gap
        return starts
