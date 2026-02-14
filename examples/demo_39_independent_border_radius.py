# =========================================================================
# Demo 39：P2-1 四角独立 border-radius
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save


def demo_39_independent_border_radius():
    heading("Demo 39: 四角独立 border-radius")

    grid = GridContainer(style={
        "width": "720px",
        "padding": "20px",
        "background-color": "#f8f9fa",
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "grid-template-rows": ["auto", "auto", "auto"],
        "gap": "16px",
    })

    # ── Row 1: Tab 标签风格（仅顶部圆角）──
    tab = GridContainer(style={
        "background-color": "#3498db",
        "border-radius": "12px 12px 0 0",
        "padding": "12px 20px",
        "grid-template-columns": ["1fr"],
    })
    tab.add(TextNode("Tab 标签（顶部圆角）", style={
        "font-size": "14px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(tab, row=1, col=1)

    # 仅左上角
    tl_only = GridContainer(style={
        "background-color": "#2ecc71",
        "border-top-left-radius": "24px",
        "padding": "12px 20px",
        "grid-template-columns": ["1fr"],
    })
    tl_only.add(TextNode("仅左上圆角 24px", style={
        "font-size": "14px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(tl_only, row=1, col=2)

    # 对角圆角
    diag = GridContainer(style={
        "background-color": "#e74c3c",
        "border-radius": "20px 0 20px 0",
        "padding": "12px 20px",
        "grid-template-columns": ["1fr"],
    })
    diag.add(TextNode("对角圆角", style={
        "font-size": "14px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(diag, row=1, col=3)

    # ── Row 2: 对话气泡风格 ──
    bubble = GridContainer(style={
        "background-color": "#dfe6e9",
        "border-radius": "16px 16px 16px 0",
        "padding": "14px 14px",
        "grid-template-columns": ["1fr"],
    })
    bubble.add(TextNode("对话气泡（左下直角）", style={
        "font-size": "13px", "color": "#2d3436", "text-align": "left",
    }), row=1, col=1)
    grid.add(bubble, row=2, col=1)

    bubble_r = GridContainer(style={
        "background-color": "#74b9ff",
        "border-radius": "16px 16px 0 16px",
        "padding": "14px 14px",
        "grid-template-columns": ["1fr"],
    })
    bubble_r.add(TextNode("对话气泡（右下直角）", style={
        "font-size": "13px", "color": "#ffffff", "text-align": "right",
    }), row=1, col=1)
    grid.add(bubble_r, row=2, col=2)

    # 底部圆角卡片
    bottom_card = GridContainer(style={
        "background-color": "#fdcb6e",
        "border-radius": "0 0 16px 16px",
        "padding": "14px 14px",
        "grid-template-columns": ["1fr"],
    })
    bottom_card.add(TextNode("仅底部圆角", style={
        "font-size": "13px", "color": "#2d3436", "text-align": "center",
    }), row=1, col=1)
    grid.add(bottom_card, row=2, col=3)

    # ── Row 3: 带边框的四角独立 ──
    border_tab = GridContainer(style={
        "background-color": "#ffffff",
        "border": "2px solid #6c5ce7",
        "border-radius": "10px 10px 0 0",
        "padding": "12px 14px",
        "grid-template-columns": ["1fr"],
    })
    border_tab.add(TextNode("边框 Tab", style={
        "font-size": "13px", "color": "#6c5ce7", "text-align": "center",
    }), row=1, col=1)
    grid.add(border_tab, row=3, col=1)

    ticket = GridContainer(style={
        "background-color": "#ffeaa7",
        "border": "2px dashed #d63031",
        "border-radius": "8px 20px 8px 20px",
        "padding": "12px 14px",
        "grid-template-columns": ["1fr"],
    })
    ticket.add(TextNode("票券风格", style={
        "font-size": "13px", "color": "#d63031", "text-align": "center",
    }), row=1, col=1)
    grid.add(ticket, row=3, col=2)

    pill = GridContainer(style={
        "background-color": "#a29bfe",
        "border-radius": "50px",
        "padding": "12px 14px",
        "grid-template-columns": ["1fr"],
    })
    pill.add(TextNode("药丸按钮", style={
        "font-size": "13px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(pill, row=3, col=3)

    save(grid, "demo_39_independent_border_radius.svg")


if __name__ == "__main__":
    demo_39_independent_border_radius()
