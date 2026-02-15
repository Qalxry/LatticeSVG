"""Text shaping — line breaking, alignment, and overflow handling."""

from __future__ import annotations

import re as _re
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
    justified: bool = False            # True when text-align: justify applies
    word_spacing_justify: float = 0.0  # extra gap per word boundary for justify
    hyphenated: bool = False           # True when line ends with a hyphen from auto/manual hyphens


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
# Hyphenation helpers
# ---------------------------------------------------------------------------

# Soft hyphen character (U+00AD) used by ``hyphens: manual``
_SHY = "\u00AD"

# Module-level cache for pyphen Pyphen instances keyed by language
_hyphenators: dict = {}

def _get_hyphenator(lang: str):
    """Return a cached ``pyphen.Pyphen`` instance for *lang*, or ``None``.

    Returns ``None`` when pyphen is not installed so that callers can
    fall back gracefully.
    """
    if lang in _hyphenators:
        return _hyphenators[lang]
    try:
        import pyphen  # type: ignore
        h = pyphen.Pyphen(lang=lang)
        _hyphenators[lang] = h
        return h
    except Exception:
        _hyphenators[lang] = None
        return None


def _hyphen_points_auto(word: str, lang: str) -> List[int]:
    """Return valid hyphenation positions (char indices) using pyphen.

    Each index *i* means the word can be split as ``word[:i]`` + ``-``.
    Returns an empty list when pyphen is unavailable or the word has no
    valid break points.
    """
    h = _get_hyphenator(lang)
    if h is None:
        return []
    return h.positions(word)


def _hyphen_points_manual(word: str) -> List[int]:
    """Return hyphenation positions from soft-hyphen (U+00AD) markers.

    The returned indices refer to the *original* word (with SHY chars
    present).  ``word[:i]`` (excluding the SHY itself) + ``-`` is the
    visible prefix.
    """
    positions: List[int] = []
    for i, ch in enumerate(word):
        if ch == _SHY:
            positions.append(i)
    return positions


def _strip_shy(text: str) -> str:
    """Remove all soft-hyphen characters from *text*."""
    return text.replace(_SHY, "")


def _try_hyphenate(
    word: str,
    remaining_width: float,
    font_path,
    size: int,
    fm: FontManager,
    points: List[int],
    letter_spacing: float,
    hyphen_w: float,
    is_manual: bool = False,
) -> Optional[Tuple[str, str]]:
    """Try to break *word* at the best hyphenation point.

    Returns ``(prefix_with_hyphen, suffix)`` if a valid split is found
    that fits within *remaining_width*, or ``None`` otherwise.

    For ``manual`` mode, *points* are indices into the original word
    (which may contain SHY chars that must be stripped from the output).
    """
    best: Optional[Tuple[str, str]] = None
    for pos in points:
        if is_manual:
            # pos is index of the SHY char; prefix is word[:pos] without SHY
            prefix_raw = word[:pos]
            suffix_raw = word[pos + 1:]  # skip the SHY character
            prefix_clean = _strip_shy(prefix_raw)
            suffix_clean = _strip_shy(suffix_raw)
        else:
            prefix_clean = word[:pos]
            suffix_clean = word[pos:]
        if not prefix_clean or not suffix_clean:
            continue
        prefix_display = prefix_clean + "-"
        pw = measure_text(prefix_display, font_path, size, fm=fm,
                          letter_spacing=letter_spacing)
        if pw <= remaining_width:
            # Pick the longest prefix that fits
            best = (prefix_display, suffix_clean)
    return best


# ---------------------------------------------------------------------------
# Core measurement
# ---------------------------------------------------------------------------


def measure_text(
    text: str,
    font_path: str,
    size: int,
    *,
    fm: Optional[FontManager] = None,
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
) -> float:
    """Return the total advance width of *text* in pixels."""
    if fm is None:
        fm = FontManager.instance()
    total = 0.0
    n = len(text)
    for i, ch in enumerate(text):
        gm = fm.glyph_metrics(font_path, size, ch)
        total += gm.advance_x
        # letter-spacing: extra space between characters (not after last)
        if letter_spacing and i < n - 1:
            total += letter_spacing
        # word-spacing: extra space on space characters
        if word_spacing and ch == ' ':
            total += word_spacing
    return total


