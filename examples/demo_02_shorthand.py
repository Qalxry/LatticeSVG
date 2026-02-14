# =========================================================================
# Demo 2：简写展开
# =========================================================================

from utils import heading

def demo_02_shorthand():
    heading("Demo 2: 简写属性展开")

    from latticesvg.style.parser import expand_shorthand

    cases = [
        ("margin",  "10px"),
        ("margin",  "10px 20px"),
        ("margin",  "1px 2px 3px 4px"),
        ("padding", "15px"),
        ("gap",     "10px"),
        ("gap",     "10px 20px"),
    ]

    for prop, val in cases:
        result = expand_shorthand(prop, val)
        print(f"  {prop}: {val!r:20s} → {result}")

if __name__ == "__main__":
    demo_02_shorthand()