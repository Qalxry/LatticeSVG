# =========================================================================
# Demo 51：字体路径查询 API + MplNode 自动字体配置（2×2 多字体对比）
# =========================================================================

from latticesvg import GridContainer, MplNode, TextNode
from latticesvg.text import get_font_path, list_fonts
from utils import heading, save


# 四组字体配置：(显示名称, CSS font-family 值)
FONT_CONFIGS = [
    ("微软雅黑 Microsoft YaHei",  "Microsoft YaHei, sans-serif"),
    ("楷体 KaiTi",                "KaiTi, serif"),
    ("仿宋 FangSong",            "FangSong, serif"),
    ("Noto Sans CJK JP",         "Noto Sans CJK JP, sans-serif"),
]


def _make_chart(plt, title: str, chart_type: int):
    """Create a small matplotlib figure with mixed CJK/Latin labels.

    Note: tight_layout() is intentionally omitted here — MplNode's
    auto_mpl_font will re-run it inside the correct rc_context so
    that text metrics match the final font.
    """
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)

    if chart_type == 0:
        x = [1, 2, 3, 4, 5]
        y = [3, 7, 5, 9, 6]
        ax.plot(x, y, "o-", color="#e74c3c", linewidth=2)
        ax.set_title(title)
        ax.set_xlabel("Sample 样本编号")
        ax.set_ylabel("Value 数值 (px)")
    elif chart_type == 1:
        categories = ["春季 Spring", "夏季 Summer", "秋季 Autumn", "冬季 Winter"]
        values = [28, 45, 36, 18]
        colors = ["#2ecc71", "#e74c3c", "#f39c12", "#3498db"]
        ax.bar(categories, values, color=colors)
        ax.set_title(title)
        ax.set_ylabel("Count 数量")
        ax.tick_params(axis="x", rotation=15)
    elif chart_type == 2:
        labels = ["类别A Cat-A", "类别B Cat-B", "类别C Cat-C", "其他 Other"]
        sizes = [35, 30, 20, 15]
        ax.pie(sizes, labels=labels, autopct="%1.0f%%", startangle=90,
               colors=["#e74c3c", "#3498db", "#2ecc71", "#f39c12"])
        ax.set_title(title)
    else:
        import numpy as np
        x = np.linspace(0, 2 * np.pi, 80)
        ax.fill_between(x, 0, np.sin(x), alpha=0.4, color="#3498db", label="sin 正弦")
        ax.fill_between(x, 0, np.cos(x), alpha=0.4, color="#e74c3c", label="cos 余弦")
        ax.set_title(title)
        ax.set_xlabel("Angle 角度 (rad)")
        ax.legend(loc="upper right")

    ax.grid(True, alpha=0.2)
    return fig


def demo_51_font_query_mpl():
    heading("Demo 51: 字体路径查询 & MplNode 自动字体（2×2 对比）")

    # ── Part 1: 字体路径查询 API ─────────────────────────────
    print("\n  [get_font_path]")
    for label, css_val in FONT_CONFIGS:
        name = css_val.split(",")[0].strip()
        path = get_font_path(name)
        print(f"    {name:30s} => {path}")

    print(f"\n  [list_fonts] 共索引 {len(list_fonts())} 个字体")

    # ── Part 2: 2×2 图表，每个使用不同字体 ───────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np  # noqa: F401 — used inside _make_chart
    except ImportError:
        print("  ⚠ matplotlib/numpy 未安装，跳过图表演示")
        return

    grid = GridContainer(style={
        "width": "860px",
        "padding": "20px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "12px",
    })

    # 标题行（跨两列）
    grid.add(TextNode(
        "MplNode auto_mpl_font 多字体对比",
        style={
            "font-size": "22px",
            "font-weight": "bold",
            "text-align": "center",
            "font-family": "Microsoft YaHei, sans-serif",
            "grid-column": "1 / 3",
        },
    ), row=1, col=1)

    for i, (label, css_font) in enumerate(FONT_CONFIGS):
        row = 2 + i // 2 * 2  # rows: 2,2,4,4
        col = i % 2 + 1       # cols: 1,2,1,2

        chart_title = f"{label} 示例 Chart"
        fig = _make_chart(plt, chart_title, chart_type=i)

        # 每个图表放在独立的子容器中，设置各自的 font-family
        # MplNode 的 auto_mpl_font 会自动读取 CSS font-family
        # 并在 savefig 时通过 rc_context 应用到 matplotlib
        cell = GridContainer(style={
            "grid-template-columns": ["1fr"],
            "gap": "4px",
            "font-family": css_font,
        })
        cell.add(MplNode(fig), row=1, col=1)
        cell.add(TextNode(
            f"字体 Font: {label}",
            style={
                "font-size": "12px",
                "text-align": "center",
                "color": "#555555",
            },
        ), row=2, col=1)

        grid.add(cell, row=row, col=col)

    save(grid, "51_font_query_mpl.svg")
    plt.close("all")


if __name__ == "__main__":
    demo_51_font_query_mpl()
