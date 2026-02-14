# =========================================================================
# Demo 11：Padding & Border
# =========================================================================

from latticesvg import GridContainer
from utils import heading, save, ColorBox

def demo_11_box_model():
    heading("Demo 11: Padding 与 Border 盒模型")

    grid = GridContainer(style={
        "width": "500px",
        "padding": "20px",
        "background-color": "#fdfefe",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "20px",
        "border-width": "3px",
        "border-color": "#2c3e50",
    })

    # 有 padding 的色块
    grid.add(ColorBox(50, 80, **{
        "background-color": "#e8daef",
        "padding": "15px",
        "border-width": "2px",
        "border-color": "#8e44ad",
    }))

    grid.add(ColorBox(50, 80, **{
        "background-color": "#d5f5e3",
        "padding": "10px",
        "border-width": "1px",
        "border-color": "#27ae60",
    }))

    save(grid, "11_box_model.svg", 500)
    
if __name__ == "__main__":
    demo_11_box_model()