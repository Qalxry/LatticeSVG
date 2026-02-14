"""Text shaping — line breaking, alignment, and overflow handling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

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
# CJK detection
# ---------------------------------------------------------------------------

def _is_cjk_char(ch: str) -> bool:
    """Return True if *ch* is a CJK ideograph or fullwidth character."""
    cp = ord(ch)
    return (
        (0x4E00 <= cp <= 0x9FFF)   or  # CJK Unified Ideographs
        (0x3400 <= cp <= 0x4DBF)   or  # CJK Extension A
        (0x20000 <= cp <= 0x2A6DF) or  # CJK Extension B
        (0xF900 <= cp <= 0xFAFF)   or  # CJK Compatibility Ideographs
        (0x3000 <= cp <= 0x303F)   or  # CJK Symbols and Punctuation
        (0xFF01 <= cp <= 0xFF60)   or  # Fullwidth Latin / Punctuation
        (0xFFE0 <= cp <= 0xFFEF)   or  # Fullwidth signs
        (0x3040 <= cp <= 0x309F)   or  # Hiragana
        (0x30A0 <= cp <= 0x30FF)   or  # Katakana
        (0xAC00 <= cp <= 0xD7AF)   or  # Hangul Syllables
        (0x2E80 <= cp <= 0x2EFF)   or  # CJK Radicals Supplement
        (0x2F00 <= cp <= 0x2FDF)   or  # Kangxi Radicals
        (0xFE30 <= cp <= 0xFE4F)   or  # CJK Compatibility Forms
        (0x3200 <= cp <= 0x32FF)   or  # Enclosed CJK Letters
        (0x3300 <= cp <= 0x33FF)   or  # CJK Compatibility
        (0xFE10 <= cp <= 0xFE1F)       # Vertical Forms
    )


def _tokenize_breakable(text: str) -> List[Tuple[str, bool]]:
    """Split *text* into breakable segments.

    Each CJK character becomes its own segment (breakable).
    Consecutive non-CJK/non-space characters form a "word" segment.
    Spaces are separate segments.

    Returns a list of ``(text, is_space)`` tuples.
    """
    tokens: List[Tuple[str, bool]] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == ' ':
            tokens.append((' ', True))
            i += 1
        elif _is_cjk_char(ch):
            tokens.append((ch, False))
            i += 1
        else:
            # Accumulate non-CJK, non-space word
            j = i + 1
            while j < n and text[j] != ' ' and not _is_cjk_char(text[j]):
                j += 1
            tokens.append((text[i:j], False))
            i = j
    return tokens


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
    overflow_wrap: str = "normal",
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
    overflow_wrap : str
        ``'normal'`` — break only at allowed break points.
        ``'break-word'`` — allow breaking within words when a word
        overflows the available width.
        ``'anywhere'`` — same as ``'break-word'`` (simplified).
    """
    if fm is None:
        fm = FontManager.instance()

    break_word = overflow_wrap in ("break-word", "anywhere")

    if white_space == "pre":
        return _break_pre(text, font_path, size, fm, wrap=False)
    if white_space == "pre-wrap":
        return _break_pre(text, font_path, size, fm, wrap=True, available_width=available_width)
    if white_space == "pre-line":
        return _break_pre_line(text, available_width, font_path, size, fm, break_word=break_word)
    if white_space == "nowrap":
        # Collapse whitespace, single line
        collapsed = " ".join(text.split())
        w = measure_text(collapsed, font_path, size, fm=fm)
        return [Line(text=collapsed, width=w, char_count=len(collapsed))]

    # white_space == "normal" — default
    return _break_normal(text, available_width, font_path, size, fm, break_word=break_word)


