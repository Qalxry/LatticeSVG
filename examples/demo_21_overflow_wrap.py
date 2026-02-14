# =========================================================================
# Demo 21：overflow-wrap: break-word
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

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
    
if __name__ == "__main__":
    demo_21_overflow_wrap()