# 样式系统 API

样式模块负责 CSS 属性的解析、注册和计算。

## 模块概览

| 子模块 | 职责 |
|---|---|
| `style.properties` | 属性注册表 (`PROPERTY_REGISTRY`) |
| `style.parser` | 值解析器和特殊值类型 |
| `style.computed` | `ComputedStyle` 计算样式对象 |

## ComputedStyle

`ComputedStyle` 是每个节点的样式容器，负责：

- 存储显式设置的属性值
- 提供属性继承（从父节点）
- 计算最终使用值

```python
from latticesvg import ComputedStyle

cs = ComputedStyle({"font-size": 24, "color": "red"})
print(cs.font_size)     # 24
print(cs.get("color"))  # "red"
```

## 自动生成的 API 文档

### 样式属性

::: latticesvg.style.properties
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4

### 值解析器

::: latticesvg.style.parser
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4

### 计算样式

::: latticesvg.style.computed
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4
