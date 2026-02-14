# LatticeSVG 功能建议

> 基于项目定位「小而美的无浏览器 Python 矢量布局引擎」，按优先级组织。
> 上一版全部提案（P1 + P2）已完成并合入，本文档为新一轮建议。

---

## 现状总结

LatticeSVG v0.1.0 已是一个**功能完备的版本**：

- CSS Grid Level 1 核心算法完备（固定/百分比/fr/auto/min-content/max-content/minmax 轨道，repeat() 函数，自动放置含 dense，跨行列，命名区域，隐式轨道 grid-auto-rows/columns）
- 6 种节点类型（GridContainer、TextNode、ImageNode、SVGNode、MplNode、MathNode）+ 可扩展的自定义 Node
- 基于 FreeType 的精确文本排版引擎（CJK 混排、字体回退链、5 种 white-space 模式、富文本标记）
- 标记系统（HTML 子集 + Markdown 子集，支持粗体/斜体/代码/删除线/上下标/内联数学）
- LaTeX 数学公式渲染（QuickJax 后端，独立公式 + 内联公式）
- 字体子集化嵌入（WOFF2 格式，完全自包含 SVG）
- 56 个 CSS 属性、完整盒模型、四角独立圆角、clip-path、渐变背景、text-decoration
- 42 个演示 + 11 个测试文件（279 个测试函数）
- ~7,650 行核心代码，硬依赖 `drawsvg` + `freetype-py` + `quickjax`

以下建议严格控制在**不改变项目定位、不膨胀架构**的前提下。

---

## P1 — 高价值增量功能

### P1-1. `text-align: justify` 渲染完成

**场景**：学术报告、论文排版中两端对齐（justify）是最常见的段落对齐方式。当前 shaper 已识别 `justify` 关键字并为非末行设置 `offset = 0`，但渲染器未实现逐词间距分散，实际效果等同于左对齐。

**现状**：shaper.py 中 `align_lines()` 对 justify 非末行设置 `offset = 0` 并注释 "justify handled per-word at render time"，但 renderer.py 中无任何对应实现。

**方案**：

```python
text = TextNode("This is a justified paragraph with enough words to wrap.", style={
    "text-align": "justify",
    "width": "300px",
})
```

**技术路径**：

1. `shaper.py` 的 `align_lines()` 对 justify 非末行计算每个单词间隙：`extra_space = available_width - line_width`，`word_gap = extra_space / (word_count - 1)`
2. 返回值从单个 `offset` 扩展为 `(offset, word_gaps)` 或在 `Line` 数据结构中增加 `word_positions` 列表
3. `renderer.py` 渲染时使用逐词绝对定位（多个 `<text>` 元素）或 SVG `textLength` + `lengthAdjust="spacing"` 属性
4. 富文本 `align_lines_rich()` 同步支持

**改动范围**：修改 `shaper.py`（~30 行），修改 `renderer.py`（~40 行）。

**注意**：末行保持左对齐（CSS 标准行为）。CJK 文本的 justify 可按字符均匀分散。

### P1-2. `box-shadow` 支持

**场景**：卡片投影、按钮悬浮效果等是报告设计中极常见的视觉需求。当前仅有 `border` 和 `outline` 提供边缘装饰，无法实现柔和阴影效果。

**方案**：

```python
card = GridContainer(style={
    "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "border-radius": "8px",
    "background-color": "white",
    "padding": "20px",
})

# 多重阴影
card = GridContainer(style={
    "box-shadow": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
})
```

**技术路径**：

1. `properties.py` 新增 `box-shadow` 属性（默认 `none`，parser_hint `box-shadow`）
2. `parser.py` 新增 `parse_box_shadow(raw)` 函数，解析 `offset-x offset-y blur-radius spread-radius color` 语法（支持多重阴影以逗号分隔）
3. `renderer.py` 生成 SVG `<filter>` 元素（`<feDropShadow>` 或 `<feGaussianBlur>` + `<feOffset>` + `<feFlood>` + `<feMerge>` 组合）
4. 阴影不影响布局，仅在渲染阶段附加

**数据类**：`BoxShadow(offset_x, offset_y, blur_radius, spread_radius, color, inset=False)`

**改动范围**：`parser.py`（~60 行），`properties.py`（+2 行），`renderer.py`（~50 行）。

**注意**：仅支持外阴影（`inset` 可作为二期），不支持 `filter: drop-shadow()` 等通用滤镜。

### P1-3. `transform` 基础支持

**场景**：微调元素位置（`translate`）、旋转标签文字（`rotate`）、缩放装饰元素（`scale`）是排版中的常见需求。

**方案**：

```python
label = TextNode("Y 轴", style={
    "transform": "rotate(-90deg)",
})

badge = TextNode("NEW", style={
    "transform": "translate(10px, -5px) scale(0.8)",
})
```

**支持的函数（最小集）**：

| 函数 | 语法 | 说明 |
|---|---|---|
| `translate()` | `translate(x, y)` / `translateX(x)` / `translateY(y)` | 平移 |
| `rotate()` | `rotate(angle)` | 旋转（支持 `deg` / `rad`） |
| `scale()` | `scale(x, y)` / `scale(x)` | 缩放 |

