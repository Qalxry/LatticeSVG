"""Math formula rendering — pluggable backend system.

Default backend: ``quickjax`` (in-process MathJax v4 via QuickJS).

Usage::

    from latticesvg.math import get_backend

    backend = get_backend()          # default QuickJax
    frag = backend.render(r"E=mc^2", font_size=16)
"""

from __future__ import annotations

from typing import Dict, Optional, Type

from .backend import MathBackend, SVGFragment, QuickJaxBackend

__all__ = [
    "MathBackend",
    "SVGFragment",
    "QuickJaxBackend",
    "set_default_backend",
    "get_default_backend_name",
    "get_backend",
    "register_backend",
]

# ---------------------------------------------------------------------------
# Global registry
# ---------------------------------------------------------------------------

_backend_registry: Dict[str, Type[MathBackend]] = {}
_backend_instances: Dict[str, MathBackend] = {}
_default_backend_name: str = "quickjax"


def register_backend(name: str, cls: Type[MathBackend]) -> None:
    """Register a math backend class under *name*."""
    _backend_registry[name] = cls
    # Invalidate cached instance if the class changed
    _backend_instances.pop(name, None)


def set_default_backend(name: str) -> None:
    """Set the global default math backend by name."""
    global _default_backend_name
    _default_backend_name = name


def get_default_backend_name() -> str:
    """Return the name of the current default backend."""
    return _default_backend_name


def get_backend(name: Optional[str] = None) -> MathBackend:
    """Return a (cached) backend instance.

    Parameters
    ----------
    name : str or None
        Backend name.  ``None`` → use the global default.

    Raises
    ------
    ValueError
        If the requested backend is not registered.
    RuntimeError
        If the backend reports itself as unavailable.
    """
    if name is None:
        name = _default_backend_name

    if name in _backend_instances:
        return _backend_instances[name]

    cls = _backend_registry.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown math backend {name!r}. "
            f"Registered: {list(_backend_registry)}"
        )

    inst = cls()
    if not inst.available():
        raise RuntimeError(
            f"Math backend {name!r} is not available. "
            f"Check its dependencies (pip install quickjax)."
        )
    _backend_instances[name] = inst
    return inst


# ---------------------------------------------------------------------------
# Auto-register built-in backends
# ---------------------------------------------------------------------------

register_backend("quickjax", QuickJaxBackend)
