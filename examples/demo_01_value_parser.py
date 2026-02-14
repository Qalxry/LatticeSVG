# =========================================================================
# Demo 1：CSS 值解析器
# =========================================================================

from latticesvg.style.parser import parse_value
from utils import heading

def demo_01_value_parser():
    heading("Demo 1: CSS 值解析器")

    examples = [
        ("200px",  {}),
        ("50%",    {"reference_length": 400}),
        ("2em",    {"font_size": 16}),
        ("1.5fr",  {}),
        ("12pt",   {}),
        ("auto",   {}),
        ("min-content", {}),
        ("#ff0000",     {}),
        ("#f00",        {}),
        ("red",         {}),
        ("rgb(0, 128, 255)", {}),
        ("rgba(0, 0, 0, 0.5)", {}),
        ("center",      {}),
        ("bold",        {}),
        ("row dense",   {}),
    ]

    for raw, kwargs in examples:
        result = parse_value(raw, **kwargs)
        print(f"  parse_value({raw!r:25s}) → {result!r}")

if __name__ == "__main__":
    demo_01_value_parser()