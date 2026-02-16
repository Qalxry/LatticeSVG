# CSS Properties Reference

LatticeSVG supports 63 CSS properties organized into six categories.

## Box Model (Non-Inheritable)

| Property | Default | Type | Description |
|---|---|---|---|
| `width` | `auto` | length | Element width |
| `height` | `auto` | length | Element height |
| `min-width` | `0px` | length | Minimum width |
| `max-width` | `none` | length | Maximum width |
| `min-height` | `0px` | length | Minimum height |
| `max-height` | `none` | length | Maximum height |
| `margin-top` | `0px` | length | Top margin |
| `margin-right` | `0px` | length | Right margin |
| `margin-bottom` | `0px` | length | Bottom margin |
| `margin-left` | `0px` | length | Left margin |
| `padding-top` | `0px` | length | Top padding |
| `padding-right` | `0px` | length | Right padding |
| `padding-bottom` | `0px` | length | Bottom padding |
| `padding-left` | `0px` | length | Left padding |
| `border-top-width` | `0px` | length | Top border width |
| `border-right-width` | `0px` | length | Right border width |
| `border-bottom-width` | `0px` | length | Bottom border width |
| `border-left-width` | `0px` | length | Left border width |
| `border-top-color` | `none` | color | Top border color |
| `border-right-color` | `none` | color | Right border color |
| `border-bottom-color` | `none` | color | Bottom border color |
| `border-left-color` | `none` | color | Left border color |
| `border-top-style` | `none` | keyword | Top border style (`solid`/`dashed`/`dotted`) |
| `border-right-style` | `none` | keyword | Right border style |
| `border-bottom-style` | `none` | keyword | Bottom border style |
| `border-left-style` | `none` | keyword | Left border style |
| `border-top-left-radius` | `0px` | length | Top-left corner radius |
| `border-top-right-radius` | `0px` | length | Top-right corner radius |
| `border-bottom-right-radius` | `0px` | length | Bottom-right corner radius |
| `border-bottom-left-radius` | `0px` | length | Bottom-left corner radius |
| `box-sizing` | `border-box` | keyword | Box model calculation |
| `outline-width` | `0px` | length | Outline width |
| `outline-color` | `none` | color | Outline color |
| `outline-style` | `none` | keyword | Outline style |
| `outline-offset` | `0px` | length | Outline offset |

## Shorthand Properties

| Shorthand | Expands To |
|---|---|
| `margin` | `margin-top/right/bottom/left` |
| `padding` | `padding-top/right/bottom/left` |
| `border` | `border-*-width/color/style` |
| `border-width` | `border-top/right/bottom/left-width` |
| `border-color` | `border-top/right/bottom/left-color` |
| `border-radius` | All four corner radii |
| `border-top/right/bottom/left` | Per-side width/color/style |
| `gap` | `row-gap` + `column-gap` |
| `outline` | `outline-width/color/style` |
| `background` | `background-color` or `background-image` (gradient) |

## Grid Layout (Non-Inheritable)

| Property | Default | Type | Description |
|---|---|---|---|
| `display` | `block` | keyword | Display type (`grid`/`block`) |
| `grid-template-columns` | `none` | track-list | Column track definitions |
| `grid-template-rows` | `none` | track-list | Row track definitions |
| `row-gap` | `0px` | length | Row gap |
| `column-gap` | `0px` | length | Column gap |
| `justify-items` | `stretch` | keyword | Horizontal alignment for children |
| `align-items` | `stretch` | keyword | Vertical alignment for children |
| `justify-self` | `auto` | keyword | Per-item horizontal alignment |
| `align-self` | `auto` | keyword | Per-item vertical alignment |
| `grid-template-areas` | `none` | grid-areas | Named area template |
| `grid-auto-flow` | `row` | keyword | Auto-placement direction |
| `grid-auto-rows` | `auto` | track-list | Implicit row track size |
| `grid-auto-columns` | `auto` | track-list | Implicit column track size |
| `grid-row` | `none` | grid-line | Item row position |
| `grid-column` | `none` | grid-line | Item column position |
| `grid-area` | `none` | keyword | Item named area |

