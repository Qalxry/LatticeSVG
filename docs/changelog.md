# Changelog

This project follows [Semantic Versioning](https://semver.org/).

## v0.1.3 — Matplotlib Font Helpers & Fallback Fix (2026-03-19)

### New Features

- **Matplotlib font helpers** (`latticesvg.text`)
    - `mpl_font_context(font_family)` — context manager that temporarily applies LatticeSVG fonts to matplotlib; restores on exit.
    - `apply_mpl_fonts(font_family)` — apply LatticeSVG font resolution to matplotlib’s global `rcParams`.
    - `restore_mpl_fonts()` — revert `rcParams` to the state before `apply_mpl_fonts`.
    - All three accept a CSS `font-family` string, register fonts via `addfont()`, and set `svg.fonttype: "path"` + `axes.unicode_minus: False`.

### Bug Fixes

- **Fixed matplotlib font fallback failure.** Previously, `font.family` was set to a generic name (`"sans-serif"`) which caused matplotlib to resolve only one font file, losing per-glyph CJK fallback. Now `font.family` is set to the concrete name list (e.g. `["Arial", "Microsoft YaHei"]`) so that `_find_fonts_by_props` builds an `FT2Font` with `_fallback_list`, enabling per-glyph fallback.
- **Fixed MplNode regression with pre-created figures.** Also populates `font.sans-serif`, `font.serif`, `font.monospace` lists so that text elements created before `rc_context` (whose `FontProperties` default to `"sans-serif"`) can still resolve to the correct fonts.

### Internal

- Refactored `MplNode._resolve_mpl_font_rc()` and `_register_fonts_with_mpl()` to delegate to shared `_build_mpl_rc()` and `_register_mpl_fonts()` in `latticesvg.text`.

---

## v0.1.2 — Font Query API & MplNode Auto-Font (2026-03-19)

### New Features

- **Font Query API** (`latticesvg.text`)
    - `get_font_path(family, weight="normal", style="normal") -> Optional[str]` — resolve a CSS family name to its filesystem path without silent fallback.
    - `list_fonts() -> List[FontInfo]` — enumerate every indexed font as a `FontInfo` dataclass (fields: `family`, `path`, `weight`, `style`, `format`, `face_index`).
    - `parse_font_families(value) -> List[str]` — parse a CSS `font-family` string / list / `None` into a flat list of family names.
    - `FontInfo` frozen dataclass exported from `latticesvg.text`.
    - New `FontManager` methods: `get_font_path()` and `list_fonts()` (same semantics as the convenience wrappers above).

- **MplNode — Auto-font configuration**
    - New parameter `auto_mpl_font: bool = True` — when enabled, `MplNode` reads `font-family` from its computed/inherited style, resolves font paths via `FontManager`, registers them with `matplotlib.font_manager.fontManager.addfont()`, and wraps `savefig()` in a `matplotlib.rc_context()` so the chart text uses the same font family as the surrounding LatticeSVG layout.
    - `svg.fonttype` is always set to `"path"` inside the context, ensuring text renders as vector outlines for cross-platform consistency.
    - New parameter `tight_layout: bool = True` — calls `figure.tight_layout()` inside the font-aware `rc_context` (so label metrics are correct before the layout adjustment).
    - `font-family` is inherited from a parent `GridContainer` when not set on `MplNode` directly.

### Examples

- `demo_51_font_query_mpl.py` — 2×2 multi-font comparison showcasing `get_font_path`, `list_fonts`, and `MplNode` auto-font with Microsoft YaHei, KaiTi, FangSong, and Noto Sans CJK JP.

---

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
