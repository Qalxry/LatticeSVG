# CSS 属性参考

LatticeSVG 支持 63 个 CSS 属性，分为六大类。

## 盒模型（不可继承）

| 属性 | 默认值 | 类型 | 说明 |
|---|---|---|---|
| `width` | `auto` | length | 元素宽度 |
| `height` | `auto` | length | 元素高度 |
| `min-width` | `0px` | length | 最小宽度 |
| `max-width` | `none` | length | 最大宽度 |
| `min-height` | `0px` | length | 最小高度 |
| `max-height` | `none` | length | 最大高度 |
| `margin-top` | `0px` | length | 上外边距 |
| `margin-right` | `0px` | length | 右外边距 |
| `margin-bottom` | `0px` | length | 下外边距 |
| `margin-left` | `0px` | length | 左外边距 |
| `padding-top` | `0px` | length | 上内边距 |
| `padding-right` | `0px` | length | 右内边距 |
| `padding-bottom` | `0px` | length | 下内边距 |
| `padding-left` | `0px` | length | 左内边距 |
| `border-top-width` | `0px` | length | 上边框宽度 |
| `border-right-width` | `0px` | length | 右边框宽度 |
| `border-bottom-width` | `0px` | length | 下边框宽度 |
| `border-left-width` | `0px` | length | 左边框宽度 |
| `border-top-color` | `none` | color | 上边框颜色 |
| `border-right-color` | `none` | color | 右边框颜色 |
| `border-bottom-color` | `none` | color | 下边框颜色 |
| `border-left-color` | `none` | color | 左边框颜色 |
| `border-top-style` | `none` | keyword | 上边框样式 (`solid`/`dashed`/`dotted`) |
| `border-right-style` | `none` | keyword | 右边框样式 |
| `border-bottom-style` | `none` | keyword | 下边框样式 |
| `border-left-style` | `none` | keyword | 左边框样式 |
| `border-top-left-radius` | `0px` | length | 左上圆角半径 |
| `border-top-right-radius` | `0px` | length | 右上圆角半径 |
| `border-bottom-right-radius` | `0px` | length | 右下圆角半径 |
| `border-bottom-left-radius` | `0px` | length | 左下圆角半径 |
| `box-sizing` | `border-box` | keyword | 盒模型计算方式 |
| `outline-width` | `0px` | length | 轮廓宽度 |
| `outline-color` | `none` | color | 轮廓颜色 |
| `outline-style` | `none` | keyword | 轮廓样式 |
| `outline-offset` | `0px` | length | 轮廓偏移 |

## 简写属性

以下简写属性会被自动展开为对应的长写属性：

| 简写 | 展开为 |
|---|---|
| `margin` | `margin-top/right/bottom/left` |
| `padding` | `padding-top/right/bottom/left` |
| `border` | `border-*-width/color/style` |
| `border-width` | `border-top/right/bottom/left-width` |
| `border-color` | `border-top/right/bottom/left-color` |
| `border-radius` | `border-top-left/top-right/bottom-right/bottom-left-radius` |
| `border-top` | `border-top-width/color/style` |
| `border-right` | `border-right-width/color/style` |
| `border-bottom` | `border-bottom-width/color/style` |
| `border-left` | `border-left-width/color/style` |
| `gap` | `row-gap` + `column-gap` |
| `outline` | `outline-width/color/style` |
| `background` | `background-color` 或 `background-image`（渐变） |

## Grid 布局（不可继承）

| 属性 | 默认值 | 类型 | 说明 |
|---|---|---|---|
| `display` | `block` | keyword | 显示类型（`grid`/`block`） |
| `grid-template-columns` | `none` | track-list | 列轨道定义 |
| `grid-template-rows` | `none` | track-list | 行轨道定义 |
| `row-gap` | `0px` | length | 行间距 |
| `column-gap` | `0px` | length | 列间距 |
| `justify-items` | `stretch` | keyword | 子项水平对齐 |
| `align-items` | `stretch` | keyword | 子项垂直对齐 |
| `justify-self` | `auto` | keyword | 单个子项水平对齐 |
| `align-self` | `auto` | keyword | 单个子项垂直对齐 |
| `grid-template-areas` | `none` | grid-areas | 命名区域模板 |
| `grid-auto-flow` | `row` | keyword | 自动放置方向 |
| `grid-auto-rows` | `auto` | track-list | 隐式行轨道大小 |
| `grid-auto-columns` | `auto` | track-list | 隐式列轨道大小 |
| `grid-row` | `none` | grid-line | 子项行位置 |
| `grid-column` | `none` | grid-line | 子项列位置 |
| `grid-area` | `none` | keyword | 子项命名区域 |

