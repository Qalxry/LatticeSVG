# Node Types API

This page provides detailed documentation for all node type constructors, properties, and methods.

## Rect

An axis-aligned rectangle with top-left origin (y-axis points down).

```python
from latticesvg import Rect

r = Rect(x=10, y=20, width=100, height=50)
print(r.right)   # 110.0
print(r.bottom)  # 70.0
r2 = r.copy()
```

| Property | Type | Description |
|---|---|---|
| `x` | `float` | Top-left x coordinate (default 0.0) |
| `y` | `float` | Top-left y coordinate (default 0.0) |
| `width` | `float` | Width (default 0.0) |
| `height` | `float` | Height (default 0.0) |
| `right` | `float` | Read-only, equals `x + width` |
| `bottom` | `float` | Read-only, equals `y + height` |

| Method | Returns | Description |
|---|---|---|
| `copy()` | `Rect` | Returns a copy |

---

## LayoutConstraints

Constraints passed from parent to child during layout.

```python
from latticesvg import LayoutConstraints

c = LayoutConstraints(available_width=800, available_height=600)
```

| Property | Type | Default | Description |
|---|---|---|---|
| `available_width` | `float \| None` | `None` | Available width |
| `available_height` | `float \| None` | `None` | Available height |

---

## Node (Base Class)

Abstract base for all layoutable elements. Subclasses must implement `measure()` and `layout()`.

```python
from latticesvg import Node

node = Node(style={"width": 100, "height": 50, "background": "#f0f0f0"})
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `style` | `dict[str, Any] \| None` | `None` | CSS style properties dict |
| `parent` | `Node \| None` | `None` | Parent node (usually set automatically by `add()`) |

### Properties

| Property | Type | Description |
|---|---|---|
| `style` | `ComputedStyle` | Computed style object |
| `parent` | `Node \| None` | Parent node |
| `children` | `list[Node]` | Child node list |
| `border_box` | `Rect` | Border box rect after layout |
| `padding_box` | `Rect` | Padding box rect after layout |
| `content_box` | `Rect` | Content box rect after layout |
| `placement` | `PlacementHint` | Grid placement info |

### Methods

#### `add(child, *, row=None, col=None, row_span=1, col_span=1, area=None)`

Append a child node and optionally set grid placement.

| Parameter | Type | Description |
|---|---|---|
| `child` | `Node` | Child node to add |
| `row` | `int \| None` | Row start position (1-based CSS Grid line number) |
| `col` | `int \| None` | Column start position (1-based CSS Grid line number) |
| `row_span` | `int` | Number of rows to span (default 1) |
| `col_span` | `int` | Number of columns to span (default 1) |
| `area` | `str \| None` | Named grid area |

**Returns:** The added child node (enables chaining)

```python
grid.add(child, row=1, col=2, row_span=1, col_span=2)
grid.add(child, area="header")
```

#### `measure(constraints) → (min_w, max_w, intrinsic_h)`

Returns the node's minimum content width, maximum content width, and intrinsic height. Called by the grid solver.

#### `layout(constraints)`

Computes `border_box`, `padding_box`, and `content_box`. Must be implemented by subclasses.

---

## GridContainer

A CSS Grid layout container node that arranges children using grid layout.

```python
from latticesvg import GridContainer

grid = GridContainer(style={
    "grid-template-columns": "200px 1fr",
    "grid-template-rows": "auto auto",
    "gap": 10,
    "width": 600,
    "padding": 20,
})
```

### Constructor Parameters

Inherits from `Node`, accepts `style` and `parent`. `display` is automatically set to `"grid"`.

### Methods

#### `layout(constraints=None, available_width=None, available_height=None)`

Runs the full layout computation. As a root node, you can pass the available width directly:

```python
grid.layout(available_width=800)
```

If `available_width` is not provided, the `width` style property is used, or defaults to 800.

#### `measure(constraints) → (min_w, max_w, intrinsic_h)`

Used for nested grid size calculations. Results are cached.

---

## TextNode

Text node supporting automatic line wrapping, rich text markup, and vertical typesetting.

```python
from latticesvg import TextNode

# Plain text
text = TextNode("Hello, World!", style={"font-size": 24, "color": "#333"})

# HTML rich text
rich = TextNode("<b>Bold</b> and <i>italic</i>", markup="html")

# Markdown rich text
md = TextNode("**Bold** and *italic*", markup="markdown")
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `text` | `str` | *required* | Text content |
| `style` | `dict \| None` | `None` | Style properties |
| `parent` | `Node \| None` | `None` | Parent node |
| `markup` | `str` | `"none"` | Markup mode: `"none"`, `"html"`, `"markdown"` |

