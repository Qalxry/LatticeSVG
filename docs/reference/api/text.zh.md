# 文本引擎 API

文本模块负责字体加载、文本测量、自动换行和垂直排版。

## 模块概览

| 子模块 | 职责 |
|---|---|
| `text.font` | 字体管理器 (`FontManager`)，FreeType/Pillow 后端 |
| `text.shaper` | 文本测量、换行、对齐（`measure_text`, `break_lines`, `align_lines`） |
| `text.embed` | 字体子集化和 WOFF2 嵌入 |

## FontManager

全局单例，管理字体查找和加载。

```python
from latticesvg.text.font import FontManager

fm = FontManager.instance()
path = fm.find_font("Noto Sans SC", weight="bold")
chain = fm.find_font_chain(["Times New Roman", "SimSun"], weight="normal")
```

## 自动生成的 API 文档

### 字体管理

::: latticesvg.text.font
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4

### 文本排版

::: latticesvg.text.shaper
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4

### 字体嵌入

::: latticesvg.text.embed
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4
