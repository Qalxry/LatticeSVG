"""Text shaping — line breaking, alignment, and overflow handling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .font import FontManager


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class Line:
    """A single line of shaped text."""
    text: str
    width: float          # measured width in px
    x_offset: float = 0.0 # horizontal offset after alignment
    char_count: int = 0


# ---------------------------------------------------------------------------
# Core measurement
# ---------------------------------------------------------------------------


def measure_text(
    text: str,
    font_path: str,
    size: int,
    *,
    fm: Optional[FontManager] = None,
) -> float:
    """Return the total advance width of *text* in pixels."""
    if fm is None:
        fm = FontManager.instance()
    total = 0.0
    for ch in text:
        gm = fm.glyph_metrics(font_path, size, ch)
        total += gm.advance_x
    return total


def measure_word(
    word: str,
    font_path: str,
    size: int,
    *,
    fm: Optional[FontManager] = None,
) -> float:
    """Measure a single word's advance width."""
    return measure_text(word, font_path, size, fm=fm)


# ---------------------------------------------------------------------------
# Line breaking
# ---------------------------------------------------------------------------


def break_lines(
    text: str,
    available_width: float,
    font_path: str,
    size: int,
    white_space: str = "normal",
    *,
    fm: Optional[FontManager] = None,
) -> List[Line]:
    """Break *text* into lines that fit within *available_width*.

    Parameters
    ----------
    white_space : str
        ``'normal'`` — collapse whitespace, wrap at word boundaries.
        ``'nowrap'`` — collapse whitespace, no wrapping.
        ``'pre'``    — preserve whitespace and newlines, no wrapping.
        ``'pre-wrap'`` — preserve whitespace, wrap if needed.
    """
    if fm is None:
        fm = FontManager.instance()

    if white_space == "pre":
        return _break_pre(text, font_path, size, fm, wrap=False)
    if white_space == "pre-wrap":
        return _break_pre(text, font_path, size, fm, wrap=True, available_width=available_width)
    if white_space == "nowrap":
        # Collapse whitespace, single line
        collapsed = " ".join(text.split())
        w = measure_text(collapsed, font_path, size, fm=fm)
        return [Line(text=collapsed, width=w, char_count=len(collapsed))]

    # white_space == "normal" — default
    return _break_normal(text, available_width, font_path, size, fm)


def _break_normal(
    text: str,
    available_width: float,
    font_path: str,
    size: int,
    fm: FontManager,
) -> List[Line]:
    """Greedy line-breaking for 'normal' white-space mode."""
    # Collapse whitespace
    collapsed = " ".join(text.split())
    if not collapsed:
        return [Line(text="", width=0.0, char_count=0)]

    words = collapsed.split(" ")
    lines: List[Line] = []
    current_words: List[str] = []
    current_width = 0.0
    space_width = measure_text(" ", font_path, size, fm=fm)

    for word in words:
        word_width = measure_text(word, font_path, size, fm=fm)
        needed = word_width if not current_words else current_width + space_width + word_width
        if current_words and needed > available_width:
            # Flush current line
            line_text = " ".join(current_words)
            lines.append(Line(text=line_text, width=current_width, char_count=len(line_text)))
            current_words = [word]
            current_width = word_width
        else:
            if current_words:
                current_width += space_width + word_width
            else:
                current_width = word_width
            current_words.append(word)

    # Flush remainder
    if current_words:
        line_text = " ".join(current_words)
        lines.append(Line(text=line_text, width=current_width, char_count=len(line_text)))

    return lines if lines else [Line(text="", width=0.0, char_count=0)]


def _break_pre(
    text: str,
    font_path: str,
    size: int,
    fm: FontManager,
    wrap: bool = False,
    available_width: float = float("inf"),
) -> List[Line]:
    """Line-breaking for 'pre'/'pre-wrap' white-space mode."""
    raw_lines = text.split("\n")
    result: List[Line] = []
    for raw in raw_lines:
        if not wrap or available_width == float("inf"):
            w = measure_text(raw, font_path, size, fm=fm)
            result.append(Line(text=raw, width=w, char_count=len(raw)))
        else:
            # Character-level wrapping for pre-wrap
            current = ""
            current_w = 0.0
            for ch in raw:
                cw = fm.glyph_metrics(font_path, size, ch).advance_x
                if current and current_w + cw > available_width:
                    result.append(Line(text=current, width=current_w, char_count=len(current)))
                    current = ch
                    current_w = cw
                else:
                    current += ch
                    current_w += cw
            result.append(Line(text=current, width=current_w, char_count=len(current)))
    return result if result else [Line(text="", width=0.0, char_count=0)]


# ---------------------------------------------------------------------------
# Alignment
# ---------------------------------------------------------------------------


def align_lines(
    lines: List[Line],
    available_width: float,
    text_align: str = "left",
) -> List[Line]:
    """Set ``x_offset`` on each line based on *text_align*.

    Does **not** mutate the input list; returns a new list.
    """
    result: List[Line] = []
    for line in lines:
        offset = 0.0
        if text_align == "center":
            offset = (available_width - line.width) / 2.0
        elif text_align == "right":
            offset = available_width - line.width
        elif text_align == "justify" and line is not lines[-1]:
            offset = 0.0  # justify handled per-word at render time
        result.append(Line(
            text=line.text,
            width=line.width,
            x_offset=max(0.0, offset),
            char_count=line.char_count,
        ))
    return result


# ---------------------------------------------------------------------------
# Text block sizing
# ---------------------------------------------------------------------------


def compute_text_block_size(
    lines: List[Line],
    line_height: float,
    font_size: float,
) -> tuple:
    """Return ``(width, height)`` of a text block.

    *line_height* is either a multiplier (e.g. 1.5) or absolute px value.
    If multiplier (≤ 5), it's relative to *font_size*.
    """
    if line_height <= 5.0:
        # Treat as multiplier
        lh = font_size * line_height
    else:
        lh = line_height

    max_width = max((l.width for l in lines), default=0.0)
    total_height = lh * len(lines) if lines else 0.0
    return (max_width, total_height)


def get_min_content_width(
    text: str,
    font_path: str,
    size: int,
    white_space: str = "normal",
    *,
    fm: Optional[FontManager] = None,
) -> float:
    """Return the minimum content width — the width of the longest word."""
    if fm is None:
        fm = FontManager.instance()
    if white_space in ("pre", "nowrap"):
        return measure_text(text, font_path, size, fm=fm)
    words = text.split()
    if not words:
        return 0.0
    return max(measure_text(w, font_path, size, fm=fm) for w in words)


def get_max_content_width(
    text: str,
    font_path: str,
    size: int,
    white_space: str = "normal",
    *,
    fm: Optional[FontManager] = None,
) -> float:
    """Return the max-content width — text on a single line."""
    if fm is None:
        fm = FontManager.instance()
    if white_space == "pre":
        # Longest physical line
        raw_lines = text.split("\n")
        return max((measure_text(l, font_path, size, fm=fm) for l in raw_lines), default=0.0)
    collapsed = " ".join(text.split())
    return measure_text(collapsed, font_path, size, fm=fm)
