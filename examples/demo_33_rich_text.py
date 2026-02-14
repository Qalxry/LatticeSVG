# =========================================================================
# Demo 33：Rich Text — HTML 标记富文本
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save


def demo_33_rich_text():
    heading("Demo 33: Rich Text (HTML 标记)")

    grid = GridContainer(style={
        "width": "600px",
        "padding": "24px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "16px",
    })

    # 标题
    grid.add(TextNode("HTML 富文本演示", style={
        "font-size": "24px",
        "font-weight": "bold",
        "color": "#2c3e50",
        "text-align": "center",
    }))

    # Bold + Italic
    grid.add(TextNode(
        "This sentence has <b>bold text</b>, <i>italic text</i>, "
        "and <b><i>bold italic</i></b> combined.",
        style={"font-size": "16px", "color": "#333", "line-height": "1.5"},
        markup="html",
    ))

    # Inline code
    grid.add(TextNode(
        "运行 <code>pip install latticesvg</code> 来安装，"
        "或使用 <code>python -m latticesvg</code> 执行。",
        style={"font-size": "15px", "color": "#333", "line-height": "1.5"},
        markup="html",
    ))

    # Color spans
    grid.add(TextNode(
        '彩色文本：<span style="color: #e74c3c">红色</span>、'
        '<span style="color: #27ae60">绿色</span>、'
        '<span style="color: #2980b9">蓝色</span>。',
        style={"font-size": "16px", "color": "#333"},
        markup="html",
    ))

    # Subscript and superscript
    grid.add(TextNode(
        "化学式：H<sub>2</sub>O，数学：x<sup>2</sup> + y<sup>2</sup> = r<sup>2</sup>",
        style={"font-size": "16px", "color": "#333"},
        markup="html",
    ))

    # Text decoration
    grid.add(TextNode(
        "<u>下划线文本</u>，以及 <del>删除线文本</del>",
        style={"font-size": "16px", "color": "#333"},
        markup="html",
    ))

    # Line break
    grid.add(TextNode(
        "第一行文本<br>第二行文本<br>第三行文本",
        style={"font-size": "15px", "color": "#555"},
        markup="html",
    ))

    save(grid, "33_rich_text.svg", 600)


if __name__ == "__main__":
    demo_33_rich_text()
