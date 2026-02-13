#!/usr/bin/env python3
"""LatticeSVG 功能展示脚本

为每个核心功能生成独立的 SVG 文件，存放在 demo_output/ 目录中。
运行：  python demo.py
"""

from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path

# 确保 src 在路径中
sys.path.insert(0, str(Path(__file__).parent / "src"))

from latticesvg import (
    GridContainer, TextNode, ImageNode, SVGNode, MplNode,
    Renderer, Rect, LayoutConstraints, Node, ComputedStyle,
    templates,
)
from latticesvg.style.parser import parse_value, FrValue, AUTO, MIN_CONTENT, MAX_CONTENT

OUTPUT_DIR = Path(__file__).parent / "demo_output"

# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------

class ColorBox(Node):
    """纯色方块，用于可视化布局效果。"""

    def __init__(self, width=80, height=50, label="", **style_kw):
        super().__init__(style=style_kw)
        self._w = width
        self._h = height
        self.label = label

    def measure(self, c):
        ph = self.style.padding_horizontal + self.style.border_horizontal
        pv = self.style.padding_vertical + self.style.border_vertical
        return (self._w + ph, self._w + ph, self._h + pv)

    def layout(self, c):
        self._resolve_box_model(self._w, self._h)


def save(node: Node, filename: str, width: float = None):
    """布局 → 渲染 → 保存 SVG。"""
    if width is None:
        w = node.style.get("width")
        width = float(w) if isinstance(w, (int, float)) else 800.0
    node.layout(available_width=width) if hasattr(node, 'layout') else None
    renderer = Renderer()
    path = OUTPUT_DIR / filename
    renderer.render(node, str(path))
    print(f"  ✓ {filename}")
    return path


def heading(title: str):
    """打印章节标题。"""
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# =========================================================================
# Demo 1：CSS 值解析器
# =========================================================================

def demo_01_value_parser():
    heading("Demo 1: CSS 值解析器")

    examples = [
        ("200px",  {}),
        ("50%",    {"reference_length": 400}),
        ("2em",    {"font_size": 16}),
        ("1.5fr",  {}),
        ("12pt",   {}),
        ("auto",   {}),
        ("min-content", {}),
        ("#ff0000",     {}),
        ("#f00",        {}),
        ("red",         {}),
        ("rgb(0, 128, 255)", {}),
        ("rgba(0, 0, 0, 0.5)", {}),
        ("center",      {}),
        ("bold",        {}),
        ("row dense",   {}),
    ]

    for raw, kwargs in examples:
        result = parse_value(raw, **kwargs)
        print(f"  parse_value({raw!r:25s}) → {result!r}")


# =========================================================================
# Demo 2：简写展开
# =========================================================================

def demo_02_shorthand():
    heading("Demo 2: 简写属性展开")

    from latticesvg.style.parser import expand_shorthand

    cases = [
        ("margin",  "10px"),
        ("margin",  "10px 20px"),
        ("margin",  "1px 2px 3px 4px"),
        ("padding", "15px"),
        ("gap",     "10px"),
        ("gap",     "10px 20px"),
    ]

    for prop, val in cases:
        result = expand_shorthand(prop, val)
        print(f"  {prop}: {val!r:20s} → {result}")


# =========================================================================
# Demo 3：ComputedStyle & 继承
# =========================================================================

def demo_03_computed_style():
    heading("Demo 3: ComputedStyle 与属性继承")

    parent = ComputedStyle({
        "font-size": "24px",
        "color": "#ff0000",
        "width": "600px",
    })
    child = ComputedStyle({"font-size": "14px"}, parent_style=parent)

    print(f"  父节点 font-size  = {parent.get('font-size')}")
    print(f"  父节点 color      = {parent.get('color')}")
    print(f"  父节点 width      = {parent.get('width')}")
    print(f"  子节点 font-size  = {child.get('font-size')}  ← 覆盖")
    print(f"  子节点 color      = {child.get('color')}  ← 继承")
    print(f"  子节点 width      = {child.get('width')}     ← 不继承，默认 auto")

    s = ComputedStyle({"padding": "10px 20px"})
    print(f"  padding shorthand → T={s.padding_top} R={s.padding_right} "
          f"B={s.padding_bottom} L={s.padding_left}")
    print(f"  padding_horizontal = {s.padding_horizontal}")


