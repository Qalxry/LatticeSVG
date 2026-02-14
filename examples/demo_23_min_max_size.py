# =========================================================================
# Demo 23：min/max-width/height
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save, ColorBox

def demo_23_min_max_size():
    heading("Demo 23: min/max-width/height 约束")

    grid = GridContainer(style={
        "width": "800px",
        "padding": "20px",
        "gap": "12px",
        "background-color": "#f5f5f5",
        "grid-template-columns": ["1fr"],
    })

    grid.add(TextNode("Demo 23: min-width / max-width / min-height / max-height", style={
        "font-size": "18px", "font-weight": "bold", "color": "#333",
    }), row=1, col=1)

    # --- max-width 测试 ---
    row_mw = GridContainer(style={
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "gap": "10px",
    })

    # 无约束：占满列宽
    row_mw.add(ColorBox(240, 60, **{
        "background-color": "#3498db",
    }), row=1, col=1)
    row_mw.add(TextNode("无约束\n占满列宽", style={
        "font-size": "11px", "color": "#666", "white-space": "pre",
    }), row=2, col=1)

    # max-width: 150px
    row_mw.add(ColorBox(240, 60, **{
        "background-color": "#e74c3c",
        "max-width": "150px",
    }), row=1, col=2)
    row_mw.add(TextNode("max-width: 150px\n红色块应≤150px", style={
        "font-size": "11px", "color": "#666", "white-space": "pre",
    }), row=2, col=2)

    # min-width: 300px
    row_mw.add(ColorBox(100, 60, **{
        "background-color": "#2ecc71",
        "min-width": "300px",
    }), row=1, col=3)
    row_mw.add(TextNode("min-width: 300px\n绿色块应≥300px", style={
        "font-size": "11px", "color": "#666", "white-space": "pre",
    }), row=2, col=3)

    grid.add(row_mw, row=2, col=1)

    # --- min/max-height 测试 ---
    row_mh = GridContainer(style={
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "grid-template-rows": ["120px"],
        "gap": "10px",
    })

    row_mh.add(ColorBox(200, 120, **{
        "background-color": "#9b59b6",
    }), row=1, col=1)
    row_mh.add(TextNode("无约束\n占满行高 120px", style={
        "font-size": "11px", "color": "#666", "white-space": "pre",
    }), row=2, col=1)

    row_mh.add(ColorBox(200, 120, **{
        "background-color": "#e67e22",
        "max-height": "60px",
    }), row=1, col=2)
    row_mh.add(TextNode("max-height: 60px\n橙色块应≤60px高", style={
        "font-size": "11px", "color": "#666", "white-space": "pre",
    }), row=2, col=2)

    row_mh.add(ColorBox(200, 30, **{
        "background-color": "#1abc9c",
        "min-height": "80px",
        "align-self": "start",
    }), row=1, col=3)
    row_mh.add(TextNode("min-height: 80px\n青色块应≥80px高", style={
        "font-size": "11px", "color": "#666", "white-space": "pre",
    }), row=2, col=3)

    grid.add(row_mh, row=3, col=1)

    save(grid, "23_min_max_size.svg")
    
if __name__ == "__main__":
    demo_23_min_max_size()