### 轨道值类型

| 值类型 | 示例 | 说明 |
|---|---|---|
| 固定像素 | `"200px"` | 固定宽度 |
| 弹性单位 | `"1fr"`, `"2fr"` | 按比例分配剩余空间 |
| 百分比 | `"50%"` | 相对于容器可用宽度 |
| `auto` | `"auto"` | 由内容决定 |
| `min-content` | `"min-content"` | 内容最小宽度 |
| `max-content` | `"max-content"` | 内容最大宽度 |
| `minmax()` | `"minmax(100px, 1fr)"` | 尺寸范围 |
| `repeat()` | `"repeat(3, 1fr)"` | 重复轨道 |

## 文本（可继承）

| 属性 | 默认值 | 类型 | 说明 |
|---|---|---|---|
| `font-family` | `sans-serif` | font-family | 字体族 |
| `font-size` | `16px` | length | 字号 |
| `font-weight` | `normal` | keyword | 字重 (`normal`/`bold`) |
| `font-style` | `normal` | keyword | 字形 (`normal`/`italic`) |
| `text-align` | `left` | keyword | 对齐 (`left`/`center`/`right`/`justify`) |
| `line-height` | `1.2` | line-height | 行高（无单位倍数/像素值） |
| `white-space` | `normal` | keyword | 空白处理 |
| `overflow-wrap` | `normal` | keyword | 溢出换行 (`normal`/`break-word`) |
| `word-break` | `normal` | keyword | 词断行 |
| `color` | `#000000` | color | 文字颜色 |
| `letter-spacing` | `normal` | length | 字间距 |
| `word-spacing` | `normal` | length | 词间距 |
| `hyphens` | `none` | keyword | 自动断词 (`none`/`auto`) |
| `lang` | `en` | keyword | 语言（用于断词规则） |

## 文本装饰（不可继承）

| 属性 | 默认值 | 类型 | 说明 |
|---|---|---|---|
| `text-decoration` | `none` | keyword | 文本装饰 (`underline`/`line-through`) |
| `text-overflow` | `clip` | keyword | 溢出处理 (`clip`/`ellipsis`) |

## 书写模式（可继承）

| 属性 | 默认值 | 类型 | 说明 |
|---|---|---|---|
| `writing-mode` | `horizontal-tb` | keyword | 书写方向 (`horizontal-tb`/`vertical-rl`) |
| `text-orientation` | `mixed` | keyword | 文字朝向 (`mixed`/`upright`/`sideways`) |
| `text-combine-upright` | `none` | keyword | 纵中横 (`none`/`all`/`digits N`) |

## 视觉（不可继承）

| 属性 | 默认值 | 类型 | 说明 |
|---|---|---|---|
| `background-color` | `none` | color | 背景色 |
| `background-image` | `none` | gradient | 背景图（渐变） |
| `opacity` | `1` | number | 透明度 (0~1) |
| `overflow` | `visible` | keyword | 溢出处理 (`visible`/`hidden`) |
| `clip-path` | `none` | clip-path | 裁剪路径 |
| `box-shadow` | `none` | box-shadow | 盒阴影 |
| `transform` | `none` | transform | 变换 |
| `filter` | `none` | filter | 滤镜 |

## 图片（不可继承）

| 属性 | 默认值 | 类型 | 说明 |
|---|---|---|---|
| `object-fit` | `fill` | keyword | 图片缩放 (`fill`/`contain`/`cover`) |

## 值类型参考

### 长度值

支持的单位：`px`（像素）、`pt`（点，1pt = 1.333px）、`%`（百分比）。
无单位数字解释为像素。

```python
"16px"   # 16 像素
"12pt"   # 16 像素
"50%"    # 参考长度的 50%
16       # 16 像素（数字类型直接传入）
```

### 颜色值

```python
"#ff0000"                    # 十六进制
"#f00"                       # 简写十六进制
"rgb(255, 0, 0)"             # RGB
"rgba(255, 0, 0, 0.5)"       # RGBA
"red"                        # CSS 命名颜色
"transparent"                # 透明
```

### 渐变值

```python
"linear-gradient(135deg, #667eea, #764ba2)"
"linear-gradient(to right, red, blue)"
"radial-gradient(circle, #f093fb, #f5576c)"
"radial-gradient(ellipse at center, #fff, #000)"
```
