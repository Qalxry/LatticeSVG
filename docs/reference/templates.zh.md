# 内置模板

LatticeSVG 提供 17 个预定义样式模板和表格构建工具。

## 用法

```python
from latticesvg import templates

# 方式 1：直接使用模板
page = GridContainer(style=templates.REPORT_PAGE)

# 方式 2：合并覆盖
page = GridContainer(style={
    **templates.REPORT_PAGE,
    "width": "1000px",
})

# 方式 3：通过名称访问
style = templates.ALL_TEMPLATES["report-page"]
```

## 布局模板

### REPORT_PAGE

标准报告页面：800px 宽，白色背景，单列，30px 内边距。

```python
REPORT_PAGE = {
    "width": "800px",
    "padding": "30px",
    "background-color": "#ffffff",
    "grid-template-columns": ["1fr"],
    "gap": "20px",
}
```

### TWO_COLUMN

两列等宽布局。

```python
TWO_COLUMN = {
    "grid-template-columns": ["1fr", "1fr"],
    "gap": "20px",
}
```

### THREE_COLUMN

三列等宽布局。

```python
THREE_COLUMN = {
    "grid-template-columns": ["1fr", "1fr", "1fr"],
    "gap": "20px",
}
```

### SIDEBAR_LAYOUT

固定侧边栏 + 弹性主区域。

```python
SIDEBAR_LAYOUT = {
    "grid-template-columns": ["240px", "1fr"],
    "gap": "24px",
}
```

### CHART_CONTAINER

2×2 图表网格。

```python
CHART_CONTAINER = {
    "grid-template-columns": ["1fr", "1fr"],
    "grid-template-rows": ["1fr", "1fr"],
    "gap": "10px",
}
```

## 排版模板

### HEADER / FOOTER

深色背景的页眉/页脚。

```python
HEADER = {
    "padding": "16px 24px",
    "background-color": "#2c3e50",
    "color": "#ffffff",
    "font-size": "18px",
    "font-weight": "bold",
}

FOOTER = {
    "padding": "12px 24px",
    "background-color": "#34495e",
    "color": "#ecf0f1",
    "font-size": "12px",
    "text-align": "center",
}
```

### TITLE / SUBTITLE

标题与副标题。

```python
TITLE = {
    "font-size": "28px",
    "font-weight": "bold",
    "color": "#1a1a1a",
    "text-align": "center",
    "line-height": "1.3",
}

SUBTITLE = {
    "font-size": "20px",
    "font-weight": "bold",
    "color": "#333333",
    "line-height": "1.4",
}
```

### H1 / H2 / H3

各级标题。

| 模板 | 字号 | 颜色 |
|---|---|---|
| `H1` | 24px | #222222 |
| `H2` | 20px | #333333 |
| `H3` | 16px | #444444 |

### PARAGRAPH

正文段落：14px，灰色，行高 1.6。

```python
PARAGRAPH = {
    "font-size": "14px",
    "color": "#333333",
    "line-height": "1.6",
    "text-align": "left",
}
```

### CAPTION

图注/表注：12px，浅灰色，居中。

```python
CAPTION = {
    "font-size": "12px",
    "color": "#888888",
    "text-align": "center",
    "line-height": "1.4",
}
```

### CODE

代码样式：等宽字体，粉色，浅灰背景。

```python
CODE = {
    "font-family": "monospace",
    "font-size": "13px",
    "color": "#d63384",
    "background-color": "#f8f9fa",
    "padding": "2px 6px",
    "line-height": "1.5",
    "white-space": "pre",
}
```

## 视觉模板

### CARD

简洁卡片：白色背景，浅灰边框。

```python
CARD = {
    "padding": "16px",
    "background-color": "#ffffff",
    "border": "1px solid #e0e0e0",
}
```

### HIGHLIGHT_BOX

高亮提示框：黄色系。

```python
HIGHLIGHT_BOX = {
    "padding": "12px 16px",
    "background-color": "#fff3cd",
    "border": "1px solid #ffc107",
    "color": "#856404",
}
```

## ALL_TEMPLATES 字典

所有模板可通过名称字符串访问：

```python
from latticesvg.templates import ALL_TEMPLATES

for name, style in ALL_TEMPLATES.items():
    print(f"{name}: {list(style.keys())}")
```

| 键名 | 对应模板 |
|---|---|
| `"report-page"` | `REPORT_PAGE` |
| `"two-column"` | `TWO_COLUMN` |
| `"three-column"` | `THREE_COLUMN` |
| `"sidebar-layout"` | `SIDEBAR_LAYOUT` |
| `"chart-container"` | `CHART_CONTAINER` |
| `"header"` | `HEADER` |
| `"footer"` | `FOOTER` |
| `"title"` | `TITLE` |
| `"subtitle"` | `SUBTITLE` |
| `"h1"` ~ `"h3"` | `H1` ~ `H3` |
| `"paragraph"` | `PARAGRAPH` |
| `"caption"` | `CAPTION` |
| `"code"` | `CODE` |
| `"card"` | `CARD` |
| `"highlight-box"` | `HIGHLIGHT_BOX` |

## 表格构建

### build_table()

便捷创建表格的函数，返回一个 `GridContainer` 节点树：

```python
from latticesvg.templates import build_table

table = build_table(
    headers=["名称", "值", "单位"],
    rows=[
        ["温度", "23.5", "°C"],
        ["湿度", "65", "%"],
        ["气压", "1013", "hPa"],
    ],
    col_widths=["120px", "80px", "1fr"],
    stripe_color="#f8f9fa",
)
```

**参数说明：**

| 参数 | 类型 | 说明 |
|---|---|---|
| `headers` | `Sequence[str]` | 列标题 |
| `rows` | `Sequence[Sequence]` | 数据行 |
| `style` | `dict` | 覆盖表格容器样式 |
| `header_style` | `dict` | 覆盖表头单元格样式 |
| `cell_style` | `dict` | 覆盖数据单元格样式 |
| `col_widths` | `list[str]` | 列宽定义，默认全 `1fr` |
| `stripe_color` | `str \| None` | 斑马纹颜色，`None` 禁用 |

### 表格默认样式

```python
TABLE_DEFAULT = {
    "background-color": "#ffffff",
    "border": "1px solid #dee2e6",
}

TABLE_HEADER_DEFAULT = {
    "background-color": "#f1f3f5",
    "padding": "8px 12px",
    "border-bottom": "2px solid #dee2e6",
    "font-size": "13px",
    "font-weight": "bold",
    "color": "#212529",
    "text-align": "left",
}

TABLE_CELL_DEFAULT = {
    "padding": "6px 12px",
    "border-bottom": "1px solid #dee2e6",
    "font-size": "13px",
    "color": "#495057",
    "text-align": "left",
}
```