# =========================================================================
# Demo 4：固定列 Grid
# =========================================================================

def demo_04_fixed_grid():
    heading("Demo 4: 固定列宽 Grid")

    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
    grid = GridContainer(style={
        "width": "600px",
        "padding": "15px",
        "background-color": "#ecf0f1",
        "grid-template-columns": ["150px", "150px", "150px"],
        "grid-template-rows": ["60px", "60px"],
        "gap": "15px",
    })

    for i, color in enumerate(colors):
        grid.add(ColorBox(
            width=150, height=60,
            **{"background-color": color}
        ))

    save(grid, "04_fixed_grid.svg", 600)


# =========================================================================
# Demo 5：fr 弹性列
# =========================================================================

def demo_05_fr_grid():
    heading("Demo 5: fr 弹性列分配")

    grid = GridContainer(style={
        "width": "700px",
        "padding": "15px",
        "background-color": "#ecf0f1",
        "grid-template-columns": ["1fr", "2fr", "1fr"],
        "gap": "10px",
    })

    labels_colors = [
        ("1fr", "#e74c3c"),
        ("2fr", "#3498db"),
        ("1fr", "#2ecc71"),
    ]
    for label, color in labels_colors:
        grid.add(ColorBox(
            width=50, height=60,
            **{"background-color": color}
        ))

    save(grid, "05_fr_grid.svg", 700)


# =========================================================================
# Demo 6：混合 fixed + fr
# =========================================================================

def demo_06_mixed_tracks():
    heading("Demo 6: 混合 fixed + fr 轨道")

    grid = GridContainer(style={
        "width": "800px",
        "padding": "10px",
        "background-color": "#f5f5f5",
        "grid-template-columns": ["200px", "1fr", "150px"],
        "gap": "10px",
    })

    items = [
        ("sidebar 200px", "#8e44ad"),
        ("main 1fr",      "#2980b9"),
        ("aside 150px",   "#27ae60"),
    ]
    for label, color in items:
        grid.add(ColorBox(
            width=50, height=80,
            **{"background-color": color}
        ))

    save(grid, "06_mixed_tracks.svg", 800)


# =========================================================================
# Demo 7：自动放置
# =========================================================================

def demo_07_auto_placement():
    heading("Demo 7: 自动放置（grid-auto-flow: row）")

    grid = GridContainer(style={
        "width": "500px",
        "padding": "10px",
        "background-color": "#fdfefe",
        "grid-template-columns": ["1fr", "1fr", "1fr", "1fr"],
        "gap": "8px",
    })

    colors = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
        "#9b59b6", "#1abc9c", "#e67e22", "#34495e",
    ]
    for color in colors:
        grid.add(ColorBox(
            width=50, height=50,
            **{"background-color": color}
        ))

    save(grid, "07_auto_placement.svg", 500)


# =========================================================================
# Demo 8：跨列 / 跨行
# =========================================================================

def demo_08_spanning():
    heading("Demo 8: 跨列与跨行")

    grid = GridContainer(style={
        "width": "500px",
        "padding": "8px",
        "background-color": "#fdfefe",
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "grid-template-rows": ["80px", "80px", "80px"],
        "gap": "8px",
    })

    # 跨 2 列
    grid.add(ColorBox(50, 80, **{"background-color": "#e74c3c"}),
             row=1, col=1, col_span=2)
    # 跨 2 行
    grid.add(ColorBox(50, 80, **{"background-color": "#3498db"}),
             row=1, col=3, row_span=2)
    # 跨 2 行
    grid.add(ColorBox(50, 80, **{"background-color": "#2ecc71"}),
             row=2, col=1, row_span=2)
    # 普通
    grid.add(ColorBox(50, 80, **{"background-color": "#f39c12"}),
             row=2, col=2)
    # 跨 2 列
    grid.add(ColorBox(50, 80, **{"background-color": "#1abc9c"}),
             row=3, col=2, col_span=2)

    save(grid, "08_spanning.svg", 500)


