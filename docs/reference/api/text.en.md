# Text Engine API

The text module handles font loading, text measurement, automatic line breaking, and vertical typesetting.

## Module Overview

| Submodule | Responsibility |
|---|---|
| `text.font` | Font manager (`FontManager`), FreeType/Pillow backends |
| `text.shaper` | Text measurement, line breaking, alignment (`measure_text`, `break_lines`, `align_lines`) |
| `text.embed` | Font subsetting and WOFF2 embedding |

## FontManager

Global singleton managing font discovery and loading.

```python
from latticesvg.text.font import FontManager

fm = FontManager.instance()
path = fm.find_font("Noto Sans SC", weight="bold")
chain = fm.find_font_chain(["Times New Roman", "SimSun"], weight="normal")
```

## Auto-generated API Docs

### Font Management

::: latticesvg.text.font
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4

### Text Shaping

::: latticesvg.text.shaper
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4

### Font Embedding

::: latticesvg.text.embed
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4
