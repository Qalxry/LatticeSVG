# =========================================================================
# Demo 17：PNG 输出
# =========================================================================

from latticesvg import GridContainer, Renderer
from utils import heading, ColorBox, OUTPUT_DIR

def demo_17_png_output():
    heading("Demo 17: PNG 输出（cairosvg）")

    try:
        import cairosvg  # noqa: F401
    except ImportError:
        print("  ⚠ cairosvg 未安装，跳过 PNG 输出演示")
        return

    grid = GridContainer(style={
        "width": "400px",
        "padding": "20px",
        "background-color": "#2c3e50",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "10px",
    })
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
    for c in colors:
        grid.add(ColorBox(50, 50, **{"background-color": c}))

    grid.layout(available_width=400)
    renderer = Renderer()

    png_path = OUTPUT_DIR / "17_png_output.png"
    renderer.render_png(grid, str(png_path), scale=2)
    size = png_path.stat().st_size
    print(f"  ✓ 17_png_output.png  ({size:,} bytes, scale=2x)")
    
if __name__ == "__main__":
    demo_17_png_output()