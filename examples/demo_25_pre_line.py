# =========================================================================
# Demo 25：white-space: pre-line
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

def demo_25_pre_line():
    heading("Demo 25: white-space: pre-line")

    grid = GridContainer(style={
        "width": "800px",
        "padding": "20px",
        "gap": "16px",
        "background-color": "#fafafa",
        "grid-template-columns": ["1fr"],
    })

    grid.add(TextNode("Demo 25: white-space: pre-line", style={
        "font-size": "18px", "font-weight": "bold", "color": "#333",
    }), row=1, col=1)

    compare = GridContainer(style={
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "gap": "12px",
    })

    sample_text = "第一行内容\n第二行内容   带多个空格\n第三行是一段比较长的文本用于测试自动折行是否在保留换行符的同时正常工作"

    # normal
    compare.add(TextNode("white-space: normal", style={
        "font-size": "12px", "font-weight": "bold", "color": "#e74c3c",
        "margin": "0 0 4px 0",
    }), row=1, col=1)
    compare.add(TextNode(sample_text, style={
        "font-size": "13px", "color": "#333",
        "white-space": "normal",
        "background-color": "#fff3f3",
        "padding": "10px",
        "border": "1px solid #e74c3c",
    }), row=2, col=1)
    compare.add(TextNode("折叠空白 + 折叠换行\n→ 全部连成一段", style={
        "font-size": "10px", "color": "#999", "white-space": "pre",
    }), row=3, col=1)

    # pre-line
    compare.add(TextNode("white-space: pre-line", style={
        "font-size": "12px", "font-weight": "bold", "color": "#27ae60",
        "margin": "0 0 4px 0",
    }), row=1, col=2)
    compare.add(TextNode(sample_text, style={
        "font-size": "13px", "color": "#333",
        "white-space": "pre-line",
        "background-color": "#f0fff0",
        "padding": "10px",
        "border": "1px solid #27ae60",
    }), row=2, col=2)
    compare.add(TextNode("折叠空白 + 保留换行\n→ \\n 处断行，空格折叠", style={
        "font-size": "10px", "color": "#999", "white-space": "pre",
    }), row=3, col=2)

    # pre
    compare.add(TextNode("white-space: pre", style={
        "font-size": "12px", "font-weight": "bold", "color": "#3498db",
        "margin": "0 0 4px 0",
    }), row=1, col=3)
    compare.add(TextNode(sample_text, style={
        "font-size": "13px", "color": "#333",
        "white-space": "pre",
        "background-color": "#f0f4ff",
        "padding": "10px",
        "border": "1px solid #3498db",
    }), row=2, col=3)
    compare.add(TextNode("保留空白 + 保留换行\n→ 完全保留原始格式", style={
        "font-size": "10px", "color": "#999", "white-space": "pre",
    }), row=3, col=3)

    grid.add(compare, row=2, col=1)

    grid.add(TextNode("✓ 预期：pre-line 列应在 \\n 处断行，但多余空格被折叠为一个；长行自动折行", style={
        "font-size": "12px", "color": "#27ae60",
    }), row=3, col=1)

    save(grid, "25_pre_line.svg")

if __name__ == "__main__":
    demo_25_pre_line()