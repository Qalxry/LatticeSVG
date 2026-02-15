# LatticeSVG 功能建议

> 基于项目定位「小而美的无浏览器 Python 矢量布局引擎」，按优先级组织。
>
> 本文档同时记录代码审计中发现的设计缺陷、BUG、反直觉行为与不足之处。

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

## P0 — 正确性缺陷（直接影响输出结果）

### P0-1. `add()` 不触发样式继承

**位置**：`nodes/base.py:95-102`

**现象**：用户通过 `parent.add(child)` 添加子节点后，子节点**不会继承**父节点的可继承属性（`color`、`font-family`、`font-size`、`line-height` 等）。

**原因**：`add()` 中的守卫条件 `if not isinstance(child.style, ComputedStyle)` 永远为 `True`——因为 `Node.__init__` 已在构造时将 `style` 包装为 `ComputedStyle`，所以 `add()` 中重新绑定带 `parent_style` 的 `ComputedStyle` 的逻辑**永远不会执行**。

```python
# base.py __init__:
self.style = ComputedStyle(style)  # 已经是 ComputedStyle

# base.py add():
if not isinstance(child.style, ComputedStyle):   # ← 永远 False
    child.style = ComputedStyle(None, parent_style=self.style)  # ← 死代码
```

**影响**：只有在构造时通过 `parent=` 参数传入的父节点才能正确继承。后续调用 `add()` 添加的子节点全部丢失继承链。这是核心 API 的正确性问题。

**建议修复**：`add()` 应无条件地以 `parent_style=self.style` 重建子节点的 `ComputedStyle`，同时保留子节点自身的样式覆盖。

---

### P0-2. `line-height` ≤ 5.0 魔法阈值

**位置**：`text/shaper.py:713`、`text/shaper.py:1328`、`render/renderer.py:978`、`render/renderer.py:1122`（共 4 处）

**现象**：`line-height: 4px`（绝对 4 像素）会被错误地当作 4× 乘数，得到 `font_size × 4`（如 64px）；`line-height: 6`（6× 乘数）会被错误地当作绝对 6px。

**原因**：CSS 规范用类型（`<number>` vs `<length>`）区分乘数与绝对值，但 `parse_value()` 将 `"4px"` 解析为 `float(4.0)` 后丢失了单位信息。后续代码用 `if line_height <= 5.0` 这一启发式阈值猜测类型，不符合规范且在阈值附近产生错误结果。

```python
# 4 处相同逻辑：
if line_height <= 5.0:
    lh = line_height * font_size   # 当作乘数
else:
    lh = line_height               # 当作绝对值
```

**影响**：所有使用 `1px`–`5px` 绝对行高或 `≥ 6` 倍乘数的场景结果错误。

**建议修复**：在 `parse_value()` 阶段保留类型信息——例如让无单位数值返回一个 `LineHeightMultiplier(value)` 包装类型，带单位的返回纯 `float`。下游直接通过 `isinstance` 判断，不再使用阈值。

---

### P0-3. `rem` 单位等价于 `em`

**位置**：`style/parser.py` 的 `parse_value()` 函数

**现象**：`2rem` 在 `font-size: 24px` 的子节点中解析为 `48px`（2 × 24），而 CSS 规范要求解析为 `32px`（2 × 根元素 16px）。

**原因**：`parse_value()` 内 `em` 和 `rem` 使用同一个 `font_size` 参数做乘法，没有单独的 `root_font_size` 参数。

```python
if unit == 'em':
    return num * font_size
elif unit == 'rem':
    return num * font_size   # ← 应该用 root_font_size
```

**影响**：所有使用 `rem` 单位的场景——用户合理预期 `rem` 相对于根节点字号，但实际行为等同于 `em`。

**建议修复**：为 `parse_value()` 增加 `root_font_size` 参数（默认 `16`），`rem` 分支使用该参数。

---

### P0-4. `margin` 属性可解析但布局从不使用

**位置**：`style/properties.py`（注册了 5 个 margin 属性）、`layout/grid_solver.py`（无任何 margin 读取）

**现象**：用户设置 `margin: "10px"` 语法正确、解析无报错，但**对布局没有任何效果**。内置模板（如 `templates.py` 中的 `default` 模板）甚至自己也在用 `margin`，进一步误导用户。