# =========================================================================
# Demo 9：对齐方式
# =========================================================================

def demo_09_alignment():
    heading("Demo 9: justify-self / align-self 对齐")

    grid = GridContainer(style={
        "width": "600px",
        "padding": "10px",
        "background-color": "#f0f0f0",
        "grid-template-columns": ["200px", "200px", "200px"],
        "grid-template-rows": ["120px", "120px"],
        "gap": "0px",
        "border-width": "1px",
        "border-color": "#cccccc",
    })

    alignments = [
        ("start",  "start",  "#e74c3c"),
        ("center", "center", "#3498db"),
        ("end",    "end",    "#2ecc71"),
        ("start",  "end",    "#f39c12"),
        ("center", "start",  "#9b59b6"),
        ("end",    "center", "#e67e22"),
    ]

    for justify, align, color in alignments:
        box = ColorBox(60, 40, **{
            "background-color": color,
            "justify-self": justify,
            "align-self": align,
        })
        grid.add(box)

    save(grid, "09_alignment.svg", 600)


# =========================================================================
# Demo 10：嵌套 Grid
# =========================================================================

def demo_10_nested_grid():
    heading("Demo 10: 嵌套 Grid")

    outer = GridContainer(style={
        "width": "700px",
        "padding": "15px",
        "background-color": "#ecf0f1",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "15px",
    })

    # 左侧：纯色块
    outer.add(ColorBox(50, 120, **{"background-color": "#2c3e50"}),
              row=1, col=1)

    # 右侧：嵌套 2×2 子网格
    inner = GridContainer(style={
        "grid-template-columns": ["1fr", "1fr"],
        "grid-template-rows": ["55px", "55px"],
        "gap": "10px",
        "background-color": "#bdc3c7",
        "padding": "5px",
    })
    inner_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
    for color in inner_colors:
        inner.add(ColorBox(50, 55, **{"background-color": color}))

    outer.add(inner, row=1, col=2)

    save(outer, "10_nested_grid.svg", 700)


# =========================================================================
# Demo 11：Padding & Border
# =========================================================================

def demo_11_box_model():
    heading("Demo 11: Padding 与 Border 盒模型")

    grid = GridContainer(style={
        "width": "500px",
        "padding": "20px",
        "background-color": "#fdfefe",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "20px",
        "border-width": "3px",
        "border-color": "#2c3e50",
    })

    # 有 padding 的色块
    grid.add(ColorBox(50, 80, **{
        "background-color": "#e8daef",
        "padding": "15px",
        "border-width": "2px",
        "border-color": "#8e44ad",
    }))

    grid.add(ColorBox(50, 80, **{
        "background-color": "#d5f5e3",
        "padding": "10px",
        "border-width": "1px",
        "border-color": "#27ae60",
    }))

    save(grid, "11_box_model.svg", 500)


# =========================================================================
# Demo 12：TextNode 基本排版
# =========================================================================

def demo_12_text_basic():
    heading("Demo 12: TextNode 文本排版")

    grid = GridContainer(style={
        "width": "600px",
        "padding": "20px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "12px",
    })

    # 标题
    grid.add(TextNode("LatticeSVG 文本排版演示", style={
        "font-size": "28px",
        "font-weight": "bold",
        "color": "#2c3e50",
        "text-align": "center",
    }))

    # 正文段落
    grid.add(TextNode(
        "LatticeSVG 是一个基于 CSS Grid 的矢量布局引擎。它使用 FreeType "
        "进行精确的字形测量，支持自动换行、多种对齐方式和丰富的排版控制。"
        "所有样式属性名称与 CSS 标准保持一致，降低学习成本。",
        style={
            "font-size": "15px",
            "color": "#333333",
            "line-height": "1.6",
        },
    ))

    # 右对齐
    grid.add(TextNode("—— 右对齐文本示例", style={
        "font-size": "14px",
        "color": "#7f8c8d",
        "text-align": "right",
    }))

    save(grid, "12_text_basic.svg", 600)


# =========================================================================
# Demo 13：TextNode white-space 模式
# =========================================================================

