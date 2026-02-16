# Renderer API

The `Renderer` class converts a laid-out node tree to SVG (or PNG) output.

## Basic Usage

```python
from latticesvg import GridContainer, TextNode, Renderer

grid = GridContainer(style={"width": 400, "padding": 20, "background": "white"})
grid.add(TextNode("Hello!", style={"font-size": 24}))

renderer = Renderer()

# Output SVG file
renderer.render(grid, "output.svg")

# Output PNG file (requires cairosvg)
renderer.render_png(grid, "output.png", scale=2)

# Get drawsvg.Drawing object
drawing = renderer.render_to_drawing(grid)

# Get SVG string
svg_string = renderer.render_to_string(grid)
```

## Constructor

```python
Renderer()
```

No parameters. Creates an internal `drawsvg.Drawing` instance.

## Methods

### `render(node, output_path, *, embed_fonts=False)`

Renders a node and its descendants to an SVG file.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `node` | `Node` | *required* | Root node |
| `output_path` | `str` | *required* | Output path for SVG file |
| `embed_fonts` | `bool` | `False` | Whether to embed subsetted WOFF2 fonts |

**Returns:** `drawsvg.Drawing` — available for further use

---

### `render_to_drawing(node, *, embed_fonts=False)`

Renders a node to a `drawsvg.Drawing` object without writing any file.

!!! info "Automatic Layout"
    This method automatically runs `node.layout()`, so callers don't need to call it manually (calling it beforehand is harmless).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `node` | `Node` | *required* | Root node |
| `embed_fonts` | `bool` | `False` | Whether to embed subsetted WOFF2 fonts |

**Returns:** `drawsvg.Drawing`

---

### `render_to_string(node, *, embed_fonts=False)`

Renders a node to an SVG string (no file I/O).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `node` | `Node` | *required* | Root node |
| `embed_fonts` | `bool` | `False` | Whether to embed subsetted WOFF2 fonts |

**Returns:** `str` — SVG XML string

---

### `render_png(node, output_path, scale=1.0, *, embed_fonts=False)`

Renders to SVG first, then converts to PNG via cairosvg.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `node` | `Node` | *required* | Root node |
| `output_path` | `str` | *required* | Output path for PNG file |
| `scale` | `float` | `1.0` | Scale factor (`2.0` outputs 2x resolution) |
| `embed_fonts` | `bool` | `False` | Whether to embed fonts for accurate glyphs |

!!! warning "Dependency Required"
    PNG output requires `cairosvg`:
    ```bash
    pip install latticesvg[png]
    # or
    pip install cairosvg
    ```

---

## Font Embedding

When `embed_fonts=True`, the Renderer will:

1. Traverse the node tree to collect all used fonts and characters
2. Extract required glyphs from font files (subsetting)
3. Package subsetted fonts as WOFF2 format
4. Insert `@font-face` rules into the SVG

This makes the generated SVG fully self-contained, independent of fonts installed on the viewing device.

!!! note "Dependency"
    Font embedding requires the `fonttools` package:
    ```bash
    pip install fonttools[woff]
    ```

## Properties

| Property | Type | Description |
|---|---|---|
| `drawing` | `drawsvg.Drawing \| None` | The Drawing object from the most recent render |

## Auto-generated API Docs

::: latticesvg.render.renderer.Renderer
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3
