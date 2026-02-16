# Grid 布局

本教程涵盖 LatticeSVG 中 CSS Grid 布局的各种技巧，从基础到高级。

## 固定轨道

最简单的网格——指定固定像素宽度：

```python
from latticesvg import GridContainer, TextNode, Renderer

grid = GridContainer(style={
    "width": "500px",
    "padding": "16px",
    "grid-template-columns": ["200px", "280px"],
    "gap": "12px",
    "background-color": "#f5f5f5",
})

grid.add(TextNode("200px 宽", style={"background-color": "#e3f2fd", "padding": "12px"}))
grid.add(TextNode("280px 宽", style={"background-color": "#fce4ec", "padding": "12px"}))

Renderer().render(grid, "fixed_grid.svg")
```

<figure markdown="span">
  ![固定轨道](../assets/images/examples/grid_fixed.svg){ loading=lazy }
  <figcaption>固定像素宽度的两列网格</figcaption>
</figure>

## 弹性单位 `fr`

`fr` 单位按比例分配剩余空间：

```python
grid = GridContainer(style={
    "width": "600px",
    "padding": "16px",
    "grid-template-columns": ["1fr", "2fr", "1fr"],  # 1:2:1 比例
    "gap": "12px",
})
```

<figure markdown="span">
  ![fr 单位](../assets/images/examples/grid_fr.svg){ loading=lazy }
  <figcaption>fr 单位按比例分配空间</figcaption>
</figure>

## 混合轨道

固定宽度与弹性单位混用：

```python
grid = GridContainer(style={
    "width": "800px",
    "padding": "16px",
    "grid-template-columns": ["240px", "1fr"],  # 固定侧边栏 + 弹性主区域
    "gap": "24px",
})
```

<figure markdown="span">
  ![混合轨道](../assets/images/examples/grid_mixed.svg){ loading=lazy }
  <figcaption>固定侧边栏 + 弹性主区域</figcaption>
</figure>

!!! tip "经典侧边栏布局"
    `["240px", "1fr"]` 是最常见的侧边栏布局模式，也可以使用内置模板
    `templates.SIDEBAR_LAYOUT`。

## 自动放置

不指定 `row`/`col` 时，子节点按照 `grid-auto-flow` 自动放置：

```python
grid = GridContainer(style={
    "width": "600px",
    "grid-template-columns": ["1fr", "1fr", "1fr"],
    "gap": "8px",
    "padding": "16px",
})

# 自动按行填充：第 1 行 3 个，第 2 行 2 个
for i in range(5):
    grid.add(TextNode(f"项目 {i+1}", style={
        "padding": "12px",
        "background-color": "#e8eaf6",
        "text-align": "center",
    }))
```

<figure markdown="span">
  ![自动放置](../assets/images/examples/grid_auto_placement.svg){ loading=lazy }
  <figcaption>自动放置：子节点按行填充</figcaption>
</figure>

## 跨行跨列

使用 `row_span` 和 `col_span` 让元素跨越多个轨道：

```python
grid = GridContainer(style={
    "width": "500px",
    "grid-template-columns": ["1fr", "1fr", "1fr"],
    "grid-template-rows": ["auto", "auto", "auto"],
    "gap": "8px",
    "padding": "16px",
})

# 跨 2 列
grid.add(TextNode("跨 2 列", style={
    "background-color": "#bbdefb",
    "padding": "16px",
    "text-align": "center",
}), row=1, col=1, col_span=2)

# 跨 2 行
grid.add(TextNode("跨 2 行", style={
    "background-color": "#c8e6c9",
    "padding": "16px",
    "text-align": "center",
}), row=1, col=3, row_span=2)

grid.add(TextNode("普通", style={
    "background-color": "#fff9c4",
    "padding": "16px",
}), row=2, col=1)

grid.add(TextNode("普通", style={
    "background-color": "#ffccbc",
    "padding": "16px",
}), row=2, col=2)
```

<figure markdown="span">
  ![跨行跨列](../assets/images/examples/grid_spanning.svg){ loading=lazy }
  <figcaption>跨行跨列布局示例</figcaption>
</figure>

## 命名区域

使用 `grid-template-areas` 定义命名区域，用 `area` 参数放置子节点：