### Properties

| Property | Type | Description |
|---|---|---|
| `text` | `str` | Raw text content |
| `markup` | `str` | Markup mode |
| `lines` | `list[Line]` | Lines after layout (plain text mode) |

### Key Style Properties

TextNode responds to these style properties (see [CSS Properties Reference](../css-properties.md)):

- **Font:** `font-family`, `font-size`, `font-weight`, `font-style`
- **Typography:** `text-align`, `line-height`, `letter-spacing`, `word-spacing`
- **Wrapping:** `white-space`, `overflow-wrap`, `hyphens`, `lang`
- **Overflow:** `overflow`, `text-overflow`
- **Vertical:** `writing-mode`, `text-orientation`, `text-combine-upright`

---

## ImageNode

Image node supporting multiple image sources and `object-fit` scaling.

```python
from latticesvg import ImageNode

# File path
img = ImageNode("photo.png", style={"width": 200, "height": 150})

# URL
img = ImageNode("https://example.com/image.png")

# bytes
img = ImageNode(raw_bytes, object_fit="contain")

# PIL Image
from PIL import Image
img = ImageNode(Image.open("photo.png"), object_fit="cover")
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `src` | `str \| bytes \| PIL.Image` | *required* | Image source (path/URL/bytes/PIL) |
| `style` | `dict \| None` | `None` | Style properties |
| `parent` | `Node \| None` | `None` | Parent node |
| `object_fit` | `str \| None` | `None` | Scaling mode |

### object-fit Modes

| Value | Description |
|---|---|
| `"fill"` | Stretch to fill (default, may distort) |
| `"contain"` | Scale proportionally, fully contained |
| `"cover"` | Scale proportionally, fully covering |
| `"none"` | Original size, no scaling |

### Properties

| Property | Type | Description |
|---|---|---|
| `intrinsic_width` | `float` | Image intrinsic width (read-only, lazily loaded) |
| `intrinsic_height` | `float` | Image intrinsic height (read-only, lazily loaded) |

---

## SVGNode

A node for embedding external SVG content.

```python
from latticesvg import SVGNode

# SVG string
svg = SVGNode('<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>')

# File
svg = SVGNode("icon.svg", is_file=True)

# URL
svg = SVGNode("https://example.com/icon.svg")
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `svg` | `str` | *required* | SVG content (string/path/URL) |
| `style` | `dict \| None` | `None` | Style properties (keyword-only) |
| `parent` | `Node \| None` | `None` | Parent node (keyword-only) |
| `is_file` | `bool` | `False` | Whether to treat as file path (keyword-only) |

Intrinsic size is parsed from the `viewBox` or `width`/`height` attributes.

---

## MplNode

Matplotlib figure embedding node.

```python
import matplotlib.pyplot as plt
from latticesvg import MplNode

fig, ax = plt.subplots(figsize=(4, 3))
ax.plot([1, 2, 3], [1, 4, 9])

node = MplNode(fig, style={"padding": 10})
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `figure` | `matplotlib.figure.Figure` | *required* | Matplotlib figure object |
| `style` | `dict \| None` | `None` | Style properties |
| `parent` | `Node \| None` | `None` | Parent node |

!!! note "Important Notes"
    - All Matplotlib customization should be done **before** creating the node
    - The figure is automatically resized during layout to match allocated space
    - SVG coordinates use 72 DPI uniformly

---

## MathNode

LaTeX formula rendering node based on QuickJax (MathJax v4).

```python
from latticesvg import MathNode

# display mode (standalone formula)
formula = MathNode(r"E = mc^2", style={"font-size": 24})

# inline mode
inline = MathNode(r"\alpha + \beta", display=False)
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `latex` | `str` | *required* | LaTeX math expression |
| `style` | `dict \| None` | `None` | Style properties (keyword-only) |
| `backend` | `str \| None` | `None` | Backend name, None uses default (keyword-only) |
| `display` | `bool` | `True` | Whether to use display mode (keyword-only) |
| `parent` | `Node \| None` | `None` | Parent node (keyword-only) |

### Properties

| Property | Type | Description |
|---|---|---|
| `latex` | `str` | LaTeX source |
| `display` | `bool` | display/inline mode |
| `scale_x` | `float` | Horizontal scale factor after layout |
| `scale_y` | `float` | Vertical scale factor after layout |

## Auto-generated API Docs

::: latticesvg.nodes
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3
