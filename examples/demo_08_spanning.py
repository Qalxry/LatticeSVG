# =========================================================================
# Demo 8：跨列 / 跨行
# =========================================================================

from latticesvg import GridContainer
from utils import heading, save, ColorBox

def demo_08_spanning():
    heading("Demo 8: 跨列与跨行")

    grid = GridContainer(style={
        "width": "500px",
        "padding": "8px",
        "background-color": "#fdfefe",
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "grid-template-rows": ["80px", "80px", "80px"],
        "gap": "8px",
    })

    # 跨 2 列
    grid.add(ColorBox(50, 80, **{"background-color": "#e74c3c"}),
             row=1, col=1, col_span=2)
    # 跨 2 行
    grid.add(ColorBox(50, 80, **{"background-color": "#3498db"}),
             row=1, col=3, row_span=2)
    # 跨 2 行
    grid.add(ColorBox(50, 80, **{"background-color": "#2ecc71"}),
             row=2, col=1, row_span=2)
    # 普通
    grid.add(ColorBox(50, 80, **{"background-color": "#f39c12"}),
             row=2, col=2)
    # 跨 2 列
    grid.add(ColorBox(50, 80, **{"background-color": "#1abc9c"}),
             row=3, col=2, col_span=2)

    save(grid, "08_spanning.svg")

if __name__ == "__main__":
    demo_08_spanning()