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


# ------------------------------------------------------------------
# min-width / max-width / min-height / max-height
# ------------------------------------------------------------------

class TestMinMaxSize:
    def test_max_width_clamps_child(self):
        """A child with max-width should not exceed it."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["400px"],
        })
        # Node wants 400px wide but max-width says 200
        a = MockNode(min_w=50, max_w=400, height=30,
                     style={"max-width": "200px"})
        grid.add(a, row=1, col=1)
        grid.layout(available_width=400)

        assert a.border_box.width == pytest.approx(200.0)

    def test_min_width_expands_child(self):
        """A child with min-width should not shrink below it."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["100px"],
        })
        # Node allocated 100px but min-width says 150
        a = MockNode(min_w=50, max_w=100, height=30,
                     style={"min-width": "150px", "justify-self": "start"})
        grid.add(a, row=1, col=1)
        grid.layout(available_width=400)

        assert a.border_box.width == pytest.approx(150.0)

    def test_max_height_clamps_child(self):
        """A child with max-height should not exceed it."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["400px"],
            "grid-template-rows": ["200px"],
        })
        a = MockNode(height=200, style={"max-height": "80px"})
        grid.add(a, row=1, col=1)
        grid.layout(available_width=400)

        assert a.border_box.height == pytest.approx(80.0)

    def test_min_height_expands_child(self):
        """A child with min-height should not shrink below it."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["400px"],
        })
        a = MockNode(height=20, style={"min-height": "60px", "align-self": "start"})
        grid.add(a, row=1, col=1)
        grid.layout(available_width=400)

        assert a.border_box.height == pytest.approx(60.0)

    def test_no_constraints_leaves_size_unchanged(self):
        """Without min/max, normal sizing should be unaffected."""
        grid = GridContainer(style={
            "width": "300px",
            "grid-template-columns": ["300px"],
        })
        a = MockNode(height=50)
        grid.add(a, row=1, col=1)
        grid.layout(available_width=300)

        assert a.border_box.width == pytest.approx(300.0)
        assert a.border_box.height == pytest.approx(50.0)


# ------------------------------------------------------------------
# grid-template-areas placement
# ------------------------------------------------------------------

class TestGridTemplateAreas:
    def test_area_placement_via_add_kwarg(self):
        """Children placed via area= kwarg get positioned correctly."""
        grid = GridContainer(style={
            "width": "600px",
            "grid-template-columns": ["200px", "200px", "200px"],
            "grid-template-rows": ["50px", "100px", "40px"],
            "grid-template-areas": '"header header header" "sidebar main main" "footer footer footer"',
        })
        header = MockNode(height=50)
        sidebar = MockNode(height=100)
        main = MockNode(height=100)
        footer = MockNode(height=40)
        grid.add(header, area="header")
        grid.add(sidebar, area="sidebar")
        grid.add(main, area="main")
        grid.add(footer, area="footer")
        grid.layout(available_width=600)

        # header spans all 3 columns
        assert header.border_box.width == pytest.approx(600.0)
        assert header.border_box.x == pytest.approx(0.0)
        assert header.border_box.y == pytest.approx(0.0)

        # sidebar is column 1 only, row 2
        assert sidebar.border_box.width == pytest.approx(200.0)
        assert sidebar.border_box.x == pytest.approx(0.0)
        assert sidebar.border_box.y == pytest.approx(50.0)

        # main spans columns 2-3, row 2
        assert main.border_box.width == pytest.approx(400.0)
        assert main.border_box.x == pytest.approx(200.0)
        assert main.border_box.y == pytest.approx(50.0)

        # footer spans all 3 columns, row 3
        assert footer.border_box.width == pytest.approx(600.0)
        assert footer.border_box.y == pytest.approx(150.0)

    def test_area_placement_via_grid_area_style(self):
        """Children placed via grid-area CSS property."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["200px", "200px"],
            "grid-template-areas": '"a a" "b c"',
        })
        node_a = MockNode(height=30)
        node_b = MockNode(height=50)
        node_c = MockNode(height=50)
        grid.add(node_a, area="a")
        grid.add(node_b, area="b")
        grid.add(node_c, area="c")
        grid.layout(available_width=400)

        assert node_a.border_box.width == pytest.approx(400.0)
        assert node_b.border_box.width == pytest.approx(200.0)
        assert node_c.border_box.x == pytest.approx(200.0)

    def test_area_with_empty_cells(self):
        """Dot cells don't create named areas but affect grid structure."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["200px", "200px"],
            "grid-template-areas": '"header header" ". content"',
        })
        h = MockNode(height=30)
        c = MockNode(height=50)
        grid.add(h, area="header")
        grid.add(c, area="content")
        grid.layout(available_width=400)

        assert h.border_box.width == pytest.approx(400.0)
        assert c.border_box.x == pytest.approx(200.0)
        assert c.border_box.y == pytest.approx(30.0)

    def test_area_with_row_span(self):
        """Area spanning multiple rows."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["200px", "200px"],
            "grid-template-rows": ["50px", "50px"],
            "grid-template-areas": '"side main" "side footer"',
        })
        side = MockNode(height=100)
        main_node = MockNode(height=50)
        foot = MockNode(height=50)
        grid.add(side, area="side")
        grid.add(main_node, area="main")
        grid.add(foot, area="footer")
        grid.layout(available_width=400)

        # side spans 2 rows
        assert side.border_box.height == pytest.approx(100.0)
        assert side.border_box.x == pytest.approx(0.0)
        assert main_node.border_box.y == pytest.approx(0.0)
        assert foot.border_box.y == pytest.approx(50.0)

    def test_area_implicit_tracks(self):
        """Areas define implicit tracks when no explicit track defs given."""
        grid = GridContainer(style={
            "width": "600px",
            "grid-template-columns": ["1fr", "1fr", "1fr"],
            "grid-template-areas": '"a b c"',
        })
        a = MockNode(height=40)
        b = MockNode(height=40)
        c = MockNode(height=40)
        grid.add(a, area="a")
        grid.add(b, area="b")
        grid.add(c, area="c")
        grid.layout(available_width=600)

        # 3 equal fr columns should share 600px equally
        assert a.border_box.width == pytest.approx(200.0)
        assert b.border_box.width == pytest.approx(200.0)
        assert c.border_box.width == pytest.approx(200.0)

    def test_area_mixed_with_explicit_placement(self):
        """Mix of area placement and row/col placement."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["200px", "200px"],
            "grid-template-areas": '"header header" "left right"',
        })
        h = MockNode(height=30)
        left = MockNode(height=50)
        right = MockNode(height=50)
        grid.add(h, area="header")
        grid.add(left, row=2, col=1)  # explicit placement
        grid.add(right, area="right")
        grid.layout(available_width=400)

        assert h.border_box.width == pytest.approx(400.0)
        assert left.border_box.x == pytest.approx(0.0)
        assert left.border_box.y == pytest.approx(30.0)
        assert right.border_box.x == pytest.approx(200.0)