# =========================================================================
# Main — 自动发现并运行所有 demo_XX_*.py
# =========================================================================

import importlib
import re
from pathlib import Path

from utils import OUTPUT_DIR

# 所在目录
_DEMO_DIR = Path(__file__).resolve().parent


def _discover_demos():
    """扫描当前目录下所有 demo_XX_*.py，按编号排序后返回 (module_name, func_name) 列表。"""
    pattern = re.compile(r"^(demo_(\d+)_.+)\.py$")
    entries = []
    for p in sorted(_DEMO_DIR.glob("demo_*.py")):
        m = pattern.match(p.name)
        if m:
            module_name = m.group(1)       # e.g. "demo_01_value_parser"
            num = int(m.group(2))           # e.g. 1
            func_name = module_name         # 约定：函数名 == 模块名
            entries.append((num, module_name, func_name))
    entries.sort(key=lambda t: t[0])
    return [(mod, func) for _, mod, func in entries]


def main():
    demos = _discover_demos()

    print("=" * 60)
    print("  LatticeSVG 功能展示")
    print("=" * 60)

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"\n输出目录: {OUTPUT_DIR.absolute()}")
    print(f"检测到 {len(demos)} 个 demo\n")

    # 依次导入并执行
    for module_name, func_name in demos:
        mod = importlib.import_module(module_name)
        fn = getattr(mod, func_name, None)
        if fn is None:
            print(f"  ⚠  {module_name}.py 中未找到函数 {func_name}()，跳过")
            continue
        fn()

    # 汇总
    svg_count = len(list(OUTPUT_DIR.glob("*.svg")))
    png_count = len(list(OUTPUT_DIR.glob("*.png")))
    print(f"\n{'='*60}")
    print(f"  完成！共生成 {svg_count} 个 SVG + {png_count} 个 PNG")
    print(f"  输出目录: {OUTPUT_DIR.absolute()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()