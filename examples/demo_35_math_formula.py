# =========================================================================
# Demo 35：MathNode — LaTeX 数学公式独立节点
# =========================================================================

from latticesvg import GridContainer, TextNode, MathNode
from utils import heading, save


def demo_35_math_formula():
    heading("Demo 35: MathNode 数学公式")

    grid = GridContainer(style={
        "width": "700px",
        "padding": "24px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "20px",
    })

    grid.add(TextNode("LaTeX 数学公式渲染", style={
        "font-size": "24px",
        "font-weight": "bold",
        "color": "#2c3e50",
        "text-align": "center",
    }))

    # Simple equation
    grid.add(TextNode("欧拉公式：", style={
        "font-size": "14px", "color": "#666",
    }))
    grid.add(MathNode(
        r"e^{i\pi} + 1 = 0",
        style={"font-size": "24px", "padding": "8px"},
    ))

    # Integral
    grid.add(TextNode("高斯积分：", style={
        "font-size": "14px", "color": "#666",
    }))
    grid.add(MathNode(
        r"\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}",
        style={"font-size": "22px", "padding": "8px"},
    ))

    # Matrix
    grid.add(TextNode("矩阵：", style={
        "font-size": "14px", "color": "#666",
    }))
    grid.add(MathNode(
        r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}"
        r"\begin{pmatrix} x \\ y \end{pmatrix} = "
        r"\begin{pmatrix} ax+by \\ cx+dy \end{pmatrix}",
        style={"font-size": "20px", "padding": "8px"},
    ))

    # Sum
    grid.add(MathNode(
        r"\sum_{k=0}^{n} \binom{n}{k} x^k y^{n-k} = (x+y)^n",
        style={"font-size": "22px", "padding": "8px"},
    ))

    save(grid, "35_math_formula.svg", 700)


if __name__ == "__main__":
    demo_35_math_formula()
