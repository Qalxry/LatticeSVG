#!/usr/bin/env python3
"""Demo 50 — text-combine-upright compatibility with other CSS properties.

Tests TCU interaction with:
  1. text-orientation (mixed / upright / sideways)
  2. text-align (left / center / right)
  3. word-spacing
  4. letter-spacing
  5. font-size variations
  6. writing-mode (vertical-rl vs vertical-lr)
"""
from utils import save, heading
from latticesvg import GridContainer, TextNode


def demo_50_tcu_compat():
    heading("Demo 50: text-combine-upright compatibility tests")
    
    root = GridContainer(style={
        "width": "1000px",
        "grid-template-columns": "1fr",
        "justify-items": "center",
        "row-gap": "24px",
        "padding": "20px",
        "background-color": "#FFFFFF",
        "font-family": "serif",
    })

    root.add(TextNode("text-combine-upright: compatibility tests", style={
        "font-size": "22px",
        "font-weight": "bold",
        "color": "#2c3e50",
    }))

    sample = "令和5年12月25日"

    # =================================================================
    # Test 1: text-orientation interaction
    # =================================================================
    root.add(TextNode("Test 1: text-orientation × tcu: all", style={
        "font-size": "14px", "font-weight": "bold", "color": "#555",
    }))

    g1 = GridContainer(style={
        "width": "600px",
        "grid-template-columns": "repeat(3, 1fr)",
        "column-gap": "12px",
        "row-gap": "6px",
        "padding": "12px",
        "background-color": "#f8f9fa",
        "border": "1px solid #dee2e6",
        "font-family": "serif",
    })

    for orient in ["mixed", "upright", "sideways"]:
        g1.add(TextNode(f"orientation: {orient}", style={
            "font-size": "10px", "color": "#888", "text-align": "center",
        }))

    for orient in ["mixed", "upright", "sideways"]:
        g1.add(TextNode(sample, style={
            "writing-mode": "vertical-rl",
            "text-combine-upright": "all",
            "text-orientation": orient,
            "font-size": "16px",
            "color": "#212529",
            "padding": "8px",
            "background-color": "white",
            "border": "1px solid #dee2e6",
            "height": "220px",
        }))

    root.add(g1)

    # =================================================================
    # Test 2: text-align interaction
    # =================================================================
    root.add(TextNode("Test 2: text-align × tcu: all", style={
        "font-size": "14px", "font-weight": "bold", "color": "#555",
    }))

    g2 = GridContainer(style={
        "width": "600px",
        "grid-template-columns": "repeat(3, 1fr)",
        "column-gap": "12px",
        "row-gap": "6px",
        "padding": "12px",
        "background-color": "#f8f9fa",
        "border": "1px solid #dee2e6",
        "font-family": "serif",
    })

    for align in ["left", "center", "right"]:
        g2.add(TextNode(f"text-align: {align}", style={
            "font-size": "10px", "color": "#888", "text-align": "center",
        }))

    short_text = "第23節"
    for align in ["left", "center", "right"]:
        g2.add(TextNode(short_text, style={
            "writing-mode": "vertical-rl",
            "text-combine-upright": "all",
            "text-align": align,
            "font-size": "18px",
            "color": "#212529",
            "padding": "8px",
            "background-color": "white",
            "border": "1px solid #dee2e6",
            "height": "200px",
        }))

    root.add(g2)

    # =================================================================
    # Test 3: word-spacing interaction
    # =================================================================
    root.add(TextNode("Test 3: word-spacing × tcu: all", style={
        "font-size": "14px", "font-weight": "bold", "color": "#555",
    }))

    g3 = GridContainer(style={
        "width": "600px",
        "grid-template-columns": "repeat(3, 1fr)",
        "column-gap": "12px",
        "row-gap": "6px",
        "padding": "12px",
        "background-color": "#f8f9fa",
        "border": "1px solid #dee2e6",
        "font-family": "serif",
    })

    ws_text = "売上 120億 円"  # spaces between words
    for ws in ["0px", "8px", "16px"]:
        g3.add(TextNode(f"word-spacing: {ws}", style={
            "font-size": "10px", "color": "#888", "text-align": "center",
        }))

    for ws in ["0px", "8px", "16px"]:
        g3.add(TextNode(ws_text, style={
            "writing-mode": "vertical-rl",
            "text-combine-upright": "all",
            "word-spacing": ws,
            "font-size": "16px",
            "color": "#212529",
            "padding": "8px",
            "background-color": "white",
            "border": "1px solid #dee2e6",
            "height": "240px",
        }))

    root.add(g3)

    # =================================================================
    # Test 4: letter-spacing interaction
    # =================================================================
    root.add(TextNode("Test 4: letter-spacing × tcu: all", style={
        "font-size": "14px", "font-weight": "bold", "color": "#555",
    }))

    g4 = GridContainer(style={
        "width": "600px",
        "grid-template-columns": "repeat(3, 1fr)",
        "column-gap": "12px",
        "row-gap": "6px",
        "padding": "12px",
        "background-color": "#f8f9fa",
        "border": "1px solid #dee2e6",
        "font-family": "serif",
    })

    for ls in ["0px", "4px", "8px"]:
        g4.add(TextNode(f"letter-spacing: {ls}", style={
            "font-size": "10px", "color": "#888", "text-align": "center",
        }))

    for ls in ["0px", "4px", "8px"]:
        g4.add(TextNode(sample, style={
            "writing-mode": "vertical-rl",
            "text-combine-upright": "all",
            "letter-spacing": ls,
            "font-size": "16px",
            "color": "#212529",
            "padding": "8px",
            "background-color": "white",
            "border": "1px solid #dee2e6",
            "height": "280px",
        }))

    root.add(g4)

    # =================================================================
    # Test 5: font-size variations
    # =================================================================
    root.add(TextNode("Test 5: font-size × tcu: all", style={
        "font-size": "14px", "font-weight": "bold", "color": "#555",
    }))

    g5 = GridContainer(style={
        "width": "600px",
        "grid-template-columns": "repeat(3, 1fr)",
        "column-gap": "12px",
        "row-gap": "6px",
        "padding": "12px",
        "background-color": "#f8f9fa",
        "border": "1px solid #dee2e6",
        "font-family": "serif",
    })

    for fs in ["12px", "18px", "24px"]:
        g5.add(TextNode(f"font-size: {fs}", style={
            "font-size": "10px", "color": "#888", "text-align": "center",
        }))

    for fs in ["12px", "18px", "24px"]:
        g5.add(TextNode("達成率98％", style={
            "writing-mode": "vertical-rl",
            "text-combine-upright": "all",
            "font-size": fs,
            "color": "#212529",
            "padding": "8px",
            "background-color": "white",
            "border": "1px solid #dee2e6",
            "height": "200px",
        }))

    root.add(g5)

    # =================================================================
    # Test 6: vertical-rl vs vertical-lr
    # =================================================================
    root.add(TextNode("Test 6: vertical-rl vs vertical-lr × tcu: all", style={
        "font-size": "14px", "font-weight": "bold", "color": "#555",
    }))

    g6 = GridContainer(style={
        "width": "400px",
        "grid-template-columns": "repeat(2, 1fr)",
        "column-gap": "12px",
        "row-gap": "6px",
        "padding": "12px",
        "background-color": "#f8f9fa",
        "border": "1px solid #dee2e6",
        "font-family": "serif",
    })

    for wm in ["vertical-rl", "vertical-lr"]:
        g6.add(TextNode(wm, style={
            "font-size": "10px", "color": "#888", "text-align": "center",
        }))

    for wm in ["vertical-rl", "vertical-lr"]:
        g6.add(TextNode("2024年度報告", style={
            "writing-mode": wm,
            "text-combine-upright": "all",
            "font-size": "20px",
            "color": "#212529",
            "padding": "8px",
            "background-color": "white",
            "border": "1px solid #dee2e6",
            "height": "240px",
        }))

    root.add(g6)

    # =================================================================
    # Test 7: display:grid + align-items:center (cross-axis centering)
    # =================================================================
    root.add(TextNode("Test 7: display:grid + align-items:center × tcu: all", style={
        "font-size": "14px", "font-weight": "bold", "color": "#555",
    }))

    g7 = GridContainer(style={
        "width": "600px",
        "grid-template-columns": "repeat(3, 1fr)",
        "column-gap": "12px",
        "row-gap": "6px",
        "padding": "12px",
        "background-color": "#f8f9fa",
        "border": "1px solid #dee2e6",
        "font-family": "serif",
    })

    for ai in ["start", "center", "end"]:
        g7.add(TextNode(f"align-items: {ai}", style={
            "font-size": "10px", "color": "#888", "text-align": "center",
        }))

    # Note: align-items on TextNode requires display:grid
    # For vertical text, align-items controls the inline-axis (horizontal)
    # positioning within the column.
    for ai in ["start", "center", "end"]:
        g7.add(TextNode("第23節", style={
            "writing-mode": "vertical-rl",
            "text-combine-upright": "all",
            "display": "grid",
            "align-items": ai,
            "font-size": "18px",
            "color": "#212529",
            "padding": "8px",
            "background-color": "white",
            "border": "1px solid #dee2e6",
            "height": "200px",
        }))

    root.add(g7)

    save(root, "50_tcu_compat.svg")


if __name__ == "__main__":
    demo_50_tcu_compat()
