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
    measure_word,
    _strip_shy,
    _hyphen_points_manual,
    _SHY,
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


# ------------------------------------------------------------------
# white-space: pre-line
# ------------------------------------------------------------------

class TestPreLine:
    def test_pre_line_preserves_newlines(self, mock_fm):
        """pre-line should preserve explicit \n breaks."""
        text = "Hello\nWorld"
        lines = break_lines(text, 200, FAKE_FONT, 16, "pre-line", fm=mock_fm)
        assert len(lines) == 2
        assert lines[0].text == "Hello"
        assert lines[1].text == "World"

    def test_pre_line_collapses_spaces(self, mock_fm):
        """pre-line should collapse consecutive spaces like normal mode."""
        text = "Hello   World"
        lines = break_lines(text, 200, FAKE_FONT, 16, "pre-line", fm=mock_fm)
        assert len(lines) == 1
        assert lines[0].text == "Hello World"

    def test_pre_line_wraps_long_segments(self, mock_fm):
        """pre-line should word-wrap within each segment."""
        # "Hello World" = 110px, avail = 80px => wraps
        text = "Hello World"
        lines = break_lines(text, 80, FAKE_FONT, 16, "pre-line", fm=mock_fm)
        assert len(lines) == 2
        assert lines[0].text == "Hello"
        assert lines[1].text == "World"

    def test_pre_line_newline_plus_wrap(self, mock_fm):
        """pre-line combines newline preservation and wrapping."""
        # segment1 fits, segment2 needs wrapping
        text = "Hi\nHello World"
        lines = break_lines(text, 80, FAKE_FONT, 16, "pre-line", fm=mock_fm)
        assert len(lines) == 3
        assert lines[0].text == "Hi"
        assert lines[1].text == "Hello"
        assert lines[2].text == "World"


# ------------------------------------------------------------------
# letter-spacing / word-spacing (P2-4)
# ------------------------------------------------------------------

class TestLetterSpacing:
    """Tests for letter-spacing support in measure_text & break_lines."""

    def test_measure_text_letter_spacing(self, mock_fm):
        # "Hello" = 5 chars × 10px = 50px
        # letter-spacing=2 adds 2px between chars (4 gaps) = 8px
        w = measure_text("Hello", FAKE_FONT, 16, fm=mock_fm, letter_spacing=2.0)
        assert w == pytest.approx(58.0)

    def test_measure_text_letter_spacing_single_char(self, mock_fm):
        # Single char — no gap added
        w = measure_text("A", FAKE_FONT, 16, fm=mock_fm, letter_spacing=5.0)
        assert w == pytest.approx(10.0)

    def test_measure_text_letter_spacing_empty(self, mock_fm):
        w = measure_text("", FAKE_FONT, 16, fm=mock_fm, letter_spacing=5.0)
        assert w == pytest.approx(0.0)

    def test_measure_word_passes_through(self, mock_fm):
        # measure_word should accept and pass letter_spacing
        w = measure_word("Hi", FAKE_FONT, 16, fm=mock_fm, letter_spacing=3.0)
        assert w == pytest.approx(23.0)  # 2 × 10 + 1 × 3

    def test_break_lines_with_letter_spacing(self, mock_fm):
        # "Hello World" with letter_spacing=2
        # Tokens: "Hello"(58), " "(10), "World"(58)
        # Token widths: "Hello" = 5×10 + 4×2 = 58
        # Bridge: when appending " " after "Hello", bridge=0 (space)
        # When appending "World" after " ", bridge=0 (previous is space)
        # But flush re-measures: "Hello" = 58px
        # Available 70px → "Hello"(58) + " "(10) = 68, then
        # "World"(58) → 68 + 58 = 126 > 70 → wraps
        lines = break_lines("Hello World", 70, FAKE_FONT, 16,
                            fm=mock_fm, letter_spacing=2.0)
        assert len(lines) == 2
        assert lines[0].text == "Hello"
        assert lines[1].text == "World"

    def test_break_lines_letter_spacing_bridge(self, mock_fm):
        """Adjacent CJK chars get bridge letter-spacing at token boundary."""
        # Two adjacent CJK chars: each is its own token (10px each)
        # With letter_spacing=5, bridge=5 between them
        # Available 24px: 10 + 5(bridge) + 10 = 25 > 24 → should wrap
        # Without bridge fix: 10 + 10 = 20 ≤ 24 → would NOT wrap (bug)
        lines = break_lines("\u4f60\u597d", 24, FAKE_FONT, 16,
                            fm=mock_fm, letter_spacing=5.0)
        assert len(lines) == 2
        assert lines[0].text == "\u4f60"
        assert lines[1].text == "\u597d"

    def test_break_lines_letter_spacing_no_overflow(self, mock_fm):
        """With enough width, letter-spacing bridge doesn't cause false wraps."""
        # "AB" = two non-CJK chars form one token → no bridge
        # Token width = 2×10 + 1×2 = 22px, available 30 → fits
        lines = break_lines("AB", 30, FAKE_FONT, 16,
                            fm=mock_fm, letter_spacing=2.0)
        assert len(lines) == 1
        assert lines[0].text == "AB"

    def test_min_content_width_with_letter_spacing(self, mock_fm):
        # Longest word "World" (5 chars): 50 + 4 × 2 = 58
        result = get_min_content_width("Hello World", FAKE_FONT, 16,
                                       fm=mock_fm, letter_spacing=2.0)
        assert result == pytest.approx(58.0)

    def test_max_content_width_with_letter_spacing(self, mock_fm):
        # "Hello World" = 11 chars × 10 + 10 × 2 (letter-spacing) = 130
        result = get_max_content_width("Hello World", FAKE_FONT, 16,
                                       fm=mock_fm, letter_spacing=2.0)
        assert result == pytest.approx(130.0)