**原因**：`GridSolver.solve()` 仅使用 `gap` 做项目间距，从未读取任何 `margin-*` 属性。

**影响**：用户被静默误导，设置后无效果且无任何警告。这是 API 的一致性缺陷。

**建议修复**：二选一——
1. 在 `GridSolver` 中实现 margin 支持（在挤出 content box 时减去 margin）；
2. 或从 `PROPERTY_REGISTRY` 移除 margin 属性，在 `parse_value()` 遇到 margin 时发出 `warnings.warn()`。

---

### P0-5. `border-radius` 同时作为简写属性和普通属性注册

**位置**：`style/properties.py:73`（在 `PROPERTY_REGISTRY` 中注册）、`style/parser.py` 的 `expand_shorthand()`（作为简写展开）

**现象**：`border-radius: "10px"` 经 `expand_shorthand()` 后产生 `border-top-left-radius`、`border-top-right-radius` 等四个键，**同时** `border-radius` 本身作为已注册属性也被保留。`ComputedStyle` 中会同时存在原始键和四个展开键，可能导致读取时取到过期的值。

**建议修复**：将 `border-radius` 从 `PROPERTY_REGISTRY` 中移除（它本质是简写属性，不应出现在普通属性注册表中），或在 `expand_shorthand()` 展开后显式删除原始键。

---

### P0-6. 圆角边框只渲染单边样式

**位置**：`render/renderer.py` 约第 530–545 行

**现象**：当 `border-radius > 0` 时，渲染器只取第一个 `border-width > 0` 的边的 `color` / `width` / `style`，然后绘制整个边框轮廓。如果用户为不同边设置了不同颜色或宽度（如 `border-top: "2px solid red"`、`border-bottom: "4px solid blue"`），只有第一个被采用，其余静默丢弃。

**原因**：圆角路径绘制使用单一 `stroke` + `stroke-width`，无法直接表达四边不同样式。但至少应在存在差异时发出警告。

**建议修复**：短期——检测到四边样式不一致时发出 `warnings.warn()`。长期——为圆角边框分段绘制四条带弧线的路径。

---

### P0-7. 行轨道内在尺寸计算中 `layout()` 的副作用

**位置**：`layout/grid_solver.py` 约第 658–664 行

**现象**：在 `_resolve_tracks_axis()` 计算行轨道高度时，为获取子项的自然高度，代码调用了 `item.node.layout(c)`。这会**修改节点的内部盒模型状态**（`_content_width`、`_content_height` 等）。随后在主 `solve()` 循环中节点会被**再次 `layout()`**，覆盖前序结果。

**影响**：
1. 第一次 `layout()` 的计算结果被浪费，存在性能开销；
2. 如果两次 `layout()` 的 `LayoutConstraints` 不同，可能产生不一致的中间状态。

**建议修复**：引入一个只读的 `measure(constraints) → (width, height)` 方法，与会修改状态的 `layout()` 分离。行轨道内在尺寸阶段只调用 `measure()`。

---

## P1 — 设计缺陷与反直觉行为

### P1-1. `FilterFunction` 冻结数据类被 `object.__setattr__` 绕过

**位置**：`style/parser.py` 约第 1290 行

**现象**：`FilterFunction` 声明为 `@dataclass(frozen=True)`，但 `drop-shadow` 的颜色值通过 `object.__setattr__(fns[-1], "_color", color)` 强行写入，违反了冻结契约。

**影响**：如果后续任何代码依赖 `FilterFunction` 的不可变性（如用作 dict 键或 set 成员），会出现隐蔽 bug。

**建议修复**：将 `_color` 设为 `FilterFunction` 的正式字段（可选，默认 `None`），或改用非冻结数据类。

---

### P1-2. `_Percentage` 是私有 API 却被跨模块使用

**位置**：`style/parser.py` 中定义；`style/computed.py`、`layout/grid_solver.py`、`render/renderer.py` 中 `isinstance` 检查

**现象**：`_Percentage` 以下划线前缀命名表示"模块内部使用"，但实际上被 4 个不同模块导入。

**建议修复**：重命名为 `Percentage` 并纳入公开 API，或统一收归到一个内部工具模块。

---

### P1-3. 未知 CSS 属性静默接受

**位置**：`style/parser.py` 的 `parse_value()`、`style/computed.py`

