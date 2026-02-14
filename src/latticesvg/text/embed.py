"""Font subsetting and embedding for self-contained SVG output.

Collects all characters used per font path from the laid-out node tree,
creates WOFF2 subsets via *fontTools*, and generates ``@font-face`` CSS
rules that are injected into the ``drawsvg.Drawing``.

Requires the optional ``fonttools`` package (with the ``brotli`` extension
for WOFF2 compression).  When these are unavailable, the module raises
``ImportError`` at call time — it is never imported unconditionally.
"""

from __future__ import annotations

import base64
import io
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    import drawsvg as dw
    from ..nodes.base import Node

log = logging.getLogger(__name__)


# -----------------------------------------------------------------------
# Data structures
# -----------------------------------------------------------------------

@dataclass
class _FontUsage:
    """Accumulated character usage for a single font file."""
    font_path: str
    css_family: str
    css_weight: str = "normal"          # "normal" | "bold"
    css_style: str = "normal"           # "normal" | "italic"
    chars: Set[str] = field(default_factory=set)


# -----------------------------------------------------------------------
# Collecting character usage from the node tree
# -----------------------------------------------------------------------

def _collect_font_usage(root: "Node") -> Dict[str, _FontUsage]:
    """Walk the laid-out node tree and return ``{font_path: _FontUsage}``."""
    from ..nodes.text import TextNode
    from ..nodes.grid import GridContainer
    from .font import FontManager

    fm = FontManager.instance()
    usage: Dict[str, _FontUsage] = {}

    def _ensure(font_path: str, weight: str = "normal", style: str = "normal") -> _FontUsage:
        """Get or create a ``_FontUsage`` entry for *font_path*."""
        if font_path in usage:
            return usage[font_path]
        css_name = fm.font_family_name(font_path) or Path(font_path).stem
        u = _FontUsage(
            font_path=font_path,
            css_family=css_name,
            css_weight=weight,
            css_style=style,
        )
        usage[font_path] = u
        return u

    def _add_chars(chain: list, chars: str, weight: str = "normal", style: str = "normal") -> None:
        """Assign each character to the first font in *chain* that has it."""
        if not chain:
            return
        for ch in chars:
            placed = False
            for fp in chain:
                if fm._has_glyph(fp, ch):
                    _ensure(fp, weight, style).chars.add(ch)
                    placed = True
                    break
            if not placed:
                # .notdef — add to primary font so subset still works
                _ensure(chain[0], weight, style).chars.add(ch)

    def _walk(node: "Node") -> None:
        if isinstance(node, TextNode):
            _process_text_node(node, fm, _add_chars)
        if isinstance(node, GridContainer):
            for child in node.children:
                _walk(child)

    _walk(root)
    return usage


def _process_text_node(node, fm, _add_chars) -> None:
    """Extract characters from a single ``TextNode`` and feed them to *_add_chars*."""
    from ..markup.parser import TextSpan

    chain: list = getattr(node, "_resolved_font_chain", None) or []
    if not chain:
        return

    base_weight = node.style.get("font-weight") or "normal"
    base_style = node.style.get("font-style") or "normal"

    rich_lines = getattr(node, "_rich_lines", None)
    if rich_lines:
        # Rich text — per-fragment chain
        spans = getattr(node, "_spans", None) or []
        font_size = node._font_size_int()

        for rline in rich_lines:
            for frag in rline.fragments:
                if frag.svg_fragment is not None:
                    continue  # math SVG — no font chars
                if not frag.text:
                    continue

                span_src = spans[frag.span_index] if frag.span_index < len(spans) else None

                # Determine weight / style for this fragment
                w = base_weight
                st = base_style
                frag_chain = chain

                if span_src:
                    if span_src.font_weight:
                        w = span_src.font_weight
                    if span_src.font_style:
                        st = span_src.font_style
                    # If span overrides family/weight/style, resolve its own chain
                    if span_src.font_family or span_src.font_weight or span_src.font_style:
                        families: list = []
                        if span_src.font_family:
                            families = [f.strip().strip('"').strip("'")
                                        for f in span_src.font_family.split(",") if f.strip()]
                        if not families:
                            for fp in chain:
                                n = fm.font_family_name(fp)
                                if n and n not in families:
                                    families.append(n)
                            if not families:
                                families = ["sans-serif"]
                        resolved = fm.find_font_chain(
                            families,
                            weight=span_src.font_weight or "normal",
                            style=span_src.font_style or "normal",
                        )
                        if resolved:
                            frag_chain = resolved

                _add_chars(frag_chain, frag.text, w, st)
    else:
        # Plain text
        lines = getattr(node, "lines", None) or []
        all_text = "".join(line.text for line in lines)
        _add_chars(chain, all_text, base_weight, base_style)


# -----------------------------------------------------------------------
# Font subsetting
# -----------------------------------------------------------------------

