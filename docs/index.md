---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

# LatticeSVG

**基于 CSS Grid 的声明式矢量布局引擎**

用 Python 字典描述布局 → 引擎完成测量、排版、渲染 → 输出精确到像素的 SVG / PNG

[快速开始](getting-started/quickstart.md){ .md-button .md-button--primary }
[API 参考](reference/api/index.md){ .md-button }

</div>

<figure markdown="span">
  ![示例效果](assets/images/examples/landing_hero.svg){ loading=lazy }
  <figcaption>LatticeSVG 渲染效果预览</figcaption>
</figure>

---

<div class="feature-grid" markdown>

<div class="feature-card" markdown>

### :material-grid: CSS Grid 布局

完整的 CSS Grid Level 1 实现——固定轨道、`fr` 弹性单位、`minmax()`、`repeat()`、命名区域、自动放置算法，一切尽在掌握。

</div>

<div class="feature-card" markdown>

### :material-format-text: 精确文本排版

基于 FreeType 的字形级精确测量，支持自动折行、CJK 排版、两端对齐、富文本标记、竖排文本、自动断词。

</div>

<div class="feature-card" markdown>

### :material-puzzle: 多节点类型

`TextNode`、`ImageNode`、`SVGNode`、`MplNode`（Matplotlib）、`MathNode`（LaTeX 公式）——任意组合嵌套。

</div>

<div class="feature-card" markdown>

### :material-palette: 完整视觉样式

63 个 CSS 属性：盒模型、圆角、边框样式、渐变背景、阴影、变换、滤镜、裁剪路径、透明度。

</div>

<div class="feature-card" markdown>

### :material-file-document: 声明式 API

所有配置通过 Python `dict` 传入，属性名与 CSS 一致。无需学习新的 DSL，CSS 经验直接复用。

</div>

<div class="feature-card" markdown>

### :material-image-multiple: SVG & PNG 输出

默认输出矢量 SVG，可选通过 CairoSVG 导出高分辨率 PNG。支持 WOFF2 字体子集化嵌入。

</div>

</div>

---

## 极简示例

```python
from latticesvg import GridContainer, TextNode, Renderer

# 1. 创建 Grid 容器
page = GridContainer(style={
    "width": "600px",
    "padding": "24px",
    "grid-template-columns": ["1fr", "1fr"],
    "gap": "16px",
    "background-color": "#ffffff",
})

# 2. 添加子节点
page.add(TextNode("Hello", style={"font-size": "24px", "color": "#2c3e50"}))
page.add(TextNode("World", style={"font-size": "24px", "color": "#e74c3c"}))

# 3. 渲染输出
Renderer().render(page, "hello.svg")
```

<figure markdown="span">
  ![极简示例效果](assets/images/examples/quickstart_two_col.svg){ loading=lazy }
  <figcaption>上述代码的渲染结果</figcaption>
</figure>

---

## 安装

```bash
pip install latticesvg

# 如需 PNG 输出
pip install latticesvg[png]

# 如需自动断词
pip install latticesvg[hyphens]
```

!!! info "系统依赖"
    LatticeSVG 需要系统安装 FreeType 库。大多数 Linux 发行版和 macOS 已预装。
    Windows 用户请参阅 [安装指南](getting-started/installation.md)。

---

## 项目状态

| 指标 | 数据 |
|---|---|
| 版本 | v0.1.0 |
| 许可证 | MIT |
| Python | ≥ 3.8 |
| 核心代码 | ~8,900 行 |
| 测试 | 352 个测试函数 |
| 演示 | 50 个示例脚本 |
