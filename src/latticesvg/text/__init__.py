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


__all__ = [
    "FontInfo",
    "FontManager",
    "GlyphMetrics",
    "parse_font_families",
    "get_font_path",
    "list_fonts",
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