**技术路径**：

1. `properties.py` 新增 `transform` 属性（默认 `none`，parser_hint `transform`）
2. `parser.py` 新增 `parse_transform(raw)` 解析函数链
3. `renderer.py` 在节点 `<g>` 包裹元素上添加 `transform` 属性——直接映射为 SVG transform 字符串
4. Transform 不影响布局——与 CSS 标准一致，仅影响视觉渲染

**改动范围**：`parser.py`（~40 行），`properties.py`（+2 行），`renderer.py`（~15 行）。

**注意**：不做 `transform-origin`（默认元素中心），不做 3D 变换。

---

## P2 — 按需评估

### P2-1. SVG 无障碍元数据

**价值**：为 SVG 输出添加结构化的无障碍信息（`<title>`、`<desc>`、`role`、`aria-label`），使屏幕阅读器能解读文档内容。在学术出版和政府文档场景中可能是合规要求。

**代价**：Node 基类新增可选 `title` / `description` / `aria_label` 属性，渲染器生成对应 SVG 元素。约 40 行改动。

**评估**：实现成本低，但对核心排版功能无直接增强，按需评估。

### P2-2. CSS `filter` 支持

**价值**：`filter: blur(5px)`、`filter: grayscale(100%)` 等可增强视觉表现力。SVG 原生有 `<filter>` 元素完整支持。

**代价**：需解析 `blur()` / `brightness()` / `contrast()` / `grayscale()` / `drop-shadow()` 等函数语法，每种映射到对应的 SVG filter primitive。

**评估**：与 `box-shadow`（P1-2）部分重叠。如果 P1-2 已完成 `<filter>` 基础设施，扩展到通用 filter 的增量成本较低。

### P2-3. 容器自动高度优化

**价值**：当前 GridContainer 在不指定 `height` 时依赖 `available_height`（默认无穷大），容器高度实际由所有行轨道之和决定。但某些边缘场景下高度计算可能不够精确（如百分比高度的递归解析）。

**代价**：需审计 `grid_solver.py` 中的高度推算逻辑，确保百分比 height 的子项能正确基于容器内容高度解析。

**评估**：当前行为在主流场景下已正确，优化边缘情况可按实际反馈进行。

### P2-4. `letter-spacing` / `word-spacing`

**价值**：字间距和词间距是排版精细调整的常用属性。对中文排版（`letter-spacing`）和英文排版（`word-spacing`）都有价值。

**代价**：`shaper.py` 在度量和折行时需考虑额外间距，`renderer.py` 输出 SVG `letter-spacing` / `word-spacing` 属性。约 30 行改动。

**评估**：实现简单，与 `text-align: justify`（P1-1）有协同价值。

### P2-5. 列表标记支持

**价值**：在 HTML 标记中支持 `<ul>` / `<ol>` / `<li>` 渲染无序 / 有序列表，Markdown 中支持 `- item` / `1. item` 语法。在报告生成中列表是常见的内容组织方式。

**代价**：列表涉及缩进、标记符号（要点符 / 数字）、嵌套层级等逻辑，已超出纯内联标记范畴，需要在 `TextNode` 内部实现块级分段能力。

**评估**：实现复杂度中等偏高，且可通过多个 `TextNode` + Grid 布局手动组合实现，优先级不高。

---

## 不建议做的方向

以下方向会显著扩大项目范围，与"小而美"定位相悖：

| 方向 | 不做的理由 |
|---|---|
| **Flexbox 布局引擎** | CSS Grid 已覆盖绝大多数二维布局需求，引入第二套布局引擎会造成维护负担翻倍 |
| **动画 / 交互** | 偏离"静态矢量输出"的核心定位，且 SVG 动画的跨平台兼容性差 |
| **PDF 直出** | 可通过 `cairosvg` → PDF 或 `weasyprint` 等外部工具链式完成，不必内建 |
| **完整 CSS 文本解析器** | 项目不是浏览器，`dict` 风格输入比解析 CSS 文本更 Pythonic、更可控 |
| **JavaScript 集成 / Web 预览** | 超出静态文档生成的职责范围 |
| **完整 HTML 渲染** | 富文本仅支持内联标签子集，不做块级元素解析——那是浏览器的工作 |
| **完整 LaTeX 排版** | 仅支持数学公式渲染（通过可插拔后端），不做多行推导编号、交叉引用、段落排版——那是 LaTeX 的工作 |
| **竖排文本 (writing-mode)** | CJK 竖排涉及字形旋转、标点挤压、行间距方向翻转等大量复杂度，收益有限 |
| **3D 变换** | SVG 不原生支持 3D，需 JavaScript 辅助，超出项目定位 |

---

## 总结

当前最有价值的增量方向是 **P1-1（justify 对齐）**——它是已有代码的收尾工作，对学术报告排版场景有直接价值。**P1-2（box-shadow）** 和 **P1-3（transform）** 是低成本高收益的视觉增强，直接映射到 SVG 原生能力，不引入架构复杂度。P2 层均可按实际使用反馈决定是否实现。