class TestWordSpacing:
    """Tests for word-spacing support in measure_text & break_lines."""

    def test_measure_text_word_spacing(self, mock_fm):
        # "Hi Ho" = 5 chars × 10px = 50px
        # word-spacing=4 adds 4px for the space at index 2 = 54px
        w = measure_text("Hi Ho", FAKE_FONT, 16, fm=mock_fm, word_spacing=4.0)
        assert w == pytest.approx(54.0)

    def test_measure_text_word_spacing_no_spaces(self, mock_fm):
        # "Hello" has no spaces — word-spacing has no effect
        w = measure_text("Hello", FAKE_FONT, 16, fm=mock_fm, word_spacing=10.0)
        assert w == pytest.approx(50.0)

    def test_measure_text_combined_spacing(self, mock_fm):
        # "A B" = 3 chars × 10px = 30px
        # letter-spacing=2 → 2 gaps × 2 = 4 → 34px
        # word-spacing=5 → 1 space × 5 = 5 → 39px
        w = measure_text("A B", FAKE_FONT, 16, fm=mock_fm,
                         letter_spacing=2.0, word_spacing=5.0)
        assert w == pytest.approx(39.0)


# ------------------------------------------------------------------
# text-align: justify (P1-1)
# ------------------------------------------------------------------

class TestJustify:
    """Tests for text-align: justify in align_lines."""

    def test_justify_multi_word(self):
        """Multiple words → extra space distributed into word gaps."""
        lines = [
            Line("Hello World Test", 160, char_count=16),
            Line("End", 30, char_count=3),
        ]
        result = align_lines(lines, 200, "justify")
        # First line: extra = 200 - 160 = 40, 2 word gaps → 20px each
        assert result[0].justified is True
        assert result[0].word_spacing_justify == pytest.approx(20.0)
        # Last line: stays left-aligned (CSS standard)
        assert result[1].justified is False
        assert result[1].x_offset == 0.0

    def test_justify_single_line_not_justified(self):
        """A single line (last line) should NOT be justified."""
        lines = [Line("Hello", 50, char_count=5)]
        result = align_lines(lines, 200, "justify")
        assert result[0].justified is False
        assert result[0].x_offset == 0.0

    def test_justify_single_word_line(self):
        """A line with one word cannot be justified (no gaps)."""
        lines = [
            Line("Superlongword", 130, char_count=13),
            Line("End", 30, char_count=3),
        ]
        result = align_lines(lines, 200, "justify")
        # Single word without spaces — try CJK-style char distribution
        # But "Superlongword" has no CJK detection logic; it falls through
        # to CJK fallback: extra = 200-130 = 70, 12 char gaps → ≈5.83
        assert result[0].justified is True

    def test_justify_cjk_no_spaces(self):
        """CJK text without spaces distributes gaps between characters."""
        lines = [
            Line("你好世界测试", 60, char_count=6),
            Line("末", 10, char_count=1),
        ]
        result = align_lines(lines, 100, "justify")
        # extra = 100 - 60 = 40, 5 char gaps → 8px each
        assert result[0].justified is True
        assert result[0].word_spacing_justify == pytest.approx(8.0)

    def test_justify_preserves_line_data(self):
        """Justify should preserve original text and width."""
        lines = [
            Line("Hello World", 110, char_count=11),
            Line("End", 30, char_count=3),
        ]
        result = align_lines(lines, 200, "justify")
        assert result[0].text == "Hello World"
        assert result[0].width == 110

    def test_justify_x_offset_zero(self):
        """Justified lines have x_offset=0 (content starts at left edge)."""
        lines = [
            Line("Hello World", 110, char_count=11),
            Line("End", 30, char_count=3),
        ]
        result = align_lines(lines, 200, "justify")
        assert result[0].x_offset == 0.0


