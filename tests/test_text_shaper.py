"""Tests for text shaping (line breaking, alignment, sizing)."""

import pytest
from unittest.mock import MagicMock, patch
from latticesvg.text.shaper import (
    Line,
    align_lines,
    break_lines,
    compute_text_block_size,
    get_max_content_width,
    get_min_content_width,
    measure_text,
)
from latticesvg.text.font import FontManager, GlyphMetrics


# ------------------------------------------------------------------
# Mock font manager to avoid system font dependency
# ------------------------------------------------------------------

@pytest.fixture
def mock_fm():
    """A FontManager-like mock where every char has advance_x=10."""
    fm = MagicMock(spec=FontManager)
    fm.glyph_metrics.return_value = GlyphMetrics(
        advance_x=10.0,
        bearing_x=0.0,
        bearing_y=10.0,
        width=8.0,
        height=12.0,
    )
    return fm


FAKE_FONT = "/fake/font.ttf"


# ------------------------------------------------------------------
# measure_text
# ------------------------------------------------------------------

class TestMeasureText:
    def test_empty_string(self, mock_fm):
        assert measure_text("", FAKE_FONT, 16, fm=mock_fm) == 0.0

    def test_single_char(self, mock_fm):
        assert measure_text("A", FAKE_FONT, 16, fm=mock_fm) == 10.0

    def test_multiple_chars(self, mock_fm):
        assert measure_text("Hello", FAKE_FONT, 16, fm=mock_fm) == 50.0


# ------------------------------------------------------------------
# break_lines
# ------------------------------------------------------------------

class TestBreakLines:
    def test_single_word_fits(self, mock_fm):
        lines = break_lines("Hello", 100, FAKE_FONT, 16, fm=mock_fm)
        assert len(lines) == 1
        assert lines[0].text == "Hello"

    def test_wrap_at_word_boundary(self, mock_fm):
        # "Hello World" = 11 chars * 10px = 110px
        # Available width = 60px → should wrap
        lines = break_lines("Hello World", 60, FAKE_FONT, 16, fm=mock_fm)
        assert len(lines) == 2
        assert lines[0].text == "Hello"
        assert lines[1].text == "World"

    def test_nowrap(self, mock_fm):
        lines = break_lines("Hello World", 30, FAKE_FONT, 16, "nowrap", fm=mock_fm)
        assert len(lines) == 1

    def test_pre_preserves_newlines(self, mock_fm):
        lines = break_lines("Line1\nLine2\nLine3", 1000, FAKE_FONT, 16, "pre", fm=mock_fm)
        assert len(lines) == 3
        assert lines[0].text == "Line1"
        assert lines[1].text == "Line2"

    def test_whitespace_collapse(self, mock_fm):
        lines = break_lines("  Hello   World  ", 1000, FAKE_FONT, 16, fm=mock_fm)
        assert len(lines) == 1
        assert lines[0].text == "Hello World"


# ------------------------------------------------------------------
# overflow-wrap: break-word
# ------------------------------------------------------------------

class TestBreakWord:
    """Tests for ``overflow-wrap: break-word`` behaviour."""

    def test_normal_does_not_break_word(self, mock_fm):
        # "Superlongword" = 13 chars × 10px = 130px, avail=50px
        # With normal overflow-wrap, it stays as one unbroken token.
        lines = break_lines("Superlongword", 50, FAKE_FONT, 16,
                            overflow_wrap="normal", fm=mock_fm)
        assert len(lines) == 1
        assert lines[0].text == "Superlongword"

    def test_break_word_splits_single_long_word(self, mock_fm):
        # "Superlongword" = 13 chars × 10px = 130px, avail=50px → 5 chars per line
        lines = break_lines("Superlongword", 50, FAKE_FONT, 16,
                            overflow_wrap="break-word", fm=mock_fm)
        assert len(lines) == 3
        assert lines[0].text == "Super"
        assert lines[1].text == "longw"
        assert lines[2].text == "ord"

    def test_break_word_moves_word_to_next_line_if_fits(self, mock_fm):
        # "Hello World" at 60px; each char 10px.
        # "Hello" (50) + " " (10) = 60; "World" (50) fits on a new line.
        # overflow-wrap:break-word should behave like normal here — no breaking.
        lines = break_lines("Hello World", 60, FAKE_FONT, 16,
                            overflow_wrap="break-word", fm=mock_fm)
        assert len(lines) == 2
        assert lines[0].text == "Hello"
        assert lines[1].text == "World"

    def test_break_word_after_short_words(self, mock_fm):
        # "Hi Superlongword" avail=50px
        # "Hi" (20) fits, "Superlongword" (130) overflows AND > avail (50).
        # Flush "Hi", then break "Superlongword" into 50px chunks.
        lines = break_lines("Hi Superlongword", 50, FAKE_FONT, 16,
                            overflow_wrap="break-word", fm=mock_fm)
        assert lines[0].text == "Hi"
        assert lines[1].text == "Super"
        assert lines[2].text == "longw"
        assert lines[3].text == "ord"

    def test_break_word_anywhere_alias(self, mock_fm):
        # "anywhere" should behave like "break-word"
        lines = break_lines("Superlongword", 50, FAKE_FONT, 16,
                            overflow_wrap="anywhere", fm=mock_fm)
        assert len(lines) == 3
        assert lines[0].text == "Super"


# ------------------------------------------------------------------
# align_lines
# ------------------------------------------------------------------

class TestAlignLines:
    def test_left_align(self):
        lines = [Line("Hello", 50, char_count=5)]
        result = align_lines(lines, 200, "left")
        assert result[0].x_offset == 0.0

    def test_center_align(self):
        lines = [Line("Hello", 50, char_count=5)]
        result = align_lines(lines, 200, "center")
        assert result[0].x_offset == pytest.approx(75.0)

    def test_right_align(self):
        lines = [Line("Hello", 50, char_count=5)]
        result = align_lines(lines, 200, "right")
        assert result[0].x_offset == pytest.approx(150.0)


# ------------------------------------------------------------------
# compute_text_block_size
# ------------------------------------------------------------------

class TestTextBlockSize:
    def test_single_line(self):
        lines = [Line("Hello", 50, char_count=5)]
        w, h = compute_text_block_size(lines, 1.5, 16)
        assert w == 50.0
        assert h == pytest.approx(24.0)  # 16 * 1.5

    def test_multiple_lines(self):
        lines = [
            Line("Hello", 50, char_count=5),
            Line("World", 50, char_count=5),
        ]
        w, h = compute_text_block_size(lines, 1.5, 16)
        assert w == 50.0
        assert h == pytest.approx(48.0)  # 2 * 24


# ------------------------------------------------------------------
# min/max content width
# ------------------------------------------------------------------

class TestContentWidth:
    def test_min_content_width(self, mock_fm):
        # Longest word: "World" = 5 chars * 10 = 50
        result = get_min_content_width("Hello World", FAKE_FONT, 16, fm=mock_fm)
        assert result == pytest.approx(50.0)

    def test_max_content_width(self, mock_fm):
        # Single line: "Hello World" = 11 chars * 10 = 110
        result = get_max_content_width("Hello World", FAKE_FONT, 16, fm=mock_fm)
        assert result == pytest.approx(110.0)