def _subset_font_woff2(font_path: str, chars: Set[str], face_index: int = 0) -> bytes:
    """Subset *font_path* to include only *chars*, return WOFF2 bytes.

    Falls back to raw OpenType (OTF/TTF) bytes if ``brotli`` is not
    installed.
    """
    from fontTools.ttLib import TTFont
    from fontTools.subset import Subsetter, Options

    font = TTFont(font_path, fontNumber=face_index)

    options = Options()
    options.desubroutinize = True
    # Retain glyph names for better debuggability, but drop unused tables
    options.name_IDs = ["*"]
    options.name_languages = ["*"]

    subsetter = Subsetter(options=options)
    text = "".join(sorted(chars))
    subsetter.populate(text=text)
    subsetter.subset(font)

    buf = io.BytesIO()
    try:
        font.flavor = "woff2"
        font.save(buf)
        fmt = "woff2"
    except ImportError:
        # brotli not available — fall back to raw OTF
        log.warning(
            "brotli not installed; embedding fonts as raw OpenType "
            "instead of WOFF2.  Install brotli for smaller SVG output."
        )
        font.flavor = None
        font.save(buf)
        fmt = "opentype"

    return buf.getvalue(), fmt


def _font_weight_from_path(font_path: str) -> str:
    """Guess CSS font-weight from font metadata."""
    from .font import FontManager, _FreeTypeBackend
    fm = FontManager.instance()
    if isinstance(fm._backend, _FreeTypeBackend):
        try:
            face = fm._backend._freetype.Face(font_path)
            style = face.style_name
            if isinstance(style, bytes):
                style = style.decode("utf-8", errors="replace")
            low = style.lower()
            if "bold" in low:
                return "bold"
        except Exception:
            pass
    # Fallback: check filename
    stem = Path(font_path).stem.lower()
    if "bold" in stem:
        return "bold"
    return "normal"


def _font_style_from_path(font_path: str) -> str:
    """Guess CSS font-style from font metadata."""
    from .font import FontManager, _FreeTypeBackend
    fm = FontManager.instance()
    if isinstance(fm._backend, _FreeTypeBackend):
        try:
            face = fm._backend._freetype.Face(font_path)
            style = face.style_name
            if isinstance(style, bytes):
                style = style.decode("utf-8", errors="replace")
            low = style.lower()
            if "italic" in low or "oblique" in low:
                return "italic"
        except Exception:
            pass
    stem = Path(font_path).stem.lower()
    if "italic" in stem or "oblique" in stem:
        return "italic"
    return "normal"


# -----------------------------------------------------------------------
# CSS generation
# -----------------------------------------------------------------------

def _generate_font_face_css(usage_map: Dict[str, _FontUsage]) -> str:
    """Generate ``@font-face`` CSS rules from the usage map.

    Multiple font paths that share the same CSS
    ``(font-family, font-weight, font-style)`` triplet are merged:
    their character sets are combined and the first font path is used
    for subsetting.
    """
    # ── Step 1: Group by CSS triplet  ──────────────────────────────
    # key = (css_family, css_weight, css_style)
    # value = (font_path, merged_chars)
    merged: Dict[tuple, tuple] = {}  # triplet → (font_path, chars)

    for font_path, usg in usage_map.items():
        if not usg.chars:
            continue
        weight = _font_weight_from_path(font_path)
        style = _font_style_from_path(font_path)
        triplet = (usg.css_family, weight, style)

        if triplet in merged:
            existing_path, existing_chars = merged[triplet]
            merged[triplet] = (existing_path, existing_chars | usg.chars)
        else:
            merged[triplet] = (font_path, set(usg.chars))

    # ── Step 2: Subset and emit CSS rules ─────────────────────────
    rules: List[str] = []

    for (css_family, weight, style), (font_path, chars) in merged.items():
        if not chars:
            continue

        try:
            data, fmt = _subset_font_woff2(font_path, chars)
        except Exception as exc:
            log.warning("Failed to subset %s: %s", font_path, exc)
            continue

        b64 = base64.b64encode(data).decode("ascii")

        if fmt == "woff2":
            mime = "font/woff2"
            fmt_hint = 'format("woff2")'
        else:
            mime = "font/otf"
            fmt_hint = 'format("opentype")'

        rule = (
            f"@font-face {{\n"
            f'  font-family: "{css_family}";\n'
            f"  font-weight: {weight};\n"
            f"  font-style: {style};\n"
            f"  src: url(data:{mime};base64,{b64}) {fmt_hint};\n"
            f"}}"
        )
        rules.append(rule)

    return "\n".join(rules)


# -----------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------

def embed_fonts(drawing: "dw.Drawing", root: "Node") -> None:
    """Collect used glyphs, subset fonts, and embed ``@font-face`` rules.

    Modifies *drawing* in place by appending CSS via
    ``drawing.append_css()``.

    Raises ``ImportError`` if *fonttools* is not installed.
    """
    # Eagerly check for fonttools
    try:
        from fontTools.ttLib import TTFont  # noqa: F401
        from fontTools.subset import Subsetter  # noqa: F401
    except ImportError:
        raise ImportError(
            "fonttools is required for font embedding.  "
            "Install it with:  pip install fonttools"
        ) from None

    usage = _collect_font_usage(root)
    if not usage:
        return

    css = _generate_font_face_css(usage)
    if css:
        drawing.append_css(css)
