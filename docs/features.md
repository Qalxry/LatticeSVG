# LatticeSVG 功能全景

> 版本 0.1.0 · 基于 CSS Grid 的矢量布局引擎，输出高质量 SVG / PNG

---

## 1. 项目定位

LatticeSVG 是一个 **Python 声明式矢量布局引擎**——用户以类似 CSS 的 `dict` 描述布局意图，引擎完成测量、排版、渲染全流水线，输出精确到像素的 SVG（可选 PNG）。

核心场景：程序化生成实验报告、数据可视化排版、论文图表拼接等需要精确控制位置和字体的静态矢量文档。

### 依赖

| 依赖 | 角色 |
|---|---|
| `drawsvg ≥ 2.0` | SVG 文档生成（元素创建、序列化） |
| `freetype-py ≥ 2.3` | FreeType 绑定，精确字形度量 |
| `cairosvg ≥ 2.5`（可选） | SVG → PNG 转换 |
| `Pillow`（可选） | 字形度量后备 + 图片尺寸探测 |
| `matplotlib`（可选） | `MplNode` 图表嵌入 |

### 公开 API

```python
from latticesvg import (
    GridContainer,   # Grid 容器节点
    TextNode,        # 文本节点
    ImageNode,       # 光栅图片节点
    SVGNode,         # 嵌入 SVG 节点
    MplNode,         # 嵌入 Matplotlib 图表节点
    Renderer,        # 渲染器
    Node,            # 抽象基类（可继承扩展）
    Rect,            # 轴对齐矩形
    LayoutConstraints,
    ComputedStyle,   # 计算后的样式对象
    templates,       # 17 个内置样式模板
    build_table,     # 表格便捷构建函数
)
```

---

## 2. 架构总览

```
                 User Code
                     │
                     ▼
┌──────────────────────────────────────────┐
│  Public API Layer  (__init__.py)         │
│  GridContainer, TextNode, ImageNode, ... │
└────────────────────┬─────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
       style/      nodes/      text/
       parser      base        font
       properties  grid        shaper
       computed    text/image
                   svg/mpl
                     │
             ┌───────┴───────┐
             ▼               ▼
          layout/          render/
          grid_solver      renderer
```

**数据流**：构建节点树 → `ComputedStyle` 解析样式 → `GridSolver` 执行布局（measure + solve）→ `Renderer` 生成 SVG / PNG。

---

## 3. 样式系统

### 3.1 CSS 属性注册表

共注册 **50+ 个属性**，分为四大类：

#### 盒模型（不可继承）

| 属性 | 默认值 | 说明 |
|---|---|---|
| `width` / `height` | `auto` | 显式尺寸 |
| `min-width` / `max-width` | `0px` / `none` | 尺寸约束 |
| `min-height` / `max-height` | `0px` / `none` | 尺寸约束 |
| `margin-top/right/bottom/left` | `0px` | 外边距（支持 `margin` 简写） |
| `padding-top/right/bottom/left` | `0px` | 内边距（支持 `padding` 简写） |
| `border-*-width` | `0px` | 边框宽度（支持 `border-width` / `border` 简写） |
| `border-*-color` | `none` | 边框颜色 |
| `border-*-style` | `none` | 边框样式（`solid` / `dashed` / `dotted`） |
| `border-radius` | `0px` | 圆角半径（统一值） |
| `box-sizing` | `border-box` | 盒尺寸模型（`border-box` / `content-box`） |
| `outline-width` / `outline-color` | `0px` / `none` | 外轮廓宽度和颜色 |
| `outline-style` | `none` | 外轮廓样式（`solid` / `dashed` / `dotted`） |
| `outline-offset` | `0px` | 外轮廓与边框的间距 |

#### Grid 布局（不可继承）

| 属性 | 默认值 | 说明 |
|---|---|---|
| `display` | `block` | 仅 `grid` 有效 |
| `grid-template-columns` | `None` | 列轨道模板 |
| `grid-template-rows` | `None` | 行轨道模板 |
| `grid-template-areas` | `None` | 命名区域模板 |
| `row-gap` / `column-gap` | `0px` | 轨道间距（支持 `gap` 简写） |
| `justify-items` / `align-items` | `stretch` | 网格项默认对齐 |
| `justify-self` / `align-self` | `auto` | 网格项个体对齐 |
| `grid-auto-flow` | `row` | 自动放置方向 |
| `grid-row` / `grid-column` | `None` | 显式行/列位置 |
| `grid-area` | `None` | 命名区域放置（配合 `grid-template-areas`） |

