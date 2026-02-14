"""Tests for the math backend and MathNode."""

import pytest
from unittest.mock import MagicMock, patch
from latticesvg.math.backend import SVGFragment, QuickJaxBackend, _ex_to_px, _EX_RATIO
from latticesvg.math import (
    get_backend,
    register_backend,
    set_default_backend,
    get_default_backend_name,
    _backend_registry,
    _backend_instances,
)
from latticesvg.nodes.math import MathNode
from latticesvg.nodes.base import LayoutConstraints


# -----------------------------------------------------------------------
# SVGFragment dataclass
# -----------------------------------------------------------------------


class TestSVGFragment:
    def test_basic(self):
        f = SVGFragment(svg_content="<g/>", width=100.0, height=50.0)
        assert f.width == 100.0
        assert f.height == 50.0
        assert f.depth == 0.0

    def test_depth(self):
        f = SVGFragment(svg_content="<g/>", width=10.0, height=20.0, depth=3.0)
        assert f.depth == 3.0


# -----------------------------------------------------------------------
# ex → px conversion
# -----------------------------------------------------------------------


class TestExToPx:
    def test_at_16px(self):
        # 1ex at 16px = 16 * 0.4315 = 6.904
        assert _ex_to_px(1.0, 16.0) == pytest.approx(16.0 * _EX_RATIO)

    def test_zero(self):
        assert _ex_to_px(0.0, 16.0) == 0.0

    def test_scaling(self):
        assert _ex_to_px(2.0, 20.0) == pytest.approx(2.0 * 20.0 * _EX_RATIO)


# -----------------------------------------------------------------------
# QuickJaxBackend
# -----------------------------------------------------------------------


class TestQuickJaxBackend:
    def test_available(self):
        backend = QuickJaxBackend()
        # quickjax should be installed in dev environment
        assert isinstance(backend.available(), bool)

    @pytest.mark.skipif(
        not QuickJaxBackend().available(),
        reason="quickjax not installed",
    )
    def test_render_simple(self):
        backend = QuickJaxBackend()
        frag = backend.render(r"E=mc^2", 16.0)
        assert isinstance(frag, SVGFragment)
        assert frag.width > 0
        assert frag.height > 0
        assert len(frag.svg_content) > 0
        # Should not contain xmlns (stripped for embedding)
        assert 'xmlns="http://www.w3.org/2000/svg"' not in frag.svg_content

    @pytest.mark.skipif(
        not QuickJaxBackend().available(),
        reason="quickjax not installed",
    )
    def test_render_caches(self):
        backend = QuickJaxBackend()
        frag1 = backend.render(r"x^2", 16.0)
        frag2 = backend.render(r"x^2", 16.0)
        assert frag1 is frag2  # Same object from cache

    @pytest.mark.skipif(
        not QuickJaxBackend().available(),
        reason="quickjax not installed",
    )
    def test_render_different_sizes(self):
        backend = QuickJaxBackend()
        frag16 = backend.render(r"x", 16.0)
        frag32 = backend.render(r"x", 32.0)
        # Larger font → larger dimensions
        assert frag32.width > frag16.width
        assert frag32.height > frag16.height

    @pytest.mark.skipif(
        not QuickJaxBackend().available(),
        reason="quickjax not installed",
    )
    def test_render_display_mode(self):
        backend = QuickJaxBackend()
        frag_inline = backend.render(r"\sum_{i=0}^n i", 16.0, display=False)
        frag_display = backend.render(r"\sum_{i=0}^n i", 16.0, display=True)
        # Display mode typically produces different (often taller) output
        assert isinstance(frag_display, SVGFragment)
        assert isinstance(frag_inline, SVGFragment)

    @pytest.mark.skipif(
        not QuickJaxBackend().available(),
        reason="quickjax not installed",
    )
    def test_embeddable_px_units(self):
        backend = QuickJaxBackend()
        frag = backend.render(r"a+b", 16.0)
        # width= and height= attributes should be in px (no "ex")
        import re
        # Check that width="..." and height="..." don't contain "ex"
        for attr in ("width", "height"):
            m = re.search(rf'{attr}="([^"]+)"', frag.svg_content)
            assert m is not None, f"Missing {attr} attribute"
            assert "ex" not in m.group(1), f"{attr} still in ex units"


# -----------------------------------------------------------------------
# Backend registry
# -----------------------------------------------------------------------


