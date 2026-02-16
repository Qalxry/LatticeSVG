# 快速上手

本教程将带你用 5 分钟完成第一个 LatticeSVG 布局。

## 基本流程

LatticeSVG 的工作流程分为三步：

1. **创建 `GridContainer`** — 定义布局容器和样式
2. **添加子节点** — 使用 `.add()` 添加文本、图片等内容
3. **渲染输出** — 调用 `Renderer` 生成 SVG 或 PNG

## 第一个示例

```python
from latticesvg import GridContainer, TextNode, Renderer

# 步骤 1：创建页面容器
page = GridContainer(style={
    "width": "600px",
    "padding": "32px",
    "background-color": "#ffffff",
    "grid-template-columns": ["1fr"],  # 单列布局
    "gap": "16px",
})

# 步骤 2：添加内容
page.add(TextNode("欢迎使用 LatticeSVG", style={
    "font-size": "28px",
    "font-weight": "bold",
    "color": "#2c3e50",
    "text-align": "center",
}))

page.add(TextNode(
    "LatticeSVG 是一个基于 CSS Grid 的声明式矢量布局引擎，"
    "用 Python 字典描述样式，输出高质量 SVG。",
    style={
        "font-size": "14px",
        "color": "#555555",
        "line-height": "1.6",
    },
))

# 步骤 3：渲染
Renderer().render(page, "my_first_layout.svg")
```

<figure markdown="span">
  ![第一个示例](../assets/images/examples/quickstart_first.svg){ loading=lazy }
  <figcaption>渲染结果</figcaption>
</figure>

## 两列布局

```python
from latticesvg import GridContainer, TextNode, Renderer

page = GridContainer(style={
    "width": "600px",
    "padding": "24px",
    "background-color": "#f8f9fa",
    "grid-template-columns": ["1fr", "1fr"],  # 两列等宽
    "gap": "16px",
})

page.add(TextNode("左侧内容", style={
    "padding": "16px",
    "background-color": "#ffffff",
    "border": "1px solid #dee2e6",
    "font-size": "14px",
}))

page.add(TextNode("右侧内容", style={
    "padding": "16px",
    "background-color": "#ffffff",
    "border": "1px solid #dee2e6",
    "font-size": "14px",
}))

Renderer().render(page, "two_columns.svg")
```

<figure markdown="span">
  ![两列布局](../assets/images/examples/quickstart_two_col.svg){ loading=lazy }
  <figcaption>两列等宽布局</figcaption>
</figure>

## 使用内置模板

LatticeSVG 提供 17 个内置样式模板，可以直接使用或覆盖部分属性：

```python
from latticesvg import GridContainer, TextNode, Renderer, templates

page = GridContainer(style={
    **templates.REPORT_PAGE,  # 800px 宽，白色背景，单列
})

page.add(TextNode("报告标题", style={
    **templates.TITLE,  # 28px 加粗居中
}))

page.add(TextNode("这是一段正文内容。", style={
    **templates.PARAGRAPH,  # 14px，行高 1.6
}))

Renderer().render(page, "report.svg")
```

<figure markdown="span">
  ![模板示例](../assets/images/examples/quickstart_template.svg){ loading=lazy }
  <figcaption>使用内置模板快速创建报告</figcaption>
</figure>

## Grid 放置

使用 `row`、`col` 参数精确控制子节点在网格中的位置：

```python
grid = GridContainer(style={
    "width": "400px",
    "grid-template-columns": ["1fr", "1fr", "1fr"],
    "grid-template-rows": ["auto", "auto"],
    "gap": "8px",
    "padding": "16px",
})

# 第 1 行第 1 列，横跨 2 列
grid.add(TextNode("跨两列"), row=1, col=1, col_span=2)

# 第 1 行第 3 列
grid.add(TextNode("右上角"), row=1, col=3)

# 第 2 行，横跨全部 3 列
grid.add(TextNode("底部全宽"), row=2, col=1, col_span=3)

Renderer().render(grid, "grid_placement.svg")
```

## 输出 PNG

```python
renderer = Renderer()
renderer.render_png(page, "output.png", scale=2.0)  # 2x 高清
```

!!! note "需要安装 `latticesvg[png]`"
    PNG 输出依赖 CairoSVG，请先运行 `pip install latticesvg[png]`。

## 下一步

- 📐 [Grid 布局教程](../tutorials/grid-layout.md) — 深入学习 CSS Grid 的各种技巧
- 📝 [文本排版教程](../tutorials/text-typography.md) — 掌握文本排版的精髓
- 🧩 [节点类型](../tutorials/node-types.md) — 了解所有可用节点
- 📖 [CSS 属性参考](../reference/css-properties.md) — 查阅所有支持的属性