**现象**：用户写出 `"backgroud-color": "red"`（拼写错误）不会收到任何警告或异常，属性被静默存储但永远不被使用。

**影响**：打字错误极难排查。用户可能长时间以为某个属性已生效，实际上因为拼写错误从未生效。

**建议修复**：在 `ComputedStyle.__init__` 或 `parse_value()` 中，对不在 `PROPERTY_REGISTRY` 中的属性名发出 `warnings.warn(f"Unknown CSS property: '{name}'")`。

---

### P1-4. `font-size` 被截断为 `int`

**位置**：`nodes/text.py:98-102` 的 `_font_size_int()` 方法；被 7+ 处调用

**现象**：`font-size: 13.5px` → `int(13.5)` → `13`。CSS `font-size` 完全可以是分数值（如 `0.9em × 16 = 14.4px`），截断会导致文本度量偏差和像素级对齐问题。同样的截断也出现在 `text/shaper.py:877` 的 `int(span.font_size)`。

**建议修复**：
1. 将 `_font_size_int()` 改为 `_font_size() -> float`，返回浮点值；
2. 仅在 FreeType `set_char_size()` 等必须整数的接口处做 `round()`。

---

### P1-5. `resolve_percentages()` 原地修改且无防重入保护

**位置**：`style/computed.py` 的 `resolve_percentages()` 方法

**现象**：该方法遍历所有属性，将 `_Percentage` 实例原地替换为解析后的 `float`。如果被调用两次（使用不同的 `ref_w` / `ref_h`），第二次会在已经是 `float` 的值上操作，不会触发 `isinstance(_Percentage)` 分支，导致静默地保留第一次解析的结果。

**影响**：在节点被移动到不同尺寸的容器中时，百分比值不会被重新解析。

**建议修复**：记录原始 `_Percentage` 值（如保存到 `_raw_values` 字典），每次 `resolve_percentages()` 从原始值重新计算；或添加一个 `_resolved` 标记防止重复调用。

---

### P1-6. `build_table()` 每个单元格创建一个 `GridContainer`

**位置**：`templates.py` 的 `build_table()` 函数

**现象**：每个表格单元格被包装在一个独立的 `GridContainer`（内含一个 `TextNode`）中。一个 10×10 的表格会产生 **201 个节点**（100 个 GridContainer + 100 个 TextNode + 1 个外层容器），其中 100 个 GridContainer 各自要走完整的 Grid 布局求解流程。

**影响**：性能浪费——单元格内只有一个 TextNode，不需要 Grid 布局。

**建议修复**：直接将 TextNode 放入外层 Grid 的对应网格位置，不做中间层包装。如需单元格级样式（padding、背景色），可在 TextNode 自身的 box model 上处理。

---

### P1-7. `_find_row` 硬编码 200 行上限

**位置**：`layout/grid_solver.py:481`

**现象**：自动放置算法在第 200 行后停止搜索空位，返回 `0`——这会导致新项目**覆盖第一行的已有内容**，造成静默的布局冲突。`_auto_place_row` / `_auto_place_col` 也有 10000 次迭代上限，超出后返回可能错误的位置。

**建议修复**：
1. 将上限从 200 提升到 `max(200, len(explicit_rows) + len(items))`，动态适应；
2. 超出时抛出 `LayoutError` 而非静默返回 `0`。

---

### P1-8. `grid-line` 解析器仅支持 `"start / span N"` 格式

**位置**：`style/parser.py` 的 grid-line 相关解析

**现象**：只支持 `"2 / span 3"` 这一种格式。不支持：
- `"2 / 5"`（起始行 / 结束行）
- `"-1"`（负行号，从末尾计数）
- 命名行号

CSS Grid Level 1 规范定义了以上所有格式。

**建议修复**：至少支持 `"start / end"` 格式和负行号。命名行号可列为 P2。

---

### P1-9. `opacity` 仅作用于背景矩形

**位置**：`render/renderer.py` 中 `_draw_background()` 与节点渲染逻辑

**现象**：CSS `opacity` 属性只被应用到背景矩形的 `fill-opacity` 上，文本内容、边框、子节点均不受影响。CSS 规范中 `opacity` 应作用于**整个元素及其内容**。

