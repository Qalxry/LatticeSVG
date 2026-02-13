"""Tests for the SVG renderer."""

import pytest
import xml.etree.ElementTree as ET

from latticesvg.nodes.grid import GridContainer
from latticesvg.nodes.text import TextNode
from latticesvg.nodes.base import LayoutConstraints, Node
from latticesvg.render.renderer import Renderer


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

class BoxNode(Node):
    """Minimal node with explicit size for renderer testing."""

    def __init__(self, width=100, height=50, **style):
        super().__init__(style=style)
        self._w = width
        self._h = height

    def measure(self, c):
        ph = self.style.padding_horizontal + self.style.border_horizontal
        pv = self.style.padding_vertical + self.style.border_vertical
        return (self._w + ph, self._w + ph, self._h + pv)

    def layout(self, c):
        self._resolve_box_model(self._w, self._h)


def _parse_svg(svg_string: str) -> ET.Element:
    """Parse an SVG string, stripping namespaces for easier querying."""
    # Remove default namespace to simplify XPath
    svg_string = svg_string.replace('xmlns="http://www.w3.org/2000/svg"', '')
    svg_string = svg_string.replace("xmlns:xlink='http://www.w3.org/1999/xlink'", '')
    return ET.fromstring(svg_string)


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

class TestRendererBasic:
    def test_renders_svg_string(self):
        grid = GridContainer(style={
            "width": "300px",
            "grid-template-columns": ["300px"],
            "background-color": "#ffffff",
        })
        box = BoxNode(width=300, height=50)
        grid.add(box, row=1, col=1)
        grid.layout(available_width=300)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)

        assert "<svg" in svg
        assert "</svg>" in svg

    def test_background_color_rendered(self):
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)

        # The red background should appear as a fill
        assert "#ff0000" in svg

    def test_border_rendered(self):
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "border-width": "2px",
            "border-color": "#0000ff",
        })
        # Need to set border-*-color individually since shorthand
        # expansion in computed style handles it
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        # Should contain border color somewhere
        assert "0000ff" in svg.lower() or "line" in svg.lower()

    def test_drawing_dimensions(self):
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["1fr"],
        })
        box = BoxNode(width=400, height=80)
        grid.add(box, row=1, col=1)
        grid.layout(available_width=400)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        root = _parse_svg(svg)

        width = float(root.attrib.get("width", 0))
        assert width == pytest.approx(400.0)
