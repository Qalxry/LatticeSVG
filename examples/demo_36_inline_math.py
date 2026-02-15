# =========================================================================
# Demo 36：Inline Math — 行内数学公式
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save


def demo_36_inline_math():
    heading("Demo 36: Inline Math 行内公式")

    grid = GridContainer(style={
        "width": "650px",
        "padding": "24px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "16px",
    })

    grid.add(TextNode("行内数学公式演示", style={
        "font-size": "24px",
        "font-weight": "bold",
        "color": "#2c3e50",
        "text-align": "center",
    }))

    # HTML markup with <math> tags
    grid.add(TextNode(
        "爱因斯坦的质能方程 <math>E = mc^2</math> 是物理学中最著名的公式之一。",
        style={"font-size": "16px", "color": "#333", "line-height": "1.6"},
        markup="html",
    ))

    # Markdown markup with $ delimiters
    grid.add(TextNode(
        "勾股定理告诉我们 $a^2 + b^2 = c^2$，"
        "其中 $c$ 是斜边长度。",
        style={"font-size": "16px", "color": "#333", "line-height": "1.6"},
        markup="markdown",
    ))

    # Mixed text with math
    grid.add(TextNode(
        "对于圆，面积 $A = \\pi r^2$，周长 $C = 2\\pi r$。"
        "当 $r = 1$ 时，$A = \\pi \\approx 3.14159$。",
        style={"font-size": "15px", "color": "#333", "line-height": "1.6"},
        markup="markdown",
    ))

    # Complex inline formula
    grid.add(TextNode(
        "正态分布的概率密度函数为 "
        "$f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}$。",
        style={"font-size": "15px", "color": "#333", "line-height": "1.8"},
        markup="markdown",
    ))

    save(grid, "36_inline_math.svg")


if __name__ == "__main__":
    demo_36_inline_math()
