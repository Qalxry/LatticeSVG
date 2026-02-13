"""GridContainer — the CSS Grid layout container node."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .base import LayoutConstraints, Node, Rect
from ..style.parser import AUTO, AutoValue


class GridContainer(Node):
    """A container node that arranges its children using CSS Grid layout.

    Delegates the heavy-lifting (track sizing, placement, alignment)
    to :class:`~latticesvg.layout.grid_solver.GridSolver`.
    """

    def __init__(
        self,
        style: Optional[Dict[str, Any]] = None,
        parent: Optional[Node] = None,
    ) -> None:
        if style is None:
            style = {}
        # Ensure display is grid
        style.setdefault("display", "grid")
        super().__init__(style=style, parent=parent)

    # -----------------------------------------------------------------
    # Convenience: layout(available_width=…)
    # -----------------------------------------------------------------

    def layout(self, constraints: Optional[LayoutConstraints] = None,
               available_width: Optional[float] = None,
               available_height: Optional[float] = None) -> None:
        """Run the full layout pass for this container and all descendants.

        Can be called directly as ``grid.layout(available_width=800)``.
        """
        if constraints is None:
            # Derive from explicit width or arguments
            aw = available_width
            if aw is None:
                explicit_w = self._resolve_width(LayoutConstraints())
                aw = explicit_w if explicit_w is not None else 800.0
            constraints = LayoutConstraints(
                available_width=aw,
                available_height=available_height,
            )

        self._layout_grid(constraints)

    # -----------------------------------------------------------------
    # Measurement (for nested grids)
    # -----------------------------------------------------------------

    def measure(self, constraints: LayoutConstraints) -> Tuple[float, float, float]:
        from ..layout.grid_solver import GridSolver

        solver = GridSolver(self)
        return solver.measure(constraints)

    # -----------------------------------------------------------------
    # Grid layout implementation
    # -----------------------------------------------------------------

    def _layout_grid(self, constraints: LayoutConstraints) -> None:
        from ..layout.grid_solver import GridSolver

        solver = GridSolver(self)
        solver.solve(constraints)

    def __repr__(self) -> str:
        return f"GridContainer(children={len(self.children)})"
