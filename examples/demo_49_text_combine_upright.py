#!/usr/bin/env python3
"""Demo 49 — text-combine-upright (tate-chū-yoko / 纵中横).

Showcases horizontal-in-vertical text composition, commonly used in
East Asian typography for embedding short runs of horizontal characters
(digits, abbreviations) within vertical text.
"""
from utils import save, heading
from latticesvg import GridContainer, TextNode


def demo_49_text_combine_upright():
    heading("Demo 49: text-combine-upright (tate-chū-yoko / 纵中横)")
    
    root = GridContainer(style={
        "width": "900px",
        "grid-template-columns": "1fr",
        "justify-items": "center",
        "row-gap": "20px",
        "padding": "20px",
        "background-color": "#FFFFFF",
        "font-family": "serif",
    })

    root.add(TextNode("text-combine-upright (纵中横 / tate-chū-yoko)", style={
        "font-size": "24px",
        "font-weight": "bold",
        "color": "#2c3e50",
    }))

    # ===================================================================
    # Part 1: text-combine-upright: all — practical use cases
    # ===================================================================
    root.add(TextNode("text-combine-upright: all", style={
        "font-size": "16px",
        "font-weight": "bold",
        "color": "#333",
    }))

    grid1 = GridContainer(style={
        "width": "700px",
        "grid-template-columns": "repeat(4, 1fr)",
        "column-gap": "16px",
        "row-gap": "8px",
        "padding": "16px",
        "background-color": "#f8f9fa",
        "border": "1px solid #dee2e6",
        "font-family": "serif",
    })

    # Example texts with numbers that should be combined
    examples_all = [
        ("年号", "令和5年12月25日"),
        ("章节", "第1章第23節"),
        ("时间", "午前10時30分"),
        ("百分比", "達成率98％"),
    ]

    for label, text in examples_all:
        grid1.add(TextNode(label, style={
            "font-size": "12px",
            "font-weight": "bold",
            "color": "#6c757d",
            "text-align": "center",
        }))

    for label, text in examples_all:
        grid1.add(TextNode(text, style={
            "writing-mode": "vertical-rl",
            "text-combine-upright": "all",
            "font-size": "18px",
            "color": "#212529",
            "padding": "8px",
            "background-color": "white",
            "border": "1px solid #dee2e6",
            "height": "240px",
        }))

    root.add(grid1)

    # ===================================================================
    # Part 2: Comparison — none vs all vs digits
    # ===================================================================
    root.add(TextNode("Comparison: none / all / digits 2", style={
        "font-size": "16px",
        "font-weight": "bold",
        "color": "#333",
    }))

    grid2 = GridContainer(style={
        "width": "500px",
        "grid-template-columns": "repeat(3, 1fr)",
        "column-gap": "12px",
        "row-gap": "8px",
        "padding": "16px",
        "background-color": "#f8f9fa",
        "border": "1px solid #dee2e6",
        "font-family": "serif",
    })

    sample_text = "平成30年4月1日"
    tcu_modes = [
        ("none", "none"),
        ("all", "all"),
        ("digits 2", "digits 2"),
    ]

    for label, _ in tcu_modes:
        grid2.add(TextNode(f"tcu: {label}", style={
            "font-size": "11px",
            "font-weight": "bold",
            "color": "#6c757d",
            "text-align": "center",
        }))

    for _, tcu_val in tcu_modes:
        grid2.add(TextNode(sample_text, style={
            "writing-mode": "vertical-rl",
            "text-combine-upright": tcu_val,
            "font-size": "20px",
            "color": "#212529",
            "padding": "8px",
            "background-color": "white",
            "border": "1px solid #dee2e6",
            "height": "240px",
        }))

    root.add(grid2)

    # ===================================================================
    # Part 3: Mixed CJK + combined numbers in vertical-lr
    # ===================================================================
    root.add(TextNode("vertical-lr with text-combine-upright: all", style={
        "font-size": "16px",
        "font-weight": "bold",
        "color": "#333",
    }))

    grid3 = GridContainer(style={
        "width": "600px",
        "grid-template-columns": "1fr 1fr",
        "column-gap": "16px",
        "padding": "16px",
        "background-color": "#f8f9fa",
        "border": "1px solid #dee2e6",
        "font-family": "serif",
    })

    grid3.add(TextNode("2024年度業績報告書", style={
        "writing-mode": "vertical-lr",
        "text-combine-upright": "all",
        "font-size": "22px",
        "font-weight": "bold",
        "color": "#1a237e",
        "padding": "12px",
        "background-color": "white",
        "border": "1px solid #dee2e6",
        "height": "300px",
    }))

    grid3.add(TextNode("売上高は前年比15%増の120億円", style={
        "writing-mode": "vertical-lr",
        "text-combine-upright": "all",
        "font-size": "18px",
        "color": "#212529",
        "padding": "12px",
        "background-color": "white",
        "border": "1px solid #dee2e6",
        "height": "300px",
    }))

    root.add(grid3)

    save(root, "49_text_combine_upright.svg")


if __name__ == "__main__":
    demo_49_text_combine_upright()
