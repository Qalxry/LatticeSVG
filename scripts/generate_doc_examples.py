#!/usr/bin/env python3
"""Generate example SVG images for the documentation site.

This script:
1. Copies relevant demo outputs to docs/assets/images/examples/
2. Generates new doc-specific examples (quickstart, etc.)

Usage:
    python scripts/generate_doc_examples.py
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO_OUT = ROOT / "examples" / "demo_output"
DOC_IMG = ROOT / "docs" / "assets" / "images" / "examples"

sys.path.insert(0, str(ROOT / "src"))

from latticesvg import GridContainer, TextNode, MathNode, Renderer, templates
from latticesvg.templates import build_table


def ensure_dir():
    DOC_IMG.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------
# Copy existing demo SVGs (renamed for clarity)
# -----------------------------------------------------------------------
DEMO_COPIES = {
    # grid-layout tutorial
    "04_fixed_grid.svg": "grid_fixed.svg",
    "05_fr_grid.svg": "grid_fr.svg",
    "06_mixed_tracks.svg": "grid_mixed.svg",
    "07_auto_placement.svg": "grid_auto_placement.svg",
    "08_spanning.svg": "grid_spanning.svg",
    "09_alignment.svg": "grid_alignment.svg",
    "10_nested_grid.svg": "grid_nested.svg",
    "30_grid_template_areas.svg": "grid_areas.svg",
    "38_grid_auto_tracks.svg": "grid_auto_tracks.svg",
    "41_repeat_minmax.svg": "grid_repeat_minmax.svg",
    "43_justify_spacing.svg": "grid_justify_spacing.svg",
    # text tutorial
    "12_text_basic.svg": "text_basic.svg",
    "13_text_whitespace.svg": "text_whitespace.svg",
    "20_mixed_fonts.svg": "text_mixed_fonts.svg",
    "21_overflow_wrap.svg": "text_overflow.svg",
    "24_ellipsis_precision.svg": "text_ellipsis.svg",
    "25_pre_line.svg": "text_pre_line.svg",
    "44_hyphens.svg": "text_hyphens.svg",
    "48_vertical_row_headers.svg": "text_vertical.svg",
    "49_text_combine_upright.svg": "text_tcu.svg",
    # node types
    "14_svg_node.svg": "node_svg.svg",
    "15_mpl_node.svg": "node_mpl.svg",
    "35_math_formula.svg": "node_math.svg",
    "36_inline_math.svg": "node_inline_math.svg",
    "22_image_gallery.svg": "node_image_gallery.svg",
    # styling
    "11_box_model.svg": "style_box_model.svg",
    "26_opacity.svg": "style_opacity.svg",
    "27_border_radius.svg": "style_border_radius.svg",
    "28_border_style.svg": "style_border_style.svg",
    "39_independent_border_radius.svg": "style_independent_radius.svg",
    "40_clip_path.svg": "style_clip_path.svg",
    "42_gradient_bg.svg": "style_gradient.svg",
    "45_box_shadow.svg": "style_box_shadow.svg",
    "46_transform.svg": "style_transform.svg",
    "47_css_filter.svg": "style_filter.svg",
    # rich text
    "33_rich_text.svg": "rich_text_html.svg",
    "34_markdown_text.svg": "rich_text_markdown.svg",
    # advanced
    "16_templates.svg": "advanced_templates.svg",
    "31_table_api.svg": "advanced_table.svg",
    "32_waterfall_cards.svg": "advanced_waterfall.svg",
    "18_full_report.svg": "advanced_report.svg",
    "37b_font_embed_on.svg": "advanced_font_embed.svg",
    # concepts / landing
    "29_render_to_drawing.svg": "concepts_render.svg",
    "50_tcu_compat.svg": "text_tcu_compat.svg",
}


def copy_demos():
    """Copy and rename demo outputs."""
    copied = 0
    for src_name, dst_name in DEMO_COPIES.items():
        src = DEMO_OUT / src_name
        dst = DOC_IMG / dst_name
        if src.exists():
            shutil.copy2(src, dst)
            copied += 1
        else:
            print(f"  SKIP (not found): {src_name}")
    print(f"  Copied {copied}/{len(DEMO_COPIES)} demo SVGs")


# -----------------------------------------------------------------------
# Generate quickstart examples
# -----------------------------------------------------------------------

def gen_quickstart_first():
    """Generate the first quickstart example."""
    page = GridContainer(style={
        "width": "600px",
        "padding": "32px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "16px",
    })

    page.add(TextNode("欢迎使用 LatticeSVG", style={
        "font-size": "28px",
        "font-weight": "bold",
        "color": "#2c3e50",
        "text-align": "center",
    }))

    page.add(TextNode(
        "LatticeSVG 是一个基于 CSS Grid 的声明式矢量布局引擎，"
        "用 Python 字典描述样式，输出高质量 SVG。",
        style={
            "font-size": "14px",
            "color": "#555555",
            "line-height": "1.6",
        },
    ))

    r = Renderer()
    r.render(page, str(DOC_IMG / "quickstart_first.svg"))


def gen_quickstart_two_col():
    """Generate the two-column quickstart example."""
    page = GridContainer(style={
        "width": "600px",
        "padding": "24px",
        "background-color": "#f8f9fa",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "16px",
    })

    page.add(TextNode("左侧内容\n\n这是左列的示例文本。", style={
        "padding": "16px",
        "background-color": "#ffffff",
        "border": "1px solid #dee2e6",
        "font-size": "14px",
        "line-height": "1.6",
    }))

    page.add(TextNode("右侧内容\n\n这是右列的示例文本。", style={
        "padding": "16px",
        "background-color": "#ffffff",
        "border": "1px solid #dee2e6",
        "font-size": "14px",
        "line-height": "1.6",
    }))

    r = Renderer()
    r.render(page, str(DOC_IMG / "quickstart_two_col.svg"))


def gen_quickstart_template():
    """Generate a template-based quickstart example."""
    page = GridContainer(style={
        **templates.REPORT_PAGE,
        "gap": "16px",
    })

    page.add(TextNode("使用模板的报告", style=templates.TITLE))
    page.add(TextNode(
        "LatticeSVG 内置 17 个样式模板，涵盖常见的布局和排版场景。"
        "只需解包模板字典并按需覆盖即可快速上手。",
        style={**templates.PARAGRAPH, "line-height": "1.6"},
    ))

    r = Renderer()
    r.render(page, str(DOC_IMG / "quickstart_template.svg"))


# -----------------------------------------------------------------------
# Generate landing page hero example
# -----------------------------------------------------------------------

def gen_landing_hero():
    """Generate a compact example for the landing page."""
    page = GridContainer(style={
        "width": "500px",
        "padding": "24px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "12px",
        "border": "1px solid #e0e0e0",
        "border-radius": "8px",
    })

    page.add(TextNode("LatticeSVG", style={
        "font-size": "22px",
        "font-weight": "bold",
        "color": "#1a237e",
        "padding": "12px",
        "background-color": "#e8eaf6",
        "border-radius": "6px",
        "text-align": "center",
    }), col_span=2)

    page.add(TextNode("Grid 布局\n精确控制行列分配", style={
        "font-size": "13px",
        "padding": "12px",
        "background": "linear-gradient(135deg, #667eea, #764ba2)",
        "color": "#ffffff",
        "border-radius": "6px",
        "line-height": "1.6",
    }))

    page.add(TextNode("文本排版\n自动换行与多字体支持", style={
        "font-size": "13px",
        "padding": "12px",
        "background": "linear-gradient(135deg, #f093fb, #f5576c)",
        "color": "#ffffff",
        "border-radius": "6px",
        "line-height": "1.6",
    }))

    r = Renderer()
    r.render(page, str(DOC_IMG / "landing_hero.svg"))


# -----------------------------------------------------------------------
# Generate a styling showcase
# -----------------------------------------------------------------------

def gen_style_showcase():
    """Material-design card with shadows, gradients, rounded corners."""
    page = GridContainer(style={
        "width": "500px",
        "padding": "24px",
        "background-color": "#f5f5f5",
        "grid-template-columns": ["1fr"],
        "gap": "16px",
    })

    # Card with shadow
    card = GridContainer(style={
        "padding": "20px",
        "background-color": "#ffffff",
        "border-radius": "12px",
        "box-shadow": "0 4px 20px rgba(0, 0, 0, 0.12)",
        "grid-template-columns": ["1fr"],
        "gap": "8px",
    })
    card.add(TextNode("Material Card", style={
        "font-size": "18px",
        "font-weight": "bold",
        "color": "#1a237e",
    }))
    card.add(TextNode(
        "这张卡片展示了圆角、阴影和渐变等视觉样式。"
        "LatticeSVG 支持 63 种 CSS 属性。",
        style={"font-size": "13px", "color": "#666", "line-height": "1.6"},
    ))
    page.add(card)

    # Gradient banner
    page.add(TextNode("渐变背景", style={
        "padding": "16px",
        "color": "#ffffff",
        "font-size": "16px",
        "font-weight": "bold",
        "text-align": "center",
        "background": "linear-gradient(135deg, #667eea, #764ba2)",
        "border-radius": "8px",
    }))

    r = Renderer()
    r.render(page, str(DOC_IMG / "style_showcase.svg"))


# -----------------------------------------------------------------------
# Generate concepts architecture example
# -----------------------------------------------------------------------

def gen_concepts_example():
    """Simple pipeline visualization for the concepts page."""
    page = GridContainer(style={
        "width": "600px",
        "padding": "20px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "gap": "12px",
    })

    steps = [
        ("1. 创建节点", "#e3f2fd", "#1565c0"),
        ("2. 布局计算", "#e8f5e9", "#2e7d32"),
        ("3. 渲染输出", "#fff3e0", "#e65100"),
    ]

    for label, bg, fg in steps:
        page.add(TextNode(label, style={
            "padding": "16px",
            "background-color": bg,
            "color": fg,
            "font-size": "15px",
            "font-weight": "bold",
            "text-align": "center",
            "border-radius": "8px",
        }))

    r = Renderer()
    r.render(page, str(DOC_IMG / "concepts_pipeline.svg"))


# -----------------------------------------------------------------------
# Generate a table example for reference
# -----------------------------------------------------------------------

def gen_table_example():
    """Table for the templates/reference page."""
    table = build_table(
        headers=["属性", "类型", "默认值", "说明"],
        rows=[
            ["width", "length", "auto", "元素宽度"],
            ["padding", "length", "0px", "内边距"],
            ["font-size", "length", "16px", "字号"],
            ["color", "color", "#000000", "文字颜色"],
            ["background", "color", "transparent", "背景色"],
        ],
        col_widths=["120px", "80px", "100px", "1fr"],
        stripe_color="#f8f9fa",
    )

    Renderer().render(table, str(DOC_IMG / "ref_table.svg"))


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    ensure_dir()

    print("Copying demo outputs...")
    copy_demos()

    print("Generating quickstart examples...")
    gen_quickstart_first()
    gen_quickstart_two_col()
    gen_quickstart_template()

    print("Generating landing page example...")
    gen_landing_hero()

    print("Generating styling showcase...")
    gen_style_showcase()

    print("Generating concepts example...")
    gen_concepts_example()

    print("Generating table example...")
    gen_table_example()

    print(f"\nDone! SVGs written to {DOC_IMG.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