def demo_13_text_whitespace():
    heading("Demo 13: TextNode white-space 模式")

    grid = GridContainer(style={
        "width": "600px",
        "padding": "20px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "15px",
    })

    # normal — 折行
    grid.add(TextNode(
        "white-space: normal — 这段文字会自动按照可用宽度折行。"
        "超出容器宽度的内容会被拆分到下一行显示。",
        style={"font-size": "14px", "color": "#2c3e50"},
    ))

    # pre — 保留换行
    grid.add(TextNode(
        "white-space: pre\n  保留换行符\n  和前导空格",
        style={
            "font-size": "14px",
            "color": "#8e44ad",
            "white-space": "pre",
            "background-color": "#f8f9fa",
        },
    ))

    # nowrap — 不折行
    grid.add(TextNode(
        "white-space: nowrap — 这段文字不会折行，即使超出容器宽度也保持单行。"
        "在正常模式下这段文字应该会换行，但 nowrap 让它保持在一行中直到结束。",
        style={
            "font-size": "14px",
            "color": "#e74c3c",
            "white-space": "nowrap",
        },
    ))

    save(grid, "13_text_whitespace.svg", 600)


# =========================================================================
# Demo 14：SVGNode 嵌入外部 SVG
# =========================================================================

def demo_14_svg_node():
    heading("Demo 14: SVGNode 嵌入 SVG 内容")

    # 内联创建一个简单 SVG 图形
    circle_svg = '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="45" fill="#3498db" opacity="0.8"/>
  <circle cx="50" cy="50" r="25" fill="#2ecc71" opacity="0.9"/>
  <circle cx="50" cy="50" r="10" fill="#e74c3c"/>
</svg>'''

    star_svg = '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <polygon points="50,5 61,35 95,35 68,57 79,91 50,70 21,91 32,57 5,35 39,35"
           fill="#f39c12" stroke="#e67e22" stroke-width="2"/>
</svg>'''

    grid = GridContainer(style={
        "width": "500px",
        "padding": "20px",
        "background-color": "#fdfefe",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "20px",
    })

    grid.add(SVGNode(circle_svg, style={
        "background-color": "#eaf2f8",
        "padding": "10px",
    }), row=1, col=1)

    grid.add(SVGNode(star_svg, style={
        "background-color": "#fef9e7",
        "padding": "10px",
    }), row=1, col=2)

    save(grid, "14_svg_node.svg", 500)


# =========================================================================
# Demo 15：MplNode（Matplotlib 图表嵌入）
# =========================================================================

def demo_15_mpl_node():
    heading("Demo 15: MplNode Matplotlib 图表嵌入")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  ⚠ matplotlib/numpy 未安装，跳过此演示")
        return

    # 创建两个图表
    fig1, ax1 = plt.subplots(figsize=(4, 3), dpi=100)
    x = np.linspace(0, 2 * np.pi, 100)
    ax1.plot(x, np.sin(x), color="#e74c3c", linewidth=2, label="sin(x)")
    ax1.plot(x, np.cos(x), color="#3498db", linewidth=2, label="cos(x)")
    ax1.set_title("Trigonometric Functions")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    fig2, ax2 = plt.subplots(figsize=(4, 3), dpi=100)
    categories = ["A", "B", "C", "D"]
    values = [23, 45, 56, 78]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
    ax2.bar(categories, values, color=colors)
    ax2.set_title("Bar Chart")
    ax2.set_ylabel("Value")

    grid = GridContainer(style={
        "width": "800px",
        "padding": "15px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "15px",
    })

    grid.add(MplNode(fig1), row=1, col=1)
    grid.add(MplNode(fig2), row=1, col=2)

    save(grid, "15_mpl_node.svg", 800)

    plt.close("all")


# =========================================================================
# Demo 16：内置样式模板
# =========================================================================

