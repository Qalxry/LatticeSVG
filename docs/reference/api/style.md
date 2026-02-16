# Style System API

The style module handles CSS property parsing, registration, and computation.

## Module Overview

| Submodule | Responsibility |
|---|---|
| `style.properties` | Property registry (`PROPERTY_REGISTRY`) |
| `style.parser` | Value parsers and special value types |
| `style.computed` | `ComputedStyle` computed style object |

## ComputedStyle

`ComputedStyle` is the style container for each node, responsible for:

- Storing explicitly set property values
- Property inheritance (from parent nodes)
- Computing final used values

```python
from latticesvg import ComputedStyle

cs = ComputedStyle({"font-size": 24, "color": "red"})
print(cs.font_size)     # 24
print(cs.get("color"))  # "red"
```

## Auto-generated API Docs

### Style Properties

::: latticesvg.style.properties
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4

### Value Parser

::: latticesvg.style.parser
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4

### Computed Style

::: latticesvg.style.computed
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4
