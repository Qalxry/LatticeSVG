# =========================================================================
# Demo 46：P1-3 transform 变换
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import ColorBox, heading, save


def demo_46_transform():
    heading("Demo 46: transform 变换")

    grid = GridContainer(style={
        "width": "700px",
        "padding": "40px",
        "background-color": "#f8f9fa",
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "grid-template-rows": ["120px", "120px"],
        "gap": "24px",
    })

    # Row 1: 旋转
    rotations = [
        ("rotate(15deg)", "rotate(15°)"),
        ("rotate(45deg)", "rotate(45°)"),
        ("rotate(-30deg)", "rotate(-30°)"),
    ]
    for i, (tf, label) in enumerate(rotations):
        box = GridContainer(style={
            "background-color": "#3498db",
            "border-radius": "4px",
            "transform": tf,
            "padding": "12px",
            "grid-template-columns": ["1fr"],
        })
        box.add(TextNode(label, style={
            "font-size": "13px", "color": "white", "text-align": "center",
        }), row=1, col=1)
        grid.add(box, row=1, col=i + 1)

    # Row 2: 平移 + 缩放
    transforms = [
        ("translate(10px, -5px)", "translate"),
        ("scale(0.8)", "scale(0.8)"),
        ("translate(5px, 5px) scale(1.1)", "组合变换"),
    ]
    for i, (tf, label) in enumerate(transforms):
        box = GridContainer(style={
            "background-color": "#e74c3c",
            "border-radius": "4px",
            "transform": tf,
            "padding": "12px",
            "grid-template-columns": ["1fr"],
        })
        box.add(TextNode(label, style={
            "font-size": "13px", "color": "white", "text-align": "center",
        }), row=1, col=1)
        grid.add(box, row=2, col=i + 1)

    save(grid, "46_transform.svg")


if __name__ == "__main__":
    demo_46_transform()