**建议修复**：在渲染节点时创建一个 `<g opacity="...">` 分组，将该节点的所有视觉元素（背景、边框、内容、子节点）放入其中。

---

### P1-10. `_col_starts()` / `_row_starts()` 重复计算

**位置**：`layout/grid_solver.py` 中 `_apply_alignment()` 和 `_compute_positions()` 多处调用

**现象**：这两个方法每次调用都重新遍历轨道数组计算前缀和，在 `solve()` 过程中被调用多次。

**建议修复**：在轨道尺寸确定后计算一次，缓存到实例变量。

---

### P1-11. `display: block` 是默认值但无对应布局引擎

**位置**：`style/properties.py`（`display` 默认值为 `"block"`）

**现象**：所有节点默认 `display: block`，但代码中没有 block 流式布局实现——只有 `GridContainer` 才能通过 `GridSolver` 布局。一个没有显式设置为 Grid 的 Node 不会获得任何布局行为。

**影响**：`display` 属性的默认值具有误导性。

**建议修复**：将默认值改为 `"grid"`（因为所有容器事实上都是 Grid），或将 `display` 的默认值改为一个表示"无布局"的值（如 `"contents"`），并在文档中说明。

---

### P1-12. `MathNode.layout()` 中无意义的缓存失效

**位置**：`nodes/math.py` 约第 110–115 行

**现象**：

```python
self._svg_cache = None          # ← 清除缓存
self._svg_cache = self._get_fragment()  # ← 立即重建
```

第一行的 `None` 赋值毫无作用，且每次 `layout()` 都无条件重新渲染数学公式（调用 QuickJax），完全跳过了缓存机制。

**建议修复**：仅在输入（公式文本、字号、显示模式）变化时才重建。可通过比较 hash 或脏标记来实现。

---

### P1-13. `AutoValue.__eq__("auto")` 的魔法比较

**位置**：`style/parser.py` 的 `AutoValue` 类

**现象**：`AUTO == "auto"` 返回 `True`（通过 `__eq__` 中的字符串特判）。这意味着：

```python
value = parse_value(...)  # 返回 AutoValue 实例
if value == "auto":       # True — 看起来像在比较字符串，实际在与 sentinel 比较
```

**影响**：代码可读性差，新维护者可能误以为值是字符串 `"auto"` 而非 sentinel 对象。

**建议修复**：统一使用 `value is AUTO` 或 `isinstance(value, AutoValue)` 做判断，移除 `__eq__` 中的字符串特判。

---

### P1-14. `_Percentage` 缺少数值运算符

**位置**：`style/parser.py:296-305`

**现象**：`_Percentage` 只有 `resolve(reference)` 方法，没有 `__lt__`、`__gt__`、`__float__` 等运算符。如果未解析的 `_Percentage` 意外泄漏到需要数值比较的代码路径（如 `if val <= 5.0`），会抛出不友好的 `TypeError`。

**建议修复**：至少添加 `__repr__` 用于调试信息（`Percentage(50%)`），并在 `__lt__` 等方法中抛出有意义的错误信息（如 `"Percentage must be resolved before comparison"`）。

---

### P1-15. `border-radius` 百分比解析的轴判断错误

**位置**：`style/computed.py` 的 `resolve_percentages()` 方法

**现象**：该方法通过检查属性名是否包含 `"height"` / `"top"` / `"bottom"` 来决定百分比的参考轴。但 CSS 规范中 `border-radius` 的百分比应分别参考宽度和高度（水平半径参考宽度，垂直半径参考高度），而名为 `border-top-left-radius` 的属性包含 `"top"`，因此其百分比会被错误地以**高度**为参考解析。

```python
# 当前逻辑：
if any(k in prop for k in ("height", "top", "bottom")):
    ref = ref_h   # ← border-top-left-radius 匹配了 "top"，但应该用 ref_w
else:
    ref = ref_w
```

**建议修复**：为 `border-*-radius` 属性添加特殊处理，或在 `PROPERTY_REGISTRY` 中标注百分比参考轴。

---

## P2 — 待评估提案

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

### P2-4. `_has_glyph` Pillow 后端永远返回 `True`

**位置**：`text/font.py:450-458`

