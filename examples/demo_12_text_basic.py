# =========================================================================
# Demo 12：TextNode 基本排版
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

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
    
if __name__ == "__main__":
    demo_12_text_basic()