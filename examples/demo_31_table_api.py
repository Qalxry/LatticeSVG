# =========================================================================
# Demo 31：P2-2 表格便捷 API
# =========================================================================

from latticesvg import GridContainer, TextNode, build_table
from utils import heading, save

def demo_31_table_api():
    heading("Demo 31: build_table() 表格便捷 API")

    # ---- 表格 1：基础实验数据表 ----
    page = GridContainer(style={
        "width": "700px",
        "padding": "20px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr"],
        "gap": "20px",
    })

    page.add(TextNode("实验数据记录表", style={
        "font-size": "20px", "font-weight": "bold",
        "color": "#2c3e50", "text-align": "center",
    }), row=1, col=1)

    tbl1 = build_table(
        headers=["样品编号", "温度 (°C)", "压力 (kPa)", "产率 (%)"],
        rows=[
            ["S-001", "25.0", "101.3", "87.2"],
            ["S-002", "30.0", "101.3", "91.5"],
            ["S-003", "35.0", "101.3", "89.8"],
            ["S-004", "40.0", "101.3", "85.3"],
            ["S-005", "45.0", "101.3", "82.1"],
        ],
        col_widths=["120px", "1fr", "1fr", "1fr"],
    )
    page.add(tbl1, row=2, col=1)

    # ---- 表格 2：自定义样式表 ----
    page.add(TextNode("成绩单（自定义样式）", style={
        "font-size": "20px", "font-weight": "bold",
        "color": "#2c3e50", "text-align": "center",
    }), row=3, col=1)

    tbl2 = build_table(
        headers=["姓名", "数学", "物理", "英语", "总分"],
        rows=[
            ["张三", "92", "88", "95", "275"],
            ["李四", "85", "91", "82", "258"],
            ["王五", "78", "95", "88", "261"],
        ],
        header_style={
            "background-color": "#2c3e50",
            "color": "#ffffff",
            "font-size": "14px",
            "text-align": "center",
        },
        cell_style={
            "font-size": "14px",
            "text-align": "center",
        },
        stripe_color="#eaf2f8",
        col_widths=["120px", "1fr", "1fr", "1fr", "1fr"],
    )
    page.add(tbl2, row=4, col=1)

    page.add(TextNode(
        "✓ 预期：两张表格 — 上方默认样式数据表（灰色表头 + 条纹），"
        "下方深色表头 + 蓝色条纹 + 居中对齐",
        style={"font-size": "12px", "color": "#2ecc71"},
    ), row=5, col=1)

    save(page, "31_table_api.svg")
    
if __name__ == "__main__":
    demo_31_table_api()