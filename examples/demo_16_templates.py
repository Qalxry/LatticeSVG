# =========================================================================
# Demo 16：内置样式模板
# =========================================================================

from latticesvg import GridContainer, TextNode, templates
from utils import heading, save

def demo_16_templates():
    heading("Demo 16: 内置样式模板")

    print(f"  可用模板列表 ({len(templates.ALL_TEMPLATES)} 个):")
    for name, tmpl in templates.ALL_TEMPLATES.items():
        keys = ", ".join(tmpl.keys())
        print(f"    {name:20s} → {keys}")

    # 使用模板构建页面
    grid = GridContainer(style={
        **templates.REPORT_PAGE,
        "width": "600px",
    })

    grid.add(TextNode("使用 TITLE 模板", style=templates.TITLE))
    grid.add(TextNode("使用 SUBTITLE 模板", style=templates.SUBTITLE))
    grid.add(TextNode(
        "使用 PARAGRAPH 模板。这是一段正文示例，展示了段落的默认"
        "字号、行高和颜色配置。模板可以通过字典合并进行自定义。",
        style=templates.PARAGRAPH,
    ))
    grid.add(TextNode("使用 CAPTION 模板 — 图表说明文字", style=templates.CAPTION))
    grid.add(TextNode("CODE 模板\n  def hello():\n    print('world')", style=templates.CODE))

    save(grid, "16_templates.svg", 600)
    
if __name__ == "__main__":
    demo_16_templates()