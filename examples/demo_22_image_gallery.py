# =========================================================================
# Demo 22：图像生成模型 Gallery
# =========================================================================

from latticesvg import GridContainer, TextNode
from utils import heading, save, ColorBox

def demo_22_image_gallery():
    heading("Demo 22: 图像生成模型 Gallery")
    import colorsys

    IMG_H = 60                 # 统一展示高度
    FONT = "Times New Roman, SimSun, serif"

    # 10 张图片的原始分辨率 (w, h)
    specs = [
        (512, 512),   (512, 512),       # img 1-2  : 1:1
        (1024, 1024), (1024, 1024),      # img 3-4  : 1:1
        (512, 384),   (512, 384),        # img 5-6  : 4:3
        (786, 1024),  (786, 1024),       # img 7-8  : ≈3:4
        (1920, 1080), (1920, 1080),      # img 9-10 : 16:9
    ]
    # 等高缩放后的展示宽度
    dw = [round(IMG_H * w / h, 1) for w, h in specs]

    NAME_W = 90
    GAP = 4
    PAD = 12
    total_w = NAME_W + sum(dw) + GAP * 10 + PAD * 2
    cols = [f"{NAME_W}px"] + [f"{w}px" for w in dw]

    grid = GridContainer(style={
        "width": f"{total_w}px",
        "padding": f"{PAD}px",
        "grid-template-columns": cols,
        "gap": f"{GAP}px",
        "background-color": "#1a1a2e",
    })

    # ── 第 1 行：表头 ──
    grid.add(TextNode("模型名称", style={
        "font-family": FONT, "font-size": "12px", "font-weight": "bold",
        "color": "#e8e8e8", "text-align": "center",
        "padding": "8px 4px", "background-color": "#16213e",
        "display": "flex", "align-items": "center",
    }), row=1, col=1)

    grid.add(TextNode("生成图片对比", style={
        "font-family": FONT, "font-size": "14px", "font-weight": "bold",
        "color": "#ffffff", "text-align": "center",
        "padding": "8px", "background-color": "#0f3460",
        "display": "flex", "align-items": "center",
    }), row=1, col=2, col_span=10)

    # ── 第 2–10 行：模型图片 ──
    models = [
        "DALL\u00b7E 3", "Midjourney v6", "SD XL 1.0",
        "Flux.1 Pro", "Imagen 3", "Adobe Firefly",
        "Kandinsky 3", "\u901a\u4e49\u4e07\u76f8", "Ideogram 2",
    ]

    for i, name in enumerate(models):
        r = i + 2
        grid.add(TextNode(name, style={
            "font-family": FONT, "font-size": "10px",
            "color": "#d0d0d0", "text-align": "center",
            "padding": "4px 2px", "background-color": "#16213e",
            "display": "flex", "align-items": "center",
        }), row=r, col=1)

        hue = i / len(models)
        for j in range(10):
            sat = 0.50 + (j % 5) * 0.08
            lit = 0.32 + (j % 4) * 0.08
            rgb = colorsys.hls_to_rgb(hue, lit, sat)
            color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
            grid.add(
                ColorBox(dw[j], IMG_H, **{"background-color": color}),
                row=r, col=j + 2,
            )

    # ── 第 11 行：图片参数 ──
    grid.add(TextNode("图片参数：", style={
        "font-family": FONT, "font-size": "10px", "font-weight": "bold",
        "color": "#e0e0e0", "text-align": "center",
        "padding": "6px 2px", "background-color": "#16213e",
        "display": "flex", "align-items": "center",
    }), row=11, col=1)

    param_info = [
        ("1girl, solo, upper body, looking at viewer, smile",   "512\u00d7512",   "1:1"),
        ("1boy, playing guitar, standing, outdoors",            "512\u00d7512",   "1:1"),
        ("landscape, mountains, river, sunset, vibrant colors", "1024\u00d71024", "1:1"),
        ("cityscape, night, neon lights, rainy, reflections",   "1024\u00d71024", "1:1"),
        ("cute cat, sitting, big eyes, colorful background",    "512\u00d7384",   "4:3"),
        ("futuristic robot, metallic, glowing eyes, city",      "512\u00d7384",   "4:3"),
        ("fantasy castle, floating islands, bright sky",        "786\u00d71024",  "\u22483:4"),
        ("portrait of a woman, detailed, soft lighting",        "786\u00d71024",  "\u22483:4"),
        ("space scene, planets, stars, nebula, vibrant colors", "1920\u00d71080", "16:9"),
        ("vintage car, driving on road, countryside, sunny",    "1920\u00d71080", "16:9"),
    ]
    for j, (prompt, res, ratio) in enumerate(param_info):
        grid.add(TextNode(f"{prompt}\n{res}\n{ratio}", style={
            "font-family": FONT, "font-size": "8px",
            "color": "#b0b0b0", "text-align": "center",
            "padding": "4px 2px", "background-color": "#0f3460",
            "white-space": "pre-wrap",
            "display": "flex", "align-items": "center",
        }), row=11, col=j + 2)

    save(grid, "22_image_gallery.svg")
    print(f"  → 9 个模型 × 10 张图片对比，宽 {total_w:.0f}px")
    
if __name__ == "__main__":
    demo_22_image_gallery()