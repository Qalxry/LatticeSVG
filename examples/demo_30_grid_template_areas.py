# =========================================================================
# Demo 30：P2-1 grid-template-areas 命名区域
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

def demo_30_grid_template_areas():
    heading("Demo 30: grid-template-areas 命名区域布局")

    # 经典 Holy Grail 布局：header / sidebar + main / footer
    grid = GridContainer(style={
        "width": "700px",
        "padding": "12px",
        "background-color": "#ecf0f1",
        "grid-template-columns": ["180px", "1fr"],
        "grid-template-rows": ["50px", "200px", "40px"],
        "grid-template-areas": '"header header" "sidebar main" "footer footer"',
        "gap": "10px",
    })

    # Header — 跨两列
    header = GridContainer(style={
        "background-color": "#2c3e50",
        "border-radius": "6px",
        "padding": "10px",
        "grid-template-columns": ["1fr"],
        "justify-items": "center",
        "align-items": "center",
    })
    header.add(TextNode("Header 区域 (跨两列)", style={
        "font-size": "18px", "color": "#ffffff", "text-align": "center",
    }), row=1, col=1)
    grid.add(header, area="header")

    # Sidebar — 左侧
    sidebar = GridContainer(style={
        "background-color": "#3498db",
        "border-radius": "6px",
        "padding": "10px",
        "grid-template-columns": ["1fr"],
    })
    for i, label in enumerate(["导航项 A", "导航项 B", "导航项 C"], 1):
        sidebar.add(TextNode(label, style={
            "font-size": "13px", "color": "#ffffff",
        }), row=i, col=1)
    grid.add(sidebar, area="sidebar")

    # Main — 主内容
    main_area = GridContainer(style={
        "background-color": "#ffffff",
        "border-radius": "6px",
        "border": "1px solid #bdc3c7",
        "padding": "16px",
        "grid-template-columns": ["1fr"],
    })
    main_area.add(TextNode("Main 内容区域", style={
        "font-size": "16px", "color": "#2c3e50", "font-weight": "bold",
    }), row=1, col=1)
    main_area.add(TextNode(
        "通过 grid-template-areas 定义命名区域，子元素使用 area= 参数放置。"
        "支持跨行跨列的区域定义，以及使用 \".\" 表示空单元格。",
        style={"font-size": "13px", "color": "#7f8c8d", "line-height": "1.6"},
    ), row=2, col=1)
    grid.add(main_area, area="main")

    # Footer — 跨两列
    footer = GridContainer(style={
        "background-color": "#2c3e50",
        "border-radius": "6px",
        "padding": "8px",
        "grid-template-columns": ["1fr"],
        "justify-items": "center",
        "align-items": "center",
    })
    footer.add(TextNode("Footer © 2025", style={
        "font-size": "12px", "color": "#95a5a6", "text-align": "center",
    }), row=1, col=1)
    grid.add(footer, area="footer")

    grid.add(TextNode(
        "✓ 预期：经典 Holy Grail 布局 — header/footer 全宽，sidebar 在左，main 在右",
        style={"font-size": "12px", "color": "#2ecc71"},
    ), row=4, col=1, col_span=2)

    save(grid, "30_grid_template_areas.svg")
    
if __name__ == "__main__":
    demo_30_grid_template_areas()