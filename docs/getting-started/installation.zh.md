# 安装

## 使用 pip 安装

```bash
pip install latticesvg
```

## 可选功能

LatticeSVG 提供两组可选依赖，按需安装：

=== "PNG 输出"

    ```bash
    pip install latticesvg[png]
    ```

    安装 [CairoSVG](https://cairosvg.org/) 以支持 SVG → PNG 转换。

=== "自动断词"

    ```bash
    pip install latticesvg[hyphens]
    ```

    安装 [Pyphen](https://github.com/Kozea/Pyphen) 以支持多语言自动断词（`hyphens: auto`）。

=== "全部安装"

    ```bash
    pip install latticesvg[png,hyphens]
    ```

## 系统依赖

### FreeType

LatticeSVG 使用 [freetype-py](https://github.com/rougier/freetype-py) 进行字形精确测量，需要系统安装 FreeType 库。

=== "Linux (Debian/Ubuntu)"

    ```bash
    sudo apt install libfreetype6-dev
    ```

=== "Linux (Fedora/RHEL)"

    ```bash
    sudo dnf install freetype-devel
    ```

=== "macOS"

    ```bash
    brew install freetype
    ```

    macOS 通常已预装 FreeType。

=== "Windows"

    freetype-py 会自动下载预编译的 FreeType DLL，通常无需额外操作。

### Cairo（仅 PNG 输出）

如需 PNG 输出，还需安装 Cairo 图形库：

=== "Linux (Debian/Ubuntu)"

    ```bash
    sudo apt install libcairo2-dev
    ```

=== "macOS"

    ```bash
    brew install cairo
    ```

=== "Windows"

    参阅 [CairoSVG 安装指南](https://cairosvg.org/documentation/#installation)。

## 验证安装

```python
import latticesvg
print(latticesvg.__version__)  # 0.1.0
```

```python
from latticesvg import GridContainer, TextNode, Renderer

page = GridContainer(style={"width": "200px", "padding": "10px"})
page.add(TextNode("Hello LatticeSVG!"))
Renderer().render(page, "test.svg")
print("✓ LatticeSVG 安装成功")
```

## 开发安装

如果你想从源码安装并参与开发：

```bash
git clone https://github.com/nicholasgasior/LatticeSVG.git
cd LatticeSVG
pip install -e ".[dev,docs]"
pytest  # 运行测试
```
