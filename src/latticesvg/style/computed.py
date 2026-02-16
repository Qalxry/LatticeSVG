"""ComputedStyle — resolved style object with inheritance and shorthand expansion."""

from __future__ import annotations

import warnings
from typing import Any, Dict, Optional

from .parser import (
    AUTO,
    FrValue,
    LineHeightMultiplier,
    _Percentage,
    expand_shorthand,
    parse_box_shadow,
    parse_clip_path,
    parse_filter,
    parse_gradient,
    parse_grid_template_areas,
    parse_track_template,
    parse_transform,
    parse_value,
)
from .properties import PROPERTY_REGISTRY, get_default, is_inheritable

import re

# CSS shorthand properties recognised by ``expand_shorthand()``.
# They are *not* in ``PROPERTY_REGISTRY`` (only longhands live there)
# but are perfectly valid user-supplied names.
_KNOWN_SHORTHANDS = frozenset({
    "margin", "padding", "border-width", "border-color",
    "gap", "border", "outline", "border-radius", "background",
    "border-top", "border-right", "border-bottom", "border-left",
})

_RE_HAS_UNIT = re.compile(r"[a-zA-Z]+\s*$")


def _parse_line_height(raw: Any, *, font_size: float = 16.0) -> Any:
    """Parse a ``line-height`` value, preserving the multiplier vs absolute distinction.

    * A bare number (``1.5``, ``"1.5"``) → ``LineHeightMultiplier(1.5)``
    * A length with a unit (``"24px"``, ``"1.5em"``) → ``float`` (absolute px)
    * The keyword ``"normal"`` → ``LineHeightMultiplier(1.2)``
    """
    if isinstance(raw, LineHeightMultiplier):
        return raw
    if isinstance(raw, (int, float)):
        return LineHeightMultiplier(float(raw))
    if not isinstance(raw, str):
        return LineHeightMultiplier(1.2)
    s = raw.strip()
    if s.lower() == "normal":
        return LineHeightMultiplier(1.2)
    # Check if the string has a unit suffix (px, em, rem, pt, %)
    if _RE_HAS_UNIT.search(s):
        # Has a unit → parse as a normal length, returns absolute px
        return parse_value(s, font_size=font_size)
    # Bare number (no unit) → multiplier
    try:
        return LineHeightMultiplier(float(s))
    except ValueError:
        return LineHeightMultiplier(1.2)


