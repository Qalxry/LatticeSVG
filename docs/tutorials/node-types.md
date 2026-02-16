# Node Types

LatticeSVG provides 6 node types for different content needs.

## GridContainer

Container node that arranges children using CSS Grid. All layouts start with `GridContainer`.

```python
from latticesvg import GridContainer

container = GridContainer(style={
    "width": "600px",
    "padding": "20px",
    "grid-template-columns": ["1fr", "1fr"],
    "gap": "16px",
    "background-color": "#ffffff",
})
```

See the [Grid Layout Tutorial](grid-layout.md) for detailed usage.

## TextNode

Text leaf node with automatic line breaking.

```python
from latticesvg import TextNode

# Simple text
text = TextNode("Hello, World!", style={"font-size": "18px", "color": "#333"})

# Rich text (HTML markup)
rich = TextNode(
    "This is <b>bold</b> and <i>italic</i> text.",
    style={"font-size": "14px"},
    markup="html",
)

# Rich text (Markdown markup)
md = TextNode(
    "This is **bold** and *italic* text.",
    style={"font-size": "14px"},
    markup="markdown",
)
```

See [Text Typography](text-typography.md) and [Rich Text](rich-text.md) tutorials for details.

## ImageNode

Image leaf node for embedding raster images (PNG, JPEG, etc.).

```python
from latticesvg import ImageNode

# From file path
img = ImageNode("photo.png", style={"width": "300px", "height": "200px"})

# From bytes
with open("photo.png", "rb") as f:
    img = ImageNode(f.read(), style={"width": "300px"})

# From PIL Image
from PIL import Image
pil_img = Image.open("photo.png")
img = ImageNode(pil_img, style={"width": "300px"})
```

### object-fit

Control how the image scales within its container:

```python
ImageNode("photo.png", style={
    "width": "200px",
    "height": "200px",
    "object-fit": "cover",     # crop to fill
    # "contain"   — show completely, may have whitespace
    # "fill"      — stretch to fill (default)
})
```

## SVGNode

Embed SVG content from strings or files.

```python
from latticesvg import SVGNode

# From SVG string
icon = SVGNode(
    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#4CAF50"/></svg>',
    style={"width": "48px", "height": "48px"},
)

# From file
logo = SVGNode("logo.svg", is_file=True, style={"width": "200px"})

# From URL
remote = SVGNode("https://example.com/icon.svg", style={"width": "64px"})
```

<figure markdown="span">
  ![SVGNode example](../assets/images/examples/node_svg.svg){ loading=lazy }
  <figcaption>SVGNode embedding vector icons</figcaption>
</figure>

## MplNode

Embed Matplotlib figures. Pass a `matplotlib.figure.Figure` object.

```python
import matplotlib.pyplot as plt
from latticesvg import MplNode

fig, ax = plt.subplots(figsize=(4, 3))
ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
ax.set_title("Sample Chart")

chart = MplNode(fig, style={"width": "400px"})
```

<figure markdown="span">
  ![MplNode example](../assets/images/examples/node_mpl.svg){ loading=lazy }
  <figcaption>MplNode embedding a Matplotlib chart</figcaption>
</figure>

!!! warning "Note"
    `MplNode` requires Matplotlib (`pip install matplotlib`).
    Charts are embedded as SVG, preserving vector quality.

## MathNode

Render LaTeX math formulas using QuickJax (based on MathJax v4).

```python
from latticesvg import MathNode

formula = MathNode(r"E = mc^2", style={"font-size": "24px"})

integral = MathNode(
    r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}",
    style={"font-size": "20px"},
)

# Inline mode
inline = MathNode(r"\alpha + \beta = \gamma", display=False, style={"font-size": "16px"})
```

<figure markdown="span">
  ![MathNode example](../assets/images/examples/node_math.svg){ loading=lazy }
  <figcaption>MathNode rendering LaTeX formulas</figcaption>
</figure>

### Inline Math (within TextNode)

Embed math formulas in rich text:

=== "HTML Markup"

    ```python
    TextNode(
        "Einstein's equation <math>E = mc^2</math> is one of the most famous.",
        markup="html",
    )
    ```

=== "Markdown Markup"

    ```python
    TextNode(
        "Einstein's equation $E = mc^2$ is one of the most famous.",
        markup="markdown",
    )
    ```

<figure markdown="span">
  ![Inline math](../assets/images/examples/node_inline_math.svg){ loading=lazy }
  <figcaption>Inline math formulas in text</figcaption>
</figure>

## Combined Example

Mix multiple node types in a single layout:

```python
from latticesvg import GridContainer, TextNode, ImageNode, MathNode, Renderer, templates

page = GridContainer(style={**templates.REPORT_PAGE, "gap": "16px"})

page.add(TextNode("Experiment Report", style=templates.TITLE))

figure_area = GridContainer(style={
    "grid-template-columns": ["1fr"],
    "gap": "8px",
    "padding": "16px",
    "border": "1px solid #e0e0e0",
})
figure_area.add(ImageNode("experiment.png", style={"width": "100%"}))
figure_area.add(TextNode("Fig 1: Experimental Setup", style=templates.CAPTION))
page.add(figure_area)

page.add(MathNode(r"F = G \frac{m_1 m_2}{r^2}", style={"font-size": "20px"}))
page.add(TextNode("Based on the formula above...", style=templates.PARAGRAPH))

Renderer().render(page, "report.svg")
```

<figure markdown="span">
  ![Combined report](../assets/images/examples/advanced_report.svg){ loading=lazy }
  <figcaption>Report page combining multiple node types</figcaption>
</figure>
