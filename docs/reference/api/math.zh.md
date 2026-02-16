# 数学公式 API

数学模块提供 LaTeX 公式渲染后端的注册与管理。

## 模块概览

| 导出 | 类型 | 职责 |
|---|---|---|
| `MathBackend` | Protocol | 后端接口协议 |
| `SVGFragment` | dataclass | 渲染结果（SVG 内容 + 尺寸） |
| `QuickJaxBackend` | 类 | 默认后端（基于 QuickJax / MathJax v4） |
| `register_backend()` | 函数 | 注册自定义后端 |
| `set_default_backend()` | 函数 | 设置默认后端 |
| `get_backend()` | 函数 | 获取后端实例 |
| `get_default_backend_name()` | 函数 | 获取默认后端名称 |

## 基本用法

```python
from latticesvg.math import get_backend

backend = get_backend()  # 默认 QuickJax
fragment = backend.render(r"E = mc^2", font_size=20, display=True)
print(fragment.width, fragment.height)
print(fragment.svg)  # SVG 字符串片段
```

## 自定义后端

```python
from latticesvg.math import register_backend, set_default_backend

class MyBackend:
    def render(self, latex: str, font_size: float, display: bool = True):
        # 返回 SVGFragment
        ...

register_backend("my_backend", MyBackend)
set_default_backend("my_backend")
```

## 自动生成的 API 文档

### 后端管理

::: latticesvg.math
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4

### QuickJax 后端

::: latticesvg.math.backend
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4