#### 文本（可继承）

| 属性 | 默认值 | 说明 |
|---|---|---|
| `font-family` | `sans-serif` | 字体族（支持回退链） |
| `font-size` | `16px` | 字号 |
| `font-weight` | `normal` | 字重（`normal` / `bold`） |
| `font-style` | `normal` | 字形（`normal` / `italic`） |
| `text-align` | `left` | 水平对齐（`left` / `center` / `right`） |
| `line-height` | `1.2` | 行高（≤ 5.0 视为倍数，否则为绝对值） |
| `white-space` | `normal` | 空白处理（`normal` / `nowrap` / `pre` / `pre-wrap` / `pre-line`） |
| `overflow-wrap` | `normal` | 溢出折行（`normal` / `break-word` / `anywhere`） |
| `color` | `#000000` | 文本颜色 |

#### 视觉（不可继承，除 `color`）

| 属性 | 默认值 | 说明 |
|---|---|---|
| `background-color` | `none` | 背景色 |
| `opacity` | `1` | 不透明度 |
| `overflow` | `visible` | 溢出处理（`visible` / `hidden`） |
| `text-overflow` | `clip` | 文本溢出（`clip` / `ellipsis`） |
| `object-fit` | `fill` | 图片适配（`fill` / `contain` / `cover` / `none`） |

### 3.2 值解析

**支持的长度单位**：

| 单位 | 说明 |
|---|---|
| `px` | 像素（默认） |
| `%` | 百分比（相对父级对应轴尺寸，延迟解析） |
| `em` | 相对当前元素 `font-size` |
| `rem` | 相对根元素 `font-size`（默认 16px） |
| `fr` | Grid 弹性单位 |
| `pt` | 磅（1pt = 4/3 px @96dpi） |

**颜色格式**：

| 格式 | 示例 |
|---|---|
| `#hex` (3/4/6/8 位) | `#f00`, `#ff0000`, `#ff000080` |
| `rgb()` | `rgb(255, 0, 0)` |
| `rgba()` | `rgba(255, 0, 0, 0.5)` |
| 命名颜色 | `red`, `blue`, `transparent` 等 26 种 |

**简写展开**：

| 简写 | 展开为 |
|---|---|
| `margin` | `margin-top/right/bottom/left`（1→4 值规则） |
| `padding` | `padding-top/right/bottom/left` |
| `border-width` | `border-top/right/bottom/left-width` |
| `border-color` | `border-top/right/bottom/left-color` |
| `gap` | `row-gap` + `column-gap` |
| `border` | 拆解为 `width` + `style` + `color` |
| `outline` | 拆解为 `outline-width` + `outline-style` + `outline-color` |

**Grid 行列线规范**：支持 `"2 / span 3"` 语法，解析为 `(start, span)` 元组。

### 3.3 ComputedStyle

- 合并父级样式（可继承属性自动继承）→ 填充默认值 → 解析用户声明值
- 优先解析 `font-size`（因为 `em` 单位依赖它）
- 支持 Python 属性风格访问：`style.font_size` ⇔ `style.get("font-size")`
- 便利属性：`margin_horizontal`、`padding_vertical`、`border_horizontal` 等聚合访问器
- `resolve_percentages(ref_width, ref_height)` 延迟解析百分比

---

## 4. 节点类型

### 4.1 Node（抽象基类）

所有节点的公共接口：

| API | 说明 |
|---|---|
| `.style: ComputedStyle` | 计算后的样式 |
| `.children: List[Node]` | 子节点 |
| `.border_box` / `.padding_box` / `.content_box` | 三层盒模型矩形（布局后填充） |
| `.placement: PlacementHint` | Grid 放置信息（行/列起始 + 跨度） |
| `.add(child, *, row, col, row_span, col_span)` | 添加子节点并设置 Grid 位置 |
| `.measure(constraints) → (min_w, max_w, h)` | 测量（子类实现） |
| `.layout(constraints)` | 执行布局（子类实现） |

`Rect(x, y, width, height)` 是轴对齐矩形，提供 `.right`、`.bottom`、`.copy()` 便利方法。

### 4.2 GridContainer

CSS Grid 布局容器。所有 Grid 算法委托给 `GridSolver`。

