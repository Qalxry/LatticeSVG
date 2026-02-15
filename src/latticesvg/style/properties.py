"""CSS property registry — default values, inheritance flags, and type hints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class PropertyDef:
    """Definition of a single CSS property."""

    default: Any
    """Default (initial) value — raw CSS string or Python object."""

    inheritable: bool = False
    """Whether this property is inherited from the parent element."""

    parser_hint: Optional[str] = None
    """Hint for the parser: 'length', 'color', 'keyword', 'track-list', etc."""


# ---------------------------------------------------------------------------
# Master registry
# ---------------------------------------------------------------------------

PROPERTY_REGISTRY: dict[str, PropertyDef] = {
    # ── Box model ──────────────────────────────────────────────────────
    "width": PropertyDef(default="auto", parser_hint="length"),
    "height": PropertyDef(default="auto", parser_hint="length"),
    "min-width": PropertyDef(default="0px", parser_hint="length"),
    "max-width": PropertyDef(default="none", parser_hint="length"),
    "min-height": PropertyDef(default="0px", parser_hint="length"),
    "max-height": PropertyDef(default="none", parser_hint="length"),

    # Margin (longhand — shorthands are expanded before lookup)
    "margin-top": PropertyDef(default="0px", parser_hint="length"),
    "margin-right": PropertyDef(default="0px", parser_hint="length"),
    "margin-bottom": PropertyDef(default="0px", parser_hint="length"),
    "margin-left": PropertyDef(default="0px", parser_hint="length"),

    # Padding
    "padding-top": PropertyDef(default="0px", parser_hint="length"),
    "padding-right": PropertyDef(default="0px", parser_hint="length"),
    "padding-bottom": PropertyDef(default="0px", parser_hint="length"),
    "padding-left": PropertyDef(default="0px", parser_hint="length"),

    # Border width
    "border-top-width": PropertyDef(default="0px", parser_hint="length"),
    "border-right-width": PropertyDef(default="0px", parser_hint="length"),
    "border-bottom-width": PropertyDef(default="0px", parser_hint="length"),
    "border-left-width": PropertyDef(default="0px", parser_hint="length"),

    # Border color
    "border-top-color": PropertyDef(default="none", parser_hint="color"),
    "border-right-color": PropertyDef(default="none", parser_hint="color"),
    "border-bottom-color": PropertyDef(default="none", parser_hint="color"),
    "border-left-color": PropertyDef(default="none", parser_hint="color"),

    # Border style (solid, dashed, …)
    "border-top-style": PropertyDef(default="none", parser_hint="keyword"),
    "border-right-style": PropertyDef(default="none", parser_hint="keyword"),
    "border-bottom-style": PropertyDef(default="none", parser_hint="keyword"),
    "border-left-style": PropertyDef(default="none", parser_hint="keyword"),

    # Border radius (shorthand is expanded into four longhands)
    "border-radius": PropertyDef(default="0px", parser_hint="length"),
    "border-top-left-radius": PropertyDef(default="0px", parser_hint="length"),
    "border-top-right-radius": PropertyDef(default="0px", parser_hint="length"),
    "border-bottom-right-radius": PropertyDef(default="0px", parser_hint="length"),
    "border-bottom-left-radius": PropertyDef(default="0px", parser_hint="length"),

    # Box sizing
    "box-sizing": PropertyDef(default="border-box", parser_hint="keyword"),

    # Outline (does not affect layout, drawn outside border-box)
    "outline-width": PropertyDef(default="0px", parser_hint="length"),
    "outline-color": PropertyDef(default="none", parser_hint="color"),
    "outline-style": PropertyDef(default="none", parser_hint="keyword"),
    "outline-offset": PropertyDef(default="0px", parser_hint="length"),

    # ── Grid layout ───────────────────────────────────────────────────
    "display": PropertyDef(default="block", parser_hint="keyword"),
    "grid-template-columns": PropertyDef(default=None, parser_hint="track-list"),
    "grid-template-rows": PropertyDef(default=None, parser_hint="track-list"),
    "row-gap": PropertyDef(default="0px", parser_hint="length"),
    "column-gap": PropertyDef(default="0px", parser_hint="length"),
    "justify-items": PropertyDef(default="stretch", parser_hint="keyword"),
    "align-items": PropertyDef(default="stretch", parser_hint="keyword"),
    "justify-self": PropertyDef(default="auto", parser_hint="keyword"),
    "align-self": PropertyDef(default="auto", parser_hint="keyword"),
    "grid-template-areas": PropertyDef(default=None, parser_hint="grid-areas"),
    "grid-auto-flow": PropertyDef(default="row", parser_hint="keyword"),
    "grid-auto-rows": PropertyDef(default="auto", parser_hint="track-list"),
    "grid-auto-columns": PropertyDef(default="auto", parser_hint="track-list"),
    "grid-row": PropertyDef(default=None, parser_hint="grid-line"),
    "grid-column": PropertyDef(default=None, parser_hint="grid-line"),
    "grid-area": PropertyDef(default=None, parser_hint="keyword"),

    # ── Text ──────────────────────────────────────────────────────────
    "font-family": PropertyDef(
        default="sans-serif", inheritable=True, parser_hint="font-family"
    ),
    "font-size": PropertyDef(
        default="16px", inheritable=True, parser_hint="length"
    ),
    "font-weight": PropertyDef(
        default="normal", inheritable=True, parser_hint="keyword"
    ),
    "font-style": PropertyDef(
        default="normal", inheritable=True, parser_hint="keyword"
    ),
    "text-align": PropertyDef(
        default="left", inheritable=True, parser_hint="keyword"
    ),
    "line-height": PropertyDef(
        default="1.2", inheritable=True, parser_hint="length"
    ),
    "white-space": PropertyDef(
        default="normal", inheritable=True, parser_hint="keyword"
    ),
    "overflow-wrap": PropertyDef(
        default="normal", inheritable=True, parser_hint="keyword"
    ),
    "word-break": PropertyDef(
        default="normal", inheritable=True, parser_hint="keyword"
    ),
    "color": PropertyDef(
        default="#000000", inheritable=True, parser_hint="color"
    ),
    "letter-spacing": PropertyDef(
        default="normal", inheritable=True, parser_hint="length"
    ),
    "word-spacing": PropertyDef(
        default="normal", inheritable=True, parser_hint="length"
    ),
    "text-decoration": PropertyDef(
        default="none", inheritable=False, parser_hint="keyword"
    ),
    "text-overflow": PropertyDef(default="clip", parser_hint="keyword"),
    "hyphens": PropertyDef(
        default="none", inheritable=True, parser_hint="keyword"
    ),
    "lang": PropertyDef(
        default="en", inheritable=True, parser_hint="keyword"
    ),

    # ── Visual ────────────────────────────────────────────────────────
    "background-color": PropertyDef(default="none", parser_hint="color"),
    "background-image": PropertyDef(default="none", parser_hint="gradient"),
    "opacity": PropertyDef(default="1", parser_hint="length"),
    "overflow": PropertyDef(default="visible", parser_hint="keyword"),
    "clip-path": PropertyDef(default="none", parser_hint="clip-path"),
    "box-shadow": PropertyDef(default="none", parser_hint="box-shadow"),
    "transform": PropertyDef(default="none", parser_hint="transform"),
    "filter": PropertyDef(default="none", parser_hint="filter"),

    # ── Image ─────────────────────────────────────────────────────────
    "object-fit": PropertyDef(default="fill", parser_hint="keyword"),
}


def get_default(prop: str) -> Any:
    """Return the default value for a property, or ``None`` if unknown."""
    defn = PROPERTY_REGISTRY.get(prop)
    return defn.default if defn else None


def is_inheritable(prop: str) -> bool:
    """Return whether a property is inherited from the parent."""
    defn = PROPERTY_REGISTRY.get(prop)
    return defn.inheritable if defn else False
