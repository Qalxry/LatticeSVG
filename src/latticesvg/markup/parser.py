"""HTML-subset and Markdown markup parser for rich text spans.

Supports a minimal set of inline tags/syntax to produce ``List[TextSpan]``.
This is **not** a full HTML renderer — only inline-level elements are
recognised; block-level tags (``<div>``, ``<p>``, …) are silently ignored.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional


# -----------------------------------------------------------------------
# Data structures
# -----------------------------------------------------------------------

@dataclass
class TextSpan:
    """A contiguous run of text sharing the same inline style overrides.

    Fields set to *None* mean "inherit from the parent ``TextNode`` style".
    """

    text: str = ""
    font_weight: Optional[str] = None       # "bold" | "normal" | None
    font_style: Optional[str] = None        # "italic" | "normal" | None
    font_family: Optional[str] = None       # e.g. "monospace" for <code>
    font_size: Optional[float] = None       # px override
    color: Optional[str] = None
    background_color: Optional[str] = None  # e.g. <code> highlight
    baseline_shift: Optional[str] = None    # "super" | "sub" | None
    text_decoration: Optional[str] = None   # "underline" | "line-through"
    is_line_break: bool = False             # True for <br> pseudo-span
    is_math: bool = False                   # True for <math> inline formula


# -----------------------------------------------------------------------
# Inline style parser  (style="color:red; font-size:12px")
# -----------------------------------------------------------------------

_INLINE_STYLE_RE = re.compile(r"([\w-]+)\s*:\s*([^;]+)")


def _parse_inline_style(css: str) -> Dict[str, str]:
    """Parse a simplified CSS inline style string into a dict."""
    result: Dict[str, str] = {}
    for m in _INLINE_STYLE_RE.finditer(css):
        result[m.group(1).strip().lower()] = m.group(2).strip()
    return result


def _parse_css_length(raw: str) -> Optional[float]:
    """Best-effort parse of a CSS length value to float px."""
    raw = raw.strip().lower()
    if raw.endswith("px"):
        try:
            return float(raw[:-2])
        except ValueError:
            return None
    if raw.endswith("pt"):
        try:
            return float(raw[:-2]) * 96 / 72
        except ValueError:
            return None
    if raw.endswith("em") or raw.endswith("rem"):
        # Cannot resolve without context; store as-is — caller should
        # handle or ignore.
        return None
    try:
        return float(raw)
    except ValueError:
        return None


# -----------------------------------------------------------------------
# Stack-based HTML subset parser
# -----------------------------------------------------------------------

# Tags that push style state
_STYLE_TAGS = frozenset({
    "b", "strong", "i", "em", "code", "span",
    "sub", "sup", "u", "s", "del", "math",
})


@dataclass
class _StyleFrame:
    """One level on the tag-style stack."""
    tag: str
    font_weight: Optional[str] = None
    font_style: Optional[str] = None
    font_family: Optional[str] = None
    font_size: Optional[float] = None
    color: Optional[str] = None
    background_color: Optional[str] = None
    baseline_shift: Optional[str] = None
    text_decoration: Optional[str] = None
    is_math: bool = False


class _RichHTMLParser(HTMLParser):
    """Feed HTML-subset text and accumulate ``TextSpan`` list."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.spans: List[TextSpan] = []
        self._stack: List[_StyleFrame] = []

    # -- helpers --

    def _current_style(self) -> Dict[str, Any]:
        """Merge style frames from bottom to top."""
        merged: Dict[str, Any] = {}
        for frame in self._stack:
            if frame.font_weight is not None:
                merged["font_weight"] = frame.font_weight
            if frame.font_style is not None:
                merged["font_style"] = frame.font_style
            if frame.font_family is not None:
                merged["font_family"] = frame.font_family
            if frame.font_size is not None:
                merged["font_size"] = frame.font_size
            if frame.color is not None:
                merged["color"] = frame.color
            if frame.background_color is not None:
                merged["background_color"] = frame.background_color
            if frame.baseline_shift is not None:
                merged["baseline_shift"] = frame.baseline_shift
            if frame.text_decoration is not None:
                merged["text_decoration"] = frame.text_decoration
            if frame.is_math:
                merged["is_math"] = True
        return merged

    def _make_span(self, text: str) -> TextSpan:
        s = self._current_style()
        return TextSpan(
            text=text,
            font_weight=s.get("font_weight"),
            font_style=s.get("font_style"),
            font_family=s.get("font_family"),
            font_size=s.get("font_size"),
            color=s.get("color"),
            background_color=s.get("background_color"),
            baseline_shift=s.get("baseline_shift"),
            text_decoration=s.get("text_decoration"),
            is_math=s.get("is_math", False),
        )

    # -- HTMLParser callbacks --

    def handle_starttag(self, tag: str, attrs: list) -> None:
        tag = tag.lower()

        if tag == "br":
            self.spans.append(TextSpan(is_line_break=True))
            return

        if tag not in _STYLE_TAGS:
            return  # silently ignore unknown tags

        frame = _StyleFrame(tag=tag)

        if tag in ("b", "strong"):
            frame.font_weight = "bold"
        elif tag in ("i", "em"):
            frame.font_style = "italic"
        elif tag == "code":
            frame.font_family = "monospace"
            frame.background_color = "#f0f0f0"
        elif tag == "u":
            frame.text_decoration = "underline"
        elif tag in ("s", "del"):
            frame.text_decoration = "line-through"
        elif tag == "sub":
            frame.baseline_shift = "sub"
        elif tag == "sup":
            frame.baseline_shift = "super"
        elif tag == "math":
            frame.is_math = True
        elif tag == "span":
            attrs_dict = dict(attrs)
            style_str = attrs_dict.get("style", "")
            if style_str:
                css = _parse_inline_style(style_str)
                if "color" in css:
                    frame.color = css["color"]
                if "background-color" in css:
                    frame.background_color = css["background-color"]
                if "font-size" in css:
                    v = _parse_css_length(css["font-size"])
                    if v is not None:
                        frame.font_size = v
                if "font-family" in css:
                    frame.font_family = css["font-family"]
                if "font-weight" in css:
                    frame.font_weight = css["font-weight"]
                if "font-style" in css:
                    frame.font_style = css["font-style"]
                if "text-decoration" in css:
                    frame.text_decoration = css["text-decoration"]

        self._stack.append(frame)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "br":
            return
        if tag not in _STYLE_TAGS:
            return
        # Pop matching tag (tolerant: pop the most recent match)
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i].tag == tag:
                self._stack.pop(i)
                break

    def handle_data(self, data: str) -> None:
        if not data:
            return
        # Check if we're inside a <math> tag
        in_math = any(f.is_math for f in self._stack)
        if in_math:
            # Inside <math>, accumulate the raw LaTeX text as a single span
            span = self._make_span(data)
            self.spans.append(span)
        else:
            span = self._make_span(data)
            self.spans.append(span)


