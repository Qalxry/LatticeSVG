# =========================================================================
# Demo 45：P1-2 box-shadow 阴影
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save


def demo_45_box_shadow():
    heading("Demo 45: box-shadow 阴影")

    grid = GridContainer(style={
        "width": "700px",
        "padding": "30px",
        "background-color": "#f0f0f0",
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "grid-template-rows": ["auto", "auto"],
        "gap": "24px",
    })

    # Row 1: 不同阴影效果
    for i, (shadow, label) in enumerate([
        ("0 2px 4px rgba(0,0,0,0.2)", "轻柔阴影"),
        ("0 4px 8px rgba(0,0,0,0.3)", "中等阴影"),
        ("0 8px 16px rgba(0,0,0,0.4)", "深度阴影"),
    ]):
        card = GridContainer(style={
            "background-color": "white",
            "border-radius": "8px",
            "box-shadow": shadow,
            "padding": "20px",
            "grid-template-columns": ["1fr"],
        })
        card.add(TextNode(label, style={
            "font-size": "14px", "text-align": "center",
        }), row=1, col=1)
        grid.add(card, row=1, col=i + 1)

    # Row 2: 带偏移的阴影 / 多重阴影 / 彩色阴影
    for i, (shadow, label) in enumerate([
        ("4px 4px 0px rgba(0,0,0,0.15)", "偏移阴影"),
        ("0 1px 3px rgba(0,0,0,0.12), 0 4px 6px rgba(0,0,0,0.15)", "多重阴影"),
        ("0 4px 12px rgba(52,152,219,0.4)", "彩色阴影"),
    ]):
        card = GridContainer(style={
            "background-color": "white",
            "border-radius": "8px",
            "box-shadow": shadow,
            "padding": "20px",
            "grid-template-columns": ["1fr"],
        })
        card.add(TextNode(label, style={
            "font-size": "14px", "text-align": "center",
        }), row=1, col=1)
        grid.add(card, row=2, col=i + 1)

    save(grid, "45_box_shadow.svg")


if __name__ == "__main__":
    demo_45_box_shadow()
