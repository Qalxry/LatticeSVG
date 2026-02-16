# API Overview

LatticeSVG's public API exports 13 symbols from the top-level package.

## Quick Import

```python
from latticesvg import (
    # Node types
    Node,            # Abstract base class
    GridContainer,   # Grid container
    TextNode,        # Text node
    ImageNode,       # Image node
    SVGNode,         # SVG embedding node
    MplNode,         # Matplotlib node
    MathNode,        # LaTeX formula node

    # Geometry types
    Rect,            # Rectangle
    LayoutConstraints,  # Layout constraints

    # Rendering
    Renderer,        # SVG/PNG renderer

    # Style
    ComputedStyle,   # Computed style object

    # Templates
    templates,       # Built-in style templates module
    build_table,     # Table builder function
)
```

## Module Structure

| Module | Responsibility | Key Exports |
|---|---|---|
| [`latticesvg.nodes`](nodes.md) | Node type definitions | `Node`, `GridContainer`, `TextNode`, `ImageNode`, `SVGNode`, `MplNode`, `MathNode` |
| [`latticesvg.render`](renderer.md) | SVG rendering | `Renderer` |
| [`latticesvg.style`](style.md) | Style parsing & computation | `ComputedStyle`, `parse_value`, `PROPERTY_REGISTRY` |
| [`latticesvg.text`](text.md) | Text measurement & layout | `FontManager`, `measure_text`, `break_lines` |
| [`latticesvg.layout`](layout.md) | Grid layout solver | `GridSolver` |
| [`latticesvg.markup`](markup.md) | Rich text markup parsing | `TextSpan`, `parse_markup`, `parse_html`, `parse_markdown` |
| [`latticesvg.math`](math.md) | Mathematical formula rendering | `MathBackend`, `QuickJaxBackend`, `SVGFragment` |
| [`latticesvg.templates`](../templates.md) | Built-in style templates | 17 templates + `build_table()` |

## Version

```python
import latticesvg
print(latticesvg.__version__)  # "0.1.0"
```
