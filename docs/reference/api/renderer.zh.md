# 渲染器 API

`Renderer` 类负责将布局后的节点树转换为 SVG（或 PNG）输出。

## 基本用法

```python
from latticesvg import GridContainer, TextNode, Renderer

grid = GridContainer(style={"width": 400, "padding": 20, "background": "white"})
grid.add(TextNode("Hello!", style={"font-size": 24}))

renderer = Renderer()

# 输出 SVG 文件
renderer.render(grid, "output.svg")

# 输出 PNG 文件（需要 cairosvg）
renderer.render_png(grid, "output.png", scale=2)

# 获取 drawsvg.Drawing 对象
drawing = renderer.render_to_drawing(grid)

# 获取 SVG 字符串
svg_string = renderer.render_to_string(grid)
```

## 构造函数

```python
Renderer()
```

无参数。内部创建 `drawsvg.Drawing` 实例。

## 方法

### `render(node, output_path, *, embed_fonts=False)`

渲染节点及其后代为 SVG 文件。

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `node` | `Node` | *必填* | 根节点 |
| `output_path` | `str` | *必填* | SVG 文件的输出路径 |
| `embed_fonts` | `bool` | `False` | 是否嵌入子集化 WOFF2 字体 |

**返回值：** `drawsvg.Drawing` — 可用于进一步操作

---

### `render_to_drawing(node, *, embed_fonts=False)`

渲染节点为 `drawsvg.Drawing` 对象，不写入任何文件。

!!! info "自动布局"
    此方法会自动执行 `node.layout()`，无需手动调用（调了也无妨，会重新执行）。

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `node` | `Node` | *必填* | 根节点 |
| `embed_fonts` | `bool` | `False` | 是否嵌入子集化 WOFF2 字体 |

**返回值：** `drawsvg.Drawing`

---

### `render_to_string(node, *, embed_fonts=False)`

渲染节点为 SVG 字符串（无文件 I/O）。

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `node` | `Node` | *必填* | 根节点 |
| `embed_fonts` | `bool` | `False` | 是否嵌入子集化 WOFF2 字体 |

**返回值：** `str` — SVG XML 字符串

---

### `render_png(node, output_path, scale=1.0, *, embed_fonts=False)`

先渲染为 SVG，再通过 cairosvg 转换为 PNG。

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `node` | `Node` | *必填* | 根节点 |
| `output_path` | `str` | *必填* | PNG 文件的输出路径 |
| `scale` | `float` | `1.0` | 缩放因子（`2.0` 输出 2 倍分辨率） |
| `embed_fonts` | `bool` | `False` | 是否嵌入字体以确保字形准确 |

!!! warning "依赖要求"
    PNG 输出需要安装 `cairosvg`：
    ```bash
    pip install latticesvg[png]
    # 或
    pip install cairosvg
    ```

---

## 字体嵌入

当 `embed_fonts=True` 时，Renderer 会：

1. 遍历节点树，收集所有使用的字体和字符
2. 从字体文件中提取所需字形（子集化）
3. 将子集化后的字体打包为 WOFF2 格式
4. 在 SVG 中插入 `@font-face` 规则

这使得生成的 SVG 完全自包含，不依赖查看端安装的字体。

!!! note "依赖"
    字体嵌入需要安装 `fonttools` 包：
    ```bash
    pip install fonttools[woff]
    ```

## 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `drawing` | `drawsvg.Drawing \| None` | 最近一次渲染生成的 Drawing 对象 |

## 自动生成的 API 文档

::: latticesvg.render.renderer.Renderer
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3