```python
grid = GridContainer(style={
    "width": "800px",
    "grid-template-columns": ["200px", "1fr", "1fr"],
    "grid-template-rows": ["auto", "1fr"],
    "gap": "10px",
})
grid.add(child, row=1, col=1, col_span=2)
grid.layout(available_width=800)
```

**支持的轨道类型**：`<length>` / `<percentage>` / `fr` / `auto` / `min-content` / `max-content`

**命名区域**：`grid-template-areas` 支持语义化布局声明，如 `"header header" "sidebar main" "footer footer"`。使用 `.add(child, area="header")` 将子节点放置到命名区域。

**自动放置**：`grid-auto-flow: row | column | row dense | column dense`

**对齐**：`justify-items/self` + `align-items/self`，值可为 `stretch`（默认）/ `start` / `center` / `end`

**嵌套**：Grid 可作为另一个 Grid 的子项，递归布局。

### 4.3 TextNode

精确排版的文本叶节点：

```python
text = TextNode("Hello, 世界！", style={
    "font-family": "Times, SimSun, serif",
    "font-size": "14px",
    "text-align": "center",
    "white-space": "normal",
    "overflow-wrap": "break-word",
})
```

**特性**：

- **字体回退链**：按 `font-family` 列表顺序逐字符查找可用字形
- **CJK 混排**：中日韩字符逐字可断行，与西文自然混排
- **white-space 模式**：`normal`（折行+折叠空白）、`nowrap`（不折行）、`pre`（保留换行和空白）、`pre-wrap`（保留空白但可折行）、`pre-line`（折叠空白但保留显式换行）
- **overflow-wrap**：`normal` / `break-word`（超宽单词逐字符拆分）/ `anywhere`
- **text-align**：`left` / `center` / `right`
- **line-height**：支持倍数和绝对值

### 4.4 ImageNode

光栅图片嵌入：

```python
img = ImageNode("photo.png", style={"width": "200px"})
```

- **支持格式**：PNG、JPEG、GIF、WebP、SVG
- **object-fit**：`fill`（拉伸）/ `contain`（等比缩小）/ `cover`（等比放大裁切）/ `none`（原尺寸居中）
- **嵌入方式**：base64 编码为 data URI

### 4.5 SVGNode

嵌入外部或内联 SVG：

```python
# 从文件
svg = SVGNode("diagram.svg", is_file=True)
# 从字符串
svg = SVGNode('<circle cx="50" cy="50" r="40" fill="red"/>')
```

- 自动从 `viewBox` 或 `width/height` 解析固有尺寸
- 布局后计算缩放因子，等比适配分配空间
- 剥离外层 `<svg>` 标签，作为子内容嵌入

### 4.6 MplNode

嵌入 Matplotlib Figure：

```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
node = MplNode(fig, style={"width": "400px", "height": "300px"})
```

- 使用 72 DPI 作为 SVG 坐标系基准
- 布局时自动调用 `figure.set_size_inches()` 使输出精确匹配分配空间
- SVG 片段缓存，避免重复导出

### 4.7 自定义 Node

继承 `Node` 并实现 `measure()` + `layout()` 即可创建自定义节点：

```python
class ColorBox(Node):
    def __init__(self, color, style=None, parent=None):
        super().__init__(style=style or {}, parent=parent)
        self.color = color

    def measure(self, constraints):
        w = self._resolve_width(constraints) or 100
        return (w, w, self._resolve_height(constraints) or 100)

    def layout(self, constraints):
        w = self._resolve_width(constraints) or 100
        h = self._resolve_height(constraints) or 100
        self._resolve_box_model(w, h, 0, 0)
```

---

## 5. 文本引擎

### 5.1 字体管理（FontManager）

- **单例模式**：`FontManager.instance()`
- **系统字体发现**：自动扫描 Linux / macOS / Windows 系统字体目录
- **自定义字体目录**：`fm.add_font_directory(path)`
- **索引方式**：按文件名 stem + FreeType 嵌入的 family name 双重索引
- **generic family 别名**：
  - `sans-serif` → Noto Sans CJK / DejaVu Sans / Arial / …
  - `serif` → Noto Serif CJK / DejaVu Serif / Times New Roman / …
  - `monospace` → DejaVu Sans Mono / Courier New / …
- **weight/style 匹配**：拼接 `bold` / `italic` 后缀检索候选字体

### 5.2 字体回退链

对每个字符，按 `font-family` 列表顺序查找第一个拥有该字形的字体：

```
font-family: "Times New Roman, SimSun, serif"
  → 'A' 使用 Times New Roman
  → '中' Times 无此字形 → 回退到 SimSun
```