def demo_16_templates():
    heading("Demo 16: 内置样式模板")

    print(f"  可用模板列表 ({len(templates.ALL_TEMPLATES)} 个):")
    for name, tmpl in templates.ALL_TEMPLATES.items():
        keys = ", ".join(tmpl.keys())
        print(f"    {name:20s} → {keys}")

    # 使用模板构建页面
    grid = GridContainer(style={
        **templates.REPORT_PAGE,
        "width": "600px",
    })

    grid.add(TextNode("使用 TITLE 模板", style=templates.TITLE))
    grid.add(TextNode("使用 SUBTITLE 模板", style=templates.SUBTITLE))
    grid.add(TextNode(
        "使用 PARAGRAPH 模板。这是一段正文示例，展示了段落的默认"
        "字号、行高和颜色配置。模板可以通过字典合并进行自定义。",
        style=templates.PARAGRAPH,
    ))
    grid.add(TextNode("使用 CAPTION 模板 — 图表说明文字", style=templates.CAPTION))
    grid.add(TextNode("CODE 模板\n  def hello():\n    print('world')", style=templates.CODE))

    save(grid, "16_templates.svg", 600)


# =========================================================================
# Demo 17：PNG 输出
# =========================================================================

def demo_17_png_output():
    heading("Demo 17: PNG 输出（cairosvg）")

    try:
        import cairosvg  # noqa: F401
    except ImportError:
        print("  ⚠ cairosvg 未安装，跳过 PNG 输出演示")
        return

    grid = GridContainer(style={
        "width": "400px",
        "padding": "20px",
        "background-color": "#2c3e50",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "10px",
    })
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
    for c in colors:
        grid.add(ColorBox(50, 50, **{"background-color": c}))

    grid.layout(available_width=400)
    renderer = Renderer()

    png_path = OUTPUT_DIR / "17_png_output.png"
    renderer.render_png(grid, str(png_path), scale=2)
    size = png_path.stat().st_size
    print(f"  ✓ 17_png_output.png  ({size:,} bytes, scale=2x)")


# =========================================================================
# Demo 18：综合报告页面
# =========================================================================

def demo_18_full_report():
    heading("Demo 18: 综合报告页面")

    page = GridContainer(style={
        "width": "800px",
        "padding": "30px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "16px",
    })

    # ── Header ──
    header = GridContainer(style={
        **templates.HEADER,
        "grid-template-columns": ["1fr"],
    })
    header.add(TextNode("LatticeSVG 综合功能报告", style={
        "font-size": "22px",
        "font-weight": "bold",
        "color": "#ffffff",
        "text-align": "center",
    }))
    page.add(header)

    # ── 简介 ──
    page.add(TextNode(
        "本报告由 LatticeSVG 布局引擎自动生成，展示了 CSS Grid 布局、"
        "文本排版、嵌入 SVG 图形等功能的综合效果。",
        style=templates.PARAGRAPH,
    ))

    # ── 两列区域 ──
    two_col = GridContainer(style={
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "20px",
    })

    # 左列：文字
    left = GridContainer(style={
        "grid-template-columns": ["1fr"],
        "gap": "8px",
    })
    left.add(TextNode("核心特性", style=templates.H2))
    left.add(TextNode(
        "• CSS Grid Level 1 布局算法\n"
        "• FreeType 字形精确测量\n"
        "• drawsvg 矢量渲染\n"
        "• 嵌套网格支持\n"
        "• 17 种内置样式模板",
        style={**templates.PARAGRAPH, "white-space": "pre"},
    ))

    two_col.add(left, row=1, col=1)

    # 右列：嵌入 SVG 图形
    chart_svg = '''<svg viewBox="0 0 200 150" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="100" width="30" height="40" fill="#e74c3c" rx="3"/>
  <rect x="50" y="60"  width="30" height="80" fill="#3498db" rx="3"/>
  <rect x="90" y="30"  width="30" height="110" fill="#2ecc71" rx="3"/>
  <rect x="130" y="10" width="30" height="130" fill="#f39c12" rx="3"/>
  <line x1="5" y1="145" x2="195" y2="145" stroke="#bdc3c7" stroke-width="1"/>
</svg>'''
    right = GridContainer(style={
        "grid-template-columns": ["1fr"],
        "gap": "5px",
        "background-color": "#f8f9fa",
        "padding": "10px",
    })
    right.add(SVGNode(chart_svg, style={"padding": "5px"}))
    right.add(TextNode("图表：功能覆盖率", style=templates.CAPTION))
    two_col.add(right, row=1, col=2)

    page.add(two_col)

    # ── 色卡 ──
    page.add(TextNode("主题色板", style=templates.H3))
    palette = GridContainer(style={
        "grid-template-columns": ["1fr", "1fr", "1fr", "1fr", "1fr", "1fr"],
        "gap": "8px",
    })
    palette_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
    for c in palette_colors:
        palette.add(ColorBox(30, 40, **{"background-color": c}))
    page.add(palette)

    # ── Footer ──
    footer = GridContainer(style={
        **templates.FOOTER,
        "grid-template-columns": ["1fr"],
    })
    footer.add(TextNode("Generated by LatticeSVG v0.1.0", style={
        "font-size": "11px",
        "color": "#bdc3c7",
        "text-align": "center",
    }))
    page.add(footer)

    save(page, "18_full_report.svg", 800)