**现象**：当使用 Pillow 后端（FreeType 不可用时的回退）时，`_has_glyph()` 无条件返回 `True`。这导致字体回退链完全失效——所有字符都会使用链中的第一个字体，即使该字体不包含该字形。在中英文混排场景下，英文字体可能被用于渲染中文字符（获得 `.notdef` 方框）。

**建议修复**：Pillow 后端通过检查 `font.getbbox(char)` 返回值是否为全零来近似判断字形是否存在。

### P2-5. 缓存键设计混用

**位置**：`text/font.py` 的 `FontManager._cache`

**现象**：`_has_glyph` 使用键 `('_has', font_path, char)`，字形度量使用键 `(font_path, size, char)`，两类数据共存于同一个 `dict`。当前不会冲突，但设计脆弱——如果 `font_path` 恰好是字符串 `"_has"`，会产生键冲突。

**建议修复**：使用两个独立的字典，或统一使用带类型标签的 `namedtuple` 做键。

### P2-6. 单边 `border` 简写缺失

**位置**：`style/parser.py` 的 `expand_shorthand()`

**现象**：`expand_shorthand()` 仅处理 `border` 全局简写，`border-top`、`border-right`、`border-bottom`、`border-left` 这四个单边简写**不被识别**。用户写 `"border-bottom": "2px solid red"` 会被当作普通属性存储而非展开为 `border-bottom-width` / `border-bottom-style` / `border-bottom-color`。

**建议修复**：在 `expand_shorthand()` 中增加四个单边简写的展开逻辑。

### P2-7. `_text_y_offset` 使用 `display: flex` 判断

**位置**：`nodes/text.py`

**现象**：TextNode 内部用 `self.style.get("display") == "flex"` 来决定文本的垂直偏移量。但 LatticeSVG 不支持 Flexbox 布局，这个判断永远为 False（除非用户手动设置 `display: flex`，此时也没有实际的 flex 布局效果）。

**建议修复**：移除 flex 分支，改用显式的对齐属性控制垂直偏移。

### P2-8. 模板使用了未实现的 `margin` 属性

**位置**：`templates.py` 中的多个内置模板

**现象**：如 `default` 模板中设置了 `margin` 值。由于 P0-4 指出 margin 在布局中无效，这些模板中的 margin 设置实质上是装饰性代码——只是巧合地因为无效而不影响输出。

**建议修复**：随 P0-4 一并处理——如果不实现 margin，则从模板中移除相关设置。

### P2-9. 富文本 `_flush` 的性能问题

**位置**：`text/shaper.py` 的 `_flush()` 函数

**现象**：每次 flush 时为每个 `SpanFragment` 重新调用度量函数。对于长段富文本，碎片数量多时度量调用开销会线性增长。

**建议修复**：批量度量或缓存 span 级别的度量结果。

### P2-10. `_normalise_hex` 对 4 位 / 8 位 hex 的下游兼容性

**位置**：`style/parser.py` 的 `_normalise_hex()`

**现象**：4 位 hex `#f0fa` 被正确展开为 8 位 `#ff00ffaa`，但下游（如 drawsvg 的颜色参数）可能不接受 8 位 hex。如果渲染库只支持 6 位 hex + 独立 alpha，则颜色会异常。

**建议修复**：在传递给 drawsvg 前，将 8 位 hex 拆分为 6 位颜色 + `opacity` 属性。

---

## 测试覆盖缺口

以下关键场景在当前 352 个测试函数中**缺乏覆盖**，建议补充：

| 模块 | 缺失场景 | 关联提案 |
|------|---------|---------|
| `nodes/base.py` | 通过 `add()` 添加子节点后的样式继承验证 | P0-1 |
| `text/shaper.py` | `line-height` 在 5.0 附近的边界值（4.9 / 5.0 / 5.1） | P0-2 |
| `style/parser.py` | `rem` 单位在非根节点上的解析值 | P0-3 |
| `nodes/text.py` | 分数 `font-size`（如 `13.5px`、`14.4px`）的度量精度 | P1-4 |
| `text/font.py` | Pillow 后端下 `_has_glyph` 的字体回退链行为 | P2-4 |
| `layout/grid_solver.py` | 超过 200 行的大型网格自动放置 | P1-7 |
| `style/computed.py` | 未解析 `_Percentage` 泄漏到数值运算路径 | P1-14 |
| `style/computed.py` | `border-radius` 百分比的参考轴正确性 | P1-15 |

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