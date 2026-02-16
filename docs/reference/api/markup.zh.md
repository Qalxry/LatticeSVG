# 标记解析 API

标记解析模块负责将 HTML 和 Markdown 富文本解析为 `TextSpan` 树。

## 模块概览

| 导出 | 类型 | 职责 |
|---|---|---|
| `TextSpan` | dataclass | 富文本片段（含样式覆盖和子 span） |
| `parse_markup()` | 函数 | 统一入口，根据 mode 选择解析器 |
| `parse_html()` | 函数 | HTML 标记解析 |
| `parse_markdown()` | 函数 | Markdown 标记解析 |

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

## 解析示例

```python
from latticesvg.markup.parser import parse_markup

# HTML
spans = parse_markup("<b>Bold</b> text", "html")

# Markdown
spans = parse_markup("**Bold** text", "markdown")
```

## 自动生成的 API 文档

::: latticesvg.markup.parser
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3
