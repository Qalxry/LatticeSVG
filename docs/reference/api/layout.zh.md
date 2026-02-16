# 布局引擎 API

布局模块包含 CSS Grid 求解器，负责轨道尺寸计算、子项放置和对齐。

## 模块概览

| 类 | 职责 |
|---|---|
| `GridSolver` | Grid 布局求解器主类 |
| `TrackDef` | 轨道定义（fixed/fr/auto/minmax/etc.） |
| `Track` | 求解后的轨道（含实际尺寸） |
| `GridItem` | 包装子节点的 Grid 项 |
| `SizeType` | 尺寸类型枚举 |

## GridSolver

```python
from latticesvg.layout.grid_solver import GridSolver
from latticesvg import GridContainer, LayoutConstraints

grid = GridContainer(style={"grid-template-columns": "1fr 2fr", "width": 600})
solver = GridSolver(grid)
solver.solve(LayoutConstraints(available_width=600))
```

## 自动生成的 API 文档

::: latticesvg.layout.grid_solver
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3
