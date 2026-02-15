# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------

from latticesvg import Node, Renderer
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "demo_output"

class ColorBox(Node):
    """纯色方块，用于可视化布局效果。"""

    def __init__(self, width=80, height=50, label="", **style_kw):
        super().__init__(style=style_kw)
        self._w = width
        self._h = height
        self.label = label

    def measure(self, c):
        ph = self.style.padding_horizontal + self.style.border_horizontal
        pv = self.style.padding_vertical + self.style.border_vertical
        return (self._w + ph, self._w + ph, self._h + pv)

    def layout(self, c):
        self._resolve_box_model(self._w, self._h)


def save(node: Node, filename: str, width: float = None, embed_fonts: bool = False) -> Path:
    """渲染 → 保存 SVG（layout 由 render 自动触发）。"""
    renderer = Renderer()
    path = OUTPUT_DIR / filename
    renderer.render(node, str(path), embed_fonts=embed_fonts)
    print(f"  ✓ {path.absolute()}")
    return path


def heading(title: str):
    """打印章节标题。"""
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")
