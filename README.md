# LatticeSVG

基于 CSS Grid 的矢量布局引擎，输出高质量 SVG/PNG。

## 安装

```bash
pip install latticesvg

# 如需 PNG 输出
pip install latticesvg[png]
```

## 快速开始

```python
from latticesvg import GridContainer, TextNode, ImageNode, Renderer

grid = GridContainer(style={
    "width": "800px",
    "padding": "20px",
    "background-color": "#ffffff",
    "grid-template-columns": ["200px", "1fr"],
    "gap": "20px",
})

title = TextNode("实验报告", style={
    "font-size": "24px",
    "font-weight": "bold",
    "color": "#333333",
    "justify-self": "center",
})
grid.add(title, row=1, col=1)

grid.layout(available_width=800)

renderer = Renderer()
renderer.render(grid, "report.svg")
```

## 依赖

- Python ≥ 3.8
- drawsvg — SVG 生成
- freetype-py — 文本测量
- cairosvg（可选）— PNG 转换

## 许可证

MIT