def _break_normal(
    text: str,
    available_width: float,
    font_path: str,
    size: int,
    fm: FontManager,
    break_word: bool = False,
) -> List[Line]:
    """Greedy line-breaking for 'normal' white-space mode.

    Supports CJK text by treating each CJK character as an individual
    breakable unit.

    When *break_word* is ``True`` (``overflow-wrap: break-word``), tokens
    that are wider than *available_width* are split character-by-character.
    If a token overflows the remaining space on the current line but would
    fit on a fresh line, it simply moves to the next line (no breaking).
    """
    # Collapse whitespace
    collapsed = " ".join(text.split())
    if not collapsed:
        return [Line(text="", width=0.0, char_count=0)]

    tokens = _tokenize_breakable(collapsed)
    lines: List[Line] = []
    current_parts: List[str] = []
    current_width = 0.0

    def _flush_line() -> None:
        """Flush *current_parts* into *lines*."""
        nonlocal current_parts, current_width
        line_text = "".join(current_parts).rstrip()
        if line_text:
            line_w = measure_text(line_text, font_path, size, fm=fm)
            lines.append(Line(text=line_text, width=line_w, char_count=len(line_text)))
        current_parts = []
        current_width = 0.0

    for token_text, is_space in tokens:
        token_w = measure_text(token_text, font_path, size, fm=fm)

        fits_current = (not current_parts) or (current_width + token_w <= available_width)

        if not fits_current:
            if is_space:
                # Space at overflow — flush line, drop the space
                _flush_line()
                continue

            if break_word and token_w > available_width:
                # Token wider than a full line — must break it.
                # Flush current line first, then split the token.
                _flush_line()
                _split_token_into_lines(
                    token_text, available_width,
                    font_path, size, fm,
                    current_parts, lines,
                )
                current_width = measure_text(
                    "".join(current_parts), font_path, size, fm=fm
                )
            else:
                # Normal overflow — flush and start new line with this token
                _flush_line()
                current_parts = [token_text]
                current_width = token_w
        else:
            # Check: fresh line with a single oversized token
            if break_word and not current_parts and token_w > available_width:
                _split_token_into_lines(
                    token_text, available_width,
                    font_path, size, fm,
                    current_parts, lines,
                )
                current_width = measure_text(
                    "".join(current_parts), font_path, size, fm=fm
                )
            else:
                current_parts.append(token_text)
                current_width += token_w

    # Flush remainder
    if current_parts:
        _flush_line()

    return lines if lines else [Line(text="", width=0.0, char_count=0)]


def _split_token_into_lines(
    token: str,
    available_width: float,
    font_path: str,
    size: int,
    fm: FontManager,
    current_parts: List[str],
    lines: List[Line],
) -> None:
    """Split *token* character-by-character into lines of up to *available_width*.

    Complete lines are appended to *lines*.  Any leftover characters are
    placed into *current_parts* so the caller can continue accumulating.
    """
    buf = ""
    buf_w = 0.0

    for ch in token:
        cw = fm.glyph_metrics(font_path, size, ch).advance_x
        if buf and buf_w + cw > available_width:
            # Flush completed line
            lines.append(Line(text=buf, width=buf_w, char_count=len(buf)))
            buf = ch
            buf_w = cw
        else:
            buf += ch
            buf_w += cw

    # Leftover goes into current_parts for the caller
    if buf:
        current_parts.clear()
        current_parts.append(buf)


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
            # Word-boundary wrapping for pre-wrap (preserves spaces)
            sub_lines = _wrap_pre_line(raw, available_width, font_path, size, fm)
            result.extend(sub_lines)
    return result if result else [Line(text="", width=0.0, char_count=0)]


def _wrap_pre_line(
    text: str,
    available_width: float,
    font_path: str,
    size: int,
    fm: FontManager,
) -> List[Line]:
    """Wrap a single physical line at word boundaries for pre-wrap.

    Unlike ``_break_normal``, whitespace is preserved (not collapsed)
    and breaking happens at word/CJK boundaries.
    """
    if not text:
        return [Line(text="", width=0.0, char_count=0)]

    tokens = _tokenize_breakable(text)
    lines: List[Line] = []
    current_parts: List[str] = []
    current_width = 0.0

    def _flush() -> None:
        nonlocal current_parts, current_width
        line_text = "".join(current_parts)
        if line_text or not lines:  # allow empty first line
            line_w = measure_text(line_text, font_path, size, fm=fm) if line_text else 0.0
            lines.append(Line(text=line_text, width=line_w, char_count=len(line_text)))
        current_parts = []
        current_width = 0.0

    for token_text, is_space in tokens:
        token_w = measure_text(token_text, font_path, size, fm=fm)

        if current_parts and current_width + token_w > available_width:
            if is_space:
                # Wrap at space — include the space on the current line or drop it
                _flush()
                continue
            # Word overflow — flush, put word on new line
            _flush()
            # If the token itself is wider than available_width, break by char
            if token_w > available_width:
                _split_token_into_lines(
                    token_text, available_width,
                    font_path, size, fm,
                    current_parts, lines,
                )
                current_width = measure_text(
                    "".join(current_parts), font_path, size, fm=fm
                )
            else:
                current_parts = [token_text]
                current_width = token_w
        else:
            current_parts.append(token_text)
            current_width += token_w

    # Flush remainder (always, even if empty — preserves trailing newlines)
    line_text = "".join(current_parts)
    line_w = measure_text(line_text, font_path, size, fm=fm) if line_text else 0.0
    lines.append(Line(text=line_text, width=line_w, char_count=len(line_text)))

    return lines


