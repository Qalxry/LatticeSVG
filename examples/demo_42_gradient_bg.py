# =========================================================================
# Demo 42：渐变背景（linear-gradient / radial-gradient）
# =========================================================================
#
# 展示 CSS 渐变背景语法：
# - linear-gradient：线性渐变，支持角度和方向关键字
# - radial-gradient：径向渐变，支持 circle/ellipse 形状
# - 渐变可通过 background shorthand 属性指定
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save


def _card(bg: str, label: str, text_color: str = "#ffffff") -> GridContainer:
    """创建一个渐变背景卡片。"""
    card = GridContainer(style={
        "background": bg,
        "border-radius": "12px",
        "padding": "20px",
        "grid-template-columns": ["1fr"],
        "align-items": "center",
    })
    card.add(TextNode(label, style={
        "font-size": "14px", "font-weight": "bold",
        "color": text_color, "text-align": "center",
    }))
    return card


def demo_42_gradient_bg():
    heading("Demo 42: 渐变背景")

    root = GridContainer(style={
        "width": "560px",
        "padding": "20px",
        "background-color": "#f0f0f0",
        "grid-template-columns": ["1fr"],
        "gap": "16px",
    })

    root.add(TextNode(
        "渐变背景（linear-gradient / radial-gradient）",
        style={
            "font-size": "22px", "font-weight": "bold",
            "color": "#2c3e50", "text-align": "center",
            "padding-bottom": "8px",
        },
    ))

    # ---- Linear gradients section ----
    root.add(TextNode("线性渐变", style={
        "font-size": "18px", "font-weight": "bold",
        "color": "#2c3e50", "padding": "4px 0",
    }))

    linear_grid = GridContainer(style={
        "grid-template-columns": "repeat(2, 1fr)",
        "gap": "12px",
    })

    linear_grid.add(_card(
        "linear-gradient(#e66465, #9198e5)",
        "默认方向 (to bottom)",
    ))
    linear_grid.add(_card(
        "linear-gradient(to right, #f093fb, #f5576c)",
        "to right",
    ))
    linear_grid.add(_card(
        "linear-gradient(45deg, #4facfe, #00f2fe)",
        "45deg",
    ))
    linear_grid.add(_card(
        "linear-gradient(to bottom right, #667eea, #764ba2)",
        "to bottom right",
    ))

    root.add(linear_grid)

    # ---- Multi-stop linear gradient ----
    root.add(TextNode("多色标", style={
        "font-size": "18px", "font-weight": "bold",
        "color": "#2c3e50", "padding": "4px 0",
    }))

    multi_grid = GridContainer(style={
        "grid-template-columns": ["1fr"],
        "gap": "12px",
    })

    multi_grid.add(_card(
        "linear-gradient(to right, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082)",
        "彩虹渐变",
    ))
    multi_grid.add(_card(
        "linear-gradient(to right, #2c3e50 0%, #3498db 50%, #2ecc71 100%)",
        "带位置的色标 (0% / 50% / 100%)",
    ))

    root.add(multi_grid)

    # ---- Radial gradients section ----
    root.add(TextNode("径向渐变", style={
        "font-size": "18px", "font-weight": "bold",
        "color": "#2c3e50", "padding": "4px 0",
    }))

    radial_grid = GridContainer(style={
        "grid-template-columns": "repeat(2, 1fr)",
        "gap": "12px",
    })

    radial_grid.add(_card(
        "radial-gradient(circle, #f9d423, #ff4e50)",
        "circle 径向渐变",
    ))
    radial_grid.add(_card(
        "radial-gradient(ellipse, #a8edea, #fed6e3)",
        "ellipse 径向渐变",
        text_color="#333333",
    ))
    radial_grid.add(_card(
        "radial-gradient(circle at 30% 30%, #ffffff, #000000)",
        "偏移圆心 (30% 30%)",
    ))
    radial_grid.add(_card(
        "radial-gradient(circle, #667eea, #764ba2, #f093fb)",
        "三色标径向",
    ))

    root.add(radial_grid)

    save(root, "demo_42_gradient_bg.svg")


if __name__ == "__main__":
    demo_42_gradient_bg()
