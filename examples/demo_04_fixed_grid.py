# =========================================================================
# Demo 4：固定列 Grid
# =========================================================================
from latticesvg import GridContainer
from utils import heading, save, ColorBox

def demo_04_fixed_grid():
    heading("Demo 4: 固定列宽 Grid")

    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
    grid = GridContainer(style={
        "width": "600px",
        "padding": "15px",
        "background-color": "#ecf0f1",
        "grid-template-columns": ["150px", "150px", "150px"],
        "grid-template-rows": ["60px", "60px"],
        "gap": "15px",
    })

    for i, color in enumerate(colors):
        grid.add(ColorBox(
            width=150, height=60,
            **{"background-color": color}
        ))

    save(grid, "04_fixed_grid.svg", 600)
    
if __name__ == "__main__":
    demo_04_fixed_grid()