def measure_word(
    word: str,
    font_path: str,
    size: int,
    *,
    fm: Optional[FontManager] = None,
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
) -> float:
    """Measure a single word's advance width."""
    return measure_text(word, font_path, size, fm=fm,
                        letter_spacing=letter_spacing,
                        word_spacing=word_spacing)


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
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
    hyphens: str = "none",
    lang: str = "en",
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
    _ls, _ws = letter_spacing, word_spacing

    if white_space == "pre":
        return _break_pre(text, font_path, size, fm, wrap=False,
                          letter_spacing=_ls, word_spacing=_ws)
    if white_space == "pre-wrap":
        return _break_pre(text, font_path, size, fm, wrap=True, available_width=available_width,
                          letter_spacing=_ls, word_spacing=_ws)
    if white_space == "pre-line":
        return _break_pre_line(text, available_width, font_path, size, fm, break_word=break_word,
                               letter_spacing=_ls, word_spacing=_ws,
                               hyphens=hyphens, lang=lang)
    if white_space == "nowrap":
        # Collapse whitespace, single line
        collapsed = " ".join(text.split())
        if hyphens != "none":
            collapsed = _strip_shy(collapsed)
        w = measure_text(collapsed, font_path, size, fm=fm,
                         letter_spacing=_ls, word_spacing=_ws)
        return [Line(text=collapsed, width=w, char_count=len(collapsed))]

    # white_space == "normal" — default
    return _break_normal(text, available_width, font_path, size, fm, break_word=break_word,
                         letter_spacing=_ls, word_spacing=_ws,
                         hyphens=hyphens, lang=lang)


