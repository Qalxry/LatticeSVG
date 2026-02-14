# =========================================================================
# Demo 24：text-overflow: ellipsis 精度
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

def demo_24_ellipsis_precision():
    heading("Demo 24: text-overflow: ellipsis 精确截断")

    grid = GridContainer(style={
        "width": "800px",
        "padding": "20px",
        "gap": "16px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
    })

    grid.add(TextNode("Demo 24: text-overflow: ellipsis 精确截断", style={
        "font-size": "18px", "font-weight": "bold", "color": "#333",
    }), row=1, col=1)

    # 对比行 — 使用固定窄列 (300px) 确保文本必须溢出
    row = GridContainer(style={
        "grid-template-columns": ["80px", "300px"],
        "gap": "8px",
    })

    cases = [
        ("英文窄盒", "The quick brown fox jumps over the lazy dog and keeps running forever and ever"),
        ("中文窄盒", "这是一段很长的中文测试文本，用于验证省略号截断在中日韩字符下的精确度和边界表现如何"),
        ("中英混合", "Hello世界！This is a mixed中英文text for ellipsis精度测试，看看效果如何呢"),
        ("数字密集", "3.141592653589793238462643383279502884197169399375105820974944592307816"),
    ]

    for i, (label, text) in enumerate(cases):
        r = i * 2 + 1
        row.add(TextNode(label, style={
            "font-size": "12px", "font-weight": "bold", "color": "#555",
            "display": "flex", "align-items": "center",
        }), row=r, col=1)

        row.add(TextNode(text, style={
            "font-size": "14px", "color": "#333",
            "overflow": "hidden",
            "text-overflow": "ellipsis",
            "white-space": "nowrap",
            "background-color": "#f0f4f8",
            "padding": "6px 8px",
            "border": "1px solid #d0d8e0",
        }), row=r, col=2)

        # 无截断对照
        row.add(TextNode("", style={"font-size": "4px"}), row=r+1, col=1)
        row.add(TextNode(f"原文：{text}", style={
            "font-size": "10px", "color": "#999",
            "padding": "0 8px", "white-space": "nowrap",
        }), row=r+1, col=2)

    grid.add(row, row=2, col=1)

    grid.add(TextNode("✓ 预期：文本应在 300px 框内被截断并以「…」结尾，截断位置紧贴右边界", style={
        "font-size": "12px", "color": "#27ae60",
    }), row=3, col=1)

    save(grid, "24_ellipsis_precision.svg")

if __name__ == "__main__":
    demo_24_ellipsis_precision()