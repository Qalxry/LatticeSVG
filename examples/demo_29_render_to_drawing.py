# =========================================================================
# Demo 29：P1-3 render_to_drawing()
# =========================================================================

from latticesvg import GridContainer, TextNode, Renderer
from utils import heading, OUTPUT_DIR

def demo_29_render_to_drawing():
    heading("Demo 29: render_to_drawing() 无文件渲染")

    import drawsvg as dw

    grid = GridContainer(style={
        "width": "400px",
        "padding": "20px",
        "background-color": "#ecf0f1",
        "grid-template-columns": ["1fr"],
    })
    grid.add(TextNode("由 render_to_drawing() 生成", style={
        "font-size": "18px", "color": "#2c3e50", "text-align": "center",
    }), row=1, col=1)

    grid.layout(available_width=400)

    renderer = Renderer()
    drawing = renderer.render_to_drawing(grid)

    # 在 Drawing 上叠加水印 — 证明返回的 Drawing 可继续操作
    drawing.append(dw.Text(
        "WATERMARK", 24,
        200, 40,
        fill="#e74c3c",
        opacity=0.3,
        text_anchor="middle",
        font_weight="bold",
    ))

    path = OUTPUT_DIR / "29_render_to_drawing.svg"
    drawing.save_svg(str(path))
    print(f"  ✓ 29_render_to_drawing.svg (含水印叠加)")
    
if __name__ == "__main__":
    demo_29_render_to_drawing()