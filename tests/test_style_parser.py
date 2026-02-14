"""Tests for the CSS value parser."""

import pytest
from latticesvg.style.parser import (
    AUTO,
    AreaMapping,
    FrValue,
    MIN_CONTENT,
    MAX_CONTENT,
    _Percentage,
    expand_shorthand,
    parse_grid_template_areas,
    parse_track_template,
    parse_value,
)


# ------------------------------------------------------------------
# Unit parsing
# ------------------------------------------------------------------

class TestParseValue:
    def test_px_explicit(self):
        assert parse_value("200px") == 200.0

    def test_px_implicit(self):
        assert parse_value("42") == 42.0

    def test_numeric_passthrough_int(self):
        assert parse_value(100) == 100.0

    def test_numeric_passthrough_float(self):
        assert parse_value(3.14) == 3.14

    def test_percent_with_reference(self):
        assert parse_value("50%", reference_length=400.0) == 200.0

    def test_percent_deferred(self):
        result = parse_value("50%")
        assert isinstance(result, _Percentage)
        assert result.resolve(400.0) == 200.0

    def test_em_unit(self):
        assert parse_value("2em", font_size=16.0) == 32.0

    def test_em_default_font_size(self):
        assert parse_value("1.5em") == 24.0  # 1.5 * 16 default

    def test_fr_unit(self):
        result = parse_value("1fr")
        assert isinstance(result, FrValue)
        assert result.value == 1.0

    def test_fr_fractional(self):
        result = parse_value("2.5fr")
        assert isinstance(result, FrValue)
        assert result.value == 2.5

    def test_pt_unit(self):
        result = parse_value("12pt")
        assert result == pytest.approx(16.0)

    def test_auto_keyword(self):
        assert parse_value("auto") is AUTO

    def test_min_content(self):
        assert parse_value("min-content") is MIN_CONTENT

    def test_max_content(self):
        assert parse_value("max-content") is MAX_CONTENT

    def test_keywords(self):
        assert parse_value("center") == "center"
        assert parse_value("hidden") == "hidden"
        assert parse_value("bold") == "bold"
        assert parse_value("nowrap") == "nowrap"
        assert parse_value("row dense") == "row dense"

    def test_list_passthrough(self):
        result = parse_value(["200px", "1fr"])
        assert result[0] == 200.0
        assert isinstance(result[1], FrValue)


# ------------------------------------------------------------------
# Color parsing
# ------------------------------------------------------------------

class TestColorParsing:
    def test_hex_6(self):
        assert parse_value("#ff0000") == "#ff0000"

    def test_hex_3(self):
        assert parse_value("#f00") == "#ff0000"

    def test_named_color(self):
        assert parse_value("red") == "#ff0000"
        assert parse_value("white") == "#ffffff"

    def test_rgb_function(self):
        assert parse_value("rgb(255, 0, 0)") == "#ff0000"

    def test_rgba_function(self):
        assert parse_value("rgba(255, 0, 0, 0.5)") == "rgba(255,0,0,0.5)"


# ------------------------------------------------------------------
# Shorthand expansion
# ------------------------------------------------------------------

class TestExpandShorthand:
    def test_margin_single(self):
        result = expand_shorthand("margin", "10px")
        assert result == {
            "margin-top": "10px",
            "margin-right": "10px",
            "margin-bottom": "10px",
            "margin-left": "10px",
        }

    def test_margin_two(self):
        result = expand_shorthand("margin", "10px 20px")
        assert result["margin-top"] == "10px"
        assert result["margin-right"] == "20px"
        assert result["margin-bottom"] == "10px"
        assert result["margin-left"] == "20px"

    def test_margin_four(self):
        result = expand_shorthand("margin", "1px 2px 3px 4px")
        assert result["margin-top"] == "1px"
        assert result["margin-right"] == "2px"
        assert result["margin-bottom"] == "3px"
        assert result["margin-left"] == "4px"

    def test_padding_shorthand(self):
        result = expand_shorthand("padding", "5px")
        assert result["padding-top"] == "5px"

    def test_gap_single(self):
        result = expand_shorthand("gap", "10px")
        assert result == {"row-gap": "10px", "column-gap": "10px"}

    def test_gap_two(self):
        result = expand_shorthand("gap", "10px 20px")
        assert result == {"row-gap": "10px", "column-gap": "20px"}

    def test_non_shorthand(self):
        result = expand_shorthand("width", "200px")
        assert result == {"width": "200px"}


# ------------------------------------------------------------------
# Track template parsing
# ------------------------------------------------------------------

class TestTrackTemplate:
    def test_list_input(self):
        result = parse_track_template(["200px", "1fr"])
        assert result[0] == 200.0
        assert isinstance(result[1], FrValue)

    def test_string_input(self):
        result = parse_track_template("200px 1fr auto")
        assert result[0] == 200.0
        assert isinstance(result[1], FrValue)
        assert result[2] is AUTO

    def test_single_value(self):
        result = parse_track_template("300px")
        assert result == [300.0]


# ------------------------------------------------------------------
# grid-template-areas parsing
# ------------------------------------------------------------------

class TestGridTemplateAreas:
    def test_simple_three_by_three(self):
        result = parse_grid_template_areas(
            '"header header header" "sidebar main main" "footer footer footer"'
        )
        assert isinstance(result, AreaMapping)
        assert result.num_rows == 3
        assert result.num_cols == 3
        assert result.areas["header"] == (0, 0, 1, 3)
        assert result.areas["sidebar"] == (1, 0, 1, 1)
        assert result.areas["main"] == (1, 1, 1, 2)
        assert result.areas["footer"] == (2, 0, 1, 3)

    def test_two_by_two_with_span(self):
        result = parse_grid_template_areas(
            '"a a" "b c"'
        )
        assert result.num_rows == 2
        assert result.num_cols == 2
        assert result.areas["a"] == (0, 0, 1, 2)
        assert result.areas["b"] == (1, 0, 1, 1)
        assert result.areas["c"] == (1, 1, 1, 1)

    def test_dot_empty_cell(self):
        result = parse_grid_template_areas(
            '"header header" ". main"'
        )
        assert result.num_rows == 2
        assert result.num_cols == 2
        assert "." not in result.areas
        assert result.areas["header"] == (0, 0, 1, 2)
        assert result.areas["main"] == (1, 1, 1, 1)

    def test_list_input(self):
        result = parse_grid_template_areas(
            ["header header", "sidebar main"]
        )
        assert result.num_rows == 2
        assert result.num_cols == 2
        assert result.areas["header"] == (0, 0, 1, 2)

    def test_row_spanning_area(self):
        result = parse_grid_template_areas(
            '"sidebar main" "sidebar footer"'
        )
        assert result.areas["sidebar"] == (0, 0, 2, 1)
        assert result.areas["main"] == (0, 1, 1, 1)
        assert result.areas["footer"] == (1, 1, 1, 1)

    def test_none_returns_none(self):
        assert parse_grid_template_areas(None) is None
        assert parse_grid_template_areas("none") is None

    def test_non_rectangular_raises(self):
        with pytest.raises(ValueError, match="not rectangular"):
            parse_grid_template_areas('"a b" "b a"')

    def test_inconsistent_columns_raises(self):
        with pytest.raises(ValueError, match="columns"):
            parse_grid_template_areas('"a b" "c d e"')