# =========================================================================
# Demo 9：对齐方式
# =========================================================================

from latticesvg import GridContainer
from utils import heading, save, ColorBox

def demo_09_alignment():
    heading("Demo 9: justify-self / align-self 对齐")

    grid = GridContainer(style={
        "width": "600px",
        "padding": "10px",
        "background-color": "#f0f0f0",
        "grid-template-columns": ["200px", "200px", "200px"],
        "grid-template-rows": ["120px", "120px"],
        "gap": "0px",
        "border-width": "1px",
        "border-color": "#cccccc",
    })

    alignments = [
        ("start",  "start",  "#e74c3c"),
        ("center", "center", "#3498db"),
        ("end",    "end",    "#2ecc71"),
        ("start",  "end",    "#f39c12"),
        ("center", "start",  "#9b59b6"),
        ("end",    "center", "#e67e22"),
    ]

    for justify, align, color in alignments:
        box = ColorBox(60, 40, **{
            "background-color": color,
            "justify-self": justify,
            "align-self": align,
        })
        grid.add(box)

    save(grid, "09_alignment.svg")

if __name__ == "__main__":
    demo_09_alignment()