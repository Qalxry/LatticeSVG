"""End-to-end integration tests."""

import pytest
from latticesvg import GridContainer, TextNode, ImageNode, SVGNode, Renderer
from latticesvg.nodes.base import Node, LayoutConstraints


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

class DummyNode(Node):
    """A simple box with fixed dimensions."""

    def __init__(self, w=100, h=50, **style_kw):
        super().__init__(style=style_kw)
        self._w = w
        self._h = h

    def measure(self, c):
        return (self._w, self._w, self._h)

    def layout(self, c):
        self._resolve_box_model(self._w, self._h)


# ------------------------------------------------------------------
# Integration tests
# ------------------------------------------------------------------

class TestBasicGridLayout:
    """Build a simple grid, layout, and render to SVG string."""

    def test_two_column_layout(self):
        grid = GridContainer(style={
            "width": "600px",
            "padding": "10px",
            "grid-template-columns": ["200px", "1fr"],
            "gap": "10px",
        })

        left = DummyNode(w=200, h=80)
        right = DummyNode(w=100, h=60)
        grid.add(left, row=1, col=1)
        grid.add(right, row=1, col=2)

        grid.layout(available_width=600)

        # Verify layout results
        assert left.border_box.width == pytest.approx(200.0)
        # Right column: 600 - 20(padding) - 200(col1) - 10(gap) = 370
        assert right.border_box.width == pytest.approx(370.0)

        # Render
        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "<svg" in svg

    def test_nested_grid(self):
        outer = GridContainer(style={
            "width": "800px",
            "grid-template-columns": ["1fr", "1fr"],
            "gap": "20px",
        })

        inner = GridContainer(style={
            "grid-template-columns": ["1fr", "1fr"],
            "gap": "5px",
        })
        inner.add(DummyNode(w=50, h=30), row=1, col=1)
        inner.add(DummyNode(w=50, h=30), row=1, col=2)

        outer.add(DummyNode(w=100, h=50), row=1, col=1)
        outer.add(inner, row=1, col=2)

        outer.layout(available_width=800)

        # Both top-level columns should get ~390px each
        assert outer.children[0].border_box.width == pytest.approx(390.0)
        assert inner.border_box.width == pytest.approx(390.0)

        # Inner grid should also have laid out its children
        assert inner.children[0].border_box.width > 0
        assert inner.children[1].border_box.width > 0

    def test_auto_placement_multiple_rows(self):
        grid = GridContainer(style={
            "width": "300px",
            "grid-template-columns": ["100px", "100px", "100px"],
        })
        nodes = [DummyNode(w=80, h=40) for _ in range(6)]
        for n in nodes:
            grid.add(n)

        grid.layout(available_width=300)

        # Should form a 2x3 grid
        # Row 0
        assert nodes[0].border_box.y == nodes[1].border_box.y
        assert nodes[1].border_box.y == nodes[2].border_box.y
        # Row 1
        assert nodes[3].border_box.y == nodes[4].border_box.y
        assert nodes[4].border_box.y == nodes[5].border_box.y
        # Row 1 is below row 0
        assert nodes[3].border_box.y > nodes[0].border_box.y


class TestSVGNodeIntegration:
    def test_embed_svg_in_grid(self):
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
        })
        svg_node = SVGNode(svg_content)
        grid.add(svg_node, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "circle" in svg


class TestRendererOutput:
    def test_svg_has_correct_root(self):
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["1fr"],
            "background-color": "#fff",
        })
        grid.add(DummyNode(w=400, h=100), row=1, col=1)
        grid.layout(available_width=400)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)

        assert svg.strip().startswith("<")
        assert "svg" in svg[:100].lower()
