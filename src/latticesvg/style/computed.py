"""ComputedStyle — resolved style object with inheritance and shorthand expansion."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .parser import (
    AUTO,
    FrValue,
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

    __slots__ = ("_values",)

    def __init__(
        self,
        raw: Optional[Dict[str, Any]] = None,
        parent_style: Optional["ComputedStyle"] = None,
    ) -> None:
        self._values: Dict[str, Any] = {}

        # 1. Inherit inheritable properties from parent
        if parent_style is not None:
            for prop, defn in PROPERTY_REGISTRY.items():
                if defn.inheritable:
                    self._values[prop] = parent_style.get(prop)

        # 2. Apply defaults for all non-inherited properties
        for prop, defn in PROPERTY_REGISTRY.items():
            if prop not in self._values:
                self._values[prop] = parse_value(defn.default) if defn.default is not None else None

        # 3. Parse & expand user-supplied values
        if raw:
            # Resolve font-size first (needed for em units)
            if "font-size" in raw:
                parent_fs = parent_style.get("font-size") if parent_style else 16.0
                self._values["font-size"] = parse_value(
                    raw["font-size"], font_size=parent_fs
                )

            font_size = self._values.get("font-size", 16.0)
            if not isinstance(font_size, (int, float)):
                font_size = 16.0

            for prop, val in raw.items():
                if prop == "font-size":
                    continue  # already handled

                expanded = expand_shorthand(prop, val)
                for long_prop, long_val in expanded.items():
                    if PROPERTY_REGISTRY.get(long_prop, None) is not None:
                        hint = PROPERTY_REGISTRY[long_prop].parser_hint
                        if hint == "track-list":
                            self._values[long_prop] = parse_track_template(long_val)
                        elif hint == "grid-areas":
                            self._values[long_prop] = parse_grid_template_areas(long_val)
                        elif hint == "clip-path":
                            self._values[long_prop] = parse_clip_path(long_val)
                        elif hint == "gradient":
                            self._values[long_prop] = parse_gradient(long_val)
                        elif hint == "box-shadow":
                            self._values[long_prop] = parse_box_shadow(long_val)
                        elif hint == "transform":
                            self._values[long_prop] = parse_transform(long_val)
                        elif hint == "filter":
                            self._values[long_prop] = parse_filter(long_val)
                        else:
                            self._values[long_prop] = parse_value(
                                long_val, font_size=font_size
                            )
                    else:
                        # Unknown property — store as-is
                        self._values[long_prop] = parse_value(
                            long_val, font_size=font_size
                        )

    # -----------------------------------------------------------------
    # Access helpers
    # -----------------------------------------------------------------

    def get(self, prop: str, default: Any = None) -> Any:
        """Get a property value by its CSS name (e.g. ``'font-size'``)."""
        return self._values.get(prop, default)

    def set(self, prop: str, value: Any) -> None:
        """Override a computed property value."""
        self._values[prop] = value

    def resolve_percentages(self, ref_width: float, ref_height: Optional[float] = None) -> None:
        """Resolve any remaining ``_Percentage`` values."""
        for prop, val in list(self._values.items()):
            if isinstance(val, _Percentage):
                # Choose reference based on property axis
                if "height" in prop or "top" in prop or "bottom" in prop:
                    ref = ref_height if ref_height is not None else ref_width
                else:
                    ref = ref_width
                self._values[prop] = val.resolve(ref)

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
