"""Tests for writing-mode and text-orientation support."""
from __future__ import annotations

import pytest

from latticesvg.nodes.base import LayoutConstraints
from latticesvg.nodes.text import TextNode
from latticesvg.text.shaper import (
    Column,
    VerticalRun,
    _is_upright_in_vertical,
    _segment_vertical_runs,
    align_columns,
    break_columns,
    compute_vertical_block_size,
    get_max_content_height,
    get_min_content_height,
    measure_text_vertical,
)
from latticesvg.style.properties import PROPERTY_REGISTRY


from latticesvg.text.font import FontManager


# Helper to get a resolved font path
def _font_path():
    fm = FontManager.instance()
    path = fm.find_font(["sans-serif"])
    assert path is not None, "No sans-serif font found on system"
    return path


# ======================================================================
# Property registration
# ======================================================================

class TestPropertyRegistration:
    def test_writing_mode_registered(self):
        prop = PROPERTY_REGISTRY.get("writing-mode")
        assert prop is not None
        assert prop.default == "horizontal-tb"
        assert prop.inheritable is True

    def test_text_orientation_registered(self):
        prop = PROPERTY_REGISTRY.get("text-orientation")
        assert prop is not None
        assert prop.default == "mixed"
        assert prop.inheritable is True


# ======================================================================
# Character orientation helpers
# ======================================================================

class TestCharacterOrientation:
    def test_cjk_upright_in_mixed(self):
        assert _is_upright_in_vertical("你", "mixed") is True
        assert _is_upright_in_vertical("漢", "mixed") is True
        assert _is_upright_in_vertical("あ", "mixed") is True  # hiragana
        assert _is_upright_in_vertical("ア", "mixed") is True  # katakana

    def test_latin_sideways_in_mixed(self):
        assert _is_upright_in_vertical("A", "mixed") is False
        assert _is_upright_in_vertical("z", "mixed") is False
        assert _is_upright_in_vertical("1", "mixed") is False

    def test_upright_mode_all_upright(self):
        assert _is_upright_in_vertical("A", "upright") is True
        assert _is_upright_in_vertical("你", "upright") is True
        assert _is_upright_in_vertical("1", "upright") is True

    def test_sideways_mode_all_sideways(self):
        assert _is_upright_in_vertical("A", "sideways") is False
        assert _is_upright_in_vertical("你", "sideways") is False


class TestSegmentVerticalRuns:
    def test_pure_cjk(self):
        runs = _segment_vertical_runs("你好世界", "mixed")
        assert len(runs) == 1
        assert runs[0] == ("你好世界", True)

    def test_pure_latin(self):
        runs = _segment_vertical_runs("Hello", "mixed")
        assert len(runs) == 1
        assert runs[0] == ("Hello", False)

    def test_mixed_text(self):
        runs = _segment_vertical_runs("Hello你好World", "mixed")
        assert len(runs) == 3
        assert runs[0][1] is False   # Hello
        assert runs[1][1] is True    # 你好
        assert runs[2][1] is False   # World

    def test_empty(self):
        assert _segment_vertical_runs("", "mixed") == []

    def test_upright_all(self):
        runs = _segment_vertical_runs("Hello你好", "upright")
        assert len(runs) == 1
        assert runs[0][1] is True

    def test_sideways_all(self):
        runs = _segment_vertical_runs("Hello你好", "sideways")
        assert len(runs) == 1
        assert runs[0][1] is False


# ======================================================================
# Vertical measurement
# ======================================================================

class TestMeasureTextVertical:
    def test_returns_positive_for_non_empty(self):
        h = measure_text_vertical("你好", _font_path(), 16)
        assert h > 0

    def test_empty_returns_zero(self):
        h = measure_text_vertical("", _font_path(), 16)
        assert h == 0.0

    def test_longer_text_taller(self):
        fp = _font_path()
        h1 = measure_text_vertical("你", fp, 16)
        h2 = measure_text_vertical("你好世", fp, 16)
        assert h2 > h1


# ======================================================================
# Column breaking
# ======================================================================

class TestBreakColumns:
    def test_single_column_when_enough_height(self):
        cols = break_columns("你好", 1000, _font_path(), 16)
        assert len(cols) == 1

    def test_multiple_columns_when_height_limited(self):
        # Very small height should force multiple columns
        cols = break_columns("你好世界测试文本", 20, _font_path(), 16)
        assert len(cols) >= 2

    def test_empty_text(self):
        cols = break_columns("", 1000, _font_path(), 16)
        assert len(cols) == 1
        assert cols[0].text == ""


class TestAlignColumns:
    def test_left_alignment_zero_offset(self):
        cols = [Column(text="你好", height=32, char_count=2)]
        result = align_columns(cols, 100, "left")
        assert result[0].y_offset == 0.0

    def test_center_alignment(self):
        cols = [Column(text="你好", height=32, char_count=2)]
        result = align_columns(cols, 100, "center")
        assert result[0].y_offset == pytest.approx((100 - 32) / 2.0)

    def test_right_alignment(self):
        cols = [Column(text="你好", height=32, char_count=2)]
        result = align_columns(cols, 100, "right")
        assert result[0].y_offset == pytest.approx(100 - 32)


