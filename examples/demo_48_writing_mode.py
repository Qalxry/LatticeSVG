#!/usr/bin/env python3
"""Demo 48 — writing-mode: 5 modes + text-orientation.

Showcases vertical row headers in a table-like layout and all five
``writing-mode`` values with three ``text-orientation`` options.
"""
from utils import save, heading
from latticesvg import GridContainer, TextNode


def demo_48_writing_mode():
    heading("Demo 48: CSS Writing Modes and Text Orientation in LatticeSVG")
    
    root = GridContainer(style={
        "width": "900px",
        "grid-template-columns": "1fr",
        "justify-items": "center",
        "row-gap": "20px",
        "padding": "20px",
        "background-color": "#FFFFFF",
    })
    
    root.add(TextNode("CSS Writing Modes and Text Orientation in LatticeSVG", style={
        "font-size": "24px",
        "font-weight": "bold",
        "color": "#2c3e50",
    }))
    
    # ===================================================================
    # Part 1: Vertical row headers (practical use case)
    # ===================================================================
    root.add(TextNode("Table with vertical row headers (writing-mode: sideways-lr)", style={
        "font-size": "16px",
        "font-weight": "bold",
        "color": "#333",
    }))
    
    grid1 = GridContainer(style={
        "width": "600px",
        "height": "auto",
        "grid-template-columns": "40px 1fr 1fr 1fr",
        "grid-template-rows": "40px repeat(3, 60px)",
        "row-gap": "2px",
        "column-gap": "2px",
        "background-color": "#f0f0f0",
        "padding": "10px",
        "border": "1px solid #ccc",
    })

    # Column headers
    for ci, hdr in enumerate(["", "Q1", "Q2", "Q3"]):
        grid1.add(TextNode(hdr, style={
            "background-color": "#3498db",
            "color": "white",
            "font-weight": "bold",
            "font-size": "14px",
            "text-align": "center",
            "display": "grid",
            "align-items": "center",
            "padding": "4px",
        }), row=1, col=ci + 1)

    # Row headers with sideways-rl writing mode
    row_labels = ["销售额", "成本", "利润"]
    for ri, label in enumerate(row_labels):
        grid1.add(TextNode(label, style={
            "writing-mode": "sideways-lr",
            "background-color": "#2c3e50",
            "color": "white",
            "font-size": "12px",
            "text-align": "center",
            "display": "grid",
            "align-items": "center",
            "padding": "2px",
        }), row=ri + 2, col=1)

    # Data cells
    data = [
        ["¥120万", "¥150万", "¥180万"],
        ["¥80万", "¥90万", "¥100万"],
        ["¥40万", "¥60万", "¥80万"],
    ]
    for ri, row in enumerate(data):
        for ci, val in enumerate(row):
            grid1.add(TextNode(val, style={
                "background-color": "white",
                "font-size": "13px",
                "text-align": "center",
                "display": "grid",
                "align-items": "center",
                "padding": "4px",
            }), row=ri + 2, col=ci + 2)
            
    root.add(grid1)

    # ===================================================================
    # Part 2: All 5 writing modes side by side
    # ===================================================================
    root.add(TextNode("All 5 writing modes with the same text", style={
        "font-size": "16px",
        "font-weight": "bold",
        "color": "#333",
    }))
    
    modes = [
        ("horizontal-tb", "Hello 你好"),
        ("vertical-rl", "Hello 你好"),
        ("vertical-lr", "Hello 你好"),
        ("sideways-rl", "Hello 你好"),
        ("sideways-lr", "Hello 你好"),
    ]

    grid2 = GridContainer(style={
        "width": "700px",
        "height": "auto",
        "grid-template-columns": f"repeat({len(modes)}, 1fr)",
        "grid-template-rows": "30px 200px",
        "column-gap": "8px",
        "row-gap": "4px",
        "padding": "10px",
        "background-color": "#fafafa",
        "border": "1px solid #ccc",
    })

    for ci, (mode, text) in enumerate(modes):
        # Label
        grid2.add(TextNode(mode, style={
            "font-size": "11px",
            "text-align": "center",
            "color": "#666",
        }), row=1, col=ci + 1)
        # Text cell
        grid2.add(TextNode(text, style={
            "writing-mode": mode,
            # "text-align": "center",
            "background-color": "white",
            "font-size": "18px",
            "padding": "8px",
            "border": "1px solid #ccc",
        }), row=2, col=ci + 1)

    root.add(grid2)
    
    # ===================================================================
    # Part 3: text-orientation variations (vertical-rl)
    # ===================================================================
    root.add(TextNode("text-orientation variations (writing-mode: vertical-rl)", style={
        "font-size": "16px",
        "font-weight": "bold",
        "color": "#333",
    }))
    
    orientations = ["mixed", "upright", "sideways"]

    grid3 = GridContainer(style={
        "width": "800px",
        # "height": "auto",
        "grid-template-columns": f"repeat({len(orientations)}, 1fr)",
        "grid-template-rows": "30px 300px",
        "column-gap": "8px",
        "row-gap": "4px",
        "padding": "10px",
        "background-color": "#fafafa",
        "word-spacing": "1em",
        "font-family": "serif",
        "border": "1px solid #ccc",
    })

    sample_text = "民國105年4月29日\nCSS竖排Text排版\nabc 123 The quick brown fox jumps over the lazy dog."
    for ci, orient in enumerate(orientations):
        grid3.add(TextNode(f"orientation: {orient}", style={
            "font-size": "11px",
            "text-align": "center",
            "color": "#666",
        }), row=1, col=ci + 1)
        grid3.add(TextNode(sample_text, style={
            "writing-mode": "vertical-rl",
            "text-orientation": orient,
            "white-space": "pre-line",
            "background-color": "white",
            "font-size": "20px",
            "padding": "10px",
            "border": "1px solid #ccc",
        }), row=2, col=ci + 1)

    root.add(grid3)
    save(root, "48_vertical_row_headers.svg")


if __name__ == "__main__":
    demo_48_writing_mode()
