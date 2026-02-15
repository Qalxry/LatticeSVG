# =========================================================================
# Demo 20：中英文混合字体
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

def demo_20_mixed_fonts():
    heading("Demo 20: 中英文混合字体（字体回退链）")

    grid = GridContainer(style={
        "width": "600px",
        "padding": "20px",
        "grid-template-columns": ["1fr"],
        "gap": "16px",
        "background-color": "#fdf6e3",
    })

    # 标题 —— Times New Roman + SimSun 混排
    title = TextNode(
        "LatticeSVG：CSS Grid Layout Engine for SVG",
        style={
            "font-family": "Times New Roman, SimSun, serif",
            "font-size": "24px",
            "color": "#073642",
            "text-align": "center",
            "padding": "12px",
            "background-color": "#eee8d5",
        },
    )
    grid.add(title, row=1, col=1)

    # 正文 —— 中英文混排段落
    body = TextNode(
        "字体回退链（Font Fallback Chain）是一种常见的排版策略。"
        "当主字体（Primary Font）缺少某个字符的字形（Glyph）时，"
        "引擎会自动尝试回退链中的下一个字体。"
        "例如：英文使用 Times New Roman，中文使用 SimSun（宋体）。",
        style={
            "font-family": "Times New Roman, SimSun, serif",
            "font-size": "16px",
            "color": "#586e75",
            "padding": "10px",
            "background-color": "#ffffff",
            "border": "1px solid #93a1a1",
        },
    )
    grid.add(body, row=2, col=1)

    # 技术说明
    tech = TextNode(
        "实现原理：FontManager.glyph_metrics() 接受字体路径列表，"
        "对每个字符调用 FreeType 的 get_char_index() 判断字形覆盖，"
        "选择第一个能提供该字符字形的字体进行度量。"
        "SVG 输出使用 font-family 属性列出完整回退链。",
        style={
            "font-family": "Times New Roman, SimSun, serif",
            "font-size": "14px",
            "color": "#657b83",
            "padding": "10px",
            "background-color": "#fefbf1",
        },
    )
    grid.add(tech, row=3, col=1)

    save(grid, "20_mixed_fonts.svg")
    print("  → 标题与正文使用 Times New Roman + SimSun 混合渲染")
    
if __name__ == "__main__":
    demo_20_mixed_fonts()