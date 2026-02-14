# =========================================================================
# Demo 7：自动放置
# =========================================================================

from latticesvg import GridContainer
from utils import heading, save, ColorBox

def demo_07_auto_placement():
    heading("Demo 7: 自动放置（grid-auto-flow: row）")

    grid = GridContainer(style={
        "width": "500px",
        "padding": "10px",
        "background-color": "#fdfefe",
        "grid-template-columns": ["1fr", "1fr", "1fr", "1fr"],
        "gap": "8px",
    })

    colors = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
        "#9b59b6", "#1abc9c", "#e67e22", "#34495e",
    ]
    for color in colors:
        grid.add(ColorBox(
            width=50, height=50,
            **{"background-color": color}
        ))

    save(grid, "07_auto_placement.svg", 500)

if __name__ == "__main__":
    demo_07_auto_placement()