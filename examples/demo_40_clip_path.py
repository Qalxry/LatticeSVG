# =========================================================================
# Demo 40：P2-2 clip-path 裁切
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save


def demo_40_clip_path():
    heading("Demo 40: clip-path 裁切效果")

    grid = GridContainer(style={
        "width": "840px",
        "padding": "20px",
        "background-color": "#f0f0f0",
        "grid-template-columns": ["250px", "250px", "250px"],
        "grid-template-rows": ["250px", "250px"],
        "gap": "20px",
    })

    # ── Row 1 ──

    # circle — 圆形裁切（头像风格）
    circle_box = GridContainer(style={
        "background-color": "#3498db",
        "clip-path": "circle(50% at 50% 50%)",
        "padding": "80px 20px",
        "grid-template-columns": ["1fr"],
    })
    circle_box.add(TextNode("circle(50%)", style={
        "font-size": "14px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(circle_box, row=1, col=1)

    # ellipse — 椭圆裁切
    ellipse_box = GridContainer(style={
        "background-color": "#e74c3c",
        "clip-path": "ellipse(50% 25% at 50% 50%)",
        "padding": "80px 20px",
        "grid-template-columns": ["1fr"],
    })
    ellipse_box.add(TextNode("ellipse(50% 45%)", style={
        "font-size": "14px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(ellipse_box, row=1, col=2)

    # polygon — 三角形
    tri_box = GridContainer(style={
        "background-color": "#2ecc71",
        "clip-path": "polygon(50% 7.2%, 100% 93.8%, 0% 93.8%)",
        "padding": "80px 20px",
        "grid-template-columns": ["1fr"],
    })
    tri_box.add(TextNode("△ triangle", style={
        "font-size": "14px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(tri_box, row=1, col=3)

    # ── Row 2 ──

    # polygon — 菱形
    diamond_box = GridContainer(style={
        "background-color": "#f39c12",
        "clip-path": "polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)",
        "padding": "80px 20px",
        "grid-template-columns": ["1fr"],
    })
    diamond_box.add(TextNode("◇ diamond", style={
        "font-size": "14px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(diamond_box, row=2, col=1)

    # inset — 内缩裁切
    inset_box = GridContainer(style={
        "background-color": "#9b59b6",
        "clip-path": "inset(10px 15px round 8px)",
        "padding": "80px 20px",
        "grid-template-columns": ["1fr"],
    })
    inset_box.add(TextNode("inset(10 15 round 8)", style={
        "font-size": "13px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(inset_box, row=2, col=2)

    # polygon — 六边形
    hex_box = GridContainer(style={
        "background-color": "#1abc9c",
        "clip-path": "polygon(50% 0%, 93.3% 25%, 93.3% 75%, 50% 100%, 6.7% 75%, 6.7% 25%)",
        "padding": "80px 20px",
        "grid-template-columns": ["1fr"],
    })
    hex_box.add(TextNode("⬡ hexagon", style={
        "font-size": "14px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(hex_box, row=2, col=3)

    save(grid, "demo_40_clip_path.svg")


if __name__ == "__main__":
    demo_40_clip_path()
