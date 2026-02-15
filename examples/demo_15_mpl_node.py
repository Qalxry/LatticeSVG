# =========================================================================
# Demo 15：MplNode（Matplotlib 图表嵌入）
# =========================================================================

from latticesvg import GridContainer, MplNode
from utils import heading, save

def demo_15_mpl_node():
    heading("Demo 15: MplNode Matplotlib 图表嵌入")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  ⚠ matplotlib/numpy 未安装，跳过此演示")
        return

    # 创建两个图表
    fig1, ax1 = plt.subplots(figsize=(4, 3), dpi=100)
    x = np.linspace(0, 2 * np.pi, 100)
    ax1.plot(x, np.sin(x), color="#e74c3c", linewidth=2, label="sin(x)")
    ax1.plot(x, np.cos(x), color="#3498db", linewidth=2, label="cos(x)")
    ax1.set_title("Trigonometric Functions")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    fig2, ax2 = plt.subplots(figsize=(4, 3), dpi=100)
    categories = ["A", "B", "C", "D"]
    values = [23, 45, 56, 78]
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
    ax2.bar(categories, values, color=colors)
    ax2.set_title("Bar Chart")
    ax2.set_ylabel("Value")

    grid = GridContainer(style={
        "width": "800px",
        "padding": "15px",
        "background-color": "#ffffff",
        "grid-template-columns": ["1fr", "1fr"],
        "gap": "15px",
    })

    grid.add(MplNode(fig1), row=1, col=1)
    grid.add(MplNode(fig2), row=1, col=2)

    save(grid, "15_mpl_node.svg")

    plt.close("all")
    
if __name__ == "__main__":
    demo_15_mpl_node()