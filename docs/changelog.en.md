# Changelog

This project follows [Semantic Versioning](https://semver.org/).

## v0.1.0 — Initial Release

First public release.

### Core Features

- **CSS Grid Layout Engine**
    - `grid-template-columns` / `grid-template-rows` (fixed, fr, auto, min-content, max-content)
    - `repeat()` and `minmax()` functions
    - `grid-template-areas` named areas
    - `grid-auto-rows` / `grid-auto-columns` auto tracks
    - `gap` / `row-gap` / `column-gap`
    - Auto-placement algorithm
    - Child spanning (`row_span`, `col_span`)
    - Container-level alignment (`justify-content`, `align-content`)
    - Item-level alignment (`justify-self`, `align-self`)

- **Text Typesetting Engine**
    - FreeType font measurement (Pillow fallback)
    - Automatic line wrapping (`white-space`: normal, nowrap, pre, pre-wrap, pre-line)
    - `overflow-wrap: break-word`
    - `text-overflow: ellipsis`
    - Auto-hyphenation (`hyphens: auto`, requires pyphen)
    - `letter-spacing` / `word-spacing`
    - Multi-font fallback chains (comma-separated `font-family`)
    - Line height control (`line-height`)
    - Vertical typesetting (`writing-mode: vertical-rl/lr`, `sideways-rl/lr`)
    - `text-orientation` / `text-combine-upright`

- **Rich Text Support**
    - HTML markup (`<b>`, `<i>`, `<span style="...">`, `<br>`, `<math>`, etc.)
    - Markdown markup (`**bold**`, `*italic*`, `` `code` ``, `$math$`, etc.)
    - Inline math formula embedding

- **Node Types**
    - `GridContainer` — Grid layout container
    - `TextNode` — Text node
    - `ImageNode` — Image node (file/URL/bytes/PIL)
    - `SVGNode` — SVG embedding node
    - `MplNode` — Matplotlib figure embedding
    - `MathNode` — LaTeX formula node

- **Visual Styling** (63 CSS properties)
    - Box model (margin, padding, border, width/height, min/max-width/height)
    - `border-radius` (independent corners)
    - `border-style` (solid, dashed, dotted, double, none)
    - `background` (solid color + linear/radial gradients)
    - `opacity`
    - `box-shadow` (single/multiple)
    - `transform` (translate, rotate, scale, skew)
    - `filter` (blur, drop-shadow, brightness, contrast, etc.)
    - `clip-path` (circle, ellipse, polygon, inset)
    - `box-sizing: border-box / content-box`

- **Render Output**
    - SVG file output (`render()`)
    - SVG string (`render_to_string()`)
    - `drawsvg.Drawing` object (`render_to_drawing()`)
    - PNG output (`render_png()`, requires cairosvg)
    - Font subsetting and embedding (`embed_fonts=True`, requires fonttools)

- **Template System**
    - 17 built-in style templates
    - `build_table()` table builder
    - `ALL_TEMPLATES` template index

- **Math Formula Engine**
    - QuickJax backend (MathJax v4 in-process)
    - Display / inline modes
    - Custom backend registration

### Dependencies

- Python ≥ 3.8
- drawsvg ≥ 2.0
- freetype-py ≥ 2.3
- quickjax ≥ 0.1.0
- Optional: cairosvg (PNG output), pyphen (hyphenation), fonttools (font embedding)
