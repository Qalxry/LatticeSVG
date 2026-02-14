"""CSS value parser — converts raw CSS strings to resolved Python values.

Handles units (px, %, em, fr), keywords, colors, and shorthand expansion.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


# ---------------------------------------------------------------------------
# Sentinel / marker types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FrValue:
    """Represents an ``fr`` flexible-length value (CSS Grid)."""
    value: float

    def __repr__(self) -> str:
        return f"FrValue({self.value})"


class AutoValue:
    """Singleton representing the ``auto`` keyword."""
    _instance: Optional["AutoValue"] = None

    def __new__(cls) -> "AutoValue":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "auto"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AutoValue) or other == "auto"

    def __hash__(self) -> int:
        return hash("auto")


AUTO = AutoValue()


@dataclass(frozen=True)
class MinContent:
    """Sentinel for ``min-content``."""
    def __repr__(self) -> str:
        return "min-content"


@dataclass(frozen=True)
class MaxContent:
    """Sentinel for ``max-content``."""
    def __repr__(self) -> str:
        return "max-content"


MIN_CONTENT = MinContent()
MAX_CONTENT = MaxContent()


# ---------------------------------------------------------------------------
# Named CSS colors (subset — the most common ones)
# ---------------------------------------------------------------------------

NAMED_COLORS: Dict[str, str] = {
    "black": "#000000",
    "white": "#ffffff",
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "yellow": "#ffff00",
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
    "gray": "#808080",
    "grey": "#808080",
    "silver": "#c0c0c0",
    "maroon": "#800000",
    "olive": "#808000",
    "lime": "#00ff00",
    "aqua": "#00ffff",
    "teal": "#008080",
    "navy": "#000080",
    "fuchsia": "#ff00ff",
    "purple": "#800080",
    "orange": "#ffa500",
    "pink": "#ffc0cb",
    "brown": "#a52a2a",
    "coral": "#ff7f50",
    "gold": "#ffd700",
    "indigo": "#4b0082",
    "ivory": "#fffff0",
    "khaki": "#f0e68c",
    "lavender": "#e6e6fa",
    "beige": "#f5f5dc",
    "transparent": "rgba(0,0,0,0)",
}

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

_RE_NUMBER_UNIT = re.compile(
    r"^\s*(-?\d+(?:\.\d+)?)\s*(px|%|em|rem|fr|pt)?\s*$", re.IGNORECASE
)

_RE_HEX_COLOR = re.compile(
    r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$"
)

_RE_RGB = re.compile(
    r"^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)$",
    re.IGNORECASE,
)

_RE_GRID_LINE = re.compile(
    r"^\s*(\d+)\s*(?:/\s*(?:span\s+)?(\d+)\s*)?$"
)

# ---------------------------------------------------------------------------
# Value parsing
# ---------------------------------------------------------------------------


def parse_value(
    raw: Any,
    *,
    reference_length: Optional[float] = None,
    font_size: Optional[float] = None,
) -> Any:
    """Parse a single CSS value string into a resolved Python value.

    Parameters
    ----------
    raw : str | int | float | list | Any
        The raw value.  Non-string types are returned as-is (numbers) or
        processed (lists).
    reference_length : float, optional
        The reference length for resolving ``%`` values.
    font_size : float, optional
        Current computed font-size for resolving ``em`` / ``rem`` units.

    Returns
    -------
    Resolved value — float (px), FrValue, AutoValue, MinContent, MaxContent,
    str (color / keyword), or list.
    """
    # Passthrough for already-resolved types
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, (FrValue, AutoValue, MinContent, MaxContent)):
        return raw
    if isinstance(raw, list):
        return [
            parse_value(v, reference_length=reference_length, font_size=font_size)
            for v in raw
        ]

    if not isinstance(raw, str):
        return raw

    s = raw.strip()

    # --- Keywords ---
    lower = s.lower()
    if lower == "auto":
        return AUTO
    if lower == "min-content":
        return MIN_CONTENT
    if lower == "max-content":
        return MAX_CONTENT
    if lower in ("none", "normal", "nowrap", "pre", "pre-wrap", "pre-line",
                  "hidden", "visible", "scroll",
                  "left", "right", "center", "justify",
                  "start", "end", "stretch", "baseline",
                  "bold", "italic", "oblique",
                  "row", "column", "dense", "row dense", "column dense",
                  "contain", "cover", "fill",
                  "ellipsis", "clip",
                  "inherit", "initial", "unset"):
        return lower

    # --- Colors ---
    color = _parse_color(s)
    if color is not None:
        return color

    # --- Number + unit ---
    m = _RE_NUMBER_UNIT.match(s)
    if m:
        num = float(m.group(1))
        unit = (m.group(2) or "").lower()
        if unit == "" or unit == "px":
            return num
        if unit == "%":
            if reference_length is not None:
                return num / 100.0 * reference_length
            # Return a deferred percentage object
            return _Percentage(num)
        if unit in ("em", "rem"):
            fs = font_size if font_size is not None else 16.0
            return num * fs
        if unit == "fr":
            return FrValue(num)
        if unit == "pt":
            return num * (4.0 / 3.0)  # 1pt = 4/3 px at 96dpi

    # --- Grid line spec  e.g. "1 / span 2" ---
    gm = _RE_GRID_LINE.match(s)
    if gm:
        start = int(gm.group(1))
        span = int(gm.group(2)) if gm.group(2) else 1
        return (start, span)

    # Font-family list (comma separated unquoted names)
    if "," in s:
        return [part.strip().strip("'\"") for part in s.split(",")]

    # Return as-is (e.g. font family single name)
    return s


# ---------------------------------------------------------------------------
# Deferred percentage (resolved later when reference length is known)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _Percentage:
    """Unresolved percentage — will be resolved once the reference length is known."""
    value: float  # the raw number, e.g. 50 for "50%"

    def resolve(self, reference: float) -> float:
        return self.value / 100.0 * reference

    def __repr__(self) -> str:
        return f"{self.value}%"


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------


def _parse_color(s: str) -> Optional[str]:
    """Try to parse *s* as a CSS color. Returns normalised hex or ``None``."""
    lower = s.lower()
    if lower in NAMED_COLORS:
        return NAMED_COLORS[lower]

    if _RE_HEX_COLOR.match(s):
        return _normalise_hex(s)

    m = _RE_RGB.match(s)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = m.group(4)
        if a is not None:
            return f"rgba({r},{g},{b},{a})"
        return f"#{r:02x}{g:02x}{b:02x}"

    return None


def _normalise_hex(h: str) -> str:
    """Expand shorthand hex (#rgb → #rrggbb)."""
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    elif len(h) == 4:
        h = "".join(c * 2 for c in h)
    return f"#{h.lower()}"


# ---------------------------------------------------------------------------
# Shorthand expansion
# ---------------------------------------------------------------------------

_FOUR_SIDE_PROPS = {
    "margin": ("margin-top", "margin-right", "margin-bottom", "margin-left"),
    "padding": ("padding-top", "padding-right", "padding-bottom", "padding-left"),
    "border-width": (
        "border-top-width",
        "border-right-width",
        "border-bottom-width",
        "border-left-width",
    ),
    "border-color": (
        "border-top-color",
        "border-right-color",
        "border-bottom-color",
        "border-left-color",
    ),
}


def expand_shorthand(prop: str, value: Any) -> Dict[str, Any]:
    """Expand CSS shorthand properties into their longhands.

    Returns a dict of ``{longhand_name: raw_value}`` pairs.
    If *prop* is not a shorthand, returns ``{prop: value}``.
    """
    # --- Four-side shorthands ---
    if prop in _FOUR_SIDE_PROPS:
        top, right, bottom, left = _FOUR_SIDE_PROPS[prop]
        parts = _split_shorthand_parts(value)
        t, r, b, l = _expand_four(parts)
        return {top: t, right: r, bottom: b, left: l}

    # --- gap → row-gap + column-gap ---
    if prop == "gap":
        parts = _split_shorthand_parts(value)
        if len(parts) == 1:
            return {"row-gap": parts[0], "column-gap": parts[0]}
        return {"row-gap": parts[0], "column-gap": parts[1]}

    # --- border (simplified: width style color) ---
    if prop == "border":
        parts = _split_shorthand_parts(value)
        result: Dict[str, Any] = {}
        for p in parts:
            pv = parse_value(p)
            if isinstance(pv, (int, float)):
                for side in ("top", "right", "bottom", "left"):
                    result[f"border-{side}-width"] = p
            elif isinstance(pv, str) and (pv.startswith("#") or pv.startswith("rgb") or pv in NAMED_COLORS):
                for side in ("top", "right", "bottom", "left"):
                    result[f"border-{side}-color"] = p
            else:
                for side in ("top", "right", "bottom", "left"):
                    result[f"border-{side}-style"] = p
        return result if result else {prop: value}

    # --- outline (simplified: width style color) ---
    if prop == "outline":
        parts = _split_shorthand_parts(value)
        result2: Dict[str, Any] = {}
        for p in parts:
            pv = parse_value(p)
            if isinstance(pv, (int, float)):
                result2["outline-width"] = p
            elif isinstance(pv, str) and (pv.startswith("#") or pv.startswith("rgb") or pv in NAMED_COLORS):
                result2["outline-color"] = p
            else:
                result2["outline-style"] = p
        return result2 if result2 else {prop: value}

    # --- Not a shorthand ---
    return {prop: value}


def _split_shorthand_parts(value: Any) -> List[str]:
    """Split a shorthand value into its component parts."""
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    if isinstance(value, str):
        return value.split()
    return [str(value)]


def _expand_four(parts: List[str]) -> Tuple[str, str, str, str]:
    """Expand 1-4 parts into (top, right, bottom, left)."""
    n = len(parts)
    if n == 1:
        return (parts[0], parts[0], parts[0], parts[0])
    if n == 2:
        return (parts[0], parts[1], parts[0], parts[1])
    if n == 3:
        return (parts[0], parts[1], parts[2], parts[1])
    return (parts[0], parts[1], parts[2], parts[3])


# ---------------------------------------------------------------------------
# Track template parsing
# ---------------------------------------------------------------------------


def parse_track_template(raw: Any, reference_length: Optional[float] = None) -> list:
    """Parse a ``grid-template-columns`` / ``grid-template-rows`` value.

    Accepts a list of strings (``["200px", "1fr"]``) or a single
    space-separated string (``"200px 1fr"``).
    """
    if isinstance(raw, str):
        parts = raw.split()
    elif isinstance(raw, (list, tuple)):
        parts = list(raw)
    else:
        return [parse_value(raw, reference_length=reference_length)]

    return [parse_value(p, reference_length=reference_length) for p in parts]


# ---------------------------------------------------------------------------
# grid-template-areas parsing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AreaMapping:
    """Parsed result of ``grid-template-areas``.

    Attributes
    ----------
    areas : dict mapping area name → (row_start, col_start, row_span, col_span)
        Indices are **0-based**.
    num_rows : int
        Number of rows implied by the template.
    num_cols : int
        Number of columns implied by the template.
    """
    areas: Dict[str, Tuple[int, int, int, int]]
    num_rows: int
    num_cols: int


def parse_grid_template_areas(raw: Any) -> Optional[AreaMapping]:
    """Parse a ``grid-template-areas`` value.

    The CSS syntax is a series of quoted row strings, e.g.::

        "header header header"
        "sidebar main main"
        "footer footer footer"

    A single dot ``.`` represents an empty cell (unnamed).

    The value may be supplied as:
    * a single string with quoted substrings (CSS syntax)
    * a list of strings, each representing one row

    Returns ``None`` if the value is ``None`` or ``"none"``.
    Raises ``ValueError`` on malformed input (non-rectangular areas, etc.).
    """
    if raw is None or raw == "none":
        return None

    # Accept a list of row strings directly
    if isinstance(raw, (list, tuple)):
        row_strings = [str(r).strip() for r in raw]
    elif isinstance(raw, str):
        # Try to extract quoted strings first  ("header header" "main main")
        quoted = re.findall(r'"([^"]*)"', raw)
        if quoted:
            row_strings = [s.strip() for s in quoted]
        else:
            # Maybe it's a single-row template without quotes
            row_strings = [raw.strip()]
    else:
        return None

    if not row_strings:
        return None

    # Build the 2-D grid of cell names
    grid: List[List[str]] = []
    num_cols: Optional[int] = None
    for r_idx, row_str in enumerate(row_strings):
        tokens = row_str.split()
        if not tokens:
            continue
        if num_cols is None:
            num_cols = len(tokens)
        elif len(tokens) != num_cols:
            raise ValueError(
                f"grid-template-areas row {r_idx} has {len(tokens)} columns, "
                f"expected {num_cols}"
            )
        grid.append(tokens)

    if not grid or num_cols is None:
        return None

    num_rows = len(grid)

    # Collect each area name → list of (row, col) cells
    name_cells: Dict[str, List[Tuple[int, int]]] = {}
    for r in range(num_rows):
        for c in range(num_cols):
            name = grid[r][c]
            if name == ".":
                continue
            name_cells.setdefault(name, []).append((r, c))

    # Convert to rectangular area mappings
    areas: Dict[str, Tuple[int, int, int, int]] = {}
    for name, cells in name_cells.items():
        rows = [rc[0] for rc in cells]
        cols = [rc[1] for rc in cells]
        r_min, r_max = min(rows), max(rows)
        c_min, c_max = min(cols), max(cols)
        row_span = r_max - r_min + 1
        col_span = c_max - c_min + 1

        # Verify that the area forms a proper rectangle
        if len(cells) != row_span * col_span:
            raise ValueError(
                f"grid-template-areas: area '{name}' is not rectangular"
            )
        # Verify all cells in the bounding rect belong to this area
        for rr in range(r_min, r_max + 1):
            for cc in range(c_min, c_max + 1):
                if grid[rr][cc] != name:
                    raise ValueError(
                        f"grid-template-areas: area '{name}' is not rectangular "
                        f"(cell [{rr}][{cc}] is '{grid[rr][cc]}')"
                    )

        areas[name] = (r_min, c_min, row_span, col_span)

    return AreaMapping(areas=areas, num_rows=num_rows, num_cols=num_cols)
