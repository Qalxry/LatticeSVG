"""Tests for the build_table helper in templates.py."""

import pytest
from latticesvg import GridContainer, Renderer, build_table
from latticesvg.nodes.text import TextNode
from latticesvg.templates import (
    TABLE_CELL_DEFAULT,
    TABLE_DEFAULT,
    TABLE_HEADER_DEFAULT,
    build_table,
)


# ------------------------------------------------------------------
# Structure tests
# ------------------------------------------------------------------

class TestBuildTableStructure:
    def test_returns_grid_container(self):
        tbl = build_table(headers=["A", "B"], rows=[["1", "2"]])
        assert isinstance(tbl, GridContainer)

    def test_correct_child_count(self):
        """2 headers + 2×3 data cells = 8 children."""
        tbl = build_table(
            headers=["A", "B"],
            rows=[["1", "2"], ["3", "4"], ["5", "6"]],
        )
        assert len(tbl.children) == 8

    def test_header_cells_are_grid_containers(self):
        tbl = build_table(headers=["X", "Y"], rows=[["a", "b"]])
        # First two children are header cells
        for child in tbl.children[:2]:
            assert isinstance(child, GridContainer)

    def test_header_text_content(self):
        tbl = build_table(headers=["Name", "Score"], rows=[])
        # Each header cell is a GridContainer wrapping a TextNode
        for i, label in enumerate(["Name", "Score"]):
            cell = tbl.children[i]
            assert len(cell.children) == 1
            text_node = cell.children[0]
            assert isinstance(text_node, TextNode)
            assert text_node.text == label

    def test_data_cell_values_are_stringified(self):
        tbl = build_table(
            headers=["K", "V"],
            rows=[[42, 3.14]],
        )
        # Data cells are children[2] and children[3]
        for idx, expected in [(2, "42"), (3, "3.14")]:
            cell = tbl.children[idx]
            text_node = cell.children[0]
            assert text_node.text == expected

    def test_missing_columns_become_empty_string(self):
        """If a row has fewer values than headers, missing cells are empty."""
        tbl = build_table(
            headers=["A", "B", "C"],
            rows=[["only_one"]],
        )
        # children: 3 headers + 3 data cells = 6
        assert len(tbl.children) == 6
        # Data cells: indices 3, 4, 5
        assert tbl.children[3].children[0].text == "only_one"
        assert tbl.children[4].children[0].text == ""
        assert tbl.children[5].children[0].text == ""


# ------------------------------------------------------------------
# Style tests
# ------------------------------------------------------------------

class TestBuildTableStyles:
    def test_default_col_widths(self):
        """Without explicit col_widths, all columns use 1fr."""
        tbl = build_table(headers=["A", "B", "C"], rows=[])
        cols = tbl.style.get("grid-template-columns")
        # Should be three FrValue(1.0) elements
        assert len(cols) == 3

    def test_custom_col_widths(self):
        tbl = build_table(
            headers=["A", "B"],
            rows=[],
            col_widths=["200px", "1fr"],
        )
        cols = tbl.style.get("grid-template-columns")
        assert cols[0] == pytest.approx(200.0)

    def test_stripe_color_applied_to_even_rows(self):
        """Even data rows (0-indexed: 1, 3, …) get stripe background."""
        tbl = build_table(
            headers=["H"],
            rows=[["r0"], ["r1"], ["r2"], ["r3"]],
            stripe_color="#eeeeee",
        )
        # Children: 1 header + 4 data cells = 5
        # Data cells indices: 1 (row0), 2 (row1-even), 3 (row2), 4 (row3-even)
        r1_cell = tbl.children[2]  # row1 — even
        r0_cell = tbl.children[1]  # row0 — odd
        assert r1_cell.style.get("background-color") == "#eeeeee"
        # Row 0 should NOT have stripe
        assert r0_cell.style.get("background-color") != "#eeeeee"

    def test_stripe_disabled(self):
        tbl = build_table(
            headers=["H"],
            rows=[["r0"], ["r1"]],
            stripe_color=None,
        )
        # No cell should have the default stripe color
        for child in tbl.children[1:]:
            bg = child.style.get("background-color")
            assert bg != "#f8f9fa" or bg is None

    def test_custom_header_style(self):
        tbl = build_table(
            headers=["A"],
            rows=[],
            header_style={"background-color": "#ff0000", "font-size": "20px"},
        )
        h_cell = tbl.children[0]
        assert h_cell.style.get("background-color") == "#ff0000"

    def test_custom_cell_style(self):
        tbl = build_table(
            headers=["A"],
            rows=[["x"]],
            cell_style={"color": "#ff0000"},
        )
        d_cell = tbl.children[1]
        text_node = d_cell.children[0]
        assert text_node.style.get("color") == "#ff0000"

    def test_custom_table_style_width(self):
        tbl = build_table(
            headers=["A"],
            rows=[],
            style={"width": "500px"},
        )
        assert tbl.style.get("width") == pytest.approx(500.0)


# ------------------------------------------------------------------
# Layout & render integration
# ------------------------------------------------------------------

class TestBuildTableRender:
    def test_layout_and_render(self):
        tbl = build_table(
            headers=["Name", "Value", "Unit"],
            rows=[
                ["alpha", "1.0", "m/s"],
                ["beta", "2.5", "kg"],
            ],
            style={"width": "500px"},
        )
        tbl.layout(available_width=500)
        renderer = Renderer()
        svg = renderer.render_to_string(tbl)
        assert "<svg" in svg
        assert "alpha" in svg
        assert "beta" in svg

    def test_empty_rows(self):
        """Table with only headers, no data rows."""
        tbl = build_table(
            headers=["A", "B"],
            rows=[],
            style={"width": "300px"},
        )
        tbl.layout(available_width=300)
        svg = Renderer().render_to_string(tbl)
        assert "<svg" in svg