def _break_pre_line(
    text: str,
    available_width: float,
    font_path: str,
    size: int,
    fm: FontManager,
    break_word: bool = False,
) -> List[Line]:
    """Line-breaking for 'pre-line' white-space mode.

    Pre-line collapses consecutive spaces (like ``normal``) but preserves
    explicit ``\\n`` line breaks.  Each segment between ``\\n`` is then
    word-wrapped independently using the ``normal`` algorithm.
    """
    segments = text.split("\n")
    result: List[Line] = []
    for segment in segments:
        sub = _break_normal(segment, available_width, font_path, size, fm, break_word=break_word)
        result.extend(sub)
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
    """Return the minimum content width — the width of the longest word.

    For CJK text each character is breakable so the min width is the
    widest single CJK character or the widest non-CJK word.
    """
    if fm is None:
        fm = FontManager.instance()
    if white_space in ("pre", "nowrap"):
        return measure_text(text, font_path, size, fm=fm)
    collapsed = " ".join(text.split())
    if not collapsed:
        return 0.0
    tokens = _tokenize_breakable(collapsed)
    max_w = 0.0
    for token_text, is_space in tokens:
        if not is_space:
            w = measure_text(token_text, font_path, size, fm=fm)
            max_w = max(max_w, w)
    return max_w


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


# ---------------------------------------------------------------------------
# Rich text (multi-span) data types
# ---------------------------------------------------------------------------

@dataclass
class SpanFragment:
    """A fragment of a ``TextSpan`` that lives on one rendered line."""

    text: str
    width: float
    span_index: int            # index into the original List[TextSpan]
    font_path: str = ""        # resolved font for this fragment
    font_size: int = 16        # resolved size for this fragment
    # Inline math rendering result (set during line-breaking)
    svg_fragment: Optional[object] = None  # math.backend.SVGFragment


@dataclass
class RichLine:
    """A single line of rich (multi-span) text."""

    fragments: List[SpanFragment] = field(default_factory=list)
    width: float = 0.0
    x_offset: float = 0.0


# ---------------------------------------------------------------------------
# Rich text helpers
# ---------------------------------------------------------------------------

def _resolve_span_font(
    span: "TextSpan",
    base_font_chain: list,
    base_size: int,
    fm: FontManager,
) -> tuple:
    """Return ``(font_path_or_chain, size)`` for a single TextSpan.

    Uses the span's overrides (font_weight, font_style, font_family,
    font_size) falling back to the base values.
    """
    from ..markup.parser import TextSpan  # deferred to avoid circular

    size = int(span.font_size) if span.font_size is not None else base_size

    # If the span specifies a different family / weight / style, resolve
    # a new font chain; otherwise reuse the base chain.
    if span.font_family or span.font_weight or span.font_style:
        families: list = []
        if span.font_family:
            families = [f.strip().strip('"').strip("'")
                        for f in span.font_family.split(",") if f.strip()]
        if not families:
            # Use names derived from base chain
            for fp in base_font_chain:
                n = fm.font_family_name(fp)
                if n and n not in families:
                    families.append(n)
            if not families:
                families = ["sans-serif"]

        weight = span.font_weight or "normal"
        style = span.font_style or "normal"
        chain = fm.find_font_chain(families, weight=weight, style=style)
        if chain:
            return (chain, size)

    return (base_font_chain, size)


def _measure_span_text(
    text: str,
    font_chain: list,
    size: int,
    fm: FontManager,
) -> float:
    """Measure *text* using a font chain."""
    if not text:
        return 0.0
    return measure_text(text, font_chain, size, fm=fm)


# ---------------------------------------------------------------------------
# Rich text line breaking
# ---------------------------------------------------------------------------