### Track Value Types

| Type | Example | Description |
|---|---|---|
| Fixed pixels | `"200px"` | Fixed width |
| Flexible | `"1fr"`, `"2fr"` | Proportional remaining space |
| Percentage | `"50%"` | Relative to container |
| `auto` | `"auto"` | Content-determined |
| `min-content` | `"min-content"` | Minimum content width |
| `max-content` | `"max-content"` | Maximum content width |
| `minmax()` | `"minmax(100px, 1fr)"` | Size range |
| `repeat()` | `"repeat(3, 1fr)"` | Repeated tracks |

## Text (Inheritable)

| Property | Default | Type | Description |
|---|---|---|---|
| `font-family` | `sans-serif` | font-family | Font family |
| `font-size` | `16px` | length | Font size |
| `font-weight` | `normal` | keyword | Font weight (`normal`/`bold`) |
| `font-style` | `normal` | keyword | Font style (`normal`/`italic`) |
| `text-align` | `left` | keyword | Alignment (`left`/`center`/`right`/`justify`) |
| `line-height` | `1.2` | line-height | Line height |
| `white-space` | `normal` | keyword | Whitespace handling |
| `overflow-wrap` | `normal` | keyword | Overflow wrap (`normal`/`break-word`) |
| `word-break` | `normal` | keyword | Word break |
| `color` | `#000000` | color | Text color |
| `letter-spacing` | `normal` | length | Letter spacing |
| `word-spacing` | `normal` | length | Word spacing |
| `hyphens` | `none` | keyword | Auto-hyphenation (`none`/`auto`) |
| `lang` | `en` | keyword | Language (for hyphenation rules) |

## Text Decoration (Non-Inheritable)

| Property | Default | Type | Description |
|---|---|---|---|
| `text-decoration` | `none` | keyword | Text decoration (`underline`/`line-through`) |
| `text-overflow` | `clip` | keyword | Overflow handling (`clip`/`ellipsis`) |

## Writing Mode (Inheritable)

| Property | Default | Type | Description |
|---|---|---|---|
| `writing-mode` | `horizontal-tb` | keyword | Writing direction |
| `text-orientation` | `mixed` | keyword | Text orientation |
| `text-combine-upright` | `none` | keyword | Tate-chu-yoko |

## Visual (Non-Inheritable)

| Property | Default | Type | Description |
|---|---|---|---|
| `background-color` | `none` | color | Background color |
| `background-image` | `none` | gradient | Background image (gradient) |
| `opacity` | `1` | number | Opacity (0–1) |
| `overflow` | `visible` | keyword | Overflow (`visible`/`hidden`) |
| `clip-path` | `none` | clip-path | Clip path |
| `box-shadow` | `none` | box-shadow | Box shadow |
| `transform` | `none` | transform | Transform |
| `filter` | `none` | filter | Filter |

## Image (Non-Inheritable)

| Property | Default | Type | Description |
|---|---|---|---|
| `object-fit` | `fill` | keyword | Image scaling (`fill`/`contain`/`cover`) |

## Value Type Reference

### Lengths

Supported units: `px` (pixels), `pt` (points, 1pt = 1.333px), `%` (percentage).
Unitless numbers are interpreted as pixels.

### Colors

```python
"#ff0000"                    # hex
"#f00"                       # shorthand hex
"rgb(255, 0, 0)"             # RGB
"rgba(255, 0, 0, 0.5)"       # RGBA
"red"                        # CSS named color
"transparent"                # transparent
```

### Gradients

```python
"linear-gradient(135deg, #667eea, #764ba2)"
"radial-gradient(circle, #f093fb, #f5576c)"
```
