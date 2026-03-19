import contextlib
import copy
from typing import Any, Dict, List, Optional

from .font import FontInfo, FontManager, GlyphMetrics, parse_font_families
from .shaper import (
    measure_text,
    break_lines,
    align_lines,
    compute_text_block_size,
    # Vertical text support
    Column,
    VerticalRun,
    measure_text_vertical,
    break_columns,
    align_columns,
    compute_vertical_block_size,
)


def get_font_path(
    family: str,
    weight: str = "normal",
    style: str = "normal",
):
    """Convenience wrapper for :meth:`FontManager.get_font_path`."""
    return FontManager.instance().get_font_path(family, weight, style)


def list_fonts():
    """Convenience wrapper for :meth:`FontManager.list_fonts`."""
    return FontManager.instance().list_fonts()


# ── matplotlib font helpers ───────────────────────────────────────


def _build_mpl_rc(
    font_family: str,
    weight: str = "normal",
    style: str = "normal",
) -> tuple:
    """Build ``(rc_dict, font_paths)`` from a CSS ``font-family`` value.

    *rc_dict* is ready for :func:`matplotlib.rc_context` or
    ``rcParams.update()``.  *font_paths* must be registered with
    :func:`_register_mpl_fonts` before the overrides take effect.
    """
    from .font import _GENERIC_FAMILIES

    families = parse_font_families(font_family)

    generic = "sans-serif"
    for fam in reversed(families):
        if fam.lower() in _GENERIC_FAMILIES:
            generic = fam.lower()
            break

    fm = FontManager.instance()
    chain = fm.find_font_chain(families, weight=weight, style=style)

    mpl_names: List[str] = []
    seen: set = set()
    for path in chain:
        name = fm.font_family_name(path)
        if name and name not in seen:
            seen.add(name)
            mpl_names.append(name)

    rc: Dict[str, Any] = {
        "svg.fonttype": "path",
        "axes.unicode_minus": False,
    }
    if mpl_names:
        # Set font.family to the concrete name list so that
        # matplotlib's _find_fonts_by_props iterates each entry
        # and builds an FT2Font with _fallback_list — enabling
        # per-glyph fallback (e.g. Latin from Arial, CJK from YaHei).
        rc["font.family"] = mpl_names
        # Also populate generic family lists so that pre-existing
        # text elements (whose FontProperties default to e.g.
        # "sans-serif") can still resolve to our fonts.
        for generic_key in ("font.sans-serif", "font.serif", "font.monospace"):
            rc[generic_key] = mpl_names

    return rc, chain


def _register_mpl_fonts(font_paths: List[str]) -> None:
    """Register LatticeSVG-discovered font paths with matplotlib."""
    from matplotlib.font_manager import fontManager

    known = {fe.fname for fe in fontManager.ttflist}
    for path in font_paths:
        if path not in known:
            try:
                fontManager.addfont(path)
            except Exception:
                pass


_mpl_saved_rc: Optional[Dict[str, Any]] = None


def apply_mpl_fonts(
    font_family: str,
    weight: str = "normal",
    style: str = "normal",
) -> None:
    """Apply LatticeSVG font resolution to matplotlib's global ``rcParams``.

    Call :func:`restore_mpl_fonts` to revert to the previous state.

    Example::

        from latticesvg.text import apply_mpl_fonts, restore_mpl_fonts

        apply_mpl_fonts("Arial, Microsoft YaHei, sans-serif")
        # ... create figures ...
        restore_mpl_fonts()
    """
    import matplotlib

    global _mpl_saved_rc

    rc, paths = _build_mpl_rc(font_family, weight, style)

    _mpl_saved_rc = {
        key: copy.deepcopy(matplotlib.rcParams[key])
        for key in rc
        if key in matplotlib.rcParams
    }

    _register_mpl_fonts(paths)
    matplotlib.rcParams.update(rc)


def restore_mpl_fonts() -> None:
    """Restore matplotlib ``rcParams`` to the state before :func:`apply_mpl_fonts`."""
    import matplotlib

    global _mpl_saved_rc

    if _mpl_saved_rc is not None:
        for key, val in _mpl_saved_rc.items():
            matplotlib.rcParams[key] = val
        _mpl_saved_rc = None


@contextlib.contextmanager
def mpl_font_context(
    font_family: str,
    weight: str = "normal",
    style: str = "normal",
):
    """Context manager that temporarily applies LatticeSVG fonts to matplotlib.

    Example::

        from latticesvg.text import mpl_font_context

        with mpl_font_context("Arial, Microsoft YaHei, sans-serif"):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            ax.set_title("中英文混排 Title")
            fig.savefig("chart.svg")
    """
    import matplotlib

    rc, paths = _build_mpl_rc(font_family, weight, style)
    _register_mpl_fonts(paths)
    with matplotlib.rc_context(rc):
        yield


__all__ = [
    "FontInfo",
    "FontManager",
    "GlyphMetrics",
    "parse_font_families",
    "get_font_path",
    "list_fonts",
    "apply_mpl_fonts",
    "restore_mpl_fonts",
    "mpl_font_context",
    "measure_text",
    "break_lines",
    "align_lines",
    "compute_text_block_size",
    "Column",
    "VerticalRun",
    "measure_text_vertical",
    "break_columns",
    "align_columns",
    "compute_vertical_block_size",
]
