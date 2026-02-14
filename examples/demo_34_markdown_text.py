# =========================================================================
# Demo 34：Markdown 标记富文本
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save


def demo_34_markdown_text():
    heading("Demo 34: Markdown Rich Text")

    grid = GridContainer(style={
        "width": "600px",
        "padding": "24px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "16px",
    })

    grid.add(TextNode("Markdown 富文本演示", style={
        "font-size": "24px",
        "font-weight": "bold",
        "color": "#2c3e50",
        "text-align": "center",
    }))

    # Bold + italic
    grid.add(TextNode(
        "This has **bold**, *italic*, and **both *nested* styles**.",
        style={"font-size": "16px", "color": "#333", "line-height": "1.5"},
        markup="markdown",
    ))

    # Inline code
    grid.add(TextNode(
        "Install with `pip install latticesvg` and run `python demo.py`.",
        style={"font-size": "15px", "color": "#333", "line-height": "1.5"},
        markup="markdown",
    ))

    # Strikethrough
    grid.add(TextNode(
        "This is ~~no longer valid~~ updated information.",
        style={"font-size": "15px", "color": "#333", "line-height": "1.5"},
        markup="markdown",
    ))

    # Inline math ($ ... $)
    grid.add(TextNode(
        "The equation $E = mc^2$ is well known. "
        "Also consider $\\int_0^\\infty e^{-x} dx = 1$.",
        style={"font-size": "16px", "color": "#333", "line-height": "1.6"},
        markup="markdown",
    ))

    save(grid, "34_markdown_text.svg", 600)


if __name__ == "__main__":
    demo_34_markdown_text()
