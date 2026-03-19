# LatticeSVG

A declarative vector layout engine powered by CSS Grid. Describe layouts with Python dicts, get pixel-perfect SVG/PNG output.

## Features

- **Full CSS Grid Level 1** — fixed tracks, `fr` units, `minmax()`, `repeat()`, named areas, auto-placement
- **Precise text typesetting** — FreeType-based glyph measurement, auto line-breaking, CJK support, rich text (HTML/Markdown), vertical writing
- **Multiple node types** — `TextNode`, `ImageNode`, `SVGNode`, `MplNode` (Matplotlib with auto font sync), `MathNode` (LaTeX)
- **Font query API** — `get_font_path()`, `list_fonts()` for programmatic font discovery
- **63 CSS properties** — box model, border-radius, gradients, shadows, transforms, filters, clip-path, opacity
- **SVG & PNG output** — vector SVG by default, optional high-res PNG via CairoSVG, WOFF2 font embedding

## Installation

```bash
pip install latticesvg

# For PNG output
pip install latticesvg[png]

# For auto-hyphenation
pip install latticesvg[hyphens]
```

## Quick Start

```python
from latticesvg import GridContainer, TextNode, Renderer

page = GridContainer(style={
    "width": "600px",
    "padding": "24px",
    "grid-template-columns": ["1fr", "1fr"],
    "gap": "16px",
    "background-color": "#ffffff",
})

page.add(TextNode("Hello", style={"font-size": "24px", "color": "#2c3e50"}))
page.add(TextNode("World", style={"font-size": "24px", "color": "#e74c3c"}))

Renderer().render(page, "hello.svg")
```

## Documentation

Full documentation is available at [https://qalxry.github.io/LatticeSVG/](https://qalxry.github.io/LatticeSVG/)

## Dependencies

- Python ≥ 3.8
- [drawsvg](https://pypi.org/project/drawsvg/) — SVG generation
- [freetype-py](https://pypi.org/project/freetype-py/) — text measurement
- [quickjax](https://pypi.org/project/quickjax/) — LaTeX math rendering
- [cairosvg](https://pypi.org/project/cairosvg/) (optional) — PNG conversion

## License

MIT
