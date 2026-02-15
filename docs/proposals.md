# LatticeSVG 功能建议

> 基于项目定位「小而美的无浏览器 Python 矢量布局引擎」，按优先级组织。
> 前几轮提案已全部完成并合入，本文档为剩余待评估建议。

---

## 现状总结

LatticeSVG v0.1.0 已是一个**功能完备的版本**：

- CSS Grid Level 1 核心算法完备（固定/百分比/fr/auto/min-content/max-content/minmax 轨道，repeat() 函数，自动放置含 dense，跨行列，命名区域，隐式轨道 grid-auto-rows/columns）
- 6 种节点类型（GridContainer、TextNode、ImageNode、SVGNode、MplNode、MathNode）+ 可扩展的自定义 Node
- 基于 FreeType 的精确文本排版引擎（CJK 混排、字体回退链、5 种 white-space 模式、富文本标记）
- 标记系统（HTML 子集 + Markdown 子集，支持粗体/斜体/代码/删除线/上下标/内联数学）
- LaTeX 数学公式渲染（QuickJax 后端，独立公式 + 内联公式）
- 字体子集化嵌入（WOFF2 格式，完全自包含 SVG）
- 63 个 CSS 属性、完整盒模型、四角独立圆角、clip-path、渐变背景、text-decoration
- text-align: justify、box-shadow、transform、CSS filter、letter-spacing/word-spacing、hyphens 断词
- 47 个演示 + 10 个测试文件（352 个测试函数）
- ~8,900 行核心代码，硬依赖 `drawsvg` + `freetype-py` + `quickjax`

以下建议严格控制在**不改变项目定位、不膨胀架构**的前提下。

---

## 待评估提案

### P2-1. SVG 无障碍元数据

**价值**：为 SVG 输出添加结构化的无障碍信息（`<title>`、`<desc>`、`role`、`aria-label`），使屏幕阅读器能解读文档内容。在学术出版和政府文档场景中可能是合规要求。

**代价**：Node 基类新增可选 `title` / `description` / `aria_label` 属性，渲染器生成对应 SVG 元素。约 40 行改动。

**评估**：实现成本低，但对核心排版功能无直接增强，按需评估。

### P2-2. 容器自动高度优化

**价值**：当前 GridContainer 在不指定 `height` 时依赖 `available_height`（默认无穷大），容器高度实际由所有行轨道之和决定。但某些边缘场景下高度计算可能不够精确（如百分比高度的递归解析）。

**代价**：需审计 `grid_solver.py` 中的高度推算逻辑，确保百分比 height 的子项能正确基于容器内容高度解析。

**评估**：当前行为在主流场景下已正确，优化边缘情况可按实际反馈进行。

### P2-3. 列表标记支持

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

P1 层提案已全部完成并合入（justify 对齐、box-shadow、transform），P2 层中 filter、letter-spacing/word-spacing、hyphens 也已完成。剩余三个待评估提案（SVG 无障碍元数据、容器自动高度优化、列表标记支持）均可按实际使用反馈决定是否实现。
