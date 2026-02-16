# 节点类型 API

本页面详细介绍所有节点类型的构造函数、属性和方法。

## Rect

轴对齐矩形，左上角原点，y 轴向下。

```python
from latticesvg import Rect

r = Rect(x=10, y=20, width=100, height=50)
print(r.right)   # 110.0
print(r.bottom)  # 70.0
r2 = r.copy()
```

| 属性 | 类型 | 说明 |
|---|---|---|
| `x` | `float` | 左上角 x 坐标（默认 0.0） |
| `y` | `float` | 左上角 y 坐标（默认 0.0） |
| `width` | `float` | 宽度（默认 0.0） |
| `height` | `float` | 高度（默认 0.0） |
| `right` | `float` | 只读，等价于 `x + width` |
| `bottom` | `float` | 只读，等价于 `y + height` |

| 方法 | 返回类型 | 说明 |
|---|---|---|
| `copy()` | `Rect` | 返回副本 |

---

## LayoutConstraints

布局约束，从父节点传递给子节点。

```python
from latticesvg import LayoutConstraints

c = LayoutConstraints(available_width=800, available_height=600)
```

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `available_width` | `float \| None` | `None` | 可用宽度 |
| `available_height` | `float \| None` | `None` | 可用高度 |

---

## Node（基类）

所有可布局元素的抽象基类。子类需要实现 `measure()` 和 `layout()`。

```python
from latticesvg import Node

node = Node(style={"width": 100, "height": 50, "background": "#f0f0f0"})
```

### 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `style` | `dict[str, Any] \| None` | `None` | CSS 样式属性字典 |
| `parent` | `Node \| None` | `None` | 父节点（通常由 `add()` 自动设置） |

### 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `style` | `ComputedStyle` | 计算后的样式对象 |
| `parent` | `Node \| None` | 父节点 |
| `children` | `list[Node]` | 子节点列表 |
| `border_box` | `Rect` | 布局后的边框盒矩形 |
| `padding_box` | `Rect` | 布局后的内边距盒矩形 |
| `content_box` | `Rect` | 布局后的内容盒矩形 |
| `placement` | `PlacementHint` | Grid 放置信息 |

### 方法

#### `add(child, *, row=None, col=None, row_span=1, col_span=1, area=None)`

将子节点添加到当前节点，可选地设置 Grid 放置位置。

| 参数 | 类型 | 说明 |
|---|---|---|
| `child` | `Node` | 要添加的子节点 |
| `row` | `int \| None` | 行起始位置（1-based CSS Grid 行号） |
| `col` | `int \| None` | 列起始位置（1-based CSS Grid 行号） |
| `row_span` | `int` | 跨行数（默认 1） |
| `col_span` | `int` | 跨列数（默认 1） |
| `area` | `str \| None` | 命名区域名称 |

**返回值：** 被添加的子节点（支持链式调用）

```python
grid.add(child, row=1, col=2, row_span=1, col_span=2)
grid.add(child, area="header")
```

#### `measure(constraints) → (min_w, max_w, intrinsic_h)`

返回节点的最小内容宽度、最大内容宽度和固有高度。由 Grid 求解器调用。

#### `layout(constraints)`

计算 `border_box`、`padding_box` 和 `content_box`。子类必须实现。

---

## GridContainer

CSS Grid 布局容器节点。将子节点排列为网格布局。

```python
from latticesvg import GridContainer

grid = GridContainer(style={
    "grid-template-columns": "200px 1fr",
    "grid-template-rows": "auto auto",
    "gap": 10,
    "width": 600,
    "padding": 20,
})
```

### 构造参数

继承自 `Node`，同样接受 `style` 和 `parent` 参数。`display` 自动设为 `"grid"`。

### 方法

#### `layout(constraints=None, available_width=None, available_height=None)`

运行完整的布局计算。作为根节点时可以直接传入可用宽度：

```python
grid.layout(available_width=800)
```

如果不提供 `available_width`，优先使用样式中的 `width` 属性，否则默认为 800。

#### `measure(constraints) → (min_w, max_w, intrinsic_h)`

用于嵌套 Grid 尺寸计算，结果会被缓存。

---

## TextNode

文本节点，支持自动换行、富文本标记和垂直排版。

```python
from latticesvg import TextNode

# 纯文本
text = TextNode("Hello, World!", style={"font-size": 24, "color": "#333"})

# HTML 富文本
rich = TextNode("<b>Bold</b> and <i>italic</i>", markup="html")

# Markdown 富文本
md = TextNode("**Bold** and *italic*", markup="markdown")
```

