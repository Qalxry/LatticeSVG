# =========================================================================
# Demo 26：opacity 渲染
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save, ColorBox

def demo_26_opacity():
    heading("Demo 26: opacity 渲染")

    grid = GridContainer(style={
        "width": "800px",
        "padding": "20px",
        "gap": "12px",
        "background-color": "#1a1a2e",
        "grid-template-columns": ["1fr"],
    })

    grid.add(TextNode("Demo 26: opacity 渲染", style={
        "font-size": "18px", "font-weight": "bold", "color": "#ffffff",
    }), row=1, col=1)

    # 背景 opacity 渐变
    bg_row = GridContainer(style={
        "grid-template-columns": ["1fr"] * 5,
        "gap": "8px",
    })

    for i, op in enumerate([1.0, 0.8, 0.6, 0.4, 0.2]):
        bg_row.add(ColorBox(140, 60, **{
            "background-color": "#3498db",
            "opacity": str(op),
        }), row=1, col=i+1)
        bg_row.add(TextNode(f"opacity: {op}", style={
            "font-size": "11px", "color": "#aaaaaa", "text-align": "center",
        }), row=2, col=i+1)

    grid.add(bg_row, row=2, col=1)

    # 文字 opacity 渐变
    text_row = GridContainer(style={
        "grid-template-columns": ["1fr"] * 5,
        "gap": "8px",
    })

    for i, op in enumerate([1.0, 0.8, 0.6, 0.4, 0.2]):
        text_row.add(TextNode("LatticeSVG", style={
            "font-size": "16px", "font-weight": "bold",
            "color": "#e74c3c",
            "opacity": str(op),
            "text-align": "center",
            "padding": "10px",
            "background-color": "#2a2a4e",
        }), row=1, col=i+1)
        text_row.add(TextNode(f"text opacity: {op}", style={
            "font-size": "11px", "color": "#aaaaaa", "text-align": "center",
        }), row=2, col=i+1)

    grid.add(text_row, row=3, col=1)

    grid.add(TextNode("✓ 预期：从左到右透明度递增，背景和文字均应逐渐变淡", style={
        "font-size": "12px", "color": "#2ecc71",
    }), row=4, col=1)

    save(grid, "26_opacity.svg")
    
if __name__ == "__main__":
    demo_26_opacity()