class TestBackendRegistry:
    def test_default_backend_name(self):
        assert get_default_backend_name() == "quickjax"

    def test_quickjax_registered(self):
        assert "quickjax" in _backend_registry

    @pytest.mark.skipif(
        not QuickJaxBackend().available(),
        reason="quickjax not installed",
    )
    def test_get_backend_default(self):
        backend = get_backend()
        assert isinstance(backend, QuickJaxBackend)

    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="Unknown math backend"):
            get_backend("nonexistent_backend_xyz")

    def test_register_custom(self):
        class DummyBackend:
            def render(self, latex, font_size):
                return SVGFragment("<g/>", 10.0, 10.0)
            def available(self):
                return True

        register_backend("dummy_test", DummyBackend)
        assert "dummy_test" in _backend_registry
        b = get_backend("dummy_test")
        assert isinstance(b, DummyBackend)
        # Cleanup
        _backend_registry.pop("dummy_test", None)
        _backend_instances.pop("dummy_test", None)


# -----------------------------------------------------------------------
# MathNode
# -----------------------------------------------------------------------


class TestMathNode:
    """Test MathNode measure/layout using a mock backend."""

    @pytest.fixture
    def mock_backend(self):
        """Create a mock math backend that returns a fixed SVGFragment."""
        backend = MagicMock()
        backend.available.return_value = True
        backend.render.return_value = SVGFragment(
            svg_content='<g><text>E=mc²</text></g>',
            width=100.0,
            height=30.0,
            depth=2.0,
        )
        return backend

    def test_repr(self):
        node = MathNode(r"E=mc^2")
        assert "E=mc^2" in repr(node)

    def test_repr_truncated(self):
        node = MathNode("x" * 50)
        r = repr(node)
        assert "…" in r

    def test_measure(self, mock_backend):
        node = MathNode(r"E=mc^2", style={"font-size": "16px"})
        with patch.object(node, "_get_backend", return_value=mock_backend):
            min_w, max_w, h = node.measure(LayoutConstraints())
        assert min_w == pytest.approx(100.0)
        assert max_w == pytest.approx(100.0)
        assert h == pytest.approx(30.0)

    def test_measure_with_padding(self, mock_backend):
        node = MathNode(r"E=mc^2", style={"font-size": "16px", "padding": "10px"})
        with patch.object(node, "_get_backend", return_value=mock_backend):
            min_w, max_w, h = node.measure(LayoutConstraints())
        # padding: 10px on each side = 20 extra horizontal, 20 vertical
        assert min_w == pytest.approx(120.0)
        assert h == pytest.approx(50.0)

    def test_layout_natural_size(self, mock_backend):
        node = MathNode(r"E=mc^2", style={"font-size": "16px"})
        with patch.object(node, "_get_backend", return_value=mock_backend):
            node.layout(LayoutConstraints(available_width=200))
        assert node.content_box.width == pytest.approx(100.0, abs=1.0)
        assert node.content_box.height == pytest.approx(30.0, abs=1.0)

    def test_layout_aspect_ratio(self, mock_backend):
        node = MathNode(r"E=mc^2", style={"font-size": "16px"})
        with patch.object(node, "_get_backend", return_value=mock_backend):
            node.layout(LayoutConstraints(available_width=50))
        # Shrunk to 50px wide, height should scale proportionally
        assert node.content_box.width == pytest.approx(50.0, abs=1.0)
        assert node.content_box.height == pytest.approx(15.0, abs=1.0)

    def test_get_svg_fragment(self, mock_backend):
        node = MathNode(r"E=mc^2", style={"font-size": "16px"})
        with patch.object(node, "_get_backend", return_value=mock_backend):
            node.layout(LayoutConstraints(available_width=200))
            content = node.get_svg_fragment()
        assert "<text>E=mc²</text>" in content

    def test_display_flag(self):
        node_display = MathNode(r"x", display=True)
        node_inline = MathNode(r"x", display=False)
        assert node_display.display is True
        assert node_inline.display is False

    def test_backend_name(self):
        node = MathNode(r"x", backend="custom_be")
        assert node._backend_name == "custom_be"

    @pytest.mark.skipif(
        not QuickJaxBackend().available(),
        reason="quickjax not installed",
    )
    def test_end_to_end_with_quickjax(self):
        """Integration: MathNode with actual quickjax backend."""
        node = MathNode(r"E=mc^2", style={"font-size": "20px"})
        min_w, max_w, h = node.measure(LayoutConstraints())
        assert min_w > 0
        assert h > 0

        node.layout(LayoutConstraints(available_width=300))
        assert node.content_box.width > 0
        assert node.content_box.height > 0

        svg = node.get_svg_fragment()
        assert len(svg) > 0
