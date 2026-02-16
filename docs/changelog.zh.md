# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## v0.1.0 — 初始版本

首个公开发布版本。

### 核心功能

- **CSS Grid 布局引擎**
    - `grid-template-columns` / `grid-template-rows`（fixed, fr, auto, min-content, max-content）
    - `repeat()` 和 `minmax()` 函数
    - `grid-template-areas` 命名区域
    - `grid-auto-rows` / `grid-auto-columns` 自动轨道
    - `gap` / `row-gap` / `column-gap`
    - 自动放置算法
    - 子项跨行/列 (`row_span`, `col_span`)
    - 容器级对齐 (`justify-content`, `align-content`)
    - 子项级对齐 (`justify-self`, `align-self`)

- **文本排版引擎**
    - FreeType 字体测量（Pillow 后备）
    - 自动换行（`white-space`: normal, nowrap, pre, pre-wrap, pre-line）
    - `overflow-wrap: break-word`
    - `text-overflow: ellipsis`
    - 自动断字 (`hyphens: auto`，需 pyphen)
    - `letter-spacing` / `word-spacing`
    - 多字体回退链 (`font-family` 逗号分隔)
    - 行高控制 (`line-height`)
    - 垂直排版 (`writing-mode: vertical-rl/lr`, `sideways-rl/lr`)
    - `text-orientation` / `text-combine-upright`

- **富文本支持**
    - HTML 标记 (`<b>`, `<i>`, `<span style="...">`, `<br>`, `<math>`, etc.)
    - Markdown 标记 (`**bold**`, `*italic*`, `` `code` ``, `$math$`, etc.)
    - 行内数学公式嵌入

- **节点类型**
    - `GridContainer` — Grid 布局容器
    - `TextNode` — 文本节点
    - `ImageNode` — 图片节点（文件/URL/bytes/PIL）
    - `SVGNode` — SVG 嵌入节点
    - `MplNode` — Matplotlib 图形嵌入
    - `MathNode` — LaTeX 公式节点

- **视觉样式**（63 个 CSS 属性）
    - 盒模型（margin, padding, border, width/height, min/max-width/height）
    - `border-radius`（四角独立）
    - `border-style`（solid, dashed, dotted, double, none）
    - `background`（纯色 + 线性/径向渐变）
    - `opacity`
    - `box-shadow`（单个/多个）
    - `transform`（translate, rotate, scale, skew）
    - `filter`（blur, drop-shadow, brightness, contrast, etc.）
    - `clip-path`（circle, ellipse, polygon, inset）
    - `box-sizing: border-box / content-box`

- **渲染输出**
    - SVG 文件输出 (`render()`)
    - SVG 字符串 (`render_to_string()`)
    - `drawsvg.Drawing` 对象 (`render_to_drawing()`)
    - PNG 输出 (`render_png()`，需 cairosvg)
    - 字体子集化嵌入 (`embed_fonts=True`，需 fonttools)

- **模板系统**
    - 17 个内置样式模板
    - `build_table()` 表格构建器
    - `ALL_TEMPLATES` 模板索引

- **数学公式引擎**
    - QuickJax 后端（MathJax v4 in-process）
    - display / inline 两种模式
    - 可注册自定义后端

### 依赖

- Python ≥ 3.8
- drawsvg ≥ 2.0
- freetype-py ≥ 2.3
- quickjax ≥ 0.1.0
- 可选：cairosvg（PNG 输出）、pyphen（断字）、fonttools（字体嵌入）