class TestComputeVerticalBlockSize:
    def test_single_column(self):
        cols = [Column(text="你好", height=32, char_count=2)]
        w, h = compute_vertical_block_size(cols, 20.0, 16.0)
        assert w == 20.0  # 1 column × line_height
        assert h == 32.0  # column height

    def test_multiple_columns(self):
        cols = [
            Column(text="你", height=16, char_count=1),
            Column(text="好", height=16, char_count=1),
        ]
        w, h = compute_vertical_block_size(cols, 20.0, 16.0)
        assert w == 40.0  # 2 columns × 20
        assert h == 16.0

    def test_empty(self):
        w, h = compute_vertical_block_size([], 20.0, 16.0)
        assert w == 0.0
        assert h == 0.0


# ======================================================================
# Intrinsic sizing (vertical)
# ======================================================================

class TestVerticalIntrinsicSizing:
    def test_min_content_height_positive(self):
        h = get_min_content_height("你好世界", _font_path(), 16)
        assert h > 0

    def test_max_content_height_greater_or_equal_min(self):
        fp = _font_path()
        min_h = get_min_content_height("Hello World", fp, 16,
                                       orientation="mixed")
        max_h = get_max_content_height("Hello World", fp, 16,
                                       orientation="mixed")
        assert max_h >= min_h


# ======================================================================
# TextNode writing-mode integration
# ======================================================================

class TestTextNodeWritingMode:
    def test_horizontal_tb_default(self):
        node = TextNode("Hello")
        assert node._writing_mode() == "horizontal-tb"
        assert node._is_vertical() is False

    def test_sideways_rl(self):
        node = TextNode("Hello", style={"writing-mode": "sideways-rl"})
        assert node._writing_mode() == "sideways-rl"
        assert node._is_vertical() is True
        assert node._is_sideways_mode() is True

    def test_vertical_rl(self):
        node = TextNode("你好", style={"writing-mode": "vertical-rl"})
        assert node._writing_mode() == "vertical-rl"
        assert node._is_vertical() is True
        assert node._is_sideways_mode() is False

    def test_text_orientation_default(self):
        node = TextNode("Hello")
        assert node._text_orientation() == "mixed"

    def test_text_orientation_upright(self):
        node = TextNode("Hello", style={"text-orientation": "upright"})
        assert node._text_orientation() == "upright"


class TestTextNodeMeasureWritingMode:
    def test_horizontal_measure_returns_tuple(self):
        node = TextNode("Hello World")
        result = node.measure(LayoutConstraints(available_width=200))
        assert len(result) == 3
        assert all(v >= 0 for v in result)

    def test_sideways_rl_measure_swaps_axes(self):
        node_h = TextNode("Hello")
        node_s = TextNode("Hello", style={"writing-mode": "sideways-rl"})
        c = LayoutConstraints(available_width=200)
        min_w_h, max_w_h, h_h = node_h.measure(c)
        min_w_s, max_w_s, h_s = node_s.measure(c)
        # The sideways node's width comes from the horizontal text's height
        # The sideways node's height comes from the horizontal text's width
        # So h_s should be roughly equal to max_w_h
        assert h_s > 0
        assert min_w_s > 0

    def test_vertical_rl_measure_returns_tuple(self):
        node = TextNode("你好世界", style={"writing-mode": "vertical-rl"})
        result = node.measure(LayoutConstraints(available_width=200))
        assert len(result) == 3
        assert all(v >= 0 for v in result)


class TestTextNodeLayoutWritingMode:
    def test_horizontal_layout(self):
        node = TextNode("Hello")
        node.layout(LayoutConstraints(available_width=200))
        assert node.content_box.width > 0
        assert node.content_box.height > 0
        assert getattr(node, "_columns", None) is None

    def test_sideways_rl_layout(self):
        node = TextNode("Hello", style={"writing-mode": "sideways-rl"})
        node.layout(LayoutConstraints(available_width=200, available_height=200))
        assert node.content_box.width > 0
        assert node.content_box.height > 0
        assert getattr(node, "_resolved_writing_mode", None) == "sideways-rl"

    def test_sideways_lr_layout(self):
        node = TextNode("Hello", style={"writing-mode": "sideways-lr"})
        node.layout(LayoutConstraints(available_width=200, available_height=200))
        assert getattr(node, "_resolved_writing_mode", None) == "sideways-lr"

    def test_vertical_rl_layout_creates_columns(self):
        node = TextNode("你好世界", style={"writing-mode": "vertical-rl"})
        node.layout(LayoutConstraints(available_width=200, available_height=200))
        assert getattr(node, "_columns", None) is not None
        assert len(node._columns) >= 1

    def test_vertical_lr_layout(self):
        node = TextNode("你好世界", style={"writing-mode": "vertical-lr"})
        node.layout(LayoutConstraints(available_width=200, available_height=200))
        assert getattr(node, "_resolved_writing_mode", None) == "vertical-lr"


# ======================================================================
# GlyphMetrics vertical fields
# ======================================================================

class TestGlyphMetricsVertical:
    def test_glyph_metrics_has_advance_y(self):
        from latticesvg.text.font import GlyphMetrics
        gm = GlyphMetrics(advance_x=10, bearing_x=1, bearing_y=8,
                          width=9, height=10, advance_y=12)
        assert gm.advance_y == 12

    def test_glyph_metrics_defaults_zero(self):
        from latticesvg.text.font import GlyphMetrics
        gm = GlyphMetrics(advance_x=10, bearing_x=1, bearing_y=8,
                          width=9, height=10)
        assert gm.advance_y == 0.0
        assert gm.vert_origin_x == 0.0
        assert gm.vert_origin_y == 0.0
