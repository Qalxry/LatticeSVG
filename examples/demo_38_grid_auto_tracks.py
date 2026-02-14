# =========================================================================
# Demo 38：grid-auto-rows / grid-auto-columns
# =========================================================================
#
# 大量自动放置项目时，通过 grid-auto-rows / grid-auto-columns
# 控制隐式轨道的尺寸，而非使用默认的 auto。
# 输出为单个 SVG，使用嵌套 Grid 展示三个场景。
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save, ColorBox

COLORS = [
    "#e74c3c", "#3498db", "#2ecc71",
    "#f39c12", "#9b59b6", "#1abc9c",
    "#e67e22", "#34495e", "#c0392b",
]


def _section_title(title: str) -> TextNode:
    return TextNode(title, style={
        "font-size": "18px", "font-weight": "bold",
        "color": "#2c3e50", "padding": "4px 0",
    })


def _section_desc(text: str) -> TextNode:
    return TextNode(text, style={
        "font-size": "13px", "color": "#555", "line-height": "1.5",
        "padding-bottom": "4px",
    })


def demo_38_grid_auto_tracks():
    heading("Demo 38: grid-auto-rows / grid-auto-columns")

    root = GridContainer(style={
        "width": "500px",
        "padding": "20px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "14px",
    })

    root.add(TextNode(
        "通过 grid-auto-rows / grid-auto-columns 控制隐式轨道尺寸",
        style={
            "font-size": "22px", "font-weight": "bold",
            "color": "#2c3e50", "text-align": "center",
            "padding-bottom": "10px",
        },
    ))
    # ── 38a: grid-auto-rows: 80px ────────────────────────────────
    root.add(_section_title("① grid-auto-rows: 80px"))
    root.add(_section_desc(
        "3 列模板 + 9 个色块自动放置。未定义 grid-template-rows，"
        "所有隐式行由 grid-auto-rows 统一设为 80px。"
    ))

    grid_a = GridContainer(style={
        "padding": "10px",
        "background-color": "#f8f9fa",
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "grid-auto-rows": "80px",
        "gap": "8px",
    })
    for color in COLORS:
        grid_a.add(ColorBox(40, 30, **{"background-color": color}))
    root.add(grid_a)

    # ── 38b: grid-auto-columns: 120px ────────────────────────────
    root.add(_section_title("② grid-auto-columns: 120px + column flow"))
    root.add(_section_desc(
        "仅定义 2 行模板 (60px×2)，grid-auto-flow 设为 column。"
        "6 个色块纵向填充，隐式列宽由 grid-auto-columns 固定为 120px。"
    ))

    grid_b = GridContainer(style={
        "padding": "10px",
        "background-color": "#f8f9fa",
        "grid-template-rows": ["60px", "60px"],
        "grid-auto-flow": "column",
        "grid-auto-columns": "120px",
        "gap": "8px",
    })
    for color in COLORS[:6]:
        grid_b.add(ColorBox(40, 30, **{"background-color": color}))
    root.add(grid_b)

    # ── 38c: 默认 auto ──────────────────────────────────────────
    root.add(_section_title("③ 对比：默认 auto（无 grid-auto-rows）"))
    root.add(_section_desc(
        "不设 grid-auto-rows，各行高度由内容决定（取同行最大值）。"
        "默认 align-items:stretch 使同行 item 拉伸至行高。"
    ))

    grid_c = GridContainer(style={
        "padding": "10px",
        "background-color": "#f8f9fa",
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "gap": "8px",
    })
    heights = [30, 60, 40, 50, 25, 70]
    for color, h in zip(COLORS[:6], heights):
        grid_c.add(ColorBox(40, h, **{"background-color": color}))
    root.add(grid_c)

    save(root, "38_grid_auto_tracks.svg", 500)


if __name__ == "__main__":
    demo_38_grid_auto_tracks()
