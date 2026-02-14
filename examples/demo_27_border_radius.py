# =========================================================================
# Demo 27：P1-1 border-radius 圆角
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

def demo_27_border_radius():
    heading("Demo 27: border-radius 圆角")

    grid = GridContainer(style={
        "width": "700px",
        "padding": "20px",
        "background-color": "#f8f9fa",
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "grid-template-rows": ["auto", "auto", "auto"],
        "gap": "16px",
    })

    # Row 1: 不同圆角大小
    for i, (r, label) in enumerate([
        ("0px", "radius: 0"),
        ("8px", "radius: 8px"),
        ("20px", "radius: 20px"),
    ]):
        box = GridContainer(style={
            "background-color": "#3498db",
            "border-radius": r,
            "padding": "16px",
            "grid-template-columns": ["1fr"],
        })
        box.add(TextNode(label, style={
            "font-size": "14px", "color": "#ffffff", "text-align": "center",
        }), row=1, col=1)
        grid.add(box, row=1, col=i + 1)

    # Row 2: 圆角 + 边框
    for i, (r, bs, label) in enumerate([
        ("12px", "solid", "圆角 + solid"),
        ("12px", "dashed", "圆角 + dashed"),
        ("12px", "dotted", "圆角 + dotted"),
    ]):
        box = GridContainer(style={
            "background-color": "#eaf6ff",
            "border": f"3px {bs} #2980b9",
            "border-radius": r,
            "padding": "16px",
            "grid-template-columns": ["1fr"],
        })
        box.add(TextNode(label, style={
            "font-size": "14px", "color": "#2c3e50", "text-align": "center",
        }), row=1, col=1)
        grid.add(box, row=2, col=i + 1)

    # Row 3: 大圆角（药丸/胶囊按钮）
    pill = GridContainer(style={
        "background-color": "#2ecc71",
        "border-radius": "50px",
        "padding": "12px 24px",
        "grid-template-columns": ["1fr"],
        "align-self": "center",
    })
    pill.add(TextNode("药丸按钮 (r=50px)", style={
        "font-size": "14px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(pill, row=3, col=1, col_span=2)

    card = GridContainer(style={
        "background-color": "#ffffff",
        "border": "1px solid #dee2e6",
        "border-radius": "12px",
        "padding": "16px",
        "grid-template-columns": ["1fr"],
    })
    card.add(TextNode("卡片样式", style={
        "font-size": "14px", "color": "#495057", "text-align": "center",
    }), row=1, col=1)
    grid.add(card, row=3, col=3)

    grid.add(TextNode("✓ 预期：第一行圆角递增；第二行圆角+不同边框样式；第三行药丸按钮和卡片", style={
        "font-size": "12px", "color": "#2ecc71",
    }), row=4, col=1, col_span=3)

    save(grid, "27_border_radius.svg")
    
if __name__ == "__main__":
    demo_27_border_radius()