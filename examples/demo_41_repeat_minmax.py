# =========================================================================
# Demo 41：repeat() / minmax() 轨道函数
# =========================================================================
#
# 展示 CSS Grid 的 repeat() 和 minmax() 轨道定义函数。
# - repeat(n, pattern)：重复展开轨道模式
# - minmax(min, max)：定义轨道尺寸的最小 / 最大范围
# - 两者可组合使用：repeat(3, minmax(100px, 1fr))
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

COLORS = [
    "#e74c3c", "#3498db", "#2ecc71",
    "#f39c12", "#9b59b6", "#1abc9c",
    "#e67e22", "#34495e", "#c0392b",
]


def _cell(text: str, bg: str) -> TextNode:
    """带文字标签的彩色单元格。"""
    return TextNode(text, style={
        "font-size": "13px", "color": "#fff", "font-weight": "bold",
        "text-align": "center", "padding": "10px 6px",
        "background-color": bg,
        "border-radius": "4px",
    })


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


def demo_41_repeat_minmax():
    heading("Demo 41: repeat() / minmax() 轨道函数")

    root = GridContainer(style={
        "width": "560px",
        "padding": "20px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "14px",
    })

    root.add(TextNode(
        "repeat() / minmax() 轨道函数",
        style={
            "font-size": "22px", "font-weight": "bold",
            "color": "#2c3e50", "text-align": "center",
            "padding-bottom": "10px",
        },
    ))

    # ---- Section 1: repeat(3, 1fr) ----
    root.add(_section_title("① repeat(3, 1fr)"))
    root.add(_section_desc('等价于 "1fr 1fr 1fr"，三列等宽'))

    grid1 = GridContainer(style={
        "grid-template-columns": "repeat(3, 1fr)",
        "gap": "8px",
    })
    for i in range(3):
        grid1.add(_cell(f"1fr ({i+1})", COLORS[i]))
    root.add(grid1)

    # ---- Section 2: repeat(2, 100px 1fr) ----
    root.add(_section_title("② repeat(2, 100px 1fr)"))
    root.add(_section_desc('展开为 "100px 1fr 100px 1fr"'))

    grid2 = GridContainer(style={
        "grid-template-columns": "repeat(2, 100px 1fr)",
        "gap": "8px",
    })
    labels2 = ["100px", "1fr", "100px", "1fr"]
    for i in range(4):
        grid2.add(_cell(labels2[i], COLORS[i + 3]))
    root.add(grid2)

    # ---- Section 3: minmax(100px, 300px) 1fr ----
    root.add(_section_title("③ minmax(100px, 300px) 1fr"))
    root.add(_section_desc("第一列在 100~300px 范围内弹性伸缩"))

    grid3 = GridContainer(style={
        "grid-template-columns": "minmax(100px, 300px) 1fr",
        "gap": "8px",
    })
    grid3.add(_cell("minmax\n(100px, 300px)", "#e74c3c"))
    grid3.add(_cell("1fr", "#3498db"))
    root.add(grid3)

    # ---- Section 4: repeat(3, minmax(80px, 1fr)) ----
    root.add(_section_title("④ repeat(3, minmax(80px, 1fr))"))
    root.add(_section_desc("三列均分，每列最小 80px"))

    grid4 = GridContainer(style={
        "grid-template-columns": "repeat(3, minmax(80px, 1fr))",
        "gap": "8px",
    })
    for i in range(3):
        grid4.add(_cell(f"minmax\n(80px, 1fr)", COLORS[i + 6]))
    root.add(grid4)

    # ---- Section 5: 综合对比 ----
    root.add(_section_title("⑤ 综合：minmax + 固定 + fr"))
    root.add(_section_desc('"120px minmax(80px, 200px) 1fr" — 三种轨道并列'))

    grid5 = GridContainer(style={
        "grid-template-columns": "120px minmax(80px, 200px) 1fr",
        "gap": "8px",
    })
    grid5.add(_cell("120px\n固定", "#8e44ad"))
    grid5.add(_cell("minmax\n(80px, 200px)", "#16a085"))
    grid5.add(_cell("1fr\n弹性", "#d35400"))
    root.add(grid5)

    save(root, "41_repeat_minmax.svg")


if __name__ == "__main__":
    demo_41_repeat_minmax()