def _break_normal(
    text: str,
    available_width: float,
    font_path: str,
    size: int,
    fm: FontManager,
    break_word: bool = False,
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
    hyphens: str = "none",
    lang: str = "en",
) -> List[Line]:
    """Greedy line-breaking for 'normal' white-space mode.

    Supports CJK text by treating each CJK character as an individual
    breakable unit.

    When *break_word* is ``True`` (``overflow-wrap: break-word``), tokens
    that are wider than *available_width* are split character-by-character.
    If a token overflows the remaining space on the current line but would
    fit on a fresh line, it simply moves to the next line (no breaking).
    """
    _ls, _ws = letter_spacing, word_spacing

    # Collapse whitespace
    collapsed = " ".join(text.split())
    if not collapsed:
        return [Line(text="", width=0.0, char_count=0)]

    tokens = _tokenize_breakable(collapsed)
    lines: List[Line] = []
    current_parts: List[str] = []
    current_width = 0.0

    # Pre-compute hyphen width once if hyphenation is active
    _hyph_active = hyphens != "none"
    _hyphen_w = measure_text("-", font_path, size, fm=fm) if _hyph_active else 0.0

    def _flush_line(hyphenated: bool = False) -> None:
        """Flush *current_parts* into *lines*."""
        nonlocal current_parts, current_width
        line_text = "".join(current_parts).rstrip()
        # Strip soft-hyphen characters from output
        if _hyph_active:
            line_text = _strip_shy(line_text)
        if line_text:
            line_w = measure_text(line_text, font_path, size, fm=fm,
                                  letter_spacing=_ls, word_spacing=_ws)
            lines.append(Line(text=line_text, width=line_w,
                              char_count=len(line_text),
                              hyphenated=hyphenated))
        current_parts = []
        current_width = 0.0

    def _get_hyph_points(word: str) -> List[int]:
        """Return hyphenation points for *word*."""
        if hyphens == "auto":
            return _hyphen_points_auto(_strip_shy(word), lang)
        return _hyphen_points_manual(word)

    def _measure_word(word: str) -> float:
        """Measure *word*, stripping SHY if needed."""
        clean = _strip_shy(word) if _hyph_active else word
        return measure_text(clean, font_path, size, fm=fm,
                            letter_spacing=_ls, word_spacing=_ws)

    def _place_with_hyph(word: str) -> None:
        """Place *word* on a fresh line, hyphenating iteratively.

        Assumes ``current_parts`` is empty.  Repeatedly splits off the
        longest fitting prefix until the remainder fits on one line.
        """
        nonlocal current_parts, current_width
        while True:
            w = _measure_word(word)
            if w <= available_width:
                # Remaining piece fits — done
                current_parts = [word]
                current_width = w
                return
            pts = _get_hyph_points(word)
            result = _try_hyphenate(
                word, available_width, font_path, size, fm,
                pts, _ls, _hyphen_w,
                is_manual=(hyphens == "manual"),
            )
            if result is not None:
                prefix, suffix = result
                current_parts = [prefix]
                _flush_line(hyphenated=True)
                word = suffix  # loop with the remainder
            else:
                # Cannot hyphenate — place as-is (will overflow)
                current_parts = [word]
                current_width = w
                return

    for token_text, is_space in tokens:
        # SHY chars are zero-width for measurement purposes
        token_measure_text = _strip_shy(token_text) if _hyph_active else token_text
        token_w = measure_text(token_measure_text, font_path, size, fm=fm,
                               letter_spacing=_ls, word_spacing=_ws)

        # letter-spacing bridge: when appending a new token to an
        # existing line, the last char of the previous token and the
        # first char of this token are adjacent — letter-spacing
        # applies between them but isn't included in either token's
        # individual width.
        bridge = _ls if (current_parts and _ls) else 0.0

        fits_current = (not current_parts) or (current_width + bridge + token_w <= available_width)

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
                    _strip_shy(token_text) if _hyph_active else token_text,
                    available_width,
                    font_path, size, fm,
                    current_parts, lines,
                    letter_spacing=_ls,
                )
                current_width = measure_text(
                    "".join(current_parts), font_path, size, fm=fm,
                    letter_spacing=_ls, word_spacing=_ws,
                )
            elif _hyph_active and not is_space:
                # --- Hyphenation attempt ---
                remaining = available_width - current_width - bridge
                pts = _get_hyph_points(token_text)
                result = _try_hyphenate(
                    token_text, remaining, font_path, size, fm,
                    pts, _ls, _hyphen_w,
                    is_manual=(hyphens == "manual"),
                )
                if result is not None:
                    prefix, suffix = result
                    current_parts.append(prefix)
                    _flush_line(hyphenated=True)
                    # Suffix may still exceed available_width → loop
                    _place_with_hyph(suffix)
                else:
                    # Remaining space too small — flush, then try on
                    # a fresh line with full width (iterative).
                    _flush_line()
                    _place_with_hyph(token_text)
            else:
                # Normal overflow — flush and start new line with this token
                _flush_line()
                current_parts = [token_text]
                current_width = token_w
        else:
            # Check: fresh line with a single oversized token
            if break_word and not current_parts and token_w > available_width:
                _split_token_into_lines(
                    _strip_shy(token_text) if _hyph_active else token_text,
                    available_width,
                    font_path, size, fm,
                    current_parts, lines,
                    letter_spacing=_ls,
                )
                current_width = measure_text(
                    "".join(current_parts), font_path, size, fm=fm,
                    letter_spacing=_ls, word_spacing=_ws,
                )
            elif _hyph_active and not is_space and not current_parts and token_w > available_width:
                # Oversized token on a fresh line — iterative hyphenation
                _place_with_hyph(token_text)
            else:
                current_parts.append(token_text)
                current_width += bridge + token_w

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
    letter_spacing: float = 0.0,
) -> None:
    """Split *token* character-by-character into lines of up to *available_width*.

    Complete lines are appended to *lines*.  Any leftover characters are
    placed into *current_parts* so the caller can continue accumulating.
    """
    buf = ""
    buf_w = 0.0

    for ch in token:
        cw = fm.glyph_metrics(font_path, size, ch).advance_x
        effective_w = cw + letter_spacing if buf else cw  # no spacing before first
        if buf and buf_w + effective_w > available_width:
            # Flush completed line
            lines.append(Line(text=buf, width=buf_w, char_count=len(buf)))
            buf = ch
            buf_w = cw
        else:
            if buf:
                buf_w += letter_spacing  # spacing between previous and this char
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
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
) -> List[Line]:
    """Line-breaking for 'pre'/'pre-wrap' white-space mode."""
    raw_lines = text.split("\n")
    result: List[Line] = []
    for raw in raw_lines:
        if not wrap or available_width == float("inf"):
            w = measure_text(raw, font_path, size, fm=fm,
                             letter_spacing=letter_spacing, word_spacing=word_spacing)
            result.append(Line(text=raw, width=w, char_count=len(raw)))
        else:
            # Word-boundary wrapping for pre-wrap (preserves spaces)
            sub_lines = _wrap_pre_line(raw, available_width, font_path, size, fm,
                                       letter_spacing=letter_spacing, word_spacing=word_spacing)
            result.extend(sub_lines)
    return result if result else [Line(text="", width=0.0, char_count=0)]


