# =========================================================================
# Demo 47：P2-2 CSS filter 滤镜
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save


def demo_47_css_filter():
    heading("Demo 47: CSS filter 滤镜")

    grid = GridContainer(style={
        "width": "700px",
        "padding": "20px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr", "1fr", "1fr", "1fr"],
        "grid-template-rows": ["auto", "auto"],
        "gap": "16px",
    })

    # Row 1: 单一滤镜
    filters_row1 = [
        ("blur(2px)", "blur(2px)"),
        ("grayscale(100%)", "grayscale"),
        ("sepia(100%)", "sepia"),
        ("brightness(150%)", "brightness"),
    ]
    for i, (f, label) in enumerate(filters_row1):
        card = GridContainer(style={
            "background-color": "#3498db",
            "border-radius": "8px",
            "filter": f,
            "padding": "16px",
            "grid-template-columns": ["1fr"],
        })
        card.add(TextNode(label, style={
            "font-size": "12px", "color": "white", "text-align": "center",
        }), row=1, col=1)
        grid.add(card, row=1, col=i + 1)

    # Row 2: 组合滤镜 + 其他
    filters_row2 = [
        ("contrast(200%)", "contrast"),
        ("saturate(200%)", "saturate"),
        ("opacity(50%)", "opacity"),
        ("grayscale(50%) blur(1px)", "组合"),
    ]
    for i, (f, label) in enumerate(filters_row2):
        card = GridContainer(style={
            "background-color": "#e74c3c",
            "border-radius": "8px",
            "filter": f,
            "padding": "16px",
            "grid-template-columns": ["1fr"],
        })
        card.add(TextNode(label, style={
            "font-size": "12px", "color": "white", "text-align": "center",
        }), row=1, col=1)
        grid.add(card, row=2, col=i + 1)

    save(grid, "47_css_filter.svg")


if __name__ == "__main__":
    demo_47_css_filter()
