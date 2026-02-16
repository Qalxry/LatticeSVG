"""Tests for ComputedStyle."""

import pytest
from latticesvg.style.computed import ComputedStyle
from latticesvg.style.parser import AUTO


class TestComputedStyleCreation:
    def test_default_values(self):
        s = ComputedStyle()
        assert s.get("font-size") == 16.0
        assert s.get("color") == "#000000"
        assert s.get("display") == "block"

    def test_explicit_width(self):
        s = ComputedStyle({"width": "200px"})
        assert s.get("width") == 200.0

    def test_padding_shorthand(self):
        s = ComputedStyle({"padding": "10px"})
        assert s.padding_top == 10.0
        assert s.padding_right == 10.0
        assert s.padding_bottom == 10.0
        assert s.padding_left == 10.0

    def test_gap_shorthand(self):
        s = ComputedStyle({"gap": "15px"})
        assert s.get("row-gap") == 15.0
        assert s.get("column-gap") == 15.0


class TestComputedStyleInheritance:
    def test_font_size_inherited(self):
        parent = ComputedStyle({"font-size": "24px"})
        child = ComputedStyle(None, parent_style=parent)
        assert child.get("font-size") == 24.0

    def test_color_inherited(self):
        parent = ComputedStyle({"color": "#ff0000"})
        child = ComputedStyle(None, parent_style=parent)
        assert child.get("color") == "#ff0000"

    def test_width_not_inherited(self):
        parent = ComputedStyle({"width": "500px"})
        child = ComputedStyle(None, parent_style=parent)
        assert child.get("width") is AUTO  # default is auto

    def test_child_overrides_parent(self):
        parent = ComputedStyle({"font-size": "24px"})
        child = ComputedStyle({"font-size": "12px"}, parent_style=parent)
        assert child.get("font-size") == 12.0


class TestComputedStyleAccess:
    def test_getattr_underscore_to_hyphen(self):
        s = ComputedStyle({"font-size": "20px"})
        assert s.font_size == 20.0

    def test_getattr_missing(self):
        s = ComputedStyle()
        with pytest.raises(AttributeError):
            _ = s.nonexistent_property

    def test_padding_horizontal(self):
        s = ComputedStyle({"padding": "10px 20px"})
        assert s.padding_horizontal == 40.0  # 20 + 20

    def test_padding_vertical(self):
        s = ComputedStyle({"padding": "10px 20px"})
        assert s.padding_vertical == 20.0  # 10 + 10

    def test_border_horizontal(self):
        s = ComputedStyle({"border-width": "2px"})
        assert s.border_horizontal == 4.0

    def test_set_and_get(self):
        s = ComputedStyle()
        s.set("width", 300.0)
        assert s.get("width") == 300.0
