# =========================================================================
# Demo 32：三列瀑布流卡片 — 精美样式
# =========================================================================

from pathlib import Path
from latticesvg import GridContainer, TextNode, ImageNode, SVGNode
from utils import heading, save

# 资源路径
ASSETS_DIR = Path(__file__).parent / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
IMAGES_DIR = ASSETS_DIR / "images"

def demo_32_waterfall_cards():
    heading("Demo 32: 三列瀑布流卡片（精美样式）")

    # 卡片数据
    cards_data = [
        # 列1：旅行与探索
        {
            "title": "Mountain Adventure",
            "description": "Explore breathtaking peaks and discover hidden trails in the Alps.",
            "image": str(IMAGES_DIR / "mountain.jpg"),
            "icon": str(ICONS_DIR / "mountain.svg"),
            "category": "Travel",
            "color": "#3498db",
        },
        {
            "title": "Ocean Serenity",
            "description": "Find peace in the rhythm of waves and endless blue horizons.",
            "image": str(IMAGES_DIR / "ocean.jpg"),
            "icon": str(ICONS_DIR / "waves.svg"),
            "category": "Nature",
            "color": "#16a085",
        },
        {
            "title": "Urban Exploration",
            "description": "Navigate vibrant streets and architectural marvels in global cities.",
            "image": str(IMAGES_DIR / "city.jpg"),
            "icon": str(ICONS_DIR / "building.svg"),
            "category": "Urban",
            "color": "#34495e",
        },
        
        # 列2：艺术与设计
        {
            "title": "Creative Studio",
            "description": "Unleash your imagination with cutting-edge design tools and inspiration.",
            "image": str(IMAGES_DIR / "studio.jpg"),
            "icon": str(ICONS_DIR / "palette.svg"),
            "category": "Design",
            "color": "#e74c3c",
        },
        {
            "title": "Photography Journey",
            "description": "Capture moments that tell stories through the lens of your camera.",
            "image": str(IMAGES_DIR / "photo.jpg"),
            "icon": str(ICONS_DIR / "camera.svg"),
            "category": "Art",
            "color": "#9b59b6",
        },
        {
            "title": "Music & Sound",
            "description": "Immerse yourself in melodies that transcend language and culture.",
            "image": str(IMAGES_DIR / "music.jpg"),
            "icon": str(ICONS_DIR / "music.svg"),
            "category": "Audio",
            "color": "#1abc9c",
        },
        
        # 列3：科技与未来
        {
            "title": "Code & Innovation",
            "description": "Build tomorrow's solutions with modern programming paradigms.",
            "image": str(IMAGES_DIR / "code.jpg"),
            "icon": str(ICONS_DIR / "code.svg"),
            "category": "Tech",
            "color": "#2ecc71",
        },
        {
            "title": "Space Frontier",
            "description": "Journey beyond Earth and explore the mysteries of the cosmos.",
            "image": str(IMAGES_DIR / "space.jpg"),
            "icon": str(ICONS_DIR / "rocket.svg"),
            "category": "Science",
            "color": "#8e44ad",
        },
        {
            "title": "Digital Future",
            "description": "Experience the convergence of AI, blockchain, and virtual reality.",
            "image": str(IMAGES_DIR / "future.jpg"),
            "icon": str(ICONS_DIR / "sparkles.svg"),
            "category": "Innovation",
            "color": "#f39c12",
        },
    ]

    # ==================== 主容器 ====================
    page = GridContainer(style={
        "width": "1200px",
        "padding": "40px",
        "background-color": "#f8f9fa",
        "grid-template-columns": ["1fr"],
        "gap": "32px",
    })

    # ==================== 标题区域 ====================
    header = GridContainer(style={
        "grid-template-columns": ["1fr"],
        "gap": "12px",
    })
    header.add(TextNode("Discover Amazing Experiences", style={
        "font-size": "36px",
        "font-weight": "bold",
        "color": "#2c3e50",
        "text-align": "center",
    }), row=1, col=1)
    header.add(TextNode("Curated collection of inspiring destinations, creative pursuits, and technological wonders", style={
        "font-size": "16px",
        "color": "#7f8c8d",
        "text-align": "center",
    }), row=2, col=1)
    page.add(header, row=1, col=1)

    # ==================== 三列瀑布流网格 ====================
    # 使用三个独立的列容器实现真正的瀑布流效果
    cards_grid = GridContainer(style={
        "grid-template-columns": ["1fr", "1fr", "1fr"],
        "gap": "24px",
        "align-items": "start",
    })

    # 创建三个列容器
    columns = []
    for i in range(3):
        column = GridContainer(style={
            "grid-template-columns": ["1fr"],
            "gap": "24px",
        })
        columns.append(column)
        cards_grid.add(column, row=1, col=i+1)

    # 将卡片分配到三列中
    for idx, card in enumerate(cards_data):
        col_idx = idx % 3
        row_in_col = (idx // 3) + 1
        
        # ---------- 单个卡片容器 ----------
        card_container = GridContainer(style={
            "background-color": "#ffffff",
            "border-radius": "16px",
            "overflow": "hidden",
            "grid-template-columns": ["1fr"],
            "grid-template-rows": ["auto", "auto"],
            "gap": "0px",
        })

        # 图片区域
        card_container.add(ImageNode(card["image"], style={
            "width": "100%",
            "height": "auto",
        }, object_fit="cover"), row=1, col=1)

        # 内容区域
        content = GridContainer(style={
            "padding": "20px",
            "grid-template-columns": ["1fr"],
            "gap": "12px",
        })

        # 分类标签 + 图标
        category_row = GridContainer(style={
            "grid-template-columns": ["24px", "1fr"],
            "gap": "8px",
            "align-items": "center",
        })
        
        # 图标 (使用小的 SVG)
        category_row.add(SVGNode(card["icon"], is_file=True, style={
            "width": "20px",
            "height": "20px",
        }), row=1, col=1)
        
        # 分类标签
        category_row.add(TextNode(card["category"], style={
            "font-size": "12px",
            "font-weight": "bold",
            "color": card["color"],
            "text-align": "left",
        }), row=1, col=2)
        content.add(category_row, row=1, col=1)

        # 标题
        content.add(TextNode(card["title"], style={
            "font-size": "20px",
            "font-weight": "bold",
            "color": "#2c3e50",
            "line-height": "1.3",
        }), row=2, col=1)

        # 描述文字
        content.add(TextNode(card["description"], style={
            "font-size": "14px",
            "color": "#7f8c8d",
            "line-height": "1.6",
            "white-space": "normal",
        }), row=3, col=1)

        # 底部装饰线
        content.add(GridContainer(style={
            "height": "3px",
            "background-color": card["color"],
            "border-radius": "2px",
            "width": "60px",
        }), row=4, col=1)

        card_container.add(content, row=2, col=1)
        
        # 将卡片添加到对应的列
        columns[col_idx].add(card_container, row=row_in_col, col=1)

    page.add(cards_grid, row=2, col=1)

    # ==================== 底部说明 ====================
    footer = GridContainer(style={
        "grid-template-columns": ["1fr"],
        "padding": "20px",
        "background-color": "#ecf0f1",
        "border-radius": "12px",
    })
    footer.add(TextNode("💡 Images from picsum.photos • Icons from Lucide Icons • Powered by LatticeSVG", style={
        "font-size": "13px",
        "color": "#95a5a6",
        "text-align": "center",
    }), row=1, col=1)
    page.add(footer, row=3, col=1)

    # ==================== 布局和渲染 ====================
    save(page, "demo_32_waterfall_cards.svg")
    print("  ✓ 完成！包含 9 个精美卡片，三列瀑布流布局")


if __name__ == "__main__":
    demo_32_waterfall_cards()