# =========================================================================
# Demo 19：布局信息打印
# =========================================================================

def demo_19_layout_inspection():
    heading("Demo 19: 布局结果检查")

    grid = GridContainer(style={
        "width": "400px",
        "padding": "10px",
        "grid-template-columns": ["100px", "1fr"],
        "gap": "10px",
    })

    a = ColorBox(100, 40, **{"background-color": "#e74c3c"})
    b = ColorBox(50, 40, **{"background-color": "#3498db"})
    grid.add(a, row=1, col=1)
    grid.add(b, row=1, col=2)
    grid.layout(available_width=400)

    print(f"  Grid container:")
    print(f"    border_box  = {grid.border_box}")
    print(f"    padding_box = {grid.padding_box}")
    print(f"    content_box = {grid.content_box}")
    print(f"  Child A (100px fixed):")
    print(f"    border_box  = {a.border_box}")
    print(f"  Child B (1fr):")
    print(f"    border_box  = {b.border_box}")
    print(f"    → content width = {b.content_box.width:.1f}px "
          f"(= 400 - 20pad - 100col1 - 10gap = 270)")


# =========================================================================
# Demo 20：中英文混合字体
# =========================================================================

def demo_20_mixed_fonts():
    heading("Demo 20: 中英文混合字体（字体回退链）")

    grid = GridContainer(style={
        "width": "600px",
        "padding": "20px",
        "grid-template-columns": ["1fr"],
        "gap": "16px",
        "background-color": "#fdf6e3",
    })

    # 标题 —— Times New Roman + SimSun 混排
    title = TextNode(
        "LatticeSVG：CSS Grid Layout Engine for SVG",
        style={
            "font-family": "Times New Roman, SimSun, serif",
            "font-size": "24px",
            "color": "#073642",
            "text-align": "center",
            "padding": "12px",
            "background-color": "#eee8d5",
        },
    )
    grid.add(title, row=1, col=1)

    # 正文 —— 中英文混排段落
    body = TextNode(
        "字体回退链（Font Fallback Chain）是一种常见的排版策略。"
        "当主字体（Primary Font）缺少某个字符的字形（Glyph）时，"
        "引擎会自动尝试回退链中的下一个字体。"
        "例如：英文使用 Times New Roman，中文使用 SimSun（宋体）。",
        style={
            "font-family": "Times New Roman, SimSun, serif",
            "font-size": "16px",
            "color": "#586e75",
            "padding": "10px",
            "background-color": "#ffffff",
            "border": "1px solid #93a1a1",
        },
    )
    grid.add(body, row=2, col=1)

    # 技术说明
    tech = TextNode(
        "实现原理：FontManager.glyph_metrics() 接受字体路径列表，"
        "对每个字符调用 FreeType 的 get_char_index() 判断字形覆盖，"
        "选择第一个能提供该字符字形的字体进行度量。"
        "SVG 输出使用 font-family 属性列出完整回退链。",
        style={
            "font-family": "Times New Roman, SimSun, serif",
            "font-size": "14px",
            "color": "#657b83",
            "padding": "10px",
            "background-color": "#fefbf1",
        },
    )
    grid.add(tech, row=3, col=1)

    save(grid, "20_mixed_fonts.svg", 600)
    print("  → 标题与正文使用 Times New Roman + SimSun 混合渲染")


