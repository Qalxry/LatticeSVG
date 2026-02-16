# Styling & Visuals

LatticeSVG supports a rich set of CSS visual styling properties.

## Box Model

Every node has a full box model: `margin`, `padding`, `border`.

```python
from latticesvg import GridContainer, TextNode, Renderer

card = GridContainer(style={
    "width": "300px",
    "margin": "20px",
    "padding": "16px",
    "border": "2px solid #3498db",
    "background-color": "#ffffff",
    "grid-template-columns": ["1fr"],
})

card.add(TextNode("Card with full box model", style={"font-size": "14px"}))
```

<figure markdown="span">
  ![Box model](../assets/images/examples/style_box_model.svg){ loading=lazy }
  <figcaption>Box model: margin, padding, border</figcaption>
</figure>

!!! info "box-sizing"
    Default is `box-sizing: border-box` — `width` includes padding and border.

### Per-Direction Settings

```python
style = {
    "padding-top": "8px",
    "padding-right": "16px",
    "padding-bottom": "8px",
    "padding-left": "16px",
    # Or use shorthand
    "padding": "8px 16px",
}
```

## Border Radius

```python
# Uniform
TextNode("Rounded card", style={
    "padding": "16px", "background-color": "#e3f2fd", "border-radius": "8px",
})

# Independent corners
TextNode("Asymmetric", style={
    "padding": "16px",
    "background-color": "#fce4ec",
    "border-top-left-radius": "20px",
    "border-bottom-right-radius": "20px",
})
```

<figure markdown="span">
  ![Border radius](../assets/images/examples/style_border_radius.svg){ loading=lazy }
  <figcaption>Uniform and independent border-radius</figcaption>
</figure>

## Border Styles

Supports `solid`, `dashed`, and `dotted` styles, independently per side:

```python
TextNode("Dashed border", style={"padding": "16px", "border": "2px dashed #e74c3c"})

TextNode("Mixed borders", style={
    "padding": "16px",
    "border-top": "3px solid #2ecc71",
    "border-right": "2px dashed #3498db",
    "border-bottom": "1px dotted #9b59b6",
    "border-left": "2px solid #e67e22",
})
```

<figure markdown="span">
  ![Border styles](../assets/images/examples/style_border_style.svg){ loading=lazy }
  <figcaption>Solid, dashed, and dotted border styles</figcaption>
</figure>

## Opacity

```python
TextNode("Semi-transparent", style={"opacity": "0.5", "font-size": "24px", "color": "#e74c3c"})
```

<figure markdown="span">
  ![Opacity](../assets/images/examples/style_opacity.svg){ loading=lazy }
  <figcaption>Opacity effect</figcaption>
</figure>

## Gradient Backgrounds

```python
# Linear gradient
TextNode("Linear", style={
    "padding": "24px", "color": "#fff",
    "background": "linear-gradient(135deg, #667eea, #764ba2)",
})

# Radial gradient
TextNode("Radial", style={
    "padding": "24px", "color": "#fff",
    "background": "radial-gradient(circle, #f093fb, #f5576c)",
})
```

<figure markdown="span">
  ![Gradients](../assets/images/examples/style_gradient.svg){ loading=lazy }
  <figcaption>Linear and radial gradients</figcaption>
</figure>

## Box Shadow

```python
TextNode("Shadow card", style={
    "padding": "20px", "background-color": "#fff", "border-radius": "8px",
    "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
})

# Multiple shadows
TextNode("Multiple shadows", style={
    "padding": "20px", "background-color": "#fff",
    "box-shadow": "0 2px 4px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1)",
})
```

<figure markdown="span">
  ![Box shadow](../assets/images/examples/style_box_shadow.svg){ loading=lazy }
  <figcaption>Single and multiple box shadows</figcaption>
</figure>

## Transforms

```python
TextNode("Rotated", style={"transform": "rotate(5deg)", "padding": "16px", "background-color": "#e8eaf6"})
TextNode("Scaled", style={"transform": "scale(1.2)"})
TextNode("Combined", style={"transform": "rotate(-3deg) scale(0.9) translate(10px, 5px)"})
```

<figure markdown="span">
  ![Transforms](../assets/images/examples/style_transform.svg){ loading=lazy }
  <figcaption>Rotate, scale, and translate transforms</figcaption>
</figure>

## Filters

```python
TextNode("Blurred", style={"filter": "blur(2px)"})
ImageNode("photo.png", style={"filter": "grayscale(100%)", "width": "200px"})
ImageNode("photo.png", style={"filter": "brightness(1.2) contrast(1.1)", "width": "200px"})
```

<figure markdown="span">
  ![Filters](../assets/images/examples/style_filter.svg){ loading=lazy }
  <figcaption>CSS filter effects</figcaption>
</figure>

## Clip Path

```python
ImageNode("avatar.png", style={"width": "100px", "height": "100px", "clip-path": "circle(50%)"})
ImageNode("photo.png", style={"width": "200px", "clip-path": "ellipse(40% 50% at 50% 50%)"})
TextNode("Hexagon", style={
    "padding": "40px", "background-color": "#4caf50", "color": "#fff",
    "clip-path": "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
})
```

<figure markdown="span">
  ![Clip path](../assets/images/examples/style_clip_path.svg){ loading=lazy }
  <figcaption>Circle, polygon, and inset clip paths</figcaption>
</figure>

## Outline

```python
TextNode("Outlined", style={
    "padding": "16px", "background-color": "#fff",
    "outline": "2px solid #2196f3", "outline-offset": "4px",
})
```

## Full Example: Material Card

```python
card = GridContainer(style={
    "width": "320px",
    "background-color": "#ffffff",
    "border-radius": "12px",
    "box-shadow": "0 2px 8px rgba(0,0,0,0.12), 0 1px 3px rgba(0,0,0,0.08)",
    "overflow": "hidden",
    "grid-template-columns": ["1fr"],
    "gap": "0px",
})

card.add(TextNode("Feature Card", style={
    "padding": "24px",
    "background": "linear-gradient(135deg, #667eea, #764ba2)",
    "color": "#ffffff", "font-size": "20px", "font-weight": "bold",
}))

card.add(TextNode(
    "A complete Material Design card example showcasing border-radius, "
    "shadows, gradients, and other visual effects.",
    style={"padding": "16px 24px", "font-size": "14px", "color": "#555", "line-height": "1.6"},
))
```
