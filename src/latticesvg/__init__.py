"""LatticeSVG — Grid-based vector layout engine.

Public API exports, matching the usage example in SPECS.md §7.
"""

from .nodes.base import Node, Rect, LayoutConstraints
from .nodes.grid import GridContainer
from .nodes.text import TextNode
from .nodes.image import ImageNode
from .nodes.mpl import MplNode
from .nodes.svg import SVGNode
from .render.renderer import Renderer
from .style.computed import ComputedStyle
from . import templates

__all__ = [
    "Node",
    "Rect",
    "LayoutConstraints",
    "GridContainer",
    "TextNode",
    "ImageNode",
    "MplNode",
    "SVGNode",
    "Renderer",
    "ComputedStyle",
    "templates",
]

__version__ = "0.1.0"