# ------------------------------------------------------------------
# Hyphens helpers
# ------------------------------------------------------------------

class TestHyphensHelpers:
    def test_strip_shy(self):
        assert _strip_shy("hel\u00ADlo") == "hello"
        assert _strip_shy("abc") == "abc"
        assert _strip_shy("") == ""

    def test_hyphen_points_manual(self):
        word = "un\u00ADbreak\u00ADable"
        pts = _hyphen_points_manual(word)
        assert pts == [2, 8]

    def test_hyphen_points_manual_no_shy(self):
        assert _hyphen_points_manual("hello") == []


# ------------------------------------------------------------------
# Hyphens — manual mode
# ------------------------------------------------------------------

class TestHyphensManual:
    """Test hyphens='manual' using soft-hyphen (U+00AD) insertion points."""

    def test_manual_break_at_shy(self, mock_fm):
        """A word with SHY should break at the soft-hyphen when it overflows."""
        # "un\u00ADbreakable" — with 10px/char, total clean = 11 chars = 110px
        # width=70 → "un-" prefix (30px) fits, "breakable" goes to next line
        text = f"un{_SHY}breakable"
        lines = break_lines(text, 70, FAKE_FONT, 16, fm=mock_fm,
                            hyphens="manual")
        assert len(lines) == 2
        assert lines[0].text == "un-"
        assert lines[0].hyphenated is True
        assert lines[1].text == "breakable"

    def test_manual_no_break_when_fits(self, mock_fm):
        """Word with SHY that fits on one line — SHY is stripped, no hyphen."""
        text = f"he{_SHY}llo"
        lines = break_lines(text, 200, FAKE_FONT, 16, fm=mock_fm,
                            hyphens="manual")
        assert len(lines) == 1
        assert lines[0].text == "hello"
        assert lines[0].hyphenated is False

    def test_manual_noop_without_shy(self, mock_fm):
        """Without SHY chars, manual mode should not break words."""
        text = "longword"  # 80px
        lines = break_lines(text, 50, FAKE_FONT, 16, fm=mock_fm,
                            hyphens="manual")
        # Cannot hyphenate — word stays as-is on new line
        assert len(lines) == 1
        assert lines[0].text == "longword"

    def test_manual_multiple_shy(self, mock_fm):
        """Multiple SHY points — should pick the longest fitting prefix."""
        # "un\u00ADbreak\u00ADable" → clean "unbreakable" = 110px
        # width=80: "un-" = 30px fits, "unbreak-" = 80px (7 chars + '-')
        # "unbreak-" = measure_text("unbreak-", ...) = 8*10 = 80px — fits exactly
        text = f"un{_SHY}break{_SHY}able"
        lines = break_lines(text, 80, FAKE_FONT, 16, fm=mock_fm,
                            hyphens="manual")
        assert len(lines) == 2
        assert lines[0].text == "unbreak-"
        assert lines[0].hyphenated is True
        assert lines[1].text == "able"

    def test_manual_nowrap_strips_shy(self, mock_fm):
        """In nowrap mode, SHY chars are stripped but no wrapping occurs."""
        text = f"hel{_SHY}lo wor{_SHY}ld"
        lines = break_lines(text, 50, FAKE_FONT, 16, white_space="nowrap",
                            fm=mock_fm, hyphens="manual")
        assert len(lines) == 1
        assert lines[0].text == "hello world"


