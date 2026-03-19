# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## v0.1.3 — Matplotlib 字体便捷函数与回退修复（2026-03-19）

### 新增功能

- **Matplotlib 字体便捷函数**（`latticesvg.text`）
    - `mpl_font_context(font_family)` — 上下文管理器，临时将 LatticeSVG 字体应用于 matplotlib，退出时自动恢复。
    - `apply_mpl_fonts(font_family)` — 将 LatticeSVG 字体解析应用于 matplotlib 全局 `rcParams`。
    - `restore_mpl_fonts()` — 恢复到 `apply_mpl_fonts` 之前的状态。
    - 三个函数均接受 CSS `font-family` 字符串，通过 `addfont()` 注册字体，并设置 `svg.fonttype: "path"` + `axes.unicode_minus: False`。

### Bug 修复

- **修复 matplotlib 字体回退失败。** 此前 `font.family` 被设为泛型名（`"sans-serif"`），导致 matplotlib 只解析到一个字体文件，丢失逐字形 CJK 回退。现在设为具体字体名列表（如 `["Arial", "Microsoft YaHei"]`），使 `_find_fonts_by_props` 构建带 `_fallback_list` 的 `FT2Font`，实现逐字形回退。
- **修复 MplNode 对预创建 figure 的回退问题。** 同时填充 `font.sans-serif`、`font.serif`、`font.monospace` 列表，使在 `rc_context` 之前创建的 text 元素（其 `FontProperties` 默认为 `"sans-serif"`）也能解析到正确字体。

### 内部重构

- `MplNode._resolve_mpl_font_rc()` 和 `_register_fonts_with_mpl()` 已委托给 `latticesvg.text` 中的共享 `_build_mpl_rc()` 和 `_register_mpl_fonts()`。

---

## v0.1.2 — 字体查询 API 与 MplNode 自动字体配置（2026-03-19）

### 新增功能

- **字体查询 API**（`latticesvg.text`）
    - `get_font_path(family, weight="normal", style="normal") -> Optional[str]` — 将 CSS 字族名解析为文件系统路径，找不到时返回 `None`（不进行静默回退）。
    - `list_fonts() -> List[FontInfo]` — 枚举所有已索引字体，返回 `FontInfo` 数据类列表（字段：`family`、`path`、`weight`、`style`、`format`、`face_index`）。
    - `parse_font_families(value) -> List[str]` — 将 CSS `font-family` 字符串 / 列表 / `None` 解析为字族名平铺列表。
    - `FontInfo` 不可变数据类从 `latticesvg.text` 对外导出。
    - `FontManager` 新增实例方法：`get_font_path()` 和 `list_fonts()`。

- **MplNode — 自动字体配置**
    - 新参数 `auto_mpl_font: bool = True` — 启用后，`MplNode` 从计算/继承样式中读取 `font-family`，通过 `FontManager` 解析字体路径，调用 `fontManager.addfont()` 注册到 matplotlib，并在 `rc_context()` 中执行 `savefig()`，使图表文字与 LatticeSVG 布局使用相同字体。
    - 上下文内始终设置 `svg.fonttype="path"`，确保文字以矢量轮廓渲染。
    - 新参数 `tight_layout: bool = True` — 在字体感知的 `rc_context` 内调用 `figure.tight_layout()`，使标签度量在布局调整前即已正确。
    - 未在 `MplNode` 直接设置 `font-family` 时，自动继承父级 `GridContainer` 的字体设置。

### 示例

- `demo_51_font_query_mpl.py` — 2×2 多字体对比演示，展示 `get_font_path`、`list_fonts` 及 `MplNode` 自动字体，涵盖微软雅黑、楷体、仿宋、Noto Sans CJK JP。

---

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