def _wrap_pre_line(
    text: str,
    available_width: float,
    font_path: str,
    size: int,
    fm: FontManager,
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
) -> List[Line]:
    """Wrap a single physical line at word boundaries for pre-wrap.

    Unlike ``_break_normal``, whitespace is preserved (not collapsed)
    and breaking happens at word/CJK boundaries.
    """
    if not text:
        return [Line(text="", width=0.0, char_count=0)]

    _ls, _ws = letter_spacing, word_spacing
    tokens = _tokenize_breakable(text)
    lines: List[Line] = []
    current_parts: List[str] = []
    current_width = 0.0

    def _flush() -> None:
        nonlocal current_parts, current_width
        line_text = "".join(current_parts)
        if line_text or not lines:  # allow empty first line
            line_w = measure_text(line_text, font_path, size, fm=fm,
                                  letter_spacing=_ls, word_spacing=_ws) if line_text else 0.0
            lines.append(Line(text=line_text, width=line_w, char_count=len(line_text)))
        current_parts = []
        current_width = 0.0

    for token_text, is_space in tokens:
        token_w = measure_text(token_text, font_path, size, fm=fm,
                               letter_spacing=_ls, word_spacing=_ws)

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
                    letter_spacing=_ls,
                )
                current_width = measure_text(
                    "".join(current_parts), font_path, size, fm=fm,
                    letter_spacing=_ls, word_spacing=_ws,
                )
            else:
                current_parts = [token_text]
                current_width = token_w
        else:
            current_parts.append(token_text)
            current_width += token_w

    # Flush remainder (always, even if empty — preserves trailing newlines)
    line_text = "".join(current_parts)
    line_w = measure_text(line_text, font_path, size, fm=fm,
                          letter_spacing=_ls, word_spacing=_ws) if line_text else 0.0
    lines.append(Line(text=line_text, width=line_w, char_count=len(line_text)))

    return lines


