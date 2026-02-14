"""Tests for the markup (HTML/Markdown) parser."""

import pytest
from latticesvg.markup.parser import (
    TextSpan,
    parse_html,
    parse_markdown,
    parse_markup,
    _parse_inline_style,
)


# -----------------------------------------------------------------------
# Inline CSS helper
# -----------------------------------------------------------------------


class TestParseInlineStyle:
    def test_single_property(self):
        assert _parse_inline_style("color: red") == {"color": "red"}

    def test_multiple_properties(self):
        result = _parse_inline_style("color: red; font-size: 14px")
        assert result == {"color": "red", "font-size": "14px"}

    def test_extra_whitespace(self):
        result = _parse_inline_style("  color :  blue ;  ")
        assert result["color"] == "blue"

    def test_empty_string(self):
        assert _parse_inline_style("") == {}


# -----------------------------------------------------------------------
# HTML subset parser
# -----------------------------------------------------------------------


class TestParseHTML:
    def test_plain_text(self):
        spans = parse_html("Hello world")
        assert len(spans) == 1
        assert spans[0].text == "Hello world"
        assert spans[0].font_weight is None

    def test_bold(self):
        spans = parse_html("Hello <b>world</b>!")
        assert len(spans) == 3
        assert spans[0].text == "Hello "
        assert spans[1].text == "world"
        assert spans[1].font_weight == "bold"
        assert spans[2].text == "!"
        assert spans[2].font_weight is None

    def test_strong(self):
        spans = parse_html("<strong>bold</strong>")
        assert spans[0].font_weight == "bold"

    def test_italic_em(self):
        spans = parse_html("<em>italic</em>")
        assert spans[0].font_style == "italic"

    def test_italic_i(self):
        spans = parse_html("<i>italic</i>")
        assert spans[0].font_style == "italic"

    def test_code(self):
        spans = parse_html("run <code>python</code>")
        code = spans[1]
        assert code.text == "python"
        assert code.font_family == "monospace"
        assert code.background_color == "#f0f0f0"

    def test_br(self):
        spans = parse_html("line1<br>line2")
        assert len(spans) == 3
        assert spans[1].is_line_break is True

    def test_sub(self):
        spans = parse_html("H<sub>2</sub>O")
        assert spans[1].baseline_shift == "sub"

    def test_sup(self):
        spans = parse_html("x<sup>2</sup>")
        assert spans[1].baseline_shift == "super"

    def test_underline(self):
        spans = parse_html("<u>underlined</u>")
        assert spans[0].text_decoration == "underline"

    def test_strikethrough_s(self):
        spans = parse_html("<s>deleted</s>")
        assert spans[0].text_decoration == "line-through"

    def test_strikethrough_del(self):
        spans = parse_html("<del>deleted</del>")
        assert spans[0].text_decoration == "line-through"

    def test_span_color(self):
        spans = parse_html('<span style="color: red">red</span>')
        assert spans[0].color == "red"

    def test_span_font_size(self):
        spans = parse_html('<span style="font-size: 24px">big</span>')
        assert spans[0].font_size == 24.0

    def test_span_font_family(self):
        spans = parse_html('<span style="font-family: serif">serif</span>')
        assert spans[0].font_family == "serif"

    def test_span_background_color(self):
        spans = parse_html('<span style="background-color: yellow">hi</span>')
        assert spans[0].background_color == "yellow"

    def test_span_font_weight(self):
        spans = parse_html('<span style="font-weight: bold">bold</span>')
        assert spans[0].font_weight == "bold"

    def test_span_font_style(self):
        spans = parse_html('<span style="font-style: italic">ital</span>')
        assert spans[0].font_style == "italic"

    def test_span_text_decoration(self):
        spans = parse_html('<span style="text-decoration: underline">u</span>')
        assert spans[0].text_decoration == "underline"

    def test_nested_bold_italic(self):
        spans = parse_html("<b><i>both</i></b>")
        assert spans[0].font_weight == "bold"
        assert spans[0].font_style == "italic"

    def test_math_inline(self):
        spans = parse_html("Energy: <math>E=mc^2</math>")
        assert len(spans) == 2
        assert spans[0].text == "Energy: "
        assert spans[0].is_math is False
        assert spans[1].text == "E=mc^2"
        assert spans[1].is_math is True

    def test_unknown_tag_ignored(self):
        spans = parse_html("<div>hello</div>")
        assert len(spans) == 1
        assert spans[0].text == "hello"

    def test_empty_input(self):
        spans = parse_html("")
        assert spans == []

    def test_multiple_mixed(self):
        spans = parse_html("A <b>bold</b> and <i>italic</i> text")
        texts = [s.text for s in spans]
        assert texts == ["A ", "bold", " and ", "italic", " text"]


# -----------------------------------------------------------------------
# Markdown parser
# -----------------------------------------------------------------------


class TestParseMarkdown:
    def test_bold(self):
        spans = parse_markdown("Hello **world**!")
        assert spans[1].text == "world"
        assert spans[1].font_weight == "bold"

    def test_italic(self):
        spans = parse_markdown("Hello *world*!")
        assert spans[1].text == "world"
        assert spans[1].font_style == "italic"

    def test_strikethrough(self):
        spans = parse_markdown("~~deleted~~")
        assert spans[0].text_decoration == "line-through"

    def test_inline_code(self):
        spans = parse_markdown("run `python`")
        code = spans[1]
        assert code.font_family == "monospace"

    def test_inline_math(self):
        spans = parse_markdown("Area = $\\pi r^2$")
        math_span = [s for s in spans if s.is_math]
        assert len(math_span) == 1
        assert math_span[0].text == "\\pi r^2"

    def test_bold_italic_together(self):
        spans = parse_markdown("**bold** and *italic*")
        assert spans[0].font_weight == "bold"
        italic_spans = [s for s in spans if s.font_style == "italic"]
        assert len(italic_spans) == 1

    def test_plain_text(self):
        spans = parse_markdown("no formatting here")
        assert len(spans) == 1
        assert spans[0].text == "no formatting here"


# -----------------------------------------------------------------------
# Unified parse_markup()
# -----------------------------------------------------------------------


class TestParseMarkup:
    def test_mode_none(self):
        spans = parse_markup("Hello <b>world</b>", markup="none")
        assert len(spans) == 1
        # Tags are NOT processed in "none" mode
        assert "<b>" in spans[0].text

    def test_mode_html(self):
        spans = parse_markup("Hello <b>world</b>", markup="html")
        assert any(s.font_weight == "bold" for s in spans)

    def test_mode_markdown(self):
        spans = parse_markup("Hello **world**", markup="markdown")
        assert any(s.font_weight == "bold" for s in spans)

    def test_unknown_mode_returns_plain(self):
        spans = parse_markup("test", markup="xml")
        assert len(spans) == 1
        assert spans[0].text == "test"
