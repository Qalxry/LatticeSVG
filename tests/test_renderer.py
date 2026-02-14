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


class TestOpacityRendering:
    def test_background_opacity(self):
        """Background rect should use opacity from style."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "opacity": "0.5",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        # opacity="0.5" should appear on the background rect
        assert 'opacity="0.5"' in svg

    def test_text_opacity(self):
        """Text elements should include opacity when < 1."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
        })
        text = TextNode("Hello", style={
            "font-size": "16px",
            "opacity": "0.3",
        })
        grid.add(text, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert '0.3' in svg

    def test_default_opacity_omitted(self):
        """When opacity is 1 (default), it should not clutter the SVG text."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
        })
        text = TextNode("Hello", style={"font-size": "16px"})
        grid.add(text, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        # opacity should not appear on text elements when it's 1.0
        root = _parse_svg(svg)
        text_elems = root.findall('.//text')
        for te in text_elems:
            assert te.attrib.get('opacity') is None


class TestBorderRadius:
    """P1-1: border-radius support."""

    def test_background_rect_has_rx_ry(self):
        """Background rect should have rx/ry when border-radius is set."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "border-radius": "12px",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        root = _parse_svg(svg)
        rects = root.findall('.//rect')
        # At least one rect should have rx
        rx_values = [r.attrib.get('rx') for r in rects if r.attrib.get('rx')]
        assert any(float(v) == 12.0 for v in rx_values)

    def test_border_rect_with_radius(self):
        """Border with radius should render as rect, not lines."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "border": "2px solid #0000ff",
            "border-radius": "8px",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        root = _parse_svg(svg)
        # Should have a rect with stroke (border) and rx (radius)
        rects = root.findall('.//rect')
        border_rects = [r for r in rects if r.attrib.get('stroke') and r.attrib.get('rx')]
        assert len(border_rects) >= 1
        br = border_rects[0]
        assert float(br.attrib['rx']) == 8.0

    def test_no_radius_uses_paths(self):
        """Without border-radius, borders render as line paths (not rect)."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "border": "2px solid #0000ff",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        root = _parse_svg(svg)
        # drawsvg renders Line as <path> — should have path elements with stroke
        paths = root.findall('.//path')
        stroke_paths = [p for p in paths if p.attrib.get('stroke')]
        assert len(stroke_paths) >= 1

    def test_no_radius_no_rx(self):
        """Background rect without border-radius should not have rx/ry."""
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
        root = _parse_svg(svg)
        rects = root.findall('.//rect')
        for r in rects:
            # rx should either be absent or 0
            rx = r.attrib.get('rx')
            assert rx is None or float(rx) == 0


class TestBorderStyle:
    """P1-2: border-style dashed/dotted support."""

    def test_dashed_border(self):
        """Dashed border should produce stroke-dasharray."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "border": "2px dashed #333333",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "stroke-dasharray" in svg

    def test_dotted_border(self):
        """Dotted border should produce stroke-dasharray."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "border": "2px dotted #999999",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "stroke-dasharray" in svg

    def test_solid_border_no_dasharray(self):
        """Solid border should NOT have stroke-dasharray."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "border": "2px solid #000000",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "stroke-dasharray" not in svg

    def test_dashed_with_radius(self):
        """Dashed border + border-radius should work together."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "border": "3px dashed #ff0000",
            "border-radius": "10px",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        root = _parse_svg(svg)
        rects = root.findall('.//rect')
        border_rects = [r for r in rects if r.attrib.get('stroke')]
        assert len(border_rects) >= 1
        br = border_rects[0]
        assert float(br.attrib.get('rx')) == 10.0
        assert 'stroke-dasharray' in br.attrib


class TestRenderToDrawing:
    """P1-3: render_to_drawing() convenience method."""

    def test_returns_drawing_without_file(self, tmp_path):
        """render_to_drawing should return a Drawing without creating a file."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#aabbcc",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        drawing = renderer.render_to_drawing(grid)

        # Should be a drawsvg.Drawing
        import drawsvg as dw
        assert isinstance(drawing, dw.Drawing)

        # No file should have been created
        import os
        files_before = set(os.listdir(tmp_path))
        assert len(files_before) == 0  # tmp_path is empty

    def test_drawing_matches_render(self):
        """render_to_drawing SVG output should match render_to_string."""
        grid = GridContainer(style={
            "width": "300px",
            "grid-template-columns": ["300px"],
            "background-color": "#ffffff",
        })
        box = BoxNode(width=300, height=80)
        grid.add(box, row=1, col=1)
        grid.layout(available_width=300)

        renderer = Renderer()
        drawing = renderer.render_to_drawing(grid)
        svg_from_drawing = drawing.as_svg()

        renderer2 = Renderer()
        svg_from_string = renderer2.render_to_string(grid)

        assert svg_from_drawing == svg_from_string

    def test_render_uses_render_to_drawing(self, tmp_path):
        """render() should produce a file AND return the same Drawing."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ccddee",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        out = str(tmp_path / "test.svg")
        renderer = Renderer()
        d = renderer.render(grid, out)

        import drawsvg as dw
        assert isinstance(d, dw.Drawing)

        import os
        assert os.path.exists(out)


# ------------------------------------------------------------------
# Font embedding (P2-6)
# ------------------------------------------------------------------

class TestFontEmbedding:
    """Tests for ``embed_fonts=True``."""

    def test_embed_fonts_injects_font_face(self, tmp_path):
        """embedded SVG should contain @font-face with WOFF2 data URIs."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["1fr"],
        })
        grid.add(TextNode("Hello world", style={"font-size": 16}))
        grid.layout(available_width=400)

        renderer = Renderer()
        svg = renderer.render_to_string(grid, embed_fonts=True)

        assert "@font-face" in svg
        assert "font/woff2" in svg
        assert "base64," in svg

    def test_embed_fonts_no_duplicates(self, tmp_path):
        """Each (font-family, weight, style) triplet should appear once."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["1fr"],
        })
        # Two TextNodes using the same font → single @font-face
        grid.add(TextNode("Hello", style={"font-size": 14}))
        grid.add(TextNode("World", style={"font-size": 14}))
        grid.layout(available_width=400)

        renderer = Renderer()
        svg = renderer.render_to_string(grid, embed_fonts=True)

        # Count occurrences — there should be exactly one per font used
        import re
        faces = re.findall(r"@font-face", svg)
        families = re.findall(r'font-family:\s*"([^"]+)"', svg)
        # Should have no duplicate (family, weight) pairs in @font-face
        weight_re = re.findall(r"font-weight:\s*(\w+)", svg)
        pairs = list(zip(families, weight_re))
        assert len(pairs) == len(set(pairs)), f"Duplicate @font-face: {pairs}"

    def test_embed_fonts_false_no_font_face(self, tmp_path):
        """Without embed_fonts the SVG must NOT contain @font-face."""
        grid = GridContainer(style={
            "width": "400px",
            "grid-template-columns": ["1fr"],
        })
        grid.add(TextNode("Hello", style={"font-size": 14}))
        grid.layout(available_width=400)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "@font-face" not in svg

    def test_embed_fonts_rich_text(self, tmp_path):
        """Rich text with bold/italic/code → multiple @font-face rules."""
        grid = GridContainer(style={
            "width": "500px",
            "grid-template-columns": ["1fr"],
        })
        grid.add(TextNode(
            '<b>Bold</b> and <code>code</code>',
            style={"font-size": 14},
            markup="html",
        ))
        grid.layout(available_width=500)

        renderer = Renderer()
        svg = renderer.render_to_string(grid, embed_fonts=True)

        import re
        faces = re.findall(r"@font-face", svg)
        # At least 2: normal + bold (code may add a third for monospace)
        assert len(faces) >= 2, f"Expected >=2 @font-face rules, got {len(faces)}"

    def test_render_to_file_with_embed(self, tmp_path):
        """render() with embed_fonts=True should produce a valid file."""
        grid = GridContainer(style={
            "width": "300px",
            "grid-template-columns": ["1fr"],
        })
        grid.add(TextNode("Test", style={"font-size": 14}))
        grid.layout(available_width=300)

        out = str(tmp_path / "embedded.svg")
        renderer = Renderer()
        d = renderer.render(grid, out, embed_fonts=True)

        import drawsvg as dw
        assert isinstance(d, dw.Drawing)

        import os
        assert os.path.exists(out)
        with open(out) as f:
            content = f.read()
        assert "@font-face" in content


