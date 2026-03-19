"""Tests for font query API and MplNode auto-font."""
import pytest

from latticesvg.text.font import (
    FontInfo,
    FontManager,
    GlyphMetrics,
    _GENERIC_FAMILIES,
    parse_font_families,
)
from latticesvg.text import get_font_path, list_fonts


# ---------------------------------------------------------------
# parse_font_families
# ---------------------------------------------------------------


class TestParseFontFamilies:
    def test_none_returns_sans_serif(self):
        assert parse_font_families(None) == ["sans-serif"]

    def test_single_string(self):
        assert parse_font_families("Arial") == ["Arial"]

    def test_comma_separated(self):
        result = parse_font_families("Arial, 'Noto Sans', sans-serif")
        assert result == ["Arial", "Noto Sans", "sans-serif"]

    def test_double_quoted(self):
        result = parse_font_families('"Times New Roman", serif')
        assert result == ["Times New Roman", "serif"]

    def test_list_input(self):
        result = parse_font_families(["Arial", "Helvetica, sans-serif"])
        assert result == ["Arial", "Helvetica", "sans-serif"]

    def test_empty_string_returns_default(self):
        assert parse_font_families("") == ["sans-serif"]

    def test_non_string_returns_default(self):
        assert parse_font_families(42) == ["sans-serif"]


# ---------------------------------------------------------------
# FontManager.get_font_path
# ---------------------------------------------------------------


class TestGetFontPath:
    def setup_method(self):
        FontManager.reset()

    def test_returns_none_for_missing(self):
        fm = FontManager.instance()
        assert fm.get_font_path("NonExistentFont99999") is None

    def test_returns_string_path(self):
        fm = FontManager.instance()
        # Try a generic family; most systems have at least one
        path = fm.get_font_path("sans-serif")
        if path is not None:
            assert isinstance(path, str)
            assert path.endswith((".ttf", ".otf", ".ttc"))

    def test_weight_style(self):
        fm = FontManager.instance()
        path = fm.get_font_path("sans-serif", weight="bold")
        # Should return a path or None — just verify it doesn't crash
        assert path is None or isinstance(path, str)

    def test_convenience_wrapper_matches(self):
        FontManager.reset()
        fm = FontManager.instance()
        direct = fm.get_font_path("sans-serif")
        wrapper = get_font_path("sans-serif")
        assert direct == wrapper


# ---------------------------------------------------------------
# FontManager.list_fonts
# ---------------------------------------------------------------


class TestListFonts:
    def setup_method(self):
        FontManager.reset()

    def test_returns_list_of_fontinfo(self):
        fm = FontManager.instance()
        fonts = fm.list_fonts()
        assert isinstance(fonts, list)
        if fonts:
            f = fonts[0]
            assert isinstance(f, FontInfo)
            assert f.family
            assert f.path
            assert f.format in ("ttf", "otf", "ttc")
            assert f.weight in ("normal", "bold")
            assert f.style in ("normal", "italic")

    def test_convenience_wrapper(self):
        FontManager.reset()
        fm = FontManager.instance()
        assert len(fm.list_fonts()) == len(list_fonts())

    def test_sorted_by_family(self):
        fonts = list_fonts()
        if len(fonts) >= 2:
            names = [f.family.lower() for f in fonts]
            assert names == sorted(names)


# ---------------------------------------------------------------
# MplNode auto-font
# ---------------------------------------------------------------


class TestMplNodeAutoFont:
    @pytest.fixture
    def mpl_figure(self):
        pytest.importorskip("matplotlib")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.plot([1, 2], [1, 2])
        ax.set_title("测试标题")
        yield fig
        plt.close(fig)

    def test_auto_mpl_font_default_true(self, mpl_figure):
        from latticesvg.nodes.mpl import MplNode
        node = MplNode(mpl_figure)
        assert node._auto_mpl_font is True
        assert node._tight_layout is True

    def test_auto_mpl_font_can_disable(self, mpl_figure):
        from latticesvg.nodes.mpl import MplNode
        node = MplNode(mpl_figure, auto_mpl_font=False)
        assert node._auto_mpl_font is False

    def test_tight_layout_can_disable(self, mpl_figure):
        from latticesvg.nodes.mpl import MplNode
        node = MplNode(mpl_figure, tight_layout=False)
        assert node._tight_layout is False

    def test_resolve_mpl_font_rc_sans_serif(self, mpl_figure):
        from latticesvg.nodes.mpl import MplNode
        node = MplNode(mpl_figure, style={"font-family": "Arial, sans-serif"})
        rc, paths = node._resolve_mpl_font_rc()
        assert isinstance(rc["font.family"], list)
        assert len(rc["font.family"]) > 0
        assert rc["svg.fonttype"] == "path"
        assert isinstance(paths, list)

    def test_resolve_mpl_font_rc_serif(self, mpl_figure):
        from latticesvg.nodes.mpl import MplNode
        node = MplNode(mpl_figure, style={"font-family": "Times New Roman, serif"})
        rc, paths = node._resolve_mpl_font_rc()
        assert isinstance(rc["font.family"], list)
        assert len(rc["font.family"]) > 0

    def test_resolve_mpl_font_rc_monospace(self, mpl_figure):
        from latticesvg.nodes.mpl import MplNode
        node = MplNode(mpl_figure, style={"font-family": "monospace"})
        rc, paths = node._resolve_mpl_font_rc()
        assert isinstance(rc["font.family"], list)
        assert len(rc["font.family"]) > 0

    def test_get_svg_fragment_with_auto_font(self, mpl_figure):
        from latticesvg.nodes.mpl import MplNode
        from latticesvg.nodes.base import LayoutConstraints
        node = MplNode(mpl_figure, style={"font-family": "sans-serif"})
        # Need to layout first to get valid dimensions
        node.layout(LayoutConstraints(available_width=300))
        svg = node.get_svg_fragment()
        assert isinstance(svg, str)
        assert len(svg) > 0
        # With svg.fonttype='path', text should be rendered as paths
        # so we should NOT see font-family references to our fonts
        # (paths are <path d="..."/> elements instead of <text>)

    def test_get_svg_fragment_without_auto_font(self, mpl_figure):
        from latticesvg.nodes.mpl import MplNode
        from latticesvg.nodes.base import LayoutConstraints
        node = MplNode(mpl_figure, auto_mpl_font=False, style={"font-family": "sans-serif"})
        node.layout(LayoutConstraints(available_width=300))
        svg = node.get_svg_fragment()
        assert isinstance(svg, str)
        assert len(svg) > 0

    def test_svg_fonttype_always_path(self, mpl_figure):
        """Even with auto_mpl_font=False, svg.fonttype should be 'path'."""
        from latticesvg.nodes.mpl import MplNode
        from latticesvg.nodes.base import LayoutConstraints
        node = MplNode(mpl_figure, auto_mpl_font=False)
        node.layout(LayoutConstraints(available_width=300))
        svg = node.get_svg_fragment()
        # With fonttype='path', there should be no <text> tags
        # (matplotlib converts all text to paths)
        assert "<text" not in svg


