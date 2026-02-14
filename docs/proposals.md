# LatticeSVG 功能建议

> 基于项目定位「小而美的 CSS Grid 矢量布局引擎」，按"修补 → 补强 → 克制"三层组织。

---

## 评估结论

LatticeSVG v0.1.0 已经是一个**完整度较高的首版**：CSS Grid Level 1 核心算法完备，5 种节点类型覆盖主要内容需求，文本引擎含 CJK 混排和字体回退链，样式系统 50+ 属性。对于"程序化生成矢量报告/图表"这一定位，当前能力已经足够撑起实际使用。

以下建议严格控制在**不改变项目定位、不膨胀架构**的前提下。

---

## ~~P0 — 修补已声明但未完成的功能~~（已完成）

这些属性已在代码中注册/标注，但未实际接线。不修则形成"文档说支持但实际不工作"的落差。

### ~~P0-1. `min-width` / `max-width` / `min-height` / `max-height` 接线~~（已完成）

**现状**：`properties.py` 中已注册这四个属性并有默认值，`ComputedStyle` 可正常读取，但 `GridSolver` 完全未使用它们。

**建议**：在 `GridSolver` 的列/行轨道尺寸计算后增加 clamp 逻辑：

```python
resolved_w = max(min_width, min(resolved_w, max_width))
```

或者如果短期不打算实现，从属性注册表中移除以避免误导用户。

**改动范围**：`grid_solver.py` 的 `_resolve_tracks_axis` 和子节点布局阶段。

### ~~P0-2. `text-overflow: ellipsis` 精度修正~~（已完成）

**现状**：`renderer.py` 中截断判断使用 `font_size * 0.6` 近似每个字符宽度，导致在 CJK 或非等宽字体下偏差明显。

**建议**：使用 `measure_text("…", font_path, font_size)` 获取省略号的精确宽度，用 `measure_text()` 逐步截断文本直到放得下。

**改动范围**：`renderer.py` 的 `_render_text` 方法，约 10-20 行改动。

### ~~P0-3. `white-space: pre-line` 实现~~（已完成）

**现状**：`parser.py` 接受 `pre-line` 关键字且不报错，但 `shaper.py` 的 `break_lines()` 无对应分支，会 fallback 到默认行为。

**建议**：`pre-line` 语义为"折叠连续空格，但保留显式换行符 `\n`"。在 `break_lines()` 中增加一个分支：先按 `\n` 分段，每段内按 `normal` 模式折行。

**改动范围**：`shaper.py` 增加 `_break_pre_line()` 函数，约 15-20 行。

### ~~P0-4. `opacity` 渲染~~（已完成）

**现状**：`properties.py` 注册了 `opacity` 属性（默认 `1`），但渲染器未读取。

**建议**：在 `_render_node` 中为背景矩形和文本元素添加 `opacity` 属性输出。drawsvg 支持 `opacity` 参数。

**改动范围**：`renderer.py`，约 5 行。

---

## ~~P1 — 高频场景补强~~（已完成）

投入小、收益大的增量功能，面向实际报告生成场景中的高频需求。

### ~~P1-1. `border-radius` 支持~~（已完成）

**场景**：卡片、提示框、按钮样式在报告中极其常见，圆角是最基础的视觉修饰。

**方案**：
1. `properties.py` 新增 `border-radius` 属性（默认 `0px`）
2. `renderer.py` 将当前的四条 `Line` 边框改为 `<rect>` 并设置 `rx` / `ry`

**改动范围**：两个文件，约 20-30 行。支持统一圆角即可，不需要四角独立值。

### ~~P1-2. `border-style: dashed | dotted` 支持~~（已完成）

**场景**：表格分隔线、辅助参考线常用虚线。

**方案**：渲染器中根据 `border-*-style` 值设置 `stroke-dasharray`。当前属性和样式注册已在位，仅需渲染器增加判断。

**改动范围**：`renderer.py` 边框渲染部分，约 10 行。

### ~~P1-3. 便捷的 `render_to_drawing()` 语义~~（已完成）

**场景**：用户想在 LatticeSVG 渲染后继续操作 Drawing——比如添加水印、手动叠加标注、合并多个布局结果。

**现状**：`render()` 方法已返回 `drawsvg.Drawing`，但它同时执行了文件写入。用户如果只想拿 Drawing 对象不得不用 `render_to_string()` 再自行构建 Drawing。

**方案**：无需新增方法，只需在文档中明确说明 `render()` 的返回值可以继续使用。或者如果希望更清晰，提供一个不写文件的 `render_to_drawing()` 方法。

**改动范围**：约 5 行代码 + 文档。

---

## P2 — 按需评估

以下功能有一定价值但不紧迫，可根据实际使用反馈决定是否实现。

### P2-1. `grid-template-areas` 命名区域

**价值**：`"header header" "sidebar main" "footer footer"` 式语义化布局声明可读性更好。
**代价**：解析器 + GridSolver 均需扩展，中等复杂度。
**评估**：当前行列线放置（`row=1, col=2, col_span=2`）已够用，命名区域是锦上添花。

### P2-2. 表格便捷 API

**价值**：`Table(headers=["名称", "值"], rows=data, style=...)` 式的快速封装，在实验报告场景高频出现。
**评估**：这属于"上层工具" 而非"引擎核心"——可以作为 `templates.py` 中的辅助函数或独立的 `contrib` 模块，不应侵入核心节点体系。

### P2-3. `grid-auto-rows` / `grid-auto-columns`

**价值**：控制隐式轨道尺寸（当前硬编码为 `auto`）。
**评估**：仅在大量自动放置项场景下有用，优先级低。

### P2-4. 四角独立 `border-radius`

**价值**：支持 `border-radius: 10px 20px 0 5px` 四角独立值及 `10px 20px` 对角缩写，可实现 Tab 标签、对话气泡等仅部分圆角的场景。
**代价**：SVG `<rect>` 的 `rx/ry` 仅支持统一值，四角独立需改用 `<path>` 绘制圆角矩形，渲染器改动较大。百分比（`50%`）和斜杠语法（`10px / 20px`）收益过低，不纳入。
**评估**：当前统一单值已覆盖卡片/按钮等主流场景，四角独立按需再做。

### P2-5. `clip-path` 支持

**价值**：CSS `clip-path` 可实现圆形裁剪、多边形蒙版、不规则形状容器等高级视觉效果。在头像裁圆、斜切 Banner、装饰性形状等场景中有用。
**代价**：需要在属性注册表中新增 `clip-path` 属性，解析器需支持 `circle()`、`ellipse()`、`polygon()`、`inset()` 等函数语法，渲染器中映射到 SVG `<clipPath>` 元素。解析复杂度中等偏高。
**评估**：SVG 原生支持 `<clipPath>`，映射路径清晰；但函数语法解析需较多代码，且在报告生成场景中并非刚需。按需评估。

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

---

## 总结

LatticeSVG 当前最需要的是 **P0 层的"完善性修补"**——让已声明的功能真正工作。P1 层的 `border-radius` 和 `border-style` 对实际使用体验提升最大，建议在 v0.2.0 纳入。P2 及以下均可不做，保持项目的克制和聚焦。
