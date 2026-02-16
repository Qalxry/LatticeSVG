# Math Formula API

The math module provides registration and management of LaTeX formula rendering backends.

## Module Overview

| Export | Type | Responsibility |
|---|---|---|
| `MathBackend` | Protocol | Backend interface protocol |
| `SVGFragment` | dataclass | Render result (SVG content + dimensions) |
| `QuickJaxBackend` | class | Default backend (based on QuickJax / MathJax v4) |
| `register_backend()` | function | Register a custom backend |
| `set_default_backend()` | function | Set the default backend |
| `get_backend()` | function | Get a backend instance |
| `get_default_backend_name()` | function | Get the default backend name |

## Basic Usage

```python
from latticesvg.math import get_backend

backend = get_backend()  # Default QuickJax
fragment = backend.render(r"E = mc^2", font_size=20, display=True)
print(fragment.width, fragment.height)
print(fragment.svg)  # SVG string fragment
```

## Custom Backends

```python
from latticesvg.math import register_backend, set_default_backend

class MyBackend:
    def render(self, latex: str, font_size: float, display: bool = True):
        # Return SVGFragment
        ...

register_backend("my_backend", MyBackend)
set_default_backend("my_backend")
```

## Auto-generated API Docs

### Backend Management

::: latticesvg.math
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4

### QuickJax Backend

::: latticesvg.math.backend
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 4