# ------------------------------------------------------------------
# Hyphens — auto mode
# ------------------------------------------------------------------

class TestHyphensAuto:
    """Test hyphens='auto' with a mocked pyphen backend."""

    def test_auto_basic_split(self, mock_fm):
        """Auto-hyphens with a mock that claims 'hyphenation' breaks as 'hy-phenation'."""
        # Use side_effect so only "hyphenation" gets split; suffix gets no points
        def _mock_points(word, lang):
            if word == "hyphenation":
                return [2]
            return []
        with patch("latticesvg.text.shaper._hyphen_points_auto", side_effect=_mock_points):
            # "hyphenation" = 11 chars = 110px; width=50
            # With split at 2: "hy-" = 30px fits in 50px
            lines = break_lines("hyphenation", 50, FAKE_FONT, 16, fm=mock_fm,
                                hyphens="auto", lang="en")
        assert len(lines) == 2
        assert lines[0].text == "hy-"
        assert lines[0].hyphenated is True
        assert lines[1].text == "phenation"

    def test_auto_no_points_fallback(self, mock_fm):
        """If pyphen returns no points, word moves to next line intact."""
        with patch("latticesvg.text.shaper._hyphen_points_auto", return_value=[]):
            lines = break_lines("longword", 50, FAKE_FONT, 16, fm=mock_fm,
                                hyphens="auto", lang="en")
        assert len(lines) == 1
        assert lines[0].text == "longword"
        assert lines[0].hyphenated is False

    def test_auto_picks_best_point(self, mock_fm):
        """Should pick the longest prefix that fits (greedy)."""
        # "examination" = 11 chars; split points at [2, 5, 7]
        # width=80 → "examina-" = 8*10 = 80px fits exactly
        def _mock_points(word, lang):
            if word == "examination":
                return [2, 5, 7]
            return []
        with patch("latticesvg.text.shaper._hyphen_points_auto", side_effect=_mock_points):
            lines = break_lines("examination", 80, FAKE_FONT, 16, fm=mock_fm,
                                hyphens="auto", lang="en")
        assert len(lines) == 2
        assert lines[0].text == "examina-"
        assert lines[0].hyphenated is True
        assert lines[1].text == "tion"


# ------------------------------------------------------------------
# Hyphens — min-content-width
# ------------------------------------------------------------------

class TestHyphensMinContentWidth:
    """get_min_content_width should be syllable-aware when hyphens != 'none'."""

    def test_min_content_auto(self, mock_fm):
        """With auto hyphens, min-width should be the widest syllable + hyphen."""
        # "hyphenation" = 110px without hyphens
        # With split at [2, 5]: syllables "hy", "phe", "nation"
        # widths: "hy-" = 30, "phe-" = 40, "nation" = 60
        # min-content = 60
        with patch("latticesvg.text.shaper._hyphen_points_auto", return_value=[2, 5]):
            w = get_min_content_width("hyphenation", FAKE_FONT, 16, fm=mock_fm,
                                      hyphens="auto", lang="en")
        assert w == 60.0

    def test_min_content_manual(self, mock_fm):
        """With manual hyphens, SHY positions determine syllables."""
        text = f"un{_SHY}break{_SHY}able"
        w = get_min_content_width(text, FAKE_FONT, 16, fm=mock_fm,
                                  hyphens="manual")
        # syllables: "un-" = 30, "break-" = 60, "able" = 40
        # min-content = 60
        assert w == 60.0

    def test_min_content_none_ignores_shy(self, mock_fm):
        """With hyphens='none', SHY does not affect min-content width."""
        # "unbreakable" with SHY should still measure as full word
        text = f"un{_SHY}breakable"
        w = get_min_content_width(text, FAKE_FONT, 16, fm=mock_fm,
                                  hyphens="none")
        # The SHY char itself has advance_x=10 in our mock, so
        # 12 chars * 10 = 120
        assert w == 120.0
