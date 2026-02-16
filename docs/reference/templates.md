# Built-in Templates

LatticeSVG provides 17 predefined style templates and a table builder.

## Usage

```python
from latticesvg import templates

# Direct use
page = GridContainer(style=templates.REPORT_PAGE)

# Merge and override
page = GridContainer(style={**templates.REPORT_PAGE, "width": "1000px"})

# Access by name
style = templates.ALL_TEMPLATES["report-page"]
```

## Layout Templates

| Template | Description | Key Properties |
|---|---|---|
| `REPORT_PAGE` | Standard report page | 800px, white, single column, 30px padding |
| `TWO_COLUMN` | Two equal columns | `1fr 1fr`, 20px gap |
| `THREE_COLUMN` | Three equal columns | `1fr 1fr 1fr`, 20px gap |
| `SIDEBAR_LAYOUT` | Fixed sidebar + flexible main | `240px 1fr`, 24px gap |
| `CHART_CONTAINER` | 2×2 chart grid | `1fr 1fr` × `1fr 1fr`, 10px gap |

## Typography Templates

| Template | Font Size | Weight | Color | Alignment |
|---|---|---|---|---|
| `HEADER` | 18px | bold | #ffffff | left |
| `FOOTER` | 12px | normal | #ecf0f1 | center |
| `TITLE` | 28px | bold | #1a1a1a | center |
| `SUBTITLE` | 20px | bold | #333333 | left |
| `H1` | 24px | bold | #222222 | left |
| `H2` | 20px | bold | #333333 | left |
| `H3` | 16px | bold | #444444 | left |
| `PARAGRAPH` | 14px | normal | #333333 | left |
| `CAPTION` | 12px | normal | #888888 | center |
| `CODE` | 13px | normal | #d63384 | left |

## Visual Templates

| Template | Description |
|---|---|
| `CARD` | White card with light border |
| `HIGHLIGHT_BOX` | Yellow warning/highlight box |

## ALL_TEMPLATES Dictionary

All templates accessible by string name:

```python
from latticesvg.templates import ALL_TEMPLATES
for name, style in ALL_TEMPLATES.items():
    print(f"{name}: {list(style.keys())}")
```

## Table Builder

### build_table()

Convenience function that returns a `GridContainer` node tree:

```python
from latticesvg.templates import build_table

table = build_table(
    headers=["Name", "Value", "Unit"],
    rows=[["Temperature", "23.5", "°C"], ["Humidity", "65", "%"]],
    col_widths=["120px", "80px", "1fr"],
    stripe_color="#f8f9fa",
)
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `headers` | `Sequence[str]` | Column headers |
| `rows` | `Sequence[Sequence]` | Data rows |
| `style` | `dict` | Override table container styles |
| `header_style` | `dict` | Override header cell styles |
| `cell_style` | `dict` | Override body cell styles |
| `col_widths` | `list[str]` | Column widths, defaults to `1fr` each |
| `stripe_color` | `str \| None` | Stripe color, `None` to disable |
