# =========================================================================
# Demo 13：TextNode white-space 模式
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

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
    
if __name__ == "__main__":
    demo_13_text_whitespace()