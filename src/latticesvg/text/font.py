"""Font loading, glyph measurement, and caching via FreeType (with Pillow fallback)."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Glyph metrics
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FontInfo:
    """Metadata for an indexed font."""
    family: str
    path: str
    weight: str
    style: str
    format: str       # "ttf", "otf", or "ttc"
    face_index: int


@dataclass(frozen=True)
class GlyphMetrics:
    """Metrics for a single glyph at a given size."""
    advance_x: float   # horizontal advance in px
    bearing_x: float   # left-side bearing
    bearing_y: float   # top-side bearing
    width: float       # bitmap / outline width
    height: float      # bitmap / outline height
    # Vertical metrics (populated when available)
    advance_y: float = 0.0       # vertical advance in px
    vert_origin_x: float = 0.0   # vertical origin X offset
    vert_origin_y: float = 0.0   # vertical origin Y offset


# ---------------------------------------------------------------------------
# Backend abstraction
# ---------------------------------------------------------------------------

class _FreeTypeBackend:
    """Measure glyphs using freetype-py."""

    def __init__(self) -> None:
        import freetype  # type: ignore
        self._freetype = freetype
        self._faces: Dict[Tuple[str, int], object] = {}

    def _get_face(self, font_path: str, size: int) -> object:
        key = (font_path, size)
        if key not in self._faces:
            face = self._freetype.Face(font_path)
            face.set_pixel_sizes(0, size)
            self._faces[key] = face
        return self._faces[key]

    def glyph_metrics(self, font_path: str, size: int, char: str) -> GlyphMetrics:
        face = self._get_face(font_path, size)
        # Use NO_HINTING to get floating-point advance widths that
        # match SVG renderers (Chrome, Firefox, librsvg) which render
        # <text> without pixel grid alignment.  FT_LOAD_DEFAULT rounds
        # advances to integers, causing cumulative drift for long runs,
        # especially noticeable when mixing bold and normal spans.
        face.load_char(char, self._freetype.FT_LOAD_NO_HINTING)  # type: ignore
        glyph = face.glyph
        m = glyph.metrics
        # FreeType metrics are in 26.6 fixed point (1/64 px)
        # Read vertical metrics if the font provides them.
        try:
            vert_adv = m.vertAdvance / 64.0 if m.vertAdvance else 0.0
            vert_ox = m.vertBearingX / 64.0 if m.vertBearingX else 0.0
            vert_oy = m.vertBearingY / 64.0 if m.vertBearingY else 0.0
        except (AttributeError, TypeError):
            vert_adv = 0.0
            vert_ox = 0.0
            vert_oy = 0.0
        return GlyphMetrics(
            advance_x=glyph.advance.x / 64.0,
            bearing_x=m.horiBearingX / 64.0,
            bearing_y=m.horiBearingY / 64.0,
            width=m.width / 64.0,
            height=m.height / 64.0,
            advance_y=vert_adv,
            vert_origin_x=vert_ox,
            vert_origin_y=vert_oy,
        )

    def ascender(self, font_path: str, size: int) -> float:
        face = self._get_face(font_path, size)
        return face.size.ascender / 64.0

    def descender(self, font_path: str, size: int) -> float:
        face = self._get_face(font_path, size)
        return face.size.descender / 64.0

    def units_per_em(self, font_path: str, size: int) -> float:
        face = self._get_face(font_path, size)
        return float(face.units_per_EM)


class _PillowBackend:
    """Fallback glyph measurement using Pillow."""

    def __init__(self) -> None:
        from PIL import ImageFont  # type: ignore
        self._ImageFont = ImageFont
        self._fonts: Dict[Tuple[str, int], object] = {}

    def _get_font(self, font_path: str, size: int) -> object:
        key = (font_path, size)
        if key not in self._fonts:
            self._fonts[key] = self._ImageFont.truetype(font_path, size)
        return self._fonts[key]

    def glyph_metrics(self, font_path: str, size: int, char: str) -> GlyphMetrics:
        font = self._get_font(font_path, size)
        bbox = font.getbbox(char)  # (left, top, right, bottom)
        advance = font.getlength(char)
        return GlyphMetrics(
            advance_x=advance,
            bearing_x=float(bbox[0]),
            bearing_y=float(-bbox[1]),  # approximate
            width=float(bbox[2] - bbox[0]),
            height=float(bbox[3] - bbox[1]),
        )

    def ascender(self, font_path: str, size: int) -> float:
        font = self._get_font(font_path, size)
        asc, desc = font.getmetrics()
        return float(asc)

    def descender(self, font_path: str, size: int) -> float:
        font = self._get_font(font_path, size)
        asc, desc = font.getmetrics()
        return float(-desc)


# ---------------------------------------------------------------------------
# Font discovery
# ---------------------------------------------------------------------------

_SYSTEM_FONT_DIRS: List[str] = []

if sys.platform == "linux":
    _SYSTEM_FONT_DIRS = [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.local/share/fonts"),
        os.path.expanduser("~/.fonts"),
    ]
elif sys.platform == "darwin":
    _SYSTEM_FONT_DIRS = [
        "/System/Library/Fonts",
        "/Library/Fonts",
        os.path.expanduser("~/Library/Fonts"),
    ]
elif sys.platform == "win32":
    windir = os.environ.get("WINDIR", r"C:\Windows")
    _SYSTEM_FONT_DIRS = [
        os.path.join(windir, "Fonts"),
        os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Fonts"),
    ]


# Generic family names recognised by CSS
_GENERIC_FAMILIES = frozenset({"serif", "sans-serif", "monospace", "cursive", "fantasy"})


def parse_font_families(value) -> List[str]:
    """Parse a CSS ``font-family`` value into a flat list of family names.

    Accepts a comma-separated string, a list of strings, or ``None``
    (which falls back to ``["sans-serif"]``).
    """
    if value is None:
        return ["sans-serif"]
    if isinstance(value, list):
        result: List[str] = []
        for item in value:
            if isinstance(item, str):
                result.extend(
                    x.strip().strip('"').strip("'")
                    for x in item.split(",")
                )
        return [x for x in result if x] or ["sans-serif"]
    if isinstance(value, str):
        return [
            x.strip().strip('"').strip("'")
            for x in value.split(",")
            if x.strip()
        ] or ["sans-serif"]
    return ["sans-serif"]


# Common font-family aliases
_FAMILY_ALIASES: Dict[str, List[str]] = {
    "sans-serif": [
        # CJK-capable fonts first for consistent measurement
        "NotoSansCJK", "Noto Sans CJK",
        "NotoSans", "Noto Sans",
        "DejaVuSans", "DejaVu Sans",
        "Arial", "Helvetica", "Liberation Sans",
        "FreeSans",
    ],
    "serif": [
        "NotoSerifCJK", "Noto Serif CJK",
        "NotoSerif", "Noto Serif",
        "DejaVuSerif", "DejaVu Serif",
        "Times New Roman", "Liberation Serif",
        "FreeSerif",
    ],
    "monospace": [
        "NotoSansMono", "Noto Sans Mono",
        "DejaVuSansMono", "DejaVu Sans Mono",
        "Courier New", "Liberation Mono",
        "FreeMono",
    ],
}


class FontManager:
    """Manages font discovery, loading, and glyph metric caching.

    Usage::

        fm = FontManager.instance()
        path = fm.find_font(["Arial", "sans-serif"])
        metrics = fm.glyph_metrics(path, 16, "A")
    """

    _singleton: Optional["FontManager"] = None

    def __init__(self) -> None:
        self._backend = self._create_backend()
        self._cache: Dict[Tuple[str, int, str], GlyphMetrics] = {}
        self._font_index: Optional[Dict[str, str]] = None  # family_lower -> path
        self._extra_dirs: List[str] = []

    @classmethod
    def instance(cls) -> "FontManager":
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._singleton = None

    def add_font_directory(self, path: str) -> None:
        """Register an additional directory to search for fonts."""
        self._extra_dirs.append(path)
        self._font_index = None  # force re-scan

    # -----------------------------------------------------------------
    # Backend
    # -----------------------------------------------------------------

    @staticmethod
    def _create_backend():
        try:
            return _FreeTypeBackend()
        except ImportError:
            pass
        try:
            return _PillowBackend()
        except ImportError:
            pass
        raise RuntimeError(
            "Neither freetype-py nor Pillow is available. "
            "Install at least one: pip install freetype-py"
        )

    # -----------------------------------------------------------------
    # Font discovery
    # -----------------------------------------------------------------

    def _build_font_index(self) -> Dict[str, str]:
        """Scan system font directories and build a name→path index."""
        index: Dict[str, str] = {}
        dirs = list(_SYSTEM_FONT_DIRS) + self._extra_dirs
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for root, _, files in os.walk(d):
                for fname in files:
                    low = fname.lower()
                    if low.endswith((".ttf", ".otf", ".ttc")):
                        fullpath = os.path.join(root, fname)
                        # Index by filename stem (lowered)
                        stem = Path(fname).stem.lower()
                        index[stem] = fullpath
                        # Also index without hyphens/spaces
                        clean = stem.replace("-", "").replace(" ", "").replace("_", "")
                        index[clean] = fullpath
                        # Index by embedded family name (FreeType only)
                        self._index_by_family_name(index, fullpath)
        return index

    def _index_by_family_name(self, index: Dict[str, str], font_path: str) -> None:
        """Read font's embedded family name via FreeType and add to index.

        For TTC/OTF fonts that share the same family name across weights
        (e.g. "Noto Sans CJK JP" for Regular, Bold, Medium …), we also
        index ``{family}{style}`` so that ``_name_candidates`` can locate
        the correct weight variant (e.g. "notosanscjkjpbold").
        """
        if not isinstance(self._backend, _FreeTypeBackend):
            return
        try:
            face = self._backend._freetype.Face(font_path)
            name = face.family_name
            if isinstance(name, bytes):
                name = name.decode('utf-8', errors='replace')
            style = face.style_name
            if isinstance(style, bytes):
                style = style.decode('utf-8', errors='replace')
            if name:
                key = name.lower().replace(' ', '').replace('-', '').replace('_', '')
                index.setdefault(key, font_path)
                # Also index {family}{style} so bold/italic lookup works
                # for fonts where all weights share the same family name.
                if style:
                    style_lower = style.lower().replace(' ', '').replace('-', '').replace('_', '')
                    if style_lower and style_lower not in ('', ):
                        style_key = key + style_lower
                        index.setdefault(style_key, font_path)
        except Exception:
            pass

    def _get_font_index(self) -> Dict[str, str]:
        if self._font_index is None:
            self._font_index = self._build_font_index()
        return self._font_index

    def find_font(
        self,
        family_list: Optional[list] = None,
        weight: str = "normal",
        style: str = "normal",
    ) -> Optional[str]:
        """Find a font file matching the requested family list.

        Returns the first match found, or ``None``.
        """
        if family_list is None:
            family_list = ["sans-serif"]
        if isinstance(family_list, str):
            family_list = [family_list]

        idx = self._get_font_index()

        # Expand families  (e.g. "sans-serif" → multiple concrete names)
        expanded: List[str] = []
        for fam in family_list:
            if fam.lower() in _FAMILY_ALIASES:
                expanded.extend(_FAMILY_ALIASES[fam.lower()])
            else:
                expanded.append(fam)

        # Build candidate stems
        weight_suffix = ""
        if weight == "bold":
            weight_suffix = "bold"
        style_suffix = ""
        if style in ("italic", "oblique"):
            style_suffix = "italic"

        for name in expanded:
            candidates = self._name_candidates(name, weight_suffix, style_suffix)
            for c in candidates:
                if c in idx:
                    return idx[c]

        # Last resort — return first font found in index
        if idx:
            return next(iter(idx.values()))

        return None

    def find_font_chain(
        self,
        family_list: Optional[list] = None,
        weight: str = "normal",
        style: str = "normal",
    ) -> List[str]:
        """Resolve each family to a font path, returning an ordered fallback chain.

        Unlike :meth:`find_font` (which returns only the first match), this
        method resolves *every* distinct family in *family_list* so that
        characters missing in the primary font can be measured with a
        fallback font.

        When a generic family (e.g. ``"sans-serif"``) is given, **all**
        concrete fonts reachable through the alias list are included in
        the chain, giving a wide Unicode coverage.
        """
        if family_list is None:
            family_list = ["sans-serif"]
        if isinstance(family_list, str):
            family_list = [family_list]

        idx = self._get_font_index()
        weight_suffix = "bold" if weight == "bold" else ""
        style_suffix = "italic" if style in ("italic", "oblique") else ""

        chain: List[str] = []
        seen: set = set()

        for fam in family_list:
            # Expand generic families into their full alias list so
            # that *every* available concrete font is added — not
            # just the first hit.
            if fam.lower() in _FAMILY_ALIASES:
                names = _FAMILY_ALIASES[fam.lower()]
            else:
                names = [fam]

            for name in names:
                candidates = self._name_candidates(name, weight_suffix, style_suffix)
                for c in candidates:
                    if c in idx:
                        path = idx[c]
                        if path not in seen:
                            chain.append(path)
                            seen.add(path)
                        break  # found this name, move to next

        if not chain:
            fallback = self.find_font(family_list, weight, style)
            if fallback:
                chain.append(fallback)
        return chain

    def _resolve_single_family(
        self, family: str, weight: str = "normal", style: str = "normal",
    ) -> Optional[str]:
        """Find a font path for a single family name."""
        idx = self._get_font_index()

        if family.lower() in _FAMILY_ALIASES:
            names = _FAMILY_ALIASES[family.lower()]
        else:
            names = [family]

        weight_suffix = "bold" if weight == "bold" else ""
        style_suffix = "italic" if style in ("italic", "oblique") else ""

        for name in names:
            candidates = self._name_candidates(name, weight_suffix, style_suffix)
            for c in candidates:
                if c in idx:
                    return idx[c]
        return None

    @staticmethod
    def _name_candidates(name: str, weight_suffix: str, style_suffix: str) -> List[str]:
        """Generate candidate index keys for a font name."""
        base = name.lower().replace(" ", "").replace("-", "").replace("_", "")
        candidates = []
        if weight_suffix and style_suffix:
            candidates.append(f"{base}{weight_suffix}{style_suffix}")
            candidates.append(f"{base}-{weight_suffix}{style_suffix}")
        if weight_suffix:
            candidates.append(f"{base}{weight_suffix}")
            candidates.append(f"{base}-{weight_suffix}")
        if style_suffix:
            candidates.append(f"{base}{style_suffix}")
            candidates.append(f"{base}-{style_suffix}")
        # Prefer explicit "regular" over bare base name so that
        # the bare name (which may point to any weight/style) is
        # only used as a last resort.
        candidates.append(f"{base}regular")
        candidates.append(f"{base}-regular")
        candidates.append(base)
        return candidates

    # -----------------------------------------------------------------
    # Glyph measurement (cached)
    # -----------------------------------------------------------------

    def glyph_metrics(self, font_path, size: int, char: str) -> GlyphMetrics:
        """Return glyph metrics for *char*.

        *font_path* may be a single path string **or** an ordered list
        of paths (a fallback chain).  When a list is given the first
        font that contains a glyph for *char* is used.
        """
        if isinstance(font_path, list):
            return self._glyph_metrics_chain(font_path, size, char)
        key = (font_path, size, char)
        if key not in self._cache:
            self._cache[key] = self._backend.glyph_metrics(font_path, size, char)
        return self._cache[key]

    def _glyph_metrics_chain(self, chain: List[str], size: int, char: str) -> GlyphMetrics:
        """Find the first font in *chain* that has a glyph for *char*."""
        for fp in chain:
            if self._has_glyph(fp, char):
                return self.glyph_metrics(fp, size, char)
        # None have it — use first font's .notdef
        return self.glyph_metrics(chain[0], size, char)

    def _has_glyph(self, font_path: str, char: str) -> bool:
        """Return True if *font_path* contains a glyph for *char*."""
        key = ('_has', font_path, char)
        if key not in self._cache:
            if isinstance(self._backend, _FreeTypeBackend):
                face = self._backend._get_face(font_path, 16)
                self._cache[key] = face.get_char_index(ord(char)) != 0
            else:
                self._cache[key] = True  # Pillow: assume yes
        return self._cache[key]

    def ascender(self, font_path, size: int) -> float:
        if isinstance(font_path, list):
            font_path = font_path[0]
        return self._backend.ascender(font_path, size)

    def descender(self, font_path, size: int) -> float:
        if isinstance(font_path, list):
            font_path = font_path[0]
        return self._backend.descender(font_path, size)

    def font_family_name(self, font_path: str) -> Optional[str]:
        """Get the CSS font-family name from a font file using FreeType."""
        key = ('_family_name', font_path)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        result: Optional[str] = None
        if isinstance(self._backend, _FreeTypeBackend):
            try:
                face = self._backend._freetype.Face(font_path)
                name = face.family_name
                if isinstance(name, bytes):
                    name = name.decode('utf-8', errors='replace')
                result = name
            except Exception:
                pass
        if result is None:
            # Fallback: derive from filename stem
            result = Path(font_path).stem.replace('-', ' ').replace('_', ' ')
        self._cache[key] = result
        return result

    # -----------------------------------------------------------------
    # Public query API
    # -----------------------------------------------------------------

    def get_font_path(
        self,
        family: str,
        weight: str = "normal",
        style: str = "normal",
    ) -> Optional[str]:
        """Return the filesystem path for *family*, or ``None`` if not found.

        Unlike :meth:`find_font`, this method does **not** fall back to an
        arbitrary default font when no match is found.
        """
        return self._resolve_single_family(family, weight, style)

    def list_fonts(self) -> List[FontInfo]:
        """Return a :class:`FontInfo` for every indexed font file."""
        idx = self._get_font_index()
        seen_paths: Dict[str, FontInfo] = {}
        for path in idx.values():
            if path in seen_paths:
                continue
            ext = Path(path).suffix.lower().lstrip(".")
            fmt = ext if ext in ("ttf", "otf", "ttc") else ext
            family_name = ""
            weight = "normal"
            style_name = "normal"
            face_index = 0
            if isinstance(self._backend, _FreeTypeBackend):
                try:
                    face = self._backend._freetype.Face(path)
                    raw_name = face.family_name
                    if isinstance(raw_name, bytes):
                        raw_name = raw_name.decode("utf-8", errors="replace")
                    family_name = raw_name or Path(path).stem
                    raw_style = face.style_name
                    if isinstance(raw_style, bytes):
                        raw_style = raw_style.decode("utf-8", errors="replace")
                    sl = (raw_style or "").lower()
                    weight = "bold" if "bold" in sl else "normal"
                    style_name = "italic" if "italic" in sl or "oblique" in sl else "normal"
                except Exception:
                    family_name = Path(path).stem
            else:
                family_name = Path(path).stem
            seen_paths[path] = FontInfo(
                family=family_name,
                path=path,
                weight=weight,
                style=style_name,
                format=fmt,
                face_index=face_index,
            )
        # For TTC files, enumerate additional faces
        ttc_extras: List[FontInfo] = []
        if isinstance(self._backend, _FreeTypeBackend):
            for path, info in list(seen_paths.items()):
                if info.format != "ttc":
                    continue
                try:
                    face = self._backend._freetype.Face(path)
                    num = face.num_faces
                    for fi in range(1, num):
                        face_i = self._backend._freetype.Face(path, fi)
                        raw_name = face_i.family_name
                        if isinstance(raw_name, bytes):
                            raw_name = raw_name.decode("utf-8", errors="replace")
                        raw_style = face_i.style_name
                        if isinstance(raw_style, bytes):
                            raw_style = raw_style.decode("utf-8", errors="replace")
                        sl = (raw_style or "").lower()
                        ttc_extras.append(FontInfo(
                            family=raw_name or family_name,
                            path=path,
                            weight="bold" if "bold" in sl else "normal",
                            style="italic" if "italic" in sl or "oblique" in sl else "normal",
                            format="ttc",
                            face_index=fi,
                        ))
                except Exception:
                    pass
        result = list(seen_paths.values()) + ttc_extras
        result.sort(key=lambda f: (f.family.lower(), f.weight, f.style))
        return result