# -----------------------------------------------------------------------
# Public API: HTML subset parser
# -----------------------------------------------------------------------

def parse_html(text: str) -> List[TextSpan]:
    """Parse an HTML-subset string into a list of ``TextSpan``.

    Supported tags: ``<b>``/``<strong>``, ``<i>``/``<em>``, ``<code>``,
    ``<span style="...">``, ``<br>``, ``<sub>``, ``<sup>``, ``<u>``,
    ``<s>``/``<del>``, ``<math>`` (inline LaTeX formula).

    Unsupported tags are silently ignored (their text content is still
    included as plain text).

    Example::

        >>> spans = parse_html('Hello <b>world</b>!')
        >>> [(s.text, s.font_weight) for s in spans]
        [('Hello ', None), ('world', 'bold'), ('!', None)]
    """
    parser = _RichHTMLParser()
    parser.feed(text)
    return parser.spans


# -----------------------------------------------------------------------
# Public API: Markdown subset parser
# -----------------------------------------------------------------------

# Order matters: ** before *, ~~ before ~, $$ before $
_MD_PATTERNS = [
    # Bold: **text**
    (re.compile(r"\*\*(.+?)\*\*", re.DOTALL), r"<b>\1</b>"),
    # Italic: *text*
    (re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", re.DOTALL), r"<i>\1</i>"),
    # Strikethrough: ~~text~~
    (re.compile(r"~~(.+?)~~", re.DOTALL), r"<del>\1</del>"),
    # Inline code: `text`
    (re.compile(r"`(.+?)`"), r"<code>\1</code>"),
    # Inline math: $tex$ (but not $$...$$)
    (re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)"), r"<math>\1</math>"),
]


def _markdown_to_html(text: str) -> str:
    """Convert a Markdown-subset string to the HTML subset."""
    for pattern, replacement in _MD_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def parse_markdown(text: str) -> List[TextSpan]:
    """Parse a Markdown-subset string into a list of ``TextSpan``.

    Supported syntax: ``**bold**``, ``*italic*``, `` `code` ``,
    ``~~strikethrough~~``, ``$latex$`` (inline math).

    Example::

        >>> spans = parse_markdown('Hello **world**!')
        >>> [(s.text, s.font_weight) for s in spans]
        [('Hello ', None), ('world', 'bold'), ('!', None)]
    """
    html = _markdown_to_html(text)
    return parse_html(html)


# -----------------------------------------------------------------------
# Unified entry point
# -----------------------------------------------------------------------

def parse_markup(text: str, markup: str = "none") -> List[TextSpan]:
    """Parse *text* according to the *markup* mode.

    Parameters
    ----------
    text : str
        The source text, possibly containing inline markup.
    markup : str
        ``"none"`` — return a single plain-text span (default).
        ``"html"`` — parse HTML subset tags.
        ``"markdown"`` — parse Markdown subset syntax.

    Returns
    -------
    List[TextSpan]
        Ordered list of styled text segments.
    """
    if markup == "html":
        return parse_html(text)
    if markup == "markdown":
        return parse_markdown(text)
    # "none" or anything else — plain text
    return [TextSpan(text=text)]
