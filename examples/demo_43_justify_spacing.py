# =========================================================================
# Demo 43：text-align: justify / letter-spacing / word-spacing
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save


SAMPLE_EN = (
    "LatticeSVG is a declarative vector layout engine inspired by CSS Grid. "
    "It provides precise glyph measurement via FreeType, automatic line "
    "breaking, and rich typographic controls for generating SVG output."
)

SAMPLE_ZH = (
    "这是一段中文测试文本，用于验证两端对齐在无空格的中日韩文字中的效果。"
    "每个字符之间将均匀分布额外的间距，使文本占满整行宽度。"
)


def demo_43_justify_spacing():
    heading("Demo 43: text-align: justify & letter/word-spacing")

    grid = GridContainer(style={
        "width": "520px",
        "padding": "20px",
        "background-color": "#f8fafe",
        "grid-template-columns": ["1fr"],
        "gap": "16px",
    })
    
    grid.add(TextNode(
        "justify 对齐与字距/词距控制",
        style={
            "font-size": "22px", "font-weight": "bold",
            "color": "#2c3e50", "text-align": "center",
            "padding-bottom": "10px",
        },
    ))
    
    # ---------- Section 0: comparison baseline ----------
    grid.add(TextNode("0. 对比基线（默认 left + normal spacing）", style={
        "font-size": "18px",
        "font-weight": "bold",
        "color": "#2c3e50",
    }))
    
    grid.add(TextNode(SAMPLE_EN, style={
        "font-size": "14px",
        "color": "#333333",
        "line-height": "1.6",
        "outline": "1px dashed #cccccc",
    }))
    
    grid.add(TextNode(SAMPLE_ZH, style={
        "font-size": "14px",
        "color": "#333333",
        "line-height": "1.6",
        "outline": "1px dashed #cccccc",
    }))

    # ---------- Section 1: text-align: justify ----------
    grid.add(TextNode("1. text-align: justify", style={
        "font-size": "18px",
        "font-weight": "bold",
        "color": "#2c3e50",
    }))

    # English justify
    grid.add(TextNode(SAMPLE_EN, style={
        "font-size": "14px",
        "color": "#333333",
        "line-height": "1.6",
        "text-align": "justify",
        "outline": "1px dashed #cccccc",
    }))

    # Chinese justify
    grid.add(TextNode(SAMPLE_ZH, style={
        "font-size": "14px",
        "color": "#333333",
        "line-height": "1.6",
        "text-align": "justify",
        "outline": "1px dashed #cccccc",
    }))

    # ---------- Section 2: letter-spacing ----------
    grid.add(TextNode("2. letter-spacing", style={
        "font-size": "18px",
        "font-weight": "bold",
        "color": "#2c3e50",
    }))

    for ls_val in ("normal", "1px", "3px", "10px"):
        grid.add(TextNode(f"letter-spacing: {ls_val} — The quick brown fox", style={
            "font-size": "14px",
            "color": "#555555",
            "letter-spacing": ls_val,
            "outline": "1px dashed #cccccc",
        }))

    # ---------- Section 3: word-spacing ----------
    grid.add(TextNode("3. word-spacing", style={
        "font-size": "18px",
        "font-weight": "bold",
        "color": "#2c3e50",
    }))

    for ws_val in ("normal", "4px", "8px", "16px"):
        grid.add(TextNode(f"word-spacing: {ws_val} — The quick brown fox x x x x x x x x x x x x x x x x x x x x x x x", style={
            "font-size": "14px",
            "color": "#555555",
            "word-spacing": ws_val,
            "outline": "1px dashed #cccccc",
        }))

    # ---------- Section 4: combined ----------
    grid.add(TextNode("4. justify + spacing 组合", style={
        "font-size": "18px",
        "font-weight": "bold",
        "color": "#2c3e50",
    }))
    
    grid.add(TextNode("4.1 justify + letter-spacing: 2px", style={
        "font-size": "15px",
        "font-weight": "bold",
        "color": "#2c3e50",
    }))

    grid.add(TextNode(SAMPLE_EN, style={
        "font-size": "14px",
        "color": "#333333",
        "line-height": "1.6",
        "text-align": "justify",
        "letter-spacing": "4px",
        "outline": "1px dashed #cccccc",
    }))
    
    grid.add(TextNode(SAMPLE_ZH, style={
        "font-size": "14px",
        "color": "#333333",
        "line-height": "1.6",
        "text-align": "justify",
        "letter-spacing": "4px",
        "outline": "1px dashed #cccccc",
    }))
    
    grid.add(TextNode("4.2 justify + word-spacing: 4px", style={
        "font-size": "15px",
        "font-weight": "bold",
        "color": "#2c3e50",
    }))
    
    grid.add(TextNode(SAMPLE_EN, style={
        "font-size": "14px",
        "color": "#333333",
        "line-height": "1.6",
        "text-align": "justify",
        "word-spacing": "4px",
        "outline": "1px dashed #cccccc",
    }))
    
    grid.add(TextNode(SAMPLE_ZH, style={
        "font-size": "14px",
        "color": "#333333",
        "line-height": "1.6",
        "text-align": "justify",
        "word-spacing": "4px",
        "outline": "1px dashed #cccccc",
    }))

    save(grid, "43_justify_spacing.svg")


if __name__ == "__main__":
    demo_43_justify_spacing()
