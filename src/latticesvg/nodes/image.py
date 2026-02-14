"""ImageNode — a leaf node that embeds a raster image."""

from __future__ import annotations

import base64
import io
import os
from typing import Any, Dict, Optional, Tuple, Union

from .base import LayoutConstraints, Node, Rect


class ImageNode(Node):
    """Node that displays a raster image (PNG, JPEG, etc.).

    The image's intrinsic size is read lazily via Pillow.  The
    ``object-fit`` property controls how the image is scaled within the
    allocated space.

    Parameters
    ----------
    src : str, bytes, or PIL.Image
        Image source:
        - File path (str)
        - URL starting with 'http://' or 'https://' (str)
        - Raw image bytes (bytes)
        - PIL Image object
    style : dict, optional
        Style properties
    parent : Node, optional
        Parent node
    object_fit : str, optional
        Object-fit mode ('fill', 'contain', 'cover', 'none')
    """

    def __init__(
        self,
        src: Union[str, bytes, Any],
        style: Optional[Dict[str, Any]] = None,
        parent: Optional[Node] = None,
        object_fit: Optional[str] = None,
    ) -> None:
        super().__init__(style=style, parent=parent)
        self.src: Union[str, bytes, Any] = src
        if object_fit:
            self.style.set("object-fit", object_fit)
        self._intrinsic_width: Optional[float] = None
        self._intrinsic_height: Optional[float] = None
        self._base64_data: Optional[str] = None
        self._image_bytes: Optional[bytes] = None
        self._pil_image: Optional[Any] = None

    # -----------------------------------------------------------------
    # Lazy intrinsic size detection
    # -----------------------------------------------------------------

    def _load_image(self) -> Any:
        """Load the PIL Image from various sources."""
        if self._pil_image is not None:
            return self._pil_image

        try:
            from PIL import Image  # type: ignore

            # If already a PIL Image
            if hasattr(self.src, 'size') and hasattr(self.src, 'mode'):
                self._pil_image = self.src
                return self._pil_image

            # If bytes
            if isinstance(self.src, bytes):
                self._pil_image = Image.open(io.BytesIO(self.src))
                return self._pil_image

            # If URL
            if isinstance(self.src, str) and (self.src.startswith('http://') or self.src.startswith('https://')):
                import urllib.request
                with urllib.request.urlopen(self.src) as response:
                    self._image_bytes = response.read()
                self._pil_image = Image.open(io.BytesIO(self._image_bytes))
                return self._pil_image

            # Otherwise assume file path
            self._pil_image = Image.open(self.src)
            return self._pil_image

        except Exception as e:
            # Fallback — return None, will use default size
            return None

    def _ensure_intrinsic_size(self) -> None:
        if self._intrinsic_width is not None:
            return
        
        img = self._load_image()
        if img is not None:
            self._intrinsic_width = float(img.width)
            self._intrinsic_height = float(img.height)
        else:
            # Fallback — assume a reasonable default
            self._intrinsic_width = 300.0
            self._intrinsic_height = 150.0

    @property
    def intrinsic_width(self) -> float:
        self._ensure_intrinsic_size()
        return self._intrinsic_width  # type: ignore

    @property
    def intrinsic_height(self) -> float:
        self._ensure_intrinsic_size()
        return self._intrinsic_height  # type: ignore

    # -----------------------------------------------------------------
    # Base64 encoding for SVG embedding
    # -----------------------------------------------------------------

    def get_base64(self) -> str:
        """Return the image as a base64-encoded data URI."""
        if self._base64_data is not None:
            return self._base64_data

        # Determine MIME type
        mime = "image/png"
        if isinstance(self.src, str):
            if self.src.startswith('http://') or self.src.startswith('https://'):
                # Guess from URL
                lower = self.src.lower()
                if '.jpg' in lower or '.jpeg' in lower:
                    mime = "image/jpeg"
                elif '.gif' in lower:
                    mime = "image/gif"
                elif '.webp' in lower:
                    mime = "image/webp"
                elif '.svg' in lower:
                    mime = "image/svg+xml"
            else:
                # File path
                ext = os.path.splitext(self.src)[1].lower()
                mime = {
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".gif": "image/gif",
                    ".webp": "image/webp",
                    ".svg": "image/svg+xml",
                }.get(ext, "image/png")

        # Get bytes
        img_bytes: bytes
        if isinstance(self.src, bytes):
            img_bytes = self.src
        elif hasattr(self.src, 'size') and hasattr(self.src, 'mode'):
            # PIL Image — save to bytes
            from PIL import Image  # type: ignore
            buf = io.BytesIO()
            # Determine format from mime
            fmt = "PNG"
            if "jpeg" in mime:
                fmt = "JPEG"
            elif "gif" in mime:
                fmt = "GIF"
            elif "webp" in mime:
                fmt = "WEBP"
            self.src.save(buf, format=fmt)
            img_bytes = buf.getvalue()
        elif isinstance(self.src, str) and (self.src.startswith('http://') or self.src.startswith('https://')):
            # URL — use cached bytes if available
            if self._image_bytes is None:
                import urllib.request
                with urllib.request.urlopen(self.src) as response:
                    self._image_bytes = response.read()
            img_bytes = self._image_bytes
        else:
            # File path
            with open(self.src, "rb") as f:
                img_bytes = f.read()

        data = base64.b64encode(img_bytes).decode("ascii")
        self._base64_data = f"data:{mime};base64,{data}"
        return self._base64_data

    # -----------------------------------------------------------------
    # Measurement
    # -----------------------------------------------------------------

    def measure(self, constraints: LayoutConstraints) -> Tuple[float, float, float]:
        iw = self.intrinsic_width
        ih = self.intrinsic_height
        ph = self.style.padding_horizontal + self.style.border_horizontal
        pv = self.style.padding_vertical + self.style.border_vertical
        return (iw + ph, iw + ph, ih + pv)

    # -----------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------

    def layout(self, constraints: LayoutConstraints) -> None:
        iw = self.intrinsic_width
        ih = self.intrinsic_height

        # Available content area
        content_w = self._content_available_width(constraints)
        if content_w is None:
            content_w = iw

        explicit_w = self._resolve_width(constraints)
        if explicit_w is not None:
            content_w = max(0.0, explicit_w - self.style.padding_horizontal - self.style.border_horizontal)

        explicit_h = self._resolve_height(constraints)
        content_h: float
        if explicit_h is not None:
            content_h = max(0.0, explicit_h - self.style.padding_vertical - self.style.border_vertical)
        else:
            # Scale height to maintain aspect ratio
            if iw > 0:
                content_h = ih * (content_w / iw)
            else:
                content_h = ih

        self._resolve_box_model(content_w, content_h)

        # Compute actual image draw rect within content box (object-fit)
        self.image_rect = self._compute_object_fit(content_w, content_h, iw, ih)

    def _compute_object_fit(
        self, box_w: float, box_h: float, img_w: float, img_h: float
    ) -> Rect:
        """Compute the image draw rect inside the content box."""
        fit = self.style.get("object-fit") or "fill"

        if fit == "fill":
            return Rect(0, 0, box_w, box_h)

        if fit == "none":
            # Centre at intrinsic size
            x = (box_w - img_w) / 2
            y = (box_h - img_h) / 2
            return Rect(x, y, img_w, img_h)

        # contain / cover
        scale_x = box_w / img_w if img_w else 1.0
        scale_y = box_h / img_h if img_h else 1.0

        if fit == "contain":
            scale = min(scale_x, scale_y)
        else:  # cover
            scale = max(scale_x, scale_y)

        draw_w = img_w * scale
        draw_h = img_h * scale
        x = (box_w - draw_w) / 2
        y = (box_h - draw_h) / 2
        return Rect(x, y, draw_w, draw_h)

    def __repr__(self) -> str:
        return f'ImageNode("{self.src}")'
