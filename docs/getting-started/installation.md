# Installation

## Install with pip

```bash
pip install latticesvg
```

## Optional Extras

LatticeSVG provides two optional dependency groups:

=== "PNG Output"

    ```bash
    pip install latticesvg[png]
    ```

    Installs [CairoSVG](https://cairosvg.org/) for SVG → PNG conversion.

=== "Auto-Hyphenation"

    ```bash
    pip install latticesvg[hyphens]
    ```

    Installs [Pyphen](https://github.com/Kozea/Pyphen) for multi-language auto-hyphenation (`hyphens: auto`).

=== "Install All"

    ```bash
    pip install latticesvg[png,hyphens]
    ```

## System Dependencies

### FreeType

LatticeSVG uses [freetype-py](https://github.com/rougier/freetype-py) for precise glyph measurement, which requires the FreeType library on your system.

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

    macOS usually comes with FreeType pre-installed.

=== "Windows"

    freetype-py automatically downloads a pre-compiled FreeType DLL — no extra steps needed.

### Cairo (PNG Output Only)

For PNG output, you also need the Cairo graphics library:

=== "Linux (Debian/Ubuntu)"

    ```bash
    sudo apt install libcairo2-dev
    ```

=== "macOS"

    ```bash
    brew install cairo
    ```

=== "Windows"

    See the [CairoSVG installation guide](https://cairosvg.org/documentation/#installation).

## Verify Installation

```python
import latticesvg
print(latticesvg.__version__)  # 0.1.0
```

```python
from latticesvg import GridContainer, TextNode, Renderer

page = GridContainer(style={"width": "200px", "padding": "10px"})
page.add(TextNode("Hello LatticeSVG!"))
Renderer().render(page, "test.svg")
print("✓ LatticeSVG installed successfully")
```

## Development Installation

To install from source and contribute:

```bash
git clone https://github.com/nicholasgasior/LatticeSVG.git
cd LatticeSVG
pip install -e ".[dev,docs]"
pytest  # Run tests
```