```python
grid = GridContainer(style={
    "width": "600px",
    "padding": "16px",
    "grid-template-columns": ["200px", "1fr"],
    "grid-template-rows": ["auto", "1fr", "auto"],
    "grid-template-areas": '"header header" "sidebar main" "footer footer"',
    "gap": "8px",
})

grid.add(TextNode("页眉", style={
    "background-color": "#2c3e50",
    "color": "#fff",
    "padding": "16px",
}), area="header")

grid.add(TextNode("侧边栏", style={
    "background-color": "#ecf0f1",
    "padding": "16px",
}), area="sidebar")

grid.add(TextNode("主内容", style={
    "background-color": "#ffffff",
    "padding": "16px",
}), area="main")

grid.add(TextNode("页脚", style={
    "background-color": "#34495e",
    "color": "#ecf0f1",
    "padding": "12px",
    "text-align": "center",
}), area="footer")
```

<figure markdown="span">
  ![命名区域](../assets/images/examples/grid_areas.svg){ loading=lazy }
  <figcaption>grid-template-areas 命名区域布局</figcaption>
</figure>

## 对齐控制

### 容器级对齐

- `justify-items` — 水平对齐所有子项（`start` | `center` | `end` | `stretch`）
- `align-items` — 垂直对齐所有子项

### 子项级对齐

- `justify-self` — 覆盖单个子项的水平对齐
- `align-self` — 覆盖单个子项的垂直对齐

```python
grid = GridContainer(style={
    "width": "400px",
    "grid-template-columns": ["1fr", "1fr"],
    "gap": "12px",
    "padding": "16px",
    "justify-items": "center",   # 所有子项水平居中
    "align-items": "center",     # 所有子项垂直居中
})
```

<figure markdown="span">
  ![对齐控制](../assets/images/examples/grid_alignment.svg){ loading=lazy }
  <figcaption>对齐控制示例</figcaption>
</figure>

## `repeat()` 和 `minmax()`

使用 `repeat()` 简化重复轨道定义，`minmax()` 设置轨道尺寸范围：

```python
grid = GridContainer(style={
    "width": "800px",
    "padding": "16px",
    # repeat(3, minmax(150px, 1fr)) → 3 列，每列最少 150px
    "grid-template-columns": "repeat(3, minmax(150px, 1fr))",
    "gap": "12px",
})
```

<figure markdown="span">
  ![repeat 和 minmax](../assets/images/examples/grid_repeat_minmax.svg){ loading=lazy }
  <figcaption>repeat() 和 minmax() 示例</figcaption>
</figure>

## 自动轨道

当子节点超出显式定义的轨道时，`grid-auto-rows` 和 `grid-auto-columns` 控制隐式轨道的大小：

```python
grid = GridContainer(style={
    "width": "400px",
    "grid-template-columns": ["1fr", "1fr"],
    # 只定义了列，行由自动轨道控制
    "grid-auto-rows": "80px",  # 每行固定 80px
    "gap": "8px",
    "padding": "16px",
})

# 添加 6 个元素 → 自动创建 3 行 × 2 列
for i in range(6):
    grid.add(TextNode(f"单元格 {i+1}", style={
        "background-color": "#e0f7fa",
        "padding": "8px",
        "text-align": "center",
    }))
```

<figure markdown="span">
  ![自动轨道](../assets/images/examples/grid_auto_tracks.svg){ loading=lazy }
  <figcaption>自动轨道示例</figcaption>
</figure>

## 嵌套网格

`GridContainer` 可以作为另一个 `GridContainer` 的子节点：

```python
outer = GridContainer(style={
    "width": "800px",
    "padding": "24px",
    "grid-template-columns": ["1fr", "1fr"],
    "gap": "16px",
})

# 左侧卡片（也是一个 Grid）
left_card = GridContainer(style={
    "padding": "16px",
    "background-color": "#ffffff",
    "border": "1px solid #e0e0e0",
    "grid-template-columns": ["1fr"],
    "gap": "8px",
})
left_card.add(TextNode("卡片标题", style={"font-weight": "bold"}))
left_card.add(TextNode("卡片内容"))

outer.add(left_card)
```

<figure markdown="span">
  ![嵌套网格](../assets/images/examples/grid_nested.svg){ loading=lazy }
  <figcaption>嵌套 GridContainer 示例</figcaption>
</figure>

## `justify-content` 间距

利用 `column-gap` 和 `row-gap` 独立控制行列间距：

```python
grid = GridContainer(style={
    "width": "600px",
    "grid-template-columns": ["1fr", "1fr", "1fr"],
    "column-gap": "24px",   # 列间距
    "row-gap": "8px",       # 行间距
    "padding": "16px",
})
```

!!! note "简写属性"
    `gap` 是 `row-gap` 和 `column-gap` 的简写。`"gap": "8px 24px"` 等同于
    `"row-gap": "8px"` + `"column-gap": "24px"`。