### 5.3 文本排版（shaper）

| 函数 | 说明 |
|---|---|
| `measure_text()` | 测量文本总 advance 宽度 |
| `break_lines()` | 核心折行算法 |
| `align_lines()` | 设置行内水平偏移 |
| `compute_text_block_size()` | 计算折行后的文本块尺寸 |
| `get_min_content_width()` | 最小内容宽度（最宽单词 / CJK 单字） |
| `get_max_content_width()` | 最大内容宽度（不折行的单行宽度） |

**CJK 支持细节**：覆盖 CJK 统一汉字、扩展 A/B、兼容、日文假名、韩文音节、全角字符等 15+ Unicode 区块。CJK 字符逐字拆分为独立可断行 token，与西文空格分词自然混排。

**折行算法**：贪心行填充，`overflow-wrap: break-word` 时超宽 token 逐字符拆分。

---

## 6. 布局引擎（GridSolver）

实现 CSS Grid Level 1 布局算法，约 780 行代码，是项目最核心的模块。

### 6.1 算法流程

1. **容器宽度解析**：显式 `width` 或 `available_width`
2. **轨道模板解析**：样式值 → `TrackDef` 列表
3. **项目放置**：
   - Pass 1：显式放置（`row` + `col` 均指定）
   - Pass 2：自动放置（`grid-auto-flow`，支持 `dense`）
4. **列轨道尺寸计算**：
   - 固定/百分比轨道直接设置
   - 内在轨道（auto/min-content/max-content）用子项 measure 结果
   - 跨越项空间分配（`_distribute_spanning`）
   - `fr` 轨道按比例分配剩余空间
5. **行轨道尺寸计算**：类似列，但依赖列宽做文本回流
6. **容器盒模型**：三层 Rect 计算
7. **子位置计算 + 递归子布局**
8. **对齐**：`justify-self` / `align-self`（`stretch` / `start` / `center` / `end`）

### 6.2 关键特性

- **跨行列**：`row_span` / `col_span`，跨越项空间按轨道比例分配
- **嵌套 Grid**：对齐后通过 `_shift_descendants()` 递归偏移所有后代坐标
- **两遍布局**：先 measure 收集尺寸约束，再 solve 分配空间
- **三层盒模型**：content → padding → border，精确处理各层边距

---

## 7. 渲染器

### 7.1 输出格式

| 方法 | 输出 |
|---|---|
| `renderer.render(node, "out.svg")` | SVG 文件（返回 `drawsvg.Drawing`） |
| `renderer.render_to_drawing(node)` | `drawsvg.Drawing` 对象（不写文件） |
| `renderer.render_to_string(node)` | SVG 字符串 |
| `renderer.render_png(node, "out.png", scale=2)` | PNG 文件（依赖 cairosvg） |

### 7.2 渲染细节

| 节点类型 | 渲染方式 |
|---|---|
| `GridContainer` | 背景矩形 + 四条边框线 → 递归子节点 |
| `TextNode` | 逐行 `<text>` 元素，含字体族、颜色、对齐偏移 |
| `ImageNode` | base64 `<image>` 元素 |
| `SVGNode` | `<g transform="translate(x,y) scale(sx,sy)">` 包裹内部 SVG |
| `MplNode` | `<g transform>` 包裹 Matplotlib SVG 片段 |
| 自定义 `Node` | 仅背景 + 边框 |

**额外特性**：

- `overflow: hidden` → 生成 `<clipPath>` 裁切
- `text-overflow: ellipsis` + `overflow: hidden` → 精确截断末行加 `…`（使用字形测量）
- `white-space: pre/pre-wrap` → `xml:space="preserve"`
- `border-radius` → SVG `<rect rx="..." ry="...">` 圆角矩形
- `border-style: dashed / dotted` → `stroke-dasharray` 属性
- `opacity` → 背景和文本透明度
- `outline` → 不占布局空间的外部描边（支持 `solid` / `dashed` / `dotted` + 圆角外扩）

---

## 8. 内置样式模板

17 个预设 `dict`，可直接传入 `style` 参数或合并自定义：