# ---------------------------------------------------------------
# _GENERIC_FAMILIES constant
# ---------------------------------------------------------------


class TestGenericFamilies:
    def test_contains_standard(self):
        for name in ("serif", "sans-serif", "monospace"):
            assert name in _GENERIC_FAMILIES


# ---------------------------------------------------------------
# mpl font helpers (apply_mpl_fonts / restore / context manager)
# ---------------------------------------------------------------


mpl = pytest.importorskip("matplotlib")
plt = pytest.importorskip("matplotlib.pyplot")


class TestBuildMplRc:
    def test_returns_rc_and_paths(self):
        from latticesvg.text import _build_mpl_rc
        rc, paths = _build_mpl_rc("sans-serif")
        assert isinstance(rc, dict)
        assert isinstance(paths, list)
        assert rc["svg.fonttype"] == "path"
        assert rc["axes.unicode_minus"] is False

    def test_generic_serif(self):
        from latticesvg.text import _build_mpl_rc
        rc, _ = _build_mpl_rc("Times New Roman, serif")
        assert isinstance(rc["font.family"], list)
        assert len(rc["font.family"]) > 0

    def test_generic_monospace(self):
        from latticesvg.text import _build_mpl_rc
        rc, _ = _build_mpl_rc("monospace")
        assert isinstance(rc["font.family"], list)
        assert len(rc["font.family"]) > 0


class TestApplyRestoreMplFonts:
    def test_apply_changes_rcparams(self):
        from latticesvg.text import apply_mpl_fonts, restore_mpl_fonts
        old_family = mpl.rcParams["font.family"]
        apply_mpl_fonts("sans-serif")
        assert mpl.rcParams["axes.unicode_minus"] is False
        restore_mpl_fonts()
        assert mpl.rcParams["font.family"] == old_family

    def test_restore_is_idempotent(self):
        from latticesvg.text import restore_mpl_fonts
        restore_mpl_fonts()  # should not raise when nothing saved

    def test_apply_twice_overwrites_snapshot(self):
        from latticesvg.text import apply_mpl_fonts, restore_mpl_fonts
        apply_mpl_fonts("sans-serif")
        apply_mpl_fonts("serif")
        # font.family is now a concrete name list
        family = mpl.rcParams["font.family"]
        assert isinstance(family, list)
        assert len(family) > 0
        restore_mpl_fonts()

    def test_apply_sets_svg_fonttype(self):
        from latticesvg.text import apply_mpl_fonts, restore_mpl_fonts
        apply_mpl_fonts("sans-serif")
        assert mpl.rcParams["svg.fonttype"] == "path"
        restore_mpl_fonts()


class TestMplFontContext:
    def test_context_applies_and_restores(self):
        from latticesvg.text import mpl_font_context
        old_minus = mpl.rcParams["axes.unicode_minus"]
        old_fonttype = mpl.rcParams["svg.fonttype"]
        with mpl_font_context("sans-serif"):
            assert mpl.rcParams["axes.unicode_minus"] is False
            assert mpl.rcParams["svg.fonttype"] == "path"
        # Restored after exit
        assert mpl.rcParams["axes.unicode_minus"] == old_minus
        assert mpl.rcParams["svg.fonttype"] == old_fonttype

    def test_context_with_figure(self):
        from latticesvg.text import mpl_font_context
        with mpl_font_context("sans-serif"):
            fig, ax = plt.subplots()
            ax.plot([1, 2], [3, 4])
            ax.set_title("Test")
            plt.close(fig)
        # Just verify no exception
