# API 概览

LatticeSVG 的公共 API 通过顶层包导出 13 个符号。

## 快速导入

```python
from latticesvg import (
    # 节点类型
    Node,            # 抽象基类
    GridContainer,   # Grid 容器
    TextNode,        # 文本节点
    ImageNode,       # 图片节点
    SVGNode,         # SVG 嵌入节点
    MplNode,         # Matplotlib 节点
    MathNode,        # LaTeX 公式节点

    # 几何类型
    Rect,            # 矩形
    LayoutConstraints,  # 布局约束

    # 渲染
    Renderer,        # SVG/PNG 渲染器

    # 样式
    ComputedStyle,   # 计算后的样式对象

    # 模板
    templates,       # 内置样式模板模块
    build_table,     # 表格构建函数
)
```

## 模块结构

| 模块 | 职责 | 主要导出 |
|---|---|---|
| [`latticesvg.nodes`](nodes.md) | 节点类型定义 | `Node`, `GridContainer`, `TextNode`, `ImageNode`, `SVGNode`, `MplNode`, `MathNode` |
| [`latticesvg.render`](renderer.md) | SVG 渲染 | `Renderer` |
| [`latticesvg.style`](style.md) | 样式解析与计算 | `ComputedStyle`, `parse_value`, `PROPERTY_REGISTRY` |
| [`latticesvg.text`](text.md) | 文本测量与排版 | `FontManager`, `measure_text`, `break_lines` |
| [`latticesvg.layout`](layout.md) | Grid 布局求解 | `GridSolver` |
| [`latticesvg.markup`](markup.md) | 富文本标记解析 | `TextSpan`, `parse_markup`, `parse_html`, `parse_markdown` |
| [`latticesvg.math`](math.md) | 数学公式渲染 | `MathBackend`, `QuickJaxBackend`, `SVGFragment` |
| [`latticesvg.templates`](../templates.md) | 内置样式模板 | 17 个模板 + `build_table()` |

## 版本

```python
import latticesvg
print(latticesvg.__version__)  # "0.1.0"
```