| 模板 | 用途 |
|---|---|
| `REPORT_PAGE` | 800px 白底报告页面 |
| `TWO_COLUMN` / `THREE_COLUMN` | 等宽多列布局 |
| `SIDEBAR_LAYOUT` | 240px 侧栏 + 1fr 主区 |
| `CHART_CONTAINER` | 2×2 图表网格 |
| `HEADER` / `FOOTER` | 深色页眉 / 页脚 |
| `TITLE` / `SUBTITLE` | 大标题 / 副标题 |
| `H1` / `H2` / `H3` | 标题层级 |
| `PARAGRAPH` | 正文段落 |
| `CAPTION` | 图表说明文字 |
| `CODE` | 等宽代码块 |
| `CARD` | 带边框白底卡片 |
| `HIGHLIGHT_BOX` | 黄色高亮提示框 |

使用方式：

```python
from latticesvg.templates import REPORT_PAGE, TITLE

grid = GridContainer(style={**REPORT_PAGE, "width": "1000px"})
title = TextNode("标题", style=TITLE)
```

`ALL_TEMPLATES` 字典提供按名称的程序化访问。

### 8.2 表格便捷构建

`build_table()` 函数提供快速创建表格的便捷 API：

```python
from latticesvg import build_table

table = build_table(
    headers=["编号", "名称", "数值"],
    rows=[
        ["001", "Alpha", "1.23"],
        ["002", "Beta", "4.56"],
        ["003", "Gamma", "7.89"],
    ],
    col_widths=["100px", "1fr", "1fr"],
    stripe_color="#f8f9fa",  # 斑马纹背景色
)
```

**参数**：
- `headers`: 列标题
- `rows`: 数据行（每行为一个序列）
- `style`: 覆盖表格容器样式
- `header_style`: 覆盖表头单元格样式
- `cell_style`: 覆盖数据单元格样式
- `col_widths`: 列宽度列表（默认全部 `1fr`）
- `stripe_color`: 偶数行背景色（设为 `None` 禁用斑马纹）

返回一个完全构建好的 `GridContainer` 节点树，可直接布局和渲染。

---

## 9. 已知限制

以下是当前版本中已知的限制和未完成项：

1. **`text-align: justify`**：代码注释中标注了计划但渲染器未实现逐词分布
2. **`grid-auto-rows/columns` 未显式支持**：隐式轨道总是按 `auto` 处理
3. **无 `z-index` / 叠放控制**：渲染顺序固定为节点添加顺序
4. **Pillow 后备的字形检测**：`_has_glyph()` 始终返回 `True`，无法真正判断字体覆盖
5. **自动放置搜索上限**：行上限硬编码为 200，迭代上限 10000 次
6. **四角独立 `border-radius`**：仅支持统一圆角值，不支持 `10px 20px 0 5px` 四角独立语法

---

## 10. 演示覆盖

`examples/` 包含 32 个演示（demo_01 ~ demo_32），覆盖：

- CSS 值解析、简写展开、样式继承
- 固定列 / fr 弹性列 / 混合轨道
- 自动放置、跨行列、对齐
- 嵌套 Grid、padding + border 盒模型
- TextNode 排版、white-space 模式（包括 `pre-line`）、overflow-wrap
- SVGNode / MplNode / ImageNode 嵌入
- 内置模板、PNG 输出
- `min-width` / `max-width` / `min-height` / `max-height` 尺寸约束
- `text-overflow: ellipsis` 精确截断
- `opacity` 透明度渲染
- `border-radius` 圆角矩形
- `border-style: dashed / dotted` 虚线边框
- `render_to_drawing()` 无文件写入渲染
- `grid-template-areas` 命名区域布局
- `build_table()` 表格便捷 API
- 综合报告页面、中英文混排
- 复杂画廊表格（9×10 矩阵，11 行 11 列）
- 多级嵌套卡片式布局（瀑布流风格）

---

## 11. 测试覆盖

7 个测试文件，使用 pytest：

| 文件 | 覆盖范围 |
|---|---|
| `test_style_parser.py` | 值解析、颜色、简写展开、轨道模板 |
| `test_computed_style.py` | ComputedStyle 创建、继承、便利属性 |
| `test_grid_solver.py` | 固定/fr/混合轨道、gap、自动放置、跨列、对齐 |
| `test_nodes.py` | SVGNode / ImageNode 尺寸解析与 object-fit |
| `test_renderer.py` | SVG 输出、背景色、边框渲染 |
| `test_text_shaper.py` | 文本度量、折行、空白处理、break-word、对齐 |
| `test_integration.py` | 端到端：两栏布局、嵌套 Grid、自动放置、SVG 嵌入 |
| `test_table_builder.py` | 表格便捷构建函数 |
