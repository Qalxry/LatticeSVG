# =========================================================================
# Demo 3：ComputedStyle & 继承
# =========================================================================

from latticesvg import ComputedStyle
from utils import heading

def demo_03_computed_style():
    heading("Demo 3: ComputedStyle 与属性继承")

    parent = ComputedStyle({
        "font-size": "24px",
        "color": "#ff0000",
        "width": "600px",
    })
    child = ComputedStyle({"font-size": "14px"}, parent_style=parent)

    print(f"  父节点 font-size  = {parent.get('font-size')}")
    print(f"  父节点 color      = {parent.get('color')}")
    print(f"  父节点 width      = {parent.get('width')}")
    print(f"  子节点 font-size  = {child.get('font-size')}  ← 覆盖")
    print(f"  子节点 color      = {child.get('color')}  ← 继承")
    print(f"  子节点 width      = {child.get('width')}     ← 不继承，默认 auto")

    s = ComputedStyle({"padding": "10px 20px"})
    print(f"  padding shorthand → T={s.padding_top} R={s.padding_right} "
          f"B={s.padding_bottom} L={s.padding_left}")
    print(f"  padding_horizontal = {s.padding_horizontal}")
    
if __name__ == "__main__":
    demo_03_computed_style()