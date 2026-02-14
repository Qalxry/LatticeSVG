# LatticeSVG 功能建议

> 基于项目定位「小而美的无浏览器 Python 矢量布局引擎」，按优先级组织。
> 上一版 P0 / P1 及部分 P2 已全部完成并合入，本文档仅保留剩余和新增项。

---

## 现状总结

LatticeSVG v0.1.0 已是一个**完整度较高的版本**：

- CSS Grid Level 1 核心算法完备（固定/百分比/fr/auto/min-content/max-content 轨道，自动放置含 dense，跨行列，命名区域）
- 5 种节点类型（GridContainer、TextNode、ImageNode、SVGNode、MplNode）+ 可扩展的自定义 Node
- 基于 FreeType 的精确文本排版引擎（CJK 混排、字体回退链、5 种 white-space 模式）
- 50+ CSS 属性、完整的盒模型（含 box-sizing）、outline、border-radius、opacity
- 32 个演示 + 8 个测试文件
- 仅 ~4,600 行核心代码，硬依赖仅 `drawsvg` + `freetype-py`

以下建议严格控制在**不改变项目定位、不膨胀架构**的前提下。

---

## P1 — 高价值增量功能

### P1-1. 富文本 / 内联样式支持

**场景**：在报告生成中，一个段落内经常需要混合粗体、斜体、颜色高亮、代码片段等样式。当前 `TextNode` 仅支持整段统一样式，用户必须手动拆分为多个节点并用 Grid 拼接，极不方便。

**方案**：引入轻量级标记语法，在单个 `TextNode` 内支持内联样式片段。

```python
# 方案 A：HTML 子集（推荐）
text = TextNode(
    '这是<b>加粗</b>和<i>斜体</i>以及<span style="color:red">红色</span>文字',
    style={"font-size": "14px"},
    markup="html",
)

# 方案 B：Markdown 子集
text = TextNode(
    "这是**加粗**和*斜体*以及`代码`文字",
    style={"font-size": "14px"},
    markup="markdown",  # default="markdown"
)
```

**支持的标签/语法（最小集）**：

| HTML 标签 | Markdown | 效果 |
|---|---|---|
| `<b>` / `<strong>` | `**text**` | 加粗 |
| `<i>` / `<em>` | `*text*` | 斜体 |
| `<code>` | `` `text` `` | 等宽字体 + 可选背景色 |
| `<span style="...">` | — | 内联样式（`color`、`font-size`、`background-color`） |
| `<br>` | — | 强制换行 |
| `<sub>` / `<sup>` | — | 下标 / 上标（缩小字号 + 偏移 baseline） |

**技术路径**：

1. 新增 `markup/` 模块，使用 Python 标准库 `html.parser.HTMLParser` 解析 HTML 子集
2. 解析结果为 `List[TextSpan]`，每个 span 带独立样式覆盖
3. `shaper.py` 的 `break_lines()` 扩展为接受 span 列表输入，每个 span 独立度量
4. `renderer.py` 渲染为 SVG `<tspan>` 元素嵌入 `<text>` 内
5. Markdown 支持可作为二期，先用正则预处理转为 HTML 子集 AST

**改动范围**：新增 `markup/parser.py`（~150 行），修改 `shaper.py`（~80 行），修改 `renderer.py`（~40 行）。

**注意**：不做完整的 HTML 渲染——不支持块级元素（`<div>`、`<p>`）、不支持嵌套列表、不支持 CSS class。保持叶节点语义：`TextNode` 依然是一个文本块，只是内部可含不同样式的 span。

### P1-2. LaTeX 数学公式支持（可插拔后端）

**场景**：论文图表、实验报告中频繁出现数学公式。当前用户只能预渲染公式为图片再用 `ImageNode` 嵌入，流程割裂且无法保持矢量输出。

**方案**：新增 `MathNode` 节点类型，接受 LaTeX 数学表达式，渲染为 SVG 路径嵌入。后端设计为可插拔架构，默认使用 `matplotlib.mathtext`，可配置切换到 MathJax 等更强大的后端。

```python
# 独立公式块（默认后端）
formula = MathNode(r"E = mc^2", style={"font-size": "20px"})

# 指定后端
formula = MathNode(
    r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}",
    style={"font-size": "18px"},
    backend="quickjax",  # 使用 QuickJaxBackend（MathJax v4 via QuickJS）
)

# 内联公式（配合 P1-1 富文本）
text = TextNode(
    r'由欧拉公式 <math>e^{i\pi} + 1 = 0</math> 可知...',
    style={"font-size": "14px"},
    markup="html",
)

# 内联公式（配合 P1-1 富文本）
text = TextNode(
    r'由欧拉公式 $e^{i\pi} + 1 = 0$ 可知...',
    style={"font-size": "14px"},
    markup="markdown",
)

# 全局配置默认后端
from latticesvg.math import set_default_backend
set_default_backend("katex")
```

