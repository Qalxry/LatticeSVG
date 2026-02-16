# Layout Engine API

The layout module contains the CSS Grid solver, responsible for track sizing, item placement, and alignment.

## Module Overview

| Class | Responsibility |
|---|---|
| `GridSolver` | Main grid layout solver |
| `TrackDef` | Track definition (fixed/fr/auto/minmax/etc.) |
| `Track` | Solved track (with actual size) |
| `GridItem` | Grid item wrapping child nodes |
| `SizeType` | Size type enum |

## GridSolver

```python
from latticesvg.layout.grid_solver import GridSolver
from latticesvg import GridContainer, LayoutConstraints

grid = GridContainer(style={"grid-template-columns": "1fr 2fr", "width": 600})
solver = GridSolver(grid)
solver.solve(LayoutConstraints(available_width=600))
```

## Auto-generated API Docs

::: latticesvg.layout.grid_solver
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3
