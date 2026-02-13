"""Tests for the Grid layout solver."""

import pytest
from latticesvg.nodes.base import LayoutConstraints, Node, Rect
from latticesvg.nodes.grid import GridContainer
from latticesvg.style.parser import FrValue


# ------------------------------------------------------------------
# Helpers — simple mock content node with known intrinsic sizes
# ------------------------------------------------------------------

class MockNode(Node):
    """A node with controllable intrinsic sizes for testing."""

    def __init__(self, min_w=50, max_w=100, height=30, **kwargs):
        super().__init__(**kwargs)
        self._min_w = min_w
        self._max_w = max_w
        self._height = height

    def measure(self, constraints):
        return (self._min_w, self._max_w, self._height)

    def layout(self, constraints):
        w = constraints.available_width or self._max_w
        self._resolve_box_model(w, self._height)


# ------------------------------------------------------------------
# Test cases
# ------------------------------------------------------------------

class TestFixedTracks:
    def test_two_fixed_columns(self):
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["150px", "200px"],
        })
        a = MockNode()
        b = MockNode()
        grid.add(a, row=1, col=1)
        grid.add(b, row=1, col=2)
        grid.layout(available_width=400)

        # Check that the children were positioned
        assert a.border_box.width == pytest.approx(150.0)
        assert b.border_box.width == pytest.approx(200.0)
        assert b.border_box.x > a.border_box.x

    def test_fixed_with_gap(self):
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["100px", "100px"],
            "gap": "20px",
        })
        a = MockNode()
        b = MockNode()
        grid.add(a, row=1, col=1)
        grid.add(b, row=1, col=2)
        grid.layout(available_width=400)

        gap_between = b.border_box.x - (a.border_box.x + a.border_box.width)
        assert gap_between == pytest.approx(20.0)


class TestFrTracks:
    def test_single_fr(self):
        grid = GridContainer(style={
            "width": "300px",
            "grid-template-columns": ["1fr"],
        })
        a = MockNode()
        grid.add(a, row=1, col=1)
        grid.layout(available_width=300)

        assert a.border_box.width == pytest.approx(300.0)

    def test_two_equal_fr(self):
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["1fr", "1fr"],
        })
        a = MockNode()
        b = MockNode()
        grid.add(a, row=1, col=1)
        grid.add(b, row=1, col=2)
        grid.layout(available_width=400)

        assert a.border_box.width == pytest.approx(200.0)
        assert b.border_box.width == pytest.approx(200.0)

    def test_mixed_fixed_and_fr(self):
        grid = GridContainer(style={
            "width": "500px",
            "grid-template-columns": ["200px", "1fr"],
        })
        a = MockNode()
        b = MockNode()
        grid.add(a, row=1, col=1)
        grid.add(b, row=1, col=2)
        grid.layout(available_width=500)

        assert a.border_box.width == pytest.approx(200.0)
        assert b.border_box.width == pytest.approx(300.0)

    def test_fr_with_gap(self):
        grid = GridContainer(style={
            "width": "420px",
            "grid-template-columns": ["1fr", "1fr"],
            "gap": "20px",
        })
        a = MockNode()
        b = MockNode()
        grid.add(a, row=1, col=1)
        grid.add(b, row=1, col=2)
        grid.layout(available_width=420)

        # Each fr = (420 - 20) / 2 = 200
        assert a.border_box.width == pytest.approx(200.0)
        assert b.border_box.width == pytest.approx(200.0)


class TestAutoPlacement:
    def test_auto_flow_row(self):
        grid = GridContainer(style={
            "width": "300px",
            "grid-template-columns": ["100px", "100px", "100px"],
        })
        items = [MockNode() for _ in range(5)]
        for item in items:
            grid.add(item)

        grid.layout(available_width=300)

        # Should fill row by row: 3 in row 0, 2 in row 1
        assert items[0].border_box.x < items[1].border_box.x < items[2].border_box.x
        assert items[3].border_box.y > items[0].border_box.y

    def test_explicit_placement(self):
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["200px", "200px"],
        })
        a = MockNode()
        b = MockNode()
        grid.add(a, row=1, col=2)  # Place in second column
        grid.add(b, row=1, col=1)  # Place in first column

        grid.layout(available_width=400)

        # b should be to the left of a
        assert b.border_box.x < a.border_box.x


class TestSpanningItems:
    def test_col_span_2(self):
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["200px", "200px"],
        })
        a = MockNode()
        grid.add(a, row=1, col=1, col_span=2)
        grid.layout(available_width=400)

        assert a.border_box.width == pytest.approx(400.0)


class TestAlignment:
    def test_justify_self_center(self):
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["400px"],
        })
        a = MockNode(max_w=100)
        a.style.set("justify-self", "center")
        grid.add(a, row=1, col=1)
        grid.layout(available_width=400)

        # The item should be centered horizontally
        # Cell is 400px wide, item is 100px
        expected_x = grid.content_box.x + (400 - 100) / 2
        assert a.border_box.x == pytest.approx(expected_x, abs=1)

    def test_align_self_end(self):
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "grid-template-rows": ["100px"],
        })
        a = MockNode(height=30)
        a.style.set("align-self", "end")
        grid.add(a, row=1, col=1)
        grid.layout(available_width=200)

        # Item should be at bottom of 100px cell
        cell_bottom = grid.content_box.y + 100
        assert a.border_box.y + a.border_box.height == pytest.approx(cell_bottom, abs=1)


class TestPaddingAndBorder:
    def test_container_padding(self):
        grid = GridContainer(style={
            "width": "400px",
            "padding": "20px",
            "grid-template-columns": ["1fr"],
        })
        a = MockNode()
        grid.add(a, row=1, col=1)
        grid.layout(available_width=400)

        # Content area = 400 - 40 = 360
        assert a.border_box.width == pytest.approx(360.0)
        assert a.border_box.x == pytest.approx(20.0)