#### 后端架构

```
MathNode
  │
  ▼
MathBackend (Protocol)          # 抽象接口
  ├── .render(latex, font_size) → SVGFragment(svg_content, width, height)
  └── .available() → bool       # 检查后端是否可用
  │
  ├── QuickJaxBackend (默认)    # MathJax v4 via QuickJS
  └── (用户可自定义后端)
```

### P1-3. `grid-auto-rows` / `grid-auto-columns`

**场景**：大量自动放置项目时，隐式轨道尺寸不可控（当前硬编码为 `auto`），无法指定统一行高。

**方案**：

```python
grid = GridContainer(style={
    "grid-template-columns": ["1fr", "1fr", "1fr"],
    "grid-auto-rows": "150px",   # 所有隐式行都是 150px
})
```

1. `properties.py` 新增两个属性
2. `grid_solver.py` 的 `_extend_tracks()` 从样式中读取默认隐式轨道尺寸

**改动范围**：约 15 行。

---

## P2 — 按需评估

### P2-1. 四角独立 `border-radius`

**价值**：支持 `border-radius: 10px 20px 0 5px` 四角独立值，可实现 Tab 标签、对话气泡等仅部分圆角的场景。

**代价**：SVG `<rect>` 的 `rx/ry` 仅支持统一值，四角独立需改用 `<path>` 绘制圆角矩形，渲染器改动较大。

**评估**：当前统一单值已覆盖卡片/按钮等主流场景，四角独立按需再做。

### P2-2. `clip-path` 支持

**价值**：CSS `clip-path` 可实现圆形裁剪、多边形蒙版等高级视觉效果（头像裁圆、斜切 Banner 等）。

**代价**：需解析 `circle()`、`ellipse()`、`polygon()`、`inset()` 等函数语法，解析复杂度中等偏高。

**评估**：SVG 原生支持 `<clipPath>`，映射路径清晰，但在报告生成场景中并非刚需。

### P2-3. `repeat()` / `minmax()` 轨道函数

**价值**：避免手动写 `["1fr"] * 10`，支持 `"repeat(3, 1fr)"` 和 `"minmax(100px, 1fr)"` 语法。

**代价**：解析器需新增函数语法支持（正则 + 递归下降），`minmax` 还需扩展轨道尺寸算法。

**评估**：`repeat()` 实现简单（解析后展开为列表即可），`minmax()` 需要修改 `_resolve_tracks_axis` 逻辑。建议先做 `repeat()`。

### P2-4. 渐变背景

**价值**：`background: linear-gradient(#e66465, #9198e5)` 可增强视觉表现力，SVG 原生有 `<linearGradient>` / `<radialGradient>` 支持。

**代价**：需在样式解析器中新增渐变语法解析，渲染器中创建 `<defs>` + `<linearGradient>` 元素并关联 `fill="url(#grad)"` 引用。

**评估**：解析器改动中等，渲染路径清晰，属于视觉增强功能，按需评估。

### P2-5. `text-decoration` 支持

**价值**：下划线（`underline`）、删除线（`line-through`）在文档排版中常用。

**代价**：SVG `<text>` 原生支持 `text-decoration` 属性，实现成本极低。

**评估**：约 5 行改动即可实现基本支持，建议与 P1-1 富文本一并实现。

### P2-6. 字体嵌入 / 子集化

**价值**：当前 SVG 输出中的 `<text>` 使用 `font-family` 名称引用，目标机器缺少该字体时显示会不一致。将使用的字形子集化嵌入到 SVG 的 `<defs><style>@font-face{...}</style></defs>` 中可实现完全自包含的 SVG。

**代价**：需要 `fonttools` 依赖做子集化提取（`from fontTools.subset import Subsetter`），约 100-150 行代码。

**评估**：对"确定性渲染"定位有显著提升，但引入新依赖，属于高级功能按需评估。

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

---

## 总结

当前最有价值的增量方向是 **P1-1（富文本）** 和 **P1-2（LaTeX 公式）**——它们直接扩展了"矢量报告生成"的表达能力，且技术方案克制（HTML 子集 + matplotlib.mathtext），不引入重量级依赖。P1-3 是小而确定的补强。P2 层均可按实际使用反馈决定是否实现。
