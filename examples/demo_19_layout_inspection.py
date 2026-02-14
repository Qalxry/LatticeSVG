# =========================================================================
# Demo 19：布局信息打印
# =========================================================================

from latticesvg import GridContainer
from utils import heading, ColorBox

def demo_19_layout_inspection():
    heading("Demo 19: 布局结果检查")

    grid = GridContainer(style={
        "width": "400px",
        "padding": "10px",
        "grid-template-columns": ["100px", "1fr"],
        "gap": "10px",
    })

    a = ColorBox(100, 40, **{"background-color": "#e74c3c"})
    b = ColorBox(50, 40, **{"background-color": "#3498db"})
    grid.add(a, row=1, col=1)
    grid.add(b, row=1, col=2)
    grid.layout(available_width=400)

    print(f"  Grid container:")
    print(f"    border_box  = {grid.border_box}")
    print(f"    padding_box = {grid.padding_box}")
    print(f"    content_box = {grid.content_box}")
    print(f"  Child A (100px fixed):")
    print(f"    border_box  = {a.border_box}")
    print(f"  Child B (1fr):")
    print(f"    border_box  = {b.border_box}")
    print(f"    → content width = {b.content_box.width:.1f}px "
          f"(= 400 - 20pad - 100col1 - 10gap = 270)")
    
if __name__ == "__main__":
    demo_19_layout_inspection()