def break_lines_rich(
    spans: "List[TextSpan]",
    available_width: float,
    base_font_chain: list,
    base_size: int,
    white_space: str = "normal",
    overflow_wrap: str = "normal",
    *,
    fm: Optional[FontManager] = None,
    math_backend: Optional[object] = None,
) -> List[RichLine]:
    """Break a list of ``TextSpan`` into ``RichLine`` objects.

    This is the rich-text counterpart of :func:`break_lines`.  Each span
    may use a different font/size; ``<br>`` spans force line breaks;
    ``<math>`` spans are measured via *math_backend* if provided.
    """
    from ..markup.parser import TextSpan  # type: ignore

    if fm is None:
        fm = FontManager.instance()

    break_word = overflow_wrap in ("break-word", "anywhere")
    collapse_ws = white_space in ("normal", "nowrap")
    wrap = white_space not in ("nowrap", "pre")

    # ---- pre-process spans: resolve fonts, handle <br> ----
    # Build a flat list of "segment" dicts ready for tokenization.
    segments: list = []  # list of dict with keys: text, span_idx, chain, size, is_math, svg_frag
    for idx, span in enumerate(spans):
        if span.is_line_break:
            segments.append({"br": True, "span_idx": idx})
            continue

        chain, sz = _resolve_span_font(span, base_font_chain, base_size, fm)
        fp = chain[0] if isinstance(chain, list) and chain else chain

        if span.is_math and math_backend is not None:
            # Render math and use its metrics as a single "token"
            svg_frag = math_backend.render(span.text, float(sz))
            segments.append({
                "br": False,
                "text": span.text,
                "span_idx": idx,
                "chain": chain,
                "fp": fp,
                "size": sz,
                "is_math": True,
                "svg_frag": svg_frag,
                "width": svg_frag.width,
            })
            continue

        text = span.text
        if collapse_ws:
            text = " ".join(text.split()) if text.strip() else (" " if text else "")

        segments.append({
            "br": False,
            "text": text,
            "span_idx": idx,
            "chain": chain,
            "fp": fp,
            "size": sz,
            "is_math": False,
            "svg_frag": None,
            "width": None,  # calculated per-token
        })

    # ---- tokenize and break lines ----
    lines: List[RichLine] = []
    cur_frags: List[SpanFragment] = []
    cur_width = 0.0

    def _flush() -> None:
        nonlocal cur_frags, cur_width
        # Strip trailing whitespace fragment
        while cur_frags and cur_frags[-1].text.endswith(" "):
            last = cur_frags[-1]
            stripped = last.text.rstrip(" ")
            if stripped:
                new_w = _measure_span_text(stripped, [last.font_path] if last.font_path else base_font_chain, last.font_size, fm)
                cur_frags[-1] = SpanFragment(
                    text=stripped, width=new_w,
                    span_index=last.span_index,
                    font_path=last.font_path, font_size=last.font_size,
                    svg_fragment=last.svg_fragment,
                )
            else:
                cur_frags.pop()
        total_w = sum(f.width for f in cur_frags)
        lines.append(RichLine(fragments=list(cur_frags), width=total_w))
        cur_frags = []
        cur_width = 0.0

    for seg in segments:
        if seg.get("br"):
            _flush()
            continue

        if seg["is_math"]:
            # Math spans behave as a single indivisible token
            tw = seg["width"]
            if wrap and cur_frags and cur_width + tw > available_width:
                _flush()
            cur_frags.append(SpanFragment(
                text=seg["text"], width=tw,
                span_index=seg["span_idx"],
                font_path=seg["fp"] if isinstance(seg["fp"], str) else (seg["fp"][0] if seg["fp"] else ""),
                font_size=seg["size"],
                svg_fragment=seg["svg_frag"],
            ))
            cur_width += tw
            continue

        text = seg["text"]
        span_idx = seg["span_idx"]
        chain = seg["chain"]
        fp = seg["fp"]
        sz = seg["size"]

        if not text:
            continue

        # Tokenize this span's text
        if white_space in ("pre", "pre-wrap"):
            # Split on newlines first, preserve spaces
            sub_lines = text.split("\n")
            for li, sub in enumerate(sub_lines):
                if li > 0:
                    _flush()  # newline = force break
                tokens = _tokenize_breakable(sub) if sub else []
                for tok_text, is_space in tokens:
                    tok_w = _measure_span_text(tok_text, chain, sz, fm)
                    if wrap and cur_frags and cur_width + tok_w > available_width and not is_space:
                        _flush()
                    cur_frags.append(SpanFragment(
                        text=tok_text, width=tok_w,
                        span_index=span_idx,
                        font_path=fp if isinstance(fp, str) else (fp[0] if fp else ""),
                        font_size=sz,
                    ))
                    cur_width += tok_w
        else:
            tokens = _tokenize_breakable(text)
            for tok_text, is_space in tokens:
                tok_w = _measure_span_text(tok_text, chain, sz, fm)

                fits = (not cur_frags) or (cur_width + tok_w <= available_width)

                if not fits and wrap:
                    if is_space:
                        _flush()
                        continue

                    if break_word and tok_w > available_width:
                        _flush()
                        # Character-by-character split
                        buf = ""
                        buf_w = 0.0
                        for ch in tok_text:
                            cw = fm.glyph_metrics(fp if isinstance(fp, str) else fp[0], sz, ch).advance_x
                            if buf and buf_w + cw > available_width:
                                cur_frags.append(SpanFragment(
                                    text=buf, width=buf_w,
                                    span_index=span_idx,
                                    font_path=fp if isinstance(fp, str) else (fp[0] if fp else ""),
                                    font_size=sz,
                                ))
                                cur_width = buf_w
                                _flush()
                                buf = ch
                                buf_w = cw
                            else:
                                buf += ch
                                buf_w += cw
                        if buf:
                            cur_frags.append(SpanFragment(
                                text=buf, width=buf_w,
                                span_index=span_idx,
                                font_path=fp if isinstance(fp, str) else (fp[0] if fp else ""),
                                font_size=sz,
                            ))
                            cur_width += buf_w
                    else:
                        _flush()
                        cur_frags.append(SpanFragment(
                            text=tok_text, width=tok_w,
                            span_index=span_idx,
                            font_path=fp if isinstance(fp, str) else (fp[0] if fp else ""),
                            font_size=sz,
                        ))
                        cur_width += tok_w
                else:
                    cur_frags.append(SpanFragment(
                        text=tok_text, width=tok_w,
                        span_index=span_idx,
                        font_path=fp if isinstance(fp, str) else (fp[0] if fp else ""),
                        font_size=sz,
                    ))
                    cur_width += tok_w

    # Flush remainder
    if cur_frags:
        _flush()

    if not lines:
        lines.append(RichLine())

    return lines