# =========================================================================
# Demo 21：overflow-wrap: break-word
# =========================================================================

def demo_21_overflow_wrap():
    heading("Demo 21: overflow-wrap: break-word")

    grid = GridContainer(style={
        "width": "400px",
        "padding": "16px",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "12px",
        "background-color": "#f5f5f5",
    })

    # 左列：默认 normal — 长单词不断行
    left = TextNode(
        "默认模式（normal）：当主字体（PrimaryFont）缺少某个字符的字形（Glyph）时，"
        "Pneumonoultramicroscopicsilicovolcanoconiosis 不会被截断。",
        style={
            "font-size": "14px",
            "padding": "8px",
            "background-color": "#ffffff",
            "border": "1px solid #ccc",
        },
    )
    grid.add(left, row=1, col=1)

    # 右列：break-word — 长单词会在行尾断开
    right = TextNode(
        "断词模式（break-word）：当主字体（PrimaryFont）缺少某个字符的字形（Glyph）时，"
        "Pneumonoultramicroscopicsilicovolcanoconiosis 会被截断。",
        style={
            "font-size": "14px",
            "padding": "8px",
            "background-color": "#ffffff",
            "border": "1px solid #2ecc71",
            "overflow-wrap": "break-word",
        },
    )
    grid.add(right, row=1, col=2)

    save(grid, "21_overflow_wrap.svg", 400)
    print("  → 左列：长单词溢出不断行 / 右列：overflow-wrap: break-word 自动断词")


# =========================================================================
# Demo 22：图像生成模型 Gallery
# =========================================================================

