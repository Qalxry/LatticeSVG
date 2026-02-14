# =========================================================================
# Demo 28：P1-2 border-style dashed/dotted
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

def demo_28_border_style():
    heading("Demo 28: border-style dashed / dotted")

    grid = GridContainer(style={
        "width": "700px",
        "padding": "20px",
        "background-color": "#f8f9fa",
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "grid-template-rows": ["auto", "auto"],
        "gap": "16px",
    })

    # Row 1: solid / dashed / dotted（无圆角，独立边线渲染）
    for i, (bs, label) in enumerate([
        ("solid", "solid 边框"),
        ("dashed", "dashed 虚线"),
        ("dotted", "dotted 点线"),
    ]):
        box = GridContainer(style={
            "background-color": "#ffffff",
            "border": f"2px {bs} #e74c3c",
            "padding": "20px",
            "grid-template-columns": ["1fr"],
        })
        box.add(TextNode(label, style={
            "font-size": "14px", "color": "#2c3e50", "text-align": "center",
        }), row=1, col=1)
        grid.add(box, row=1, col=i + 1)

    # Row 2: 不同粗细的虚线
    for i, (bw, label) in enumerate([
        ("1px", "dashed 1px"),
        ("3px", "dashed 3px"),
        ("5px", "dashed 5px"),
    ]):
        box = GridContainer(style={
            "background-color": "#fff9e6",
            "border": f"{bw} dashed #f39c12",
            "padding": "20px",
            "grid-template-columns": ["1fr"],
        })
        box.add(TextNode(label, style={
            "font-size": "14px", "color": "#2c3e50", "text-align": "center",
        }), row=1, col=1)
        grid.add(box, row=2, col=i + 1)

    grid.add(TextNode("✓ 预期：第一行三种边框样式对比；第二行虚线粗细递增", style={
        "font-size": "12px", "color": "#2ecc71",
    }), row=3, col=1, col_span=3)

    save(grid, "28_border_style.svg")

if __name__ == "__main__":
    demo_28_border_style()