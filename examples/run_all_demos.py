# =========================================================================
# Main
# =========================================================================

from utils import OUTPUT_DIR
from demo_01_value_parser import demo_01_value_parser
from demo_02_shorthand import demo_02_shorthand
from demo_03_computed_style import demo_03_computed_style
from demo_04_fixed_grid import demo_04_fixed_grid
from demo_05_fr_grid import demo_05_fr_grid
from demo_06_mixed_tracks import demo_06_mixed_tracks
from demo_07_auto_placement import demo_07_auto_placement
from demo_08_spanning import demo_08_spanning
from demo_09_alignment import demo_09_alignment
from demo_10_nested_grid import demo_10_nested_grid
from demo_11_box_model import demo_11_box_model
from demo_12_text_basic import demo_12_text_basic
from demo_13_text_whitespace import demo_13_text_whitespace
from demo_14_svg_node import demo_14_svg_node
from demo_15_mpl_node import demo_15_mpl_node
from demo_16_templates import demo_16_templates
from demo_17_png_output import demo_17_png_output
from demo_18_full_report import demo_18_full_report
from demo_19_layout_inspection import demo_19_layout_inspection
from demo_20_mixed_fonts import demo_20_mixed_fonts
from demo_21_overflow_wrap import demo_21_overflow_wrap
from demo_22_image_gallery import demo_22_image_gallery
from demo_23_min_max_size import demo_23_min_max_size
from demo_24_ellipsis_precision import demo_24_ellipsis_precision
from demo_25_pre_line import demo_25_pre_line
from demo_26_opacity import demo_26_opacity
from demo_27_border_radius import demo_27_border_radius
from demo_28_border_style import demo_28_border_style
from demo_29_render_to_drawing import demo_29_render_to_drawing
from demo_30_grid_template_areas import demo_30_grid_template_areas
from demo_31_table_api import demo_31_table_api

def main():
    print("=" * 60)
    print("  LatticeSVG 功能展示")
    print("=" * 60)

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"\n输出目录: {OUTPUT_DIR.absolute()}")

    # 纯计算演示（无文件输出）
    demo_01_value_parser()
    demo_02_shorthand()
    demo_03_computed_style()

    # SVG 文件输出演示
    demo_04_fixed_grid()
    demo_05_fr_grid()
    demo_06_mixed_tracks()
    demo_07_auto_placement()
    demo_08_spanning()
    demo_09_alignment()
    demo_10_nested_grid()
    demo_11_box_model()
    demo_12_text_basic()
    demo_13_text_whitespace()
    demo_14_svg_node()
    demo_15_mpl_node()
    demo_16_templates()
    demo_17_png_output()
    demo_18_full_report()
    demo_19_layout_inspection()
    demo_20_mixed_fonts()
    demo_21_overflow_wrap()
    demo_22_image_gallery()

    # P0 验收演示
    demo_23_min_max_size()
    demo_24_ellipsis_precision()
    demo_25_pre_line()
    demo_26_opacity()

    # P1 验收演示
    demo_27_border_radius()
    demo_28_border_style()
    demo_29_render_to_drawing()

    # P2 验收演示
    demo_30_grid_template_areas()
    demo_31_table_api()

    # 汇总
    svg_count = len(list(OUTPUT_DIR.glob("*.svg")))
    png_count = len(list(OUTPUT_DIR.glob("*.png")))
    print(f"\n{'='*60}")
    print(f"  完成！共生成 {svg_count} 个 SVG + {png_count} 个 PNG")
    print(f"  输出目录: {OUTPUT_DIR.absolute()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()