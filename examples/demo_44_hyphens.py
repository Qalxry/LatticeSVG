# =========================================================================
# Demo 44：CSS hyphens 属性（none / manual / auto）
# =========================================================================
#
# 展示三种连字符断词模式在窄列布局中的效果：
#   - hyphens: none   — 不断词（默认行为）
#   - hyphens: manual — 仅在 soft-hyphen (U+00AD) 位置断词
#   - hyphens: auto   — 基于 pyphen 字典自动断词
#
# 要使用 auto 模式，需安装 pyphen：
#   pip install pyphen
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save

# Soft-hyphen character
SHY = "\u00AD"


def _column(
    title: str,
    text: str,
    hyphens: str = "none",
    lang: str = "en",
    style: dict = {},
) -> GridContainer:
    """创建一个带标题的窄列文本卡片。"""
    col = GridContainer(style={
        "grid-template-columns": ["1fr"],
        "gap": "4px",
        "padding": "10px",
        "background-color": "#ffffff",
        "border": "1px solid #ccc",
        "border-radius": "6px",
    })
    col.add(TextNode(title, style={
        "font-size": "11px",
        "font-weight": "bold",
        "color": "#666",
    }))
    col.add(TextNode(text, style={
        "font-size": "14px",
        "color": "#222",
        "border": "1px dashed #ccc",
        "border-radius": "4px",
        "hyphens": hyphens,
        "lang": lang,
        **style,
    }))
    return col


def demo_44_hyphens():
    heading("Demo 44: CSS hyphens")

    root = GridContainer(style={
        "width": "600px",
        "padding": "16px",
        "background-color": "#f4f4f4",
        "grid-template-columns": ["1fr"],
        "gap": "20px",
    })
    
    root.add(TextNode(
        "CSS hyphens 属性：none / manual / auto",
        style={
            "font-size": "22px", "font-weight": "bold",
            "color": "#2c3e50", "text-align": "center",
            "padding-bottom": "10px",
        },
    ))

    # ---- Section 1: English comparison (narrow columns) ----
    section1_title = TextNode("English — narrow 100px columns", style={
        "font-size": "13px", "font-weight": "bold", "color": "#333",
    })
    root.add(section1_title)

    english_text = "Extraordinary circumstances necessitate unconventional methodologies."
    english_manual = (
        f"Extra{SHY}ordi{SHY}nary circum{SHY}stances "
        f"neces{SHY}si{SHY}tate uncon{SHY}ven{SHY}tional "
        f"method{SHY}olo{SHY}gies."
    )

    row1 = GridContainer(style={
        "grid-template-columns": ["100px", "100px", "100px"],
        "gap": "12px",
    })
    row1.add(_column("hyphens: none", english_text, hyphens="none"))
    row1.add(_column("hyphens: manual", english_manual, hyphens="manual"))
    row1.add(_column("hyphens: auto", english_text, hyphens="auto", lang="en"))
    root.add(row1)

    # ---- Section 2: Auto hyphens with different languages ----
    section2_title = TextNode("Auto hyphens — multiple languages", style={
        "font-size": "13px", "font-weight": "bold", "color": "#333",
    })
    root.add(section2_title)

    row2 = GridContainer(style={
        "grid-template-columns": ["140px", "140px"],
        "gap": "12px",
    })

    row2.add(_column(
        "English (en)",
        "Internationalization and interoperability requirements.",
        hyphens="auto", lang="en",
    ))
    row2.add(_column(
        "German (de)",
        "Donaudampfschifffahrtsgesellschaftskapitän ist ein langes Wort.",
        hyphens="auto", lang="de",
    ))
    root.add(row2)

    # ---- Section 3: Manual mode with soft-hyphens ----
    section3_title = TextNode("Manual mode — soft-hyphens (U+00AD)", style={
        "font-size": "13px", "font-weight": "bold", "color": "#333",
    })
    root.add(section3_title)

    row3 = GridContainer(style={
        "grid-template-columns": ["150px", "150px"],
        "gap": "12px",
    })
    row3.add(_column(
        "Without SHY",
        "Supercalifragilisticexpialidocious is a very long word.",
        hyphens="manual",
    ))
    row3.add(_column(
        "With SHY markers",
        f"Su{SHY}per{SHY}cal{SHY}i{SHY}frag{SHY}i{SHY}lis{SHY}tic{SHY}"
        f"ex{SHY}pi{SHY}al{SHY}i{SHY}do{SHY}cious is a very long word.",
        hyphens="manual",
    ))
    root.add(row3)

    # ---- Section 4: justify with auto hyphens ----
    section4_title = TextNode("Justify alignment with auto hyphens", style={
        "font-size": "13px", "font-weight": "bold", "color": "#333",
    })
    root.add(section4_title)
    justify_text = (
        "Another paragraph to demonstrate hyphenation: antidisestablishmentalism is a long word that might break with a hyphen. "
        "Also, consider the word pneumonoultramicroscopicsilicovolcanoconiosis which is even longer. "
        "In LaTeX, such words would be hyphenated according to language rules, improving the justified text appearance. "
        "The browser's hyphenation engine (when supported) will insert soft hyphens at appropriate syllable boundaries."
    )
    root.add(_column(
        "Justify + auto hyphens",
        justify_text,
        hyphens="auto", 
        lang="en", 
        style={"text-align": "justify"},
    ))
    
    save(root, "44_hyphens.svg")


if __name__ == "__main__":
    demo_44_hyphens()
