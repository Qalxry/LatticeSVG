# =========================================================================
# Demo 5：fr 弹性列
# =========================================================================

from latticesvg import GridContainer
from utils import heading, save, ColorBox

def demo_05_fr_grid():
    heading("Demo 5: fr 弹性列分配")

    grid = GridContainer(style={
        "width": "700px",
        "padding": "15px",
        "background-color": "#ecf0f1",
        "grid-template-columns": ["1fr", "2fr", "1fr"],
        "gap": "10px",
    })

    labels_colors = [
        ("1fr", "#e74c3c"),
        ("2fr", "#3498db"),
        ("1fr", "#2ecc71"),
    ]
    for label, color in labels_colors:
        grid.add(ColorBox(
            width=50, height=60,
            **{"background-color": color}
        ))

    save(grid, "05_fr_grid.svg", 700)
    
if __name__ == "__main__":
    demo_05_fr_grid()