def _break_pre_line(
    text: str,
    available_width: float,
    font_path: str,
    size: int,
    fm: FontManager,
    break_word: bool = False,
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
    hyphens: str = "none",
    lang: str = "en",
) -> List[Line]:
    """Line-breaking for 'pre-line' white-space mode.

    Pre-line collapses consecutive spaces (like ``normal``) but preserves
    explicit ``\\n`` line breaks.  Each segment between ``\\n`` is then
    word-wrapped independently using the ``normal`` algorithm.
    """
    segments = text.split("\n")
    result: List[Line] = []
    for segment in segments:
        sub = _break_normal(segment, available_width, font_path, size, fm, break_word=break_word,
                            letter_spacing=letter_spacing, word_spacing=word_spacing,
                            hyphens=hyphens, lang=lang)
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

    For ``text-align: justify``, computes per-word (or per-character for
    CJK) extra spacing.  The last line is always left-aligned (CSS
    standard behaviour).
    """
    result: List[Line] = []
    num_lines = len(lines)
    for i, line in enumerate(lines):
        offset = 0.0
        justified = False
        word_gap = 0.0
        if text_align == "center":
            offset = (available_width - line.width) / 2.0
        elif text_align == "right":
            offset = available_width - line.width
        elif text_align == "justify" and i < num_lines - 1:
            extra = available_width - line.width
            if extra > 0:
                words = line.text.split()
                if len(words) > 1:
                    # Western text: distribute extra space across word gaps
                    word_gap = extra / (len(words) - 1)
                    justified = True
                elif line.char_count > 1 and ' ' not in line.text:
                    # CJK text without spaces: distribute across char gaps
                    word_gap = extra / (line.char_count - 1)
                    justified = True
        result.append(Line(
            text=line.text,
            width=line.width,
            x_offset=max(0.0, offset),
            char_count=line.char_count,
            justified=justified,
            word_spacing_justify=word_gap,
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

    *line_height* is the resolved line-height in absolute px.
    *font_size* is retained for API compatibility but unused when
    *line_height* is already absolute.
    """
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
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
    hyphens: str = "none",
    lang: str = "en",
) -> float:
    """Return the minimum content width — the width of the longest word.

    For CJK text each character is breakable so the min width is the
    widest single CJK character or the widest non-CJK word.

    When *hyphens* is ``auto`` or ``manual``, words can be split at
    hyphenation points so the min width is the widest syllable fragment
    (plus a trailing hyphen character).
    """
    if fm is None:
        fm = FontManager.instance()
    if white_space in ("pre", "nowrap"):
        return measure_text(text, font_path, size, fm=fm,
                            letter_spacing=letter_spacing, word_spacing=word_spacing)
    collapsed = " ".join(text.split())
    if not collapsed:
        return 0.0
    tokens = _tokenize_breakable(collapsed)
    max_w = 0.0
    _hyph_active = hyphens != "none"
    hyphen_w = measure_text("-", font_path, size, fm=fm) if _hyph_active else 0.0
    for token_text, is_space in tokens:
        if not is_space:
            if _hyph_active:
                # Split the word at hyphenation points and find the
                # widest syllable fragment (with hyphen appended to
                # all but the last fragment).
                clean = _strip_shy(token_text)
                if hyphens == "auto":
                    pts = _hyphen_points_auto(clean, lang)
                else:
                    pts = _hyphen_points_manual(token_text)
                if pts:
                    # Build syllable fragments
                    fragments: List[str] = []
                    if hyphens == "manual":
                        prev = 0
                        for p in pts:
                            frag = _strip_shy(token_text[prev:p])
                            fragments.append(frag)
                            prev = p + 1  # skip the SHY
                        tail = _strip_shy(token_text[prev:])
                        if tail:
                            fragments.append(tail)
                    else:
                        prev = 0
                        for p in pts:
                            fragments.append(clean[prev:p])
                            prev = p
                        tail = clean[prev:]
                        if tail:
                            fragments.append(tail)
                    for fi, frag in enumerate(fragments):
                        fw = measure_text(frag, font_path, size, fm=fm,
                                          letter_spacing=letter_spacing)
                        # All fragments except the last get a trailing hyphen
                        if fi < len(fragments) - 1:
                            fw += hyphen_w
                        max_w = max(max_w, fw)
                else:
                    w = measure_text(clean, font_path, size, fm=fm,
                                     letter_spacing=letter_spacing, word_spacing=word_spacing)
                    max_w = max(max_w, w)
            else:
                w = measure_text(token_text, font_path, size, fm=fm,
                                 letter_spacing=letter_spacing, word_spacing=word_spacing)
                max_w = max(max_w, w)
    return max_w


