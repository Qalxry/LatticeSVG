# =========================================================================
# Demo 37：字体嵌入 / 子集化
# =========================================================================

from latticesvg import GridContainer, TextNode, Renderer
from utils import heading, OUTPUT_DIR

def demo_37_font_embed():
    """
    演示将 WOFF2 字体嵌入到 SVG 中，实现自包含输出。
    生成的 SVG 在任意机器上都能正确显示，无需安装字体。
    """
    
    heading("字体嵌入 / 子集化")

    # --- 构建包含多样文本的布局 ---
    root = GridContainer(
        style={
            "width": 700,
            "grid-template-columns": ["1fr"],
            "grid-auto-rows": "auto",
            "gap": 12,
            "padding": 20,
            "background-color": "#ffffff",
        }
    )

    # 标题
    root.add(TextNode(
        "字体嵌入演示  —  自包含 SVG",
        style={
            "font-size": 22,
            "font-weight": "bold",
            "color": "#1a1a2e",
        },
    ))

    # 富文本：粗体、斜体、代码
    root.add(TextNode(
        '该 SVG 已嵌入<b>子集字体</b>。'
        '<i>在任何机器上</i>都能保持一致显示。'
        '不依赖<code>font-family</code>。',
        style={"font-size": 14, "color": "#333333"},
        markup="html",
    ))

    # 中英文混排
    root.add(TextNode(
        "The quick brown fox jumps over the lazy dog. "
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
        style={"font-size": 13, "color": "#555555"},
    ))

    # 中文 + 特殊字符
    root.add(TextNode(
        "中文文本：汉字、拼音与标点混合。"
        "特殊字符测试：ᵗʰ ℃ ™ © ® § ¶ † ‡ ✅ 🚀 Ḧ̵́̓e̸͊̚l̶͐̚l̷̓̇o̴̾̅ ̵́̚T̴͛͝y̵̋͛p̶͌̋ô̴̌g̵͑̂r̸͐͑a̷͐̚p̸̈́̓ḣ̴̅y̶̾̅!̴͠͝ 成功！",
        style={"font-size": 14, "color": "#2d3436"},
    ))

    # 上下标（富文本）
    root.add(TextNode(
        'H<sub>2</sub>O 是水，E=mc<sup>2</sup> 是爱因斯坦的质能方程。',
        style={"font-size": 14, "color": "#0984e3"},
        markup="html",
    ))
    
    # ── 渲染 ──
    renderer = Renderer()

    # --- 不嵌入字体（参考） ---
    path_no_embed = OUTPUT_DIR / "37a_font_embed_off.svg"
    renderer.render(root, str(path_no_embed))
    svg_no = path_no_embed.stat().st_size
    print(f"  ✓ 未嵌入: {path_no_embed}  ({svg_no:,} bytes)")

    # --- 嵌入字体 ---
    path_embed = OUTPUT_DIR / "37b_font_embed_on.svg"
    renderer.render(root, str(path_embed), embed_fonts=True)
    svg_yes = path_embed.stat().st_size
    print(f"  ✓ 已嵌入: {path_embed}  ({svg_yes:,} bytes)")

    # 统计信息
    print(f"\n  尺寸增加: {svg_yes - svg_no:,} bytes "
          f"(+{(svg_yes / svg_no - 1)*100:.0f}%)")
    print("  嵌入后 SVG 完全自包含 — 无需字体即可精确显示。")


if __name__ == "__main__":
    demo_37_font_embed()