### 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `text` | `str` | *必填* | 文本内容 |
| `style` | `dict \| None` | `None` | 样式属性 |
| `parent` | `Node \| None` | `None` | 父节点 |
| `markup` | `str` | `"none"` | 标记模式：`"none"`, `"html"`, `"markdown"` |

### 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `text` | `str` | 原始文本内容 |
| `markup` | `str` | 标记模式 |
| `lines` | `list[Line]` | 布局后的行列表（纯文本模式） |

### 关键样式属性

文本节点响应以下样式属性（详见 [CSS 属性参考](../css-properties.md)）：

- **字体：** `font-family`, `font-size`, `font-weight`, `font-style`
- **排版：** `text-align`, `line-height`, `letter-spacing`, `word-spacing`
- **换行：** `white-space`, `overflow-wrap`, `hyphens`, `lang`
- **溢出：** `overflow`, `text-overflow`
- **垂直：** `writing-mode`, `text-orientation`, `text-combine-upright`

---

## ImageNode

图片节点，支持多种图片来源和 `object-fit` 缩放模式。

```python
from latticesvg import ImageNode

# 文件路径
img = ImageNode("photo.png", style={"width": 200, "height": 150})

# URL
img = ImageNode("https://example.com/image.png")

# bytes
img = ImageNode(raw_bytes, object_fit="contain")

# PIL Image
from PIL import Image
img = ImageNode(Image.open("photo.png"), object_fit="cover")
```

### 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `src` | `str \| bytes \| PIL.Image` | *必填* | 图片源（路径/URL/bytes/PIL） |
| `style` | `dict \| None` | `None` | 样式属性 |
| `parent` | `Node \| None` | `None` | 父节点 |
| `object_fit` | `str \| None` | `None` | 缩放模式 |

### object-fit 模式

| 值 | 说明 |
|---|---|
| `"fill"` | 拉伸填满（默认，可能变形） |
| `"contain"` | 等比缩放，完全包含在区域内 |
| `"cover"` | 等比缩放，完全覆盖区域 |
| `"none"` | 原始尺寸，不缩放 |

### 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `intrinsic_width` | `float` | 图片固有宽度（只读，惰性加载） |
| `intrinsic_height` | `float` | 图片固有高度（只读，惰性加载） |

---

## SVGNode

嵌入外部 SVG 内容的节点。

```python
from latticesvg import SVGNode

# SVG 字符串
svg = SVGNode('<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>')

# 文件
svg = SVGNode("icon.svg", is_file=True)

# URL
svg = SVGNode("https://example.com/icon.svg")
```

### 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `svg` | `str` | *必填* | SVG 内容（字符串/路径/URL） |
| `style` | `dict \| None` | `None` | 样式属性（仅限关键字参数） |
| `parent` | `Node \| None` | `None` | 父节点（仅限关键字参数） |
| `is_file` | `bool` | `False` | 是否视为文件路径（仅限关键字参数） |

SVG 的固有尺寸从 `viewBox` 或 `width`/`height` 属性解析。

---

## MplNode

Matplotlib 图形嵌入节点。

```python
import matplotlib.pyplot as plt
from latticesvg import MplNode

fig, ax = plt.subplots(figsize=(4, 3))
ax.plot([1, 2, 3], [1, 4, 9])

node = MplNode(fig, style={"padding": 10})
```

### 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `figure` | `matplotlib.figure.Figure` | *必填* | Matplotlib 图形对象 |
| `style` | `dict \| None` | `None` | 样式属性 |
| `parent` | `Node \| None` | `None` | 父节点 |

!!! note "注意事项"
    - 所有 Matplotlib 自定义应在创建节点**之前**完成
    - 布局时会根据分配的空间自动调整 figure 大小
    - SVG 坐标统一使用 72 DPI

---

## MathNode

LaTeX 公式渲染节点，基于 QuickJax（MathJax v4）。

```python
from latticesvg import MathNode

# display 模式（独立公式）
formula = MathNode(r"E = mc^2", style={"font-size": 24})

# inline 模式
inline = MathNode(r"\alpha + \beta", display=False)
```

### 构造参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `latex` | `str` | *必填* | LaTeX 数学表达式 |
| `style` | `dict \| None` | `None` | 样式属性（仅限关键字参数） |
| `backend` | `str \| None` | `None` | 后端名称，None 使用默认（仅限关键字参数） |
| `display` | `bool` | `True` | 是否为 display 模式（仅限关键字参数） |
| `parent` | `Node \| None` | `None` | 父节点（仅限关键字参数） |

### 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `latex` | `str` | LaTeX 源码 |
| `display` | `bool` | display/inline 模式 |
| `scale_x` | `float` | 布局后的水平缩放因子 |
| `scale_y` | `float` | 布局后的垂直缩放因子 |

## 自动生成的 API 文档

::: latticesvg.nodes
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3