# ---------------------------------------------------------------------------
# Rich text alignment & sizing
# ---------------------------------------------------------------------------

def align_lines_rich(
    lines: List[RichLine],
    available_width: float,
    text_align: str = "left",
) -> List[RichLine]:
    """Set ``x_offset`` on each ``RichLine`` based on *text_align*."""
    result: List[RichLine] = []
    for line in lines:
        offset = 0.0
        if text_align == "center":
            offset = (available_width - line.width) / 2.0
        elif text_align == "right":
            offset = available_width - line.width
        result.append(RichLine(
            fragments=line.fragments,
            width=line.width,
            x_offset=max(0.0, offset),
        ))
    return result


def compute_rich_block_size(
    lines: List[RichLine],
    line_height: float,
    font_size: float,
) -> tuple:
    """Return ``(width, height)`` for a rich text block."""
    if line_height <= 5.0:
        lh = font_size * line_height
    else:
        lh = line_height
    max_w = max((l.width for l in lines), default=0.0)
    total_h = lh * len(lines) if lines else 0.0
    return (max_w, total_h)


def get_min_content_width_rich(
    spans: "List[TextSpan]",
    base_font_chain: list,
    base_size: int,
    white_space: str = "normal",
    *,
    fm: Optional[FontManager] = None,
    math_backend: Optional[object] = None,
) -> float:
    """Return the min-content width for a rich span list."""
    from ..markup.parser import TextSpan  # type: ignore

    if fm is None:
        fm = FontManager.instance()
    if white_space in ("pre", "nowrap"):
        return get_max_content_width_rich(spans, base_font_chain, base_size, white_space, fm=fm, math_backend=math_backend)

    max_w = 0.0
    for span in spans:
        if span.is_line_break:
            continue
        chain, sz = _resolve_span_font(span, base_font_chain, base_size, fm)

        if span.is_math and math_backend is not None:
            svg_frag = math_backend.render(span.text, float(sz))
            max_w = max(max_w, svg_frag.width)
            continue

        text = " ".join(span.text.split()) if span.text.strip() else ""
        if not text:
            continue
        tokens = _tokenize_breakable(text)
        for tok_text, is_space in tokens:
            if not is_space:
                w = _measure_span_text(tok_text, chain, sz, fm)
                max_w = max(max_w, w)
    return max_w


def get_max_content_width_rich(
    spans: "List[TextSpan]",
    base_font_chain: list,
    base_size: int,
    white_space: str = "normal",
    *,
    fm: Optional[FontManager] = None,
    math_backend: Optional[object] = None,
) -> float:
    """Return the max-content width for a rich span list (single line)."""
    from ..markup.parser import TextSpan  # type: ignore

    if fm is None:
        fm = FontManager.instance()

    total = 0.0
    for span in spans:
        if span.is_line_break:
            continue
        chain, sz = _resolve_span_font(span, base_font_chain, base_size, fm)

        if span.is_math and math_backend is not None:
            svg_frag = math_backend.render(span.text, float(sz))
            total += svg_frag.width
            continue

        text = span.text
        if white_space not in ("pre", "pre-wrap"):
            text = " ".join(text.split()) if text.strip() else (" " if text else "")
        total += _measure_span_text(text, chain, sz, fm)
    return total
