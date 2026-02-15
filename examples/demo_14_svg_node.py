# =========================================================================
# Demo 14：SVGNode 嵌入外部 SVG
# =========================================================================

from latticesvg import GridContainer, SVGNode
from utils import heading, save

def demo_14_svg_node():
    heading("Demo 14: SVGNode 嵌入 SVG 内容")

    # 内联创建一个简单 SVG 图形
    circle_svg = '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="45" fill="#3498db" opacity="0.8"/>
  <circle cx="50" cy="50" r="25" fill="#2ecc71" opacity="0.9"/>
  <circle cx="50" cy="50" r="10" fill="#e74c3c"/>
</svg>'''

    star_svg = '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <polygon points="50,5 61,35 95,35 68,57 79,91 50,70 21,91 32,57 5,35 39,35"
           fill="#f39c12" stroke="#e67e22" stroke-width="2"/>
</svg>'''

    grid = GridContainer(style={
        "width": "500px",
        "padding": "20px",
        "background-color": "#fdfefe",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "20px",
    })

    grid.add(SVGNode(circle_svg, style={
        "background-color": "#eaf2f8",
        "padding": "10px",
    }), row=1, col=1)

    grid.add(SVGNode(star_svg, style={
        "background-color": "#fef9e7",
        "padding": "10px",
    }), row=1, col=2)

    save(grid, "14_svg_node.svg")
    
if __name__ == "__main__":
    demo_14_svg_node()