# ------------------------------------------------------------------
# Independent border-radius (P2-1)
# ------------------------------------------------------------------

class TestIndependentBorderRadius:
    """P2-1: four-corner independent border-radius."""

    def test_uniform_radius_still_uses_rect(self):
        """When all four corners are equal, background should use <rect rx=...>."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "border-radius": "10px",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        root = _parse_svg(svg)
        rects = root.findall('.//rect')
        rx_values = [r.attrib.get('rx') for r in rects if r.attrib.get('rx')]
        assert any(float(v) == 10.0 for v in rx_values)

    def test_independent_corners_use_path(self):
        """When corners differ, background should use <path> instead of <rect>."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "border-radius": "10px 20px 0 5px",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        root = _parse_svg(svg)
        # Should have a <path> with fill (background rendered as path)
        paths = root.findall('.//path')
        fill_paths = [p for p in paths if p.attrib.get('fill', 'none') != 'none']
        assert len(fill_paths) >= 1, "Expected path element for non-uniform border-radius background"

    def test_independent_corners_border_path(self):
        """Border with non-uniform radius should render as <path>."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "border": "2px solid #0000ff",
            "border-radius": "10px 0 10px 0",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        root = _parse_svg(svg)
        # Border path should have stroke and no fill
        paths = root.findall('.//path')
        border_paths = [p for p in paths
                        if p.attrib.get('stroke') and p.attrib.get('fill') == 'none']
        assert len(border_paths) >= 1

    def test_individual_longhand_properties(self):
        """Setting individual corner radii via longhand properties."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "border-top-left-radius": "20px",
            "border-top-right-radius": "0",
            "border-bottom-right-radius": "20px",
            "border-bottom-left-radius": "0",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        root = _parse_svg(svg)
        # Non-uniform → should use <path>
        paths = root.findall('.//path')
        fill_paths = [p for p in paths if p.attrib.get('fill', 'none') != 'none']
        assert len(fill_paths) >= 1

    def test_zero_radius_no_path(self):
        """All-zero radius should produce neither rx nor path arcs."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "border-radius": "0",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        root = _parse_svg(svg)
        rects = root.findall('.//rect')
        for r in rects:
            rx = r.attrib.get('rx')
            assert rx is None or float(rx) == 0


# ------------------------------------------------------------------
# clip-path rendering (P2-2)
# ------------------------------------------------------------------

class TestClipPathRendering:
    """P2-2: CSS clip-path property."""

    def test_circle_clip(self):
        """clip-path: circle() should create a <clipPath> with <circle>."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "clip-path": "circle(50% at 50% 50%)",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "clipPath" in svg or "clip-path" in svg
        root = _parse_svg(svg)
        circles = root.findall('.//{http://www.w3.org/2000/svg}circle')
        if not circles:
            circles = root.findall('.//circle')
        assert len(circles) >= 1

    def test_polygon_clip(self):
        """clip-path: polygon() should produce a path in clipPath."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "clip-path": "polygon(50% 0%, 100% 100%, 0% 100%)",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "clipPath" in svg or "clip-path" in svg

    def test_ellipse_clip(self):
        """clip-path: ellipse() should create an ellipse element."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "clip-path": "ellipse(40% 30% at 50% 50%)",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "clipPath" in svg or "clip-path" in svg
        root = _parse_svg(svg)
        ellipses = root.findall('.//{http://www.w3.org/2000/svg}ellipse')
        if not ellipses:
            ellipses = root.findall('.//ellipse')
        assert len(ellipses) >= 1

    def test_inset_clip(self):
        """clip-path: inset() should create a rect in clipPath."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "clip-path": "inset(10px)",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "clipPath" in svg or "clip-path" in svg

    def test_clip_path_none(self):
        """clip-path: none should not add any clipPath."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background-color": "#ff0000",
            "clip-path": "none",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "clipPath" not in svg


# ------------------------------------------------------------------
# Gradient background rendering (P2-4)
# ------------------------------------------------------------------

class TestGradientRendering:
    def test_linear_gradient_svg_output(self):
        """A linear-gradient background should produce a <linearGradient> in the SVG."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background": "linear-gradient(#e66465, #9198e5)",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "linearGradient" in svg

    def test_radial_gradient_svg_output(self):
        """A radial-gradient background should produce a <radialGradient> in the SVG."""
        grid = GridContainer(style={
            "width": "200px",
            "grid-template-columns": ["200px"],
            "background": "radial-gradient(circle, red, blue)",
        })
        box = BoxNode()
        grid.add(box, row=1, col=1)
        grid.layout(available_width=200)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "radialGradient" in svg

    def test_gradient_with_solid_bg_child(self):
        """Grid with gradient bg + child with solid bg color."""
        grid = GridContainer(style={
            "width": "300px",
            "grid-template-columns": ["300px"],
            "background": "linear-gradient(to right, #ff0000, #0000ff)",
        })
        box = BoxNode(background_color="#ffffff")
        grid.add(box, row=1, col=1)
        grid.layout(available_width=300)

        renderer = Renderer()
        svg = renderer.render_to_string(grid)
        assert "linearGradient" in svg
