"""Tests for individual node types — measure() and layout()."""

import pytest
from latticesvg.nodes.base import LayoutConstraints
from latticesvg.nodes.text import TextNode
from latticesvg.nodes.image import ImageNode
from latticesvg.nodes.svg import SVGNode


# ------------------------------------------------------------------
# SVGNode
# ------------------------------------------------------------------

class TestSVGNode:
    def test_parse_viewbox(self):
        svg = '<svg viewBox="0 0 100 50" xmlns="http://www.w3.org/2000/svg"></svg>'
        node = SVGNode(svg)
        assert node.intrinsic_width == 100.0
        assert node.intrinsic_height == 50.0

    def test_parse_width_height(self):
        svg = '<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg"></svg>'
        node = SVGNode(svg)
        assert node.intrinsic_width == 200.0
        assert node.intrinsic_height == 150.0

    def test_measure(self):
        svg = '<svg viewBox="0 0 100 80" xmlns="http://www.w3.org/2000/svg"></svg>'
        node = SVGNode(svg)
        min_w, max_w, h = node.measure(LayoutConstraints())
        assert min_w == pytest.approx(100.0)
        assert h == pytest.approx(80.0)

    def test_layout_scales(self):
        svg = '<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg"></svg>'
        node = SVGNode(svg)
        node.layout(LayoutConstraints(available_width=100))
        # Should scale to 100x50 (maintain aspect ratio)
        assert node.content_box.width == pytest.approx(100.0)
        assert node.content_box.height == pytest.approx(50.0)


# ------------------------------------------------------------------
# ImageNode
# ------------------------------------------------------------------

class TestImageNode:
    def test_object_fit_contain(self):
        node = ImageNode("test.png", object_fit="contain")
        node._intrinsic_width = 200.0
        node._intrinsic_height = 100.0
        node.layout(LayoutConstraints(available_width=100))

        ir = node.image_rect
        # With contain, 200x100 scaled into 100x50, maintaining ratio
        assert ir.width == pytest.approx(100.0)
        assert ir.height == pytest.approx(50.0)

    def test_object_fit_fill(self):
        node = ImageNode("test.png", object_fit="fill")
        node._intrinsic_width = 200.0
        node._intrinsic_height = 100.0
        node.layout(LayoutConstraints(available_width=300))

        ir = node.image_rect
        # Fill stretches to box
        assert ir.width == pytest.approx(node.content_box.width)
        assert ir.height == pytest.approx(node.content_box.height)

    def test_measure(self):
        node = ImageNode("test.png")
        node._intrinsic_width = 400.0
        node._intrinsic_height = 300.0
        min_w, max_w, h = node.measure(LayoutConstraints())
        assert min_w == pytest.approx(400.0)
        assert h == pytest.approx(300.0)