def demo_22_image_gallery():
    heading("Demo 22: 图像生成模型 Gallery")
    import colorsys

    IMG_H = 60                 # 统一展示高度
    FONT = "Times New Roman, SimSun, serif"

    # 10 张图片的原始分辨率 (w, h)
    specs = [
        (512, 512),   (512, 512),       # img 1-2  : 1:1
        (1024, 1024), (1024, 1024),      # img 3-4  : 1:1
        (512, 384),   (512, 384),        # img 5-6  : 4:3
        (786, 1024),  (786, 1024),       # img 7-8  : ≈3:4
        (1920, 1080), (1920, 1080),      # img 9-10 : 16:9
    ]
    # 等高缩放后的展示宽度
    dw = [round(IMG_H * w / h, 1) for w, h in specs]

    NAME_W = 90
    GAP = 4
    PAD = 12
    total_w = NAME_W + sum(dw) + GAP * 10 + PAD * 2
    cols = [f"{NAME_W}px"] + [f"{w}px" for w in dw]

    grid = GridContainer(style={
        "width": f"{total_w}px",
        "padding": f"{PAD}px",
        "grid-template-columns": cols,
        "gap": f"{GAP}px",
        "background-color": "#1a1a2e",
    })

    # ── 第 1 行：表头 ──
    grid.add(TextNode("模型名称", style={
        "font-family": FONT, "font-size": "12px", "font-weight": "bold",
        "color": "#e8e8e8", "text-align": "center",
        "padding": "8px 4px", "background-color": "#16213e",
        "display": "flex", "align-items": "center",
    }), row=1, col=1)

    grid.add(TextNode("生成图片对比", style={
        "font-family": FONT, "font-size": "14px", "font-weight": "bold",
        "color": "#ffffff", "text-align": "center",
        "padding": "8px", "background-color": "#0f3460",
        "display": "flex", "align-items": "center",
    }), row=1, col=2, col_span=10)

    # ── 第 2–10 行：模型图片 ──
    models = [
        "DALL\u00b7E 3", "Midjourney v6", "SD XL 1.0",
        "Flux.1 Pro", "Imagen 3", "Adobe Firefly",
        "Kandinsky 3", "\u901a\u4e49\u4e07\u76f8", "Ideogram 2",
    ]

    for i, name in enumerate(models):
        r = i + 2
        grid.add(TextNode(name, style={
            "font-family": FONT, "font-size": "10px",
            "color": "#d0d0d0", "text-align": "center",
            "padding": "4px 2px", "background-color": "#16213e",
            "display": "flex", "align-items": "center",
        }), row=r, col=1)

        hue = i / len(models)
        for j in range(10):
            sat = 0.50 + (j % 5) * 0.08
            lit = 0.32 + (j % 4) * 0.08
            rgb = colorsys.hls_to_rgb(hue, lit, sat)
            color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
            grid.add(
                ColorBox(dw[j], IMG_H, **{"background-color": color}),
                row=r, col=j + 2,
            )

    # ── 第 11 行：图片参数 ──
    grid.add(TextNode("图片参数：", style={
        "font-family": FONT, "font-size": "10px", "font-weight": "bold",
        "color": "#e0e0e0", "text-align": "center",
        "padding": "6px 2px", "background-color": "#16213e",
        "display": "flex", "align-items": "center",
    }), row=11, col=1)

    param_info = [
        ("1girl, solo, upper body, looking at viewer, smile",   "512\u00d7512",   "1:1"),
        ("1boy, playing guitar, standing, outdoors",            "512\u00d7512",   "1:1"),
        ("landscape, mountains, river, sunset, vibrant colors", "1024\u00d71024", "1:1"),
        ("cityscape, night, neon lights, rainy, reflections",   "1024\u00d71024", "1:1"),
        ("cute cat, sitting, big eyes, colorful background",    "512\u00d7384",   "4:3"),
        ("futuristic robot, metallic, glowing eyes, city",      "512\u00d7384",   "4:3"),
        ("fantasy castle, floating islands, bright sky",        "786\u00d71024",  "\u22483:4"),
        ("portrait of a woman, detailed, soft lighting",        "786\u00d71024",  "\u22483:4"),
        ("space scene, planets, stars, nebula, vibrant colors", "1920\u00d71080", "16:9"),
        ("vintage car, driving on road, countryside, sunny",    "1920\u00d71080", "16:9"),
    ]
    for j, (prompt, res, ratio) in enumerate(param_info):
        grid.add(TextNode(f"{prompt}\n{res}\n{ratio}", style={
            "font-family": FONT, "font-size": "8px",
            "color": "#b0b0b0", "text-align": "center",
            "padding": "4px 2px", "background-color": "#0f3460",
            "white-space": "pre-wrap",
            "display": "flex", "align-items": "center",
        }), row=11, col=j + 2)

    save(grid, "22_image_gallery.svg", total_w)
    print(f"  \u2192 9 \u4e2a\u6a21\u578b \u00d7 10 \u5f20\u56fe\u7247\u5bf9\u6bd4\uff0c\u5bbd {total_w:.0f}px")


# =========================================================================
# Main
# =========================================================================

def main():
    print("=" * 60)
    print("  LatticeSVG 功能展示")
    print("=" * 60)

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"\n输出目录: {OUTPUT_DIR}")

    # 纯计算演示（无文件输出）
    demo_01_value_parser()
    demo_02_shorthand()
    demo_03_computed_style()

    # SVG 文件输出演示
    demo_04_fixed_grid()
    demo_05_fr_grid()
    demo_06_mixed_tracks()
    demo_07_auto_placement()
    demo_08_spanning()
    demo_09_alignment()
    demo_10_nested_grid()
    demo_11_box_model()
    demo_12_text_basic()
    demo_13_text_whitespace()
    demo_14_svg_node()
    demo_15_mpl_node()
    demo_16_templates()
    demo_17_png_output()
    demo_18_full_report()
    demo_19_layout_inspection()
    demo_20_mixed_fonts()
    demo_21_overflow_wrap()
    demo_22_image_gallery()

    # 汇总
    svg_count = len(list(OUTPUT_DIR.glob("*.svg")))
    png_count = len(list(OUTPUT_DIR.glob("*.png")))
    print(f"\n{'='*60}")
    print(f"  完成！共生成 {svg_count} 个 SVG + {png_count} 个 PNG")
    print(f"  输出目录: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