def get_max_content_width(
    text: str,
    font_path: str,
    size: int,
    white_space: str = "normal",
    *,
    fm: Optional[FontManager] = None,
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
) -> float:
    """Return the max-content width — text on a single line."""
    if fm is None:
        fm = FontManager.instance()
    if white_space == "pre":
        # Longest physical line
        raw_lines = text.split("\n")
        return max((measure_text(l, font_path, size, fm=fm,
                                 letter_spacing=letter_spacing, word_spacing=word_spacing)
                    for l in raw_lines), default=0.0)
    collapsed = " ".join(text.split())
    return measure_text(collapsed, font_path, size, fm=fm,
                        letter_spacing=letter_spacing, word_spacing=word_spacing)


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
    justified: bool = False            # True when text-align: justify applies
    word_spacing_justify: float = 0.0  # extra gap per word boundary for justify
    _cjk_justify: bool = False         # True when CJK per-char distribution
    hyphenated: bool = False           # True when line ends with a hyphen from auto/manual hyphens


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
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
) -> float:
    """Measure *text* using a font chain."""
    if not text:
        return 0.0
    return measure_text(text, font_chain, size, fm=fm,
                        letter_spacing=letter_spacing,
                        word_spacing=word_spacing)


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
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
    hyphens: str = "none",
    lang: str = "en",
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
    _ls, _ws = letter_spacing, word_spacing

    # ---- pre-process spans: resolve fonts, handle <br> ----
    # Build a flat list of "segment" dicts ready for tokenization.
    segments: list = []  # list of dict with keys: text, span_idx, chain, size, is_math, svg_frag
    for idx, span in enumerate(spans):
        if span.is_line_break:
            segments.append({"br": True, "span_idx": idx})
            continue

        chain, sz = _resolve_span_font(span, base_font_chain, base_size, fm)
        fp = chain[0] if isinstance(chain, list) and chain else chain

        # Sub/super: if no explicit font-size override, measure at the
        # same shrunk size that the renderer will use (0.7×).
        if span.baseline_shift in ("super", "sub") and span.font_size is None:
            sz = max(1, int(base_size * 0.7))

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
            # Collapse internal whitespace runs to single space but
            # keep a single leading/trailing space so that inter-span
            # spacing is preserved (CSS inline whitespace behaviour).
            text = _re.sub(r'\s+', ' ', text) if text else ""

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

    # ---- Cross-span whitespace dedup ----
    # CSS collapses whitespace across element boundaries: if span A
    # ends with a space and span B starts with a space, only one
    # space should appear.  Also strip leading space on the very
    # first text segment (line-start behaviour).
    if collapse_ws:
        first_text_seen = False
        prev_ended_space = False
        for seg in segments:
            if seg.get("br"):
                prev_ended_space = False
                first_text_seen = False
                continue
            if seg.get("is_math"):
                prev_ended_space = False
                first_text_seen = True
                continue
            txt = seg["text"]
            if not txt:
                continue
            # Strip leading space if previous segment ended with one,
            # or if this is the very first text on the line.
            if (prev_ended_space or not first_text_seen) and txt.startswith(" "):
                txt = txt.lstrip(" ")
            seg["text"] = txt
            prev_ended_space = txt.endswith(" ") if txt else False
            first_text_seen = True

    # ---- tokenize and break lines ----
    lines: List[RichLine] = []
    cur_frags: List[SpanFragment] = []
    cur_width = 0.0
    _hyph_active = hyphens != "none"

    def _flush(hyphenated: bool = False) -> None:
        nonlocal cur_frags, cur_width
        # Strip soft-hyphen from all fragment texts
        if _hyph_active:
            cur_frags = [
                SpanFragment(
                    text=_strip_shy(f.text), width=_measure_span_text(_strip_shy(f.text), [f.font_path] if f.font_path else base_font_chain, f.font_size, fm, letter_spacing=_ls, word_spacing=_ws) if _SHY in f.text else f.width,
                    span_index=f.span_index, font_path=f.font_path, font_size=f.font_size, svg_fragment=f.svg_fragment,
                ) if f.svg_fragment is None and _SHY in f.text else f
                for f in cur_frags
            ]
        # Strip trailing whitespace fragment
        while cur_frags and cur_frags[-1].text.endswith(" "):
            last = cur_frags[-1]
            stripped = last.text.rstrip(" ")
            if stripped:
                new_w = _measure_span_text(stripped, [last.font_path] if last.font_path else base_font_chain, last.font_size, fm,
                                           letter_spacing=_ls, word_spacing=_ws)
                cur_frags[-1] = SpanFragment(
                    text=stripped, width=new_w,
                    span_index=last.span_index,
                    font_path=last.font_path, font_size=last.font_size,
                    svg_fragment=last.svg_fragment,
                )
            else:
                cur_frags.pop()
        total_w = sum(f.width for f in cur_frags)
        lines.append(RichLine(fragments=list(cur_frags), width=total_w,
                               hyphenated=hyphenated))
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
                    tok_w = _measure_span_text(tok_text, chain, sz, fm,
                                               letter_spacing=_ls, word_spacing=_ws)
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
                tok_measure = _strip_shy(tok_text) if (_hyph_active and _SHY in tok_text) else tok_text
                tok_w = _measure_span_text(tok_measure, chain, sz, fm,
                                           letter_spacing=_ls, word_spacing=_ws)

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
                            effective_cw = cw + _ls if buf else cw
                            if buf and buf_w + effective_cw > available_width:
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
                                if buf:
                                    buf_w += _ls  # letter-spacing between chars
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
                        # --- Hyphenation attempt (rich text) ---
                        _fp_str = fp if isinstance(fp, str) else (fp[0] if fp else "")
                        if _hyph_active and not is_space:
                            remaining = available_width - cur_width
                            hyp_w = _measure_span_text("-", chain, sz, fm, letter_spacing=_ls)

                            def _get_rich_hyph_pts(w):
                                if hyphens == "auto":
                                    return _hyphen_points_auto(_strip_shy(w), lang)
                                return _hyphen_points_manual(w)

                            def _meas_rich(w):
                                c = _strip_shy(w) if (_SHY in w) else w
                                return _measure_span_text(c, chain, sz, fm,
                                                          letter_spacing=_ls, word_spacing=_ws)

                            # First attempt: fit in remaining space
                            pts = _get_rich_hyph_pts(tok_text)
                            result = _try_hyphenate(
                                tok_text, remaining, _fp_str, sz, fm,
                                pts, _ls, hyp_w,
                                is_manual=(hyphens == "manual"),
                            )
                            if result is not None:
                                prefix, suffix = result
                                cur_frags.append(SpanFragment(
                                    text=prefix, width=_meas_rich(prefix),
                                    span_index=span_idx, font_path=_fp_str, font_size=sz,
                                ))
                                _flush(hyphenated=True)
                                word_rem = suffix
                            else:
                                # Remaining space too small — flush, retry on fresh line
                                _flush()
                                word_rem = tok_text

                            # Iteratively hyphenate until remainder fits
                            while True:
                                w_rem = _meas_rich(word_rem)
                                if w_rem <= available_width:
                                    break
                                pts2 = _get_rich_hyph_pts(word_rem)
                                r2 = _try_hyphenate(
                                    word_rem, available_width, _fp_str, sz, fm,
                                    pts2, _ls, hyp_w,
                                    is_manual=(hyphens == "manual"),
                                )
                                if r2 is not None:
                                    p2, s2 = r2
                                    cur_frags.append(SpanFragment(
                                        text=p2, width=_meas_rich(p2),
                                        span_index=span_idx, font_path=_fp_str, font_size=sz,
                                    ))
                                    _flush(hyphenated=True)
                                    word_rem = s2
                                else:
                                    break  # can't split further

                            cur_frags.append(SpanFragment(
                                text=word_rem, width=_meas_rich(word_rem),
                                span_index=span_idx, font_path=_fp_str, font_size=sz,
                            ))
                            cur_width = cur_frags[-1].width
                        else:
                            _flush()
                            cur_frags.append(SpanFragment(
                                text=tok_text, width=tok_w,
                                span_index=span_idx,
                                font_path=_fp_str,
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
    """Set ``x_offset`` on each ``RichLine`` based on *text_align*.

    For ``text-align: justify``, counts space fragments as word gaps and
    distributes extra space evenly.  The last line stays left-aligned.
    """
    result: List[RichLine] = []
    num_lines = len(lines)
    for i, line in enumerate(lines):
        offset = 0.0
        justified = False
        word_gap = 0.0
        is_cjk_justify = False
        if text_align == "center":
            offset = (available_width - line.width) / 2.0
        elif text_align == "right":
            offset = available_width - line.width
        elif text_align == "justify" and i < num_lines - 1:
            extra = available_width - line.width
            if extra > 0:
                # Count space-only fragments as word boundaries
                space_count = 0
                has_non_space = False
                for frag in line.fragments:
                    if frag.svg_fragment is not None:
                        has_non_space = True
                        continue
                    if frag.text.strip():
                        has_non_space = True
                    elif frag.text == ' ':
                        space_count += 1
                if space_count > 0 and has_non_space:
                    word_gap = extra / space_count
                    justified = True
                elif space_count == 0 and has_non_space:
                    # CJK text: count total chars for per-char distribution
                    total_chars = sum(
                        len(f.text) for f in line.fragments
                        if f.svg_fragment is None and f.text.strip()
                    )
                    if total_chars > 1:
                        word_gap = extra / (total_chars - 1)
                        justified = True
                        is_cjk_justify = True
        result.append(RichLine(
            fragments=line.fragments,
            width=line.width,
            x_offset=max(0.0, offset),
            justified=justified,
            word_spacing_justify=word_gap,
            _cjk_justify=is_cjk_justify,
        ))
    return result


def compute_rich_block_size(
    lines: List[RichLine],
    line_height: float,
    font_size: float,
) -> tuple:
    """Return ``(width, height)`` for a rich text block."""
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
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
    hyphens: str = "none",
    lang: str = "en",
) -> float:
    """Return the min-content width for a rich span list."""
    from ..markup.parser import TextSpan  # type: ignore

    if fm is None:
        fm = FontManager.instance()
    if white_space in ("pre", "nowrap"):
        return get_max_content_width_rich(spans, base_font_chain, base_size, white_space, fm=fm, math_backend=math_backend,
                                          letter_spacing=letter_spacing, word_spacing=word_spacing)

    _hyph_active = hyphens != "none"
    max_w = 0.0
    for span in spans:
        if span.is_line_break:
            continue
        chain, sz = _resolve_span_font(span, base_font_chain, base_size, fm)
        fp = chain[0] if isinstance(chain, list) and chain else chain

        if span.baseline_shift in ("super", "sub") and span.font_size is None:
            sz = max(1, int(base_size * 0.7))

        if span.is_math and math_backend is not None:
            svg_frag = math_backend.render(span.text, float(sz))
            max_w = max(max_w, svg_frag.width)
            continue

        text = _re.sub(r'\s+', ' ', span.text).strip() if span.text.strip() else ""
        if not text:
            continue
        tokens = _tokenize_breakable(text)
        hyphen_w = _measure_span_text("-", chain, sz, fm) if _hyph_active else 0.0
        for tok_text, is_space in tokens:
            if not is_space:
                if _hyph_active:
                    clean = _strip_shy(tok_text)
                    if hyphens == "auto":
                        pts = _hyphen_points_auto(clean, lang)
                    else:
                        pts = _hyphen_points_manual(tok_text)
                    if pts:
                        fragments_r: List[str] = []
                        if hyphens == "manual":
                            prev_r = 0
                            for p in pts:
                                frag_r = _strip_shy(tok_text[prev_r:p])
                                fragments_r.append(frag_r)
                                prev_r = p + 1
                            tail_r = _strip_shy(tok_text[prev_r:])
                            if tail_r:
                                fragments_r.append(tail_r)
                        else:
                            prev_r = 0
                            for p in pts:
                                fragments_r.append(clean[prev_r:p])
                                prev_r = p
                            tail_r = clean[prev_r:]
                            if tail_r:
                                fragments_r.append(tail_r)
                        for fi, frag_r in enumerate(fragments_r):
                            fw = _measure_span_text(frag_r, chain, sz, fm,
                                                    letter_spacing=letter_spacing)
                            if fi < len(fragments_r) - 1:
                                fw += hyphen_w
                            max_w = max(max_w, fw)
                    else:
                        w = _measure_span_text(clean, chain, sz, fm,
                                               letter_spacing=letter_spacing, word_spacing=word_spacing)
                        max_w = max(max_w, w)
                else:
                    w = _measure_span_text(tok_text, chain, sz, fm,
                                           letter_spacing=letter_spacing, word_spacing=word_spacing)
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
    letter_spacing: float = 0.0,
    word_spacing: float = 0.0,
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

        if span.baseline_shift in ("super", "sub") and span.font_size is None:
            sz = max(1, int(base_size * 0.7))

        if span.is_math and math_backend is not None:
            svg_frag = math_backend.render(span.text, float(sz))
            total += svg_frag.width
            continue

        text = span.text
        if white_space not in ("pre", "pre-wrap"):
            text = _re.sub(r'\s+', ' ', text) if text else ""
        w = _measure_span_text(text, chain, sz, fm,
                               letter_spacing=letter_spacing, word_spacing=word_spacing)
        total += w
    return total
