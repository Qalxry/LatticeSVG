# =========================================================================
# Demo 10：嵌套 Grid
# =========================================================================

from latticesvg import GridContainer
from utils import heading, save, ColorBox

def demo_10_nested_grid():
    heading("Demo 10: 嵌套 Grid")

    outer = GridContainer(style={
        "width": "700px",
        "padding": "15px",
        "background-color": "#ecf0f1",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "15px",
    })

    # 左侧：纯色块
    outer.add(ColorBox(50, 120, **{"background-color": "#2c3e50"}),
              row=1, col=1)

    # 右侧：嵌套 2×2 子网格
    inner = GridContainer(style={
        "grid-template-columns": ["1fr", "1fr"],
        "grid-template-rows": ["55px", "55px"],
        "gap": "10px",
        "background-color": "#bdc3c7",
        "padding": "5px",
    })
    inner_colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
    for color in inner_colors:
        inner.add(ColorBox(50, 55, **{"background-color": color}))

    outer.add(inner, row=1, col=2)

    save(outer, "10_nested_grid.svg", 700)
    
if __name__ == "__main__":
    demo_10_nested_grid()