class ComputedStyle:
    """Holds fully-resolved CSS property values for a single node.

    Construction
    ------------
    >>> style = ComputedStyle({"width": "200px", "padding": "10px"}, parent_style=None)
    >>> style.width          # 200.0
    >>> style.padding_top    # 10.0

    Attribute access maps underscores to hyphens so ``style.font_size``
    reads the ``font-size`` property.
    """

    __slots__ = ("_values", "_raw", "_explicit_props", "_pct_originals")

    def __init__(
        self,
        raw: Optional[Dict[str, Any]] = None,
        parent_style: Optional["ComputedStyle"] = None,
    ) -> None:
        self._values: Dict[str, Any] = {}
        self._raw: Optional[Dict[str, Any]] = raw
        self._explicit_props: set = set()
        self._pct_originals: Optional[Dict[str, _Percentage]] = None

        # 1. Inherit inheritable properties from parent
        if parent_style is not None:
            for prop, defn in PROPERTY_REGISTRY.items():
                if defn.inheritable:
                    self._values[prop] = parent_style.get(prop)

        # 2. Apply defaults for all non-inherited properties
        for prop, defn in PROPERTY_REGISTRY.items():
            if prop not in self._values:
                if defn.default is not None:
                    if defn.parser_hint == "line-height":
                        self._values[prop] = _parse_line_height(defn.default)
                    else:
                        self._values[prop] = parse_value(defn.default)
                else:
                    self._values[prop] = None

        # 3. Parse & expand user-supplied values
        if raw:
            # Resolve font-size first (needed for em units)
            if "font-size" in raw:
                parent_fs = parent_style.get("font-size") if parent_style else 16.0
                self._values["font-size"] = parse_value(
                    raw["font-size"], font_size=parent_fs
                )
                self._explicit_props.add("font-size")

            font_size = self._values.get("font-size", 16.0)
            if not isinstance(font_size, (int, float)):
                font_size = 16.0

            for prop, val in raw.items():
                if prop == "font-size":
                    continue  # already handled

                # Warn about unknown CSS properties (P1-3)
                if (prop not in PROPERTY_REGISTRY
                        and prop not in _KNOWN_SHORTHANDS):
                    warnings.warn(
                        f"Unknown CSS property: '{prop}'",
                        stacklevel=3,
                    )

                expanded = expand_shorthand(prop, val)
                for long_prop, long_val in expanded.items():
                    self._explicit_props.add(long_prop)
                    self._values[long_prop] = self._parse_prop(
                        long_prop, long_val, font_size
                    )

            # Warn about margin (parsed but not applied in grid layout)
            _MARGIN_PROPS = {"margin", "margin-top", "margin-right",
                             "margin-bottom", "margin-left"}
            used_margins = _MARGIN_PROPS & set(raw.keys())
            if used_margins:
                warnings.warn(
                    f"margin properties ({', '.join(sorted(used_margins))}) are "
                    "parsed but not applied during grid layout. Use 'gap' or "
                    "'padding' for spacing instead.",
                    stacklevel=3,
                )

    # -----------------------------------------------------------------
    # Access helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _parse_prop(prop: str, raw_val: Any, font_size: float) -> Any:
        """Parse a single longhand property value according to its registry hint."""
        defn = PROPERTY_REGISTRY.get(prop)
        if defn is not None:
            hint = defn.parser_hint
            if hint == "track-list":
                return parse_track_template(raw_val)
            if hint == "grid-areas":
                return parse_grid_template_areas(raw_val)
            if hint == "clip-path":
                return parse_clip_path(raw_val)
            if hint == "gradient":
                return parse_gradient(raw_val)
            if hint == "box-shadow":
                return parse_box_shadow(raw_val)
            if hint == "transform":
                return parse_transform(raw_val)
            if hint == "filter":
                return parse_filter(raw_val)
            if hint == "line-height":
                return _parse_line_height(raw_val, font_size=font_size)
            return parse_value(raw_val, font_size=font_size, root_font_size=16.0)
        return parse_value(raw_val, font_size=font_size, root_font_size=16.0)

    def get(self, prop: str, default: Any = None) -> Any:
        """Get a property value by its CSS name (e.g. ``'font-size'``)."""
        return self._values.get(prop, default)

    def set(self, prop: str, value: Any) -> None:
        """Set a CSS property, with shorthand expansion and value parsing.

        Supports both longhand and shorthand properties::

            style.set("padding", "10px 20px")      # expands to 4 longhands
            style.set("border", "1px solid red")    # expands to 12 longhands
            style.set("font-size", "18px")          # parsed to float 18.0
            style.set("width", 200)                 # numeric values kept as-is
        """
        # Warn about unknown CSS properties (P1-3)
        if prop not in PROPERTY_REGISTRY and prop not in _KNOWN_SHORTHANDS:
            warnings.warn(
                f"Unknown CSS property: '{prop}'",
                stacklevel=2,
            )

        font_size = self._values.get("font-size", 16.0)
        if not isinstance(font_size, (int, float)):
            font_size = 16.0

        expanded = expand_shorthand(prop, value)
        for long_prop, long_val in expanded.items():
            self._explicit_props.add(long_prop)
            self._values[long_prop] = self._parse_prop(long_prop, long_val, font_size)

    def __setattr__(self, name: str, value: Any) -> None:
        # Allow normal slot assignment for internal attributes
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        # Map Python attribute name to CSS property name
        css_name = name.replace("_", "-")
        self.set(css_name, value)

    def _rebind_parent(self, parent_style: "ComputedStyle") -> None:
        """Re-inherit inheritable properties from *parent_style*.

        Only updates properties that were **not** explicitly set by the
        user (via the constructor *raw* dict or :meth:`set`).
        """
        for prop, defn in PROPERTY_REGISTRY.items():
            if defn.inheritable and prop not in self._explicit_props:
                self._values[prop] = parent_style.get(prop)

    def resolve_percentages(self, ref_width: float, ref_height: Optional[float] = None) -> None:
        """Resolve any remaining ``_Percentage`` values.

        The original ``_Percentage`` instances are preserved internally so
        that this method can be called again with different reference
        dimensions (e.g. when ``layout()`` is invoked multiple times).
        """
        for prop, val in list(self._values.items()):
            pct = val
            # If already resolved, check for the stashed original
            if not isinstance(pct, _Percentage):
                pct = self._pct_originals.get(prop) if self._pct_originals else None
            if isinstance(pct, _Percentage):
                # Choose reference based on property axis
                if "height" in prop or "top" in prop or "bottom" in prop:
                    ref = ref_height if ref_height is not None else ref_width
                else:
                    ref = ref_width
                # Stash original _Percentage before overwriting
                if self._pct_originals is None:
                    self._pct_originals = {}
                self._pct_originals[prop] = pct
                self._values[prop] = pct.resolve(ref)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        css_name = name.replace("_", "-")
        if css_name in self._values:
            return self._values[css_name]
        # Also try the original name
        if name in self._values:
            return self._values[name]
        raise AttributeError(f"No CSS property '{css_name}'")

    def __repr__(self) -> str:
        interesting = {
            k: v
            for k, v in self._values.items()
            if v is not None
            and v != get_default(k)
        }
        return f"ComputedStyle({interesting})"

    # -----------------------------------------------------------------
    # Convenience box-model accessors (return float, default 0)
    # -----------------------------------------------------------------

    def _float(self, prop: str) -> float:
        v = self._values.get(prop, 0)
        return float(v) if isinstance(v, (int, float)) else 0.0

    @property
    def margin_top(self) -> float:
        return self._float("margin-top")

    @property
    def margin_right(self) -> float:
        return self._float("margin-right")

    @property
    def margin_bottom(self) -> float:
        return self._float("margin-bottom")

    @property
    def margin_left(self) -> float:
        return self._float("margin-left")

    @property
    def padding_top(self) -> float:
        return self._float("padding-top")

    @property
    def padding_right(self) -> float:
        return self._float("padding-right")

    @property
    def padding_bottom(self) -> float:
        return self._float("padding-bottom")

    @property
    def padding_left(self) -> float:
        return self._float("padding-left")

    @property
    def border_top_width(self) -> float:
        return self._float("border-top-width")

    @property
    def border_right_width(self) -> float:
        return self._float("border-right-width")

    @property
    def border_bottom_width(self) -> float:
        return self._float("border-bottom-width")

    @property
    def border_left_width(self) -> float:
        return self._float("border-left-width")

    @property
    def padding_horizontal(self) -> float:
        return self.padding_left + self.padding_right

    @property
    def padding_vertical(self) -> float:
        return self.padding_top + self.padding_bottom

    @property
    def border_horizontal(self) -> float:
        return self.border_left_width + self.border_right_width

    @property
    def border_vertical(self) -> float:
        return self.border_top_width + self.border_bottom_width

    @property
    def margin_horizontal(self) -> float:
        return self.margin_left + self.margin_right

    @property
    def margin_vertical(self) -> float:
        return self.margin_top + self.margin_bottom

    # -----------------------------------------------------------------
    # Border-radius corner accessors
    # -----------------------------------------------------------------

    @property
    def border_top_left_radius(self) -> float:
        return self._float("border-top-left-radius")

    @property
    def border_top_right_radius(self) -> float:
        return self._float("border-top-right-radius")

    @property
    def border_bottom_right_radius(self) -> float:
        return self._float("border-bottom-right-radius")

    @property
    def border_bottom_left_radius(self) -> float:
        return self._float("border-bottom-left-radius")

    @property
    def border_radii(self) -> tuple:
        """Return ``(top-left, top-right, bottom-right, bottom-left)`` radii."""
        return (
            self.border_top_left_radius,
            self.border_top_right_radius,
            self.border_bottom_right_radius,
            self.border_bottom_left_radius,
        )

    @property
    def has_uniform_radius(self) -> bool:
        """True when all four corner radii are equal."""
        r = self.border_radii
        return r[0] == r[1] == r[2] == r[3]
