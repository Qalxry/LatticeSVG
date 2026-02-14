# LatticeSVG 示例集

本目录包含多个独立的功能演示，每个文件可单独运行。

## 快速开始

```bash
# 运行单个示例
python examples/demo_12_text_basic.py

# 运行所有示例
python examples/run_all_demos.py
```

## 示例索引

### 基础 API (01-03)
- `demo_01_value_parser.py` - CSS 值解析器
- `demo_02_shorthand.py` - 样式简写属性
- `demo_03_computed_style.py` - 计算样式

### Grid 布局 (04-11)
- `demo_04_fixed_grid.py` - 固定列宽
- `demo_05_fr_grid.py` - 弹性单位 fr
- `demo_06_mixed_tracks.py` - 混合轨道
- `demo_07_auto_placement.py` - 自动放置
- `demo_08_spanning.py` - 跨行跨列
- `demo_09_alignment.py` - 对齐方式
- `demo_10_nested_grid.py` - 嵌套网格
- `demo_11_box_model.py` - 盒模型

### 文本排版 (12-13, 20-21, 24-25)
- `demo_12_text_basic.py` - 基本文本
- `demo_13_text_whitespace.py` - 空白符处理
- `demo_20_mixed_fonts.py` - 多字体混排
- `demo_21_overflow_wrap.py` - 换行控制
- `demo_24_ellipsis_precision.py` - 省略号精度
- `demo_25_pre_line.py` - 预格式文本

### 节点类型 (14-15)
- `demo_14_svg_node.py` - SVG 节点嵌入
- `demo_15_mpl_node.py` - Matplotlib 图表

### 高级功能 (16-19, 22-23, 30-31)
- `demo_16_templates.py` - 样式模板
- `demo_17_png_output.py` - PNG 导出
- `demo_18_full_report.py` - 综合报告
- `demo_19_layout_inspection.py` - 布局检查
- `demo_22_image_gallery.py` - 图片画廊
- `demo_23_min_max_size.py` - 尺寸约束
- `demo_30_grid_template_areas.py` - 命名区域
- `demo_31_table_api.py` - 表格 API

### 视觉样式 (26-29)
- `demo_26_opacity.py` - 不透明度
- `demo_27_border_radius.py` - 圆角边框
- `demo_28_border_style.py` - 边框样式
- `demo_29_render_to_drawing.py` - 自定义渲染

## 文件结构

每个示例文件都遵循统一模板：

```python
# =========================================================================
# Demo XX：功能描述
# =========================================================================
from latticesvg import ...
from utils import heading, save, ColorBox

def demo_XX_feature():
    heading("Demo XX: ...")
    
    # 创建布局
    grid = GridContainer(style={...})
    
    # 添加内容
    grid.add(...)
    
    # 保存输出
    save(grid, "XX_feature.svg", 600)
    
if __name__ == "__main__":
    demo_XX_feature()
```

## 工具函数

`utils.py` 提供共享工具：
- `ColorBox` - 可视化布局的彩色方块
- `save(node, filename, width)` - 布局 + 渲染 + 保存
- `heading(title)` - 打印章节标题
- `OUTPUT_DIR` - 输出目录路径

## 输出

所有生成的文件保存在 `examples/demo_output/` 目录。
