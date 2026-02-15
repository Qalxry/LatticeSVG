"""Tests for the CSS value parser."""

import pytest
from latticesvg.style.parser import (
    AUTO,
    AreaMapping,
    BoxShadow,
    FilterFunction,
    FrValue,
    MIN_CONTENT,
    MAX_CONTENT,
    MinMaxValue,
    GradientStop,
    LinearGradientValue,
    RadialGradientValue,
    TransformFunction,
    _Percentage,
    expand_shorthand,
    parse_box_shadow,
    parse_filter,
    parse_gradient,
    parse_grid_template_areas,
    parse_track_template,
    parse_transform,
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

    # --- repeat() ---

    def test_repeat_basic(self):
        result = parse_track_template("repeat(3, 1fr)")
        assert len(result) == 3
        assert all(isinstance(v, FrValue) and v.value == 1.0 for v in result)

    def test_repeat_multiple_values(self):
        result = parse_track_template("repeat(2, 100px 1fr)")
        assert len(result) == 4
        assert result[0] == 100.0
        assert isinstance(result[1], FrValue)
        assert result[2] == 100.0
        assert isinstance(result[3], FrValue)

    def test_repeat_mixed(self):
        result = parse_track_template("200px repeat(2, 1fr) 100px")
        assert len(result) == 4
        assert result[0] == 200.0
        assert isinstance(result[1], FrValue)
        assert isinstance(result[2], FrValue)
        assert result[3] == 100.0

    # --- minmax() ---

    def test_minmax_basic(self):
        result = parse_track_template("minmax(100px, 1fr)")
        assert len(result) == 1
        v = result[0]
        assert isinstance(v, MinMaxValue)
        assert v.min_val == 100.0
        assert isinstance(v.max_val, FrValue) and v.max_val.value == 1.0

    def test_minmax_fixed_range(self):
        result = parse_track_template("minmax(100px, 300px)")
        assert len(result) == 1
        v = result[0]
        assert isinstance(v, MinMaxValue)
        assert v.min_val == 100.0
        assert v.max_val == 300.0

    def test_minmax_auto_max(self):
        result = parse_track_template("minmax(100px, auto)")
        assert len(result) == 1
        v = result[0]
        assert isinstance(v, MinMaxValue)
        assert v.min_val == 100.0
        assert v.max_val is AUTO

    def test_repeat_with_minmax(self):
        result = parse_track_template("repeat(3, minmax(100px, 1fr))")
        assert len(result) == 3
        for v in result:
            assert isinstance(v, MinMaxValue)
            assert v.min_val == 100.0
            assert isinstance(v.max_val, FrValue)

    def test_mixed_with_functions(self):
        result = parse_track_template("200px repeat(2, 1fr) minmax(100px, auto)")
        assert len(result) == 4
        assert result[0] == 200.0
        assert isinstance(result[1], FrValue)
        assert isinstance(result[2], FrValue)
        assert isinstance(result[3], MinMaxValue)


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


# ------------------------------------------------------------------
# border-radius shorthand expansion (P2-1)
# ------------------------------------------------------------------

class TestBorderRadiusShorthand:
    """Expand ``border-radius`` into four corner longhands."""

    def test_single_value(self):
        result = expand_shorthand("border-radius", "10px")
        assert result == {
            "border-top-left-radius": "10px",
            "border-top-right-radius": "10px",
            "border-bottom-right-radius": "10px",
            "border-bottom-left-radius": "10px",
        }

    def test_two_values(self):
        result = expand_shorthand("border-radius", "10px 20px")
        assert result == {
            "border-top-left-radius": "10px",
            "border-top-right-radius": "20px",
            "border-bottom-right-radius": "10px",
            "border-bottom-left-radius": "20px",
        }

    def test_three_values(self):
        result = expand_shorthand("border-radius", "10px 20px 30px")
        assert result == {
            "border-top-left-radius": "10px",
            "border-top-right-radius": "20px",
            "border-bottom-right-radius": "30px",
            "border-bottom-left-radius": "20px",
        }

    def test_four_values(self):
        result = expand_shorthand("border-radius", "10px 20px 0 5px")
        assert result == {
            "border-top-left-radius": "10px",
            "border-top-right-radius": "20px",
            "border-bottom-right-radius": "0",
            "border-bottom-left-radius": "5px",
        }


# ------------------------------------------------------------------
# clip-path parsing (P2-2)
# ------------------------------------------------------------------

from latticesvg.style.parser import (
    parse_clip_path,
    ClipCircle,
    ClipEllipse,
    ClipPolygon,
    ClipInset,
)


class TestClipPathParsing:
    def test_none(self):
        assert parse_clip_path("none") == "none"
        assert parse_clip_path(None) == "none"

    def test_circle_defaults(self):
        result = parse_clip_path("circle(50%)")
        assert isinstance(result, ClipCircle)
        assert isinstance(result.radius, _Percentage)
        assert result.radius.value == 50

    def test_circle_at_position(self):
        result = parse_clip_path("circle(40px at 100px 80px)")
        assert isinstance(result, ClipCircle)
        assert result.radius == 40.0
        assert result.cx == 100.0
        assert result.cy == 80.0

    def test_circle_percent_position(self):
        result = parse_clip_path("circle(50% at 50% 50%)")
        assert isinstance(result, ClipCircle)
        assert isinstance(result.cx, _Percentage)
        assert result.cx.value == 50

    def test_ellipse(self):
        result = parse_clip_path("ellipse(50% 40% at 50% 50%)")
        assert isinstance(result, ClipEllipse)
        assert isinstance(result.rx, _Percentage)
        assert result.rx.value == 50
        assert isinstance(result.ry, _Percentage)
        assert result.ry.value == 40

    def test_ellipse_px(self):
        result = parse_clip_path("ellipse(100px 60px at 150px 100px)")
        assert isinstance(result, ClipEllipse)
        assert result.rx == 100.0
        assert result.ry == 60.0
        assert result.cx == 150.0
        assert result.cy == 100.0

    def test_polygon(self):
        result = parse_clip_path("polygon(0% 0%, 100% 0%, 50% 100%)")
        assert isinstance(result, ClipPolygon)
        assert len(result.points) == 3
        # First point
        assert isinstance(result.points[0][0], _Percentage)
        assert result.points[0][0].value == 0

    def test_polygon_px(self):
        result = parse_clip_path("polygon(0px 0px, 200px 0px, 100px 200px)")
        assert isinstance(result, ClipPolygon)
        assert len(result.points) == 3
        assert result.points[0] == (0.0, 0.0)
        assert result.points[1] == (200.0, 0.0)
        assert result.points[2] == (100.0, 200.0)

    def test_inset_single(self):
        result = parse_clip_path("inset(10px)")
        assert isinstance(result, ClipInset)
        assert result.top == 10.0
        assert result.right == 10.0
        assert result.bottom == 10.0
        assert result.left == 10.0
        assert result.round_radii is None

    def test_inset_four_values(self):
        result = parse_clip_path("inset(10px 20px 30px 40px)")
        assert isinstance(result, ClipInset)
        assert result.top == 10.0
        assert result.right == 20.0
        assert result.bottom == 30.0
        assert result.left == 40.0

    def test_inset_with_round(self):
        result = parse_clip_path("inset(10px round 5px)")
        assert isinstance(result, ClipInset)
        assert result.top == 10.0
        assert result.round_radii is not None
        assert result.round_radii == (5.0, 5.0, 5.0, 5.0)

    def test_inset_with_round_four(self):
        result = parse_clip_path("inset(10px 20px round 5px 10px 15px 20px)")
        assert isinstance(result, ClipInset)
        assert result.top == 10.0
        assert result.right == 20.0
        assert result.bottom == 10.0
        assert result.left == 20.0
        assert result.round_radii == (5.0, 10.0, 15.0, 20.0)

    def test_invalid_returns_none_string(self):
        assert parse_clip_path("url(#clip)") == "none"
        assert parse_clip_path("invalid") == "none"


# ------------------------------------------------------------------
# Gradient parsing (P2-4)
# ------------------------------------------------------------------

class TestGradientParsing:
    def test_linear_gradient_basic(self):
        result = parse_gradient("linear-gradient(#e66465, #9198e5)")
        assert isinstance(result, LinearGradientValue)
        assert result.angle == 180.0  # default: to bottom
        assert len(result.stops) == 2
        assert result.stops[0].position == 0.0
        assert result.stops[1].position == 1.0

    def test_linear_gradient_angle(self):
        result = parse_gradient("linear-gradient(45deg, red, blue)")
        assert isinstance(result, LinearGradientValue)
        assert result.angle == 45.0
        assert len(result.stops) == 2

    def test_linear_gradient_to_right(self):
        result = parse_gradient("linear-gradient(to right, red, blue)")
        assert isinstance(result, LinearGradientValue)
        assert result.angle == 90.0

    def test_linear_gradient_to_top(self):
        result = parse_gradient("linear-gradient(to top, red, blue)")
        assert isinstance(result, LinearGradientValue)
        assert result.angle == 0.0

    def test_linear_gradient_stops_with_position(self):
        result = parse_gradient("linear-gradient(red 0%, yellow 50%, blue 100%)")
        assert isinstance(result, LinearGradientValue)
        assert len(result.stops) == 3
        assert result.stops[0].position == pytest.approx(0.0)
        assert result.stops[1].position == pytest.approx(0.5)
        assert result.stops[2].position == pytest.approx(1.0)

    def test_linear_gradient_auto_positions(self):
        result = parse_gradient("linear-gradient(red, green, blue)")
        assert isinstance(result, LinearGradientValue)
        assert len(result.stops) == 3
        assert result.stops[0].position == pytest.approx(0.0)
        assert result.stops[1].position == pytest.approx(0.5)
        assert result.stops[2].position == pytest.approx(1.0)

    def test_radial_gradient_basic(self):
        result = parse_gradient("radial-gradient(circle, red, blue)")
        assert isinstance(result, RadialGradientValue)
        assert result.shape == "circle"
        assert len(result.stops) == 2

    def test_radial_gradient_default_ellipse(self):
        result = parse_gradient("radial-gradient(red, blue)")
        assert isinstance(result, RadialGradientValue)
        assert result.shape == "ellipse"
        assert len(result.stops) == 2

    def test_radial_gradient_with_position(self):
        result = parse_gradient("radial-gradient(circle at 30% 70%, red, blue)")
        assert isinstance(result, RadialGradientValue)
        assert result.shape == "circle"
        assert result.cx == pytest.approx(0.3)
        assert result.cy == pytest.approx(0.7)

    def test_gradient_none(self):
        assert parse_gradient("none") == "none"
        assert parse_gradient(None) == "none"
        assert parse_gradient("invalid-text") == "none"

    def test_linear_gradient_with_rgb(self):
        result = parse_gradient("linear-gradient(rgb(255, 0, 0), rgb(0, 0, 255))")
        assert isinstance(result, LinearGradientValue)
        assert len(result.stops) == 2


# ------------------------------------------------------------------
# background shorthand expansion (P2-4)
# ------------------------------------------------------------------

class TestBackgroundShorthand:
    def test_background_color_passthrough(self):
        result = expand_shorthand("background", "red")
        assert result == {"background-color": "red"}

    def test_background_hex(self):
        result = expand_shorthand("background", "#ff0000")
        assert result == {"background-color": "#ff0000"}

    def test_background_gradient(self):
        result = expand_shorthand("background", "linear-gradient(red, blue)")
        assert result == {"background-image": "linear-gradient(red, blue)"}

    def test_background_radial_gradient(self):
        result = expand_shorthand("background", "radial-gradient(circle, red, blue)")
        assert result == {"background-image": "radial-gradient(circle, red, blue)"}


# ------------------------------------------------------------------
# box-shadow parsing
# ------------------------------------------------------------------

class TestBoxShadowParsing:
    def test_none(self):
        assert parse_box_shadow("none") == "none"

    def test_none_value(self):
        assert parse_box_shadow(None) == "none"

    def test_simple_shadow(self):
        result = parse_box_shadow("0 4px 6px rgba(0,0,0,0.1)")
        assert isinstance(result, tuple)
        assert len(result) == 1
        s = result[0]
        assert isinstance(s, BoxShadow)
        assert s.offset_x == 0.0
        assert s.offset_y == 4.0
        assert s.blur_radius == 6.0
        assert s.spread_radius == 0.0
        assert "0,0,0" in s.color
        assert s.inset is False

    def test_shadow_with_spread(self):
        result = parse_box_shadow("2px 3px 4px 5px #ff0000")
        assert len(result) == 1
        s = result[0]
        assert s.offset_x == 2.0
        assert s.offset_y == 3.0
        assert s.blur_radius == 4.0
        assert s.spread_radius == 5.0

    def test_multiple_shadows(self):
        result = parse_box_shadow("0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_inset_shadow(self):
        result = parse_box_shadow("inset 0 2px 4px black")
        assert len(result) == 1
        assert result[0].inset is True
        assert result[0].offset_x == 0.0
        assert result[0].offset_y == 2.0

    def test_color_at_start(self):
        result = parse_box_shadow("red 0 4px 6px")
        assert len(result) == 1
        assert result[0].blur_radius == 6.0

    def test_offset_only(self):
        result = parse_box_shadow("5px 5px")
        assert len(result) == 1
        s = result[0]
        assert s.offset_x == 5.0
        assert s.offset_y == 5.0
        assert s.blur_radius == 0.0


# ------------------------------------------------------------------
# transform parsing
# ------------------------------------------------------------------

class TestTransformParsing:
    def test_none(self):
        assert parse_transform("none") == "none"

    def test_none_value(self):
        assert parse_transform(None) == "none"

    def test_rotate_deg(self):
        result = parse_transform("rotate(-90deg)")
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert result[0].name == "rotate"
        assert result[0].args == (-90.0,)

    def test_rotate_bare_number(self):
        result = parse_transform("rotate(45)")
        assert result[0].args == (45.0,)

    def test_rotate_rad(self):
        result = parse_transform("rotate(3.14159rad)")
        assert abs(result[0].args[0] - 180.0) < 0.1

    def test_translate(self):
        result = parse_transform("translate(10px, -5px)")
        assert result[0].name == "translate"
        assert result[0].args == (10.0, -5.0)

    def test_translate_single(self):
        result = parse_transform("translate(20px)")
        assert result[0].args == (20.0,)

    def test_scale_uniform(self):
        result = parse_transform("scale(0.8)")
        assert result[0].name == "scale"
        assert result[0].args == (0.8,)

    def test_scale_xy(self):
        result = parse_transform("scale(2, 0.5)")
        assert result[0].args == (2.0, 0.5)

    def test_function_chain(self):
        result = parse_transform("translate(10px, -5px) scale(0.8)")
        assert len(result) == 2
        assert result[0].name == "translate"
        assert result[1].name == "scale"

    def test_translateX(self):
        result = parse_transform("translateX(10px)")
        assert result[0].name == "translatex"
        assert result[0].args == (10.0,)

    def test_translateY(self):
        result = parse_transform("translateY(-20px)")
        assert result[0].name == "translatey"
        assert result[0].args == (-20.0,)


# ------------------------------------------------------------------
# CSS filter parsing
# ------------------------------------------------------------------

class TestFilterParsing:
    def test_none(self):
        assert parse_filter("none") == "none"

    def test_none_value(self):
        assert parse_filter(None) == "none"

    def test_blur(self):
        result = parse_filter("blur(5px)")
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert result[0].name == "blur"
        assert result[0].args == (5.0,)

    def test_grayscale_percent(self):
        result = parse_filter("grayscale(100%)")
        assert result[0].name == "grayscale"
        assert result[0].args == (1.0,)

    def test_grayscale_number(self):
        result = parse_filter("grayscale(0.5)")
        assert result[0].name == "grayscale"
        assert result[0].args == (0.5,)

    def test_brightness(self):
        result = parse_filter("brightness(150%)")
        assert result[0].name == "brightness"
        assert result[0].args == (1.5,)

    def test_contrast(self):
        result = parse_filter("contrast(200%)")
        assert result[0].name == "contrast"
        assert result[0].args == (2.0,)

    def test_opacity(self):
        result = parse_filter("opacity(50%)")
        assert result[0].name == "opacity"
        assert result[0].args == (0.5,)

    def test_saturate(self):
        result = parse_filter("saturate(200%)")
        assert result[0].name == "saturate"
        assert result[0].args == (2.0,)

    def test_sepia(self):
        result = parse_filter("sepia(100%)")
        assert result[0].name == "sepia"
        assert result[0].args == (1.0,)

    def test_filter_chain(self):
        result = parse_filter("grayscale(100%) blur(2px)")
        assert len(result) == 2
        assert result[0].name == "grayscale"
        assert result[1].name == "blur"

    def test_drop_shadow(self):
        result = parse_filter("drop-shadow(4px 4px 6px black)")
        assert len(result) == 1
        assert result[0].name == "drop-shadow"
        assert result[0].args[0] == 4.0  # offset-x
        assert result[0].args[1] == 4.0  # offset-y
        assert result[0].args[2] == 6.0  # blur

    def test_unknown_filter_ignored(self):
        result = parse_filter("url(#foo)")
        assert result == "none"