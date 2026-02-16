# Markup Parser API

The markup parser module converts HTML and Markdown rich text into `TextSpan` trees.

## Module Overview

| Export | Type | Responsibility |
|---|---|---|
| `TextSpan` | dataclass | Rich text fragment (with style overrides and child spans) |
| `parse_markup()` | function | Unified entry point, selects parser by mode |
| `parse_html()` | function | HTML markup parser |
| `parse_markdown()` | function | Markdown markup parser |

## TextSpan

```python
from latticesvg.markup.parser import TextSpan

span = TextSpan(
    text="Hello",
    bold=True,
    color="#ff0000",
    children=[
        TextSpan(text=" World", italic=True)
    ],
)
```

## Parsing Examples

```python
from latticesvg.markup.parser import parse_markup

# HTML
spans = parse_markup("<b>Bold</b> text", "html")

# Markdown
spans = parse_markup("**Bold** text", "markdown")
```

## Auto-generated API Docs

::: latticesvg.markup.parser
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3
